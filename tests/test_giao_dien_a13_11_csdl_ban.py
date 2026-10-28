"""A13.11 (N3) — giao diện nói rõ "CSDL đang bận" khi app.db đang bị tiến trình khác giữ.

Chromium thật qua `browser_host`. Trước: "Kiểm tra dữ liệu" báo "Dữ liệu chưa hợp lệ" và "Chạy
sắp xếp" báo "Chạy thất bại" chung chung, dù dữ liệu không sai gì — CSDL chỉ đang bận.
Máy nào không có playwright / Chromium thì bỏ qua cả tệp.
"""

import contextlib
import os
import sqlite3

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402

from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAU_BAN = "đang bận"


@contextlib.contextmanager
def _khoa_csdl(db):
    conn = sqlite3.connect(db, isolation_level=None)
    conn.execute("BEGIN EXCLUSIVE")
    try:
        yield
    finally:
        conn.execute("ROLLBACK")
        conn.close()


@pytest.fixture
def trang(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api.create_or_update_club("a", "A", 2, 0, "")
    api.create_or_update_club("b", "B", 5, 0, "")
    for sid in ("N1", "N2", "N3"):
        assert api.create_student_if_missing(sid, sid)["ok"]
        assert api.submit_preferences(sid, ["a", "b"])["ok"]
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        page = br.new_page(bypass_csp=True)
        page.goto(url)
        page.wait_for_selector("#btnRun")
        page.wait_for_function("document.querySelector('#statStudents').textContent === '3'")
        yield page, api
        br.close()


def _toast_loi(page):
    page.wait_for_selector(".toast.is-error", timeout=20000)
    return page.locator(".toast.is-error").first.inner_text()


def test_kiem_tra_du_lieu_gap_csdl_ban_noi_dang_ban_khong_noi_du_lieu_sai(trang):
    page, api = trang
    with _khoa_csdl(api.db_path):
        page.click("#btnValidate")
        chu = _toast_loi(page)
    assert CAU_BAN in chu, chu
    assert "chưa hợp lệ" not in chu, chu


def test_chay_sap_xep_gap_csdl_ban_noi_dang_ban(trang):
    page, api = trang
    with _khoa_csdl(api.db_path):
        page.click("#btnRun")
        chu = _toast_loi(page)
    assert CAU_BAN in chu, chu
    assert "thất bại" not in chu.lower() or CAU_BAN in chu


def test_o_canh_bao_du_lieu_va_tong_quan_noi_dang_ban(trang):
    page, api = trang
    with _khoa_csdl(api.db_path):
        page.click("#btnHealthRecheck")
        page.wait_for_function(
            "document.querySelector('#healthSummary').textContent.includes('đang bận')",
            timeout=20000)
        # tổng quan: gọi lại tải thống kê (thẻ Vận hành tự làm khi quay lại thẻ)
        page.evaluate("refreshDashboardStats()")
        chu = _toast_loi(page)
    assert CAU_BAN in chu, chu


def test_het_bi_giu_thi_chay_lai_binh_thuong(trang):
    page, api = trang
    with _khoa_csdl(api.db_path):
        page.click("#btnValidate")
        _toast_loi(page)
    page.wait_for_function("!document.querySelector('#btnValidate').disabled")
    page.click("#btnValidate")
    page.wait_for_selector(".toast.is-success", timeout=20000)
