"""Điểm Wharton (A13, vòng 2): mục sức khoẻ dữ liệu (`get_data_health_report`).

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.

  * Wharton TẮT: báo cáo y hệt trước vòng 2 (không có mục nào về Wharton, dù bảng có dòng);
  * BẬT: hồ sơ sai là mức "high" (vì sẽ chặn chạy), vắng thi là "medium".
"""

import pytest

from _wharton import bat_wharton, chen_bids, dung_clb, dung_hs


def _ma(api):
    kq = api.get_data_health_report()
    assert kq["ok"], kq["errors"]
    return kq["data"]["warnings"]


def _wharton(ds):
    return [w for w in ds if "wharton" in w["code"]]


@pytest.fixture
def w(api):
    """Wharton bật; ba em cùng nguyện vọng A, B, C, đều không thi; HS1 hợp lệ."""
    bat_wharton(api)
    dung_clb(api, A=5, B=5, C=5)
    dung_hs(api, "HS1", "HS2", "HS3")
    for sid in ("HS1", "HS2", "HS3"):
        assert api.submit_preferences(sid, ["A", "B", "C"])["ok"]
    assert api.submit_wharton("HS1", {}, {"A": 50, "B": 30, "C": 20})["ok"]
    return api


def test_tat_wharton_khong_co_muc_nao_ke_ca_khi_bang_co_dong_sai(api):
    dung_clb(api, A=5)
    dung_hs(api, "HS1")
    assert api.submit_preferences("HS1", ["A"])["ok"]
    chen_bids(api, [("HS1", "A", 2, 7)])                  # sai, nhưng workspace tắt
    co_dong = _ma(api)
    assert _wharton(co_dong) == []
    # đối chứng: bỏ hết dòng bids thì báo cáo y hệt (bảng không quyết định gì khi tắt)
    with api._ket_noi_ghi() as cur:
        cur.execute("DELETE FROM wharton_bids")
    assert _ma(api) == co_dong


def test_bat_wharton_du_lieu_sach_khong_co_muc_wharton(w):
    with w._ket_noi_ghi() as cur:
        cur.executemany("INSERT INTO wharton_bids VALUES (?, ?, 2, ?)",
                        [(s, c, p) for s in ("HS2", "HS3") for c, p in (("A", 50), ("B", 30), ("C", 20))])
    assert _wharton(_ma(w)) == []


def test_hai_em_sai_thi_co_muc_high_n_bang_2(w):
    with w._ket_noi_ghi() as cur:                          # HS2 tổng 90; HS3 chưa chia gì
        cur.executemany("INSERT INTO wharton_bids VALUES ('HS2', ?, 2, ?)",
                        [("A", 50), ("B", 30), ("C", 10)])
    ds = _wharton(_ma(w))
    assert [(x["code"], x["params"], x["severity"]) for x in ds] == [
        ("health_wharton_chua_hop_le", {"n": 2}, "high")]


def test_mot_em_vang_thi_thi_co_muc_medium_n_bang_1(api):
    bat_wharton(api)
    dung_clb(api, Ly=1, Toan=5)
    dung_hs(api, "An", "Quan", tick={"An": ["Ly"], "Quan": ["Ly"]})
    for sid in ("An", "Quan"):
        assert api.submit_preferences(sid, ["Ly", "Toan"])["ok"]
        assert api.submit_wharton(sid, {"Ly": 100}, {"Toan": 100})["ok"]
    assert api.submit_club_scores("Ly", [{"student_id": "An", "score": 5.0}])["ok"]   # Quân vắng
    ds = _wharton(_ma(api))
    assert [(x["code"], x["params"], x["severity"]) for x in ds] == [
        ("health_wharton_vang_thi", {"n": 1}, "medium")]


def test_muc_wharton_dung_sau_cac_muc_san_co(w):
    api = w
    dung_clb(api, Toi=5)                                   # CLB có người thi mà chưa ai được chấm
    dung_hs(api, "HS4", tick={"HS4": ["Toi"]})
    assert api.submit_preferences("HS4", ["Toi"])["ok"]
    ds = _ma(api)
    ma = [x["code"] for x in ds]
    assert "health_scoring_none" in ma and "health_wharton_chua_hop_le" in ma
    assert ma.index("health_scoring_none") < ma.index("health_wharton_chua_hop_le")


def test_bao_cao_van_ok_khi_khong_co_hoc_sinh_nao(api):
    bat_wharton(api)
    assert _ma(api) == []
