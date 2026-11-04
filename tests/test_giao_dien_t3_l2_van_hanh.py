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
