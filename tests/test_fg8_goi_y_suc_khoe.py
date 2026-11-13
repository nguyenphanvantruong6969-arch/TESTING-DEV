"""FG-8 (STEP0, spec §3), phần chữ: gợi ý của khung "Cảnh báo dữ liệu" nói rằng mục NGHIÊM TRỌNG chặn việc chạy, ở CẢ HAI
ngôn ngữ. Đọc thẳng `i18n.js`. Dữ liệu MÔ PHỎNG."""
import os
import re

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _gia_tri():
    with open(os.path.join(GOC, "i18n.js"), encoding="utf-8") as f:
        js = f.read()
    ds = re.findall(r'health_panel_hint:\s*"((?:[^"\\]|\\.)*)"', js)
    assert len(ds) == 2, ds                                  # đúng hai bản: vi trước, en sau
    return ds


def test_goi_y_vi_noi_muc_nghiem_trong_chan_chay():
    vi = _gia_tri()[0].lower()
    assert "nghiêm trọng" in vi and re.search(r"chặn|dừng", vi)
    assert "không chặn việc sắp xếp" not in vi              # câu cũ nói ngược lại cho mọi mục


def test_goi_y_en_noi_muc_serious_chan_chay():
    en = _gia_tri()[1].lower()
    assert "serious" in en and re.search(r"stop|block", en)
    assert "don't stop the allocation" not in en
