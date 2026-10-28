"""Mục "Kết quả sắp xếp" của phần Xuất dữ liệu bị khoá khi chưa có kết quả (A13.5, vấn đề #4;
Playwright + Chromium, qua `browser_host`). Dữ liệu là dữ liệu MÔ PHỎNG.

  * chưa có kết quả: ô xuất kết quả (và ô kèm CSV) bị khoá, bỏ chọn, kèm dòng vàng;
  * các mục xuất khác (dữ liệu đầu vào...) vẫn dùng được;
  * chạy xếp bị chặn thì vẫn khoá; chạy xếp thành công thì mở lại và chọn sẵn.
"""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _wharton import bat_wharton, chen_bids, dung_clb, dung_hs  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402

DONG_VANG = "Chưa có kết quả xếp. Chạy xếp trước."


def _du_lieu(api, bi_chan=False):
    if bi_chan:
        bat_wharton(api)
    dung_clb(api, A=5, B=5)
    dung_hs(api, "HS1", "HS2")
    for sid in ("HS1", "HS2"):
        assert api.submit_preferences(sid, ["A", "B"])["ok"]
    if bi_chan:
        chen_bids(api, [("HS1", "A", 2, 40), ("HS1", "B", 2, 20),
                        ("HS2", "A", 2, 50), ("HS2", "B", 2, 50)])


@pytest.fixture
def mo(tmp_path, api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo(bi_chan=False):
        _du_lieu(api, bi_chan)
        api.thu_muc_xuat = str(tmp_path / "TaiXuong")
        os.makedirs(api.thu_muc_xuat, exist_ok=True)
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", viewport={"width": 1280, "height": 1400}, bypass_csp=True)
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


def _sang_ket_qua(page):
    page.locator('[data-tab="results"]').click()
    page.wait_for_selector("#xuatPanel")
    page.wait_for_timeout(300)


def test_chua_co_ket_qua_o_xuat_ket_qua_bi_khoa_kem_dong_vang(mo):
    page, api, loi = mo()
    _sang_ket_qua(page)
    page.wait_for_function("() => document.getElementById('xuatKetQua').disabled")
    assert not page.locator("#xuatKetQua").is_checked()
    assert page.locator("#xuatKemCsv").is_disabled()
    dong = page.locator("#xuatKetQuaKhoa")
    assert dong.is_visible() and dong.inner_text().strip() == DONG_VANG
    assert "canh-bao-vang" in dong.get_attribute("class")
    assert not loi, loi


def test_muc_khac_van_xuat_duoc_khi_chua_co_ket_qua(mo):
    page, api, loi = mo()
    _sang_ket_qua(page)
    page.wait_for_function("() => document.getElementById('xuatKetQua').disabled")
    assert page.locator("#xuatDauVao").is_enabled()
    page.check("#xuatDauVao")
    page.click("#btnXuatTuyChon")
    page.wait_for_function(
        "() => document.getElementById('xuatFeedback').textContent.length > 0")
    tep = os.listdir(api.thu_muc_xuat)
    assert len(tep) == 1 and tep[0].startswith("SO_NHAP_CLB")
    assert not loi, loi


def test_chay_xep_thanh_cong_thi_mo_khoa_va_chon_san(mo):
    page, api, loi = mo()
    _sang_ket_qua(page)
    page.wait_for_function("() => document.getElementById('xuatKetQua').disabled")
    page.locator('[data-tab="pipeline"]').click()
    page.click("#btnRun")
    page.wait_for_selector(".toast.is-success", timeout=20000)
    _sang_ket_qua(page)
    page.wait_for_function("() => !document.getElementById('xuatKetQua').disabled")
    assert page.locator("#xuatKetQua").is_checked()
    assert page.locator("#xuatKetQuaKhoa").is_hidden()
    page.click("#btnXuatTuyChon")
    page.wait_for_function("() => document.getElementById('xuatFeedback').textContent.includes('xlsx')")
    assert any(f.endswith(".xlsx") for f in os.listdir(api.thu_muc_xuat))
    assert not loi, loi


def test_chay_xep_bi_chan_thi_nut_van_khoa(mo):
    page, api, loi = mo(bi_chan=True)
    page.locator('[data-tab="pipeline"]').click()
    page.click("#btnRun")
    page.wait_for_selector("#logPanel:not([hidden])", timeout=20000)
    _sang_ket_qua(page)
    page.wait_for_function("() => document.getElementById('xuatKetQua').disabled")
    assert page.locator("#xuatKetQuaKhoa").is_visible()
    assert os.listdir(api.thu_muc_xuat) == []
    assert not loi, loi


def test_tieng_anh_dong_vang_doi_theo(mo):
    page, api, loi = mo()
    _sang_ket_qua(page)
    page.wait_for_function("() => document.getElementById('xuatKetQua').disabled")
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("document.documentElement.lang === 'en'")
    assert page.locator("#xuatKetQuaKhoa").inner_text().strip() == \
        "No allocation results yet. Run the allocation first."
    assert not loi, loi
