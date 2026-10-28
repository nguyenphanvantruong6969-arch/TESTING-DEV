"""A13.12 — kiosk "Nhập tại chỗ" (docs/ke_hoach/BAO_CAO_SOAT_NHAP.md, Chromium thật). Dữ liệu MÔ PHỎNG.

  2.2      ô điểm quyết tâm tự điền 100 (khung một CLB) KHÔNG được gửi lên khi Lưu (cách A);
  1.8/2.4  ô tự điền không làm vừa chọn em đã báo "Chưa lưu" giả;
  1.7/2.3  phản hồi lưu về muộn: mốc "đã lưu" và dòng thông báo không ghi đè lên em đang mở /
           các CLB bấm thêm trong lúc chờ vẫn là "chưa lưu";
  1.9/2.6  xoá em đang mở thì dọn sạch Bước 3, xếp hạng và mốc "đã lưu";
  2.5      chọn em khác thì dòng "Đã lưu n nguyện vọng" của em trước biến mất;
  1.6      trang danh sách vượt tổng (xoá em cuối của trang) lùi về trang cuối, không báo "không tìm thấy".
"""

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from _wharton import bat_wharton, dong_bids, dung_clb, dung_hs  # noqa: E402
from test_giao_dien_wharton import _chon, _cho_buoc_3, _dem, _o, mo  # noqa: E402,F401


def _du_lieu_hai_em(api, bat):
    """HS1 thi A, HS2 thi B: ô tick khác nhau để mốc "đã lưu" của hai em phân biệt được."""
    if bat:
        bat_wharton(api)
    dung_clb(api, A=5, B=5, C=5, D=5)
    dung_hs(api, "HS1", "HS2", tick={"HS1": ["A"], "HS2": ["B"]})
    assert api.submit_preferences("HS1", ["A", "B", "C"])["ok"]
    assert api.submit_preferences("HS2", ["A", "B"])["ok"]


# ------------------------------------------------------------------ 2.2 + 1.8/2.4

def test_o_tu_dien_100_khong_bao_chua_luu_va_khong_duoc_gui_len(mo):  # noqa: F811
    page, api, loi = mo(du_lieu=_du_lieu_hai_em)
    _chon(page, "HS2")                       # HS2: thi B (quỹ 1), A không thi (quỹ 2): hai khung một CLB
    _cho_buoc_3(page)
    assert _o(page, "B").input_value() == "100" and _o(page, "B").is_disabled()
    assert _o(page, "A").input_value() == "100" and _o(page, "A").is_disabled()
    assert page.locator("#chuaLuuWharton").is_hidden()          # 1.8 / 2.4: không còn "Chưa lưu" giả
    page.locator("#btnSubmitWharton").click()
    page.wait_for_function(
        "() => document.getElementById('whartonFeedback').textContent.includes('Đã lưu')")
    assert dong_bids(api) == []                                  # 2.2: không ghi 100 tự điền
    # Thêm CLB C vào cùng quỹ 2: quỹ đó phải đòi chia lại, không phải để A mang sẵn 100 còn C nhận 0.
    assert api.submit_preferences("HS2", ["A", "B", "C"])["ok"]
    w = api.get_student_entry_state("HS2")["data"]["wharton"]
    assert w["w1"] == {} and w["w2"] == {}
    assert not loi, loi


def test_khung_mot_clb_ket_hop_khung_hai_clb_chi_gui_o_nguoi_nhap(mo):  # noqa: F811
    page, api, loi = mo(du_lieu=_du_lieu_hai_em)
    _chon(page, "HS1")        # thi A; không thi B, C: khung quỹ 1 một CLB (tự điền), quỹ 2 hai CLB
    _cho_buoc_3(page)
    assert page.locator("#chuaLuuWharton").is_hidden()
    _o(page, "B").fill("60")
    assert page.locator("#chuaLuuWharton").is_visible()          # em gõ thật thì là "chưa lưu"
    _o(page, "C").fill("40")
    page.locator("#btnSubmitWharton").click()
    page.wait_for_function("() => document.getElementById('chuaLuuWharton').hidden")
    assert dong_bids(api) == [("HS1", "B", 2, 60), ("HS1", "C", 2, 40)]
    assert not loi, loi


# ------------------------------------------------------------------ 1.7 / 2.3: phản hồi về muộn

def _giu_yeu_cau(page, ten_ham):
    """Giữ mọi yêu cầu `ten_ham`; trả (danh sách đang giữ, hàm thả)."""
    giu = []
    page.route("**/__api__/" + ten_ham, lambda route: giu.append(route))

    def tha():
        for r in giu:
            r.continue_()
        giu.clear()
    return giu, tha


def test_luu_tick_phan_hoi_ve_muon_khong_ghi_moc_len_em_khac(mo):  # noqa: F811
    page, api, loi = mo(du_lieu=_du_lieu_hai_em)
    _chon(page, "HS1")
    giu, tha = _giu_yeu_cau(page, "submit_test_selection")
    page.locator("#btnSubmitTestSelection").click()
    page.wait_for_function("() => true")
    for _ in range(40):
        if giu:
            break
        page.wait_for_timeout(50)
    assert giu
    _chon(page, "HS2")                         # sang HS2 khi phản hồi của HS1 còn treo
    tha()
    page.wait_for_timeout(600)
    assert page.locator("#chuaLuuThi").is_hidden(), "mốc của HS1 đã bị ghi lên HS2"
    assert page.locator("#testSelectionFeedback").inner_text().strip() == ""
    assert not loi, loi


def test_bam_them_clb_trong_luc_cho_luu_nguyen_vong_thi_clb_do_van_chua_luu(mo):  # noqa: F811
    page, api, loi = mo(du_lieu=_du_lieu_hai_em)
    _chon(page, "HS1")
    giu, tha = _giu_yeu_cau(page, "submit_preferences")
    page.locator("#btnSubmitPreferences").click()
    for _ in range(40):
        if giu:
            break
        page.wait_for_timeout(50)
    assert giu
    page.locator('#rankingSourceGrid .option-row[data-club-id="D"]').click()   # thêm D khi đang chờ
    assert page.locator("#rankingList li").count() == 4
    tha()
    page.wait_for_function(
        "() => document.getElementById('preferencesFeedback').textContent.includes('Đã lưu')")
    assert page.locator("#chuaLuuNv").is_visible(), "CLB thêm trong lúc chờ bị coi là đã lưu"
    assert not loi, loi


# ------------------------------------------------------------------ 1.9 / 2.6 / 2.5

def test_xoa_em_dang_mo_don_sach_trang_thai_buoc_3_va_moc(mo):  # noqa: F811
    page, api, loi = mo(du_lieu=_du_lieu_hai_em)
    _chon(page, "HS1")
    _cho_buoc_3(page)
    nut = page.locator("#btnDeleteStudent")
    nut.click()
    nut.click()
    page.wait_for_function("() => document.getElementById('fallbackWorkArea').hidden")
    assert page.evaluate("currentFallbackStudent === null && whartonState === null "
                         "&& currentRanking.length === 0 && daLuuNv.length === 0 "
                         "&& daLuuThi.length === 0 && daLuuWharton === ''")
    assert page.locator("#fbWhartonBody .wh-khung").count() == 0
    assert page.locator("#fbWhartonStep").is_hidden()
    assert not loi, loi


def test_chon_em_khac_xoa_dong_da_luu_cua_em_truoc(mo):  # noqa: F811
    page, api, loi = mo(du_lieu=_du_lieu_hai_em)
    _chon(page, "HS1")
    page.locator("#btnSubmitPreferences").click()
    page.wait_for_function(
        "() => document.getElementById('preferencesFeedback').textContent.includes('Đã lưu')")
    _chon(page, "HS2")
    assert page.locator("#preferencesFeedback").inner_text().strip() == ""
    assert page.locator("#testSelectionFeedback").inner_text().strip() == ""
    assert not loi, loi


# ------------------------------------------------------------------ 1.6: trang vượt tổng

def test_xoa_em_cuoi_cua_trang_thi_lui_ve_trang_truoc_khong_bao_khong_tim_thay(mo):  # noqa: F811
    def du_lieu(api, bat):
        bat_wharton(api, bat)
        dung_clb(api, A=5)
        dung_hs(api, *["S%02d" % i for i in range(9)])        # 9 em, 8 em / trang: trang 2 có 1 em
    page, api, loi = mo(du_lieu=du_lieu)
    page.locator("#btnFallbackNextPage").click()
    page.wait_for_selector('#studentSearchResults .hs-card[data-student-id="S08"]')
    assert api.delete_student("S08")["ok"]
    page.locator("#btnStudentSearch").click()                  # tải lại: trang 2 không còn em nào
    page.wait_for_function("() => document.querySelectorAll('#studentSearchResults .hs-card').length === 8")
    assert page.evaluate("fallbackStudentPage") == 1
    assert "1" in page.locator("#fallbackPaginationLabel").inner_text()
    assert not loi, loi
