"""Vòng sửa lỗi thứ hai của nhánh workspace — mỗi test khoá lại MỘT lỗi đã sửa.

  1. Workspace có app.db hỏng vẫn xoá được (dời vào _trash, còn bản để cứu).
  2. Nhập zip: có trần dung lượng giải nén tính trên byte thật (chống zip bomb); bỏ tệp phụ SQLite.
  3. Slug: tên dài bị cắt; tên thiết bị của Windows (con, nul, com1...) không làm slug.
  4. Màn chọn lúc khởi động: workspace "mở tạm" chưa được người dùng chọn thì xoá được.
  5. run_history ghi luật xếp đã dùng (NULL khi là luật mặc định của trường học).
"""

import io
import json
import os
import sqlite3
import zipfile

import pytest

import rbda_priority_pipeline as rp
import workspace as ws
from api import PipelineAPI


@pytest.fixture
def goc(tmp_path):
    g = tmp_path / "goc"
    g.mkdir()
    return str(g)


# ------------------------------------------------------------------ 1. xoá workspace hỏng

def test_xoa_workspace_co_app_db_hong_van_duoc(goc):
    slug = ws.tao(goc, "Hỏng")
    db = ws.duong_dan_db(goc, slug)
    with open(db, "wb") as f:
        f.write(b"khong phai sqlite " * 100)

    rac = ws.xoa(goc, slug)

    assert os.path.dirname(rac) == os.path.join(goc, "workspaces", ws.THU_MUC_RAC)
    assert os.path.isfile(os.path.join(rac, "app.db"))
    assert any(t.startswith("app.db.bak-") for t in os.listdir(rac))   # còn bản để cứu
    assert slug not in {w["slug"] for w in ws.danh_sach(goc)}


# ------------------------------------------------------------------ 2. nhập zip

def _zip_voi(duong, muc):
    with zipfile.ZipFile(duong, "w", zipfile.ZIP_DEFLATED) as z:
        for ten, du_lieu in muc:
            z.writestr(ten, du_lieu)
    return str(duong)


def _app_db_that(goc):
    slug = ws.tao(goc, "Nguồn")
    b = io.BytesIO()
    with open(ws.duong_dan_db(goc, slug), "rb") as f:
        b.write(f.read())
    return b.getvalue()


def test_nhap_zip_bo_tep_phu_cua_sqlite_nhung_giu_tep_thuong(goc, tmp_path):
    zp = _zip_voi(tmp_path / "x.zip", [
        ("app.db", _app_db_that(goc)),
        ("ghi-chu.txt", b"giu"),
        ("app.db-journal", b"khong duoc ra"),
        ("app.db-wal", b"khong duoc ra"),
        ("app.db-shm", b"khong duoc ra"),
        ("app.db.bak-evil", b"khong duoc ra"),
    ])
    slug = ws.nhap_zip(goc, zp)
    thu_muc = os.path.join(goc, "workspaces", slug)
    assert sorted(os.listdir(thu_muc)) == ["app.db", "ghi-chu.txt"]


def test_nhap_zip_tran_tinh_tren_tong_cac_muc(goc, tmp_path, monkeypatch):
    """Mục đệm lớn (không phải app.db) cũng bị chặn: trần tính trên TỔNG dung lượng giải nén."""
    monkeypatch.setattr(ws, "TRAN_GIAI_NEN_BYTE", 100_000)
    zp = _zip_voi(tmp_path / "dem.zip", [
        ("app.db", _app_db_that(goc)),
        ("dem.bin", b"\0" * 2_000_000),
    ])
    with pytest.raises(ValueError):
        ws.nhap_zip(goc, zp)
    assert [x for x in os.listdir(os.path.join(goc, "workspaces")) if x.startswith("_nhap")] == []


def test_nhap_zip_tu_choi_khi_vuot_tran_giai_nen(goc, tmp_path, monkeypatch):
    monkeypatch.setattr(ws, "TRAN_GIAI_NEN_BYTE", 100_000)
    zp = _zip_voi(tmp_path / "bomb.zip", [("app.db", b"SQLite format 3\x00" + b"\0" * 2_000_000)])
    antes = set(os.listdir(os.path.join(goc, "workspaces"))) if os.path.isdir(
        os.path.join(goc, "workspaces")) else set()
    with pytest.raises(ValueError):
        ws.nhap_zip(goc, zp)
    # không để lại thư mục tạm hay workspace dở
    sau = set(os.listdir(os.path.join(goc, "workspaces")))
    assert sau == antes


def test_nhap_zip_tran_dem_theo_byte_that_khong_tin_tieu_de(goc, tmp_path, monkeypatch):
    """Tiêu đề zip khai nhỏ mà dữ liệu thật lớn: vẫn phải bị chặn."""
    monkeypatch.setattr(ws, "TRAN_GIAI_NEN_BYTE", 100_000)
    zp = _zip_voi(tmp_path / "noi_doi.zip", [("app.db", b"SQLite format 3\x00" + b"\0" * 2_000_000)])
    # sửa file_size trong cả tiêu đề cục bộ lẫn thư mục trung tâm thành 10 byte
    du = bytearray(open(zp, "rb").read())
    thuc = 16 + 2_000_000
    mau = thuc.to_bytes(4, "little")
    gia = (10).to_bytes(4, "little")
    i = 0
    while True:
        i = du.find(mau, i)
        if i < 0:
            break
        du[i:i + 4] = gia
        i += 4
    open(zp, "wb").write(bytes(du))
    with pytest.raises((ValueError, zipfile.BadZipFile)):
        ws.nhap_zip(goc, zp)


def test_nhap_zip_binh_thuong_van_chay(goc, tmp_path):
    zp = _zip_voi(tmp_path / "ok.zip", [("app.db", _app_db_that(goc))])
    assert ws.nhap_zip(goc, zp)


# ------------------------------------------------------------------ 3. slug

def test_slug_ten_dai_bi_cat(goc):
    slug = ws.tao(goc, "x" * 300)
    assert len(slug) <= 60
    assert os.path.isfile(ws.duong_dan_db(goc, slug))


@pytest.mark.parametrize("ten", ["CON", "nul", "Com1", "aux", "PRN", "lpt9"])
def test_slug_khong_la_ten_thiet_bi_windows(goc, ten):
    slug = ws.tao(goc, ten)
    assert slug.split("-")[0] not in {"con", "nul", "prn", "aux", "com1", "lpt9"}
    assert ws._RE_SLUG.match(slug)
    assert os.path.isfile(ws.duong_dan_db(goc, slug))


# ------------------------------------------------------------------ 4. xoa o man chon

def test_xoa_workspace_chua_duoc_chon_o_man_chon(goc):
    a = ws.tao(goc, "A")
    ws.tao(goc, "B")
    # khởi động nhiều workspace: db_path chỉ là chỗ tạm, người dùng CHƯA chọn
    api = PipelineAPI(ws.duong_dan_db(goc, a), thu_muc_goc_ws=goc, ws_da_chon=False)
    res = api.delete_workspace(a, "XOA")
    assert res["ok"], res


def test_van_khong_xoa_duoc_workspace_nguoi_dung_da_chon(goc):
    a = ws.tao(goc, "A")
    api = PipelineAPI(ws.duong_dan_db(goc, a), thu_muc_goc_ws=goc, ws_da_chon=True)
    res = api.delete_workspace(a, "XOA")
    assert not res["ok"] and res["errors"][0]["code"] == "ws_khong_xoa_dang_mo"


# ------------------------------------------------------------------ 5. run_history ghi luật

def _cau_hinh(**luat):
    return {"rules": luat}


def _chay(goc, tmp_path, cfg, seed):
    slug = ws.tao(goc, "W%d" % seed, cfg)
    xuat = tmp_path / ("xuat%d" % seed)
    xuat.mkdir()
    api = PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_xuat=str(xuat), thu_muc_goc_ws=goc)
    assert api.create_or_update_club("a", "A", 1, 0, "")["ok"]
    for sid in ("N1", "N2"):
        assert api.create_student_if_missing(sid, sid)["ok"]
        assert api.submit_preferences(sid, ["a"])["ok"]
    with api._ket_noi_ghi() as cur:
        cur.execute("UPDATE students SET reserve_group = 'Cấp 1' WHERE student_id = 'N1'")
    res = api.run_pipeline(seed=seed)
    assert res["ok"], res
    return api


def test_run_history_luat_mac_dinh_la_null(goc, tmp_path):
    api = _chay(goc, tmp_path, {}, 1)
    dong = api.get_run_history()["data"][0]
    assert "luat_xep" in dong and dong["luat_xep"] is None


def test_run_history_ghi_luat_khac_mac_dinh(goc, tmp_path):
    api = _chay(goc, tmp_path, _cau_hinh(tier_mode="strict", tiers=["Cấp 1", "Cấp 2"]), 2)
    dong = api.get_run_history()["data"][0]
    luat = json.loads(dong["luat_xep"])
    assert luat == {"priority": "score", "tier_mode": "strict",
                    "score_scope": "per_slot", "tiers": ["Cấp 1", "Cấp 2"]}


def test_di_tru_them_cot_luat_xep_vao_run_history_cu(tmp_path):
    db = str(tmp_path / "cu.db")
    rp.init_db(db)
    conn = sqlite3.connect(db)
    conn.execute("ALTER TABLE run_history RENAME TO run_history_moi")
    conn.execute("CREATE TABLE run_history (run_id INTEGER PRIMARY KEY AUTOINCREMENT, seed INTEGER, "
                 "run_at TEXT, rounds_run INTEGER, n_matched INTEGER, n_total INTEGER, "
                 "stb_redrawn INTEGER NOT NULL DEFAULT 0)")
    conn.execute("INSERT INTO run_history (seed, run_at) VALUES (7, 'x')")
    conn.execute("DROP TABLE run_history_moi")
    conn.commit()
    conn.close()
    rp.init_db(db)
    rp.init_db(db)          # chạy lặp an toàn
    conn = sqlite3.connect(db)
    cot = [r[1] for r in conn.execute("PRAGMA table_info(run_history)")]
    dong = conn.execute("SELECT seed, luat_xep FROM run_history").fetchall()
    conn.close()
    assert "luat_xep" in cot
    assert dong == [(7, None)]          # dòng cũ nguyên vẹn, không bị dựng lại


# ------------------------------------------------------------------ 6. run_full_pipeline

def test_run_full_pipeline_tu_choi_khi_luat_khac_mac_dinh(goc, tmp_path):
    slug = ws.tao(goc, "Cứng", _cau_hinh(tier_mode="strict", tiers=["A"]))
    db = ws.duong_dan_db(goc, slug)
    with pytest.raises(RuntimeError, match="luat xep"):
        rp.run_full_pipeline(db, seed=1, output_csv_path=str(tmp_path / "x.csv"))


def test_run_full_pipeline_van_chay_voi_luat_mac_dinh(goc, tmp_path):
    slug = ws.tao(goc, "Mặc định")
    db = ws.duong_dan_db(goc, slug)
    rp.seed_sample_data(db, n_students=20)
    rp.run_full_pipeline(db, seed=1, output_csv_path=str(tmp_path / "x.csv"))


# ------------------------------------------------------------------ 7. nhãn thành công thức Excel

@pytest.mark.parametrize("nhan", ["=1+1", "+cmd", "-x", "@SUM(1)"])
def test_nhan_bat_dau_bang_ky_tu_cong_thuc_bi_tu_choi(goc, nhan):
    import cau_hinh_ws as ch
    cfg = {"labels": {"group": {"vi": nhan}}}
    with pytest.raises(ValueError):
        ch.chuan_hoa(cfg)
    with pytest.raises(ValueError):
        ws.tao(goc, "Xấu", cfg)
    cfg_en = {"labels": {"slot": {"vi": "Dự án", "en": nhan}}}
    with pytest.raises(ValueError):
        ch.chuan_hoa(cfg_en)


def test_nhan_trong_zip_nhap_vao_khong_thanh_cong_thuc(goc, tmp_path):
    """Zip mang cấu hình có nhãn '=...': đọc lại ra mặc định, sổ nhập không có ô công thức."""
    import openpyxl
    import cau_hinh_ws as ch
    import so_nhap
    slug = ws.tao(goc, "Nguồn")
    db = ws.duong_dan_db(goc, slug)
    xau = {"name": "Nguồn", "labels": {"group": {"vi": "=1+1", "en": "=1+1"}}}
    conn = sqlite3.connect(db)
    conn.execute("UPDATE workspace_settings SET value = ? WHERE key = 'config'",
                 (json.dumps(xau),))
    conn.commit()
    conn.close()
    cfg = ch.doc_cau_hinh(db)                    # cấu hình không qua kiểm -> mặc định
    p = str(tmp_path / "so.xlsx")
    so_nhap.ghi_so_nhap(p, [], [], cfg=cfg)
    wb = openpyxl.load_workbook(p)
    assert [c.coordinate for w in wb for r in w.iter_rows() for c in r if c.data_type == "f"] == []
