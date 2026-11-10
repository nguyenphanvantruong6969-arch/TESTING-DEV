"""GAP-0: nhật ký điều chỉnh sau khi xếp (`fa_dieu_chinh`) và hàm thuần `vi_tri_hien_tai`.

Kết quả DA (`match_results`) không bao giờ bị sửa tại chỗ: chỗ hiện tại = kết quả lần chạy gốc + các dòng điều chỉnh
phát lại theo `id`. Dữ liệu là dữ liệu MÔ PHỎNG.
"""
import copy
import os
import sqlite3
import sys

import pytest

import fa_sau_xep as sx
from _fa import bat_fa, dung_fa_clb, dung_hs_fa
from rbda_priority_pipeline import di_tru_schema, init_db

KQ = {("s1", "thu_2"): "A", ("s2", "thu_2"): "B"}
RUN = {"thu_2": 1}


def _d(id_, kind, club_from=None, club_to=None, sid="s1", buoi="thu_2", run=1):
    return {"id": id_, "created_at": "2026-11-10 08:00:00", "run_id_base": run, "buoi": buoi,
            "student_id": sid, "club_from": club_from, "club_to": club_to, "kind": kind, "actor": "", "note": ""}


def test_khong_co_dieu_chinh_thi_giu_nguyen():
    vt, lech = sx.vi_tri_hien_tai(KQ, RUN, [])
    assert vt == KQ and lech == []


def test_giai_phong_roi_nhan_loi_moi():
    vt, lech = sx.vi_tri_hien_tai(KQ, RUN, [_d(1, "release", "A"), _d(2, "invite_accept", None, "B")])
    assert vt == {("s1", "thu_2"): "B", ("s2", "thu_2"): "B"} and lech == []


def test_phat_lai_theo_id_khong_theo_thu_tu_dua_vao():
    vt, lech = sx.vi_tri_hien_tai(KQ, RUN, [_d(2, "invite_accept", None, "B"), _d(1, "release", "A")])
    assert vt[("s1", "thu_2")] == "B" and lech == []


def test_club_from_khong_khop_thi_bo_qua_va_bao_lech():
    vt, lech = sx.vi_tri_hien_tai(KQ, RUN, [_d(1, "release", "C")])
    assert vt == KQ and lech == [{"id": 1, "ly_do": "khong_khop"}]


def test_hoc_sinh_khong_co_trong_ket_qua_la_khong_khop():
    vt, lech = sx.vi_tri_hien_tai(KQ, RUN, [_d(1, "release", "A", sid="s9")])
    assert vt == KQ and lech == [{"id": 1, "ly_do": "khong_khop"}]


def test_dieu_chinh_cua_lan_chay_cu_khong_ap_dung():
    vt, lech = sx.vi_tri_hien_tai(KQ, {"thu_2": 2}, [_d(1, "release", "A", run=1)])
    assert vt == KQ and lech == [{"id": 1, "ly_do": "run_cu"}]


@pytest.mark.parametrize("kind", ["invite_offer", "invite_decline", "invite_expire", "appeal_rerun"])
def test_loai_khong_doi_cho(kind):
    vt, lech = sx.vi_tri_hien_tai(KQ, RUN, [_d(1, kind, "A", "B")])
    assert vt == KQ and lech == []


def test_vong_2_doi_cho():
    kq = {("s1", "thu_2"): None}
    vt, _ = sx.vi_tri_hien_tai(kq, RUN, [_d(1, "round2", None, "C")])
    assert vt == {("s1", "thu_2"): "C"}


def test_khong_sua_dau_vao():
    kq, run, dc = copy.deepcopy(KQ), dict(RUN), [_d(2, "invite_accept", None, "B"), _d(1, "release", "A")]
    truoc = copy.deepcopy((kq, run, dc))
    sx.vi_tri_hien_tai(kq, run, dc)
    assert (kq, run, dc) == truoc


# ----------------------------------------------------------------------------- CSDL

def _bang(db):
    con = sqlite3.connect(db)
    try:
        return sorted(r[0] for r in con.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL"))
    finally:
        con.close()


def test_csdl_moi_co_bang_va_csdl_cu_duoc_nang(tmp_path):
    db = str(tmp_path / "cu.db")
    init_db(db)
    con = sqlite3.connect(db)
    con.execute("DROP TABLE fa_dieu_chinh")
    con.commit()
    con.close()
    assert "fa_dieu_chinh" not in " ".join(_bang(db))
    init_db(db)                                    # mở lại = nâng cấp
    assert any("fa_dieu_chinh" in s for s in _bang(db))
    truoc = _bang(db)
    assert di_tru_schema(db) == []                 # lần hai không làm gì
    assert _bang(db) == truoc


def test_ghi_dieu_chinh_tu_choi_loai_la_va_doc_vi_tri_ap_dung(api):
    bat_fa(api)
    dung_fa_clb(api, A=(5, "GIOI_HAN"), T=(9, "TU_DO"))
    dung_hs_fa(api, "s1", "s2", nv={"s1": ["A", "T"], "s2": ["A", "T"]})
    assert api.run_pipeline(seed=3)["ok"]
    with api._ket_noi_ghi() as cur:
        vt, lech, run_goc = sx.doc_vi_tri(cur)
        buoi = next(iter(run_goc))
        assert vt[("s1", buoi)] == "A"
        with pytest.raises(ValueError):
            sx.ghi_dieu_chinh(cur, run_goc[buoi], buoi, "s1", "A", None, "edit")
        i = sx.ghi_dieu_chinh(cur, run_goc[buoi], buoi, "s1", "A", None, "release", actor="t", note="n")
        assert isinstance(i, int)
    with api._ket_noi_doc() as cur:
        vt, lech, _ = sx.doc_vi_tri(cur)
        mr = cur.execute("SELECT club_id FROM match_results WHERE student_id='s1'").fetchone()[0]
    assert vt[("s1", buoi)] is None and lech == []
    assert mr == "A"                                # kết quả DA không bị sửa


def test_run_goc_theo_buoi_sau_khi_chay_lai_mot_buoi(api):
    bat_fa(api)
    dung_fa_clb(api, A=(3, "GIOI_HAN", None, None, None, "thu_2"), B=(3, "GIOI_HAN", None, None, None, "thu_3"),
                FA=(9, "TU_DO", None, None, None, "thu_2"), FB=(9, "TU_DO", None, None, None, "thu_3"))
    dung_hs_fa(api, "s1", "s2", nv={s: ["A", "FA", "B", "FB"] for s in ("s1", "s2")})
    assert api.run_pipeline(seed=3)["ok"]
    assert api.run_pipeline(seed=3, chi_buoi=["thu_2"])["ok"]
    with api._ket_noi_doc() as cur:
        r = [x[0] for x in cur.execute("SELECT run_id FROM run_history ORDER BY run_id")]
        assert sx.run_goc_theo_buoi(cur) == {"thu_2": r[-1], "thu_3": r[-2]}


def test_kiem_nhanh_canh_bang_dieu_chinh():
    goc = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(goc, ".claude", "skills", "soat-ma", "scripts"))
    import kiem_nhanh
    assert "fa_dieu_chinh" in kiem_nhanh.BANG_NHAT_KY
