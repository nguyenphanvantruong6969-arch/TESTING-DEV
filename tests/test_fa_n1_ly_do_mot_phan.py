"""FA-N1: lý do theo TỪNG buổi sau khi chạy lại một phần (`chi_buoi`). Dữ liệu là dữ liệu MÔ PHỎNG."""

import csv

import cau_hinh_ws as ch
from _fa import bat_fa, dung_fa_clb, dung_hs_fa, ma


def _dung_hai_buoi(api):
    bat_fa(api)
    dung_fa_clb(api, A=(3, "GIOI_HAN", None, None, None, "thu_2"),
                B=(3, "GIOI_HAN", None, None, None, "thu_3"),
                FA=(9, "TU_DO", None, None, None, "thu_2"),
                FB=(9, "TU_DO", None, None, None, "thu_3"))
    ds = ["s1", "s2", "s3", "s4"]
    dung_hs_fa(api, *ds, nv={s: ["A", "FA", "B", "FB"] for s in ds})


def _doc(api, tmp_path, ten):
    ra = api.export_ly_do_csv(str(tmp_path / ten))
    assert ra["ok"], ra
    with open(ra["data"]["path"], encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def test_chay_lai_mot_buoi_van_giu_ly_do_cac_buoi_khac(api, tmp_path):
    _dung_hai_buoi(api)
    assert api.run_pipeline(seed=3)["ok"]                      # run 1: hai buổi
    ban_dau = _doc(api, tmp_path, "a.csv")
    assert {d["buoi"] for d in ban_dau} == {"thu_2", "thu_3"}
    assert api.run_pipeline(seed=3, chi_buoi=["thu_2"])["ok"]  # run 2: chỉ thu_2
    sau = _doc(api, tmp_path, "b.csv")
    assert {d["buoi"] for d in sau} == {"thu_2", "thu_3"}
    assert len([d for d in sau if d["buoi"] == "thu_3"]) == \
        len([d for d in ban_dau if d["buoi"] == "thu_3"])
    cau = api.get_ly_do_ket_qua()["data"]["cau"]
    assert all(set(v) == {"thu_2", "thu_3"} for v in cau.values())


def test_buoi_chay_lai_bang_chay_khong_fa_khong_con_ly_do_va_co_canh_bao(api, tmp_path):
    _dung_hai_buoi(api)
    assert api.run_pipeline(seed=3)["ok"]                      # run 1: FA, hai buổi
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": False, "wharton": False}})
    assert api.run_pipeline(seed=3, chi_buoi=["thu_2"])["ok"]  # run 2: không FA, chỉ thu_2
    ra = api.export_ly_do_csv(str(tmp_path / "c.csv"))
    assert ra["ok"], ra
    with open(ra["data"]["path"], encoding="utf-8-sig", newline="") as f:
        dong = list(csv.DictReader(f))
    assert {d["buoi"] for d in dong} == {"thu_3"}              # thu_2 không còn lý do cũ
    assert ra["data"].get("canh_bao"), ra


def test_khong_ngay_nao_co_ly_do_thi_van_bao_loi(api, tmp_path):
    _dung_hai_buoi(api)
    assert api.run_pipeline(seed=3)["ok"]
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": False, "wharton": False}})
    assert api.run_pipeline(seed=3)["ok"]                      # chạy đủ, không FA
    ra = api.export_ly_do_csv(str(tmp_path / "d.csv"))
    assert not ra["ok"] and ma(ra["errors"]) == ["fa_chua_co_ly_do"]


def test_ly_do_sap_theo_thu_tu_ngay_chu_nhat_cuoi_tuan(api, tmp_path):
    """FA-O1: `chu_nhat` đứng SAU `thu_2` (như THU_TU_BUOI), cả ở tệp xuất lẫn cột "Lý do"."""
    bat_fa(api)
    dung_fa_clb(api, A=(3, "GIOI_HAN", None, None, None, "chu_nhat"),
                B=(3, "GIOI_HAN", None, None, None, "thu_2"),
                FA=(9, "TU_DO", None, None, None, "chu_nhat"),
                FB=(9, "TU_DO", None, None, None, "thu_2"))
    dung_hs_fa(api, "s1", "s2", nv={s: ["A", "FA", "B", "FB"] for s in ("s1", "s2")})
    assert api.run_pipeline(seed=3)["ok"]
    for ten in ("a.csv", "b.csv"):                              # cả khi chạy lại một phần
        dong = _doc(api, tmp_path, ten)
        for sid in ("s1", "s2"):
            ngay = [d["buoi"] for d in dong if d["student_id"] == sid]
            assert ngay and ngay == sorted(ngay, key=["thu_2", "chu_nhat"].index), (sid, ngay)
        assert api.run_pipeline(seed=3, chi_buoi=["chu_nhat"])["ok"]
    cau = api.get_ly_do_ket_qua()["data"]["cau"]
    assert all(list(v) == ["thu_2", "chu_nhat"] for v in cau.values())
