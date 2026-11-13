# -*- coding: utf-8 -*-
"""SG-6 (H1), phần giao diện (Playwright + Chromium): giờ và địa điểm CLB hiện ở bảng "Theo từng câu lạc bộ" và
bảng Quản lý, và CHỈ khi đã khai (dữ liệu cũ: không thêm chữ nào). Dữ liệu MÔ PHỎNG."""
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from _trinh_duyet import CHROMIUM  # noqa: E402
from _wharton import tat_wharton  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIO, DIA = "15:30-17:00", "Sân A"


def _mo(api, voi_gio):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    tat_wharton(api)
    api.create_or_update_club("a", "CLB A", 1, 0, "")
    api.create_or_update_club("b", "CLB B", 5, 0, "")
    assert api.import_preferences_csv(
        "student_id,name,pref_1,pref_2\nHS1,Em 1,a,b\nHS2,Em 2,a,b\n")["ok"]
    if voi_gio:
        with api._ket_noi_ghi() as cur:
            cur.execute("UPDATE clubs SET gio = ?, dia_diem = ? WHERE club_id = 'a'", (GIO, DIA))
    assert api.run_pipeline(seed=7)["ok"]
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(bypass_csp=True)
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    page.goto(url)
    return pw, br, page, loi


@pytest.mark.parametrize("voi_gio", [True, False])
def test_bang_theo_clb_va_quan_ly(api, voi_gio):
    pw, br, page, loi = _mo(api, voi_gio)
    try:
        page.click('.nav-item[data-tab="others"]')
        page.wait_for_selector("#clbPanel .panel-toggle")
        page.click("#clbPanel .panel-toggle")
        page.wait_for_selector("#clbBody tr")
        theo_clb = page.inner_text("#clbBody")
        page.click('.nav-item[data-tab="admin"]')
        page.wait_for_selector("#adminClubTableBody tr")
        quan_ly = page.inner_text("#adminClubTableBody")
        for chu in (theo_clb, quan_ly):
            assert (GIO in chu and DIA in chu) == voi_gio, chu
        assert not loi, loi
    finally:
        br.close()
        pw.stop()
