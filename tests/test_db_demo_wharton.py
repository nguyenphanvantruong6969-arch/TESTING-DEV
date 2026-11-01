# -*- coding: utf-8 -*-
"""A13.13 (tiếp): CSDL demo thể hiện điểm quyết tâm + đường dẫn script đo.

* `tao_db_demo.py` mặc định: Wharton BẬT, nạp SO_NHAP_DQT_120HS_HOP_LE.xlsx,
  CHƯA chạy phân bổ, chạy được trên bản sao.
* `tao_db_demo.py --tat-wharton`: dựng y như trước (bộ ba TEST_01..03,
  wharton=false), match_results trùng khít với nạp thẳng bộ ba TEST, seed 42.
* Không script du_lieu_test nào được ghi cứng đường dẫn máy khác.
"""

import base64
import io
import json
import os
import shutil
import sqlite3
import sys

import pytest

from api import PipelineAPI

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DLT = os.path.join(GOC, "du_lieu_test")
sys.path.insert(0, DLT)

import tao_db_demo  # noqa: E402


def _dem(db, bang):
    c = sqlite3.connect(db)
    try:
        return c.execute("SELECT COUNT(*) FROM %s" % bang).fetchone()[0]
    finally:
        c.close()


def _mr(db):
    c = sqlite3.connect(db)
    try:
        return sorted(c.execute("SELECT * FROM match_results").fetchall())
    finally:
        c.close()


@pytest.fixture(scope="module")
def db_bat(tmp_path_factory):
    ra = str(tmp_path_factory.mktemp("bat") / "demo.db")
    tao_db_demo.main(["--ra", ra])
    return ra


@pytest.fixture(scope="module")
def db_tat(tmp_path_factory):
    ra = str(tmp_path_factory.mktemp("tat") / "demo.db")
    tao_db_demo.main(["--tat-wharton", "--ra", ra])
    return ra


def test_bat_chua_chay_phan_bo_va_co_diem_quyet_tam(db_bat):
    assert _dem(db_bat, "match_results") == 0
    assert _dem(db_bat, "run_history") == 0
    assert _dem(db_bat, "students") == 120
    assert _dem(db_bat, "wharton_bids") > 0


def test_bat_chay_duoc_tren_ban_sao(db_bat, tmp_path):
    ban = str(tmp_path / "app.db")
    shutil.copy(db_bat, ban)
    r = PipelineAPI(ban).run_pipeline(seed=42)
    assert r["ok"], r["errors"]
    assert not [e for e in r["errors"] if "wharton" in e["code"]]
    c = sqlite3.connect(ban)
    try:
        luat = json.loads(c.execute("SELECT luat_xep FROM run_history").fetchone()[0])
    finally:
        c.close()
    assert luat["wharton"] is True


def test_csdl_demo_trong_kho_la_ban_bat():
    db = os.path.join(DLT, "app_DEMO_da_cham_diem.db")
    assert _dem(db, "wharton_bids") > 0
    assert _dem(db, "match_results") == 0


def test_tat_khong_co_bids_va_trung_khit_bo_ba_test(db_tat, tmp_path):
    assert _dem(db_tat, "wharton_bids") == 0
    assert _dem(db_tat, "match_results") == 0

    # Nạp thẳng bộ ba TEST với Wharton tắt tường minh, cùng seed 42.
    ref = str(tmp_path / "ref.db")
    api_ref = PipelineAPI(ref)
    __import__("cau_hinh_ws").ghi_cau_hinh(api_ref.db_path, {"rules": {"wharton": False}})
    for ten in tao_db_demo.TEP:
        with open(os.path.join(DLT, ten), "rb") as f:
            csv = api_ref.xlsx_to_csv_text(base64.b64encode(f.read()).decode())["data"]
        assert api_ref.import_csv_auto(csv["csv_text"] if isinstance(csv, dict) else csv)["ok"]
    ban = str(tmp_path / "tat.db")
    shutil.copy(db_tat, ban)
    assert PipelineAPI(ban).run_pipeline(seed=42)["ok"]
    assert api_ref.run_pipeline(seed=42)["ok"]
    mr = _mr(ban)
    assert mr and mr == _mr(ref)


def test_khong_script_du_lieu_test_ghi_cung_duong_dan_may_khac():
    sai = []
    for goc, _, tep in os.walk(DLT):
        for t in tep:
            if t.endswith(".py"):
                duong = os.path.join(goc, t)
                with io.open(duong, encoding="utf-8") as f:
                    if "/home/user/truong" in f.read():
                        sai.append(os.path.relpath(duong, DLT))
    assert sai == [], sai
