# -*- coding: utf-8 -*-
"""T4M-DEMO: chạy thử TRỌN CHUỖI bằng một lệnh, hoàn toàn ngoại tuyến, để cho giáo viên ECA xem.

    python du_lieu_test/demo_t4m.py --ra ./demo_ra
    python du_lieu_test/demo_t4m.py --ra ./demo_ra --so-hs 200 --seed 7
    python du_lieu_test/demo_t4m.py --ra ./demo_ra --moi-clb     # cách B: mỗi CLB một biểu mẫu
    python du_lieu_test/demo_t4m.py --ra ./demo_ra --day-du      # Top 7 + tick chọn thi + điểm quyết tâm

Các bước (đúng đường phần mềm dùng thật, không đụng app.db của workspace nào):
  1. sinh tệp Lists giả (nguyện vọng; mã CLB lấy từ de_thi.json)      -> lists_gia.csv
  2. sinh tệp Forms chỉ-thi giả (Email + câu hỏi + Points)            -> forms_chi_thi_gia.xlsx
  3. bộ chuyển đổi --chi-thi                                          -> SO_NHAP_CLB.xlsx, BANG_DIEM.xlsx
  4. nạp Sổ nhập vào CSDL TẠM và chạy pipeline (PipelineAPI.import_so_nhap, run_pipeline)
  5. xuất Excel theo lớp chủ nhiệm (export_theo_lop)                  -> ket_qua_theo_lop/
  6. in tóm tắt tiếng Việt

--moi-clb (cách B, T4M_CONG_THI.md): bước 2 tách phiếu giả thành MỘT tệp xuất mỗi CLB có đề (không câu
cổng) trong forms_moi_clb/, sinh BaiThi.csv giả như flow "Đã làm" ghi (cố ý thiếu một dòng), và bước 3
chạy bộ chuyển đổi với --bai-thi. Cùng seed thì kết quả xếp trùng với chế độ một biểu mẫu chung.

--day-du (T4M-Q5c, kết hợp được với --moi-clb): List giả có THIk (tick chọn thi, tối đa 5 mỗi ngày) và WPk
(điểm quyết tâm, hai quỹ 100); số ô nguyện vọng mỗi ngày = min(7, số CLB của ngày); phiếu Forms giả chỉ cho CLB
đã tick, gài thêm: một em tick mà vắng, một em nộp bài mà không tick, một quỹ điểm cộng thiếu 100. Bộ chuyển đổi
báo hai trường hợp đầu; quỹ sai làm kiosk CHẶN lần chạy đầu (đúng thiết kế), demo sửa quỹ đó ở "Bước 3" của
kiosk (admin_save_wharton) rồi chạy lại. Điểm quyết tâm trong CSDL TẠM được BẬT (không có --day-du: TẮT, như cũ).
Dòng "Điểm quyết tâm: BẬT/TẮT" luôn có trong tóm tắt.

DỮ LIỆU MÔ PHỎNG: tên, email (miền example.test), lớp, điểm đều bịa; không phải khảo sát thật.
Cùng --seed cho cùng kết quả. Thư mục `ket_qua_theo_lop` cũ trong --ra (của lần chạy trước) bị thay.
"""

import argparse
import base64
import copy
import csv
import os
import shutil
import sqlite3
import sys
import tempfile

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (GOC, os.path.join(GOC, "mau_forms_thi_clb"), os.path.dirname(os.path.abspath(__file__))):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import bieu_mau as bm  # noqa: E402
import chuyen_forms_sang_phan_mem as cv  # noqa: E402
import sinh_xuat_lists_gia as lists_gia  # noqa: E402
import tao_mau_forms as tm  # noqa: E402

SO_HS_MAC_DINH = 120
SEED_MAC_DINH = 6112026          # 06/11/2026


def _clb_theo_ngay(de):
    theo_ngay = {}
    for ngay in lists_gia.NGAY:
        buoi = cv._ma_buoi_tu_thu(de, ngay)
        theo_ngay[ngay] = [c["club_id"] for c in de["cau_lac_bo"] if c["buoi"] == buoi]
        if not theo_ngay[ngay]:
            raise ValueError("de_thi.json không có CLB nào ở %s" % ngay)
    return theo_ngay


def sinh_lists(de, duong, so_hs=SO_HS_MAC_DINH, seed=SEED_MAC_DINH):
    """Tệp Lists giả dùng đúng mã CLB của `de` (mỗi ngày trong Lists = một buổi của de_thi.json)."""
    return lists_gia.ghi_csv(duong, so_hs=so_hs, seed=seed, clb_theo_ngay=_clb_theo_ngay(de))


TOP_TOI_DA = 7                      # số nguyện vọng tối đa mỗi ngày (Truong quyết 06/11/2026)


def sinh_lists_day_du(de, duong, so_hs=SO_HS_MAC_DINH, seed=SEED_MAC_DINH):
    """Lists giả có THIk + WPk (T4M-Q5c) và MỘT quỹ điểm cố ý cộng thiếu. Số ô NV = min(7, số CLB nhiều nhất
    của một ngày). Trả {"n": số dòng, "so_nv": số ô, "quy_sai": {email, thu, quy, club_id, thieu}}."""
    theo_ngay = _clb_theo_ngay(de)
    so_nv = min(TOP_TOI_DA, max(len(v) for v in theo_ngay.values()))
    co_de = {c["club_id"] for c in bm.clb_co_thi(de)}
    dong = lists_gia.sinh(so_hs=so_hs, seed=seed, clb_theo_ngay=theo_ngay, so_nv=so_nv,
                          co_tick=True, co_wp=True, clb_co_de=co_de)
    quy_sai = lists_gia.gai_quy_khong_du(dong, so_nv)
    if quy_sai is None:
        raise ValueError("không có dòng nào để gài quỹ điểm thiếu 100 (tăng --so-hs)")
    n = lists_gia.ghi_dong(duong, dong, so_nv, True, True)
    return {"n": n, "so_nv": so_nv, "quy_sai": quy_sai}


def _so(x):
    """Ô điểm đọc bằng doc_tep_xuat (chuỗi) -> số; ô trống = 0."""
    if x in (None, ""):
        return 0
    v = float(x)
    return int(v) if v.is_integer() else v


def tach_moi_clb(de, duong_chung, thu_muc):
    """Cách B: tách tệp Forms giả chung (có câu cổng) thành một tệp xuất mỗi CLB có đề, như mỗi biểu mẫu
    một CLB xuất ra: không câu cổng, chỉ phiếu đã chọn "Có" cho CLB đó, ID đánh lại từ 1. Trả các đường dẫn."""
    from openpyxl import Workbook

    tieu, cac_dong = cv.doc_tep_xuat(duong_chung)
    vi_tri = {h: i for i, h in enumerate(tieu)}
    if os.path.isdir(thu_muc):
        shutil.rmtree(thu_muc)
    os.makedirs(thu_muc)
    ra = []
    for clb in bm.clb_co_thi(de):
        cong = bm.cau_cong_thi(de, clb, chi_thi=True)
        cau = []
        for i in range(1, len(clb["de_thi"]) + 1):
            td = bm.cau_de_thi(clb, i)
            cau += [td, cv.TIEN_TO_DIEM + td]
        tieu_moi = ["ID", "Start time", "Completion time", "Email", "Name", "Total points"] + cau
        wb = Workbook()
        ws = wb.active
        ws.title = "Sheet1"
        ws.append(tieu_moi)
        n = 0
        for dong in cac_dong:
            if dong[vi_tri[cong]] != bm.CO:
                continue
            n += 1
            o = [dong[vi_tri[h]] for h in cau]
            for k in range(1, len(o), 2):                 # cột Points: số, như Forms xuất
                o[k] = _so(o[k])
            tong = sum(o[k] for k in range(1, len(o), 2))
            ws.append([n] + [dong[vi_tri[h]] for h in ("Start time", "Completion time", "Email", "Name")]
                      + [tong] + o)
        duong = os.path.join(thu_muc, "%s.xlsx" % clb["club_id"])
        wb.save(duong)
        ra.append(duong)
    return ra


def ghi_bai_thi_gia(de, cac_tep, duong):
    """List BaiThi giả như flow "Đã làm" ghi (mỗi phiếu một dòng, email chữ thường), cố ý THIẾU dòng của
    phiếu đầu tiên chỉ nộp một lần trong tệp đầu có phiếu (flow lỗi một lần). Trả (email, club_id) bị thiếu."""
    dong_ra, thieu = [], None
    for tep in cac_tep:
        ma = os.path.splitext(os.path.basename(tep))[0]
        tieu, cac_dong = cv.doc_tep_xuat(tep)
        i_id, i_email, i_luc = tieu.index("ID"), tieu.index("Email"), tieu.index("Completion time")
        dem = {}
        for dong in cac_dong:
            e = str(dong[i_email]).strip().lower()
            dem[e] = dem.get(e, 0) + 1
        for dong in cac_dong:
            email = str(dong[i_email]).strip().lower()
            if thieu is None and dem[email] == 1:          # em nộp hai lần vẫn còn dòng kia: bỏ qua
                thieu = (email, ma)
                continue
            luc = dong[i_luc]
            dong_ra.append([email, ma, "%s-%s" % (ma, dong[i_id]),
                            str(luc).replace(" ", "T") + "Z"])    # dạng ISO như flow ghi
    if thieu is None:
        raise ValueError("không có phiếu thi nào để dựng BaiThi giả")
    with open(duong, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\r\n")
        w.writerow(["Email", "ClubId", "ResponseId", "NopLuc"])
        w.writerows(dong_ra)
    return thieu


def he_so_cho_tu_dong(de, so_hs):
    """Chỉ tiêu mẫu trong de_thi.json (~42 chỗ/buổi) chỉ đủ cho ~50 em; nhân lên để mỗi buổi có chỗ
    cho khoảng 70% số em (còn cạnh tranh để thấy Tầng 1 có tác dụng), không nhỏ hơn 1."""
    theo_buoi = {}
    for c in de["cau_lac_bo"]:
        theo_buoi[c["buoi"]] = theo_buoi.get(c["buoi"], 0) + c["capacity"]
    tb = sum(theo_buoi.values()) / len(theo_buoi)
    return max(1.0, round(0.7 * so_hs / tb, 1))


def sua_quy_gai(api, duong_db, quy_sai):
    """Giả lập "Bước 3. Điểm quyết tâm" của kiosk: cộng phần điểm thiếu vào CLB bị gài, lưu bằng
    admin_save_wharton (cùng luật kiểm với kiosk). Trả kết quả của API."""
    sid = quy_sai["email"].lower()
    con = sqlite3.connect(duong_db)
    try:
        dong = con.execute("SELECT club_id, tier, points FROM wharton_bids WHERE student_id = ?", (sid,)).fetchall()
    finally:
        con.close()
    w = {1: {}, 2: {}}
    for club, tier, diem in dong:
        w[tier][club] = diem + (quy_sai["thieu"] if club == quy_sai["club_id"] else 0)
    return api.admin_save_wharton(sid, w[1], w[2])


def chay_demo(ra, so_hs=SO_HS_MAC_DINH, seed=SEED_MAC_DINH, he_so_cho=None, moi_clb=False, day_du=False):
    """Chạy trọn chuỗi vào thư mục `ra`. Trả tóm tắt (dict) để in hoặc kiểm.

    `moi_clb`: cách B (mỗi CLB một biểu mẫu + BaiThi.csv + --bai-thi); thêm khoá `doi_chieu`, `n_bieu_mau`.
    `day_du` (T4M-Q5c): List có THIk + WPk, điểm quyết tâm BẬT trong CSDL tạm; thêm `quy_sai`, `bi_chan_lan_dau`.
    Luôn có khoá `diem_quyet_tam` (True/False: giá trị rules.wharton thật sự dùng khi chạy).

    `he_so_cho`: nhân chỉ tiêu mỗi CLB của de_thi.json (bản sao trong bộ nhớ; tệp không đổi).
    None = tự tính theo `so_hs`; 1 = giữ nguyên chỉ tiêu mẫu."""
    import cau_hinh_ws as ch
    from api import PipelineAPI

    de = bm.doc_de_thi()
    if he_so_cho is None:
        he_so_cho = he_so_cho_tu_dong(de, so_hs)
    de = copy.deepcopy(de)
    for c in de["cau_lac_bo"]:
        c["capacity"] = max(1, round(c["capacity"] * he_so_cho))
    ra = os.path.abspath(ra)
    os.makedirs(ra, exist_ok=True)
    duong_lists = os.path.join(ra, "lists_gia.csv")
    duong_forms = os.path.join(ra, "forms_chi_thi_gia.xlsx")
    if day_du:
        gai_lists = sinh_lists_day_du(de, duong_lists, so_hs, seed)
    else:
        sinh_lists(de, duong_lists, so_hs, seed)
    danh_sach, canh_bao_lists = cv.doc_lists(duong_lists, de)
    if not moi_clb:
        gai = tm.ghi_mau_xuat_chi_thi(de, duong_forms, danh_sach, hat_giong=seed)
        kq_cv = cv.chuyen_chi_thi([duong_forms], duong_lists, ra, de)
    else:
        with tempfile.TemporaryDirectory(prefix="demo_t4m_chung_") as tam_chung:
            duong_chung = os.path.join(tam_chung, "forms_chung.xlsx")
            gai = tm.ghi_mau_xuat_chi_thi(de, duong_chung, danh_sach, hat_giong=seed)
            cac_tep = tach_moi_clb(de, duong_chung, os.path.join(ra, "forms_moi_clb"))
        duong_bt = os.path.join(ra, "BaiThi.csv")
        gai["bai_thi_thieu"] = ghi_bai_thi_gia(de, cac_tep, duong_bt)
        kq_cv = cv.chuyen_chi_thi(cac_tep, duong_lists, ra, de, bai_thi=duong_bt)
    duong_so = os.path.join(ra, cv.TEN_SO)
    thu_muc_lop = os.path.join(ra, "ket_qua_theo_lop")
    if os.path.isdir(thu_muc_lop):
        shutil.rmtree(thu_muc_lop)

    with tempfile.TemporaryDirectory(prefix="demo_t4m_") as tam:
        duong_db = os.path.join(tam, "app.db")
        api = PipelineAPI(duong_db)
        # Không --day-du: dữ liệu demo không có điểm quyết tâm (mặc định BẬT): tắt trong CSDL TẠM, như người
        # quản trị tắt ở Cài đặt workspace. Có --day-du: Sổ có điểm quyết tâm nên BẬT.
        ch.ghi_cau_hinh(duong_db, {"rules": {"wharton": bool(day_du)}})
        diem_quyet_tam = bool(ch.doc_cau_hinh(duong_db)["rules"]["wharton"])
        with open(duong_so, "rb") as f:
            r = api.import_so_nhap(base64.b64encode(f.read()).decode())
        if not r["ok"]:
            raise RuntimeError("nạp Sổ nhập thất bại: %s" % r["errors"])
        r = api.run_pipeline(seed=seed)
        bi_chan = False
        if not r["ok"] and day_du and any(e["code"] == "wharton_ho_so_chua_hop_le" for e in r["errors"]):
            # Quỹ điểm bị gài làm kiosk chặn (đúng thiết kế): sửa như người dùng ở Bước 3, rồi chạy lại.
            bi_chan = True
            sua = sua_quy_gai(api, duong_db, gai_lists["quy_sai"])
            if not sua["ok"]:
                raise RuntimeError("sửa quỹ điểm quyết tâm thất bại: %s" % sua["errors"])
            r = api.run_pipeline(seed=seed)
        if not r["ok"]:
            raise RuntimeError("chạy pipeline thất bại: %s" % r["errors"])
        r = api.export_theo_lop(thu_muc_lop)
        if not r["ok"]:
            raise RuntimeError("xuất theo lớp thất bại: %s" % r["errors"])
        n_tep_lop = r["data"]["n_tep"]
        con = sqlite3.connect(duong_db)
        try:
            ket_qua = con.execute(
                "SELECT student_id, buoi, club_id, round_num, matched_tier, rank_in_student_pref "
                "FROM match_results ORDER BY student_id, buoi").fetchall()
            n_hs = con.execute("SELECT COUNT(*) FROM students").fetchone()[0]
            n_luot = con.execute(
                "SELECT COUNT(*) FROM (SELECT DISTINCT p.student_id, c.buoi FROM preferences p "
                "JOIN clubs c ON c.club_id = p.club_id)").fetchone()[0]
            n_clb = con.execute("SELECT COUNT(*) FROM clubs").fetchone()[0]
            n_tang1 = con.execute("SELECT COUNT(DISTINCT club_id) FROM club_scores").fetchone()[0]
        finally:
            con.close()

    kq = {"n_hoc_sinh": n_hs, "n_luot": n_luot, "he_so_cho": he_so_cho,
            "n_dat_nv": sum(1 for x in ket_qua if x[5] is not None),
            "n_nv1": sum(1 for x in ket_qua if x[5] == 1), "n_clb": n_clb, "n_tang1": n_tang1,
            "n_bai_thi": kq_cv["n_bai_thi"], "n_tep_lop": n_tep_lop,
            "canh_bao": canh_bao_lists + kq_cv["canh_bao"], "gai": gai, "ket_qua": ket_qua,
            "ra": ra, "diem_quyet_tam": diem_quyet_tam}
    if day_du:
        gai["quy_sai"] = gai_lists["quy_sai"]
        kq["bi_chan_lan_dau"] = bi_chan
        kq["so_nv"] = gai_lists["so_nv"]
    if moi_clb:
        kq["doi_chieu"] = kq_cv["doi_chieu_bai_thi"]
        kq["n_bieu_mau"] = len(cac_tep)
    return kq


def in_tom_tat(kq, out=None):
    out = out or sys.stdout
    p = lambda s="": print(s, file=out)   # noqa: E731
    p("=== CHẠY THỬ TRỌN CHUỖI (dữ liệu MÔ PHỎNG) ===")
    if "doi_chieu" in kq:
        p("Cách B: mỗi CLB một biểu mẫu (%d tệp xuất trong forms_moi_clb/, không câu cổng)." % kq["n_bieu_mau"])
    p("Điểm quyết tâm: %s" % ("BẬT (Sổ nhập có cột điểm quyết tâm)" if kq["diem_quyet_tam"] else "TẮT (dữ liệu không có)"))
    if "bi_chan_lan_dau" in kq:
        q = kq["gai"]["quy_sai"]
        p("Số ô nguyện vọng mỗi ngày = %d (= min(7, số CLB của ngày)), tick chọn thi (tối đa 5 CLB/ngày), hai quỹ 100 điểm. "
          "Quỹ %d của %s bị gài thiếu %d điểm: "
          "kiosk %s lần chạy đầu, demo sửa ở Bước 3 rồi chạy lại."
          % (kq["so_nv"], q["quy"], q["email"], q["thieu"], "CHẶN" if kq["bi_chan_lan_dau"] else "không chặn"))
        e, c = kq["gai"]["tick_vang"]
        p("Gài tick mà vắng thi: %s ở %s (bộ chuyển đổi không báo; kiosk cảnh báo vắng thi và bỏ điểm quỹ 1 của CLB đó)." % (e, c))
        e, c = kq["gai"]["nop_khong_tick"]
        p("Gài nộp bài mà không tick: %s ở %s (điểm bỏ khỏi Sổ nhập, có cảnh báo)." % (e, c))
    p("%d học sinh, %d bài thi đã chấm, %d CLB (%d CLB có thi tuyển = Tầng 1)."
      % (kq["n_hoc_sinh"], kq["n_bai_thi"], kq["n_clb"], kq["n_tang1"]))
    ty_le = 100.0 * kq["n_nv1"] / kq["n_luot"] if kq["n_luot"] else 0.0
    p("Chỉ tiêu mỗi CLB = chỉ tiêu mẫu ở de_thi.json × %g (để vừa %d em; --he-so-cho 1 để giữ nguyên)."
      % (kq["he_so_cho"], kq["n_hoc_sinh"]))
    p("Trong %d lượt đăng ký (em × buổi): %d lượt vào nguyện vọng 1 (%.0f%%), %d lượt vào một nguyện vọng "
      "đã chọn. Phần còn lại được xếp bù vào chỗ trống." % (kq["n_luot"], kq["n_nv1"], ty_le, kq["n_dat_nv"]))
    p("Excel theo lớp: %d tệp trong %s" % (kq["n_tep_lop"], os.path.join(kq["ra"], "ket_qua_theo_lop")))
    p("")
    p("%d cảnh báo (cố ý gài; chi tiết trong BANG_DIEM.xlsx, sheet 'Cảnh báo'):" % len(kq["canh_bao"]))
    for dong, sid, nd in kq["canh_bao"]:
        p("  dòng %s %s: %s" % (dong, sid, nd))
    p("")
    if "doi_chieu" in kq:
        dc = kq["doi_chieu"]
        p("")
        p("Đối chiếu BaiThi (list trạng thái của flow với các tệp xuất; chỉ báo, không đổi điểm): %s"
          % ("khớp hết." if not dc else "%d chỗ lệch (cố ý gài: flow bỏ sót một bài):" % len(dc)))
        for loai, email, ma, _nd in dc:
            p("  %s %s %s" % (loai, email, ma))
        p("")
        p("Tệp ra: lists_gia.csv, forms_moi_clb/, BaiThi.csv, SO_NHAP_CLB.xlsx, BANG_DIEM.xlsx, ket_qua_theo_lop/")
        return
    p("Tệp ra: lists_gia.csv, forms_chi_thi_gia.xlsx, SO_NHAP_CLB.xlsx, BANG_DIEM.xlsx, ket_qua_theo_lop/")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Chạy thử trọn chuỗi: Lists + Forms giả -> Sổ nhập -> xếp CLB -> Excel theo lớp.")
    ap.add_argument("--ra", required=True, help="thư mục ghi các tệp kết quả")
    ap.add_argument("--so-hs", type=int, default=SO_HS_MAC_DINH, help="số học sinh giả (mặc định %(default)s)")
    ap.add_argument("--seed", type=int, default=SEED_MAC_DINH, help="hạt giống (mặc định %(default)s)")
    ap.add_argument("--he-so-cho", type=float, default=None,
                    help="nhân chỉ tiêu mỗi CLB (mặc định: tự tính theo số học sinh; 1 = giữ nguyên de_thi.json)")
    ap.add_argument("--day-du", action="store_true",
                    help="Top 7 + tick chọn thi (tối đa 5/ngày) + điểm quyết tâm (hai quỹ 100); bật điểm quyết tâm")
    ap.add_argument("--moi-clb", action="store_true",
                    help="cách B: mỗi CLB một biểu mẫu (tệp xuất riêng, BaiThi.csv giả, đối chiếu --bai-thi)")
    a = ap.parse_args(argv)
    try:
        kq = chay_demo(a.ra, so_hs=a.so_hs, seed=a.seed, he_so_cho=a.he_so_cho, moi_clb=a.moi_clb,
                      day_du=a.day_du)
    except (bm.LoiDeThi, cv.LoiTepXuat, RuntimeError, ValueError) as e:
        print("DEMO DỪNG — %s" % e, file=sys.stderr)
        return 1
    in_tom_tat(kq)
    return 0


if __name__ == "__main__":
    sys.exit(main())
