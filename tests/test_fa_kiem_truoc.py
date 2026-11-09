"""FA-2 (A5, FA-DAA): kiểm trước khi chạy — `kiem_truoc_fa`, nối vào pipeline và báo cáo sức khoẻ.

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.
Một test cho mỗi luật chặn; pipeline từ chối chạy và KHÔNG ghi gì (không vẽ số, không run_history).
"""

import pytest

import fa_daa
from _fa import bat_fa, dung_fa_clb, dung_hs_fa, giu_cho, ma


def _c(buoi="b1", cho=5, loai="GIOI_HAN", san=None, toi=None, phong=None):
    return {"buoi": buoi, "capacity": cho, "loai": loai, "diem_san": san,
            "so_toi_thieu": toi, "suc_chua_phong": phong}


HOP_LE = {"T": _c(loai="TU_DO", cho=50), "G": _c(), "S": _c(loai="TUYEN_CHON", san=5)}


def test_hop_le_khong_loi():
    assert fa_daa.kiem_truoc_fa(HOP_LE, [], {}) == []


def test_moi_buoi_can_clb_tu_do():
    clubs = {"T1": _c("b1", 50, "TU_DO"), "G2": _c("b2")}
    loi = fa_daa.kiem_truoc_fa(clubs, [], {})
    assert ma(loi) == ["fa_thieu_clb_tu_do"]
    assert loi[0]["params"]["buoi"] == "b2"


def test_moi_clb_can_loai():
    clubs = {**HOP_LE, "X": _c(loai=None)}
    loi = fa_daa.kiem_truoc_fa(clubs, [], {})
    assert ma(loi) == ["fa_clb_thieu_loai"] and loi[0]["params"]["club_id"] == "X"


@pytest.mark.parametrize("loai", ["GIOI_HAN", "TUYEN_CHON"])
def test_gioi_han_va_tuyen_chon_can_suc_chua(loai):
    clubs = {"T": _c(loai="TU_DO", cho=50), "X": _c(cho=None, loai=loai, san=5)}
    assert ma(fa_daa.kiem_truoc_fa(clubs, [], {})) == ["fa_clb_thieu_suc_chua"]
    clubs["X"]["capacity"] = 0
    assert ma(fa_daa.kiem_truoc_fa(clubs, [], {})) == ["fa_clb_thieu_suc_chua"]


def test_tuyen_chon_can_diem_san():
    clubs = {**HOP_LE, "S": _c(loai="TUYEN_CHON", san=None)}
    loi = fa_daa.kiem_truoc_fa(clubs, [], {})
    assert ma(loi) == ["fa_clb_thieu_diem_san"] and loi[0]["params"]["club_id"] == "S"


def test_tu_do_khong_can_suc_chua_hay_diem_san():
    clubs = {"T": _c(loai="TU_DO", cho=None)}
    assert fa_daa.kiem_truoc_fa(clubs, [], {}) == []


def test_giu_cho_vuot_suc_chua():
    clubs = {**HOP_LE, "G": _c(cho=2)}
    hs = {s: {} for s in ("s1", "s2", "s3")}
    prefs = {s: ["G"] for s in hs}
    loi = fa_daa.kiem_truoc_fa(clubs, [("G", s) for s in hs], hs, prefs)
    assert ma(loi) == ["fa_giu_cho_vuot_suc_chua"]
    assert loi[0]["params"]["n"] == 3 and loi[0]["params"]["suc_chua"] == 2
    ok = fa_daa.kiem_truoc_fa(clubs, [("G", "s1"), ("G", "s2")], hs, prefs)
    assert ok == []


def test_giu_cho_hoc_sinh_la_la_canh_bao_khong_tinh():
    clubs = {**HOP_LE, "G": _c(cho=1)}
    loi = fa_daa.kiem_truoc_fa(clubs, [("G", "ghost"), ("G", "s1")], {"s1": {}}, {"s1": ["G"]})
    assert ma(loi) == ["fa_giu_cho_hoc_sinh_la"]           # ghost không tính -> 1 <= 1, không vượt
    assert fa_daa.chi_loi_chan(loi) == []


def test_giu_cho_khong_xep_clb_la_canh_bao_khong_tinh():
    clubs = {**HOP_LE, "G": _c(cho=1)}
    hs = {"s1": {}, "s2": {}}
    loi = fa_daa.kiem_truoc_fa(clubs, [("G", "s1"), ("G", "s2")], hs, {"s1": ["G"], "s2": ["S"]})
    assert ma(loi) == ["fa_giu_cho_khong_xep_clb"]
    assert loi[0]["params"]["student_id"] == "s2"
    assert fa_daa.chi_loi_chan(loi) == []
    assert fa_daa.giu_cho_hop_le(clubs, [("G", "s1"), ("G", "s2")], hs, {"s1": ["G"], "s2": ["S"]}
                                 ) == {("G", "s1")}


def test_thu_tu_loi_co_dinh():
    clubs = {"B": _c("b2", loai=None), "A": _c("b1", loai=None)}
    a = ma(fa_daa.kiem_truoc_fa(clubs, [], {}))
    b = ma(fa_daa.kiem_truoc_fa(dict(reversed(list(clubs.items()))), [], {}))
    assert a == b


# --------------------------------------------------------------- nối vào pipeline và sức khoẻ

def _dung(api, **kw):
    bat_fa(api)
    dung_fa_clb(api, T=(50, "TU_DO"), G=(2, "GIOI_HAN"), **kw)
    dung_hs_fa(api, "s1", "s2", nv={"s1": ["G", "T"], "s2": ["G", "T"]})


def _dem(api, bang):
    with api._ket_noi_doc() as cur:
        return cur.execute("SELECT COUNT(*) FROM %s" % bang).fetchone()[0]


def test_pipeline_tu_choi_va_khong_ghi_gi(api):
    _dung(api)
    dung_fa_clb(api, X=(3, None))            # thiếu loại
    kq = api.run_pipeline(seed=7)
    assert not kq["ok"]
    assert "fa_clb_thieu_loai" in ma(kq["errors"])
    assert _dem(api, "run_history") == 0 and _dem(api, "match_results") == 0
    with api._ket_noi_doc() as cur:
        khoa = cur.execute("SELECT is_locked FROM stb_lock WHERE id = 1").fetchone()
        assert not khoa or not khoa[0]
        assert cur.execute("SELECT COUNT(*) FROM students WHERE stb_number IS NOT NULL"
                           ).fetchone()[0] == 0


def test_pipeline_giu_cho_vuot_bi_chan(api):
    _dung(api)
    dung_hs_fa(api, "s3", nv={"s3": ["G", "T"]})
    giu_cho(api, ("G", "s1"), ("G", "s2"), ("G", "s3"))
    kq = api.run_pipeline(seed=7)
    assert not kq["ok"] and "fa_giu_cho_vuot_suc_chua" in ma(kq["errors"])
    assert _dem(api, "run_history") == 0


def test_bao_cao_suc_khoe_co_loi_fa(api):
    _dung(api)
    dung_fa_clb(api, X=(3, None))
    kq = api.get_data_health_report()
    assert kq["ok"], kq
    codes = ma(kq["data"]["warnings"])
    assert "fa_clb_thieu_loai" in codes
    muc = next(w for w in kq["data"]["warnings"] if w["code"] == "fa_clb_thieu_loai")
    assert muc["severity"] == "high"


def test_fa_tat_khong_kiem_gi(api):
    # FA tắt: thiếu loại là chuyện bình thường (hành vi cũ)
    dung_fa_clb(api, X=(3, None))
    kq = api.get_data_health_report()
    assert not [c for c in ma(kq["data"]["warnings"]) if c.startswith("fa_")]
