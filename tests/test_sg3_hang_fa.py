"""SG-3 (C2): ở chế độ FA, `match_results.rank_in_student_pref` là thứ hạng trong danh sách GỐC của em
(cùng giá trị với `rank_in_list` của fa_ly_do); em được xếp bằng bước dự phòng vào CLB Tự do mà em không
khai thì NULL (quyết định D3). Bảng điều khiển "Vào NV1" và bảng "Mức đáp ứng nguyện vọng" đọc giá trị đó.

Dữ liệu là dữ liệu MÔ PHỎNG dựng trong test.
"""

import pytest

from rbda_priority_pipeline import BUOI_MAC_DINH

from _fa import bat_fa, dung_fa_clb, dung_hs_fa


def _dung(api):
    """HS001: khai S (Tuyển chọn, không thi -> bị bỏ), G, T -> vào G, thứ hạng gốc 2 (không phải 1).
    HS002: chỉ khai S (bị bỏ) -> dự phòng vào T, em không khai T -> NULL.
    HS003: khai G -> vào G, thứ hạng 1. HS004: không khai gì -> dự phòng vào T, NULL.
    HS005: thi S đạt -> vào S, thứ hạng 1."""
    bat_fa(api)
    dung_fa_clb(api, S=(5, "TUYEN_CHON", 5), G=(5, "GIOI_HAN"), T=(5, "TU_DO"))
    dung_hs_fa(api, "HS001", "HS002", "HS003", "HS004", "HS005",
               nv={"HS001": ["S", "G", "T"], "HS002": ["S"], "HS003": ["G"], "HS005": ["S"]})
    # HS005 thi S được 9 điểm (để CLB S có điểm, qua chốt kiểm trước); HS001/HS002 không thi S
    assert api.submit_test_selection("HS005", ["S"])["ok"]
    assert api.submit_club_scores("S", [{"student_id": "HS005", "score": 9}])["ok"]
    return api


def _hang(api):
    with api._ket_noi_doc() as cur:
        return {r[0]: (r[1], r[2]) for r in cur.execute(
            "SELECT student_id, club_id, rank_in_student_pref FROM match_results")}


def test_hs001_hang_theo_danh_sach_goc(api):
    _dung(api)
    assert api.run_pipeline(seed=7)["ok"]
    cid, hang = _hang(api)["HS001"]
    assert cid == "G"
    assert hang == 2                                   # S bị bỏ nhưng vẫn chiếm vị trí 1 trong danh sách gốc


def test_hang_giong_rank_in_list_cua_ly_do(api):
    _dung(api)
    assert api.run_pipeline(seed=7)["ok"]
    with api._ket_noi_doc() as cur:
        ly_do = {r[0]: r[1] for r in cur.execute(
            "SELECT student_id, rank_in_list FROM fa_ly_do WHERE outcome = 'ACCEPTED'")}
    mr = _hang(api)
    assert ly_do and all(mr[s][1] == h for s, h in ly_do.items())


def test_hs002_du_phong_khong_khai_thi_null(api):
    _dung(api)
    assert api.run_pipeline(seed=7)["ok"]
    mr = _hang(api)
    assert mr["HS002"] == ("T", None)
    assert mr["HS004"] == ("T", None)                  # không khai gì cũng NULL (trước đây là 1)


def _dem_truc_tiep(api):
    """Đếm trực tiếp trên `preferences`: CLB đầu tiên của buổi trong danh sách gốc == CLB được xếp."""
    with api._ket_noi_doc() as cur:
        mr = cur.execute("SELECT student_id, buoi, club_id FROM match_results "
                         "WHERE club_id IS NOT NULL").fetchall()
        dau = {}
        for sid, cid, buoi in cur.execute(
                "SELECT p.student_id, p.club_id, COALESCE(NULLIF(c.buoi,''), ?) FROM preferences p "
                "JOIN clubs c ON c.club_id = p.club_id ORDER BY p.student_id, p.rank",
                (BUOI_MAC_DINH,)):
            dau.setdefault((sid, buoi), cid)
    nv1 = sum(1 for sid, buoi, cid in mr if dau.get((sid, buoi)) == cid)
    return nv1, len(mr)


def test_dashboard_nv1_bang_dem_truc_tiep(api):
    _dung(api)
    assert api.run_pipeline(seed=7)["ok"]
    nv1, tong = _dem_truc_tiep(api)
    d = api.get_dashboard()["data"]
    ty_le = next(c["gia_tri"] for c in d["chi_so"] if c["ma"] == "ty_le_nv1")
    assert nv1 == 2                                    # HS003, HS005 (HS001 vào G là NV2)
    assert ty_le == pytest.approx(nv1 / tong)


def test_bang_muc_dap_ung_tach_du_phong(api):
    _dung(api)
    assert api.run_pipeline(seed=7)["ok"]
    d = api.get_phan_bo_nguyen_vong()["data"]
    so = {h["hang"]: h["so_em"] for h in d["phan_bo"] if not h["gop"]}
    assert so[1] == 2 and so[2] == 1                   # HS003, HS005; HS001
    assert d["ngoai_danh_sach"] == 2                   # HS002, HS004: dự phòng, không tính là NV nào
    assert d["khong_ro"] == 0
    assert d["tong_da_xep"] == 5
