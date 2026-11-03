# -*- coding: utf-8 -*-
"""A14 (C2) — các Sổ / bộ CSV MẪU người dùng thấy có cột Lớp MÔ PHỎNG.

Lớp do `du_lieu_test/them_lop_vao_mau.py` gán bằng seed cố định (DỮ LIỆU MÔ PHỎNG, không phải
khảo sát thật). Điều phải giữ: cột đúng chỗ (Sổ: ngay sau Họ tên; CSV: ngay sau reserve_group),
mọi em có lớp, nạp không còn cảnh báo thiếu lớp, và LỚP KHÔNG ĐỔI KẾT QUẢ XẾP: `match_results`
của từng bộ giống từng dòng với số đã chốt TRƯỚC khi thêm lớp. `bo_sach` (dữ liệu đề tài)
không bị đụng."""

import base64
import csv
import hashlib
import io
import os
import re
import sqlite3

import openpyxl
import pytest

import so_nhap
from api import PipelineAPI

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAU = os.path.join(GOC, "mau_csv")
DLT = os.path.join(GOC, "du_lieu_test")
RE_LOP = re.compile(r"^1[0-2]A[1-3]$")
TEN3 = ("danh_sach_CLB", "chon_CLB_muon_thi", "xep_hang_nguyen_vong")

# (thư mục, mẫu tên bộ ba, băm match_results seed 42 chốt TRƯỚC khi thêm lớp, số dòng)
BO = {
    "huong_dan": (os.path.join(DLT, "vi_du_huong_dan"), "VIDU_0%d_%s.csv",
                  "0306924fe367540bf98632c1ea58f32a81465af556c7a26ba4a6c3c68324a897", 10),
    "day_du": (os.path.join(MAU, "vi_du_day_du"), "0%d_%s.csv",
               "6fc9386ef44ad07eb58af592f6161f10383d8a841763561c1a839c1cae3e016a", 72),
    "ca_tuan": (os.path.join(MAU, "vi_du_ca_tuan"), "0%d_%s.csv",
                "e178ee2eb3d664b4b1dd15e6cd5c51f16c6160219706233a23750d84ba54d7da", 360),
}
NHIEU_BUOI = ("06_danh_sach_club_nhieu_buoi", "07_chon_club_thi_nhieu_buoi",
              "08_nguyen_vong_nhieu_buoi")
BAM_NHIEU_BUOI = "db12f67a104a4aea03c8898f4467de39f84b1e20662e5a123e1dcb6e53661371"
SO_MAU = [os.path.join(MAU, "SO_NHAP_CLB.xlsx"),
          os.path.join(MAU, "vi_du_day_du", "SO_NHAP_CLB_vi_du.xlsx"),
          os.path.join(MAU, "vi_du_ca_tuan", "SO_NHAP_CLB_vi_du.xlsx"),
          os.path.join(DLT, "vi_du_huong_dan", "SO_NHAP_VIDU.xlsx")]
SO_CO_HS = SO_MAU[1:]            # sổ mẫu trống không có em nào


def _doc_csv(p):
    with io.open(p, encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames), list(r)


def _tep_hs(bo):
    d, mau, _, _ = BO[bo]
    return [os.path.join(d, mau % (i, TEN3[i - 1])) for i in (2, 3)]


def _tat_ca_tep_hs():
    return [t for b in BO for t in _tep_hs(b)] + [
        os.path.join(MAU, NHIEU_BUOI[1] + ".csv"), os.path.join(MAU, NHIEU_BUOI[2] + ".csv")]


def _bam(api):
    c = sqlite3.connect(api.db_path)
    try:
        rows = c.execute("SELECT student_id, buoi, club_id, matched_tier, rank_in_student_pref "
                         "FROM match_results ORDER BY 1, 2").fetchall()
    finally:
        c.close()
    return hashlib.sha256(repr(rows).encode()).hexdigest(), len(rows)


def _nap_csv(api, tep, bo_lop=True):
    for p in tep:
        with io.open(p, encoding="utf-8-sig") as f:
            txt = f.read()
        if not bo_lop:                          # bản KHÔNG có cột lớp, để so sánh
            dong = list(csv.reader(io.StringIO(txt)))
            if "class_id" in dong[0]:
                j = dong[0].index("class_id")
                dong = [r[:j] + r[j + 1:] for r in dong]
            buf = io.StringIO()
            csv.writer(buf).writerows(dong)
            txt = buf.getvalue()
        kq = api.import_csv_auto(txt)
        assert kq["ok"], (p, kq.get("errors"))


@pytest.fixture
def api(tmp_path):
    return PipelineAPI(str(tmp_path / "app.db"))


# ------------------------------------------------------------------ CSV mẫu

@pytest.mark.parametrize("tep", _tat_ca_tep_hs(), ids=os.path.basename)
def test_csv_mau_co_cot_class_id_ngay_sau_reserve_group_va_moi_em_co_lop(tep):
    tieu, dong = _doc_csv(tep)
    j = tieu.index("reserve_group")
    assert tieu[j + 1] == "class_id", tieu[:6]
    assert dong and all(RE_LOP.match(r["class_id"]) for r in dong), tep


def test_hai_tep_hoc_sinh_cung_bo_cho_cung_mot_lop():
    for bo in BO:
        a, b = (_doc_csv(t)[1] for t in _tep_hs(bo))
        assert {r["student_id"]: r["class_id"] for r in a} == {
            r["student_id"]: r["class_id"] for r in b}, bo
    a, b = (_doc_csv(os.path.join(MAU, f + ".csv"))[1] for f in NHIEU_BUOI[1:])
    assert {r["student_id"]: r["class_id"] for r in a} == {r["student_id"]: r["class_id"] for r in b}


def test_xlsx_cua_bo_huong_dan_cung_co_cot_lop():
    for ten in ("VIDU_02_chon_CLB_muon_thi.xlsx", "VIDU_03_xep_hang_nguyen_vong.xlsx"):
        ws = openpyxl.load_workbook(os.path.join(DLT, "vi_du_huong_dan", ten)).worksheets[0]
        tieu = [c.value for c in ws[1]]
        assert tieu[tieu.index("reserve_group") + 1] == "class_id"
        assert all(RE_LOP.match(str(ws.cell(row=i, column=tieu.index("class_id") + 1).value))
                   for i in range(2, ws.max_row + 1))


def test_bo_sach_khong_bi_dung_den():
    d = os.path.join(DLT, "bo_sach")
    for ten in os.listdir(d):
        if ten.endswith(".csv"):
            assert "class_id" not in _doc_csv(os.path.join(d, ten))[0], ten


# ------------------------------------------------------------------ Sổ mẫu

@pytest.mark.parametrize("so", SO_MAU, ids=lambda p: os.path.relpath(p, GOC))
def test_so_mau_co_cot_lop_ngay_sau_ho_ten(so):
    ws = openpyxl.load_workbook(so)[so_nhap.SHEET_HS]
    assert [c.value for c in ws[1]][:3] == ["Mã HS", "Họ tên", "Lớp"]


@pytest.mark.parametrize("so", SO_CO_HS, ids=lambda p: os.path.relpath(p, GOC))
def test_so_mau_moi_em_co_lop(so):
    d = so_nhap.doc_so_nhap(openpyxl.load_workbook(so))
    assert not d["loi"] and d["students"]
    assert all(RE_LOP.match(s["class_id"] or "") for s in d["students"])


@pytest.mark.parametrize("so", SO_CO_HS, ids=lambda p: os.path.relpath(p, GOC))
def test_nap_so_mau_khong_canh_bao_thieu_lop_va_lop_khop_csv(api, so):
    with open(so, "rb") as f:
        kq = api.import_so_nhap(base64.b64encode(f.read()).decode())
    assert kq["ok"], kq
    assert "so_nhap_canh_bao_thieu_lop" not in [w["code"] for w in kq["data"]["warnings"]]
    c = sqlite3.connect(api.db_path)
    n_khong_lop = c.execute("SELECT COUNT(*) FROM students WHERE class_id IS NULL").fetchone()[0]
    c.close()
    assert n_khong_lop == 0


# ------------------------------------------------------------------ BẤT BIẾN: lớp không đổi kết quả

@pytest.mark.parametrize("bo", sorted(BO))
def test_match_results_giong_het_truoc_khi_them_lop(api, bo):
    d, mau, bam, n = BO[bo]
    _nap_csv(api, [os.path.join(d, mau % (i, TEN3[i - 1])) for i in (1, 2, 3)])
    assert api.run_pipeline(seed=42)["ok"]
    assert _bam(api) == (bam, n)


def test_match_results_nhieu_buoi_giong_het_truoc_khi_them_lop(api):
    _nap_csv(api, [os.path.join(MAU, f + ".csv") for f in NHIEU_BUOI])
    assert api.run_pipeline(seed=42)["ok"]
    assert _bam(api) == (BAM_NHIEU_BUOI, 18)


@pytest.mark.parametrize("bo", sorted(BO))
def test_co_va_khong_co_cot_lop_cho_cung_ket_qua(api_factory, bo):
    d, mau, _, _ = BO[bo]
    tep = [os.path.join(d, mau % (i, TEN3[i - 1])) for i in (1, 2, 3)]
    a, b = api_factory(), api_factory()
    _nap_csv(a, tep, bo_lop=True)
    _nap_csv(b, tep, bo_lop=False)
    a.run_pipeline(seed=7), b.run_pipeline(seed=7)
    assert _bam(a) == _bam(b)


# ------------------------------------------------------------------ script

def test_script_gan_lop_xac_dinh_va_dung_khuon():
    import sys
    sys.path.insert(0, DLT)
    import them_lop_vao_mau as t
    ids = ["HS%03d" % i for i in range(1, 25)]
    l1, l2 = t.gan_lop(ids, 112026201), t.gan_lop(ids, 112026201)
    assert l1 == l2 and set(l1) == set(ids) and all(RE_LOP.match(v) for v in l1.values())
    assert t.gan_lop(ids, 112026202) != l1          # seed khác → khác
    assert len(set(l1.values())) > 3                # nhiều lớp, không dồn một lớp


def test_script_ghi_ro_la_du_lieu_mo_phong():
    with open(os.path.join(DLT, "them_lop_vao_mau.py"), encoding="utf-8") as f:
        nguon = f.read()
    assert "MÔ PHỎNG" in nguon and "seed" in nguon.lower()
