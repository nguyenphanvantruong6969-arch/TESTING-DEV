# -*- coding: utf-8 -*-
"""SG-11a: vệ sinh giao diện (M6, M7, L1, L4, L5) trong TRÌNH DUYỆT THẬT.

Báo cáo của Fable không đọc được (D-A1) nên mỗi lỗi được kiểm từ dòng đặc tả:
M6 color-scheme sáng; M7 tab Kết quả ở 1024 px không tràn ngang; L1 .hs-buoi-nhan dùng
--gold-text; L4 tab Nhập điểm cùng bề rộng nội dung với tab cạnh nó; L5 một dòng giải thích
khi nút xuất chỉ-FA bị ẩn.
"""
import io
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from _wharton import tat_wharton  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BO_MAU = os.path.join(GOC, "du_lieu_test", "bo_nhieu_buoi")


@pytest.fixture
def may(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    tat_wharton(api)
    for ten in ("NHIEUBUOI_01_danh_sach_CLB.csv",
                "NHIEUBUOI_02_chon_CLB_muon_thi.csv",
                "NHIEUBUOI_03_xep_hang_nguyen_vong.csv"):
        with io.open(os.path.join(BO_MAU, ten), encoding="utf-8-sig") as f:
            assert api.import_csv_auto(f.read())["ok"]
    assert api.run_pipeline(seed=42)["ok"]
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])

    def mo(rong=1366, cao=768, **kw):
        ctx = br.new_context(viewport={"width": rong, "height": cao}, bypass_csp=True, **kw)
        page = ctx.new_page()
        page.goto(url)
        page.wait_for_selector(".nav-item")
        return page

    yield mo, api
    br.close()
    pw.stop()


def test_m6_color_scheme_sang_du_may_o_che_do_toi(may):
    mo, _ = may
    page = mo(color_scheme="dark")
    assert page.evaluate("getComputedStyle(document.documentElement).colorScheme") == "light"


def _do_tran(page, vung):
    """Tran trang, phan tu vuot man hinh, va moi bang rong hon khung chua no (phai cuon ngang)."""
    return page.evaluate("""(vung) => {
      const se = document.scrollingElement;
      const bang = [];
      for (const t of document.querySelectorAll(vung + ' table')) {
        const c = t.closest('.scroll-x') || t.parentElement;
        if (t.offsetParent && t.scrollWidth > c.clientWidth + 1) bang.push(t.id + ' ' + c.clientWidth + '/' + t.scrollWidth);
      }
      return {trang: se.scrollWidth - se.clientWidth, bang: bang};
    }""", vung)


@pytest.mark.parametrize("rong", [1024, 1366, 1920])
@pytest.mark.parametrize("cach", ["clb", "ma"])
def test_m7_ket_qua_khong_tran_ngang(may, rong, cach):
    mo, _ = may
    page = mo(rong, 768)
    page.click('.nav-item[data-tab="results"]')
    page.wait_for_function("document.querySelectorAll('#view-results table tbody tr').length > 0")
    page.click('#view-results [data-kq="%s"]' % cach)
    page.wait_for_timeout(600)
    if rong < 1366 or cach == "clb":
        kq = _do_tran(page, "#view-results")
        assert kq["trang"] <= 0 and kq["bang"] == [], kq


@pytest.mark.parametrize("rong", [1024, 1366, 1920])
def test_m7_chi_tiet_va_xuat_tep_khong_tran_ngang(may, rong):
    mo, _ = may
    page = mo(rong, 768)
    page.click('.nav-item[data-tab="others"]')
    page.wait_for_timeout(1000)
    kq = _do_tran(page, "#view-others")
    assert kq["trang"] <= 0 and kq["bang"] == [], kq


def test_l1_hs_buoi_nhan_dung_gold_text(may):
    mo, _ = may
    page = mo()
    mau = page.evaluate("""() => {
      const e = document.createElement('span'); e.className = 'hs-buoi-nhan'; document.body.appendChild(e);
      const t = document.createElement('span'); document.body.appendChild(t);
      t.style.color = 'var(--gold-text)';
      return [getComputedStyle(e).color, getComputedStyle(t).color];
    }""")
    assert mau[0] == mau[1]


@pytest.mark.parametrize("rong", [1366, 1920])
def test_l4_nhap_diem_cung_be_rong_noi_dung_voi_tab_canh(may, rong):
    mo, _ = may
    page = mo(rong, 900)
    do = {}
    for tab in ("scoring", "results"):
        page.click('.nav-item[data-tab="%s"]' % tab)
        do[tab] = page.evaluate("""(t) => {
          const v = document.querySelector('#view-' + t);
          const r = v.getBoundingClientRect(); return Math.round(r.width);
        }""", tab)
    assert do["scoring"] == do["results"], do


FA_NUT = ("btnXuatLyDo", "btnXuatNhuCau", "btnXuatGoiY", "btnXuatBienBan")


def _trang_xuat(page):
    page.click('.nav-item[data-tab="others"]')
    page.wait_for_timeout(600)
    return page.evaluate("""(ids) => ({
      nut: ids.map(i => !document.getElementById(i).hidden),
      goi_y: Array.from(document.querySelectorAll('[data-sg11a-xuat-fa]')).filter(e => !e.hidden && e.offsetParent).length,
      van: (document.querySelector('[data-sg11a-xuat-fa]') || {}).textContent || ''
    })""", list(FA_NUT))


def test_l5_khong_fa_mot_dong_giai_thich_nut_bi_an(may):
    mo, api = may
    page = mo()
    # vao tab Ket qua truoc de js/03 dat cac nut hidden theo co FA
    page.click('.nav-item[data-tab="results"]')
    page.wait_for_timeout(600)
    kq = _trang_xuat(page)
    assert kq["nut"] == [False] * 4
    assert kq["goi_y"] == 1
    assert kq["van"].strip() and "fa_" not in kq["van"] and "{" not in kq["van"]


def test_l5_co_fa_giau_dong_giai_thich_va_hien_nut(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    from test_giao_dien_fa_ket_qua import _fa
    _fa(api)
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    try:
        page = br.new_page(viewport={"width": 1400, "height": 1400}, bypass_csp=True)
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.click('.nav-item[data-tab="others"]')
        page.wait_for_selector("#btnXuatLyDo:not([hidden])")
        kq = _trang_xuat(page)
        assert kq["nut"] == [True] * 4
        assert kq["goi_y"] == 0
    finally:
        br.close()
        pw.stop()
