"""T3-L1: chữ trong tệp Excel xuất (T3-43), tiêu đề cửa sổ (T3-38), khoảng số (T3-39). Dữ liệu MÔ PHỎNG."""

import os
import re

import openpyxl
import pytest

import main
from _wharton import tat_wharton

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GACH_DAI = "—"


@pytest.fixture
def api(api):
    tat_wharton(api)
    return api


def _toan_bo_chu(wb):
    return [(w.title, c.coordinate, str(c.value)) for w in wb.worksheets
            for hang in w.iter_rows() for c in hang if c.value is not None]


def _xuat(api, tmp_path):
    ra = str(tmp_path / "kq.csv")
    assert api.export_csv(ra)["ok"]
    return openpyxl.load_workbook(os.path.splitext(ra)[0] + ".xlsx")


def test_excel_co_ket_qua_khong_gach_dai_khong_dai_tu_em_khong_ngoac_thua(api, tmp_path):
    api.create_or_update_club("clb_a", "CLB A", 1)
    api.create_or_update_club("clb_b", "CLB B", 1)
    for i in range(1, 4):  # 3 học sinh, 2 chỗ: có người chưa có chỗ
        sid = "HS%d" % i
        api.create_student_if_missing(sid, "Học sinh %d" % i)
        api.submit_test_selection(sid, ["clb_a"])
        api.submit_preferences(sid, ["clb_a"])
    assert api.run_pipeline(42)["ok"]
    cac_o = _toan_bo_chu(_xuat(api, tmp_path))
    xau = [(t, o, v[:80]) for t, o, v in cac_o
           if v.strip() != GACH_DAI and (GACH_DAI in v or re.search(r"\b[Ee]m\b|\bcác em\b|[{}]", v))]
    assert not xau, xau[:8]


def test_excel_chua_chay_khong_gach_dai_khong_dai_tu_em(api, tmp_path):
    api.create_or_update_club("clb_a", "CLB A", 1)
    api.create_student_if_missing("HS1", "Học sinh 1")
    cac_o = _toan_bo_chu(_xuat(api, tmp_path)) if api.export_csv(str(tmp_path / "x.csv"))["ok"] else []
    xau = [(t, o, v[:80]) for t, o, v in cac_o
           if v.strip() != GACH_DAI and (GACH_DAI in v or re.search(r"\b[Ee]m\b|\bcác em\b|[{}]", v))]
    assert not xau, xau[:8]


def test_tieu_de_cua_so_dung_cham_giua_va_khong_con_ten_thuat_toan():
    assert GACH_DAI not in main.APP_TITLE and "RB-DA" not in main.APP_TITLE


def test_khoang_so_o_hop_tao_workspace_viet_tu_den_khong_gach_ngang():
    nguon = open(os.path.join(GOC, "i18n.js"), encoding="utf-8").read()
    for khoa in ("ws_r_max_choices", "ws_r_max_tests"):
        for dong in re.findall(r"^\s+%s: (.*)$" % khoa, nguon, re.M):
            assert "–" not in dong and "—" not in dong, dong
    assert "(từ 1 đến 20)" in nguon and "(từ 0 đến 20)" in nguon
