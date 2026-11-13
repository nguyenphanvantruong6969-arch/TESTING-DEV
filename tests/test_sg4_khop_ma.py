"""SG-4 (M3): khiếu nại gõ tay dùng cùng luật khớp mã với đường Forms (`fa_sau_xep.khop_ma_hoc_sinh`);
hai nguyên nhân từ chối có hai mã lỗi riêng. Dữ liệu MÔ PHỎNG."""
from _fa import dung_fa_clb, dung_hs_fa, ma
from test_fa_gap3_khieu_nai import _bat, _buoi, gio  # noqa: F401 (fixture)


def _dem_kn(api):
    with api._ket_noi_doc() as cur:
        return cur.execute("SELECT COUNT(*) FROM fa_khieu_nai").fetchone()[0]


def _dung(api, *ids):
    _bat(api)
    dung_fa_clb(api, G=(2, "GIOI_HAN"), T=(9, "TU_DO"))
    dung_hs_fa(api, *ids, nv={s: ["G", "T"] for s in ids})
    assert api.run_pipeline(seed=5)["ok"]


def test_ma_go_tay_khac_hoa_thuong_va_khoang_trang_duoc_nhan(api, gio):  # noqa: F811
    _dung(api, "HS010", "HS011", "HS012", "HS013")
    gio(api, days=1)
    ra = api.gui_khieu_nai("hs010 ", _buoi(api), "Điểm sai")
    assert ra["ok"], ra
    with api._ket_noi_doc() as cur:                       # mã LƯU không bị đổi
        assert [r[0] for r in cur.execute("SELECT student_id FROM fa_khieu_nai")] == ["HS010"]


def test_ma_mo_ho_bi_tu_choi_nhu_duong_forms(api, gio):  # noqa: F811
    _dung(api, "HS010", "hs010", "HS012", "HS013")        # "hs010 " khớp mềm với CẢ HAI -> mơ hồ
    gio(api, days=1)
    ra = api.gui_khieu_nai("Hs010", _buoi(api), "x")
    assert ma(ra["errors"]) == ["khieu_nai_hs_khong_co"]     # cùng cách Forms: coi như không khớp
    assert _dem_kn(api) == 0
    assert api.gui_khieu_nai("hs010", _buoi(api), "x")["ok"]      # khớp đúng vẫn thắng


def test_hai_nguyen_nhan_hai_ma_va_hai_thong_bao(api, gio):  # noqa: F811
    _dung(api, "s1", "s2", "s3", "s4")
    dung_hs_fa(api, "s5", nv={"s5": ["G", "T"]})          # có trong CSDL, chưa có kết quả
    gio(api, days=1)
    b = _buoi(api)
    la = api.gui_khieu_nai("s9", b, "x")["errors"]
    chua = api.gui_khieu_nai("s5", b, "x")["errors"]
    sai_buoi = api.gui_khieu_nai("s1", "khong_co", "x")["errors"]
    assert ma(la) == ["khieu_nai_hs_khong_co"]
    assert ma(chua) == ["khieu_nai_chua_co_ket_qua"] and ma(sai_buoi) == ["khieu_nai_chua_co_ket_qua"]
    from i18n_errors import format_message as dich_loi
    vi = {dich_loi(e["code"], e["params"], "vi") for e in (la + chua)}
    en = {dich_loi(e["code"], e["params"], "en") for e in (la + chua)}
    assert len(vi) == 2 and len(en) == 2
    assert "s9" in dich_loi(la[0]["code"], la[0]["params"], "vi")
    assert "s5" in dich_loi(chua[0]["code"], chua[0]["params"], "vi")


def test_ma_moi_co_trong_i18n_vi_en_va_js():
    import i18n_errors as ie
    for c in ("khieu_nai_hs_khong_co", "khieu_nai_chua_co_ket_qua"):
        assert ie.MESSAGES[c]["vi"] and ie.MESSAGES[c]["en"]
    assert "khieu_nai_khong_hop_le" in ie.MESSAGES            # mã cũ còn cho đường Forms
