"""A13.13: cấu hình mặc định của workspace trường học BẬT điểm Wharton.

Truong đã duyệt ngoại lệ bất biến 1 cho mục này. Tổ hợp luật không cho phép Wharton
(priority "tier", score_scope "per_person") mà KHÔNG ghi rõ `wharton` thì tự tắt; ghi rõ
`wharton: true` với tổ hợp đó vẫn báo lỗi.
"""

import copy
import json
import sqlite3

import pytest

import cau_hinh_ws as ch
import workspace as ws
from rbda_priority_pipeline import init_db


def _luat(**rest):
    return ch.chuan_hoa({"rules": dict(rest)})["rules"]


def test_mac_dinh_bat():
    assert ch.MAC_DINH_TRUONG_HOC["rules"]["wharton"] is True
    assert _luat()["wharton"] is True


@pytest.mark.parametrize("rest", [
    {"priority": "tier"},
    {"score_scope": "per_person"},
    {"priority": "tier", "score_scope": "per_person"},
])
def test_to_hop_khong_cho_phep_khong_ghi_wharton_thi_tu_tat(rest):
    assert _luat(**rest)["wharton"] is False


@pytest.mark.parametrize("rest", [
    {"wharton": True, "priority": "tier"},
    {"wharton": True, "score_scope": "per_person"},
])
def test_ghi_ro_true_voi_to_hop_sai_van_loi(rest):
    with pytest.raises(ValueError):
        _luat(**rest)


def test_tat_ro_rang_van_duoc():
    assert _luat(wharton=False)["wharton"] is False


def test_tron_len_doi_sang_tier_khong_nhac_wharton_thi_tu_tat(tmp_path):
    db = str(tmp_path / "app.db")
    init_db(db)
    da_luu = ch.ghi_cau_hinh(db, {})
    assert da_luu["rules"]["wharton"] is True
    moi = ch.tron_len(da_luu, {"rules": {"priority": "tier"}})
    assert ch.ghi_cau_hinh(db, moi)["rules"]["wharton"] is False
    # ghi rõ true cùng lúc thì vẫn lỗi
    with pytest.raises(ValueError):
        ch.ghi_cau_hinh(db, ch.tron_len(da_luu, {"rules": {"priority": "tier", "wharton": True}}))


def test_cau_hinh_cu_khong_co_khoa_wharton_voi_tier_van_mo_duoc(tmp_path):
    db = str(tmp_path / "app.db")
    init_db(db)
    cu = copy.deepcopy(ch.MAC_DINH_TRUONG_HOC)
    cu["rules"]["priority"] = "tier"
    del cu["rules"]["wharton"]
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE IF NOT EXISTS workspace_settings (key TEXT PRIMARY KEY, value TEXT)")
    conn.execute("INSERT OR REPLACE INTO workspace_settings VALUES (?, ?)",
                 (ch.KHOA_CAU_HINH, json.dumps(cu)))
    conn.commit()
    conn.close()
    doc = ch.doc_cau_hinh(db, nghiem=True)
    assert doc["rules"]["priority"] == "tier" and doc["rules"]["wharton"] is False


def test_workspace_moi_tao_co_wharton_bat(tmp_path):
    slug = ws.tao(str(tmp_path), "Truong A", None)
    cfg = ch.doc_cau_hinh(str(tmp_path / "workspaces" / slug / ws.TEN_DB))
    assert cfg["rules"]["wharton"] is True


def test_csdl_khong_co_hang_cau_hinh_la_bat(tmp_path):
    db = str(tmp_path / "app.db")
    init_db(db)
    assert ch.doc_cau_hinh(db)["rules"]["wharton"] is True


def test_workspace_di_tru_tu_app_db_cu_co_wharton_bat(tmp_path):
    init_db(str(tmp_path / "app.db"))
    assert ws.di_chuyen_db_cu(str(tmp_path)) is True
    db = str(tmp_path / "workspaces" / ws.SLUG_TRUONG_HOC / ws.TEN_DB)
    assert ch.doc_cau_hinh(db)["rules"]["wharton"] is True


def test_mau_dung_san_truong_hoc_bat_wharton(tmp_path):
    mau = ws.danh_sach_mau(str(tmp_path))[0]
    assert mau["builtin"] and mau["config"]["rules"]["wharton"] is True
