"""SG-10 (Playwright + Chromium, 1366x768): thẻ kết quả với CLB Tự do có nhiều thành viên hơn chỉ tiêu lưu.

  * dòng CLB Tự do: "12 ... không giới hạn chỗ", không có "%" và không có thanh lấp đầy;
  * ô "Chỗ còn trống" chỉ tính CLB có giới hạn (tử số và mẫu số);
  * không FA: dòng CLB vẫn có "%".
Dữ liệu MÔ PHỎNG.
"""
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import cau_hinh_ws as ch  # noqa: E402
from _fa import bat_fa, dung_fa_clb, dung_hs_fa  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _fa(api):
    bat_fa(api)
    dung_fa_clb(api, G=(3, "GIOI_HAN"), T=(5, "TU_DO"))
    ids = [f"HS{i:03d}" for i in range(1, 13)]
    dung_hs_fa(api, *ids, nv={i: ["T"] for i in ids})
    assert api.run_pipeline(seed=7)["ok"]


def _khong_fa(api):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"wharton": False}})
    dung_fa_clb(api, A=(5,), B=(5,))
    dung_hs_fa(api, "s1", "s2", nv={"s1": ["A"], "s2": ["B"]})
    assert api.run_pipeline(seed=9)["ok"]


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo(du_lieu):
        du_lieu(api)
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", viewport={"width": 1366, "height": 768}, bypass_csp=True)
        page.set_default_timeout(8000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.locator('[data-tab="others"]').click()
        page.wait_for_selector("#clbBody tr", state="attached")
        return page, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def test_clb_tu_do_khong_phan_tram(mo):
    page, loi = mo(_fa)
    t = page.locator('#clbBody tr[data-clb="T"]')
    g = page.locator('#clbBody tr[data-clb="G"]')
    lap = t.locator(".clb-lap").inner_text()
    assert "12" in lap and "không giới hạn chỗ" in lap
    assert "%" not in lap and t.locator(".fill-track").count() == 0
    assert "không giới hạn chỗ" in t.locator(".clb-chi-tieu").inner_text()
    assert "%" in g.locator(".clb-lap").inner_text() and g.locator(".fill-track").count() == 1
    assert t.locator(".fill-tag").count() == 0
    assert not loi


def test_cho_con_trong_bo_clb_tu_do(mo):
    page, loi = mo(_fa)
    o = page.locator('#tomTatLuoi .kpi-o[data-muc="clbPanel"]')
    assert "trên tổng 3 chỗ" in o.inner_text()     # chỉ CLB G (chỉ tiêu 3); T không vào mẫu số
    assert not loi


def test_khong_fa_van_co_phan_tram(mo):
    page, loi = mo(_khong_fa)
    assert "%" in page.locator('#clbBody tr[data-clb="A"] .clb-lap').inner_text()
    assert page.locator("#clbBody .clb-lap", has_text="không giới hạn").count() == 0
    assert not loi
