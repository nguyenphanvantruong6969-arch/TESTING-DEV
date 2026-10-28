"""Thẻ "Quản lý" chia tab con (A13.5; Playwright + Chromium, qua `browser_host`).

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.

  * tắt điểm quyết tâm: 3 tab con (CLB, Học sinh, Dữ liệu), mỗi tab có đủ các khối cũ;
  * bật: 5 tab con (thêm Điểm quyết tâm và Điểm chuẩn);
  * bấm thì chỉ một vùng nội dung hiện; `aria-selected` đúng; phím mũi tên, Home, End chuyển tab;
  * tải lại trang thì mở lại đúng tab con vừa dùng; kho lưu trữ ném lỗi thì vẫn mở tab đầu.
"""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _wharton import bat_wharton, chen_bids, dung_clb, dung_hs  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402

TAB = '#qlTabs [role="tab"]'


def _dung_du_lieu(api, bat):
    if bat:
        bat_wharton(api)
    dung_clb(api, A=(5, "thu_3"), B=(5, "thu_3"), C=(5, "thu_3"))
    dung_hs(api, "HS1", "HS2", tick={"HS1": ["A"]})
    assert api.submit_preferences("HS1", ["A", "B", "C"])["ok"]
    assert api.submit_preferences("HS2", ["B", "C"])["ok"]
    if bat:
        chen_bids(api, [("HS1", "A", 1, 100), ("HS1", "B", 2, 60), ("HS1", "C", 2, 40)])


@pytest.fixture
def mo(tmp_path, api):
    """mo(bat=True, khoang=None) -> (page, api, loi, mo_lai). Mở thẻ Quản lý."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo(bat=True, kho_hong=False):
        _dung_du_lieu(api, bat)
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", viewport={"width": 1280, "height": 1400}, bypass_csp=True)
        page.set_default_timeout(8000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        if kho_hong:
            page.add_init_script("""
                Storage.prototype.getItem = function () { throw new Error('khong doc duoc'); };
                Storage.prototype.setItem = function () { throw new Error('khong ghi duoc'); };
            """)

        def vao_the_quan_ly(tai_lai=False):
            if tai_lai:
                # cờ của chính ứng dụng: tải lại trang không phải đóng cửa sổ (browser_host)
                page.evaluate("window.__DANG_TAI_LAI = true")
                page.reload()
            else:
                page.goto(url)
            page.wait_for_selector("#dropZone")
            page.locator('[data-tab="admin"]').click()
            page.wait_for_selector("#btnResetAll", state="attached")
            if bat:
                page.wait_for_selector("#adminWhartonBlock:not([hidden])", state="attached")
                page.wait_for_selector("#adminDiemChuanBlock:not([hidden])", state="attached")
            else:
                page.wait_for_selector("#adminClubTableBody tr")
                page.wait_for_timeout(300)

        vao_the_quan_ly()
        return page, api, loi, vao_the_quan_ly

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _tab_hien(page):
    return page.eval_on_selector_all(
        TAB + ":not([hidden])", "ns => ns.map(n => n.dataset.qlTab)")


def _vung_hien(page):
    return page.eval_on_selector_all(
        '#view-admin [role="tabpanel"]',
        "ns => ns.filter(n => !n.hidden && n.offsetParent !== null).map(n => n.dataset.qlTab)")


def _chon(page):
    return page.eval_on_selector_all(
        TAB + '[aria-selected="true"]', "ns => ns.map(n => n.dataset.qlTab)")


def _tab(page, ten):
    return page.locator(TAB + '[data-ql-tab="%s"]' % ten)


# ------------------------------------------------------------------ tắt: ba tab con

def test_tat_co_ba_tab_con_va_noi_dung_cu_day_du(mo):
    page, api, loi, _ = mo(bat=False)
    assert _tab_hien(page) == ["clb", "hs", "du_lieu"]
    assert _chon(page) == ["clb"] and _vung_hien(page) == ["clb"]
    # tab CLB: biểu mẫu và bảng CLB
    for sel in ("#clubFormId", "#btnSaveClub", "#adminClubTableBody"):
        assert page.locator(sel).is_visible(), sel
    _tab(page, "hs").click()
    assert _vung_hien(page) == ["hs"]
    for sel in ("#adminStudentSearch", "#btnBulkAssign", "#adminStudentTableBody"):
        assert page.locator(sel).is_visible(), sel
    _tab(page, "du_lieu").click()
    assert _vung_hien(page) == ["du_lieu"]
    for sel in ("#btnResetStudents", "#btnResetAll"):
        assert page.locator(sel).is_visible(), sel
    assert page.locator("#adminWhartonBlock").is_hidden()
    assert page.locator("#adminDiemChuanBlock").is_hidden()
    assert not loi, loi


# ------------------------------------------------------------------ bật: năm tab con

def test_bat_co_nam_tab_con_dung_thu_tu(mo):
    page, api, loi, _ = mo()
    assert _tab_hien(page) == ["clb", "hs", "wh", "dc", "du_lieu"]
    _tab(page, "wh").click()
    assert _vung_hien(page) == ["wh"]
    assert page.locator("#adminWhartonBlock").is_visible() and page.locator("#whQlBody tr").count()
    _tab(page, "dc").click()
    assert _vung_hien(page) == ["dc"]
    assert page.locator("#adminDiemChuanBlock").is_visible()
    assert not loi, loi


def test_bam_tab_chi_mot_vung_hien_va_aria_selected_dung(mo):
    page, api, loi, _ = mo()
    for ten in ("hs", "wh", "dc", "du_lieu", "clb"):
        _tab(page, ten).click()
        assert _chon(page) == [ten]
        assert _vung_hien(page) == [ten]
        # mỗi tab trỏ đúng vùng của nó, vùng trỏ ngược lại tab
        ma_vung = _tab(page, ten).get_attribute("aria-controls")
        assert page.locator("#" + ma_vung).get_attribute("aria-labelledby") == \
            _tab(page, ten).get_attribute("id")
    assert page.locator("#qlTabs").get_attribute("role") == "tablist"
    assert not loi, loi


def test_phim_mui_ten_home_end_chuyen_tab(mo):
    page, api, loi, _ = mo()
    _tab(page, "clb").focus()
    page.keyboard.press("ArrowRight")
    assert _chon(page) == ["hs"] and _vung_hien(page) == ["hs"]
    page.keyboard.press("ArrowRight")
    assert _chon(page) == ["wh"]
    page.keyboard.press("End")
    assert _chon(page) == ["du_lieu"]
    page.keyboard.press("ArrowRight")                      # quay vòng về đầu
    assert _chon(page) == ["clb"]
    page.keyboard.press("ArrowLeft")                       # quay vòng về cuối
    assert _chon(page) == ["du_lieu"]
    page.keyboard.press("Home")
    assert _chon(page) == ["clb"]
    # chỉ tab đang chọn nằm trong thứ tự Tab của bàn phím
    assert page.eval_on_selector_all(
        TAB + '[tabindex="0"]', "ns => ns.map(n => n.dataset.qlTab)") == ["clb"]
    assert not loi, loi


def test_phim_mui_ten_bo_qua_tab_dang_an(mo):
    page, api, loi, _ = mo(bat=False)
    _tab(page, "hs").focus()
    page.keyboard.press("ArrowRight")
    assert _chon(page) == ["du_lieu"]                      # nhảy qua hai tab điểm đang ẩn
    assert not loi, loi


# ------------------------------------------------------------------ nhớ tab đang mở

def test_tai_lai_trang_mo_lai_tab_con_vua_dung(mo):
    page, api, loi, vao_lai = mo()
    _tab(page, "wh").click()
    vao_lai(tai_lai=True)
    assert _chon(page) == ["wh"] and _vung_hien(page) == ["wh"]
    _tab(page, "du_lieu").click()
    vao_lai(tai_lai=True)
    assert _chon(page) == ["du_lieu"]
    assert not loi, loi


def test_tab_da_nho_khong_con_ton_tai_thi_mo_tab_dau(mo):
    """Nhớ 'wh' nhưng tính năng đã tắt: không có tab đó, mở tab đầu."""
    page, api, loi, vao_lai = mo()
    _tab(page, "wh").click()
    bat_wharton(api, bat=False)
    page.evaluate("window.__DANG_TAI_LAI = true")
    page.reload()
    page.wait_for_selector("#dropZone")
    page.locator('[data-tab="admin"]').click()
    page.wait_for_selector("#adminClubTableBody tr")
    page.wait_for_timeout(300)
    assert _tab_hien(page) == ["clb", "hs", "du_lieu"]
    assert _chon(page) == ["clb"] and _vung_hien(page) == ["clb"]
    assert not loi, loi


def test_kho_luu_tru_nem_loi_van_mo_tab_dau_va_chuyen_tab_duoc(mo):
    page, api, loi, _ = mo(kho_hong=True)
    assert _chon(page) == ["clb"] and _vung_hien(page) == ["clb"]
    _tab(page, "hs").click()
    assert _chon(page) == ["hs"] and _vung_hien(page) == ["hs"]
    assert not loi, loi


def test_tieng_anh_ten_tab_doi_theo(mo):
    page, api, loi, _ = mo()
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("document.documentElement.lang === 'en'")
    chu = page.eval_on_selector_all(TAB + ":not([hidden])", "ns => ns.map(n => n.textContent.trim())")
    assert chu[2:] == ["Preference points", "Cut-off points", "Data"]
    assert not loi, loi
