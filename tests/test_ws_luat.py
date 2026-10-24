"""Luật xếp của workspace: nhóm xếp cứng (strict), chỉ theo nhóm (tier), điểm theo NGƯỜI.

Điều phải giữ:
  * Luật mặc định (trường học) cho ra KẾT QUẢ Y HỆT trước khi có luật: so với
    tests/du_lieu_ws/ket_qua_truoc_luat.json (chụp từ bản chưa có luật).
  * Mỗi chế độ vẫn cho kết quả ỔN ĐỊNH (không có cặp phá vỡ) trên dữ liệu ngẫu nhiên.
  * `compute_club_priority` không bao giờ nhận thứ hạng nguyện vọng.
"""

import inspect
import json
import os
import random
import sqlite3

import pytest

import rbda_priority_pipeline as rp
import workspace as ws
from api import PipelineAPI
from _ket_qua_bo_test import BO, chay_bo

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANH_CHUP = os.path.join(GOC, "tests", "du_lieu_ws", "ket_qua_truoc_luat.json")

NHAN = {
    "person": {"vi": "Nhân viên", "en": "Employee"},
    "slot": {"vi": "Dự án", "en": "Project"},
    "session": {"vi": "Ca", "en": "Shift"},
    "group": {"vi": "Cấp bậc", "en": "Level"},
    "score": {"vi": "Điểm", "en": "Score"},
}


def _luat(**rest):
    return {"industry": "company", "labels": NHAN, "rules": rest}


@pytest.fixture
def goc(tmp_path):
    g = tmp_path / "goc"
    g.mkdir()
    return str(g)


def _api(goc, tmp_path, cfg, ten="Thử"):
    slug = ws.tao(goc, ten, cfg)
    xuat = tmp_path / "xuat"
    xuat.mkdir(exist_ok=True)
    return PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_xuat=str(xuat), thu_muc_goc_ws=goc)


def _dung(api, clubs, students, prefs, diem_ca_nhan=None, nhom=None):
    """clubs {id: cho}; students [id]; prefs {sid: [club]}."""
    for cid, cho in clubs.items():
        assert api.create_or_update_club(cid, cid.upper(), cho, 0, "")["ok"]
    for sid in students:
        assert api.create_student_if_missing(sid, sid)["ok"]
    for sid, ds in prefs.items():
        assert api.submit_preferences(sid, ds)["ok"]
    with api._ket_noi_ghi() as cur:
        for sid, d in (diem_ca_nhan or {}).items():
            cur.execute("UPDATE students SET diem_ca_nhan = ? WHERE student_id = ?", (d, sid))
        for sid, g in (nhom or {}).items():
            cur.execute("UPDATE students SET reserve_group = ? WHERE student_id = ?", (g, sid))


def _ket_qua(api):
    with api._ket_noi_doc() as cur:
        return dict(cur.execute("SELECT student_id, club_id FROM match_results"))


# ------------------------------------------------------------------ mặc định == trước đây

def test_mac_dinh_truong_hoc_ra_dung_ket_qua_truoc_khi_co_luat(tmp_path):
    truoc = json.load(open(ANH_CHUP, encoding="utf-8"))
    for ten_bo in BO:
        api = PipelineAPI(str(tmp_path / (ten_bo + ".db")))
        assert chay_bo(api, ten_bo) == truoc[ten_bo], ten_bo


def test_mac_dinh_trong_workspace_cung_ra_dung_ket_qua(goc, tmp_path):
    truoc = json.load(open(ANH_CHUP, encoding="utf-8"))
    api = _api(goc, tmp_path, {})
    assert chay_bo(api, "sach") == truoc["sach"]


def test_luat_tham_so_mac_dinh_la_duong_cu():
    assert rp.tham_so_luat(None, {"a": {"reserve_group": "x"}}) == {
        "tier_rank": None, "bo_qua_du_tru": False}
    assert rp.tham_so_luat({}, {}) == rp.tham_so_luat(rp.luat_xep_cua(None), {})
    assert rp.diem_theo_nguoi(None) is False


def test_dau_van_tay_mac_dinh_khong_doi_va_luat_khac_thi_doi(tmp_path):
    db = str(tmp_path / "a.db")
    rp.init_db(db)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    goc = rp.dau_van_tay_du_lieu(cur)
    assert rp.dau_van_tay_du_lieu(cur, None) == goc
    assert rp.dau_van_tay_du_lieu(cur, {"priority": "score", "tier_mode": "reserve",
                                        "score_scope": "per_slot", "tiers": [],
                                        "max_choices": 3}) == goc      # trần nhập không tính
    assert rp.dau_van_tay_du_lieu(cur, {"tier_mode": "strict", "tiers": ["A"]}) != goc
    assert rp.dau_van_tay_du_lieu(cur, {"priority": "tier"}) != goc
    assert rp.dau_van_tay_du_lieu(cur, {"score_scope": "per_person"}) != goc


# ------------------------------------------------------------------ thứ tự ưu tiên

def test_ham_uu_tien_khong_nhan_thu_hang_nguyen_vong():
    # chữ ký KHÔNG đổi: hạng nhóm đi qua hàm bọc `uu_tien_theo_nhom`, không qua hàm này
    assert list(inspect.signature(rp.compute_club_priority).parameters) == [
        "club_id", "applicants_for_club", "tested_scores_for_club", "stb_lottery"]
    ham_boc = set(inspect.signature(rp.uu_tien_theo_nhom).parameters)
    assert ham_boc == {"club_id", "applicants_for_club", "tested_scores_for_club",
                       "stb_lottery", "tier_rank"}
    assert not any("pref" in t for t in ham_boc)


def test_nhom_xep_cung_dung_truoc_diem():
    stb = {"a": 3, "b": 2, "c": 1, "d": 4}
    diem = {"a": 9.0, "b": 5.0}
    # mặc định: hai người đã chấm lên trước, rồi theo STB
    assert rp.compute_club_priority("x", ["a", "b", "c", "d"], diem, stb) == ["a", "b", "c", "d"]
    # d thuộc nhóm 0, c nhóm 1, a nhóm 2: nhóm quyết định trước điểm
    hang = {"d": 0, "c": 1, "a": 2, "b": 2}
    assert rp.uu_tien_theo_nhom("x", ["a", "b", "c", "d"], diem, stb, hang) \
        == ["d", "c", "a", "b"]


def test_trong_cung_nhom_van_diem_roi_stb_roi_ma():
    stb = {"a": 5, "b": 5, "c": 1, "d": 9}
    diem = {"a": 7.0, "d": 8.0}
    hang = {"a": 0, "b": 0, "c": 0, "d": 0}
    # đã chấm trước (d 8 > a 7), rồi chưa chấm theo STB (c 1 < b 5)
    assert rp.uu_tien_theo_nhom("x", list("abcd"), diem, stb, hang) \
        == ["d", "a", "c", "b"]
    # STB trùng nhau thì mã quyết định: kết quả không phụ thuộc thứ tự nhập
    assert rp.uu_tien_theo_nhom("x", list("ba"), {}, {"a": 5, "b": 5}, {}) == ["a", "b"]
    assert rp.uu_tien_theo_nhom("x", list("ab"), {}, {"a": 5, "b": 5}, {}) == ["a", "b"]


def test_xay_tier_rank_khong_phan_biet_hoa_thuong_dau_va_bo_nguoi_la():
    sv = {"1": {"reserve_group": "Khối 12"}, "2": {"reserve_group": "khoi 11"},
          "3": {"reserve_group": "lạ"}, "4": {"reserve_group": None}, "5": {}}
    assert rp.xay_tier_rank(sv, ["khoi 12", "Khối 11"]) == {"1": 0, "2": 1}
    assert rp.xay_tier_rank(sv, []) == {}


def test_tham_so_luat_ma_tran():
    sv = {"1": {"reserve_group": "A"}, "2": {"reserve_group": "B"}}
    # strict, điểm: nhóm cứng, bỏ suất dự trữ, vẫn dùng điểm
    t = rp.tham_so_luat({"tier_mode": "strict", "tiers": ["B", "A"]}, sv)
    assert t == {"tier_rank": {"2": 0, "1": 1}, "bo_qua_du_tru": True}
    # score+tier ở chế độ reserve: giữ suất dự trữ như cũ
    t = rp.tham_so_luat({"priority": "score+tier", "tiers": ["A"]}, sv)
    assert t == {"tier_rank": None, "bo_qua_du_tru": False}
    # chỉ theo nhóm: nhóm cứng + bỏ điểm, kể cả khi tier_mode là reserve
    t = rp.tham_so_luat({"priority": "tier", "tiers": ["A"]}, sv)
    assert t == {"tier_rank": {"1": 0}, "bo_qua_du_tru": True}
    assert rp.diem_theo_nguoi({"score_scope": "per_person"}) is True
    assert rp.diem_theo_nguoi({"score_scope": "per_person", "priority": "tier"}) is False


# ------------------------------------------------------------------ chạy thật

def test_strict_nhom_thang_diem_trong_pipeline(goc, tmp_path):
    """Một suất, hai người: người nhóm cao hơn thắng dù điểm thấp hơn."""
    api = _api(goc, tmp_path, _luat(tier_mode="strict", tiers=["Cấp 1", "Cấp 2"]))
    _dung(api, {"a": 1}, ["N1", "N2"], {"N1": ["a"], "N2": ["a"]},
          nhom={"N1": "Cấp 2", "N2": "Cấp 1"})
    with api._ket_noi_ghi() as cur:
        cur.execute("INSERT INTO club_test_selection VALUES ('N1','a')")
        cur.execute("INSERT INTO club_test_selection VALUES ('N2','a')")
    assert api.submit_club_scores("a", [{"student_id": "N1", "score": 10},
                                        {"student_id": "N2", "score": 1}])["ok"]
    res = api.run_pipeline(seed=1)
    assert res["ok"], res
    kq = _ket_qua(api)
    assert kq["N2"] == "a" and kq["N1"] is None


def test_strict_bo_suat_du_tru(goc, tmp_path):
    """Strict xếp theo thứ tự nhóm, không giữ thêm suất dự trữ cho nhóm nhãn trên CLB."""
    tren = {"tier_mode": "strict", "tiers": ["Cấp 1", "Cấp 2"]}
    api = _api(goc, tmp_path, _luat(**tren))
    assert api.create_or_update_club("a", "A", 2, 1, "Cấp 2")["ok"]     # 1 suất dành cho Cấp 2
    for sid, g in (("N1", "Cấp 1"), ("N2", "Cấp 1"), ("N3", "Cấp 2")):
        assert api.create_student_if_missing(sid, sid)["ok"]
        assert api.submit_preferences(sid, ["a"])["ok"]
        with api._ket_noi_ghi() as cur:
            cur.execute("UPDATE students SET reserve_group=? WHERE student_id=?", (g, sid))
    assert api.run_pipeline(seed=3)["ok"]
    # Hai suất đều về Cấp 1 (đứng trước), dù CLB để dành một suất cho Cấp 2.
    assert {s for s, c in _ket_qua(api).items() if c == "a"} == {"N1", "N2"}


def test_theo_nhom_bo_qua_diem(goc, tmp_path):
    api = _api(goc, tmp_path, _luat(priority="tier", tiers=["Cấp 1", "Cấp 2"]))
    _dung(api, {"a": 1}, ["N1", "N2"], {"N1": ["a"], "N2": ["a"]},
          nhom={"N1": "Cấp 2", "N2": "Cấp 1"})
    with api._ket_noi_ghi() as cur:
        cur.execute("INSERT INTO club_test_selection VALUES ('N1','a')")
        cur.execute("INSERT INTO club_scores VALUES ('N1','a',99)")
    assert api.run_pipeline(seed=1)["ok"]
    assert _ket_qua(api)["N2"] == "a"              # điểm 99 của N1 không được tính
    tested = rp.load_from_sqlite(api.db_path, api._cfg_ws()["rules"])[2]
    assert tested == {"a": {}}


def test_diem_theo_nguoi_mo_rong_ra_moi_nguyen_vong(goc, tmp_path):
    api = _api(goc, tmp_path, _luat(score_scope="per_person"))
    _dung(api, {"a": 1, "b": 1}, ["N1", "N2", "N3"],
          {"N1": ["a", "b"], "N2": ["b"], "N3": ["a"]},
          diem_ca_nhan={"N1": 7.0, "N2": 9.0})
    quy = api._cfg_ws()["rules"]
    _, _, tested, applicants, _, _ = rp.load_from_sqlite(api.db_path, quy)
    assert tested == {"a": {"N1": 7.0}, "b": {"N1": 7.0, "N2": 9.0}}
    # luật mặc định thì bỏ qua cột này: điểm theo CLB (rỗng ở đây)
    assert rp.load_from_sqlite(api.db_path)[2] == {"a": {}, "b": {}}
    assert api.run_pipeline(seed=1)["ok"]
    kq = _ket_qua(api)
    assert kq["N2"] == "b" and kq["N1"] == "a"      # N2 điểm cao nhất ở b; N1 đứng trước N3 ở a


def test_diem_theo_nguoi_nguoi_chua_cham_xuong_sau(goc, tmp_path):
    api = _api(goc, tmp_path, _luat(score_scope="per_person"))
    _dung(api, {"a": 1}, ["N1", "N2"], {"N1": ["a"], "N2": ["a"]}, diem_ca_nhan={"N2": 0.0})
    assert api.run_pipeline(seed=5)["ok"]
    assert _ket_qua(api)["N2"] == "a"               # 0 điểm vẫn là "đã chấm", hơn chưa chấm


# ------------------------------------------------------------------ ổn định trên dữ liệu ngẫu nhiên

def _ngau_nhien(rng, n_nguoi, n_clb):
    nhom = ["A", "B", "C", None]
    students = {f"s{i}": {"stb": 0, "reserve_group": rng.choice(nhom)} for i in range(n_nguoi)}
    stb = rp.generate_stb_lottery(list(students), rng.randint(0, 10**6))
    for sid in students:
        students[sid]["stb"] = stb[sid]
    clubs = {f"c{j}": {"capacity": rng.randint(1, 4), "reserve_capacity": 0,
                       "reserve_group": None, "buoi": rp.BUOI_MAC_DINH} for j in range(n_clb)}
    for c in clubs.values():
        if rng.random() < 0.5:
            c["reserve_capacity"] = rng.randint(0, c["capacity"])
            c["reserve_group"] = rng.choice(["A", "B", "C"])
    prefs = {}
    for sid in students:
        if rng.random() < 0.9:
            prefs[sid] = rng.sample(list(clubs), rng.randint(1, min(4, n_clb)))
    dang_ky = {cid: [] for cid in clubs}
    diem_nguoi = {sid: round(rng.uniform(0, 10), 1) for sid in students if rng.random() < 0.6}
    return students, clubs, prefs, dang_ky, diem_nguoi, stb


@pytest.mark.parametrize("che_do", ["mac_dinh", "strict", "tier", "score+tier_strict", "per_person"])
def test_on_dinh_tren_du_lieu_ngau_nhien(che_do):
    quy = {"mac_dinh": {},
           "strict": {"tier_mode": "strict", "tiers": ["B", "A"]},
           "tier": {"priority": "tier", "tiers": ["C", "A", "B"]},
           "score+tier_strict": {"priority": "score+tier", "tier_mode": "strict",
                                 "tiers": ["A", "B", "C"]},
           "per_person": {"score_scope": "per_person"}}[che_do]
    rng = random.Random(hash(che_do) % 1000 + 7)
    for lan in range(25):
        students, clubs, prefs, dang_ky, diem_nguoi, stb = _ngau_nhien(
            rng, rng.randint(4, 24), rng.randint(2, 6))
        applicants = rp.hop_ung_vien(dang_ky, prefs)
        if che_do == "per_person":
            tested = {cid: {s: diem_nguoi[s] for s in ds if s in diem_nguoi}
                      for cid, ds in applicants.items()}
        elif che_do == "tier":
            tested = {cid: {} for cid in clubs}
        else:
            tested = {cid: {s: diem_nguoi[s] for s in ds[:2] if s in diem_nguoi}
                      for cid, ds in applicants.items()}
        tham = rp.tham_so_luat(quy, students)
        reserve_fn = rp.default_reserve_eligible_fn(students, clubs)
        kq = rp.run_rbda_nhieu_buoi(
            students, clubs, tested, applicants, prefs, stb, is_reserve_eligible_fn=reserve_fn,
            seed=lan, tier_rank=tham["tier_rank"], bo_qua_du_tru=tham["bo_qua_du_tru"])
        van_de = rp.verify_stability_tuan(
            kq, clubs, prefs, reserve_fn, bo_qua_du_tru=tham["bo_qua_du_tru"])
        assert all(not v for v in van_de.values()), (che_do, lan, van_de)
        for buoi, k in kq.per_buoi.items():
            assert rp.sanity_check_result(k, clubs, prefs) == []


def test_kiem_on_dinh_phai_dung_cung_ham_voi_lan_chay():
    """Xếp bỏ suất dự trữ mà kiểm có suất dự trữ thì báo cặp phá vỡ giả: cờ phải đi cùng."""
    students = {"y": {"stb": 1, "reserve_group": "A"}, "w": {"stb": 2, "reserve_group": "A"},
                "z": {"stb": 3, "reserve_group": "B"}}
    clubs = {"c": {"capacity": 2, "reserve_capacity": 1, "reserve_group": "B",
                   "buoi": rp.BUOI_MAC_DINH}}
    prefs = {s: ["c"] for s in students}
    stb = {s: v["stb"] for s, v in students.items()}
    hang = {"y": 0, "w": 1, "z": 2}
    app = rp.hop_ung_vien({"c": []}, prefs)
    fn = rp.default_reserve_eligible_fn(students, clubs)
    kq = rp.run_rbda_nhieu_buoi(students, clubs, {"c": {}}, app, prefs, stb, fn, seed=1,
                                tier_rank=hang, bo_qua_du_tru=True)
    assert not any(rp.verify_stability_tuan(kq, clubs, prefs, fn, bo_qua_du_tru=True).values())
    assert any(rp.verify_stability_tuan(kq, clubs, prefs, fn, bo_qua_du_tru=False).values())


# ------------------------------------------------------------------ API chấm điểm theo người

def test_cham_diem_theo_nguoi_va_chap_mu(goc, tmp_path):
    api = _api(goc, tmp_path, _luat(score_scope="per_person"))
    _dung(api, {"a": 2}, ["N1", "N2"], {"N1": ["a"]})
    ds = api.get_person_scoring_list()
    assert ds["ok"], ds
    dong = ds["data"]["persons"]
    assert [d["student_id"] for d in dong] == ["N1", "N2"]
    assert set(dong[0]) == {"student_id", "name", "score"}         # chấm mù: không STB, không NV
    r = api.submit_person_scores([{"student_id": "N1", "score": "8,5"},
                                  {"student_id": "N2", "score": -1},
                                  {"student_id": "Z", "score": 3},
                                  {"student_id": "N2", "score": "abc"}])
    assert r["ok"] and r["data"]["n_saved"] == 1
    codes = sorted(w["code"] for w in r["data"]["warnings"])
    assert codes == ["score_negative", "score_not_a_number", "student_not_found"]
    assert api.get_person_scoring_list()["data"]["persons"][0]["score"] == 8.5
    assert api.get_person_scoring_list()["data"]["n_scored"] == 1
    # ô trống xoá điểm
    assert api.submit_person_scores([{"student_id": "N1", "score": ""}])["ok"]
    assert api.get_person_scoring_list()["data"]["persons"][0]["score"] is None
    assert api.submit_person_scores([])["ok"] is False


def test_cham_diem_theo_nguoi_bi_tu_choi_khi_workspace_cham_theo_clb(goc, tmp_path):
    api = _api(goc, tmp_path, _luat())
    for res in (api.get_person_scoring_list(), api.submit_person_scores([{"student_id": "a", "score": 1}])):
        assert res["ok"] is False and res["errors"][0]["code"] == "scoring_not_per_person"
    # …và workspace theo người vẫn dùng được màn theo CLB cũ mà không hỏng
    api2 = _api(goc, tmp_path, _luat(score_scope="per_person"), ten="Hai")
    assert api2.get_scoring_overview()["ok"]


def test_dat_lai_nguoi_giu_diem_theo_nguoi(goc, tmp_path):
    # Điểm theo người do giáo viên chấm, không gắn với ô tick: em nhập lại nguyện vọng ở kiosk
    # không được xoá nó (khác điểm từng CLB, đi theo ô tick).
    api = _api(goc, tmp_path, _luat(score_scope="per_person"))
    _dung(api, {"a": 1}, ["N1"], {"N1": ["a"]}, diem_ca_nhan={"N1": 7.0})
    res = api.reset_student_entry("N1")
    assert res["ok"] and res["data"]["n_scores_removed"] == 0
    assert api.get_person_scoring_list()["data"]["persons"][0]["score"] == 7.0


def test_nap_so_diem_theo_nguoi_ghi_o_nguoi_va_nap_lai_xoa_diem(goc, tmp_path):
    import base64
    import io

    import openpyxl
    api = _api(goc, tmp_path, _luat(max_choices=3, score_scope="per_person"))
    api.create_or_update_club("a", "Dự án A", 3, 0, "")
    wb = openpyxl.load_workbook(api.tao_so_nhap_mau()["data"]["path"])
    hs = wb["2. Nhân viên"]
    hs.append(["N1", "Lan", None, 8.5, "Dự án A"])
    hs.append(["N2", "Mai", None, "thi", "Dự án A"])
    b = io.BytesIO()
    wb.save(b)
    assert api.import_so_nhap(base64.b64encode(b.getvalue()).decode())["ok"]
    diem = {p["student_id"]: p["score"] for p in api.get_person_scoring_list()["data"]["persons"]}
    assert diem == {"N1": 8.5, "N2": None}
    # nạp lại với ô điểm trống: xoá điểm cũ (sổ là bản đầy đủ)
    wb2 = openpyxl.load_workbook(api.tao_so_nhap_mau()["data"]["path"])
    wb2["2. Nhân viên"].append(["N1", "Lan", None, None, "Dự án A"])
    b2 = io.BytesIO()
    wb2.save(b2)
    assert api.import_so_nhap(base64.b64encode(b2.getvalue()).decode())["ok"]
    assert api.get_person_scoring_list()["data"]["persons"][0]["score"] is None


def test_xuat_du_lieu_dau_vao_co_diem_theo_nguoi_va_nap_lai_giong_het(goc, tmp_path):
    import base64

    api = _api(goc, tmp_path, _luat(max_choices=3, score_scope="per_person"))
    _dung(api, {"a": 2, "b": 2}, ["N1", "N2"], {"N1": ["a", "b"], "N2": ["b"]},
          diem_ca_nhan={"N1": 6.5})
    tep = api.export_du_lieu_dau_vao()["data"]["path"]
    api2 = _api(goc, tmp_path, _luat(max_choices=3, score_scope="per_person"), ten="Hai")
    assert api2.import_so_nhap(base64.b64encode(open(tep, "rb").read()).decode())["ok"]
    d2 = {p["student_id"]: p["score"] for p in api2.get_person_scoring_list()["data"]["persons"]}
    assert d2 == {"N1": 6.5, "N2": None}


# ------------------------------------------------------------------ dấu vân tay / kết quả cũ

def test_ket_qua_cu_khi_sua_diem_nguoi_hoac_doi_luat(goc, tmp_path):
    api = _api(goc, tmp_path, _luat(score_scope="per_person"))
    _dung(api, {"a": 1}, ["N1", "N2"], {"N1": ["a"], "N2": ["a"]}, diem_ca_nhan={"N1": 5.0})
    assert api.run_pipeline(seed=1)["ok"]
    assert api.get_trang_thai_ket_qua()["data"]["ket_qua_cu"] is False
    assert api.submit_person_scores([{"student_id": "N2", "score": 9}])["ok"]
    assert api.get_trang_thai_ket_qua()["data"]["ket_qua_cu"] is True
    assert api.run_pipeline(seed=1)["ok"]
    assert api.get_trang_thai_ket_qua()["data"]["ket_qua_cu"] is False
    cfg = api.get_workspace_config()["data"]["config"]
    cfg["rules"]["tier_mode"] = "strict"
    cfg["rules"]["tiers"] = ["A"]
    assert api.update_workspace_config(cfg)["ok"]
    assert api.get_trang_thai_ket_qua()["data"]["ket_qua_cu"] is True     # luật đổi => kết quả cũ


# ------------------------------------------------------------------ sức khoẻ dữ liệu

def _ma(api):
    return sorted({w["code"] for w in api.get_data_health_report()["data"]["warnings"]})


def test_suc_khoe_diem_theo_nguoi(goc, tmp_path):
    api = _api(goc, tmp_path, _luat(score_scope="per_person"))
    _dung(api, {"a": 2}, ["N1", "N2"], {"N1": ["a"], "N2": ["a"]})
    assert "health_person_score_none" in _ma(api)
    w = [x for x in api.get_data_health_report()["data"]["warnings"]
         if x["code"] == "health_person_score_none"][0]
    assert w["severity"] == "high"
    api.submit_person_scores([{"student_id": "N1", "score": 5}])
    ma = _ma(api)
    assert "health_person_score_missing" in ma and "health_person_score_none" not in ma
    api.submit_person_scores([{"student_id": "N2", "score": 5}])
    assert not {"health_person_score_missing", "health_person_score_none"} & set(_ma(api))
    # theo CLB: các cảnh báo chấm điểm từng CLB không áp dụng
    with api._ket_noi_ghi() as cur:
        cur.execute("INSERT INTO club_test_selection VALUES ('N1','a')")
    assert not {"health_scoring_none", "health_scoring_partial"} & set(_ma(api))


def test_suc_khoe_theo_clb_van_nhu_cu(goc, tmp_path):
    api = _api(goc, tmp_path, {})
    _dung(api, {"a": 2}, ["N1"], {"N1": ["a"]})
    with api._ket_noi_ghi() as cur:
        cur.execute("INSERT INTO club_test_selection VALUES ('N1','a')")
    ma = _ma(api)
    assert "health_scoring_none" in ma
    assert not {"health_person_score_none", "health_tier_missing", "health_tiers_empty"} & set(ma)


def test_suc_khoe_thieu_nhom_khi_xep_cung(goc, tmp_path):
    api = _api(goc, tmp_path, _luat(tier_mode="strict", tiers=["Cấp 1"]))
    _dung(api, {"a": 2}, ["N1", "N2", "N3"], {"N1": ["a"], "N2": ["a"], "N3": ["a"]},
          nhom={"N1": "cấp 1", "N2": "Cấp 9"})
    kq = [x for x in api.get_data_health_report()["data"]["warnings"]
          if x["code"] == "health_tier_missing"]
    assert len(kq) == 1 and kq[0]["params"]["n"] == 2          # N2 (nhóm lạ) và N3 (trống)
    assert "N2" in kq[0]["params"]["sample"] and "N1" not in kq[0]["params"]["sample"]
    assert "health_tiers_empty" not in _ma(api)


def test_suc_khoe_danh_sach_nhom_trong_va_bo_canh_bao_du_tru(goc, tmp_path):
    api = _api(goc, tmp_path, _luat(priority="tier"))
    _dung(api, {"a": 2}, ["N1"], {"N1": ["a"]}, nhom={"N1": "lạ"})
    ma = _ma(api)
    assert "health_tiers_empty" in ma
    assert "health_orphan_student_group" not in ma          # không còn suất dự trữ để mà đối chiếu
    # chế độ reserve: cảnh báo nhãn lạc vẫn như cũ
    api2 = _api(goc, tmp_path, _luat(), ten="Hai")
    _dung(api2, {"a": 2}, ["N1"], {"N1": ["a"]}, nhom={"N1": "lạ"})
    assert "health_orphan_student_group" in _ma(api2)


def test_thong_bao_moi_co_du_vi_va_en():
    from i18n_errors import MESSAGES, format_message
    for ma in ("health_person_score_none", "health_person_score_missing", "health_tier_missing",
               "health_tiers_empty", "scoring_not_per_person"):
        assert MESSAGES[ma]["vi"] and MESSAGES[ma]["en"], ma
    chu = format_message("health_tier_missing", {"n": 2, "sample": "N2, N3"}, "en", NHAN)
    assert "employee" in chu and "level" in chu and "N2, N3" in chu
    chu = format_message("health_person_score_none", {}, "vi", NHAN)
    assert "nhân viên" in chu and "điểm" in chu


# ------------------------------------------------------------------ di trú

def test_di_tru_them_cot_diem_ca_nhan_vao_csdl_cu(tmp_path):
    db = str(tmp_path / "cu.db")
    conn = sqlite3.connect(db)
    conn.executescript("""
        CREATE TABLE students (student_id TEXT PRIMARY KEY, name TEXT, stb_number INTEGER,
                               reserve_group TEXT);
        INSERT INTO students VALUES ('A', 'An', 1, NULL);
    """)
    conn.commit()
    conn.close()
    lam = rp.di_tru_schema(db)
    assert "students.diem_ca_nhan" in lam
    assert "students.diem_ca_nhan" not in rp.di_tru_schema(db)        # chạy lại không làm gì
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT diem_ca_nhan FROM students").fetchall() == [(None,)]
    conn.close()


def test_ham_boc_nhom_bang_khoa_sap_ba_tang():
    """Hàm bọc cho ra đúng thứ tự của khoá (nhóm, đã-chấm, -điểm, STB, mã) trên dữ liệu ngẫu nhiên."""
    rng = random.Random(11)
    for _ in range(200):
        sids = [f"s{i}" for i in range(rng.randint(1, 12))]
        stb = {s: rng.randint(1, 5) for s in sids}                  # cố ý trùng STB
        diem = {s: float(rng.randint(0, 3)) for s in sids if rng.random() < 0.5}
        hang = {s: rng.randint(0, 2) for s in sids if rng.random() < 0.8}
        cuoi = max(hang.values(), default=-1) + 1
        mong = sorted(sids, key=lambda s: (hang.get(s, cuoi), 0 if s in diem else 1,
                                            -diem.get(s, 0), stb[s], s))
        assert rp.uu_tien_theo_nhom("x", sids, diem, stb, hang) == mong
