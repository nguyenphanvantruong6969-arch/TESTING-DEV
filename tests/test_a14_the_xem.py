"""A14 phần B — dữ liệu cho hai thẻ XEM (06 Thành viên CLB, 07 Theo lớp). Dữ liệu MÔ PHỎNG.

Backend: `get_thoi_khoa_bieu(search, class_id)` (None = cũ, "" = chưa có lớp, buoi theo NGÀY, không
theo vần) và `get_danh_sach_clb` có `class_id`. Chỉ kết quả xếp: không cột điểm / bốc thăm."""

import pytest
from _wharton import tat_wharton


@pytest.fixture
def api(api):
    tat_wharton(api)
    return api


def _dat_lop(api, sid, lop):
    with api._ket_noi_ghi() as cur:
        cur.execute("UPDATE students SET class_id = ? WHERE student_id = ?", (lop or None, sid))


@pytest.fixture
def api_tuan(api):
    """Ba buổi đặt tên "2", "3", "10": theo vần là 10, 2, 3; theo thứ tự (số) là 2, 3, 10."""
    for b in ("10", "3", "2"):
        api.create_or_update_club("a_" + b, "CLB A " + b, 5, 0, "", buoi=b)
    cot = "student_id,name,2_pref_1,3_pref_1,10_pref_1\n"
    dong = "".join("HS00%d,Em %d,a_2,a_3,a_10\n" % (i, i) for i in range(1, 5))
    r = api.import_preferences_csv(cot + dong)
    assert r["ok"], r["errors"]
    for sid, lop in (("HS001", "10A2"), ("HS002", "10A10"), ("HS003", "10A2")):
        _dat_lop(api, sid, lop)
    assert api.run_pipeline(seed=3)["ok"]
    return api


def test_tkb_buoi_theo_ngay_khong_theo_van(api_tuan):
    d = api_tuan.get_thoi_khoa_bieu()["data"]
    assert d["ds_buoi"] == ["2", "3", "10"]


def test_tkb_none_la_hanh_vi_cu_va_moi_dong_co_class_id(api_tuan):
    d = api_tuan.get_thoi_khoa_bieu()["data"]
    assert [e["student_id"] for e in d["hoc_sinh"]] == ["HS001", "HS002", "HS003", "HS004"]
    assert {e["student_id"]: e["class_id"] for e in d["hoc_sinh"]} == {
        "HS001": "10A2", "HS002": "10A10", "HS003": "10A2", "HS004": None}
    assert d == api_tuan.get_thoi_khoa_bieu("", None)["data"]


def test_tkb_loc_lop_va_chua_co_lop(api_tuan):
    ds = lambda lop: [e["student_id"] for e in api_tuan.get_thoi_khoa_bieu("", lop)["data"]["hoc_sinh"]]  # noqa: E731
    assert ds("10A2") == ["HS001", "HS003"]
    assert ds(" 10a2 ") == ["HS001", "HS003"]          # chuẩn hoá như nơi khác
    assert ds("") == ["HS004"]
    assert ds("99Z") == []


def test_tkb_loc_lop_ket_hop_tim_kiem(api_tuan):
    d = api_tuan.get_thoi_khoa_bieu("Em 3", "10A2")["data"]
    assert [e["student_id"] for e in d["hoc_sinh"]] == ["HS003"]


def test_tkb_moi_em_chi_co_ket_qua_khong_diem(api_tuan):
    e = api_tuan.get_thoi_khoa_bieu()["data"]["hoc_sinh"][0]
    o = e["theo_buoi"]["2"]
    assert set(o) == {"club_id", "club_name", "matched_tier", "rank_in_student_pref"}
    assert "stb" not in e and "score" not in e


def test_danh_sach_clb_co_class_id_moi_thanh_vien(api_tuan):
    d = api_tuan.get_danh_sach_clb("a_2")["data"]
    assert {t["student_id"]: t["class_id"] for t in d["thanh_vien"]}["HS001"] == "10A2"
    assert all("class_id" in t for t in d["thanh_vien"])
    assert d["capacity"] == 5


def test_tkb_chua_chay_xep_khong_co_em(api):
    api.create_or_update_club("a", "CLB A", 1, 0, "")
    assert api.get_thoi_khoa_bieu()["data"]["hoc_sinh"] == []
