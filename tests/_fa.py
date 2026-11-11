"""Trợ giúp dùng chung cho các test FA-DAA. Dữ liệu là dữ liệu MÔ PHỎNG."""

import cau_hinh_ws as ch


def bat_fa(api, bat=True):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": bat}})


def dung_fa_clb(api, **clb):
    """dung_fa_clb(api, A=(cho, "TUYEN_CHON", diem_san, toi_thieu, phong, buoi)); phần tử sau cho
    có thể bỏ. Giá trị chỉ là số `cho` -> CLB không có kiểu (NULL)."""
    for cid, gt in clb.items():
        gt = gt if isinstance(gt, tuple) else (gt,)
        cho, loai, san, toi, phong, buoi = (list(gt) + [None] * 6)[:6]
        assert api.create_or_update_club(cid, "CLB " + cid, cho, 0, "", buoi or "")["ok"]
        with api._ket_noi_ghi() as cur:
            cur.execute(
                "UPDATE clubs SET loai=?, diem_san=?, so_toi_thieu=?, suc_chua_phong=? "
                "WHERE club_id=?", (loai, san, toi, phong, cid))


def dung_hs_fa(api, *ds, nv=None):
    """Tạo học sinh; `nv` {sid: [clb…]} đặt nguyện vọng."""
    for sid in ds:
        assert api.create_student_if_missing(sid, "Em " + sid)["ok"]
    for sid, ds_clb in (nv or {}).items():
        assert api.submit_preferences(sid, ds_clb)["ok"]


def giu_cho(api, *cap):
    with api._ket_noi_ghi() as cur:
        cur.executemany("INSERT INTO giu_cho (club_id, student_id) VALUES (?, ?)", cap)


def ma(loi):
    return [e["code"] for e in loi]
