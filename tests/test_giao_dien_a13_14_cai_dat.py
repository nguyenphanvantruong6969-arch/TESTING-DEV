"""A13.14, hộp Cài đặt (Playwright + Chromium). Dữ liệu MÔ PHỎNG.

Bánh răng ở thanh trái mở được từ mọi tab, Esc đóng; đổi luật (có hộp xác nhận khi đã chạy xếp);
giao diện (ngôn ngữ, hiệu ứng, cỡ chữ); dữ liệu và sao lưu (xuất / nhập zip, đặt lại có xác nhận); VI + EN.
"""

import glob
import os
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import cau_hinh_ws as ch  # noqa: E402
import workspace as ws  # noqa: E402
from api import PipelineAPI  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from _wharton import dung_clb  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _du_lieu(api, chay):
    dung_clb(api, A=2, B=2)
    for sid in ("HS1", "HS2", "HS3"):
        assert api.create_student_if_missing(sid, "Em " + sid)["ok"]
        assert api.submit_preferences(sid, ["A", "B"])["ok"]
    if chay:
        assert api.run_pipeline(seed=3)["ok"]


@pytest.fixture
def mo(tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo(chay=False, co_ws=True, color_scheme="light", dqt=False):
        if co_ws:
            goc = str(tmp_path / "goc")
            os.makedirs(goc, exist_ok=True)
            slug = ws.tao_truong_hoc_mac_dinh(goc)
            api = PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_goc_ws=goc,
                              thu_muc_xuat=str(tmp_path / "xuat"))
            os.makedirs(str(tmp_path / "xuat"), exist_ok=True)
            # Trường học mặc định bật Điểm quyết tâm (A13.13); các ca này không nhập điểm nên TẮT tường minh.
            ch.ghi_cau_hinh(api.db_path, ch.tron_len(ch.doc_cau_hinh(api.db_path), {"rules": {"wharton": dqt}}))
        else:
            api = PipelineAPI(str(tmp_path / "app.db"))
        _du_lieu(api, chay)
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", viewport={"width": 1280, "height": 1000}, bypass_csp=True,
                           color_scheme=color_scheme)
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


def _mo_hop(page):
    page.click("#btnCaiDat")
    page.wait_for_selector("#caiDatOverlay:not([hidden]) #cdWharton")


def _luat(api):
    return ch.doc_cau_hinh(api.db_path)["rules"]


# ------------------------------------------------------------------ mở / đóng

def test_banh_rang_co_nhan_mo_tu_moi_tab_esc_dong_va_tra_tieu_diem(mo):
    page, api, loi = mo()
    nut = page.locator("#btnCaiDat")
    assert nut.get_attribute("aria-label") == "Mở cài đặt"
    assert page.locator("#btnLangToggle").is_visible()          # nút EN vẫn ở thanh trái
    for tab in ("pipeline", "results", "fallback", "admin", "scoring"):
        page.locator('[data-tab="%s"]' % tab).click()
        assert nut.is_visible()
        nut.click()
        page.wait_for_selector("#caiDatOverlay:not([hidden])")
        assert page.locator("#caiDatOverlay").get_attribute("role") == "dialog"
        assert page.locator("#caiDatOverlay").get_attribute("aria-modal") == "true"
        page.keyboard.press("Escape")
        page.wait_for_selector("#caiDatOverlay", state="hidden")
        assert page.evaluate("document.activeElement.id") == "btnCaiDat"
    assert not loi, loi


def test_nut_dong_va_bam_ra_ngoai_cung_dong(mo):
    page, api, loi = mo()
    _mo_hop(page)
    page.click("#caiDatDong")
    page.wait_for_selector("#caiDatOverlay", state="hidden")
    _mo_hop(page)
    page.mouse.click(5, 500)
    page.wait_for_selector("#caiDatOverlay", state="hidden")
    assert not loi, loi


def test_tab_khong_roi_khoi_hop(mo):
    page, api, loi = mo()
    _mo_hop(page)
    for _ in range(60):
        page.keyboard.press("Tab")
        assert page.evaluate("document.getElementById('caiDatOverlay').contains(document.activeElement)")
    assert not loi, loi


# ------------------------------------------------------------------ luật

def test_doi_luat_chua_chay_luu_ngay_khong_hoi_xac_nhan(mo):
    page, api, loi = mo(chay=False)
    _mo_hop(page)
    page.fill("#cdMaxChoices", "7")
    page.select_option("#cdPriority", "score+tier")
    page.select_option("#cdTierMode", "strict")
    page.fill("#cdTiers", "Khối 12\nKhối 11")
    page.click("#cdLuu")
    page.wait_for_selector("#toastStack .toast", state="attached")
    assert page.locator("#cdXacNhan").is_hidden()
    luat = _luat(api)
    assert luat["max_choices"] == 7 and luat["priority"] == "score+tier"
    assert luat["tier_mode"] == "strict" and luat["tiers"] == ["Khối 11".replace("11", "12"), "Khối 11"]
    assert glob.glob(api.db_path + ".bak-*") == []
    assert not loi, loi


def test_da_chay_xep_hien_hop_xac_nhan_huy_khong_ghi_dong_y_thi_sao_luu_roi_ghi(mo):
    page, api, loi = mo(chay=True)
    _mo_hop(page)
    page.fill("#cdMaxChoices", "6")
    page.click("#cdLuu")
    page.wait_for_selector("#cdXacNhan:not([hidden])")
    chu = page.locator("#cdXacNhan").inner_text()
    assert "1 lần chạy xếp" in chu and "kết quả khác" in chu, chu
    assert _luat(api)["max_choices"] != 6
    page.click("#cdXacNhanHuy")
    assert page.locator("#cdXacNhan").is_hidden() and _luat(api)["max_choices"] != 6
    page.click("#cdLuu")
    page.wait_for_selector("#cdXacNhan:not([hidden])")
    page.click("#cdXacNhanDongY")
    page.wait_for_selector("#cdXacNhan", state="hidden")
    page.wait_for_function("() => document.querySelector('#toastStack').textContent.includes('app.db.bak-')")
    assert _luat(api)["max_choices"] == 6
    assert len(glob.glob(api.db_path + ".bak-*")) >= 1
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM run_history").fetchone()[0] == 1
    # khoá bốc thăm vẫn khoá và được nói rõ trong hộp
    assert "đang khoá" in page.locator("#cdKhoa").inner_text()
    assert not loi, loi


def test_luat_sai_bao_loi_theo_hop_dong_va_khong_ghi(mo):
    page, api, loi = mo()
    _mo_hop(page)
    truoc = _luat(api)
    page.fill("#cdMaxChoices", "0")
    page.click("#cdLuu")
    page.wait_for_selector("#cdLoi:not([hidden])")
    assert page.locator("#cdLoi").inner_text().strip()
    assert _luat(api) == truoc
    # trần thấp hơn dữ liệu đang có: HS có 2 nguyện vọng
    page.fill("#cdMaxChoices", "1")
    page.click("#cdLuu")
    page.wait_for_function("() => document.querySelector('#cdLoi').textContent.includes('Chưa đổi được')")
    assert _luat(api) == truoc
    assert not loi, loi


def test_diem_quyet_tam_bat_tat_va_o_tu_khoa_khi_to_hop_khong_dung_duoc(mo):
    page, api, loi = mo(dqt=True)
    assert _luat(api)["wharton"] is True
    _mo_hop(page)
    assert page.locator("#cdWharton").is_checked()
    page.uncheck("#cdWharton")
    page.click("#cdLuu")
    page.wait_for_function("() => document.querySelector('#toastStack .toast')")
    assert _luat(api)["wharton"] is False
    assert page.evaluate("WHARTON_BAT") is False
    page.check("#cdWharton")
    page.select_option("#cdPriority", "tier")                  # xếp theo nhóm: Điểm quyết tâm không dùng được
    assert page.locator("#cdWharton").is_disabled() and not page.locator("#cdWharton").is_checked()
    page.select_option("#cdPriority", "score")
    assert page.locator("#cdWharton").is_enabled()
    assert not loi, loi


def test_ngon_ngu_en_nhan_va_hop_xac_nhan(mo):
    page, api, loi = mo(chay=True)
    _mo_hop(page)
    page.click("#cdNgonEn")
    page.wait_for_function("() => document.getElementById('caiDatTieuDe').textContent === 'Settings'")
    assert page.locator("#cdLuu").inner_text() == "Save rules"
    assert page.locator("#btnCaiDat").get_attribute("aria-label") == "Open settings"
    page.fill("#cdMaxChoices", "5")                           # đổi ngôn ngữ giữa chừng không mất ô đang sửa
    page.click("#cdNgonVi")
    page.wait_for_function("() => document.getElementById('caiDatTieuDe').textContent === 'Cài đặt'")
    assert page.input_value("#cdMaxChoices") == "5"
    page.click("#cdNgonEn")
    page.wait_for_function("() => document.getElementById('caiDatTieuDe').textContent === 'Settings'")
    page.click("#cdLuu")
    page.wait_for_selector("#cdXacNhan:not([hidden])")
    chu = page.locator("#cdXacNhan").inner_text()
    assert "run 1 time(s)" in chu and "different results" in chu, chu
    assert not re.search(r"[Tt]ầng|\bWharton\b", page.locator("#caiDatHop").inner_text())
    assert not loi, loi


# ------------------------------------------------------------------ giao diện

def test_co_chu_ba_muc_luu_qua_tai_lai(mo):
    page, api, loi = mo()
    _mo_hop(page)
    assert page.locator('[data-cd-co="vua"]').get_attribute("aria-pressed") == "true"
    page.click('[data-cd-co="lon"]')
    assert page.evaluate("document.documentElement.classList.contains('co-chu-lon')")
    assert page.locator('[data-cd-co="lon"]').get_attribute("aria-pressed") == "true"
    page.click('[data-cd-co="rat_lon"]')
    assert page.evaluate("document.documentElement.classList.contains('co-chu-rat_lon')")
    assert not page.evaluate("document.documentElement.classList.contains('co-chu-lon')")
    page.reload()
    page.wait_for_selector("#btnCaiDat")
    assert page.evaluate("document.documentElement.classList.contains('co-chu-rat_lon')")
    _mo_hop(page)
    page.click('[data-cd-co="vua"]')
    assert page.evaluate("[...document.documentElement.classList].filter(c => c.startsWith('co-chu-')).join()") == "co-chu-vua"
    assert page.evaluate("getComputedStyle(document.body).zoom") == "1"
    assert not loi, loi


def test_ngon_ngu_trong_hop_va_nut_en_o_thanh_trai_dong_bo(mo):
    page, api, loi = mo()
    _mo_hop(page)
    assert page.locator("#cdNgonVi").get_attribute("aria-pressed") == "true"
    page.click("#cdNgonEn")
    page.wait_for_function("() => document.getElementById('btnLangToggle').textContent.trim() === 'VI'")
    assert page.locator("#cdNgonEn").get_attribute("aria-pressed") == "true"
    assert not loi, loi


# ------------------------------------------------------------------ dữ liệu và sao lưu

def test_nhom_du_lieu_co_ws_xuat_zip_mo_duoc_khong_ws_thi_khoa(mo, tmp_path):
    page, api, loi = mo()
    _mo_hop(page)
    assert page.locator("#cdThuMucXuat").inner_text() == str(tmp_path / "xuat")
    assert page.locator("#cdThuMucSaoLuu").inner_text() == os.path.dirname(api.db_path)
    assert page.locator("#cdXuatZip").is_enabled() and page.locator("#cdNhapZip").is_enabled()
    page.click("#cdXuatZip")
    page.wait_for_function("() => document.querySelector('#toastStack').textContent.includes('.zip')")
    assert glob.glob(str(tmp_path / "xuat" / "*.zip"))
    assert not loi, loi


def test_khong_workspace_xuat_nhap_zip_bi_khoa_co_giai_thich(mo):
    page, api, loi = mo(co_ws=False)
    _mo_hop(page)
    assert page.locator("#cdXuatZip").is_disabled() and page.locator("#cdNhapZip").is_disabled()
    assert page.locator("#cdChiWs").is_visible()
    assert not loi, loi


def test_dat_lai_du_lieu_phai_co_hop_xac_nhan(mo):
    page, api, loi = mo(chay=True)
    _mo_hop(page)
    page.click("#cdResetHs")
    page.wait_for_selector("#cdResetXn:not([hidden])")
    page.click("#cdResetHuy")
    assert page.locator("#cdResetXn").is_hidden()
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 3
    page.click("#cdResetHs")
    page.click("#cdResetDongY")
    page.wait_for_function("() => document.querySelector('#toastStack').textContent.includes('app.db.bak-')")
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0
        assert cur.execute("SELECT COUNT(*) FROM clubs").fetchone()[0] == 2      # giữ CLB
        assert cur.execute("SELECT COUNT(*) FROM run_history").fetchone()[0] == 1  # lịch sử còn
    assert not loi, loi


# ------------------------------------------------------------------ tông kem, đọc được

def test_hop_cai_dat_tong_kem_doc_duoc_ke_ca_khi_he_dieu_hanh_toi(mo):
    page, api, loi = mo(color_scheme="dark")
    _mo_hop(page)

    def kenh(c):
        return [int(x) for x in re.findall(r"\d+", c)[:3]]

    def do_sang(c):
        def k(v):
            v /= 255
            return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
        r, g, b = [k(x) for x in kenh(c)]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def tuong_phan(a, b):
        x, y = sorted([do_sang(a), do_sang(b)], reverse=True)
        return (x + 0.05) / (y + 0.05)
    mau = "s => { const c = getComputedStyle(document.querySelector(s)); return [c.color, c.backgroundColor]; }"
    nen = page.evaluate(mau, "#caiDatHop")[1]
    assert sum(kenh(nen)) / 3 > 235, nen
    for sel in ("#caiDatTieuDe", "#cdTenGiaoDien", "#cdNgonVi", "#btnMotionToggle", "#cdLuu", "#cdResetHs",
                "#cdThuMucXuat", ".cd-nhan"):
        chu, nen_phan_tu = page.evaluate(mau, sel)
        if kenh(nen_phan_tu) == [0, 0, 0] and "rgba(0, 0, 0, 0)" in nen_phan_tu:
            nen_phan_tu = nen
        assert tuong_phan(chu, nen_phan_tu) >= 4.5, (sel, chu, nen_phan_tu)
    assert not loi, loi
