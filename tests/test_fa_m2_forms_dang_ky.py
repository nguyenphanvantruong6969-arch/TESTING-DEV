"""FA-M2 (TH = chưa thử trên Microsoft thật): biểu mẫu đăng ký đường B, một biểu mẫu mỗi ngày (`--fa-daa`).

Quyết định D12: không câu Ranking; ba câu chọn riêng bắt buộc "Nguyện vọng 1/2/3"; hai câu huy chương tuỳ chọn.
Dữ liệu MÔ PHỎNG. Không đổi hành vi khi không có cờ.
"""
import copy
import filecmp
import os
import sys

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))

import bieu_mau as bm  # noqa: E402
import tao_mau_forms as tmf  # noqa: E402


@pytest.fixture
def de():
    return bm.doc_de_thi()


def _cau(phan):
    return [c for _, cs in phan for c in cs]


def test_moi_ngay_ba_cau_nguyen_vong_bat_buoc_khong_ranking(de):
    phan = bm.cac_phan_fa(de, "thu_2")
    cau = _cau(phan)
    assert all(loai != "ranking" for _, loai, _, _ in cau)
    nv = [c for c in cau if "Nguyện vọng" in c[0]]
    assert [bm.ma_cua_cau(c[0]) for c in nv] == ["thu_2-nv1", "thu_2-nv2", "thu_2-nv3"]
    ds = [bm.lua_chon_clb(c) for c in bm.clb_cua_buoi(de, "thu_2")]
    for _, loai, lua_chon, bat_buoc in nv:
        assert loai == "choice" and bat_buoc is True and lua_chon == ds


def test_ngay_it_hon_ba_clb_chi_hoi_bang_so_clb(de):
    de2 = copy.deepcopy(de)
    de2["cau_lac_bo"] = [c for c in de2["cau_lac_bo"] if c["buoi"] != "thu_2"] + \
        [c for c in de["cau_lac_bo"] if c["buoi"] == "thu_2"][:2]
    nv = [c for c in _cau(bm.cac_phan_fa(de2, "thu_2")) if "Nguyện vọng" in c[0]]
    assert len(nv) == 2


def test_co_thong_tin_hoc_sinh_va_hai_cau_huy_chuong_tuy_chon(de):
    cau = _cau(bm.cac_phan_fa(de, "thu_3"))
    ma = [bm.ma_cua_cau(c[0]) for c in cau]
    assert ma[:2] == ["student_id", "name"]
    assert ma[-2:] == ["thu_3-vang", "thu_3-doi"]
    vang, doi = cau[-2], cau[-1]
    assert vang[3] is False and doi[3] is False                       # tuỳ chọn
    assert bm.GIU_MAC_DINH_VANG in vang[2]
    assert doi[2] == [bm.DOI_KHONG, bm.DOI_CO]
    assert "để trống = giữ mặc định" not in vang[0]                   # Forms không bỏ chọn được: có lựa chọn "giữ mặc định"
    assert "Đặt huy chương vàng vào CLB khác NV1?" in vang[0]
    assert "Đổi chỗ huy chương bạc và đồng?" in doi[0]


def test_cau_vang_bo_clb_tu_do_khi_de_thi_co_loai(de):
    de2 = copy.deepcopy(de)
    for c in de2["cau_lac_bo"]:
        c["loai"] = "TU_DO" if c["club_id"] == "clb_covua" else "GIOI_HAN"
    vang = _cau(bm.cac_phan_fa(de2, "thu_2"))[-2]
    assert not any("clb_covua" in x for x in vang[2])
    assert any("clb_vanhoc" in x for x in vang[2])


def test_mot_cau_nguyen_vong_khong_co_trong_che_do_cu(de):
    """Chế độ mặc định không đổi: vẫn Ranking, không câu nv/vang/doi."""
    cau = _cau(bm.cac_phan(de))
    assert any(loai == "ranking" for _, loai, _, _ in cau)
    assert not any("-nv" in (bm.ma_cua_cau(c[0]) or "") for c in cau)


def test_the_cau_khong_trung_ma_clb(de):
    cau = _cau(bm.cac_phan_fa(de, "thu_2"))
    ma = [bm.ma_cua_cau(c[0]) for c in cau]
    assert len(ma) == len(set(ma))
    assert not set(ma) & {c["club_id"] for c in de["cau_lac_bo"]}


def test_sinh_ghi_huong_dan_va_mot_docx_moi_ngay(de, tmp_path):
    ra = tmf.sinh_dang_ky(de, str(tmp_path))
    ten = sorted(os.path.basename(p) for p in ra)
    assert tmf.TEN_CAI_DAT_DANG_KY in ten
    assert sum(t.startswith(tmf.TIEN_TO_DOCX_DANG_KY) for t in ten) == len(de["buoi"])
    md = (tmp_path / tmf.TEN_CAI_DAT_DANG_KY).read_text(encoding="utf-8")
    assert "TH" in md and "CHƯA thử" in md
    assert bm.CAU_HUONG_DAN_DANG_KY in md
    assert "Shuffle options" in md and "Shuffle questions" in md
    assert "Ranking" in md                                         # nói rõ KHÔNG dùng Ranking
    assert "Shuffle questions | **TẮT**" in md                      # xáo câu làm hỏng rẽ nhánh/thứ tự NV1..3
    assert "đề xuất" not in md.lower() and "khuyến nghị" not in md.lower()      # D8 còn mở


def test_sinh_hai_lan_ra_tep_giong_het(de, tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    tmf.sinh_dang_ky(de, str(a))
    tmf.sinh_dang_ky(de, str(b))
    ten = sorted(os.listdir(a))
    assert ten == sorted(os.listdir(b))
    assert filecmp.cmpfiles(a, b, ten, shallow=False)[0] == ten


def test_main_fa_daa_va_xung_khac_che_do_khac(tmp_path):
    assert tmf.main(["--fa-daa", "--ra", str(tmp_path)]) == 0
    assert (tmp_path / tmf.TEN_CAI_DAT_DANG_KY).exists()
    with pytest.raises(SystemExit):
        tmf.main(["--fa-daa", "--chi-thi", "--ra", str(tmp_path)])
    with pytest.raises(SystemExit):
        tmf.main(["--fa-daa", "--moi-clb", "--ra", str(tmp_path)])


def test_ngay_nhieu_hon_ba_clb_van_chi_ba_cau_nguyen_vong(de):
    de2 = copy.deepcopy(de)
    mau = copy.deepcopy([c for c in de["cau_lac_bo"] if c["buoi"] == "thu_2"][0])
    mau.update(club_id="clb_them", name="CLB Thêm", de_thi=[])
    de2["cau_lac_bo"].append(mau)
    assert len(bm.clb_cua_buoi(de2, "thu_2")) == 4
    nv = [c for c in _cau(bm.cac_phan_fa(de2, "thu_2")) if "Nguyện vọng" in c[0]]
    assert len(nv) == 3


# ------------------------------------------- FA-S6: đọc Loại từ Sổ nhập CLB (FA-M1)
def _so_nhap_clb(de, tmp_path, tu_do):
    import so_nhap
    clubs = [{"club_id": c["club_id"], "name": c["name"], "capacity": 40, "reserve_capacity": 0, "reserve_group": "",
              "buoi": c["buoi"], "loai": so_nhap.TU_DO if c["club_id"] == tu_do else so_nhap.GIOI_HAN}
             for c in de["cau_lac_bo"]]
    p = str(tmp_path / "clb.xlsx")
    so_nhap.ghi_so_nhap(p, clubs=clubs)
    return p


def test_fa_s6_so_nhap_clb_bo_clb_tu_do_khoi_cau_vang(de, tmp_path):
    tu_do = next(c for c in de["cau_lac_bo"])
    sn = _so_nhap_clb(de, tmp_path, tu_do["club_id"])
    de2, _ = tmf.de_theo_so_nhap_clb(de, sn)
    assert "loai" not in tu_do                                       # không sửa de gốc
    vang = _cau(bm.cac_phan_fa(de2, tu_do["buoi"]))[-2]
    assert not any(tu_do["club_id"] in x for x in vang[2])
    assert tmf.main(["--fa-daa", "--so-nhap-clb", sn, "--ra", str(tmp_path / "ra")]) == 0
    md = (tmp_path / "ra" / tmf.TEN_CAI_DAT_DANG_KY).read_text(encoding="utf-8")
    assert "chưa ghi `loai`" not in md and "Sổ nhập CLB" in md


def test_fa_s6_so_nhap_clb_chi_dung_cung_fa_daa(tmp_path):
    with pytest.raises(SystemExit):
        tmf.main(["--so-nhap-clb", "x.xlsx", "--ra", str(tmp_path)])
