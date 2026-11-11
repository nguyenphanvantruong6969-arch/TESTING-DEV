"""GAP-5 (Playwright + Chromium): ba câu phản hồi một chạm ở thẻ "Kết quả", tổng hợp ở thẻ "Chi tiết và xuất tệp".

  * cờ `fa_phan_hoi` tắt: không có khung nào;
  * bật: gõ mã, chạm 4 sao, "Có", "Đặt huy chương", gửi -> câu cảm ơn và một dòng trong CSDL; khung tổng hợp hiện 1 em.
Dữ liệu MÔ PHỎNG.
"""
import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_fa_gap5_phan_hoi import _dung  # noqa: E402
from test_giao_dien_fa_gap1_theo_doi import mo  # noqa: E402,F401 (fixture)


def _tat(api):
    _dung(api, ph=False)


def test_co_tat_khong_co_khung(mo):  # noqa: F811
    page, _, loi = mo(_tat)
    page.wait_for_timeout(300)
    assert page.locator("#phanHoiTongPanel[hidden]").count() == 1
    page.locator('[data-tab="results"]').click()
    page.wait_for_timeout(300)
    assert page.locator("#phanHoiPanel[hidden]").count() == 1
    assert not loi, loi


def test_cham_ba_cau_roi_gui(mo):  # noqa: F811
    page, api, loi = mo(_dung)
    page.locator('[data-tab="results"]').click()
    page.wait_for_selector("#phanHoiPanel:not([hidden])")
    page.fill("#phMa", "s1")
    page.locator('button.ph-hai-long[data-gia-tri="4"]').click()
    page.locator('button.ph-hieu[data-gia-tri="1"]').click()
    page.locator('button.ph-kho[data-gia-tri="huy_chuong"]').click()
    assert page.locator('button.ph-hai-long[data-gia-tri="4"]').get_attribute("aria-pressed") == "true"
    page.locator("#btnGuiPhanHoi").click()
    page.wait_for_function("() => document.getElementById('phKetQua').textContent.includes('Cảm ơn')")
    with api._ket_noi_doc() as cur:
        assert [tuple(r) for r in cur.execute("SELECT hai_long, hieu_ly_do, kho_nhat FROM fa_phan_hoi")] == \
            [(4, 1, "huy_chuong")]
    page.locator('[data-tab="others"]').click()
    page.wait_for_function("() => document.getElementById('phTongHop').textContent.includes('1')")
    assert not loi, loi


def test_thieu_cau_tra_loi_khong_gui(mo):  # noqa: F811
    page, api, loi = mo(_dung)
    page.locator('[data-tab="results"]').click()
    page.wait_for_selector("#phanHoiPanel:not([hidden])")
    page.fill("#phMa", "s1")
    page.locator('button.ph-hai-long[data-gia-tri="4"]').click()
    page.locator("#btnGuiPhanHoi").click()
    page.wait_for_function("() => document.getElementById('phKetQua').textContent.length > 0")
    assert "Cảm ơn" not in page.locator("#phKetQua").inner_text()
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM fa_phan_hoi").fetchone()[0] == 0
    assert not loi, loi
