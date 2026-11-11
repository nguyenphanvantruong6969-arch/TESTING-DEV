"""FA-5 (A6, FA-DAA): số thành viên tối thiểu — đóng CLB thiếu người, mỗi vòng một CLB (D3).

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.
Tiêu chí V§13.11: đóng CLB thiếu người thì chạy lại hội tụ, không vòng lặp vô hạn. Mỗi CLB mở đạt
tối thiểu hoặc bị đóng; chạy lại cùng STB cho đúng kết quả cũ; thứ tự đóng không phụ thuộc thứ tự
đầu vào; hai CLB cùng thiếu thì CLB thiếu NHIỀU hơn đóng trước.
"""


import pytest

import rbda_priority_pipeline as rp
from _fa import bat_fa, dung_fa_clb, dung_hs_fa, ma
from test_fa_chay import _bo, _chay, _thanh_vien


def _clb(cho, loai, toi=None, san=None):
    return ({"capacity": cho, "reserve_capacity": 0, "reserve_group": None, "buoi": "b1"},
            {"loai": loai, "diem_san": san, "so_toi_thieu": toi, "suc_chua_phong": None})


def _nho(clubs_spec, prefs, n=None):
    """Bộ nhỏ tự dựng: `clubs_spec` {cid: (cho, loai, toi)}, `prefs` {sid: [cid]} (không huy chương,
    không điểm thi); STB theo mã học sinh."""
    clubs, fa = {}, {}
    for cid, spec in clubs_spec.items():
        clubs[cid], fa[cid] = _clb(*spec)
    sids = sorted(set(prefs) | {"z%d" % i for i in range(n or 0)})
    stb = {s: i + 1 for i, s in enumerate(sids)}
    students = {s: {"stb": stb[s], "reserve_group": None} for s in sids}
    return dict(students=students, clubs=clubs, tested_scores={c: {} for c in clubs},
                applicants=rp.hop_ung_vien({c: [] for c in clubs}, prefs), preferences=prefs,
                stb_lottery=stb, fa_clb=fa, giu_cho=[], huy_chuong={})


def _bo_thieu(seed):
    bo = _bo(n=16, seed=seed)
    for cid in ("G", "S"):
        bo["clubs"][cid]["capacity"] = 8
        bo["fa_clb"][cid]["so_toi_thieu"] = 6
    bo["fa_clb"]["S"]["diem_san"] = 2
    return bo


@pytest.mark.parametrize("seed", range(10))
def test_moi_clb_mo_dat_toi_thieu_hoac_bi_dong(seed):
    bo = _bo_thieu(seed)
    kq = _chay(bo, seed=seed)
    tv = _thanh_vien(kq)
    dong = {d["club_id"] for d in kq.dong_cua}
    for cid in ("G", "S"):
        if cid in dong:
            assert len(tv.get(cid, [])) == 0
        else:
            assert len(tv.get(cid, [])) >= 6, (cid, tv.get(cid))
    assert len(kq.dong_cua) <= len(bo["clubs"])                    # hội tụ, không quá số CLB


def test_bo_mo_phong_co_that_su_dong_clb():
    # canh cho test ở trên không đúng một cách tầm thường: ít nhất vài seed phải đóng CLB
    so_dong = sum(len(_chay(_bo_thieu(s), seed=s).dong_cua) for s in range(10))
    assert so_dong >= 5


def test_cung_stb_chay_lai_giong_het_va_khong_phu_thuoc_thu_tu():
    bo = _bo(n=50, seed=4)
    bo["fa_clb"]["G"]["so_toi_thieu"] = 4
    a, b = _chay(bo, seed=4), _chay(bo, seed=4)
    dao = {**bo, "clubs": dict(reversed(list(bo["clubs"].items()))),
           "preferences": dict(reversed(list(bo["preferences"].items())))}
    c = _chay(dao, seed=4)
    assert a.ket_qua.assignment == b.ket_qua.assignment == c.ket_qua.assignment
    assert a.dong_cua == b.dong_cua == c.dong_cua


def test_hai_clb_thieu_thi_clb_thieu_nhieu_hon_dong_truoc():
    bo = _nho({"G": (5, "GIOI_HAN", 5), "H": (5, "GIOI_HAN", 3), "T": (50, "TU_DO", None)},
              {"x": ["G", "T"], "y": ["H", "T"]})
    kq = _chay(bo)
    assert [d["club_id"] for d in kq.dong_cua] == ["G", "H"]       # G thiếu 4, H thiếu 2
    assert kq.dong_cua[0]["thieu"] == 4 and kq.dong_cua[0]["lan"] == 1
    assert kq.dong_cua[1]["lan"] == 2


def test_dong_tung_clb_mot_khong_dong_tat_ca_cung_luc():
    # G thiếu nhiều (min 5, có 1), H thiếu ít (min 2, có 1). Đóng G đưa x sang H -> H đủ 2 người.
    # Đóng cả hai cùng lúc sẽ đóng oan H.
    bo = _nho({"G": (5, "GIOI_HAN", 5), "H": (5, "GIOI_HAN", 2), "T": (50, "TU_DO", None)},
              {"x": ["G", "H", "T"], "y": ["H", "T"]})
    kq = _chay(bo)
    assert [d["club_id"] for d in kq.dong_cua] == ["G"]
    assert sorted(_thanh_vien(kq)["H"]) == ["x", "y"]


def test_hoa_thieu_thi_it_nguoi_hon_roi_ma_clb():
    # A: min 4, có 2 (thiếu 2); B: min 3, có 1 (thiếu 2) -> hoà thiếu, B ít người hơn nên đóng trước
    bo = _nho({"A": (5, "GIOI_HAN", 4), "B": (5, "GIOI_HAN", 3), "T": (50, "TU_DO", None)},
              {"p": ["A", "T"], "q": ["A", "T"], "r": ["B", "T"]})
    assert _chay(bo).dong_cua[0]["club_id"] == "B"
    # hoà hoàn toàn (cùng thiếu, cùng số người): club_id nhỏ trước
    bo2 = _nho({"A": (5, "GIOI_HAN", 4), "B": (5, "GIOI_HAN", 4), "T": (50, "TU_DO", None)},
               {"p": ["A", "T"], "r": ["B", "T"]})
    assert _chay(bo2).dong_cua[0]["club_id"] == "A"


def test_ghi_lai_clb_closed_cho_nguoi_xin():
    bo = _nho({"G": (5, "GIOI_HAN", 5), "T": (50, "TU_DO", None)}, {"x": ["G", "T"], "y": ["G", "T"]})
    kq = _chay(bo)
    dong = [r for r in kq.loai_bo if r["ly_do"] == "CLUB_CLOSED"]
    assert sorted(r["student_id"] for r in dong) == ["x", "y"] and {r["club_id"] for r in dong} == {"G"}
    assert all(kq.ket_qua.assignment[s]["b1"] == "T" for s in ("x", "y"))   # rơi về CLB Tự do


def test_tu_do_va_toi_thieu_bang_khong_khong_bi_dong():
    bo = _nho({"T": (50, "TU_DO", 10), "G": (5, "GIOI_HAN", 0), "H": (5, "GIOI_HAN", None)},
              {"x": ["G", "T"], "y": ["H", "T"]})
    assert _chay(bo).dong_cua == []


def test_clb_dong_co_nhan_canh_bao_xap_xi():
    bo = _nho({"G": (5, "GIOI_HAN", 5), "T": (50, "TU_DO", None)}, {"x": ["G", "T"]})
    kq = _chay(bo)
    assert "fa_clb_dong_thieu_nguoi" in ma(kq.canh_bao)
    e = next(e for e in kq.canh_bao if e["code"] == "fa_clb_dong_thieu_nguoi")
    assert e["params"]["club_id"] == "G"
    from i18n_errors import format_message
    assert "xấp xỉ" in format_message(e["code"], e["params"], "vi")


def test_khong_dong_khi_tat_ca_du():
    bo = _nho({"G": (5, "GIOI_HAN", 2), "T": (50, "TU_DO", None)},
              {"x": ["G", "T"], "y": ["G", "T"], "z": ["G", "T"]})
    kq = _chay(bo)
    assert kq.dong_cua == [] and len(_thanh_vien(kq)["G"]) == 3


def test_pipeline_dong_clb_va_van_hop_le(api):
    bat_fa(api)
    dung_fa_clb(api, T=(50, "TU_DO"), G=(3, "GIOI_HAN", None, 3), H=(3, "GIOI_HAN", None, 1))
    dung_hs_fa(api, "a", "b", "c", nv={"a": ["G", "H", "T"], "b": ["H", "T"], "c": ["T"]})
    kq = api.run_pipeline(seed=5)
    assert kq["ok"], kq["errors"]
    with api._ket_noi_doc() as cur:
        mr = dict(cur.execute("SELECT student_id, club_id FROM match_results").fetchall())
    assert "G" not in mr.values()                                  # G (min 3, chỉ 1 người) bị đóng
    assert mr["a"] == "H" and mr["b"] == "H" and mr["c"] == "T"
