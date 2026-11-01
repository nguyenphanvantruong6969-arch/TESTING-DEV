"""A13.13: cấu hình mặc định của workspace trường học BẬT điểm Wharton.

Truong đã duyệt ngoại lệ bất biến 1 cho mục này. Tổ hợp luật không cho phép Wharton
(priority "tier", score_scope "per_person") mà KHÔNG ghi rõ `wharton` thì tự tắt; ghi rõ
`wharton: true` với tổ hợp đó vẫn báo lỗi.
"""

import copy
import sqlite3
import json


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


# ------------------------------------------------------------------ ảnh hưởng tới workspace / dữ liệu cũ

def test_cau_hinh_luu_truoc_a13_thieu_khoa_wharton_doc_thanh_bat(tmp_path):
    """Khoá `wharton` thiếu trong cấu hình đã lưu => BẬT (không di trú; xem CHANGELOG A13.13)."""
    db = str(tmp_path / "app.db")
    init_db(db)
    cu = copy.deepcopy(ch.MAC_DINH_TRUONG_HOC)
    del cu["rules"]["wharton"]
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE IF NOT EXISTS workspace_settings (key TEXT PRIMARY KEY, value TEXT)")
    conn.execute("INSERT OR REPLACE INTO workspace_settings VALUES (?, ?)",
                 (ch.KHOA_CAU_HINH, json.dumps(cu)))
    conn.commit()
    conn.close()
    assert ch.doc_cau_hinh(db)["rules"]["wharton"] is True


def _dung_du_lieu_khong_diem_quyet_tam(api):
    assert api.create_or_update_club("A", "CLB A", 1, 0, "")["ok"]
    assert api.create_or_update_club("B", "CLB B", 5, 0, "")["ok"]
    assert api.create_or_update_club("C", "CLB C", 5, 0, "")["ok"]
    # Quỹ 2 có hai CLB (B, C) nên KHÔNG tự điền 100 được (cách A chỉ tự điền quỹ một CLB).
    for sid in ("HS1", "HS2"):
        assert api.create_student_if_missing(sid, sid)["ok"]
        assert api.submit_test_selection(sid, ["A"])["ok"]
        assert api.submit_preferences(sid, ["A", "B", "C"])["ok"]
    assert api.submit_club_scores("A", [{"student_id": "HS1", "score": 5},
                                        {"student_id": "HS2", "score": 9}])["ok"]


def test_mac_dinh_du_lieu_chua_co_diem_quyet_tam_bi_chan_va_thong_bao_chi_cach_go(tmp_path):
    from api import PipelineAPI
    from i18n_errors import format_message
    api = PipelineAPI(str(tmp_path / "app.db"))
    _dung_du_lieu_khong_diem_quyet_tam(api)
    kq = api.run_pipeline(seed=1)
    assert not kq["ok"]
    codes = [e["code"] for e in kq["errors"]]
    assert "wharton_ho_so_chua_hop_le" in codes
    loi = next(e for e in kq["errors"] if e["code"] == "wharton_ho_so_chua_hop_le")
    for ngon in ("vi", "en"):
        chu = format_message(loi["code"], loi["params"], ngon).lower()
        # chỉ cách khắc phục: điền điểm, hoặc tắt trong cấu hình workspace
        assert ("điền" in chu and "tắt" in chu) if ngon == "vi" else ("fill in" in chu and "turn off" in chu)


def test_tat_ro_rang_thi_cung_du_lieu_chay_duoc(tmp_path):
    from api import PipelineAPI
    api = PipelineAPI(str(tmp_path / "app.db"))
    ch.ghi_cau_hinh(api.db_path, {"rules": {"wharton": False}})
    _dung_du_lieu_khong_diem_quyet_tam(api)
    assert api.run_pipeline(seed=1)["ok"]
