"""SG-6 (H1): giờ và địa điểm của CLB không được rơi mất giữa Phiếu thiết lập CLB và kết quả.

Tái hiện của Fable: phiếu CLB có hai câu "Giờ" và "Địa điểm"; bộ đọc bỏ chúng, nên giáo viên gõ
"15:30-17:00" / "Sân A" mà không chỗ nào trong phần mềm hay tệp xuất hiện lại. Dữ liệu MÔ PHỎNG.
"""
import base64
import os
import shutil
import sqlite3
import sys

import pytest
from _wharton import tat_wharton
from openpyxl import Workbook, load_workbook

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))
sys.path.insert(0, GOC)

import chuyen_phieu_clb as pc  # noqa: E402
import rbda_priority_pipeline as rp  # noqa: E402
import so_nhap  # noqa: E402

GIO, DIA = "15:30-17:00", "Sân A"


@pytest.fixture
def api(api):
    tat_wharton(api)
    return api


def _b64(duong):
    with open(duong, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def _so(tmp_path, voi_gio=True, ten="so.xlsx"):
    clubs = [{"club_id": "a", "name": "CLB A", "capacity": 1, "reserve_capacity": 0,
              "reserve_group": "", "buoi": ""},
             {"club_id": "b", "name": "CLB B", "capacity": 5, "reserve_capacity": 0,
              "reserve_group": "", "buoi": ""}]
    if voi_gio:
        clubs[0].update(gio=GIO, dia_diem=DIA)
    hs = [{"student_id": "HS00%d" % i, "name": "Em %d" % i, "reserve_group": "",
           "nv": [{"club_id": "a", "thi": False, "diem": ""},
                  {"club_id": "b", "thi": False, "diem": ""}]} for i in range(1, 4)]
    p = str(tmp_path / ten)
    so_nhap.ghi_so_nhap(p, clubs, hs)
    return p


def _nap_va_chay(api, tmp_path, **kw):
    r = api.import_so_nhap(_b64(_so(tmp_path, **kw)))
    assert r["ok"], r["errors"]
    assert api.run_pipeline(seed=7)["ok"]


def _chu_cac_o(ws):
    return " | ".join(str(c.value) for row in ws.iter_rows() for c in row if c.value is not None)


# ---- bộ đọc Phiếu CLB -------------------------------------------------------
def _phieu(tmp_path, gio=GIO, dia=DIA):
    wb = Workbook()
    ws = wb.active
    ws.append(pc.TIEU_DE_PHIEU)
    dong = [""] * len(pc.TIEU_DE_PHIEU)
    dong[pc.C_TEN], dong[pc.C_BUOI] = "CLB Cờ vua", "Thứ 3"
    dong[pc.C_GIO], dong[pc.C_DIA_DIEM] = gio, dia
    dong[pc.C_MO_NHOM] = "Không"
    dong[pc.C_CHO], dong[pc.C_LY_DO], dong[pc.C_CAN_THI] = "20", "Phòng", "Không"
    ws.append(dong)
    p = str(tmp_path / "phieu.xlsx")
    wb.save(p)
    return p


def test_phieu_giu_gio_dia_diem_vao_so_nhap(tmp_path):
    kq = pc.doc_phieu_clb(_phieu(tmp_path))
    c = kq["clubs"][0]
    assert (c["gio"], c["dia_diem"]) == (GIO, DIA)
    pc.chuyen_phieu(_phieu(tmp_path), str(tmp_path / "ra"))
    wb = load_workbook(str(tmp_path / "ra" / "SO_NHAP_CLB.xlsx"))
    dau = [c.value for c in wb[so_nhap.SHEET_CLB][1]]
    assert "Giờ" in dau and "Địa điểm" in dau
    du = so_nhap.doc_so_nhap(wb)
    assert du["loi"] == []
    assert (du["clubs"][0]["gio"], du["clubs"][0]["dia_diem"]) == (GIO, DIA)


def test_phieu_bo_trong_gio_thi_so_nhap_khong_them_cot(tmp_path):
    pc.chuyen_phieu(_phieu(tmp_path, gio="", dia=""), str(tmp_path / "ra"))
    dau = [c.value for c in load_workbook(str(tmp_path / "ra" / "SO_NHAP_CLB.xlsx"))
           [so_nhap.SHEET_CLB][1]]
    assert "Giờ" not in dau and "Địa điểm" not in dau       # dữ liệu cũ không thêm cột


# ---- nạp sổ -> CSDL ---------------------------------------------------------
def test_so_cu_khong_co_cot_van_nap_va_cot_la_null(api, tmp_path):
    _nap_va_chay(api, tmp_path, voi_gio=False)
    with api._ket_noi_doc() as cur:
        assert [tuple(r) for r in cur.execute("SELECT gio, dia_diem FROM clubs")] == [(None, None)] * 2


def test_so_co_gio_vao_csdl_va_nap_lai_sach(api, tmp_path):
    _nap_va_chay(api, tmp_path)
    with api._ket_noi_doc() as cur:
        assert tuple(cur.execute("SELECT gio, dia_diem FROM clubs WHERE club_id='a'").fetchone()) == (GIO, DIA)
    # Sổ KHÔNG có cột: giữ giá trị đang lưu (cột vắng = "không biết").
    r = api.import_so_nhap(_b64(_so(tmp_path, voi_gio=False, ten="cu.xlsx")))
    assert r["ok"], r["errors"]
    with api._ket_noi_doc() as cur:
        assert tuple(cur.execute("SELECT gio, dia_diem FROM clubs WHERE club_id='a'").fetchone()) == (GIO, DIA)


# ---- hiển thị ---------------------------------------------------------------
def test_hien_o_bang_clb_quan_ly_ket_qua_danh_sach(api, tmp_path):
    _nap_va_chay(api, tmp_path)
    ql = {c["club_id"]: c for c in api.list_clubs_admin()["data"]}
    assert (ql["a"]["gio"], ql["a"]["dia_diem"]) == (GIO, DIA)
    thong_ke = {c["club_id"]: c for c in api.get_club_fill_stats()["data"]}
    assert (thong_ke["a"]["gio"], thong_ke["a"]["dia_diem"]) == (GIO, DIA)
    assert not thong_ke["b"].get("gio") and not thong_ke["b"].get("dia_diem")
    ds = api.get_danh_sach_clb("a")["data"]
    assert (ds["gio"], ds["dia_diem"]) == (GIO, DIA)
    cac_o = [o for em in api.get_thoi_khoa_bieu()["data"]["hoc_sinh"] for o in em["theo_buoi"].values()]
    o_a = next(o for o in cac_o if o["club_id"] == "a")
    assert (o_a["gio"], o_a["dia_diem"]) == (GIO, DIA)
    assert all("gio" not in o for o in cac_o if o["club_id"] == "b")


def test_hien_o_excel_theo_clb_va_theo_lop(api, tmp_path):
    _nap_va_chay(api, tmp_path)
    r = api.export_ket_qua(str(tmp_path / "kq.xlsx"))
    assert r["ok"], r["errors"]
    wb = load_workbook(r["data"]["path"])
    for ten in ("Theo CLB", "Theo lớp"):
        chu = _chu_cac_o(wb[ten])
        assert GIO in chu and DIA in chu, ten


def test_du_lieu_cu_khong_them_chu_nao(api, tmp_path):
    _nap_va_chay(api, tmp_path, voi_gio=False)
    r = api.export_ket_qua(str(tmp_path / "kq.xlsx"))
    wb = load_workbook(r["data"]["path"])
    for ten in ("Theo CLB", "Theo lớp"):
        assert "Giờ" not in _chu_cac_o(wb[ten]) and "Địa điểm" not in _chu_cac_o(wb[ten])


def test_xuat_so_nhap_nap_lai_giu_gio(api, tmp_path):
    _nap_va_chay(api, tmp_path)
    r = api.export_du_lieu_dau_vao(str(tmp_path / "dv.xlsx"))
    assert r["ok"], r["errors"]
    du = so_nhap.doc_so_nhap(load_workbook(r["data"]["path"]))
    a = next(c for c in du["clubs"] if c["club_id"] == "a")
    assert (a["gio"], a["dia_diem"]) == (GIO, DIA)


# ---- di trú -----------------------------------------------------------------
def _csdl_cu(tmp_path):
    """app.db có dữ liệu nhưng chưa có hai cột (xoá chúng đi bằng cách dựng lại bảng)."""
    from api import PipelineAPI
    db = str(tmp_path / "cu" / "app.db")
    os.makedirs(os.path.dirname(db))
    a = PipelineAPI(db)
    a.create_or_update_club("a", "CLB A", 3, 0, "")
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("ALTER TABLE clubs DROP COLUMN gio")
    conn.execute("ALTER TABLE clubs DROP COLUMN dia_diem")
    conn.commit()
    conn.close()
    return db


def test_di_tru_hai_lan_la_no_op_va_co_sao_luu(tmp_path):
    db = _csdl_cu(tmp_path)
    truoc = set(os.listdir(os.path.dirname(db)))
    lan1 = rp.di_tru_schema(db)
    assert "clubs.gio" in lan1 and "clubs.dia_diem" in lan1
    moi = set(os.listdir(os.path.dirname(db))) - truoc
    assert any(".bak-" in t for t in moi)                      # sao lưu trước khi sửa
    sau1 = set(os.listdir(os.path.dirname(db)))
    assert rp.di_tru_schema(db) == []                          # lần hai: không việc nào
    assert set(os.listdir(os.path.dirname(db))) == sau1        # và không thêm bản sao lưu
    conn = sqlite3.connect(db)
    cot = [r[1] for r in conn.execute("PRAGMA table_info(clubs)")]
    conn.close()
    assert "gio" in cot and "dia_diem" in cot


def test_csdl_cu_dong_clb_cu_giu_nguyen(tmp_path):
    db = _csdl_cu(tmp_path)
    rp.di_tru_schema(db)
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT club_id, name, capacity, gio, dia_diem FROM clubs").fetchall() == [
        ("a", "CLB A", 3, None, None)]
    conn.close()
    shutil.rmtree(os.path.dirname(db))


def test_bang_buoc_1_chi_them_khoa_khi_da_khai():
    from api import PipelineAPI
    cu = PipelineAPI._clb_hien_thi([{"club_id": "x", "name": "X", "capacity": 5}])[0]
    assert "gio" not in cu and "dia_diem" not in cu            # phiếu cũ: dữ liệu y như trước
    moi = PipelineAPI._clb_hien_thi([{"club_id": "x", "name": "X", "capacity": 5, "gio": GIO, "dia_diem": DIA}])[0]
    assert (moi["gio"], moi["dia_diem"]) == (GIO, DIA)
