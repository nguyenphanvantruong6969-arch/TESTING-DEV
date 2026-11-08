"""FA-M3 (một phần, Truong duyệt 08/11/2026): đặt huy chương trên đường B (chỉ Microsoft Forms).

Huy chương mặc định theo thứ tự nguyện vọng (ngoại lệ bất biến 2 trong CLAUDE.md, quyết định D2), cộng hai câu
tuỳ chọn để học sinh đổi được MỌI cách đặt (D12):
  * "Đặt huy chương vàng vào CLB khác NV1? (để trống = giữ mặc định)" -> `vang`
  * "Đổi chỗ huy chương bạc và đồng? (để trống = giữ mặc định)"         -> `doi_bac_dong` ("Có" / trống)
Vàng 60, bạc 30, đồng 10; CLB Tự do không nhận huy chương. Dữ liệu MÔ PHỎNG.
"""
import itertools
import os
import sys

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))

import chuyen_forms_sang_phan_mem as cv  # noqa: E402

DIEM = (60, 30, 10)


def _dat(nv, tu_do=(), vang="", doi=""):
    return cv.dat_huy_chuong_duong_b(nv, set(tu_do), vang, doi)


@pytest.mark.parametrize("cach_dat", list(itertools.permutations(["A", "B", "C"])))
def test_ca_6_cach_dat_deu_dat_duoc(cach_dat):
    """Với 3 CLB không Tự do, mọi hoán vị (vàng, bạc, đồng) đều đạt được bằng hai câu tuỳ chọn."""
    nv = ["A", "B", "C"]
    vang, bac, dong = cach_dat
    o_vang = "" if vang == nv[0] else vang
    con_lai = [c for c in nv if c != vang]
    o_doi = "" if [bac, dong] == con_lai else "Có"
    huy_chuong, canh_bao = _dat(nv, vang=o_vang, doi=o_doi)
    assert huy_chuong == {vang: 60, bac: 30, dong: 10}
    assert canh_bao == []


def test_sau_cach_dat_khac_nhau_tung_doi_mot():
    """Bốn tổ hợp câu trả lời × ba lựa chọn vàng sinh ra đúng 6 cách đặt khác nhau (không trùng, không thiếu)."""
    nv = ["A", "B", "C"]
    thay = set()
    for vang in ("", "B", "C"):
        for doi in ("", "Có"):
            hc, _ = _dat(nv, vang=vang, doi=doi)
            thay.add(tuple(sorted(hc.items())))
    assert len(thay) == 6


def test_vang_ghi_ro_nv1_giong_de_trong():
    assert _dat(["A", "B", "C"], vang="A") == _dat(["A", "B", "C"])


def test_bo_qua_clb_tu_do_khi_dat_mac_dinh():
    hc, canh_bao = _dat(["F", "A", "B"], tu_do={"F"})
    assert hc == {"A": 60, "B": 30}
    assert canh_bao == []


def test_vang_vao_clb_tu_do_hay_ngoai_danh_sach_thi_giu_mac_dinh_va_bao():
    for vang in ("F", "X"):
        hc, canh_bao = _dat(["F", "A", "B"], tu_do={"F"}, vang=vang)
        assert hc == {"A": 60, "B": 30}
        assert len(canh_bao) == 1 and vang in canh_bao[0]


def test_doi_khi_chi_con_mot_clb_thi_giu_va_bao():
    hc, canh_bao = _dat(["F", "A", "B"], tu_do={"F"}, doi="Có")
    assert hc == {"A": 60, "B": 30}
    assert len(canh_bao) == 1


def test_doi_gia_tri_la_thi_giu_mac_dinh_va_bao():
    hc, canh_bao = _dat(["A", "B", "C"], doi="có lẽ")
    assert hc == {"A": 60, "B": 30, "C": 10}
    assert len(canh_bao) == 1


@pytest.mark.parametrize("doi", ["có", " Có ", "CÓ", "co"])
def test_doi_chap_nhan_hoa_thuong_va_khoang_trang(doi):
    hc, _ = _dat(["A", "B", "C"], doi=doi)
    assert hc == {"A": 60, "C": 30, "B": 10}


def test_nguyen_vong_trung_chi_tinh_mot_lan():
    hc, _ = _dat(["A", "A", "B"])
    assert hc == {"A": 60, "B": 30}


def test_khong_co_clb_nao_nhan_huy_chuong():
    assert _dat(["F"], tu_do={"F"}) == ({}, [])


def test_moi_clb_toi_da_mot_huy_chuong_va_moi_muc_mot_lan():
    for vang in ("", "A", "B", "C"):
        for doi in ("", "Có"):
            hc, _ = _dat(["A", "B", "C"], vang=vang, doi=doi)
            assert sorted(hc.values(), reverse=True) == list(DIEM)
