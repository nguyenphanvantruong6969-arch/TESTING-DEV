"""A13.12 (ngoài phạm vi A13, Truong chọn sửa): đổi ngôn ngữ khi đang mở một học sinh ở "Nhập tại chỗ"
thì dòng "Đã xếp hạng ở n/N buổi" (`fallback_phu_buoi`) và liên kết "xoá" (`btn_remove_ranked`) ở
Bước 2 phải vẽ lại sang ngôn ngữ mới. Dữ liệu MÔ PHỎNG dựng trong test."""

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from _wharton import bat_wharton, dung_clb, dung_hs  # noqa: E402
from test_giao_dien_wharton import _chon, mo  # noqa: E402,F401


def _du_lieu_hai_buoi(api, bat):
    bat_wharton(api)
    dung_clb(api, A=(5, "thu_5"), B=(5, "thu_5"), C=(5, "thu_3"), D=(5, "thu_3"))
    dung_hs(api, "HS1", tick={"HS1": ["A", "C"]})
    assert api.submit_preferences("HS1", ["A", "C"])["ok"]


def test_doi_ngon_ngu_ve_lai_dong_phu_buoi_va_nut_xoa_o_buoc_2(mo):  # noqa: F811
    page, api, loi = mo(du_lieu=_du_lieu_hai_buoi)
    _chon(page, "HS1")
    page.wait_for_selector("#rankingList li button")
    page.wait_for_selector("#fallbackPhuBuoi .phu-buoi-tom")
    assert page.locator("#rankingList li button").first.inner_text() == "xoá"
    assert "Đã xếp hạng ở 2/2" in page.locator("#fallbackPhuBuoi .phu-buoi-tom").inner_text()

    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("document.documentElement.lang === 'en'")
    page.wait_for_function(
        "() => document.querySelector('#rankingList li button').textContent === 'remove'")
    page.wait_for_function(
        "() => /Ranked in 2 of 2/.test(document.querySelector('#fallbackPhuBuoi .phu-buoi-tom').textContent)")

    page.evaluate("window.I18N.setLang('vi')")
    page.wait_for_function(
        "() => document.querySelector('#rankingList li button').textContent === 'xoá'")
    page.wait_for_function(
        "() => /Đã xếp hạng ở 2\\/2/.test(document.querySelector('#fallbackPhuBuoi .phu-buoi-tom').textContent)")
    assert not loi, loi


def test_doi_ngon_ngu_khong_mat_xep_hang_dang_chon(mo):  # noqa: F811
    """Vẽ lại chỉ đổi chữ: danh sách xếp hạng (chưa lưu hay đã lưu) giữ nguyên thứ tự."""
    page, api, loi = mo(du_lieu=_du_lieu_hai_buoi)
    _chon(page, "HS1")
    page.wait_for_selector("#rankingList li button")
    truoc = page.locator("#rankingList li .hs-chip-hang").all_inner_texts()
    ten = page.locator("#rankingList li .ranking-ten").all_inner_texts()
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("document.documentElement.lang === 'en'")
    page.wait_for_function(
        "() => document.querySelector('#rankingList li button').textContent === 'remove'")
    assert page.locator("#rankingList li .hs-chip-hang").all_inner_texts() == truoc
    assert page.locator("#rankingList li .ranking-ten").all_inner_texts() == ten
    assert not loi, loi
