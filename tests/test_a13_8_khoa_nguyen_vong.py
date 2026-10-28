"""A13.8, lỗi 2.1 + 3.2: điểm quyết tâm đang khoá thì em ĐÃ có điểm không đổi được nguyện vọng
lẫn ô tick "muốn thi" (kiosk / Quản lý trả `wharton_da_khoa`; nạp CSV / Sổ nhập bỏ qua em đó và
cảnh báo từng em). Gửi lại đúng danh sách cũ thì vẫn ok. Dữ liệu MÔ PHỎNG dựng trong test."""

import pytest

import api as api_mod
from _wharton import bat_wharton, dong_bids, ma_loi, canh_bao
from test_wharton import sinh_bo
from test_wharton_pipeline import _nap_bo_vao_api


def _nk(api):
    with api._ket_noi_doc() as cur:
        return [tuple(r) for r in cur.execute("SELECT * FROM wharton_nhat_ky ORDER BY id")]


def _nv(api, sid):
    with api._ket_noi_doc() as cur:
        return [r[0] for r in cur.execute(
            "SELECT club_id FROM preferences WHERE student_id = ? ORDER BY rank", (sid,))]


def _tick(api, sid):
    with api._ket_noi_doc() as cur:
        return sorted(r[0] for r in cur.execute(
            "SELECT club_id FROM club_test_selection WHERE student_id = ?", (sid,)))


@pytest.fixture
def khoa_san(tmp_path):
    bo = sinh_bo(77, n_hs=12, n_clb=4)
    api = api_mod.PipelineAPI(str(tmp_path / "k.db"))
    bat_wharton(api)
    _nap_bo_vao_api(api, bo)
    assert api.run_pipeline(seed=3)["ok"]
    return api, bo


def _em_co_diem(api, bo):
    co = {d[0] for d in dong_bids(api)}
    return next(s for s in bo.sids if s in co and len(_nv(api, s)) >= 2 and _tick(api, s))


def _snap(api):
    return dong_bids(api), _nk(api)


# ------------------------------------------------------------------ kiosk / Quản lý (API)

def test_submit_preferences_khi_khoa_doi_nguyen_vong_bi_chan(khoa_san):
    api, bo = khoa_san
    sid = _em_co_diem(api, bo)
    cu = _nv(api, sid)
    truoc = _snap(api)
    kq = api.submit_preferences(sid, cu[:1])                       # bỏ bớt CLB: trước đây tỉa im lặng
    assert kq["ok"] is False and [e["code"] for e in kq["errors"]] == ["wharton_da_khoa"]
    assert _nv(api, sid) == cu and _snap(api) == truoc


def test_submit_preferences_khi_khoa_doi_thu_tu_cung_bi_chan(khoa_san):
    api, bo = khoa_san
    sid = _em_co_diem(api, bo)
    cu = _nv(api, sid)
    kq = api.submit_preferences(sid, list(reversed(cu)))
    assert kq["ok"] is False and [e["code"] for e in kq["errors"]] == ["wharton_da_khoa"]
    assert _nv(api, sid) == cu


def test_submit_preferences_khi_khoa_gui_lai_dung_danh_sach_cu_van_ok(khoa_san):
    api, bo = khoa_san
    sid = _em_co_diem(api, bo)
    cu = _nv(api, sid)
    truoc = _snap(api)
    assert api.submit_preferences(sid, cu)["ok"]
    assert _nv(api, sid) == cu and _snap(api) == truoc


def test_submit_preferences_khi_khoa_em_chua_co_diem_van_doi_duoc(khoa_san):
    api, bo = khoa_san
    with api._ket_noi_ghi() as cur:
        cur.execute("DELETE FROM wharton_bids WHERE student_id = ?", (bo.sids[0],))
    sid = bo.sids[0]
    assert api.submit_preferences(sid, _nv(api, sid)[:1])["ok"]


def test_submit_preferences_mo_khoa_roi_thi_doi_duoc_va_tia_diem(khoa_san):
    api, bo = khoa_san
    sid = _em_co_diem(api, bo)
    assert api.mo_khoa_wharton("MO")["ok"]
    assert api.submit_preferences(sid, _nv(api, sid)[:1])["ok"]


def test_submit_test_selection_khi_khoa_doi_tick_bi_chan(khoa_san):
    api, bo = khoa_san
    sid = _em_co_diem(api, bo)
    cu = _tick(api, sid)
    truoc = _snap(api)
    kq = api.submit_test_selection(sid, cu[1:])
    assert kq["ok"] is False and [e["code"] for e in kq["errors"]] == ["wharton_da_khoa"]
    assert _tick(api, sid) == cu and _snap(api) == truoc


def test_submit_test_selection_khi_khoa_gui_lai_dung_tap_cu_van_ok(khoa_san):
    api, bo = khoa_san
    sid = _em_co_diem(api, bo)
    cu = _tick(api, sid)
    truoc = _snap(api)
    assert api.submit_test_selection(sid, list(reversed(cu)))["ok"]
    assert _tick(api, sid) == cu and _snap(api) == truoc


def test_khi_wharton_tat_van_tia_va_doi_nhu_cu(tmp_path):
    """Tắt tính năng: hành vi cũ, không chặn gì."""
    bo = sinh_bo(77, n_hs=12, n_clb=4)
    api = api_mod.PipelineAPI(str(tmp_path / "t.db"))
    bat_wharton(api)
    _nap_bo_vao_api(api, bo)
    assert api.run_pipeline(seed=3)["ok"]
    bat_wharton(api, False)
    sid = _em_co_diem(api, bo)
    assert api.submit_preferences(sid, _nv(api, sid)[:1])["ok"]
    assert api.submit_test_selection(sid, [])["ok"]


# ------------------------------------------------------------------ nạp CSV / Sổ nhập

def test_nap_csv_nguyen_vong_khi_khoa_bo_qua_em_co_diem_va_canh_bao(khoa_san):
    api, bo = khoa_san
    sid = _em_co_diem(api, bo)
    cu = _nv(api, sid)
    truoc = _snap(api)
    kq = api.import_preferences_csv(
        "student_id,name,pref_1\n%s,Em,%s\n" % (sid, cu[0]))
    assert kq["ok"], kq["errors"]
    assert kq["data"]["n_students_with_preferences_written"] == 0
    assert kq["data"]["n_students_skipped"] == 1
    w = canh_bao(kq, "csv_wharton_khoa_giu_nguyen")
    assert len(w) == 1 and w[0]["params"]["student_id"] == sid
    assert _nv(api, sid) == cu and _snap(api) == truoc


def test_nap_csv_nguyen_vong_khi_khoa_dung_danh_sach_cu_van_nap(khoa_san):
    api, bo = khoa_san
    sid = _em_co_diem(api, bo)
    cu = _nv(api, sid)
    csv = "student_id,name," + ",".join("pref_%d" % (i + 1) for i in range(len(cu))) + \
          "\n%s,Em,%s\n" % (sid, ",".join(cu))
    kq = api.import_preferences_csv(csv)
    assert kq["ok"], kq["errors"]
    assert kq["data"]["n_students_with_preferences_written"] == 1
    assert "csv_wharton_khoa_giu_nguyen" not in ma_loi(kq)


def test_nap_csv_nguyen_vong_khi_khoa_em_khac_chua_co_diem_van_nap(khoa_san):
    api, bo = khoa_san
    co_diem = _em_co_diem(api, bo)
    khac = next(s for s in bo.sids if s != co_diem)
    with api._ket_noi_ghi() as cur:
        cur.execute("DELETE FROM wharton_bids WHERE student_id = ?", (khac,))
    cid = _nv(api, khac)[0]
    kq = api.import_preferences_csv(
        "student_id,name,pref_1\n%s,Em,%s\n%s,Em,%s\n" % (
            co_diem, _nv(api, co_diem)[0], khac, cid))
    assert kq["data"]["n_students_with_preferences_written"] == 1
    assert [w["params"]["student_id"] for w in canh_bao(kq, "csv_wharton_khoa_giu_nguyen")] == [co_diem]
    assert _nv(api, khac) == [cid]


def test_nap_csv_chon_thi_khi_khoa_bo_qua_em_co_diem_va_canh_bao(khoa_san):
    api, bo = khoa_san
    sid = _em_co_diem(api, bo)
    cu = _tick(api, sid)
    truoc = _snap(api)
    kq = api.import_test_selection_csv("student_id,name,test_club_1\n%s,Em,%s\n" % (sid, cu[0]))
    assert kq["ok"], kq["errors"]
    assert kq["data"]["n_students_with_selection_written"] == 0
    assert kq["data"]["n_students_skipped"] == 1
    w = canh_bao(kq, "csv_wharton_khoa_giu_nguyen")
    assert len(w) == 1 and w[0]["params"]["student_id"] == sid
    assert _tick(api, sid) == cu and _snap(api) == truoc


def test_nap_csv_chon_thi_khi_khoa_dung_tap_cu_van_nap(khoa_san):
    api, bo = khoa_san
    sid = _em_co_diem(api, bo)
    cu = _tick(api, sid)
    csv = "student_id,name," + ",".join("test_club_%d" % (i + 1) for i in range(len(cu))) + \
          "\n%s,Em,%s\n" % (sid, ",".join(cu))
    kq = api.import_test_selection_csv(csv)
    assert kq["ok"], kq["errors"]
    assert kq["data"]["n_students_with_selection_written"] == 1
    assert _tick(api, sid) == cu
