"""Các lỗi tìm thấy khi rà nhánh workspace — mỗi test khoá lại MỘT lỗi đã sửa.

  1. Di trú app.db cũ chạy lại sau khi dừng giữa chừng KHÔNG được đè app.db thật.
  2. Đổi tên / nhân bản / lưu mẫu KHÔNG được ghi mặc định đè lên cấu hình đọc không được.
  3. Tiêu đề tệp CSV mang nhãn do người dùng đặt: không để Excel hiểu thành công thức.
  4. Hồ sơ học sinh của workspace chấm điểm theo NGƯỜI phải có điểm đó.
  5. Tên nhóm ưu tiên khớp qua khoảng trắng thừa / dấu cách không ngắt.
"""

import csv
import json
import os
import shutil
import sqlite3

import pytest

import cau_hinh_ws
import rbda_priority_pipeline as rp
import workspace as ws
from api import PipelineAPI
from api_chung import _ghi_csv


@pytest.fixture
def goc(tmp_path):
    g = tmp_path / "goc"
    g.mkdir()
    return str(g)


def _db_co_hoc_sinh(duong, ma, ten="x"):
    rp.init_db(duong)
    conn = sqlite3.connect(duong)
    conn.execute("INSERT INTO students (student_id, name) VALUES (?, ?)", (ma, ten))
    conn.commit()
    conn.close()


def _ma_hoc_sinh(duong):
    conn = sqlite3.connect(duong)
    try:
        return [r[0] for r in conn.execute("SELECT student_id FROM students ORDER BY 1")]
    finally:
        conn.close()


# ------------------------------------------------------------------ 1. di trú chạy lại

def _dung_canh_dang_dung_do(goc):
    """app.db THẬT đã được dời vào thư mục dựng dở, rồi một app.db MỚI mọc lên ở gốc."""
    that = os.path.join(goc, "app.db")
    _db_co_hoc_sinh(that, "HS_THAT")
    dich = os.path.join(goc, ws._THU_MUC_DANG_DUNG, ws.SLUG_TRUONG_HOC)
    os.makedirs(dich)
    shutil.move(that, os.path.join(dich, "app.db"))
    _db_co_hoc_sinh(that, "HS_MOI")      # vd màn phục hồi "bắt đầu mới", hay bản cũ chạy lại
    return dich


def test_di_tru_chay_lai_khong_de_app_db_that_bang_app_db_moi(goc):
    _dung_canh_dang_dung_do(goc)
    assert ws.di_chuyen_db_cu(goc) is True
    db = ws.duong_dan_db(goc, "truong-hoc")
    assert _ma_hoc_sinh(db) == ["HS_THAT"]                       # dữ liệu thật còn nguyên
    thu_muc = os.path.dirname(db)
    ben_canh = [t for t in os.listdir(thu_muc) if t.startswith("app.db.trung-")]
    assert len(ben_canh) == 1                                    # bản mới không mất, để cạnh
    assert _ma_hoc_sinh(os.path.join(thu_muc, ben_canh[0])) == ["HS_MOI"]
    assert not os.path.exists(os.path.join(goc, "app.db"))


def test_di_tru_chay_lai_khong_ghep_nhat_ky_cua_app_db_moi_vao_app_db_that(goc):
    dich = _dung_canh_dang_dung_do(goc)
    nhat_ky_moi = os.path.join(goc, "app.db-journal")
    with open(nhat_ky_moi, "wb") as f:
        f.write(b"nhat ky cua app.db MOI")
    ws.di_chuyen_db_cu(goc)
    # Nhật ký của app.db mới mà nằm cạnh app.db thật thì SQLite sẽ thử "phục hồi" app.db thật.
    assert not os.path.exists(os.path.join(dich, "app.db-journal"))
    assert not os.path.exists(os.path.join(goc, "workspaces", "truong-hoc", "app.db-journal"))
    assert any(t.startswith("app.db-journal.trung-")
               for t in os.listdir(os.path.join(goc, "workspaces", "truong-hoc")))


def test_di_tru_lan_dau_van_chuyen_nguyen_ven_nhu_cu(goc):
    that = os.path.join(goc, "app.db")
    _db_co_hoc_sinh(that, "HS1")
    with open(os.path.join(goc, "app.db.bak-20260101_000000_000000"), "wb") as f:
        f.write(b"sao luu")
    assert ws.di_chuyen_db_cu(goc) is True
    thu_muc = os.path.join(goc, "workspaces", "truong-hoc")
    assert sorted(t for t in os.listdir(thu_muc)) == ["app.db", "app.db.bak-20260101_000000_000000"]
    assert _ma_hoc_sinh(os.path.join(thu_muc, "app.db")) == ["HS1"]


# ------------------------------------------------------------------ 2. cấu hình đọc không được

NHAN_CONG_TY = {"person": {"vi": "Nhân viên", "en": "Employee"}}


def _ws_co_cau_hinh_la(goc):
    """Workspace có nhãn/luật riêng, rồi cấu hình bị ghi thêm một khoá lạ (vd bởi bản mới hơn)."""
    slug = ws.tao(goc, "Công ty", {"labels": NHAN_CONG_TY, "rules": {"max_choices": 3}})
    db = ws.duong_dan_db(goc, slug)
    conn = sqlite3.connect(db)
    tho = json.loads(conn.execute(
        "SELECT value FROM workspace_settings WHERE key = 'config'").fetchone()[0])
    tho["rules"]["luat_cua_ban_moi"] = 1
    conn.execute("UPDATE workspace_settings SET value = ? WHERE key = 'config'",
                 (json.dumps(tho),))
    conn.commit()
    conn.close()
    return slug, db, json.dumps(tho)


def _gia_tri_tho(db):
    conn = sqlite3.connect(db)
    try:
        return conn.execute("SELECT value FROM workspace_settings WHERE key = 'config'").fetchone()[0]
    finally:
        conn.close()


def test_doi_ten_tu_choi_khi_cau_hinh_doc_khong_duoc_chu_khong_ghi_mac_dinh_de_len(goc):
    slug, db, truoc = _ws_co_cau_hinh_la(goc)
    with pytest.raises(ValueError):
        ws.doi_ten(goc, slug, "Tên mới")
    assert _gia_tri_tho(db) == truoc                      # không đụng gì


def test_nhan_ban_va_luu_mau_cung_tu_choi_chu_khong_nhan_ban_mot_cau_hinh_doan(goc):
    slug, db, truoc = _ws_co_cau_hinh_la(goc)
    with pytest.raises(ValueError):
        ws.nhan_ban(goc, slug, "Bản sao", kem_du_lieu=True)
    with pytest.raises(ValueError):
        ws.nhan_ban(goc, slug, "Bản sao 2", kem_du_lieu=False)
    with pytest.raises(ValueError):
        ws.luu_mau(goc, slug, "Mẫu")
    assert [w["slug"] for w in ws.danh_sach(goc)] == [slug]    # không để lại thư mục dở dang
    assert not os.path.exists(os.path.join(goc, ws.THU_MUC_MAU))
    assert _gia_tri_tho(db) == truoc


def test_doc_cau_hinh_mac_dinh_van_khong_bao_gio_nem(goc):
    _, db, _ = _ws_co_cau_hinh_la(goc)
    assert cau_hinh_ws.doc_cau_hinh(db)["rules"]["max_choices"] == 10      # như cũ: rơi về mặc định


def test_doc_cau_hinh_nghiem_chi_cho_mac_dinh_khi_that_su_chua_co_cau_hinh(tmp_path):
    mac_dinh = cau_hinh_ws.doc_cau_hinh(str(tmp_path / "khong_co.db"))
    assert cau_hinh_ws.doc_cau_hinh(str(tmp_path / "khong_co.db"), nghiem=True) == mac_dinh

    cu = str(tmp_path / "cu.db")                          # CSDL trước khi có bảng cấu hình
    conn = sqlite3.connect(cu)
    conn.execute("CREATE TABLE students (student_id TEXT)")
    conn.commit()
    conn.close()
    assert cau_hinh_ws.doc_cau_hinh(cu, nghiem=True) == mac_dinh

    chua_co_hang = str(tmp_path / "chua_co_hang.db")
    rp.init_db(chua_co_hang)
    assert cau_hinh_ws.doc_cau_hinh(chua_co_hang, nghiem=True) == mac_dinh

    hong = str(tmp_path / "hong.db")
    rp.init_db(hong)
    conn = sqlite3.connect(hong)
    conn.execute("INSERT INTO workspace_settings VALUES ('config', '{khong phai json')")
    conn.commit()
    conn.close()
    assert cau_hinh_ws.doc_cau_hinh(hong) == mac_dinh
    with pytest.raises(ValueError):
        cau_hinh_ws.doc_cau_hinh(hong, nghiem=True)


def test_doi_ten_workspace_binh_thuong_van_giu_nhan_va_luat(goc):
    slug = ws.tao(goc, "Công ty", {"labels": NHAN_CONG_TY, "rules": {"max_choices": 3}})
    ws.doi_ten(goc, slug, "Công ty mới")
    cfg = cau_hinh_ws.doc_cau_hinh(ws.duong_dan_db(goc, slug), nghiem=True)
    assert cfg["name"] == "Công ty mới"
    assert cfg["labels"]["person"]["vi"] == "Nhân viên" and cfg["rules"]["max_choices"] == 3


def test_api_doi_ten_bao_loi_dich_duoc_khi_cau_hinh_la(goc, tmp_path):
    slug, db, truoc = _ws_co_cau_hinh_la(goc)
    api = PipelineAPI(db, thu_muc_xuat=str(tmp_path), thu_muc_goc_ws=goc)
    r = api.rename_workspace(slug, "Tên mới")
    assert not r["ok"] and r["errors"][0]["code"] == "ws_du_lieu_sai"
    assert _gia_tri_tho(db) == truoc


# ------------------------------------------------------------------ 3. tiêu đề CSV

def test_ghi_csv_chan_cong_thuc_ca_o_dong_tieu_de(tmp_path):
    duong = str(tmp_path / "a.csv")
    _ghi_csv(duong, ["Mã", '=HYPERLINK("http://x","y")', "+1", "@a", "Tên"],
             [["=1+1", "ok"]])
    dong = list(csv.reader(open(duong, encoding="utf-8-sig")))
    assert dong[0] == ["Mã", '\'=HYPERLINK("http://x","y")', "'+1", "'@a", "Tên"]
    assert dong[1][0] == "'=1+1"


def test_tieu_de_csv_mac_dinh_khong_doi_byte_nao(tmp_path):
    duong = str(tmp_path / "a.csv")
    _ghi_csv(duong, ["Mã học sinh", "Họ tên", "Điểm", "Nguyện vọng thứ"], [])
    assert open(duong, encoding="utf-8-sig", newline="").read() == \
        "Mã học sinh,Họ tên,Điểm,Nguyện vọng thứ\r\n"


def _api_ws(goc, tmp_path, cfg):
    slug = ws.tao(goc, "Thử", cfg)
    xuat = tmp_path / "xuat"
    xuat.mkdir(exist_ok=True)
    return PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_xuat=str(xuat), thu_muc_goc_ws=goc)


def test_nhan_la_cong_thuc_khong_thanh_cong_thuc_trong_tep_ho_so_hoc_sinh(goc, tmp_path):
    # Lớp 1: cấu hình không nhận nhãn mở đầu bằng ký tự công thức (xem test_ws_sua_loi_2).
    with pytest.raises(ValueError):
        ws.tao(goc, "Xấu", {"labels": {"score": {"vi": '=HYPERLINK("http://x","Điểm")'}}})
    # Lớp 2 (phòng thủ chiều sâu): dù tiêu đề lọt tới đây bằng đường nào, `_ghi_csv` vẫn chặn.
    duong = str(tmp_path / "t.csv")
    _ghi_csv(duong, ['=HYPERLINK("http://x","Điểm")', "ok"], [["1", "2"]])
    tieu_de = next(csv.reader(open(duong, encoding="utf-8-sig")))
    assert all(o[:1] not in ("=", "+", "-", "@") for o in tieu_de), tieu_de
    assert '\'=HYPERLINK("http://x","Điểm")' in tieu_de


# ------------------------------------------------------------------ 4. điểm theo người

def _dung_hai_em(api, diem):
    assert api.create_or_update_club("a", "A", 1, 0, "")["ok"]
    for sid in diem:
        assert api.create_student_if_missing(sid, sid)["ok"]
        assert api.submit_preferences(sid, ["a"])["ok"]
    with api._ket_noi_ghi() as cur:
        for sid, d in diem.items():
            cur.execute("UPDATE students SET diem_ca_nhan = ? WHERE student_id = ?", (d, sid))


def _doc_ho_so(api, ids):
    r = api.export_hoc_sinh_csv(ids)
    assert r["ok"], r
    dong = list(csv.reader(open(r["data"]["path"], encoding="utf-8-sig")))
    cot = dong[0].index("Điểm")
    return {d[0]: d[cot] for d in dong[1:]}


def test_ho_so_hoc_sinh_workspace_cham_theo_nguoi_co_diem_cua_em(goc, tmp_path):
    api = _api_ws(goc, tmp_path, {"rules": {"score_scope": "per_person"}})
    _dung_hai_em(api, {"s1": 5, "s2": 9.5})
    assert api.run_pipeline()["ok"]
    with api._ket_noi_doc() as cur:
        assert dict(cur.execute("SELECT student_id, club_id FROM match_results"))["s2"] == "a"
    assert _doc_ho_so(api, ["s1", "s2"]) == {"s1": "5", "s2": "9.5"}


def test_ho_so_hoc_sinh_em_chua_co_diem_thi_o_diem_trong(goc, tmp_path):
    api = _api_ws(goc, tmp_path, {"rules": {"score_scope": "per_person"}})
    _dung_hai_em(api, {"s1": None, "s2": 7})
    assert _doc_ho_so(api, ["s1", "s2"]) == {"s1": "", "s2": "7"}


def test_ho_so_hoc_sinh_truong_hoc_van_doc_diem_tung_clb_nhu_cu(goc, tmp_path):
    api = _api_ws(goc, tmp_path, {})
    assert api.create_or_update_club("a", "A", 1, 0, "")["ok"]
    assert api.create_student_if_missing("s1", "S1")["ok"]
    assert api.submit_preferences("s1", ["a"])["ok"]
    assert api.submit_test_selection("s1", ["a"])["ok"]
    assert api.submit_club_scores("a", [{"student_id": "s1", "score": "8,5"}])["ok"]
    with api._ket_noi_ghi() as cur:       # có điểm theo người cũng không được lẫn vào chế độ này
        cur.execute("UPDATE students SET diem_ca_nhan = 1 WHERE student_id = 's1'")
    assert _doc_ho_so(api, ["s1"]) == {"s1": "8.5"}


# ------------------------------------------------------------------ 5. khớp tên nhóm

@pytest.mark.parametrize("nhom", [
    "Khối 12", "khoi 12", "KHỐI  12", " Khối 12 ", "Khối 12", "Khối  12", "Khối\t12",
])
def test_ten_nhom_khop_qua_khoang_trang_thua_va_dau_cach_khong_ngat(nhom):
    hang = rp.xay_tier_rank({"a": {"reserve_group": nhom}}, ["Khối 12", "Khối 11"])
    assert hang == {"a": 0}


def test_ten_nhom_khac_that_su_van_khong_khop():
    hang = rp.xay_tier_rank({"a": {"reserve_group": "Khối 1 2"},
                             "b": {"reserve_group": "Khối 11"},
                             "c": {"reserve_group": None},
                             "d": {"reserve_group": "   "}}, ["Khối 12", "Khối 11"])
    assert hang == {"b": 1}
