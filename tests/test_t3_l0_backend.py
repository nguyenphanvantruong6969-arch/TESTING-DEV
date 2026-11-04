"""T3-L0 (B1/T3-26, B2/T3-01, B3/T3-42): ba lỗi sản phẩm, tầng backend. Dữ liệu MÔ PHỎNG dựng trong test."""

import pytest

from _wharton import tat_wharton
from i18n_errors import format_message


@pytest.fixture
def api(api):
    tat_wharton(api)
    return api


def _clb(api, cid):
    with api._ket_noi_doc() as cur:
        return tuple(cur.execute(
            "SELECT name, capacity, reserve_capacity, reserve_group, buoi FROM clubs WHERE club_id = ?",
            (cid,)).fetchone())


# ---------------------------------------------------------------- B1 / T3-26
def test_sua_chi_tieu_khong_xoa_suat_du_tru_nhom_buoi(api):
    assert api.create_or_update_club("clb_k", "CLB K", 10, 4, "chinh_sach", "thu_2")["ok"]
    # Gọi thiếu ba trường cuối = "không gửi": chỉ đổi tên và chỉ tiêu.
    assert api.create_or_update_club("clb_k", "CLB K moi", 20)["ok"]
    assert _clb(api, "clb_k") == ("CLB K moi", 20, 4, "chinh_sach", "thu_2")


def test_gui_ro_rang_thi_van_xoa_duoc(api):
    api.create_or_update_club("clb_k", "CLB K", 10, 4, "chinh_sach", "thu_2")
    assert api.create_or_update_club("clb_k", "CLB K", 10, 0, "", "")["ok"]
    assert _clb(api, "clb_k") == ("CLB K", 10, 0, None, None)


def test_none_nhu_khong_gui_giu_ten_cu(api):
    api.create_or_update_club("clb_k", "CLB K", 10, 4, "chinh_sach", "thu_2")
    assert api.create_or_update_club("clb_k", None, 12, None, None, None)["ok"]
    assert _clb(api, "clb_k") == ("CLB K", 12, 4, "chinh_sach", "thu_2")


def test_clb_moi_thieu_truong_lay_mac_dinh(api):
    assert api.create_or_update_club("clb_m", "CLB M", 8)["ok"]
    assert _clb(api, "clb_m") == ("CLB M", 8, 0, None, None)


def test_ha_chi_tieu_duoi_suat_du_tru_cu_bi_tu_choi_va_khong_ghi(api):
    api.create_or_update_club("clb_k", "CLB K", 10, 4, "chinh_sach", "thu_2")
    r = api.create_or_update_club("clb_k", "CLB K", 3)  # suất cũ 4 > 3
    assert not r["ok"] and r["errors"][0]["code"] == "reserve_capacity_exceeds_capacity"
    assert _clb(api, "clb_k") == ("CLB K", 10, 4, "chinh_sach", "thu_2")


# ---------------------------------------------------------------- B2 / T3-01
def _dem(api):
    with api._ket_noi_doc() as cur:
        return (cur.execute("SELECT COUNT(*) FROM run_history").fetchone()[0],
                cur.execute("SELECT COALESCE(SUM(is_locked), 0) FROM stb_lock").fetchone()[0],
                cur.execute("SELECT COUNT(*) FROM match_results").fetchone()[0])


def test_chay_khong_hoc_sinh_khong_clb_bi_chan_khong_ghi_gi(api):
    truoc = _dem(api)
    r = api.run_pipeline(42)
    assert r["ok"] is False
    assert [e["code"] for e in r["errors"]] == ["chua_co_du_lieu_de_chay"]
    assert _dem(api) == truoc == (0, 0, 0)
    assert api.get_stb_lock_status()["data"].get("locked") in (False, None, 0)


def test_chay_co_clb_nhung_khong_hoc_sinh_bi_chan(api):
    api.create_or_update_club("clb_a", "A", 5)
    r = api.run_pipeline(42)
    assert not r["ok"] and r["errors"][0]["code"] == "chua_co_du_lieu_de_chay"
    assert _dem(api) == (0, 0, 0)


def test_chay_co_hoc_sinh_nhung_khong_clb_bi_chan(api):
    with api._ket_noi_ghi() as cur:
        cur.execute("INSERT INTO students (student_id, name) VALUES ('s1', 'S1')")
    r = api.run_pipeline(42)
    assert not r["ok"] and r["errors"][0]["code"] == "chua_co_du_lieu_de_chay"
    assert _dem(api) == (0, 0, 0)


def test_sau_khi_bi_chan_seed_khac_van_chay_duoc_khi_co_du_lieu(api):
    api.run_pipeline(42)  # bị chặn
    api.create_or_update_club("clb_a", "A", 5)
    with api._ket_noi_ghi() as cur:
        cur.execute("INSERT INTO students (student_id, name) VALUES ('s1', 'S1')")
    assert api.run_pipeline(7)["ok"]  # seed 42 không bị khoá oan


# ---------------------------------------------------------------- B3 / T3-42
@pytest.mark.parametrize("lang", ["vi", "en"])
def test_cau_wharton_khong_bao_tat_tinh_nang(lang):
    van = format_message("wharton_ho_so_chua_hop_le", {"n": 2, "person_l": "x"}, lang)
    thap = van.lower()
    assert "tắt" not in thap and "turn off" not in thap
    assert ("Điểm quyết tâm" in van and "Phóng cho đủ 100" in van) if lang == "vi" else (
        "Commitment points" in van and "Scale to 100" in van)
