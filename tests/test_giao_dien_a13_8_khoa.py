"""A13.8 lỗi 3.2: kiosk "Nhập tại chỗ" — điểm quyết tâm đang khoá và em ĐÃ có điểm thì hai nút
"Lưu CLB dự thi" / "Lưu nguyện vọng" bị vô hiệu hoá kèm ghi chú; em chưa có điểm, hoặc đã mở khoá,
thì nút bình thường. Dữ liệu MÔ PHỎNG dựng trong test."""

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from _wharton import chen_bids  # noqa: E402
from test_giao_dien_wharton import _chon, _cho_buoc_3, mo  # noqa: E402,F401


def _khoa_db(api, khoa=True):
    with api._ket_noi_ghi() as cur:
        cur.execute("INSERT OR REPLACE INTO wharton_lock (id, is_locked, locked_at) VALUES (1, ?, 'x')",
                    (1 if khoa else 0,))


def test_khoa_va_em_co_diem_thi_hai_nut_luu_bi_vo_hieu_va_co_ghi_chu(mo):  # noqa: F811
    page, api, loi = mo()
    chen_bids(api, [("HS1", "A", 1, 100), ("HS1", "B", 2, 50), ("HS1", "C", 2, 50)])
    _khoa_db(api)
    _chon(page, "HS1")
    _cho_buoc_3(page)
    assert page.locator("#btnSubmitTestSelection").is_disabled()
    assert page.locator("#btnSubmitPreferences").is_disabled()
    assert page.locator("#testSelectionKhoa").is_visible()
    assert page.locator("#preferencesKhoa").is_visible()
    assert "khoá" in page.locator("#preferencesKhoa").inner_text()
    assert not loi, loi


def test_khoa_nhung_em_chua_co_diem_thi_nut_luu_binh_thuong(mo):  # noqa: F811
    page, api, loi = mo()
    _khoa_db(api)
    _chon(page, "HS1")
    _cho_buoc_3(page)
    assert page.locator("#btnSubmitTestSelection").is_enabled()
    assert page.locator("#btnSubmitPreferences").is_enabled()
    assert page.locator("#testSelectionKhoa").is_hidden()
    assert not loi, loi


def test_chua_khoa_em_co_diem_thi_nut_luu_binh_thuong(mo):  # noqa: F811
    page, api, loi = mo()
    chen_bids(api, [("HS1", "A", 1, 100), ("HS1", "B", 2, 50), ("HS1", "C", 2, 50)])
    _chon(page, "HS1")
    _cho_buoc_3(page)
    assert page.locator("#btnSubmitTestSelection").is_enabled()
    assert page.locator("#btnSubmitPreferences").is_enabled()
    assert page.locator("#preferencesKhoa").is_hidden()
    assert not loi, loi


def test_chuyen_tu_em_bi_khoa_sang_em_khac_nut_bat_lai(mo):  # noqa: F811
    page, api, loi = mo()
    chen_bids(api, [("HS1", "A", 1, 100), ("HS1", "B", 2, 50), ("HS1", "C", 2, 50)])
    _khoa_db(api)
    _chon(page, "HS1")
    _cho_buoc_3(page)
    assert page.locator("#btnSubmitPreferences").is_disabled()
    _chon(page, "HS2")
    _cho_buoc_3(page)
    assert page.locator("#btnSubmitPreferences").is_enabled()
    assert page.locator("#preferencesKhoa").is_hidden()
    assert not loi, loi


def test_wharton_tat_hai_nut_luu_luon_bat(mo):  # noqa: F811
    page, api, loi = mo(bat=False)
    _chon(page, "HS1")
    assert page.locator("#btnSubmitTestSelection").is_enabled()
    assert page.locator("#btnSubmitPreferences").is_enabled()
    assert page.locator("#preferencesKhoa").is_hidden()
    assert not loi, loi
