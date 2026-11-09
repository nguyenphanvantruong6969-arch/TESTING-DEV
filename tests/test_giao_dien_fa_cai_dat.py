"""FA-UI-1 (Playwright + Chromium): công tắc "Xếp theo loại CLB và huy chương" (`rules.fa_daa`) ở bước luật
của trình hướng dẫn tạo không gian làm việc.

  * ô `#wzFaDaa` tắt sẵn, nhãn tiếng Việt / tiếng Anh, không có chữ "Wharton" hay "FA-DAA";
  * bật rồi tạo -> `rules.fa_daa` lưu true, hàng xem lại `#rvFaDaa` ghi "Bật"; lần sau mở bước luật thì
    vẫn tích (đi về giữ nguyên); tắt -> không có khoá fa_daa = true;
  * bật FA mà tắt điểm quyết tâm -> backend từ chối bằng lỗi sẵn có (`ws_du_lieu_sai`), lỗi hiện trên màn hình.
Dữ liệu MÔ PHỎNG.
"""

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_ws_wharton_giao_dien import _cho_ten, _toi_buoc_luat  # noqa: E402
from test_ws_wharton_giao_dien import mo_trang  # noqa: E402,F401 (fixture)


def test_o_fa_tat_san_va_nhan_khong_biet_ngu(mo_trang):  # noqa: F811 (fixture dùng lại)
    page, _, loi = mo_trang()
    _toi_buoc_luat(page)
    o = page.locator("#wzFaDaa")
    assert o.count() == 1 and not o.is_checked()
    nhan = page.locator('label[for="wzFaDaa"]').inner_text()
    assert nhan == "Xếp theo loại CLB và huy chương"
    hop = page.locator("#wsHop").inner_text()
    assert "Wharton" not in hop and "FA-DAA" not in hop
    assert not loi, loi


def test_nhan_tieng_anh(mo_trang):  # noqa: F811 (fixture dùng lại)
    page, _, loi = mo_trang()
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("document.documentElement.lang === 'en'")
    _toi_buoc_luat(page, "Round")
    assert page.locator('label[for="wzFaDaa"]').inner_text() == "Allocate by club type and medals"
    assert not loi, loi


def test_bat_roi_tao_thi_luu_fa_daa_va_quay_lai_van_tich(mo_trang):  # noqa: F811 (fixture dùng lại)
    page, api, loi = mo_trang()
    _toi_buoc_luat(page, "Đợt FA")
    page.locator("#wzFaDaa").check()
    page.locator("#wzTiep").click()                          # sang bước xem lại
    assert page.locator("#rvFaDaa").inner_text() == "Bật"
    page.locator("#wzLui").click()
    page.wait_for_selector("#wzFaDaa")
    assert page.locator("#wzFaDaa").is_checked()             # đi về giữ nguyên
    page.locator("#wzTiep").click()
    page.locator("#wzTao").click()
    _cho_ten(page, "Đợt FA")
    rules = api.get_workspace_config()["data"]["config"]["rules"]
    assert rules["fa_daa"] is True and rules["wharton"] is True
    assert not loi, loi


def test_mac_dinh_tat_va_xem_lai_ghi_tat(mo_trang):  # noqa: F811 (fixture dùng lại)
    page, api, loi = mo_trang()
    _toi_buoc_luat(page, "Đợt thường")
    page.locator("#wzTiep").click()
    assert page.locator("#rvFaDaa").inner_text() == "Tắt"
    page.locator("#wzTao").click()
    _cho_ten(page, "Đợt thường")
    assert api.get_workspace_config()["data"]["config"]["rules"].get("fa_daa") is not True
    assert not loi, loi


def test_bat_fa_ma_tat_diem_quyet_tam_bi_tu_choi_va_hien_loi(mo_trang):  # noqa: F811 (fixture dùng lại)
    page, api, loi = mo_trang()
    _toi_buoc_luat(page, "Đợt sai")
    page.locator("#wzWharton").uncheck()
    page.locator("#wzFaDaa").check()
    page.locator("#wzTiep").click()
    page.locator("#wzTao").click()
    page.wait_for_selector(".toast.is-error", timeout=10000)
    assert "chưa hợp lệ" in page.locator(".toast.is-error").first.inner_text()   # lỗi sẵn có ws_du_lieu_sai
    ten = [w["name"] for w in api.list_workspaces()["data"]["workspaces"]]
    assert "Đợt sai" not in ten
    assert not loi, loi
