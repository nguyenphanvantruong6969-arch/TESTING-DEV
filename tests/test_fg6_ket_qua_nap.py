"""FG-6 (STEP0, spec §3), phần API: kết quả nạp tệp Forms có khoá thống nhất, mã không khớp, dòng bị bỏ qua có lý do,
tệp rỗng có mã riêng. Dữ liệu MÔ PHỎNG; mọi việc Forms là TH.

Khoá (spec FG-6): hoc_sinh, dong_moi, dong_trung, ma_khong_khop [mã], dong_bo_qua [{dong, ly_do}], khieu_nai_moi,
khieu_nai_trung, khieu_nai_loi, canh_bao.
"""
import datetime

from _fa import ma
from test_fa_m6b_sau_ket_qua import (  # noqa: F401 (fixture)
    _b64, _buoi, _buoi_cell, _dung, _hang_gop, _hs_kn, _run_at, _tep_api, _tl, de, gio,
)

KHOA = {"hoc_sinh", "dong_moi", "dong_trung", "ma_khong_khop", "dong_bo_qua", "khieu_nai_moi", "khieu_nai_trung",
        "khieu_nai_loi", "canh_bao"}


def test_ket_qua_co_du_khoa_va_dem_dung(api, de, gio):  # noqa: F811
    _dung(api)
    r0 = _run_at(api)
    gio(api, days=1)
    dong = [_tl(de, "s1", 4, 1, "huy_chuong"),
            _hs_kn(de, api, "s2", luc=r0 + datetime.timedelta(hours=3)),      # phản hồi + 1 khiếu nại
            _tl(de, "khong_ai", 3, 1, "chon_clb"),                             # mã lạ
            _tl(de, "s3", 5, 1, "chon_clb", co_sai=1, buoi="", ghi_chu="thiếu buổi")]   # khiếu nại không chọn buổi
    ra = api.nhap_sau_ket_qua_forms(_tep_api(de, api, dong))
    assert ra["ok"], ra
    d = ra["data"]
    assert KHOA <= set(d)
    assert d["hoc_sinh"] == 3 and d["dong_moi"] == 3 and d["dong_trung"] == 0     # s1, s2, s3 có phản hồi mới
    assert d["ma_khong_khop"] == ["khong_ai"]
    assert d["khieu_nai_moi"] == 1 and d["khieu_nai_trung"] == 0 and d["khieu_nai_loi"] == []
    assert [x["dong"] for x in d["dong_bo_qua"]] == [5]                            # dòng 5 của tệp: s3 không chọn buổi
    assert all(isinstance(x["ly_do"], str) and x["ly_do"] for x in d["dong_bo_qua"])


def test_nap_phan_hoi_forms_cung_khoa_thong_nhat(api, de, gio):  # noqa: F811
    from test_fa_m6b_sau_ket_qua import _lc_cu, bm
    _dung(api)
    gio(api, days=1)
    tep = _b64([[bm.cau_ma_hoc_sinh(), bm.CAU_HAI_LONG, bm.CAU_HIEU_LY_DO, bm.CAU_KHO_NHAT],
                ["s1", _lc_cu(bm.CAU_HAI_LONG, "4"), _lc_cu(bm.CAU_HIEU_LY_DO, "1"), _lc_cu(bm.CAU_KHO_NHAT, "huy_chuong")],
                ["s9", _lc_cu(bm.CAU_HAI_LONG, "5"), _lc_cu(bm.CAU_HIEU_LY_DO, "1"), _lc_cu(bm.CAU_KHO_NHAT, "khong_co")]])
    d = api.nhap_phan_hoi_forms(tep)["data"]
    assert {"hoc_sinh", "dong_moi", "dong_trung", "ma_khong_khop", "dong_bo_qua"} <= set(d)
    assert d["dong_moi"] == 1 and d["ma_khong_khop"] == ["s9"] and d["hoc_sinh"] == 1


def test_tep_rong_co_ma_rieng(api, de):  # noqa: F811
    _dung(api)
    for ham in (api.nhap_phan_hoi_forms, api.nhap_sau_ket_qua_forms):
        assert ma(ham(_b64([]))["errors"]) == ["phan_hoi_tep_rong"], ham.__name__
    chi_tieu_de = _b64(_hang_gop(de, [])[:1])                                      # có hàng tiêu đề, không có dòng nào
    assert ma(api.nhap_sau_ket_qua_forms(chi_tieu_de)["errors"]) == ["phan_hoi_tep_rong"]


def test_ma_loi_moi_co_trong_i18n():
    import i18n_errors
    m = i18n_errors.MESSAGES["phan_hoi_tep_rong"]
    assert m["vi"] and m["en"] and m["vi"] != i18n_errors.MESSAGES["phan_hoi_tep_sai"]["vi"]


def test_khieu_nai_buoi_cell_dung_cung_ngay(api, de, gio):  # noqa: F811
    """Khiếu nại hai buổi của cùng một em: đếm theo khiếu nại (2), không theo dòng tệp (1)."""
    _dung(api)
    r0 = _run_at(api)
    gio(api, days=1)
    b = _buoi(api)
    dong = [_tl(de, "s1", co_sai=1, buoi=_buoi_cell(b, "thu_9"), ghi_chu="x", luc=r0 + datetime.timedelta(hours=1))]
    d = api.nhap_sau_ket_qua_forms(_tep_api(de, api, dong))["data"]
    assert d["khieu_nai_moi"] == 1 and d["dong_moi"] == 1
