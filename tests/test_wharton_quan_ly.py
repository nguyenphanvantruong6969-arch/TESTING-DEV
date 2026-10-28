"""Điểm Wharton (A13.3): API đọc cho thẻ Quản lý — bảng điểm, cảnh báo, nhật ký.

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.

Điều phải giữ:
  * `list_wharton_admin`: phân trang và tìm như `list_students_admin`, mỗi ô điểm kèm cờ `tu_dien`
    (ô 100 tự điền trong bộ nhớ, không có trong CSDL), tổng mỗi quỹ mỗi buổi, lỗi và vắng thi của
    em; bộ lọc quỹ / buổi / CLB / "chỉ hồ sơ có vấn đề";
  * `list_wharton_canh_bao` trùng với hai mục Wharton của `get_data_health_report`;
  * `get_wharton_nhat_ky`: dòng mới nhất trước, có phân trang;
  * Wharton tắt: cả ba trả `wharton_chua_bat`;
  * 2000 em × 5 nguyện vọng: trang đầu dưới 2 giây.
"""

import time

import pytest

from _wharton import bat_wharton, chen_bids, dung_clb, dung_hs


@pytest.fixture
def w(api):
    """Wharton bật; CLB A (thi), B, C ở thứ 3, D ở thứ 5; bốn em với đủ loại hồ sơ.

    HS1 Nguyễn Văn Bình : hợp lệ.
    HS2 Trần Thị Lan    : quỹ 2 mới 90 điểm (chưa chia đủ).
    HS3 Lê Hoàng Nam    : tick thi A nhưng vắng thi (không có điểm thi), hồ sơ hợp lệ.
    HS4 Phạm Quang Huy  : mỗi quỹ đúng một CLB, để trống: tự điền 100.
    """
    bat_wharton(api)
    dung_clb(api, A=(5, "thu_3"), B=(5, "thu_3"), C=(5, "thu_3"), D=(5, "thu_5"))
    for sid, ten in (("HS1", "Nguyễn Văn Bình"), ("HS2", "Trần Thị Lan"),
                     ("HS3", "Lê Hoàng Nam"), ("HS4", "Phạm Quang Huy")):
        assert api.create_student_if_missing(sid, ten)["ok"]
    for sid in ("HS1", "HS2", "HS3"):
        assert api.submit_test_selection(sid, ["A"])["ok"]
    assert api.submit_test_selection("HS4", ["A"])["ok"]
    assert api.submit_preferences("HS1", ["A", "B", "C", "D"])["ok"]
    assert api.submit_preferences("HS2", ["A", "B", "C"])["ok"]
    assert api.submit_preferences("HS3", ["A", "B"])["ok"]
    assert api.submit_preferences("HS4", ["A", "B"])["ok"]
    assert api.submit_club_scores("A", [{"student_id": "HS1", "score": 8},
                                        {"student_id": "HS2", "score": 7},
                                        {"student_id": "HS4", "score": 6}])["ok"]
    chen_bids(api, [("HS1", "A", 1, 100), ("HS1", "B", 2, 60), ("HS1", "C", 2, 40),
                    ("HS1", "D", 2, 100),
                    ("HS2", "A", 1, 100), ("HS2", "B", 2, 60), ("HS2", "C", 2, 30),
                    ("HS3", "A", 1, 100), ("HS3", "B", 2, 100)])
    return api


def _ds(kq):
    assert kq["ok"], kq["errors"]
    return kq["data"]


def _theo_ma(kq):
    return {r["student_id"]: r for r in _ds(kq)["rows"]}


# ------------------------------------------------------------------ list_wharton_admin

def test_dong_cua_em_hop_le_co_o_diem_theo_buoi_va_tong(w):
    r = _theo_ma(w.list_wharton_admin())["HS1"]
    assert r["name"] == "Nguyễn Văn Bình"
    assert [(d["club_id"], d["buoi"], d["quy"], d["diem"], d["tu_dien"], d["ten_clb"])
            for d in r["diem"]] == [
        ("A", "thu_3", 1, 100, False, "CLB A"), ("B", "thu_3", 2, 60, False, "CLB B"),
        ("C", "thu_3", 2, 40, False, "CLB C"), ("D", "thu_5", 2, 100, False, "CLB D")]
    assert r["tong"] == {"thu_3": {"1": 100, "2": 100}, "thu_5": {"1": 0, "2": 100}}
    assert r["loi"] == [] and r["vang_thi"] == [] and r["lech_tick"] is False


def test_o_tu_dien_trong_bo_nho_co_co_tu_dien_va_tinh_vao_tong(w):
    r = _theo_ma(w.list_wharton_admin())["HS4"]
    assert [(d["club_id"], d["quy"], d["diem"], d["tu_dien"]) for d in r["diem"]] == [
        ("A", 1, 100, True), ("B", 2, 100, True)]
    assert r["tong"] == {"thu_3": {"1": 100, "2": 100}}
    assert r["loi"] == []
    with w._ket_noi_doc() as cur:                           # và KHÔNG có trong CSDL
        assert cur.execute("SELECT COUNT(*) FROM wharton_bids WHERE student_id = 'HS4'"
                           ).fetchone()[0] == 0


def test_loi_cua_em_chua_chia_du(w):
    r = _theo_ma(w.list_wharton_admin())["HS2"]
    assert [e["code"] for e in r["loi"]] == ["wharton_chua_dung_het"]
    assert r["loi"][0]["params"]["student_id"] == "HS2"
    assert r["tong"] == {"thu_3": {"1": 100, "2": 90}}


def test_vang_thi_khong_nam_trong_loi(w):
    r = _theo_ma(w.list_wharton_admin())["HS3"]
    assert r["vang_thi"] == ["A"] and r["loi"] == []


def test_em_chua_co_nguyen_vong_van_co_dong_nhung_khong_co_o_diem(w):
    dung_hs(w, "HS9")
    r = _theo_ma(w.list_wharton_admin())["HS9"]
    assert r["diem"] == [] and r["tong"] == {} and r["loi"] == []


def test_o_chua_dat_co_diem_none(w):
    assert w.submit_preferences("HS4", ["A", "B", "C"])["ok"]       # quỹ 2 nay có B, C chưa chia
    r = _theo_ma(w.list_wharton_admin())["HS4"]
    cell = {d["club_id"]: d for d in r["diem"]}
    assert cell["B"]["diem"] is None and cell["B"]["tu_dien"] is False and cell["B"]["quy"] == 2
    assert [e["code"] for e in r["loi"]] == ["wharton_chua_dung_het"]


def test_lech_tick_khi_doi_o_tick_sau_khi_chia(w):
    assert w.submit_test_selection("HS1", ["A", "B"])["ok"]         # B chuyển sang quỹ 1
    r = _theo_ma(w.list_wharton_admin())["HS1"]
    assert r["lech_tick"] is True
    b = [d for d in r["diem"] if d["club_id"] == "B"][0]
    assert (b["quy"], b["diem"]) == (2, 60)                         # giữ nguyên chỗ đã lưu


def test_phan_trang_nhu_list_students_admin(w):
    a = _ds(w.list_wharton_admin(page=1, page_size=3))
    b = _ds(w.list_wharton_admin(page=2, page_size=3))
    assert (a["total"], a["total_pages"], a["page"], a["page_size"]) == (4, 2, 1, 3)
    assert [r["student_id"] for r in a["rows"]] == ["HS1", "HS2", "HS3"]
    assert [r["student_id"] for r in b["rows"]] == ["HS4"]
    assert _ds(w.list_wharton_admin(page=1, page_size=9999))["page_size"] == 500


@pytest.mark.parametrize("q,mong", [("binh", ["HS1"]), ("BÌNH", ["HS1"]), ("hs3", ["HS3"]),
                                    ("nguyen van", ["HS1"]), ("zzz", [])])
def test_tim_khong_dau(w, q, mong):
    d = _ds(w.list_wharton_admin(search=q))
    assert [r["student_id"] for r in d["rows"]] == mong and d["total"] == len(mong)


def test_chi_loi_chi_tra_em_co_loi_hoac_vang_thi(w):
    d = _ds(w.list_wharton_admin(chi_loi=True))
    assert [r["student_id"] for r in d["rows"]] == ["HS2", "HS3"] and d["total"] == 2


def test_loc_theo_quy_buoi_clb_chi_giu_o_khop(w):
    r = _theo_ma(w.list_wharton_admin(quy=1))
    assert set(r) == {"HS1", "HS2", "HS3", "HS4"}
    assert all(d["quy"] == 1 for x in r.values() for d in x["diem"])
    r = _theo_ma(w.list_wharton_admin(buoi="thu_5"))
    assert set(r) == {"HS1"} and [d["club_id"] for d in r["HS1"]["diem"]] == ["D"]
    r = _theo_ma(w.list_wharton_admin(club_id="C"))
    assert set(r) == {"HS1", "HS2"}
    assert all([d["club_id"] for d in x["diem"]] == ["C"] for x in r.values())
    assert _ds(w.list_wharton_admin(club_id="C"))["total"] == 2


def test_loc_ket_hop_va_loc_khong_co_ket_qua(w):
    assert _ds(w.list_wharton_admin(quy=1, buoi="thu_5"))["rows"] == []
    d = _ds(w.list_wharton_admin(club_id="B", chi_loi=True))
    assert [r["student_id"] for r in d["rows"]] == ["HS2", "HS3"]


# ------------------------------------------------------------------ list_wharton_canh_bao

def test_canh_bao_liet_ke_em_chua_hop_le_va_vang_thi(w):
    ds = _ds(w.list_wharton_canh_bao())
    assert [(c["student_id"], c["name"], c["loai"], c["ma_loi"]) for c in ds] == [
        ("HS2", "Trần Thị Lan", "chua_hop_le", ["wharton_chua_dung_het"]),
        ("HS3", "Lê Hoàng Nam", "vang_thi", ["wharton_vang_thi"])]


def test_canh_bao_trung_voi_bao_cao_suc_khoe_du_lieu(w):
    ds = _ds(w.list_wharton_canh_bao())
    bc = {x["code"]: x["params"] for x in
          _ds(w.get_data_health_report())["warnings"] if "wharton" in x["code"]}
    assert bc["health_wharton_chua_hop_le"]["n"] == len(
        [c for c in ds if c["loai"] == "chua_hop_le"])
    assert bc["health_wharton_vang_thi"]["n"] == len([c for c in ds if c["loai"] == "vang_thi"])


def test_em_vua_sai_vua_vang_thi_co_hai_dong_canh_bao(w):
    with w._ket_noi_ghi() as cur:
        cur.execute("UPDATE wharton_bids SET points = 50 WHERE student_id = 'HS3' AND club_id = 'B'")
    ds = _ds(w.list_wharton_canh_bao())
    assert [(c["student_id"], c["loai"]) for c in ds if c["student_id"] == "HS3"] == [
        ("HS3", "chua_hop_le"), ("HS3", "vang_thi")]


def test_tat_ca_hop_le_thi_canh_bao_rong(api):
    bat_wharton(api)
    assert _ds(api.list_wharton_canh_bao()) == []


# ------------------------------------------------------------------ get_wharton_nhat_ky

def test_nhat_ky_moi_nhat_truoc_va_phan_trang(w):
    # dựng nhật ký rõ ràng: ba lần lưu liên tiếp của HS2 với điểm khác nhau
    for b in (50, 40, 30):
        assert w.submit_wharton("HS2", {"A": 100}, {"B": b, "C": 100 - b})["ok"]
    d = _ds(w.get_wharton_nhat_ky(student_id="HS2", page=1, page_size=2))
    assert d["total"] == 3 and d["total_pages"] == 2
    assert [r["moi"]["w2"]["B"] for r in d["rows"]] == [30, 40]       # mới nhất trước
    d2 = _ds(w.get_wharton_nhat_ky(student_id="HS2", page=2, page_size=2))
    assert [r["moi"]["w2"]["B"] for r in d2["rows"]] == [50]
    assert set(d["rows"][0]) >= {"id", "luc", "nguon", "nguoi", "hanh_dong", "student_id", "cu", "moi"}
    toan = _ds(w.get_wharton_nhat_ky())
    assert toan["total"] >= 3 and toan["rows"][0]["id"] > toan["rows"][-1]["id"]


# ------------------------------------------------------------------ Wharton tắt

def test_wharton_tat_ba_ham_bao_chua_bat(api):
    for kq in (api.list_wharton_admin(), api.list_wharton_canh_bao(), api.get_wharton_nhat_ky()):
        assert kq["ok"] is False and [e["code"] for e in kq["errors"]] == ["wharton_chua_bat"]


# ------------------------------------------------------------------ hiệu năng

def test_2000_em_5_nguyen_vong_trang_dau_duoi_2_giay(api):
    bat_wharton(api)
    dung_clb(api, A=500, B=500, C=500, D=500, E=500)
    with api._ket_noi_ghi() as cur:
        cur.executemany("INSERT INTO students (student_id, name) VALUES (?, ?)",
                        [("S%04d" % i, "Em so %d" % i) for i in range(2000)])
        cur.executemany("INSERT INTO club_test_selection VALUES (?, ?)",
                        [("S%04d" % i, "A") for i in range(2000)])
        cur.executemany("INSERT INTO preferences VALUES (?, ?, ?)",
                        [("S%04d" % i, c, k + 1) for i in range(2000)
                         for k, c in enumerate("ABCDE")])
        cur.executemany("INSERT INTO wharton_bids VALUES (?, ?, ?, ?)",
                        [("S%04d" % i, c, t, p) for i in range(2000)
                         for c, t, p in (("A", 1, 100), ("B", 2, 25), ("C", 2, 25),
                                         ("D", 2, 25), ("E", 2, 25))])
    t0 = time.perf_counter()
    d = _ds(api.list_wharton_admin(page=1, page_size=100))
    dt = time.perf_counter() - t0
    assert d["total"] == 2000 and len(d["rows"]) == 100
    assert dt < 2.0, dt
    t0 = time.perf_counter()
    _ds(api.list_wharton_canh_bao())
    assert time.perf_counter() - t0 < 2.0
