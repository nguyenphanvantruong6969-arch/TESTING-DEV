"""A13.10, thiết kế lại màn Quản lý, Điểm chuẩn (Playwright + Chromium). Dữ liệu MÔ PHỎNG.

  * bảng tổng: hai cột điểm chuẩn riêng, mỗi ô có thanh; không còn dòng chữ nhỏ dưới tên CLB;
  * "Đơn / chỗ": thanh tỉ lệ nhỏ kèm số, màu theo mức cạnh tranh, không còn chấm đỏ;
  * chi tiết một CLB: ĐÚNG MỘT biểu đồ SVG, vạch chuẩn ghi số, được / không được nhận phân biệt;
  * `prefers-reduced-motion` tắt hiệu ứng; `prefers-color-scheme: dark` đổi màu khối;
  * nhãn mới có mặt ở cả VI và EN.
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


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo(**tuy):
        bat_wharton(api)
        dung_clb(api, A=4, B=10, C=3)
        bids = []
        for i in range(8):
            sid = "HS%d" % (i + 1)
            assert api.create_student_if_missing(sid, "Em số %d" % (i + 1))["ok"]
            assert api.submit_preferences(sid, ["A", "B"])["ok"]
            p = 95 - 10 * i
            bids += [(sid, "A", 2, p), (sid, "B", 2, 100 - p)]
        chen_bids(api, bids)
        assert api.run_pipeline(seed=3)["ok"]
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(locale="vi-VN", viewport={"width": 1280, "height": 1400}, bypass_csp=True,
                           **tuy)
        page.set_default_timeout(8000)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.locator('[data-tab="admin"]').click()
        page.locator('#qlTabs [data-ql-tab="dc"]').click()
        page.wait_for_selector("#adminDiemChuanBlock:not([hidden]) #dcChiTiet:not([hidden]) svg[data-bieu-do]")
        return page, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


# ------------------------------------------------------------------ bảng tổng

def test_bang_co_hai_cot_diem_chuan_rieng_moi_o_co_thanh(mo):
    page, loi = mo()
    th = page.locator("#dcQlTongQuan thead th")
    chu = [x.strip() for x in th.all_inner_texts()]
    assert [c.lower() for c in chu] == ["clb", "xét điểm thi", "xét điểm quyết tâm", "đơn và chỗ"], chu
    assert page.locator('#dcQlTongQuan th[data-tang="1"]').count() == 1
    assert page.locator('#dcQlTongQuan th[data-tang="2"]').count() == 1
    a = page.locator('#dcQlTongQuan tr[data-club-id="A"]')
    # A không thi: ô điểm thi là "—", ô điểm quyết tâm có thanh dài đúng 65 trên thang 100
    assert a.locator('td[data-tang="1"]').inner_text().strip() == "—"
    thanh = a.locator('td[data-tang="2"] svg.dc-thanh')
    assert thanh.count() == 1 and thanh.get_attribute("data-tang") == "2"
    assert float(thanh.locator("path.dc-thanh-do, rect.dc-thanh-do").get_attribute("data-diem")) == 65
    assert a.locator('td[data-tang="2"] .dc-gtri').inner_text().strip() == "65"
    assert thanh.locator("title").text_content().strip()
    assert not loi, loi


def test_bang_khong_con_dong_chu_nho_duoi_ten_clb(mo):
    page, loi = mo()
    assert page.locator("#dcQlTongQuan .dc-phu").count() == 0
    for ten in page.locator("#dcQlTongQuan tbody tr td:first-child").all_inner_texts():
        assert "\n" not in ten.strip(), ten
    assert not loi, loi


def test_don_va_cho_co_nhan_muc_bang_chu_so_ro_don_vi_va_thanh_chung_thang(mo):
    page, loi = mo()
    assert page.locator("#dcQlTongQuan .dc-nong").count() == 0
    th = page.locator("#dcQlTongQuan thead th").nth(3).inner_text().strip().lower()
    assert th == "đơn và chỗ", th
    # A: 8 đơn cho 4 chỗ (gấp 2, "Đông"); B: 8 đơn cho 10 chỗ ("Đủ chỗ"); C: 0 đơn cho 3 chỗ
    mong = {"A": ("Đông", "8 đơn · 4 chỗ", "vua", (4, 4, 0)),
            "B": ("Đủ chỗ", "8 đơn · 10 chỗ", "thap", (8, 0, 2)),
            "C": ("Đủ chỗ", "0 đơn · 3 chỗ", "thap", (0, 0, 3))}
    mau = {}
    for cid, (nhan, chu, muc, (trong, vuot, con)) in mong.items():
        o = page.locator('#dcQlTongQuan tr[data-club-id="%s"] td.dc-don' % cid)
        assert o.locator(".dc-chip").inner_text().strip() == nhan
        assert o.locator(".dc-chip").get_attribute("data-muc") == muc
        assert o.locator(".dc-don-so").inner_text().strip() == chu
        svg = o.locator("svg.dc-ti-le")
        assert svg.get_attribute("data-muc") == muc and svg.locator("title").text_content().strip()
        assert tuple(int(svg.get_attribute("data-" + k)) for k in ("trong", "vuot", "con")) == (trong, vuot, con)
        mau[cid] = o.locator(".dc-chip").evaluate("e => getComputedStyle(e).backgroundColor")
    assert mau["A"] != mau["B"] and mau["B"] == mau["C"], mau          # mức khác nhau, màu khác nhau
    # cùng một thang: đơn dài gấp đôi thì thanh dài gấp đôi (A: 8 đơn, B: 8 đơn, cùng tổng "trong + vuot")
    dai = page.evaluate("""() => ['A','B'].map(c => [...document.querySelectorAll(
        '#dcQlTongQuan tr[data-club-id="' + c + '"] svg.dc-ti-le rect.dc-ti-le-trong, '
        + '#dcQlTongQuan tr[data-club-id="' + c + '"] svg.dc-ti-le rect.dc-ti-le-vuot')]
        .reduce((t, r) => t + (+r.getAttribute('width')), 0))""")
    assert dai[0] == pytest.approx(dai[1], abs=0.5), dai
    # chú giải: ba phần của thanh và lời giải thích ba mức
    assert page.locator("#dcQlTongQuan .dc-chu-giai li").count() == 3
    chu = page.locator("#dcQlTongQuan").inner_text()
    assert "Đủ chỗ:" in chu and "Rất đông:" in chu
    assert not loi, loi


# ------------------------------------------------------------------ biểu đồ chi tiết: một SVG

def test_chi_tiet_la_dung_mot_svg_beeswarm_khop_du_lieu(mo):
    page, loi = mo()
    assert page.locator("#dcChiTiet svg").count() == 1
    assert page.locator("#dcChiTiet svg[data-bieu-do=chi-tiet]").count() == 1
    assert page.locator("#dcChiTiet figure").count() == 1
    cham = page.locator("svg[data-bieu-do=chi-tiet] circle.dc-cham")
    assert cham.count() == 8
    assert page.locator("svg[data-bieu-do=chi-tiet] circle.dc-cham-duoc").count() == 4
    assert page.locator("svg[data-bieu-do=chi-tiet] circle.dc-cham-khong").count() == 4
    c1 = page.locator('svg[data-bieu-do=chi-tiet] circle.dc-cham[data-student-id="HS1"]')
    assert c1.get_attribute("data-diem") == "95"
    assert float(c1.get_attribute("cx")) == pytest.approx(20 + 0.95 * (560 - 20 - 20), abs=0.01)
    vach = page.locator("svg[data-bieu-do=chi-tiet] line.dc-chuan-vach")
    assert vach.count() == 1 and vach.get_attribute("data-diem") == "65"
    assert float(vach.get_attribute("x1")) == pytest.approx(20 + 0.65 * (560 - 20 - 20), abs=0.01)
    assert "Chuẩn 65" in page.locator("svg[data-bieu-do=chi-tiet] text.dc-chuan-nhan").text_content()
    # không có hai chấm nào chồng lên nhau
    toa = page.locator("svg[data-bieu-do=chi-tiet] circle.dc-cham").evaluate_all(
        "c => c.map(e => [+e.getAttribute('cx'), +e.getAttribute('cy'), +e.getAttribute('r')])")
    for i, p in enumerate(toa):
        for q in toa[i + 1:]:
            assert ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5 >= p[2] + q[2] - 0.01, (p, q)
    assert not loi, loi


def test_chi_tiet_chu_giai_gon_tieu_de_bang_chu_va_tooltip(mo):
    page, loi = mo()
    fig = page.locator("#dcChiTiet figure")
    assert fig.locator("figcaption").inner_text().strip()
    assert fig.locator("svg").get_attribute("role") == "img"
    assert fig.locator("svg title").first.text_content().strip()
    assert fig.locator(".dc-chu-giai li").count() == 3          # được, không được, vạch chuẩn
    assert fig.locator("table.dc-an-chu tbody tr").count() == 8
    fig.locator('circle.dc-cham-hit[data-student-id="HS3"]').focus()
    page.wait_for_selector("#bieuDoTooltip:not([hidden])")
    chu = page.locator("#bieuDoTooltip").inner_text()
    assert "HS3" in chu and "75" in chu and "Được nhận" in chu
    assert not loi, loi


def test_chon_clb_khong_ai_xin_thi_khong_con_svg(mo):
    page, loi = mo()
    page.locator("#dcChonClb").select_option("C")
    page.wait_for_function("() => document.querySelector('#dcChiTiet figure').textContent.includes('Chưa có')")
    assert page.locator("#dcChiTiet svg").count() == 0
    assert not loi, loi


# ------------------------------------------------------------------ chuyển động, sáng / tối, ngôn ngữ

def test_reduced_motion_tat_hieu_ung_con_binh_thuong_thi_co(mo):
    page, loi = mo()
    lay = "() => getComputedStyle(document.querySelector('svg[data-bieu-do=chi-tiet] circle.dc-cham')).animationName"
    page.emulate_media(reduced_motion="reduce")
    assert page.evaluate(lay) == "none"
    page.emulate_media(reduced_motion="no-preference")
    assert page.evaluate(lay) != "none"
    assert not loi, loi


def test_che_do_toi_doi_mau_khoi_va_giu_chu_doc_duoc(mo):
    page, loi = mo()

    def sang(c):
        r, g, b = [int(x) for x in re.findall(r"\d+", c)[:3]]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    lay = """() => { const s = getComputedStyle(document.querySelector('#adminDiemChuanBlock'));
        return [s.backgroundColor, s.color]; }"""
    page.emulate_media(color_scheme="light")
    nen_sang, _ = page.evaluate(lay)
    assert sang(nen_sang) > 200, nen_sang
    page.emulate_media(color_scheme="dark")
    nen_toi, chu_toi = page.evaluate(lay)
    assert sang(nen_toi) < 90 and sang(chu_toi) > 160, (nen_toi, chu_toi)
    # chấm "được nhận" và vạch chuẩn vẫn tương phản với nền tối
    mau = page.evaluate("""() => [getComputedStyle(document.querySelector('svg[data-bieu-do=chi-tiet] circle.dc-cham-duoc')).fill,
        getComputedStyle(document.querySelector('svg[data-bieu-do=chi-tiet] line.dc-chuan-vach')).stroke]""")
    assert all(sang(m) > 110 for m in mau), mau
    assert not loi, loi


def test_ngon_ngu_en_nhan_moi_o_bang_va_bieu_do(mo):
    page, loi = mo()
    page.evaluate("window.I18N.setLang('en')")
    page.wait_for_function("() => document.querySelector('#dcQlTongQuan th[data-tang=\"1\"]').textContent.trim() === 'Exam-based'")
    assert page.locator('#dcQlTongQuan th[data-tang="2"]').text_content().strip() == "Commitment points"
    page.wait_for_function("() => document.querySelector('svg[data-bieu-do=chi-tiet] text.dc-chuan-nhan').textContent.includes('Cut-off 65')")
    chu = page.locator("#adminDiemChuanBlock").inner_text()
    assert not re.search(r"[Tt]ầng|\b[Tt]ier\b|Wharton", chu), chu
    assert not loi, loi
