"""A13.14, API của hộp Cài đặt: `get_cai_dat`, `save_cai_dat`. Dữ liệu MÔ PHỎNG.

  * đọc: chỉ các khoá luật đã có trong `cau_hinh_ws.py`; chạy được cả không có workspace;
  * ghi: kiểm bằng `cau_hinh_ws.chuan_hoa` (lỗi ra {ok, data, errors} dịch được);
  * đã chạy xếp: phải xác nhận, rồi sao lưu trước khi ghi; `run_history` và hai khoá không đổi;
  * mặc định không đổi gì: lưu đúng giá trị đang có thì không ghi, không sao lưu.
"""

import glob
import json
import os

import pytest

import cau_hinh_ws as ch
import workspace as ws
from api import PipelineAPI
from i18n_errors import MESSAGES as ERRORS
from _wharton import chen_bids, dung_clb


@pytest.fixture
def api(tmp_path):
    return PipelineAPI(str(tmp_path / "app.db"))


@pytest.fixture
def api_ws(tmp_path):
    goc = str(tmp_path / "goc")
    os.makedirs(goc)
    slug = ws.tao(goc, "Trường học", None)
    return PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_goc_ws=goc)


def _ma(res):
    return [e["code"] for e in res["errors"]]


def _luat(api):
    return ch.doc_cau_hinh(api.db_path)["rules"]


def _du_lieu_nho(api):
    for sid in ("HS1", "HS2"):
        assert api.create_student_if_missing(sid, "Em " + sid)["ok"]
    dung_clb(api, A=1, B=1)
    assert api.submit_preferences("HS1", ["A", "B"])["ok"]
    assert api.submit_preferences("HS2", ["A"])["ok"]


def test_get_chi_co_cac_khoa_luat_da_co_va_chay_duoc_khong_workspace(api):
    r = api.get_cai_dat()
    assert r["ok"], r
    d = r["data"]
    assert set(d["rules"]) == {"priority", "tier_mode", "max_choices", "max_tests", "score_scope",
                               "wharton", "tiers"}
    assert set(d["rules"]) <= set(ch.MAC_DINH_TRUONG_HOC["rules"])
    assert d["che_do_ws"] is False and d["so_lan_chay"] == 0
    assert d["khoa_stb"] is False and d["khoa_diem_quyet_tam"] is False
    assert d["toi_da"] == {"max_choices": 20, "max_tests": 20}


def test_get_o_workspace_co_slug(api_ws):
    d = api_ws.get_cai_dat()["data"]
    assert d["che_do_ws"] is True and d["slug"] == "truong-hoc"


def test_luu_doi_luat_chua_chay_thi_ghi_khong_can_xac_nhan_khong_sao_luu(api):
    r = api.save_cai_dat({"max_choices": 7, "priority": "score+tier", "tier_mode": "strict",
                          "tiers": ["A", "B"]})
    assert r["ok"] and r["data"]["da_doi"] is True and r["data"]["sao_luu"] == ""
    luat = _luat(api)
    assert luat["max_choices"] == 7 and luat["priority"] == "score+tier" and luat["tiers"] == ["A", "B"]
    assert glob.glob(api.db_path + ".bak-*") == []


def test_khoa_khong_nhac_toi_giu_nguyen(api):
    api.save_cai_dat({"max_choices": 6})
    api.save_cai_dat({"max_tests": 3})
    luat = _luat(api)
    assert luat["max_choices"] == 6 and luat["max_tests"] == 3
    assert api.get_cai_dat()["data"]["rules"]["max_choices"] == 6


def test_luu_dung_gia_tri_dang_co_thi_khong_doi_gi(api):
    truoc = ch.doc_cau_hinh(api.db_path)
    r = api.save_cai_dat(dict(api.get_cai_dat()["data"]["rules"]))
    assert r["ok"] and r["data"]["da_doi"] is False
    assert ch.doc_cau_hinh(api.db_path) == truoc


@pytest.mark.parametrize("rules,ma_mong", [
    ({"max_choices": 0}, "ws_du_lieu_sai"),
    ({"max_choices": 21}, "ws_du_lieu_sai"),
    ({"priority": "ngau_nhien"}, "ws_du_lieu_sai"),
    ({"wharton": True, "priority": "tier"}, "ws_du_lieu_sai"),
    ({"wharton": True, "score_scope": "per_person"}, "ws_du_lieu_sai"),
    ({"tiers": ["A", "A"]}, "ws_du_lieu_sai"),
    ({"khong_co_khoa_nay": 1}, "ws_du_lieu_sai"),
])
def test_luat_sai_bi_tu_choi_theo_hop_dong_va_khong_ghi(api, rules, ma_mong):
    truoc = ch.doc_cau_hinh(api.db_path)
    r = api.save_cai_dat(rules)
    assert r["ok"] is False and _ma(r) == [ma_mong], r
    assert "detail" in r["errors"][0]["params"]
    assert ch.doc_cau_hinh(api.db_path) == truoc


def test_khong_phai_tu_dien_bi_tu_choi(api):
    assert _ma(api.save_cai_dat("max_choices=3")) == ["ws_du_lieu_sai"]
    assert _ma(api.save_cai_dat(None)) == ["ws_du_lieu_sai"]


def test_tran_thap_hon_du_lieu_dang_co_bi_tu_choi_khong_cat_bot(api):
    _du_lieu_nho(api)                                   # HS1 có 2 nguyện vọng
    r = api.save_cai_dat({"max_choices": 1})
    assert _ma(r) == ["cai_dat_nguyen_vong_vuot_tran"]
    assert r["errors"][0]["params"] == {"n_em": 1, "tran": 1, "cao_nhat": 2}
    assert _luat(api)["max_choices"] == ch.MAC_DINH_TRUONG_HOC["rules"]["max_choices"]
    assert api.save_cai_dat({"max_choices": 2})["ok"]


def _chay_xep(api):
    _du_lieu_nho(api)
    assert api.run_pipeline(seed=3)["ok"]


def test_da_chay_xep_phai_xac_nhan_roi_sao_luu_truoc_khi_ghi(api):
    _chay_xep(api)
    n_hist = _dem_run_history(api)
    assert n_hist == 1
    r = api.save_cai_dat({"max_choices": 8})
    assert _ma(r) == ["cai_dat_can_xac_nhan"] and r["errors"][0]["params"] == {"n_lan_chay": 1}
    assert _luat(api)["max_choices"] != 8                # chưa ghi gì
    n_bak_truoc = len(glob.glob(api.db_path + ".bak-*"))
    r = api.save_cai_dat({"max_choices": 8}, xac_nhan=True)
    assert r["ok"] and r["data"]["da_doi"] is True
    assert r["data"]["sao_luu"].startswith("app.db.bak-")
    assert len(glob.glob(api.db_path + ".bak-*")) == n_bak_truoc + 1
    assert _luat(api)["max_choices"] == 8
    assert _dem_run_history(api) == n_hist               # lịch sử giữ nguyên


def test_xac_nhan_phai_dung_true_chu_khong_phai_gia_tri_bat_ky(api):
    _chay_xep(api)
    assert _ma(api.save_cai_dat({"max_choices": 8}, xac_nhan="true")) == ["cai_dat_can_xac_nhan"]
    assert _ma(api.save_cai_dat({"max_choices": 8}, xac_nhan=1)) == ["cai_dat_can_xac_nhan"]


def test_doi_luat_roi_chay_lai_cho_ket_qua_hop_le_va_them_mot_dong_lich_su(api):
    _chay_xep(api)
    assert api.save_cai_dat({"max_choices": 8}, xac_nhan=True)["ok"]
    assert api.run_pipeline(seed=3)["ok"] is True
    assert _dem_run_history(api) == 2


def test_khoa_stb_khong_tu_mo_khi_doi_luat(api):
    _chay_xep(api)
    truoc = api.get_stb_lock_status()["data"]
    assert truoc["is_locked"] is True
    assert api.save_cai_dat({"max_choices": 8}, xac_nhan=True)["ok"]
    assert api.get_stb_lock_status()["data"] == truoc
    d = api.get_cai_dat()["data"]
    assert d["khoa_stb"] is True and d["so_lan_chay"] == 1


def test_tat_diem_quyet_tam_sau_khi_khoa_van_giu_khoa_va_du_lieu_diem(api):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"wharton": True}})
    dung_clb(api, A=2)
    assert api.create_student_if_missing("HS1", "Em")["ok"]
    assert api.submit_preferences("HS1", ["A"])["ok"]
    chen_bids(api, [("HS1", "A", 2, 100)])
    assert api.run_pipeline(seed=3)["ok"]
    d = api.get_cai_dat()["data"]
    assert d["khoa_diem_quyet_tam"] is True
    assert api.save_cai_dat({"wharton": False}, xac_nhan=True)["ok"]
    d2 = api.get_cai_dat()["data"]
    assert d2["rules"]["wharton"] is False and d2["khoa_diem_quyet_tam"] is True
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM wharton_bids").fetchone()[0] == 1


def test_cai_dat_hong_thi_tu_choi_khong_ghi_de(api):
    import sqlite3
    ch.ghi_cau_hinh(api.db_path, {})
    c = sqlite3.connect(api.db_path)
    c.execute("UPDATE workspace_settings SET value = '{hong' WHERE key = 'config'")
    c.commit()
    c.close()
    r = api.save_cai_dat({"max_choices": 4})
    assert r["ok"] is False and _ma(r) == ["ws_cau_hinh_hong"]
    c = sqlite3.connect(api.db_path)
    assert c.execute("SELECT value FROM workspace_settings WHERE key='config'").fetchone()[0] == "{hong"
    c.close()


def test_phan_hoi_la_json_va_ma_loi_co_ban_dich(api):
    _chay_xep(api)
    for r in (api.get_cai_dat(), api.save_cai_dat({"max_choices": 0}),
              api.save_cai_dat({"max_choices": 8})):
        json.dumps(r)
        for e in r["errors"]:
            assert e["code"] in ERRORS and set(ERRORS[e["code"]]) >= {"vi", "en"}


def _dem_run_history(api):
    with api._ket_noi_doc() as cur:
        return cur.execute("SELECT COUNT(*) FROM run_history").fetchone()[0]
