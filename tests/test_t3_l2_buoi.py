"""T3-14 (đường a): nhãn buổi hiển thị = bảng JS phản chiếu `so_nhap.NHAN_BUOI`, qua i18n.js. Dữ liệu MÔ PHỎNG."""

import os
import re

import so_nhap

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN = {"thu_2": "Mon", "thu_3": "Tue", "thu_4": "Wed", "thu_5": "Thu", "thu_6": "Fri", "thu_7": "Sat", "chu_nhat": "Sun"}


def _doc(ten):
    with open(os.path.join(GOC, ten), encoding="utf-8") as f:
        return f.read()


def _khoi(chu, ngon_ngu):
    """Phần thân bảng chuỗi của một ngôn ngữ trong i18n.js (khối `vi: {` hoặc `en: {` đầu tiên)."""
    m = re.search(r"\n\s+%s:\s*\{" % ngon_ngu, chu)
    assert m, ngon_ngu
    return chu[m.end():]


def test_bang_nhan_buoi_trong_i18n_bang_bang_python():
    chu = _doc("i18n.js")
    for ngon_ngu in ("vi", "en"):
        khoi = _khoi(chu, ngon_ngu)
        for nhan, ma in so_nhap.NHAN_BUOI:
            m = re.search(r'\bbuoi_ma_%s:\s*"([^"]*)"' % ma, khoi)
            assert m, (ngon_ngu, ma)
            mong = nhan if ngon_ngu == "vi" else EN[ma]
            assert m.group(1) == mong, (ngon_ngu, ma, m.group(1))


def test_nhan_buoi_js_tra_nhan_cho_ma_buoi_va_giu_chu_la():
    js = _doc("js/05_quan_ly.js")
    m = re.search(r"function nhanBuoi\(buoi\) \{(.*?)\n\}", js, re.S)
    assert m and "buoi_ma_" in m.group(1)


def test_tieu_de_cot_buoi_khong_tu_viet_hoa():
    css = _doc("style.css")
    assert re.search(r"th\.cot-buoi-tieu-de\s*\{[^}]*text-transform:\s*none", css)


def test_t3_28_bo_lich_tuan_va_ti_le_dau_phay():
    """T3-28: một bảng "Tải theo buổi"; không còn khối Lịch tuần; tỉ lệ viết dấu phẩy, không "×"."""
    html, js = _doc("index.html"), _doc("js/05_quan_ly.js")
    assert "lichTuan" not in html and "loadLichTuan" not in js
    assert "admin_lich_tuan" not in _doc("i18n.js")
    assert 'replace(".", ",")' in js and '+ "×"' not in js


def test_t3_21_va_t3_23_khung_gop():
    """T3-21: không còn thẻ fillPanel, ô sắp xếp nằm trong clbPanel. T3-23: ô tích phụ nằm trong mục thu gọn."""
    html = _doc("index.html")
    assert 'id="fillPanel"' not in html and 'id="clubFillList"' not in html
    assert html.index('id="clbPanel"') < html.index('id="fillSapXep"') < html.index('id="clbTable"')
    nang_cao = html[html.index('id="xuatNangCao"'):]
    nang_cao = nang_cao[:nang_cao.index("</details>")]
    for ma in ("xuatKetQua", "xuatKemCsv", "xuatDauVao", "xuatThayDoi", "xuatHocSinh", "btnChonHocSinh"):
        assert 'id="%s"' % ma in nang_cao, ma
    assert html.index('id="btnXuatTuyChon"') > html.index("</details>", html.index('id="xuatNangCao"'))
