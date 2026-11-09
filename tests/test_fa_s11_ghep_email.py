"""FA-S11 (TH = chưa thử trên Microsoft thật): bộ chuyển đổi `--fa-daa` ghi EMAIL_MA_HS.csv (email, student_id;
dữ liệu cá nhân, chỉ trên máy IT) và `ghep_ket_qua_email.py` ghép ket_qua_ly_do.csv với tệp đó thành
KETQUA_NHAP_LIST.csv có các cột list `KetQua` của FA_SAU_XEP.md §2. Email trong test là MÔ PHỎNG.
"""
import csv
import os
import sys

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import chuyen_forms_sang_phan_mem as cv  # noqa: E402
import ghep_ket_qua_email as gh  # noqa: E402
from test_fa_m4_phan_tich import _bo_thi_lai, _chay_thu_tu  # noqa: E402

COT_KETQUA = ["Email", "MaHS", "Buoi", "CLB", "Nhom", "MaLyDo", "CauGiaiThich", "STB", "ViTriCho"]


def _doc(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def test_chuyen_fa_daa_ghi_email_ma_hs(tmp_path):
    de, lists, tep, sn, emails = _bo_thi_lai(tmp_path)
    _chay_thu_tu(tmp_path, de, lists, tep, sn)
    dong = _doc(tmp_path / "ra" / cv.TEN_EMAIL_MA_HS)
    assert list(dong[0]) == ["Email", "student_id"]
    assert sorted(d["Email"] for d in dong) == sorted(emails)
    assert all(d["student_id"] for d in dong)


def _ghi(p, cot, hang):
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(cot)
        w.writerows(hang)


def test_ghep_moi_dong_co_email_thieu_thi_canh_bao_giu_dong(tmp_path):
    ly_do = tmp_path / "ket_qua_ly_do.csv"
    _ghi(ly_do, ["student_id", "buoi", "club", "group", "reason", "sentence", "stb", "waitlist_pos"],
         [["HS1", "thu_2", "CLB Cờ vua", "1", "SCORE", "Em được nhận.", "12", ""],
          ["HS1", "thu_3", "CLB Văn", "", "LOTTERY", "Em chưa được nhận.", "12", "2"],
          ["HS2", "thu_2", "CLB Cờ vua", "1", "MEDAL", "Em được nhận.", "40", ""],
          ["HS9", "thu_2", "CLB Cờ vua", "", "BELOW_PASS", "Em chưa đạt.", "7", ""]])
    em = tmp_path / "EMAIL_MA_HS.csv"
    _ghi(em, ["Email", "student_id"], [["Hs1@Truong.Mo.Phong", "HS1"], ["hs2@truong.mo.phong", "HS2"]])
    ra = tmp_path / "KETQUA_NHAP_LIST.csv"
    canh_bao = gh.ghep(str(ly_do), str(em), str(ra))
    dong = _doc(ra)
    assert list(dong[0]) == COT_KETQUA
    assert len(dong) == 4
    assert [d["Email"] for d in dong] == ["hs1@truong.mo.phong", "hs1@truong.mo.phong", "hs2@truong.mo.phong", ""]
    assert dong[1] == {"Email": "hs1@truong.mo.phong", "MaHS": "HS1", "Buoi": "thu_3", "CLB": "CLB Văn", "Nhom": "",
                       "MaLyDo": "LOTTERY", "CauGiaiThich": "Em chưa được nhận.", "STB": "12", "ViTriCho": "2"}
    assert len(canh_bao) == 1 and "HS9" in canh_bao[0]


def test_cot_khop_tai_lieu_fa_sau_xep():
    md = open(os.path.join(GOC, "docs", "he_sinh_thai", "FA_SAU_XEP.md"), encoding="utf-8").read()
    for c in COT_KETQUA:
        assert "| `%s` |" % c in md, c
    assert "ghep_ket_qua_email.py" in md and "EMAIL_MA_HS.csv" in md


def test_main_cli(tmp_path):
    ly_do = tmp_path / "l.csv"
    _ghi(ly_do, ["student_id", "buoi", "club", "group", "reason", "sentence", "stb", "waitlist_pos"],
         [["HS1", "thu_2", "C", "", "SCORE", "x", "1", ""]])
    em = tmp_path / "e.csv"
    _ghi(em, ["Email", "student_id"], [["a@b.c", "HS1"]])
    assert gh.main([str(ly_do), str(em), "--ra", str(tmp_path / "o.csv")]) == 0
    assert _doc(tmp_path / "o.csv")[0]["Email"] == "a@b.c"
