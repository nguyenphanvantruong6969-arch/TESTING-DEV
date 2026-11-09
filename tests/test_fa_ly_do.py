"""FA-6 (C3, FA-DAA): lý do mỗi kết quả, điểm chuẩn, danh sách chờ, câu giải thích.

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.
Tiêu chí V§13.9: mọi từ chối có lý do hợp lệ. Câu giải thích của một học sinh KHÔNG chứa mã hay tên
của học sinh khác (rủi ro C3). Danh sách chờ (D4): Tuyển chọn = điểm, huy chương, bốc thăm; Giới hạn =
huy chương, bốc thăm; chỉ học sinh xếp CLB đó CAO hơn CLB hiện tại.
"""

import copy
import csv
import re

import pytest

import fa_daa
import fa_ly_do
import rbda_priority_pipeline as rp
from _fa import bat_fa, dung_fa_clb, dung_hs_fa, ma
from test_fa_chay import _bo, _chay
from test_fa_toi_thieu import _nho

HOP_LE = {"ACCEPTED", "REJECTED", "REMOVED", "FALLBACK"}
MA_LY_DO = {"SCORE", "MEDAL", "LOTTERY", "RESERVED", "BELOW_PASS", "NOT_ATTEMPTED", "CLUB_CLOSED",
            "KHONG_DANG_KY", "HET_NGUYEN_VONG", "ACCEPTED"}


def _rows(bo, **kw):
    kq = _chay(bo, **kw)
    rows = fa_daa.ly_do_ket_qua(kq, bo["preferences"], bo["huy_chuong"], bo["fa_clb"])
    return kq, rows


def _tim(rows, sid, cid):
    r = [x for x in rows if x["student_id"] == sid and x["club_id"] == cid]
    assert len(r) == 1, (sid, cid, r)
    return r[0]


def _hs(bo, **diem):
    """Đặt điểm thi CLB S theo {sid: điểm}."""
    bo["tested_scores"]["S"] = dict(diem)
    bo["applicants"] = rp.hop_ung_vien({**{c: [] for c in bo["clubs"]}, "S": list(diem)},
                                       bo["preferences"])
    return bo


# ------------------------------------------------------------------- từng mã lý do


def test_score_diem_chuan_va_cho():
    bo = _nho({"S": (1, "TUYEN_CHON", None, 3), "T": (50, "TU_DO", None)},
              {"a": ["S", "T"], "b": ["S", "T"], "c": ["S", "T"], "d": ["S", "T"]})
    _hs(bo, a=9.0, b=8.0, c=7.0, d=7.0)
    bo["huy_chuong"] = {"c": {"S": 60}, "d": {"S": 30}}
    kq, rows = _rows(bo)
    assert _tim(rows, "a", "S")["outcome"] == "ACCEPTED" and _tim(rows, "a", "S")["rank_in_list"] == 1
    b = _tim(rows, "b", "S")
    assert (b["outcome"], b["reason"], b["cut_score"], b["waitlist_pos"]) == ("REJECTED", "SCORE", 9.0, 1)
    # danh sách chờ Tuyển chọn: điểm, rồi huy chương, rồi bốc thăm
    assert [(_tim(rows, s, "S")["waitlist_pos"]) for s in ("b", "c", "d")] == [1, 2, 3]
    assert _tim(rows, "c", "S")["reason"] == "SCORE"


def test_medal_khi_bang_diem_o_tuyen_chon():
    bo = _nho({"S": (1, "TUYEN_CHON", None, 3), "T": (50, "TU_DO", None)},
              {"a": ["S", "T"], "b": ["S", "T"]})
    _hs(bo, a=7.0, b=7.0)
    bo["huy_chuong"] = {"a": {"S": 60}, "b": {"S": 10}}
    _, rows = _rows(bo)
    b = _tim(rows, "b", "S")
    assert (b["reason"], b["cut_medal"]) == ("MEDAL", 60)


def test_medal_o_gioi_han_va_waitlist_khong_co_diem():
    bo = _nho({"G": (1, "GIOI_HAN", None), "T": (50, "TU_DO", None)},
              {"a": ["G", "T"], "b": ["G", "T"], "c": ["G", "T"]})
    bo["huy_chuong"] = {"a": {"G": 60}, "b": {"G": 30}, "c": {"G": 30}}
    _, rows = _rows(bo)
    assert _tim(rows, "b", "G")["reason"] == "MEDAL" and _tim(rows, "b", "G")["cut_score"] is None
    # b và c cùng huy chương 30: thứ tự chờ theo bốc thăm (stb b=2 < c=3)
    assert [_tim(rows, s, "G")["waitlist_pos"] for s in ("b", "c")] == [1, 2]
    assert _tim(rows, "c", "G")["reason"] == "MEDAL"
    # khác huy chương thì huy chương trước bốc thăm: c (30, stb 3) chờ trước b (10, stb 2)
    bo["huy_chuong"] = {"a": {"G": 60}, "b": {"G": 10}, "c": {"G": 30}}
    _, rows = _rows(bo)
    assert [_tim(rows, s, "G")["waitlist_pos"] for s in ("c", "b")] == [1, 2]


def test_lottery_dem_n_va_k():
    bo = _nho({"G": (2, "GIOI_HAN", None), "T": (50, "TU_DO", None)},
              {s: ["G", "T"] for s in ("a", "b", "c", "d")})
    _, rows = _rows(bo)
    d = _tim(rows, "d", "G")
    assert d["reason"] == "LOTTERY" and d["n_hoa"] == 3 and d["k_cho"] == 2     # bằng 3 bạn, 2 chỗ
    assert d["cut_stb"] == 2 and d["waitlist_pos"] == 2     # c (stb 3) chờ trước d (stb 4)


def test_reserved_thang_huy_chuong_cao_hon():
    bo = _nho({"G": (1, "GIOI_HAN", None), "T": (50, "TU_DO", None)},
              {"a": ["G", "T"], "b": ["G", "T"]})
    bo["huy_chuong"] = {"b": {"G": 60}}
    bo["giu_cho"] = [("G", "a")]
    kq, rows = _rows(bo)
    assert _tim(rows, "a", "G")["outcome"] == "ACCEPTED"
    assert _tim(rows, "b", "G")["reason"] == "RESERVED"


def test_duoi_san_chua_thi_va_clb_dong_va_du_phong():
    bo = _nho({"S": (5, "TUYEN_CHON", None, 5), "G": (5, "GIOI_HAN", 4), "T": (50, "TU_DO", None)},
              {"c": ["S", "T"], "d": ["S", "T"], "e": ["G", "T"], "f": ["G"], "g": []})
    _hs(bo, c=2.0)
    kq, rows = _rows(bo)
    c = _tim(rows, "c", "S")
    assert (c["outcome"], c["reason"], c["cut_score"]) == ("REMOVED", "BELOW_PASS", 5)   # mốc 5
    assert _tim(rows, "d", "S")["reason"] == "NOT_ATTEMPTED"
    assert _tim(rows, "e", "G")["reason"] == "CLUB_CLOSED"
    # f chỉ xếp G (bị đóng) và g không đăng ký: cả hai vào CLB Tự do
    f = [r for r in rows if r["student_id"] == "f" and r["outcome"] == "FALLBACK"]
    g = [r for r in rows if r["student_id"] == "g" and r["outcome"] == "FALLBACK"]
    assert f[0]["reason"] == "HET_NGUYEN_VONG" and f[0]["club_id"] == "T"
    assert g[0]["reason"] == "KHONG_DANG_KY" and g[0]["club_id"] == "T"


def test_clb_xep_thap_hon_clb_nhan_thi_khong_co_dong_va_khong_o_danh_sach_cho():
    bo = _nho({"G": (1, "GIOI_HAN", None), "H": (1, "GIOI_HAN", None), "T": (50, "TU_DO", None)},
              {"a": ["G", "T"], "b": ["H", "G", "T"], "c": ["G", "H", "T"]})
    bo["huy_chuong"] = {"a": {"G": 60}, "c": {"G": 30}}
    kq, rows = _rows(bo)
    assert kq.ket_qua.assignment["b"]["b1"] == "H"
    assert not [r for r in rows if r["student_id"] == "b" and r["club_id"] == "G"]   # G xếp dưới H
    assert _tim(rows, "c", "G")["waitlist_pos"] == 1       # c xếp G cao hơn CLB hiện tại -> có chờ
    assert [r["student_id"] for r in rows if r["club_id"] == "G" and r["waitlist_pos"]] == ["c"]


def test_khoa_tot_hon_nguoi_cuoi_nhan_thi_ném_loi_on_dinh():
    bo = _nho({"G": (1, "GIOI_HAN", None), "T": (50, "TU_DO", None)},
              {"a": ["G", "T"], "b": ["G", "T"]})
    bo["huy_chuong"] = {"a": {"G": 60}}
    kq = _chay(bo)
    kq.ket_qua.per_buoi["b1"].assignment.update({"a": "T", "b": "G"})   # xếp ngược: b thắng oan
    with pytest.raises(ValueError, match="ổn định|on dinh|stability"):
        fa_daa.ly_do_ket_qua(kq, bo["preferences"], bo["huy_chuong"], bo["fa_clb"])


# ------------------------------------------------------------------- tính chất


@pytest.mark.parametrize("seed", range(8))
def test_moi_tu_choi_co_ly_do_hop_le(seed):
    bo = _bo(n=40, seed=seed, hai_buoi=True)
    bo["fa_clb"]["G"]["so_toi_thieu"] = 2
    kq, rows = _rows(bo, seed=seed)
    cac = {(r["student_id"], r["club_id"], r["buoi"]): r for r in rows}
    for sid, p in bo["preferences"].items():
        for buoi in ("b1", "b2"):
            ds = [c for c in p if kq.clubs[c]["buoi"] == buoi]
            cuoi = kq.ket_qua.assignment[sid][buoi]
            vi_tri = ds.index(cuoi) if cuoi in ds else len(ds)
            for c in ds[:vi_tri]:                       # mọi CLB xếp trên CLB cuối cùng đều có dòng
                r = cac[(sid, c, buoi)]
                assert r["reason"] in MA_LY_DO and r["outcome"] in HOP_LE
                assert r["outcome"] in ("REJECTED", "REMOVED")
    assert all(r["reason"] in MA_LY_DO for r in rows)


@pytest.mark.parametrize("seed", range(4))
def test_hang_cho_tuyen_chon_khong_dat_nguoi_diem_thap_truoc(seed):
    bo = _bo(n=60, seed=seed, san=2)
    kq, rows = _rows(bo, seed=seed)
    diem = bo["tested_scores"]["S"]
    cho = sorted((r for r in rows if r["club_id"] == "S" and r["waitlist_pos"]),
                 key=lambda r: r["waitlist_pos"])
    assert [r["waitlist_pos"] for r in cho] == list(range(1, len(cho) + 1))
    diem_cho = [diem[r["student_id"]] for r in cho]
    assert diem_cho == sorted(diem_cho, reverse=True)


def test_cau_giai_thich_khong_chua_ma_hoc_sinh_khac():
    bo = _nho({"S": (1, "TUYEN_CHON", None, 3), "G": (1, "GIOI_HAN", None), "T": (50, "TU_DO", None)},
              {"anna": ["S", "G", "T"], "binh": ["S", "G", "T"], "chau": ["G", "T"], "duy": ["G", "T"]})
    _hs(bo, anna=9.0, binh=8.0)
    kq, rows = _rows(bo)
    ten = {"S": "CLB Sáng tạo", "G": "CLB Cờ", "T": "CLB Tự do"}
    for r in rows:
        cau = fa_ly_do.cau_ly_do(r, ten[r["club_id"]])
        assert cau and isinstance(cau, str)
        for sid in bo["students"]:
            assert not re.search(r"\b%s\b" % sid, cau), (sid, cau)


def test_cau_theo_mau_v9_1():
    r = {"outcome": "ACCEPTED", "reason": "ACCEPTED", "rank_in_list": 1}
    assert fa_ly_do.cau_ly_do(r, "CLB X") == "Em được xếp vào CLB X – nguyện vọng 1 của em."
    r = {"outcome": "REJECTED", "reason": "SCORE", "cut_score": 8.0, "diem_em": 6.0}
    assert fa_ly_do.cau_ly_do(r, "CLB X") == (
        "CLB X đủ chỗ với các bạn có điểm thử thách cao hơn (điểm chuẩn 8, em 6).")
    r = {"outcome": "REJECTED", "reason": "MEDAL"}
    assert "huy chương cao hơn ở CLB X được xét trước" in fa_ly_do.cau_ly_do(r, "CLB X")
    r = {"outcome": "REJECTED", "reason": "LOTTERY", "n_hoa": 3, "k_cho": 2, "waitlist_pos": 1}
    cau = fa_ly_do.cau_ly_do(r, "CLB X")
    assert "bằng 3 bạn khác ở mọi tiêu chí, tranh 2 chỗ cuối" in cau and "thứ 1 danh sách chờ" in cau
    assert "ưu tiên bù" not in cau                      # D1 hoãn: không hứa điều chưa có
    r = {"outcome": "REMOVED", "reason": "BELOW_PASS", "cut_score": 5}
    assert fa_ly_do.cau_ly_do(r, "CLB X") == "Em chưa đạt mốc 5 điểm của CLB X."
    r = {"outcome": "REMOVED", "reason": "CLUB_CLOSED"}
    assert fa_ly_do.cau_ly_do(r, "CLB X") == (
        "CLB X không đủ thành viên tối thiểu nên tạm không mở kỳ này.")


# ------------------------------------------------------------------- pipeline và xuất tệp


def _dung(api):
    bat_fa(api)
    dung_fa_clb(api, T=(50, "TU_DO", None, None, 3), G=(1, "GIOI_HAN"), S=(1, "TUYEN_CHON", 5))
    ds = ["s1", "s2", "s3", "s4"]
    dung_hs_fa(api, *ds, nv={"s1": ["S", "G", "T"], "s2": ["S", "G", "T"], "s3": ["G", "T"],
                             "s4": ["G", "T"]})
    for s, d in (("s1", 9), ("s2", 7)):
        assert api.submit_test_selection(s, ["S"])["ok"]
    assert api.submit_club_scores("S", [{"student_id": "s1", "score": 9},
                                        {"student_id": "s2", "score": 7}])["ok"]
    assert api.submit_huy_chuong("s3", {"G": 60})["ok"]


def test_pipeline_ghi_fa_ly_do_va_xuat_csv(api, tmp_path):
    _dung(api)
    assert api.run_pipeline(seed=9)["ok"]
    with api._ket_noi_doc() as cur:
        rows = [tuple(r) for r in cur.execute(
            "SELECT run_id, student_id, club_id, outcome, reason FROM fa_ly_do ORDER BY 1,2,3")]
    assert rows and {r[0] for r in rows} == {1}
    kq = {(r[1], r[2]): r[4] for r in rows}
    assert kq[("s2", "S")] == "SCORE"
    # chạy lại: thêm (không ghi đè)
    assert api.run_pipeline(seed=9)["ok"]
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(DISTINCT run_id) FROM fa_ly_do").fetchone()[0] == 2
    ra = api.export_ly_do_csv(str(tmp_path / "ly_do.csv"))
    assert ra["ok"], ra
    with open(ra["data"]["path"], encoding="utf-8-sig", newline="") as f:
        dong = list(csv.DictReader(f))
    assert {"student_id", "buoi", "club", "group", "reason", "sentence", "stb",
            "waitlist_pos"} <= set(dong[0])
    s2 = [d for d in dong if d["student_id"] == "s2"]
    assert any("điểm chuẩn" in d["sentence"] for d in s2)
    for d in dong:                                       # không lẫn mã học sinh khác
        for sid in ("s1", "s2", "s3", "s4"):
            if sid != d["student_id"]:
                assert not re.search(r"\b%s\b" % sid, d["sentence"])
    # chỉ lấy lần chạy MỚI NHẤT (run_id 2)
    assert len([d for d in dong if d["student_id"] == "s1" and d["reason"] == "ACCEPTED"]) == 1


def test_fa_tat_khong_tao_fa_ly_do(api):
    dung_fa_clb(api, T=(5,), G=(2,))
    dung_hs_fa(api, "a", nv={"a": ["G"]})
    import cau_hinh_ws as ch
    ch.ghi_cau_hinh(api.db_path, {"rules": {"wharton": False}})
    assert api.run_pipeline(seed=1)["ok"]
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM fa_ly_do").fetchone()[0] == 0
    assert not api.export_ly_do_csv("")["ok"]


def test_khong_sua_dau_vao():
    bo = _nho({"G": (1, "GIOI_HAN", None), "T": (50, "TU_DO", None)}, {"a": ["G", "T"], "b": ["G", "T"]})
    kq = _chay(bo)
    sao = copy.deepcopy((kq.preferences, kq.ket_qua.assignment))
    fa_daa.ly_do_ket_qua(kq, bo["preferences"], bo["huy_chuong"], bo["fa_clb"])
    assert sao == (kq.preferences, kq.ket_qua.assignment)


def test_fa_s7_xuat_ly_do_chi_lay_lan_chay_moi_nhat(api, tmp_path):
    """FA-S7: lần chạy mới nhất không phải FA -> báo lỗi, không xuất lý do của lần FA cũ."""
    _dung(api)
    assert api.run_pipeline(seed=9)["ok"]                # run 1 (FA)
    assert api.run_pipeline(seed=9)["ok"]                # run 2 (FA)
    import cau_hinh_ws as ch
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": False, "wharton": False}})
    assert api.run_pipeline(seed=9)["ok"]                # run 3 (không FA)
    ra = api.export_ly_do_csv(str(tmp_path / "a.csv"))
    assert not ra["ok"] and ma(ra["errors"]) == ["fa_chua_co_ly_do"]
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True, "wharton": True}})
    assert api.run_pipeline(seed=9)["ok"]                # run 4 (FA)
    ra = api.export_ly_do_csv(str(tmp_path / "b.csv"))
    assert ra["ok"], ra
    assert ra["data"]["run_id"] == 4


def test_fa_s9_chay_hong_sau_khi_ghi_fa_rollback_ca_hai_bang(api, monkeypatch):
    """FA-S9: lỗi ném SAU lần ghi FA cuối (bước khoá điểm) -> fa_nhom, fa_ly_do, match_results,
    run_history giữ nguyên như sau lần chạy trước."""
    _dung(api)
    assert api.run_pipeline(seed=9)["ok"]

    def chup():
        with api._ket_noi_doc() as cur:
            return {b: [tuple(r) for r in cur.execute("SELECT * FROM %s ORDER BY 1, 2, 3" % b)]
                    for b in ("fa_nhom", "fa_ly_do", "match_results", "run_history")}

    truoc = chup()
    assert truoc["fa_ly_do"]

    def hong(*a, **k):
        raise RuntimeError("hỏng giả sau khi ghi FA")

    monkeypatch.setattr(api, "_wharton_dang_khoa", hong)
    ra = api.run_pipeline(seed=9)
    assert not ra["ok"]
    assert any(s["step"] == "rollback" for s in ra["data"]["steps"])
    assert chup() == truoc
