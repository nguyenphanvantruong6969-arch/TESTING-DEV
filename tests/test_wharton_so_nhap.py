"""Điểm Wharton (A13, vòng 2): Sổ nhập có cột "Điểm W k", đọc, đổi sang CSV, và xuất ngược.

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.

Điều phải giữ:
  * Wharton TẮT (hoặc không có cfg): sổ GIỐNG HỆT trước vòng 2 — từng ô, độ rộng, kiểm dữ liệu;
  * Wharton BẬT: mỗi nhóm cột thành "NV k · Điểm k · Điểm W k", sheet hướng dẫn nói về hai quỹ;
  * đọc sổ nhận "Điểm W k" (tiêu đề không dấu, hoa thường lẫn lộn); ô sai không chặn cả sổ mà đi
    qua CSV thành cảnh báo `csv_wp_khong_hop_le`;
  * sổ xuất ra nạp lại được y nguyên (`wharton_bids` giống hệt);
  * so_nhap.py vẫn chạy được một mình (test_dong_goi_skill canh).
"""

import base64
import io

import pytest

openpyxl = pytest.importorskip("openpyxl")

import cau_hinh_ws as ch  # noqa: E402
import so_nhap  # noqa: E402
from _so_nhap_dump import chup  # noqa: E402
from _wharton import (bat_wharton, canh_bao, chen_bids, dong_bids, dung_clb, dung_hs)  # noqa: E402
from api import PipelineAPI  # noqa: E402

CFG_W = {"rules": {"wharton": True, "max_choices": 10, "max_tests": 5, "score_scope": "per_slot"}}
CFG_TAT = {"rules": {"wharton": False}}


def _clb(cid, ten, cho=5, buoi=""):
    return {"club_id": cid, "name": ten, "capacity": cho, "reserve_capacity": 0,
            "reserve_group": "", "buoi": buoi}


CLUBS = [_clb("A", "CLB A"), _clb("B", "CLB B"), _clb("C", "CLB C")]


def _nv(cid, thi=False, diem="", **kw):
    return {"club_id": cid, "thi": thi, "diem": diem, **kw}


def _hs(sid, nv):
    return {"student_id": sid, "name": "Em " + sid, "reserve_group": "", "nv": nv}


def _bytes(clubs=CLUBS, students=(), **kw):
    b = io.BytesIO()
    so_nhap.ghi_so_nhap(b, clubs, students, **kw)
    return b.getvalue()


def _doc(du_lieu, cfg=None):
    wb = openpyxl.load_workbook(io.BytesIO(du_lieu), read_only=True, data_only=True)
    try:
        return so_nhap.doc_so_nhap(wb, cfg=cfg)
    finally:
        wb.close()


def _ve_mot_hang(du_lieu):
    """Chuyển sổ hai hàng (A13.4) về sổ MỘT hàng cũ ("NV1", "Điểm 1", "Điểm W 1") để thử đường
    đọc dạng cũ: gỡ ô gộp, ghép hai hàng tiêu đề thành một, xoá hàng 2."""
    wb = openpyxl.load_workbook(io.BytesIO(du_lieu))
    ws = wb["2. Học sinh"]
    for rng in list(ws.merged_cells.ranges):
        ws.unmerge_cells(str(rng))
    mau = {"CLB": "NV%d", "Điểm thi": "Điểm %d", "Điểm quyết tâm": "Điểm W %d"}
    k = 0
    for c in range(1, ws.max_column + 1):
        v1, v2 = ws.cell(row=1, column=c).value, ws.cell(row=2, column=c).value
        if str(v1 or "").startswith("Nguyện vọng"):
            k = int(str(v1).split()[-1])
        if v2:
            ws.cell(row=1, column=c).value = mau[v2] % k
    ws.delete_rows(2)
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


def _hang(du_lieu, sheet, so_hang):
    wb = openpyxl.load_workbook(io.BytesIO(du_lieu))
    return [c.value for c in wb[sheet][so_hang]]


SV_THUONG = [_hs("HS1", [_nv("A", True, 7.5), _nv("B"), _nv("C")]),
             _hs("HS2", [_nv("B"), _nv("A")])]
SV_CO_W = [_hs("HS1", [_nv("A", True, 7.5, diem_w=100), _nv("B", diem_w=60), _nv("C", diem_w=40)]),
           _hs("HS2", [_nv("B", diem_w=70), _nv("A", diem_w=30)])]


# ------------------------------------------------------------------ ghi: tắt thì y hệt

def test_tat_wharton_so_nhap_giong_het_khong_cfg_ke_ca_khi_nv_mang_diem_w():
    goc = chup(_bytes(students=SV_THUONG))
    assert chup(_bytes(students=SV_THUONG, cfg=CFG_TAT)) == goc
    assert chup(_bytes(students=SV_THUONG, cfg=ch.MAC_DINH_TRUONG_HOC)) == goc
    # nv có diem_w mà workspace tắt: cột W KHÔNG xuất hiện, sổ vẫn như cũ
    co_w_nhung_tat = [_hs("HS1", [_nv("A", True, 7.5, diem_w=100), _nv("B", diem_w=60),
                                  _nv("C", diem_w=40)]),
                      _hs("HS2", [_nv("B", diem_w=70), _nv("A", diem_w=30)])]
    assert chup(_bytes(students=co_w_nhung_tat, cfg=CFG_TAT)) == goc


def test_per_person_khong_bao_gio_co_cot_w():
    cfg = {"rules": {"wharton": True, "score_scope": "per_person"}}
    khong_w = {"rules": {"score_scope": "per_person"}}
    assert chup(_bytes(students=SV_CO_W, cfg=cfg)) == chup(_bytes(students=SV_CO_W, cfg=khong_w))


# ------------------------------------------------------------------ ghi: bật

def test_bat_wharton_nhom_cot_thanh_nv_diem_diem_w():
    du = _bytes(students=SV_CO_W, cfg=CFG_W)
    # Hai hàng tiêu đề (A13.4): hàng 1 ô gộp "Nguyện vọng k", hàng 2 CLB / Điểm thi / Điểm quyết tâm.
    dau = _hang(du, "2. Học sinh", 1)
    hang_2 = _hang(du, "2. Học sinh", 2)
    assert dau[:9] == ["Mã HS", "Họ tên", "Nhóm ưu tiên", "Nguyện vọng 1", None, None,
                       "Nguyện vọng 2", None, None]
    assert hang_2[3:9] == ["CLB", "Điểm thi", "Điểm quyết tâm"] * 2
    n_nv = (len(dau) - 3) // 3
    assert len(dau) == 3 + 3 * n_nv and n_nv >= 10
    assert dau[3 + 3 * (n_nv - 1):] == [f"Nguyện vọng {n_nv}", None, None]
    hs1 = _hang(du, "2. Học sinh", 3)
    assert hs1[:12] == ["HS1", "Em HS1", None, "CLB A", 7.5, 100, "CLB B", None, 60,
                        "CLB C", None, 40]
    hs2 = _hang(du, "2. Học sinh", 4)
    assert hs2[3:9] == ["CLB B", None, 70, "CLB A", None, 30]


def test_bat_wharton_co_kiem_so_nguyen_o_cot_w_va_to_mau_rieng():
    du = _bytes(students=SV_CO_W, cfg=CFG_W)
    wb = openpyxl.load_workbook(io.BytesIO(du))
    ws = wb["2. Học sinh"]
    cot_w = [i for i, c in enumerate(ws[2], start=1) if c.value == "Điểm quyết tâm"]
    assert cot_w[:2] == [6, 9]
    cac_kiem = [(dv.type, str(dv.sqref)) for dv in ws.data_validations.dataValidation]
    assert any(t == "whole" and "F3:F" in s for t, s in cac_kiem)       # cột "Điểm quyết tâm" nhóm 1
    assert ws.cell(row=3, column=6).fill.fgColor.rgb != ws.cell(row=3, column=4).fill.fgColor.rgb


def test_bat_wharton_sheet_huong_dan_giai_thich_hai_quy():
    du = _bytes(students=SV_CO_W, cfg=CFG_W)
    hd = "\n".join(str(r[0].value) for r in openpyxl.load_workbook(io.BytesIO(du))["Hướng dẫn"].iter_rows()
                   if r[0].value)
    assert "Điểm quyết tâm" in hd and "100" in hd and "quỹ" in hd
    tat = "\n".join(str(r[0].value) for r in openpyxl.load_workbook(
        io.BytesIO(_bytes(students=SV_THUONG)))["Hướng dẫn"].iter_rows() if r[0].value)
    assert "Điểm quyết tâm" not in tat and "Điểm W" not in tat


def test_bat_wharton_so_nv_theo_tran_thap_van_du_3_cot_moi_nhom():
    cfg = {"rules": {"wharton": True, "max_choices": 3, "max_tests": 5}}
    du = _bytes(students=SV_CO_W, cfg=cfg)
    assert _hang(du, "2. Học sinh", 1) == ["Mã HS", "Họ tên", "Nhóm ưu tiên"] + [
        x for k in (1, 2, 3) for x in (f"Nguyện vọng {k}", None, None)]
    assert _hang(du, "2. Học sinh", 2) == [None] * 3 + ["CLB", "Điểm thi", "Điểm quyết tâm"] * 3


# ------------------------------------------------------------------ đọc

def test_doc_so_nhap_nhan_diem_w_vao_nv():
    du = _bytes(students=SV_CO_W, cfg=CFG_W)
    kq = _doc(du, CFG_W)
    assert kq["loi"] == []
    hs1 = next(s for s in kq["students"] if s["student_id"] == "HS1")
    assert [(x["club_id"], x["thi"], x["diem"], x["diem_w"]) for x in hs1["nv"]] == [
        ("A", True, "7.5", "100"), ("B", False, "", "60"), ("C", False, "", "40")]


@pytest.mark.parametrize("tieu_de", ["diem w 1", "ĐIỂM W1", "Điểm  W   1", "điểm w1"])
def test_doc_nhan_tieu_de_khong_dau_hoa_thuong_lan_lon(tieu_de):
    du = _ve_mot_hang(_bytes(students=SV_CO_W, cfg=CFG_W))      # dạng một hàng của vòng 2
    wb = openpyxl.load_workbook(io.BytesIO(du))
    wb["2. Học sinh"].cell(row=1, column=6).value = tieu_de
    b = io.BytesIO()
    wb.save(b)
    kq = _doc(b.getvalue(), CFG_W)
    assert kq["loi"] == []
    assert kq["students"][0]["nv"][0]["diem_w"] == "100"


def test_doc_khong_phu_thuoc_cfg_van_nhan_cot_w():
    du = _bytes(students=SV_CO_W, cfg=CFG_W)
    kq = _doc(du, cfg=None)        # workspace chưa bật: việc bỏ qua do bước nạp, không phải do đọc
    assert kq["loi"] == [] and kq["students"][0]["nv"][0]["diem_w"] == "100"


def test_doc_so_khong_co_cot_w_nv_giu_nguyen_khong_co_khoa_moi():
    kq = _doc(_bytes(students=SV_THUONG))
    for s in kq["students"]:
        assert "diem_w_mo_coi" not in s
        for x in s["nv"]:
            assert set(x) == {"club_id", "thi", "diem"}


def test_doc_o_w_sai_khong_chan_ca_so_chuyen_nguyen_van_xuong_duoi():
    sv = [_hs("HS1", [_nv("A", diem_w="12,5"), _nv("B", diem_w="abc")])]
    kq = _doc(_bytes(students=sv, cfg=CFG_W), CFG_W)
    assert kq["loi"] == []
    assert [x["diem_w"] for x in kq["students"][0]["nv"]] == ["12,5", "abc"]


def test_doc_o_w_ma_nv_trong_duoc_ghi_lai_de_canh_bao():
    du = _bytes(students=[_hs("HS1", [_nv("A", diem_w=100)])], cfg=CFG_W)
    wb = openpyxl.load_workbook(io.BytesIO(du))
    wb["2. Học sinh"].cell(row=3, column=9).value = 50          # "Điểm quyết tâm" nhóm 2 mà CLB trống
    b = io.BytesIO()
    wb.save(b)
    kq = _doc(b.getvalue(), CFG_W)
    assert kq["loi"] == []
    assert kq["students"][0]["diem_w_mo_coi"] == ["Điểm quyết tâm (Nguyện vọng 2)"]
    # sổ MỘT hàng cũ vẫn gọi cột bằng tên cũ
    cu = _ve_mot_hang(_bytes(students=[_hs("HS1", [_nv("A", diem_w=100)])], cfg=CFG_W))
    wb = openpyxl.load_workbook(io.BytesIO(cu))
    wb["2. Học sinh"].cell(row=2, column=9).value = 50
    b = io.BytesIO()
    wb.save(b)
    assert _doc(b.getvalue(), CFG_W)["students"][0]["diem_w_mo_coi"] == ["Điểm W 2"]


def test_per_person_cot_w_co_chu_thi_bi_chan_nhu_cot_diem_sai_che_do():
    cfg = {"rules": {"score_scope": "per_person"}}
    du = _bytes(students=[_hs("HS1", [_nv("A")])], cfg=cfg)
    wb = openpyxl.load_workbook(io.BytesIO(du))
    ws = wb["2. Học sinh"]
    ws.cell(row=1, column=ws.max_column + 1).value = "Điểm W 1"
    ws.cell(row=3, column=ws.max_column).value = 50
    b = io.BytesIO()
    wb.save(b)
    kq = _doc(b.getvalue(), cfg)
    assert [e["code"] for e in kq["loi"]] == ["so_nhap_diem_sai_che_do"]


# ------------------------------------------------------------------ đổi sang CSV

def test_thanh_csv_co_wp_k_di_cap_pref_k():
    kq = _doc(_bytes(students=SV_CO_W, cfg=CFG_W), CFG_W)
    csv_text = so_nhap.thanh_csv(kq)
    dong = csv_text["preferences"].splitlines()
    assert dong[0] == "student_id,name,reserve_group,pref_1,pref_2,pref_3,wp_1,wp_2,wp_3"
    assert dong[1] == "HS1,Em HS1,,A,B,C,100,60,40"
    assert dong[2] == "HS2,Em HS2,,B,A,,70,30,"


def test_thanh_csv_khong_co_cot_w_thi_dau_ra_y_nhu_cu():
    kq = _doc(_bytes(students=SV_THUONG))
    dong = so_nhap.thanh_csv(kq)["preferences"].splitlines()
    assert dong[0] == "student_id,name,reserve_group,pref_1,pref_2,pref_3"
    assert "wp" not in so_nhap.thanh_csv(kq)["preferences"]


# ------------------------------------------------------------------ qua API

def _b64(du):
    return base64.b64encode(du).decode()


def _dung_du_lieu(api):
    dung_clb(api, A=5, B=5, C=5)
    dung_hs(api, "HS1", "HS2", tick={"HS1": ["A"]})
    assert api.submit_preferences("HS1", ["A", "B", "C"])["ok"]
    assert api.submit_preferences("HS2", ["B", "A"])["ok"]
    assert api.submit_club_scores("A", [{"student_id": "HS1", "score": 7.5}])["ok"]
    chen_bids(api, [("HS1", "A", 1, 100), ("HS1", "B", 2, 60), ("HS1", "C", 2, 40),
                    ("HS2", "A", 2, 30), ("HS2", "B", 2, 70)])


def test_xuat_roi_nap_lai_vao_workspace_moi_wharton_bids_giong_het(api, tmp_path):
    bat_wharton(api)
    _dung_du_lieu(api)
    xuat = api.export_du_lieu_dau_vao()
    assert xuat["ok"], xuat["errors"]
    with open(xuat["data"]["path"], "rb") as f:
        du = f.read()
    assert "Điểm quyết tâm" in _hang(du, "2. Học sinh", 2)     # cột có mặt vì workspace bật

    (tmp_path / "moi").mkdir()
    moi = PipelineAPI(str(tmp_path / "moi" / "app.db"))
    bat_wharton(moi)
    kq = moi.import_so_nhap(_b64(du))
    assert kq["ok"], kq["errors"]
    assert dong_bids(moi) == dong_bids(api)
    assert [w for w in kq["data"]["warnings"] if w["code"].startswith("wharton_")] == []


def test_xuat_khi_tat_wharton_khong_co_cot_w(api):
    _dung_du_lieu(api)                                         # bảng có dòng nhưng workspace tắt
    with open(api.export_du_lieu_dau_vao()["data"]["path"], "rb") as f:
        du = f.read()
    dau = _hang(du, "2. Học sinh", 1) + _hang(du, "2. Học sinh", 2)
    assert not any(str(c).startswith(("Điểm W", "Điểm quyết tâm")) for c in dau)


def test_nap_so_o_w_sai_thanh_canh_bao_csv_wp_khong_hop_le(api):
    bat_wharton(api)
    sv = [_hs("HS1", [_nv("A", diem_w="12,5"), _nv("B", diem_w=100)])]
    kq = api.import_so_nhap(_b64(_bytes(students=sv, cfg=CFG_W)))
    assert kq["ok"], kq["errors"]
    ds = canh_bao(kq, "csv_wp_khong_hop_le")
    assert [(e["params"]["student_id"], e["params"]["club_id"], e["params"]["gia_tri"])
            for e in ds] == [("HS1", "A", "12,5")]
    assert dong_bids(api) == [("HS1", "B", 2, 100)]


def test_nap_so_o_w_mo_coi_thanh_canh_bao_khong_co_nguyen_vong(api):
    bat_wharton(api)
    du = _bytes(students=[_hs("HS1", [_nv("A", diem_w=100)])], cfg=CFG_W)
    wb = openpyxl.load_workbook(io.BytesIO(du))
    wb["2. Học sinh"].cell(row=3, column=9).value = 50
    b = io.BytesIO()
    wb.save(b)
    kq = api.import_so_nhap(_b64(b.getvalue()))
    assert kq["ok"], kq["errors"]
    ds = canh_bao(kq, "csv_wp_khong_co_nguyen_vong")
    assert [(e["params"]["student_id"], e["params"]["cot"]) for e in ds] == [
        ("HS1", "Điểm quyết tâm (Nguyện vọng 2)")]


def test_nap_so_khi_workspace_tat_bo_qua_kem_canh_bao_va_xem_truoc_noi_truoc(api):
    du = _bytes(students=SV_CO_W, cfg=CFG_W)
    pv = api.xem_truoc_so_nhap(_b64(du))
    assert pv["ok"]
    assert [e["params"]["n"] for e in pv["data"]["canh_bao"] if e["code"] == "csv_wp_bo_qua"] == [5]
    kq = api.import_so_nhap(_b64(du))
    assert kq["ok"], kq["errors"]
    assert [e["params"]["n"] for e in canh_bao(kq, "csv_wp_bo_qua")] == [5]
    assert dong_bids(api) == []
