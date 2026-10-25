"""Nút "Tải sổ nhập mẫu" dùng cấu hình của workspace đang mở (TASK 5) — trình duyệt thật."""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
openpyxl = pytest.importorskip("openpyxl")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import workspace as ws  # noqa: E402
from api import PipelineAPI  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402

CONG_TY = {
    "industry": "company",
    "labels": {"person": {"vi": "Nhân viên", "en": "Employee"},
               "slot": {"vi": "Dự án", "en": "Project"},
               "group": {"vi": "Cấp bậc", "en": "Level"}},
    "rules": {"max_choices": 3, "max_tests": None},
}


@pytest.fixture
def mo_trang(tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def mo(cfg):
        goc = tmp_path / "goc"
        goc.mkdir(exist_ok=True)
        slug = ws.tao(str(goc), "Thử", cfg)
        xuat = tmp_path / "xuat"
        xuat.mkdir(exist_ok=True)
        api = PipelineAPI(ws.duong_dan_db(str(goc), slug), thu_muc_xuat=str(xuat),
                          thu_muc_goc_ws=str(goc))
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(bypass_csp=True)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        return page, api, str(xuat), loi

    yield mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _tai_mau(page, thu_muc_xuat):
    page.locator("#btnTaiSoMau").click()
    page.wait_for_function(
        "document.querySelector('#toastStack').innerText.indexOf('.xlsx') !== -1", timeout=10000)
    tep = [f for f in os.listdir(thu_muc_xuat) if f.endswith(".xlsx")]
    assert tep, os.listdir(thu_muc_xuat)
    return openpyxl.load_workbook(os.path.join(thu_muc_xuat, tep[0]))


def test_tai_so_mau_cua_workspace_cong_ty(mo_trang):
    page, api, xuat, loi = mo_trang(CONG_TY)
    api.create_or_update_club("a", "Dự án A", 3, 0, "")
    wb = _tai_mau(page, xuat)
    assert wb.sheetnames == ["1. Dự án", "2. Nhân viên", "Hướng dẫn"]
    tieu_de = [c.value for c in wb["2. Nhân viên"][1]]
    assert tieu_de[:3] == ["Mã HS", "Họ tên", "Cấp bậc"]
    assert sum(1 for t in tieu_de if str(t).startswith("Nguyện vọng")) == 3     # max_choices
    assert wb["1. Dự án"]["A2"].value == "Dự án A"
    assert not loi, loi


def test_tai_so_mau_truong_hoc_giu_nguyen(mo_trang):
    page, api, xuat, loi = mo_trang({})
    wb = _tai_mau(page, xuat)
    assert wb.sheetnames == ["1. CLB", "2. Học sinh", "Hướng dẫn"]
    assert not loi, loi


def test_ui_chan_theo_tran_cua_workspace(mo_trang):
    """Ô nhập tại chỗ (thẻ 03) dùng trần của workspace: không giới hạn thi, nguyện vọng 3."""
    page, api, xuat, loi = mo_trang(CONG_TY)
    for i in range(6):
        api.create_or_update_club("c%d" % i, "Dự án %d" % i, 5, 0, "")
    api.create_student_if_missing("S1", "An")
    page.wait_for_function("TRAN_CLB_THI_MOI_BUOI === Infinity && TRAN_NGUYEN_VONG_MOI_BUOI === 3",
                           timeout=10000)
    # câu gợi ý của bước 1 là câu "không giới hạn", không còn số 5 ghi cứng
    page.wait_for_function(
        "document.getElementById('fallbackStep1Hint').getAttribute('data-i18n') === "
        "'fallback_step1_hint_khong_gioi_han'", timeout=10000)
    gioi_y = page.locator("#fallbackStep1Hint").inner_text()
    assert "5" not in gioi_y and "dự án" in gioi_y
    assert "tối đa 3 dự án" in page.locator("[data-i18n='fallback_step2_hint']").inner_text()
    assert not loi, loi
