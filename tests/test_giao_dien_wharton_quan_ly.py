"""Thẻ "Quản lý" — khối "Điểm Wharton" (Playwright + Chromium, qua `browser_host`).

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test. Mọi phép kiểm cuối cùng nhìn vào CSDL, không
chỉ nhìn chữ trên màn hình.

  * Wharton TẮT: khối không hiện, thẻ Quản lý còn đủ các khối cũ;
  * BẬT: bảng điểm đúng số và tổng; tìm không dấu; lọc "chỉ hồ sơ có vấn đề"; bấm một dòng cảnh báo
    thì mở màn sửa đúng em; sửa rồi lưu thì CSDL đổi và nhật ký có dòng `quan_ly` / `luu`;
  * lưu thiếu thì báo và không đổi gì; xoá một em, xoá tất cả (gõ sai chữ thì không xoá);
  * sau lần chạy xếp: "Đang khoá", màn sửa và Bước 3 ở kiosk chỉ đọc; mở khoá bằng hộp xác nhận và
    chữ MO; STB không đổi;
  * tiếng Anh: chữ của khối đổi theo, không còn chữ có dấu.
"""

import json
import os
import re
import sqlite3

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _wharton import bat_wharton, chen_bids, dong_bids, dung_clb, dung_hs  # noqa: E402
from test_wharton import sinh_bo  # noqa: E402
from test_wharton_pipeline import _nap_bo_vao_api, _trang_thai_stb  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402

DAU_VIET = re.compile(
    "[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]", re.I)


def _dung_du_lieu(api, bat=True):
    """HS1 hợp lệ; HS2 quỹ 2 mới 90 điểm; HS3 tick thi A mà vắng thi (hồ sơ hợp lệ)."""
    if bat:
        bat_wharton(api)
    dung_clb(api, A=(5, "thu_3"), B=(5, "thu_3"), C=(5, "thu_3"), D=(5, "thu_5"))
    for sid, ten in (("HS1", "Nguyễn Văn Bình"), ("HS2", "Trần Thị Lan"), ("HS3", "Lê Hoàng Nam")):
        assert api.create_student_if_missing(sid, ten)["ok"]
        assert api.submit_test_selection(sid, ["A"])["ok"]
    assert api.submit_preferences("HS1", ["A", "B", "C", "D"])["ok"]
    assert api.submit_preferences("HS2", ["A", "B", "C"])["ok"]
    assert api.submit_preferences("HS3", ["A", "B"])["ok"]
    assert api.submit_club_scores("A", [{"student_id": "HS1", "score": 8},
                                        {"student_id": "HS2", "score": 7}])["ok"]
    chen_bids(api, [("HS1", "A", 1, 100), ("HS1", "B", 2, 60), ("HS1", "C", 2, 40),
                    ("HS1", "D", 2, 100),
                    ("HS2", "A", 1, 100), ("HS2", "B", 2, 60), ("HS2", "C", 2, 30),
                    ("HS3", "A", 1, 100), ("HS3", "B", 2, 100)])


@pytest.fixture
def mo(tmp_path, api):
    """mo(bat=True, du_lieu=None) -> (page, api, loi). Mở thẻ Quản lý; đóng trình duyệt khi xong."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo(bat=True, du_lieu=None, api_dung=None):
        a = api_dung or api
        (du_lieu or _dung_du_lieu)(a, bat)
        url = browser_host.serve(a, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", viewport={"width": 1280, "height": 1400}, bypass_csp=True)
        page.set_default_timeout(8000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.locator('[data-tab="admin"]').click()
        page.wait_for_selector("#btnResetAll")
        if bat:
            page.wait_for_selector("#adminWhartonBlock:not([hidden]) #whQlBody tr")
        return page, a, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _hang(page, sid):
    return page.locator('#whQlBody tr[data-student-id="%s"]' % sid)


def _o(page, cid):
    return page.locator('#whQlSuaKhung input.wh-diem[data-clb="%s"]' % cid)


def _mo_man_sua(page, sid):
    page.locator('.wh-cb-dong[data-student-id="%s"]' % sid).click()
    page.wait_for_function(
        "(m) => !document.getElementById('whQlSua').hidden && "
        "document.getElementById('whQlSuaTen').textContent.includes(m)", arg=sid)
    page.wait_for_selector("#whQlSuaKhung .wh-khung")


def _nk(api):
    conn = sqlite3.connect(api.db_path)
    try:
        return [(r[0], r[1], r[2], json.loads(r[3]) if r[3] else None,
                 json.loads(r[4]) if r[4] else None)
                for r in conn.execute("SELECT nguon, hanh_dong, student_id, cu_json, moi_json "
                                      "FROM wharton_nhat_ky ORDER BY id")]
    finally:
        conn.close()


# ------------------------------------------------------------------ 1. tắt: thẻ Quản lý như cũ

def test_wharton_tat_khong_co_khoi_va_the_quan_ly_con_du_khoi_cu(mo):
    page, api, loi = mo(bat=False)
    page.wait_for_selector("#adminStudentTableBody tr")
    page.wait_for_timeout(300)
    assert page.locator("#adminWhartonBlock").is_hidden()
    for sel in ("#adminClubTableBody", "#adminStudentTableBody", "#btnResetStudents", "#btnResetAll",
                "#btnBulkAssign"):
        assert page.locator(sel).count() == 1, sel
    assert page.locator("#adminStudentTableBody tr").count() == 3
    assert not loi, loi


# ------------------------------------------------------------------ 2. bảng điểm

def test_bang_hien_dung_diem_tong_va_tim_khong_dau_va_loc(mo):
    page, api, loi = mo()
    assert page.locator("#whQlBody tr").count() == 3
    hs1 = _hang(page, "HS1")
    assert hs1.locator('.wh-ql-quy[data-buoi="thu_3"][data-quy="2"] .wh-ql-o[data-clb="B"]'
                       ).inner_text() == "CLB B: 60"
    assert hs1.locator('.wh-ql-quy[data-buoi="thu_3"][data-quy="2"] .wh-ql-tong').inner_text() == "Tổng 100"
    assert hs1.locator('.wh-ql-quy[data-buoi="thu_5"][data-quy="2"] .wh-ql-tong').inner_text() == "Tổng 100"
    hs2 = _hang(page, "HS2")
    assert hs2.locator('.wh-ql-quy[data-quy="2"] .wh-ql-tong').inner_text() == "Tổng 90"
    assert "Chưa hợp lệ" in hs2.inner_text()
    # tìm "binh" (không dấu) ra đúng em
    page.locator("#whQlTim").fill("binh")
    page.wait_for_function("() => document.querySelectorAll('#whQlBody tr').length === 1")
    assert page.locator("#whQlBody tr").first.get_attribute("data-student-id") == "HS1"
    page.locator("#whQlTim").fill("")
    page.wait_for_function("() => document.querySelectorAll('#whQlBody tr').length === 3")
    # "chỉ hồ sơ có vấn đề" chỉ còn em sai (HS2 sai, HS3 vắng thi)
    page.locator("#whLocChiLoi").check()
    page.wait_for_function("() => document.querySelectorAll('#whQlBody tr').length === 2")
    assert page.locator("#whQlBody tr").evaluate_all("rs => rs.map(r => r.dataset.studentId)") == [
        "HS2", "HS3"]
    page.locator("#whLocChiLoi").uncheck()
    page.locator("#whLocQuy").select_option("1")
    page.wait_for_function(
        "() => !document.querySelector('#whQlBody .wh-ql-quy[data-quy=\"2\"]')"
        " && document.querySelectorAll('#whQlBody tr').length === 3")
    assert not loi, loi


def test_o_tu_dien_hien_dau_tu_dien(mo):
    def du_lieu(api, bat):
        bat_wharton(api)
        dung_clb(api, A=5, B=5)
        dung_hs(api, "HS1", tick={"HS1": ["A"]})
        assert api.submit_preferences("HS1", ["A", "B"])["ok"]
    page, api, loi = mo(du_lieu=du_lieu)
    assert "tự điền" in _hang(page, "HS1").inner_text()
    assert dong_bids(api) == []
    assert not loi, loi


# ------------------------------------------------------------------ 3, 4. sửa từng em

def test_bam_dong_canh_bao_mo_man_sua_sua_cho_du_100_va_luu(mo):
    page, api, loi = mo()
    _mo_man_sua(page, "HS2")
    assert "Trần Thị Lan" in page.locator("#whQlSuaTen").inner_text()
    assert _o(page, "B").input_value() == "60" and _o(page, "C").input_value() == "30"
    _o(page, "C").fill("40")
    assert page.locator("#whQlChuaLuu").is_visible()
    page.locator("#btnWhLuu").click()
    page.wait_for_function(
        "() => document.getElementById('whQlSuaPhanHoi').textContent.includes('Đã lưu')")
    assert ("HS2", "C", 2, 40) in dong_bids(api)
    # em biến khỏi danh sách "chưa chia đủ"; vắng thi (HS3) vẫn còn
    page.wait_for_function(
        "() => !document.querySelector('.wh-cb-dong[data-student-id=\"HS2\"]')")
    assert page.locator('.wh-cb-dong[data-student-id="HS3"]').count() == 1
    nk = _nk(api)
    assert [(n[0], n[1], n[2]) for n in nk] == [("quan_ly", "luu", "HS2")]
    assert nk[0][3]["w2"] == {"B": 60, "C": 30} and nk[0][4]["w2"] == {"B": 60, "C": 40}
    # nhật ký của em hiện trong màn sửa
    page.wait_for_selector('#whQlNhatKy li[data-hanh-dong="luu"]')
    assert not loi, loi


def test_luu_khi_chua_du_100_bao_thieu_va_khong_doi_csdl(mo):
    page, api, loi = mo()
    _mo_man_sua(page, "HS2")
    truoc = dong_bids(api)
    _o(page, "C").fill("20")
    page.locator("#btnWhLuu").click()
    page.wait_for_function(
        "() => document.getElementById('whQlSuaPhanHoi').textContent.includes('Chưa dùng hết')")
    assert dong_bids(api) == truoc and _nk(api) == []
    assert not loi, loi


# ------------------------------------------------------------------ 5. xoá

def test_xoa_diem_mot_em_hai_buoc(mo):
    page, api, loi = mo()
    _mo_man_sua(page, "HS2")
    page.locator("#btnWhXoaMot").click()                      # bấm một lần: chưa xoá
    assert [d for d in dong_bids(api) if d[0] == "HS2"] != []
    page.locator("#btnWhXoaMot").click()                      # lần hai: xoá
    for _ in range(50):
        if not [d for d in dong_bids(api) if d[0] == "HS2"]:
            break
        page.wait_for_timeout(100)
    assert [d for d in dong_bids(api) if d[0] == "HS2"] == []
    assert [d for d in dong_bids(api) if d[0] == "HS1"] != []
    assert _nk(api)[-1][:3] == ("quan_ly", "xoa_mot_em", "HS2")
    assert not loi, loi


def test_xoa_tat_ca_go_sai_chu_khong_xoa_go_xoa_thi_xoa_het(mo):
    page, api, loi = mo()
    n_truoc = len(dong_bids(api))
    page.locator("#btnWhXoaTatCa").click()
    assert page.locator("#whXoaTatCaHop").is_visible()
    page.locator("#whXoaTatCaGo").fill("xoa")                 # sai chữ (thường)
    page.locator("#btnWhXoaTatCaXn").click()
    page.wait_for_function(
        "() => Array.from(document.querySelectorAll('.toast')).some(t => t.textContent.includes('XOA'))")
    assert len(dong_bids(api)) == n_truoc and _nk(api) == []
    page.locator("#whXoaTatCaGo").fill("XOA")
    page.locator("#btnWhXoaTatCaXn").click()
    for _ in range(50):
        if not dong_bids(api):
            break
        page.wait_for_timeout(100)
    assert dong_bids(api) == []
    nk = _nk(api)
    assert [(n[0], n[1]) for n in nk] == [("quan_ly", "xoa_tat_ca")]
    assert nk[0][3]["so_dong"] == n_truoc
    assert not loi, loi


# ------------------------------------------------------------------ 6, 7. khoá và mở khoá

def _chay_va_khoa(tmp_path, mo, api):
    """Dựng bộ mô phỏng hợp lệ bằng API, mở thẻ Quản lý, rồi chạy xếp: sang trạng thái khoá."""
    bo = sinh_bo(77, n_hs=12, n_clb=4)

    def du_lieu(a, bat):
        bat_wharton(a)
        _nap_bo_vao_api(a, bo)
    page, a, loi = mo(du_lieu=du_lieu)
    return page, a, loi, bo


def test_sau_khi_chay_xep_khoi_khoa_man_sua_va_buoc_3_kiosk_chi_doc_roi_mo_khoa(tmp_path, mo, api):
    page, api, loi, bo = _chay_va_khoa(tmp_path, mo, api)
    sid = bo.sids[0]
    assert page.locator("#whQlKhoa").inner_text().startswith("Đang mở")
    assert page.locator("#btnWhMoKhoa").is_hidden()
    assert api.run_pipeline(seed=3)["ok"]
    stb = _trang_thai_stb(api)
    page.locator('[data-tab="admin"]').click()              # mở lại thẻ: đọc trạng thái mới
    page.wait_for_function(
        "() => document.getElementById('whQlKhoa').textContent.startsWith('Đang khoá từ')")
    assert page.locator("#btnWhMoKhoa").is_visible()
    # màn sửa chỉ đọc
    page.locator('#whQlBody tr[data-student-id="%s"]' % sid).click()
    page.wait_for_selector("#whQlSua:not([hidden]) .wh-khung")
    assert page.locator("#whQlSuaKhoa").is_visible()
    assert page.locator("#btnWhLuu").is_disabled() and page.locator("#btnWhXoaMot").is_disabled()
    assert all(page.locator("#whQlSuaKhung input.wh-diem").nth(i).is_disabled()
               for i in range(page.locator("#whQlSuaKhung input.wh-diem").count()))
    # API ghi bị chặn
    assert [e["code"] for e in api.submit_wharton(sid, {}, {})["errors"]] == ["wharton_da_khoa"]
    # Bước 3 ở kiosk cũng chỉ đọc
    page.locator('[data-tab="fallback"]').click()
    page.wait_for_selector("#studentSearchResults .hs-card")
    page.locator('#studentSearchResults .hs-card[data-student-id="%s"]' % sid).click()
    page.wait_for_selector("#fbWhartonStep:not([hidden]) .wh-khung")
    assert page.locator("#fbWhartonKhoa").is_visible()
    assert page.locator("#btnSubmitWharton").is_disabled()
    assert all(page.locator("#fbWhartonBody input.wh-diem").nth(i).is_disabled()
               for i in range(page.locator("#fbWhartonBody input.wh-diem").count()))
    # mở khoá: nút -> hộp xác nhận -> gõ sai chữ không mở -> gõ MO mới mở
    page.locator('[data-tab="admin"]').click()
    page.wait_for_selector("#btnWhMoKhoa:not([hidden])")
    page.locator("#btnWhMoKhoa").click()
    assert page.locator("#whMoKhoaHop").is_visible()
    page.locator("#whMoKhoaGo").fill("mo")
    page.locator("#btnWhMoKhoaXn").click()
    page.wait_for_timeout(400)
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT is_locked FROM wharton_lock").fetchone()[0] == 1
    page.locator("#whMoKhoaGo").fill("MO")
    page.locator("#btnWhMoKhoaXn").click()
    page.wait_for_function(
        "() => document.getElementById('whQlKhoa').textContent.startsWith('Đang mở')")
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT is_locked FROM wharton_lock").fetchone()[0] == 0
    assert _trang_thai_stb(api) == stb                       # STB không đổi
    page.wait_for_function(
        "() => !document.getElementById('btnWhLuu').disabled && "
        "document.querySelector('#whQlSuaKhung input.wh-diem:not(:disabled)') !== null")
    assert page.locator("#whQlSuaKhoa").is_hidden()
    assert ("quan_ly", "mo_khoa", None, None, None) in _nk(api)
    assert not loi, loi


# ------------------------------------------------------------------ 8. tiếng Anh

def test_tieng_anh_chu_cua_khoi_doi_theo_va_khong_con_chu_co_dau(mo):
    page, api, loi = mo()
    _mo_man_sua(page, "HS2")
    assert "Điểm quyết tâm" in page.locator("#adminWhartonBlock h2").inner_text()
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("document.documentElement.lang === 'en'")
    page.wait_for_function(
        "() => document.querySelector('#adminWhartonBlock h2').textContent === 'Preference points'")
    page.wait_for_function(
        "() => document.querySelector('#whQlBody tr[data-student-id=\"HS2\"]').textContent"
        ".includes('Not valid')")
    # chỉ xét chữ của khối; tên em (có dấu, do người dùng nhập) nằm ngoài phép kiểm
    van_ban = page.evaluate("""() => {
        const goc = document.getElementById('adminWhartonBlock').cloneNode(true);
        goc.querySelectorAll('td:nth-child(2), #whCanhBao button, #whQlSuaTen').forEach(n => n.remove());
        goc.querySelectorAll('input, select').forEach(n => n.remove());
        return goc.innerText;
    }""")
    assert "Total" in van_ban and "Fund" in van_ban
    assert not DAU_VIET.search(van_ban), van_ban
    assert not loi, loi


def test_man_sua_chi_doc_nhat_ky_cua_chinh_em_do(mo):
    """Màn sửa của một em chỉ đọc nhật ký của chính em đó."""
    page, api, loi = mo()
    assert api.admin_save_wharton("HS1", {"A": 100}, {"B": 10, "C": 90, "D": 100})["ok"]
    _mo_man_sua(page, "HS2")
    page.wait_for_timeout(300)
    assert page.locator("#whQlNhatKy li").count() == 0
    assert not loi, loi
