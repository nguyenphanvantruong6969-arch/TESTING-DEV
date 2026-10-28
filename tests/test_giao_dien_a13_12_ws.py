"""A13.12 — trình hướng dẫn tạo workspace (BAO_CAO_SOAT_NHAP 4.8, 4.10). Chromium thật; MÔ PHỎNG.

  4.8   tạo xong mà mở workspace lỗi: bấm "Tạo" lần nữa chỉ thử MỞ lại cái đã tạo, không đẻ thêm
        workspace trùng ("name-2");
  4.10  nhãn bắt đầu bằng = + - @ bị chặn ngay ở bước 2 (cùng luật với backend), chỉ rõ mục sai.
"""

import json

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_ws_giao_dien import mo_trang  # noqa: E402,F401


def test_tao_xong_mo_loi_bam_tao_lai_khong_de_workspace_trung(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    lan = []

    def hong_lan_dau(route):
        lan.append(1)
        if len(lan) == 1:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(
                {"ok": False, "data": None, "errors": [{"code": "ws_loi_khong_ro", "params": {}}]}))
        else:
            route.continue_()

    page.route("**/__api__/open_workspace", hong_lan_dau)
    page.locator("#btnWorkspace").click()
    page.locator("#wsBtnMoi").click()
    page.fill("#wzTen", "Công ty ABC")
    for _ in range(3):
        page.locator("#wzTiep").click()
    page.locator("#wzTao").click()
    page.wait_for_function("() => document.querySelector('#toastStack').textContent.trim() !== ''")
    assert len(api.list_workspaces()["data"]["workspaces"]) == 2          # Trường học + Công ty ABC
    page.locator("#wzTao").click()                                         # thử lại
    page.wait_for_function(
        "n => document.querySelector('#wsTenHienTai').textContent === n", arg="Công ty ABC", timeout=10000)
    assert [w["name"] for w in api.list_workspaces()["data"]["workspaces"]].count("Công ty ABC") == 1
    assert len(api.list_workspaces()["data"]["workspaces"]) == 2
    assert not loi, loi


@pytest.mark.parametrize("o,chu", [("wzNhan_slot_vi", "-Dự án"), ("wzNhan_person_en", "=Employee"),
                                   ("wzNhan_slot_en", "@Project"), ("wzNhan_slot_vi", "+Dự án")])
def test_wizard_chan_nhan_bat_dau_bang_ky_tu_cong_thuc_o_buoc_2(mo_trang, o, chu):  # noqa: F811
    page, api, goc, loi = mo_trang()
    page.locator("#btnWorkspace").click()
    page.locator("#wsBtnMoi").click()
    page.fill("#wzTen", "A")
    page.locator("#wzTiep").click()
    page.fill("#" + o, chu)
    page.locator("#wzTiep").click()
    assert page.locator("#wzLoi").is_visible()
    assert page.locator("#" + o).is_visible()                 # vẫn ở bước 2
    assert "=" in page.locator("#wzLoi").inner_text()
    assert not loi, loi


def test_wizard_nhan_binh_thuong_van_di_tiep(mo_trang):  # noqa: F811
    page, api, goc, loi = mo_trang()
    page.locator("#btnWorkspace").click()
    page.locator("#wsBtnMoi").click()
    page.fill("#wzTen", "A")
    page.locator("#wzTiep").click()
    page.fill("#wzNhan_slot_vi", "Dự án 1-2")                 # dấu trừ ở GIỮA thì hợp lệ
    page.locator("#wzTiep").click()
    assert page.locator("#wzMaxChoices").is_visible()
    assert not loi, loi
