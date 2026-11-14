"""SG-7 (H4, M1): bước 4 và khung cảnh báo của thẻ Nhập cùng một luật FG-6 qua MỘT hàm dùng chung.

Mỗi mã: số đếm + tối đa 5 ví dụ + một dòng "và N trường hợp nữa"; nhóm ≤ 5 thì hiện hết, không dòng "nữa".
Chromium qua `browser_host`; API trả cảnh báo giả (route) để nạp 110 + 3 cảnh báo mà không dựng cả sổ nhập.
Dữ liệu MÔ PHỎNG. Không có Chromium thì bỏ qua (khi đó KHÔNG phải là đã qua).
"""
import json
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import cau_hinh_ws as ch  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo(chuan_bi=True):
        ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True}})
        assert api.dat_fa_duong("B")["ok"]
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", viewport={"width": 1400, "height": 1600}, bypass_csp=True)
        page.set_default_timeout(15000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        if not chuan_bi:
            return page, loi
        page.wait_for_function("() => !document.querySelector('.nav-item[data-tab=chuan_bi]').hidden")
        page.locator('.nav-item[data-tab="chuan_bi"]').click()
        page.wait_for_function("() => window.ChuanBi.duong() === 'B'")
        return page, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _canh_bao_buoc4(n1=110, n2=3):
    ds = [{"dong": i, "ma": "phieu_nop_nhieu_lan", "noi_dung": "Phiếu nộp nhiều lần số %03d" % i} for i in range(1, n1 + 1)]
    ds += [{"dong": 900 + i, "ma": "phieu_mac_dinh_ky_truoc", "noi_dung": "Mặc định kỳ trước số %d" % i} for i in range(1, n2 + 1)]
    return ds


def _canh_bao_nhap(n1=110, n2=3):
    ds = [{"code": "wharton_chua_dung_het", "params": {"student_id": "HS%03d" % i, "thieu": 100, "quy": 1}}
          for i in range(1, n1 + 1)]
    ds += [{"code": "wharton_tang_lech", "params": {"student_id": "KH%d" % i}} for i in range(1, n2 + 1)]
    return ds


def _route_buoc4(page, canh_bao):
    ok = lambda d: {"status": 200, "content_type": "application/json", "body": json.dumps({"ok": True, "data": d, "errors": []})}  # noqa: E731
    tep = [{"ten": "dk.xlsx", "loai": "dang_ky", "bien_the_doan": "", "loi": None}]
    page.route("**/__api__/nhan_dien_tep_forms", lambda r: r.fulfill(**ok({"tep": tep, "can_chon_de": False})))
    kq = {"trang_thai": "xong", "n_hoc_sinh": 10, "n_bai_thi": 0, "canh_bao": canh_bao, "ghi_chu": [],
          "cau_co_co": [], "xem_truoc": None, "loi_xem_truoc": []}
    page.route("**/__api__/chuyen_tep_forms", lambda r: r.fulfill(**ok(kq)))


def _kiem_nhom(hop, ma_dau, ma_hai):
    """Hai nhóm: 110 cái và 3 cái. Nhóm lớn: số đếm + 5 ví dụ + 'và 105 trường hợp nữa'; nhóm nhỏ: 3 dòng, không 'nữa'."""
    nhom = hop.locator(".canh-bao-nhom")
    assert nhom.count() == 2
    lon, nho = nhom.nth(0), nhom.nth(1)
    assert "110" in lon.locator(".canh-bao-tieu-de").inner_text()
    assert lon.locator(".canh-bao-dong").count() == 5
    assert "105" in lon.locator(".canh-bao-con-lai").inner_text()
    assert "trường hợp nữa" in lon.locator(".canh-bao-con-lai").inner_text()
    assert nho.locator(".canh-bao-dong").count() == 3
    assert nho.locator(".canh-bao-con-lai").count() == 0
    assert hop.locator(".canh-bao-dong").count() == 8            # không có dòng thứ 6 của nhóm lớn
    chu = hop.inner_text()
    assert ma_dau not in chu and ma_hai not in chu              # không lộ mã nội bộ
    assert "SG-" not in chu and "FG-" not in chu


def test_buoc4_gom_theo_ma_nam_vi_du_va_dong_con_lai(mo):
    page, loi = mo()
    _route_buoc4(page, _canh_bao_buoc4())
    page.locator("#cb-nap-tep").set_input_files({"name": "dk.xlsx", "mimeType": "application/octet-stream", "buffer": b"x"})
    page.wait_for_selector("#cb-nap-chuyen:not([disabled])")
    page.locator("#cb-nap-chuyen").click()
    page.wait_for_selector("#cb-nap-canh-bao")
    hop = page.locator("#cb-nap-canh-bao")
    _kiem_nhom(hop, "phieu_nop_nhieu_lan", "phieu_mac_dinh_ky_truoc")
    assert "Phiếu nộp nhiều lần số 001" in hop.inner_text() and "số 006" not in hop.inner_text()
    assert not loi, loi


def test_khung_nhap_gom_theo_ma_nam_vi_du_va_dong_con_lai(mo):
    page, loi = mo(chuan_bi=False)
    page.evaluate("(w) => { canhBaoNhapGanNhat = w; veCanhBaoNhap(); }", _canh_bao_nhap())
    hop = page.locator("#importWarnings")
    assert hop.is_visible()
    _kiem_nhom(hop, "wharton_chua_dung_het", "wharton_tang_lech")
    assert hop.locator("button").count() == 0                    # không còn kiểu thứ ba (nút "Xem 5 dòng đầu")
    assert not loi, loi


def test_khung_nhap_it_dong_hien_het_khong_dong_nua(mo):
    page, loi = mo(chuan_bi=False)
    page.evaluate("(w) => { canhBaoNhapGanNhat = w; veCanhBaoNhap(); }", _canh_bao_nhap(5, 2))
    hop = page.locator("#importWarnings")
    assert hop.locator(".canh-bao-dong").count() == 7
    assert hop.locator(".canh-bao-con-lai").count() == 0 and hop.locator(".canh-bao-tieu-de").count() == 0
    assert not loi, loi


def test_hai_cho_dung_chung_mot_ham_va_khong_con_kieu_cu():
    nen = open(os.path.join(GOC, "js", "00_nen.js"), encoding="utf-8").read()
    van_hanh = open(os.path.join(GOC, "js", "02_van_hanh.js"), encoding="utf-8").read()
    buoc4 = open(os.path.join(GOC, "js", "12_chuan_bi_nap.js"), encoding="utf-8").read()
    assert nen.count("function veCanhBaoGom(") == 1
    assert "veCanhBaoGom(" in van_hanh and "veCanhBaoGom(" in buoc4
    assert "canh-bao-xem" not in van_hanh and "CANH_BAO_HIEN_DAU" not in van_hanh
    assert "slice(0, 30)" not in buoc4.split("veKetQua")[1].split("xem_truoc")[0]
