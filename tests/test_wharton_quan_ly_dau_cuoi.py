"""Điểm Wharton (A13.3): kịch bản đầu cuối, từ Sổ nhập tới khoá, mở khoá và xoá dữ liệu.

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test (15 học sinh, 4 CLB, 2 buổi).

  1. nạp Sổ nhập có điểm W; hai em chia sai (90 điểm);
  2. thẻ Quản lý thấy đúng hai cảnh báo; sửa hai em bằng `admin_save_wharton`;
  3. chạy xếp thành công: khoá bật;
  4. nạp lại tệp: phần Wharton bị bỏ, kèm cảnh báo `wharton_da_khoa`;
  5. mở khoá, sửa một em, chạy lại: khoá lại, `match_results` đổi đúng chỗ em đó ảnh hưởng (buổi thứ 5);
  6. nhật ký có đủ chuỗi thao tác theo đúng thứ tự;
  7. tắt Wharton và chạy lại cùng seed: kết quả bằng kết quả của bộ không có điểm Wharton;
  8. `reset_data`: nhật ký vẫn còn đủ.
"""

import base64
import io

import pytest

openpyxl = pytest.importorskip("openpyxl")

import api as api_mod  # noqa: E402
import so_nhap  # noqa: E402
from _wharton import bat_wharton, dong_bids  # noqa: E402

SEED = 3
SAI = ("HS03", "HS07")                       # hai em chia sai: 50 + 40 = 90
CFG_W = {"rules": {"wharton": True, "max_choices": 10, "max_tests": 5, "score_scope": "per_slot"}}
CFG_TAT = {"rules": {"wharton": False, "max_choices": 10, "max_tests": 5, "score_scope": "per_slot"}}


def _clb(cid, buoi, cho):
    return {"club_id": cid, "name": "CLB " + cid, "capacity": cho, "reserve_capacity": 0,
            "reserve_group": "", "buoi": buoi}


CLUBS = [_clb("A", "thu_3", 8), _clb("B", "thu_3", 8), _clb("C", "thu_5", 3), _clb("D", "thu_5", 3)]
SIDS = ["HS%02d" % i for i in range(1, 16)]


def _chia_cd(i):
    """Điểm quỹ 2 của buổi thứ 5 (CLB C và D). HS01 cố ý để C thấp nhất; em sai thiếu 10 điểm."""
    c = 0 if i == 1 else 20 + i
    d = 100 - c
    return (c - 10, d) if SIDS[i - 1] in SAI else (c, d)


def _so_nhap(co_w=True, doi=None):
    """Sổ nhập: ai cũng tick thi A (có điểm); buổi thứ 5 không ai thi nên C, D chung quỹ 2."""
    doi = doi or {}
    hs = []
    for i, sid in enumerate(SIDS, start=1):
        c, d = doi.get(sid, _chia_cd(i))
        nv = [{"club_id": "A", "thi": True, "diem": 5 + (i % 5)},
              {"club_id": "B", "thi": False, "diem": ""},
              {"club_id": "C", "thi": False, "diem": "", **({"diem_w": c} if co_w else {})},
              {"club_id": "D", "thi": False, "diem": "", **({"diem_w": d} if co_w else {})}]
        hs.append({"student_id": sid, "name": "Em " + sid, "reserve_group": "", "nv": nv})
    b = io.BytesIO()
    so_nhap.ghi_so_nhap(b, CLUBS, hs, cfg=CFG_W if co_w else CFG_TAT)
    return base64.b64encode(b.getvalue()).decode()


def _nk(api):
    with api._ket_noi_doc() as cur:
        return [(r["nguon"], r["hanh_dong"]) for r in cur.execute(
            "SELECT * FROM wharton_nhat_ky ORDER BY id")]


def _kq(api):
    with api._ket_noi_doc() as cur:
        return {(r[0], r[1]): r[2] for r in cur.execute(
            "SELECT student_id, buoi, club_id FROM match_results")}


def _nap(api, **kw):
    kq = api.import_so_nhap(_so_nhap(**kw))
    assert kq["ok"], kq["errors"]
    return kq


def test_kich_ban_dau_cuoi(tmp_path):
    api = api_mod.PipelineAPI(str(tmp_path / "a.db"))
    bat_wharton(api)

    # 1. nạp Sổ nhập; hai em chia sai được cảnh báo (nạp không bị chặn)
    kq = _nap(api)
    sai = [w for w in kq["data"]["warnings"] if w["code"] == "wharton_chua_dung_het"]
    assert sorted(w["params"]["student_id"] for w in sai) == sorted(SAI)
    assert len(dong_bids(api)) == 15 * 2

    # 2. thẻ Quản lý thấy đúng 2 cảnh báo; sửa hai em
    cb = api.list_wharton_canh_bao()["data"]
    assert [(c["student_id"], c["loai"]) for c in cb] == [(s, "chua_hop_le") for s in sorted(SAI)]
    for sid in SAI:
        i = SIDS.index(sid) + 1
        c = 0 if i == 1 else 20 + i
        assert api.admin_save_wharton(sid, {}, {"C": c, "D": 100 - c})["ok"]
    assert api.list_wharton_canh_bao()["data"] == []

    # 3. chạy xếp thành công: khoá bật
    assert api.run_pipeline(seed=SEED)["ok"]
    assert api.get_wharton_lock_status()["data"]["is_locked"] is True
    truoc = _kq(api)
    bids_truoc = dong_bids(api)

    # 4. nạp lại tệp (điểm HS01 đổi): phần Wharton bị bỏ, kèm cảnh báo
    kq = _nap(api, doi={"HS01": (100, 0)})
    assert "wharton_da_khoa" in [w["code"] for w in kq["data"]["warnings"]]
    assert dong_bids(api) == bids_truoc

    # 5. mở khoá, sửa HS01 (C từ thấp nhất lên cao nhất), chạy lại: khoá lại
    assert api.mo_khoa_wharton("MO")["ok"]
    assert api.get_wharton_lock_status()["data"]["is_locked"] is False
    assert api.admin_save_wharton("HS01", {}, {"C": 100, "D": 0})["ok"]
    assert api.run_pipeline(seed=SEED)["ok"]
    assert api.get_wharton_lock_status()["data"]["is_locked"] is True
    sau = _kq(api)
    doi_cho = {k for k in truoc if truoc[k] != sau.get(k)}
    assert doi_cho and all(buoi == "thu_5" for _sid, buoi in doi_cho)     # buổi thứ 3 không đổi
    assert ("HS01", "thu_5") in doi_cho and sau[("HS01", "thu_5")] == "C"

    # 6. nhật ký có đủ chuỗi thao tác theo đúng thứ tự
    assert _nk(api) == (
        [("nap_tep", "luu")] * 15 + [("quan_ly", "luu")] * 2 + [("he_thong", "khoa")]
        + [("quan_ly", "mo_khoa"), ("quan_ly", "luu"), ("he_thong", "khoa")])
    n_nk = len(_nk(api))

    # 7. tắt Wharton, chạy lại cùng seed: bằng kết quả của bộ không có điểm Wharton
    bat_wharton(api, bat=False)
    assert api.run_pipeline(seed=SEED)["ok"]
    ket_tat = _kq(api)
    doi_chung = api_mod.PipelineAPI(str(tmp_path / "b.db"))
    bat_wharton(doi_chung, bat=False)
    _nap(doi_chung, co_w=False)
    assert doi_chung.run_pipeline(seed=SEED)["ok"]
    assert ket_tat == _kq(doi_chung)
    assert len(_nk(api)) == n_nk                        # tắt Wharton: không ghi thêm gì

    # 8. reset_data: nhật ký vẫn còn đủ (và có thêm dòng mở khoá + xoá tất cả)
    bat_wharton(api)
    assert api.reset_data("hoc_sinh", "XOA")["ok"]
    nk = _nk(api)
    assert nk[:n_nk] == (
        [("nap_tep", "luu")] * 15 + [("quan_ly", "luu")] * 2 + [("he_thong", "khoa")]
        + [("quan_ly", "mo_khoa"), ("quan_ly", "luu"), ("he_thong", "khoa")])
    assert nk[n_nk:] == [("xoa_du_lieu", "xoa_tat_ca"), ("xoa_du_lieu", "mo_khoa")]
    assert api.get_wharton_lock_status()["data"]["is_locked"] is False
