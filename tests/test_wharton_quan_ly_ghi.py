"""Điểm Wharton (A13.3): API ghi cho thẻ Quản lý — `admin_save_wharton` và `clear_wharton`.

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.

Điều phải giữ:
  * `admin_save_wharton` dùng lại lõi của `submit_wharton` (cùng ok / errors / dòng CSDL), chỉ khác
    `nguon` của nhật ký là `quan_ly`;
  * `clear_wharton(sid)` xoá điểm một em; `clear_wharton(None, "XOA")` xoá tất cả, sao lưu trước;
  * đang khoá thì cả hai trả `wharton_da_khoa`; Wharton tắt thì `wharton_chua_bat`.
"""

import json
import os

import pytest

from _wharton import bat_wharton, chen_bids, dong_bids, dung_clb, dung_hs


def _nk(api):
    with api._ket_noi_doc() as cur:
        return [(r["nguon"], r["hanh_dong"], r["student_id"],
                 json.loads(r["cu_json"]) if r["cu_json"] else None,
                 json.loads(r["moi_json"]) if r["moi_json"] else None)
                for r in cur.execute("SELECT * FROM wharton_nhat_ky ORDER BY id")]


def _khoa(api):
    with api._ket_noi_ghi() as cur:
        cur.execute("INSERT INTO wharton_lock (id, is_locked, locked_at) VALUES (1, 1, 't') "
                    "ON CONFLICT(id) DO UPDATE SET is_locked = 1")


@pytest.fixture
def w(api):
    """Wharton bật; HS1 tick A, nguyện vọng A, B, C; HS2 nguyện vọng B, C."""
    bat_wharton(api)
    dung_clb(api, A=5, B=5, C=5)
    dung_hs(api, "HS1", "HS2", tick={"HS1": ["A"]})
    assert api.submit_preferences("HS1", ["A", "B", "C"])["ok"]
    assert api.submit_preferences("HS2", ["B", "C"])["ok"]
    return api


# ------------------------------------------------------------------ admin_save_wharton

DAU_VAO = [
    ({"A": 100}, {"B": 60, "C": 40}),             # hợp lệ
    ({}, {"B": 70, "C": 30}),                     # quỹ 1 một CLB: tự điền trong bộ nhớ
    ({"A": 100}, {"B": 50, "C": 40}),             # thiếu
    ({"A": 100}, {"B": 60, "C": 50}),             # vượt
    ({"B": 100}, {"C": 100}),                     # ngoài tập
]


@pytest.mark.parametrize("w1,w2", DAU_VAO)
def test_cung_ket_qua_voi_submit_wharton_chi_khac_nguon_nhat_ky(tmp_path, w1, w2):
    import api as api_mod
    ket = []
    for ham in ("submit_wharton", "admin_save_wharton"):
        a = api_mod.PipelineAPI(str(tmp_path / (ham + ".db")))
        bat_wharton(a)
        dung_clb(a, A=5, B=5, C=5)
        dung_hs(a, "HS1", tick={"HS1": ["A"]})
        assert a.submit_preferences("HS1", ["A", "B", "C"])["ok"]
        kq = getattr(a, ham)("HS1", dict(w1), dict(w2))
        ket.append((kq, dong_bids(a), _nk(a)))
    (k1, d1, n1), (k2, d2, n2) = ket
    assert k1 == k2 and d1 == d2
    assert [n[1:] for n in n1] == [n[1:] for n in n2]            # cùng hành động, cùng cũ / mới
    assert {n[0] for n in n1} <= {"kiosk"} and {n[0] for n in n2} <= {"quan_ly"}


def test_admin_save_sua_diem_ghi_cu_va_moi(w):
    assert w.admin_save_wharton("HS1", {"A": 100}, {"B": 60, "C": 40})["ok"]
    assert w.admin_save_wharton("HS1", {"A": 100}, {"B": 10, "C": 90})["ok"]
    nk = _nk(w)
    assert [n[:3] for n in nk] == [("quan_ly", "luu", "HS1")] * 2
    assert nk[1][3] == {"w1": {"A": 100}, "w2": {"B": 60, "C": 40}}
    assert nk[1][4] == {"w1": {"A": 100}, "w2": {"B": 10, "C": 90}}


def test_admin_save_ho_so_sai_khong_doi_gi(w):
    kq = w.admin_save_wharton("HS1", {"A": 100}, {"B": 50, "C": 40})
    assert kq["ok"] is False and kq["errors"][0]["code"] == "wharton_chua_dung_het"
    assert dong_bids(w) == [] and _nk(w) == []


def test_admin_save_em_khong_ton_tai(w):
    kq = w.admin_save_wharton("KHONG_CO", {}, {})
    assert [e["code"] for e in kq["errors"]] == ["student_not_found"]


def test_admin_save_khi_khoa(w):
    _khoa(w)
    kq = w.admin_save_wharton("HS1", {"A": 100}, {"B": 60, "C": 40})
    assert [e["code"] for e in kq["errors"]] == ["wharton_da_khoa"]
    assert dong_bids(w) == [] and _nk(w) == []


# ------------------------------------------------------------------ clear_wharton (một em)

def test_xoa_mot_em_chi_xoa_em_do_va_ghi_nhat_ky(w):
    chen_bids(w, [("HS1", "A", 1, 100), ("HS1", "B", 2, 100), ("HS2", "B", 2, 100)])
    kq = w.clear_wharton("HS1")
    assert kq["ok"], kq["errors"]
    assert kq["data"]["student_id"] == "HS1" and kq["data"]["n_rows"] == 2
    assert dong_bids(w) == [("HS2", "B", 2, 100)]
    assert _nk(w) == [("quan_ly", "xoa_mot_em", "HS1", {"w1": {"A": 100}, "w2": {"B": 100}}, None)]


def test_xoa_mot_em_khong_co_diem_thi_ok_va_khong_ghi(w):
    kq = w.clear_wharton("HS1")
    assert kq["ok"] and kq["data"]["n_rows"] == 0 and _nk(w) == []


def test_xoa_mot_em_khong_ton_tai(w):
    assert [e["code"] for e in w.clear_wharton("KHONG_CO")["errors"]] == ["student_not_found"]


def test_xoa_mot_em_khi_khoa(w):
    chen_bids(w, [("HS1", "A", 1, 100)])
    _khoa(w)
    assert [e["code"] for e in w.clear_wharton("HS1")["errors"]] == ["wharton_da_khoa"]
    assert dong_bids(w) == [("HS1", "A", 1, 100)] and _nk(w) == []


# ------------------------------------------------------------------ clear_wharton (tất cả)

def _so_ban_sao(api):
    return len([f for f in os.listdir(os.path.dirname(api.db_path)) if ".bak-" in f])


def test_xoa_tat_ca_go_dung_chu_xoa_sao_luu_va_ghi_mot_dong_tong(w):
    chen_bids(w, [("HS1", "A", 1, 100), ("HS1", "B", 2, 100), ("HS2", "B", 2, 100)])
    truoc = _so_ban_sao(w)
    kq = w.clear_wharton(None, "XOA")
    assert kq["ok"], kq["errors"]
    assert kq["data"]["n_students"] == 2 and kq["data"]["n_rows"] == 3
    assert os.path.exists(kq["data"]["backup_path"])
    assert kq["data"]["backup_name"] == os.path.basename(kq["data"]["backup_path"])
    assert _so_ban_sao(w) == truoc + 1
    assert dong_bids(w) == []
    nk = _nk(w)
    assert len(nk) == 1 and nk[0][:3] == ("quan_ly", "xoa_tat_ca", None)
    assert nk[0][3] == {"so_dong": 3, "ma_hoc_sinh": ["HS1", "HS2"]} and nk[0][4] is None


@pytest.mark.parametrize("go", ["", "xoa", "XÓA", "MO", None])
def test_xoa_tat_ca_sai_chu_khong_doi_gi_va_khong_sao_luu(w, go):
    chen_bids(w, [("HS1", "A", 1, 100)])
    truoc = _so_ban_sao(w)
    kq = w.clear_wharton(None, go)
    assert [e["code"] for e in kq["errors"]] == ["wharton_xoa_sai_xac_nhan"]
    assert dong_bids(w) == [("HS1", "A", 1, 100)] and _nk(w) == [] and _so_ban_sao(w) == truoc


def test_xoa_tat_ca_khi_khoa_va_khi_tat(w, api):
    chen_bids(w, [("HS1", "A", 1, 100)])
    _khoa(w)
    truoc = _so_ban_sao(w)
    assert [e["code"] for e in w.clear_wharton(None, "XOA")["errors"]] == ["wharton_da_khoa"]
    assert dong_bids(w) == [("HS1", "A", 1, 100)] and _so_ban_sao(w) == truoc
    bat_wharton(w, bat=False)
    for kq in (w.clear_wharton(None, "XOA"), w.clear_wharton("HS1"),
               w.admin_save_wharton("HS1", {}, {})):
        assert [e["code"] for e in kq["errors"]] == ["wharton_chua_bat"]


def test_xoa_tat_ca_khi_bang_rong_van_ok(w):
    kq = w.clear_wharton(None, "XOA")
    assert kq["ok"] and kq["data"]["n_rows"] == 0 and kq["data"]["n_students"] == 0
    assert _nk(w) == []
