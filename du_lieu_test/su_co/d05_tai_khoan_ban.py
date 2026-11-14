# -*- coding: utf-8 -*-
"""FA-SC diễn tập S37: em A làm bài trên máy còn đăng nhập tài khoản của bạn B cùng trường. Bài của A được ghi cho B;
B bị "One response per person" chặn nên không có bài của chính mình. Dữ liệu MÔ PHỎNG."""
import copy
import os

import chung as c

NGAY = "thu_2"
THU_TOI_DA = 12


def dien_tap(ra, seed=c.SEED, so_hs=c.SO_HS):
    dot = c.sinh_dot(so_hs, seed)
    sach = c.chay(dot, os.path.join(ra, "sach"), seed)
    loai = sach["loai"]
    a, clb = c.chon_em_trung_tuyen(dot, sach, loai, NGAY)
    ung_vien = [h["sid"] for h in dot["hs"] if sach["ket_qua"].get((h["sid"], NGAY)) != clb and h["nv"][NGAY][0] == clb
                and h["thi"][clb][0] < c.em(dot, a)["thi"][clb][0]][:THU_TOI_DA]
    for i, b in enumerate(ung_vien):                      # thử lần lượt tới khi gặp một B được lợi (tất định)
        loi = copy.deepcopy(dot)
        ha, hb = c.em(loi, a), c.em(loi, b)
        hb["thi"][clb] = ha["thi"].pop(clb)
        r = c.chay(loi, os.path.join(ra, "loi_%d" % i), seed)
        if r["ket_qua"].get((b, NGAY)) == clb:
            break
    o_doi, em_doi = c.so_sanh(sach["ket_qua"], r["ket_qua"], bo_qua=(a, b))
    return c.in_bang("d05 S37 thi bằng tài khoản của bạn", [
        ("bị chặn ở bước", r["buoc_chan"]),
        ("số cặp (A, B) đã thử tới khi B được lợi", i + 1),
        ("cảnh báo nhắc tới B (em được ghi điểm nhầm)", sum(1 for x in r["canh_bao_day_du"] if x[1] in (b, hb["email"]))),
        ("cảnh báo NOT_ATTEMPTED của A", sum(1 for x in r["canh_bao_day_du"] if x[1] in (a, ha["email"]) and "NOT_ATTEMPTED" in x[2])),
        ("A: CLB ngày đó (sạch -> lỗi)", "%s -> %s" % (sach["ket_qua"].get((a, NGAY)), r["ket_qua"].get((a, NGAY)))),
        ("B: CLB ngày đó (sạch -> lỗi)", "%s -> %s" % (sach["ket_qua"].get((b, NGAY)), r["ket_qua"].get((b, NGAY)))),
        ("em KHÁC đổi CLB so với lần sạch", em_doi),
    ])


if __name__ == "__main__":
    c.main(dien_tap, __doc__)
