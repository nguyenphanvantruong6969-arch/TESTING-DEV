"""T3-L1 giao diện (Chromium, qua `browser_host`): chữ và hiển thị nhỏ ở thẻ chạy, nhập điểm, hộp tạo workspace.
Dữ liệu MÔ PHỎNG dựng trong test. Máy không có playwright/Chromium thì bỏ qua cả tệp."""

import os
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from _wharton import tat_wharton  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def api(api):
    tat_wharton(api)
    return api


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo():
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", viewport={"width": 1280, "height": 1000}, bypass_csp=True)
        page.set_default_timeout(8000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        return page, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _du_lieu(api, n=6):
    api.create_or_update_club("clb_a", "CLB A", 3)
    for i in range(1, n + 1):
        sid = "HS%02d" % i
        api.create_student_if_missing(sid, "Học sinh %02d" % i)
        api.submit_test_selection(sid, ["clb_a"])
        api.submit_preferences(sid, ["clb_a"])


# ---------------------------------------------------------------- T3-05
def test_o_ma_boc_tham_nam_trong_muc_nang_cao_thu_gon(api, mo):
    _du_lieu(api)
    page, loi = mo()
    assert page.eval_on_selector("#nangCao", "e => e.open") is False
    assert page.locator("#seedInput").is_hidden()
    assert page.input_value("#seedInput") == "42"
    assert page.locator("#seedLockHint").count() == 0  # bỏ dòng chữ đơn thứ hai
    page.locator("#nangCao > summary").click()
    assert page.locator("#seedInput").is_visible()
    assert not loi


def test_sau_khi_khoa_chi_con_mot_dong_bao_da_boc_tham(api, mo):
    _du_lieu(api)
    assert api.run_pipeline(42)["ok"]
    page, _ = mo()
    page.wait_for_function("document.querySelector('#stbLockLine').textContent.indexOf('Đã bốc thăm lúc') !== -1")
    dong = page.inner_text("#stbLockLine")
    assert re.search(r"Đã bốc thăm lúc \d{2}/\d{2}/\d{4} \d{2}:\d{2}\.", dong), dong
    assert "Bốc thăm lại" in dong and "số khởi tạo" not in dong.lower()


# ---------------------------------------------------------------- T3-08
def test_dai_so_lieu_khong_con_o_da_nop_nguyen_vong_va_gio_dang_nguoi_doc(api, mo):
    _du_lieu(api)
    assert api.run_pipeline(42)["ok"]
    page, _ = mo()
    assert page.locator("#statPrefs").count() == 0
    assert page.locator("#statusStrip .strip-item").count() == 3  # học sinh, CLB, đã xếp
    page.wait_for_function("document.querySelector('#lastRunLine').textContent.indexOf('Chạy gần nhất') !== -1")
    dong = page.inner_text("#lastRunLine")
    assert re.search(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}", dong) and "T" not in dong.split(":", 1)[1][:12]
    assert "khởi tạo" not in dong and "202" in dong


# ---------------------------------------------------------------- T3-09
def test_the_lich_su_chi_hien_tu_hai_lan_chay(api, mo):
    _du_lieu(api)
    assert api.run_pipeline(42)["ok"]
    page, _ = mo()
    page.wait_for_function("document.querySelector('#stbLockLine').textContent.length > 0")
    assert page.locator("#historyPanel").is_hidden()
    assert api.run_pipeline(42)["ok"]
    page.reload()
    page.wait_for_selector("#dropZone")
    page.wait_for_function("!document.querySelector('#historyPanel').hidden")
    assert page.locator("#historyPanel").is_visible()


# ---------------------------------------------------------------- T3-13 / T3-30
def test_bo_ten_thuat_toan_khoi_giao_dien_va_doi_ten_tab_xoa(api, mo):
    page, _ = mo()
    assert page.locator(".brand-sub").count() == 0
    assert page.title() == "Sắp xếp Câu lạc bộ" and "RB-DA" not in page.title()
    assert page.inner_text('.nav-item[data-tab="pipeline"]').strip().endswith("Xếp CLB")
    page.locator('[data-tab="admin"]').click()
    assert page.inner_text("#qlTabDuLieu").strip() == "Xoá dữ liệu"


# ---------------------------------------------------------------- T3-36
def test_bang_tien_do_cham_bo_cot_ma_clb_va_nut_cham_khong_mui_ten(api, mo):
    _du_lieu(api)
    page, _ = mo()
    page.locator('.nav-item[data-tab="scoring"]').click()
    page.wait_for_selector("#scoringOverviewBody .btn-row-link")
    dau = page.eval_on_selector_all("#scoringClubPanel thead th", "e => e.map(x => x.textContent.trim())")
    assert "Mã CLB" not in dau and dau[0] == "Tên"
    nut = page.locator("#scoringOverviewBody .btn-row-link").first
    assert nut.inner_text().strip() == "Chấm" and "btn-secondary" in nut.get_attribute("class")
    assert page.locator("#scoringOverviewBody .scoring-progress-bar").count() == 0
