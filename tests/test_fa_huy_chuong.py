"""FA-3 (A13, FA-DAA): huy chương MỘT quỹ — `kiem_ho_so_huy_chuong`, `diem_huy_chuong_hieu_luc`,
`submit_huy_chuong`, và chặn chạy khi hồ sơ huy chương sai.

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.
Tiêu chí V§13.8: mỗi CLB nhận tối đa một huy chương từ một học sinh, mỗi học sinh tối đa 3 huy
chương mỗi ngày. Bất biến 2: hoán vị thứ tự nguyện vọng khi huy chương cố định không đổi thứ tự
ưu tiên của CLB nào.
"""

import itertools

import fa_daa
import rbda_priority_pipeline as rp
from _fa import bat_fa, dung_fa_clb, dung_hs_fa, ma

CLUBS = {
    "T1": {"buoi": "b1", "loai": "TU_DO", "capacity": 50},
    "G1": {"buoi": "b1", "loai": "GIOI_HAN", "capacity": 3},
    "S1": {"buoi": "b1", "loai": "TUYEN_CHON", "capacity": 3, "diem_san": 5},
    "H1": {"buoi": "b1", "loai": "GIOI_HAN", "capacity": 3},
    "T2": {"buoi": "b2", "loai": "TU_DO", "capacity": 50},
    "G2": {"buoi": "b2", "loai": "GIOI_HAN", "capacity": 3},
}
PREFS = {"s1": ["G1", "S1", "H1", "T1", "G2", "T2"]}


def _kiem(bids, prefs=None):
    return fa_daa.kiem_ho_so_huy_chuong(prefs or PREFS, bids, CLUBS)


def test_hop_le_ba_mot_hai_va_khong_huy_chuong():
    assert _kiem({"s1": {"G1": 60, "S1": 30, "H1": 10, "G2": 60}}) == []
    assert _kiem({"s1": {"G1": 30}}) == []
    assert _kiem({"s1": {}}) == []
    assert _kiem({}) == []


def test_gia_tri_ngoai_60_30_10():
    for xau in (50, 0, 100, 5, 20, -60, 60.0, True, "60", None):
        loi = _kiem({"s1": {"G1": xau}})
        assert ma(loi) == ["fa_huy_chuong_gia_tri_sai"], xau
        assert loi[0]["params"]["club_id"] == "G1"


def test_trung_gia_tri_trong_mot_ngay_nhung_khac_ngay_thi_duoc():
    loi = _kiem({"s1": {"G1": 60, "S1": 60}})
    assert ma(loi) == ["fa_huy_chuong_trung_gia_tri"]
    assert loi[0]["params"]["gia_tri"] == 60 and loi[0]["params"]["buoi"] == "b1"
    assert _kiem({"s1": {"G1": 60, "G2": 60}}) == []


def test_clb_ngoai_nguyen_vong_bi_loi():
    loi = _kiem({"s1": {"G1": 60}}, prefs={"s1": ["S1", "T1"]})
    assert ma(loi) == ["fa_huy_chuong_ngoai_nguyen_vong"]


def test_clb_tu_do_khong_nhan_huy_chuong():
    loi = _kiem({"s1": {"T1": 60}})
    assert ma(loi) == ["fa_huy_chuong_clb_tu_do"]


def test_hoc_sinh_khong_co_nguyen_vong_van_bi_kiem():
    loi = _kiem({"ghost": {"G1": 60}}, prefs={})
    assert ma(loi) == ["fa_huy_chuong_ngoai_nguyen_vong"]


def test_thu_tu_loi_co_dinh():
    bids = {"s2": {"G1": 50}, "s1": {"G1": 40}}
    prefs = {"s1": ["G1"], "s2": ["G1"]}
    a = _kiem(bids, prefs)
    b = _kiem(dict(reversed(list(bids.items()))), prefs)
    assert a == b and [e["params"]["student_id"] for e in a] == ["s1", "s2"]


# ----------------------------------------------------------- điểm hiệu lực: một quỹ


def test_diem_hieu_luc_mot_quy_bo_qua_tier():
    hl = fa_daa.diem_huy_chuong_hieu_luc(PREFS, {"s1": {"G1": 60, "S1": 30}})
    assert hl["G1"]["s1"] == 60 and hl["S1"]["s1"] == 30
    assert hl["H1"]["s1"] == 0 and hl["T1"]["s1"] == 0       # có trong nguyện vọng, chưa huy chương


def test_diem_hieu_luc_khong_phu_thuoc_thu_tu_nguyen_vong():
    bids = {"s1": {"G1": 60, "S1": 30, "H1": 10}}
    goc = fa_daa.diem_huy_chuong_hieu_luc(PREFS, bids)
    for hv in itertools.permutations(PREFS["s1"]):
        assert fa_daa.diem_huy_chuong_hieu_luc({"s1": list(hv)}, bids) == goc


def test_thu_tu_uu_tien_khong_doi_khi_hoan_vi_nguyen_vong():
    # nhiều học sinh cùng nộp vào G1; hoán vị danh sách của một em không đổi thứ tự của G1
    bids = {"a": {"G1": 10}, "b": {"G1": 60}, "c": {"G1": 30}}
    stb = {"a": 1, "b": 3, "c": 2}

    def thu_tu(pa):
        prefs = {"a": pa, "b": ["G1", "H1"], "c": ["H1", "G1"]}
        hl = fa_daa.diem_huy_chuong_hieu_luc(prefs, bids)
        return rp.uu_tien_wharton("G1", ["a", "b", "c"], {}, stb, hl["G1"])

    goc = thu_tu(["G1", "H1", "T1"])
    assert goc == ["b", "c", "a"]                      # huy chương 60 > 30 > 10, không do STB
    assert all(thu_tu(list(p)) == goc for p in itertools.permutations(["G1", "H1", "T1"]))


def test_huy_chuong_60_khong_thang_diem_cao_hon_o_tuyen_chon():
    bids = {"a": {"S1": 60}, "b": {"S1": 10}}
    hl = fa_daa.diem_huy_chuong_hieu_luc({"a": ["S1"], "b": ["S1"]}, bids)
    diem = {"a": 6.0, "b": 8.0}
    assert rp.uu_tien_wharton("S1", ["a", "b"], diem, {"a": 1, "b": 2}, hl["S1"]) == ["b", "a"]
    # cùng điểm: huy chương quyết định
    diem = {"a": 7.0, "b": 7.0}
    assert rp.uu_tien_wharton("S1", ["a", "b"], diem, {"a": 2, "b": 1}, hl["S1"]) == ["a", "b"]


def test_gioi_han_xep_theo_huy_chuong_roi_boc_tham():
    bids = {"a": {"G1": 30}, "b": {"G1": 30}, "c": {}}
    hl = fa_daa.diem_huy_chuong_hieu_luc({s: ["G1"] for s in "abc"}, bids)
    ds = rp.uu_tien_wharton("G1", ["a", "b", "c"], {}, {"a": 3, "b": 1, "c": 2}, hl["G1"])
    assert ds == ["b", "a", "c"]


# ----------------------------------------------------------- API và pipeline


def _dung(api):
    bat_fa(api)
    dung_fa_clb(api, T=(50, "TU_DO"), G=(2, "GIOI_HAN"), S=(2, "TUYEN_CHON", 5), H=(2, "GIOI_HAN"))
    dung_hs_fa(api, "s1", "s2", nv={"s1": ["G", "S", "H", "T"], "s2": ["G", "T"]})


def _bids(api):
    with api._ket_noi_doc() as cur:
        return [tuple(r) for r in cur.execute(
            "SELECT student_id, club_id, points FROM wharton_bids ORDER BY student_id, club_id")]


def test_submit_huy_chuong_ghi_va_thay_the(api):
    _dung(api)
    kq = api.submit_huy_chuong("s1", {"G": 60, "S": 30, "H": 10})
    assert kq["ok"], kq
    assert _bids(api) == [("s1", "G", 60), ("s1", "H", 10), ("s1", "S", 30)]
    assert api.submit_huy_chuong("s1", {"S": 60})["ok"]                 # thay thế, không cộng dồn
    assert _bids(api) == [("s1", "S", 60)]
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM wharton_nhat_ky").fetchone()[0] == 2


def test_submit_huy_chuong_sai_khong_ghi_gi(api):
    _dung(api)
    assert api.submit_huy_chuong("s1", {"G": 60})["ok"]
    for xau, ma_loi in (({"G": 50}, "fa_huy_chuong_gia_tri_sai"),
                        ({"G": 60, "S": 60}, "fa_huy_chuong_trung_gia_tri"),
                        ({"T": 60}, "fa_huy_chuong_clb_tu_do"),
                        ({"nope": 60}, "fa_huy_chuong_ngoai_nguyen_vong")):
        kq = api.submit_huy_chuong("s1", xau)
        assert not kq["ok"] and ma_loi in ma(kq["errors"]), (xau, kq)
    assert _bids(api) == [("s1", "G", 60)]


def test_submit_huy_chuong_can_fa_bat(api):
    dung_fa_clb(api, G=(2, "GIOI_HAN"))
    dung_hs_fa(api, "s1", nv={"s1": ["G"]})
    kq = api.submit_huy_chuong("s1", {"G": 60})
    assert not kq["ok"] and ma(kq["errors"]) == ["fa_chua_bat"]
    assert _bids(api) == []


def test_submit_huy_chuong_hoc_sinh_la(api):
    _dung(api)
    kq = api.submit_huy_chuong("ghost", {"G": 60})
    assert not kq["ok"] and ma(kq["errors"]) == ["student_not_found"]


def test_submit_huy_chuong_bi_khoa(api):
    _dung(api)
    with api._ket_noi_ghi() as cur:
        cur.execute("INSERT OR REPLACE INTO wharton_lock (id, is_locked, locked_at) "
                    "VALUES (1, 1, 'x')")
    kq = api.submit_huy_chuong("s1", {"G": 60})
    assert not kq["ok"] and ma(kq["errors"]) == ["wharton_da_khoa"]


def test_pipeline_chan_khi_ho_so_huy_chuong_sai(api):
    _dung(api)
    with api._ket_noi_ghi() as cur:       # ghi thẳng giá trị sai, qua mặt submit_huy_chuong
        cur.execute("INSERT INTO wharton_bids (student_id, club_id, tier, points) "
                    "VALUES ('s1', 'G', 2, 50)")
    kq = api.run_pipeline(seed=3)
    assert not kq["ok"]
    assert "fa_huy_chuong_gia_tri_sai" in ma(kq["errors"])
    assert "wharton_ho_so_chua_hop_le" not in ma(kq["errors"])     # không đòi chia 2 quỹ x 100
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM run_history").fetchone()[0] == 0


def test_pipeline_chay_duoc_voi_huy_chuong_khong_can_100_diem(api):
    _dung(api)
    # SG-1: CLB Tuyển chọn có người đăng ký thì phải có ít nhất một điểm thi, nếu không lần chạy bị chặn.
    assert api.submit_test_selection("s1", ["S"])["ok"]
    assert api.submit_club_scores("S", [{"student_id": "s1", "score": 9}])["ok"]
    assert api.submit_huy_chuong("s1", {"G": 60})["ok"]
    kq = api.run_pipeline(seed=3)
    assert kq["ok"], kq["errors"]


def test_bao_cao_suc_khoe_co_loi_huy_chuong(api):
    _dung(api)
    with api._ket_noi_ghi() as cur:
        cur.execute("INSERT INTO wharton_bids (student_id, club_id, tier, points) "
                    "VALUES ('s1', 'T', 2, 60)")
    kq = api.get_data_health_report()
    assert "fa_huy_chuong_clb_tu_do" in ma(kq["data"]["warnings"])
