"""GAP-3 (Playwright + Chromium): khung khiếu nại ở thẻ "Chi tiết và xuất tệp".

  * cờ `fa_khieu_nai` tắt: không có khung;
  * bật: gửi một khiếu nại từ biểu mẫu -> dòng "Đang chờ xử lý"; bấm "Chấp nhận" -> "Đã chấp nhận";
  * trình hướng dẫn có ô `#wzFaKhieuNai`.
Dữ liệu MÔ PHỎNG.
"""
import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_fa_gap3_khieu_nai import _dung  # noqa: E402
from test_giao_dien_fa_gap1_theo_doi import mo  # noqa: E402,F401 (fixture)
from test_ws_wharton_giao_dien import _cho_ten, _toi_buoc_luat  # noqa: E402
from test_ws_wharton_giao_dien import mo_trang  # noqa: E402,F401 (fixture)


def _tat(api):
    _dung(api, kn=False)


def test_co_tat_khong_co_khung(mo):  # noqa: F811
    page, _, loi = mo(_tat)
    page.wait_for_timeout(300)
    assert page.locator("#khieuNaiPanel[hidden]").count() == 1
    assert not loi, loi


def test_gui_roi_chap_nhan(mo):  # noqa: F811
    page, api, loi = mo(_dung)
    page.wait_for_selector("#khieuNaiPanel:not([hidden])")
    page.fill("#knMa", "s1")
    page.fill("#knGhiChu", "Điểm thi nhập sai")
    page.locator("#btnGuiKhieuNai").click()
    page.wait_for_function("() => document.getElementById('knDanhSach').textContent.includes('Đang chờ xử lý')")
    assert "Điểm thi nhập sai" in page.locator("#knDanhSach").inner_text()
    page.locator('#knDanhSach button.kn-xu-ly[data-chap-nhan="1"]').click()
    page.wait_for_function("() => document.getElementById('knDanhSach').textContent.includes('Đã chấp nhận')")
    assert page.locator("#knDanhSach button.kn-xu-ly").count() == 0
    assert api.get_khieu_nai()["data"]["khieu_nai"][0]["trang_thai"] == "CHAP_NHAN"
    assert not loi, loi


def test_gui_sai_ma_hien_loi(mo):  # noqa: F811
    page, _, loi = mo(_dung)
    page.wait_for_selector("#khieuNaiPanel:not([hidden])")
    page.fill("#knMa", "khong_co")
    page.locator("#btnGuiKhieuNai").click()
    page.wait_for_selector(".toast.is-error")
    assert "khong_co" in page.locator(".toast.is-error").first.inner_text()
    assert not loi, loi


def test_wizard_co_o_khieu_nai(mo_trang):  # noqa: F811
    page, api, loi = mo_trang()
    _toi_buoc_luat(page, "Đợt khiếu nại")
    assert not page.locator("#wzFaKhieuNai").is_checked()
    page.locator("#wzFaDaa").check()
    page.locator("#wzFaKhieuNai").check()
    page.locator("#wzTiep").click()
    assert page.locator("#rvFaKhieuNai").inner_text() == "Bật"
    page.locator("#wzTao").click()
    _cho_ten(page, "Đợt khiếu nại")
    assert api.get_workspace_config()["data"]["config"]["rules"]["fa_khieu_nai"] is True
    assert not loi, loi
