"""A14 phần B — giao diện LỚP (Playwright + Chromium, qua `browser_host`; dữ liệu MÔ PHỎNG).

Kiosk: ô chọn lớp ẩn khi chưa có lớp nào, BẮT BUỘC khi có. Quản lý: lọc / sắp / sửa lớp từng em.
Kết quả: lọc, và nút "Xuất theo lớp" khoá khi chưa có kết quả. Workspace: ô nhãn thứ 6. Chữ vi
không lẫn tiếng Anh. Cần các API lớp của phiên A (set_student_class, list_classes...)."""

import os
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _wharton import dung_clb, dung_hs, tat_wharton  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402
from test_ws_giao_dien import mo_trang  # noqa: E402,F401


@pytest.fixture
def api(api):
    tat_wharton(api)
    return api


@pytest.fixture
def mo(tmp_path, api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo(lop=None, chay=False):
        """lop: {sid: lớp}. Có HS1..HS3 và hai CLB; chay=True thì chạy xếp."""
        dung_clb(api, A=5, B=5)
        dung_hs(api, "HS1", "HS2", "HS3")
        for sid in ("HS1", "HS2", "HS3"):
            assert api.submit_preferences(sid, ["A", "B"])["ok"]
        for sid, l in (lop or {}).items():
            assert api.set_student_class(sid, l)["ok"]
        if chay:
            assert api.run_pipeline(seed=1)["ok"]
        api.thu_muc_xuat = str(tmp_path / "TaiXuong")
        os.makedirs(api.thu_muc_xuat, exist_ok=True)
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", viewport={"width": 1280, "height": 1600}, bypass_csp=True)
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


def _chon_hs(page, sid):
    page.locator('[data-tab="fallback"]').click()
    page.wait_for_selector(".hs-card")
    page.locator('.hs-card[data-student-id="%s"]' % sid).click()
    page.wait_for_selector("#fallbackWorkArea:not([hidden])")


def _sang_quan_ly_hs(page):
    page.locator('[data-tab="admin"]').click()
    page.locator("#qlTabHs").click()
    page.wait_for_selector("#adminStudentTableBody tr")


def _hang_quan_ly(page):
    return page.evaluate("""() => Array.from(document.querySelectorAll('#adminStudentTableBody tr'))
        .map(tr => [tr.children[1].textContent, tr.querySelector('.lop-sua').value])""")


# ------------------------------------------------------------------ kiosk
def test_kiosk_khong_co_lop_an_o_chon(mo):
    page, api, loi = mo()
    _chon_hs(page, "HS1")
    assert page.locator("#kioskLopHang").is_hidden()
    assert page.locator("#newStudentLop").is_hidden()
    page.locator("#rankingSourceGrid .option-row").first.click()
    page.locator("#btnSubmitPreferences").click()
    page.wait_for_function("() => document.getElementById('preferencesFeedback').textContent.trim() !== ''")
    assert not loi, loi


def test_kiosk_co_lop_bat_buoc_chon_truoc_khi_luu(mo):
    page, api, loi = mo({"HS1": "10A1"})
    _chon_hs(page, "HS2")
    assert page.locator("#kioskLopHang").is_visible()
    assert page.locator("#kioskLop").input_value() == ""
    page.locator("#btnSubmitPreferences").click()
    assert page.locator("#kioskLopNhac").is_visible()
    # chưa lưu: lớp của HS2 vẫn trống
    ds = {r["student_id"]: r["class_id"] for r in api.list_students_admin("", 1, 50)["data"]["rows"]}
    assert not ds["HS2"]
    page.select_option("#kioskLop", "10A1")
    page.locator("#btnSubmitPreferences").click()
    page.wait_for_function("() => document.getElementById('preferencesFeedback').textContent.trim() !== ''")
    ds = {r["student_id"]: r["class_id"] for r in api.list_students_admin("", 1, 50)["data"]["rows"]}
    assert ds["HS2"] == "10A1"
    assert not loi, loi


def test_kiosk_hien_san_lop_hien_tai_cua_em(mo):
    page, api, loi = mo({"HS1": "10A1", "HS2": "10A2"})
    _chon_hs(page, "HS2")
    assert page.locator("#kioskLop").input_value() == "10A2"
    opts = page.locator("#kioskLop option").all_inner_texts()
    assert opts[1:] == ["10A1", "10A2"]          # danh sách cố định từ list_classes
    assert not loi, loi


def test_kiosk_tao_em_moi_phai_chon_lop_va_gui_lop(mo):
    page, api, loi = mo({"HS1": "10A1"})
    page.locator('[data-tab="fallback"]').click()
    page.wait_for_selector("#newStudentLop:not([hidden])")
    page.fill("#newStudentId", "HS9")
    page.fill("#newStudentName", "Em Chín")
    page.locator("#btnCreateStudent").click()
    ds = {r["student_id"] for r in api.list_students_admin("", 1, 50)["data"]["rows"]}
    assert "HS9" not in ds                       # chưa chọn lớp: không tạo
    page.select_option("#newStudentLop", "10A1")
    page.locator("#btnCreateStudent").click()
    page.wait_for_function("""() => document.querySelector('.hs-card[data-student-id="HS9"]')""")
    ds = {r["student_id"]: r["class_id"] for r in api.list_students_admin("", 1, 50)["data"]["rows"]}
    assert ds["HS9"] == "10A1"
    assert not loi, loi


# ------------------------------------------------------------------ quản lý
def test_quan_ly_loc_sap_va_sua_lop(mo):
    page, api, loi = mo({"HS1": "10A10", "HS2": "10A2"})
    _sang_quan_ly_hs(page)
    assert [h[0] for h in _hang_quan_ly(page)] == ["HS1", "HS2", "HS3"]
    page.select_option("#adminSapXep", "class_id")
    page.wait_for_function("() => document.querySelector('#adminStudentTableBody tr td:nth-child(2)').textContent === 'HS2'")
    assert [h[0] for h in _hang_quan_ly(page)] == ["HS2", "HS1", "HS3"]      # tự nhiên, trống cuối
    page.select_option("#adminLopLoc", "10A2")
    page.wait_for_function("() => document.querySelectorAll('#adminStudentTableBody tr').length === 1")
    assert _hang_quan_ly(page) == [["HS2", "10A2"]]
    page.select_option("#adminLopLoc", "")                                     # Chưa có lớp
    page.wait_for_function("() => document.querySelector('#adminStudentTableBody .lop-sua').dataset.studentId === 'HS3'")
    # sửa lớp HS3 thành "  11b " -> chuẩn hoá 11B, rời khỏi bộ lọc "Chưa có lớp"
    o = page.locator("#adminStudentTableBody .lop-sua").first
    o.fill("  11b ")
    o.blur()
    page.wait_for_function("() => !document.querySelector('#adminStudentTableBody .lop-sua') "
                           "|| document.querySelector('#adminStudentTableBody .lop-sua').dataset.studentId !== 'HS3'")
    ds = {r["student_id"]: r["class_id"] for r in api.list_students_admin("", 1, 50)["data"]["rows"]}
    assert ds["HS3"] == "11B"
    assert not loi, loi


# ------------------------------------------------------------------ kết quả
def test_ket_qua_nut_xuat_theo_lop_khoa_khi_chua_co_ket_qua(mo):
    page, api, loi = mo({"HS1": "10A1"})
    page.locator('[data-tab="results"]').click()
    page.wait_for_function("() => document.getElementById('xuatKetQua').disabled")
    assert page.locator("#btnXuatTheoLop").is_disabled()
    assert not loi, loi


def test_ket_qua_loc_va_xuat_theo_lop(mo, tmp_path):
    page, api, loi = mo({"HS1": "10A1", "HS2": "10A2"}, chay=True)
    page.locator('[data-tab="results"]').click()
    page.wait_for_selector("#resultsTableBody tr", state="attached")
    assert page.locator("#btnXuatTheoLop").is_enabled()
    heads = page.locator("#view-results #dsXepPanel thead th").all_inner_texts()
    assert heads[heads.index("Họ tên") + 1] == "Lớp"
    page.select_option("#resultsLopLoc", "10A2")
    page.wait_for_function("() => document.querySelectorAll('#resultsTableBody tr').length === 1")
    assert page.locator("#resultsTableBody tr").first.locator("td").nth(1).inner_text() == "HS2"
    page.select_option("#resultsLopLoc", "__tat_ca__")
    page.locator("#btnXuatTheoLop").click()
    page.wait_for_function("() => document.getElementById('xuatFeedback').textContent.includes('3 tệp')")
    thu_muc = tmp_path / "TaiXuong"
    cac = [p for p in thu_muc.iterdir() if p.is_dir()]
    assert len(cac) == 1 and sorted(os.listdir(cac[0])) == ["10A1.xlsx", "10A2.xlsx", "_chua_co_lop.xlsx"]
    assert not loi, loi


# ------------------------------------------------------------------ workspace và chữ
def test_workspace_co_o_nhan_thu_sau_cohort(mo_trang):
    page, api, goc, loi = mo_trang()
    page.locator("#btnWorkspace").click()
    page.locator("#wsBtnMoi").click()
    page.fill("#wzTen", "Công ty ABC")
    page.locator("#wzTiep").click()
    assert page.locator("#wzNhan_cohort_vi").input_value() == "Lớp"
    assert page.locator("#wzNhan_cohort_en").input_value() == "Class"
    page.fill("#wzNhan_cohort_vi", "Phòng ban")
    page.locator("#wzTiep").click()
    page.locator("#wzTiep").click()
    assert page.locator("#rvNhan_cohort").inner_text().startswith("Phòng ban")
    assert not loi, loi


TU_ANH_CAM = re.compile(r"\b(class|filter|export|sort|save|student|club|choose|all|by|file|team)\b", re.I)


def test_chu_moi_vi_sach_tieng_anh_va_en_khong_dung_you():
    """Đọc thẳng i18n.js: 19 khoá mới × 2 ngôn ngữ (vi đứng trước en trong tệp)."""
    with open(os.path.join(GOC, "i18n.js"), encoding="utf-8") as f:
        nguon = f.read()
    mach = re.compile(r'^\s{6}((?:lop_|kiosk_lop|th_cohort|btn_xuat_theo_lop|xuat_theo_lop|'
                      r'xuat_kq_theo_lop|xuat_muc_theo_lop|aria_loc_lop|aria_sap_xep|toast_lop|'
                      r'ws_dt_cohort)\w*): "(.*)",$', re.M)
    cap = mach.findall(nguon)
    assert len(cap) == 38, len(cap)
    vi, en = cap[:19], cap[19:]
    assert [k for k, _ in vi] == [k for k, _ in en]
    for k, v in vi:
        assert not TU_ANH_CAM.search(re.sub(r"\{\w+\}", "", v)), (k, v)
    for k, v in en:
        assert not re.search(r"\byou\b", v, re.I), (k, v)
