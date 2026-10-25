"""Sổ nhập có HAI hàng tiêu đề (A13.4). Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.

Quyết định của Truong (25/10/2026), thay đổi hợp đồng Sổ nhập (bất biến 7):
  * sheet học sinh luôn có hai hàng tiêu đề, kể cả khi tắt tính năng: hàng 1 là ô gộp
    "Nguyện vọng k" trên mỗi nhóm, hàng 2 là "CLB", "Điểm thi" và (khi bật) "Điểm quyết tâm";
    cột đầu gộp dọc hai hàng; dữ liệu bắt đầu từ hàng 3; sheet CLB vẫn một hàng;
  * nạp đọc được ba dạng, nhận dạng bằng hàng 1: sổ một hàng cũ, sổ một hàng có "Điểm W k"
    của vòng 2, sổ hai hàng mới; ba dạng chứa cùng dữ liệu thì ra cùng CSV;
  * chèn hay xoá cột làm lệch nhóm thì báo lỗi nêu sheet, cột, nhóm và không nạp gì;
  * cột CSV (wp_k) không đổi; so_nhap.py vẫn chạy một mình.
"""

import base64
import io

import pytest

openpyxl = pytest.importorskip("openpyxl")

import so_nhap  # noqa: E402
from _wharton import bat_wharton, chen_bids, dong_bids, dung_clb, dung_hs  # noqa: E402
from api import PipelineAPI  # noqa: E402

CFG_W = {"rules": {"wharton": True, "max_choices": 10, "max_tests": 5, "score_scope": "per_slot"}}
CFG_TAT = {"rules": {"wharton": False}}
HS = "2. Học sinh"


def _clb(cid, ten, cho=5, buoi=""):
    return {"club_id": cid, "name": ten, "capacity": cho, "reserve_capacity": 0,
            "reserve_group": "", "buoi": buoi}


CLUBS = [_clb("A", "CLB A"), _clb("B", "CLB B"), _clb("C", "CLB C")]


def _nv(cid, thi=False, diem="", **kw):
    return {"club_id": cid, "thi": thi, "diem": diem, **kw}


def _hs(sid, nv):
    return {"student_id": sid, "name": "Em " + sid, "reserve_group": "", "nv": nv}


SV = [_hs("HS1", [_nv("A", True, 7.5), _nv("B"), _nv("C")]),
      _hs("HS2", [_nv("B"), _nv("A", True, "thi")])]
SV_W = [_hs("HS1", [_nv("A", True, 7.5, diem_w=100), _nv("B", diem_w=60), _nv("C", diem_w=40)]),
        _hs("HS2", [_nv("B", diem_w=70), _nv("A", True, "thi", diem_w=30)])]


def _bytes(students=SV, cfg=None, **kw):
    b = io.BytesIO()
    so_nhap.ghi_so_nhap(b, CLUBS, students, cfg=cfg, **kw)
    return b.getvalue()


def _wb(du, **kw):
    return openpyxl.load_workbook(io.BytesIO(du), **kw)


def _doc(du, cfg=None):
    wb = openpyxl.load_workbook(io.BytesIO(du), read_only=True, data_only=True)
    try:
        return so_nhap.doc_so_nhap(wb, cfg=cfg)
    finally:
        wb.close()


def _b64(du):
    return base64.b64encode(du).decode()


def _mot_hang(students, co_w=False, so_nv=3):
    """Dựng tay sổ MỘT hàng (dạng cũ: 'NV k', 'Điểm k', và 'Điểm W k' của vòng 2)."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "1. CLB"
    ws.append(so_nhap.COT_CLB)
    for c in CLUBS:
        ws.append([c["name"], None, c["capacity"], None, None, c["club_id"]])
    wh = wb.create_sheet(HS)
    dau = ["Mã HS", "Họ tên", "Nhóm ưu tiên"]
    for k in range(1, so_nv + 1):
        dau += [f"NV{k}", f"Điểm {k}"] + ([f"Điểm W {k}"] if co_w else [])
    wh.append(dau)
    ten = {c["club_id"]: c["name"] for c in CLUBS}
    for s in students:
        dong = [s["student_id"], s["name"], None]
        for x in s["nv"]:
            dong += [ten[x["club_id"]], (x["diem"] or "thi") if x["thi"] else None]
            if co_w:
                dong.append(x.get("diem_w"))
        wh.append(dong)
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


# ------------------------------------------------------------------ 1. ghi: hai hàng

@pytest.mark.parametrize("cfg,co_w", [(None, False), (CFG_TAT, False), (CFG_W, True)])
def test_ghi_hai_hang_tieu_de(cfg, co_w):
    ws = _wb(_bytes(SV_W if co_w else SV, cfg=cfg))[HS]
    buoc = 3 if co_w else 2
    cac_gop = {str(r) for r in ws.merged_cells.ranges}
    # cột đầu gộp dọc hai hàng
    for cot in "ABC":
        assert f"{cot}1:{cot}2" in cac_gop
    assert [ws.cell(row=1, column=i).value for i in (1, 2, 3)] == ["Mã HS", "Họ tên", "Nhóm ưu tiên"]
    for k in range(1, 4):
        c1 = 4 + buoc * (k - 1)
        assert ws.cell(row=1, column=c1).value == f"Nguyện vọng {k}"
        gop = f"{ws.cell(row=1, column=c1).coordinate}:{ws.cell(row=1, column=c1 + buoc - 1).coordinate}"
        assert gop in cac_gop
        sub = [ws.cell(row=2, column=c1 + j).value for j in range(buoc)]
        assert sub == (["CLB", "Điểm thi", "Điểm quyết tâm"] if co_w else ["CLB", "Điểm thi"])
    # không có số k ở hàng 2
    assert not any(any(ch.isdigit() for ch in str(o.value or "")) for o in ws[2])


def test_ghi_du_lieu_bat_dau_o_hang_3_va_giu_dinh_dang():
    wb = _wb(_bytes(SV))
    ws = wb[HS]
    assert ws["A3"].value == "HS1" and ws["D3"].value == "CLB A" and ws["E3"].value == 7.5
    assert ws["A3"].number_format == "@" and ws["A1"].alignment.horizontal == "center"
    assert ws.freeze_panes == "D3"
    kiem = {(dv.type, str(dv.sqref)) for dv in ws.data_validations.dataValidation}
    assert ("list", "D3:D1500") in kiem or any(t == "list" and s.startswith("D3") for t, s in kiem)
    assert any(t == "custom" and s.startswith("E3") for t, s in kiem)
    # sheet CLB vẫn một hàng
    clb = wb["1. CLB"]
    assert clb.freeze_panes == "A2" and clb["A2"].value == "CLB A"
    assert not clb.merged_cells.ranges


def test_ghi_cong_thuc_kiem_va_to_do_tro_vao_hang_3():
    ws = _wb(_bytes(SV))[HS]
    ct = [f for rng in ws.conditional_formatting for r in rng.rules for f in r.formula]
    assert any(f.startswith('AND(A3<>""') for f in ct)          # trùng mã HS
    assert any("$D3" in f and "$F3" in f for f in ct)            # trùng CLB trên một dòng
    custom = {str(dv.sqref).split(":")[0]: dv.formula1
              for dv in ws.data_validations.dataValidation if dv.type == "custom"}
    assert custom["E3"] == 'OR(ISNUMBER(E3),LOWER(E3)="thi")'


# ------------------------------------------------------------------ 2. đọc ba dạng

def test_doc_hai_hang_moi_giong_mot_hang_cu_khong_diem_w():
    cu = _doc(_mot_hang(SV))
    moi = _doc(_bytes(SV))
    assert cu["loi"] == [] and moi["loi"] == []
    assert so_nhap.thanh_csv(moi) == so_nhap.thanh_csv(cu)
    assert moi["students"][0]["nv"][0] == {"club_id": "A", "thi": True, "diem": "7.5"} or \
        moi["students"][0]["nv"][0]["club_id"] == "A"


def test_doc_hai_hang_moi_giong_mot_hang_vong_hai_co_diem_w():
    cu = _doc(_mot_hang(SV_W, co_w=True))
    moi = _doc(_bytes(SV_W, cfg=CFG_W))
    assert cu["loi"] == [] and moi["loi"] == []
    assert so_nhap.thanh_csv(moi) == so_nhap.thanh_csv(cu)
    assert "wp_1" in so_nhap.thanh_csv(moi)["preferences"]


def test_doc_ba_dang_nhan_dang_bang_hang_1_khong_phu_thuoc_cfg():
    # cfg tắt mà sổ có cột điểm quyết tâm: vẫn đọc (việc bỏ qua là của bước nạp, như vòng 2)
    moi_w = _doc(_bytes(SV_W, cfg=CFG_W), cfg=CFG_TAT)
    assert moi_w["loi"] == []
    assert so_nhap.thanh_csv(moi_w)["preferences"].count("wp_") == 3


def test_doc_hai_hang_nhan_tieu_de_ngoai_le():
    wb = _wb(_bytes(SV))
    ws = wb[HS]
    ws["D1"] = "nguyen vong 1"       # không dấu, chữ thường
    ws["E2"] = "DIEM THI"
    b = io.BytesIO()
    wb.save(b)
    kq = _doc(b.getvalue())
    assert kq["loi"] == []
    assert kq["students"][0]["nv"][0]["thi"] is True


def test_doc_hai_hang_o_trong_nv_k_va_sau_giu_thu_tu():
    kq = _doc(_bytes([_hs("HS1", [_nv("B"), _nv("A", True, 9)])]))
    assert [x["club_id"] for x in kq["students"][0]["nv"]] == ["B", "A"]
    assert kq["students"][0]["nv"][1]["diem"] in ("9", "9.0")


# ------------------------------------------------------------------ 3. lệch nhóm

def _sua(du, ham):
    wb = _wb(du)
    ham(wb[HS])
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


def _ma_loi(kq):
    return [(e["code"], e["params"]) for e in kq["loi"]]


def test_chen_cot_trong_nhom_bao_loi_co_sheet_cot_nhom_va_khong_nap_gi():
    # chèn một cột trống giữa "CLB" và "Điểm thi" của nhóm 2 (Excel mở rộng ô gộp)
    kq = _doc(_sua(_bytes(SV), lambda ws: ws.insert_cols(7)))
    lech = [p for c, p in _ma_loi(kq) if c == "so_nhap_cot_lech_nhom"]
    assert lech, _ma_loi(kq)
    assert lech[0]["sheet"] == HS and lech[0]["k"] == 2 and lech[0]["cot"]
    assert kq["students"] == []                  # có lỗi nghĩa là không đọc ra học sinh nào


def test_xoa_cot_diem_cua_mot_nhom_bao_loi_nhom_thieu_cot():
    kq = _doc(_sua(_bytes(SV), lambda ws: ws.delete_cols(7)))      # "Điểm thi" của nhóm 2
    thieu = [p for c, p in _ma_loi(kq) if c == "so_nhap_nhom_thieu_cot"]
    assert thieu and thieu[0]["sheet"] == HS and thieu[0]["k"] == 2 and thieu[0]["cot"]
    assert kq["students"] == []


def test_tieu_de_la_trong_nhom_bao_loi():
    def doi(ws):
        ws["E2"] = "Ghi chú"
    kq = _doc(_sua(_bytes(SV), doi))
    lech = [p for c, p in _ma_loi(kq) if c == "so_nhap_cot_lech_nhom"]
    assert lech and lech[0]["k"] == 1 and lech[0]["cot"] == "E"


def test_du_lieu_trong_cot_chen_giua_hai_nhom_bao_loi():
    # chèn một cột trống GIỮA nhóm 1 và nhóm 2 rồi gõ vào đó
    def chen(ws):
        ws.insert_cols(6)
        ws["F3"] = "lạc"
    kq = _doc(_sua(_bytes(SV), chen))
    assert any(c == "so_nhap_cot_lech_nhom" for c, _ in _ma_loi(kq)), _ma_loi(kq)


def test_loi_nhom_khong_nap_gi_o_pham_vi_api(api):
    def chen(ws):
        ws.insert_cols(7)
    du = _sua(_bytes(SV), chen)
    kq = api.import_so_nhap(_b64(du))
    assert not kq["ok"]
    assert any(e["code"] in ("so_nhap_cot_lech_nhom", "so_nhap_nhom_thieu_cot") for e in kq["errors"])
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0
        assert cur.execute("SELECT COUNT(*) FROM clubs").fetchone()[0] == 0


# ------------------------------------------------------------------ 4. đi một vòng

def _dung_du_lieu(api):
    dung_clb(api, A=5, B=5, C=5)
    dung_hs(api, "HS1", "HS2", tick={"HS1": ["A"]})
    assert api.submit_preferences("HS1", ["A", "B", "C"])["ok"]
    assert api.submit_preferences("HS2", ["B", "A"])["ok"]
    assert api.submit_club_scores("A", [{"student_id": "HS1", "score": 7.5}])["ok"]
    chen_bids(api, [("HS1", "A", 1, 100), ("HS1", "B", 2, 60), ("HS1", "C", 2, 40),
                    ("HS2", "A", 2, 30), ("HS2", "B", 2, 70)])


def test_xuat_roi_nap_lai_hai_hang_wharton_bids_giong_het(api, tmp_path):
    bat_wharton(api)
    _dung_du_lieu(api)
    xuat = api.export_du_lieu_dau_vao()
    assert xuat["ok"], xuat["errors"]
    with open(xuat["data"]["path"], "rb") as f:
        du = f.read()
    ws = _wb(du)[HS]
    assert ws["D1"].value == "Nguyện vọng 1" and ws["D2"].value == "CLB"
    assert "Điểm quyết tâm" in [ws.cell(row=2, column=i).value for i in range(4, 12)]
    (tmp_path / "moi").mkdir()
    moi = PipelineAPI(str(tmp_path / "moi" / "app.db"))
    bat_wharton(moi)
    kq = moi.import_so_nhap(_b64(du))
    assert kq["ok"], kq["errors"]
    assert dong_bids(moi) == dong_bids(api)
    for bang, sap in (("preferences", "student_id, club_id"), ("club_scores", "club_id, student_id"),
                      ("test_selection", "student_id, club_id"), ("clubs", "club_id")):
        with api._ket_noi_doc() as a, moi._ket_noi_doc() as b:
            try:
                x = [tuple(r) for r in a.execute(f"SELECT * FROM {bang} ORDER BY {sap}")]
            except Exception:
                continue                                     # bảng không có ở bản này
            assert x == [tuple(r) for r in b.execute(f"SELECT * FROM {bang} ORDER BY {sap}")], bang


def test_xuat_tat_wharton_van_hai_hang_khong_co_cot_quyet_tam(api):
    _dung_du_lieu(api)
    with open(api.export_du_lieu_dau_vao()["data"]["path"], "rb") as f:
        ws = _wb(f.read())[HS]
    assert ws["D1"].value == "Nguyện vọng 1" and ws["D2"].value == "CLB"
    assert "Điểm quyết tâm" not in [c.value for c in ws[2]]


def test_mau_khong_hoc_sinh_nap_duoc_danh_sach_clb(api):
    kq = api.import_so_nhap(_b64(_bytes([])))
    assert kq["ok"], kq["errors"]
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM clubs").fetchone()[0] == 3


def test_sheet_hai_hang_khong_hoc_sinh_chi_co_tieu_de_van_doc_duoc():
    kq = _doc(_bytes([]))
    assert kq["loi"] == [] and kq["students"] == []


# ------------------------------------------------------------------ 5. chạy một mình

def test_so_nhap_van_chay_mot_minh():
    import ast
    import os
    goc = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cay = ast.parse(open(os.path.join(goc, "so_nhap.py"), encoding="utf-8").read())
    nap = set()
    for n in cay.body:
        if isinstance(n, ast.Import):
            nap |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.level == 0:
            nap.add((n.module or "").split(".")[0])
    assert not ({"rbda_priority_pipeline", "cau_hinh_ws"} & nap)
