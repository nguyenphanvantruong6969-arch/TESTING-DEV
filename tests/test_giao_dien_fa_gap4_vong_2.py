"""GAP-4 (Playwright + Chromium): khung vòng 2 ở thẻ "Chi tiết và xuất tệp".

  * cờ `fa_vong_2` tắt: không có khung;
  * bật: liệt kê học sinh cần vòng 2; chọn CLB còn chỗ, bấm "Chạy vòng 2" -> báo 1 em được xếp, nút khoá lại.
Dữ liệu MÔ PHỎNG.
"""
import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_fa_gap4_vong_2 import _dung  # noqa: E402
from test_giao_dien_fa_gap1_theo_doi import mo  # noqa: E402,F401 (fixture)


def _tat(api):
    _dung(api, v2=False)


def test_co_tat_khong_co_khung(mo):  # noqa: F811
    page, _, loi = mo(_tat)
    page.wait_for_timeout(300)
    assert page.locator("#vong2Panel[hidden]").count() == 1
    assert not loi, loi


def test_chon_roi_chay_vong_2(mo):  # noqa: F811
    page, api, loi = mo(_dung)
    page.wait_for_selector("#vong2Panel:not([hidden])")
    o = page.locator("#v2Bang select.v2-chon")
    o.first.wait_for()
    assert o.count() == 1
    o.first.select_option("G")
    page.locator("#btnChayVong2").click()
    page.wait_for_function("() => document.getElementById('v2KetQua').textContent.includes('Đã xếp 1')")
    assert page.locator("#btnChayVong2").is_disabled()
    assert api.get_vong_2()["data"]["da_chay"] is True
    assert not loi, loi
