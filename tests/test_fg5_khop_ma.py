"""FG-5 (STEP0, spec §3): mã học sinh gõ khác hoa/thường hay thừa khoảng trắng. Dữ liệu MÔ PHỎNG; việc Forms là TH."""
import datetime

from _fa import dung_hs_fa
from test_fa_m6b_sau_ket_qua import (  # noqa: F401 (fixture)
    _buoi, _dem, _dung, _hs_kn, _run_at, _tep_api, _tl, de, gio,
)


def test_khop_ma_ham_thuan():
    import fa_sau_xep as sx
    ds = ["s1", "s2", "HS001", "ab", "AB"]
    assert sx.khop_ma_hoc_sinh("s1", ds) == "s1"                     # khớp đúng
    assert sx.khop_ma_hoc_sinh("s2 ", ds) == "s2"                    # thừa khoảng trắng
    assert sx.khop_ma_hoc_sinh("hs001", ds) == "HS001"               # khác hoa/thường, duy nhất
    assert sx.khop_ma_hoc_sinh("Ab", ds) is None                     # hai em ab/AB -> mơ hồ
    assert sx.khop_ma_hoc_sinh("ab", ds) == "ab"                     # khớp đúng luôn thắng
    assert sx.khop_ma_hoc_sinh("AB", ds) == "AB"
    assert sx.khop_ma_hoc_sinh("zzz", ds) is None
    assert sx.khop_ma_hoc_sinh("", ds) is None


def _nap(api, de_, dong):
    ra = api.nhap_sau_ket_qua_forms(_tep_api(de_, api, dong))
    assert ra["ok"], ra
    return ra["data"]


def _ma_da_luu(api):
    with api._ket_noi_doc() as cur:
        return sorted(r[0] for r in cur.execute("SELECT student_id FROM fa_phan_hoi"))


def test_phan_hoi_ma_gom_khoang_trang_va_hoa_thuong_ghi_dung_ma_cu(api, de, gio):  # noqa: F811
    _dung(api)
    gio(api, days=1)
    d = _nap(api, de, [_tl(de, "S1 ", 4, 1, "huy_chuong"), _tl(de, "  s2", 3, 1, "chon_clb")])
    assert _ma_da_luu(api) == ["s1", "s2"]                           # mã lưu KHÔNG đổi, mã gõ được khớp
    assert d["dong_moi"] == 2 and d["ma_khong_khop"] == []


def test_khieu_nai_ma_gom_khoang_trang_van_vao_dung_em(api, de, gio):  # noqa: F811
    _dung(api)
    r0 = _run_at(api)
    gio(api, days=1)
    d = _nap(api, de, [_hs_kn(de, api, "S3 ", luc=r0 + datetime.timedelta(hours=2))])
    assert d["khieu_nai_moi"] == 1 and d["ma_khong_khop"] == []
    assert api.get_khieu_nai()["data"]["khieu_nai"][0]["student_id"] == "s3"


def test_mo_ho_hai_em_ab_AB_bi_bo_qua_va_liet_ke(api, de, gio):  # noqa: F811
    _dung(api)
    dung_hs_fa(api, "ab", "AB")
    gio(api, days=1)
    d = _nap(api, de, [_tl(de, "Ab", 4, 1, "huy_chuong"), _tl(de, "ab", 3, 1, "chon_clb")])
    assert _ma_da_luu(api) == ["ab"]                                 # "ab" khớp đúng; "Ab" mơ hồ -> bỏ
    assert d["ma_khong_khop"] == ["Ab"]
    assert _dem(api, "fa_phan_hoi") == 1


def test_ma_la_duoc_liet_ke_toi_da_20(api, de, gio):  # noqa: F811
    _dung(api)
    gio(api, days=1)
    d = _nap(api, de, [_tl(de, "la%02d" % i, 4, 1, "huy_chuong") for i in range(25)])
    assert len(d["ma_khong_khop"]) == 20 and d["ma_khong_khop"][0] == "la00"
    assert _dem(api, "fa_phan_hoi") == 0


def test_nhap_phan_hoi_forms_cung_dung_khop_mem(api, gio):  # noqa: F811
    """Đường nạp tệp 3 câu cũ (`nhap_phan_hoi_forms`) cũng khớp mềm và trả danh sách mã không khớp."""
    from test_fa_m6b_sau_ket_qua import _b64, _lc_cu, bm
    _dung(api)
    gio(api, days=1)

    def hang(ma_):
        return [ma_, _lc_cu(bm.CAU_HAI_LONG, "4"), _lc_cu(bm.CAU_HIEU_LY_DO, "1"), _lc_cu(bm.CAU_KHO_NHAT, "huy_chuong")]
    tep = _b64([[bm.cau_ma_hoc_sinh(), bm.CAU_HAI_LONG, bm.CAU_HIEU_LY_DO, bm.CAU_KHO_NHAT],
                hang("S1 "), hang("khong_co_em_nay")])
    ra = api.nhap_phan_hoi_forms(tep)
    assert ra["ok"], ra
    assert ra["data"]["ma_khong_khop"] == ["khong_co_em_nay"]
    assert _ma_da_luu(api) == ["s1"]
