"""FA-UI-2 (Playwright + Chromium): bảng CLB ở thẻ Quản lý có cột Loại, Điểm sàn, Tối thiểu, Sức chứa phòng,
Giữ chỗ (số em) CHỈ khi workspace bật xếp theo loại CLB và huy chương; tắt thì bảng như cũ. Dữ liệu MÔ PHỎNG.
"""
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _fa import bat_fa, dung_fa_clb, dung_hs_fa, giu_cho  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COT_CU = ["Mã CLB", "Tên", "Chỉ tiêu", "Suất ưu tiên", "Nhóm ưu tiên"]
COT_FA = ["Loại", "Điểm sàn", "Tối thiểu", "Sức chứa phòng", "Giữ chỗ"]


def _du_lieu(api, bat):
    dung_fa_clb(api, T=(30, "TU_DO", None, None, 40), G=(5, "GIOI_HAN", None, 3), S=(4, "TUYEN_CHON", 6))
    dung_hs_fa(api, "s1", "s2")
    giu_cho(api, ("G", "s1"), ("G", "s2"))
    if bat:
        bat_fa(api)


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo(bat=True, du_lieu=_du_lieu):
        du_lieu(api, bat)
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", viewport={"width": 1280, "height": 1400}, bypass_csp=True)
        page.set_default_timeout(8000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.locator('[data-tab="admin"]').click()
        page.wait_for_selector("#adminClubTableBody tr")
        return page, api, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _tieu_de(page):
    return page.eval_on_selector_all(
        "table:has(#adminClubTableBody) thead th",
        "ths => ths.filter(t => t.offsetParent !== null && !t.querySelector('.sr-only'))"
        ".map(t => t.textContent.trim())")


def _hang(page, cid):
    return [x.strip() for x in page.locator('#adminClubTableBody tr[data-club-id="%s"] td.cot-fa' % cid)
            .all_inner_texts()]


def test_fa_tat_bang_clb_nhu_cu(mo):
    page, _, loi = mo(bat=False)
    assert _tieu_de(page) == COT_CU
    assert page.locator("table:has(#adminClubTableBody) .cot-fa").count() == 0   # không thêm phần tử nào
    assert not loi, loi


def test_fa_bat_co_cot_va_gia_tri(mo):
    page, _, loi = mo(bat=True)
    assert _tieu_de(page) == COT_CU + COT_FA
    assert _hang(page, "T") == ["Tự do", "—", "—", "40", "0"]
    assert _hang(page, "G") == ["Giới hạn", "—", "3", "—", "2"]
    assert _hang(page, "S") == ["Tuyển chọn", "6", "—", "—", "0"]
    assert not loi, loi


def test_tieng_anh(mo):
    page, _, loi = mo(bat=True)
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("document.documentElement.lang === 'en'")
    page.wait_for_function("() => document.querySelector('#adminClubTableBody tr[data-club-id=\"S\"]')"
                           " && document.querySelector('#adminClubTableBody tr[data-club-id=\"S\"]')"
                           ".innerText.includes('Selective')")
    assert "Room capacity" in _tieu_de(page)
    assert not loi, loi
