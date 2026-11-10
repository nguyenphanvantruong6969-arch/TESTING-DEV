"""GAP-2: chỗ được giải phóng -> mời học sinh đầu danh sách chờ (D4: Tuyển chọn điểm→huy chương→bốc thăm, Giới hạn
huy chương→bốc thăm; chỉ em thua ở CLB đó và xếp CLB đó cao hơn CLB hiện tại). Mỗi bước là một dòng `fa_dieu_chinh`;
`match_results` và `run_history` không đổi. Dữ liệu là dữ liệu MÔ PHỎNG.
"""
import fa_sau_xep as sx
from _fa import ma
from test_fa_gap1_diem_danh import _anh_chup, _dung, _thanh_vien


def _cho(api):
    """Danh sách chờ G của lần chạy: [student_id theo waitlist_pos]."""
    with api._ket_noi_doc() as cur:
        return [r[0] for r in cur.execute(
            "SELECT student_id FROM fa_ly_do WHERE club_id='G' AND outcome='REJECTED' ORDER BY waitlist_pos")]


def _moi(api, kind="invite_offer"):
    with api._ket_noi_doc() as cur:
        return [dict(zip(("id", "student_id", "club_from", "club_to"), r)) for r in cur.execute(
            "SELECT id, student_id, club_from, club_to FROM fa_dieu_chinh WHERE kind=? ORDER BY id", (kind,))]


def _giai_phong_mot_em_g(api):
    em = _thanh_vien(api, "G")[0]
    api.luu_diem_danh("G", em, 1, "VANG_KHONG_PHEP")
    assert api.luu_diem_danh("G", em, 2, "VANG_KHONG_PHEP")["data"]["da_giai_phong"]
    return em


def test_giai_phong_thi_moi_dung_mot_em_dau_danh_sach_cho(api):
    _dung(api)
    cho = _cho(api)
    assert len(cho) == 2
    _giai_phong_mot_em_g(api)
    moi = _moi(api)
    assert [m["student_id"] for m in moi] == [cho[0]]
    assert moi[0]["club_to"] == "G" and moi[0]["club_from"] == "T"
    d = api.get_moi_cho_trong()["data"]
    assert d["bat"] is True and [(m["student_id"], m["trang_thai"]) for m in d["moi"]] == [(cho[0], "CHO")]


def test_nhan_thi_doi_cho_va_khong_moi_cho_clb_tu_do(api):
    _dung(api)
    truoc = _anh_chup(api)
    cho = _cho(api)
    _giai_phong_mot_em_g(api)
    id_moi = _moi(api)[0]["id"]
    ra = api.tra_loi_moi(id_moi, "nhan")
    assert ra["ok"], ra
    assert cho[0] in _thanh_vien(api, "G") and cho[0] not in _thanh_vien(api, "T")
    assert len(_moi(api)) == 1                                   # T là Tự do: không mời ai
    assert _moi(api, "invite_accept")[0]["student_id"] == cho[0]
    assert api.get_moi_cho_trong()["data"]["moi"][0]["trang_thai"] == "NHAN"
    assert _anh_chup(api) == truoc                               # match_results + run_history không đổi


def test_tu_choi_thi_moi_em_ke_tiep_het_han_thi_het_nguoi(api):
    _dung(api)
    cho = _cho(api)
    _giai_phong_mot_em_g(api)
    assert api.tra_loi_moi(_moi(api)[0]["id"], "tu_choi")["ok"]
    moi = _moi(api)
    assert [m["student_id"] for m in moi] == cho
    assert api.tra_loi_moi(moi[1]["id"], "het_han")["ok"]
    assert len(_moi(api)) == 2                                   # không còn ai trong danh sách chờ
    tt = {m["student_id"]: m["trang_thai"] for m in api.get_moi_cho_trong()["data"]["moi"]}
    assert tt == {cho[0]: "TU_CHOI", cho[1]: "HET_HAN"}


def test_tra_loi_loi_moi_khong_con_cho_va_gia_tri_la(api):
    _dung(api)
    _giai_phong_mot_em_g(api)
    i = _moi(api)[0]["id"]
    assert ma(api.tra_loi_moi(i, "co")["errors"]) == ["diem_danh_gia_tri_sai"]
    assert api.tra_loi_moi(i, "nhan")["ok"]
    assert ma(api.tra_loi_moi(i, "tu_choi")["errors"]) == ["moi_khong_con_cho"]
    assert ma(api.tra_loi_moi(99999, "nhan")["errors"]) == ["moi_khong_con_cho"]


def test_co_tat_thi_khong_co_loi_moi(api):
    _dung(api, diem_danh=False)
    assert api.get_moi_cho_trong() == {"ok": True, "data": {"bat": False}, "errors": []}
    assert ma(api.tra_loi_moi(1, "nhan")["errors"]) == ["fa_diem_danh_chua_bat"]


# ----------------------------------------------------------------------------- hàm thuần hang_cho

def _ld(sid, cid, outcome, rank, pos=None, buoi="b", run=1):
    return {"run_id": run, "buoi": buoi, "student_id": sid, "club_id": cid, "outcome": outcome,
            "rank_in_list": rank, "waitlist_pos": pos}


def _dc(id_, kind, sid, club_from, club_to, buoi="b", run=1):
    return {"id": id_, "created_at": "", "run_id_base": run, "buoi": buoi, "student_id": sid,
            "club_from": club_from, "club_to": club_to, "kind": kind, "actor": "", "note": ""}


RUN = {"b": 1}
LD = [_ld("a", "S", "REJECTED", 1, 2), _ld("a", "L", "REJECTED", 2, 1), _ld("a", "T", "ACCEPTED", 3),
      _ld("c", "S", "REJECTED", 1, 1), _ld("c", "T", "ACCEPTED", 2),
      _ld("m", "S", "ACCEPTED", 1), _ld("n", "L", "ACCEPTED", 1)]
VT = {("a", "b"): "T", ("c", "b"): "T", ("m", "b"): "S", ("n", "b"): "L"}


def test_hang_cho_theo_waitlist_pos_clb_tuyen_chon():
    assert sx.hang_cho(LD, VT, RUN, [], "b", "S") == ["c", "a"]


def test_hang_cho_bo_em_da_vao_clb_cao_hon():
    vt = dict(VT)
    vt[("a", "b")] = "S"                                          # a đã vào S (hạng 1) qua một lời mời trước
    dc = [_dc(1, "invite_offer", "a", "T", "S"), _dc(2, "invite_accept", "a", "T", "S")]
    assert sx.hang_cho(LD, vt, RUN, dc, "b", "L") == []           # L (hạng 2) thấp hơn S: không mời a


def test_hang_cho_bo_em_dang_co_loi_moi_hoac_da_tu_choi():
    dc = [_dc(1, "invite_offer", "c", "T", "S")]
    assert sx.hang_cho(LD, VT, RUN, dc, "b", "S") == ["a"]        # c đang có lời mời
    dc += [_dc(2, "invite_decline", "c", "T", "S")]
    assert sx.hang_cho(LD, VT, RUN, dc, "b", "S") == ["a"]        # c đã từ chối S
    assert sx.hang_cho(LD, VT, {"b": 2}, [], "b", "S") == []      # dòng lý do của lần chạy khác


def test_moi_dang_cho_thuan():
    dc = [_dc(1, "invite_offer", "c", "T", "S"), _dc(2, "invite_offer", "a", "T", "L"),
          _dc(3, "invite_accept", "a", "T", "L")]
    assert set(sx.moi_dang_cho(dc, RUN)) == {1}
