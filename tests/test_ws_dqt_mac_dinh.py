"""A13.13, workspace "Trường học" mặc định mở lên là BẬT Điểm quyết tâm. Dữ liệu MÔ PHỎNG.

  * workspace mới dựng lúc mở app lần đầu: `rules.wharton` = True; mặc định CHUNG vẫn False
    (workspace ngành khác, CSDL không workspace);
  * workspace "Trường học" cũ còn nguyên mặc định cũ và chưa từng chạy xếp: mở app thì bật, có sao lưu;
  * đã chạy xếp, đã đổi luật / nhãn, hoặc người dùng tắt lại sau đó: KHÔNG đổi;
  * di trú chạy hai lần như một.
"""

import glob
import os
import sys

import pytest

import cau_hinh_ws as ch
import workspace as ws
from api import PipelineAPI


@pytest.fixture
def main_mod(monkeypatch, tmp_path):
    import main

    goc = tmp_path / "goc"
    goc.mkdir()
    monkeypatch.setattr(main, "BASE_DIR", str(goc))
    monkeypatch.setattr(sys, "argv", ["main.py"])
    return main


def _dung_cu(goc, **ghi_de):
    """Workspace "Trường học" như bản TRƯỚC A13.13 dựng: cấu hình mặc định, Điểm quyết tâm tắt."""
    slug = ws.tao(goc, ws.TEN_TRUONG_HOC, None)
    db = ws.duong_dan_db(goc, slug)
    assert slug == ws.SLUG_TRUONG_HOC
    assert ch.doc_cau_hinh(db)["rules"]["wharton"] is False
    if ghi_de:
        ch.ghi_cau_hinh(db, ch.tron_len(ch.doc_cau_hinh(db), ghi_de))
    return db


def _bat(db):
    return ch.doc_cau_hinh(db)["rules"]["wharton"]


def _bak(db):
    return glob.glob(db + ".bak-*")


def _ghi_lan_chay(db):
    api = PipelineAPI(db)
    with api._ket_noi_ghi() as cur:
        cur.execute(
            "INSERT INTO run_history (seed, run_at, rounds_run, n_matched, n_total, stb_redrawn) "
            "VALUES (42, '2025-01-01', 3, 1, 2, 1)")


def test_workspace_moi_lan_dau_mo_app_bat_diem_quyet_tam(main_mod):
    db = main_mod.khoi_dong_workspace()[0]
    assert _bat(db) is True
    assert _bak(db) == []                       # dựng mới: chẳng có gì để sao lưu


def test_mo_lai_app_khong_doi_gi(main_mod):
    db = main_mod.khoi_dong_workspace()[0]
    truoc = ch.doc_cau_hinh(db)
    assert main_mod.khoi_dong_workspace()[0] == db
    assert ch.doc_cau_hinh(db) == truoc and _bak(db) == []


def test_mac_dinh_chung_va_workspace_nganh_khac_van_tat(tmp_path):
    assert ch.MAC_DINH_TRUONG_HOC["rules"]["wharton"] is False
    goc = str(tmp_path)
    slug = ws.tao(goc, "Công ty", {"industry": "company"})
    assert _bat(ws.duong_dan_db(goc, slug)) is False
    # mở app (bật cho Trường học) cũng không đụng tới workspace khác
    ws.bat_dqt_mac_dinh_truong_hoc(goc)
    assert _bat(ws.duong_dan_db(goc, slug)) is False
    # CSDL không workspace: mặc định giữ nguyên
    assert ch.doc_cau_hinh(str(tmp_path / "khong_co.db"))["rules"]["wharton"] is False


def test_workspace_cu_chua_chay_nguyen_mac_dinh_thi_bat_va_sao_luu(main_mod):
    db = _dung_cu(main_mod.BASE_DIR)
    assert main_mod.khoi_dong_workspace()[0] == db
    assert _bat(db) is True
    assert len(_bak(db)) == 1
    # chỉ Điểm quyết tâm đổi; mọi thứ khác của cấu hình y nguyên
    moi, cu = ch.doc_cau_hinh(db), ch.chuan_hoa({"name": ws.TEN_TRUONG_HOC})
    moi["rules"]["wharton"] = False
    assert moi == cu


def test_di_tru_chay_hai_lan_nhu_mot(main_mod):
    db = _dung_cu(main_mod.BASE_DIR)
    assert ws.bat_dqt_mac_dinh_truong_hoc(main_mod.BASE_DIR) is True
    sau_lan_1 = ch.doc_cau_hinh(db)
    n_bak = len(_bak(db))
    assert ws.bat_dqt_mac_dinh_truong_hoc(main_mod.BASE_DIR) is False
    assert ch.doc_cau_hinh(db) == sau_lan_1 and len(_bak(db)) == n_bak == 1


def test_da_chay_xep_thi_giu_nguyen(main_mod):
    db = _dung_cu(main_mod.BASE_DIR)
    _ghi_lan_chay(db)
    ws.bat_dqt_mac_dinh_truong_hoc(main_mod.BASE_DIR)
    assert _bat(db) is False and _bak(db) == []
    # chạy rỗng rồi sau này có xoá lịch sử cũng không bật lại (đã có dấu)
    assert ws.bat_dqt_mac_dinh_truong_hoc(main_mod.BASE_DIR) is False


def test_da_doi_luat_hoac_nhan_thi_giu_nguyen(main_mod):
    db = _dung_cu(main_mod.BASE_DIR, rules={"max_choices": 8})
    assert ws.bat_dqt_mac_dinh_truong_hoc(main_mod.BASE_DIR) is False
    assert _bat(db) is False and ch.doc_cau_hinh(db)["rules"]["max_choices"] == 8


def test_nguoi_dung_tat_lai_sau_khi_da_bat_thi_khong_bi_bat_lai(main_mod):
    db = main_mod.khoi_dong_workspace()[0]              # dựng mới: bật
    api = PipelineAPI(db)
    ch.ghi_cau_hinh(db, ch.tron_len(ch.doc_cau_hinh(db), {"rules": {"wharton": False}}))
    del api
    main_mod.khoi_dong_workspace()
    assert _bat(db) is False
    # cũng đúng với workspace cũ được bật bởi di trú
    goc2 = os.path.join(main_mod.BASE_DIR, "..", "goc2")
    os.makedirs(goc2)
    db2 = _dung_cu(goc2)
    assert ws.bat_dqt_mac_dinh_truong_hoc(goc2) is True
    ch.ghi_cau_hinh(db2, ch.tron_len(ch.doc_cau_hinh(db2), {"rules": {"wharton": False}}))
    assert ws.bat_dqt_mac_dinh_truong_hoc(goc2) is False
    assert _bat(db2) is False


def test_cau_hinh_hong_thi_bo_qua_khong_ghi_de(main_mod):
    import sqlite3
    db = _dung_cu(main_mod.BASE_DIR)
    conn = sqlite3.connect(db)
    conn.execute("UPDATE workspace_settings SET value = '{hong' WHERE key = 'config'")
    conn.commit()
    conn.close()
    assert ws.bat_dqt_mac_dinh_truong_hoc(main_mod.BASE_DIR) is False
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT value FROM workspace_settings WHERE key = 'config'").fetchone()[0] == "{hong"
    conn.close()


def test_xoa_het_roi_dung_lai_truong_hoc_van_bat(tmp_path):
    goc = tmp_path / "goc"
    goc.mkdir()
    g = str(goc)
    slug = ws.tao(g, "Trường học", None)           # workspace đang mở (kiểu cũ, tắt)
    ws.tao(g, "Khác", None)
    api = PipelineAPI(ws.duong_dan_db(g, "khac"), thu_muc_goc_ws=g, ws_da_chon=False)
    assert api.delete_workspace(slug, "XOA")["ok"] is True
    assert api.delete_workspace("khac", "XOA")["ok"] is True        # xoá hết: dựng lại mặc định
    moi = ws.duong_dan_db(g, ws.SLUG_TRUONG_HOC)
    assert os.path.isfile(moi) and _bat(moi) is True
