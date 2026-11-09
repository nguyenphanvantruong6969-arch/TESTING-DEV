"""FA-N4: CLB chỉ có MỘT đề thì em bị gắn cờ làm quá nhanh không thể thi lại (thi lại cần đề khác): bộ chuyển
đổi phải báo "không có đề thi lại", và hướng dẫn `CAI_DAT_FORMS_BIEN_THE.md` nói rõ. Dữ liệu MÔ PHỎNG."""
import copy
import csv
import os
import sys

_MP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mau_forms_thi_clb")
if _MP not in sys.path:
    sys.path.insert(0, _MP)

import bieu_mau as bm  # noqa: E402
import chuyen_forms_sang_phan_mem as cv  # noqa: E402
import so_nhap  # noqa: E402
import tao_mau_forms as tmf  # noqa: E402
from test_fa_m4_phan_tich import _de_bien_the, _tep_thi_gio  # noqa: E402


def _bo(tmp_path, co_hai_de):
    de = _de_bien_the() if co_hai_de else copy.deepcopy(bm.doc_de_thi())
    clb = next(c for c in de["cau_lac_bo"] if c["club_id"] == "clb_covua")
    emails = ["t%d@x.vn" % i for i in range(12)]
    dong = [("t0@x.vn", 1, 60)] + [(e, 4, 600) for e in emails[1:]]
    if co_hai_de:                                   # cùng đề giao cho mọi em: chỉ cần tệp đề A
        import phan_tich_cau_hoi as pt
        dong = [d for d in dong if pt.chon_bien_the(d[0], 2) == 0]
    pa = _tep_thi_gio(tmp_path, clb, dong, "thi_A.xlsx")
    p = tmp_path / "list.csv"
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Email", "HoTen", "Thu", "NV1", "TrangThai"])
        for e in emails:
            w.writerow([e, e, "Thứ 2", "clb_covua", "SUBMITTED"])
    clubs = [{"club_id": c["club_id"], "name": c["name"], "capacity": 40, "reserve_capacity": 0, "reserve_group": "",
              "buoi": c["buoi"], "loai": so_nhap.TU_DO if c["club_id"] == "clb_nhiepanh" else so_nhap.GIOI_HAN}
             for c in de["cau_lac_bo"]]
    sn = str(tmp_path / "clb.xlsx")
    so_nhap.ghi_so_nhap(sn, clubs=clubs)
    return de, str(p), pa, sn


def _chay(tmp_path, co_hai_de):
    de, lists, pa, sn = _bo(tmp_path, co_hai_de)
    return cv.chuyen_fa_daa(str(tmp_path / "ra"), de, sn, lists=lists, quiz_xlsx=[pa],
                            bien_the_tep={"thi_A.xlsx": "A"}, giu_diem_goc=True)


def test_mot_de_bi_co_nhanh_thi_bao_khong_co_de_thi_lai(tmp_path):
    kq = _chay(tmp_path, co_hai_de=False)
    ca_em = [c[2] for c in kq["canh_bao"] if c[1] == "t0@x.vn"]
    assert any("không có đề thi lại" in c for c in ca_em), ca_em
    assert not any("cho thi lại một lần bằng đề khác" in c for c in ca_em)    # không hứa điều không làm được
    assert sum("không có đề thi lại" in c[2] for c in kq["canh_bao"]) == 1


def test_hai_de_bi_co_nhanh_van_noi_thi_lai_nhu_cu(tmp_path):
    kq = _chay(tmp_path, co_hai_de=True)
    ca_em = [c[2] for c in kq["canh_bao"] if c[1] == "t0@x.vn"]
    assert any("cho thi lại một lần bằng đề khác" in c for c in ca_em), ca_em
    assert not any("không có đề thi lại" in c for c in ca_em)


def test_huong_dan_noi_ro_chi_mot_de_thi_khong_thi_lai(tmp_path):
    de = _de_bien_the()
    tmf.sinh_bien_the(de, str(tmp_path))
    md = (tmp_path / tmf.TEN_CAI_DAT_BIEN_THE).read_text(encoding="utf-8")
    assert "chỉ có MỘT đề" in md and "không thi lại được" in md
