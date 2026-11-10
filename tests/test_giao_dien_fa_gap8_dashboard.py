"""GAP-8 (Playwright + Chromium): bảng điều khiển quản trị ở thẻ "Quản lý".

  * FA tắt: không có khung;
  * FA bật: bảng 12 chỉ số theo thứ tự V§11; chỉ số chưa có nguồn ghi "chưa có dữ liệu"; nút xuất tạo dashboard.xlsx.
Dữ liệu MÔ PHỎNG.
"""
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from _fa import bat_fa  # noqa: E402
from test_fa_gap8_dashboard import THU_TU, _dung  # noqa: E402
from test_giao_dien_fa_gap1_theo_doi import mo  # noqa: E402,F401 (fixture)


def _co_ket_qua(api):
    _dung(api)
    assert api.run_pipeline(seed=3)["ok"]


def _tat(api):
    _co_ket_qua(api)
    bat_fa(api, False)


def test_fa_tat_khong_co_khung(mo):  # noqa: F811
    page, _, loi = mo(_tat)
    page.locator('[data-tab="admin"]').click()
    page.wait_for_selector("#adminClubTableBody tr", state="attached")
    page.wait_for_timeout(300)
    assert page.locator("#dashboardPanel[hidden]").count() == 1
    assert not loi, loi


def test_bang_chi_so_va_xuat(mo):  # noqa: F811
    page, _, loi = mo(_co_ket_qua)
    page.locator('[data-tab="admin"]').click()
    page.wait_for_selector("#dashboardPanel:not([hidden]) #dbBangBody tr")
    hang = page.locator("#dbBangBody tr")
    assert [hang.nth(i).get_attribute("data-ma") for i in range(hang.count())] == THU_TU
    chua = page.locator('#dbBangBody tr[data-ma="ty_le_dang_ky_3_ngay"] td').nth(1).text_content()
    assert chua == "chưa có dữ liệu"
    assert page.locator('#dbBangBody tr[data-ma="thua_boc_tham_1_lan"] td').nth(1).text_content() == "3"
    assert page.locator('#dbBangBody tr[data-ma="khong_co_clb"] td').nth(3).text_content() == "Đạt"
    page.locator("#btnXuatDashboard").click()
    page.wait_for_function("() => document.getElementById('dbFeedback').textContent.includes('dashboard.xlsx')")
    txt = page.locator("#dbFeedback").inner_text()
    duong = [w.strip(".,;") for w in txt.split() if "dashboard.xlsx" in w]
    assert duong and os.path.exists(duong[0]), txt
    assert not loi, loi
