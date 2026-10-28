"""A13.12 — thẻ Quản lý / Điểm quyết tâm (BAO_CAO_SOAT_NHAP 3.4): sau một thao tác ĐỔI dữ liệu trên
máy chủ, màn sửa không được điền lại chữ cũ đang gõ đè lên dữ liệu mới. Chromium thật; MÔ PHỎNG."""

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from _wharton import dong_bids  # noqa: E402
from test_giao_dien_wharton_quan_ly import _mo_man_sua, _o, mo  # noqa: E402,F401


def test_xoa_diem_mot_em_roi_man_sua_khong_dien_lai_chu_dang_go(mo):  # noqa: F811
    page, api, loi = mo()
    _mo_man_sua(page, "HS2")
    assert _o(page, "B").input_value() == "60"
    _o(page, "B").fill("55")                                  # đang gõ, chưa lưu
    nut = page.locator("#btnWhXoaMot")
    nut.click()
    nut.click()                                               # xác nhận xoá điểm HS2 trên máy chủ
    page.wait_for_function(
        "() => document.querySelector('#toastStack') && "
        "document.querySelector('#toastStack').textContent.includes('HS2')")
    assert [b for b in dong_bids(api) if b[0] == "HS2"] == []
    page.wait_for_timeout(600)
    assert _o(page, "B").input_value() == "", "chữ đang gõ (55) đã đè lên dữ liệu vừa đổi trên máy chủ"
    assert not loi, loi


def test_doi_ngon_ngu_van_giu_chu_dang_go(mo):  # noqa: F811
    page, api, loi = mo()
    _mo_man_sua(page, "HS2")
    _o(page, "B").fill("55")
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("document.documentElement.lang === 'en'")
    page.wait_for_timeout(600)
    assert _o(page, "B").input_value() == "55"
    assert not loi, loi
