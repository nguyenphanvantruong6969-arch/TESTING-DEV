"""Điểm Wharton (A13, vòng 2): khoá luật `rules.wharton` của workspace.

Mặc định TẮT. Chỉ bật được khi priority là "score" hoặc "score+tier" VÀ score_scope là
"per_slot" (điểm Wharton cần biết em có thi CLB nào, nên cần điểm theo từng CLB).
Luật tắt thì bản đem ghi vào `run_history.luat_xep` và đem băm vào dấu vân tay KHÔNG có khoá
`wharton` — để workspace tuỳ biến cũ giữ nguyên từng byte (bất biến 1).
"""

import copy
import json

import pytest

import cau_hinh_ws as ch
import rbda_priority_pipeline as rp


def _luat(**rest):
    cfg = {"rules": dict(rest)}
    return ch.chuan_hoa(cfg)["rules"]


# ------------------------------------------------------------------ cau_hinh_ws

def test_mac_dinh_tat():
    assert ch.MAC_DINH_TRUONG_HOC["rules"]["wharton"] is False
    assert _luat()["wharton"] is False


@pytest.mark.parametrize("rest", [
    {"wharton": True},
    {"wharton": True, "priority": "score", "score_scope": "per_slot"},
    {"wharton": True, "priority": "score+tier", "score_scope": "per_slot"},
    {"wharton": True, "priority": "score+tier", "tier_mode": "strict", "tiers": ["A", "B"]},
])
def test_bat_duoc_voi_to_hop_hop_le(rest):
    assert _luat(**rest)["wharton"] is True


@pytest.mark.parametrize("rest", [
    {"wharton": True, "priority": "tier"},
    {"wharton": True, "score_scope": "per_person"},
    {"wharton": True, "priority": "tier", "score_scope": "per_person"},
])
def test_to_hop_khac_bi_tu_choi_kem_cau_noi_ro_ly_do(rest):
    with pytest.raises(ValueError) as e:
        _luat(**rest)
    cau = str(e.value)
    assert "wharton" in cau and "per_slot" in cau and "score" in cau


@pytest.mark.parametrize("gia_tri", ["yes", 1, 0, None, "true", [], {}])
def test_phai_la_bool_that(gia_tri):
    with pytest.raises(ValueError):
        _luat(wharton=gia_tri)


def test_tat_thi_tron_che_do_nao_cung_duoc():
    # tắt thì không ràng buộc gì thêm: priority "tier" hay per_person vẫn như cũ
    assert _luat(wharton=False, priority="tier")["wharton"] is False
    assert _luat(wharton=False, score_scope="per_person")["priority"] == "score"


def test_tron_len_giu_duoc_gia_tri():
    da_luu = copy.deepcopy(ch.MAC_DINH_TRUONG_HOC)
    moi = ch.tron_len(da_luu, {"rules": {"wharton": True}})
    assert moi["rules"]["wharton"] is True and moi["rules"]["max_choices"] == 10
    assert da_luu["rules"]["wharton"] is False                    # không sửa đầu vào
    gop = ch.tron_len(moi, {"rules": {"priority": "score+tier"}})
    assert gop["rules"]["wharton"] is True                        # khoá không nhắc tới thì giữ


# ------------------------------------------------------------------ rbda_priority_pipeline

def test_luat_xep_mac_dinh_co_khoa_wharton_tat():
    assert rp.LUAT_XEP_MAC_DINH["wharton"] is False


def test_luat_de_ghi_mac_dinh_van_la_none():
    assert rp.luat_xep_de_ghi(None) is None
    assert rp.luat_xep_de_ghi({}) is None
    assert rp.luat_xep_de_ghi({"wharton": False}) is None
    assert rp.luat_xep_de_ghi(ch.MAC_DINH_TRUONG_HOC["rules"]) is None


def test_luat_de_ghi_bat_thi_co_khoa_wharton_true():
    s = rp.luat_xep_de_ghi({"wharton": True})
    assert json.loads(s)["wharton"] is True
    assert json.loads(s)["priority"] == "score"


def test_luat_de_ghi_khac_mac_dinh_nhung_tat_wharton_giu_nguyen_tung_byte():
    """Workspace tuỳ biến cũ (nhóm xếp cứng) không được đổi chuỗi ghi vì có khoá mới."""
    cu = json.dumps({"priority": "score", "tier_mode": "strict", "score_scope": "per_slot",
                     "tiers": ["A"]}, sort_keys=True, ensure_ascii=False)
    assert rp.luat_xep_de_ghi({"tier_mode": "strict", "tiers": ["A"]}) == cu
    assert rp.luat_xep_de_ghi({"tier_mode": "strict", "tiers": ["A"], "wharton": False}) == cu


@pytest.mark.parametrize("rules,mong_doi", [
    (None, False), ({}, False), ({"wharton": False}, False),
    ({"wharton": True}, True),
    ({"wharton": True, "priority": "score+tier"}, True),
])
def test_dung_wharton(rules, mong_doi):
    assert rp.dung_wharton(rules) is mong_doi


@pytest.mark.parametrize("rules", [
    {"wharton": True, "priority": "tier"},
    {"wharton": True, "score_scope": "per_person"},
    {"wharton": "yes"},
])
def test_dung_wharton_cau_hinh_hong_thi_nem_loi_khong_chay_kieu_khac(rules):
    with pytest.raises(ValueError):
        rp.dung_wharton(rules)


def test_luat_xep_hieu_luc_giu_khoa_wharton():
    assert rp.luat_xep_hieu_luc({"wharton": True})["wharton"] is True
    assert rp.luat_xep_hieu_luc({})["wharton"] is False
