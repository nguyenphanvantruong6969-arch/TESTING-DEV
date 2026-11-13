"""FG-1 (STEP0, spec §3), phần giao diện (Playwright + Chromium): menu "Tính năng sau khi xếp…" ở dòng không gian làm
việc mở hộp thoại 5 ô + số ngày; lưu qua `update_workspace_config`. Dữ liệu MÔ PHỎNG.

Giao ước cho người làm FG-1: hộp thoại có `role="dialog"`; nhãn ô dùng lại các chuỗi sẵn có của trình hướng dẫn
(`ws_r_fa_phan_hoi`, …); nút lưu tên "Lưu".
"""
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

import cau_hinh_ws as ch  # noqa: E402
from test_ws_giao_dien import mo_trang  # noqa: E402,F401 (fixture)

NHAN_PHAN_HOI = "Phản hồi 3 câu và khảo sát tuần 3"


def _mo_hop_thoai(page):
    page.locator("#btnWorkspace").click()
    page.locator('tr[data-slug="truong-hoc"] .menu-khac > summary').click()
    page.locator('tr[data-slug="truong-hoc"]').get_by_text(re.compile("Tính năng sau khi xếp")).click()
    hop = page.get_by_role("dialog")
    hop.wait_for()
    return hop


def test_khong_fa_thi_cac_o_bi_khoa_va_co_mot_dong_giai_thich(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    hop = _mo_hop_thoai(page)
    o = hop.get_by_role("checkbox")
    assert o.count() == len(ch.CO_SAU_XEP)
    assert all(o.nth(i).is_disabled() for i in range(o.count()))
    assert "loại CLB" in hop.inner_text()                      # nói phải chọn FA khi TẠO không gian làm việc
    assert not loi, loi


def test_bat_phan_hoi_roi_khung_hien_o_the_chi_tiet(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    assert api.update_workspace_config({"rules": {"fa_daa": True}})["ok"]
    hop = _mo_hop_thoai(page)
    hop.get_by_label(NHAN_PHAN_HOI).check()
    hop.get_by_role("button", name="Lưu").click()
    page.wait_for_function("() => !document.querySelector('[role=dialog]')")
    assert api.get_workspace_config()["data"]["config"]["rules"]["fa_phan_hoi"] is True
    if page.locator("#wsBtnDong").count() and page.locator("#wsBtnDong").is_visible():
        page.locator("#wsBtnDong").click()
    page.locator('[data-tab="others"]').click()
    page.wait_for_selector("#phanHoiTongPanel:not([hidden])")      # không cần khởi động lại
    assert not loi, loi


def test_so_ngay_ngoai_khoang_giu_hop_thoai_va_hien_loi(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    assert api.update_workspace_config({"rules": {"fa_daa": True}})["ok"]
    hop = _mo_hop_thoai(page)
    hop.get_by_role("spinbutton").fill("30")
    hop.get_by_role("button", name="Lưu").click()
    page.wait_for_timeout(400)
    assert page.get_by_role("dialog").count() == 1              # còn mở
    assert hop.get_by_role("alert").count() >= 1 or "14" in hop.inner_text()
    assert api.get_workspace_config()["data"]["config"]["rules"]["fa_khieu_nai_so_ngay"] == 3
    assert not loi, loi
