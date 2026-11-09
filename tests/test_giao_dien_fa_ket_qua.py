"""FA-UI-4 (Playwright + Chromium): thẻ kết quả, khi workspace bật xếp theo loại CLB và huy chương.

  * bảng kết quả có cột "Lý do" với câu giải thích của lần chạy mới nhất cho từng học sinh;
  * hai nút "Xuất lý do kết quả (CSV)" và "Xuất bảng nhu cầu (CSV)" tạo ra tệp thật;
  * FA tắt: không cột, không nút (trang như cũ).
Dữ liệu MÔ PHỎNG.
"""
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import cau_hinh_ws as ch  # noqa: E402
from _fa import dung_fa_clb, dung_hs_fa  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from test_fa_ly_do import _dung  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _fa(api):
    _dung(api)
    assert api.run_pipeline(seed=9)["ok"]


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
        page = br.new_page(locale="vi-VN", viewport={"width": 1400, "height": 1400}, bypass_csp=True)
        page.set_default_timeout(8000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.locator('[data-tab="others"]').click()
        page.wait_for_selector("#resultsTableBody tr", state="attached")
        return page, api, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def test_fa_tat_khong_cot_khong_nut(mo):
    page, _, loi = mo(_khong_fa)
    page.wait_for_timeout(500)
    assert page.locator("#view-others .cot-ly-do").count() == 0
    assert page.locator("#btnXuatLyDo").is_hidden() and page.locator("#btnXuatNhuCau").is_hidden()
    assert page.locator("#btnXuatBienBan").is_hidden()
    assert not loi, loi


def test_fa_bat_co_cau_ly_do_moi_hoc_sinh(mo):
    page, _, loi = mo(_fa)
    page.wait_for_selector("#resultsTableBody td.cot-ly-do", state="attached")
    assert page.locator("#view-others thead th.cot-ly-do").text_content().strip() == "Lý do"
    hang = page.locator("#resultsTableBody tr", has=page.locator('input[data-student-id="s2"]'))
    cau = hang.locator("td.cot-ly-do").text_content()
    assert "điểm chuẩn" in cau                                       # s2 thua điểm ở S
    for sid in ("s1", "s3", "s4"):                                   # không lộ mã em khác
        assert sid not in cau
    assert not loi, loi


def test_hai_nut_xuat_tao_tep(mo):
    page, _, loi = mo(_fa)
    page.wait_for_selector("#btnXuatLyDo:not([hidden])")
    page.locator("#btnXuatLyDo").click()
    page.wait_for_function("() => document.getElementById('xuatFeedback').textContent.includes('ket_qua_ly_do.csv')")
    page.locator("#btnXuatNhuCau").click()
    page.wait_for_function("() => document.getElementById('xuatFeedback').textContent.includes('bang_nhu_cau')")
    txt = page.locator("#xuatFeedback").inner_text()
    duong = [w for w in txt.split() if w.endswith(".csv")]
    assert duong and all(os.path.exists(d.strip(".,;")) for d in duong), txt
    assert not loi, loi


def test_nut_bien_ban_boc_tham_tao_tep_khong_co_ma_hoc_sinh(mo):
    """FA-9: nút xuất biên bản bốc thăm (chỉ khi FA bật)."""
    page, _, loi = mo(_fa)
    page.wait_for_selector("#btnXuatBienBan:not([hidden])")
    page.locator("#btnXuatBienBan").click()
    page.wait_for_function("() => document.getElementById('xuatFeedback').textContent.includes('bien_ban_boc_tham')")
    txt = page.locator("#xuatFeedback").inner_text()
    duong = [w for w in txt.split() if w.endswith(".html")]
    assert duong and os.path.exists(duong[0].strip(".,;")), txt
    with open(duong[0].strip(".,;"), encoding="utf-8") as f:
        h = f.read()
    assert "Biên bản bốc thăm" in h and "Giáo viên chứng kiến" in h
    for sid in ("s1", "s2", "s3", "s4"):
        assert sid not in h
    assert not loi, loi
