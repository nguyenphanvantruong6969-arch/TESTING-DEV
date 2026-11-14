# -*- coding: utf-8 -*-
"""FA-SC diễn tập S1: em định thi CLB X (đã xếp) nhưng bấm nhầm, làm bài của CLB Y (không xếp). Để có một CLB "không
xếp" trong bộ mẫu ba CLB mỗi ngày, em bỏ trống nguyện vọng 3 ở ngày của Y. Dữ liệu MÔ PHỎNG."""
import copy
import os

import chung as c

NGAY_X, NGAY_Y = "thu_2", "thu_3"


def dien_tap(ra, seed=c.SEED, so_hs=c.SO_HS):
    dot = c.sinh_dot(so_hs, seed)
    loai = c.de_fa()[1]
    y = next(k for k, v in loai.items() if v == "TUYEN_CHON" and k in dot["hs"][0]["nv"][NGAY_Y])
    for h in dot["hs"]:                                   # nền: em nào xếp Y cuối thì bỏ Y (không ảnh hưởng tới X)
        if h["nv"][NGAY_Y][-1] == y:
            h["nv"][NGAY_Y] = h["nv"][NGAY_Y][:2]
            h["thi"].pop(y, None)
    sach = c.chay(dot, os.path.join(ra, "sach"), seed)
    sid, x = next((h["sid"], sach["ket_qua"][(h["sid"], NGAY_X)]) for h in dot["hs"]
                  if y not in h["nv"][NGAY_Y] and loai[sach["ket_qua"][(h["sid"], NGAY_X)]] == "TUYEN_CHON")
    loi = copy.deepcopy(dot)
    h = c.em(loi, sid)
    h["thi"][y] = h["thi"].pop(x)
    r = c.chay(loi, os.path.join(ra, "loi"), seed)
    cua_em = [t[2] for t in r["canh_bao_day_du"] if t[1] in (sid, h["email"])]
    o_doi, em_doi = c.so_sanh(sach["ket_qua"], r["ket_qua"], bo_qua=(sid,))
    return c.in_bang("d06 S1 thi nhầm CLB", [
        ("bị chặn ở bước", r["buoc_chan"]),
        ("cảnh báo 'làm bài nhưng KHÔNG xếp CLB này'", c.dem(cua_em, "KHÔNG xếp")),
        ("cảnh báo NOT_ATTEMPTED cho CLB định thi", c.dem(cua_em, "NOT_ATTEMPTED")),
        ("hai cảnh báo nằm ở hai dòng rời nhau", "có" if len(cua_em) >= 2 else "không"),
        ("tổng số dòng cảnh báo IT phải đọc", len(r["canh_bao"])),
        ("CLB của em ngày X (sạch -> lỗi)", "%s -> %s" % (sach["ket_qua"].get((sid, NGAY_X)), r["ket_qua"].get((sid, NGAY_X)))),
        ("em KHÁC đổi CLB so với lần sạch", em_doi),
    ])


if __name__ == "__main__":
    c.main(dien_tap, __doc__)
