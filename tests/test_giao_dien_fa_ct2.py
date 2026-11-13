"""FA-CT2 (Playwright + Chromium): nút "Gợi ý chia lại chỗ theo nhu cầu" ở thẻ kết quả.

  * FA bật: nút, hai ô số và dòng hướng dẫn hiện; ô trống -> mặc định (tổng hiện tại, không thêm chỗ);
  * điền "Được thêm" -> tệp có cột "Chỗ thêm"; tệp nhu cầu tham khảo được gửi lên;
  * FA tắt: không nút.
Dữ liệu MÔ PHỎNG.
"""
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from openpyxl import load_workbook  # noqa: E402

from test_giao_dien_fa_ket_qua import _fa, _khong_fa, mo  # noqa: E402,F401


def _duong(page, ten):
    page.wait_for_function("(t) => document.getElementById('xuatFeedback').textContent.includes(t)", arg=ten)
    txt = page.locator("#xuatFeedback").inner_text()
    duong = [w.strip(".,;") for w in txt.split() if ten in w]
    assert duong and os.path.exists(duong[0]), txt
    return duong[0], txt


def _o(path):
    return [c for ws in load_workbook(path).worksheets for r in ws.iter_rows(values_only=True) for c in r]


def test_nut_chia_cho_mac_dinh(mo):  # noqa: F811 (fixture nhập từ test_giao_dien_fa_ket_qua)
    page, _, loi = mo(_fa)
    page.wait_for_selector("#btnXuatChiaCho:not([hidden])")
    assert page.locator("#chiaChoHint").is_visible()
    assert "thầy cô tự quyết" in page.locator("#chiaChoHint").inner_text()
    page.locator("#btnXuatChiaCho").click()
    p, _ = _duong(page, "chia_cho_theo_nhu_cau")
    o = _o(p)
    assert "Chỗ gợi ý" in o and "Chỗ thêm" not in o
    assert not loi, loi


def test_nut_chia_cho_them_va_tep(mo, tmp_path):  # noqa: F811 (fixture nhập từ test_giao_dien_fa_ket_qua)
    page, _, loi = mo(_fa)
    page.wait_for_selector("#btnXuatChiaCho:not([hidden])")
    page.fill("#chiaChoThem", "3")
    tep = tmp_path / "nhu_cau.csv"
    tep.write_text("club_id,nhu_cau\nG,4\nQQ,1\n", encoding="utf-8")
    page.set_input_files("#chiaChoTep", str(tep))
    page.wait_for_function("() => document.getElementById('chiaChoTenTep').textContent.includes('nhu_cau.csv')")
    page.locator("#btnXuatChiaCho").click()
    p, txt = _duong(page, "chia_cho_theo_nhu_cau")
    o = _o(p)
    assert "Chỗ thêm" in o and "Nhu cầu tham khảo (tệp)" in o
    assert "QQ" in txt                                     # cảnh báo mã CLB lạ
    assert not loi, loi


def test_fa_tat_khong_nut(mo):  # noqa: F811 (fixture nhập từ test_giao_dien_fa_ket_qua)
    page, _, loi = mo(_khong_fa)
    assert page.locator("#btnXuatChiaCho").is_hidden()
    assert page.locator("#chiaChoKhoi").is_hidden() and page.locator("#chiaChoHint").is_hidden()
    assert not loi, loi
