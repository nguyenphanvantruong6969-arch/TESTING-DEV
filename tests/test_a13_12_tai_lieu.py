"""A13.12 (4.2): tài liệu phải nói đúng điều mã làm. Dữ liệu MÔ PHỎNG dựng trong test.

  * `xu-li-raw-forms/SKILL.md` không được nói sổ nó ghi "giống hệt" sổ mẫu: sổ mẫu trong kho có
    cột "Điểm quyết tâm" bên phải mỗi cột "Điểm thi", sổ do kỹ năng ghi (mặc định) thì không;
  * `HUONG_DAN_SU_DUNG.md` không dùng "bạn khác" (nghĩa bạn học, nhưng trùng xưng hô cấm).
"""

import os

import openpyxl

import so_nhap

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(GOC, ".claude", "skills", "xu-li-raw-forms", "SKILL.md")


def _doc(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def _hang_2(p):
    ws = openpyxl.load_workbook(p)["2. Học sinh"]
    return [c.value for c in ws[2]]


def test_su_that_bo_cuc_so_mau_co_cot_diem_quyet_tam_so_mac_dinh_khong(tmp_path):
    mau = _hang_2(os.path.join(GOC, "mau_csv", "SO_NHAP_CLB.xlsx"))
    assert "Điểm quyết tâm" in mau
    p = str(tmp_path / "s.xlsx")
    so_nhap.ghi_so_nhap(p, clubs=[], students=[])
    assert "Điểm quyết tâm" not in _hang_2(p)


def test_skill_xu_li_raw_khong_noi_giong_het_so_mau_va_noi_ro_cot_diem_quyet_tam():
    van = _doc(SKILL)
    assert "giống hệt" not in van
    cau = [d for d in van.split("\n\n") if "sổ mẫu" in d]
    assert cau and any("Điểm quyết tâm" in d for d in cau)


def test_huong_dan_khong_con_ban_khac():
    van = _doc(os.path.join(GOC, "HUONG_DAN_SU_DUNG.md"))
    assert "bạn khác" not in van
    assert "điểm của em khác" in van
