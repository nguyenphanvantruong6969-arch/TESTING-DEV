# ruff: noqa: F811
"""Giao diện điểm quyết tâm sau khi dọn gọn (A13.4), Playwright + Chromium. Dữ liệu MÔ PHỎNG.

  * thanh tiến độ 0 đến 100 đổi đúng khi gõ, đổi màu khi đủ hoặc thừa;
  * ô sai tô màu ngay tại chỗ và có một dòng lỗi ngắn ngay dưới khung;
  * câu giải thích dài nằm sau nút (i); "Thao tác khác" đóng sẵn, mở ra vẫn làm đúng ba thao tác;
  * màn hẹp 800 px: hai khung xếp dọc, không tràn ngang; màn rộng: hai khung cạnh nhau;
  * tiếng Anh: không còn chữ có dấu và không còn chữ "Wharton".
Phép kiểm cuối nhìn vào CSDL, không chỉ nhìn chữ trên màn hình.
"""

import os
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _wharton import dong_bids  # noqa: E402
from test_giao_dien_wharton import (  # noqa: E402, F401
    DAU_VIET, _cho_buoc_3, _chon, _dem, _khung, _o, mo)
from test_giao_dien_wharton_quan_ly import _dung_du_lieu as _dung_ql  # noqa: E402
from test_giao_dien_wharton_quan_ly import _mo_thao_tac_khac  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402


def _thanh(page, quy):
    k = _khung(page, quy).locator(".wh-thanh")
    return (float(k.locator(".wh-thanh-day").evaluate("e => parseFloat(e.style.width) || 0")),
            k.get_attribute("class"), k.get_attribute("aria-valuenow"))


# ------------------------------------------------------------------ thanh tiến độ, lỗi tại chỗ

def test_thanh_tien_do_doi_theo_so_go_va_doi_mau_khi_du_hoac_thua(mo):
    page, api, loi = mo()
    _chon(page, "HS1")
    _cho_buoc_3(page)
    assert _thanh(page, 2)[0] == 0
    _o(page, "B").fill("60")
    assert _dem(page, 2) == "Đã dùng 60 / 100"
    rong, lop, now = _thanh(page, 2)
    assert rong == pytest.approx(60) and now == "60" and "is-du" not in lop and "is-vuot" not in lop
    _o(page, "C").fill("40")
    rong, lop, now = _thanh(page, 2)
    assert rong == pytest.approx(100) and "is-du" in lop
    _o(page, "C").fill("55")                                     # 115: thừa
    rong, lop, now = _thanh(page, 2)
    assert rong == pytest.approx(100) and "is-vuot" in lop and now == "100"
    # khung chỉ có một CLB: tự điền 100 nên thanh đã đầy và xanh
    assert _thanh(page, 1)[0] == pytest.approx(100) and "is-du" in _thanh(page, 1)[1]
    assert not loi, loi


def test_o_sai_to_mau_va_co_dong_loi_ngay_duoi_khung(mo):
    page, api, loi = mo()
    _chon(page, "HS1")
    _cho_buoc_3(page)
    khung = _khung(page, 2)
    assert khung.locator(".wh-loi").is_hidden()
    _o(page, "B").fill("-3")                                      # số âm
    assert "is-sai" in _o(page, "B").get_attribute("class")
    assert _o(page, "B").get_attribute("aria-invalid") == "true"
    assert khung.locator(".wh-loi").is_visible()
    assert "số nguyên từ 0" in khung.locator(".wh-loi").inner_text()
    _o(page, "B").fill("12.5")                                    # số thập phân
    assert "is-sai" in _o(page, "B").get_attribute("class")
    _o(page, "B").fill("70")
    _o(page, "C").fill("50")                                      # 120: thừa 20
    assert "is-sai" not in _o(page, "B").get_attribute("class")
    assert "thừa 20" in khung.locator(".wh-loi").inner_text()
    _o(page, "C").fill("20")                                      # 90: thiếu 10, chỉ nhắc nhẹ
    assert "thiếu 10" in khung.locator(".wh-loi").inner_text()
    assert "is-nhe" in khung.locator(".wh-loi").get_attribute("class")
    _o(page, "C").fill("30")                                      # đủ 100: hết lỗi
    assert khung.locator(".wh-loi").is_hidden()
    # lưu vẫn do server quyết định: ghi đúng vào CSDL
    page.locator("#btnSubmitWharton").click()
    page.wait_for_function(
        "() => document.getElementById('whartonFeedback').textContent.includes('Đã lưu')")
    assert ("HS1", "B", 2, 70) in dong_bids(api) and ("HS1", "C", 2, 30) in dong_bids(api)
    assert not loi, loi


def test_giai_thich_dai_nam_sau_nut_i(mo):
    page, api, loi = mo()
    _chon(page, "HS1")
    _cho_buoc_3(page)
    khung = _khung(page, 2)
    ghi = khung.locator(".wh-ghi-chu")
    assert ghi.is_hidden()
    nut = khung.locator(".wh-i")
    assert nut.get_attribute("aria-expanded") == "false" and nut.get_attribute("aria-label")
    nut.click()
    assert ghi.is_visible() and nut.get_attribute("aria-expanded") == "true"
    assert "cũng không thi" in ghi.inner_text() or "không thi" in ghi.inner_text()
    nut.click()
    assert ghi.is_hidden()
    assert not loi, loi


# ------------------------------------------------------------------ màn rộng và màn hẹp

def _hop(page, quy):
    return _khung(page, quy).bounding_box()


def test_man_rong_hai_khung_canh_nhau_man_hep_800_xep_doc_va_khong_tran_ngang(mo):
    page, api, loi = mo()
    page.set_viewport_size({"width": 1280, "height": 1200})
    _chon(page, "HS1")
    _cho_buoc_3(page)
    a, b = _hop(page, 1), _hop(page, 2)
    assert abs(a["y"] - b["y"]) < 4 and b["x"] > a["x"] + a["width"] - 4          # cạnh nhau
    page.set_viewport_size({"width": 800, "height": 1200})
    page.wait_for_timeout(250)
    a, b = _hop(page, 1), _hop(page, 2)
    assert b["y"] > a["y"] + a["height"] - 4 and abs(a["x"] - b["x"]) < 4         # xếp dọc
    assert page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth + 1")
    assert not loi, loi


def test_tieng_anh_khong_con_chu_co_dau_va_khong_con_wharton_o_buoc_3(mo):
    page, api, loi = mo()
    _chon(page, "HS1")
    _cho_buoc_3(page)
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function(
        "() => document.querySelector('#fbWhartonStep h3').textContent.startsWith('Step 3')")
    _o(page, "B").fill("-1")
    chu = page.locator("#fbWhartonStep").inner_text()
    chu_khong_ten = chu.replace("CLB", "")
    assert not DAU_VIET.search(chu_khong_ten), chu
    assert "wharton" not in chu.lower() and "Preference points" in chu
    assert not loi, loi


# ------------------------------------------------------------------ khối Quản lý: "Thao tác khác"

@pytest.fixture
def mo_ql(tmp_path, api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo(rong=1280):
        _dung_ql(api, True)
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", viewport={"width": rong, "height": 1400}, bypass_csp=True)
        page.set_default_timeout(8000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.locator('[data-tab="admin"]').click()
        page.wait_for_selector("#adminWhartonBlock:not([hidden]) #whQlBody tr")
        return page, api, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def test_thao_tac_khac_dong_san_ba_viec_hiem_nam_trong(mo_ql):
    page, api, loi = mo_ql()
    chi_tiet = page.locator("#whThaoTacKhac")
    assert chi_tiet.evaluate("d => d.open") is False
    for nut in ("#btnWhXoaTatCa", "#btnWhXemNhatKy"):
        assert page.locator(nut).is_hidden()
        assert chi_tiet.locator(nut).count() == 1                    # nằm TRONG mục
    assert chi_tiet.locator("#btnWhMoKhoa").count() == 1
    # bảng, ô tìm và bộ lọc ở ngoài và hiện sẵn
    for ngoai in ("#whQlTim", "#whLocQuy", "#whLocClb", "#whQlBody"):
        assert page.locator(ngoai).is_visible()
        assert chi_tiet.locator(ngoai).count() == 0
    # bộ lọc nằm trên một hàng (cùng độ cao) ở màn rộng
    ys = page.evaluate("""() => ['whQlTim','whLocQuy','whLocBuoi','whLocClb','whLocChiLoi']
        .map(id => { const r = document.getElementById(id).getBoundingClientRect(); return r.top + r.height / 2; })""")
    assert max(ys) - min(ys) < 12, ys
    # câu giải thích dài nằm sau nút (i)
    assert page.locator("#whQlMoTa").is_hidden()
    page.locator("#btnWhThongTin").click()
    assert page.locator("#whQlMoTa").is_visible()
    assert not loi, loi


def test_thao_tac_khac_mo_ra_xoa_tat_ca_van_xoa_va_xem_nhat_ky_van_ra(mo_ql):
    page, api, loi = mo_ql()
    assert dong_bids(api)
    _mo_thao_tac_khac(page)
    page.locator("#btnWhXemNhatKy").click()
    assert page.locator("#whNkChonEm").is_visible()                  # chưa chọn em: nhắc mở một em
    page.locator("#btnWhXoaTatCa").click()
    page.locator("#whXoaTatCaGo").fill("XOA")
    page.locator("#btnWhXoaTatCaXn").click()
    page.wait_for_function("() => document.querySelectorAll('#whQlBody tr[data-student-id]').length >= 0")
    page.wait_for_timeout(500)
    assert dong_bids(api) == []
    assert not loi, loi


def test_tieng_anh_khoi_quan_ly_khong_con_chu_co_dau_va_khong_wharton(mo_ql):
    page, api, loi = mo_ql()
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("() => document.getElementById('whThaoTacKhac').textContent.includes('More actions')")
    _mo_thao_tac_khac(page)
    chu = page.locator("#adminWhartonBlock").inner_text()
    sach = re.sub(r"Nguyễn Văn Bình|Trần Thị Lan|Lê Hoàng Nam", "", chu)
    assert not DAU_VIET.search(sach), sach
    assert "wharton" not in chu.lower()
    assert not loi, loi
