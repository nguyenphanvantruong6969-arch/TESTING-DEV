"""Kiểm nhận A13.13, do phiên cha thiết kế; dữ liệu MÔ PHỎNG.

Điểm quyết tâm (Wharton) BẬT mặc định cho workspace trường học. Quyết định đã duyệt: mặc định
bật; tổ hợp luật không cho phép mà không ghi rõ `wharton` thì tự tắt; cấu hình cũ thiếu khoá
⇒ bật; `LUAT_XEP_MAC_DINH["wharton"]` ở tầng thuật toán giữ False.
"""

import base64
import copy
import io
import json
import os
import sqlite3
import sys

import pytest

import cau_hinh_ws as ch
import rbda_priority_pipeline as rp
import workspace as ws
from _wharton import bat_wharton, chen_bids, dong_bids, dung_clb, dung_hs, tat_wharton
from api import PipelineAPI
from i18n_errors import format_message
from rbda_priority_pipeline import init_db

openpyxl = pytest.importorskip("openpyxl")

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))
TAT = {"rules": {"wharton": False}}


def _luat(**rest):
    return ch.chuan_hoa({"rules": dict(rest)})["rules"]


def _ghi_tho(db, cfg):
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE IF NOT EXISTS workspace_settings (key TEXT PRIMARY KEY, value TEXT)")
    conn.execute("INSERT OR REPLACE INTO workspace_settings VALUES (?, ?)",
                 (ch.KHOA_CAU_HINH, json.dumps(cfg)))
    conn.commit()
    conn.close()


@pytest.fixture
def goc(tmp_path):
    g = tmp_path / "goc"
    g.mkdir()
    return str(g)


@pytest.fixture
def api_ws(goc, tmp_path):
    slug = ws.tao(goc, "Trường học", None)
    xuat = tmp_path / "xuat"
    xuat.mkdir()
    return PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_xuat=str(xuat), thu_muc_goc_ws=goc)


# ================================================================== A — mặc định

def test_A1_mac_dinh_la_bat():
    assert ch.MAC_DINH_TRUONG_HOC["rules"]["wharton"] is True
    assert ch.chuan_hoa({})["rules"]["wharton"] is True


def test_A2_csdl_moi_khong_co_hang_cau_hinh(tmp_path):
    db = str(tmp_path / "app.db")
    init_db(db)
    assert ch.doc_cau_hinh(db)["rules"]["wharton"] is True
    assert ch.doc_cau_hinh(db, nghiem=True)["rules"]["wharton"] is True


def test_A3_workspace_tao_mac_dinh_va_tat_ro_rang(tmp_path):
    root = str(tmp_path)
    x = ws.tao(root, "X", None)
    y = ws.tao(root, "Y", TAT)
    assert ch.doc_cau_hinh(ws.duong_dan_db(root, x))["rules"]["wharton"] is True
    assert ch.doc_cau_hinh(ws.duong_dan_db(root, y))["rules"]["wharton"] is False
    # mở lại (đọc lại từ đĩa, qua một PipelineAPI mới) vẫn False
    lai = PipelineAPI(ws.duong_dan_db(root, y), thu_muc_goc_ws=root)
    assert lai.get_workspace_config()["data"]["config"]["rules"]["wharton"] is False
    assert ch.doc_cau_hinh(ws.duong_dan_db(root, y), nghiem=True)["rules"]["wharton"] is False


def test_A4_di_tru_app_db_cu(tmp_path):
    root = str(tmp_path)
    db_cu = os.path.join(root, "app.db")
    api = PipelineAPI(db_cu)
    tat_wharton(api)                       # dựng dữ liệu như bản cũ (chạy được)
    assert api.create_or_update_club("a", "A", 1, 0, "")["ok"]
    assert api.create_or_update_club("b", "B", 5, 0, "")["ok"]
    for sid in ("H1", "H2"):
        assert api.create_student_if_missing(sid, sid)["ok"]
        assert api.submit_preferences(sid, ["a", "b"])["ok"]
    assert api.run_pipeline(seed=1)["ok"]
    conn = sqlite3.connect(db_cu)
    conn.execute("DELETE FROM workspace_settings")        # app.db cũ: chưa có cấu hình workspace
    conn.commit()
    truoc = {b: conn.execute("SELECT COUNT(*) FROM %s" % b).fetchone()[0]
             for b in ("clubs", "students", "run_history")}
    conn.close()
    assert truoc["clubs"] == 2 and truoc["students"] == 2 and truoc["run_history"] == 1
    assert ws.di_chuyen_db_cu(root) is True
    moi = ws.duong_dan_db(root, ws.SLUG_TRUONG_HOC)
    assert ch.doc_cau_hinh(moi)["rules"]["wharton"] is True
    conn = sqlite3.connect(moi)
    sau = {b: conn.execute("SELECT COUNT(*) FROM %s" % b).fetchone()[0] for b in truoc}
    conn.close()
    assert sau == truoc


def test_A5_mau_dung_san(tmp_path):
    mau = ws.danh_sach_mau(str(tmp_path))[0]
    assert mau["builtin"] and mau["config"]["rules"]["wharton"] is True


# ================================================================== B — tổ hợp luật

@pytest.mark.parametrize("rest,mong", [
    ({"priority": "tier"}, False),
    ({"score_scope": "per_person"}, False),
    ({"priority": "score+tier"}, True),
])
def test_B1_khong_ghi_wharton(rest, mong):
    assert _luat(**rest)["wharton"] is mong


@pytest.mark.parametrize("rest", [
    {"wharton": True, "priority": "tier"},
    {"wharton": True, "score_scope": "per_person"},
])
def test_B2_ghi_ro_true_voi_to_hop_sai_la_loi(rest):
    with pytest.raises(ValueError, match="wharton"):
        _luat(**rest)


def test_B3_tron_len():
    mac_dinh = copy.deepcopy(ch.MAC_DINH_TRUONG_HOC)
    assert ch.tron_len(mac_dinh, {"rules": {"priority": "tier"}})["rules"]["wharton"] is False
    tat = ch.chuan_hoa(TAT)
    assert ch.tron_len(tat, {"rules": {"priority": "score+tier"}})["rules"]["wharton"] is False
    assert ch.tron_len(tat, {"rules": {"wharton": True}})["rules"]["wharton"] is True


def test_B3_qua_ghi_cau_hinh_khong_tu_bat_lai(tmp_path):
    db = str(tmp_path / "a.db")
    init_db(db)
    ch.ghi_cau_hinh(db, TAT)
    moi = ch.ghi_cau_hinh(db, ch.tron_len(ch.doc_cau_hinh(db, nghiem=True),
                                          {"rules": {"priority": "score+tier"}}))
    assert moi["rules"]["wharton"] is False
    moi = ch.ghi_cau_hinh(db, ch.tron_len(moi, {"rules": {"wharton": True}}))
    assert moi["rules"]["wharton"] is True


@pytest.mark.parametrize("cfg", [
    {}, {"rules": {"priority": "tier"}}, {"rules": {"score_scope": "per_person"}},
    {"rules": {"priority": "score+tier"}}, TAT,
])
def test_B4_luy_dang(cfg):
    mot = ch.chuan_hoa(cfg)
    assert ch.chuan_hoa(mot) == mot


@pytest.mark.parametrize("rest", [{"priority": "tier"}, {"score_scope": "per_person"}])
def test_B5_update_workspace_config_hop_dong(api_ws, rest):
    kq = api_ws.update_workspace_config({"rules": dict(rest, wharton=True)})
    assert kq["ok"] is False and kq["errors"]
    for e in kq["errors"]:
        assert set(e) >= {"code", "params"} and isinstance(e["params"], dict)
    # không ghi gì: cấu hình vẫn như cũ
    assert api_ws.get_workspace_config()["data"]["config"]["rules"]["wharton"] is True
    # không ghi rõ ⇒ tự tắt, ok
    ok = api_ws.update_workspace_config({"rules": rest})
    assert ok["ok"] and ok["data"]["config"]["rules"]["wharton"] is False


# ================================================================== C — chạy xếp

def _dung_khong_dqt(api):
    dung_clb(api, A=1, B=5, C=5)
    for sid in ("H1", "H2", "H3"):
        dung_hs(api, sid, tick={sid: ["A"]})
        assert api.submit_preferences(sid, ["A", "B", "C"])["ok"]
    assert api.submit_club_scores("A", [{"student_id": "H1", "score": 5},
                                        {"student_id": "H2", "score": 9},
                                        {"student_id": "H3", "score": 7}])["ok"]


def _dem(api, bang):
    with api._ket_noi_doc() as cur:
        return cur.execute("SELECT COUNT(*) FROM %s" % bang).fetchone()[0]


def test_C1_mac_dinh_khong_co_bids_bi_chan_khong_ghi_do(api_ws):
    _dung_khong_dqt(api_ws)
    truoc = _dem(api_ws, "match_results")
    kq = api_ws.run_pipeline(seed=1)
    assert kq["ok"] is False
    assert "wharton_ho_so_chua_hop_le" in [e["code"] for e in kq["errors"]]
    assert _dem(api_ws, "match_results") == truoc
    assert _dem(api_ws, "run_history") == 0


def _mr(api):
    with api._ket_noi_doc() as cur:
        return [list(r) for r in cur.execute(
            "SELECT student_id, buoi, club_id, matched_tier, rank_in_student_pref, round_num "
            "FROM match_results ORDER BY student_id, buoi")]


@pytest.mark.parametrize("tep_bo", ["vi_du_huong_dan", "bo_sach", "TEST_0*"])
@pytest.mark.parametrize("seed", [1, 7, 42])
def test_C2_tat_ro_rang_trung_khit_pipeline_truc_tiep(tmp_path, tep_bo, seed):
    from do_anh_huong_seed import BO_DU_LIEU, nap_bo
    tep = next(f for ten, f in BO_DU_LIEU if ten.strip().split()[0] == tep_bo)
    os.makedirs(str(tmp_path / "a"))
    os.makedirs(str(tmp_path / "b"))
    db_a = nap_bo(str(tmp_path / "a"), tep)
    api = PipelineAPI(db_a)
    tat_wharton(api)
    assert api.run_pipeline(seed=seed)["ok"]
    ket_api = _mr(api)
    with api._ket_noi_doc() as cur:
        lx = [r[0] for r in cur.execute("SELECT luat_xep FROM run_history")]
    assert all(l is None or "wharton" not in l for l in lx)
    # pipeline TRỰC TIẾP, rules=None (CSDL không có cấu hình), cùng dữ liệu cùng seed
    db_b = nap_bo(str(tmp_path / "b"), tep)
    rp.run_full_pipeline(db_b, seed, str(tmp_path / "b.csv"))
    ket_truc_tiep = _mr(PipelineAPI(db_b))
    assert ket_api == ket_truc_tiep


def _dung_co_dqt(api):
    """Ba em, mỗi quỹ 2 CLB, điểm quyết tâm hợp lệ."""
    dung_clb(api, A=1, B=5, C=5, D=5)
    for sid in ("H1", "H2", "H3"):
        dung_hs(api, sid, tick={sid: ["A", "B"]})
        assert api.submit_preferences(sid, ["A", "B", "C", "D"])["ok"]
    assert api.submit_club_scores("A", [{"student_id": "H1", "score": 5},
                                        {"student_id": "H2", "score": 9},
                                        {"student_id": "H3", "score": 7}])["ok"]
    assert api.submit_club_scores("B", [{"student_id": "H1", "score": 5},
                                        {"student_id": "H2", "score": 9},
                                        {"student_id": "H3", "score": 7}])["ok"]
    chen_bids(api, [(s, c, t, p) for s in ("H1", "H2", "H3")
                    for c, t, p in (("A", 1, 60), ("B", 1, 40), ("C", 2, 70), ("D", 2, 30))])


def _tong_hop(api):
    with api._ket_noi_doc() as cur:
        return {"dvt": cur.execute("SELECT dau_van_tay FROM dau_van_tay_chay WHERE id = 1").fetchone()[0],
                "lx": [r[0] for r in cur.execute("SELECT luat_xep FROM run_history ORDER BY run_id")],
                "stb": [tuple(r) for r in cur.execute(
                    "SELECT student_id, stb_number FROM students ORDER BY student_id")]}


def test_C3_C4_C5_bat_roi_tat_cung_csdl(api_ws):
    _dung_co_dqt(api_ws)
    assert api_ws.run_pipeline(seed=3)["ok"]
    bat = _tong_hop(api_ws)
    assert len(bat["lx"]) == 1 and json.loads(bat["lx"][0])["wharton"] is True          # C3
    with api_ws._ket_noi_doc() as cur:
        dong_cu = [tuple(r) for r in cur.execute("SELECT * FROM run_history ORDER BY run_id")]
    # mở khoá điểm Wharton? chạy lại sau khi TẮT: đổi cấu hình, không force_redraw_stb
    tat_wharton(api_ws)
    assert api_ws.run_pipeline(seed=3)["ok"]
    tat = _tong_hop(api_ws)
    assert tat["stb"] == bat["stb"]                                                      # C4
    assert tat["dvt"] != bat["dvt"]                                                      # C3 (vân tay)
    assert len(tat["lx"]) == 2 and (tat["lx"][1] is None or "wharton" not in tat["lx"][1])
    with api_ws._ket_noi_doc() as cur:
        dong_moi = [tuple(r) for r in cur.execute("SELECT * FROM run_history ORDER BY run_id")]
    assert dong_moi[:1] == dong_cu and len(dong_moi) == 2                                # C5


def test_C3b_dau_van_tay_khac_voi_lan_tat_tuong_minh_tren_cung_du_lieu(tmp_path):
    dvt = {}
    for bat in (True, False):
        api = PipelineAPI(str(tmp_path / ("%s.db" % bat)))
        bat_wharton(api, bat=bat)
        _dung_co_dqt(api)
        assert api.run_pipeline(seed=3)["ok"]
        dvt[bat] = _tong_hop(api)["dvt"]
    assert dvt[True] != dvt[False]


def test_C6_luat_xep_cua_none_giu_false():
    assert rp.luat_xep_cua(None)["wharton"] is False
    assert rp.LUAT_XEP_MAC_DINH["wharton"] is False


# ================================================================== D — thông báo lỗi

def test_D1_thong_bao_chi_hai_cach_khac_phuc():
    # Quyết định B3 của Truong (04/11/2026): câu chỉ trỏ tới việc làm được (điền điểm / "Phóng cho đủ 100"), KHÔNG bảo tắt.
    for ngon, can in (("vi", ("điền", "điểm quyết tâm", "phóng cho đủ 100")),
                      ("en", ("fill in", "commitment points", "scale to 100"))):
        chu = format_message("wharton_ho_so_chua_hop_le", {"n": 3, "person_l": "em"}, ngon).lower()
        for tu in can:
            assert tu in chu, (ngon, tu, chu)
        assert "tắt" not in chu and "turn off" not in chu, chu


def test_D2_i18n_loi_js_khop_ban_sinh_lai():
    import tao_i18n_js
    sinh = None
    for ten in ("sinh", "dung_noi_dung", "tao_noi_dung", "build", "render"):
        if hasattr(tao_i18n_js, ten):
            sinh = getattr(tao_i18n_js, ten)
            break
    with open(os.path.join(GOC, "i18n_loi.js"), encoding="utf-8", newline="") as f:
        hien_co = f.read()
    if sinh is None:        # không có hàm công khai: chạy script ra tệp tạm bằng cách sinh lại tại chỗ
        import subprocess
        goc_truoc = hien_co
        subprocess.run([sys.executable, "tao_i18n_js.py"], cwd=GOC, check=True, capture_output=True)
        with open(os.path.join(GOC, "i18n_loi.js"), encoding="utf-8", newline="") as f:
            sau = f.read()
        assert sau == goc_truoc
    else:
        assert sinh() == hien_co


# ================================================================== E — tệp mẫu

TEN_W = "Điểm quyết tâm"


def _sheet_hs(wb):
    return wb[[t for t in wb.sheetnames if t.startswith("2.")][0]]


def test_E1_so_mau_mac_dinh(api_ws, tmp_path):
    kq = api_ws.tao_so_nhap_mau(str(tmp_path / "mau.xlsx"))
    assert kq["ok"], kq["errors"]
    wb = openpyxl.load_workbook(kq["data"]["path"])
    hang2 = [c.value for c in _sheet_hs(wb)[2]]
    assert hang2.count("CLB") > 0 and hang2.count(TEN_W) == hang2.count("CLB")
    chu = "\n".join(str(r[0].value) for r in wb["Hướng dẫn"].iter_rows() if r[0].value).lower()
    assert "mặc định tắt" not in chu and "chỉ dùng khi" not in chu and "wharton" not in chu


def _dien_so_mau(duong, ra, co_dqt):
    wb = openpyxl.load_workbook(duong)
    ten_clb = [t for t in wb.sheetnames if t.startswith("1.")][0]
    sh = wb[ten_clb]
    tieu = [c.value for c in sh[1]]
    cot = {t: i + 1 for i, t in enumerate(tieu) if t}
    for r, (ten, cho) in enumerate((("CLB Cờ vua", 1), ("CLB Bóng đá", 5), ("CLB Vẽ", 5)), start=2):
        sh.cell(row=r, column=cot["Tên CLB"]).value = ten
        sh.cell(row=r, column=cot["Chỉ tiêu"]).value = cho
    hs = _sheet_hs(wb)
    h2 = [c.value for c in hs[2]]
    assert h2[:1]
    hang = 3
    # quỹ 1: CLB thi (Cờ vua); quỹ 2: hai CLB còn lại
    for i in range(5):
        hs.cell(row=hang + i, column=1).value = "HS%d" % (i + 1)
        hs.cell(row=hang + i, column=2).value = "Em %d" % (i + 1)
        cot_clb = [j + 1 for j, v in enumerate(h2) if v == "CLB"]
        cot_thi = [j + 1 for j, v in enumerate(h2) if v == "Điểm thi"]
        cot_w = [j + 1 for j, v in enumerate(h2) if v == TEN_W]
        for k, (clb, diem, w) in enumerate((("CLB Cờ vua", 6 + i, 100), ("CLB Bóng đá", None, 60),
                                            ("CLB Vẽ", None, 40))):
            hs.cell(row=hang + i, column=cot_clb[k]).value = clb
            if diem is not None:
                hs.cell(row=hang + i, column=cot_thi[k]).value = diem
            if co_dqt:
                hs.cell(row=hang + i, column=cot_w[k]).value = w
    wb.save(ra)
    return ra


def _b64(p):
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode()


def test_E2_vong_dau_cuoi_co_diem_quyet_tam(api_ws, tmp_path):
    mau = api_ws.tao_so_nhap_mau(str(tmp_path / "mau.xlsx"))["data"]["path"]
    so = _dien_so_mau(mau, str(tmp_path / "so.xlsx"), co_dqt=True)
    kq = api_ws.import_so_nhap(_b64(so))
    assert kq["ok"], kq["errors"]
    assert len(dong_bids(api_ws)) > 0
    run = api_ws.run_pipeline(seed=1)
    assert run["ok"], run["errors"]
    with api_ws._ket_noi_doc() as cur:
        co = {r[0] for r in cur.execute("SELECT student_id FROM match_results")}
    assert co == {"HS%d" % i for i in range(1, 6)}


def test_E3_bo_trong_diem_quyet_tam_phai_bao_loi_kem_cach_khac_phuc(api_ws, tmp_path):
    mau = api_ws.tao_so_nhap_mau(str(tmp_path / "mau.xlsx"))["data"]["path"]
    so = _dien_so_mau(mau, str(tmp_path / "so.xlsx"), co_dqt=False)
    kq = api_ws.import_so_nhap(_b64(so))
    assert kq["ok"], kq["errors"]
    run = api_ws.run_pipeline(seed=1)
    assert run["ok"] is False                       # không được thành công mà không báo gì
    loi = next(e for e in run["errors"] if e["code"] == "wharton_ho_so_chua_hop_le")
    chu = format_message(loi["code"], loi["params"], "vi").lower()
    assert "điền" in chu and "phóng cho đủ 100" in chu and "tắt" not in chu   # B3 (Truong, 04/11/2026)


@pytest.mark.parametrize("seed", [1, 7, 42])
@pytest.mark.parametrize("bo", ["vi_du_day_du", "vi_du_ca_tuan"])
def test_E4_so_vi_du_tat_ro_rang_trung_khit_bo_ba_csv(api_factory, bo, seed):
    mau = os.path.join(GOC, "mau_csv")
    api_csv, api_so = api_factory(), api_factory()
    tat_wharton(api_csv)
    tat_wharton(api_so)
    for ten in ("01_danh_sach_CLB.csv", "02_chon_CLB_muon_thi.csv", "03_xep_hang_nguyen_vong.csv"):
        with io.open(os.path.join(mau, bo, ten), encoding="utf-8-sig") as f:
            assert api_csv.import_csv_auto(f.read())["ok"]
    assert api_so.import_so_nhap(_b64(os.path.join(mau, bo, "SO_NHAP_CLB_vi_du.xlsx")))["ok"]
    assert api_csv.run_pipeline(seed=seed)["ok"] and api_so.run_pipeline(seed=seed)["ok"]
    assert _mr(api_so) and _mr(api_so) == _mr(api_csv)


def test_E4b_so_mau_trong_nap_duoc_khi_tat(api_factory):
    api = api_factory()
    tat_wharton(api)
    kq = api.import_so_nhap(_b64(os.path.join(GOC, "mau_csv", "SO_NHAP_CLB.xlsx")))
    assert kq["ok"] or [e["code"] for e in kq["errors"]] == ["so_nhap_khong_co_clb"]


# ================================================================== F — script đo

# Script KHÔNG đặt wharton False trực tiếp, kèm lý do.
NGOAI_LE_F1 = {
    "stress/s8_bao_mat.py": "tạo workspace bằng ws.tao(..., {'rules': {'wharton': False}}) trong chuỗi mẫu",
    "bo_thu_workspace/tao_bo_workspace.py": "đặt wharton False trong CAU_HINH rồi ws.tao",
    "stress/_chung.py": "tao_api ghi cấu hình (tắt khi không DQT, bật khi dqt)",
    "tao_db_demo.py": "mặc định BẬT (demo có điểm quyết tâm); chỉ cờ --tat-wharton mới ghi wharton False",
}


def test_F1_script_do_tat_wharton_ro_rang():
    thieu = []
    for goc, _, tep in os.walk(os.path.join(GOC, "du_lieu_test")):
        for t in tep:
            if not t.endswith(".py"):
                continue
            duong = os.path.join(goc, t)
            rel = os.path.relpath(duong, os.path.join(GOC, "du_lieu_test")).replace(os.sep, "/")
            with io.open(duong, encoding="utf-8") as f:
                ma = f.read()
            if "PipelineAPI(" not in ma or rel in NGOAI_LE_F1:
                continue
            if '"wharton": False' not in ma and "'wharton': False" not in ma:
                thieu.append(rel)
    assert thieu == [], thieu
    for rel in NGOAI_LE_F1:                        # ngoại lệ cũng phải thật sự có tắt tường minh
        with io.open(os.path.join(GOC, "du_lieu_test", rel), encoding="utf-8") as f:
            ma = f.read()
        assert '"wharton": False' in ma or "'wharton': False" in ma, rel
