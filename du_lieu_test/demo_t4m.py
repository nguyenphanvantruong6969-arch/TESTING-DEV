# -*- coding: utf-8 -*-
"""T4M-DEMO: chạy thử TRỌN CHUỖI bằng một lệnh, hoàn toàn ngoại tuyến, để cho giáo viên ECA xem.

    python du_lieu_test/demo_t4m.py --ra ./demo_ra
    python du_lieu_test/demo_t4m.py --ra ./demo_ra --so-hs 200 --seed 7

Các bước (đúng đường phần mềm dùng thật, không đụng app.db của workspace nào):
  1. sinh tệp Lists giả (nguyện vọng; mã CLB lấy từ de_thi.json)      -> lists_gia.csv
  2. sinh tệp Forms chỉ-thi giả (Email + câu hỏi + Points)            -> forms_chi_thi_gia.xlsx
  3. bộ chuyển đổi --chi-thi                                          -> SO_NHAP_CLB.xlsx, BANG_DIEM.xlsx
  4. nạp Sổ nhập vào CSDL TẠM và chạy pipeline (PipelineAPI.import_so_nhap, run_pipeline)
  5. xuất Excel theo lớp chủ nhiệm (export_theo_lop)                  -> ket_qua_theo_lop/
  6. in tóm tắt tiếng Việt

DỮ LIỆU MÔ PHỎNG: tên, email (miền example.test), lớp, điểm đều bịa; không phải khảo sát thật.
Cùng --seed cho cùng kết quả. Thư mục `ket_qua_theo_lop` cũ trong --ra (của lần chạy trước) bị thay.
"""

import argparse
import base64
import copy
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


def sinh_lists(de, duong, so_hs=SO_HS_MAC_DINH, seed=SEED_MAC_DINH):
    """Tệp Lists giả dùng đúng mã CLB của `de` (mỗi ngày trong Lists = một buổi của de_thi.json)."""
    theo_ngay = {}
    for ngay in lists_gia.NGAY:
        buoi = cv._ma_buoi_tu_thu(de, ngay)
        theo_ngay[ngay] = [c["club_id"] for c in de["cau_lac_bo"] if c["buoi"] == buoi]
        if not theo_ngay[ngay]:
            raise ValueError("de_thi.json không có CLB nào ở %s" % ngay)
    return lists_gia.ghi_csv(duong, so_hs=so_hs, seed=seed, clb_theo_ngay=theo_ngay)


def he_so_cho_tu_dong(de, so_hs):
    """Chỉ tiêu mẫu trong de_thi.json (~42 chỗ/buổi) chỉ đủ cho ~50 em; nhân lên để mỗi buổi có chỗ
    cho khoảng 70% số em (còn cạnh tranh để thấy Tầng 1 có tác dụng), không nhỏ hơn 1."""
    theo_buoi = {}
    for c in de["cau_lac_bo"]:
        theo_buoi[c["buoi"]] = theo_buoi.get(c["buoi"], 0) + c["capacity"]
    tb = sum(theo_buoi.values()) / len(theo_buoi)
    return max(1.0, round(0.7 * so_hs / tb, 1))


def chay_demo(ra, so_hs=SO_HS_MAC_DINH, seed=SEED_MAC_DINH, he_so_cho=None):
    """Chạy trọn chuỗi vào thư mục `ra`. Trả tóm tắt (dict) để in hoặc kiểm.

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
    sinh_lists(de, duong_lists, so_hs, seed)
    danh_sach, canh_bao_lists = cv.doc_lists(duong_lists, de)
    gai = tm.ghi_mau_xuat_chi_thi(de, duong_forms, danh_sach, hat_giong=seed)
    kq_cv = cv.chuyen_chi_thi([duong_forms], duong_lists, ra, de)
    duong_so = os.path.join(ra, cv.TEN_SO)
    thu_muc_lop = os.path.join(ra, "ket_qua_theo_lop")
    if os.path.isdir(thu_muc_lop):
        shutil.rmtree(thu_muc_lop)

    with tempfile.TemporaryDirectory(prefix="demo_t4m_") as tam:
        duong_db = os.path.join(tam, "app.db")
        api = PipelineAPI(duong_db)
        # Dữ liệu demo không có điểm quyết tâm (mặc định BẬT): tắt trong CSDL TẠM, như người quản trị
        # tắt ở Cài đặt workspace.
        ch.ghi_cau_hinh(duong_db, {"rules": {"wharton": False}})
        with open(duong_so, "rb") as f:
            r = api.import_so_nhap(base64.b64encode(f.read()).decode())
        if not r["ok"]:
            raise RuntimeError("nạp Sổ nhập thất bại: %s" % r["errors"])
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

    return {"n_hoc_sinh": n_hs, "n_luot": n_luot, "he_so_cho": he_so_cho,
            "n_dat_nv": sum(1 for x in ket_qua if x[5] is not None),
            "n_nv1": sum(1 for x in ket_qua if x[5] == 1), "n_clb": n_clb, "n_tang1": n_tang1,
            "n_bai_thi": kq_cv["n_bai_thi"], "n_tep_lop": n_tep_lop,
            "canh_bao": canh_bao_lists + kq_cv["canh_bao"], "gai": gai, "ket_qua": ket_qua,
            "ra": ra}


def in_tom_tat(kq, out=None):
    out = out or sys.stdout
    p = lambda s="": print(s, file=out)   # noqa: E731
    p("=== CHẠY THỬ TRỌN CHUỖI (dữ liệu MÔ PHỎNG) ===")
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
    p("Tệp ra: lists_gia.csv, forms_chi_thi_gia.xlsx, SO_NHAP_CLB.xlsx, BANG_DIEM.xlsx, ket_qua_theo_lop/")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Chạy thử trọn chuỗi: Lists + Forms giả -> Sổ nhập -> xếp CLB -> Excel theo lớp.")
    ap.add_argument("--ra", required=True, help="thư mục ghi các tệp kết quả")
    ap.add_argument("--so-hs", type=int, default=SO_HS_MAC_DINH, help="số học sinh giả (mặc định %(default)s)")
    ap.add_argument("--seed", type=int, default=SEED_MAC_DINH, help="hạt giống (mặc định %(default)s)")
    ap.add_argument("--he-so-cho", type=float, default=None,
                    help="nhân chỉ tiêu mỗi CLB (mặc định: tự tính theo số học sinh; 1 = giữ nguyên de_thi.json)")
    a = ap.parse_args(argv)
    try:
        kq = chay_demo(a.ra, so_hs=a.so_hs, seed=a.seed, he_so_cho=a.he_so_cho)
    except (bm.LoiDeThi, cv.LoiTepXuat, RuntimeError, ValueError) as e:
        print("DEMO DỪNG — %s" % e, file=sys.stderr)
        return 1
    in_tom_tat(kq)
    return 0


if __name__ == "__main__":
    sys.exit(main())
