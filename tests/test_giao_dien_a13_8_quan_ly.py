"""A13.8, giao diện thẻ Quản lý (Chromium, qua `browser_host`). Dữ liệu MÔ PHỎNG dựng trong test.

  * lỗi 3.1: chỉ mã `wharton_chua_bat` mới ẩn tab; lỗi khác hiện thông báo và giữ tab;
  * lỗi 3.3: tắt tính năng thì mở Quản lý KHÔNG gọi `list_wharton_canh_bao` / `get_diem_chuan`;
  * lỗi 3.4: dòng chú thích "N học sinh không tính…" có khoảng cách phía trên.
"""

import json

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_giao_dien_wharton_quan_ly import _mo_man_sua, _xem_nhat_ky, mo  # noqa: E402,F401


def _loi_api(ma):
    return {"status": 200, "content_type": "application/json", "body": json.dumps(
        {"ok": False, "data": None, "errors": [{"code": ma, "params": {"detail": "gia"}}]})}


def _chan(page, ten, ma):
    page.route("**/__api__/" + ten, lambda r: r.fulfill(**_loi_api(ma)))


def _mo_ql(page):
    page.locator('[data-tab="admin"]').click()
    page.wait_for_selector("#btnResetAll", state="attached")


@pytest.fixture
def trinh(tmp_path, api):
    """Mở trang CHƯA vào thẻ Quản lý, để đặt route trước. trinh(bat) -> (page, api, loi, goi)."""
    import os
    import browser_host
    from playwright.sync_api import sync_playwright
    from _trinh_duyet import CHROMIUM
    from test_giao_dien_wharton_quan_ly import _dung_du_lieu, GOC
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo(bat=True):
        _dung_du_lieu(api, bat)
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", viewport={"width": 1280, "height": 1400}, bypass_csp=True)
        page.set_default_timeout(8000)
        loi, goi = [], []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.on("request", lambda r: goi.append(os.path.basename(r.url)) if "/__api__/" in r.url else None)
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.wait_for_timeout(300)       # cấu hình workspace nạp xong
        return page, api, loi, goi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def test_loi_that_khong_an_tab_va_co_thong_bao(trinh):
    page, api, loi, goi = trinh(True)
    _chan(page, "list_wharton_canh_bao", "error_wharton_quan_ly")
    _chan(page, "get_diem_chuan", "error_wharton_quan_ly")
    _mo_ql(page)
    page.wait_for_selector(".toast.is-error", state="attached")
    assert page.locator("#qlTabWh").is_visible()
    assert page.locator("#qlTabDc").is_visible()
    assert not loi, loi


def test_chua_bat_thi_van_an_tab(trinh):
    page, api, loi, goi = trinh(True)
    _chan(page, "list_wharton_canh_bao", "wharton_chua_bat")
    _chan(page, "get_diem_chuan", "wharton_chua_bat")
    _mo_ql(page)
    page.wait_for_function("() => document.getElementById('adminWhartonBlock').hidden")
    page.wait_for_timeout(300)
    assert page.locator("#qlTabWh").is_hidden() and page.locator("#qlTabDc").is_hidden()
    assert page.locator(".toast.is-error").count() == 0
    assert not loi, loi


def test_loi_nhat_ky_hien_thong_bao(mo):
    page, api, loi = mo()
    _chan(page, "get_wharton_nhat_ky", "error_wharton_quan_ly")
    _mo_man_sua(page, "HS2")
    _xem_nhat_ky(page)
    page.wait_for_selector(".toast.is-error", state="attached")
    assert not loi, loi


def test_tat_tinh_nang_khong_goi_api_diem_quyet_tam(trinh):
    page, api, loi, goi = trinh(False)
    _mo_ql(page)
    page.wait_for_selector("#adminClubTableBody tr, #adminClubEmptyState")
    page.wait_for_timeout(500)
    assert "list_students_admin" in goi
    cam = {"list_wharton_canh_bao", "get_diem_chuan", "get_wharton_lock_status", "list_wharton_admin"}
    assert not (cam & set(goi)), cam & set(goi)
    assert page.locator("#qlTabWh").is_hidden() and page.locator("#qlTabDc").is_hidden()
    assert not loi, loi


def test_bat_tinh_nang_van_goi_api(trinh):
    page, api, loi, goi = trinh(True)
    _mo_ql(page)
    page.wait_for_selector("#qlTabWh:not([hidden])")
    assert "list_wharton_canh_bao" in goi and "get_diem_chuan" in goi
    assert not loi, loi


def test_dc_khong_xet_co_khoang_cach_tren(trinh):
    page, api, loi, goi = trinh(False)
    mt = page.evaluate("""() => {
      const p = document.createElement('p'); p.id = 'dcKhongXet'; document.body.appendChild(p);
      return parseFloat(getComputedStyle(p).marginTop); }""")
    assert mt >= 6
