"""Điểm Wharton (A13.3): khoá riêng `wharton_lock` — tự khoá sau lần chạy phân bổ, mở bằng `mo_khoa_wharton`.

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.

Điều phải giữ:
  * Wharton bật + chạy thành công (kể cả chạy riêng một số buổi) thì khoá, trong cùng giao dịch ghi
    kết quả; chặn hay hỏng (rollback) thì KHÔNG khoá; Wharton tắt thì không có dòng khoá nào;
  * đang khoá thì mọi cửa GHI điểm trả `wharton_da_khoa`, CSDL không đổi, không có dòng nhật ký;
  * các cửa XOÁ (xoá học sinh, làm lại từ đầu, xoá CLB, tỉa nguyện vọng, xoá dữ liệu) vẫn chạy và
    ghi nhật ký (quyết định B.4.3);
  * mở khoá cần gõ đúng "MO", ghi nhật ký, KHÔNG đụng STB; `reset_data` mở luôn khoá.
"""

import json

import pytest

import api as api_mod
from _wharton import bat_wharton, dong_bids, ma_loi
from test_wharton import sinh_bo
from test_wharton_pipeline import _nap_bo_vao_api, _trang_thai_stb


def _khoa(api):
    with api._ket_noi_doc() as cur:
        r = cur.execute("SELECT is_locked, locked_at, unlocked_at FROM wharton_lock").fetchall()
    return [tuple(x) for x in r]


def _nk(api):
    with api._ket_noi_doc() as cur:
        return [(r["nguon"], r["hanh_dong"], r["student_id"]) for r in cur.execute(
            "SELECT * FROM wharton_nhat_ky ORDER BY id")]


@pytest.fixture
def da_chay(tmp_path):
    """Wharton bật, 12 em × 4 CLB hồ sơ hợp lệ, ĐÃ chạy một lần thành công (nên đang khoá)."""
    bo = sinh_bo(77, n_hs=12, n_clb=4)
    api = api_mod.PipelineAPI(str(tmp_path / "k.db"))
    bat_wharton(api)
    _nap_bo_vao_api(api, bo)
    return api, bo


@pytest.fixture
def khoa_san(da_chay):
    api, bo = da_chay
    assert api.run_pipeline(seed=3)["ok"]
    return api, bo


# ------------------------------------------------------------------ tự khoá sau khi chạy

def test_chay_thanh_cong_thi_khoa_va_ghi_nhat_ky_he_thong(da_chay):
    api, _bo = da_chay
    assert _khoa(api) == []
    assert api.run_pipeline(seed=3)["ok"]
    (is_locked, locked_at, unlocked_at), = _khoa(api)
    assert is_locked == 1 and locked_at and unlocked_at is None
    assert _nk(api)[-1] == ("he_thong", "khoa", None)
    assert api.get_wharton_lock_status()["data"] == {
        "is_locked": True, "locked_at": locked_at, "unlocked_at": None}


def test_chay_rieng_mot_buoi_cung_khoa(tmp_path):
    bo = sinh_bo(78, n_hs=12, n_clb=4, so_buoi=2)
    api = api_mod.PipelineAPI(str(tmp_path / "b.db"))
    bat_wharton(api)
    _nap_bo_vao_api(api, bo)
    buoi = sorted({(c.get("buoi") or "") for c in bo.d[1].values()})[0]
    assert api.run_pipeline(seed=3, chi_buoi=[buoi])["ok"]
    assert _khoa(api)[0][0] == 1


def test_chay_bi_chan_vi_ho_so_sai_thi_khong_khoa(da_chay):
    api, bo = da_chay
    sid = bo.sids[0]
    with api._ket_noi_ghi() as cur:
        cur.execute("UPDATE wharton_bids SET points = points + 1 WHERE student_id = ? AND rowid = "
                    "(SELECT MIN(rowid) FROM wharton_bids WHERE student_id = ?)", (sid, sid))
    nk0 = _nk(api)
    assert api.run_pipeline(seed=3)["ok"] is False
    assert _khoa(api) == [] and _nk(api) == nk0


def test_chay_hong_giua_chung_rollback_thi_khong_khoa(da_chay, monkeypatch):
    api, _bo = da_chay

    def hong(*a, **k):
        raise RuntimeError("hong khi ghi run_history")
    monkeypatch.setattr(api_mod, "luat_xep_de_ghi", hong)
    nk0 = _nk(api)
    assert api.run_pipeline(seed=3)["ok"] is False
    assert _khoa(api) == [] and _nk(api) == nk0


def test_wharton_tat_chay_xong_khong_co_dong_khoa_va_khong_nhat_ky(tmp_path):
    bo = sinh_bo(79, n_hs=12, n_clb=4)
    api = api_mod.PipelineAPI(str(tmp_path / "t.db"))
    for cid in bo.cids:
        assert api.create_or_update_club(cid, cid, bo.cap[cid], 0, "", "")["ok"]
    for sid in bo.sids:
        assert api.create_student_if_missing(sid, sid)["ok"]
        assert api.submit_test_selection(sid, sorted(bo.tick[sid]))["ok"]
        assert api.submit_preferences(sid, bo.prefs[sid])["ok"]
    for cid in bo.cids:
        diem = [{"student_id": s, "score": v} for s, v in bo.diem_thi[cid].items()]
        if diem:
            assert api.submit_club_scores(cid, diem)["ok"]
    assert api.run_pipeline(seed=3)["ok"]
    assert _khoa(api) == [] and _nk(api) == []
    assert api.get_wharton_lock_status()["data"] == {
        "is_locked": False, "locked_at": None, "unlocked_at": None}


# ------------------------------------------------------------------ đang khoá: cửa ghi bị chặn

def test_submit_wharton_bi_chan_khi_khoa(khoa_san):
    api, bo = khoa_san
    truoc, nk_truoc = dong_bids(api), _nk(api)
    sid = bo.sids[0]
    kq = api.submit_wharton(sid, bo.w1.get(sid, {}), bo.w2.get(sid, {}))
    assert kq["ok"] is False and [e["code"] for e in kq["errors"]] == ["wharton_da_khoa"]
    assert dong_bids(api) == truoc and _nk(api) == nk_truoc


def test_nap_tep_khi_khoa_van_nap_nguyen_vong_chi_bo_phan_wharton(khoa_san):
    api, bo = khoa_san
    sid = bo.sids[0]
    truoc, nk_truoc = dong_bids(api), _nk(api)
    cid = bo.prefs[sid][0]
    kq = api.import_preferences_csv(
        "student_id,name,pref_1,wp_1\n%s,Em,%s,7\n" % (sid, cid))
    assert kq["ok"], kq["errors"]
    assert kq["data"]["n_students_with_preferences_written"] == 1
    assert ma_loi(kq).count("wharton_da_khoa") == 1
    # nguyện vọng đã đổi (chỉ còn cid), phần tỉa vẫn chạy nên dòng của CLB khác đi theo;
    # dòng của cid giữ nguyên giá trị cũ (7 KHÔNG được ghi)
    con = [d for d in dong_bids(api) if d[0] == sid]
    assert all(d[1] == cid for d in con)
    assert con == [d for d in truoc if d[0] == sid and d[1] == cid]
    da_tia = any(d[0] == sid and d[1] != cid for d in truoc)
    assert _nk(api)[len(nk_truoc):] == ([("nap_tep", "luu", sid)] if da_tia else [])


def test_nap_tep_khi_khoa_khong_co_o_wp_thi_khong_canh_bao_khoa(khoa_san):
    api, bo = khoa_san
    sid = bo.sids[0]
    kq = api.import_preferences_csv("student_id,name,pref_1\n%s,Em,%s\n" % (sid, bo.prefs[sid][0]))
    assert kq["ok"] and "wharton_da_khoa" not in ma_loi(kq)


# ------------------------------------------------------------------ đang khoá: cửa xoá vẫn chạy

def test_cua_xoa_van_chay_khi_khoa_va_ghi_nhat_ky(khoa_san):
    api, bo = khoa_san
    a, b, c = bo.sids[0], bo.sids[1], bo.sids[2]
    n0 = len(_nk(api))
    assert api.submit_preferences(a, [bo.prefs[a][0]])["ok"]                 # tỉa
    assert api.reset_student_entry(b)["ok"]
    with api._ket_noi_ghi() as cur:                                          # chưa có kết quả để xoá
        cur.execute("DELETE FROM match_results WHERE student_id = ?", (c,))
    assert api.delete_student(c)["ok"]
    moi = _nk(api)[n0:]
    assert ("kiosk", "tia_nguyen_vong", a) in moi
    assert ("kiosk", "xoa_mot_em", b) in moi
    assert ("quan_ly", "xoa_mot_em", c) in moi
    assert [d for d in dong_bids(api) if d[0] in (b, c)] == []


# ------------------------------------------------------------------ mở khoá

def test_mo_khoa_dung_chu_mo_khoa_ghi_nhat_ky_va_khong_dung_stb(khoa_san):
    api, bo = khoa_san
    stb_truoc = _trang_thai_stb(api)
    kq = api.mo_khoa_wharton("MO")
    assert kq["ok"], kq["errors"]
    (is_locked, _lock, unlocked_at), = _khoa(api)
    assert is_locked == 0 and unlocked_at
    assert _nk(api)[-1] == ("quan_ly", "mo_khoa", None)
    assert _trang_thai_stb(api) == stb_truoc
    assert api.get_wharton_lock_status()["data"]["is_locked"] is False
    sid = bo.sids[0]                                           # mở khoá: lưu lại được
    assert api.submit_wharton(sid, bo.w1.get(sid, {}), bo.w2.get(sid, {}))["ok"]
    assert api.run_pipeline(seed=3)["ok"]                      # chạy lại: khoá lại
    assert _khoa(api)[0][0] == 1


@pytest.mark.parametrize("go", ["mo", "", "MỞ", "XOA", None])
def test_mo_khoa_sai_chu_thi_khong_doi_gi(khoa_san, go):
    api, _bo = khoa_san
    truoc, nk = _khoa(api), _nk(api)
    kq = api.mo_khoa_wharton(go)
    assert kq["ok"] is False and [e["code"] for e in kq["errors"]] == ["wharton_mo_khoa_sai_xac_nhan"]
    assert _khoa(api) == truoc and _nk(api) == nk


def test_mo_khoa_khi_wharton_tat_bao_chua_bat(api):
    kq = api.mo_khoa_wharton("MO")
    assert [e["code"] for e in kq["errors"]] == ["wharton_chua_bat"]
    assert api.get_wharton_lock_status()["data"]["is_locked"] is False


def test_mo_khoa_khi_dang_mo_thi_khong_ghi_them(da_chay):
    api, _bo = da_chay
    nk0 = _nk(api)
    assert api.mo_khoa_wharton("MO")["ok"]
    assert _nk(api) == nk0 and _khoa(api) == []


# ------------------------------------------------------------------ reset_data

def test_reset_data_mo_khoa_wharton_va_ghi_nhat_ky(khoa_san):
    api, _bo = khoa_san
    assert api.reset_data("hoc_sinh", "XOA")["ok"]
    assert _khoa(api)[0][0] == 0
    nk = _nk(api)
    assert ("xoa_du_lieu", "mo_khoa", None) in nk
    assert ("xoa_du_lieu", "xoa_tat_ca", None) in nk


def test_reset_data_khong_ghi_mo_khoa_khi_chua_khoa(da_chay):
    api, _bo = da_chay
    assert api.reset_data("hoc_sinh", "XOA")["ok"]
    assert ("xoa_du_lieu", "mo_khoa", None) not in _nk(api)


# ------------------------------------------------------------------ khoá không vào dấu vân tay

def test_khoa_khong_lam_doi_dau_van_tay_va_ket_qua(tmp_path):
    bo = sinh_bo(80, n_hs=12, n_clb=4)
    ket = []
    for ten in ("a", "b"):
        api = api_mod.PipelineAPI(str(tmp_path / (ten + ".db")))
        bat_wharton(api)
        _nap_bo_vao_api(api, bo)
        assert api.run_pipeline(seed=3)["ok"]
        if ten == "b":
            assert api.mo_khoa_wharton("MO")["ok"]
            assert api.run_pipeline(seed=3)["ok"]              # chạy lần hai, khoá lại
        with api._ket_noi_doc() as cur:
            ket.append((
                cur.execute("SELECT dau_van_tay FROM dau_van_tay_chay").fetchone()[0],
                [tuple(r) for r in cur.execute(
                    "SELECT student_id, buoi, club_id FROM match_results ORDER BY 1, 2")],
                json.loads(cur.execute(
                    "SELECT luat_xep FROM run_history ORDER BY rowid DESC").fetchone()[0])))
    assert ket[0] == ket[1]


def test_trang_thai_kiosk_co_co_khoa(da_chay):
    api, bo = da_chay
    sid = bo.sids[0]
    assert api.get_student_entry_state(sid)["data"]["wharton"]["khoa"] is False
    assert api.run_pipeline(seed=3)["ok"]
    assert api.get_student_entry_state(sid)["data"]["wharton"]["khoa"] is True
    assert api.mo_khoa_wharton("MO")["ok"]
    assert api.get_student_entry_state(sid)["data"]["wharton"]["khoa"] is False
