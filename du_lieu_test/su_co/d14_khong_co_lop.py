# -*- coding: utf-8 -*-
"""FA-SC diễn tập S45: đường B không hỏi lớp. Xuất kết quả theo lớp cho giáo viên chủ nhiệm thì ra gì.
Dữ liệu MÔ PHỎNG."""
import os

import chung as c


def dien_tap(ra, seed=c.SEED, so_hs=c.SO_HS):
    dot = c.sinh_dot(so_hs, seed)
    r = c.chay(dot, os.path.join(ra, "sach"), seed)
    thu_muc = os.path.join(ra, "theo_lop")
    x = r["api"].export_theo_lop(thu_muc)
    tep = sorted(os.listdir(x["data"]["thu_muc"])) if x["ok"] else []
    r2 = c.chay(dot, os.path.join(ra, "co_ds"), seed, danh_sach_truong=c.danh_sach_that(dot))   # FA-SC L1
    x2 = r2["api"].export_theo_lop(os.path.join(ra, "theo_lop_ds"))
    tep2 = sorted(os.listdir(x2["data"]["thu_muc"])) if x2["ok"] else []
    return c.in_bang("d14 S45 không có lớp", [
        ("em không có lớp trong kiosk / tổng",
         "%d / %d" % (c.sql(r["db"], "SELECT COUNT(*) FROM students WHERE class_id IS NULL OR class_id = ''")[0][0], so_hs)),
        ("xuất theo lớp ok", x["ok"]),
        ("các tệp được ghi", ", ".join(tep)),
        ("[có danh sách trường] em không có lớp trong kiosk / tổng",
         "%d / %d" % (c.sql(r2["db"], "SELECT COUNT(*) FROM students WHERE class_id IS NULL OR class_id = ''")[0][0], so_hs)),
        ("[có danh sách trường] số tệp theo lớp", len(tep2)),
    ])


if __name__ == "__main__":
    c.main(dien_tap, __doc__)
