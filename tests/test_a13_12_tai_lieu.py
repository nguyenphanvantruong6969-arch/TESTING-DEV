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


# ------------------------------------------------------------------ 4.1: bản đồ mã định vị theo TÊN HÀM

def _doan_ban_do():
    van = _doc(os.path.join(GOC, "CLAUDE.md"))
    dau = van.index("## Bản đồ mã")
    return van[dau:van.index("\n## ", dau + 5)]


def _moi_ten_py():
    """Mọi tên `def` / `class` / hằng ở đầu dòng trong các tệp .py ở gốc kho."""
    import glob
    import re
    ten = set()
    for p in glob.glob(os.path.join(GOC, "*.py")):
        for dong in _doc(p).splitlines():
            m = re.match(r"\s*(?:def|class)\s+(\w+)|^(\w+)\s*(?::[^=]+)?=", dong)
            if m:
                ten.add(m.group(1) or m.group(2))
    for p in glob.glob(os.path.join(GOC, "js", "*.js")):
        ten.update(re.findall(r"^function\s+(\w+)", _doc(p), re.M))
    return ten


def test_ban_do_ma_khong_ghi_so_dong_de_khoi_troi():
    import re
    ban_do = _doan_ban_do()
    assert not re.search(r"\bL\d{2,4}\b", ban_do), re.findall(r"\bL\d{2,4}(?:–\d+)?", ban_do)


def test_ban_do_ma_moi_ten_ham_trong_dau_huyen_deu_ton_tai():
    import re
    ten = _moi_ten_py()
    for t in re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", _doan_ban_do()):
        if t in ("PipelineAPI", "wharton"):      # tên lớp và tên nội bộ được giải thích bằng chữ
            continue
        assert t in ten, t


def test_ban_do_ma_co_nhom_ham_diem_quyet_tam():
    ban_do = _doan_ban_do()
    for ham in ("uu_tien_wharton", "kiem_ho_so_wharton", "tu_dien_wharton_mot_clb",
                "diem_wharton_hieu_luc", "submit_wharton", "phong_wharton_hang_loat",
                "mo_khoa_wharton", "tinh_diem_chuan"):
        assert "`%s`" % ham in ban_do, ham
    assert "Điểm quyết tâm" in ban_do


def test_ban_do_ma_so_tep_test_la_so_that():
    import glob
    import re
    n_tep = len(glob.glob(os.path.join(GOC, "tests", "test_*.py")))
    dong = [d for d in _doan_ban_do().splitlines() if d.startswith("| `tests/`")]
    assert dong, "thiếu dòng tests/"
    so = re.search(r"([\d.]+) tệp", dong[0])
    assert so and int(so.group(1).replace(".", "")) == n_tep, (so and so.group(1), n_tep)


def test_doi_chieu_kho_ma_co_muc_cap_nhat_dinh_vi_theo_ten_ham():
    van = _doc(os.path.join(GOC, "docs", "ke_hoach", "DOI_CHIEU_KHO_MA.md"))
    assert "Cập nhật 28/10/2026" in van
    for ham in ("uu_tien_wharton", "kiem_ho_so_wharton", "_run_pipeline_da_khoa", "club_choice_function"):
        assert "`%s`" % ham in van
