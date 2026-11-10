"""GAP-7 (V§10): gợi ý chỉ tiêu kỳ sau = nhu cầu NV1 kỳ trước, chặn trên bởi giới hạn giáo viên khai; giáo viên chỉ
được tăng từ gợi ý. Không có dữ liệu học sinh trong tệp xuất. Dữ liệu là dữ liệu MÔ PHỎNG."""
import csv
import io

import fa_daa
from _fa import bat_fa, dung_fa_clb, dung_hs_fa, ma


def test_goi_y_thuan_chan_tren_khong_chan_va_nv1_0():
    rows = [{"buoi": "b1", "club_id": "G", "nv1": 3}, {"buoi": "b1", "club_id": "T", "nv1": 4},
            {"buoi": "b1", "club_id": "S", "nv1": 0}, {"buoi": "b1", "club_id": "H", "nv1": 2}]
    ra = {r["club_id"]: r for r in fa_daa.goi_y_chi_tieu(rows, {"G": 2, "S": 5, "H": 9})}
    assert (ra["G"]["gioi_han"], ra["G"]["goi_y_ky_sau"], ra["G"]["ghi_chu"]) == (2, 2, "chan_boi_gioi_han")
    assert (ra["T"]["gioi_han"], ra["T"]["goi_y_ky_sau"], ra["T"]["ghi_chu"]) == (None, 4, "khong_gioi_han")
    assert (ra["S"]["goi_y_ky_sau"], ra["S"]["ghi_chu"]) == (0, "khong_co_nv1")
    assert (ra["H"]["goi_y_ky_sau"], ra["H"]["ghi_chu"]) == (2, "")
    assert rows[0] == {"buoi": "b1", "club_id": "G", "nv1": 3}          # không sửa đầu vào


def test_kiem_tang_tu_goi_y():
    v = fa_daa.kiem_tang_tu_goi_y({"G": 2, "T": 4, "S": 0}, {"G": 1, "T": 6})
    assert v == [{"club_id": "G", "loi": "GIAM_SUC_CHUA", "truoc": 2, "sau": 1}]


def _dung(api):
    bat_fa(api)
    dung_fa_clb(api, G=(3, "GIOI_HAN"), T=(50, "TU_DO"))
    dung_hs_fa(api, "s1", "s2", "s3", "s4", nv={"s1": ["G", "T"], "s2": ["G", "T"], "s3": ["G", "T"],
                                                "s4": ["T", "G"]})


def _doc(p):
    with io.open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def test_xuat_goi_y_cot_va_gia_tri(api, tmp_path):
    _dung(api)
    assert api.luu_gioi_han_gv("G", 2)["ok"]
    kq = api.export_goi_y_chi_tieu(str(tmp_path / "goi_y.csv"))
    assert kq["ok"], kq
    hang = _doc(kq["data"]["path"])
    assert hang[0] == ["buoi", "club_id", "ten", "loai", "capacity", "nv1", "gioi_han", "goi_y_ky_sau", "ghi_chu"]
    d = {r[1]: r for r in hang[1:]}
    assert d["G"][4:] == ["3", "3", "2", "2", "chan_boi_gioi_han"]
    assert d["T"][4:] == ["50", "1", "", "1", "khong_gioi_han"]
    van = open(kq["data"]["path"], encoding="utf-8-sig").read()
    assert not any(s in van for s in ("s1", "s2", "s3", "s4"))
    assert api.luu_gioi_han_gv("G", None)["ok"]                         # xoá giới hạn
    d2 = {r[1]: r for r in _doc(api.export_goi_y_chi_tieu(str(tmp_path / "b.csv"))["data"]["path"])[1:]}
    assert d2["G"][6:] == ["", "3", "khong_gioi_han"]


def test_bang_nhu_cau_them_cot_cuoi(api, tmp_path):
    _dung(api)
    assert api.luu_gioi_han_gv("G", 2)["ok"]
    hang = _doc(api.export_bang_nhu_cau(str(tmp_path / "n.csv"))["data"]["path"])
    assert hang[0] == ["buoi", "club_id", "ten", "loai", "capacity", "nv1", "so_ghi", "so_dat_san", "so_giu_cho",
                       "goi_y_ky_sau"]
    d = {r[1]: r for r in hang[1:]}
    assert d["G"][5:] == ["3", "4", "", "0", "2"]


def test_kiem_chi_tieu_ky_sau(api):
    _dung(api)
    assert api.luu_gioi_han_gv("G", 2)["ok"]
    kq = api.kiem_chi_tieu_ky_sau({"G": 1, "T": 5})
    assert kq["ok"], kq
    assert kq["data"]["vi_pham"] == [{"club_id": "G", "loi": "GIAM_SUC_CHUA", "truoc": 2, "sau": 1}]
    assert api.kiem_chi_tieu_ky_sau({"G": 3, "T": 1})["data"]["vi_pham"] == []
    assert ma(api.kiem_chi_tieu_ky_sau({"G": "3"})["errors"]) == ["gioi_han_gv_sai"]


def test_fa_tat_va_gioi_han_sai_khong_ghi(api, tmp_path):
    dung_fa_clb(api, G=(3, "GIOI_HAN"))
    bat_fa(api, False)
    assert ma(api.luu_gioi_han_gv("G", 2)["errors"]) == ["fa_chua_bat"]
    assert ma(api.export_goi_y_chi_tieu(str(tmp_path / "x.csv"))["errors"]) == ["fa_chua_bat"]
    assert ma(api.kiem_chi_tieu_ky_sau({"G": 3})["errors"]) == ["fa_chua_bat"]
    bat_fa(api)
    for sai in (0, -1, "2", True, 2.5):
        assert ma(api.luu_gioi_han_gv("G", sai)["errors"]) == ["gioi_han_gv_sai"], sai
    assert ma(api.luu_gioi_han_gv("KHONG", 2)["errors"]) == ["club_not_found"]
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM fa_gioi_han_gv").fetchone()[0] == 0


def test_csdl_cu_nhan_bang_gioi_han_khi_mo(tmp_path):
    import sqlite3

    from rbda_priority_pipeline import di_tru_schema, init_db
    db = str(tmp_path / "cu.db")
    init_db(db)
    con = sqlite3.connect(db)
    con.execute("DROP TABLE fa_gioi_han_gv")
    con.commit()
    con.close()
    init_db(db)
    con = sqlite3.connect(db)
    assert con.execute("SELECT COUNT(*) FROM sqlite_master WHERE name = 'fa_gioi_han_gv'").fetchone()[0] == 1
    con.close()
    assert di_tru_schema(db) == []
