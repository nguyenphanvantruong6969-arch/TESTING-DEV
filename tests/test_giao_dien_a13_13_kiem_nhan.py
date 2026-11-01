"""Kiểm nhận A13.13 (giao diện), do phiên cha thiết kế; dữ liệu MÔ PHỎNG. Chromium thật.

  G1  trình tạo workspace, mẫu "Trường học": ô wzWharton tick sẵn; đổi priority sang "tier" thì
      ô không bật được và bước xem lại ghi "tắt"; đổi về "score" thì ô bật lại được;
  G2  workspace mặc định mới (KHÔNG đặt wharton): thẻ Nhập tại chỗ có Bước 3 điểm quyết tâm.
"""

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from _wharton import dung_clb, dung_hs  # noqa: E402
from rbda_priority_pipeline import dung_wharton  # noqa: E402
from test_giao_dien_wharton import _cho_buoc_3, _chon, mo  # noqa: E402,F401
from test_ws_giao_dien import mo_trang  # noqa: E402,F401


def _toi_buoc_luat(page):
    page.locator("#btnWorkspace").click()
    page.locator("#wsBtnMoi").click()
    page.fill("#wzTen", "Kiểm nhận")
    page.locator("#wzTiep").click()                     # -> bước 2 (nhãn)
    page.locator("#wzTiep").click()                     # -> bước 3 (luật)
    page.wait_for_selector("#wzWharton")


def test_G1_wizard_mau_truong_hoc_tick_san_va_theo_priority(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    _toi_buoc_luat(page)
    o = page.locator("#wzWharton")
    assert o.is_checked() and o.is_enabled()                  # tick sẵn (mẫu dựng sẵn bật)
    page.select_option("#wzPriority", "tier")
    assert o.is_disabled() and not o.is_checked()             # không thể bật
    page.locator("#wzTiep").click()                           # -> bước xem lại
    page.wait_for_selector("#rvWharton")
    assert page.locator("#rvWharton").inner_text().strip() in ("Tắt", "Off")
    page.locator("#wzLui").click()                            # về bước luật
    page.wait_for_selector("#wzWharton")
    page.select_option("#wzPriority", "score")
    assert page.locator("#wzWharton").is_enabled()            # bật lại được
    page.locator("#wzWharton").check()
    assert page.locator("#wzWharton").is_checked()
    assert not loi, loi


def _du_lieu_mac_dinh(api, _bat):
    """KHÔNG đặt wharton: dùng đúng mặc định của workspace mới."""
    dung_clb(api, A=5, B=5, C=5, D=5)
    dung_hs(api, "HS1", tick={"HS1": ["A"]})
    assert api.submit_preferences("HS1", ["A", "B", "C"])["ok"]


def test_G2_workspace_mac_dinh_hien_buoc_3(mo):  # noqa: F811
    page, api, loi = mo(du_lieu=_du_lieu_mac_dinh)
    assert dung_wharton(api._luat_nghiem()) is True       # mặc định thật, chưa ai đặt
    _chon(page, "HS1")
    _cho_buoc_3(page)
    assert page.locator("#fbWhartonBody .wh-khung").count() >= 1
    assert not loi, loi
