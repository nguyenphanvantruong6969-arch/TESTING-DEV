"""FA-M7 G0 (Playwright + Chromium): thẻ "Chuẩn bị đợt".

  * FA-DAA tắt: nút thẻ ẩn; bật: hiện, có năm khung `#cb-buoc-1..5` và ô chọn đường A / B;
  * chọn đường A rồi B lưu vào `rules.fa_duong`, nạp lại trang vẫn giữ.
Dữ liệu MÔ PHỎNG.
"""
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import cau_hinh_ws as ch  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo(fa_bat):
        if fa_bat:
            ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True}})
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
        return page, api, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def test_fa_tat_the_an(mo):
    page, _, loi = mo(False)
    page.wait_for_timeout(400)
    assert page.locator('.nav-item[data-tab="chuan_bi"]').is_hidden()
    assert not loi, loi


def test_fa_bat_the_hien_co_nam_khung_va_chon_duong(mo):
    page, api, loi = mo(True)
    nut = page.locator('.nav-item[data-tab="chuan_bi"]')
    page.wait_for_function("() => !document.querySelector('.nav-item[data-tab=chuan_bi]').hidden")
    assert nut.is_visible()
    nut.click()
    for i in range(1, 6):
        assert page.locator("#cb-buoc-%d" % i).count() == 1
    assert page.evaluate("() => window.ChuanBi.duong()") is None
    page.locator('input[name="cbDuong"][value="A"]').check()
    page.wait_for_function("() => window.ChuanBi.duong() === 'A'")
    assert api.get_fa_duong()["data"] == {"duong": "A"}
    page.locator('input[name="cbDuong"][value="B"]').check()
    page.wait_for_function("() => window.ChuanBi.duong() === 'B'")
    assert api.get_fa_duong()["data"] == {"duong": "B"}
    page.reload()
    page.wait_for_selector("#dropZone")
    page.locator('.nav-item[data-tab="chuan_bi"]').click()
    page.wait_for_function("() => window.ChuanBi.duong() === 'B'")
    assert page.locator('input[name="cbDuong"][value="B"]').is_checked()
    assert not loi, loi


def test_dang_ky_buoc_goi_ve_lai_khi_lam_moi(mo):
    page, _, loi = mo(True)
    page.wait_for_function("() => !document.querySelector('.nav-item[data-tab=chuan_bi]').hidden")
    page.evaluate("""() => { window.__dem = 0;
        window.ChuanBi.dangKyBuoc(5, (c) => { window.__dem++; c.textContent = 'x'; }); }""")
    page.locator('.nav-item[data-tab="chuan_bi"]').click()
    page.wait_for_function("() => window.__dem >= 1")
    assert page.locator("#cb-buoc-5").inner_text() == "x"
    assert not loi, loi
