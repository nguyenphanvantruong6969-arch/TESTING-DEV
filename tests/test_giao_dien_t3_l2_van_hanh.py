"""T3-L2 giao diện thẻ 01 (Chromium, qua `browser_host`): cảnh báo gọn, một nút kiểm tra, khung bước thu gọn,
chân thanh bên. Dữ liệu MÔ PHỎNG dựng trong test. Máy không có playwright/Chromium thì bỏ qua cả tệp."""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from _wharton import bat_wharton, dung_clb, dung_hs, tat_wharton  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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


def _canh_bao(n):
    return [{"code": "wharton_chua_dung_het", "params": {"student_id": "HS%03d" % i, "thieu": 100, "quy": 1}}
            for i in range(1, n + 1)]


# ---------------------------------------------------------------- T3-02
def test_canh_bao_nhap_cung_loai_gom_thanh_mot_dong_co_nut_xem_nam_dong(api, mo):
    tat_wharton(api)
    page, loi = mo()
    page.evaluate("(w) => { canhBaoNhapGanNhat = w; veCanhBaoNhap(); }", _canh_bao(120))
    box = page.locator("#importWarnings")
    assert box.is_visible()
    assert box.locator(".canh-bao-nhom").count() == 1
    assert "120" in box.locator(".canh-bao-nhom").inner_text()
    assert box.locator(".canh-bao-dong:visible").count() == 0  # chưa mở: không dòng nào
    box.locator(".canh-bao-xem").click()
    assert box.locator(".canh-bao-dong:visible").count() == 5
    box.locator(".canh-bao-xem").click()
    assert box.locator(".canh-bao-dong:visible").count() == 0
    assert not loi


def test_canh_bao_nhap_it_dong_van_hien_het(api, mo):
    tat_wharton(api)
    page, loi = mo()
    page.evaluate("(w) => { canhBaoNhapGanNhat = w; veCanhBaoNhap(); }", _canh_bao(4))
    box = page.locator("#importWarnings")
    assert box.locator(".canh-bao-nhom").count() == 0
    assert box.locator(".canh-bao-dong:visible").count() == 4
    assert not loi


def test_dong_chan_chay_luon_hien_va_co_nut_mo_diem_quyet_tam(api, mo):
    bat_wharton(api)  # như test_wharton_cach_a: thêm CLB vào quỹ đã tự điền -> hồ sơ chưa hợp lệ
    dung_clb(api, A=5, B=5, C=5, D=5)
    dung_hs(api, "HS1", tick={"HS1": ["A"]})
    assert api.submit_preferences("HS1", ["A", "B", "C"])["ok"]
    assert api.submit_wharton("HS1", {}, {"B": 70, "C": 30})["ok"]
    assert api.submit_preferences("HS1", ["A", "B", "C", "D"])["ok"]
    assert api.submit_test_selection("HS1", ["A", "D"])["ok"]
    page, loi = mo()
    page.wait_for_selector("#healthList .health-item.sev-high")
    nut = page.locator("#healthList .health-item.sev-high .health-di-toi")
    assert nut.is_visible()
    nut.click()
    page.wait_for_selector("#view-admin.is-active")
    assert page.locator("#qlPanelWh").is_visible()
    assert not loi


# ---------------------------------------------------------------- T3-03
def test_nut_nhap_so_va_bo_tep_an_den_khi_co_tep_trong_hang_cho(api, mo, tmp_path):
    tat_wharton(api)
    page, loi = mo()
    assert page.locator("#importActions").is_hidden()
    assert page.locator("#btnImportAll").is_hidden() and page.locator("#btnClearQueue").is_hidden()
    assert not loi


# ---------------------------------------------------------------- T3-04
def test_chi_con_mot_nut_kiem_tra_nam_trong_khung_canh_bao(api, mo):
    tat_wharton(api)
    _du_lieu(api)
    page, loi = mo()
    assert page.locator("#btnHealthRecheck").count() == 0
    assert page.locator("#btnValidate").count() == 1
    assert page.locator(".panel:has(#healthList) #btnValidate").count() == 1
    assert page.locator("#btnValidate").inner_text() == "Kiểm tra lại dữ liệu"
    page.click("#btnValidate")
    page.wait_for_selector(".toast.is-success, .toast.is-warn")  # cảnh báo nghiêm trọng về điểm thi -> toast vàng
    assert page.locator("#healthSummary").inner_text().strip() != ""
    assert not loi


# ---------------------------------------------------------------- T3-06
def test_chay_xong_thu_sau_buoc_thanh_mot_dong_va_chi_tiet_mo_lai(api, mo):
    tat_wharton(api)
    _du_lieu(api)
    page, loi = mo()
    page.click("#btnRun")
    page.wait_for_selector("#runXong:not([hidden])", timeout=20000)
    chu = page.inner_text("#runXongChu")
    assert "/6" in chu or "/" in chu and "6" in chu
    assert page.locator("#stepper").is_hidden()
    assert page.locator(".toast.is-success").count() == 0  # bỏ thông báo xanh trùng nội dung
    page.click("#btnChiTietBuoc")
    assert page.locator("#stepper").is_visible() and page.locator("#stepper .step").count() == 6
    page.click("#btnChiTietBuoc")
    assert page.locator("#stepper").is_hidden()
    assert not loi


def test_chay_lai_tra_ve_danh_sach_buoc_dang_chay_va_loi_giu_nguyen_buoc(api, mo):
    tat_wharton(api)
    _du_lieu(api)
    page, loi = mo()
    page.click("#btnRun")
    page.wait_for_selector("#runXong:not([hidden])", timeout=20000)
    page.evaluate("() => { khoa.dangChay = true; resetSteps(); }")  # như lúc bắt đầu một lần chạy mới
    assert page.locator("#runXong").is_hidden() and page.locator("#stepper").is_visible()
    assert not loi


# ---------------------------------------------------------------- T3-10
def test_moi_luc_dung_mot_nut_mau_chinh(api, mo):
    tat_wharton(api)
    page, loi = mo()  # chưa có dữ liệu
    page.wait_for_function("document.getElementById('view-pipeline').dataset.trangThai === 'trong'")
    assert page.locator("#view-pipeline .btn-primary:visible").count() == 0
    _du_lieu(api)
    page.reload()
    page.wait_for_function("document.getElementById('view-pipeline').dataset.trangThai === 'san_sang'")
    assert page.locator("#view-pipeline .btn-primary:visible").count() == 1
    assert page.locator("#btnRun.btn-primary").count() == 1
    page.click("#btnRun")
    page.wait_for_selector("#runXong:not([hidden])", timeout=20000)
    page.wait_for_function("document.getElementById('view-pipeline').dataset.trangThai === 'xong'")
    assert page.locator("#view-pipeline .btn-primary:visible").count() == 0
    assert not loi


# ---------------------------------------------------------------- T3-12
def test_chan_thanh_ben_chi_hien_khi_mat_ket_noi_va_nut_hoat_anh_nam_trong_menu(api, mo):
    tat_wharton(api)
    page, loi = mo()
    for ma in ("dbStatusLine", "lastRunLine", "cheDoHienThi"):
        assert page.locator("#" + ma).is_hidden(), ma
    assert page.locator("#btnMotionToggle").is_hidden()
    page.click("#menuThanhBen > summary")
    assert page.locator("#btnMotionToggle").is_visible()
    assert page.inner_text("#btnMotionToggle") == "Hoạt ảnh: bật"
    page.keyboard.press("Escape")
    assert page.locator("#btnMotionToggle").is_hidden()
    page.evaluate("() => { const o = document.getElementById('dbStatusLine'); o.textContent = t('backend_khong_ket_noi'); o.hidden = false; }")
    assert page.locator("#dbStatusLine").is_visible()
    assert not loi


# ---------------------------------------------------------------- tab 04 (T3-32..T3-35)
def _mo_tab(page, ten):
    page.locator('[data-tab="%s"]' % ten).click()


def test_nhap_tai_cho_hang_hoc_sinh_moi_nam_ngay_duoi_o_tim_va_menu_ba_cham(api, mo):
    tat_wharton(api)
    _du_lieu(api, 3)
    page, loi = mo()
    _mo_tab(page, "fallback")
    page.wait_for_selector("#studentSearchInput")
    y_tim = page.locator("#studentSearchInput").bounding_box()["y"]
    y_moi = page.locator("#newStudentId").bounding_box()["y"]
    assert 0 < y_moi - y_tim < 120, (y_tim, y_moi)       # T3-32: cùng cụm với ô tìm, không nằm dưới danh sách
    page.fill("#newStudentId", "HS99")
    page.fill("#newStudentName", "Em Mới")
    page.click("#btnCreateStudent")
    page.wait_for_selector("#fallbackWorkArea:not([hidden])")
    # cuộn tới phiếu: đầu phiếu nằm trong khung nhìn
    assert page.evaluate("() => document.getElementById('fallbackWorkArea').getBoundingClientRect().top < window.innerHeight")
    # T3-34: ba nút phụ nằm trong menu ⋯
    assert page.locator("#btnDeleteStudent").is_hidden()
    page.click("#menuHocSinh > summary")
    for ma in ("btnXuatEmNay", "btnResetStudentEntry", "btnDeleteStudent"):
        assert page.locator("#" + ma).is_visible(), ma
    assert page.inner_text("#btnResetStudentEntry") == "Xoá toàn bộ phiếu của học sinh này"
    assert not loi


def test_nhap_tai_cho_khong_in_ma_tho_clb_va_khong_con_cau_hai_buoc(api, mo):
    tat_wharton(api)
    _du_lieu(api, 2)
    page, loi = mo()
    _mo_tab(page, "fallback")
    page.fill("#studentSearchInput", "HS01")
    page.click("#btnStudentSearch")
    page.locator("#studentSearchResults .hs-card").first.click()
    page.wait_for_selector("#testSelectionGrid .option-row")
    for sel in ("#testSelectionGrid", "#rankingSourceGrid"):
        assert "clb_a" not in page.inner_text(sel), sel       # T3-35: bỏ mã thô
    assert "không phụ thuộc nhau" not in page.inner_text("#view-fallback")
    assert not loi


def test_phieu_chi_hien_lop_khi_da_co_lop_va_bam_doi_moi_sua(api, mo):
    tat_wharton(api)
    api.create_or_update_club("clb_a", "CLB A", 3)
    for sid, lop in (("HS01", "10A1"), ("HS02", "10A2")):
        api.create_student_if_missing(sid, "Học sinh " + sid[2:])
        assert api.set_student_class(sid, lop)["ok"]
    page, loi = mo()
    _mo_tab(page, "fallback")
    page.fill("#studentSearchInput", "HS01")
    page.click("#btnStudentSearch")
    page.locator("#studentSearchResults .hs-card").first.click()
    page.wait_for_selector("#kioskLopChu:not([hidden])")
    assert page.inner_text("#kioskLopChu") == "10A1"
    assert page.locator("#kioskLop").is_hidden()              # T3-33: chọn lớp một lần ở hàng tạo
    page.click("#btnKioskLopSua")
    assert page.locator("#kioskLop").is_visible() and page.locator("#kioskLopChu").is_hidden()
    assert not loi


# ---------------------------------------------------------------- T3-29
def test_diem_quyet_tam_mac_dinh_chi_hien_ho_so_co_van_de_co_dem_va_xem_tat_ca(api, mo):
    bat_wharton(api)
    dung_clb(api, A=5, B=5)
    dung_hs(api, "HS1", "HS2", tick={"HS2": ["A"]})
    assert api.submit_preferences("HS1", ["A", "B"])["ok"]
    assert api.submit_preferences("HS2", ["A", "B"])["ok"]
    assert api.submit_wharton("HS1", {}, {"A": 50, "B": 50})["ok"]   # HS1 hợp lệ; HS2 thi A mà chưa chia điểm
    page, loi = mo()
    _mo_tab(page, "admin")
    page.locator('#qlTabWh').click()
    page.wait_for_selector("#whQlBody tr")
    assert page.is_checked("#whLocChiLoi")
    assert page.locator("#whQlBody tr").evaluate_all("rs => rs.map(r => r.dataset.studentId)") == ["HS2"]
    assert page.inner_text("#whQlDem").startswith("1 ")
    page.click("#btnWhXemTatCa")
    page.wait_for_function("() => document.querySelectorAll('#whQlBody tr').length === 2")
    assert not page.is_checked("#whLocChiLoi") and page.locator("#btnWhXemTatCa").is_hidden()
    assert not loi
