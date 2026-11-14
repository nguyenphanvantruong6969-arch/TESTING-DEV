# -*- coding: utf-8 -*-
"""FA-SC diễn tập S4b / D-SC4: MỘT em có một giá trị huy chương sai (50 thay vì 60) trong CSDL tạm, như khi dữ liệu
đường A lọt qua app. Hỏi: lần chạy của cả trường có bị chặn không. Dữ liệu MÔ PHỎNG; chỉ sửa CSDL TẠM."""
import os
import sqlite3

import chung as c


def dien_tap(ra, seed=c.SEED, so_hs=c.SO_HS):
    dot = c.sinh_dot(so_hs, seed)
    r = c.chay(dot, os.path.join(ra, "sach"), seed)
    api, db = r["api"], r["db"]
    truoc = c.sql(db, "SELECT COUNT(*) FROM run_history")[0][0]
    con = sqlite3.connect(db)
    sid, clb = con.execute("SELECT student_id, club_id FROM wharton_bids WHERE points = 60 ORDER BY 1, 2").fetchone()
    con.execute("UPDATE wharton_bids SET points = 50 WHERE student_id = ? AND club_id = ?", (sid, clb))
    con.commit()
    con.close()
    kq = api.run_pipeline(seed=seed)
    return c.in_bang("d10 S4b một em sai huy chương", [
        ("lần chạy ok", kq["ok"]),
        ("mã lỗi", ", ".join(sorted({e["code"] for e in kq["errors"]}))),
        ("số em có lỗi / số em của trường", "1 / %d" % so_hs),
        ("run_history thêm dòng", c.sql(db, "SELECT COUNT(*) FROM run_history")[0][0] - truoc),
        ("kết quả cũ còn nguyên", c.ket_qua(db) == r["ket_qua"]),
    ])


if __name__ == "__main__":
    c.main(dien_tap, __doc__)
