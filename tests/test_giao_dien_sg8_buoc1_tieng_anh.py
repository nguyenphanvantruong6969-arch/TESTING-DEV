# -*- coding: utf-8 -*-
"""SG-8 (M5), giao diện (Playwright + Chromium): bước 1 của "Chuẩn bị đợt" hiện HOÀN TOÀN bằng tiếng Anh khi đổi
sang English — câu lỗi/cảnh báo, kiểm trước khi mở cổng, cột Loại, tóm tắt "(Tự do 1, …)" — và vẫn là chữ Việt
cũ khi để tiếng Việt. Dữ liệu MÔ PHỎNG (tên CLB không dấu để cả trang English không còn chữ có dấu nào)."""
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_giao_dien_fa_m7_nguon import _xlsx_phieu, mo as mo_buoc1  # noqa: E402,F401
from test_sg8_thong_bao_buoc1 import dong_phieu  # noqa: E402

DAU = re.compile(r"[À-ÿĀ-ſƠơƯưẠ-ỹ]")

DONG = [
    dong_phieu("Free Club", mo="Có", phong="30", ly_do="Small room"),
    dong_phieu("Limited Club", buoi="Thứ 3", mo="Không", cho="20"),
    dong_phieu("Select Club", mo="Không", cho="10", ly_do="Gear", can_thi="Có", thu_thach="Essay", moc="5"),
    dong_phieu("Broken Club", mo=""),
    dong_phieu("Limited Club", buoi="Thứ 3", mo="Không", cho="20"),
]


def _nap(mo, tmp_path, ngon_sau_khi_nap):
    page, loi = mo()
    page.locator("#cb-b1-tep").set_input_files(_xlsx_phieu(tmp_path, DONG))
    page.wait_for_selector('#cb-buoc-1 [data-trang-thai="do"]')
    if ngon_sau_khi_nap == "en":
        page.evaluate("window.I18N.setLang('en')")
        page.wait_for_function("document.documentElement.lang === 'en'")
        page.wait_for_function("() => (document.querySelector('#cb-buoc-1 .cb-trang-thai') || {textContent: ''}).textContent.includes('clubs loaded')")
    return page, loi


def test_tieng_anh_buoc_1_khong_con_chu_viet(mo_buoc1, tmp_path):  # noqa: F811
    page, loi = _nap(mo_buoc1, tmp_path, "en")
    chu = page.inner_text("#cb-buoc-1")
    assert not DAU.findall(chu), [m for m in DAU.findall(chu)] and chu
    # đủ ba Loại, câu lỗi, cảnh báo và kiểm trước đều có mặt (bằng tiếng Anh)
    assert "Free" in chu and "Limited" in chu and "Selective" in chu
    assert "Broken Club: hasn't answered question 2 (can extra groups be opened?)" in chu     # câu dịch thật, không phải mã
    assert "phieu_" not in chu
    assert page.locator("#cb-b1-loi li").count() == 1
    assert page.locator("#cb-b1-canh-bao li").count() == 6
    assert page.locator("#cb-b1-chan li").count() == 1
    assert not loi, loi


def test_tieng_viet_buoc_1_giu_chu_cu(mo_buoc1, tmp_path):  # noqa: F811
    page, loi = _nap(mo_buoc1, tmp_path, "vi")
    chu = page.inner_text("#cb-buoc-1")
    assert "Broken Club: chưa trả lời câu 2 (mở thêm nhóm được không): không phân loại được, đã bỏ qua" in chu
    assert "Free Club: khai Tự do nhưng có ghi lý do giới hạn; CLB bị giới hạn thật không được khai Tự do, cần admin xem lại" in chu
    assert "Select Club: CLB Tuyển chọn: chờ ban quản lý duyệt trước khi mở cổng" in chu
    assert "(Tự do 1, Giới hạn 1, Tuyển chọn 1)" in chu
    assert "Buổi \"Thứ 3\" chưa có CLB loại Tự do." in chu
    assert not loi, loi


@pytest.mark.parametrize("ngon", ["vi", "en"])
def test_tep_ket_qua_cu_hien_chu_khong_hien_json(mo_buoc1, api, tmp_path, ngon):  # noqa: F811
    from test_sg8_thong_bao_buoc1 import ghi_ket_qua_cu
    page, loi = mo_buoc1()
    if ngon == "en":
        page.evaluate("window.I18N.setLang('en')")
        page.wait_for_function("document.documentElement.lang === 'en'")
    ghi_ket_qua_cu(api, tmp_path)
    page.evaluate("window.ChuanBi.lamMoi()")
    page.wait_for_selector("#cb-b1-loi li")
    chu = page.inner_text("#cb-b1-loi")
    assert "{" not in chu and '"ma"' not in chu, chu
    if ngon == "vi":
        assert "Cu A: chưa trả lời câu 2 (mở thêm nhóm được không): không phân loại được, đã bỏ qua" in chu
    else:
        assert "Cu A: hasn't answered question 2" in chu
    assert "Cu B: câu lạ đã lưu" in chu                 # mã lạ: giữ chữ đã lưu
    assert not loi, loi
