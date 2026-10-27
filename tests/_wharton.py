"""Trợ giúp dùng chung cho các test điểm Wharton (A13, vòng 2). Dữ liệu là dữ liệu MÔ PHỎNG."""

import cau_hinh_ws as ch


def bat_wharton(api, bat=True, **luat):
    """Bật (hoặc tắt) `rules.wharton` của workspace đang mở bằng `api`."""
    ch.ghi_cau_hinh(api.db_path, {"rules": {"wharton": bat, **luat}})


def dong_bids(api):
    """[(student_id, club_id, tier, points)] sắp theo mã."""
    with api._ket_noi_doc() as cur:
        return [tuple(r) for r in cur.execute(
            "SELECT student_id, club_id, tier, points FROM wharton_bids "
            "ORDER BY student_id, club_id")]


def chen_bids(api, dong):
    with api._ket_noi_ghi() as cur:
        cur.executemany(
            "INSERT INTO wharton_bids (student_id, club_id, tier, points) VALUES (?, ?, ?, ?)",
            dong)


def ma_loi(ket_qua):
    """Danh sách mã trong `warnings` của một phản hồi nạp."""
    return [w["code"] for w in ket_qua["data"]["warnings"]]


def canh_bao(ket_qua, ma):
    return [w for w in ket_qua["data"]["warnings"] if w["code"] == ma]


def dung_clb(api, **clb):
    """dung_clb(api, A=5, B=5): tạo CLB không buổi; giá trị (cho, buoi) để đặt buổi."""
    for cid, gt in clb.items():
        cho, buoi = gt if isinstance(gt, tuple) else (gt, "")
        assert api.create_or_update_club(cid, "CLB " + cid, cho, 0, "", buoi)["ok"]


def dung_hs(api, *ds, tick=None):
    """Tạo học sinh; `tick` {sid: [clb]} đặt ô tick thi."""
    for sid in ds:
        assert api.create_student_if_missing(sid, "Em " + sid)["ok"]
    for sid, clbs in (tick or {}).items():
        assert api.submit_test_selection(sid, clbs)["ok"]
