# -*- coding: utf-8 -*-
"""FA-SC diễn tập S30: đường B, em tự gõ mã học sinh và gõ sai. (a) trùng mã bạn khác; (b) không trùng ai.
Dữ liệu MÔ PHỎNG."""
import copy
import os

import chung as c

EM, MA_BAN, MA_LA = "HS010", "HS011", "HS01O"


def dien_tap(ra, seed=c.SEED, so_hs=c.SO_HS):
    dot = c.sinh_dot(so_hs, seed)
    sach = c.chay(dot, os.path.join(ra, "sach"), seed)
    a = copy.deepcopy(dot)
    c.em(a, EM)["sid"] = MA_BAN
    ra_a = c.chay(a, os.path.join(ra, "trung"), seed)
    b = copy.deepcopy(dot)
    c.em(b, EM)["sid"] = MA_LA
    ra_b = c.chay(b, os.path.join(ra, "la"), seed)
    o_doi, em_doi = c.so_sanh(sach["ket_qua"], ra_b["ket_qua"], bo_qua=(EM, MA_LA))
    cu = {k[1]: v for k, v in sach["ket_qua"].items() if k[0] == EM}
    moi = {k[1]: v for k, v in ra_b["ket_qua"].items() if k[0] == MA_LA}
    return c.in_bang("d03 S30 gõ sai mã học sinh", [
        ("(a) trùng mã: bị chặn ở bước", ra_a["buoc_chan"]),
        ("(a) mã lỗi", ", ".join(sorted(set(ra_a["loi"])))),
        ("(a) cảnh báo của bộ chuyển đổi nhắc mã trùng", c.dem(ra_a["canh_bao"], MA_BAN)),
        ("(b) mã lạ: bị chặn ở bước", ra_b["buoc_chan"]),
        ("(b) cảnh báo nhắc mã lạ", c.dem(ra_b["canh_bao"], MA_LA)),
        ("(b) mã thật có kết quả / mã lạ có kết quả",
         "%d / %d" % (sum(1 for k in ra_b["ket_qua"] if k[0] == EM), len(moi))),
        ("(b) số ngày CLB của chính em đổi vì mã khác", sum(1 for d in cu if cu[d] != moi.get(d))),
        ("(b) em KHÁC đổi CLB so với lần sạch", em_doi),
    ])


if __name__ == "__main__":
    c.main(dien_tap, __doc__)
