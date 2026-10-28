"""A13.12 — thẻ Quản lý: CLB, danh sách học sinh, chi tiết điểm chuẩn (BAO_CAO_SOAT_NHAP 3.2, 3.3, 3.9,
3.10). Chromium thật; dữ liệu MÔ PHỎNG (bộ của test_giao_dien_diem_chuan)."""

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_giao_dien_diem_chuan import _cho_quan_ly, mo  # noqa: E402,F401


def _yeu_cau_dem(page, ten_ham):
    dem = []
    page.on("request", lambda r: dem.append(r.url) if r.url.endswith("/__api__/" + ten_ham) else None)
    return dem


def test_3_9_phan_hoi_cu_cua_clb_truoc_khong_de_len_clb_sau(mo):  # noqa: F811
    page, api, loi, _ = mo()
    _cho_quan_ly(page)
    giu = []

    def treo_a(route):
        if '"A"' in (route.request.post_data or ""):
            giu.append(route)
        else:
            route.continue_()

    page.route("**/__api__/get_diem_chuan_clb", treo_a)
    page.evaluate("""() => {
        dc.chon = 'A'; window.__pa = loadChiTietDiemChuan();
        dc.chon = 'C'; window.__pc = loadChiTietDiemChuan();
    }""")
    page.wait_for_function("() => dc.ct && dc.ct.club_id === 'C'")
    for r in giu:
        r.continue_()
    page.wait_for_timeout(700)
    assert page.evaluate("dc.ct.club_id") == "C", "phản hồi của CLB A về sau đã đè lên CLB C"
    assert not loi, loi


def test_3_3_trang_vuot_tong_o_danh_sach_hoc_sinh_ve_lai_trang_cuoi(mo):  # noqa: F811
    page, api, loi, _ = mo()
    page.locator('#qlTabs [data-ql-tab="hs"]').click()
    page.wait_for_selector("#adminStudentTableBody tr")
    page.evaluate("adminStudentPage = 5")
    page.evaluate("loadAdminStudents()")
    page.wait_for_function("() => adminStudentPage === 1")
    assert page.locator("#adminStudentTableBody tr").count() == 8
    assert not loi, loi


def test_3_10_luu_clb_lam_moi_bang_tai_theo_buoi_va_lich_tuan(mo):  # noqa: F811
    page, api, loi, _ = mo()
    page.locator('#qlTabs [data-ql-tab="clb"]').click()
    page.wait_for_selector("#btnSaveClub")
    page.wait_for_timeout(500)
    dem_tai = _yeu_cau_dem(page, "get_tai_theo_buoi")
    dem_buoi = _yeu_cau_dem(page, "get_danh_sach_buoi")
    page.fill("#clubFormId", "Z")
    page.fill("#clubFormName", "CLB Z")
    page.fill("#clubFormCapacity", "5")
    page.locator("#btnSaveClub").click()
    page.wait_for_function(
        "() => document.getElementById('clubFormFeedback').textContent.includes('Z')")
    page.wait_for_timeout(500)
    assert dem_tai, "bảng tải theo buổi / lịch tuần không được làm mới sau khi lưu CLB"
    assert dem_buoi, "danh sách buổi không được làm mới sau khi lưu CLB"
    assert not loi, loi


def test_3_10_xoa_clb_lam_moi_bang_tai_theo_buoi(mo):  # noqa: F811
    page, api, loi, _ = mo()
    assert api.create_or_update_club("Z", "CLB Z", 5, 0, "")["ok"]
    page.locator('#qlTabs [data-ql-tab="clb"]').click()
    page.evaluate("loadAdminClubs()")
    page.wait_for_selector('#adminClubTableBody tr:has-text("CLB Z")')
    dem_tai = _yeu_cau_dem(page, "get_tai_theo_buoi")
    hang = page.locator('#adminClubTableBody tr', has_text="CLB Z")
    nut = hang.locator("button.btn-icon-danger")
    nut.click()
    nut.click()
    page.wait_for_function("() => document.querySelector('#toastStack') && "
                           "document.querySelector('#toastStack').textContent.includes('Z')")
    page.wait_for_timeout(500)
    assert dem_tai
    assert not loi, loi


def test_3_2_xoa_clb_con_diem_da_cham_toast_noi_so_diem_va_tep_sao_luu(mo):  # noqa: F811
    page, api, loi, _ = mo(bat=False, chay=False)         # tắt điểm quyết tâm: không có khoá chặn ô tick
    assert api.create_or_update_club("Z", "CLB Z", 5, 0, "")["ok"]
    assert api.submit_test_selection("HS1", ["Z"])["ok"]
    assert api.submit_club_scores("Z", [{"student_id": "HS1", "score": 7}])["ok"]
    page.locator('#qlTabs [data-ql-tab="clb"]').click()
    page.evaluate("loadAdminClubs()")
    page.wait_for_selector('#adminClubTableBody tr:has-text("CLB Z")')
    hang = page.locator('#adminClubTableBody tr', has_text="CLB Z")
    nut = hang.locator("button.btn-icon-danger")
    nut.click()
    nut.click()
    page.wait_for_function("() => document.querySelector('#toastStack') && "
                           "document.querySelector('#toastStack').textContent.includes('sao lưu')")
    chu = page.locator("#toastStack").inner_text()
    assert "1 điểm đã chấm" in chu and "1 ô tick thi" in chu and ".bak-" in chu
    assert not loi, loi
