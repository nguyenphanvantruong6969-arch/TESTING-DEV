"""A13.12 (4.3): khoá giao diện `dc_*` (khối Điểm chuẩn) nào khai báo thì phải có nơi dùng.

Khoá chết làm bảng chữ phình ra và khiến người dịch tốn công một chuỗi không bao giờ hiện. Khoá được
ghép từ tiền tố động (`"dc_muc_" + muc`) cũng tính là có dùng. Quét chỉ trên `js/`, `index.html` và
các tệp `.py` ở gốc kho (nơi giao diện lấy chữ).
"""

import glob
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIEN_TO_DONG = ("dc_muc_",)


def _doc(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def test_khong_con_khoa_dc_chet():
    nguon = _doc(os.path.join(BASE, "i18n.js"))
    khoa = sorted(set(re.findall(r"^\s*(dc_\w+):", nguon, re.M)))
    assert len(khoa) > 20
    ma = "".join(_doc(p) for p in glob.glob(os.path.join(BASE, "js", "*.js"))
                 + [os.path.join(BASE, "index.html")] + glob.glob(os.path.join(BASE, "*.py")))
    chet = [k for k in khoa if k not in ma and not k.startswith(TIEN_TO_DONG)]
    assert chet == []


def test_tien_to_dong_that_su_duoc_ghep():
    ma = "".join(_doc(p) for p in glob.glob(os.path.join(BASE, "js", "*.js")))
    for tt in TIEN_TO_DONG:
        assert re.search(r"[\"'`]%s[\"'`]\s*\+|`%s\$\{" % (tt, tt), ma), tt
