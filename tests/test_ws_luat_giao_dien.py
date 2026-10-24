"""Thẻ Nhập điểm theo luật của workspace (Playwright + Chromium): điểm theo NGƯỜI có danh
sách người; chỉ theo nhóm thì ẩn hẳn thẻ; mặc định trường học giữ nguyên màn theo CLB."""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import workspace as ws  # noqa: E402
from api import PipelineAPI  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402

NHAN = {
    "person": {"vi": "Nhân viên", "en": "Employee"},
    "slot": {"vi": "Dự án", "en": "Project"},
    "session": {"vi": "Ca", "en": "Shift"},
    "group": {"vi": "Cấp bậc", "en": "Level"},
    "score": {"vi": "Điểm", "en": "Score"},
}


@pytest.fixture
def mo_trang(tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def mo(cfg):
        goc = tmp_path / "goc"
        goc.mkdir(exist_ok=True)
        slug = ws.tao(str(goc), "Công ty", cfg)
        api = PipelineAPI(ws.duong_dan_db(str(goc), slug), thu_muc_goc_ws=str(goc))
        for sid in ("N1", "N2"):
            api.create_student_if_missing(sid, "Tên " + sid)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(bypass_csp=True)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(browser_host.serve(api, GOC, "index.html", open_browser=False))
        page.wait_for_selector("#dropZone")
        page.wait_for_function(
            "document.querySelector('#statStudents + .strip-label').textContent.trim() !== ''",
            timeout=10000)
        return page, api, loi

    yield mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _cfg(**luat):
    return {"industry": "company", "labels": NHAN, "rules": luat}


def test_diem_theo_nguoi_nhap_va_luu_tren_man_hinh(mo_trang):
    page, api, loi = mo_trang(_cfg(score_scope="per_person"))
    page.locator('[data-tab="scoring"]').click()
    page.wait_for_selector("#scoringPersonBody .score-input")
    assert page.locator("#scoringPersonArea").is_visible()
    assert not page.locator("#scoringClubPanel").is_visible()
    assert page.locator("#scoringPersonBody .score-input").count() == 2
    assert "Điểm của từng nhân viên" in page.locator("#scoringPersonArea h2").inner_text()
    assert "Nhập một điểm cho mỗi nhân viên" in page.locator("#scoringDesc").inner_text()
    page.locator('#scoringPersonBody .score-input[data-student-id="N1"]').fill("8,5")
    page.locator('#scoringPersonBody .score-input[data-student-id="N2"]').fill("abc")
    page.locator("#btnSavePersonScores").click()
    page.wait_for_selector("#scoringPersonBody .score-input.is-invalid")
    assert page.locator('#scoringPersonBody .score-input[data-student-id="N2"]').get_attribute(
        "aria-invalid") == "true"
    persons = {p["student_id"]: p["score"] for p in api.get_person_scoring_list()["data"]["persons"]}
    assert persons == {"N1": 8.5, "N2": None}
    assert not loi, loi


def test_chi_theo_nhom_an_the_nhap_diem(mo_trang):
    page, api, loi = mo_trang(_cfg(priority="tier", tiers=["A"]))
    assert not page.locator('[data-tab="scoring"]').is_visible()
    assert page.locator('[data-tab="admin"]').is_visible()
    assert not loi, loi


def test_mac_dinh_van_la_man_theo_clb(mo_trang):
    page, api, loi = mo_trang({})
    assert page.locator('[data-tab="scoring"]').is_visible()
    page.locator('[data-tab="scoring"]').click()
    page.wait_for_selector("#scoringClubPanel")
    assert page.locator("#scoringClubPanel").is_visible()
    assert not page.locator("#scoringPersonArea").is_visible()
    assert page.locator("#scoringDesc").get_attribute("data-i18n") == "scoring_desc"
    assert not loi, loi
