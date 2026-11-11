"""FA-M6b (Playwright + Chromium): nút "Nạp biểu mẫu Sau khi xem kết quả" ở khung Phản hồi của thẻ "Chi tiết và xuất tệp".

  * cờ `fa_phan_hoi` tắt: không có khung, không có nút;
  * bật cả hai cờ: nạp một tệp xlsx MÔ PHỎNG -> một thông báo có số đếm, một khiếu nại hiện trong danh sách khiếu nại,
    khung tổng hợp phản hồi cập nhật; khiếu nại quá hạn được liệt kê trong thông báo (không làm hỏng lần nạp).
Dữ liệu MÔ PHỎNG.
"""
import datetime
import os
import tempfile

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_fa_m6b_sau_ket_qua import _buoi, _buoi_cell, _dung, _hang_gop, _run_at, _tl, bm  # noqa: E402
from test_giao_dien_fa_gap1_theo_doi import mo  # noqa: E402,F401 (fixture)


def _tat(api):
    _dung(api, ph=False, kn=False)


def _xlsx(de, dong):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    for h in _hang_gop(de, dong):
        ws.append(h)
    duong = os.path.join(tempfile.mkdtemp(), "sau_ket_qua.xlsx")
    wb.save(duong)
    return duong


def test_co_tat_khong_co_nut(mo):  # noqa: F811
    page, _, loi = mo(_tat)
    page.wait_for_timeout(300)
    assert page.locator("#phanHoiTongPanel[hidden]").count() == 1
    assert not loi, loi


def test_nap_tep_gop_hien_so_dem_va_mot_khieu_nai(mo):  # noqa: F811
    de = bm.doc_de_thi()
    page, api, loi = mo(_dung)
    r0 = _run_at(api)
    page.wait_for_selector("#phanHoiTongPanel:not([hidden])")
    nut = page.locator("#btnNhapSauKetQua")
    assert nut.is_visible() and "Sau khi xem kết quả" in nut.inner_text()
    buoi = _buoi_cell(_buoi(api))
    duong = _xlsx(de, [
        _tl(de, "s1", co_sai=1, buoi=buoi, ghi_chu="Điểm thi nhập sai", luc=r0 + datetime.timedelta(minutes=5)),
        _tl(de, "s2", co_sai=0),
        _tl(de, "s3", co_sai=1, buoi=buoi, ghi_chu="Quá hạn", luc=r0 + datetime.timedelta(days=30))])
    page.set_input_files("#phTepSauKetQua", duong)
    page.wait_for_selector(".toast")
    chu = page.locator(".toast").first.inner_text()
    assert "3 phản hồi" in chu and "1 khiếu nại" in chu, chu
    assert "s3" in chu                                         # khiếu nại quá hạn được liệt kê trong thông báo
    page.wait_for_function("() => document.getElementById('knDanhSach').textContent.includes('Điểm thi nhập sai')")
    assert page.locator("#knDanhSach li").count() == 1
    page.locator('[data-tab="others"]').click()
    page.wait_for_function("() => document.getElementById('phTongHop').textContent.includes('3 học sinh')")
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM fa_phan_hoi").fetchone()[0] == 3
        assert cur.execute("SELECT COUNT(*) FROM fa_khieu_nai").fetchone()[0] == 1
    assert not loi, loi
