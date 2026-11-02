# -*- coding: utf-8 -*-
"""A14 (backend): lớp của học sinh — API quản lý, báo cáo, và các BẤT BIẾN.

Bất biến: lớp CHỈ để hiển thị / sắp / lọc / xuất. Thuật toán không đọc nó; đổi lớp không làm
kết quả thành "cũ"; run_history không bị đụng. Dữ liệu là dữ liệu MÔ PHỎNG.
"""

import io
import os
import random
import sqlite3

import pytest

from _wharton import tat_wharton
from api import PipelineAPI

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEN_TEP = ["danh_sach_CLB", "chon_CLB_muon_thi", "xep_hang_nguyen_vong"]


@pytest.fixture
def api(tmp_path):
    a = PipelineAPI(str(tmp_path / "app.db"))
    tat_wharton(a)          # dữ liệu không có điểm quyết tâm (Wharton mặc định BẬT)
    return a


def _nap_bo_sach(api):
    for i, ten in enumerate(TEN_TEP, start=1):
        with io.open(os.path.join(GOC, "du_lieu_test/bo_sach", "SACH_0%d_%s.csv" % (i, ten)),
                     encoding="utf-8-sig") as f:
            assert api.import_csv_auto(f.read())["ok"]


def _ket_qua(api):
    conn = sqlite3.connect(api.db_path)
    try:
        return conn.execute(
            "SELECT student_id, buoi, club_id, round_num, matched_tier, rank_in_student_pref "
            "FROM match_results ORDER BY student_id, buoi").fetchall()
    finally:
        conn.close()


def _sql(api, cau, tham_so=()):
    conn = sqlite3.connect(api.db_path)
    try:
        return conn.execute(cau, tham_so).fetchall()
    finally:
        conn.close()


@pytest.fixture
def api_nho(api):
    for sid, ten, lop in [("A1", "An", "10H2A"), ("A2", "Ba", "10H10A"), ("A3", "Cu", None),
                          ("A4", "Dũng", "10H2A"), ("A5", "Em", "9C")]:
        assert api.create_student_if_missing(sid, ten)["ok"]
        assert api.set_student_class(sid, lop)["ok"]
    return api


# ------------------------------------------------------------------ API quản lý

def test_create_student_if_missing_class_id(api):
    assert api.create_student_if_missing("O", "Mẫu")["ok"]
    assert api.set_student_class("O", "10H1A")["ok"]
    assert api.create_student_if_missing("X1", "Xa", class_id=" 10h1a ")["ok"]
    assert _sql(api, "SELECT class_id FROM students WHERE student_id='X1'") == [("10H1A",)]
    kq = api.create_student_if_missing("X3", "Xc", class_id="12Z9")
    assert not kq["ok"] and kq["errors"][0]["code"] == "lop_khong_co_trong_danh_sach"
    assert _sql(api, "SELECT 1 FROM students WHERE student_id='X3'") == []     # không tạo em
    assert api.create_student_if_missing("X2", "Xb")["ok"]          # không truyền: y như cũ
    assert _sql(api, "SELECT class_id FROM students WHERE student_id='X2'") == [(None,)]


def test_set_student_class_va_xoa(api_nho):
    kq = api_nho.set_student_class("A3", " 10h3b ")
    assert kq["ok"] and kq["data"]["class_id"] == "10H3B"
    assert _sql(api_nho, "SELECT class_id FROM students WHERE student_id='A3'") == [("10H3B",)]
    assert api_nho.set_student_class("A3", "")["ok"]
    assert _sql(api_nho, "SELECT class_id FROM students WHERE student_id='A3'") == [(None,)]
    kq = api_nho.set_student_class("KHONG_CO", "10H1")
    assert not kq["ok"] and kq["errors"][0]["code"] == "student_not_found"


def test_list_classes_thu_tu_tu_nhien_va_dem_khong_lop(api_nho):
    d = api_nho.list_classes()["data"]
    assert d["classes"] == [{"class_id": "9C", "n": 1}, {"class_id": "10H2A", "n": 2},
                            {"class_id": "10H10A", "n": 1}]
    assert d["n_khong_lop"] == 1


def test_list_students_admin_co_class_id_sap_va_loc(api_nho):
    d = api_nho.list_students_admin()["data"]
    assert {r["student_id"]: r["class_id"] for r in d["rows"]} == {
        "A1": "10H2A", "A2": "10H10A", "A3": None, "A4": "10H2A", "A5": "9C"}
    assert [r["student_id"] for r in d["rows"]] == ["A1", "A2", "A3", "A4", "A5"]   # mặc định

    d = api_nho.list_students_admin(sort_by="class_id")["data"]
    # 9C < 10H2A < 10H10A (tự nhiên), trống cuối, cùng lớp thì theo student_id
    assert [r["student_id"] for r in d["rows"]] == ["A5", "A1", "A4", "A2", "A3"]
    assert d["total"] == 5

    d = api_nho.list_students_admin(class_id="10h2a")["data"]
    assert [r["student_id"] for r in d["rows"]] == ["A1", "A4"] and d["total"] == 2
    d = api_nho.list_students_admin(class_id="")["data"]
    assert [r["student_id"] for r in d["rows"]] == ["A3"]
    assert api_nho.list_students_admin(class_id=None)["data"]["total"] == 5


def test_list_students_admin_sap_theo_lop_phan_trang_va_tim_kiem(api_nho):
    t1 = api_nho.list_students_admin(sort_by="class_id", page=1, page_size=2)["data"]
    t2 = api_nho.list_students_admin(sort_by="class_id", page=2, page_size=2)["data"]
    t3 = api_nho.list_students_admin(sort_by="class_id", page=3, page_size=2)["data"]
    ghep = [r["student_id"] for t in (t1, t2, t3) for r in t["rows"]]
    assert ghep == ["A5", "A1", "A4", "A2", "A3"] and t1["total_pages"] == 3
    d = api_nho.list_students_admin(search="Ba", class_id="10H10A")["data"]
    assert [r["student_id"] for r in d["rows"]] == ["A2"]


def test_submit_preferences_class_id(api_nho):
    api_nho.create_or_update_club("C1", "CLB 1", 5, 0, "")
    # None: không đụng
    assert api_nho.submit_preferences("A3", ["C1"])["ok"]
    assert _sql(api_nho, "SELECT class_id FROM students WHERE student_id='A3'") == [(None,)]
    # lớp có trong danh sách: ghi
    assert api_nho.submit_preferences("A3", ["C1"], class_id="10h2a")["ok"]
    assert _sql(api_nho, "SELECT class_id FROM students WHERE student_id='A3'") == [("10H2A",)]
    # lớp không có trong danh sách: lỗi, KHÔNG ghi nguyện vọng, lớp giữ nguyên
    kq = api_nho.submit_preferences("A3", ["C1"], class_id="12Z9")
    assert not kq["ok"]
    assert kq["errors"][0] == {"code": "lop_khong_co_trong_danh_sach",
                               "params": {"class_id": "12Z9"}}
    assert _sql(api_nho, "SELECT class_id FROM students WHERE student_id='A3'") == [("10H2A",)]
    # "" xoá lớp
    assert api_nho.submit_preferences("A3", ["C1"], class_id="")["ok"]
    assert _sql(api_nho, "SELECT class_id FROM students WHERE student_id='A3'") == [(None,)]


# ------------------------------------------------------------------ báo cáo

def test_get_match_results_co_class_id_loc_va_sap(api):
    _nap_bo_sach(api)
    ids = [r[0] for r in _sql(api, "SELECT student_id FROM students ORDER BY student_id")]
    for i, sid in enumerate(ids):
        api.set_student_class(sid, "10H%d" % (10 if i % 3 == 0 else 2 if i % 3 == 1 else 1))
    assert api.run_pipeline(seed=42)["ok"]
    tat_ca = api.get_match_results()["data"]
    assert tat_ca and all("class_id" in r for r in tat_ca)
    theo_lop = api.get_match_results(sort_by="class_id")["data"]
    assert len(theo_lop) == len(tat_ca)
    lop = [r["class_id"] for r in theo_lop]
    thu_tu = ["10H1", "10H2", "10H10"]
    assert lop == sorted(lop, key=thu_tu.index)
    chi_h2 = api.get_match_results(class_id="10h2")["data"]
    assert chi_h2 and {r["class_id"] for r in chi_h2} == {"10H2"}
    api.set_student_class(ids[0], "")
    chua = api.get_match_results(class_id="")["data"]
    assert {r["student_id"] for r in chua} == {ids[0]}


# ------------------------------------------------------------------ BẤT BIẾN

def test_match_results_giong_het_khi_co_va_khong_co_lop(api_factory):
    sach, co_lop = api_factory(), api_factory()
    for a in (sach, co_lop):
        tat_wharton(a)
        _nap_bo_sach(a)
    ids = [r[0] for r in _sql(co_lop, "SELECT student_id FROM students ORDER BY student_id")]
    rng = random.Random(7)
    for sid in ids:
        assert co_lop.set_student_class(sid, rng.choice(["10H1", "10H2", "11A3", "12C"]))["ok"]
    for seed in (42, 7):
        assert sach.run_pipeline(seed=seed, force_redraw_stb=True)["ok"]
        assert co_lop.run_pipeline(seed=seed, force_redraw_stb=True)["ok"]
        assert _ket_qua(sach) == _ket_qua(co_lop) and _ket_qua(sach)


def test_loi_phan_bo_khong_doc_class_id():
    """Trong lõi chỉ được nhắc `class_id` ở schema, di_tru_schema và chuan_hoa_lop."""
    import re
    nguon = open(os.path.join(GOC, "rbda_priority_pipeline.py"), encoding="utf-8").read()
    dong = [i for i, d in enumerate(nguon.splitlines(), 1) if "class_id" in d]
    assert dong, "phải còn ở schema"
    # mỗi dòng nhắc phải nằm trong DEFAULT_SCHEMA, di_tru_schema hoặc chuan_hoa_lop
    vung = []
    for ten in ("di_tru_schema", "chuan_hoa_lop"):
        m = re.search(r"^def %s\(.*?(?=^\S)" % ten, nguon, re.S | re.M)
        a = nguon[:m.start()].count("\n") + 1
        vung.append((a, a + m.group(0).count("\n")))
    m = re.search(r'^DEFAULT_SCHEMA = """.*?^\);\n', nguon, re.S | re.M)
    a = nguon[:m.start()].count("\n") + 1
    vung.append((a, a + m.group(0).count("\n")))
    ngoai = [i for i in dong if not any(a <= i <= b for a, b in vung)]
    assert not ngoai, ngoai


def test_dau_van_tay_khong_doi_khi_doi_lop(api):
    _nap_bo_sach(api)
    assert api.run_pipeline(seed=42)["ok"]
    assert api.get_trang_thai_ket_qua()["data"]["ket_qua_cu"] is False
    sid = _sql(api, "SELECT student_id FROM students ORDER BY student_id LIMIT 1")[0][0]
    assert api.set_student_class(sid, "10H5")["ok"]
    assert api.get_trang_thai_ket_qua()["data"]["ket_qua_cu"] is False
    assert api.set_student_class(sid, "10H6")["ok"]
    assert api.get_trang_thai_ket_qua()["data"]["ket_qua_cu"] is False


def test_run_history_khong_bi_dung(api):
    _nap_bo_sach(api)
    assert api.run_pipeline(seed=42)["ok"]
    truoc = _sql(api, "SELECT * FROM run_history ORDER BY rowid")
    sid = _sql(api, "SELECT student_id FROM students LIMIT 1")[0][0]
    api.set_student_class(sid, "10H5")
    api.list_classes()
    assert _sql(api, "SELECT * FROM run_history ORDER BY rowid") == truoc


def test_submit_test_selection_class_id(api_nho):
    api_nho.create_or_update_club("C1", "CLB 1", 5, 0, "")
    assert api_nho.submit_test_selection("A3", ["C1"])["ok"]
    assert _sql(api_nho, "SELECT class_id FROM students WHERE student_id='A3'") == [(None,)]
    assert api_nho.submit_test_selection("A3", ["C1"], "9c")["ok"]
    assert _sql(api_nho, "SELECT class_id FROM students WHERE student_id='A3'") == [("9C",)]
    kq = api_nho.submit_test_selection("A3", [], "12Z9")      # sai lớp: KHÔNG ghi tick
    assert kq["errors"][0] == {"code": "lop_khong_co_trong_danh_sach",
                               "params": {"class_id": "12Z9"}}
    assert _sql(api_nho, "SELECT club_id FROM club_test_selection WHERE student_id='A3'") == [("C1",)]
    assert api_nho.submit_test_selection("A3", ["C1"], "")["ok"]
    assert _sql(api_nho, "SELECT class_id FROM students WHERE student_id='A3'") == [(None,)]


def test_get_student_entry_state_co_class_id(api_nho):
    assert api_nho.get_student_entry_state("A1")["data"]["class_id"] == "10H2A"
    assert api_nho.get_student_entry_state("A3")["data"]["class_id"] is None
