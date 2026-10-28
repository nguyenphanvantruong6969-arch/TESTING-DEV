"""Thẻ "Nhập tại chỗ" — Bước 3 · Điểm Wharton (Playwright + Chromium, qua `browser_host`).

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test. Mọi phép kiểm cuối cùng nhìn vào CSDL,
không chỉ nhìn chữ trên màn hình.

  * Wharton TẮT: không có khung Bước 3 (màn hình y như cũ);
  * BẬT: mỗi buổi hai khung (đã thi / không thi), mỗi ô một CLB, bộ đếm "Đã dùng X / 100"; khung
    chỉ có một CLB thì tự điền 100 và khoá ô; khung rỗng không hiện;
  * Lưu gọi `submit_wharton`; sai thì báo và KHÔNG ghi gì; đúng thì CSDL có dòng đúng tier;
  * lưu Bước 1 (tick) hoặc Bước 2 (nguyện vọng) thì Bước 3 vẽ lại; dòng lệch tier thì nhắc
    "Cần chia lại điểm";
  * điểm chưa lưu ở Bước 3 mà chọn học sinh khác thì được hỏi; học sinh không thấy điểm của người khác;
  * tiếng Anh: chữ đổi theo, không còn chữ có dấu.
"""

import os
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _wharton import bat_wharton, chen_bids, dong_bids, dung_clb, dung_hs  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402

DAU_VIET = re.compile(
    "[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]", re.I)


def _dung_du_lieu(api, bat=True):
    if bat:
        bat_wharton(api)
    dung_clb(api, A=5, B=5, C=5, D=5)
    dung_hs(api, "HS1", "HS2", tick={"HS1": ["A"], "HS2": ["A"]})
    assert api.create_student_if_missing("HS1", "Ngô Văn An")["ok"]
    assert api.submit_preferences("HS1", ["A", "B", "C"])["ok"]
    assert api.submit_preferences("HS2", ["A", "B"])["ok"]
    return api


@pytest.fixture
def mo(tmp_path, api):
    """mo(bat=True) -> (page, api, loi). Đóng trình duyệt khi test xong."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo(bat=True, du_lieu=None):
        (du_lieu or _dung_du_lieu)(api, bat)
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", bypass_csp=True)
        page.set_default_timeout(8000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.locator('[data-tab="fallback"]').click()
        page.wait_for_selector("#studentSearchResults .hs-card")
        return page, api, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _chon(page, ma):
    page.locator('#studentSearchResults .hs-card[data-student-id="%s"]' % ma).click()
    page.wait_for_function(
        "(ma) => !document.getElementById('fallbackWorkArea').hidden &&"
        " document.getElementById('currentStudentLabel').textContent.includes(ma)", arg=ma)
    page.wait_for_selector("#testSelectionGrid .option-row")


def _cho_buoc_3(page):
    page.wait_for_selector("#fbWhartonStep:not([hidden]) .wh-khung")


def _khung(page, quy, buoi=None):
    sel = '#fbWhartonBody .wh-khung[data-quy="%d"]' % quy
    if buoi:
        sel += '[data-buoi="%s"]' % buoi
    return page.locator(sel)


def _dem(page, quy, buoi=None):
    return _khung(page, quy, buoi).locator(".wh-dem").inner_text()


def _o(page, cid):
    return page.locator('#fbWhartonBody input.wh-diem[data-clb="%s"]' % cid)


# ------------------------------------------------------------------ tắt: màn hình như cũ

def test_wharton_tat_khong_co_buoc_3(mo):
    page, api, loi = mo(bat=False)
    _chon(page, "HS1")
    assert page.locator("#fbWhartonStep").is_hidden()
    assert page.locator("#fbWhartonBody .wh-khung").count() == 0
    assert not loi, loi


# ------------------------------------------------------------------ bật: hai khung

def test_hai_khung_tu_dien_va_khoa_khung_mot_clb(mo):
    page, api, loi = mo()
    _chon(page, "HS1")
    _cho_buoc_3(page)
    # em thi A; không thi B, C (D không có trong nguyện vọng nên không hiện)
    assert page.locator("#fbWhartonBody .wh-khung").count() == 2
    assert _khung(page, 1).locator("input.wh-diem").count() == 1
    assert _o(page, "A").input_value() == "100" and _o(page, "A").is_disabled()
    assert _dem(page, 1) == "Đã dùng 100 / 100"
    assert _khung(page, 2).locator("input.wh-diem").count() == 2
    assert _o(page, "B").input_value() == "" and _o(page, "B").is_enabled()
    assert _o(page, "C").is_enabled() and _o(page, "D").count() == 0
    assert _dem(page, 2) == "Đã dùng 0 / 100"
    assert _o(page, "B").get_attribute("type") == "number"
    assert _o(page, "B").get_attribute("min") == "0" and _o(page, "B").get_attribute("step") == "1"
    # tiêu đề dùng nhãn của workspace, không viết cứng
    assert "Các CLB đã thi" in _khung(page, 1).inner_text()
    assert "Các CLB không thi" in _khung(page, 2).inner_text()
    assert not loi, loi


def test_khung_rong_khong_hien(mo):
    """Em không thi CLB nào thì khung "đã thi" vắng hẳn, chỉ còn khung "không thi"."""
    def du_lieu(api, bat):
        _dung_du_lieu(api, bat)
        dung_hs(api, "HS3")
        assert api.submit_preferences("HS3", ["B", "C"])["ok"]
    page, api, loi = mo(du_lieu=du_lieu)
    _chon(page, "HS3")
    _cho_buoc_3(page)
    assert _khung(page, 1).count() == 0 and _khung(page, 2).count() == 1
    assert not loi, loi


def test_bo_dem_cap_nhat_theo_tung_phim(mo):
    page, api, loi = mo()
    _chon(page, "HS1")
    _cho_buoc_3(page)
    _o(page, "B").press_sequentially("6")
    assert _dem(page, 2) == "Đã dùng 6 / 100"
    _o(page, "B").press_sequentially("0")
    assert _dem(page, 2) == "Đã dùng 60 / 100"
    _o(page, "C").fill("55")
    assert _dem(page, 2) == "Đã dùng 115 / 100"
    assert "is-vuot" in _khung(page, 2).locator(".wh-dem").get_attribute("class")
    assert not loi, loi


# ------------------------------------------------------------------ lưu

def test_luu_thieu_40_bao_loi_va_khong_ghi_gi_roi_luu_dung_100_thi_co_dong(mo):
    page, api, loi = mo()
    _chon(page, "HS1")
    _cho_buoc_3(page)
    _o(page, "B").fill("60")
    assert _dem(page, 2) == "Đã dùng 60 / 100"
    page.locator("#btnSubmitWharton").click()
    page.wait_for_function(
        "() => document.getElementById('whartonFeedback').textContent.includes('40')")
    assert dong_bids(api) == []
    assert "Chưa dùng hết điểm quyết tâm" in page.locator("#whartonFeedback").inner_text()

    _o(page, "C").fill("40")
    page.locator("#btnSubmitWharton").click()
    page.wait_for_function(
        "() => document.getElementById('whartonFeedback').textContent.includes('Đã lưu')")
    # A13.12 (2.2, Truong chọn cách A): ô tự điền 100 của khung một CLB KHÔNG ghi vào CSDL.
    assert dong_bids(api) == [("HS1", "B", 2, 60), ("HS1", "C", 2, 40)]
    assert page.locator("#chuaLuuWharton").is_hidden()
    assert not loi, loi


def test_o_trong_la_khong_dat_diem_va_server_quyet_dinh_khong_lam_tron(mo):
    page, api, loi = mo()
    _chon(page, "HS1")
    _cho_buoc_3(page)
    _o(page, "B").fill("60.5")                    # trình duyệt KHÔNG làm tròn; server từ chối số lẻ
    _o(page, "C").fill("39.5")
    page.locator("#btnSubmitWharton").click()
    page.wait_for_function(
        "() => document.getElementById('whartonFeedback').textContent.trim() !== ''")
    assert dong_bids(api) == []
    assert "số nguyên" in page.locator("#whartonFeedback").inner_text()
    assert not loi, loi


def test_o_chua_luu_hien_dau_chua_luu_va_het_sau_khi_luu(mo):
    page, api, loi = mo()
    _chon(page, "HS1")
    _cho_buoc_3(page)
    # khung một CLB tự điền 100: KHÔNG tính là "chưa lưu" (A13.12, 1.8 / 2.4: máy chủ tự điền, không ghi)
    assert page.locator("#chuaLuuWharton").is_hidden()
    _o(page, "B").fill("60")
    _o(page, "C").fill("40")
    page.locator("#btnSubmitWharton").click()
    page.wait_for_function("() => document.getElementById('chuaLuuWharton').hidden")
    _o(page, "C").fill("30")
    assert page.locator("#chuaLuuWharton").is_visible()
    assert not loi, loi


# ------------------------------------------------------------------ đồng bộ với Bước 1, 2

def test_bo_clb_o_buoc_2_xoa_dong_va_buoc_3_ve_lai_thieu_40(mo):
    page, api, loi = mo()
    _chon(page, "HS1")
    _cho_buoc_3(page)
    _o(page, "B").fill("60")
    _o(page, "C").fill("40")
    page.locator("#btnSubmitWharton").click()
    page.wait_for_function("() => document.getElementById('chuaLuuWharton').hidden")
    assert len(dong_bids(api)) == 2           # A13.12: không có dòng 100 tự điền của A

    page.locator("#rankingList li").nth(2).locator("button").click()       # bỏ C khỏi nguyện vọng
    page.locator("#btnSubmitPreferences").click()
    page.wait_for_function(
        "() => document.getElementById('preferencesFeedback').textContent.includes('Đã lưu')")
    assert dong_bids(api) == [("HS1", "B", 2, 60)]                          # dòng C bị xoá
    page.wait_for_function("() => document.querySelectorAll('#fbWhartonBody input.wh-diem').length === 2")
    assert _o(page, "C").count() == 0 and _o(page, "B").input_value() == "60"
    assert _dem(page, 2) == "Đã dùng 60 / 100"                              # thiếu 40
    assert not loi, loi


def test_tick_them_b_o_buoc_1_thi_buoc_3_nhac_chia_lai(mo):
    page, api, loi = mo()
    chen_bids(api, [("HS1", "A", 1, 100), ("HS1", "B", 2, 60), ("HS1", "C", 2, 40)])
    _chon(page, "HS1")
    _cho_buoc_3(page)
    assert "Cần chia lại điểm" not in page.locator("#fbWhartonStep").inner_text()

    page.locator('#testSelectionGrid .option-row[data-club-id="B"]').click()
    page.locator("#btnSubmitTestSelection").click()
    page.wait_for_function(
        "() => document.getElementById('testSelectionFeedback').textContent.includes('Đã lưu')")
    page.wait_for_function(
        "() => document.getElementById('fbWhartonStep').textContent.includes('Cần chia lại điểm')")
    assert _khung(page, 1).locator("input.wh-diem").count() == 2          # A, B giờ cùng quỹ 1
    assert "Cần chia lại điểm" in _khung(page, 1).inner_text()
    assert dong_bids(api) == [("HS1", "A", 1, 100), ("HS1", "B", 2, 60), ("HS1", "C", 2, 40)]
    assert not loi, loi


# ------------------------------------------------------------------ rời màn, riêng tư, nhiều buổi

def test_diem_chua_luu_o_buoc_3_ma_chon_hoc_sinh_khac_thi_duoc_hoi(mo):
    page, api, loi = mo()
    _chon(page, "HS1")
    _cho_buoc_3(page)
    _o(page, "B").fill("10")
    the = page.locator('#studentSearchResults .hs-card[data-student-id="HS2"]')
    the.click()                                              # lần bấm đầu chỉ cảnh báo
    page.wait_for_selector(".toast.is-error", state="attached")
    assert "HS1" in page.locator("#currentStudentLabel").inner_text()
    assert _o(page, "B").input_value() == "10"
    the.click()                                              # lần hai: bỏ thay đổi và đi tiếp
    page.wait_for_function(
        "() => document.getElementById('currentStudentLabel').textContent.includes('HS2')")
    assert dong_bids(api) == []
    assert not loi, loi


def test_hoc_sinh_khong_thay_diem_cua_nguoi_khac(mo):
    page, api, loi = mo()
    chen_bids(api, [("HS2", "A", 1, 100), ("HS2", "B", 2, 73)])
    _chon(page, "HS1")
    _cho_buoc_3(page)
    van_ban = page.locator("#fbWhartonStep").inner_text()
    assert "73" not in van_ban
    assert all((o.input_value() or "") != "73" for o in page.locator("#fbWhartonBody input").all())
    assert "độ đông" not in van_ban.lower() and "điểm chuẩn" not in van_ban.lower()
    assert not loi, loi


def test_nhieu_buoi_moi_buoi_hai_khung_theo_thu_tu_ngay(tmp_path, api, mo):
    def du_lieu(api, bat):
        bat_wharton(api)
        dung_clb(api, A=(5, "thu_5"), B=(5, "thu_5"), C=(5, "thu_3"), D=(5, "thu_3"))
        dung_hs(api, "HS1", tick={"HS1": ["A", "C"]})
        assert api.submit_preferences("HS1", ["A", "B", "C", "D"])["ok"]
    page, api, loi = mo(du_lieu=du_lieu)
    _chon(page, "HS1")
    _cho_buoc_3(page)
    buoi = page.locator("#fbWhartonBody .wh-khung").evaluate_all(
        "ks => ks.map(k => k.dataset.buoi + ':' + k.dataset.quy)")
    assert buoi == ["thu_3:1", "thu_3:2", "thu_5:1", "thu_5:2"]      # thứ 3 trước thứ 5
    for cid in "ABCD":                                  # mỗi khung chỉ một CLB: tự điền 100, khoá
        assert _o(page, cid).is_disabled() and _o(page, cid).input_value() == "100"
    assert page.locator("#chuaLuuWharton").is_hidden()   # A13.12: tự điền không phải "chưa lưu"
    page.locator("#btnSubmitWharton").click()
    page.wait_for_function(
        "() => document.getElementById('whartonFeedback').textContent.includes('Đã lưu')")
    assert dong_bids(api) == []                          # A13.12: ô tự điền không đi vào CSDL
    assert not loi, loi


# ------------------------------------------------------------------ ngôn ngữ

def test_tieng_anh_chu_buoc_3_doi_theo_ngon_ngu_va_khong_con_chu_co_dau(mo):
    page, api, loi = mo()
    _chon(page, "HS1")
    _cho_buoc_3(page)
    assert "Bước 3" in page.locator("#fbWhartonStep h3").inner_text()
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("document.documentElement.lang === 'en'")
    van_ban = page.locator("#fbWhartonStep").inner_text()
    assert "Step 3" in van_ban and "Commitment points" in van_ban
    assert _dem(page, 1) == "Used 100 / 100"
    assert not DAU_VIET.search(van_ban), van_ban
    assert not loi, loi


def test_doi_ngon_ngu_khi_loi_goi_api_con_treo_buoc_3_van_ve_lai_ngay(mo):
    """Kiosk: đổi ngôn ngữ khi mọi lời gọi API còn treo thì Bước 3 vẫn đổi tức thì."""
    page, api, loi = mo()
    _chon(page, "HS1")
    _cho_buoc_3(page)
    giu, nha = [], []

    def _treo(route):
        route.continue_() if nha else giu.append(route)

    page.route("**/__api__/*", _treo)
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("document.documentElement.lang === 'en'")
    van_ban = page.locator("#fbWhartonStep").inner_text()
    assert "Step 3" in van_ban and not DAU_VIET.search(van_ban), van_ban
    nha.append(True)
    for r in giu:
        r.continue_()
    page.wait_for_timeout(400)
    assert not DAU_VIET.search(page.locator("#fbWhartonStep").inner_text())
    assert not loi, loi


def test_hai_cau_chinh_thong_bao_cho_hoc_sinh(mo):
    """Chia thiếu: câu chính là "Chưa dùng hết điểm Wharton" kèm số thiếu và quỹ."""
    page, api, loi = mo()
    _chon(page, "HS1")
    _cho_buoc_3(page)
    _o(page, "B").fill("50")
    page.locator("#btnSubmitWharton").click()
    page.wait_for_function(
        "() => document.getElementById('whartonFeedback').textContent.includes('50')")
    chu = page.locator("#whartonFeedback").inner_text()
    assert chu.startswith("Chưa dùng hết điểm quyết tâm") and "quỹ 2" in chu
    assert not loi, loi
