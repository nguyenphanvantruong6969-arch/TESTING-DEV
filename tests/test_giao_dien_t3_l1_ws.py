"""T3-L1 (T3-37): tiêu đề bước của hộp tạo workspace. Dữ liệu MÔ PHỎNG; bỏ qua nếu thiếu Chromium."""

import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_ws_giao_dien import mo_trang  # noqa: E402,F401


def test_tieu_de_buoc_hop_tao_workspace_dung_hai_cham_khong_gach_dai(mo_trang):  # noqa: F811
    page, _api, _goc, loi = mo_trang()
    page.locator("#btnWorkspace").click()
    page.locator("#wsBtnMoi").click()
    page.fill("#wzTen", "Thử bước")
    page.locator("#wzTuyChinh").click()                  # T3-11: chỉ khi "Tuỳ chỉnh" mới có tiêu đề bước
    page.wait_for_selector(".ws-buoc-ten")
    for _ in range(3):
        chu = page.inner_text(".ws-buoc-ten")
        assert re.fullmatch(r"Bước \d/\d: .+", chu), chu
        assert "\u2014" not in chu
        if page.locator("#wzTiep").count() and page.locator("#wzTiep").is_visible():
            page.locator("#wzTiep").click()
    assert not loi
