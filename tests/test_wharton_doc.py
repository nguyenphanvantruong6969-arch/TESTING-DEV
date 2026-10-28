"""Điểm Wharton (A13, vòng 2): bộ đọc `doc_du_lieu_wharton`, bản đọc nhất quán kèm dấu vân tay,
và dấu vân tay. Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.

Điều phải giữ:
  * Wharton TẮT: thêm / sửa dòng `wharton_bids` KHÔNG đổi dấu vân tay, và dấu vân tay bằng
    đúng giá trị tính bằng mã trước vòng 2 (các hằng `VANG_*` dưới đây);
  * Wharton BẬT: sửa một điểm thì đổi; bật / tắt `rules.wharton` cũng đổi;
  * dữ liệu, dấu vân tay và Wharton lấy trong CÙNG một giao dịch đọc.
"""

import inspect
import sqlite3
import threading
import time

import pytest

import rbda_priority_pipeline as rp

# Dấu vân tay của CSDL nhỏ ở `_dung_csdl`, tính bằng mã của vòng 1 (commit f938792), tức
# trước khi có điểm Wharton.
VANG_MAC_DINH = "f4db12defa0de99817ec1292563f10ba9d7ac7895be5a27140554e796532a716"
VANG_NHOM_CUNG = "2d23f775a0aa388a4660e040101431fb0171bddaf4ae8db2830661edfc7c5470"
VANG_DIEM_NGUOI = "c76911a577999c3a54f80d74ba1ce9b3edd3fbbd638e73ec8493fbfd2f485c69"
LUAT_NHOM_CUNG = {"tier_mode": "strict", "tiers": ["G"]}


def _dung_csdl(tmp_path):
    db = str(tmp_path / "w.db")
    rp.init_db(db)
    c = sqlite3.connect(db)
    c.executescript("""
        INSERT INTO students (student_id, name, reserve_group)
            VALUES ('S1', 'An', NULL), ('S2', 'Binh', 'G');
        INSERT INTO clubs (club_id, name, capacity, reserve_capacity, reserve_group, buoi)
            VALUES ('A', 'A', 2, 1, 'G', NULL), ('B', 'B', 3, 0, NULL, 'thu_3');
        INSERT INTO club_test_selection VALUES ('S1', 'A'), ('S2', 'A'), ('S2', 'B');
        INSERT INTO club_scores VALUES ('S1', 'A', 7.5), ('S2', 'B', 6.0);
        INSERT INTO preferences VALUES ('S1', 'A', 1), ('S1', 'B', 2), ('S2', 'B', 1), ('S2', 'A', 2);
    """)
    c.commit()
    c.close()
    return db


def _cur(db):
    conn = sqlite3.connect(db)
    return conn, conn.cursor()


def _ghi(db, sql, tham_so=()):
    conn = rp.connect_db(db)
    conn.execute(sql, tham_so)
    conn.commit()
    conn.close()


def _chen_bids(db, dong):
    conn = rp.connect_db(db)
    conn.executemany("INSERT INTO wharton_bids VALUES (?, ?, ?, ?)", dong)
    conn.commit()
    conn.close()


# ------------------------------------------------------------------ doc_du_lieu_wharton

def test_doc_du_lieu_wharton_tach_theo_tier(tmp_path):
    db = _dung_csdl(tmp_path)
    _chen_bids(db, [("S1", "A", 1, 100), ("S1", "B", 2, 100),
                    ("S2", "A", 1, 70), ("S2", "B", 1, 30)])
    conn, cur = _cur(db)
    w = rp.doc_du_lieu_wharton(cur)
    conn.close()
    assert w == {
        "clb_thi": {"S1": {"A"}, "S2": {"A", "B"}},
        "w1": {"S1": {"A": 100}, "S2": {"A": 70, "B": 30}},
        "w2": {"S1": {"B": 100}},
    }


def test_doc_du_lieu_wharton_bang_rong(tmp_path):
    db = _dung_csdl(tmp_path)
    conn, cur = _cur(db)
    w = rp.doc_du_lieu_wharton(cur)
    conn.close()
    assert w["w1"] == {} and w["w2"] == {}
    assert w["clb_thi"] == {"S1": {"A"}, "S2": {"A", "B"}}


def test_doc_du_lieu_wharton_giu_dong_tier_lech_voi_o_tick_hien_tai(tmp_path):
    db = _dung_csdl(tmp_path)
    _chen_bids(db, [("S1", "B", 2, 100)])
    _ghi(db, "INSERT INTO club_test_selection VALUES ('S1', 'B')")      # tick thêm B sau khi chia
    conn, cur = _cur(db)
    w = rp.doc_du_lieu_wharton(cur)
    conn.close()
    assert w["w2"] == {"S1": {"B": 100}}          # vẫn ở quỹ 2; kiem_ho_so_wharton sẽ báo lệch
    assert w["clb_thi"]["S1"] == {"A", "B"}


# ------------------------------------------------------------------ bản đọc nhất quán

def test_load_wharton_tra_ba_phan_dung_dang(tmp_path):
    db = _dung_csdl(tmp_path)
    _chen_bids(db, [("S1", "A", 1, 100)])
    du_lieu, dvt, w = rp.load_from_sqlite_kem_dau_van_tay_wharton(db, {"wharton": True})
    assert len(du_lieu) == 6 and set(du_lieu[0]) == {"S1", "S2"}
    assert isinstance(dvt, str) and len(dvt) == 64
    assert w["w1"] == {"S1": {"A": 100}}
    # dữ liệu 6 phần giống hệt bản đọc cũ
    cu, dvt_cu = rp.load_from_sqlite_kem_dau_van_tay(db, {"wharton": True})
    assert cu == du_lieu and dvt_cu == dvt


def test_ban_doc_cu_khong_doi_chu_ky_va_gia_tri_tra_ve(tmp_path):
    assert list(inspect.signature(rp.load_from_sqlite_kem_dau_van_tay).parameters) == [
        "db_path", "rules"]
    assert list(inspect.signature(rp._doc_du_lieu).parameters) == ["cur", "rules"]
    db = _dung_csdl(tmp_path)
    kq = rp.load_from_sqlite_kem_dau_van_tay(db)
    assert len(kq) == 2 and len(kq[0]) == 6 and kq[1] == VANG_MAC_DINH


def test_load_wharton_giu_khoa_doc_suot_ca_ba_lan_doc(tmp_path, monkeypatch):
    """Một lần lưu chen vào lúc đang đọc Wharton phải CHỜ (khoá đọc còn giữ), tức là ba phần
    đến từ MỘT giao dịch — khớp bài test của `load_from_sqlite_kem_dau_van_tay`."""
    db = _dung_csdl(tmp_path)
    _chen_bids(db, [("S1", "A", 1, 100)])
    ket_qua = {}

    def luu():
        conn = rp.connect_db(db)
        conn.execute("UPDATE wharton_bids SET points = 5 WHERE student_id = 'S1'")
        conn.commit()
        conn.close()
        ket_qua["xong"] = True

    goc = rp.doc_du_lieu_wharton

    def gia(cur):
        ra = goc(cur)
        t = threading.Thread(target=luu)
        t.start()
        time.sleep(0.5)
        ket_qua["thread"] = t
        ket_qua["da_xong_som"] = ket_qua.get("xong", False)
        return ra

    monkeypatch.setattr(rp, "doc_du_lieu_wharton", gia)
    _du, _dvt, w = rp.load_from_sqlite_kem_dau_van_tay_wharton(db, {"wharton": True})
    ket_qua["thread"].join(15)
    assert ket_qua["da_xong_som"] is False, "ben ghi khong cho — lan doc khong nhat quan"
    assert ket_qua["xong"] is True
    assert w["w1"] == {"S1": {"A": 100}}            # thấy bản CŨ, không thấy lần lưu chen vào


# ------------------------------------------------------------------ dấu vân tay

@pytest.mark.parametrize("rules,vang", [
    (None, VANG_MAC_DINH), ({}, VANG_MAC_DINH), ({"wharton": False}, VANG_MAC_DINH),
    (LUAT_NHOM_CUNG, VANG_NHOM_CUNG), ({**LUAT_NHOM_CUNG, "wharton": False}, VANG_NHOM_CUNG),
    ({"score_scope": "per_person"}, VANG_DIEM_NGUOI),
])
def test_tat_wharton_dau_van_tay_bang_gia_tri_truoc_vong_2(tmp_path, rules, vang):
    db = _dung_csdl(tmp_path)
    conn, cur = _cur(db)
    assert rp.dau_van_tay_du_lieu(cur, rules) == vang
    conn.close()


def test_tat_wharton_them_hay_sua_dong_bids_khong_doi_dau_van_tay(tmp_path):
    db = _dung_csdl(tmp_path)
    _chen_bids(db, [("S1", "A", 1, 100), ("S1", "B", 2, 100)])
    _ghi(db, "UPDATE wharton_bids SET points = 7 WHERE student_id = 'S1' AND club_id = 'B'")
    conn, cur = _cur(db)
    for rules in (None, {"wharton": False}, LUAT_NHOM_CUNG):
        assert rp.dau_van_tay_du_lieu(cur, rules) == (
            VANG_NHOM_CUNG if rules is LUAT_NHOM_CUNG else VANG_MAC_DINH)
    conn.close()


def test_bat_wharton_sua_mot_diem_thi_dau_van_tay_doi(tmp_path):
    db = _dung_csdl(tmp_path)
    _chen_bids(db, [("S1", "A", 1, 100), ("S1", "B", 2, 100)])
    luat = {"wharton": True}
    conn, cur = _cur(db)
    truoc = rp.dau_van_tay_du_lieu(cur, luat)
    assert rp.dau_van_tay_du_lieu(cur, luat) == truoc                  # ổn định
    conn.close()
    _ghi(db, "UPDATE wharton_bids SET points = 99 WHERE student_id = 'S1' AND club_id = 'A'")
    conn, cur = _cur(db)
    sau = rp.dau_van_tay_du_lieu(cur, luat)
    conn.close()
    assert sau != truoc
    # thêm một dòng cũng đổi
    _chen_bids(db, [("S2", "A", 1, 100)])
    conn, cur = _cur(db)
    assert rp.dau_van_tay_du_lieu(cur, luat) not in (truoc, sau)
    conn.close()


def test_bat_hay_tat_rules_wharton_deu_doi_dau_van_tay(tmp_path):
    db = _dung_csdl(tmp_path)
    _chen_bids(db, [("S1", "A", 1, 100)])
    conn, cur = _cur(db)
    tat = rp.dau_van_tay_du_lieu(cur, {"wharton": False})
    bat = rp.dau_van_tay_du_lieu(cur, {"wharton": True})
    # cả khi bảng rỗng, bật vẫn là một luật khác
    conn.close()
    assert tat != bat
    _ghi(db, "DELETE FROM wharton_bids")
    conn, cur = _cur(db)
    assert rp.dau_van_tay_du_lieu(cur, {"wharton": True}) != rp.dau_van_tay_du_lieu(
        cur, {"wharton": False})
    conn.close()
