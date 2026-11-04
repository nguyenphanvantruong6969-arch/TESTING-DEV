# -*- coding: utf-8 -*-
"""Hiệu ứng rê chuột lên khung và nút tắt hiệu ứng — kiểm bằng TRÌNH DUYỆT THẬT.

Ba điều phải đúng:

  1. Mặc định hiệu ứng BẬT: rê chuột lên một `.panel` thì khung nhấc lên
     (có `transform`) và có bóng.
  2. Bấm nút "Hiệu ứng" thì tắt: rê chuột lên khung không còn nhấc, không
     còn chuyển tiếp nào chạy — lựa chọn còn nguyên sau khi tải lại trang.
  3. Nhãn nút là chữ ĐỘNG (bật/tắt), nên đổi ngôn ngữ phải dịch lại nó.

Máy nào không có playwright/Chromium thì bỏ qua cả tệp.
"""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402


@pytest.fixture
def trang(api):
    if CHROMIUM is None:
        pytest.skip("không có Chromium")
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(bypass_csp=True)
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    page.goto(url)
    page.wait_for_selector("#btnMotionToggle", state="attached")
    yield page, loi
    br.close()
    pw.stop()


def _bam_nut(page):
    """T3-12: nút nằm trong menu ⋯ cạnh nút EN; mở menu rồi bấm."""
    page.click("#menuThanhBen > summary")
    page.click("#btnMotionToggle")


def _khung_khi_re_chuot(page):
    khung = page.locator("#view-pipeline .panel").first
    khung.hover()
    page.wait_for_timeout(400)  # chờ chuyển tiếp 220ms chạy xong
    return khung.evaluate(
        "e => { const s = getComputedStyle(e);"
        " return {transform: s.transform, shadow: s.boxShadow,"
        " transition: s.transitionDuration}; }")


def test_mac_dinh_bat_hieu_ung(trang):
    page, loi = trang
    nut = page.locator("#btnMotionToggle")
    assert nut.get_attribute("aria-pressed") == "true"
    assert nut.text_content() == "Hoạt ảnh: bật"
    s = _khung_khi_re_chuot(page)
    assert s["transform"] != "none"
    assert s["shadow"] != "none"
    assert loi == []


def test_tat_hieu_ung_va_nho_sau_khi_tai_lai(trang):
    page, loi = trang
    _bam_nut(page)
    nut = page.locator("#btnMotionToggle")
    assert nut.get_attribute("aria-pressed") == "false"
    assert nut.text_content() == "Hoạt ảnh: tắt"
    s = _khung_khi_re_chuot(page)
    assert s["transform"] == "none"
    assert s["shadow"] == "none"
    assert s["transition"] == "0s"

    page.reload()
    page.wait_for_selector("#btnMotionToggle", state="attached")
    assert page.locator("html.tat-hieu-ung").count() == 1
    assert page.locator("#btnMotionToggle").get_attribute("aria-pressed") == "false"

    _bam_nut(page)
    assert page.locator("html.tat-hieu-ung").count() == 0
    assert loi == []


def test_nhan_nut_doi_theo_ngon_ngu(trang):
    page, loi = trang
    page.click("#btnLangToggle")
    assert page.locator("#btnMotionToggle").text_content() == "Animations: on"
    _bam_nut(page)
    assert page.locator("#btnMotionToggle").text_content() == "Animations: off"
    page.click("#btnLangToggle")
    assert page.locator("#btnMotionToggle").text_content() == "Hoạt ảnh: tắt"
    assert loi == []
