"""T3-L0 giao diện (Chromium, qua `browser_host`): B1 sửa CLB không mất dữ liệu, B2 nút Chạy khi trống.
Dữ liệu MÔ PHỎNG dựng trong test. Máy không có playwright/Chromium thì bỏ qua cả tệp."""

import os

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
        page = br.new_page(locale="vi-VN", viewport={"width": 1280, "height": 1400}, bypass_csp=True)
        page.set_default_timeout(8000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        return page, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _clb(api, cid):
    with api._ket_noi_doc() as cur:
        return tuple(cur.execute(
            "SELECT name, capacity, reserve_capacity, reserve_group, buoi FROM clubs WHERE club_id = ?",
            (cid,)).fetchone())


def _vao_ql(page):
    page.locator('[data-tab="admin"]').click()
    page.wait_for_selector("#btnSaveClub", state="visible")


# ---------------------------------------------------------------- B1 / T3-26
def test_bam_dong_dien_form_va_sua_chi_tieu_khong_mat_du_lieu(api, mo):
    api.create_or_update_club("clb_k", "CLB K", 10, 4, "chinh_sach", "thu_2")
    page, loi = mo()
    _vao_ql(page)
    page.locator('#adminClubTableBody tr[data-club-id="clb_k"]').click()
    assert page.input_value("#clubFormId") == "clb_k"
    assert page.eval_on_selector("#clubFormId", "e => e.readOnly") is True
    assert page.input_value("#clubFormName") == "CLB K"
    assert page.input_value("#clubFormCapacity") == "10"
    assert page.input_value("#clubFormReserveCapacity") == "4"
    assert page.input_value("#clubFormReserveGroup") == "chinh_sach"
    assert page.input_value("#clubFormBuoi") == "thu_2"
    page.fill("#clubFormCapacity", "20")
    page.click("#btnSaveClub")
    page.wait_for_function("document.querySelector('#clubFormId').value === ''")
    assert _clb(api, "clb_k") == ("CLB K", 20, 4, "chinh_sach", "thu_2")
    assert page.eval_on_selector("#clubFormId", "e => e.readOnly") is False
    assert not loi


def test_go_tay_lai_ma_cu_chi_dien_ba_o_khong_xoa_ba_truong_con_lai(api, mo):
    api.create_or_update_club("clb_k", "CLB K", 10, 4, "chinh_sach", "thu_2")
    page, loi = mo()
    _vao_ql(page)
    page.fill("#clubFormId", "clb_k")
    page.fill("#clubFormName", "CLB K")
    page.fill("#clubFormCapacity", "20")
    page.fill("#clubFormReserveCapacity", "")
    page.click("#btnSaveClub")
    page.wait_for_function("document.querySelector('#clubFormId').value === ''")
    assert _clb(api, "clb_k") == ("CLB K", 20, 4, "chinh_sach", "thu_2")
    assert not loi


def test_go_tay_ma_cu_de_nguyen_o_suat_du_tru_mac_dinh_khong_xoa(api, mo):
    api.create_or_update_club("clb_k", "CLB K", 10, 4, "chinh_sach", "thu_2")
    page, loi = mo()
    _vao_ql(page)
    page.fill("#clubFormId", "clb_k")
    page.fill("#clubFormName", "CLB K")
    page.fill("#clubFormCapacity", "20")  # KHÔNG đụng ô suất dự trữ, nhãn, buổi
    page.click("#btnSaveClub")
    page.wait_for_function("document.querySelector('#clubFormId').value === ''")
    assert _clb(api, "clb_k") == ("CLB K", 20, 4, "chinh_sach", "thu_2")
    assert not loi


def test_dong_dang_sua_xoa_nhan_co_chu_y_la_xoa_that(api, mo):
    api.create_or_update_club("clb_k", "CLB K", 10, 4, "chinh_sach", "thu_2")
    page, _ = mo()
    _vao_ql(page)
    page.locator('#adminClubTableBody tr[data-club-id="clb_k"]').click()
    page.fill("#clubFormReserveGroup", "")
    page.fill("#clubFormReserveCapacity", "0")
    page.click("#btnSaveClub")
    page.wait_for_function("document.querySelector('#clubFormId').value === ''")
    assert _clb(api, "clb_k") == ("CLB K", 10, 0, None, "thu_2")


def test_sau_o_co_nhan_thuong_truc(api, mo):
    page, _ = mo()
    _vao_ql(page)
    nhan = page.eval_on_selector_all(
        "#clubForm .club-field", "els => els.map(e => [e.querySelector('input').id, "
        "e.querySelector('.club-field-label').textContent.trim()])")
    assert [i for i, _ in nhan] == ["clubFormId", "clubFormName", "clubFormCapacity",
                                    "clubFormReserveCapacity", "clubFormReserveGroup", "clubFormBuoi"]
    assert all(t for _, t in nhan)


# ---------------------------------------------------------------- B2 / T3-01
def test_workspace_trong_nut_chay_khoa_co_ly_do_va_khong_bao_xanh(api, mo):
    page, loi = mo()
    page.wait_for_function("document.querySelector('#btnRun').disabled === true")
    assert page.get_attribute("#btnRun", "title")
    cls = page.get_attribute("#healthSummary", "class")
    assert "is-clean" not in cls and "is-empty" in cls
    van = page.inner_text("#healthSummary")
    assert "Chưa có dữ liệu" in van and "{" not in van
    assert "{" not in page.get_attribute("#btnRun", "title")
    assert not loi


def test_co_du_lieu_nut_chay_mo(api, mo):
    api.create_or_update_club("clb_a", "A", 5)
    with api._ket_noi_ghi() as cur:
        cur.execute("INSERT INTO students (student_id, name) VALUES ('s1', 'S1')")
    page, _ = mo()
    page.wait_for_function("document.querySelector('#statStudents').textContent === '1'")
    assert page.eval_on_selector("#btnRun", "e => e.disabled") is False
    assert page.get_attribute("#healthSummary", "class").find("is-empty") == -1
