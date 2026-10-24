"""Từ vựng của workspace trên MÀN HÌNH THẬT (Playwright + Chromium): công ty thấy "nhân viên",
"dự án"…; en trống rơi về vi; tiêu đề cửa sổ; đổi workspace đổi chữ.

Phần chữ thuần (không cần trình duyệt) nằm ở tests/test_ws_nhan.py.
"""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import workspace as ws  # noqa: E402
from api import PipelineAPI  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402

CONG_TY = {
    "industry": "company",
    "labels": {
        "person": {"vi": "Nhân viên", "en": "Employee"},
        "slot": {"vi": "Dự án", "en": "Project"},
        "session": {"vi": "Ca", "en": "Shift"},
        "group": {"vi": "Nhóm dự án", "en": "Project team"},
        "score": {"vi": "Điểm", "en": "Score"},
    },
}


@pytest.fixture
def mo_trang(tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def mo(workspaces=(("Công ty ABC", CONG_TY),), mo_slug=None, che_do_ws=True):
        goc = tmp_path / "goc"
        goc.mkdir(exist_ok=True)
        slugs = [ws.tao(str(goc), ten, cfg) for ten, cfg in workspaces]
        db = ws.duong_dan_db(str(goc), mo_slug or slugs[0])
        api = PipelineAPI(db, thu_muc_goc_ws=str(goc) if che_do_ws else None)
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


def _chu_the(page, selector):
    return page.locator(selector).inner_text().strip()


def _cho_chu(page, selector, chu):
    page.wait_for_function(
        "([s, c]) => document.querySelector(s).textContent.trim() === c",
        arg=[selector, chu], timeout=10000)


def test_cong_ty_thay_tu_cua_minh_tren_man_hinh(mo_trang):
    page, api, loi = mo_trang()
    _cho_chu(page, "#statStudents + .strip-label", "nhân viên")
    assert _chu_the(page, "#statClubs + .strip-label") == "dự án"
    assert _chu_the(page, '[data-tab="scoring"]').endswith("Nhập điểm")
    mo_ta = _chu_the(page, "#view-pipeline .view-desc")
    assert mo_ta == "Kiểm tra dữ liệu, bốc thăm, xếp nhân viên vào dự án và xuất kết quả."
    assert "học sinh" not in page.locator("#view-pipeline").inner_text()
    assert not loi, loi


def test_cong_ty_sang_tieng_anh(mo_trang):
    page, api, loi = mo_trang()
    _cho_chu(page, "#statStudents + .strip-label", "nhân viên")
    page.evaluate("window.I18N.setLang('en')")
    _cho_chu(page, "#statStudents + .strip-label", "employees")
    assert _chu_the(page, "#statClubs + .strip-label") == "projects"
    mo_ta = _chu_the(page, "#view-pipeline .view-desc")
    assert mo_ta == "Check the data, draw lottery numbers, place employees in projects, and export the results."
    assert not loi, loi


def test_en_trong_roi_ve_vi_tren_man_hinh(mo_trang):
    cfg = {"industry": "company",
           "labels": {"person": {"vi": "Nhân viên", "en": ""},
                      "slot": {"vi": "Dự án", "en": "   "}}}
    page, api, loi = mo_trang(workspaces=(("Công ty", cfg),))
    _cho_chu(page, "#statStudents + .strip-label", "nhân viên")
    page.evaluate("window.I18N.setLang('en')")
    _cho_chu(page, "#statStudents + .strip-label", "nhân viên")      # không phải "Nhân viêns"
    assert _chu_the(page, "#statClubs + .strip-label") == "dự án"
    assert not loi, loi


def test_tieu_de_cua_so_la_ten_cho_xep_va_ten_workspace(mo_trang):
    page, api, loi = mo_trang()
    page.wait_for_function("document.title === 'Dự án — Công ty ABC'", timeout=10000)
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("document.title === 'Project — Công ty ABC'", timeout=10000)
    assert not loi, loi


def test_tieu_de_cua_so_goi_ve_backend(mo_trang):
    """Cửa sổ gốc (pywebview) không theo document.title: giao diện phải nhờ backend đặt."""
    page, api, loi = mo_trang()

    class CuaSo:
        tieu_de = []

        def set_title(self, t):
            self.tieu_de.append(t)

    cua_so = CuaSo()
    api._set_window(cua_so)
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("document.title === 'Project — Công ty ABC'", timeout=10000)
    page.wait_for_timeout(300)
    assert cua_so.tieu_de and cua_so.tieu_de[-1] == "Project — Công ty ABC"


def test_truong_hoc_mac_dinh_giu_nguyen_chu_va_tieu_de(mo_trang):
    page, api, loi = mo_trang(workspaces=(("Trường học", {}),))
    _cho_chu(page, "#statStudents + .strip-label", "học sinh")
    assert _chu_the(page, "#statClubs + .strip-label") == "CLB"
    page.wait_for_function("document.title === 'Câu lạc bộ — Trường học'", timeout=10000)
    assert not loi, loi


def test_chay_voi_duong_dan_csdl_rieng_giu_tieu_de_cu(mo_trang):
    page, api, loi = mo_trang(workspaces=(("X", CONG_TY),), che_do_ws=False)
    # Nhãn của CSDL đó vẫn được áp (lấy từ get_workspace_state)…
    _cho_chu(page, "#statStudents + .strip-label", "nhân viên")
    # …nhưng tiêu đề trang không bị đụng tới: "keep today's behaviour exactly".
    assert page.title() == "Sắp xếp Dự án · RB-DA"
    assert not loi, loi


def test_doi_workspace_doi_chu(mo_trang):
    page, api, loi = mo_trang(workspaces=(("Trường học", {}), ("Công ty ABC", CONG_TY)),
                              mo_slug="truong-hoc")
    _cho_chu(page, "#statStudents + .strip-label", "học sinh")
    page.locator("#btnWorkspace").click()
    page.locator('button[data-slug="cong-ty-abc"][data-hanh-dong="mo"]').click()
    _cho_chu(page, "#statStudents + .strip-label", "nhân viên")
    assert page.title() == "Dự án — Công ty ABC"
    page.locator("#btnWorkspace").click()
    page.locator('button[data-slug="truong-hoc"][data-hanh-dong="mo"]').click()
    _cho_chu(page, "#statStudents + .strip-label", "học sinh")
    assert not loi, loi


def test_loi_tu_backend_dich_theo_nhan(mo_trang):
    """Một thông báo lỗi của backend ({code, params}) cũng đi qua nhãn."""
    page, api, loi = mo_trang()
    _cho_chu(page, "#statStudents + .strip-label", "nhân viên")
    kq = page.evaluate(
        "window.I18N.translateError({code: 'student_not_found', params: {student_id: 'NV01'}})")
    assert kq == "Không tìm thấy nhân viên NV01."
    page.evaluate("window.I18N.setLang('en')")
    assert page.evaluate(
        "window.I18N.translateError({code: 'student_not_found', params: {student_id: 'NV01'}})"
    ) == "Employee NV01 wasn't found."
    assert not loi, loi
