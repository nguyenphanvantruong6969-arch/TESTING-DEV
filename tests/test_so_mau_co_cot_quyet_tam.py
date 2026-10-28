"""A13.7 — Sổ nhập MẪU luôn có cột "Điểm quyết tâm" (kể cả khi workspace tắt tính năng).

Dữ liệu là dữ liệu MÔ PHỎNG. Điều phải giữ:
  * workspace mặc định (tắt tính năng): `tao_so_nhap_mau` ra sổ có cột trong MỖI nhóm nguyện
    vọng, kèm ghi chú "chỉ dùng khi bật tính năng";
  * `mau_csv/SO_NHAP_CLB.xlsx` và hai sổ `vi_du_*` có cột;
  * tắt tính năng: nạp các sổ đó không lỗi chặn, không có `wharton_bids`, `match_results`
    trùng khít với nạp bộ ba CSV cũ (seed 1, 7, 42);
  * bật tính năng: số điền vào cột được đọc vào `wharton_bids`;
  * `ghi_so_nhap` không tham số mới, và xuất dữ liệu đầu vào: đầu ra KHÔNG đổi.
"""

import base64
import io
import os

import pytest

openpyxl = pytest.importorskip("openpyxl")

import cau_hinh_ws as ch  # noqa: E402
import so_nhap  # noqa: E402
from _so_nhap_dump import chup  # noqa: E402
from api import PipelineAPI  # noqa: E402
from rbda_priority_pipeline import dung_wharton  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAU = os.path.join(GOC, "mau_csv")
TEP_CSV = ("01_danh_sach_CLB.csv", "02_chon_CLB_muon_thi.csv", "03_xep_hang_nguyen_vong.csv")
SO_VI_DU = [os.path.join(MAU, bo, "SO_NHAP_CLB_vi_du.xlsx")
            for bo in ("vi_du_day_du", "vi_du_ca_tuan")]
CAC_SO_MAU = [os.path.join(MAU, "SO_NHAP_CLB.xlsx")] + SO_VI_DU
TEN_COT_W = "Điểm quyết tâm"


def _b64(duong):
    with open(duong, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _hang_2(nguon):
    wb = openpyxl.load_workbook(nguon)
    return [c.value for c in wb["2. Học sinh"][2]]


def _nhom_co_cot_w(hang_2):
    """True nếu MỖI nhóm cột (CLB, Điểm thi, Điểm quyết tâm) đủ ba cột."""
    so_nhom = hang_2.count("CLB")
    return so_nhom > 0 and hang_2.count(TEN_COT_W) == so_nhom


def _doc_huong_dan(nguon):
    wb = openpyxl.load_workbook(nguon)
    return "\n".join(str(r[0].value) for r in wb["Hướng dẫn"].iter_rows() if r[0].value)


# ------------------------------------------------------------------ 1. nút tải sổ mẫu

def test_workspace_mac_dinh_so_mau_co_cot_trong_moi_nhom_va_co_ghi_chu(tmp_path):
    api = PipelineAPI(str(tmp_path / "app.db"), thu_muc_xuat=str(tmp_path))
    assert dung_wharton(api._luat_nghiem()) is False
    kq = api.tao_so_nhap_mau(str(tmp_path / "mau.xlsx"))
    assert kq["ok"], kq["errors"]
    assert _nhom_co_cot_w(_hang_2(kq["data"]["path"]))
    huong_dan = _doc_huong_dan(kq["data"]["path"])
    assert TEN_COT_W in huong_dan and "chỉ dùng khi" in huong_dan.lower()
    assert "wharton" not in huong_dan.lower()


def test_ghi_chu_dung_nhan_cua_workspace_khac():
    b = io.BytesIO()
    cfg = {"labels": {"slot": {"vi": {"l": "dự án", "s": "Dự án", "su": "DỰ ÁN"}}}}
    so_nhap.ghi_so_nhap(b, [], [], cfg=cfg, luon_co_cot_w=True)
    wb = openpyxl.load_workbook(io.BytesIO(b.getvalue()))
    chu = "\n".join(str(r[0].value) for r in wb["Hướng dẫn"].iter_rows() if r[0].value)
    assert TEN_COT_W in chu


# ------------------------------------------------------------------ 2. sổ trong mau_csv/

@pytest.mark.parametrize("duong", CAC_SO_MAU)
def test_so_mau_csv_co_cot_quyet_tam(duong):
    assert _nhom_co_cot_w(_hang_2(duong)), duong
    assert TEN_COT_W in _doc_huong_dan(duong)


# ------------------------------------------------------------------ 3. tắt tính năng

@pytest.mark.parametrize("duong", CAC_SO_MAU[1:])
def test_tat_tinh_nang_nap_so_khong_loi_khong_wharton_bids(api, duong):
    kq = api.import_so_nhap(_b64(duong))
    assert kq["ok"], kq["errors"]
    assert kq["data"]["warnings"] == []
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM wharton_bids").fetchone()[0] == 0


def test_so_mau_trong_nap_duoc_khi_tat_tinh_nang(api):
    kq = api.import_so_nhap(_b64(CAC_SO_MAU[0]))
    assert kq["ok"] or [e["code"] for e in kq["errors"]] == ["so_nhap_khong_co_clb"]


@pytest.mark.parametrize("seed", (1, 7, 42))
@pytest.mark.parametrize("bo", ("vi_du_day_du", "vi_du_ca_tuan"))
def test_tat_tinh_nang_ket_qua_trung_khit_voi_bo_ba_csv(api_factory, bo, seed):
    api_csv = api_factory()
    for ten in TEP_CSV:
        with io.open(os.path.join(MAU, bo, ten), encoding="utf-8-sig") as f:
            assert api_csv.import_csv_auto(f.read())["ok"]
    api_so = api_factory()
    assert api_so.import_so_nhap(_b64(os.path.join(MAU, bo, "SO_NHAP_CLB_vi_du.xlsx")))["ok"]
    assert api_csv.run_pipeline(seed=seed)["ok"] and api_so.run_pipeline(seed=seed)["ok"]

    def ket(a):
        with a._ket_noi_doc() as cur:
            return [tuple(r) for r in cur.execute("SELECT * FROM match_results ORDER BY 1, 2")]
    assert ket(api_so) and ket(api_so) == ket(api_csv)


def test_tat_tinh_nang_so_co_so_o_cot_quyet_tam_chi_canh_bao_khong_chan(api, tmp_path):
    wb = openpyxl.load_workbook(SO_VI_DU[0])
    ws = wb["2. Học sinh"]
    cot_w = next(c.column for c in ws[2] if c.value == TEN_COT_W)
    ws.cell(row=3, column=cot_w).value = 100
    p = tmp_path / "co_so.xlsx"
    wb.save(p)
    kq = api.import_so_nhap(_b64(str(p)))
    assert kq["ok"], kq["errors"]
    assert [w["code"] for w in kq["data"]["warnings"]] == ["csv_wp_bo_qua"]
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM wharton_bids").fetchone()[0] == 0


# ------------------------------------------------------------------ 4. bật tính năng

def test_bat_tinh_nang_so_dien_vao_cot_duoc_doc_vao_wharton_bids(tmp_path):
    ch.ghi_cau_hinh(str(tmp_path / "app.db"), {"rules": {"wharton": True}})
    api = PipelineAPI(str(tmp_path / "app.db"))
    wb = openpyxl.load_workbook(SO_VI_DU[0])
    ws = wb["2. Học sinh"]
    cot_w = next(c.column for c in ws[2] if c.value == TEN_COT_W)
    sid = ws.cell(row=3, column=1).value
    ten_clb = ws.cell(row=3, column=cot_w - 2).value
    ws.cell(row=3, column=cot_w).value = 100
    p = tmp_path / "bat.xlsx"
    wb.save(p)
    kq = api.import_so_nhap(_b64(str(p)))
    assert kq["ok"], kq["errors"]
    with api._ket_noi_doc() as cur:
        dong = [tuple(r) for r in cur.execute(
            "SELECT b.student_id, c.name, b.points FROM wharton_bids b "
            "JOIN clubs c ON c.club_id = b.club_id")]
    assert dong == [(sid, ten_clb, 100)]


# ------------------------------------------------------------------ 5. đường ghi khác KHÔNG đổi

CLUBS = [{"club_id": "a", "name": "CLB A", "capacity": 5, "reserve_capacity": 0,
          "reserve_group": "", "buoi": ""}]
HS = [{"student_id": "HS1", "name": "Em 1", "reserve_group": "",
       "nv": [{"club_id": "a", "thi": True, "diem": 7}]}]


def _ghi(**kw):
    b = io.BytesIO()
    so_nhap.ghi_so_nhap(b, CLUBS, HS, **kw)
    return b.getvalue()


def test_ghi_so_nhap_mac_dinh_khong_co_cot_va_giong_het_khi_truyen_false():
    goc = chup(_ghi())
    assert chup(_ghi(luon_co_cot_w=False)) == goc
    assert TEN_COT_W not in _hang_2(io.BytesIO(_ghi()))
    assert chup(_ghi(cfg=ch.MAC_DINH_TRUONG_HOC)) == goc
    assert TEN_COT_W not in _doc_huong_dan(io.BytesIO(_ghi()))


def test_luon_co_cot_w_khong_doi_phan_con_lai_cua_dong_du_lieu():
    """Có cột thì chỉ THÊM cột; dữ liệu CLB / nguyện vọng / điểm thi y nguyên."""
    def doc(du):
        wb = openpyxl.load_workbook(io.BytesIO(du), read_only=True, data_only=True)
        return so_nhap.doc_so_nhap(wb)
    a, b = doc(_ghi()), doc(_ghi(luon_co_cot_w=True))
    assert a["loi"] == b["loi"] == []
    assert a["clubs"] == b["clubs"]
    assert [(s["student_id"], [(x["club_id"], x["thi"], x["diem"]) for x in s["nv"]])
            for s in a["students"]] == \
           [(s["student_id"], [(x["club_id"], x["thi"], x["diem"]) for x in s["nv"]])
            for s in b["students"]]


def test_xuat_du_lieu_dau_vao_workspace_mac_dinh_khong_co_cot(api, tmp_path):
    assert api.create_student_if_missing("HS1", "Em 1")["ok"]
    assert api.create_or_update_club("A", "CLB A", 5, 0, "", "")["ok"]
    kq = api.export_du_lieu_dau_vao(str(tmp_path / "xuat.xlsx"))
    assert kq["ok"], kq["errors"]
    assert TEN_COT_W not in _hang_2(kq["data"]["path"])
    assert TEN_COT_W not in _doc_huong_dan(kq["data"]["path"])
