"""Giao diện điểm chuẩn (A13.4), Playwright + Chromium qua `browser_host`. Dữ liệu MÔ PHỎNG.

  * (a) cột phân bố, (b) dải chấm, (c) bảng tổng quan: số cột / chấm / thanh và vị trí vạch chuẩn
    khớp `get_diem_chuan` và `get_diem_chuan_clb`; mỗi biểu đồ có tiêu đề, chú giải, bảng chữ;
  * vẽ được khi chặn MỌI yêu cầu ra ngoài máy (ngoại tuyến), đổi ngôn ngữ thì nhãn đổi theo;
  * tab Kết quả: mục "Điểm chuẩn" đóng sẵn, bấm mới mở, rời thẻ rồi vào lại thì đóng;
  * tab Quản lý: khối chi tiết đúng số liệu của API;
  * tắt tính năng: cả hai phần không hiện; kiosk không có chữ hay số điểm chuẩn nào.
"""

import os
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _wharton import bat_wharton, chen_bids, dung_clb  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402

DAU_VIET = re.compile(
    "[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]", re.I)


def _dung_du_lieu(api, bat=True, chay=True):
    """Tám em xin CLB A (4 chỗ, không thi) rồi B (10 chỗ); điểm quyết tâm cho A: 95, 85, …, 25."""
    if bat:
        bat_wharton(api)
    dung_clb(api, A=4, B=10, C=3)
    bids = []
    for i in range(8):
        sid = "HS%d" % (i + 1)
        assert api.create_student_if_missing(sid, "Em số %d" % (i + 1))["ok"]
        assert api.submit_preferences(sid, ["A", "B"])["ok"]
        p = 95 - 10 * i
        bids += [(sid, "A", 2, p), (sid, "B", 2, 100 - p)]
    chen_bids(api, bids) if bat else None
    if chay:
        assert api.run_pipeline(seed=3)["ok"]


@pytest.fixture
def mo(tmp_path, api):
    """mo(bat=True, chay=True, ngoai_tuyen=False) -> (page, api, loi, yeu_cau)."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo(bat=True, chay=True, chan_ngoai=False, tab="admin", rong=1280):
        _dung_du_lieu(api, bat, chay)
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", viewport={"width": rong, "height": 1400}, bypass_csp=True)
        page.set_default_timeout(8000)
        loi, yeu_cau = [], []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.on("request", lambda r: yeu_cau.append(r.url))
        if chan_ngoai:
            page.route(re.compile(r"^(?!http://127\.0\.0\.1)"), lambda r: r.abort())
        page.goto(url)
        page.wait_for_selector("#dropZone")
        if tab:
            page.locator('[data-tab="%s"]' % tab).click()
        return page, api, loi, yeu_cau

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _cho_quan_ly(page):
    page.wait_for_selector("#adminDiemChuanBlock:not([hidden]) #dcChiTiet:not([hidden]) svg[data-bieu-do=cham]")


# ------------------------------------------------------------------ (a), (b) khớp dữ liệu

def test_cot_va_cham_khop_du_lieu_va_vach_chuan(mo):
    page, api, loi, _ = mo()
    _cho_quan_ly(page)
    kq = api.get_diem_chuan_clb("A")["data"]
    em, chuan = kq["em"], kq["chuan"]["tang2"]["thuong"]["diem_quyet_tam"]
    assert len(em) == 8 and chuan == 65                # 4 em được nhận: 95, 85, 75, 65
    # (a) mười nhóm điểm; tổng được nhận / không được nhận khớp
    nhom = page.locator('svg[data-bieu-do=cot] g[data-tu]')
    assert nhom.count() == 10
    duoc = sum(int(x) for x in nhom.evaluate_all("g => g.map(e => e.dataset.duoc)"))
    khong = sum(int(x) for x in nhom.evaluate_all("g => g.map(e => e.dataset.khong)"))
    assert (duoc, khong) == (4, 4)
    # vạch chuẩn ở đúng vị trí trên thang 0..100
    vach = page.locator("svg[data-bieu-do=cot] line.dc-chuan-vach")
    assert vach.count() == 1 and vach.get_attribute("data-diem") == "65"
    x1 = float(vach.get_attribute("x1"))
    assert x1 == pytest.approx(44 + 0.65 * (560 - 44 - 12), abs=0.01)
    assert "Chuẩn 65" in page.locator("svg[data-bieu-do=cot] text.dc-chuan-nhan").text_content()
    # (b) mỗi em một chấm; đặc = được nhận, rỗng = không được nhận
    cham = page.locator("svg[data-bieu-do=cham] circle.dc-cham")
    assert cham.count() == 8
    assert page.locator("svg[data-bieu-do=cham] circle.dc-cham-duoc").count() == 4
    assert page.locator("svg[data-bieu-do=cham] circle.dc-cham-khong").count() == 4
    c_hs1 = page.locator('svg[data-bieu-do=cham] circle.dc-cham[data-student-id="HS1"]')
    assert c_hs1.get_attribute("data-diem") == "95"
    assert float(c_hs1.get_attribute("cx")) == pytest.approx(20 + 0.95 * (560 - 20 - 20), abs=0.01)
    assert not loi, loi


def test_tooltip_cham_hien_ma_hoc_sinh_va_diem(mo):
    page, api, loi, _ = mo()
    _cho_quan_ly(page)
    page.locator('svg[data-bieu-do=cham] circle.dc-cham-hit[data-student-id="HS3"]').focus()
    page.wait_for_selector("#bieuDoTooltip:not([hidden])")
    chu = page.locator("#bieuDoTooltip").inner_text()
    assert "HS3" in chu and "75" in chu and "Được nhận" in chu
    assert not loi, loi


def test_moi_bieu_do_co_tieu_de_chu_giai_va_bang_chu(mo):
    page, api, loi, _ = mo()
    _cho_quan_ly(page)
    for ten in ("cot", "cham"):
        svg = page.locator("svg[data-bieu-do=%s]" % ten)
        assert svg.get_attribute("role") == "img"
        assert svg.locator("title").text_content().strip()
    for fig in ("#dcCot", "#dcCham"):
        assert page.locator(fig + " .dc-chu-giai li").count() >= 3
        assert page.locator(fig + " table.dc-an-chu tbody tr").count() >= 2
        assert page.locator(fig + " figcaption").inner_text().strip()
    # (c) tổng quan: mỗi CLB một dòng, có thanh và tiêu đề; A đông hơn chỗ -> chấm nóng
    hang = page.locator("#dcQlTongQuan tbody tr")
    assert hang.count() == 3
    a = page.locator('#dcQlTongQuan tr[data-club-id="A"]')
    assert a.locator("svg.dc-thanh title").text_content().strip()
    assert a.locator(".dc-nong").count() == 1
    assert page.locator('#dcQlTongQuan tr[data-club-id="C"] .dc-nong').count() == 0
    assert page.locator("#dcQlTongQuan .dc-chu-giai li").count() == 1
    thanh = a.locator("path.dc-thanh-do")
    assert thanh.get_attribute("data-diem") == "65"
    assert not loi, loi


def test_ve_duoc_khi_chan_moi_yeu_cau_ra_ngoai_may(mo):
    page, api, loi, yeu_cau = mo(chan_ngoai=True)
    _cho_quan_ly(page)
    assert page.locator("svg[data-bieu-do=cot] g[data-tu]").count() == 10
    assert all(u.startswith("http://127.0.0.1") or u.startswith(("data:", "blob:")) for u in yeu_cau), \
        [u for u in yeu_cau if not u.startswith("http://127.0.0.1")]
    assert not loi, loi


def test_doi_ngon_ngu_thi_nhan_doi_theo(mo):
    page, api, loi, _ = mo()
    _cho_quan_ly(page)
    assert "Chuẩn 65" in page.locator("svg[data-bieu-do=cot] text.dc-chuan-nhan").text_content()
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function(
        "() => document.querySelector('svg[data-bieu-do=cot] text.dc-chuan-nhan')"
        " && document.querySelector('svg[data-bieu-do=cot] text.dc-chuan-nhan').textContent.includes('Cut-off 65')")
    assert "Accepted" in page.locator("#dcCot .dc-chu-giai").inner_text()
    assert "Not accepted" in page.locator("#dcCham .dc-chu-giai").inner_text()
    assert page.locator("#adminDiemChuanBlock h2").inner_text() == "Cut-off points"
    chu = page.locator("#adminDiemChuanBlock").inner_text()
    assert not DAU_VIET.search(chu.replace("Em số", "")), chu
    assert "Wharton" not in chu
    assert not loi, loi


# ------------------------------------------------------------------ bảng và khối Quản lý

def test_khoi_quan_ly_dung_so_lieu_cua_api(mo):
    page, api, loi, _ = mo()
    _cho_quan_ly(page)
    rows = {r["club_id"]: r for r in api.get_diem_chuan()["data"]["rows"]}
    a = rows["A"]
    bang = page.locator("#dcBang table")
    assert "Điểm chuẩn của" in bang.locator("caption").inner_text()
    # tầng 2, suất thường = 65
    o = bang.locator('tbody tr').nth(0).locator("td").nth(0)
    assert o.inner_text().strip() == "65"
    assert bang.locator("tbody tr").nth(0).locator("td").nth(1).inner_text().strip() == "—"
    assert page.locator("#dcBang p").inner_text().strip() == "Đã nhận %d trên %d chỗ, có %d đơn." % (
        a["so_nhan"], a["suc_chua"], a["so_don"])
    # chọn CLB khác thì vẽ lại: C không ai xin
    page.locator("#dcChonClb").select_option("C")
    page.wait_for_function("() => document.querySelector('#dcCot').textContent.includes('Chưa có')")
    assert page.locator("svg[data-bieu-do=cot]").count() == 0
    assert not loi, loi


def test_khoi_quan_ly_canh_bao_cu_khi_du_lieu_doi(mo):
    page, api, loi, _ = mo()
    _cho_quan_ly(page)
    assert page.locator("#dcQlCu").is_hidden()
    assert api.create_or_update_club("C", "CLB C", 9, 0, "", "")["ok"]
    page.locator('[data-tab="pipeline"]').click()
    page.locator('[data-tab="admin"]').click()
    page.wait_for_selector("#dcQlCu:not([hidden])")
    assert not loi, loi


def test_chua_chay_khong_co_bieu_do_va_nhac_chay(mo):
    page, api, loi, _ = mo(chay=False)
    page.wait_for_selector("#adminDiemChuanBlock:not([hidden]) #dcQlRong:not([hidden])")
    assert page.locator("#dcChiTiet").is_hidden() and page.locator("#dcChonHop").is_hidden()
    page.locator('[data-tab="results"]').click()
    assert page.locator("#dcKqPanel").is_hidden()
    assert not loi, loi


# ------------------------------------------------------------------ tab Kết quả: đóng sẵn, không nhớ

def test_ket_qua_muc_dong_san_mo_duoc_vao_lai_thi_dong(mo):
    page, api, loi, _ = mo(tab="results")
    page.wait_for_selector("#dcKqPanel:not([hidden])")
    assert page.locator("#dcKqBody").is_hidden()
    assert page.locator("#btnDcKqMo").get_attribute("aria-expanded") == "false"
    assert page.locator("#btnDcKqMo").inner_text() == "Xem điểm chuẩn"
    page.locator("#btnDcKqMo").click()
    page.wait_for_selector("#dcKqBody:not([hidden]) #dcKqTongQuan tbody tr")
    assert page.locator("#dcKqTongQuan tbody tr").count() == 3
    assert page.locator("#btnDcKqMo").inner_text() == "Ẩn điểm chuẩn"
    # đổi ngôn ngữ không làm đóng
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("() => document.getElementById('btnDcKqMo').textContent === 'Hide cut-off points'")
    assert page.locator("#dcKqBody").is_visible()
    page.evaluate("window.I18N.setLang('vi')")
    # rời thẻ rồi vào lại: đóng
    page.locator('[data-tab="admin"]').click()
    page.locator('[data-tab="results"]').click()
    page.wait_for_selector("#dcKqPanel:not([hidden])")
    assert page.locator("#dcKqBody").is_hidden()
    assert page.locator("#btnDcKqMo").inner_text() == "Xem điểm chuẩn"
    # không nhớ qua lần tải trang
    assert not page.evaluate("() => Object.keys(window.localStorage).some(k => /chuan|dc_/i.test(k))")
    assert not loi, loi


# ------------------------------------------------------------------ tắt tính năng, kiosk

def test_tat_tinh_nang_hai_phan_khong_hien(mo):
    page, api, loi, _ = mo(bat=False, chay=True, tab="admin")
    page.wait_for_selector("#btnResetAll")
    assert page.locator("#adminDiemChuanBlock").is_hidden()
    page.locator('[data-tab="results"]').click()
    page.wait_for_selector("#fillPanel")
    assert page.locator("#dcKqPanel").is_hidden()
    assert not loi, loi


def test_kiosk_khong_co_diem_chuan(mo):
    page, api, loi, _ = mo(tab="fallback")
    page.wait_for_selector("#studentSearchResults .hs-card")
    page.locator('#studentSearchResults .hs-card[data-student-id="HS1"]').click()
    page.wait_for_selector("#fbWhartonStep:not([hidden])")
    chu = page.locator("#view-fallback").inner_text().lower()
    assert "chuẩn" not in chu and "cut-off" not in chu
    assert page.locator("#view-fallback .dc-svg, #view-fallback .dc-tq").count() == 0
    assert page.locator("#view-fallback #adminDiemChuanBlock, #view-fallback #dcKqPanel").count() == 0
    assert not loi, loi
