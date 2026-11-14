"""SG-11b (M4): màn chọn workspace là hộp thoại — focus đầu vào trong hộp, bẫy Tab, Esc chỉ đóng khi đóng được.
Chromium thật. Dữ liệu MÔ PHỎNG."""
import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_ws_giao_dien import mo_trang  # noqa: E402,F401 (fixture)

TRONG = "(() => { const o = document.getElementById('wsOverlay'); return o.contains(document.activeElement); })()"


def _mo(page):
    page.locator("#btnWorkspace").click()
    page.wait_for_selector("#wsOverlay:not([hidden]) #wsBtnMoi")


def _tab(page, n, shift=False):
    for _ in range(n):
        page.keyboard.press("Shift+Tab" if shift else "Tab")


def _tat_ca_trong(page):
    return page.evaluate(TRONG)


def test_focus_ban_dau_nam_trong_hop(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _mo(page)
    assert _tat_ca_trong(page)
    assert page.evaluate("document.getElementById('wsOverlay').getAttribute('aria-modal')") == "true"
    assert not loi, loi


def test_tab_xoay_vong_ca_hai_chieu(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _mo(page)
    n = page.evaluate("""() => [...document.querySelectorAll('#wsOverlay button, #wsOverlay input, #wsOverlay summary, #wsOverlay [tabindex="0"]')]
        .filter(e => !e.disabled && e.type !== 'file' && e.offsetParent !== null).length""")
    for _ in range(n + 3):
        _tab(page, 1)
        assert _tat_ca_trong(page), "Tab lọt ra ngoài hộp"
    for _ in range(n + 3):
        _tab(page, 1, shift=True)
        assert _tat_ca_trong(page), "Shift+Tab lọt ra ngoài hộp"
    # từ ô đầu, Shift+Tab nhảy xuống ô cuối; từ ô cuối, Tab nhảy lên ô đầu
    page.focus("#wsBtnMoi")
    _tab(page, 1, shift=True)
    assert _tat_ca_trong(page)
    page.focus("#wsBtnDong")
    _tab(page, 1)
    assert _tat_ca_trong(page)
    assert not loi, loi


def test_tab_van_giu_bay_trong_trinh_huong_dan(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _mo(page)
    page.locator("#wsBtnMoi").click()
    page.wait_for_selector("#wsOverlay input, #wsOverlay select")
    assert _tat_ca_trong(page)
    for _ in range(25):
        _tab(page, 1)
        assert _tat_ca_trong(page)
    for _ in range(25):
        _tab(page, 1, shift=True)
        assert _tat_ca_trong(page)
    assert not loi, loi


def test_esc_dong_khi_dong_duoc_va_tra_focus(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _mo(page)
    page.keyboard.press("Escape")
    assert page.evaluate("document.getElementById('wsOverlay').hidden")
    assert page.evaluate("document.activeElement.id") == "btnWorkspace"
    assert not loi, loi


def test_esc_khong_dong_khi_chua_chon(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang(ten_ws=("A", "B"), da_chon=False)
    page.wait_for_selector("#wsOverlay:not([hidden]) #wsBtnMoi")
    assert _tat_ca_trong(page)
    page.keyboard.press("Escape")
    assert not page.evaluate("document.getElementById('wsOverlay').hidden")
    page.focus("#wsBtnMoi")
    page.keyboard.press("Escape")
    assert not page.evaluate("document.getElementById('wsOverlay').hidden")
    assert not loi, loi


# ---- FIX-1 ----
def test_esc_dong_khi_focus_o_body(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _mo(page)
    page.locator("#wsHop .hint-text").click()
    assert page.evaluate("document.activeElement.tagName") == "BODY"
    page.keyboard.press("Escape")
    assert page.evaluate("document.getElementById('wsOverlay').hidden")
    assert page.evaluate("document.activeElement.id") == "btnWorkspace"
    assert not loi, loi


def _mo_tinh_nang(page, mo_man=True):
    if mo_man:
        _mo(page)
    page.locator('tr[data-slug="truong-hoc"] .menu-khac > summary').click()
    page.locator('button[data-slug="truong-hoc"][data-hanh-dong="tinh_nang"]').click()
    page.wait_for_selector("#wsTnTieuDe")


def test_dong_hop_tinh_nang_tra_focus_vao_man_chon(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _mo_tinh_nang(page)
    page.keyboard.press("Escape")
    page.wait_for_selector("#wsTnTieuDe", state="detached")
    assert _tat_ca_trong(page)
    assert not page.evaluate("document.getElementById('wsOverlay').hidden")   # chỉ đóng hộp con
    _mo_tinh_nang(page, mo_man=False)
    page.get_by_role("button", name="Huỷ").click()
    page.wait_for_selector("#wsTnTieuDe", state="detached")
    assert _tat_ca_trong(page)
    assert not loi, loi


def test_aria_modal_chi_co_khi_hien(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    gt = "(() => { const o = document.getElementById('wsOverlay'); return [o.getAttribute('role'), o.getAttribute('aria-modal')]; })()"
    assert page.evaluate(gt) == [None, None]
    _mo(page)
    assert page.evaluate(gt) == ["dialog", "true"]
    page.keyboard.press("Escape")
    assert page.evaluate(gt) == [None, None]
    assert not loi, loi


def test_esc_dong_menu_truoc_roi_moi_dong_man_chon(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _mo(page)
    page.locator('tr[data-slug="truong-hoc"] .menu-khac > summary').click()
    assert page.evaluate("!!document.querySelector('details.menu-khac[open]')")
    page.keyboard.press("Escape")
    assert not page.evaluate("!!document.querySelector('details.menu-khac[open]')")
    assert not page.evaluate("document.getElementById('wsOverlay').hidden")
    assert page.evaluate("document.activeElement.tagName") == "SUMMARY"
    page.keyboard.press("Escape")
    assert page.evaluate("document.getElementById('wsOverlay').hidden")
    assert not loi, loi
