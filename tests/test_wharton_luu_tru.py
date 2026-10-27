"""Điểm Wharton (A13, vòng 2): lưu trữ — bảng `wharton_bids` và dọn nó ở mọi cửa xoá.

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.

Điều phải giữ:
  * bảng có ràng buộc đúng (tier 1/2, điểm >= 0, khoá chính, khoá ngoại);
  * CSDL cũ (chưa có bảng) mở lại được, chạy di trú lặp an toàn, dữ liệu cũ nguyên vẹn;
  * xoá học sinh / CLB / nguyện vọng thì dòng Wharton đi theo; đổi ô tick thì KHÔNG đổi gì
    (hồ sơ thành chưa hợp lệ, phần mềm không tự chuyển điểm sang quỹ kia);
  * mọi việc trên chạy y hệt khi Wharton tắt (bảng rỗng).
"""

import sqlite3

import pytest

import rbda_priority_pipeline as rp


def _ket_noi(db):
    return rp.connect_db(db)


def _dem(api, bang="wharton_bids"):
    with api._ket_noi_doc() as cur:
        return cur.execute("SELECT COUNT(*) FROM %s" % bang).fetchone()[0]


def _dong(api):
    with api._ket_noi_doc() as cur:
        return [tuple(r) for r in cur.execute(
            "SELECT student_id, club_id, tier, points FROM wharton_bids "
            "ORDER BY student_id, club_id")]


def _chen(api, dong):
    """Ghi thẳng các dòng (student_id, club_id, tier, points) — giả lập hồ sơ đã lưu."""
    with api._ket_noi_ghi() as cur:
        cur.executemany(
            "INSERT INTO wharton_bids (student_id, club_id, tier, points) VALUES (?, ?, ?, ?)",
            dong)


@pytest.fixture
def api_w(api):
    """Hai CLB thi/không thi, hai học sinh có nguyện vọng và hồ sơ Wharton (mô phỏng)."""
    api.create_or_update_club("A", "CLB A", 5, 0, "")
    api.create_or_update_club("B", "CLB B", 5, 0, "")
    api.create_or_update_club("C", "CLB C", 5, 0, "")
    for sid in ("HS1", "HS2"):
        api.create_student_if_missing(sid, "Em " + sid)
        assert api.submit_test_selection(sid, ["A"])["ok"]
        assert api.submit_preferences(sid, ["A", "B", "C"])["ok"]
    _chen(api, [("HS1", "A", 1, 100), ("HS1", "B", 2, 60), ("HS1", "C", 2, 40),
                ("HS2", "A", 1, 100), ("HS2", "B", 2, 100)])
    return api


# ------------------------------------------------------------------ bảng và ràng buộc

def test_csdl_moi_co_bang_dung_cot(tmp_path):
    db = str(tmp_path / "moi.db")
    rp.init_db(db)
    conn = _ket_noi(db)
    cot = [(r[1], r[2], r[3], r[5]) for r in conn.execute("PRAGMA table_info(wharton_bids)")]
    conn.close()
    assert cot == [("student_id", "TEXT", 1, 1), ("club_id", "TEXT", 1, 2),
                   ("tier", "INTEGER", 1, 0), ("points", "INTEGER", 1, 0)]


@pytest.fixture
def db_co_hs(tmp_path):
    db = str(tmp_path / "rb.db")
    rp.init_db(db)
    conn = _ket_noi(db)
    conn.execute("INSERT INTO students (student_id, name) VALUES ('S1', 'An')")
    conn.execute("INSERT INTO clubs (club_id, name, capacity) VALUES ('X', 'X', 5)")
    conn.commit()
    yield conn
    conn.close()


@pytest.mark.parametrize("dong,vi_sao", [
    (("S1", "X", 3, 10), "tier = 3"),
    (("S1", "X", 0, 10), "tier = 0"),
    (("S1", "X", 1, -1), "points = -1"),
    (("KHONG_CO", "X", 1, 10), "student_id không tồn tại (khoá ngoại)"),
    (("S1", "KHONG_CO", 1, 10), "club_id không tồn tại (khoá ngoại)"),
])
def test_bang_tu_choi_dong_sai(db_co_hs, dong, vi_sao):
    with pytest.raises(sqlite3.IntegrityError):
        db_co_hs.execute(
            "INSERT INTO wharton_bids (student_id, club_id, tier, points) VALUES (?, ?, ?, ?)",
            dong)


def test_bang_tu_choi_trung_khoa_chinh(db_co_hs):
    db_co_hs.execute("INSERT INTO wharton_bids VALUES ('S1', 'X', 1, 10)")
    with pytest.raises(sqlite3.IntegrityError):
        db_co_hs.execute("INSERT INTO wharton_bids VALUES ('S1', 'X', 2, 20)")


def test_bang_nhan_dong_hop_le_ke_ca_0_diem(db_co_hs):
    db_co_hs.execute("INSERT INTO wharton_bids VALUES ('S1', 'X', 2, 0)")
    assert db_co_hs.execute("SELECT points FROM wharton_bids").fetchone()[0] == 0


# ------------------------------------------------------------------ CSDL cũ

def _dung_csdl_cu(tmp_path):
    """CSDL dựng bằng bản trước vòng 2: có dữ liệu nghiệp vụ nhưng CHƯA có wharton_bids."""
    db = str(tmp_path / "cu.db")
    rp.init_db(db)
    conn = _ket_noi(db)
    conn.execute("INSERT INTO students (student_id, name) VALUES ('S1', 'An')")
    conn.execute("INSERT INTO clubs (club_id, name, capacity) VALUES ('X', 'X', 5)")
    conn.execute("INSERT INTO preferences VALUES ('S1', 'X', 1)")
    conn.execute("DROP TABLE wharton_bids")
    conn.commit()
    conn.close()
    return db


def _bang(db):
    conn = sqlite3.connect(db)
    try:
        return {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    finally:
        conn.close()


def test_csdl_cu_mo_lai_co_bang_va_du_lieu_nguyen_ven(tmp_path):
    db = _dung_csdl_cu(tmp_path)
    assert "wharton_bids" not in _bang(db)
    rp.init_db(db)
    rp.init_db(db)                      # lặp lại: không lỗi
    assert "wharton_bids" in _bang(db)
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT student_id, club_id, rank FROM preferences").fetchall() == [
        ("S1", "X", 1)]
    conn.close()


def test_di_tru_schema_chay_lap_an_toan_tren_csdl_cu(tmp_path):
    db = _dung_csdl_cu(tmp_path)
    rp.di_tru_schema(db)
    rp.di_tru_schema(db)                # lặp lại: không lỗi
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 1
    conn.close()
    rp.init_db(db)
    assert "wharton_bids" in _bang(db)


def test_soat_vi_pham_rang_buoc_van_chay_khi_co_bang(tmp_path):
    db = str(tmp_path / "s.db")
    rp.init_db(db)
    conn = _ket_noi(db)
    assert rp.soat_vi_pham_rang_buoc(conn.cursor()) == []
    conn.close()


def test_dung_lai_bang_co_rang_buoc_giu_bang_wharton_hop_le(tmp_path):
    """CSDL KIỂU CŨ (5 bảng chưa có khoá ngoại/CHECK) được dựng lại; bảng con wharton_bids
    đang có dữ liệu phải còn nguyên và khoá ngoại phải sạch."""
    db = str(tmp_path / "d.db")
    rp.init_db(db)
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA foreign_keys = OFF")
    for ten in rp._BANG_RANG_BUOC:
        conn.execute("DROP TABLE %s" % ten)
    conn.executescript("""
        CREATE TABLE clubs (club_id TEXT PRIMARY KEY, name TEXT, capacity INTEGER,
            reserve_capacity INTEGER DEFAULT 0, reserve_group TEXT, buoi TEXT);
        CREATE TABLE club_test_selection (student_id TEXT, club_id TEXT,
            PRIMARY KEY (student_id, club_id));
        CREATE TABLE club_scores (student_id TEXT, club_id TEXT, score REAL,
            PRIMARY KEY (student_id, club_id));
        CREATE TABLE preferences (student_id TEXT, club_id TEXT, rank INTEGER,
            PRIMARY KEY (student_id, club_id));
        CREATE TABLE match_results (student_id TEXT, buoi TEXT NOT NULL, club_id TEXT,
            round_num INTEGER, matched_tier TEXT, rank_in_student_pref INTEGER,
            PRIMARY KEY (student_id, buoi));
        INSERT INTO students (student_id, name) VALUES ('S1', 'An');
        INSERT INTO clubs (club_id, name, capacity) VALUES ('X', 'X', 5);
        INSERT INTO preferences VALUES ('S1', 'X', 1);
        INSERT INTO wharton_bids VALUES ('S1', 'X', 2, 100);
    """)
    conn.commit()
    conn.close()

    assert rp._dung_lai_bang_co_rang_buoc(db) is True            # thật sự đã dựng lại

    conn = _ket_noi(db)
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
    assert conn.execute("SELECT * FROM wharton_bids").fetchall() == [("S1", "X", 2, 100)]
    assert rp._co_khoa_ngoai(conn.cursor(), "preferences")       # bảng cha đã có khoá ngoại
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO wharton_bids VALUES ('S1', 'X', 3, 1)")   # CHECK còn đó
    conn.close()


# ------------------------------------------------------------------ dọn ở mọi cửa xoá

def test_delete_student_xoa_dong_cua_em_do(api_w):
    assert api_w.delete_student("HS1")["ok"]
    assert _dong(api_w) == [("HS2", "A", 1, 100), ("HS2", "B", 2, 100)]


def test_reset_student_entry_xoa_toan_bo_diem_wharton_cua_em(api_w):
    assert api_w.reset_student_entry("HS1")["ok"]
    assert [d[0] for d in _dong(api_w)] == ["HS2", "HS2"]


@pytest.mark.parametrize("pham_vi", ["hoc_sinh", "tat_ca"])
def test_reset_data_lam_bang_rong(api_w, pham_vi):
    assert api_w.reset_data(pham_vi, "XOA")["ok"]
    assert _dem(api_w) == 0


def test_delete_club_xoa_dong_cua_clb_do(api):
    api.create_or_update_club("A", "CLB A", 5, 0, "")
    api.create_or_update_club("B", "CLB B", 5, 0, "")
    api.create_student_if_missing("HS1", "Em")
    _chen(api, [("HS1", "A", 2, 40), ("HS1", "B", 2, 60)])
    # delete_club chỉ chặn khi còn nguyện vọng / kết quả; ở đây chưa có
    assert api.delete_club("B")["ok"]
    assert _dong(api) == [("HS1", "A", 2, 40)]


def test_submit_preferences_bo_mot_clb_thi_xoa_dong_clb_do_giu_dong_khac(api_w):
    assert api_w.submit_preferences("HS1", ["A", "B"])["ok"]            # bỏ C
    assert _dong(api_w) == [("HS1", "A", 1, 100), ("HS1", "B", 2, 60),
                            ("HS2", "A", 1, 100), ("HS2", "B", 2, 100)]


def test_submit_preferences_giu_nguyen_khi_khong_bo_clb_nao(api_w):
    truoc = _dong(api_w)
    assert api_w.submit_preferences("HS1", ["C", "B", "A"])["ok"]       # chỉ đổi thứ tự
    assert _dong(api_w) == truoc


def test_submit_test_selection_doi_o_tick_khong_xoa_va_khong_doi_tier(api_w):
    truoc = _dong(api_w)
    assert api_w.submit_test_selection("HS1", ["A", "B"])["ok"]         # tick thêm B
    assert _dong(api_w) == truoc                                        # tier của B vẫn 2
    assert api_w.submit_test_selection("HS1", [])["ok"]                 # bỏ hết tick
    assert _dong(api_w) == truoc


def test_wharton_tat_cac_cua_xoa_chay_y_het(api):
    """Bảng rỗng (Wharton chưa từng dùng): mọi cửa vẫn chạy như trước vòng 2."""
    api.create_or_update_club("A", "CLB A", 5, 0, "")
    api.create_student_if_missing("HS1", "Em")
    assert api.submit_test_selection("HS1", ["A"])["ok"]
    assert api.submit_preferences("HS1", ["A"])["ok"]
    assert api.submit_preferences("HS1", ["A"])["ok"]
    assert api.reset_student_entry("HS1")["ok"]
    assert api.delete_student("HS1")["ok"]
    assert api.delete_club("A")["ok"]
    assert api.reset_data("tat_ca", "XOA")["ok"]
    assert _dem(api) == 0
