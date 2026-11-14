# -*- coding: utf-8 -*-
"""FA-SC diễn tập "mất điện / lỗi giữa lần chạy" (bất biến 5): đã có kết quả; sửa một chỉ tiêu; lần chạy lại bị lỗi
ngay ở bước kiểm ổn định (giả lập bằng cách thay hàm kiểm TRONG TIẾN TRÌNH diễn tập, không sửa tệp nào).
Dữ liệu MÔ PHỎNG."""
import os
import sqlite3

import chung as c

import api as api_mod  # noqa: E402,I001  (sau chung: chung thêm thư mục gốc vào sys.path)


def dien_tap(ra, seed=c.SEED, so_hs=c.SO_HS):
    dot = c.sinh_dot(so_hs, seed)
    r = c.chay(dot, os.path.join(ra, "sach"), seed)
    api, db = r["api"], r["db"]
    truoc = (c.sql(db, "SELECT * FROM match_results ORDER BY student_id, buoi"),
             c.sql(db, "SELECT COUNT(*) FROM run_history")[0][0])
    clb = next(k for k, v in r["loai"].items() if v == "TUYEN_CHON")
    con = sqlite3.connect(db)
    con.execute("UPDATE clubs SET capacity = capacity + 5 WHERE club_id = ?", (clb,))
    con.commit()
    con.close()
    goc = api_mod.verify_stability

    def hong(*a, **k):
        raise RuntimeError("gia lap mat dien giua lan chay")

    api_mod.verify_stability = hong
    try:
        kq = api.run_pipeline(seed=seed)
    finally:
        api_mod.verify_stability = goc
    sau = (c.sql(db, "SELECT * FROM match_results ORDER BY student_id, buoi"),
           c.sql(db, "SELECT COUNT(*) FROM run_history")[0][0])
    lai = api.run_pipeline(seed=seed)
    return c.in_bang("d15 lỗi giữa lần chạy (bất biến 5)", [
        ("lần chạy bị lỗi trả ok", kq["ok"]),
        ("mã lỗi", ", ".join(sorted({e["code"] for e in kq["errors"]}))),
        ("match_results và run_history giữ nguyên sau lỗi", truoc == sau),
        ("chạy lại sau đó ok", lai["ok"]),
        ("run_history sau khi chạy lại", c.sql(db, "SELECT COUNT(*) FROM run_history")[0][0]),
    ])


if __name__ == "__main__":
    c.main(dien_tap, __doc__)
