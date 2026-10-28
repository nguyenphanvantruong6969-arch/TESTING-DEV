"""A13.9 — sửa các vấn đề của đợt stress test. Mỗi test khoá MỘT mục (số mục = số trong lệnh giao).

  1. CSDL đang bận ≠ cấu hình hỏng; đọc cấu hình chờ khoá ngắn (2–3 s).
  2. browser_host: kết nối treo (gửi dở yêu cầu) bị cắt sau 30–60 s, không giữ luồng mãi.
  3. Token không ASCII (tiêu đề / ?t=) → 403, không ném TypeError.
  9. Skill sinh-du-lieu-clb: > 20 CLB tự sinh tên; ≤ 20 đầu ra giữ nguyên từng byte.
  8. Sổ nhập 0 học sinh / 0 CLB: ok + cảnh báo mới (xem trước và nhập); chạy xếp sau đó không sập.
  7. Nhập .zip workspace: ≤ 1.000 tệp, giải nén ≤ 200 MB, từ chối tên trùng / có NUL.
  6. Xuất ra đường TUYỆT ĐỐI không ghi đè tệp đã có: "x (2).xlsx", mọi hàm xuất.
  4. loi_ung_dung.txt: trần ~1 MB giữ phần cuối; bỏ mục trùng liên tiếp.
  5. loi_ngoai_du_kien chỉ mang TÊN KIỂU ngoại lệ; thông điệp thật chỉ nằm trong nhật ký.
"""

import base64
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import socket
import sqlite3
import time
import warnings
import zipfile

import pytest

import browser_host
import cau_hinh_ws as ch
import chan_doan
import so_nhap
import workspace as ws
from api import PipelineAPI


def _ma(res):
    return [e["code"] for e in res["errors"]]


# ------------------------------------------------------------------ 1. CSDL đang bận

@pytest.fixture
def api_ws(tmp_path):
    goc = tmp_path / "goc"
    goc.mkdir()
    slug = ws.tao(str(goc), "Thử", None)
    xuat = tmp_path / "xuat"
    xuat.mkdir()
    return PipelineAPI(ws.duong_dan_db(str(goc), slug), thu_muc_xuat=str(xuat),
                       thu_muc_goc_ws=str(goc), ws_da_chon=True)


@contextlib.contextmanager
def _khoa_csdl(db):
    """Một kết nối khác giữ khoá ghi độc quyền — mô phỏng tiến trình khác đang ghi."""
    conn = sqlite3.connect(db, isolation_level=None)
    conn.execute("BEGIN EXCLUSIVE")
    try:
        yield
    finally:
        conn.execute("ROLLBACK")
        conn.close()


def test_1_csdl_ban_bao_ma_rieng_va_khong_cho_lau(api_ws):
    with _khoa_csdl(api_ws.db_path):
        t0 = time.monotonic()
        res = api_ws.check_data_integrity()
        dt = time.monotonic() - t0
    assert not res["ok"]
    assert _ma(res) == ["csdl_dang_ban"], _ma(res)
    assert dt < 6, dt   # đọc cấu hình chờ 2,5 s; trước đây 15 s


def test_1_chay_xep_gap_csdl_ban_cung_bao_csdl_dang_ban(api_ws):
    # (run_pipeline còn chờ tới 15 s ở bước sao lưu — cố ý giữ, xem báo cáo A13.9.)
    with _khoa_csdl(api_ws.db_path):
        res = api_ws.run_pipeline()
    assert "csdl_dang_ban" in _ma(res), _ma(res)
    assert "ws_cau_hinh_hong" not in _ma(res)


def test_1_cau_hinh_hong_that_van_la_ws_cau_hinh_hong(api_ws):
    conn = sqlite3.connect(api_ws.db_path)
    conn.execute("UPDATE workspace_settings SET value = '{khong phai json' WHERE key = 'config'")
    conn.commit()
    conn.close()
    assert _ma(api_ws.check_data_integrity()) == ["ws_cau_hinh_hong"]


def test_1_hang_so_cho_khoa_doc_cau_hinh_trong_2_3_giay():
    assert 2000 <= ch.CHO_KHOA_DOC_CAU_HINH_MS <= 3000


