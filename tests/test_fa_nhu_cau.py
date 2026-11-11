"""FA-7 (V§4.3): bảng nhu cầu cho giáo viên và kiểm "chỉ tăng" (`so_sanh_suc_chua.py`).

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.
Bảng nhu cầu KHÔNG chứa mã hay tên học sinh (V§13.10). Giáo viên không giảm được chỉ tiêu và không
đổi được loại CLB sau khi mở đăng ký (V§4.1).
"""

import io
import os
import subprocess
import sys

import fa_daa
import so_nhap
from _fa import bat_fa, dung_fa_clb, dung_hs_fa, giu_cho, ma

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CLUBS = {"S": {"capacity": 2, "buoi": "b1"}, "G": {"capacity": 3, "buoi": "b1"},
         "T": {"capacity": 50, "buoi": "b1"}, "X": {"capacity": 4, "buoi": "b2"}}
FA = {"S": {"loai": "TUYEN_CHON", "diem_san": 5}, "G": {"loai": "GIOI_HAN"},
      "T": {"loai": "TU_DO"}, "X": {"loai": "GIOI_HAN"}}
PREFS = {"s1": ["S", "G", "T"], "s2": ["S", "T"], "s3": ["G", "S", "T", "X"], "s4": ["G", "T"]}
DIEM = {"S": {"s1": 9.0, "s2": 3.0}}


def _bang(**kw):
    return fa_daa.bang_nhu_cau(CLUBS, PREFS, DIEM, FA, [("G", "s4")], **kw)


def _dong(rows, cid):
    return next(r for r in rows if r["club_id"] == cid)


def test_dem_dung_tren_ca_tay():
    rows = _bang()
    s = _dong(rows, "S")
    assert (s["nv1"], s["so_ghi"], s["so_dat_san"], s["capacity"], s["so_giu_cho"]) == (2, 3, 1, 2, 0)
    g = _dong(rows, "G")
    assert (g["nv1"], g["so_ghi"], g["so_dat_san"], g["capacity"], g["so_giu_cho"]) == (2, 3, None, 3, 1)
    t = _dong(rows, "T")
    assert (t["nv1"], t["so_ghi"], t["so_dat_san"]) == (0, 4, None)
    assert {r["loai"] for r in rows} == {"TUYEN_CHON", "GIOI_HAN", "TU_DO"}
    assert [r["club_id"] for r in rows] == ["G", "S", "T", "X"]            # (buổi, mã CLB)


def test_loc_theo_buoi():
    rows = _bang(buoi="b2")
    assert [r["club_id"] for r in rows] == ["X"]
    assert (rows[0]["nv1"], rows[0]["so_ghi"]) == (1, 1)        # s3 chỉ có X ở buổi b2: X là NV1 của em


def test_khong_chua_ma_hoc_sinh():
    rows = _bang(ten_clb={"S": "CLB Sáng tạo"})
    van_ban = repr(rows)
    for sid in PREFS:
        assert sid not in van_ban
    assert set(rows[0]) == {"buoi", "club_id", "ten", "loai", "capacity", "nv1", "so_ghi",
                            "so_dat_san", "so_giu_cho"}
    assert _dong(rows, "S")["ten"] == "CLB Sáng tạo"


def test_kiem_chi_tang():
    truoc = {"A": {"capacity": 5, "loai": "GIOI_HAN"}, "B": {"capacity": 5, "loai": "TU_DO"},
             "C": {"capacity": 5, "loai": None}, "D": {"capacity": 5, "loai": "GIOI_HAN"}}
    sau = {"A": {"capacity": 4, "loai": "GIOI_HAN"},          # giảm chỉ tiêu
           "B": {"capacity": 9, "loai": "GIOI_HAN"},          # tăng nhưng đổi loại
           "C": {"capacity": 7, "loai": "TUYEN_CHON"},        # lần đầu đặt loại + tăng: được
           "E": {"capacity": 3, "loai": "TU_DO"}}             # CLB mới: được; D biến mất
    loi = {(x["club_id"], x["loi"]) for x in fa_daa.kiem_chi_tang(truoc, sau)}
    assert loi == {("A", "GIAM_SUC_CHUA"), ("B", "DOI_LOAI"), ("D", "MAT_CLB")}
    assert fa_daa.kiem_chi_tang(truoc, truoc) == []


# ------------------------------------------------------------ script so_sanh_suc_chua.py


def _xlsx(tmp_path, ten, clubs):
    duong = str(tmp_path / ten)
    so_nhap.ghi_so_nhap(duong, clubs, [])
    return duong


def _clb(cid, cho, loai=None):
    d = {"club_id": cid, "name": "CLB " + cid, "capacity": cho, "reserve_capacity": 0,
         "reserve_group": "", "buoi": ""}
    if loai:
        d["loai"] = loai
    return d


def _chay_script(*args):
    return subprocess.run([sys.executable, os.path.join(GOC, "mau_forms_thi_clb", "so_sanh_suc_chua.py"),
                           *args], capture_output=True, text=True, encoding="utf-8")


def test_script_tu_choi_giam_chi_tieu_va_doi_loai(tmp_path):
    truoc = _xlsx(tmp_path, "truoc.xlsx", [_clb("A", 5, "Giới hạn"), _clb("B", 5, "Tự do")])
    sau = _xlsx(tmp_path, "sau.xlsx", [_clb("A", 4, "Giới hạn"), _clb("B", 9, "Giới hạn")])
    r = _chay_script(truoc, sau)
    assert r.returncode == 1
    assert "A" in r.stdout and "B" in r.stdout and "chỉ tiêu" in r.stdout


def test_script_chap_nhan_khi_chi_tang(tmp_path):
    truoc = _xlsx(tmp_path, "truoc.xlsx", [_clb("A", 5, "Giới hạn")])
    sau = _xlsx(tmp_path, "sau.xlsx", [_clb("A", 8, "Giới hạn"), _clb("N", 3, "Tự do")])
    r = _chay_script(truoc, sau)
    assert r.returncode == 0, r.stdout + r.stderr


def test_script_tep_hong(tmp_path):
    r = _chay_script(str(tmp_path / "khong_co.xlsx"), str(tmp_path / "khong_co2.xlsx"))
    assert r.returncode == 2


# ------------------------------------------------------------ xuất từ phần mềm


def test_xuat_bang_nhu_cau(api, tmp_path):
    bat_fa(api)
    dung_fa_clb(api, T=(50, "TU_DO"), G=(3, "GIOI_HAN"), S=(2, "TUYEN_CHON", 5))
    dung_hs_fa(api, "hs_a", "hs_b", nv={"hs_a": ["S", "G", "T"], "hs_b": ["G", "T"]})
    assert api.submit_test_selection("hs_a", ["S"])["ok"]
    assert api.submit_club_scores("S", [{"student_id": "hs_a", "score": 8}])["ok"]
    giu_cho(api, ("G", "hs_b"))
    kq = api.export_bang_nhu_cau(str(tmp_path / "nhu_cau.csv"))
    assert kq["ok"], kq
    van_ban = io.open(kq["data"]["path"], encoding="utf-8-sig").read()
    assert "hs_a" not in van_ban and "hs_b" not in van_ban
    dong = {ln.split(",")[1]: ln.split(",") for ln in van_ban.splitlines()[1:]}
    assert dong["S"][5:8] == ["1", "1", "1"]            # nv1 = 1, so_ghi = 1, so_dat_san = 1
    assert dong["G"][5] == "1" and dong["G"][8] == "1"  # nv1 = 1 (hs_b), so_giu_cho = 1


def test_xuat_bang_nhu_cau_can_fa(api, tmp_path):
    kq = api.export_bang_nhu_cau(str(tmp_path / "x.csv"))
    assert not kq["ok"] and ma(kq["errors"]) == ["fa_chua_bat"]
