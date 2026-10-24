"""Điểm Wharton (A13, vòng 2): nối vào `run_pipeline` (gọi qua `PipelineAPI`).

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.

Điều phải giữ:
  * Wharton TẮT: `match_results`, `dau_van_tay_chay` và `run_history.luat_xep` TRÙNG KHÍT bản chụp
    chạy bằng mã trước vòng 2 (tests/du_lieu_ws/wharton_moc_truoc_vong2.json; 3 bộ × 3 seed);
  * Wharton BẬT, hồ sơ hợp lệ: kết quả bằng đúng `run_rbda_nhieu_buoi` với điểm hiệu lực tính từ
    cùng dữ liệu; ổn định; `run_history.luat_xep` ghi `wharton: true`;
  * hồ sơ sai CHẶN cả lần chạy ở bước Kiểm tra dữ liệu, TRƯỚC khi bốc hay khoá STB: không vẽ số,
    không ghi gì, không thêm dòng run_history;
  * vắng thi chỉ là cảnh báo (nằm trong chi tiết bước validate).
"""

import json
import os
import tempfile

import pytest

import api as api_mod
import rbda_priority_pipeline as rp
from _wharton import bat_wharton, dung_clb, dung_hs
from test_wharton import sinh_bo

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANH_CHUP = os.path.join(GOC, "tests", "du_lieu_ws", "wharton_moc_truoc_vong2.json")


def _dem(api, bang):
    with api._ket_noi_doc() as cur:
        return cur.execute("SELECT COUNT(*) FROM %s" % bang).fetchone()[0]


def _ket_qua(api):
    with api._ket_noi_doc() as cur:
        return {(r[0], r[1]): r[2] for r in cur.execute(
            "SELECT student_id, buoi, club_id FROM match_results")}


def _trang_thai_stb(api):
    with api._ket_noi_doc() as cur:
        khoa = cur.execute("SELECT is_locked, seed FROM stb_lock WHERE id = 1").fetchone()
        so = [tuple(r) for r in cur.execute(
            "SELECT student_id, stb_number FROM students ORDER BY student_id")]
    return tuple(khoa), so


def _nap_bo_vao_api(api, bo):
    """Dựng một bộ `sinh_bo` (mô phỏng) vào CSDL bằng chính các API kiosk."""
    for cid in bo.cids:
        buoi = (bo.buoi or {}).get(cid, "")
        assert api.create_or_update_club(cid, cid, bo.cap[cid], 0, "", buoi)["ok"]
    for sid in bo.sids:
        assert api.create_student_if_missing(sid, sid)["ok"]
        assert api.submit_test_selection(sid, sorted(bo.tick[sid]))["ok"]
        assert api.submit_preferences(sid, bo.prefs[sid])["ok"]
    for cid in bo.cids:
        diem = [{"student_id": s, "score": v} for s, v in bo.diem_thi[cid].items()]
        if diem:
            assert api.submit_club_scores(cid, diem)["ok"]
    for sid in bo.sids:
        kq = api.submit_wharton(sid, bo.w1.get(sid, {}), bo.w2.get(sid, {}))
        assert kq["ok"], (sid, kq["errors"])


# ------------------------------------------------------------------ tắt: trùng khít bản chụp

@pytest.mark.parametrize("khoa", [
    "%s|%d" % (bo, seed) for bo in ("vi_du_huong_dan", "bo_sach", "TEST_0*") for seed in (1, 7, 42)])
def test_tat_wharton_trung_khit_ban_chup_truoc_vong_2(khoa):
    import sys
    sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))
    from do_anh_huong_seed import BO_DU_LIEU, nap_bo

    ten_bo, seed = khoa.split("|")
    files = next(f for ten, f in BO_DU_LIEU if ten.strip().split()[0] == ten_bo)
    with tempfile.TemporaryDirectory() as tmp:
        db = nap_bo(tmp, files)
        api = api_mod.PipelineAPI(db)
        kq = api.run_pipeline(seed=int(seed))
        assert kq["ok"], kq["errors"]
        with api._ket_noi_doc() as cur:
            mr = [list(r) for r in cur.execute(
                "SELECT student_id, buoi, club_id, matched_tier, rank_in_student_pref, round_num "
                "FROM match_results ORDER BY student_id, buoi")]
            dvt = cur.execute("SELECT dau_van_tay FROM dau_van_tay_chay WHERE id = 1").fetchone()[0]
            lx = [r[0] for r in cur.execute("SELECT luat_xep FROM run_history ORDER BY rowid")]
    goc = json.load(open(ANH_CHUP, encoding="utf-8"))[khoa]
    assert mr == goc["match_results"]
    assert dvt == goc["dau_van_tay"]
    assert lx == goc["luat_xep"]


# ------------------------------------------------------------------ bật + hợp lệ

def test_vi_du_diem_wharton_quyet_dinh_truoc_so_boc_tham(api):
    """5 em không thi cùng xin Debate (1 chỗ) rồi Robotics (1 chỗ): kết quả chỉ do điểm Wharton
    quyết định, không phụ thuộc số bốc thăm."""
    bat_wharton(api)
    dung_clb(api, Debate=1, Robotics=1)
    ds = {"P0": (0, 100), "P1": (30, 70), "P2": (50, 50), "P3": (60, 40), "P4": (80, 20)}
    for sid, (d, r) in ds.items():
        dung_hs(api, sid)
        assert api.submit_preferences(sid, ["Debate", "Robotics"])["ok"]
        assert api.submit_wharton(sid, {}, {"Debate": d, "Robotics": r})["ok"]
    for seed in (1, 7, 42):
        kq = api.run_pipeline(seed=seed, force_redraw_stb=True)
        assert kq["ok"], kq["errors"]
        ket = _ket_qua(api)
        assert ket[("P4", rp.BUOI_MAC_DINH)] == "Debate"
        assert ket[("P0", rp.BUOI_MAC_DINH)] == "Robotics"
        assert sorted(s for (s, _b), c in ket.items() if c is None) == ["P1", "P2", "P3"]


@pytest.mark.parametrize("so_buoi,seed", [(1, 3), (1, 42), (2, 7), (3, 11)])
def test_bat_wharton_ket_qua_bang_run_rbda_nhieu_buoi_voi_diem_hieu_luc(tmp_path, so_buoi, seed):
    bo = sinh_bo(500 + seed, n_hs=16, n_clb=6, so_buoi=so_buoi)
    api = api_mod.PipelineAPI(str(tmp_path / "w.db"))
    bat_wharton(api)
    _nap_bo_vao_api(api, bo)
    kq = api.run_pipeline(seed=seed)
    assert kq["ok"], kq["errors"]

    luat = api._luat_nghiem()
    du, _dvt, w = rp.load_from_sqlite_kem_dau_van_tay_wharton(api.db_path, luat)
    students, clubs, scores, app, prefs, stb = du
    hl, tb = rp.diem_wharton_hieu_luc(prefs, w["w1"], w["w2"], scores)
    assert tb == []
    elig = rp.default_reserve_eligible_fn(students, clubs)
    mong_doi = rp.run_rbda_nhieu_buoi(students, clubs, scores, app, prefs, stb, elig,
                                      seed=seed, diem_wharton=hl)
    assert _ket_qua(api) == {(s, b): c for s, theo in mong_doi.assignment.items()
                             for b, c in theo.items()}
    assert all(not v for v in rp.verify_stability_tuan(mong_doi, clubs, prefs, elig).values())
    # nhật ký: dòng chạy mới ghi luật có wharton
    lx = json.loads(api.get_run_history()["data"][0]["luat_xep"])
    assert lx["wharton"] is True


def test_bat_wharton_that_su_doi_ket_qua_so_voi_tat(tmp_path):
    """Đối chứng ngược: nếu `diem_wharton` bị bỏ qua lặng lẽ ở bước 4 thì test này đỏ."""
    khac = 0
    for seed in range(1, 13):
        bo = sinh_bo(900 + seed, n_hs=30, n_clb=5)       # đủ cạnh tranh: đo được 5/12 bộ khác
        ket = {}
        for bat in (True, False):
            db = str(tmp_path / ("%d_%s.db" % (seed, bat)))
            api = api_mod.PipelineAPI(db)
            if bat:
                bat_wharton(api)
            _nap_bo_vao_api_neu_bat(api, bo, bat)
            assert api.run_pipeline(seed=seed)["ok"]
            ket[bat] = _ket_qua(api)
        khac += ket[True] != ket[False]
    assert khac >= 2


def _nap_bo_vao_api_neu_bat(api, bo, bat):
    if bat:
        return _nap_bo_vao_api(api, bo)
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


# ------------------------------------------------------------------ bật + hồ sơ sai: chặn

@pytest.fixture
def w_sai(api):
    """Wharton bật; HS1 hợp lệ, HS2 có tổng 90 (chưa dùng hết)."""
    bat_wharton(api)
    dung_clb(api, A=5, B=5, C=5)
    dung_hs(api, "HS1", "HS2")
    for sid in ("HS1", "HS2"):
        assert api.submit_preferences(sid, ["A", "B", "C"])["ok"]
    assert api.submit_wharton("HS1", {}, {"A": 50, "B": 30, "C": 20})["ok"]
    with api._ket_noi_ghi() as cur:             # ghi thẳng: submit_wharton từ chối hồ sơ sai
        cur.executemany("INSERT INTO wharton_bids VALUES ('HS2', ?, 2, ?)",
                        [("A", 50), ("B", 30), ("C", 10)])
    return api


def test_tong_90_chan_ca_lan_chay_truoc_khi_boc_tham(w_sai):
    api = w_sai
    stb_truoc = _trang_thai_stb(api)
    n_hist, n_kq = _dem(api, "run_history"), _dem(api, "match_results")
    kq = api.run_pipeline(seed=42)
    assert kq["ok"] is False
    ma = [e["code"] for e in kq["errors"]]
    assert ma == ["wharton_ho_so_chua_hop_le", "wharton_chua_dung_het"]
    assert kq["errors"][0]["params"] == {"n": 1}
    assert kq["errors"][1]["params"]["student_id"] == "HS2"
    assert kq["errors"][1]["params"]["thieu"] == 10
    # dừng ở bước validate
    buoc = kq["data"]["steps"]
    assert [b["step"] for b in buoc if b["status"] == "error"] == ["validate"]
    assert not any(b["step"] == "stb_lottery" for b in buoc)
    # chưa vẽ / khoá số bốc thăm, chưa ghi gì
    assert _trang_thai_stb(api) == stb_truoc
    assert _trang_thai_stb(api)[0][0] == 0
    assert all(so is None for _sid, so in _trang_thai_stb(api)[1])
    assert _dem(api, "run_history") == n_hist and _dem(api, "match_results") == n_kq


def test_tra_du_danh_sach_loi_cua_nhieu_em(w_sai):
    api = w_sai
    dung_hs(api, "HS3")
    assert api.submit_preferences("HS3", ["A", "B"])["ok"]        # HS3 không chia điểm gì
    kq = api.run_pipeline(seed=42)
    assert kq["ok"] is False and kq["errors"][0]["params"] == {"n": 2}
    em_loi = {e["params"].get("student_id") for e in kq["errors"][1:]}
    assert em_loi == {"HS2", "HS3"}


def test_sua_xong_thi_chay_duoc(w_sai):
    api = w_sai
    assert api.run_pipeline(seed=42)["ok"] is False
    with api._ket_noi_ghi() as cur:
        cur.execute("UPDATE wharton_bids SET points = 20 WHERE student_id='HS2' AND club_id='C'")
    kq = api.run_pipeline(seed=42)
    assert kq["ok"], kq["errors"]
    assert _trang_thai_stb(api)[0][0] == 1                        # lần này mới khoá STB


def test_o_tick_doi_sau_khi_chia_diem_chan_lan_chay(api):
    bat_wharton(api)
    dung_clb(api, A=5, B=5)
    dung_hs(api, "HS1")
    assert api.submit_preferences("HS1", ["A", "B"])["ok"]
    assert api.submit_wharton("HS1", {}, {"A": 60, "B": 40})["ok"]
    assert api.submit_test_selection("HS1", ["A"])["ok"]          # tick A sau khi chia ở quỹ 2
    kq = api.run_pipeline(seed=1)
    assert kq["ok"] is False
    assert "wharton_ngoai_tap" in [e["code"] for e in kq["errors"]]


def test_loi_tang_lech_cung_chan_nhu_ca_tong_90(api, monkeypatch):
    """`wharton_tang_lech` (CLB có điểm thi mà em chỉ đặt ở quỹ 2) chặn như mọi mã trừ vắng thi.
    Qua dữ liệu thường không tới được (điểm luôn đi cùng ô tick), nên giả lập bước tính điểm."""
    bat_wharton(api)
    dung_clb(api, A=5)
    dung_hs(api, "HS1")
    assert api.submit_preferences("HS1", ["A"])["ok"]
    assert api.submit_wharton("HS1", {}, {})["ok"]
    gia = {"code": "wharton_tang_lech", "params": {"student_id": "HS1", "club_id": "A"}}
    monkeypatch.setattr(api_mod, "diem_wharton_hieu_luc", lambda *a, **k: ({}, [gia]))
    kq = api.run_pipeline(seed=1)
    assert kq["ok"] is False
    assert [e["code"] for e in kq["errors"]] == ["wharton_ho_so_chua_hop_le", "wharton_tang_lech"]
    assert _trang_thai_stb(api)[0][0] == 0 and _dem(api, "match_results") == 0


# ------------------------------------------------------------------ vắng thi: cảnh báo, không chặn

def test_vang_thi_chay_thanh_cong_va_canh_bao_nam_trong_buoc_validate(api):
    bat_wharton(api)
    dung_clb(api, Ly=1, Toan=5)
    dung_hs(api, "An", "Binh", "Quan", tick={"An": ["Ly"], "Binh": ["Ly"], "Quan": ["Ly"]})
    for sid in ("An", "Binh", "Quan"):
        assert api.submit_preferences(sid, ["Ly", "Toan"])["ok"]
    assert api.submit_club_scores("Ly", [{"student_id": "An", "score": 5.0},
                                         {"student_id": "Binh", "score": 4.0}])["ok"]
    for sid in ("An", "Binh", "Quan"):
        assert api.submit_wharton(sid, {"Ly": 100}, {"Toan": 100})["ok"]   # Quân tick Ly, vắng thi
    kq = api.run_pipeline(seed=5)
    assert kq["ok"], kq["errors"]
    validate = [b for b in kq["data"]["steps"] if b["step"] == "validate" and b["status"] == "done"]
    assert len(validate) == 1
    assert validate[0]["detail"] == [{"code": "wharton_vang_thi", "params": {
        "student_id": "Quan", "club_id": "Ly", "diem": 0, "diem_bo": 100}}]
    ket = _ket_qua(api)
    assert ket[("An", rp.BUOI_MAC_DINH)] == "Ly"                 # tầng 1 trước em vắng thi
    assert ket[("Quan", rp.BUOI_MAC_DINH)] == "Toan"


def test_khong_vang_thi_thi_buoc_validate_khong_co_chi_tiet(api):
    dung_clb(api, A=5)
    dung_hs(api, "HS1")
    assert api.submit_preferences("HS1", ["A"])["ok"]
    kq = api.run_pipeline(seed=1)
    assert kq["ok"]
    validate = [b for b in kq["data"]["steps"] if b["step"] == "validate" and b["status"] == "done"]
    assert validate == [{"step": "validate", "status": "done"}]


# ------------------------------------------------------------------ chạy riêng một buổi

def test_chay_rieng_mot_buoi_bang_ket_qua_buoi_do_khi_chay_ca_tuan(tmp_path):
    bo = sinh_bo(777, n_hs=20, n_clb=6, so_buoi=2)
    ds_buoi = sorted(set(bo.buoi.values()))
    ket = {}
    for ten, chi in (("tuan", None), ("rieng", [ds_buoi[1]])):
        api = api_mod.PipelineAPI(str(tmp_path / (ten + ".db")))
        bat_wharton(api)
        _nap_bo_vao_api(api, bo)
        kq = api.run_pipeline(seed=9, chi_buoi=chi)
        assert kq["ok"], kq["errors"]
        ket[ten] = {k: v for k, v in _ket_qua(api).items() if k[1] == ds_buoi[1]}
    assert ket["rieng"] == ket["tuan"] and ket["tuan"]


def test_tat_roi_bat_lai_ket_qua_chi_phu_thuoc_du_lieu_hien_tai(tmp_path):
    """Tắt Wharton thì bảng wharton_bids bị bỏ qua hoàn toàn (kể cả hồ sơ đang sai)."""
    api = api_mod.PipelineAPI(str(tmp_path / "t.db"))
    bat_wharton(api)
    dung_clb(api, A=5, B=5)
    dung_hs(api, "HS1")
    assert api.submit_preferences("HS1", ["A", "B"])["ok"]
    with api._ket_noi_ghi() as cur:
        cur.execute("INSERT INTO wharton_bids VALUES ('HS1', 'A', 2, 7)")     # hồ sơ sai
    assert api.run_pipeline(seed=2)["ok"] is False
    bat_wharton(api, bat=False)
    kq = api.run_pipeline(seed=2)
    assert kq["ok"], kq["errors"]
