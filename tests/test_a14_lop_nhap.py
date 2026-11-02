# -*- coding: utf-8 -*-
"""A14 (nhập): cột `class_id` TUỲ CHỌN trong hai CSV học sinh, cột Lớp của Sổ nhập, cảnh báo
thiếu lớp, xuất → nạp lại. Dữ liệu là dữ liệu MÔ PHỎNG."""

import base64
import io
import sqlite3

import openpyxl
import pytest

import so_nhap
from _wharton import tat_wharton


@pytest.fixture
def api(api):
    tat_wharton(api)
    return api


def _lop(api):
    conn = sqlite3.connect(api.db_path)
    try:
        return dict(conn.execute("SELECT student_id, class_id FROM students"))
    finally:
        conn.close()


@pytest.fixture
def api_clb(api):
    for ma in ("A", "B"):
        assert api.create_or_update_club(ma, "CLB " + ma, 5, 0, "")["ok"]
    return api


# ------------------------------------------------------------------ CSV

def test_csv_nguyen_vong_dang_ngang_ghi_lop_da_chuan_hoa(api_clb):
    kq = api_clb.import_preferences_csv(
        "student_id,name,reserve_group,class_id,pref_1,pref_2\n"
        "S1,An,,10h1a,A,B\nS2,Ba,, 10  h2a ,B,A\nS3,Cu,,,A,B\n")
    assert kq["ok"], kq
    assert _lop(api_clb) == {"S1": "10H1A", "S2": "10 H2A", "S3": None}


def test_csv_chon_thi_dang_ngang_va_dai(api_clb):
    assert api_clb.import_test_selection_csv(
        "student_id,name,class_id,test_club_1,score_1\nS1,An,10h1,A,\n")["ok"]
    assert _lop(api_clb) == {"S1": "10H1"}
    # dạng dài: lấy giá trị không trống ĐẦU TIÊN (như `name`)
    assert api_clb.import_test_selection_csv(
        "student_id,club_id,name,class_id,score\nS2,A,Ba,,\nS2,B,,11a2,\nS2,B,,11a3,\n")["ok"]
    assert _lop(api_clb)["S2"] == "11A2"
    assert api_clb.import_preferences_csv(
        "student_id,club_id,rank,class_id\nS4,A,1,\nS4,B,2,12c\n")["ok"]
    assert _lop(api_clb)["S4"] == "12C"


def test_csv_khong_cot_hoac_o_trong_giu_lop_cu(api_clb):
    assert api_clb.create_student_if_missing("S1", "An", class_id="10H1")["ok"]
    assert api_clb.import_preferences_csv("student_id,name,pref_1\nS1,An,A\n")["ok"]
    assert _lop(api_clb)["S1"] == "10H1"
    assert api_clb.import_preferences_csv(
        "student_id,name,class_id,pref_1\nS1,An,,A\n")["ok"]
    assert _lop(api_clb)["S1"] == "10H1"
    # lần ghi sau cùng thắng
    assert api_clb.import_preferences_csv(
        "student_id,name,class_id,pref_1\nS1,An,10h9,A\n")["ok"]
    assert _lop(api_clb)["S1"] == "10H9"


# ------------------------------------------------------------------ so_nhap (đọc / ghi)

CLUBS = [{"club_id": "a", "name": "CLB A", "capacity": 3, "reserve_capacity": 0,
          "reserve_group": "", "buoi": ""}]


def _doc(students, **kw):
    buf = io.BytesIO()
    so_nhap.ghi_so_nhap(buf, CLUBS, students, **kw)
    wb = openpyxl.load_workbook(io.BytesIO(buf.getvalue()))
    return wb, base64.b64encode(buf.getvalue()).decode()


def _hs(sid, ten, lop=None):
    return {"student_id": sid, "name": ten, "reserve_group": "", "class_id": lop,
            "nv": [{"club_id": "a", "thi": False, "diem": ""}]}


def test_ghi_so_nhap_co_lop_dat_ngay_sau_ho_ten_va_mac_dinh_khong_co():
    wb, _ = _doc([_hs("S1", "An", "10H1")], co_lop=True)
    tieu = [o.value for o in wb[so_nhap.SHEET_HS][1]][:4]
    assert tieu == ["Mã HS", "Họ tên", "Lớp", "Nhóm ưu tiên"]
    assert [o.value for o in wb[so_nhap.SHEET_HS][3]][:3] == ["S1", "An", "10H1"]
    wb2, _ = _doc([_hs("S1", "An")])
    assert [o.value for o in wb2[so_nhap.SHEET_HS][1]][:3] == ["Mã HS", "Họ tên", "Nhóm ưu tiên"]


def test_cot_nv1_van_dung_khi_co_lop(api_clb):
    """NV1 dịch sang phải một cột; nạp lại vẫn ra đúng nguyện vọng."""
    _, b64 = _doc([_hs("S1", "An", "10h1")], co_lop=True)
    kq = api_clb.import_so_nhap(b64)
    # CLB `a` chưa có trong CSDL nên sổ tự đưa vào; kiểm nguyện vọng + lớp
    assert kq["ok"], kq
    conn = sqlite3.connect(api_clb.db_path)
    assert conn.execute("SELECT club_id FROM preferences WHERE student_id='S1'").fetchall() == [("a",)]
    conn.close()
    assert _lop(api_clb)["S1"] == "10H1"


def test_doc_so_nhap_class_id_va_thanh_csv_chi_them_cot_khi_co_lop():
    wb, _ = _doc([_hs("S1", "An", "10h1"), _hs("S2", "Ba", "")], co_lop=True)
    d = so_nhap.doc_so_nhap(wb)
    assert not d["loi"]
    assert [s["class_id"] for s in d["students"]] == ["10H1", ""]
    csv = so_nhap.thanh_csv(d)
    assert csv["preferences"].splitlines()[0].startswith("student_id,name,reserve_group,class_id,pref_1")
    assert csv["test_selection"].splitlines()[0].startswith("student_id,name,reserve_group,class_id,")

    wb2, _ = _doc([_hs("S1", "An")])
    d2 = so_nhap.doc_so_nhap(wb2)
    assert [s["class_id"] for s in d2["students"]] == [None]       # sổ không có cột
    assert "class_id" not in so_nhap.thanh_csv(d2)["preferences"]
    # Sổ có cột lớp nhưng KHÔNG ai có lớp: tệp CSV y như cũ (không cột)
    wb3, _ = _doc([_hs("S1", "An", "")], co_lop=True)
    assert "class_id" not in so_nhap.thanh_csv(so_nhap.doc_so_nhap(wb3))["preferences"]


@pytest.mark.parametrize("tieu_de", ["Lớp", "Mã lớp", "Lop", "Class", "Class ID", "class_id"])
def test_bi_danh_cot_lop(tieu_de):
    wb, _ = _doc([_hs("S1", "An", "10H1")], co_lop=True)
    wb[so_nhap.SHEET_HS]["C1"] = tieu_de
    d = so_nhap.doc_so_nhap(wb)
    assert d["students"][0]["class_id"] == "10H1"


def test_nhan_cohort_tuy_chinh_duoc_nhan():
    cfg = {"labels": {"cohort": {"vi": "Phòng ban", "en": "Department"}}}
    wb, _ = _doc([_hs("S1", "An", "KT")], co_lop=True, cfg=cfg)
    assert wb[so_nhap.SHEET_HS]["C1"].value == "Phòng ban"
    assert so_nhap.doc_so_nhap(wb, cfg=cfg)["students"][0]["class_id"] == "KT"


# ------------------------------------------------------------------ cảnh báo thiếu lớp

def _ma_canh_bao(kq):
    return [w["code"] for w in kq["data"]["canh_bao"]]


def test_canh_bao_thieu_lop_chi_khi_so_co_cot(api_clb):
    _, co_cot = _doc([_hs("S1", "An", "10H1"), _hs("S2", "Ba", ""), _hs("S3", "Cu", "")],
                     co_lop=True)
    kq = api_clb.xem_truoc_so_nhap(co_cot)
    assert kq["ok"]
    w = [w for w in kq["data"]["canh_bao"] if w["code"] == "so_nhap_canh_bao_thieu_lop"]
    assert w and w[0]["params"]["n"] == 2
    _, khong_cot = _doc([_hs("S1", "An")])
    assert "so_nhap_canh_bao_thieu_lop" not in _ma_canh_bao(api_clb.xem_truoc_so_nhap(khong_cot))


def test_import_so_nhap_giu_lop_cu_khi_o_trong_va_bao(api_clb):
    api_clb.create_student_if_missing("S2", "Ba", class_id="9C")
    _, b64 = _doc([_hs("S1", "An", "10H1"), _hs("S2", "Ba", "")], co_lop=True)
    kq = api_clb.import_so_nhap(b64)
    assert kq["ok"], kq
    assert _lop(api_clb) == {"S1": "10H1", "S2": "9C"}
    assert "so_nhap_canh_bao_thieu_lop" in [w["code"] for w in kq["data"]["warnings"]]


# ------------------------------------------------------------------ xuất ↔ nạp

def test_xuat_du_lieu_dau_vao_co_lop_khi_co_em_co_lop_va_nap_lai(api_clb, tmp_path):
    for sid, lop in [("S1", "10H1"), ("S2", None)]:
        api_clb.create_student_if_missing(sid, "Em " + sid, class_id=lop)
        assert api_clb.submit_preferences(sid, ["A", "B"])["ok"]
    kq = api_clb.export_du_lieu_dau_vao(str(tmp_path / "so.xlsx"))
    assert kq["ok"], kq
    ws = openpyxl.load_workbook(kq["data"]["path"])[so_nhap.SHEET_HS]
    assert [o.value for o in ws[1]][:3] == ["Mã HS", "Họ tên", "Lớp"]


def test_xuat_du_lieu_dau_vao_khong_lop_giu_so_nhu_cu(api_clb, tmp_path):
    api_clb.create_student_if_missing("S1", "An")
    assert api_clb.submit_preferences("S1", ["A"])["ok"]
    kq = api_clb.export_du_lieu_dau_vao(str(tmp_path / "so.xlsx"))
    ws = openpyxl.load_workbook(kq["data"]["path"])[so_nhap.SHEET_HS]
    assert [o.value for o in ws[1]][:3] == ["Mã HS", "Họ tên", "Nhóm ưu tiên"]


def test_so_mau_luon_co_cot_lop(api, tmp_path):
    kq = api.tao_so_nhap_mau(str(tmp_path / "mau.xlsx"))
    assert kq["ok"], kq
    ws = openpyxl.load_workbook(kq["data"]["path"])[so_nhap.SHEET_HS]
    assert [o.value for o in ws[1]][:4] == ["Mã HS", "Họ tên", "Lớp", "Nhóm ưu tiên"]
