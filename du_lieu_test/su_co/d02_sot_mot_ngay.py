# -*- coding: utf-8 -*-
"""FA-SC diễn tập S36: mỗi ngày một biểu mẫu, một em bỏ sót biểu mẫu của một ngày. Dữ liệu MÔ PHỎNG."""
import copy
import os

import chung as c

EM, NGAY = "HS008", "thu_4"


def dien_tap(ra, seed=c.SEED, so_hs=c.SO_HS):
    dot = c.sinh_dot(so_hs, seed)
    sach = c.chay(dot, os.path.join(ra, "sach"), seed)
    loi = copy.deepcopy(dot)
    h = c.em(loi, EM)
    del h["nv"][NGAY]
    h["thi"] = {k: v for k, v in h["thi"].items() if k in [x for xs in h["nv"].values() for x in xs]}
    r = c.chay(loi, os.path.join(ra, "loi"), seed)
    o_doi, em_doi = c.so_sanh(sach["ket_qua"], r["ket_qua"], bo_qua=(EM,))
    return c.in_bang("d02 S36 sót một ngày", [
        ("bị chặn ở bước", r["buoc_chan"]),
        ("cảnh báo có nhắc tới em", c.dem(r["canh_bao"], h["email"]) + c.dem(r["canh_bao"], EM)),
        ("số ngày em được xếp (lần sạch -> lần lỗi)",
         "%d -> %d" % (sum(1 for k in sach["ket_qua"] if k[0] == EM), sum(1 for k in r["ket_qua"] if k[0] == EM))),
        ("CLB của em ở ngày bị sót", r["ket_qua"].get((EM, NGAY))),
        ("em KHÁC đổi CLB so với lần sạch", em_doi),
    ])


if __name__ == "__main__":
    c.main(dien_tap, __doc__)
