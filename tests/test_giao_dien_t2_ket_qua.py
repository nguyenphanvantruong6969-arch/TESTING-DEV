# ruff: noqa: F811
"""T2 — thẻ 02 "Kết quả" hai tầng (Playwright + Chromium, qua `browser_host`; dữ liệu MÔ PHỎNG).

Tầng 1: Theo lớp | Theo CLB | Theo mã học sinh. Tầng 2 (cách sắp): Theo ngày trong tuần | Theo mã học
sinh | Theo lớp (mục cuối CHỈ khi tầng 1 = Theo mã học sinh). Nhớ lựa chọn theo máy. Không điểm,
không số bốc thăm. Tái dùng fixture `mo` của test_giao_dien_a14_lop."""

import json
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_giao_dien_a14_lop import api, mo  # noqa: E402,F401

KHOA = "rbda_ket_qua_xem_v1"


def _mo_ket_qua(page, tang1=None):
    page.locator('.nav-item[data-tab="results"]').click()
    page.wait_for_selector("#view-results.is-active")
    if tang1:
        page.locator('#kqTang1 [data-kq="%s"]' % tang1).click()


def _sx(page, kieu):
    page.locator('#kqTang2 [data-sx="%s"]' % kieu).click()


def _ma_cot2(page):
    """Cột 'Mã học sinh' (cột 2) của bảng, theo thứ tự đang hiện."""
    return page.evaluate("() => Array.from(document.querySelectorAll('#kqThan tr')).map(r => r.children[1].textContent)")


def _thu_tu(page, mong):
    """Chờ bảng vẽ lại xong theo đúng thứ tự `mong` (việc vẽ lại là bất đồng bộ)."""
    page.wait_for_function(
        "(m) => JSON.stringify(Array.from(document.querySelectorAll('#kqThan tr'))"
        ".map(r => r.children[1].textContent)) === JSON.stringify(m)", arg=mong)
    assert _ma_cot2(page) == mong


def _bang_san_sang(page, so_hang):
    page.wait_for_function("(n) => !document.getElementById('kqBang').hidden && "
                           "document.querySelectorAll('#kqThan tr').length === n", arg=so_hang)


def test_tang1_ba_nut_mot_cho_bam_doi_khong_tai_lai_trang(mo):
    page, api, loi = mo({"HS1": "10A1", "HS2": "10A1"}, chay=True)
    page.evaluate("() => { window.__chua_tai_lai = 1; }")
    _mo_ket_qua(page)
    nhan = [x.strip() for x in page.locator("#kqTang1 .kq-seg-nut").all_inner_texts()]
    assert nhan == ["Theo lớp", "Theo CLB", "Theo mã học sinh"]
    # HIỆN THẬT trên màn hình (offsetParent), không chỉ thuộc tính hidden: CSS có thể đè hidden
    hien = lambda: page.evaluate("""() => ['kqChonLopHang','kqChonClbHang','kqTimHang']
        .map(i => document.getElementById(i).offsetParent !== null)""")  # noqa: E731
    page.wait_for_function("() => document.querySelector('#kqTang1 .is-on')")
    assert page.locator("#kqTang1 .is-on").get_attribute("data-kq") == "lop" and hien() == [True, False, False]
    for tang1, mong in (("clb", [False, True, False]), ("ma", [False, False, True]), ("lop", [True, False, False])):
        page.locator('#kqTang1 [data-kq="%s"]' % tang1).click()      # đúng MỘT cú bấm
        assert page.locator("#kqTang1 .is-on").get_attribute("data-kq") == tang1
        assert page.locator('#kqTang1 [data-kq="%s"]' % tang1).get_attribute("aria-pressed") == "true"
        assert hien() == mong
    assert page.evaluate("() => window.__chua_tai_lai") == 1             # trang không bị nạp lại
    assert not loi, loi


def test_tang2_theo_lop_chi_co_khi_tang1_la_theo_ma(mo):
    page, api, loi = mo({"HS1": "10A1"}, chay=True)
    _mo_ket_qua(page)
    ds = lambda: [x.strip() for x in page.evaluate("""() => Array.from(document.querySelectorAll('#kqTang2 .kq-seg-nut'))
        .filter(n => !n.hidden && n.offsetParent !== null).map(n => n.textContent)""")]  # noqa: E731
    for tang1 in ("lop", "clb"):
        page.locator('#kqTang1 [data-kq="%s"]' % tang1).click()
        assert ds() == ["Theo ngày trong tuần", "Theo mã học sinh"], tang1
    page.locator('#kqTang1 [data-kq="ma"]').click()
    assert ds() == ["Theo ngày trong tuần", "Theo mã học sinh", "Theo lớp"]
    assert not loi, loi


def test_sap_theo_ma_la_sap_tu_nhien_va_theo_lop_la_tu_nhien_trong_cuoi(mo):
    # HS1 10A10, HS2/HS3 10A2, HS10 10A1, HS9 chưa có lớp; năm em cùng vào CLB A (5 chỗ)
    page, api, loi = mo({"HS1": "10A10", "HS2": "10A2", "HS3": "10A2", "HS10": "10A1"},
                        chay=True, them=("HS9", "HS10"))
    _mo_ket_qua(page, "ma")
    _bang_san_sang(page, 5)
    _sx(page, "ma")
    _thu_tu(page, ["HS1", "HS2", "HS3", "HS9", "HS10"])        # tự nhiên: HS9 trước HS10
    _sx(page, "lop")
    _thu_tu(page, ["HS10", "HS2", "HS3", "HS1", "HS9"])        # 10A1 < 10A2 < 10A10, trống cuối
    page.locator('#kqTang1 [data-kq="clb"]').click()                    # sang Theo CLB: "lop" lùi về ngày
    page.wait_for_function("() => document.querySelector('#kqTang2 .is-on')")
    assert page.locator("#kqTang2 .is-on").get_attribute("data-sx") == "ngay"
    assert not loi, loi


def test_sap_theo_ngay_trong_tuan_dung_thu_tu_buoi_dau_tien_co_clb(mo):
    page, api, loi = mo({"HS1": "10A1", "HS2": "10A1", "HS3": "10A1"}, chay=True, nhieu_buoi=True)
    d = api.get_thoi_khoa_bieu()["data"]

    def khoa(em):
        vi_tri = [i for i, b in enumerate(d["ds_buoi"]) if (em["theo_buoi"].get(b) or {}).get("club_id")]
        return (vi_tri[0] if vi_tri else 99, em["student_id"])
    mong_ngay = [e["student_id"] for e in sorted(d["hoc_sinh"], key=khoa)]
    _mo_ket_qua(page, "ma")
    _bang_san_sang(page, 3)
    _sx(page, "ngay")
    _thu_tu(page, mong_ngay)
    _sx(page, "ma")
    _thu_tu(page, ["HS1", "HS2", "HS3"])
    assert not loi, loi


def test_nho_hai_tang_theo_may_va_mo_lai_van_con(mo):
    page, api, loi = mo({"HS1": "10A1"}, chay=True)
    url = page.url
    _mo_ket_qua(page, "ma")
    _sx(page, "lop")
    luu = json.loads(page.evaluate("() => localStorage.getItem('%s')" % KHOA))
    assert (luu["tang1"], luu["tang2"]) == ("ma", "lop")
    trang2 = page.context.new_page()           # cùng kho lưu trữ, như mở lại chương trình
    trang2.goto(url)
    trang2.wait_for_selector("#dropZone")
    trang2.locator('.nav-item[data-tab="results"]').click()
    trang2.wait_for_function("() => document.querySelector('#kqTang1 .is-on')")
    assert trang2.locator("#kqTang1 .is-on").get_attribute("data-kq") == "ma"
    assert trang2.locator("#kqTang2 .is-on").get_attribute("data-sx") == "lop"
    assert not loi, loi


def test_kho_luu_tru_hong_hay_bi_chan_khong_lam_hong_the(mo):
    page, api, loi = mo({"HS1": "10A1"}, chay=True)
    url = page.url
    trang2 = page.context.new_page()
    trang2.add_init_script("""
        localStorage.setItem('rbda_ket_qua_xem_v1', '{khong phai json');
        Object.defineProperty(window, 'localStorage', {get() { throw new Error('bi chan'); }});""")
    loi2 = []
    trang2.on("pageerror", lambda e: loi2.append(str(e)))
    trang2.goto(url)
    trang2.wait_for_selector("#dropZone")
    trang2.locator('.nav-item[data-tab="results"]').click()
    trang2.wait_for_function("() => !document.getElementById('kqBang').hidden")
    trang2.locator('#kqTang1 [data-kq="clb"]').click()                  # bấm vẫn chạy dù không ghi được
    trang2.wait_for_function("() => document.querySelector('#kqTang1 .is-on').dataset.kq === 'clb'")
    assert not loi2, loi2


def test_giu_lop_va_clb_da_chon_khi_quay_lai(mo):
    page, api, loi = mo({"HS1": "10A1", "HS2": "10A2", "HS3": "10A2"}, chay=True)
    _mo_ket_qua(page, "lop")
    page.wait_for_function("() => document.querySelectorAll('#kqChonLop option').length === 2")
    page.select_option("#kqChonLop", "10A2")
    _bang_san_sang(page, 2)
    page.locator('#kqTang1 [data-kq="clb"]').click()
    page.select_option("#kqChonClb", "B")
    page.locator('#kqTang1 [data-kq="lop"]').click()
    assert page.locator("#kqChonLop").input_value() == "10A2"
    _bang_san_sang(page, 2)
    page.locator('#kqTang1 [data-kq="clb"]').click()
    assert page.locator("#kqChonClb").input_value() == "B"
    page.locator('.nav-item[data-tab="pipeline"]').click()              # rời thẻ rồi quay lại
    _mo_ket_qua(page)
    page.wait_for_function("() => document.querySelectorAll('#kqChonClb option').length === 2")
    assert page.locator("#kqChonClb").input_value() == "B"
    assert not loi, loi


def test_trang_thai_rong_chua_chay_xep(mo):
    page, api, loi = mo({"HS1": "10A1"})                                 # chưa chạy xếp
    _mo_ket_qua(page, "ma")
    page.wait_for_function("() => !document.getElementById('kqRong').hidden")
    assert "Chưa có kết quả" in page.locator("#kqRong").inner_text()
    assert page.locator("#kqBang").is_hidden()
    assert not loi, loi


def test_trang_thai_rong_khong_co_lop_va_tim_khong_thay(mo):
    page, api, loi = mo({}, chay=True)                                   # đã chạy, không lớp nào
    _mo_ket_qua(page, "lop")
    page.wait_for_function("() => !document.getElementById('kqRong').hidden")
    assert "Chưa có lớp nào" in page.locator("#kqRong").inner_text()
    page.locator('#kqTang1 [data-kq="ma"]').click()                      # Theo mã vẫn xem được
    _bang_san_sang(page, 3)
    page.fill("#kqTimKiem", "khongcoai")
    page.wait_for_function("() => !document.getElementById('kqRong').hidden")
    assert "Không tìm thấy" in page.locator("#kqRong").inner_text()
    assert page.locator("#kqBang").is_hidden() and page.locator("#kqTimKiem").is_visible()
    page.fill("#kqTimKiem", "")
    _bang_san_sang(page, 3)
    assert not loi, loi


def test_doi_ngon_ngu_ve_lai_ca_hai_tang_va_bang(mo):
    page, api, loi = mo({"HS1": "10A1"}, chay=True)
    _mo_ket_qua(page, "ma")
    _bang_san_sang(page, 3)
    page.locator("#btnLangToggle").click()
    page.wait_for_function("() => document.getElementById('btnLangToggle').textContent.trim() === 'VI'")
    page.wait_for_function("() => /student/i.test(document.getElementById('kqDem').textContent)")
    chu = page.locator("#view-results").inner_text()
    assert not re.search(r"\{\w+\}", chu), chu
    assert re.search(r"By day of the week", chu) and re.search(r"By .*ID", chu), chu
    assert page.locator("#kqTang1 .is-on").get_attribute("data-kq") == "ma"      # lựa chọn không mất
    assert not loi, loi


def test_ket_qua_khong_bao_gio_co_diem_hay_so_boc_tham(mo):
    page, api, loi = mo({"HS1": "10A1", "HS2": "10A1"}, chay=True)
    cam = re.compile(r"điểm|bốc thăm|stb|tier|dự trữ|quyết tâm", re.I)
    for tang1 in ("lop", "clb", "ma"):
        _mo_ket_qua(page, tang1)
        page.wait_for_function("() => !document.getElementById('kqBang').hidden")
        dau = page.locator("#kqDau th").all_inner_texts()
        assert not any(cam.search(x) for x in dau), (tang1, dau)
        o = page.evaluate("""() => Array.from(document.querySelectorAll('#kqThan tr'))
            .flatMap(r => Array.from(r.children).slice(1).map(c => c.textContent.trim()))""")
        assert not any(re.fullmatch(r"-?\d+([.,]\d+)?", x) for x in o), (tang1, o)  # không ô nào là con số trơn
    assert not loi, loi


def test_theo_clb_tang2_ngay_nhom_theo_buoi_con_ma_la_danh_sach_phang(mo):
    page, api, loi = mo({"HS1": "10A1"}, chay=True, nhieu_buoi=True)
    _mo_ket_qua(page, "clb")
    page.wait_for_function("() => document.querySelectorAll('#kqChonClb option').length === 3")
    _sx(page, "ngay")
    page.wait_for_function("() => document.querySelectorAll('#kqChonClb optgroup').length === 3")
    assert page.locator("#kqChonClb optgroup").evaluate_all("g => g.map(x => x.label)") == ["2", "3", "10"]
    _sx(page, "ma")
    page.wait_for_function("() => document.querySelectorAll('#kqChonClb optgroup').length === 0")
    # danh sách phẳng theo vần tên: "CLB 10" đứng trước "CLB 2" (so vần), kèm buổi
    assert page.locator("#kqChonClb option").all_inner_texts() == ["10 · CLB 10", "2 · CLB 2", "3 · CLB 3"]
    assert not loi, loi


def test_nho_lop_va_clb_da_chon_sau_khi_mo_lai_va_bo_qua_neu_khong_con(mo):
    page, api, loi = mo({"HS1": "10A1", "HS2": "10A2", "HS3": "10A2"}, chay=True)
    url = page.url
    _mo_ket_qua(page, "lop")
    page.wait_for_function("() => document.querySelectorAll('#kqChonLop option').length === 2")
    page.select_option("#kqChonLop", "10A2")
    page.locator('#kqTang1 [data-kq="clb"]').click()
    page.select_option("#kqChonClb", "B")
    trang2 = page.context.new_page()
    trang2.goto(url)
    trang2.wait_for_selector("#dropZone")
    trang2.locator('.nav-item[data-tab="results"]').click()
    trang2.wait_for_function("() => document.querySelectorAll('#kqChonClb option').length === 2")
    assert trang2.locator("#kqChonClb").input_value() == "B"
    trang2.locator('#kqTang1 [data-kq="lop"]').click()
    assert trang2.locator("#kqChonLop").input_value() == "10A2"
    # giá trị đã lưu mà không còn tồn tại thì lùi về mục đầu, không lỗi
    trang3 = page.context.new_page()
    trang3.add_init_script("localStorage.setItem('rbda_ket_qua_xem_v1', JSON.stringify("
                           "{tang1: 'lop', tang2: 'ngay', lop: '99Z', clb: 'khong_co'}));")
    loi3 = []
    trang3.on("pageerror", lambda e: loi3.append(str(e)))
    trang3.goto(url)
    trang3.wait_for_selector("#dropZone")
    trang3.locator('.nav-item[data-tab="results"]').click()
    trang3.wait_for_function("() => document.querySelectorAll('#kqChonLop option').length === 2")
    assert trang3.locator("#kqChonLop").input_value() == "10A1"
    assert not loi and not loi3, (loi, loi3)


def test_so_it_so_nhieu_tieng_anh(mo):
    page, api, loi = mo({"HS1": "10A1"}, chay=True)
    _mo_ket_qua(page, "ma")
    _bang_san_sang(page, 3)
    page.locator("#btnLangToggle").click()
    page.wait_for_function("() => /^3 students/i.test(document.getElementById('kqDem').textContent.trim())")
    page.fill("#kqTimKiem", "HS1")
    page.wait_for_function("() => /^1 student$/i.test(document.getElementById('kqDem').textContent.trim())")
    assert not loi, loi
