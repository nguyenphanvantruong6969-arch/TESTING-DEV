"""Mọi kết nối SQLite mà mã sản phẩm mở phải được ĐÓNG tường minh, kể cả khi có lỗi.

Trên Linux, một kết nối bị bỏ quên được thu hồi ngay khi mất tham chiếu và không ai hay biết. Trên
Windows, tệp đang mở không dời / xoá / đổi tên được (WinError 32 / 5): xoá workspace, di trú app.db cũ,
nhập zip dọn thư mục tạm đều hỏng — mà bộ test Linux vẫn xanh (đã xảy ra: CI Windows đỏ 24 test).

Bộ dò này thay `sqlite3.connect` bằng một lớp con ghi lại kết nối nào bị HUỶ MÀ CHƯA GỌI `close()`.
Đó là cách bắt lỗi kiểu Windows ngay trên Linux.
"""

import contextlib
import gc
import os
import sqlite3

import pytest

import cau_hinh_ws as ch
import rbda_priority_pipeline as rp
import workspace as ws
from api import PipelineAPI

_THAT = sqlite3.connect


@contextlib.contextmanager
def theo_doi_ket_noi(monkeypatch):
    """Trả danh sách (đường dẫn) các kết nối bị huỷ khi chưa đóng, trong khối `with`."""
    bi_bo_quen: list = []

    class KetNoi(sqlite3.Connection):
        _da_dong = False
        _duong = ""

        def close(self):
            self._da_dong = True
            super().close()

        def __del__(self):
            if not self._da_dong:
                bi_bo_quen.append(self._duong)

    def mo(duong, *a, **k):
        k.setdefault("factory", KetNoi)
        conn = _THAT(duong, *a, **k)
        conn._duong = str(duong)
        return conn

    monkeypatch.setattr(sqlite3, "connect", mo)
    try:
        yield bi_bo_quen
    finally:
        monkeypatch.setattr(sqlite3, "connect", _THAT)
        gc.collect()


@pytest.fixture
def goc(tmp_path):
    g = tmp_path / "goc"
    g.mkdir()
    return str(g)


def _khong_ai_bo_quen(bi_bo_quen):
    gc.collect()
    assert bi_bo_quen == [], "kết nối chưa đóng: %s" % bi_bo_quen


def test_connect_db_dong_ket_noi_khi_tep_khong_phai_sqlite(tmp_path, monkeypatch):
    rac = tmp_path / "rac.db"
    rac.write_bytes(b"khong phai sqlite " * 100)
    with theo_doi_ket_noi(monkeypatch) as bo_quen:
        with pytest.raises(sqlite3.DatabaseError):
            rp.connect_db(str(rac))
        _khong_ai_bo_quen(bo_quen)


def test_hoat_dong_workspace_binh_thuong_khong_bo_quen_ket_noi(goc, tmp_path, monkeypatch):
    with theo_doi_ket_noi(monkeypatch) as bo_quen:
        slug = ws.tao(goc, "Một", {"rules": {"max_choices": 4}})
        db = ws.duong_dan_db(goc, slug)
        ch.doc_cau_hinh(db)
        ch.doc_cau_hinh(db, nghiem=True)
        ws.doi_ten(goc, slug, "Hai")
        ws.danh_sach(goc)
        ws.luu_mau(goc, slug, "Mẫu")
        nhan = ws.nhan_ban(goc, slug, "Bản sao", True)
        ws.nhan_ban(goc, slug, "Bản trống", False)
        zp = str(tmp_path / "x.zip")
        ws.xuat_zip(goc, slug, zp)
        moi = ws.nhap_zip(goc, zp)
        ws.xoa(goc, nhan)
        ws.xoa(goc, moi)
        _khong_ai_bo_quen(bo_quen)


def test_xoa_workspace_hong_khong_bo_quen_ket_noi(goc, monkeypatch):
    slug = ws.tao(goc, "Hỏng")
    with open(ws.duong_dan_db(goc, slug), "wb") as f:
        f.write(b"rac " * 500)
    with theo_doi_ket_noi(monkeypatch) as bo_quen:
        ws.xoa(goc, slug)
        _khong_ai_bo_quen(bo_quen)


def test_nhap_zip_app_db_hong_khong_bo_quen_ket_noi(goc, tmp_path, monkeypatch):
    import zipfile
    zp = str(tmp_path / "hong.zip")
    with zipfile.ZipFile(zp, "w") as z:
        z.writestr("app.db", b"khong phai sqlite " * 100)
    with theo_doi_ket_noi(monkeypatch) as bo_quen:
        with pytest.raises(ValueError):
            ws.nhap_zip(goc, zp)
        _khong_ai_bo_quen(bo_quen)
    # và không để lại thư mục tạm (trên Windows, tệp đang mở làm rmtree thất bại im lặng)
    assert [x for x in os.listdir(os.path.join(goc, "workspaces")) if x.startswith("_")] == []


def test_di_tru_app_db_cu_khong_bo_quen_ket_noi(goc, monkeypatch):
    db = os.path.join(goc, "app.db")
    rp.init_db(db)
    with theo_doi_ket_noi(monkeypatch) as bo_quen:
        assert ws.di_chuyen_db_cu(goc) is True
        _khong_ai_bo_quen(bo_quen)


def test_di_tru_app_db_cu_hong_khong_bo_quen_ket_noi(goc, monkeypatch):
    with open(os.path.join(goc, "app.db"), "wb") as f:
        f.write(b"rac " * 500)
    with theo_doi_ket_noi(monkeypatch) as bo_quen:
        assert ws.di_chuyen_db_cu(goc) is True
        _khong_ai_bo_quen(bo_quen)


def test_api_chay_xep_va_phuc_hoi_khong_bo_quen_ket_noi(goc, tmp_path, monkeypatch):
    slug = ws.tao(goc, "Chạy")
    db = ws.duong_dan_db(goc, slug)
    with theo_doi_ket_noi(monkeypatch) as bo_quen:
        api = PipelineAPI(db, thu_muc_xuat=str(tmp_path), thu_muc_goc_ws=goc)
        assert api.create_or_update_club("a", "A", 2, 0, "")["ok"]
        for sid in ("N1", "N2"):
            assert api.create_student_if_missing(sid, sid)["ok"]
            assert api.submit_preferences(sid, ["a"])["ok"]
        assert api.run_pipeline(seed=3)["ok"]
        assert api.get_run_history()["ok"]
        assert api.get_data_health_report()["ok"]
        assert api.export_workspace(slug)["ok"]
        _khong_ai_bo_quen(bo_quen)
