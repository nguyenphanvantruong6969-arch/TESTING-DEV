"""Công tắc "Dùng điểm Wharton" ở bước luật của trình hướng dẫn tạo không gian làm việc
(Playwright + Chromium), và hàng tóm tắt ở bước xem lại.

  * ô chọn `#wzWharton` có chữ tiếng Việt / tiếng Anh, tắt sẵn;
  * bị khoá — và tự bỏ chọn — khi ưu tiên là "chỉ theo nhóm" hoặc điểm là "mỗi người một điểm";
  * bước xem lại có hàng `#rvWharton`; tạo xong thì `rules.wharton` được lưu vào CSDL;
  * chọn mẫu đã bật Wharton thì điền sẵn; giao diện tiếng Việt không lẫn chữ tiếng Anh và
    giao diện tiếng Anh không lẫn chữ có dấu.
"""

import os
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import workspace as ws  # noqa: E402
from api import PipelineAPI  # noqa: E402
from test_ws_giao_dien import DAU_VIET, _chu_cac_buoc_wizard  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402


@pytest.fixture
def mo_trang(tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def mo():
        goc = tmp_path / "goc"
        goc.mkdir(exist_ok=True)
        xuat = tmp_path / "xuat"
        xuat.mkdir(exist_ok=True)
        slug = ws.tao(str(goc), "Trường học", None)
        api = PipelineAPI(ws.duong_dan_db(str(goc), slug), thu_muc_xuat=str(xuat),
                          thu_muc_goc_ws=str(goc), ws_da_chon=True)
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(bypass_csp=True)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        return page, api, loi

    yield mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _toi_buoc_luat(page, ten="Đợt thử"):
    page.locator("#btnWorkspace").click()
    page.locator("#wsBtnMoi").click()
    page.fill("#wzTen", ten)
    page.locator("#wzTiep").click()
    page.locator("#wzTiep").click()
    page.wait_for_selector("#wzPriority")


def _cho_ten(page, ten):
    page.wait_for_function(
        "n => document.querySelector('#wsTenHienTai').textContent === n", arg=ten, timeout=10000)


def test_buoc_luat_co_o_wharton_tat_san_va_nhan_dung(mo_trang):
    page, _, loi = mo_trang()
    _toi_buoc_luat(page)
    assert page.locator("#wzWharton").count() == 1
    assert not page.locator("#wzWharton").is_checked()
    assert page.locator("#wzWharton").is_enabled()
    assert page.locator('label[for="wzWharton"]').inner_text() == "Dùng điểm quyết tâm"
    assert "100" in page.locator("#wzWharton").locator("xpath=../..").inner_text()
    assert not loi, loi


def test_nhan_tieng_anh(mo_trang):
    page, _, loi = mo_trang()
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("document.documentElement.lang === 'en'")
    _toi_buoc_luat(page)
    assert page.locator('label[for="wzWharton"]').inner_text() == "Use preference points"
    assert not loi, loi


def test_khoa_va_tu_bo_chon_khi_chuyen_sang_to_hop_khong_duoc(mo_trang):
    page, _, loi = mo_trang()
    _toi_buoc_luat(page)
    page.locator("#wzWharton").check()
    assert page.locator("#wzWharton").is_checked()

    page.select_option("#wzPriority", "tier")               # chỉ theo nhóm: không có điểm
    assert page.locator("#wzWharton").is_disabled()
    assert not page.locator("#wzWharton").is_checked()
    page.select_option("#wzPriority", "score+tier")         # nhóm trước rồi đến điểm: dùng được
    assert page.locator("#wzWharton").is_enabled()
    assert not page.locator("#wzWharton").is_checked()      # không tự bật lại
    page.locator("#wzWharton").check()

    page.select_option("#wzScoreScope", "per_person")       # mỗi người một điểm: không dùng được
    assert page.locator("#wzWharton").is_disabled()
    assert not page.locator("#wzWharton").is_checked()
    page.select_option("#wzScoreScope", "per_slot")
    assert page.locator("#wzWharton").is_enabled()
    assert not loi, loi


def test_bat_roi_tao_thi_rules_wharton_duoc_luu_va_xem_lai_co_hang_rvwharton(mo_trang):
    page, api, loi = mo_trang()
    _toi_buoc_luat(page, "Đợt Wharton")
    page.locator("#wzWharton").check()
    page.locator("#wzTiep").click()                          # sang bước xem lại
    assert page.locator("#rvWharton").inner_text() == "Bật"
    page.locator("#wzTao").click()
    _cho_ten(page, "Đợt Wharton")
    rules = api.get_workspace_config()["data"]["config"]["rules"]
    assert rules["wharton"] is True and rules["score_scope"] == "per_slot"
    assert rules["priority"] == "score"
    assert not loi, loi


def test_mac_dinh_tao_ra_wharton_tat_va_xem_lai_ghi_tat(mo_trang):
    page, api, loi = mo_trang()
    _toi_buoc_luat(page, "Đợt thường")
    page.locator("#wzTiep").click()
    assert page.locator("#rvWharton").inner_text() == "Tắt"
    page.locator("#wzTao").click()
    _cho_ten(page, "Đợt thường")
    assert api.get_workspace_config()["data"]["config"]["rules"]["wharton"] is False
    assert not loi, loi


def test_quay_lai_buoc_luat_giu_nguyen_o_da_chon(mo_trang):
    page, _, loi = mo_trang()
    _toi_buoc_luat(page)
    page.locator("#wzWharton").check()
    page.locator("#wzTiep").click()
    page.locator("#wzLui").click()
    assert page.locator("#wzWharton").is_checked()
    assert not loi, loi


def test_chon_mau_da_bat_wharton_thi_dien_san(mo_trang):
    page, api, loi = mo_trang()
    cfg = {"industry": "school", "rules": {"wharton": True}}
    slug = api.create_workspace("Gốc Wharton", cfg)["data"]["slug"]
    assert api.save_as_template(slug, "Mẫu Wharton")["ok"]
    page.locator("#btnWorkspace").click()
    page.locator("#wsBtnMoi").click()
    page.fill("#wzTen", "Bản sao")
    page.select_option("#wzMau", label="Mẫu Wharton")
    page.locator("#wzTiep").click()
    page.locator("#wzTiep").click()
    assert page.locator("#wzWharton").is_checked()
    assert not loi, loi


def test_tieng_viet_khong_lan_chu_tieng_anh_o_bo_loc_cua_buoc_luat(mo_trang):
    page, _, loi = mo_trang()
    page.locator("#btnWorkspace").click()
    page.wait_for_selector("#wsTieuDe")
    buoc = _chu_cac_buoc_wizard(page, 4)
    for chu in buoc:
        assert not re.search(r"workspace|zip", chu, re.I), chu
    assert "Dùng điểm quyết tâm" in buoc[2]
    assert not loi, loi


def test_tieng_anh_khong_lan_chu_co_dau_o_buoc_luat(mo_trang):
    page, _, loi = mo_trang()
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("document.documentElement.lang === 'en'")
    page.locator("#btnWorkspace").click()
    page.wait_for_selector("#wsTieuDe")
    buoc = _chu_cac_buoc_wizard(page, 3)
    assert "Use preference points" in buoc[2]
    for chu in buoc:
        assert not DAU_VIET.search(chu), chu
    assert not loi, loi
