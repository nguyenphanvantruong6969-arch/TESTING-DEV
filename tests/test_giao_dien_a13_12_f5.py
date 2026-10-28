"""A13.12 (BAO_CAO_SOAT_NHAP 1.1, CHẶN): F5 ở chế độ trình duyệt không được tắt máy chủ.
Chromium thật qua `browser_host`; dữ liệu MÔ PHỎNG."""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_f5_nhieu_lan_may_chu_van_song_va_goi_api_duoc(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    try:
        page = br.new_page(locale="vi-VN", bypass_csp=True)
        page.set_default_timeout(8000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        for _ in range(3):
            page.reload()
            page.wait_for_selector("#dropZone")
        # Qua ngưỡng chờ sau báo đóng của lần tải lại cuối: máy chủ phải còn sống.
        page.wait_for_timeout(int((browser_host._CHO_SAU_BAO_DONG_SECONDS + 2) * 1000))
        kq = page.evaluate("window.pywebview.api.get_dashboard_status()")
        assert kq["ok"] is True
        assert not loi, loi
    finally:
        br.close()
        pw.stop()
