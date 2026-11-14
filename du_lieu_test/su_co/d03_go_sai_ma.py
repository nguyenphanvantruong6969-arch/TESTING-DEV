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
    ds = c.danh_sach_that(dot)                                    # FA-SC L1: cùng hai lỗi, có danh sách của trường
    ra_a2 = c.chay(a, os.path.join(ra, "trung_ds"), seed, danh_sach_truong=ds)
    ra_b2 = c.chay(b, os.path.join(ra, "la_ds"), seed, danh_sach_truong=ds)
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
        ("[có danh sách trường] (a) bị chặn ở bước", ra_a2["buoc_chan"]),
        ("[có danh sách trường] (a) cảnh báo nhắc email của em", c.dem(ra_a2["canh_bao"], c.em(dot, EM)["email"])),
        ("[có danh sách trường] (a) kiosk có mã thật của em", len(c.sql(ra_a2["db"], "SELECT 1 FROM students WHERE student_id = ?", (EM,))) if ra_a2.get("db") else 0),
        ("[có danh sách trường] (b) bị chặn ở bước", ra_b2["buoc_chan"]),
        ("[có danh sách trường] (b) cảnh báo nhắc mã lạ / mã thật có kết quả",
         "%d / %d" % (c.dem(ra_b2["canh_bao"], MA_LA), sum(1 for k in ra_b2["ket_qua"] if k[0] == EM))),
    ])


if __name__ == "__main__":
    c.main(dien_tap, __doc__)
