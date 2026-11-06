# -*- coding: utf-8 -*-
"""T4M-DO: đo MÔ PHỎNG — có bài thi tuyển (Tầng 1) và không có, trên dữ liệu giả của chuỗi T4M.

    python du_lieu_test/do_t4m_thi.py                 # đủ lưới 3 bộ x 20 seed x 2 điều kiện
    python du_lieu_test/do_t4m_thi.py --nhanh         # lưới nhỏ cho test (2 bộ nhỏ x 2 seed)
    python du_lieu_test/do_t4m_thi.py --ra DIR --tai-lieu TEP.md

Ba bộ dữ liệu giả (120 / 500 / 1.500 học sinh; hạt giống sinh cố định), mỗi bộ chạy với 20 hạt giống bốc
thăm STB, mỗi hạt giống hai điều kiện:
  A. không bài thi: mọi CLB xếp Tầng 2 (bỏ điểm thi khỏi đầu vào; danh sách dự tuyển giữ nguyên);
  B. có bài thi như de_thi.json: CLB có đề thi xếp Tầng 1 (-điểm rồi STB), còn lại Tầng 2.

Đường chạy là đường của phần mềm: Sổ nhập (bộ chuyển đổi --chi-thi) -> CSDL tạm -> dữ liệu đọc MỘT lần ->
với mỗi hạt giống: generate_stb_lottery + run_rbda_nhieu_buoi (cùng tham số như api.run_pipeline) +
verify_stability_tuan. Không ghi gì vào CSDL giữa các lần (không đụng stb_lock). Không sửa mã sản phẩm.

DỮ LIỆU MÔ PHỎNG: tên, email, lớp, điểm đều bịa; không phải khảo sát thật. Tệp này chỉ in bảng số.
"""

import argparse
import base64
import copy
import csv
import os
import statistics
import sys
import tempfile
import time

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (GOC, os.path.join(GOC, "mau_forms_thi_clb"), os.path.dirname(os.path.abspath(__file__))):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import bieu_mau as bm  # noqa: E402
import chuyen_forms_sang_phan_mem as cv  # noqa: E402
import demo_t4m  # noqa: E402
import rbda_priority_pipeline as loi  # noqa: E402
import tao_mau_forms as tm  # noqa: E402

# (nhãn, số học sinh, hạt giống sinh dữ liệu) — cố định.
BO_DU_LIEU = [
    ("120 hs", 120, 20261101),
    ("500 hs", 500, 20261102),
    ("1500 hs", 1500, 20261103),
]
BO_NHANH = [("40 hs", 40, 20261104), ("60 hs", 60, 20261105)]
SO_SEED = 20
SEED_BAT_DAU = 1                     # các hạt giống STB: 1..20
DIEU_KIEN = ("A", "B")
MO_TA_DK = {"A": "A. không bài thi (mọi CLB Tầng 2)", "B": "B. có bài thi theo de_thi.json (CLB có đề = Tầng 1)"}
THU_MUC_RA = os.path.join(GOC, "du_lieu_test", "ket_qua_t4m")
TEP_TAI_LIEU = os.path.join(GOC, "docs", "he_sinh_thai", "T4M_DO_MO_PHONG.md")
CHI_SO = [
    ("nv1", "Tỉ lệ xếp vào nguyện vọng 1 (% lượt em x buổi có đăng ký)"),
    ("nv3", "Tỉ lệ xếp vào top-3 nguyện vọng (%)"),
    ("khong_xep", "Số em có đăng ký mà chưa có CLB, trung bình mỗi buổi (em)"),
    ("tang1_top", "Tỉ lệ suất Tầng 1 về em thuộc nhóm điểm cao nhất CLB (%)"),
    ("cap_pha_vo", "Số cặp phá vỡ (verify_stability_tuan)"),
    ("giay", "Thời gian chạy một lần (giây)"),
]


# ---------------------------------------------------------------- dựng dữ liệu

def dung_bo(so_hs, hat_sinh, thu_muc, he_so_cho=None):
    """Dựng một bộ dữ liệu giả bằng đúng chuỗi T4M, nạp vào CSDL tạm, đọc dữ liệu MỘT lần.

    Trả dict: du_lieu (6 phần như load_from_sqlite), luat, db (đường dẫn), he_so_cho."""
    import cau_hinh_ws as ch
    from api import PipelineAPI

    de = bm.doc_de_thi()
    if he_so_cho is None:
        he_so_cho = demo_t4m.he_so_cho_tu_dong(de, so_hs)
    de = copy.deepcopy(de)
    for c in de["cau_lac_bo"]:
        c["capacity"] = max(1, round(c["capacity"] * he_so_cho))
    ra = os.path.join(thu_muc, "nguon")
    os.makedirs(ra, exist_ok=True)
    duong_lists = os.path.join(ra, "lists_gia.csv")
    duong_forms = os.path.join(ra, "forms_chi_thi_gia.xlsx")
    demo_t4m.sinh_lists(de, duong_lists, so_hs, hat_sinh)
    danh_sach, _cb = cv.doc_lists(duong_lists, de)
    tm.ghi_mau_xuat_chi_thi(de, duong_forms, danh_sach, hat_giong=hat_sinh)
    cv.chuyen_chi_thi([duong_forms], duong_lists, ra, de)
    duong_db = os.path.join(thu_muc, "app.db")
    api = PipelineAPI(duong_db)
    ch.ghi_cau_hinh(duong_db, {"rules": {"wharton": False}})
    with open(os.path.join(ra, cv.TEN_SO), "rb") as f:
        r = api.import_so_nhap(base64.b64encode(f.read()).decode())
    if not r["ok"]:
        raise RuntimeError("nạp Sổ nhập thất bại: %s" % r["errors"])
    luat = api._luat_nghiem()
    du_lieu, _dvt = loi.load_from_sqlite_kem_dau_van_tay(duong_db, luat)
    return {"du_lieu": du_lieu, "luat": luat, "db": duong_db, "he_so_cho": he_so_cho,
            "api": api}


# ---------------------------------------------------------------- một lần chạy

def _dau_vao(du_lieu, dk):
    students, clubs, diem, ung_vien, nguyen_vong, _stb = du_lieu
    if dk == "A":
        # Giữ danh sách dự tuyển (mọi em đã đăng ký CLB đều nằm trong đó, Tầng 2 cũng vậy); chỉ bỏ điểm thi.
        return students, clubs, {}, ung_vien, nguyen_vong
    return students, clubs, diem, ung_vien, nguyen_vong


def chay_mot_lan(bo, dk, seed):
    """Một lần chạy cả tuần. Trả (KetQuaTuan, số cặp phá vỡ, giây). Cùng tham số như api.run_pipeline."""
    students, clubs, diem, ung_vien, nguyen_vong = _dau_vao(bo["du_lieu"], dk)
    t0 = time.perf_counter()
    stb = loi.generate_stb_lottery(list(students.keys()), seed=seed)
    du_tru_fn = loi.default_reserve_eligible_fn(students, clubs)
    tham_so = loi.tham_so_luat(bo["luat"], students)
    kq = loi.run_rbda_nhieu_buoi(
        students, clubs, diem, ung_vien, nguyen_vong, stb, is_reserve_eligible_fn=du_tru_fn,
        che_do_boc_tham=loi.CHE_DO_BOC_THAM_MAC_DINH, seed=seed,
        tier_rank=tham_so["tier_rank"], bo_qua_du_tru=tham_so["bo_qua_du_tru"])
    van_de = loi.verify_stability_tuan(kq, clubs, nguyen_vong, du_tru_fn,
                                       bo_qua_du_tru=tham_so["bo_qua_du_tru"])
    giay = time.perf_counter() - t0
    return kq, sum(len(v) for v in van_de.values()), giay


def _nhom_diem_cao(diem_clb, suc_chua):
    """Tập em thuộc nhóm điểm cao nhất của một CLB: điểm >= điểm của người thứ `suc_chua` (hoà điểm tính hết)."""
    if not diem_clb:
        return set()
    xep = sorted(diem_clb.values(), reverse=True)
    nguong = xep[min(suc_chua, len(xep)) - 1]
    return {sid for sid, d in diem_clb.items() if d >= nguong}


def do_chi_so(bo, dk, kq, so_cap_pha_vo, giay):
    """Các chỉ số của MỘT lần chạy (dict)."""
    students, clubs, diem, _uv, nguyen_vong = _dau_vao(bo["du_lieu"], dk)
    # Tỉ lệ nguyện vọng: mẫu số = lượt (em, buổi) mà em có ít nhất một nguyện vọng trong buổi đó.
    clb_buoi = {cid: (c.get("buoi") or loi.BUOI_MAC_DINH) for cid, c in clubs.items()}
    luot, nv1, nv3, khong_xep = 0, 0, 0, 0
    for buoi, k in kq.per_buoi.items():
        co_nv = {sid for sid, ds in nguyen_vong.items() if any(clb_buoi.get(c) == buoi for c in ds)}
        luot += len(co_nv)
        for sid in co_nv:
            h = k.rank_in_student_pref.get(sid)
            if h == 1:
                nv1 += 1
            if h is not None and h <= 3:
                nv3 += 1
        khong_xep += sum(1 for sid in co_nv if k.assignment.get(sid) is None)
    # Suất Tầng 1: em được xếp vào CLB mà em có điểm thi.
    tong_t1, top_t1 = 0, 0
    if dk == "B":
        for k in kq.per_buoi.values():
            for sid, cid in k.assignment.items():
                if cid is not None and sid in diem.get(cid, {}):
                    tong_t1 += 1
                    if sid in _nhom_diem_cao(diem[cid], clubs[cid]["capacity"]):
                        top_t1 += 1
    n_buoi = max(1, len(kq.per_buoi))
    return {
        "nv1": 100.0 * nv1 / luot if luot else 0.0,
        "nv3": 100.0 * nv3 / luot if luot else 0.0,
        "khong_xep": khong_xep / n_buoi,
        "tang1_top": (100.0 * top_t1 / tong_t1) if tong_t1 else None,
        "n_t1": tong_t1,
        "cap_pha_vo": so_cap_pha_vo,
        "giay": giay,
    }


def so_em_chua_xep_theo_buoi(bo, dk, kq):
    """{buổi: số em có nguyện vọng trong buổi đó mà chưa có CLB}."""
    _s, clubs, _d, _u, nguyen_vong = _dau_vao(bo["du_lieu"], dk)
    ra = {}
    for b, k in kq.per_buoi.items():
        co_nv = {sid for sid, ds in nguyen_vong.items()
                 if any((clubs[c].get("buoi") or loi.BUOI_MAC_DINH) == b for c in ds if c in clubs)}
        ra[b] = sum(1 for sid in co_nv if k.assignment.get(sid) is None)
    return ra


# ---------------------------------------------------------------- chạy cả lưới

def chay_luoi(bo_du_lieu=None, so_seed=SO_SEED, log=None):
    """Trả (dòng_từng_lần, dòng_theo_buổi, thông_tin_bộ). Mỗi dòng là dict, thứ tự xác định."""
    bo_du_lieu = BO_DU_LIEU if bo_du_lieu is None else bo_du_lieu
    dong, theo_buoi, thong_tin = [], [], []
    for nhan, so_hs, hat_sinh in bo_du_lieu:
        with tempfile.TemporaryDirectory(prefix="do_t4m_") as tam:
            bo = dung_bo(so_hs, hat_sinh, tam)
            students, clubs, diem, uv, nv, _s = bo["du_lieu"]
            thong_tin.append({
                "bo": nhan, "so_hs": so_hs, "hat_sinh": hat_sinh, "he_so_cho": bo["he_so_cho"],
                "n_clb": len(clubs), "n_clb_thi": sum(1 for m in diem.values() if m),
                "suc_chua_buoi": round(sum(c["capacity"] for c in clubs.values())
                                       / len({c.get("buoi") for c in clubs.values()})),
                "n_luot_dk": sum(1 for sid in nv for _ in {clubs[c].get("buoi") for c in nv[sid]
                                                             if c in clubs}),
            })
            if log:
                log("bộ %s dựng xong (%d CLB, %d CLB có thi)" % (nhan, len(clubs), len(diem)))
            for dk in DIEU_KIEN:
                for i in range(so_seed):
                    seed = SEED_BAT_DAU + i
                    kq, pha_vo, giay = chay_mot_lan(bo, dk, seed)
                    cs = do_chi_so(bo, dk, kq, pha_vo, giay)
                    cs.update({"bo": nhan, "dieu_kien": dk, "seed": seed})
                    dong.append(cs)
                    for b, n in so_em_chua_xep_theo_buoi(bo, dk, kq).items():
                        theo_buoi.append({"bo": nhan, "dieu_kien": dk, "seed": seed, "buoi": b,
                                          "chua_xep": n})
                if log:
                    log("  điều kiện %s xong (%d seed)" % (dk, so_seed))
    return dong, theo_buoi, thong_tin


# ---------------------------------------------------------------- ghi kết quả

def _tom(giatri):
    gt = [x for x in giatri if x is not None]
    if not gt:
        return None
    return (statistics.mean(gt), min(gt), max(gt))


def _o(t, dp=2):
    return "—" if t is None else "%s / %s / %s" % tuple(("%." + str(dp) + "f") % x for x in t)


def ghi_csv(dong, theo_buoi, thu_muc):
    os.makedirs(thu_muc, exist_ok=True)
    tep1 = os.path.join(thu_muc, "t4m_tung_lan.csv")
    cot = ["bo", "dieu_kien", "seed", "nv1", "nv3", "khong_xep", "tang1_top", "n_t1", "cap_pha_vo", "giay"]
    with open(tep1, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cot, lineterminator="\n")
        w.writeheader()
        for d in dong:
            w.writerow({k: ("" if d[k] is None else (round(d[k], 6) if isinstance(d[k], float) else d[k]))
                        for k in cot})
    tep2 = os.path.join(thu_muc, "t4m_theo_buoi.csv")
    with open(tep2, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["bo", "dieu_kien", "seed", "buoi", "chua_xep"], lineterminator="\n")
        w.writeheader()
        w.writerows(theo_buoi)
    return [tep1, tep2]


def bang_markdown(dong, theo_buoi, thong_tin, so_seed, lenh, giay_tong=None):
    """Nội dung T4M_DO_MO_PHONG.md: phương pháp, tham số, bảng, lệnh tái lập. KHÔNG có nhận xét."""
    L = []
    p = L.append
    p("# T4M — Đo mô phỏng: có và không có bài thi tuyển")
    p("")
    p("> **MÔ PHỎNG.** Mọi con số dưới đây do dữ liệu bịa sinh ra; không phải khảo sát thật. "
      "Tệp này chỉ gồm phương pháp và bảng số (mã việc T4M-DO). Nhận xét và kết luận do học sinh tự viết.")
    p("")
    p("## 1. Phương pháp")
    p("")
    p("- Dữ liệu: chuỗi T4M ngoại tuyến (`demo_t4m.sinh_lists` -> `tao_mau_forms.ghi_mau_xuat_chi_thi` -> "
      "`chuyen_chi_thi` -> `import_so_nhap`), 15 CLB (3 mỗi buổi, 5 buổi) theo `de_thi.json`, trong đó 10 CLB có đề thi (Tầng 1 ở điều kiện B); chỉ tiêu mỗi CLB nhân hệ số "
      "ở bảng 2 (cách tính của `demo_t4m.he_so_cho_tu_dong`).")
    p("- Mỗi bộ dữ liệu x %d hạt giống STB (1..%d) x 2 điều kiện. Dữ liệu đọc MỘT lần; mỗi lần chạy sinh lại "
      "`generate_stb_lottery`, gọi `run_rbda_nhieu_buoi` (tham số như `api.run_pipeline`) rồi "
      "`verify_stability_tuan`." % (so_seed, SEED_BAT_DAU + so_seed - 1))
    for k in DIEU_KIEN:
        p("- Điều kiện %s" % MO_TA_DK[k])
    p("- Chỉ số (trung bình / nhỏ nhất / lớn nhất trên %d hạt giống):" % so_seed)
    p("  - Tỉ lệ nguyện vọng 1 và top-3: mẫu số = số lượt (em, buổi) mà em có ít nhất một nguyện vọng trong buổi đó.")
    p("  - Số em chưa có CLB: số em có ít nhất một nguyện vọng trong buổi mà kết quả buổi đó rỗng, trung bình qua các buổi; theo từng buổi ở bảng cuối.")
    p("  - Suất Tầng 1 về nhóm điểm cao nhất: trong các suất mà em được xếp vào CLB em có điểm thi, "
      "tỉ lệ em có điểm >= điểm của người thứ `chỉ tiêu` trong số em có điểm của CLB đó (hoà điểm tính hết). "
      "Chỉ có ở điều kiện B.")
    p("  - Cặp phá vỡ: tổng số vấn đề `verify_stability_tuan` trả về (phải bằng 0).")
    p("  - Thời gian: giây cho STB + xếp + kiểm ổn định của một lần chạy.")
    p("")
    p("## 2. Tham số các bộ dữ liệu (MÔ PHỎNG)")
    p("")
    p("| Bộ | Số học sinh | Hạt giống sinh dữ liệu | Hệ số chỉ tiêu | Số CLB | Số CLB có đề thi | Chỉ tiêu TB mỗi buổi |")
    p("|---|---|---|---|---|---|---|")
    for t in thong_tin:
        p("| %s | %d | %d | %g | %d | %d | %d |" % (t["bo"], t["so_hs"], t["hat_sinh"], t["he_so_cho"],
                                                    t["n_clb"], t["n_clb_thi"], t["suc_chua_buoi"]))
    p("")
    n = 2
    for cs, ten in CHI_SO:
        n += 1
        p("## %d. %s — MÔ PHỎNG" % (n, ten))
        p("")
        p("Ô: trung bình / nhỏ nhất / lớn nhất (%d hạt giống).%s" % (
            so_seed, " Chỉ điều kiện B có suất Tầng 1." if cs == "tang1_top" else ""))
        p("")
        p("| Bộ | Điều kiện A | Điều kiện B |")
        p("|---|---|---|")
        for t in thong_tin:
            o = []
            for dk in DIEU_KIEN:
                gt = [d[cs] for d in dong if d["bo"] == t["bo"] and d["dieu_kien"] == dk]
                dp = 4 if cs == "giay" else (0 if cs == "cap_pha_vo" else 2)
                o.append(_o(_tom(gt), dp))
            p("| %s | %s | %s |" % (t["bo"], o[0], o[1]))
        p("")
    n += 1
    p("## %d. Số em có đăng ký mà chưa có CLB, theo buổi — MÔ PHỎNG" % n)
    p("")
    p("Ô: trung bình / nhỏ nhất / lớn nhất (%d hạt giống), đơn vị em." % so_seed)
    p("")
    p("| Bộ | Điều kiện | " + " | ".join(sorted({d["buoi"] for d in theo_buoi})) + " |")
    ds_buoi = sorted({d["buoi"] for d in theo_buoi})
    p("|---|---|" + "---|" * len(ds_buoi))
    for t in thong_tin:
        for dk in DIEU_KIEN:
            o = []
            for b in ds_buoi:
                gt = [d["chua_xep"] for d in theo_buoi
                      if d["bo"] == t["bo"] and d["dieu_kien"] == dk and d["buoi"] == b]
                o.append(_o(_tom(gt), 1))
            p("| %s | %s | %s |" % (t["bo"], dk, " | ".join(o)))
    p("")
    n += 1
    p("## %d. Số suất Tầng 1 đã xếp (điều kiện B) — MÔ PHỎNG" % n)
    p("")
    p("| Bộ | Số suất Tầng 1 (trung bình / nhỏ nhất / lớn nhất) |")
    p("|---|---|")
    for t in thong_tin:
        gt = [d["n_t1"] for d in dong if d["bo"] == t["bo"] and d["dieu_kien"] == "B"]
        p("| %s | %s |" % (t["bo"], _o(_tom(gt), 1)))
    p("")
    p("## Tái lập")
    p("")
    p("```")
    p(lenh)
    p("```")
    p("")
    p("Tệp số liệu từng lần chạy: `du_lieu_test/ket_qua_t4m/t4m_tung_lan.csv`, `t4m_theo_buoi.csv`.")
    if giay_tong is not None:
        p("")
        p("Thời gian chạy cả lưới trên máy đo: %.0f giây (%.1f phút)." % (giay_tong, giay_tong / 60))
    p("")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description="T4M-DO: đo mô phỏng có/không bài thi tuyển (chỉ bảng số).")
    ap.add_argument("--nhanh", action="store_true", help="lưới nhỏ (2 bộ nhỏ x 2 seed) cho test; không ghi tài liệu mặc định")
    ap.add_argument("--so-seed", type=int, default=None, help="số hạt giống (mặc định %d; --nhanh: 2)" % SO_SEED)
    ap.add_argument("--ra", default=None, help="thư mục CSV (mặc định du_lieu_test/ket_qua_t4m)")
    ap.add_argument("--tai-lieu", default=None, help="tệp .md (mặc định docs/he_sinh_thai/T4M_DO_MO_PHONG.md)")
    a = ap.parse_args(argv)
    if a.nhanh:
        bo, so_seed = BO_NHANH, (a.so_seed or 2)
        if a.ra is None or a.tai_lieu is None:
            print("--nhanh cần --ra và --tai-lieu (không ghi đè kết quả đủ lưới).", file=sys.stderr)
            return 2
    else:
        bo, so_seed = BO_DU_LIEU, (a.so_seed or SO_SEED)
    ra = a.ra or THU_MUC_RA
    tai_lieu = a.tai_lieu or TEP_TAI_LIEU
    t0 = time.perf_counter()
    dong, theo_buoi, thong_tin = chay_luoi(bo, so_seed, log=lambda s: print(s, flush=True))
    giay_tong = time.perf_counter() - t0
    ghi_csv(dong, theo_buoi, ra)
    lenh = "python du_lieu_test/do_t4m_thi.py" + (" --nhanh --so-seed %d" % so_seed if a.nhanh else "")
    if a.nhanh:
        lenh += " --ra DIR --tai-lieu TEP.md"
    os.makedirs(os.path.dirname(os.path.abspath(tai_lieu)), exist_ok=True)
    with open(tai_lieu, "w", encoding="utf-8", newline="\n") as f:
        f.write(bang_markdown(dong, theo_buoi, thong_tin, so_seed, lenh, giay_tong))
    print("Xong: %d lần chạy, %.0f giây. CSV: %s ; bảng: %s" % (len(dong), giay_tong, ra, tai_lieu))
    return 0


if __name__ == "__main__":
    sys.exit(main())
