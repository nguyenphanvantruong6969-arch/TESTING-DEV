"""FG-4 (STEP0, spec §3) (Playwright + Chromium): hai nút nạp tệp Forms — trạng thái bận, đường lỗi, một hàm dùng chung.
Dữ liệu MÔ PHỎNG; mọi việc Forms là TH.

Cách đo: chặn `/__api__/<tên>` bằng `page.route`, giữ yêu cầu lại để quan sát nút khi API còn đang chạy.
"""
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

import openpyxl  # noqa: E402

from test_fa_m6b_sau_ket_qua import _dung, _hang_gop, _tl, de  # noqa: E402,F401
from test_giao_dien_fa_gap1_theo_doi import mo  # noqa: E402,F401 (fixture)

CAC_NUT = [("btnNhapSauKetQua", "phTepSauKetQua", "nhap_sau_ket_qua_forms"),
           ("btnNhapPhanHoi", "phTep", "nhap_phan_hoi_forms")]


def _tep(tmp_path, de_):
    p = tmp_path / "ket_qua_forms.xlsx"
    wb = openpyxl.Workbook()
    for h in _hang_gop(de_, [_tl(de_, "s1", 4, 1, "huy_chuong")]):
        wb.active.append(h)
    wb.save(str(p))
    return str(p)


def _giu_yeu_cau(page, ten_api):
    """Trả danh sách các `route` đang bị giữ; test tự `continue_()` hoặc `abort()`."""
    giu = []
    page.route("**/__api__/" + ten_api, lambda route: giu.append(route))
    return giu


def _cho_giu(page, giu, n=1):
    for _ in range(100):
        if len(giu) >= n:
            return
        page.wait_for_timeout(50)
    raise AssertionError("API chưa được gọi")


@pytest.mark.parametrize("nut,o_tep,ten_api", CAC_NUT)
def test_nut_bi_khoa_va_hien_dang_nap_khi_goi_api(mo, tmp_path, de, nut, o_tep, ten_api):  # noqa: F811
    page, api, loi = mo(_dung)
    page.wait_for_selector("#phanHoiTongPanel:not([hidden])")
    giu = _giu_yeu_cau(page, ten_api)
    chu_goc = page.locator("#" + nut).inner_text()
    page.set_input_files("#" + o_tep, _tep(tmp_path, de))
    _cho_giu(page, giu)
    assert page.locator("#" + nut).is_disabled()
    assert re.search("Đang nạp", page.locator("#" + nut).inner_text())
    page.locator("#" + nut).click(force=True)                       # bấm lần hai: không được sinh yêu cầu mới
    page.wait_for_timeout(300)
    assert len(giu) == 1
    giu[0].continue_()
    page.wait_for_function("id => !document.getElementById(id).disabled", arg=nut)
    assert page.locator("#" + nut).inner_text() == chu_goc
    assert page.eval_on_selector("#" + o_tep, "e => e.value") == ""
    assert not loi, loi


@pytest.mark.parametrize("nut,o_tep,ten_api", CAC_NUT)
def test_goi_api_hong_bao_loi_chung_va_mo_lai_nut(mo, tmp_path, de, nut, o_tep, ten_api):  # noqa: F811
    page, api, loi = mo(_dung)
    page.wait_for_selector("#phanHoiTongPanel:not([hidden])")
    giu = _giu_yeu_cau(page, ten_api)
    page.set_input_files("#" + o_tep, _tep(tmp_path, de))
    _cho_giu(page, giu)
    giu[0].abort()
    page.wait_for_function("id => !document.getElementById(id).disabled", arg=nut)
    assert page.locator("#toastStack").inner_text().strip() != ""   # có thông báo lỗi chung
    assert page.eval_on_selector("#" + o_tep, "e => e.value") == ""
    loi_trang = [x for x in loi if "Failed to fetch" not in x]
    assert not loi_trang, loi_trang                                  # không có lỗi JS chưa bắt (unhandled rejection)
