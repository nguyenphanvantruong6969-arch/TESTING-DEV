"""GAP-9 (TH): độ lệch giữa hai người chấm (V§7.4) — dữ liệu MÔ PHỎNG."""
import csv
import os
import sys

import pytest
from openpyxl import load_workbook

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mau_forms_thi_clb"))
import phan_tich_cau_hoi as pt  # noqa: E402


def _hang():
    return [
        {"club_id": "G", "cau": "1", "diem_1": 8, "diem_2": 6.5},     # lệch 1.5
        {"club_id": "G", "cau": "1", "diem_1": 7, "diem_2": 5.5},     # lệch 1.5 -> tb 1.5 (đúng ngưỡng)
        {"club_id": "G", "cau": "2", "diem_1": 9, "diem_2": 8},       # lệch 1
        {"club_id": "G", "cau": "2", "diem_1": 4, "diem_2": None},    # thiếu người chấm 2 -> bỏ
        {"club_id": "T", "cau": "1", "diem_1": 3, "diem_2": "4"},     # lệch 1 (chữ số đọc được)
        {"club_id": "T", "cau": "1", "diem_1": 5, "diem_2": ""},      # bỏ
    ]


def test_do_lech_thuan_theo_cau_va_clb_co_dung_nguong():
    assert pt.NGUONG_LECH_CHAM == 1.5
    kq = pt.do_lech_cham(_hang())
    cau = {(r["club_id"], r["cau"]): r for r in kq["theo_cau"]}
    assert set(cau) == {("G", "1"), ("G", "2"), ("T", "1")}
    assert cau[("G", "1")]["n"] == 2 and cau[("G", "1")]["lech_tb"] == pytest.approx(1.5)
    assert cau[("G", "1")]["co"] == "LECH_CHAM"
    assert cau[("G", "2")]["n"] == 1 and cau[("G", "2")]["lech_tb"] == pytest.approx(1.0)
    assert cau[("G", "2")]["co"] == ""
    assert cau[("T", "1")]["n"] == 1 and cau[("T", "1")]["co"] == ""
    clb = {r["club_id"]: r for r in kq["theo_clb"]}
    assert clb["G"]["n"] == 3 and clb["G"]["lech_tb"] == pytest.approx(4 / 3) and clb["G"]["co"] == ""
    assert clb["T"]["n"] == 1 and clb["T"]["lech_tb"] == pytest.approx(1.0)
    assert pt.do_lech_cham([]) == {"theo_cau": [], "theo_clb": []}


def test_bao_cao_co_trang_do_lech_va_trang_cu_khong_doi(tmp_path):
    p1 = tmp_path / "a.xlsx"
    pt.ghi_bao_cao(str(p1), so_sanh_theo_clb={})
    assert load_workbook(p1).sheetnames == ["Cân bằng đề"]
    p2 = tmp_path / "b.xlsx"
    pt.ghi_bao_cao(str(p2), so_sanh_theo_clb={}, do_lech=pt.do_lech_cham(_hang()))
    wb = load_workbook(p2)
    assert wb.sheetnames == ["Cân bằng đề", "Độ lệch chấm"]
    hang = list(wb["Độ lệch chấm"].iter_rows(values_only=True))
    assert hang[0] == ("CLB", "Câu", "Số bài", "Lệch trung bình", "Cờ")
    assert ("G", "1", 2, 1.5, "LECH_CHAM") in hang
    assert ("G", "(cả CLB)", 3, 1.333, None) in hang   # ô rỗng đọc lại thành None


def _csv(p, dau, dong):
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(dau)
        w.writerows(dong)


def test_cli_lech(tmp_path, capsys):
    vao, ra = tmp_path / "cham.csv", tmp_path / "bc.xlsx"
    _csv(vao, ["ClubId", "Cau", "Diem1", "Diem2"], [["G", "1", "8", "6"], ["G", "1", "7", "7"], ["G", "2", "5", ""]])
    assert pt.main(["lech", str(vao), "--ra", str(ra)]) == 0
    hang = list(load_workbook(ra)["Độ lệch chấm"].iter_rows(values_only=True))
    assert ("G", "1", 2, 1.0, None) in hang
    thieu = tmp_path / "thieu.csv"
    _csv(thieu, ["ClubId", "Cau", "Diem1"], [["G", "1", "8"]])
    assert pt.main(["lech", str(thieu), "--ra", str(tmp_path / "x.xlsx")]) == 1
    assert "Diem2" in capsys.readouterr().err
    assert not (tmp_path / "x.xlsx").exists()
