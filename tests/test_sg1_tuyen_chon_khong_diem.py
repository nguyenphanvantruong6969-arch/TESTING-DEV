"""SG-1 (C3): CLB Tuyển chọn có người đăng ký nhưng KHÔNG ai có điểm -> chặn chạy, báo mã
`fa_clb_tuyen_chon_chua_co_diem` {club_id, so_dang_ky, so_nv1}.

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test. Không FA: không thêm lỗi mới.
"""

import fa_daa
from _fa import bat_fa, dung_fa_clb, dung_hs_fa, ma

MA_MOI = "fa_clb_tuyen_chon_chua_co_diem"


def _c(loai="GIOI_HAN", cho=5, san=None):
    return {"buoi": "b1", "capacity": cho, "loai": loai, "diem_san": san,
            "so_toi_thieu": None, "suc_chua_phong": None}


def test_ham_thuan_chan_khi_khong_ai_co_diem():
    clubs = {"T": _c("TU_DO", 50), "S": _c("TUYEN_CHON", 3, san=5)}
    hs = {s: {} for s in ("s1", "s2", "s3")}
    prefs = {"s1": ["S", "T"], "s2": ["S", "T"], "s3": ["T", "S"]}
    loi = fa_daa.kiem_truoc_fa(clubs, [], hs, prefs, tested_scores={})
    assert ma(loi) == [MA_MOI]
    assert loi[0]["params"] == {"club_id": "S", "so_dang_ky": 3, "so_nv1": 2}
    assert MA_MOI not in fa_daa.MA_CANH_BAO                   # lỗi CHẶN
    assert fa_daa.chi_loi_chan(loi) == loi


def test_ham_thuan_hai_buoi_nv1_tinh_theo_buoi():
    # SG-1 FIX-1: nguyện vọng 1 là CLB đầu tiên TRONG BUỔI của nó, không phải đầu danh sách chung.
    clubs = {"A": {**_c("TU_DO", 50), "buoi": "b1"},
             "S": {**_c("TUYEN_CHON", 3, san=5), "buoi": "b2"},
             "B": {**_c("TU_DO", 50), "buoi": "b2"}}
    hs = {s: {} for s in ("s1", "s2")}
    prefs = {"s1": ["A", "S"], "s2": ["A", "S"]}
    loi = fa_daa.kiem_truoc_fa(clubs, [], hs, prefs, tested_scores={})
    assert ma(loi) == [MA_MOI]
    assert loi[0]["params"] == {"club_id": "S", "so_dang_ky": 2, "so_nv1": 2}


def test_ham_thuan_co_mot_diem_thi_khong_chan():
    clubs = {"T": _c("TU_DO", 50), "S": _c("TUYEN_CHON", 3, san=5)}
    hs = {s: {} for s in ("s1", "s2")}
    prefs = {"s1": ["S", "T"], "s2": ["S", "T"]}
    assert fa_daa.kiem_truoc_fa(clubs, [], hs, prefs, tested_scores={"S": {"s1": 0}}) == []


def test_ham_thuan_khong_ai_dang_ky_thi_khong_chan():
    clubs = {"T": _c("TU_DO", 50), "S": _c("TUYEN_CHON", 3, san=5)}
    hs = {"s1": {}}
    assert fa_daa.kiem_truoc_fa(clubs, [], hs, {"s1": ["T"]}, tested_scores={}) == []


def test_ham_thuan_mac_dinh_khong_them_loi():
    clubs = {"T": _c("TU_DO", 50), "S": _c("TUYEN_CHON", 3, san=5)}
    prefs = {"s1": ["S", "T"]}
    assert fa_daa.kiem_truoc_fa(clubs, [], {"s1": {}}, prefs) == []


def _dung(api, co_diem):
    bat_fa(api)
    dung_fa_clb(api, T=(50, "TU_DO"), G=(2, "GIOI_HAN"), V=(3, "TUYEN_CHON", 5))
    dung_hs_fa(api, "s1", "s2", "s3",
               nv={"s1": ["V", "G", "T"], "s2": ["V", "T"], "s3": ["G", "V", "T"]})
    if co_diem:
        assert api.submit_test_selection("s1", ["V"])["ok"]
        assert api.submit_club_scores("V", [{"student_id": "s1", "score": 9}])["ok"]


def _dem(api, bang):
    with api._ket_noi_doc() as cur:
        return cur.execute("SELECT COUNT(*) FROM %s" % bang).fetchone()[0]


def test_pipeline_bi_chan_va_khong_ghi_gi(api):
    _dung(api, co_diem=False)
    kq = api.run_pipeline(seed=5)
    assert not kq["ok"]
    loi = [e for e in kq["errors"] if e["code"] == MA_MOI]
    assert len(loi) == 1
    assert loi[0]["params"] == {"club_id": "V", "so_dang_ky": 3, "so_nv1": 2}
    assert _dem(api, "run_history") == 0 and _dem(api, "match_results") == 0


def test_bao_cao_suc_khoe_bao_muc_cao(api):
    _dung(api, co_diem=False)
    kq = api.get_data_health_report()
    assert kq["ok"], kq
    muc = [w for w in kq["data"]["warnings"] if w["code"] == MA_MOI]
    assert len(muc) == 1 and muc[0]["severity"] == "high"
    assert muc[0]["params"]["so_nv1"] == 2


def test_pipeline_co_mot_diem_thi_chay_duoc(api):
    _dung(api, co_diem=True)
    kq = api.run_pipeline(seed=5)
    assert kq["ok"], kq["errors"]


def test_khong_fa_khong_co_loi_moi(api):
    dung_fa_clb(api, V=(3, "TUYEN_CHON", 5))
    dung_hs_fa(api, "s1", nv={"s1": ["V"]})
    kq = api.get_data_health_report()
    assert MA_MOI not in ma(kq["data"]["warnings"])
