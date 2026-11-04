"""A14 phần B — giao diện LỚP (Playwright + Chromium, qua `browser_host`; dữ liệu MÔ PHỎNG).

Kiosk: ô chọn lớp ẩn khi chưa có lớp nào, BẮT BUỘC khi có. Quản lý: lọc / sắp / sửa lớp từng em.
Dữ liệu khác: lọc, và nút "Xuất theo lớp" khoá khi chưa có kết quả. Workspace: ô nhãn thứ 6. Chữ vi
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

    def _mo(lop=None, chay=False, nhieu_buoi=False, them=()):
        """lop: {sid: lớp}. Có HS1..HS3 và hai CLB; chay=True thì chạy xếp.
        nhieu_buoi: ba buổi "10", "3", "2" (theo vần: 10, 2, 3; theo thứ tự: 2, 3, 10), mỗi buổi
        một CLB 1 chỗ nên có em chưa được xếp."""
        if nhieu_buoi:
            for b in ("10", "3", "2"):
                assert api.create_or_update_club("C" + b, "CLB " + b, 1, 0, "", buoi=b)["ok"]
            dung_hs(api, "HS1", "HS2", "HS3")
            cot = "student_id,name,2_pref_1,3_pref_1,10_pref_1\n"
            hang_csv = "".join("HS%d,Em HS%d,C2,C3,C10\n" % (i, i) for i in (1, 2, 3))
            assert api.import_preferences_csv(cot + hang_csv)["ok"]
        else:
            dung_clb(api, A=5, B=5)
            dung_hs(api, "HS1", "HS2", "HS3")
            for sid in ("HS1", "HS2", "HS3"):
                assert api.submit_preferences(sid, ["A", "B"])["ok"]
        for sid in them:        # T2: thêm em (mã khó sắp) cùng nguyện vọng A, B
            dung_hs(api, sid)
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
        # Ngữ cảnh dựng tường minh để test mở được trang thứ hai CHUNG kho lưu trữ (T2)
        ctx = br.new_context(locale="vi-VN", viewport={"width": 1280, "height": 1600}, bypass_csp=True)
        page = ctx.new_page()
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
    page.locator('[data-tab="others"]').click()
    page.wait_for_function("() => document.getElementById('xuatKetQua').disabled")
    assert page.locator("#btnXuatTheoLop").is_disabled()
    assert not loi, loi


def test_ket_qua_loc_va_xuat_theo_lop(mo, tmp_path):
    page, api, loi = mo({"HS1": "10A1", "HS2": "10A2"}, chay=True)
    page.locator('[data-tab="others"]').click()
    page.wait_for_selector("#resultsTableBody tr", state="attached")
    assert page.locator("#btnXuatTheoLop").is_enabled()
    heads = page.locator("#view-others #dsXepPanel thead th").all_inner_texts()
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
def test_workspace_co_o_nhan_thu_sau_cohort(mo_trang):  # noqa: F811
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
    """Đọc thẳng i18n.js: 26 khoá mới (thẻ Kết quả) × 2 ngôn ngữ (vi đứng trước en trong tệp)."""
    with open(os.path.join(GOC, "i18n.js"), encoding="utf-8") as f:
        nguon = f.read()
    mach = re.compile(r'^\s{6}((?:lop_|kiosk_lop|th_cohort|btn_xuat_theo_lop|xuat_theo_lop|'
                      r'xuat_kq_theo_lop|xuat_muc_theo_lop|aria_loc_lop|aria_sap_xep|toast_lop|'
                      r'ws_dt_cohort|th_stt|members_|theolop_|the_xem_)\w*): "(.*)",$', re.M)
    cap = mach.findall(nguon)
    assert len(cap) == 52, len(cap)                  # 26 khoá × 2 ngôn ngữ
    vi, en = cap[:26], cap[26:]
    assert [k for k, _ in vi] == [k for k, _ in en]
    for k, v in vi:
        assert not TU_ANH_CAM.search(re.sub(r"\{\w+\}", "", v)), (k, v)
    for k, v in en:
        assert not re.search(r"\byou\b", v, re.I), (k, v)


def test_quan_ly_lan_mo_dau_hien_du_so_em_va_giu_chon_chua_co_lop(mo):
    """Lần mở đầu (ô lọc còn rỗng) phải ra ĐỦ mọi em; chọn "Chưa có lớp" thì giữ sau khi tải lại."""
    page, api, loi = mo({"HS1": "10A1", "HS2": "10A2"})
    _sang_quan_ly_hs(page)
    assert len(_hang_quan_ly(page)) == 3
    assert page.locator("#adminLopLoc").input_value() == "__tat_ca__"
    page.select_option("#adminLopLoc", "")
    page.wait_for_function("() => document.querySelectorAll('#adminStudentTableBody tr').length === 1")
    page.evaluate("() => loadAdminStudents()")
    page.wait_for_timeout(500)
    assert page.locator("#adminLopLoc").input_value() == ""
    assert [h[0] for h in _hang_quan_ly(page)] == ["HS3"]
    assert not loi, loi


# ------------------------------------------------------------------ thẻ Kết quả (02, gộp từ 02/06/07)
def _mo_ket_qua(page, tang1):
    page.locator('.nav-item[data-tab="results"]').click()
    page.wait_for_selector("#view-results.is-active")
    page.locator('#kqTang1 [data-kq="%s"]' % tang1).click()


def test_thanh_ben_sau_khi_gop_va_bao_chua_co_ket_qua(mo):
    page, api, loi = mo({"HS1": "10A1"})
    nut = page.evaluate("""() => Array.from(document.querySelectorAll('.nav-item'))
        .map(n => [n.dataset.tab, n.querySelector('.nav-icon').textContent])""")
    assert nut == [["pipeline", "01"], ["results", "02"], ["others", "03"],
                   ["fallback", "04"], ["admin", "05"], ["scoring", "06"]]
    for tang1 in ("lop", "clb", "ma"):
        _mo_ket_qua(page, tang1)
        page.wait_for_function("() => !document.getElementById('kqRong').hidden")
        assert "Chưa có kết quả" in page.locator("#kqRong").inner_text()
        assert page.locator("#kqBang").is_hidden()
    assert not loi, loi


def test_theo_clb_chon_clb_ra_bang_khong_diem(mo):
    page, api, loi = mo({"HS1": "10A1", "HS2": "10A2"}, chay=True)
    _mo_ket_qua(page, "clb")
    page.wait_for_function("() => document.querySelectorAll('#kqChonClb option').length > 1")
    page.select_option("#kqChonClb", "A")
    page.wait_for_function("() => !document.getElementById('kqBang').hidden "
                           "&& document.getElementById('kqDem').textContent.includes('3/5')")
    assert page.locator("#kqDem").inner_text() == "Đã xếp 3/5 chỗ"
    assert [x.casefold() for x in page.locator("#kqDau th").all_inner_texts()] == [
        "thứ tự", "mã học sinh", "họ tên", "lớp"]            # CSS viết hoa tiêu đề cột
    hang = page.locator("#kqThan tr").all_inner_texts()
    assert len(hang) == 3 and hang[0].split("\t")[:2] == ["1", "HS1"]
    assert not loi, loi


def test_theo_clb_nhieu_buoi_ghi_kem_buoi_va_sap_theo_ngay(mo):
    page, api, loi = mo({"HS1": "10A1"}, chay=True, nhieu_buoi=True)
    _mo_ket_qua(page, "clb")
    page.wait_for_function("() => document.querySelectorAll('#kqChonClb option').length > 2")
    # mặc định "Theo ngày trong tuần": nhóm theo buổi, thứ tự ngày (2, 3, 10), không theo vần
    assert page.locator("#kqChonClb optgroup").evaluate_all("g => g.map(x => x.label)") == ["2", "3", "10"]
    assert page.locator("#kqChonClb option").all_inner_texts() == ["CLB 2", "CLB 3", "CLB 10"]
    assert not loi, loi


def test_theo_lop_mot_buoi_mot_cot_va_dong_do(mo):
    page, api, loi = mo({"HS1": "10A1", "HS2": "10A1"}, chay=True)
    _mo_ket_qua(page, "lop")
    page.wait_for_function("() => document.querySelectorAll('#kqChonLop option').length > 1")
    assert page.locator("#kqChonLop option").all_inner_texts() == ["10A1 (2)", "Chưa có lớp (1)"]
    page.wait_for_function("() => !document.getElementById('kqBang').hidden")
    assert [x.casefold() for x in page.locator("#kqDau th").all_inner_texts()] == [
        "thứ tự", "mã học sinh", "họ tên", "câu lạc bộ"]
    assert page.locator("#kqThan tr").count() == 2
    assert page.locator("#kqDem").inner_text() == "2 học sinh · 0 chưa có chỗ"
    page.select_option("#kqChonLop", "")                       # Chưa có lớp
    page.wait_for_function("() => document.querySelectorAll('#kqThan tr').length === 1")
    assert not loi, loi


def test_theo_lop_nhieu_buoi_cot_theo_ngay_o_trong_va_dong_do(mo):
    page, api, loi = mo({"HS1": "10A1", "HS2": "10A1", "HS3": "10A1"}, chay=True, nhieu_buoi=True)
    _mo_ket_qua(page, "lop")
    page.wait_for_function("() => !document.getElementById('kqBang').hidden")
    assert [x.casefold() for x in page.locator("#kqDau th").all_inner_texts()] == [
        "thứ tự", "mã học sinh", "họ tên", "2", "3", "10"]            # theo thứ tự, không theo vần
    tong = page.locator("#kqThan tr").all_inner_texts()
    assert len(tong) == 3 and any("-" in r.split("\t", 3)[3] for r in tong)          # ô trống ghi -
    do = page.locator("#kqThan tr.dong-do").count()
    assert do == int(page.locator("#kqDem").inner_text().split("·")[1].strip().split()[0])
    assert not loi, loi


def test_theo_lop_chua_co_lop_nao_hien_dong_nhac(mo):
    page, api, loi = mo({}, chay=True)
    _mo_ket_qua(page, "lop")
    page.wait_for_function("() => !document.getElementById('kqRong').hidden")
    assert "Chưa có lớp nào" in page.locator("#kqRong").inner_text()
    assert page.locator("#kqBang").is_hidden()
    assert not loi, loi


def test_doi_ngon_ngu_ve_lai_chu_o_tha_xuong_lop_o_kiosk(mo):
    page, api, loi = mo({"HS1": "10A1"})
    _chon_hs(page, "HS2")
    assert page.locator("#kioskLop option").first.inner_text() == "Chọn lớp…"
    page.locator("#btnLangToggle").click()
    page.wait_for_function("() => document.querySelector('#kioskLop option').textContent.includes('Choose')")
    assert page.locator("#kioskLop option").first.inner_text() == "Choose class…"
    assert not loi, loi


@pytest.mark.parametrize("ngon", ["vi", "en"])
def test_cho_giu_cohort_duoc_dien_that_tren_moi_the(mo, ngon):
    """Không thẻ nào được hiện nguyên "{cohort_l}" / "{cohort}" / "{person_l}"... (cả vi lẫn en)."""
    page, api, loi = mo({"HS1": "10A1"}, chay=True)
    if ngon == "en":
        page.locator("#btnLangToggle").click()
        page.wait_for_function("() => document.documentElement.lang === 'en' || "
                               "document.getElementById('btnLangToggle').textContent.trim() === 'VI'")
    for ten in ("pipeline", "results", "others", "fallback", "admin", "scoring"):
        page.locator('.nav-item[data-tab="%s"]' % ten).click()
        page.wait_for_timeout(400)
        if ten == "admin":
            page.locator("#qlTabHs").click()
            page.wait_for_timeout(300)
        chu = page.evaluate("() => document.body.innerText")
        assert not re.search(r"\{(person|slot|session|group|score|cohort)(_\w+)?\}", chu), (ngon, ten)
    # nhãn lớp đổi trong workspace thì chữ trên màn hình đổi theo ("Phòng ban" thay "Lớp")
    page.evaluate("() => I18N.applyLabels({cohort: {vi: 'Phòng ban', en: 'Department'}})")
    page.locator('.nav-item[data-tab="results"]').click()
    page.wait_for_timeout(300)
    chu = page.locator("#kqTang1").inner_text()
    assert ("Phòng ban" if ngon == "vi" else "Department").casefold() in chu.casefold()
    assert not loi, loi


def test_xuat_theo_lop_hien_canh_bao_ket_qua_cu(mo, tmp_path):
    """B1: sửa dữ liệu sau lần chạy rồi bấm "Xuất theo lớp" → dòng cảnh báo như các nút xuất khác."""
    page, api, loi = mo({"HS1": "10A1"}, chay=True)
    assert api.submit_preferences("HS2", ["B", "A"])["ok"]
    page.locator('[data-tab="others"]').click()
    page.wait_for_function("() => !document.getElementById('btnXuatTheoLop').disabled")
    page.locator("#btnXuatTheoLop").click()
    page.wait_for_function("() => document.getElementById('xuatFeedback').textContent.trim() !== ''")
    chu = page.locator("#xuatFeedback").inner_text()
    assert "tệp theo lớp" in chu and "đã cũ" in chu.casefold(), chu
    assert not loi, loi


def test_kiosk_doi_o_lop_la_chua_luu_va_sang_em_khac_phai_bam_hai_lan(mo):
    """B2: đổi ô lớp mà chưa Lưu là thay đổi chưa lưu như tick thi / nguyện vọng."""
    page, api, loi = mo({"HS1": "10A1"})
    _chon_hs(page, "HS2")
    assert page.locator("#kioskLopChuaLuu").is_hidden()
    page.select_option("#kioskLop", "10A1")
    assert page.locator("#kioskLopChuaLuu").is_visible()
    page.locator('.hs-card[data-student-id="HS3"]').click()          # lần 1: chỉ nhắc
    assert page.evaluate("() => currentFallbackStudent") == "HS2"
    assert page.locator("#toastStack").inner_text().strip() != ""
    page.locator('.hs-card[data-student-id="HS3"]').click()          # lần 2: đi thật
    page.wait_for_function("() => currentFallbackStudent === 'HS3'")
    assert not loi, loi


def test_kiosk_luu_xong_thi_o_lop_het_chua_luu_va_chon_lai_ve_nhu_cu_cung_het(mo):
    page, api, loi = mo({"HS1": "10A1"})
    _chon_hs(page, "HS2")
    page.select_option("#kioskLop", "10A1")
    page.locator("#rankingSourceGrid .option-row").first.click()
    page.locator("#btnSubmitPreferences").click()
    page.wait_for_function("() => document.getElementById('preferencesFeedback').textContent.trim() !== ''")
    assert page.locator("#kioskLopChuaLuu").is_hidden()
    page.select_option("#kioskLop", "")                                # đổi rồi...
    assert page.locator("#kioskLopChuaLuu").is_visible()
    page.select_option("#kioskLop", "10A1")                            # ...đổi lại đúng giá trị đã lưu
    assert page.locator("#kioskLopChuaLuu").is_hidden()
    assert not loi, loi


@pytest.mark.parametrize("ngon", ["vi", "en"])
def test_dong_nhac_chua_co_lop_goi_dung_ten_the_tren_thanh_ben(mo, ngon):
    """B5: dòng nhắc ở thẻ 02 (Theo lớp) gọi đúng tên thẻ 05 như thanh bên (không viết cứng), theo nhãn workspace."""
    page, api, loi = mo({}, chay=True)
    if ngon == "en":
        page.locator("#btnLangToggle").click()
        page.wait_for_function("() => document.getElementById('btnLangToggle').textContent.trim() === 'VI'")
    page.evaluate("() => I18N.applyLabels({slot: {vi: 'Dự án', en: 'Project'}})")
    _mo_ket_qua(page, "lop")
    page.wait_for_function("() => !document.getElementById('kqRong').hidden")
    ten_the = page.locator('.nav-item[data-tab="admin"] [data-i18n="nav_admin"]').inner_text().strip()
    ten_muc = page.locator("#qlTabHs").inner_text().strip()
    chu = page.locator("#kqRong").inner_text()
    assert ten_the in chu and ten_muc in chu, (ten_the, ten_muc, chu)
    assert ("Dự án" if ngon == "vi" else "Project").casefold() in ten_the.casefold()
    assert "{" not in chu and "Quản lý." not in chu
    assert not loi, loi
