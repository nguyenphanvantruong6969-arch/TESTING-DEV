"""Điểm Wharton (A13.3): bảng nhật ký `wharton_nhat_ky` và bảng khoá `wharton_lock`.

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.

Bước 4: hai bảng mới đúng cột, CSDL cũ (trước vòng 3) mở lại và di trú lặp an toàn, `wharton_lock`
tối đa một dòng, `nguon` lạ bị CHECK từ chối. Nhật ký không có khoá ngoại (là dấu vết, phải còn
sau khi học sinh / CLB bị xoá).
"""

import sqlite3

import pytest

import rbda_priority_pipeline as rp


def _bang(db):
    conn = sqlite3.connect(db)
    try:
        return {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    finally:
        conn.close()


def _cot(db, bang):
    conn = sqlite3.connect(db)
    try:
        return [(r[1], r[2], r[3], r[5]) for r in conn.execute("PRAGMA table_info(%s)" % bang)]
    finally:
        conn.close()


def test_hai_bang_moi_dung_cot(tmp_path):
    db = str(tmp_path / "m.db")
    rp.init_db(db)
    assert {"wharton_nhat_ky", "wharton_lock"} <= _bang(db)
    assert _cot(db, "wharton_nhat_ky") == [
        ("id", "INTEGER", 0, 1), ("luc", "TEXT", 1, 0), ("nguon", "TEXT", 1, 0),
        ("nguoi", "TEXT", 1, 0), ("hanh_dong", "TEXT", 1, 0), ("student_id", "TEXT", 0, 0),
        ("cu_json", "TEXT", 0, 0), ("moi_json", "TEXT", 0, 0)]
    assert _cot(db, "wharton_lock") == [
        ("id", "INTEGER", 0, 1), ("is_locked", "INTEGER", 1, 0),
        ("locked_at", "TEXT", 0, 0), ("unlocked_at", "TEXT", 0, 0)]


def test_nhat_ky_khong_co_khoa_ngoai(tmp_path):
    db = str(tmp_path / "m.db")
    rp.init_db(db)
    conn = sqlite3.connect(db)
    assert conn.execute("PRAGMA foreign_key_list(wharton_nhat_ky)").fetchall() == []
    conn.close()


def test_csdl_cu_truoc_vong_3_mo_lai_va_di_tru_lap_an_toan(tmp_path):
    db = str(tmp_path / "cu.db")
    rp.init_db(db)
    conn = rp.connect_db(db)
    conn.execute("INSERT INTO students (student_id, name) VALUES ('S1', 'An')")
    conn.execute("INSERT INTO clubs (club_id, name, capacity) VALUES ('X', 'X', 5)")
    conn.execute("INSERT INTO preferences VALUES ('S1', 'X', 1)")
    conn.execute("DROP TABLE wharton_nhat_ky")
    conn.execute("DROP TABLE wharton_lock")
    conn.commit()
    conn.close()
    assert not ({"wharton_nhat_ky", "wharton_lock"} & _bang(db))
    rp.di_tru_schema(db)
    rp.di_tru_schema(db)                # lặp lại: không lỗi
    rp.init_db(db)
    rp.init_db(db)
    assert {"wharton_nhat_ky", "wharton_lock"} <= _bang(db)
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT student_id, club_id, rank FROM preferences").fetchall() == [
        ("S1", "X", 1)]
    conn.close()


def test_wharton_lock_chi_mot_dong(tmp_path):
    db = str(tmp_path / "m.db")
    rp.init_db(db)
    conn = rp.connect_db(db)
    conn.execute("INSERT INTO wharton_lock (id, is_locked) VALUES (1, 0)")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO wharton_lock (id, is_locked) VALUES (2, 0)")
    conn.close()


@pytest.mark.parametrize("nguon", ["quan_ly", "kiosk", "nap_tep", "xoa_du_lieu", "he_thong"])
def test_nguon_hop_le_duoc_ghi(tmp_path, nguon):
    db = str(tmp_path / "m.db")
    rp.init_db(db)
    conn = rp.connect_db(db)
    conn.execute("INSERT INTO wharton_nhat_ky (luc, nguon, hanh_dong) VALUES ('t', ?, 'luu')",
                 (nguon,))
    assert conn.execute("SELECT nguoi FROM wharton_nhat_ky").fetchone()[0] == ""
    conn.close()


def test_nguon_la_bi_check_tu_choi(tmp_path):
    db = str(tmp_path / "m.db")
    rp.init_db(db)
    conn = rp.connect_db(db)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO wharton_nhat_ky (luc, nguon, hanh_dong) "
                     "VALUES ('t', 'la_hoắc', 'luu')")
    conn.close()


# ====================================================================== Bước 5: ghi nhật ký ở mọi cửa

import getpass  # noqa: E402
import json  # noqa: E402

from _wharton import bat_wharton, chen_bids, dung_clb, dung_hs  # noqa: E402


def _nk(api):
    """[(nguon, hanh_dong, student_id, cu, moi)] theo thứ tự ghi; cu / moi đã giải JSON."""
    with api._ket_noi_doc() as cur:
        return [(r["nguon"], r["hanh_dong"], r["student_id"],
                 json.loads(r["cu_json"]) if r["cu_json"] else None,
                 json.loads(r["moi_json"]) if r["moi_json"] else None)
                for r in cur.execute("SELECT * FROM wharton_nhat_ky ORDER BY id")]


@pytest.fixture
def w(api):
    """Wharton bật; HS1 tick A, nguyện vọng A, B, C; HS2 nguyện vọng B, C."""
    bat_wharton(api)
    dung_clb(api, A=5, B=5, C=5)
    dung_hs(api, "HS1", "HS2", tick={"HS1": ["A"]})
    assert api.submit_preferences("HS1", ["A", "B", "C"])["ok"]
    assert api.submit_preferences("HS2", ["B", "C"])["ok"]
    return api


def test_submit_wharton_ghi_mot_dong_kiosk_luu_voi_cu_va_moi(w):
    assert _nk(w) == []
    assert w.submit_wharton("HS1", {"A": 100}, {"B": 60, "C": 40})["ok"]
    assert _nk(w) == [("kiosk", "luu", "HS1", {"w1": {}, "w2": {}},
                       {"w1": {"A": 100}, "w2": {"B": 60, "C": 40}})]
    assert w.submit_wharton("HS1", {"A": 100}, {"B": 10, "C": 90})["ok"]
    nk = _nk(w)
    assert len(nk) == 2
    assert nk[1][3] == {"w1": {"A": 100}, "w2": {"B": 60, "C": 40}}
    assert nk[1][4] == {"w1": {"A": 100}, "w2": {"B": 10, "C": 90}}


def test_khong_doi_diem_nao_thi_khong_ghi(w):
    assert w.submit_wharton("HS1", {"A": 100}, {"B": 60, "C": 40})["ok"]
    assert w.submit_wharton("HS1", {"A": 100}, {"B": 60, "C": 40})["ok"]      # lưu lại y nguyên
    assert len(_nk(w)) == 1


def test_luu_hong_thi_khong_ghi(w):
    assert w.submit_wharton("HS1", {"A": 100}, {"B": 60, "C": 30})["ok"] is False
    assert _nk(w) == []


def test_nguoi_la_ten_tai_khoan_may(w, monkeypatch):
    monkeypatch.setattr(getpass, "getuser", lambda: "may_truong")
    assert w.submit_wharton("HS1", {"A": 100}, {"B": 60, "C": 40})["ok"]
    with w._ket_noi_doc() as cur:
        assert cur.execute("SELECT nguoi, luc FROM wharton_nhat_ky").fetchone()[0] == "may_truong"


def test_getuser_loi_thi_nguoi_rong_va_thao_tac_van_thanh_cong(w, monkeypatch):
    def hong():
        raise OSError("khong co tai khoan")
    monkeypatch.setattr(getpass, "getuser", hong)
    kq = w.submit_wharton("HS1", {"A": 100}, {"B": 60, "C": 40})
    assert kq["ok"], kq["errors"]
    with w._ket_noi_doc() as cur:
        assert cur.execute("SELECT nguoi FROM wharton_nhat_ky").fetchone()[0] == ""


def test_nap_tep_ghi_nguon_nap_tep(w):
    kq = w.import_preferences_csv("student_id,name,pref_1,wp_1,pref_2,wp_2,pref_3,wp_3\n"
                                  "HS1,An,A,100,B,60,C,40\n")
    assert kq["ok"], kq["errors"]
    assert _nk(w) == [("nap_tep", "luu", "HS1", {"w1": {}, "w2": {}},
                       {"w1": {"A": 100}, "w2": {"B": 60, "C": 40}})]
    # nạp lại y nguyên: không đổi gì thì không ghi
    w.import_preferences_csv("student_id,name,pref_1,wp_1,pref_2,wp_2,pref_3,wp_3\n"
                             "HS1,An,A,100,B,60,C,40\n")
    assert len(_nk(w)) == 1


def test_submit_preferences_tia_clb_ghi_tia_nguyen_vong(w):
    chen_bids(w, [("HS1", "A", 1, 100), ("HS1", "B", 2, 60), ("HS1", "C", 2, 40)])
    assert w.submit_preferences("HS1", ["A", "B"])["ok"]                       # bỏ C
    assert _nk(w) == [("kiosk", "tia_nguyen_vong", "HS1",
                       {"w1": {"A": 100}, "w2": {"B": 60, "C": 40}},
                       {"w1": {"A": 100}, "w2": {"B": 60}})]
    assert w.submit_preferences("HS1", ["A", "B"])["ok"]                       # không tỉa gì nữa
    assert len(_nk(w)) == 1


def test_reset_student_entry_ghi_kiosk_xoa_mot_em(w):
    chen_bids(w, [("HS1", "A", 1, 100), ("HS1", "B", 2, 100)])
    assert w.reset_student_entry("HS1")["ok"]
    assert _nk(w) == [("kiosk", "xoa_mot_em", "HS1",
                       {"w1": {"A": 100}, "w2": {"B": 100}}, None)]
    assert w.reset_student_entry("HS2")["ok"]                  # HS2 không có điểm: không ghi
    assert len(_nk(w)) == 1


def test_delete_student_ghi_quan_ly_xoa_mot_em(w):
    chen_bids(w, [("HS2", "B", 2, 70), ("HS2", "C", 2, 30)])
    assert w.delete_student("HS2")["ok"]
    assert _nk(w) == [("quan_ly", "xoa_mot_em", "HS2", {"w1": {}, "w2": {"B": 70, "C": 30}}, None)]


def test_delete_club_ghi_xoa_theo_clb_cho_moi_em_bi_anh_huong(w):
    dung_clb(w, D=5)
    chen_bids(w, [("HS1", "D", 2, 10), ("HS1", "B", 2, 90), ("HS2", "D", 2, 100)])
    assert w.delete_club("D")["ok"]
    nk = _nk(w)
    assert [(n[0], n[1], n[2]) for n in nk] == [("quan_ly", "xoa_theo_clb", "HS1"),
                                                ("quan_ly", "xoa_theo_clb", "HS2")]
    assert nk[0][3] == {"w1": {}, "w2": {"B": 90, "D": 10}} and nk[0][4] == {"w1": {}, "w2": {"B": 90}}
    assert nk[1][3] == {"w1": {}, "w2": {"D": 100}} and nk[1][4] == {"w1": {}, "w2": {}}


def test_reset_data_ghi_mot_dong_tong_va_nhat_ky_van_con(w):
    assert w.submit_wharton("HS1", {"A": 100}, {"B": 60, "C": 40})["ok"]
    assert w.reset_data("hoc_sinh", "XOA")["ok"]
    nk = _nk(w)
    assert len(nk) == 2                                         # dòng cũ CÒN + một dòng tổng
    assert nk[0][:2] == ("kiosk", "luu")
    nguon, hanh_dong, sid, cu, moi = nk[1]
    assert (nguon, hanh_dong, sid, moi) == ("xoa_du_lieu", "xoa_tat_ca", None, None)
    assert cu["so_dong"] == 3 and cu["ma_hoc_sinh"] == ["HS1"]
    assert w.reset_data("tat_ca", "XOA")["ok"]                  # xoá nữa: nhật ký vẫn nguyên
    assert len(_nk(w)) == 2


def test_nhat_ky_nam_trong_cung_giao_dich_thao_tac_hong_thi_khong_co_dong(w, monkeypatch):
    chen_bids(w, [("HS1", "A", 1, 100), ("HS1", "B", 2, 100)])
    import api_quan_ly

    def hong(*a, **k):
        raise RuntimeError("hong giua chung")
    # Làm câu xoá cuối của reset_student_entry hỏng SAU khi đã ghi nhật ký
    goc = api_quan_ly.QuanLyMixin._xoa_diem_khong_con_tick
    monkeypatch.setattr(api_quan_ly.QuanLyMixin, "_xoa_diem_khong_con_tick", staticmethod(hong))
    assert w.reset_student_entry("HS1")["ok"] is False
    monkeypatch.setattr(api_quan_ly.QuanLyMixin, "_xoa_diem_khong_con_tick", goc)
    assert _nk(w) == []                                          # rollback: không dấu vết ma
    with w._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM wharton_bids").fetchone()[0] == 2
