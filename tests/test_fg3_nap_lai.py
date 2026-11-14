"""FG-3 (STEP0, spec §3): nạp lại CÙNG một tệp Forms không thêm gì. Dữ liệu là dữ liệu MÔ PHỎNG; mọi việc Forms là TH.

Khoá kết quả (spec FG-6): `dong_moi`, `dong_trung`, `khieu_nai_moi`, `khieu_nai_trung`, `khieu_nai_loi`.
"""
import datetime

import pytest

from test_fa_m6b_sau_ket_qua import (  # noqa: F401 (fixture)
    _buoi, _dem, _dung, _hs_kn, _run_at, _tep_api, _tl, de, gio,
)


def _nap(api, de_, dong):
    ra = api.nhap_sau_ket_qua_forms(_tep_api(de_, api, dong))
    assert ra["ok"], ra
    return ra["data"]


def test_nap_hai_lan_phan_hoi_khong_them_dong(api, de, gio):  # noqa: F811
    _dung(api)
    gio(api, days=1)
    dong = [_tl(de, "s1", 4, 1, "huy_chuong"), _tl(de, "s2", 2, 0, "khong_co")]
    d1 = _nap(api, de, dong)
    assert _dem(api, "fa_phan_hoi") == 2
    d2 = _nap(api, de, dong)
    assert _dem(api, "fa_phan_hoi") == 2                     # không thêm dòng
    assert d2["dong_trung"] == 2 and d2["dong_moi"] == 0     # báo số dòng trùng
    assert d1["dong_moi"] == 2 and d1["dong_trung"] == 0


def test_nap_hai_lan_khieu_nai_cho_xu_ly_khong_loi(api, de, gio):  # noqa: F811
    _dung(api)
    r0 = _run_at(api)
    gio(api, days=1)
    dong = [_hs_kn(de, api, "s1", luc=r0 + datetime.timedelta(hours=5))]
    _nap(api, de, dong)
    d2 = _nap(api, de, dong)
    assert _dem(api, "fa_khieu_nai") == 1
    assert d2["khieu_nai_loi"] == [] and d2["khieu_nai_trung"] == 1 and d2["khieu_nai_moi"] == 0


@pytest.mark.parametrize("chap_nhan", [True, False])
def test_khieu_nai_da_xu_ly_roi_nap_lai_van_mot_khieu_nai(api, de, gio, chap_nhan):  # noqa: F811
    """Khiếu nại đã CHAP_NHAN/TU_CHOI rồi nạp lại cùng tệp: hiện sinh thêm một khiếu nại CHO mới (lỗi cần sửa)."""
    _dung(api)
    r0 = _run_at(api)
    gio(api, days=1)
    dong = [_hs_kn(de, api, "s1", luc=r0 + datetime.timedelta(hours=5))]
    _nap(api, de, dong)
    kn = api.get_khieu_nai()["data"]["khieu_nai"][0]
    assert api.xu_ly_khieu_nai(kn["id"], chap_nhan)["ok"]
    d2 = _nap(api, de, dong)
    assert _dem(api, "fa_khieu_nai") == 1                    # vẫn đúng một khiếu nại
    assert d2["khieu_nai_loi"] == [] and d2["khieu_nai_trung"] == 1
    assert api.get_khieu_nai()["data"]["khieu_nai"][0]["trang_thai"] == ("CHAP_NHAN" if chap_nhan else "TU_CHOI")


def test_doi_cau_tra_loi_them_mot_dong_va_tong_hop_dung_dong_moi(api, de, gio):  # noqa: F811
    _dung(api)
    gio(api, days=1)
    _nap(api, de, [_tl(de, "s1", 2, 0, "chon_clb")])
    d2 = _nap(api, de, [_tl(de, "s1", 5, 1, "chon_clb")])
    assert _dem(api, "fa_phan_hoi") == 2 and d2["dong_moi"] == 1 and d2["dong_trung"] == 0
    tq = api.get_phan_hoi_tong_hop()["data"]["ket_qua"]
    assert tq["n"] == 1 and tq["hai_long_tb"] == 5
