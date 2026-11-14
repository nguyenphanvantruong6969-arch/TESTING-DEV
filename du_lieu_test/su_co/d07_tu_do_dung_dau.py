# -*- coding: utf-8 -*-
"""FA-SC diễn tập S33: em đưa CLB Tự do lên nguyện vọng 1 dù thật ra muốn CLB Tuyển chọn (và đã trúng ở lần sạch).
Dữ liệu MÔ PHỎNG."""
import copy
import os

import chung as c

NGAY = "thu_2"


def dien_tap(ra, seed=c.SEED, so_hs=c.SO_HS):
    dot = c.sinh_dot(so_hs, seed)
    sach = c.chay(dot, os.path.join(ra, "sach"), seed)
    loai = sach["loai"]
    sid, clb = c.chon_em_trung_tuyen(dot, sach, loai, NGAY)
    loi = copy.deepcopy(dot)
    h = c.em(loi, sid)
    tu_do = next(x for x in h["nv"][NGAY] if loai[x] == "TU_DO")
    h["nv"][NGAY] = [tu_do] + [x for x in h["nv"][NGAY] if x != tu_do]
    r = c.chay(loi, os.path.join(ra, "loi"), seed)
    return c.in_bang("d07 S33 CLB Tự do đứng đầu", [
        ("bị chặn ở bước", r["buoc_chan"]),
        ("cảnh báo nhắc tới em", sum(1 for x in r["canh_bao_day_du"] if x[1] in (sid, h["email"]))),
        ("CLB của em ngày đó (sạch -> lỗi)", "%s -> %s" % (clb, r["ket_qua"].get((sid, NGAY)))),
        ("điểm thi của em ở CLB Tuyển chọn (câu đúng / 5)", h["thi"][clb][0]),
    ])


if __name__ == "__main__":
    c.main(dien_tap, __doc__)
