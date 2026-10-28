"""A13.8 lỗi 2.5: `_ngu_canh_diem_chuan` đọc dữ liệu, hồ sơ điểm, `match_results`, dấu vân tay đã lưu
và `run_meta` trong CÙNG một giao dịch đọc (một kết nối), không còn hai kết nối rời. Dữ liệu MÔ PHỎNG."""

import sqlite3

import api as api_mod
from _wharton import bat_wharton
from test_wharton import sinh_bo
from test_wharton_pipeline import _nap_bo_vao_api


def _api(tmp_path):
    bo = sinh_bo(77, n_hs=12, n_clb=4)
    api = api_mod.PipelineAPI(str(tmp_path / "d.db"))
    bat_wharton(api)
    _nap_bo_vao_api(api, bo)
    assert api.run_pipeline(seed=3)["ok"]
    return api


def test_chi_mo_mot_ket_noi_cho_ca_ngu_canh(tmp_path, monkeypatch):
    api = _api(tmp_path)
    goc = sqlite3.connect
    dem = []

    def dem_ket_noi(*a, **k):
        dem.append(a)
        return goc(*a, **k)
    monkeypatch.setattr(sqlite3, "connect", dem_ket_noi)
    api._luat_nghiem()                  # việc đọc cấu hình đứng ngoài giao dịch dữ liệu
    n_luat = len(dem)
    dem.clear()
    loi, ctx = api._ngu_canh_diem_chuan()
    assert loi is None and ctx["co_ket_qua"] and ctx["match"]
    assert len(dem) == n_luat + 1, dem


def test_ket_qua_van_nhu_cu(tmp_path):
    api = _api(tmp_path)
    kq = api.get_diem_chuan()
    assert kq["ok"] and kq["data"]["co_ket_qua"] and kq["data"]["ket_qua_cu"] is False
