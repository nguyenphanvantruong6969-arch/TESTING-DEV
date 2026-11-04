"""A14 (nền): danh từ thứ sáu `cohort` (Lớp / Class), cột `students.class_id`, `chuan_hoa_lop`.

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.
"""

import glob
import os
import re
import sqlite3

import pytest

import cau_hinh_ws as ch
import nhan_ws
import rbda_priority_pipeline as rp

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ------------------------------------------------------------------ từ vựng

def test_cohort_la_danh_tu_thu_sau_voi_mac_dinh_lop_class():
    assert "cohort" in nhan_ws.DANH_TU
    assert nhan_ws.NHAN_MAC_DINH["cohort"] == {"vi": "Lớp", "en": "Class"}
    assert nhan_ws.dien("{cohort}") == "Lớp"
    assert nhan_ws.dien("{cohort}", lang="en") == "Class"
    assert nhan_ws.dien("{cohort_l}") == "lớp"
    assert nhan_ws.dien("{cohort_p}", lang="en") == "Classes"
    assert nhan_ws.dien("{cohort_u}") == "LỚP"


def test_cho_giu_nhan_ra_cohort_va_nhan_nhan_tuy_chinh():
    nhan = {"cohort": {"vi": "Phòng ban", "en": "Department"}}
    assert nhan_ws.dien("Xếp {cohort_l}", nhan) == "Xếp phòng ban"
    assert nhan_ws.dien("Xếp {cohort_p}", nhan, lang="en") == "Xếp Departments"


def test_cau_hinh_cu_thieu_cohort_nhan_mac_dinh(tmp_path):
    cu = {"labels": {"person": {"vi": "Nhân viên", "en": "Employee"}}}
    kq = ch.chuan_hoa(cu) if hasattr(ch, "chuan_hoa") else ch._chuan_hoa(cu)
    assert kq["labels"]["cohort"] == {"vi": "Lớp", "en": "Class"}
    assert kq["labels"]["person"]["vi"] == "Nhân viên"


def test_cau_hinh_chap_nhan_nhan_cohort_do_nguoi_dung_dat():
    kq = ch._chuan_hoa({"labels": {"cohort": {"vi": "Phòng", "en": ""}}})
    assert kq["labels"]["cohort"] == {"vi": "Phòng", "en": "Phòng"}


def test_cau_hinh_van_tu_choi_danh_tu_la():
    with pytest.raises(ValueError):
        ch._chuan_hoa({"labels": {"khong_co": {"vi": "x", "en": "x"}}})


def test_mac_dinh_truong_hoc_co_du_sau_danh_tu():
    assert set(ch.MAC_DINH_TRUONG_HOC["labels"]) == set(nhan_ws.DANH_TU)
    assert len(nhan_ws.DANH_TU) == 6


# ------------------------------------------------------------------ chuan_hoa_lop

@pytest.mark.parametrize("vao, ra", [
    ("10h1a", "10H1A"),
    ("  10H1A  ", "10H1A"),
    ("10  h1a", "10 H1A"),
    ("10\t H1A", "10 H1A"),
    ("Lớp  chọn", "LỚP CHỌN"),
    ("", None),
    ("   ", None),
    (None, None),
    (" 11A2 ", "11A2"),
])
def test_chuan_hoa_lop(vao, ra):
    assert rp.chuan_hoa_lop(vao) == ra


def test_chuan_hoa_lop_khong_ep_mau_va_la_ham_thuan():
    assert rp.chuan_hoa_lop("Ca sáng - nhóm 3") == "CA SÁNG - NHÓM 3"
    assert rp.chuan_hoa_lop(rp.chuan_hoa_lop(" x  y ")) == "X Y"   # lặp lại không đổi


def test_chuan_hoa_lop_nhan_so():
    assert rp.chuan_hoa_lop(12) == "12"


# ------------------------------------------------------------------ schema

def _cot(db):
    conn = sqlite3.connect(db)
    try:
        return {r[1]: r[2] for r in conn.execute("PRAGMA table_info(students)")}
    finally:
        conn.close()


def _bo_cot(conn, bang, cot):
    """Dựng lại `bang` thiếu cột `cot`, giữ dữ liệu, KHÔNG dùng `ALTER TABLE ... DROP COLUMN`.

    Đọc schema thật bằng PRAGMA nên tự theo khi bảng thêm cột; chỉ dùng cú pháp có ở mọi bản
    SQLite (DROP COLUMN cần 3.35 trở lên và từng làm CI báo "incomplete input", xem B9).
    """
    cac = [r for r in conn.execute("PRAGMA table_info(%s)" % bang) if r[1] != cot]
    pk = [r[1] for r in sorted(cac, key=lambda r: r[5]) if r[5]]
    dinh_nghia = ['"%s" %s' % (r[1], r[2]) for r in cac]
    if pk:
        dinh_nghia.append("PRIMARY KEY (%s)" % ", ".join('"%s"' % c for c in pk))
    ten = ", ".join('"%s"' % r[1] for r in cac)
    conn.execute("CREATE TABLE _tam_%s (%s)" % (bang, ", ".join(dinh_nghia)))
    conn.execute("INSERT INTO _tam_%s (%s) SELECT %s FROM %s" % (bang, ten, ten, bang))
    conn.execute("DROP TABLE %s" % bang)
    conn.execute("ALTER TABLE _tam_%s RENAME TO %s" % (bang, bang))

def test_schema_moi_co_cot_class_id(tmp_path):
    db = str(tmp_path / "m.db")
    rp.init_db(db)
    assert _cot(db)["class_id"] == "TEXT"


def test_di_tru_schema_them_cot_vao_csdl_cu_chay_lap_va_giu_du_lieu(tmp_path):
    db = str(tmp_path / "cu.db")
    rp.init_db(db)
    conn = sqlite3.connect(db)
    conn.execute("INSERT INTO students (student_id, name) VALUES ('S1', 'An')")
    _bo_cot(conn, "students", "class_id")
    conn.commit()
    conn.close()
    assert "class_id" not in _cot(db)

    da_lam = rp.di_tru_schema(db)
    assert "students.class_id" in da_lam
    assert rp.di_tru_schema(db) == []            # lặp lại: không làm gì nữa
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT student_id, name, class_id FROM students").fetchall() == [
        ("S1", "An", None)]
    conn.close()
    # Có sao lưu trước khi đụng bảng đang có dữ liệu.
    assert glob.glob(db + ".bak-*")


def test_di_tru_schema_khong_sao_luu_khi_cot_da_co(tmp_path):
    db = str(tmp_path / "m.db")
    rp.init_db(db)
    rp.di_tru_schema(db)
    assert not glob.glob(db + ".bak-*")


# ------------------------------------------------------------------ lõi không đọc lớp

def test_loi_phan_bo_khong_nhac_class_id():
    """`class_id` chỉ được xuất hiện ở schema và di_tru_schema trong lõi (chuan_hoa_lop đã chuyển sang
    lop_hoc_sinh.py ở T4-K1, nên lõi còn ít chỗ nhắc hơn)."""
    nguon = open(os.path.join(GOC, "rbda_priority_pipeline.py"), encoding="utf-8").read()
    # Cắt hai vùng được phép: DEFAULT_SCHEMA, di_tru_schema.
    def cat_ham(ten):
        m = re.search(r"^def %s\(.*?(?=^\S)" % ten, nguon, re.S | re.M)
        assert m, ten
        return m.group(0)
    con_lai = nguon
    for ten in ("di_tru_schema",):
        con_lai = con_lai.replace(cat_ham(ten), "")
    m = re.search(r'^DEFAULT_SCHEMA = """.*?^\);\n', con_lai, re.S | re.M)
    assert m
    con_lai = con_lai.replace(m.group(0), "")
    assert "class_id" not in con_lai


# ------------------------------------------------------------------ chuỗi liệt kê danh từ

def test_skill_tao_workspace_cung_biet_danh_tu_cohort():
    tep = os.path.join(GOC, ".claude", "skills", "tao-workspace-tu-raw", "SKILL.md")
    assert "cohort" in open(tep, encoding="utf-8").read()
