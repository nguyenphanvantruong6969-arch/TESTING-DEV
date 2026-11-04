# -*- coding: utf-8 -*-
"""T4-K1: cột `lop` TUỲ CHỌN (cột thứ 20, ngoài COT_RAW) đi từ tab hoc_sinh -> RAW -> cột Lớp của Sổ.

Kiểm: skill đọc `lop` khi có (chuẩn hoá bằng chuan_hoa_lop của phần mềm), lấy lớp của PHIẾU GIỮ, báo
khi các phiếu của một mã ghi lớp khác nhau; thiếu cột thì Sổ y như cũ; thư mục nhiều phần cũng đọc được.
Phía .gs: chamTheoCLB(ghiLop) mặc định TẮT (RAW 19 cột, như cũ), bật thì thêm cột `lop` từ tab hoc_sinh;
COT_RAW của .gs vẫn bằng COT_RAW của skill; tao_google_forms.noi_dung() trùng tệp .gs.
"""

import json
import os
import shutil
import subprocess

import pytest

openpyxl = pytest.importorskip("openpyxl")

import test_skill_xu_li_raw as goc  # noqa: E402
from test_skill_xu_li_raw import Raw, ghi_dap_an, ghi_clb  # noqa: E402
from test_skill_tao_google_form import CHAM  # noqa: E402

xr = pytest.fixture(scope="module", name="xr")(goc.xr.__wrapped__)
de = pytest.fixture(scope="module", name="de")(goc.de.__wrapped__)

GOC = goc.GOC


def _raw(xr, de, lop_theo_phieu, duong, tieu_de_lop=True):
    """Raw 3 phiếu (HS001, HS002, và phiếu thứ ba tuỳ kịch bản). lop_theo_phieu: [(sid, lớp)]."""
    r = Raw(xr, de)
    T2 = [c["id"] for c in de[0]["clubs"]]
    for sid, _ in lop_theo_phieu:
        r.phieu(sid, "Tên " + sid, {"thu_2": {"tick": [T2[0]], "lam": {T2[0]: 2}}})
    lop_cua_dong = {i + 1: lop for i, (_, lop) in enumerate(lop_theo_phieu)}   # phieu_so -> lớp
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(xr.COT_RAW + (["lop"] if tieu_de_lop else []))
    for d in r.rows:
        ws.append([str(x) for x in d] + ([lop_cua_dong[d[0]]] if tieu_de_lop else []))
    wb.save(duong)
    return T2


def _chay(xr, de, tmp_path, lop_theo_phieu, **kw):
    _raw(xr, de, lop_theo_phieu, str(tmp_path / "RAW_PHIEU.xlsx"), **kw)
    ghi_dap_an(de, str(tmp_path / "DAP_AN.xlsx"))
    ghi_clb(de, str(tmp_path / "01.xlsx"))
    ra = tmp_path / "ra"
    assert xr.main(["--raw", str(tmp_path / "RAW_PHIEU.xlsx"), "--dap-an", str(tmp_path / "DAP_AN.xlsx"),
                    "--clb", str(tmp_path / "01.xlsx"), "--ra", str(ra)]) == 0
    return ra


def _sheet_hs(ra):
    wb = openpyxl.load_workbook(str(ra / "SO_NHAP_CLB.xlsx"), read_only=True, data_only=True)
    try:
        return [list(r) for r in wb[wb.sheetnames[1]].iter_rows(values_only=True)]
    finally:
        wb.close()


def _lop_theo_ma(ra):
    dong = _sheet_hs(ra)
    # Hai hàng tiêu đề (A13.4): hàng 1 chứa "Lớp" ở cột C khi có cột lớp.
    assert dong[0][2] == "Lớp", dong[0][:4]
    return {r[0]: r[2] for r in dong[2:] if r[0]}


def test_co_cot_lop_ghi_vao_cot_lop_cua_so_da_chuan_hoa(tmp_path, xr, de):
    ra = _chay(xr, de, tmp_path, [("HS001", " 10a1 "), ("HS002", "11A2")])
    assert _lop_theo_ma(ra) == {"HS001": "10A1", "HS002": "11A2"}
    # Cột `lop` không đụng COT_RAW: skill vẫn nhận raw 19 cột.
    assert len(xr.COT_RAW) == 19 and "lop" not in xr.COT_RAW


def test_khong_co_cot_lop_so_y_nhu_cu(tmp_path, xr, de):
    ra = _chay(xr, de, tmp_path, [("HS001", ""), ("HS002", "")], tieu_de_lop=False)
    dong = _sheet_hs(ra)
    assert "Lớp" not in [x for r in dong[:2] for x in r]
    # So với đúng cách cũ: thanh_so + ghi_so_nhap(co_nhom=False), không co_lop.
    _, hs, _ = xr.chay(str(tmp_path / "RAW_PHIEU.xlsx"), str(tmp_path / "ra2"),
                       str(tmp_path / "DAP_AN.xlsx"), str(tmp_path / "01.xlsx"))
    clb = [{"club_id": c["id"], "name": c["name"], "capacity": "10", "reserve_capacity": "0",
            "reserve_group": "", "buoi": d["ma"]} for d in de for c in d["clubs"]]
    clubs, students = xr.sdl.thanh_so(clb, hs)
    xr.so_nhap.ghi_so_nhap(str(tmp_path / "cu.xlsx"), clubs, students, co_nhom=False)
    cu = openpyxl.load_workbook(str(tmp_path / "cu.xlsx"))
    moi = openpyxl.load_workbook(str(ra / "SO_NHAP_CLB.xlsx"))
    assert cu.sheetnames == moi.sheetnames
    for ten in cu.sheetnames:
        a = [[o.value for o in r] for r in cu[ten].iter_rows()]
        b = [[o.value for o in r] for r in moi[ten].iter_rows()]
        assert a == b, ten
    assert "các phiếu ghi lớp khác nhau" not in (ra / "BAO_CAO_BAT_THUONG.md").read_text(encoding="utf-8")


def test_lop_rong_van_ghi_cot_nhung_o_trong(tmp_path, xr, de):
    ra = _chay(xr, de, tmp_path, [("HS001", ""), ("HS002", "   ")])
    assert _lop_theo_ma(ra) == {"HS001": None, "HS002": None}


def test_lop_khac_nhau_giua_cac_phieu_lay_phieu_giu_va_bao(tmp_path, xr, de):
    # HS001 nộp hai lần: phiếu 1 (giữ) ghi 10A1, phiếu 3 ghi 11A9.
    ra = _chay(xr, de, tmp_path, [("HS001", "10A1"), ("HS002", "11A2"), ("HS001", "11A9")])
    assert _lop_theo_ma(ra) == {"HS001": "10A1", "HS002": "11A2"}
    bc = (ra / "BAO_CAO_BAT_THUONG.md").read_text(encoding="utf-8")
    assert "các phiếu ghi lớp khác nhau" in bc
    assert "HS001: phiếu 1 ghi 10A1; phiếu 3 ghi 11A9" in bc
    # Cùng lớp (chỉ khác hoa thường / khoảng trắng) thì KHÔNG báo.
    (tmp_path / "b").mkdir()
    ra2 = _chay(xr, de, tmp_path / "b", [("HS001", "10A1"), ("HS001", " 10a1")])
    assert "các phiếu ghi lớp khác nhau" not in (ra2 / "BAO_CAO_BAT_THUONG.md").read_text(encoding="utf-8")


def test_lop_o_phieu_giu_trong_thi_khong_lay_lop_phieu_bo(tmp_path, xr, de):
    """Phiếu giữ trống lớp: ô Lớp để trống (không mượn lớp của phiếu bị bỏ), nhưng vẫn ra cảnh báo? Không:
    chỉ một lớp khác rỗng nên không có gì để so."""
    ra = _chay(xr, de, tmp_path, [("HS001", ""), ("HS001", "11A9")])
    assert _lop_theo_ma(ra) == {"HS001": None}


def test_thu_muc_nhieu_phan_co_cot_lop(tmp_path, xr, de):
    _raw(xr, de, [("HS001", "10A1"), ("HS002", "10a2"), ("HS003", "11A3")], str(tmp_path / "g.xlsx"))
    _, dong = xr.doc_bang(str(tmp_path / "g.xlsx"))
    tieu_de = xr.COT_RAW + ["lop"]
    thu = tmp_path / "bo"
    thu.mkdir()
    phan1 = [d for d in dong if d["phieu_so"] in ("1", "2")]
    phan2 = [d for d in dong if d["phieu_so"] == "3"]
    for ten, ds in (("RAW_PHIEU_ky_p01.csv", phan1), ("RAW_PHIEU_ky_p02.csv", phan2)):
        import test_skill_xu_li_raw_nhieu_phan as np_
        np_._ghi_csv(str(thu / ten), tieu_de, [[d[c] for c in tieu_de] for d in ds])
    ghi_dap_an(de, str(tmp_path / "DAP_AN.xlsx"))
    ghi_clb(de, str(tmp_path / "01.xlsx"))
    ra = tmp_path / "ra"
    assert xr.main(["--raw", str(thu), "--dap-an", str(tmp_path / "DAP_AN.xlsx"),
                    "--clb", str(tmp_path / "01.xlsx"), "--ra", str(ra)]) == 0
    assert _lop_theo_ma(ra) == {"HS001": "10A1", "HS002": "10A2", "HS003": "11A3"}


# ------------------------------------------------------------------ phía .gs

def test_gs_cot_raw_van_19_va_noi_dung_trung_tep_gs():
    import re
    import sys
    sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))
    import tao_google_forms as tg
    gs = open(os.path.join(GOC, "mau_forms_thi_clb", "TAO_GOOGLE_FORM.gs"), encoding="utf-8").read()
    assert tg.noi_dung() == gs
    cot = re.findall(r"'([a-z_]+)'", re.search(r"const COT_RAW = \[(.*?)\];", gs, re.S).group(1))
    assert len(cot) == 19 and "lop" not in cot
    assert "function chamTheoCLB(ghiLop)" in gs and "function chamTheoCLBCoLop()" in gs


KICH_BAN_LOP = r"""
const hs=[['ma_hs','ho_ten','lop'],['HS1','An','10a1 '],['HS2','Bình','11A2']];
const tab={getDataRange:()=>({getValues:()=>hs})};
if (process.env.KHONG_TAB) { global.SpreadsheetApp.getActiveSpreadsheet=()=>({getSheetByName:()=>null}); }
else { global.SpreadsheetApp.getActiveSpreadsheet=()=>({getSheetByName:n=>n==='hoc_sinh'?tab:null}); }
global.__goi = process.env.GOI;
try { if (process.env.GOI==='bat') chamTheoCLB(true); else if (process.env.GOI==='menu') chamTheoCLB({event:1}); else if (process.env.GOI==='coLop') chamTheoCLBCoLop(); else chamTheoCLB(); }
catch (e) { console.log('LOI', e.message); process.exit(0); }
const raw=by('RAW_PHIEU');
console.log('RAW', JSON.stringify({tieu: raw[0], n: raw.length, dong: raw.slice(1).map(r=>[r[3], r[r.length-1], r.length])}));
"""


def _chay_gs(tmp_path, goi, khong_tab=False):
    js = tmp_path / "cham.js"
    kich_ban = CHAM.replace("chamTheoCLB();\nconst by=", "const by=").split("console.log('HS'")[0] + KICH_BAN_LOP
    js.write_text(kich_ban, encoding="utf-8")
    gs = os.path.join(GOC, "mau_forms_thi_clb", "TAO_GOOGLE_FORM.gs")
    env = dict(os.environ, GOI=goi, **({"KHONG_TAB": "1"} if khong_tab else {}))
    return subprocess.run(["node", str(js), gs, str(tmp_path / "x.json")], capture_output=True,
                          text=True, encoding="utf-8", check=True, env=env).stdout


def _raw_gs(out):
    return json.loads(next(l for l in out.splitlines() if l.startswith("RAW ")).split(" ", 1)[1])


@pytest.mark.skipif(shutil.which("node") is None, reason="cần Node.js để chạy bản giả lập FormApp")
def test_gs_mac_dinh_tat_raw_19_cot_ke_ca_khi_menu_truyen_su_kien(tmp_path):
    for goi in ("tat", "menu"):          # không đối số; đối tượng sự kiện KHÔNG được bật nhầm
        raw = _raw_gs(_chay_gs(tmp_path, goi))
        assert len(raw["tieu"]) == 19 and raw["tieu"][-1] == "ghi_chu"
        assert {d[2] for d in raw["dong"]} == {19}


@pytest.mark.skipif(shutil.which("node") is None, reason="cần Node.js để chạy bản giả lập FormApp")
def test_gs_bat_ghi_cot_lop_tu_tab_hoc_sinh(tmp_path):
    for goi in ("bat", "coLop"):
        raw = _raw_gs(_chay_gs(tmp_path, goi))
        assert len(raw["tieu"]) == 20 and raw["tieu"][-1] == "lop" and raw["tieu"][:19] == _cot_raw()
        lop = {d[0]: d[1] for d in raw["dong"]}
        assert lop == {"HS1": "10a1", "HS2": "11A2"}    # gs chỉ cắt khoảng trắng; chuẩn hoá là việc của skill
        assert {d[2] for d in raw["dong"]} == {20}


def _cot_raw():
    return goc.xr.__wrapped__().COT_RAW


@pytest.mark.skipif(shutil.which("node") is None, reason="cần Node.js để chạy bản giả lập FormApp")
def test_gs_bat_ma_thieu_tab_hoc_sinh_thi_bao_loi_khong_xuat(tmp_path):
    out = _chay_gs(tmp_path, "bat", khong_tab=True)
    assert "LOI" in out and "hoc_sinh" in out and "RAW " not in out
