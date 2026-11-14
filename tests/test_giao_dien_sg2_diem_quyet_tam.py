"""SG-2 (C1), phần giao diện (Playwright + Chromium): hộp thoại "Tính năng sau khi xếp…" có ô "Dùng điểm quyết tâm".
Không FA: ô bật (mặc định) và tắt được, lưu qua `update_workspace_config`. FA: ô khoá kèm lý do. Dữ liệu MÔ PHỎNG."""
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_ws_giao_dien import mo_trang  # noqa: E402,F401 (fixture)


def _mo_hop_thoai(page):
    page.locator("#btnWorkspace").click()
    page.locator('tr[data-slug="truong-hoc"] .menu-khac > summary').click()
    page.locator('tr[data-slug="truong-hoc"]').get_by_text(re.compile("Tính năng sau khi xếp")).click()
    hop = page.get_by_role("dialog")
    hop.wait_for()
    return hop


def test_khong_fa_o_diem_quyet_tam_bat_va_tat_duoc(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    hop = _mo_hop_thoai(page)
    o = hop.get_by_role("switch", name="Dùng điểm quyết tâm")
    page.wait_for_function("() => !document.getElementById('wsTnWharton').disabled")
    assert o.is_checked()
    o.uncheck()
    hop.get_by_role("button", name="Lưu").click()
    page.wait_for_function("() => !document.querySelector('[role=dialog]')")
    assert api.get_workspace_config()["data"]["config"]["rules"]["wharton"] is False
    assert not loi, loi


def test_co_fa_o_diem_quyet_tam_khoa_kem_ly_do(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    assert api.update_workspace_config({"rules": {"fa_daa": True}})["ok"]
    hop = _mo_hop_thoai(page)
    o = hop.get_by_role("switch", name="Dùng điểm quyết tâm")
    page.wait_for_function("() => document.getElementById('wsTnWhartonGhiChu').textContent.includes('huy chương')")
    assert o.is_disabled() and o.is_checked()
    assert "không tắt được" in hop.inner_text()
    hop.get_by_role("button", name="Lưu").click()                  # lưu các ô FA không làm đổi điểm quyết tâm
    page.wait_for_function("() => !document.querySelector('[role=dialog]')")
    assert api.get_workspace_config()["data"]["config"]["rules"]["wharton"] is True
    assert not loi, loi


def test_khung_loi_chay_bi_chan_co_nut_mo_hop_thoai(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    page.evaluate("""() => showLog([
        {code: "wharton_ho_so_chua_hop_le", params: {n: 1}},
        {code: "wharton_chua_dung_het", params: {student_id: "h1", quy: 2, thieu: 100, buoi: "_"}}])""")
    nut = page.locator("#btnMoTinhNangTuLoi")
    nut.wait_for()
    assert "tắt" in page.locator("#logBox").inner_text()
    nut.click()
    hop = page.get_by_role("dialog")
    hop.get_by_role("switch", name="Dùng điểm quyết tâm").wait_for()
    assert not loi, loi
