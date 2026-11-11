"""FA-M7 (Playwright + Chromium): bước "1. CLB" rồi "2. Đề thi" của thẻ Chuẩn bị đợt lần lượt chuyển xanh.

Bước 1: nạp tệp Phiếu thiết lập CLB -> bảng CLB + trạng thái xanh. Bước 2: tải tệp mẫu (điền sẵn CLB của bước 1),
điền câu hỏi, nạp lại -> xanh; tệp có lỗi -> đỏ, liệt kê lỗi. Mở lại thẻ vẫn thấy hai bước xanh. Dữ liệu MÔ PHỎNG.
"""
import os

import openpyxl
import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import cau_hinh_ws as ch  # noqa: E402
import forms_dot  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

forms_dot.nap_mau_forms()
import chuyen_phieu_clb as pc  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _phieu(ten, buoi, mo, phong="", cho="", ly_do=""):
    d = dict(zip(pc.TIEU_DE_PHIEU, [ten, buoi, "15:30", "Phòng A", mo, cho, ly_do, phong, "8",
                                    "Không", "", "", "", ""]))
    return [d[h] for h in pc.TIEU_DE_PHIEU]


@pytest.fixture
def mo(api, tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []
    api.thu_muc_xuat = str(tmp_path / "tai_ve")
    os.makedirs(api.thu_muc_xuat)

    def _mo():
        ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True}})
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", viewport={"width": 1400, "height": 1600}, bypass_csp=True)
        page.set_default_timeout(8000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.wait_for_function("() => !document.querySelector('.nav-item[data-tab=chuan_bi]').hidden")
        page.locator('.nav-item[data-tab="chuan_bi"]').click()
        return page, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _xlsx_phieu(tmp_path, dong):
    p = tmp_path / "phieu.xlsx"
    wb = openpyxl.Workbook()
    wb.active.append(pc.TIEU_DE_PHIEU)
    for r in dong:
        wb.active.append(r)
    wb.save(p)
    return str(p)


def test_buoc_1_roi_buoc_2_lan_luot_xanh(mo, api, tmp_path):
    page, loi = mo()
    page.wait_for_selector('#cb-buoc-1 [data-trang-thai="chua"]')
    page.wait_for_selector('#cb-buoc-2 [data-trang-thai="chua"]')
    # Bước 1
    page.locator("#cb-b1-tep").set_input_files(_xlsx_phieu(tmp_path, [
        _phieu("CLB Cờ vua", "Thứ 2", "Có", phong="30"),
        _phieu("CLB Bóng rổ", "Thứ 2", "Không", cho="20", ly_do="Sân nhỏ")]))
    page.wait_for_selector('#cb-buoc-1 [data-trang-thai="xanh"]')
    assert page.locator("#cb-b1-bang tbody tr").count() == 2
    assert "CLB Cờ vua" in page.locator("#cb-b1-bang").inner_text()
    assert page.locator('#cb-buoc-2 [data-trang-thai="xanh"]').count() == 0
    # Bước 2: tải mẫu
    page.locator("#cb-b2-tai-mau").click()
    page.wait_for_function("() => document.querySelector('#cb-b2-mau-ghi') && "
                           "document.querySelector('#cb-b2-mau-ghi').textContent.includes('MAU_DE_THI_KIOSK')")
    mau = os.path.join(api.thu_muc_xuat, "MAU_DE_THI_KIOSK.xlsx")
    assert os.path.isfile(mau)
    wb = openpyxl.load_workbook(mau)
    ma = {r[3].value: r[2].value for r in wb["CLB"].iter_rows(min_row=2)}
    # tệp lỗi trước: đáp án sai -> đỏ + liệt kê, chưa ghi gì
    loi_tep = str(tmp_path / "de_loi.xlsx")
    wb["De_thi"].append([ma["CLB Cờ vua"], "", "Q?", "a", "b", "c", "d", "z"])
    wb.save(loi_tep)
    page.locator("#cb-b2-tep").set_input_files(loi_tep)
    page.wait_for_selector('#cb-buoc-2 [data-trang-thai="do"]')
    assert "dap_an" in page.locator("#cb-b2-loi").inner_text()
    assert not os.path.exists(forms_dot.duong_de_dot(api.db_path))
    # tệp đúng -> xanh
    ok = str(tmp_path / "de_ok.xlsx")
    wb = openpyxl.load_workbook(mau)
    wb["De_thi"].append([ma["CLB Cờ vua"], "", "Q?", "a", "b", "c", "d", "b"])
    wb.save(ok)
    page.locator("#cb-b2-tep").set_input_files(ok)
    page.wait_for_selector('#cb-buoc-2 [data-trang-thai="xanh"]')
    assert os.path.isfile(forms_dot.duong_de_dot(api.db_path))
    # mở lại thẻ: cả hai bước vẫn xanh (trạng thái nằm ở tệp của đợt, không ở trang)
    page.reload()
    page.wait_for_selector("#dropZone")
    page.wait_for_function("() => !document.querySelector('.nav-item[data-tab=chuan_bi]').hidden")
    page.locator('.nav-item[data-tab="chuan_bi"]').click()
    page.wait_for_selector('#cb-buoc-1 [data-trang-thai="xanh"]')
    page.wait_for_selector('#cb-buoc-2 [data-trang-thai="xanh"]')
    assert not loi, loi


def test_buoc_1_co_dong_loi_thi_do_nhung_van_liet_ke_clb(mo, tmp_path):
    page, loi = mo()
    page.locator("#cb-b1-tep").set_input_files(_xlsx_phieu(tmp_path, [
        _phieu("CLB Cờ vua", "Thứ 2", "Có", phong="30"), _phieu("CLB Hỏng", "Thứ 2", "")]))
    page.wait_for_selector('#cb-buoc-1 [data-trang-thai="do"]')
    assert page.locator("#cb-b1-bang tbody tr").count() == 1
    assert "CLB Hỏng" in page.locator("#cb-b1-loi").inner_text()
    assert not loi, loi


def test_buoc_2_chua_co_buoc_1_bao_loi_ro(mo):
    page, loi = mo()
    page.locator("#cb-b2-tai-mau").click()
    page.wait_for_selector(".toast.is-error")
    assert not loi, loi
