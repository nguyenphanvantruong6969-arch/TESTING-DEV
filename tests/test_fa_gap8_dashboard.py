"""GAP-8 (V§11): bảng điều khiển quản trị — mọi chỉ số §11 có dữ liệu; thiếu dữ liệu ghi "chưa có dữ liệu", không
bịa số. Chỉ đọc. Dữ liệu là dữ liệu MÔ PHỎNG."""
import pytest
from openpyxl import load_workbook

import fa_sau_xep as sx
from _fa import bat_fa, dung_fa_clb, dung_hs_fa, ma

THU_TU = ["khong_co_clb", "ty_le_nv1", "ty_le_top2", "ty_le_boc_tham", "thua_boc_tham_1_lan", "ty_le_dang_ky_3_ngay",
          "ty_le_thu_thach_nghiem_tuc", "do_lech_cham", "ty_le_di_du_3_buoi", "hai_long_tb", "ty_le_hieu_ly_do",
          "ty_le_doi_huy_chuong"]


def _rong():
    return {"vi_tri": {}, "ket_qua": [], "ly_do": [], "diem_danh": [], "phan_hoi": [], "huy_chuong": {},
            "nguyen_vong": {}, "clubs": {}}


def _cs(du):
    return {c["ma"]: c for c in sx.chi_so_dashboard(du)}


def test_thu_tu_va_thieu_du_lieu_la_none_khong_phai_0():
    ds = sx.chi_so_dashboard(_rong())
    assert [c["ma"] for c in ds] == THU_TU
    assert all(set(c) == {"ma", "gia_tri", "muc_tieu", "dat", "nguon"} for c in ds)
    cs = {c["ma"]: c for c in ds}
    for m in THU_TU:                                   # chưa chạy xếp: kể cả "không có CLB" cũng chưa có dữ liệu
        assert cs[m]["gia_tri"] is None and cs[m]["dat"] is None, m
    for m in ("ty_le_dang_ky_3_ngay", "ty_le_thu_thach_nghiem_tuc", "do_lech_cham"):
        assert cs[m]["nguon"] == "ngoai_kiosk"


def test_gia_tri_tinh_tay():
    du = _rong()
    du["vi_tri"] = {("s1", "b1"): "G", ("s2", "b1"): "T", ("s3", "b1"): None, ("s3", "b2"): "X",
                    ("s4", "b1"): "G"}
    du["ket_qua"] = [{"student_id": "s1", "buoi": "b1", "club_id": "G", "rank": 1},
                     {"student_id": "s2", "buoi": "b1", "club_id": "T", "rank": 2},
                     {"student_id": "s3", "buoi": "b1", "club_id": None, "rank": None},
                     {"student_id": "s3", "buoi": "b2", "club_id": "X", "rank": 3},
                     {"student_id": "s4", "buoi": "b1", "club_id": "G", "rank": 1}]
    du["ly_do"] = [{"student_id": "s2", "outcome": "REJECTED", "reason": "LOTTERY"},
                   {"student_id": "s3", "outcome": "REJECTED", "reason": "LOTTERY"},
                   {"student_id": "s3", "outcome": "REJECTED", "reason": "SCORE"},
                   {"student_id": "s2", "outcome": "REJECTED", "reason": "MEDAL"},
                   {"student_id": "s1", "outcome": "ACCEPTED", "reason": "ACCEPTED"},
                   {"student_id": "s3", "outcome": "REMOVED", "reason": "BELOW_PASS"}]
    cs = _cs(du)
    assert cs["khong_co_clb"]["gia_tri"] == 1 and cs["khong_co_clb"]["dat"] is False
    assert cs["ty_le_nv1"]["gia_tri"] == pytest.approx(2 / 4)
    assert cs["ty_le_top2"]["gia_tri"] == pytest.approx(3 / 4)
    assert cs["ty_le_boc_tham"]["gia_tri"] == pytest.approx(2 / 4)
    assert cs["thua_boc_tham_1_lan"]["gia_tri"] == 2


def test_diem_danh_phan_hoi_va_doi_huy_chuong():
    du = _rong()
    dd = []
    for sid, ds in (("s1", ["CO_MAT"] * 3), ("s2", ["CO_MAT", "VANG_CO_PHEP", "CO_MAT"]),
                    ("s3", ["CO_MAT", "CO_MAT"])):                           # s3 chưa đủ 3 buổi: không tính
        dd += [{"club_id": "G", "student_id": sid, "buoi": "b1", "buoi_so": i + 1, "trang_thai": t}
               for i, t in enumerate(ds)]
    du["diem_danh"] = dd
    du["phan_hoi"] = [
        {"id": 1, "student_id": "s1", "loai": "ket_qua", "hai_long": 2, "hieu_ly_do": 0, "kho_nhat": "khong_co",
         "con_di": None, "muon_doi": None},
        {"id": 2, "student_id": "s1", "loai": "ket_qua", "hai_long": 4, "hieu_ly_do": 1, "kho_nhat": "khong_co",
         "con_di": None, "muon_doi": None},
        {"id": 3, "student_id": "s2", "loai": "ket_qua", "hai_long": 3, "hieu_ly_do": 0, "kho_nhat": "huy_chuong",
         "con_di": None, "muon_doi": None}]
    du["clubs"] = {"A": {"buoi": "b1", "loai": "GIOI_HAN"}, "B": {"buoi": "b1", "loai": "TUYEN_CHON"},
                   "F": {"buoi": "b1", "loai": "TU_DO"}, "C": {"buoi": "b1", "loai": "GIOI_HAN"},
                   "D": {"buoi": "b1", "loai": "GIOI_HAN"}}
    du["nguyen_vong"] = {"s1": ["A", "F", "B", "C", "D"], "s2": ["A", "B", "C"], "s3": ["A"]}
    du["huy_chuong"] = {"s1": {"A": 60, "B": 30, "C": 10},                    # đúng mặc định (bỏ qua Tự do)
                        "s2": {"B": 60, "A": 30, "C": 10}}                    # đổi vàng
    cs = _cs(du)
    assert cs["ty_le_di_du_3_buoi"]["gia_tri"] == pytest.approx(0.5) and cs["ty_le_di_du_3_buoi"]["dat"] is False
    assert cs["hai_long_tb"]["gia_tri"] == pytest.approx(3.5) and cs["hai_long_tb"]["dat"] is True
    assert cs["ty_le_hieu_ly_do"]["gia_tri"] == pytest.approx(0.5)
    assert cs["ty_le_doi_huy_chuong"]["gia_tri"] == pytest.approx(0.5)


def _dung(api):
    bat_fa(api)
    dung_fa_clb(api, G=(1, "GIOI_HAN"), T=(9, "TU_DO"))
    dung_hs_fa(api, "s1", "s2", "s3", "s4", nv={s: ["G", "T"] for s in ("s1", "s2", "s3", "s4")})


def test_api_fa_tat_va_chi_doc_lan_chay_goc_moi_nhat(api, tmp_path):
    assert api.get_dashboard()["data"] == {"bat": False}
    assert ma(api.export_dashboard(str(tmp_path / "x.xlsx"))["errors"]) == ["fa_chua_bat"]
    _dung(api)
    assert api.run_pipeline(seed=3)["ok"]
    cs = {c["ma"]: c for c in api.get_dashboard()["data"]["chi_so"]}
    assert cs["thua_boc_tham_1_lan"]["gia_tri"] == 3 and cs["ty_le_boc_tham"]["gia_tri"] == 1.0
    assert cs["ty_le_nv1"]["gia_tri"] == pytest.approx(1 / 4) and cs["khong_co_clb"]["gia_tri"] == 0
    dung_fa_clb(api, G=(4, "GIOI_HAN"))                                       # đủ chỗ: lần chạy mới không thua ai
    assert api.run_pipeline(seed=3)["ok"]
    cs = {c["ma"]: c for c in api.get_dashboard()["data"]["chi_so"]}
    assert cs["thua_boc_tham_1_lan"]["gia_tri"] == 0 and cs["ty_le_boc_tham"]["gia_tri"] is None
    assert cs["ty_le_nv1"]["gia_tri"] == 1.0


def test_xuat_chua_co_du_lieu_va_khong_co_ma_hoc_sinh(api, tmp_path):
    _dung(api)
    assert api.run_pipeline(seed=3)["ok"]
    kq = api.export_dashboard(str(tmp_path / "db.xlsx"))
    assert kq["ok"], kq
    hang = list(load_workbook(kq["data"]["path"]).active.iter_rows(values_only=True))
    assert hang[0] == ("Chỉ số", "Giá trị", "Mục tiêu", "Đạt", "Nguồn")
    assert len(hang) == 1 + len(THU_TU)
    assert sum(1 for r in hang if r[1] == "chưa có dữ liệu") >= 6
    van = " ".join(str(o) for r in hang for o in r if o is not None)
    assert not any(s in van for s in ("s1", "s2", "s3", "s4"))
