"""FA-M5 (TH = chưa thử trên Power Apps / SharePoint): cột list ECA cho FA-DAA (đường A) và đặc tả app v2.

Đường A: một dòng mỗi (học sinh, ngày); `WP1..WP7` = huy chương 60/30/10; `HC_TuChinh`; `TrangThai` DRAFT/SUBMITTED/Đã khóa.
Không còn THI1..THI7 và hai quỹ 100 điểm. Bộ dựng cũ giữ nguyên khi không có `--fa-daa`. Dữ liệu MÔ PHỎNG.
"""
import csv
import json
import os
import re
import sys

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))
sys.path.insert(0, GOC)

import bieu_mau as bm  # noqa: E402
import chuyen_forms_sang_phan_mem as cv  # noqa: E402
import tao_bo_dung_t4m as tbd  # noqa: E402
from bo_dung_t4m import cot_lists, site_script  # noqa: E402

DAC_TA = os.path.join(GOC, "docs", "he_sinh_thai", "T4M_DAC_TA_SUA_APP.md")


@pytest.fixture(scope="module")
def de():
    return bm.doc_de_thi()


def _ten(cot):
    return [c.ten for c in cot]


def test_eca_fa_co_hc_tu_chinh_khong_co_tick_va_trang_thai_moi():
    ten = _ten(cot_lists.ECA_FA)
    assert "HC_TuChinh" in ten and not any(t.startswith("THI") for t in ten)
    assert [f"WP{k}" for k in range(1, 8)] == [t for t in ten if t.startswith("WP")]
    tt = next(c for c in cot_lists.ECA_FA if c.ten == "TrangThai")
    assert tt.lua_chon == ("DRAFT", "SUBMITTED", "Đã khóa") and tt.kieu == "Choice"
    wp = next(c for c in cot_lists.ECA_FA if c.ten == "WP1")
    assert wp.kieu == "Number" and not wp.bat_buoc


def test_bo_cot_cu_khong_doi():
    ten = _ten(cot_lists.ECA)
    assert "HC_TuChinh" not in ten and "THI1" in ten
    assert cot_lists.TAT_CA["ECA"] is cot_lists.ECA
    assert cot_lists.TAT_CA_FA["ECA"] is cot_lists.ECA_FA
    assert {k: v for k, v in cot_lists.TAT_CA_FA.items() if k != "ECA"} == {k: v for k, v in cot_lists.TAT_CA.items() if k != "ECA"}


def test_site_script_fa_co_cot_moi_va_khong_tick():
    ss = json.dumps(site_script.tao_site_script(cot_lists.TAT_CA_FA), ensure_ascii=False)
    assert "HC_TuChinh" in ss and "THI1" not in ss and "DRAFT" in ss
    assert "HC_TuChinh" not in json.dumps(site_script.tao_site_script(), ensure_ascii=False)


def _csv_eca_fa(tmp_path, dong):
    p = tmp_path / "eca.csv"
    tieu = _ten(cot_lists.ECA_FA)
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(tieu)
        for r in dong:
            w.writerow([r.get(h, "") for h in tieu])
    return str(p)


def test_converter_doc_duoc_dung_cot_eca_fa_khong_canh_bao(de, tmp_path):
    p = _csv_eca_fa(tmp_path, [
        dict(Email="a@x.vn", HoTen="A", CoSo="CS1", Khoi="10", Lop="10A1", Thu="Thứ 2", NV1="clb_covua", NV2="clb_vanhoc",
             NV3="clb_nhiepanh", WP1="60", WP2="30", TrangThai="SUBMITTED"),
        dict(Email="b@x.vn", HoTen="B", CoSo="CS1", Khoi="10", Lop="10A1", Thu="Thứ 2", NV1="clb_covua", TrangThai="DRAFT"),
        dict(Email="c@x.vn", HoTen="C", CoSo="CS1", Khoi="10", Lop="10A1", Thu="Thứ 2", NV1="clb_vanhoc", NV2="clb_covua",
             HC_TuChinh="Có", WP1="10", WP2="60", TrangThai="SUBMITTED")])
    ds, cb = cv.doc_lists(p, de, fa=True)
    assert ds["a@x.vn"]["wp"]["thu_2"] == {"clb_covua": 60, "clb_vanhoc": 30, "clb_nhiepanh": None}
    assert ds["c@x.vn"]["hc"] == {"thu_2": True} and ds["c@x.vn"]["wp"]["thu_2"] == {"clb_vanhoc": 10, "clb_covua": 60}
    assert [x for x in cb if "nháp" not in x[2]] == []                  # chỉ cảnh báo duy nhất là dòng DRAFT của b


def test_bo_dung_fa_ghi_cot_fa_va_ghi_chu_giong_het_tung_byte(de, tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    tbd.tao_bo_dung(de, str(a), in_ra=lambda *x: None, fa=True)
    tbd.tao_bo_dung(de, str(b), in_ra=lambda *x: None, fa=True)
    tep = sorted(os.path.relpath(os.path.join(g, t), a) for g, _, ts in os.walk(a) for t in ts)
    assert tep == sorted(os.path.relpath(os.path.join(g, t), b) for g, _, ts in os.walk(b) for t in ts)
    for t in tep:
        assert open(os.path.join(a, t), "rb").read() == open(os.path.join(b, t), "rb").read(), t
    mau = open(a / "01_lists" / "ECA_mau.csv", encoding="utf-8-sig").readline().strip().split(",")
    assert mau == _ten(cot_lists.ECA_FA)
    assert "HC_TuChinh" in (a / "01_lists" / "KIEM_COT_ECA.md").read_text(encoding="utf-8")
    ghi_chu = (a / "00_FA_DAA_GHI_CHU.md").read_text(encoding="utf-8")
    assert "TH" in ghi_chu and "chưa chạy" in ghi_chu and "§12" in ghi_chu


def test_bo_dung_mac_dinh_khong_co_gi_cua_fa(de, tmp_path):
    tbd.tao_bo_dung(de, str(tmp_path / "x"), in_ra=lambda *x: None)
    assert not (tmp_path / "x" / "00_FA_DAA_GHI_CHU.md").exists()
    mau = open(tmp_path / "x" / "01_lists" / "ECA_mau.csv", encoding="utf-8-sig").readline().strip().split(",")
    assert mau == _ten(cot_lists.ECA) and "THI1" in mau


def test_main_fa_daa_chay_duoc(tmp_path):
    assert tbd.main(["--fa-daa", "--ra", str(tmp_path / "ra")]) == 0
    assert (tmp_path / "ra" / "00_FA_DAA_GHI_CHU.md").exists()


# ---------------------------------------------------------------- đặc tả (tài liệu)
def _muc_12():
    s = open(DAC_TA, encoding="utf-8").read()
    i = s.index("## 12. ")
    return s[i:]


def test_dac_ta_co_muc_12_voi_yeu_cau_r39_tro_di():
    m = _muc_12()
    r = sorted(int(x) for x in re.findall(r"^\| R(\d+) \|", m, re.M))
    assert r and r[0] == 39 and r == list(range(39, 39 + len(r)))
    assert len(r) >= 14


def test_dac_ta_muc_12_noi_dung_bat_buoc():
    m = _muc_12()
    for tu in ("Shuffle(", "▲", "▼", "DRAFT", "SUBMITTED", "HC_TuChinh", "WP1", "6.000", "NC-13", "TH", "D8",
               "Thêm một CLB Tự do để chắc chắn có chỗ", "Huy chương ở CLB Tuyển chọn chỉ dùng khi bằng điểm",
               "Xếp đúng thứ tự em thích", "thay"):
        assert tu in m, tu
    assert "khuyến nghị" not in m.lower() and "nên chọn" not in m.lower()          # D8 còn mở
    assert "Đã dùng X / 100" in m                                                   # nêu rõ cái bị thay thế


def test_dac_ta_muc_12_khong_chua_du_lieu_that():
    m = _muc_12()
    assert "@" not in m
    assert not re.search(r"tenantId\s*[:=]\s*\S", m) and "https://" not in m
