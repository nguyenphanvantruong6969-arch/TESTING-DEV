"""SG-5 (H3): câu huy chương học sinh hiểu được. Dữ liệu MÔ PHỎNG.

* Dòng mô tả dưới phần huy chương nói đúng luật thật của `fa_daa` (vàng/bạc/đồng theo thứ tự nguyện vọng, CLB Tự do
  không nhận, điểm thi xét trước, không đổi thì hệ thống tự đặt).
* Câu "đổi chỗ bạc và đồng" chỉ có ở ngày có >= 3 CLB đủ điều kiện nhận huy chương (không Tự do).
* Bộ nhập tệp Forms không báo sai khi câu đó vắng / vô nghĩa; tệp cũ CÓ câu đó ở ngày 2 CLB vẫn đọc được.
"""
import copy
import os
import sys

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))
sys.path.insert(0, GOC)

import bieu_mau as bm  # noqa: E402
import chuyen_forms_sang_phan_mem as cv  # noqa: E402


def _de(tu_do):
    """de_thi.json mẫu: các CLB trong `tu_do` có loai TU_DO, còn lại GIOI_HAN."""
    de = copy.deepcopy(bm.doc_de_thi())
    for c in de["cau_lac_bo"]:
        c["loai"] = "TU_DO" if c["club_id"] in tu_do else "GIOI_HAN"
    return de


def _ma_cau(de, ma_buoi):
    return [bm.ma_cua_cau(td) for _, cs in bm.cac_phan_fa(de, ma_buoi) for td, *_ in cs]


def _lc(de, club_id):
    return bm.lua_chon_clb(next(c for c in de["cau_lac_bo"] if c["club_id"] == club_id))


def test_ngay_hai_clb_du_dieu_kien_khong_co_cau_doi_bac_dong():
    de = _de({"clb_nhiepanh"})                                  # thu_2: covua, vanhoc + 1 Tự do
    ma = _ma_cau(de, "thu_2")
    assert "thu_2-vang" in ma and "thu_2-doi" not in ma
    assert "thu_2-doi" not in [bm.ma_cua_cau(td) for _, cs in bm.cac_phan_fa_gop(de) for td, *_ in cs]
    assert bm.dem_cau_fa_gop(de) == sum(len(c) for _, c in bm.cac_phan_fa_gop(de))


def test_ngay_ba_clb_du_dieu_kien_van_co_cau_doi_bac_dong():
    de = _de(set())
    assert "thu_2-doi" in _ma_cau(de, "thu_2")
    assert "thu_2-doi" in [bm.ma_cua_cau(td) for _, cs in bm.cac_phan_fa_gop(de) for td, *_ in cs]


def test_dong_mo_ta_huy_chuong_dung_luat_that():
    de = _de({"clb_nhiepanh"})
    vang = next(td for _, cs in bm.cac_phan_fa(de, "thu_2") for td, *_ in cs if td.startswith("[thu_2-vang]"))
    mo_ta = bm.MO_TA_HUY_CHUONG
    assert mo_ta in vang
    for tu in ("vàng", "bạc", "đồng", "nguyện vọng 1", "nguyện vọng 2", "nguyện vọng 3", "Tự do", "điểm thi",
               "bốc thăm", "tự đặt"):
        assert tu in mo_ta, tu
    for ma_noi_bo in ("SG-", "FG-", "FA-", "TUYEN_CHON", "GIOI_HAN", "wharton", "STB", "[", "_"):
        assert ma_noi_bo not in mo_ta, ma_noi_bo


def _tep(de, ma_buoi, cau_hoi, hang):
    tieu = ["Email", "Name"] + [td for td in cau_hoi]
    rows = []
    for k, r in enumerate(hang):
        o = {"Email": "s%d@x.vn" % k, "Name": "n", bm.cau_ma_hoc_sinh(): "HS%d" % k, bm.cau_ho_ten(): "n"}
        o.update(r)
        rows.append([o.get(h, "") for h in tieu])
    return tieu, rows


def _hang_hai_clb(de, doi):
    return {bm.cau_nguyen_vong_fa(de, "thu_2", 1): _lc(de, "clb_covua"),
            bm.cau_nguyen_vong_fa(de, "thu_2", 2): _lc(de, "clb_vanhoc"),
            bm.cau_nguyen_vong_fa(de, "thu_2", 3): _lc(de, "clb_nhiepanh"),
            bm.cau_vang_fa(de, "thu_2"): bm.GIU_MAC_DINH_VANG, bm.cau_doi_fa(de, "thu_2"): doi}


TU_DO = {"clb_nhiepanh"}


def test_tep_cu_co_cau_doi_o_ngay_hai_clb_khong_canh_bao_gia():
    """Tệp cũ: học sinh trả lời "Có" ở câu đổi dù ngày chỉ có 2 CLB nhận huy chương -> không còn cảnh báo giả."""
    de = _de(TU_DO)
    cau = [bm.cau_ma_hoc_sinh(), bm.cau_ho_ten()] + [bm.cau_nguyen_vong_fa(de, "thu_2", k) for k in (1, 2, 3)] \
        + [bm.cau_vang_fa(de, "thu_2"), bm.cau_doi_fa(de, "thu_2")]
    tieu, rows = _tep(de, "thu_2", cau, [_hang_hai_clb(de, bm.DOI_CO)] * 3)
    assert len({tuple(r) for r in rows}) == 3                 # ba email khác nhau, mỗi em Có ở câu đổi
    ds, cb = cv.doc_dang_ky_fa_forms(de, tieu, rows, TU_DO)
    assert len(cb) == 0, cb
    assert ds["s0@x.vn"]["wp"]["thu_2"] == {"clb_covua": 60, "clb_vanhoc": 30, "clb_nhiepanh": None}


def test_tep_moi_khong_co_cau_doi_khong_canh_bao():
    de = _de(TU_DO)
    cau = [bm.cau_ma_hoc_sinh(), bm.cau_ho_ten()] + [bm.cau_nguyen_vong_fa(de, "thu_2", k) for k in (1, 2, 3)] \
        + [bm.cau_vang_fa(de, "thu_2")]
    tieu, rows = _tep(de, "thu_2", cau, [_hang_hai_clb(de, "")] * 4)
    ds, cb = cv.doc_dang_ky_fa_forms(de, tieu, rows, TU_DO)
    assert len(cb) == 0 and len(ds) == 4


def test_tep_cu_ngay_ba_clb_van_doi_duoc():
    de = _de(set())
    cau = [bm.cau_ma_hoc_sinh(), bm.cau_ho_ten()] + [bm.cau_nguyen_vong_fa(de, "thu_2", k) for k in (1, 2, 3)] \
        + [bm.cau_vang_fa(de, "thu_2"), bm.cau_doi_fa(de, "thu_2")]
    tieu, rows = _tep(de, "thu_2", cau, [_hang_hai_clb(de, bm.DOI_CO)])
    ds, cb = cv.doc_dang_ky_fa_forms(de, tieu, rows, set())
    assert ds["s0@x.vn"]["wp"]["thu_2"] == {"clb_covua": 60, "clb_nhiepanh": 30, "clb_vanhoc": 10}
    assert not cb
