# -*- coding: utf-8 -*-
"""FA-SC diễn tập I2: IT nạp cùng một Sổ nhập hai lần rồi mới chạy. Dữ liệu MÔ PHỎNG."""
import os

import chung as c
import chuyen_forms_sang_phan_mem as cv


def dien_tap(ra, seed=c.SEED, so_hs=c.SO_HS):
    dot = c.sinh_dot(so_hs, seed)
    sach = c.chay(dot, os.path.join(ra, "sach"), seed)
    de, loai = c.de_fa()
    thu_muc = os.path.join(ra, "hai_lan")
    so_clb, tep_dk, tep_thi = c.ghi_tep(dot, thu_muc, de, loai)
    cv.chuyen_fa_daa(os.path.join(thu_muc, "nap"), de, so_clb, dang_ky_xlsx=tep_dk, quiz_xlsx=[tep_thi])
    api, db = c.mo_kiosk(thu_muc)
    so = os.path.join(thu_muc, "nap", cv.TEN_SO)
    n1, n2 = c.nap(api, so), c.nap(api, so)
    kq = api.run_pipeline(seed=seed)
    return c.in_bang("d13 I2 nạp cùng một sổ hai lần", [
        ("nạp lần 1 ok / lần 2 ok / chạy ok", "%s / %s / %s" % (n1["ok"], n2["ok"], kq["ok"])),
        ("số học sinh trong kiosk", c.sql(db, "SELECT COUNT(*) FROM students")[0][0]),
        ("kết quả giống hệt lần nạp một lần", c.ket_qua(db) == sach["ket_qua"]),
    ])


if __name__ == "__main__":
    c.main(dien_tap, __doc__)
