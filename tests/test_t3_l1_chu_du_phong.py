"""T3-L1 (T3-40): chữ dự phòng trong index.html phải KHỚP catalog i18n.js (mặc định trường học, tiếng Việt).

Chữ dự phòng chỉ hiện khi tải catalog thất bại, nhưng để lệch nguồn là mầm lỗi (còn gạch dài, đại từ cũ...).
Dữ liệu là chữ cố định của phần mềm, không có số liệu."""

import json
import os
import re
import shutil
import subprocess
from html.parser import HTMLParser

import pytest

import nhan_ws

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
node = shutil.which("node")

_LAY_VI = """
const fs = require("fs");
const src = fs.readFileSync(process.argv[1], "utf8");
const start = src.indexOf("const UI_STRINGS = {");
const b = src.indexOf("{", start);
let d = 0, i = b;
for (; i < src.length; i++) { if (src[i] === "{") d++; else if (src[i] === "}") { d--; if (d === 0) { i++; break; } } }
process.stdout.write(JSON.stringify(eval("(" + src.slice(b, i) + ")").vi));
"""


class _Doc(HTMLParser):
    """Gom (khoá, chữ) của phần tử LÁ có data-i18n, và (khoá, thuộc tính) cho placeholder / aria-label."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.la, self.thuoc_tinh = [], []
        self._mo = None  # [khoa, chu, co_con]

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self._mo is not None:
            self._mo[2] = True
        if "data-i18n" in a:
            self._mo = [a["data-i18n"], "", False]
        if "data-i18n-placeholder" in a:
            self.thuoc_tinh.append((a["data-i18n-placeholder"], a.get("placeholder", "")))
        if "data-i18n-aria-label" in a:
            self.thuoc_tinh.append((a["data-i18n-aria-label"], a.get("aria-label", "")))

    def handle_data(self, data):
        if self._mo is not None:
            self._mo[1] += data

    def handle_endtag(self, tag):
        if self._mo is not None:
            if not self._mo[2]:
                self.la.append((self._mo[0], self._mo[1]))
            self._mo = None


def _chuan(s):
    return re.sub(r"\s+", " ", s).strip()


def _khop(html_chu, catalog):
    mong = _chuan(nhan_ws.dien(catalog, None, "vi"))
    if "{" in mong:  # còn tham số thời gian chạy ({n}, {seed}...): khớp theo khuôn
        mau = re.escape(mong)
        mau = re.sub(r"\\\{\w+\\\}", ".+?", mau)
        return re.fullmatch(mau, _chuan(nhan_ws.dien(html_chu, None, "vi"))) is not None, mong
    return _chuan(nhan_ws.dien(html_chu, None, "vi")) == mong, mong


@pytest.mark.skipif(not node, reason="không có node")
def test_chu_du_phong_trong_index_html_khop_catalog():
    vi = json.loads(subprocess.run(
        [node, "-e", _LAY_VI, "--", os.path.join(GOC, "i18n.js")],
        capture_output=True, text=True, check=True, encoding="utf-8").stdout)
    p = _Doc()
    p.feed(open(os.path.join(GOC, "index.html"), encoding="utf-8").read())
    lech = []
    for khoa, chu in p.la:
        if chu.strip() and khoa in vi:
            ok, mong = _khop(chu, vi[khoa])
            if not ok:
                lech.append((khoa, _chuan(chu)[:80], mong[:80]))
    for khoa, chu in p.thuoc_tinh:
        if chu.strip() and khoa in vi:
            ok, mong = _khop(chu, vi[khoa])
            if not ok:
                lech.append((khoa, chu[:80], mong[:80]))
    assert not lech, "\n".join(map(str, lech))
    assert len(p.la) > 150  # có đọc đủ trang
