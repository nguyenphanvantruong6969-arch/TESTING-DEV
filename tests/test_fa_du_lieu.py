"""FA-1 (A13, FA-DAA): mô hình dữ liệu — luật `fa_daa`, cột CLB mới, bảng `giu_cho`, Sổ nhập / CSV.

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.

Điều phải giữ:
  * `rules.fa_daa` mặc định TẮT; bật cần wharton + priority score + per_slot; tắt thì khoá KHÔNG
    vào `run_history.luat_xep` và dấu vân tay (như `wharton`);
  * `di_tru_schema` thêm 4 cột CLB, chạy hai lần = cùng schema;
  * tệp không có cột mới nạp y như trước; có cột mới thì vào CSDL; sai thì báo mã lỗi, không ghi;
  * xoá CLB / học sinh / xoá dữ liệu dọn cả `giu_cho`.
"""

import base64
import io
import os
import sqlite3

import pytest

openpyxl = pytest.importorskip("openpyxl")

import cau_hinh_ws as ch  # noqa: E402
import fa_daa  # noqa: E402
import rbda_priority_pipeline as rp  # noqa: E402
import so_nhap  # noqa: E402
from _wharton import dung_clb, dung_hs  # noqa: E402


def _bat_fa(api, bat=True):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": bat}})


def _cot_clubs(api):
    with api._ket_noi_doc() as cur:
        return [r[1] for r in cur.execute("PRAGMA table_info(clubs)")]


def _fa_cua(api, cid):
    with api._ket_noi_doc() as cur:
        return tuple(cur.execute(
            "SELECT loai, diem_san, so_toi_thieu, suc_chua_phong FROM clubs WHERE club_id = ?",
            (cid,)).fetchone())


def _giu_cho(api):
    with api._ket_noi_doc() as cur:
        return [tuple(r) for r in cur.execute(
            "SELECT club_id, student_id FROM giu_cho ORDER BY club_id, student_id")]


# ------------------------------------------------------------------ luật fa_daa


def test_fa_daa_mac_dinh_tat():
    cfg = ch.chuan_hoa({})
    assert cfg["rules"]["fa_daa"] is False
    assert rp.dung_fa_daa(cfg["rules"]) is False
    assert rp.dung_fa_daa({}) is False


def test_fa_daa_bat_duoc_voi_wharton_mac_dinh(api):
    _bat_fa(api)
    assert rp.dung_fa_daa(api._cfg_ws(nghiem=True)["rules"]) is True


def test_fa_daa_can_wharton_va_per_slot():
    with pytest.raises(ValueError):
        ch.chuan_hoa({"rules": {"fa_daa": True, "wharton": False}})
    with pytest.raises(ValueError):
        ch.chuan_hoa({"rules": {"fa_daa": True, "score_scope": "per_person"}})
    with pytest.raises(ValueError):
        ch.chuan_hoa({"rules": {"fa_daa": "co"}})
    # ghi rõ wharton true + fa_daa true: hợp lệ
    assert ch.chuan_hoa({"rules": {"fa_daa": True, "wharton": True}})["rules"]["fa_daa"] is True


def test_dung_fa_daa_nem_loi_voi_cau_hinh_hong():
    with pytest.raises(ValueError):
        rp.dung_fa_daa({"fa_daa": True, "wharton": False})


def test_khoa_fa_daa_tat_khong_vao_luat_xep_de_ghi():
    # tắt: giống hệt trước FA-1 (mặc định trường học -> None)
    assert rp.luat_xep_de_ghi({}) is None
    assert rp.luat_xep_de_ghi({"fa_daa": False}) is None
    assert rp.luat_xep_de_ghi({"wharton": True, "fa_daa": False}) == rp.luat_xep_de_ghi(
        {"wharton": True})
    assert "fa_daa" not in rp.luat_xep_de_ghi({"wharton": True, "fa_daa": False})
    assert '"fa_daa": true' in rp.luat_xep_de_ghi({"wharton": True, "fa_daa": True})


def _dvt(api):
    with api._ket_noi_doc() as cur:
        return rp.dau_van_tay_du_lieu(cur, api._cfg_ws(nghiem=True)["rules"])


def test_dau_van_tay_khong_doi_khi_fa_daa_tat(api):
    dung_clb(api, A=3)
    dung_hs(api, "s1")
    truoc = _dvt(api)
    _bat_fa(api, False)
    assert _dvt(api) == truoc
    # tắt: sửa thuộc tính FA / giữ chỗ KHÔNG làm kết quả báo "cũ"
    with api._ket_noi_ghi() as cur:
        cur.execute("UPDATE clubs SET loai='GIOI_HAN', so_toi_thieu=2 WHERE club_id='A'")
        cur.execute("INSERT INTO giu_cho (club_id, student_id) VALUES ('A', 's1')")
    assert _dvt(api) == truoc


def test_dau_van_tay_doi_theo_thuoc_tinh_fa_khi_bat(api):
    dung_clb(api, A=3)
    dung_hs(api, "s1")
    _bat_fa(api, True)
    b0 = _dvt(api)
    with api._ket_noi_ghi() as cur:
        cur.execute("UPDATE clubs SET loai='GIOI_HAN' WHERE club_id='A'")
    b1 = _dvt(api)
    assert b1 != b0
    with api._ket_noi_ghi() as cur:
        cur.execute("INSERT INTO giu_cho (club_id, student_id) VALUES ('A', 's1')")
    assert _dvt(api) not in (b0, b1)


# ------------------------------------------------------------------ schema


def test_cot_clb_moi_va_bang_giu_cho(api):
    cot = _cot_clubs(api)
    for c in ("loai", "diem_san", "so_toi_thieu", "suc_chua_phong"):
        assert c in cot
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT name FROM sqlite_master WHERE name = 'giu_cho'").fetchone()
        pk = sorted(r[1] for r in cur.execute("PRAGMA table_info(giu_cho)") if r[5])
    assert pk == ["club_id", "student_id"]


def test_di_tru_hai_lan_cung_schema(tmp_path):
    db = str(tmp_path / "cu.db")
    # CSDL cũ: clubs chưa có bốn cột FA
    con = sqlite3.connect(db)
    con.executescript("""
        CREATE TABLE students (student_id TEXT PRIMARY KEY, name TEXT, stb_number INTEGER,
            reserve_group TEXT, diem_ca_nhan REAL, class_id TEXT);
        CREATE TABLE clubs (club_id TEXT PRIMARY KEY, name TEXT, capacity INTEGER NOT NULL,
            reserve_capacity INTEGER NOT NULL DEFAULT 0, reserve_group TEXT, buoi TEXT);
        INSERT INTO clubs VALUES ('A', 'CLB A', 5, 0, NULL, NULL);
    """)
    con.commit()
    con.close()
    lam1 = rp.di_tru_schema(db)
    for c in ("loai", "diem_san", "so_toi_thieu", "suc_chua_phong"):
        assert "clubs." + c in lam1

    def chup():
        c = sqlite3.connect(db)
        try:
            return [tuple(r) for r in c.execute(
                "SELECT name, sql FROM sqlite_master ORDER BY name")]
        finally:
            c.close()

    s1 = chup()
    lam2 = rp.di_tru_schema(db)
    assert not [x for x in lam2 if x.startswith("clubs.")]
    assert chup() == s1
    c = sqlite3.connect(db)
    assert c.execute("SELECT loai, diem_san FROM clubs WHERE club_id='A'").fetchone() == (None, None)
    c.close()


def test_di_tru_sao_luu_truoc_khi_them_cot(tmp_path):
    db = str(tmp_path / "cu.db")
    con = sqlite3.connect(db)
    con.executescript("""
        CREATE TABLE students (student_id TEXT PRIMARY KEY, name TEXT, stb_number INTEGER,
            reserve_group TEXT, diem_ca_nhan REAL, class_id TEXT);
        CREATE TABLE clubs (club_id TEXT PRIMARY KEY, name TEXT, capacity INTEGER NOT NULL,
            reserve_capacity INTEGER NOT NULL DEFAULT 0, reserve_group TEXT, buoi TEXT);
        INSERT INTO clubs VALUES ('A', 'CLB A', 5, 0, NULL, 'thu_3');
    """)
    con.commit()
    con.close()
    rp.di_tru_schema(db)
    assert [f for f in os.listdir(tmp_path) if ".bak-" in f]


# ------------------------------------------------------------------ kiểm thuộc tính


@pytest.mark.parametrize("loai,san,toi,phong,ma", [
    ("SAI", None, None, None, "fa_loai_sai"),
    ("TUYEN_CHON", 11, None, None, "fa_diem_san_sai"),
    ("TUYEN_CHON", -1, None, None, "fa_diem_san_sai"),
    ("TUYEN_CHON", 2.5, None, None, "fa_diem_san_sai"),
    ("GIOI_HAN", None, -1, None, "fa_toi_thieu_sai"),
    ("TU_DO", None, None, 0, "fa_suc_chua_phong_sai"),
])
def test_kiem_thuoc_tinh_bao_ma(loai, san, toi, phong, ma):
    loi = fa_daa.kiem_thuoc_tinh(loai, san, toi, phong)
    assert [e["code"] for e in loi] == [ma]


def test_kiem_thuoc_tinh_hop_le():
    assert fa_daa.kiem_thuoc_tinh("TUYEN_CHON", 6, 3, None) == []
    assert fa_daa.kiem_thuoc_tinh(None, None, None, None) == []
    assert fa_daa.kiem_thuoc_tinh("TU_DO", None, 0, 40) == []


@pytest.mark.parametrize("nhan,ma", [
    ("Tự do", "TU_DO"), ("tu do", "TU_DO"), ("Giới hạn", "GIOI_HAN"),
    ("TUYỂN CHỌN", "TUYEN_CHON"), ("tuyen chon", "TUYEN_CHON"), ("TU_DO", "TU_DO"),
    ("", None), (None, None),
])
def test_chuan_hoa_loai(nhan, ma):
    assert fa_daa.chuan_hoa_loai(nhan) == ma


def test_chuan_hoa_loai_la_ho_nem_loi():
    with pytest.raises(ValueError):
        fa_daa.chuan_hoa_loai("Bí mật")


# ------------------------------------------------------------------ Sổ nhập


def _sach(clubs, students=(), giu_cho=None, cfg=None):
    b = io.BytesIO()
    so_nhap.ghi_so_nhap(b, clubs, students, cfg=cfg, giu_cho=giu_cho)
    return b.getvalue()


def _clb(cid, ten, cho=5, **kw):
    return {"club_id": cid, "name": ten, "capacity": cho, "reserve_capacity": 0,
            "reserve_group": "", "buoi": "", **kw}


def _doc(data, **kw):
    return so_nhap.doc_so_nhap(openpyxl.load_workbook(io.BytesIO(data)), **kw)


def test_so_cu_khong_cot_fa_giong_het_truoc():
    clubs = [_clb("A", "CLB A"), _clb("B", "CLB B")]
    cu = _sach(clubs)
    # ghi_so_nhap không có giu_cho / không có khoá FA: tệp không có cột FA, không có sheet Giữ chỗ
    wb = openpyxl.load_workbook(io.BytesIO(cu))
    assert so_nhap.SHEET_GIU_CHO not in wb.sheetnames
    assert [c.value for c in wb[so_nhap.ten_sheet_clb()][1]] == so_nhap.cot_clb()
    d = _doc(cu)
    assert not d["loi"]
    assert all("loai" not in c for c in d["clubs"])
    assert d.get("giu_cho", []) == []


def test_so_nhap_cot_fa_doc_duoc():
    clubs = [_clb("A", "CLB A", loai="Tuyển chọn", diem_san=6, so_toi_thieu=3),
             _clb("B", "CLB B", loai="Giới hạn", so_toi_thieu=2),
             _clb("C", "CLB C", loai="Tự do", suc_chua_phong=30)]
    d = _doc(_sach(clubs, giu_cho=[("A", "s1"), ("A", "s2")]))
    assert not d["loi"], d["loi"]
    by = {c["club_id"]: c for c in d["clubs"]}
    assert (by["A"]["loai"], by["A"]["diem_san"], by["A"]["so_toi_thieu"]) == ("TUYEN_CHON", 6, 3)
    assert by["B"]["loai"] == "GIOI_HAN" and by["B"]["so_toi_thieu"] == 2
    assert by["C"]["loai"] == "TU_DO" and by["C"]["suc_chua_phong"] == 30
    assert d["giu_cho"] == [("A", "s1"), ("A", "s2")]


@pytest.mark.parametrize("kw,ma", [
    ({"loai": "Bí mật"}, "so_nhap_fa_loai_sai"),
    ({"loai": "Tuyển chọn", "diem_san": 11}, "so_nhap_fa_diem_san_sai"),
    ({"loai": "Giới hạn", "so_toi_thieu": -2}, "so_nhap_fa_toi_thieu_sai"),
    ({"loai": "Tự do", "suc_chua_phong": 0}, "so_nhap_fa_suc_chua_phong_sai"),
])
def test_so_nhap_cot_fa_sai_bi_tu_choi(kw, ma):
    d = _doc(_sach([_clb("A", "CLB A", **kw)]))
    assert [e["code"] for e in d["loi"]] == [ma]
    assert d["loi"][0]["params"]["dong"] == 2


def test_nap_so_vao_csdl_khi_fa_bat(api):
    _bat_fa(api)
    dung_hs(api, "s1", "s2")
    clubs = [_clb("A", "CLB A", loai="Tuyển chọn", diem_san=6, so_toi_thieu=3),
             _clb("T", "CLB T", loai="Tự do", suc_chua_phong=30)]
    data = _sach(clubs, giu_cho=[("A", "s1")])
    kq = api.import_so_nhap(base64.b64encode(data).decode())
    assert kq["ok"], kq
    assert _fa_cua(api, "A") == ("TUYEN_CHON", 6, 3, None)
    assert _fa_cua(api, "T") == ("TU_DO", None, None, 30)
    assert _giu_cho(api) == [("A", "s1")]
    # nạp lại: không nhân đôi, ghi đè
    kq = api.import_so_nhap(base64.b64encode(data).decode())
    assert kq["ok"] and _giu_cho(api) == [("A", "s1")]


def test_nap_so_fa_tat_bo_qua_kem_canh_bao(api):
    dung_hs(api, "s1")
    clubs = [_clb("A", "CLB A", loai="Tuyển chọn", diem_san=6)]
    kq = api.import_so_nhap(base64.b64encode(_sach(clubs, giu_cho=[("A", "s1")])).decode())
    assert kq["ok"], kq
    codes = [w["code"] for w in kq["data"]["warnings"]]
    assert "fa_cot_bo_qua" in codes and "fa_giu_cho_bo_qua" in codes
    assert _fa_cua(api, "A") == (None, None, None, None)
    assert _giu_cho(api) == []


def test_nap_so_cu_giu_nguyen_thuoc_tinh_fa_da_co(api):
    # Sổ KHÔNG có cột FA nạp vào CLB đã có thuộc tính FA: giữ nguyên (cột vắng = "không biết")
    _bat_fa(api)
    dung_clb(api, A=5)
    with api._ket_noi_ghi() as cur:
        cur.execute("UPDATE clubs SET loai='GIOI_HAN', so_toi_thieu=2 WHERE club_id='A'")
    kq = api.import_so_nhap(base64.b64encode(_sach([_clb("A", "CLB A")])).decode())
    assert kq["ok"], kq
    assert _fa_cua(api, "A") == ("GIOI_HAN", None, 2, None)


def test_giu_cho_khong_co_hoc_sinh_bi_canh_bao(api):
    _bat_fa(api)
    dung_hs(api, "s1")
    data = _sach([_clb("A", "CLB A", loai="Giới hạn")], giu_cho=[("A", "s1"), ("A", "ghost")])
    kq = api.import_so_nhap(base64.b64encode(data).decode())
    assert kq["ok"], kq
    assert "so_nhap_fa_giu_cho_khong_ton_tai" in [w["code"] for w in kq["data"]["warnings"]]
    assert _giu_cho(api) == [("A", "s1")]


# ------------------------------------------------------------------ CSV


def test_csv_clb_cot_fa(api):
    _bat_fa(api)
    csv_text = ("club_id,name,capacity,loai,diem_san,so_toi_thieu,suc_chua_phong\n"
                "A,CLB A,5,TUYEN_CHON,6,3,\n"
                "T,CLB T,5,Tự do,,,40\n")
    kq = api.import_clubs_csv(csv_text)
    assert kq["ok"], kq
    assert _fa_cua(api, "A") == ("TUYEN_CHON", 6, 3, None)
    assert _fa_cua(api, "T") == ("TU_DO", None, None, 40)


def test_csv_clb_cu_khong_doi(api):
    kq = api.import_clubs_csv("club_id,name,capacity\nA,CLB A,5\n")
    assert kq["ok"], kq
    assert _fa_cua(api, "A") == (None, None, None, None)


def test_csv_clb_loai_sai_bao_loi_khong_ghi(api):
    _bat_fa(api)
    kq = api.import_clubs_csv("club_id,name,capacity,loai\nA,CLB A,5,BI_MAT\n")
    assert kq["ok"], kq
    assert [w["code"] for w in kq["data"]["warnings"]] == ["csv_club_fa_invalid"]
    assert kq["data"]["n_rows_skipped"] == 1 and kq["data"]["n_clubs_created"] == 0


# ------------------------------------------------------------------ xoá dọn giu_cho


def _dung_giu_cho(api):
    dung_clb(api, A=5, B=5)
    dung_hs(api, "s1", "s2")
    with api._ket_noi_ghi() as cur:
        cur.executemany("INSERT INTO giu_cho (club_id, student_id) VALUES (?, ?)",
                        [("A", "s1"), ("B", "s1"), ("B", "s2")])


def test_xoa_clb_don_giu_cho(api):
    _dung_giu_cho(api)
    assert api.delete_club("B")["ok"]
    assert _giu_cho(api) == [("A", "s1")]


def test_xoa_hoc_sinh_don_giu_cho(api):
    _dung_giu_cho(api)
    assert api.delete_student("s1")["ok"]
    assert _giu_cho(api) == [("B", "s2")]


def test_reset_don_giu_cho(api):
    _dung_giu_cho(api)
    assert api.reset_data("hoc_sinh", "XOA")["ok"]
    assert _giu_cho(api) == []


def test_giu_cho_khoa_chinh_va_khoa_ngoai(api):
    _dung_giu_cho(api)
    with api._ket_noi_ghi() as cur:
        with pytest.raises(sqlite3.IntegrityError):
            cur.execute("INSERT INTO giu_cho (club_id, student_id) VALUES ('A', 's1')")


def test_fa_s8_csv_fa_tat_bo_cot_fa_giu_dong(api):
    """FA-S8: FA tắt -> bỏ hẳn cột FA (kể cả ô sai), GIỮ dòng, một cảnh báo `fa_cot_bo_qua`."""
    kq = api.import_clubs_csv("club_id,name,capacity,loai\nC1,CLB 1,5,abc\nC2,CLB 2,5,TU_DO\n")
    assert kq["ok"], kq
    assert kq["data"]["n_clubs_created"] == 2 and kq["data"]["n_rows_skipped"] == 0
    assert [w["code"] for w in kq["data"]["warnings"]] == ["fa_cot_bo_qua"]
    assert _fa_cua(api, "C1") == (None, None, None, None)
    assert _fa_cua(api, "C2") == (None, None, None, None)


def test_fa_s8_csv_fa_bat_giu_hanh_vi_cu(api):
    _bat_fa(api)
    kq = api.import_clubs_csv("club_id,name,capacity,loai\nC1,CLB 1,5,abc\nC2,CLB 2,5,TU_DO\n")
    assert kq["ok"], kq
    assert kq["data"]["n_clubs_created"] == 1 and kq["data"]["n_rows_skipped"] == 1
    assert [w["code"] for w in kq["data"]["warnings"]] == ["csv_club_fa_invalid"]
    assert _fa_cua(api, "C2") == ("TU_DO", None, None, None)
