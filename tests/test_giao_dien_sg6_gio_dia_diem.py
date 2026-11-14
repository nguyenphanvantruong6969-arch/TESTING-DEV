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


# ---- bước 1 của "Chuẩn bị đợt": tải Phiếu thật qua ô chọn tệp (FIX-1) ---------------
from test_giao_dien_fa_m7_nguon import _xlsx_phieu, mo as mo_buoc1  # noqa: E402,F401
import chuyen_phieu_clb as pc  # noqa: E402


def _dong_tu_do(ten):
    """Mỗi buổi cần ít nhất một CLB Tự do (luật FA), nên phiếu thử luôn có một dòng như vậy."""
    d = _dong_phieu(ten, "", "")
    d[pc.C_MO_NHOM], d[pc.C_PHONG], d[pc.C_CHO], d[pc.C_LY_DO] = "Có", "30", "", ""
    return d


def _dong_phieu(ten, gio, dia):
    d = {h: "" for h in pc.TIEU_DE_PHIEU}
    d.update({pc.TIEU_DE_PHIEU[pc.C_TEN]: ten, pc.TIEU_DE_PHIEU[pc.C_BUOI]: "Thứ 2",
              pc.TIEU_DE_PHIEU[pc.C_GIO]: gio, pc.TIEU_DE_PHIEU[pc.C_DIA_DIEM]: dia,
              pc.TIEU_DE_PHIEU[pc.C_MO_NHOM]: "Không", pc.TIEU_DE_PHIEU[pc.C_CHO]: "20",
              pc.TIEU_DE_PHIEU[pc.C_LY_DO]: "Phòng", pc.TIEU_DE_PHIEU[pc.C_CAN_THI]: "Không"})
    return [d[h] for h in pc.TIEU_DE_PHIEU]


def _tieu_de(page):
    return page.eval_on_selector_all("#cb-b1-bang thead th", "hs => hs.map(h => h.textContent.trim())")


@pytest.mark.parametrize("ngon,nhan", [("vi", ["Giờ", "Địa điểm"]), ("en", ["Time", "Place"])])
def test_buoc_1_hien_hai_cot_khi_phieu_co_gio(mo_buoc1, tmp_path, ngon, nhan):  # noqa: F811
    page, loi = mo_buoc1()
    if ngon == "en":
        page.evaluate("window.I18N.setLang('en')")
        page.wait_for_function("document.documentElement.lang === 'en'")
    page.locator("#cb-b1-tep").set_input_files(_xlsx_phieu(tmp_path, [
        _dong_phieu("CLB Cờ vua", GIO, DIA), _dong_phieu("CLB Bóng rổ", "", ""), _dong_tu_do("CLB Nhiếp ảnh")]))
    page.wait_for_selector('#cb-buoc-1 [data-trang-thai="xanh"]')
    assert _tieu_de(page)[-2:] == nhan
    assert len(_tieu_de(page)) == 6
    chu = page.inner_text("#cb-b1-bang")
    assert GIO in chu and DIA in chu
    assert not loi, loi


def test_buoc_1_phieu_khong_gio_van_bon_cot(mo_buoc1, tmp_path):  # noqa: F811
    page, loi = mo_buoc1()
    page.locator("#cb-b1-tep").set_input_files(_xlsx_phieu(tmp_path, [
        _dong_phieu("CLB Cờ vua", "", ""), _dong_phieu("CLB Bóng rổ", "", ""), _dong_tu_do("CLB Nhiếp ảnh")]))
    page.wait_for_selector('#cb-buoc-1 [data-trang-thai="xanh"]')
    assert len(_tieu_de(page)) == 4
    assert not loi, loi
