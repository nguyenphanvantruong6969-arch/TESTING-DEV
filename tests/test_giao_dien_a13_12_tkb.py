"""A13.12 (BAO_CAO_SOAT_NHAP 3.6): thẻ Kết quả, bảng thời khoá biểu — gõ chuỗi tìm không khớp em nào
thì bảng rỗng nhưng ô tìm còn đó (trước đây cả panel, kèm ô tìm, biến mất). Chromium thật; MÔ PHỎNG."""

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_giao_dien_thu_gon_ket_qua import trang  # noqa: E402,F401


def test_tim_khong_khop_giu_o_tim_va_go_lai_thi_co_ket_qua(trang):  # noqa: F811
    page, loi, api, ctx, url = trang
    co_hang = page.locator("#tkbBody tr").count()
    assert co_hang > 0
    page.fill("#tkbSearch", "zzzzkhongcoai")
    page.wait_for_function("() => document.querySelectorAll('#tkbBody tr').length === 0")
    assert page.locator("#tkbPanel").is_visible()
    assert page.locator("#tkbSearch").is_visible()
    page.fill("#tkbSearch", "")
    page.wait_for_function("(n) => document.querySelectorAll('#tkbBody tr').length === n", arg=co_hang)
    assert not loi, loi
