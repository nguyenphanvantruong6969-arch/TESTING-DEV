# -*- coding: utf-8 -*-
"""FA-SC diễn tập T3: gõ chỉ tiêu một CLB Tuyển chọn là 2 thay vì 20. Dữ liệu MÔ PHỎNG."""
import copy
import os

import chung as c

NGAY = "thu_2"


def dien_tap(ra, seed=c.SEED, so_hs=c.SO_HS):
    dot = c.sinh_dot(so_hs, seed)
    sach = c.chay(dot, os.path.join(ra, "sach"), seed)
    clb = next(k for k, v in sach["loai"].items() if v == "TUYEN_CHON" and k in dot["hs"][0]["nv"][NGAY])
    loi = copy.deepcopy(dot)
    loi["cho"][clb] = 2
    r = c.chay(loi, os.path.join(ra, "loi"), seed)
    o_doi, em_doi = c.so_sanh(sach["ket_qua"], r["ket_qua"])
    mat = sum(1 for k, v in sach["ket_qua"].items() if v == clb and r["ket_qua"].get(k) != clb)
    return c.in_bang("d09 T3 chỉ tiêu gõ nhầm (2 thay vì 20)", [
        ("bị chặn ở bước", r["buoc_chan"]),
        ("cảnh báo của bộ chuyển đổi (so với lần sạch)", "%d (sạch: %d)" % (len(r["canh_bao"]), len(sach["canh_bao"]))),
        ("em mất chỗ ở CLB đó", mat),
        ("em đổi CLB so với lần sạch", em_doi),
    ])


if __name__ == "__main__":
    c.main(dien_tap, __doc__)
