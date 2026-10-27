"""A13.6 — Bộ dữ liệu mẫu có Điểm quyết tâm (trong mã: wharton, cột CSV `wp_k`).

Dữ liệu là dữ liệu MÔ PHỎNG (tên bịa, seed cố định); không phải khảo sát thật.

Sáu tệp trong `du_lieu_test/`: hai cỡ (120 em × 3 buổi; ~800 em × 20 CLB) × ba biến thể
(HOP_LE, CO_LOI, TRONG), kèm `DQT_BANG_LOI.json` và `DQT_KIEU_CHIA.json`. Test canh:

  * mỗi tệp nạp được qua `import_so_nhap`;
  * HOP_LE chạy xếp ra kết quả, có điểm chuẩn; mọi quỹ đúng 100; đủ bốn kiểu chia điểm;
  * CO_LOI bị chặn đúng những em, đúng loại lỗi như bảng ghi lỗi;
  * TRONG nạp được, không có dòng `wharton_bids`, hành vi tự điền giữ như cũ;
  * tắt tính năng thì `match_results` trùng khít với cùng sổ bỏ cột điểm (seed 1, 7, 42);
  * bản NHỎ giữ nguyên nguyện vọng và điểm thi của SO_NHAP_MAU_120HS_3BUOI.xlsx;
  * sinh lại bằng script ra đúng nội dung ô cũ.
"""

import base64
import io
import json
import os
import subprocess
import sys

import pytest

openpyxl = pytest.importorskip("openpyxl")

import rbda_priority_pipeline as rp  # noqa: E402
import so_nhap  # noqa: E402
import workspace as ws  # noqa: E402
from _so_nhap_dump import chup  # noqa: E402
from api import PipelineAPI  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DLT = os.path.join(GOC, "du_lieu_test")
CAC_CO = ("120HS", "800HS")
CAC_BIEN_THE = ("HOP_LE", "CO_LOI", "TRONG")
KIEU = {"don_dau", "deu", "all_in", "ngau_nhien"}


def ten_tep(co, bt):
    return "SO_NHAP_DQT_%s_%s.xlsx" % (co, bt)


def duong(co, bt):
    return os.path.join(DLT, ten_tep(co, bt))


def _json(ten):
    with open(os.path.join(DLT, ten), encoding="utf-8") as f:
        return json.load(f)


def _doc(duong_tep):
    wb = openpyxl.load_workbook(duong_tep, read_only=True, data_only=True)
    try:
        return so_nhap.doc_so_nhap(wb)
    finally:
        wb.close()


def _b64(duong_tep):
    with open(duong_tep, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _api(tmp_path, ten, bat=True):
    goc = tmp_path / ("goc_" + ten)
    goc.mkdir()
    slug = ws.tao(str(goc), "Đợt " + ten, {"rules": {"wharton": bat}})
    (tmp_path / ("xuat_" + ten)).mkdir()
    return PipelineAPI(ws.duong_dan_db(str(goc), slug),
                       thu_muc_xuat=str(tmp_path / ("xuat_" + ten)),
                       thu_muc_goc_ws=str(goc))


def _nap(tmp_path, co, bt, bat=True, ten=None):
    api = _api(tmp_path, ten or "%s_%s_%s" % (co, bt, bat), bat)
    kq = api.import_so_nhap(_b64(duong(co, bt)))
    assert kq["ok"], kq["errors"]
    return api, kq


def _ket_qua(api):
    with api._ket_noi_doc() as cur:
        return {(r[0], r[1]): r[2] for r in cur.execute(
            "SELECT student_id, buoi, club_id FROM match_results")}


def _bids(api):
    with api._ket_noi_doc() as cur:
        return [tuple(r) for r in cur.execute(
            "SELECT student_id, club_id, tier, points FROM wharton_bids "
            "ORDER BY student_id, club_id")]


def _tap_theo_buoi(du):
    """{sid: {(buoi, quy): [club_id]}} từ dữ liệu đọc ra: quỹ 1 = CLB có tick thi."""
    buoi_cua = {c["club_id"]: c["buoi"] for c in du["clubs"]}
    ra = {}
    for s in du["students"]:
        d = ra.setdefault(s["student_id"], {})
        for x in s["nv"]:
            d.setdefault((buoi_cua[x["club_id"]], 1 if x["thi"] else 2), []).append(x["club_id"])
    return ra


# ------------------------------------------------------------------ 1. có đủ sáu tệp, nạp được

@pytest.mark.parametrize("co", CAC_CO)
@pytest.mark.parametrize("bt", CAC_BIEN_THE)
def test_tep_ton_tai_va_nap_duoc(tmp_path, co, bt):
    assert os.path.exists(duong(co, bt)), ten_tep(co, bt)
    du = _doc(duong(co, bt))
    assert du["loi"] == []
    api, kq = _nap(tmp_path, co, bt)
    assert kq["data"]["n_students_created"] == len(du["students"])


def test_co_nho_co_120_em_va_3_buoi_co_lon_khoang_800_em_20_clb():
    nho, lon = _doc(duong("120HS", "HOP_LE")), _doc(duong("800HS", "HOP_LE"))
    assert len(nho["students"]) == 120 and len({c["buoi"] for c in nho["clubs"]}) == 3
    assert 780 <= len(lon["students"]) <= 820 and len(lon["clubs"]) == 20


# ------------------------------------------------------------------ 2. HOP_LE

@pytest.mark.parametrize("co", CAC_CO)
def test_hop_le_ho_so_sach_chay_xep_ok_va_co_diem_chuan(tmp_path, co):
    api, kq = _nap(tmp_path, co, "HOP_LE")
    ma_w = [w["code"] for w in kq["data"]["warnings"]
            if w["code"].startswith(("wharton_", "csv_wp"))]
    assert ma_w == []
    assert api.list_wharton_canh_bao()["data"] == []
    kqc = api.run_pipeline(seed=42)
    assert kqc["ok"], kqc["errors"]
    dc = api.get_diem_chuan()
    assert dc["ok"] and dc["data"]["co_ket_qua"] and dc["data"]["rows"]


# ------------------------------------------------------------------ 7. mọi quỹ đúng 100, đủ 4 kiểu

@pytest.mark.parametrize("co", CAC_CO)
def test_hop_le_moi_quy_dung_100_dung_tap_dung_tang(tmp_path, co):
    api, _ = _nap(tmp_path, co, "HOP_LE")
    du = _doc(duong(co, "HOP_LE"))
    tap = _tap_theo_buoi(du)
    buoi_cua = {c["club_id"]: c["buoi"] for c in du["clubs"]}
    bids = _bids(api)
    tong = {}
    for sid, cid, tier, diem in bids:
        # đúng tập CLB và đúng tầng: tầng của dòng = tầng theo tick thi của chính em
        assert cid in tap[sid][(buoi_cua[cid], tier)], (sid, cid, tier)
        tong[(sid, buoi_cua[cid], tier)] = tong.get((sid, buoi_cua[cid], tier), 0) + diem
    cac_quy = {(sid, b, q) for sid, d in tap.items() for (b, q) in d}
    assert set(tong) == cac_quy
    assert set(tong.values()) == {100}


@pytest.mark.parametrize("co", CAC_CO)
def test_du_bon_kieu_chia_diem_xuat_hien(co):
    kieu = _json("DQT_KIEU_CHIA.json")[ten_tep(co, "HOP_LE")]
    assert set(kieu.values()) == KIEU
    ma_em = {s["student_id"] for s in _doc(duong(co, "HOP_LE"))["students"]}
    assert set(kieu) == ma_em


@pytest.mark.parametrize("co", CAC_CO)
def test_kieu_chia_khop_hinh_dang_diem(tmp_path, co):
    """Kiểu ghi trong JSON phải nhìn thấy được trong điểm: all_in có một ô 100 ở quỹ nhiều CLB,
    chia đều lệch nhau tối đa 1 điểm."""
    api, _ = _nap(tmp_path, co, "HOP_LE")
    kieu = _json("DQT_KIEU_CHIA.json")[ten_tep(co, "HOP_LE")]
    buoi_cua = {c["club_id"]: c["buoi"] for c in _doc(duong(co, "HOP_LE"))["clubs"]}
    quy = {}
    for sid, cid, tier, diem in _bids(api):
        quy.setdefault((sid, buoi_cua[cid], tier), []).append(diem)
    for (sid, _b, _t), ds in quy.items():
        if len(ds) < 2:
            continue
        if kieu[sid] == "all_in":
            assert sorted(ds)[-1] == 100 and sum(ds[:]) == 100
        elif kieu[sid] == "deu":
            assert max(ds) - min(ds) <= 1


# ------------------------------------------------------------------ 3. CO_LOI

LOAI_LOI = {"thieu", "thua", "ngoai_nguyen_vong", "tang_lech", "toan_0"}


@pytest.mark.parametrize("co", CAC_CO)
def test_bang_loi_co_du_loai_moi_loai_it_nhat_3_em(co):
    bang = _json("DQT_BANG_LOI.json")[ten_tep(co, "CO_LOI")]
    dem = {}
    for d in bang:
        dem.setdefault(d["loai"], set()).add(d["student_id"])
    assert set(dem) == LOAI_LOI
    assert all(len(v) >= 3 for v in dem.values())
    assert len({d["student_id"] for d in bang}) == len(bang)       # mỗi em đúng một loại lỗi


@pytest.mark.parametrize("co", CAC_CO)
def test_co_loi_pipeline_bi_chan_dung_em_dung_loai_loi(tmp_path, co):
    api, kq = _nap(tmp_path, co, "CO_LOI")
    bang = _json("DQT_BANG_LOI.json")[ten_tep(co, "CO_LOI")]
    # cảnh báo lúc nạp: ô điểm cạnh ô nguyện vọng trống
    mo_coi = {w["params"]["student_id"] for w in kq["data"]["warnings"]
              if w["code"] == "csv_wp_khong_co_nguyen_vong"}
    assert mo_coi == {d["student_id"] for d in bang if d["loai"] == "ngoai_nguyen_vong"}
    # trước và sau khi chạy: không có kết quả, không thêm dòng lịch sử
    kqc = api.run_pipeline(seed=42)
    assert not kqc["ok"]
    assert kqc["errors"][0]["code"] == "wharton_ho_so_chua_hop_le"
    that = {}
    for e in kqc["errors"][1:]:
        that.setdefault(e["params"]["student_id"], []).append(
            (e["code"], e["params"].get("quy"), e["params"]["buoi"]))
    mong = {d["student_id"]: sorted((x["code"], x["quy"], x["buoi"]) for x in d["loi_pipeline"])
            for d in bang}
    assert {s: sorted(v) for s, v in that.items()} == mong
    assert _ket_qua(api) == {}
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM run_history").fetchone()[0] == 0


@pytest.mark.parametrize("co", CAC_CO)
def test_co_loi_phan_con_lai_hop_le(co):
    """Chỉ những em trong bảng lỗi mới sai; mọi em khác có hồ sơ hợp lệ."""
    du = _doc(duong(co, "CO_LOI"))
    bang = _json("DQT_BANG_LOI.json")[ten_tep(co, "CO_LOI")]
    sai = {d["student_id"] for d in bang}
    assert len(sai) < len(du["students"])
    tap = _tap_theo_buoi(du)
    buoi_cua = {c["club_id"]: c["buoi"] for c in du["clubs"]}
    prefs, thi, w1, w2 = {}, {}, {}, {}
    for s in du["students"]:
        sid = s["student_id"]
        prefs[sid] = [x["club_id"] for x in s["nv"]]
        thi[sid] = {x["club_id"] for x in s["nv"] if x["thi"]}
        for x in s["nv"]:
            if x.get("diem_w") not in (None, ""):
                (w1 if x["thi"] else w2).setdefault(sid, {})[x["club_id"]] = int(x["diem_w"])
    clubs = {c: {"buoi": b} for c, b in buoi_cua.items()}
    loi = rp.kiem_ho_so_wharton(prefs, thi, w1, w2, clubs)
    assert {e["params"]["student_id"] for e in loi} <= sai
    assert tap


# ------------------------------------------------------------------ 4. TRONG

@pytest.mark.parametrize("co", CAC_CO)
def test_trong_nap_duoc_khong_co_dong_wharton_bids(tmp_path, co):
    api, kq = _nap(tmp_path, co, "TRONG")
    assert _bids(api) == []
    cot = [c.value for c in openpyxl.load_workbook(duong(co, "TRONG"))["2. Học sinh"][2]]
    assert "Điểm quyết tâm" in cot                      # có cột, nhưng ô trống
    assert [w for w in kq["data"]["warnings"] if w["code"] == "csv_wp_khong_co_nguyen_vong"] == []


@pytest.mark.parametrize("co", CAC_CO)
def test_trong_tu_dien_nhu_hien_co(tmp_path, co):
    """Quỹ chỉ có MỘT CLB thì tự điền 100; quỹ có từ hai CLB mà để trống thì bị chặn."""
    api, _ = _nap(tmp_path, co, "TRONG")
    du = _doc(duong(co, "TRONG"))
    mong = {sid for sid, d in _tap_theo_buoi(du).items() if any(len(v) >= 2 for v in d.values())}
    assert mong, "bộ TRONG phải có em cần tự chia"
    kqc = api.run_pipeline(seed=42)
    assert not kqc["ok"]
    that = {e["params"]["student_id"] for e in kqc["errors"][1:]}
    assert that == mong
    assert {e["code"] for e in kqc["errors"][1:]} == {"wharton_chua_dung_het"}


def test_trong_hoc_sinh_nhap_o_kiosk_thanh_hop_le(tmp_path):
    api, _ = _nap(tmp_path, "120HS", "TRONG")
    du = _doc(duong("120HS", "TRONG"))
    tap = _tap_theo_buoi(du)
    sid = next(s for s, d in sorted(tap.items()) if any(len(v) >= 2 for v in d.values()))
    buoi_cua = {c["club_id"]: c["buoi"] for c in du["clubs"]}
    w = {1: {}, 2: {}}
    for (b, q), ds in tap[sid].items():
        for i, c in enumerate(ds):
            w[q][c] = (100 - 10 * (len(ds) - 1)) if i == 0 else 10
        assert buoi_cua[ds[0]] == b
    kq = api.submit_wharton(sid, w[1], w[2])
    assert kq["ok"], kq["errors"]
    assert {d[0] for d in _bids(api)} == {sid}


# ------------------------------------------------------------------ 5. tắt tính năng: trùng khít

def _so_bo_cot_diem(duong_tep):
    """Cùng sổ nhưng bỏ cột Điểm quyết tâm (ghi bằng cfg=None)."""
    du = _doc(duong_tep)
    ten = {c["club_id"]: c["name"] for c in du["clubs"]}
    clubs = [{k: c[k] for k in ("club_id", "name", "capacity", "reserve_capacity",
                                "reserve_group", "buoi")} for c in du["clubs"]]
    hs = [{"student_id": s["student_id"], "name": s["name"],
           "reserve_group": s["reserve_group"] or "",
           "nv": [{"club_id": x["club_id"], "thi": x["thi"], "diem": x["diem"]}
                  for x in s["nv"]]} for s in du["students"]]
    assert ten
    b = io.BytesIO()
    so_nhap.ghi_so_nhap(b, clubs, hs)
    return base64.b64encode(b.getvalue()).decode()


@pytest.mark.parametrize("seed", (1, 7, 42))
def test_tat_tinh_nang_trung_khit_voi_so_bo_diem_120hs(tmp_path, seed):
    api_a = _api(tmp_path, "tat_co_diem", bat=False)
    kq = api_a.import_so_nhap(_b64(duong("120HS", "HOP_LE")))
    assert kq["ok"], kq["errors"]
    assert any(w["code"] == "csv_wp_bo_qua" for w in kq["data"]["warnings"])
    assert _bids(api_a) == []
    api_b = _api(tmp_path, "tat_bo_diem", bat=False)
    assert api_b.import_so_nhap(_so_bo_cot_diem(duong("120HS", "HOP_LE")))["ok"]
    assert api_a.run_pipeline(seed=seed)["ok"] and api_b.run_pipeline(seed=seed)["ok"]
    ket = _ket_qua(api_a)
    assert ket and ket == _ket_qua(api_b)


def test_tat_tinh_nang_trung_khit_voi_so_bo_diem_800hs(tmp_path):
    api_a = _api(tmp_path, "tat_co_diem_l", bat=False)
    assert api_a.import_so_nhap(_b64(duong("800HS", "HOP_LE")))["ok"]
    api_b = _api(tmp_path, "tat_bo_diem_l", bat=False)
    assert api_b.import_so_nhap(_so_bo_cot_diem(duong("800HS", "HOP_LE")))["ok"]
    assert api_a.run_pipeline(seed=42)["ok"] and api_b.run_pipeline(seed=42)["ok"]
    assert _ket_qua(api_a) == _ket_qua(api_b)


# ------------------------------------------------------------------ 6. bản NHỎ giữ nguyên gốc

@pytest.mark.parametrize("bt", CAC_BIEN_THE)
def test_ban_nho_giu_nguyen_nguyen_vong_va_diem_thi_cua_tep_goc(bt):
    goc = _doc(os.path.join(DLT, "SO_NHAP_MAU_120HS_3BUOI.xlsx"))
    moi = _doc(duong("120HS", bt))
    assert [{k: c[k] for k in ("club_id", "name", "capacity", "reserve_capacity",
                               "reserve_group", "buoi")} for c in moi["clubs"]] == \
           [{k: c[k] for k in ("club_id", "name", "capacity", "reserve_capacity",
                               "reserve_group", "buoi")} for c in goc["clubs"]]
    assert [s["student_id"] for s in moi["students"]] == [s["student_id"] for s in goc["students"]]
    for a, b in zip(goc["students"], moi["students"]):
        assert (a["name"], a["reserve_group"] or "") == (b["name"], b["reserve_group"] or "")
        nv_goc = [(x["club_id"], x["thi"], so_nhap.doc_diem(x["diem"]) if x["diem"] else None)
                  for x in a["nv"]]
        nv_moi = [(x["club_id"], x["thi"], so_nhap.doc_diem(x["diem"]) if x["diem"] else None)
                  for x in b["nv"] if x["club_id"]]
        assert nv_moi == nv_goc, a["student_id"]


# ------------------------------------------------------------------ 8. sinh lại ra đúng như cũ

def test_sinh_lai_bang_script_ra_dung_noi_dung_o(tmp_path):
    script = os.path.join(DLT, "sinh_du_lieu_diem_quyet_tam.py")
    ra = tmp_path / "ra"
    kq = subprocess.run([sys.executable, script, "--ra", str(ra)], capture_output=True,
                        text=True, encoding="utf-8")
    assert kq.returncode == 0, kq.stderr
    for co in CAC_CO:
        for bt in CAC_BIEN_THE:
            assert chup(str(ra / ten_tep(co, bt)))["trang"] == \
                chup(duong(co, bt))["trang"], ten_tep(co, bt)
    for ten in ("DQT_BANG_LOI.json", "DQT_KIEU_CHIA.json"):
        with open(ra / ten, encoding="utf-8") as f:
            assert json.load(f) == _json(ten)


# ------------------------------------------------------------------ kỹ năng sinh-du-lieu-clb

SKILL = os.path.join(GOC, ".claude", "skills", "sinh-du-lieu-clb", "scripts", "sinh_du_lieu.py")


def _chay_skill(*args):
    return subprocess.run([sys.executable, SKILL, *args], capture_output=True, text=True,
                          encoding="utf-8")


def test_ngan_sach_cua_skill_bang_ngan_sach_cua_thuat_toan():
    sys.path.insert(0, os.path.dirname(SKILL))
    import sinh_du_lieu as sk
    assert sk.NGAN_SACH_DQT == rp.WHARTON_NGAN_SACH


def test_skill_mac_dinh_khong_sinh_diem_dau_ra_cu_khong_doi(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    chung = ["ngau", "--hoc-sinh", "40", "--buoi", "thu_2,thu_4", "--seed", "5"]
    assert _chay_skill(*chung, "--ra", str(a)).returncode == 0
    assert _chay_skill(*chung, "--diem-quyet-tam", "khong", "--ra", str(b)).returncode == 0
    assert chup(str(a / "SO_NHAP_CLB.xlsx")) == chup(str(b / "SO_NHAP_CLB.xlsx"))
    assert not (a / "DQT_KIEU_CHIA.json").exists()
    cot = [c.value for c in openpyxl.load_workbook(a / "SO_NHAP_CLB.xlsx")["2. Học sinh"][2]]
    assert "Điểm quyết tâm" not in cot


@pytest.mark.parametrize("kieu", ("don_dau", "deu", "all_in", "ngau_nhien"))
def test_skill_ngau_hop_le_mot_kieu_cho_ca_truong(tmp_path, kieu):
    kq = _chay_skill("ngau", "--hoc-sinh", "40", "--buoi", "thu_2,thu_4", "--seed", "5",
                     "--diem-quyet-tam", "hop_le", "--kieu-chia", kieu, "--ra", str(tmp_path))
    assert kq.returncode == 0, kq.stderr
    with open(tmp_path / "DQT_KIEU_CHIA.json", encoding="utf-8") as f:
        assert set(json.load(f)["SO_NHAP_CLB.xlsx"].values()) == {kieu}
    assert _chay_skill("soat", str(tmp_path / "SO_NHAP_CLB.xlsx")).returncode == 0


def test_skill_soat_bat_loi_diem_quyet_tam():
    kq = _chay_skill("soat", duong("120HS", "CO_LOI"))
    assert kq.returncode == 1
    bang = _json("DQT_BANG_LOI.json")[ten_tep("120HS", "CO_LOI")]
    for d in bang:
        assert d["student_id"] in kq.stderr
    assert _chay_skill("soat", duong("120HS", "TRONG")).returncode == 0


def test_skill_ap_len_so_co_san_giu_nguyen_nguyen_vong(tmp_path):
    goc = os.path.join(DLT, "SO_NHAP_MAU_120HS_3BUOI.xlsx")
    kq = _chay_skill("ap", goc, "--ra", str(tmp_path), "--ten-tep", "x.xlsx", "--seed", "3")
    assert kq.returncode == 0, kq.stderr
    a, b = _doc(goc), _doc(str(tmp_path / "x.xlsx"))
    assert [[(x["club_id"], x["thi"]) for x in s["nv"]] for s in a["students"]] == \
           [[(x["club_id"], x["thi"]) for x in s["nv"]] for s in b["students"]]
    assert any(x.get("diem_w") for s in b["students"] for x in s["nv"])


def test_chia_diem_tong_dung_100_hoa_thi_theo_ma_clb():
    sys.path.insert(0, os.path.dirname(SKILL))
    import sinh_du_lieu as sk
    assert sk.lam_tron_100({"b": 1, "a": 1, "c": 1}) == {"a": 34, "b": 33, "c": 33}
    assert sk.lam_tron_100({"x": 0, "y": 0}) == {"x": 50, "y": 50}
    assert sk.lam_tron_100({"x": 0, "y": 7}) == {"x": 0, "y": 100}
    assert sum(sk.lam_tron_100({"a": 3, "b": 5, "c": 11, "d": 1}).values()) == 100
