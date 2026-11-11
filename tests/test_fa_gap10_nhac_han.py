"""GAP-10 (TH): danh sách "chưa đăng ký" theo lớp + hướng dẫn flow nhắc hạn (V§5.2) — dữ liệu MÔ PHỎNG."""
import csv
import os
import sys

from openpyxl import Workbook

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))
import bieu_mau as bm  # noqa: E402
import danh_sach_chua_dang_ky as ds  # noqa: E402


def _roster():
    return [{"student_id": "s1", "class_id": "10A1"}, {"student_id": "s2", "class_id": "10A1"},
            {"student_id": "s3", "class_id": "10A2"}, {"student_id": "s4", "class_id": "10A2"},
            {"student_id": "s5", "class_id": "10A2"}, {"student_id": "s6", "class_id": "10/A3"}]


def test_ty_le_theo_lop_va_co_duoi_50():
    assert ds.NGUONG_DANG_KY == 0.5 and ds.GIOI_HAN_YEU_CAU_NGAY == 6000
    kq = {r["class_id"]: r for r in ds.ty_le_dang_ky(_roster(), {"s1", "s3", "x9"})}
    assert list(kq) == ["10/A3", "10A1", "10A2"]
    assert (kq["10A1"]["n"], kq["10A1"]["da_dang_ky"], kq["10A1"]["ty_le"], kq["10A1"]["co"]) == (2, 1, 0.5, "")
    assert kq["10A1"]["chua"] == ["s2"]
    assert (kq["10A2"]["da_dang_ky"], kq["10A2"]["co"]) == (1, "DUOI_50")
    assert kq["10A2"]["chua"] == ["s4", "s5"]
    assert (kq["10/A3"]["ty_le"], kq["10/A3"]["co"]) == (0.0, "DUOI_50")


def _csv(p, dau, dong):
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(dau)
        w.writerows(dong)


def _doc(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def test_cli_ghi_tep_theo_lop_va_tong_hop(tmp_path, capsys):
    ros, dk, ra = tmp_path / "ds.csv", tmp_path / "dk.csv", tmp_path / "ra"
    _csv(ros, ["student_id", "class_id", "homeroom_email"],
         [[r["student_id"], r["class_id"], "gv@vi-du.test"] for r in _roster()])
    _csv(dk, ["student_id", "x"], [["s1", "1"], [" s3 ", "1"], ["", "1"]])
    assert ds.main([str(ros), str(dk), "--ra", str(ra)]) == 0
    tep = sorted(os.listdir(ra))
    assert tep == ["chua_dang_ky_10A1.csv", "chua_dang_ky_10A2.csv", "chua_dang_ky_10_A3.csv", "tong_hop.csv"]
    assert _doc(ra / "chua_dang_ky_10A2.csv") == [["student_id", "class_id"], ["s4", "10A2"], ["s5", "10A2"]]
    th = _doc(ra / "tong_hop.csv")
    assert th[0] == ["class_id", "n", "da_dang_ky", "ty_le", "co"]
    assert ["10A1", "2", "1", "0.5", ""] in th and ["10A2", "3", "1", "0.333", "DUOI_50"] in th
    out = capsys.readouterr().out
    assert "3 email" in out and "VƯỢT" not in out


def test_doc_tep_xuat_forms_co_tieu_de_ma(tmp_path):
    wb = Workbook()
    ws = wb.active
    ws.append(["ID", "Start time", bm.cau_ma_hoc_sinh(), "[name] Họ và tên"])
    ws.append([1, "", "s2", "A"])
    ws.append([2, "", 5, "B"])
    p = tmp_path / "dk.xlsx"
    wb.save(p)
    assert ds.doc_da_dang_ky(str(p)) == {"s2", "5"}
    wb2 = Workbook()
    wb2.active.append(["khong", "co"])
    p2 = tmp_path / "sai.xlsx"
    wb2.save(p2)
    try:
        ds.doc_da_dang_ky(str(p2))
    except ValueError as e:
        assert "student_id" in str(e)
    else:
        raise AssertionError("phải báo thiếu cột")


def test_canh_bao_vuot_gioi_han_va_huong_dan(tmp_path, capsys):
    ros, dk = tmp_path / "ds.csv", tmp_path / "dk.csv"
    _csv(ros, ["student_id", "class_id"], [["s%d" % i, "L%d" % i] for i in range(6001)])
    _csv(dk, ["student_id"], [])
    assert ds.main([str(ros), str(dk), "--ra", str(tmp_path / "ra")]) == 0
    assert "VƯỢT" in capsys.readouterr().out
    hd = os.path.join(GOC, "docs", "he_sinh_thai", "T4M_FLOW_NHAC_HAN.md")
    chu = open(hd, encoding="utf-8").read()
    assert "TH" in chu and "6.000" in chu and "T4M_FLOW_GUI_GVCN.md" in chu
    assert "danh_sach_chua_dang_ky.py" in chu and "−2 ngày" in chu and "−3 giờ" in chu
