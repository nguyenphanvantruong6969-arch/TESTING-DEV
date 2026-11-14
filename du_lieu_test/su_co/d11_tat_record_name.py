# -*- coding: utf-8 -*-
"""FA-SC diễn tập T2: biểu mẫu bài thi để "Record name" TẮT, mọi phiếu thi không có email. Dữ liệu MÔ PHỎNG."""
import os

import chung as c


def dien_tap(ra, seed=c.SEED, so_hs=c.SO_HS):
    dot = c.sinh_dot(so_hs, seed)
    r = c.chay(dot, os.path.join(ra, "loi"), seed, an_email_thi=True)
    return c.in_bang("d11 T2 Record name tắt", [
        ("bị chặn ở bước", r["buoc_chan"]),
        ("mã lỗi", ", ".join(sorted(set(r["loi"])))),
        ("cảnh báo 'phiếu không có Email'", c.dem(r["canh_bao"], "không có Email")),
        ("cảnh báo NOT_ATTEMPTED", c.dem(r["canh_bao"], "NOT_ATTEMPTED")),
    ])


if __name__ == "__main__":
    c.main(dien_tap, __doc__)
