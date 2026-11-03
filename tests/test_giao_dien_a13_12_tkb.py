"""A13.12 (BAO_CAO_SOAT_NHAP 3.6): thẻ Kết quả, "Theo mã học sinh" — gõ chuỗi tìm không khớp em nào
thì hiện câu báo rỗng nhưng ô tìm còn đó (trước đây cả panel, kèm ô tìm, biến mất). Chromium thật; MÔ PHỎNG."""

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from _wharton import tat_wharton  # noqa: E402
from test_giao_dien_thu_gon_ket_qua import trang  # noqa: E402,F401


@pytest.fixture
def api(api):
    """A13.13: mặc định BẬT Wharton; dữ liệu của `trang` không có điểm quyết tâm nên tắt RÕ RÀNG
    (fixture `api` ghi đè ở tệp gốc không áp cho tệp nhập `trang`)."""
    tat_wharton(api)
    return api


def test_tim_khong_khop_giu_o_tim_va_go_lai_thi_co_ket_qua(trang):  # noqa: F811
    """T2: bảng thời khoá biểu từng học sinh nằm ở thẻ Kết quả, cách xem "Theo mã học sinh"."""
    page, loi, api, ctx, url = trang
    page.locator('[data-tab="results"]').click()
    page.locator('#kqTang1 [data-kq="ma"]').click()
    page.wait_for_function("() => document.querySelectorAll('#kqThan tr').length > 0")
    co_hang = page.locator("#kqThan tr").count()
    page.fill("#kqTimKiem", "zzzzkhongcoai")
    page.wait_for_function("() => !document.getElementById('kqRong').hidden")
    assert page.locator("#kqBang").is_hidden()
    assert page.locator("#kqTimKiem").is_visible()          # ô tìm còn đó để sửa chuỗi tìm
    page.fill("#kqTimKiem", "")
    page.wait_for_function("(n) => document.querySelectorAll('#kqThan tr').length === n", arg=co_hang)
    assert not loi, loi
