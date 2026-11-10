"""GAP-11 (TH = chưa chạy trên Power Apps / SharePoint): công thức Power Fx của màn đăng ký FA (đường A, đặc tả
T4M_DAC_TA_SUA_APP.md §12, R39–R54) trong bộ dựng `tao_bo_dung_t4m.py --fa-daa`. Bộ dựng mặc định giữ nguyên. Không
chọn D8. Dữ liệu MÔ PHỎNG."""
import os
import sys

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))

import bieu_mau as bm  # noqa: E402
import tao_bo_dung_t4m as tbd  # noqa: E402
from bo_dung_t4m import cong_thuc, cong_thuc_fa  # noqa: E402


@pytest.fixture(scope="module")
def de():
    return bm.doc_de_thi()


@pytest.fixture(scope="module")
def chu(de):
    return cong_thuc_fa.tao_dang_ky_fa(de)


def test_du_cac_yeu_cau_r39_r52(chu):
    assert chu.startswith("TH: chưa chạy")
    assert "Shuffle(" in chu                                                  # R39
    assert "btnLen.Text" in chu and '"▲"' in chu and '"▼"' in chu               # R40
    assert "btnLen.DisplayMode" in chu and "btnXuong.DisplayMode" in chu
    assert "< 7" in chu                                                       # R41
    assert "Min(3," in chu and "btnNop.DisplayMode" in chu                    # R42
    assert "lblThieuTuDo.Visible" in chu                                      # R43
    assert 'TrangThai: {Value: "DRAFT"}' in chu                               # R44
    assert 'TrangThai: {Value: "SUBMITTED"}' in chu and '"Đã khóa"' in chu    # R45, R46
    assert "HC_TuChinh" in chu and 'HC_TuChinh: "Có"' in chu                  # R49
    for k in range(1, 8):                                                     # R44: một Patch ghi đủ NVk, WPk
        assert "NV%d: " % k in chu and "WP%d: " % k in chu
    assert "ddHC.DisplayMode" in chu and '"Tự do"' in chu                     # R50: không đặt vào Tự do
    assert "lblNhacVang.Visible" in chu and '"Tuyển chọn"' in chu             # R52


def test_moi_lan_tu_luu_la_mot_patch_dat_draft(chu):
    """Mọi thao tác (thêm, bỏ, ▲, ▼, đổi huy chương) kết thúc bằng đúng khối tự lưu."""
    luu = cong_thuc_fa.TU_LUU
    for o in ("btnThem.OnSelect", "btnBo.OnSelect", "btnLen.OnSelect", "btnXuong.OnSelect", "ddHC.OnChange"):
        khoi = chu.split(o + " =", 1)[1].split("\n\n", 1)[0]
        assert luu.strip().splitlines()[0].strip() in khoi, o
    assert luu.count("Patch(") == 1 and 'TrangThai: {Value: "DRAFT"}' in luu


def test_loc_tren_nguon_du_lieu_uy_quyen_duoc(chu):
    assert cong_thuc.soat_loc_uy_quyen(chu) == []


def test_bo_dung_fa_co_tep_mac_dinh_khong_co(de, tmp_path):
    tbd.tao_bo_dung(de, str(tmp_path / "fa"), in_ra=lambda *x: None, fa=True)
    tbd.tao_bo_dung(de, str(tmp_path / "thuong"), in_ra=lambda *x: None)
    p = tmp_path / "fa" / "02_app" / cong_thuc_fa.TEN_TEP
    assert p.read_text(encoding="utf-8") == cong_thuc_fa.tao_dang_ky_fa(de)
    assert cong_thuc_fa.TEN_TEP in (tmp_path / "fa" / "README_BK1.md").read_text(encoding="utf-8")
    assert not (tmp_path / "thuong" / "02_app" / cong_thuc_fa.TEN_TEP).exists()
    assert sorted(os.listdir(tmp_path / "thuong" / "02_app")) == sorted(cong_thuc.tao_cong_thuc(de))
    ghi_chu = (tmp_path / "fa" / tbd.TEN_GHI_CHU_FA).read_text(encoding="utf-8")
    assert cong_thuc_fa.TEN_TEP in ghi_chu and "chưa đổi cho FA" not in ghi_chu


def test_cung_de_cung_tung_byte(de):
    assert cong_thuc_fa.tao_dang_ky_fa(de) == cong_thuc_fa.tao_dang_ky_fa(de)
