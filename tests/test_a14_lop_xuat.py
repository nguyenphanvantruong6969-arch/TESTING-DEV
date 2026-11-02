"""A14 phần B — xuất theo LỚP (dữ liệu MÔ PHỎNG).

Khoá: trang "Theo lớp" luôn có và KHÔNG mang điểm / số bốc thăm; `export_theo_lop` ra một thư mục
mỗi lớp một tệp; cột "Lớp" ngay sau "Họ tên" ở các bảng đã duyệt; các CSV khác không đổi.
Cần phần nền của phiên A (students.class_id, set_student_class)."""

import csv
import os

import pytest
from _wharton import tat_wharton
from openpyxl import load_workbook


@pytest.fixture
def api(api):
    tat_wharton(api)          # dữ liệu ở đây không có điểm quyết tâm
    return api


def _dat_lop(api, sid, lop):
    """Gán lớp thẳng vào cột (test xuất không phụ thuộc API sửa lớp của phiên A)."""
    with api._ket_noi_ghi() as cur:
        cur.execute("UPDATE students SET class_id = ? WHERE student_id = ?", (lop or None, sid))


def _nap(api, buoi=False):
    """6 em; CLB 'a' chỉ 1 chỗ nên có em chưa có chỗ. Lớp: 10A2, 10A10, 10A1, (trống)."""
    if buoi:
        for b in ("thu_2", "thu_3"):
            api.create_or_update_club("a_" + b, "CLB A " + b, 1, 0, "", buoi=b)
            api.create_or_update_club("b_" + b, "CLB B " + b, 5, 0, "", buoi=b)
        cot = "student_id,name,thu_2_pref_1,thu_3_pref_1\n"
        dong = "".join(
            "HS00%d,Em %d,a_thu_2,a_thu_3\n" % (i, i) for i in range(1, 7))
    else:
        api.create_or_update_club("a", "CLB A", 1, 0, "")
        api.create_or_update_club("b", "CLB B", 5, 0, "")
        cot = "student_id,name,pref_1,pref_2\n"
        dong = "".join("HS00%d,Em %d,a,b\n" % (i, i) for i in range(1, 7))
        dong = dong.replace("HS006,Em 6,a,b", "HS006,Em 6,a,")
    r = api.import_preferences_csv(cot + dong)
    assert r["ok"], r["errors"]
    for sid, lop in (("HS001", "10A2"), ("HS002", "10A10"), ("HS003", "10A2"),
                     ("HS004", "10A1"), ("HS005", "10A1")):
        _dat_lop(api, sid, lop)
    assert api.run_pipeline(seed=7)["ok"]
    return api


def _sheet_theo_lop(path):
    wb = load_workbook(path)
    return wb, wb["Theo lớp"]


def _cac_o(ws):
    return [[c.value for c in row] for row in ws.iter_rows()]


def _xuat(api, tmp_path, ten="kq.xlsx", **kw):
    p = str(tmp_path / ten)
    r = api.export_ket_qua(p, **kw)
    assert r["ok"], r["errors"]
    return r["data"]["path"]


def test_trang_theo_lop_luon_co_sau_theo_clb(api, tmp_path):
    _nap(api)
    wb, _ = _sheet_theo_lop(_xuat(api, tmp_path))
    ten = wb.sheetnames
    assert ten.index("Theo lớp") == ten.index("Theo CLB") + 1


def test_khoi_thu_tu_tu_nhien_ngat_trang_va_chua_co_lop(api, tmp_path):
    _nap(api)
    _, ws = _sheet_theo_lop(_xuat(api, tmp_path))
    khoi = [r[0] for r in _cac_o(ws) if r[0] and str(r[0]).startswith(("Lớp:", "Chưa có lớp"))]
    assert [k.split(" · ")[0] for k in khoi] == ["Lớp: 10A1", "Lớp: 10A2", "Lớp: 10A10",
                                                   "Chưa có lớp"]
    assert len(ws.row_breaks.brk) == 3


def test_khong_co_cot_diem_quyet_tam_boc_tham_hay_dien(api, tmp_path):
    _nap(api)
    _, ws = _sheet_theo_lop(_xuat(api, tmp_path))
    tieu_de = {c for r in _cac_o(ws) for c in r if isinstance(c, str)}
    for cam in ("Điểm", "Điểm quyết tâm", "Số bốc thăm", "Diện trúng tuyển", "Nguyện vọng thứ"):
        assert not any(cam.casefold() in t.casefold() for t in tieu_de
                       if t.startswith(cam) and len(t) < 40), cam
    hang = [r for r in _cac_o(ws) if r[0] == "STT"]
    assert hang and hang[0][:4] == ["STT", "Mã học sinh", "Họ tên", "Câu lạc bộ được xếp"]


def test_em_chua_co_cho_to_do(api, tmp_path):
    _nap(api)
    _, ws = _sheet_theo_lop(_xuat(api, tmp_path))
    do = 0
    for row in ws.iter_rows():
        if row[1].value in ("HS001", "HS002", "HS003", "HS004", "HS005", "HS006"):
            co_cho = bool(row[3].value)
            to = row[0].fill.fgColor.rgb not in ("00000000", None) and row[0].fill.fill_type
            if not co_cho:
                assert to, row[1].value
                do += 1
    assert do >= 1


def test_nhieu_buoi_moi_buoi_mot_cot(api, tmp_path):
    _nap(api, buoi=True)
    _, ws = _sheet_theo_lop(_xuat(api, tmp_path))
    hang = [r for r in _cac_o(ws) if r[0] == "STT"][0]
    assert [c for c in hang if c][3:] == ["thu_2", "thu_3"]


def test_cot_lop_ngay_sau_ho_ten_o_danh_sach_theo_clb_va_csv(api, tmp_path):
    _nap(api)
    p = _xuat(api, tmp_path, kem_csv=True)
    wb = load_workbook(p)
    for ten in ("Danh sách học sinh", "Theo CLB"):
        ws = wb[ten]
        hang = [r for r in _cac_o(ws) if "Họ tên" in r][0]
        assert hang[hang.index("Họ tên") + 1] == "Lớp", ten
    goc = os.path.splitext(p)[0]
    with open(goc + ".csv", encoding="utf-8-sig", newline="") as f:
        dong = list(csv.reader(f))
    assert dong[0][:3] == ["Mã học sinh", "Họ tên", "Lớp"]
    assert {d[0]: d[2] for d in dong[1:]}["HS001"] == "10A2"
    tep = sorted(os.listdir(goc + "_theo_club"))
    assert tep
    with open(os.path.join(goc + "_theo_club", tep[0]), encoding="utf-8-sig", newline="") as f:
        assert next(csv.reader(f))[:3] == ["Mã học sinh", "Họ tên", "Lớp"]


def test_csv_thoi_khoa_bieu_khong_doi_nhung_excel_co_cot_lop(api, tmp_path):
    _nap(api, buoi=True)
    p = _xuat(api, tmp_path, kem_csv=True)
    goc = os.path.splitext(p)[0]
    with open(goc + "_thoi_khoa_bieu.csv", encoding="utf-8-sig", newline="") as f:
        assert next(csv.reader(f)) == ["Mã học sinh", "Họ tên", "thu_2", "thu_3", "Số CLB"]
    ws = load_workbook(p)["Danh sách học sinh"]
    hang = [r for r in _cac_o(ws) if "Họ tên" in r][0]
    assert hang[:3] == ["Mã học sinh", "Họ tên", "Lớp"]


def test_export_theo_lop_so_tep_va_chua_co_lop(api, tmp_path):
    _nap(api)
    r = api.export_theo_lop(str(tmp_path / "ra"))
    assert r["ok"], r["errors"]
    thu_muc = r["data"]["thu_muc"]
    assert sorted(os.listdir(thu_muc)) == ["10A1.xlsx", "10A10.xlsx", "10A2.xlsx",
                                           "_chua_co_lop.xlsx"]
    assert r["data"]["n_tep"] == 4
    wb = load_workbook(os.path.join(thu_muc, "10A2.xlsx"))
    assert len(wb.sheetnames) == 1


def test_export_theo_lop_khong_em_nao_co_lop_chi_tep_chua_co_lop(api, tmp_path):
    _nap(api)
    for sid in ("HS001", "HS002", "HS003", "HS004", "HS005"):
        _dat_lop(api, sid, None)
    r = api.export_theo_lop(str(tmp_path / "ra"))
    assert sorted(os.listdir(r["data"]["thu_muc"])) == ["_chua_co_lop.xlsx"]


def test_export_theo_lop_ten_la_va_trung_khong_de(api, tmp_path):
    _nap(api)
    _dat_lop(api, "HS001", "10/A:2")      # ký tự cấm trong tên tệp
    _dat_lop(api, "HS002", "10_A_2")      # trùng sau khi làm sạch
    r = api.export_theo_lop(str(tmp_path / "ra"))
    ten = os.listdir(r["data"]["thu_muc"])
    assert "10_A_2.xlsx" in ten and "10_A_2_2.xlsx" in ten
    assert all("/" not in t and ":" not in t for t in ten)
    r2 = api.export_theo_lop(str(tmp_path / "ra"))
    assert r2["data"]["thu_muc"].endswith("ra (2)")
    assert os.path.isdir(r["data"]["thu_muc"])


def test_export_theo_lop_chua_co_ket_qua_khong_tao_tep(api, tmp_path):
    api.create_or_update_club("a", "CLB A", 1, 0, "")
    r = api.export_theo_lop(str(tmp_path / "ra"))
    assert r["ok"] is False
    assert r["errors"][0]["code"] == "xuat_chua_co_ket_qua"
    assert not (tmp_path / "ra").exists()


def test_export_theo_lop_mac_dinh_vao_tai_xuong(api, tmp_path):
    _nap(api)
    r = api.export_theo_lop()
    assert r["ok"], r["errors"]
    assert os.path.basename(os.path.dirname(r["data"]["thu_muc"])) == "TaiXuong_gia"
