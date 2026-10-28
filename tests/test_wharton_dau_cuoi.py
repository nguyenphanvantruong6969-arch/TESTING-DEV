"""Điểm Wharton (A13, vòng 2): kịch bản ĐẦU CUỐI qua các API của sản phẩm.

Dữ liệu là dữ liệu MÔ PHỎNG (16 học sinh, 4 CLB, 2 buổi), dựng ngay trong test bằng `sinh_bo`;
không phải khảo sát thật.

Đường đi: tạo workspace bật Wharton → nạp Sổ nhập có "Điểm W k" → sửa điểm một em qua
`submit_wharton` → chấm điểm thi (một em vắng) → báo cáo sức khoẻ có mục vắng thi → chạy xếp,
ổn định → xuất Sổ nhập, nạp vào workspace mới, chạy lại cùng seed ra y hệt (W7 ở mức sản phẩm)
→ tắt Wharton, chạy lại cùng seed ra đúng kết quả khi không có điểm Wharton.
"""

import base64
import io

import pytest

openpyxl = pytest.importorskip("openpyxl")

import rbda_priority_pipeline as rp  # noqa: E402
import so_nhap  # noqa: E402
import workspace as ws  # noqa: E402
from _wharton import bat_wharton, canh_bao, dong_bids  # noqa: E402
from api import PipelineAPI  # noqa: E402
from test_wharton import sinh_bo  # noqa: E402
from test_wharton_pipeline import _ket_qua  # noqa: E402

SEED = 13
CFG = {"rules": {"wharton": True}}


def _api(tmp_path, ten):
    goc = tmp_path / ("goc_" + ten)
    goc.mkdir()
    slug = ws.tao(str(goc), "Đợt " + ten, CFG)
    (tmp_path / ("xuat_" + ten)).mkdir()
    return PipelineAPI(ws.duong_dan_db(str(goc), slug), thu_muc_xuat=str(tmp_path / ("xuat_" + ten)),
                       thu_muc_goc_ws=str(goc))


def _so_nhap_tu_bo(bo):
    """Sổ nhập (bytes) có "Điểm W k": mọi lượt thi ghi chữ `thi` (điểm chấm sau bằng API)."""
    clubs = [{"club_id": c, "name": "CLB " + c, "capacity": bo.cap[c], "reserve_capacity": 0,
              "reserve_group": "", "buoi": bo.buoi[c]} for c in bo.cids]
    hs = []
    for s in bo.sids:
        nv = []
        for c in bo.prefs[s]:
            w = bo.w1.get(s, {}).get(c) if c in bo.tick[s] else bo.w2.get(s, {}).get(c)
            nv.append({"club_id": c, "thi": c in bo.tick[s], "diem": "", "diem_w": w})
        hs.append({"student_id": s, "name": "Em " + s, "reserve_group": "", "nv": nv})
    b = io.BytesIO()
    so_nhap.ghi_so_nhap(b, clubs, hs, cfg={"rules": {"wharton": True}})
    return b.getvalue()


def _b64(du):
    return base64.b64encode(du).decode()


def _cham(api, bo, bo_qua):
    for cid in bo.cids:
        diem = [{"student_id": s, "score": v} for s, v in bo.diem_thi[cid].items()
                if (s, cid) != bo_qua]
        if diem:
            assert api.submit_club_scores(cid, diem)["ok"]


def test_dau_cuoi_nap_so_sua_diem_cham_thi_chay_xuat_nap_lai_va_tat_wharton(tmp_path):
    bo = sinh_bo(2026, n_hs=16, n_clb=4, so_buoi=2)
    vang = next((s, c) for s in bo.sids for c in sorted(bo.tick[s]))        # một em vắng thi
    em_sua = next(s for s in bo.sids if s != vang[0] and len(bo.prefs[s]) >= 2)

    # 1-2. workspace bật Wharton, nạp Sổ nhập có "Điểm W k"
    api = _api(tmp_path, "goc")
    assert api.get_workspace_config()["data"]["config"]["rules"]["wharton"] is True
    kq = api.import_so_nhap(_b64(_so_nhap_tu_bo(bo)))
    assert kq["ok"], kq["errors"]
    assert [w for w in kq["data"]["warnings"] if w["code"].startswith(("wharton_", "csv_wp"))] == []
    assert len(dong_bids(api)) == sum(len(p) for p in bo.prefs.values())

    # 3. sửa điểm một em qua submit_wharton (một quỹ chia lại)
    cu = [d for d in dong_bids(api) if d[0] == em_sua]
    t2 = [d[1] for d in cu if d[2] == 2]
    t1 = [d[1] for d in cu if d[2] == 1]
    w2_moi = {c: (100 if i == 0 else 0) for i, c in enumerate(t2)}   # dồn hết 100 vào CLB đầu
    w1_moi = {d[1]: d[3] for d in cu if d[2] == 1}
    kq = api.submit_wharton(em_sua, w1_moi, w2_moi)
    assert kq["ok"], kq["errors"]
    moi = [d for d in dong_bids(api) if d[0] == em_sua]
    assert {d[1]: d[3] for d in moi if d[2] == 2} == w2_moi
    assert {d[1]: d[3] for d in moi if d[2] == 1} == w1_moi and len(t1) == len(w1_moi)

    # 4-5. chấm điểm thi qua API sẵn có (một em vắng) → sức khoẻ dữ liệu có mục vắng thi
    _cham(api, bo, vang)
    suc_khoe = api.get_data_health_report()["data"]["warnings"]
    assert [(w["code"], w["params"]["n"], w["severity"]) for w in suc_khoe
            if "wharton" in w["code"]] == [("health_wharton_vang_thi", 1, "medium")]

    # 6. chạy xếp thành công, ổn định, bằng đúng run_rbda_nhieu_buoi với điểm hiệu lực
    kq = api.run_pipeline(seed=SEED)
    assert kq["ok"], kq["errors"]
    validate = [b for b in kq["data"]["steps"] if b["step"] == "validate" and b["status"] == "done"]
    assert [e["code"] for e in validate[0]["detail"]] == ["wharton_vang_thi"]
    du, _dvt, w = rp.load_from_sqlite_kem_dau_van_tay_wharton(api.db_path, api._luat_nghiem())
    students, clubs, scores, app, prefs, stb = du
    hl, _tb = rp.diem_wharton_hieu_luc(prefs, w["w1"], w["w2"], scores)
    elig = rp.default_reserve_eligible_fn(students, clubs)
    mong_doi = rp.run_rbda_nhieu_buoi(students, clubs, scores, app, prefs, stb, elig,
                                      seed=SEED, diem_wharton=hl)
    ket_goc = _ket_qua(api)
    assert ket_goc == {(s, b): c for s, theo in mong_doi.assignment.items() for b, c in theo.items()}
    assert all(not v for v in rp.verify_stability_tuan(mong_doi, clubs, prefs, elig).values())

    # 7. xuất Sổ nhập, nạp vào workspace MỚI, chạy lại cùng seed: y hệt (W7 ở mức sản phẩm)
    xuat = api.export_du_lieu_dau_vao()
    assert xuat["ok"], xuat["errors"]
    with open(xuat["data"]["path"], "rb") as f:
        du_so = f.read()
    api2 = _api(tmp_path, "moi")
    kq = api2.import_so_nhap(_b64(du_so))
    assert kq["ok"], kq["errors"]
    assert dong_bids(api2) == dong_bids(api)
    assert canh_bao(kq, "wharton_chua_dung_het") == []
    assert api2.run_pipeline(seed=SEED)["ok"]
    assert _ket_qua(api2) == ket_goc

    # 8. tắt Wharton rồi chạy lại cùng seed: bằng kết quả của một workspace chưa từng có điểm Wharton
    bat_wharton(api, bat=False)
    assert api.run_pipeline(seed=SEED)["ok"]
    ket_tat = _ket_qua(api)
    xuat_tat = api.export_du_lieu_dau_vao()
    assert xuat_tat["ok"]
    with open(xuat_tat["data"]["path"], "rb") as f:
        co_w = [c.value for c in openpyxl.load_workbook(io.BytesIO(f.read()))["2. Học sinh"][1]]
    assert not any(str(c).startswith("Điểm W") for c in co_w if c)
    api3 = PipelineAPI(str(tmp_path / "khong_wharton.db"))
    with open(xuat_tat["data"]["path"], "rb") as f:
        kq = api3.import_so_nhap(_b64(f.read()))
    assert kq["ok"], kq["errors"]
    assert dong_bids(api3) == []
    assert api3.run_pipeline(seed=SEED)["ok"]
    assert _ket_qua(api3) == ket_tat
