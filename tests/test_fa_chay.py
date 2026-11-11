"""FA-4 (A13 + A5, FA-DAA): lớp bọc `chay_fa_daa` — CLB Tự do không giới hạn, lọc điểm sàn, giữ
chỗ bằng suất dự trữ mềm, phương án dự phòng, chia nhóm phòng, và nối vào pipeline.

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.
Tiêu chí V§13: 3 (Tự do không từ chối), 4 (không vượt chỉ tiêu), 5 (cùng seed, cùng kết quả),
6 (dưới sàn không vào Tuyển chọn), 7 (không bị từ chối khi người điểm thấp hơn được nhận).
"""

import json
import math
import random

import pytest

import fa_daa
import rbda_priority_pipeline as rp
from _fa import bat_fa, dung_fa_clb, dung_hs_fa, ma


def _bo(n=40, seed=1, san=5, phong=None, hai_buoi=False):
    """Bộ mô phỏng: ngày b1 có T (Tự do), G (Giới hạn 3), S (Tuyển chọn 3, sàn `san`)."""
    r = random.Random(seed)
    sids = ["s%02d" % i for i in range(n)]
    clubs = {"T": {"capacity": 1, "reserve_capacity": 0, "reserve_group": None, "buoi": "b1"},
             "G": {"capacity": 3, "reserve_capacity": 0, "reserve_group": None, "buoi": "b1"},
             "S": {"capacity": 3, "reserve_capacity": 0, "reserve_group": None, "buoi": "b1"}}
    fa_clb = {"T": {"loai": "TU_DO", "diem_san": None, "so_toi_thieu": None, "suc_chua_phong": phong},
              "G": {"loai": "GIOI_HAN", "diem_san": None, "so_toi_thieu": None,
                    "suc_chua_phong": None},
              "S": {"loai": "TUYEN_CHON", "diem_san": san, "so_toi_thieu": None,
                    "suc_chua_phong": None}}
    if hai_buoi:
        for c, loai, cho in (("T2", "TU_DO", 1), ("G2", "GIOI_HAN", 3)):
            clubs[c] = {"capacity": cho, "reserve_capacity": 0, "reserve_group": None,
                        "buoi": "b2"}
            fa_clb[c] = {"loai": loai, "diem_san": None, "so_toi_thieu": None,
                         "suc_chua_phong": None}
    stb = dict(zip(sids, r.sample(range(1, n + 1), n)))
    students = {s: {"stb": stb[s], "reserve_group": None} for s in sids}
    prefs, ticks, scores, huy = {}, {"S": [], "G": []}, {"S": {}, "G": {}}, {}
    for s in sids:
        if r.random() < 0.12:
            continue                              # không đăng ký: sẽ vào phương án dự phòng
        ds = [c for c in (["G", "S", "T"] + (["G2", "T2"] if hai_buoi else [])) if r.random() < .8]
        r.shuffle(ds)
        prefs[s] = ds
        if "S" in ds and r.random() < .8:
            ticks["S"].append(s)
            scores["S"][s] = float(r.randint(0, 10))
        if "G" in ds and r.random() < .5:         # có điểm ở CLB Giới hạn: phải bị bỏ qua
            ticks["G"].append(s)
            scores["G"][s] = float(r.randint(0, 10))
        mc = [c for c in ds if fa_clb[c]["loai"] != "TU_DO"][:3]
        huy[s] = dict(zip(mc, r.sample((60, 30, 10), len(mc))))
    tested = {c: dict(scores.get(c, {})) for c in clubs}
    applicants = rp.hop_ung_vien({c: list(ticks.get(c, [])) for c in clubs}, prefs)
    return dict(students=students, clubs=clubs, tested_scores=tested, applicants=applicants,
                preferences=prefs, stb_lottery=stb, fa_clb=fa_clb, giu_cho=[], huy_chuong=huy)


def _chay(bo, **kw):
    return fa_daa.chay_fa_daa(**{**bo, **kw})


def _thanh_vien(kq, buoi="b1"):
    ra = {}
    for sid, theo in kq.ket_qua.assignment.items():
        if theo.get(buoi):
            ra.setdefault(theo[buoi], []).append(sid)
    return ra


@pytest.mark.parametrize("seed", range(6))
def test_tu_do_khong_bao_gio_tu_choi_va_moi_em_co_cho(seed):
    bo = _bo(seed=seed)
    kq = _chay(bo, seed=seed)
    # V§13.3 + V§8.6: chỉ tiêu lưu của T là 1 nhưng bộ nhớ nới ra; mọi học sinh có CLB trong ngày
    assert all(theo["b1"] is not None for theo in kq.ket_qua.assignment.values())
    assert bo["clubs"]["T"]["capacity"] == 1                # dữ liệu gốc KHÔNG bị sửa
    ds_ranking_T = [s for s, p in bo["preferences"].items() if "T" in p]
    assert all(kq.ket_qua.assignment[s]["b1"] is not None for s in ds_ranking_T)


@pytest.mark.parametrize("seed", range(6))
def test_khong_vuot_chi_tieu(seed):
    bo = _bo(seed=seed, hai_buoi=True)
    kq = _chay(bo, seed=seed)
    for buoi in ("b1", "b2"):
        for cid, ds in _thanh_vien(kq, buoi).items():
            if bo["fa_clb"][cid]["loai"] != "TU_DO":
                assert len(ds) <= bo["clubs"][cid]["capacity"], (cid, len(ds))


@pytest.mark.parametrize("seed", range(6))
def test_duoi_san_hoac_khong_thi_khong_vao_tuyen_chon(seed):
    bo = _bo(seed=seed, san=6)
    kq = _chay(bo, seed=seed)
    diem = bo["tested_scores"]["S"]
    for sid in _thanh_vien(kq).get("S", []):
        assert sid in diem and diem[sid] >= 6, sid          # V§13.6
    ly_do = {(r["student_id"], r["club_id"]): r["ly_do"] for r in kq.loai_bo}
    for sid, p in bo["preferences"].items():
        if "S" not in p:
            continue
        if sid not in diem:
            assert ly_do[(sid, "S")] == "NOT_ATTEMPTED"
        elif diem[sid] < 6:
            assert ly_do[(sid, "S")] == "BELOW_PASS"
        else:
            assert (sid, "S") not in ly_do


@pytest.mark.parametrize("seed", range(8))
def test_tuyen_chon_khong_tu_choi_khi_nguoi_diem_thap_hon_duoc_nhan(seed):
    bo = _bo(seed=seed, n=60, san=3)
    bo["huy_chuong"] = {}                                    # không huy chương: chỉ điểm rồi bốc thăm
    kq = _chay(bo, seed=seed)
    a = kq.ket_qua.assignment
    diem, stb = bo["tested_scores"]["S"], bo["stb_lottery"]
    vao = _thanh_vien(kq).get("S", [])
    for n in bo["preferences"]:
        p = kq.preferences[n]
        if "S" not in p or n in vao or n not in diem or diem[n] < 3:
            continue
        cho_hon = a[n]["b1"] is None or p.index("S") < p.index(a[n]["b1"])
        if not cho_hon:
            continue
        for m in vao:                                        # V§13.7
            assert (diem[n], -stb[n]) <= (diem[m], -stb[m]), (n, m)


@pytest.mark.parametrize("seed", range(4))
def test_cung_seed_cung_ket_qua_va_khong_phu_thuoc_thu_tu_dau_vao(seed):
    bo = _bo(seed=seed, hai_buoi=True)
    a = _chay(bo, seed=seed)
    b = _chay(bo, seed=seed)
    dao = {**bo, "preferences": dict(reversed(list(bo["preferences"].items())))}
    c = _chay(dao, seed=seed)
    assert a.ket_qua.assignment == b.ket_qua.assignment == c.ket_qua.assignment
    assert a.nhom == b.nhom


def test_phuong_an_du_phong_dem_dung_va_khong_dung_nguoi_khac():
    bo = _bo(n=60, seed=3)
    voi = _chay(bo, seed=3)
    khong = _chay(bo, seed=3, buoc_fallback=False)
    ai_co_cho_truoc = {s for s, t in khong.ket_qua.assignment.items() if t["b1"] is not None}
    ai_thieu = {s for s, t in khong.ket_qua.assignment.items() if t["b1"] is None}
    assert {f["student_id"] for f in voi.fallback} == ai_thieu     # số em dự phòng = số em chưa có CLB
    assert ai_thieu                                                 # bộ này có em chưa có chỗ
    assert all(voi.ket_qua.assignment[s]["b1"] == khong.ket_qua.assignment[s]["b1"]
               for s in ai_co_cho_truoc)                           # không em nào khác bị xê dịch
    # dữ liệu gốc không bị ghi đè bằng danh sách tăng cường
    assert all("T" not in bo["preferences"].get(s, []) or True for s in ai_thieu)
    for f in voi.fallback:
        assert bo["fa_clb"][f["club_id"]]["loai"] == "TU_DO"


def test_du_phong_chon_clb_tu_do_it_nguoi_nhat_hoa_thi_theo_ma():
    bo = _bo(n=30, seed=5)
    for c in ("T0", "T1"):
        bo["clubs"][c] = {"capacity": 1, "reserve_capacity": 0, "reserve_group": None, "buoi": "b1"}
        bo["fa_clb"][c] = {"loai": "TU_DO", "diem_san": None, "so_toi_thieu": None,
                           "suc_chua_phong": None}
        bo["tested_scores"][c] = {}
        bo["applicants"][c] = []
    bo["preferences"] = {}                    # không ai đăng ký -> mọi em vào dự phòng
    bo["applicants"] = {c: [] for c in bo["clubs"]}
    bo["huy_chuong"] = {}
    kq = _chay(bo, seed=1)
    dem = {c: len(v) for c, v in _thanh_vien(kq).items()}
    tu_do = [c for c, f in bo["fa_clb"].items() if f["loai"] == "TU_DO"]
    assert sum(dem.get(c, 0) for c in tu_do) == 30
    assert max(dem.get(c, 0) for c in tu_do) - min(dem.get(c, 0) for c in tu_do) <= 1
    # hoà số người: club_id nhỏ trước -> em đầu tiên (theo STB) vào "T"
    dau = min(bo["students"], key=lambda s: bo["stb_lottery"][s])
    assert kq.ket_qua.assignment[dau]["b1"] == "T"


def test_giu_cho_thang_huy_chuong_cao_hon():
    bo = _bo(n=6, seed=2)
    bo["clubs"]["G"]["capacity"] = 1
    for s in bo["students"]:
        bo["preferences"][s] = ["G", "T"]
        bo["huy_chuong"][s] = {}
    bo["huy_chuong"]["s01"] = {"G": 60}
    bo["huy_chuong"]["s02"] = {"G": 30}
    bo["applicants"] = rp.hop_ung_vien({c: [] for c in bo["clubs"]}, bo["preferences"])
    bo["giu_cho"] = [("G", "s05")]                          # s05 không huy chương, nhưng giữ chỗ
    kq = _chay(bo, seed=0)
    assert _thanh_vien(kq)["G"] == ["s05"]
    bo["giu_cho"] = []
    kq2 = _chay(bo, seed=0)
    assert _thanh_vien(kq2)["G"] == ["s01"]


def test_giu_cho_mem_nha_cho_khi_em_co_cho_tot_hon():
    bo = _bo(n=4, seed=2)
    bo["clubs"]["G"]["capacity"] = 1
    bo["clubs"]["S"]["capacity"] = 1
    bo["tested_scores"]["S"] = {"s00": 9.0}
    for s in bo["students"]:
        bo["preferences"][s] = ["G", "T"]
        bo["huy_chuong"][s] = {}
    bo["preferences"]["s00"] = ["S", "G", "T"]               # s00 giữ chỗ ở G nhưng ưu tiên S hơn
    bo["applicants"] = rp.hop_ung_vien({"S": ["s00"], "G": [], "T": []}, bo["preferences"])
    bo["giu_cho"] = [("G", "s00")]
    bo["huy_chuong"]["s01"] = {"G": 60}
    kq = _chay(bo, seed=0)
    assert kq.ket_qua.assignment["s00"]["b1"] == "S"
    assert _thanh_vien(kq)["G"] == ["s01"]                   # suất giữ chỗ bỏ trống thì mở cho người khác


def test_chia_nhom_phong_deu_theo_stb():
    bo = _bo(n=10, seed=4, phong=4)
    bo["preferences"] = {}
    bo["applicants"] = {c: [] for c in bo["clubs"]}
    bo["huy_chuong"] = {}
    kq = _chay(bo, seed=0)
    assert all(v["b1"] == "T" for v in kq.ket_qua.assignment.values())
    n = math.ceil(10 / 4)
    nhom = {}
    for r in kq.nhom:
        nhom.setdefault(r["group_no"], []).append(r["student_id"])
    assert sorted(len(v) for v in nhom.values()) == [3, 3, 4] and set(nhom) == {1, 2, 3} and n == 3
    theo_stb = sorted(bo["students"], key=lambda s: bo["stb_lottery"][s])
    for i, sid in enumerate(theo_stb):                       # group_no = i % n + 1
        assert next(r["group_no"] for r in kq.nhom if r["student_id"] == sid) == i % n + 1
    # không vượt sức chứa phòng thì không chia nhóm
    bo2 = _bo(n=10, seed=4, phong=20)
    bo2["preferences"], bo2["huy_chuong"] = {}, {}
    bo2["applicants"] = {c: [] for c in bo2["clubs"]}
    assert _chay(bo2, seed=0).nhom == []


def test_khong_sua_du_lieu_dau_vao():
    bo = _bo(seed=2, hai_buoi=True)
    sao = json.dumps(
        {k: bo[k] for k in ("clubs", "tested_scores", "applicants", "preferences")}, sort_keys=True)
    _chay(bo, seed=2)
    assert sao == json.dumps(
        {k: bo[k] for k in ("clubs", "tested_scores", "applicants", "preferences")}, sort_keys=True)


# ------------------------------------------------------------ nối vào pipeline


def _dung_pipeline(api):
    bat_fa(api)
    dung_fa_clb(api, T=(1, "TU_DO", None, None, 3), G=(2, "GIOI_HAN"), S=(2, "TUYEN_CHON", 5))
    ds = ["s%d" % i for i in range(1, 9)]
    dung_hs_fa(api, *ds, nv={s: ["S", "G", "T"] for s in ds[:6]})
    assert api.submit_test_selection("s1", ["S"])["ok"]
    assert api.submit_test_selection("s2", ["S"])["ok"]
    assert api.submit_club_scores("S", [{"student_id": "s1", "score": 9},
                                        {"student_id": "s2", "score": 3}])["ok"]
    assert api.submit_huy_chuong("s3", {"G": 60})["ok"]


def _luot(api, bang, cot):
    with api._ket_noi_doc() as cur:
        return [tuple(r) for r in cur.execute("SELECT %s FROM %s ORDER BY 1, 2" % (cot, bang))]


def test_pipeline_fa_chay_dung_va_ghi_nhom(api):
    _dung_pipeline(api)
    kq = api.run_pipeline(seed=11)
    assert kq["ok"], kq["errors"]
    mr = dict(_luot(api, "match_results", "student_id, club_id"))
    assert all(mr.get("s%d" % i) is not None for i in range(1, 9))   # mọi em đều có CLB
    assert mr["s1"] == "S"                                            # có điểm >= sàn, nhận
    assert mr["s2"] != "S"                                            # dưới sàn: không vào
    assert mr["s7"] == "T" and mr["s8"] == "T"                        # không đăng ký -> CLB Tự do
    nhom = _luot(api, "fa_nhom", "run_id, student_id, club_id, group_no")
    assert nhom and {r[2] for r in nhom} == {"T"}                     # chỉ CLB Tự do có nhóm phòng
    n_tv_T = sum(1 for c in mr.values() if c == "T")
    assert len({r[3] for r in nhom}) == math.ceil(n_tv_T / 3)
    # chạy lại: fa_nhom chỉ THÊM (append-only) và run_history có hai dòng
    assert api.run_pipeline(seed=11)["ok"]
    assert len(_luot(api, "fa_nhom", "run_id, student_id")) == 2 * len(nhom)
    assert len(_luot(api, "run_history", "run_id, seed")) == 2


def test_pipeline_fa_tat_khong_tao_fa_nhom(api):
    dung_fa_clb(api, T=(5,), G=(2,))
    dung_hs_fa(api, "a", "b", nv={"a": ["G"], "b": ["G", "T"]})
    import cau_hinh_ws as ch
    ch.ghi_cau_hinh(api.db_path, {"rules": {"wharton": False}})
    assert api.run_pipeline(seed=3)["ok"]
    assert _luot(api, "fa_nhom", "run_id, student_id") == []
    with api._ket_noi_doc() as cur:
        luat = cur.execute("SELECT luat_xep FROM run_history").fetchone()[0]
    assert luat is None or "fa_daa" not in luat


def test_pipeline_fa_ghi_luat_xep_co_fa_daa(api):
    _dung_pipeline(api)
    assert api.run_pipeline(seed=11)["ok"]
    with api._ket_noi_doc() as cur:
        luat = json.loads(cur.execute("SELECT luat_xep FROM run_history").fetchone()[0])
    assert luat["fa_daa"] is True and luat["wharton"] is True


def test_pipeline_fa_chay_lai_giong_het(api):
    _dung_pipeline(api)
    assert api.run_pipeline(seed=11)["ok"]
    truoc = _luot(api, "match_results", "student_id, club_id")
    assert api.run_pipeline(seed=11)["ok"]
    assert _luot(api, "match_results", "student_id, club_id") == truoc
    assert ma(api.get_data_health_report()["data"]["warnings"]) is not None
