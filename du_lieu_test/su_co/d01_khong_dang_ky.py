# -*- coding: utf-8 -*-
"""FA-SC diễn tập S8: một em không đăng ký gì trong cả đợt. Dữ liệu MÔ PHỎNG."""
import copy
import os

import chung as c

EM = "HS007"


def dien_tap(ra, seed=c.SEED, so_hs=c.SO_HS):
    dot = c.sinh_dot(so_hs, seed)
    sach = c.chay(dot, os.path.join(ra, "sach"), seed)
    loi = copy.deepcopy(dot)
    loi["hs"] = [h for h in loi["hs"] if h["sid"] != EM]
    r = c.chay(loi, os.path.join(ra, "loi"), seed)
    o_doi, em_doi = c.so_sanh(sach["ket_qua"], r["ket_qua"], bo_qua=(EM,))
    ds = c.danh_sach_that(dot)                                    # FA-SC L1: cùng đợt lỗi, có danh sách của trường
    r2 = c.chay(loi, os.path.join(ra, "loi_ds"), seed, danh_sach_truong=ds)
    bc = r2["bao_cao_danh_sach"] or {"chua_dang_ky": []}
    return c.in_bang("d01 S8 không đăng ký", [
        ("bị chặn ở bước", r["buoc_chan"]),
        ("cảnh báo có nhắc tới em", c.dem(r["canh_bao"], EM.lower()) + c.dem(r["canh_bao"], EM)),
        ("em có trong kiosk", c.sql(r["db"], "SELECT COUNT(*) FROM students WHERE student_id = ?", (EM,))[0][0]),
        ("số ngày em được xếp (kể cả CLB Tự do)", sum(1 for k in r["ket_qua"] if k[0] == EM)),
        ("em KHÁC đổi CLB so với lần sạch", em_doi),
        ("[có danh sách trường] em nằm trong CHUA_DANG_KY", sum(1 for _, m in bc["chua_dang_ky"] if m == EM)),
        ("[có danh sách trường] cảnh báo nhắc tới em", c.dem(r2["canh_bao"], EM)),
    ])


if __name__ == "__main__":
    c.main(dien_tap, __doc__)
