# -*- coding: utf-8 -*-
"""FA-SC diễn tập T4 / S23: giáo viên chọn nhầm "vắng không phép" ở buổi 2 cho một em đang đi học, rồi sửa lại ngay.
Dữ liệu MÔ PHỎNG."""
import os

import chung as c

NGAY = "thu_2"


def _dem(db, kind):
    return c.sql(db, "SELECT COUNT(*) FROM fa_dieu_chinh WHERE kind = ?", (kind,))[0][0]


def dien_tap(ra, seed=c.SEED, so_hs=c.SO_HS):
    dot = c.sinh_dot(so_hs, seed)
    r = c.chay(dot, os.path.join(ra, "sach"), seed, luat={"fa_diem_danh": True})
    api, db = r["api"], r["db"]
    sid, clb = c.chon_em_trung_tuyen(dot, r, r["loai"], NGAY)
    truoc = (c.sql(db, "SELECT * FROM match_results ORDER BY student_id, buoi"),
             c.sql(db, "SELECT COUNT(*) FROM run_history")[0][0])
    b1 = api.luu_diem_danh(clb, sid, 1, "VANG_KHONG_PHEP")          # buổi 1: em ốm thật, giáo viên chưa biết
    b2 = api.luu_diem_danh(clb, sid, 2, "VANG_KHONG_PHEP")          # buổi 2: chọn nhầm ô
    moi_sau_nham = _dem(db, "invite_offer")
    sua = api.luu_diem_danh(clb, sid, 2, "CO_MAT")                  # sửa lại ngay
    sua1 = api.luu_diem_danh(clb, sid, 1, "VANG_CO_PHEP")           # và ghi buổi 1 có phép
    con = [x for x in c.sql(db, "SELECT kind, student_id, club_from, club_to FROM fa_dieu_chinh ORDER BY id")]
    import fa_sau_xep as sx
    with api._ket_noi_doc() as cur:
        vi_tri, _, _ = sx.doc_vi_tri(cur)
    sau = (c.sql(db, "SELECT * FROM match_results ORDER BY student_id, buoi"),
           c.sql(db, "SELECT COUNT(*) FROM run_history")[0][0])
    return c.in_bang("d08 T4/S23 điểm danh nhầm một ô", [
        ("mọi lần lưu đều ok (không hỏi xác nhận)", all(x["ok"] for x in (b1, b2, sua, sua1))),
        ("sau ô nhầm: đã giải phóng chỗ", b2["data"]["da_giai_phong"]),
        ("sau ô nhầm: số lời mời tự ghi cho em khác", moi_sau_nham),
        ("sau khi sửa cả hai ô: em còn chỗ ở CLB đó", vi_tri.get((sid, NGAY)) == clb),
        ("sau khi sửa: lời mời cho em khác còn hiệu lực", _dem(db, "invite_offer") - _dem(db, "invite_decline")
         - _dem(db, "invite_expire") - _dem(db, "invite_accept")),
        ("các dòng nhật ký điều chỉnh (loại)", ", ".join(x[0] for x in con)),
        ("match_results và run_history không đổi (bất biến 4)", truoc == sau),
    ])


if __name__ == "__main__":
    c.main(dien_tap, __doc__)
