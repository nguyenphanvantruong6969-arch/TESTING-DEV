# -*- coding: utf-8 -*-
"""A14 — vòng sửa sau soát chéo (A1–A5). Dữ liệu là dữ liệu MÔ PHỎNG.

A1 nhãn hai danh từ trùng nhau; A2 sắp tự nhiên với chữ số Unicode; A3 chuẩn hoá NFC và ký tự
vô hình; A4 giới hạn đầu vào lớp; A5 sao lưu khi di trú không làm hỏng việc mở workspace."""

import base64
import io
import json
import os
import sqlite3

import openpyxl
import pytest

import cau_hinh_ws as ch
import rbda_priority_pipeline as rp
import so_nhap
import workspace as ws
from _wharton import tat_wharton
from api import PipelineAPI
from i18n_errors import MESSAGES

TRUNG = {"labels": {"group": {"vi": "Lớp", "en": "Class"}}}     # nhóm ưu tiên trùng nhãn Lớp


# ------------------------------------------------------------------ A1

@pytest.mark.parametrize("cfg", [
    TRUNG,                                                         # trùng cả vi lẫn en
    {"labels": {"group": {"vi": "  LỚP  ", "en": "Khối"}}},        # vi trùng sau strip + casefold
    {"labels": {"group": {"vi": "Khối", "en": " class "}}},        # chỉ en trùng
    {"labels": {"person": {"vi": "Điểm", "en": "People"}}},        # cặp khác: person ↔ score
])
def test_a1_cau_hinh_hai_danh_tu_trung_nhan_bi_tu_choi(tmp_path, cfg):
    db = str(tmp_path / "a.db")
    rp.init_db(db)
    with pytest.raises(ch.NhanTrung) as e:
        ch.ghi_cau_hinh(db, cfg)
    assert {e.value.a, e.value.b} <= set(ch.DANH_TU) and e.value.a != e.value.b
    assert isinstance(e.value, ValueError)
    with pytest.raises(ch.NhanTrung):
        ch.chuan_hoa(cfg)


def test_a1_mac_dinh_va_nhan_khac_nhau_van_hop_le(tmp_path):
    db = str(tmp_path / "a.db")
    rp.init_db(db)
    ch.ghi_cau_hinh(db, {"labels": {"group": {"vi": "Cấp bậc", "en": "Level"}}})
    ch.ghi_cau_hinh(db, {})


def test_a1_api_luu_cau_hinh_tra_ma_nhan_trung_danh_tu(tmp_path):
    goc = str(tmp_path / "goc")
    os.makedirs(goc)
    slug = ws.tao(goc, "Thử", {})
    api = PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_goc_ws=goc)
    kq = api.update_workspace_config(TRUNG, slug)
    assert not kq["ok"]
    loi = kq["errors"][0]
    assert loi["code"] == "nhan_trung_danh_tu"
    assert loi["params"]["nhan"] == "Lớp" and {loi["params"]["a"], loi["params"]["b"]} == {
        "group", "cohort"}
    assert "nhan_trung_danh_tu" in MESSAGES


def _luu_tho(db, cfg_tho):
    """Giả lập cấu hình ĐÃ LƯU từ trước (bản cũ không kiểm trùng nhãn)."""
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE IF NOT EXISTS workspace_settings (key TEXT PRIMARY KEY, value TEXT)")
    conn.execute("INSERT OR REPLACE INTO workspace_settings VALUES ('config', ?)",
                 (json.dumps(cfg_tho, ensure_ascii=False),))
    conn.commit()
    conn.close()


def test_a1_cau_hinh_cu_trung_van_doc_duoc_giu_nguyen_nhan(tmp_path):
    db = str(tmp_path / "a.db")
    rp.init_db(db)
    _luu_tho(db, TRUNG)
    cfg = ch.doc_cau_hinh(db)
    assert cfg["labels"]["group"]["vi"] == "Lớp"          # không rơi về mặc định
    assert ch.doc_cau_hinh(db, nghiem=True)["labels"]["group"]["vi"] == "Lớp"


def _so_trung(co_lop=True):
    clubs = [{"club_id": "a", "name": "CLB A", "capacity": 3, "reserve_capacity": 0,
              "reserve_group": "", "buoi": ""}]
    hs = [{"student_id": "S1", "name": "An", "reserve_group": "chinh_sach",
           "class_id": "10H1" if co_lop else None,
           "nv": [{"club_id": "a", "thi": False, "diem": ""}]}]
    buf = io.BytesIO()
    so_nhap.ghi_so_nhap(buf, clubs, hs, cfg=TRUNG, co_lop=co_lop)
    return openpyxl.load_workbook(io.BytesIO(buf.getvalue())), buf.getvalue()


def test_a1_khu_hoi_voi_cau_hinh_cu_trung_khong_dao_lop_va_nhom():
    wb, _ = _so_trung(co_lop=True)
    tieu = [o.value for o in wb[so_nhap.ten_sheet_hs(TRUNG)][1]][:4]
    assert tieu[2] == tieu[3] == "Lớp"                    # hai cột cùng tên: đúng tình huống trùng
    s = so_nhap.doc_so_nhap(wb, cfg=TRUNG)["students"][0]
    assert s["class_id"] == "10H1" and s["reserve_group"] == "chinh_sach"


def test_a1_so_cu_chi_mot_cot_trung_nhan_doc_la_nhom_nhu_truoc():
    """Sổ không có cột lớp, cột nhóm ưu tiên tình cờ tên "Lớp": vẫn là NHÓM (hành vi cũ)."""
    wb, _ = _so_trung(co_lop=False)
    s = so_nhap.doc_so_nhap(wb, cfg=TRUNG)["students"][0]
    assert s["reserve_group"] == "chinh_sach" and s["class_id"] is None


def test_a1_nap_so_cau_hinh_cu_trung_co_canh_bao(tmp_path):
    goc = str(tmp_path / "goc")
    os.makedirs(goc)
    slug = ws.tao(goc, "Thử", {})
    db = ws.duong_dan_db(goc, slug)
    api = PipelineAPI(db, thu_muc_xuat=str(tmp_path), thu_muc_goc_ws=goc)
    tat_wharton(api)                 # ghi lại cấu hình mặc định: lưu nhãn trùng SAU việc này
    _luu_tho(db, TRUNG)
    _, du_lieu = _so_trung(co_lop=True)
    kq = api.xem_truoc_so_nhap(base64.b64encode(du_lieu).decode())
    assert kq["ok"], kq
    assert "so_nhap_canh_bao_nhan_trung" in [w["code"] for w in kq["data"]["canh_bao"]]
    assert "so_nhap_canh_bao_nhan_trung" in MESSAGES


# ------------------------------------------------------------------ A2

@pytest.fixture
def api(tmp_path):
    a = PipelineAPI(str(tmp_path / "app.db"))
    tat_wharton(a)
    return a


def test_a2_lop_co_chu_so_unicode_khong_lam_hong_sap_xep(api):
    for sid, lop in (("A1", "10²"), ("A2", "10A1"), ("A3", "9B"), ("A4", "①")):
        api.create_student_if_missing(sid, sid)
        assert api.set_student_class(sid, lop)["ok"]
    kq = api.list_classes()
    assert kq["ok"], kq
    ds = api.list_students_admin(sort_by="class_id")
    assert ds["ok"], ds
    assert [r["student_id"] for r in ds["data"]["rows"]][:1] == ["A3"]     # 9B trước 10A1


# ------------------------------------------------------------------ A3

def test_a3_chuan_hoa_nfc_va_bo_ky_tu_vo_hinh():
    import unicodedata
    nfd = unicodedata.normalize("NFD", "chuyên")
    assert nfd != "chuyên"
    assert rp.chuan_hoa_lop(nfd) == rp.chuan_hoa_lop("chuyên") == "CHUYÊN"
    assert rp.chuan_hoa_lop("10A1\u200b") == rp.chuan_hoa_lop("10A1") == "10A1"
    assert rp.chuan_hoa_lop("﻿10A1") == "10A1"
    assert rp.chuan_hoa_lop("10\u200bA1") == "10A1"
    assert rp.chuan_hoa_lop("\u200b") is None


def test_a3_nfd_va_nfc_la_mot_lop(api):
    import unicodedata
    api.create_student_if_missing("A1", "x")
    api.create_student_if_missing("A2", "y")
    api.set_student_class("A1", "chuyên")
    api.set_student_class("A2", unicodedata.normalize("NFD", "chuyên"))
    assert [c["class_id"] for c in api.list_classes()["data"]["classes"]] == ["CHUYÊN"]


# ------------------------------------------------------------------ A4

@pytest.mark.parametrize("sai", [True, False, ["10A"], {"a": 1}])
def test_a4_set_student_class_tu_choi_kieu_khong_phai_chuoi_so(api, sai):
    api.create_student_if_missing("A1", "x")
    kq = api.set_student_class("A1", sai)
    assert not kq["ok"] and kq["errors"][0]["code"] == "lop_sai_kieu"


def test_a4_none_giu_nghia_cu_va_so_duoc_nhan(api):
    api.create_student_if_missing("A1", "x")
    assert api.set_student_class("A1", None)["ok"]
    assert api.set_student_class("A1", 12)["data"]["class_id"] == "12"


def test_a4_bo_ky_tu_dieu_khien(api):
    api.create_student_if_missing("A1", "x")
    assert api.set_student_class("A1", "10\x00A\x071")["data"]["class_id"] == "10A1"


def test_a4_qua_dai_sau_chuan_hoa_bi_tu_choi(api):
    api.create_student_if_missing("A1", "x")
    kq = api.set_student_class("A1", "L" * 51)
    assert kq["errors"][0] == {"code": "lop_qua_dai", "params": {"toi_da": 50}}
    assert api.set_student_class("A1", "L" * 50)["ok"]
    assert api.set_student_class("A1", "  " + "l" * 50 + "  ")["ok"]      # đo SAU chuẩn hoá


def test_a4_api_kiosk_cung_kiem(api):
    api.create_or_update_club("C1", "CLB", 5, 0, "")
    api.create_student_if_missing("A1", "x")
    for kq in (api.submit_preferences("A1", ["C1"], class_id=True),
               api.submit_test_selection("A1", ["C1"], class_id=["x"]),
               api.create_student_if_missing("A2", "y", class_id={"a": 1})):
        assert kq["errors"][0]["code"] == "lop_sai_kieu"
    assert api.submit_preferences("A1", ["C1"], class_id="L" * 51)["errors"][0]["code"] == \
        "lop_qua_dai"


def test_a4_nhap_csv_cat_con_50_va_canh_bao_khong_chan(api):
    api.create_or_update_club("C1", "CLB", 5, 0, "")
    kq = api.import_preferences_csv(
        "student_id,name,class_id,pref_1\nS1,An,%s,C1\nS2,Ba,10A1,C1\n" % ("l" * 60))
    assert kq["ok"], kq
    w = [x for x in kq["data"]["warnings"] if x["code"] == "canh_bao_lop_bi_cat"]
    assert w and w[0]["params"]["n"] == 1
    conn = sqlite3.connect(api.db_path)
    got = dict(conn.execute("SELECT student_id, class_id FROM students"))
    conn.close()
    assert got["S1"] == "L" * 50 and got["S2"] == "10A1"


def test_a4_nhap_so_cat_con_50_va_canh_bao(api):
    clubs = [{"club_id": "a", "name": "CLB A", "capacity": 3, "reserve_capacity": 0,
              "reserve_group": "", "buoi": ""}]
    hs = [{"student_id": "S1", "name": "An", "reserve_group": "", "class_id": "L" * 70,
           "nv": [{"club_id": "a", "thi": False, "diem": ""}]}]
    buf = io.BytesIO()
    so_nhap.ghi_so_nhap(buf, clubs, hs, co_lop=True)
    kq = api.import_so_nhap(base64.b64encode(buf.getvalue()).decode())
    assert kq["ok"], kq
    assert "canh_bao_lop_bi_cat" in [w["code"] for w in kq["data"]["warnings"]]
    assert api.list_classes()["data"]["classes"] == [{"class_id": "L" * 50, "n": 1}]


def test_a4_ma_loi_moi_co_trong_messages():
    for ma in ("lop_sai_kieu", "lop_qua_dai", "canh_bao_lop_bi_cat"):
        assert ma in MESSAGES


# ------------------------------------------------------------------ A5

def _csdl_cu_co_du_lieu(tmp_path):
    db = str(tmp_path / "cu.db")
    rp.init_db(db)
    conn = sqlite3.connect(db)
    conn.execute("INSERT INTO students (student_id, name) VALUES ('S1', 'An')")
    conn.execute("ALTER TABLE students DROP COLUMN class_id")
    conn.commit()
    conn.close()
    return db


def test_a5_loi_ghi_tep_sao_luu_khong_lam_hong_viec_mo_workspace(tmp_path, monkeypatch):
    db = _csdl_cu_co_du_lieu(tmp_path)
    that = sqlite3.connect

    def hong(ten, *a, **k):
        if ".bak-" in str(ten):
            raise sqlite3.OperationalError("unable to open database file")   # thư mục không ghi được
        return that(ten, *a, **k)

    monkeypatch.setattr(sqlite3, "connect", hong)
    da_lam = rp.di_tru_schema(db)                      # KHÔNG được ném
    assert "students.class_id" in da_lam
    monkeypatch.undo()
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT name, class_id FROM students").fetchall() == [("An", None)]
    conn.close()


def test_a5_sao_luu_dung_mot_lan_truoc_buoc_di_tru_dau_tien(tmp_path):
    """CSDL cũ thiếu NHIỀU cột (clubs.buoi, diem_ca_nhan, class_id): đúng một tệp sao lưu, và
    nó còn chứa schema CŨ (chụp trước bước đầu tiên)."""
    import glob
    db = str(tmp_path / "cu2.db")
    rp.init_db(db)
    conn = sqlite3.connect(db)
    conn.execute("INSERT INTO students (student_id, name) VALUES ('S1', 'An')")
    conn.execute("ALTER TABLE students DROP COLUMN class_id")
    conn.execute("ALTER TABLE students DROP COLUMN diem_ca_nhan")
    conn.execute("ALTER TABLE clubs DROP COLUMN buoi")
    conn.commit()
    conn.close()
    da_lam = rp.di_tru_schema(db)
    assert {"clubs.buoi", "students.diem_ca_nhan", "students.class_id"} <= set(da_lam)
    baks = glob.glob(db + ".bak-*")
    assert len(baks) >= 1
    cu = [b for b in baks if "buoi" not in [r[1] for r in sqlite3.connect(b).execute(
        "PRAGMA table_info(clubs)")]]
    assert len(cu) == 1                                   # đúng một bản chụp TRƯỚC khi sửa gì
    assert rp.di_tru_schema(db) == []                     # lặp lại: không làm gì, không sao lưu thêm
    assert len(glob.glob(db + ".bak-*")) == len(baks)


# ------------------------------------------------------------------ C1 (ghi lại cấu hình trùng đã lưu)

def _ws_trung(tmp_path):
    """Workspace có cấu hình ĐÃ LƯU với nhãn trùng (group = cohort = "Lớp")."""
    goc = str(tmp_path / "goc")
    os.makedirs(goc, exist_ok=True)
    slug = ws.tao(goc, "Cũ", {})
    _luu_tho(ws.duong_dan_db(goc, slug), TRUNG)
    return goc, slug


def test_c1_doi_ten_workspace_co_nhan_trung_van_duoc_va_giu_nhan(tmp_path):
    goc, slug = _ws_trung(tmp_path)
    ws.doi_ten(goc, slug, "Tên mới")
    cfg = ch.doc_cau_hinh(ws.duong_dan_db(goc, slug))
    assert cfg["name"] == "Tên mới"
    assert cfg["labels"]["group"]["vi"] == cfg["labels"]["cohort"]["vi"] == "Lớp"


def test_c1_api_cap_nhat_phan_khac_khong_dung_nhan_van_duoc(tmp_path):
    goc, slug = _ws_trung(tmp_path)
    api = PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_goc_ws=goc)
    kq = api.update_workspace_config({"name": "Đổi tên"}, slug)
    assert kq["ok"], kq
    assert kq["data"]["config"]["labels"]["group"]["vi"] == "Lớp"


def test_c1_nhan_ban_giu_nguyen_cau_hinh_trung_ca_co_va_khong_kem_du_lieu(tmp_path):
    goc, slug = _ws_trung(tmp_path)
    for kem in (False, True):
        moi = ws.nhan_ban(goc, slug, "Bản sao %s" % kem, kem)
        cfg = ch.doc_cau_hinh(ws.duong_dan_db(goc, moi))
        assert cfg["labels"]["group"]["vi"] == cfg["labels"]["cohort"]["vi"] == "Lớp"


def test_c1_van_tu_choi_khi_lan_luu_nay_tao_hoac_doi_cap_trung(tmp_path):
    goc, slug = _ws_trung(tmp_path)
    api = PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_goc_ws=goc)
    # tạo cặp trùng MỚI (person ↔ score) trên nền cấu hình đã trùng
    kq = api.update_workspace_config(
        {"labels": {"person": {"vi": "Điểm", "en": "Pupil"}}}, slug)
    assert not kq["ok"] and kq["errors"][0]["code"] == "nhan_trung_danh_tu"
    # ĐỔI cặp trùng sang nhãn khác mà vẫn trùng
    kq = api.update_workspace_config({"labels": {
        "group": {"vi": "Phòng", "en": "Dept"}, "cohort": {"vi": "Phòng", "en": "Team"}}}, slug)
    assert not kq["ok"] and kq["errors"][0]["code"] == "nhan_trung_danh_tu"
    # cấu hình lưu không bị đổi sau hai lần từ chối
    assert ch.doc_cau_hinh(ws.duong_dan_db(goc, slug))["labels"]["group"]["vi"] == "Lớp"


def test_c1_sua_cho_het_trung_thi_luu_duoc(tmp_path):
    goc, slug = _ws_trung(tmp_path)
    api = PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_goc_ws=goc)
    kq = api.update_workspace_config(
        {"labels": {"group": {"vi": "Nhóm ưu tiên", "en": "Priority group"}}}, slug)
    assert kq["ok"], kq


def test_c1_cau_hinh_hop_le_dat_nhan_trung_van_bi_tu_choi(tmp_path):
    goc = str(tmp_path / "goc")
    os.makedirs(goc)
    slug = ws.tao(goc, "Sạch", {})
    api = PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_goc_ws=goc)
    kq = api.update_workspace_config(TRUNG, slug)
    assert not kq["ok"] and kq["errors"][0]["code"] == "nhan_trung_danh_tu"
    with pytest.raises(ch.NhanTrung):
        ws.tao(goc, "Mới", TRUNG)
