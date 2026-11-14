# -*- coding: utf-8 -*-
"""FA-SC diễn tập S5: em làm bài thi bằng tài khoản không có trong danh sách đăng ký. Dữ liệu MÔ PHỎNG."""
import copy
import os

import chung as c

EMAIL_LA = "ca.nhan@ngoai.example"


def dien_tap(ra, seed=c.SEED, so_hs=c.SO_HS):
    dot = c.sinh_dot(so_hs, seed)
    sach = c.chay(dot, os.path.join(ra, "sach"), seed)
    sid, clb = c.chon_em_trung_tuyen(dot, sach, sach["loai"])
    loi = copy.deepcopy(dot)
    h = c.em(loi, sid)
    bai, h["thi"] = h["thi"], {}
    r = c.chay(loi, os.path.join(ra, "loi"), seed, phieu_thi_them=[(EMAIL_LA, bai)])
    o_doi, em_doi = c.so_sanh(sach["ket_qua"], r["ket_qua"], bo_qua=(sid,))
    return c.in_bang("d04 S5 thi bằng sai tài khoản", [
        ("bị chặn ở bước", r["buoc_chan"]),
        ("cảnh báo 'email không có trong danh sách'", c.dem(r["canh_bao"], EMAIL_LA)),
        ("cảnh báo NOT_ATTEMPTED của em", sum(1 for x in r["canh_bao_day_du"] if x[1] in (sid, h["email"]) and "NOT_ATTEMPTED" in x[2])),
        ("số ngày em mất CLB Tuyển chọn đã trúng ở lần sạch",
         sum(1 for k, v in sach["ket_qua"].items()
             if k[0] == sid and sach["loai"][v] == "TUYEN_CHON" and r["ket_qua"].get(k) != v)),
        ("em KHÁC đổi CLB so với lần sạch", em_doi),
    ])


if __name__ == "__main__":
    c.main(dien_tap, __doc__)
