"""Workspace trên đĩa (workspace.py) và cách main.py chọn workspace lúc khởi động."""

import json
import contextlib
import os
import sqlite3
import sys
import zipfile
from pathlib import Path

import pytest

import cau_hinh_ws as ch
import workspace as ws
from rbda_priority_pipeline import init_db


def _ket_noi(db):
    """Kết nối ĐÓNG tường minh khi ra khỏi khối with.

    `with sqlite3.connect(db) as c` chỉ commit, KHÔNG đóng; kết nối nằm trong vòng tham chiếu vòng
    (bộ nhớ đệm câu lệnh) nên tới khi GC chạy mới nhả tệp. Trên Windows, tệp đang mở không dời / xoá
    / đổi tên được (WinError 32) — CI Windows đỏ vì đúng chuyện này.
    """
    return contextlib.closing(sqlite3.connect(db))


def _them_clb(db, club_id="A", ten="Bóng đá"):
    with _ket_noi(db) as c:
        c.execute("INSERT INTO clubs (club_id, name, capacity, reserve_capacity) "
                  "VALUES (?, ?, 5, 0)", (club_id, ten))
        c.commit()


def _clb(db):
    with _ket_noi(db) as c:
        return c.execute("SELECT club_id, name FROM clubs ORDER BY club_id").fetchall()


def _ten_thu_muc(root, *con):
    return sorted(os.listdir(os.path.join(root, "workspaces", *con)))


@pytest.fixture
def root(tmp_path):
    # Thư mục con: conftest tự đặt "TaiXuong_gia" ngay trong tmp_path.
    goc = tmp_path / "goc"
    goc.mkdir()
    return str(goc)


# ------------------------------------------------------------------ tao / danh_sach

def test_tao_dung_thu_muc_csdl_va_cau_hinh(root):
    slug = ws.tao(root, "Trường học", None)
    assert slug == "truong-hoc"
    db = ws.duong_dan_db(root, slug)
    assert os.path.isfile(db)
    cfg = ch.doc_cau_hinh(db)
    assert cfg["name"] == "Trường học"
    assert cfg["rules"] == ch.MAC_DINH_TRUONG_HOC["rules"]
    # init_db đã chạy: bảng nghiệp vụ có đủ
    _them_clb(db)


def test_tao_nhan_cfg_va_ten_trong_cfg_bi_ten_ghi_de(root):
    cfg = {"name": "Bị ghi đè", "industry": "company",
           "labels": {"person": {"vi": "Nhân viên", "en": "Employee"}},
           "rules": {"max_choices": 3}}
    slug = ws.tao(root, "Công ty ABC", cfg)
    assert slug == "cong-ty-abc"
    doc = ch.doc_cau_hinh(ws.duong_dan_db(root, slug))
    assert doc["name"] == "Công ty ABC"
    assert doc["industry"] == "company"
    assert doc["rules"]["max_choices"] == 3
    assert ch.nhan(doc, "person", "en") == "Employee"


@pytest.mark.parametrize("ten, slug", [
    ("Trường học", "truong-hoc"),
    ("  Đại Hội   Thể  Thao  ", "dai-hoi-the-thao"),
    ("CLB (2026)!", "clb"),     # bo_dau bỏ phần trong ngoặc, như ở sổ nhập
    ("!!!", "workspace"),
])
def test_tao_slug(root, ten, slug):
    assert ws.tao(root, ten, None) == slug


def test_tao_trung_slug_them_hau_to(root):
    assert ws.tao(root, "Trường học", None) == "truong-hoc"
    assert ws.tao(root, "Truong hoc", None) == "truong-hoc-2"
    assert ws.tao(root, "TRƯỜNG HỌC", None) == "truong-hoc-3"
    # tên vẫn là tên người gõ, chỉ slug khác
    ten = {w["slug"]: w["name"] for w in ws.danh_sach(root)}
    assert ten == {"truong-hoc": "Trường học", "truong-hoc-2": "Truong hoc",
                   "truong-hoc-3": "TRƯỜNG HỌC"}


def test_tao_thu_muc_thieu_app_db_van_chiem_cho(root):
    os.makedirs(os.path.join(root, "workspaces", "a"))
    assert ws.tao(root, "A", None) == "a-2"


@pytest.mark.parametrize("ten", ["", "   ", None, 5])
def test_tao_ten_rong(root, ten):
    with pytest.raises(ValueError):
        ws.tao(root, ten, None)
    assert not os.path.exists(os.path.join(root, "workspaces"))


def test_tao_cfg_sai_khong_de_lai_thu_muc(root):
    with pytest.raises(ValueError, match="max_choices"):
        ws.tao(root, "X", {"rules": {"max_choices": 99}})
    assert not os.path.exists(os.path.join(root, "workspaces"))


def test_danh_sach_rong_khi_chua_co_gi(root):
    assert ws.danh_sach(root) == []


def test_danh_sach_truong_va_bo_qua_thung_rac_va_thu_muc_la(root):
    a = ws.tao(root, "Alpha", {"industry": "event"})
    ws.tao(root, "Beta", None)
    ws.xoa(root, "beta")
    os.makedirs(os.path.join(root, "workspaces", "khong-co-db"))
    os.makedirs(os.path.join(root, "workspaces", "_nhap-tam"))
    (open(os.path.join(root, "workspaces", "tep-le.txt"), "w")).close()
    ds = ws.danh_sach(root)
    assert [w["slug"] for w in ds] == ["alpha"]
    w = ds[0]
    assert set(w) == {"slug", "name", "industry", "path", "modified"}
    assert (w["name"], w["industry"]) == ("Alpha", "event")
    assert w["path"] == ws.duong_dan_db(root, a)
    assert os.path.isfile(w["path"])
    assert len(w["modified"]) == 19  # YYYY-MM-DD HH:MM:SS


def test_danh_sach_workspace_khong_co_cau_hinh_dung_slug_lam_ten(root):
    thu_muc = os.path.join(root, "workspaces", "cu")
    os.makedirs(thu_muc)
    init_db(os.path.join(thu_muc, "app.db"))
    w = ws.danh_sach(root)[0]
    assert (w["slug"], w["name"], w["industry"]) == ("cu", "cu", "school")


@pytest.mark.parametrize("slug", ["../x", "a/b", "_trash", "", "A", "a b", None, "..", "a\\b"])
def test_slug_xau_bi_tu_choi(root, slug):
    ws.tao(root, "A", None)
    for goi in (lambda: ws.doi_ten(root, slug, "B"), lambda: ws.xoa(root, slug),
                lambda: ws.nhan_ban(root, slug, "B", True),
                lambda: ws.luu_mau(root, slug, "B"),
                lambda: ws.xuat_zip(root, slug, os.path.join(root, "o.zip"))):
        with pytest.raises(ValueError):
            goi()


def test_slug_khong_ton_tai(root):
    with pytest.raises(ValueError, match="khong-co"):
        ws.doi_ten(root, "khong-co", "B")


# ------------------------------------------------------------------ doi_ten

def test_doi_ten_chi_doi_ten_con_thu_muc_va_luat_giu_nguyen(root):
    cfg = {"industry": "company", "rules": {"max_choices": 4, "max_tests": None}}
    slug = ws.tao(root, "Cũ", cfg)
    db = ws.duong_dan_db(root, slug)
    _them_clb(db)
    truoc = ch.doc_cau_hinh(db)
    ws.doi_ten(root, slug, "  Mới  ")
    sau = ch.doc_cau_hinh(db)
    assert sau["name"] == "Mới"
    assert {**sau, "name": None} == {**truoc, "name": None}
    assert [w["slug"] for w in ws.danh_sach(root)] == [slug] == ["cu"]
    assert _clb(db) == [("A", "Bóng đá")]


def test_doi_ten_rong(root):
    slug = ws.tao(root, "A", None)
    with pytest.raises(ValueError):
        ws.doi_ten(root, slug, "  ")
    assert ch.doc_cau_hinh(ws.duong_dan_db(root, slug))["name"] == "A"


# ------------------------------------------------------------------ xoa

def test_xoa_dua_vao_thung_rac_kem_ban_sao_luu(root):
    slug = ws.tao(root, "Sẽ xoá", None)
    db = ws.duong_dan_db(root, slug)
    _them_clb(db)

    dich = ws.xoa(root, slug)

    assert ws.danh_sach(root) == []
    assert not os.path.exists(os.path.dirname(db))
    thung = os.path.join(root, "workspaces", "_trash")
    (muc,) = os.listdir(thung)
    assert muc.startswith("se-xoa-") and os.path.join(thung, muc) == dich
    tep = sorted(os.listdir(dich))
    assert "app.db" in tep
    (sao_luu,) = [t for t in tep if t.startswith("app.db.bak-")]
    # cả app.db lẫn bản sao lưu còn nguyên dữ liệu
    assert _clb(os.path.join(dich, "app.db")) == [("A", "Bóng đá")]
    assert _clb(os.path.join(dich, sao_luu)) == [("A", "Bóng đá")]


def test_xoa_hai_lan_cung_slug_khong_de_nhau(root):
    for _ in range(2):
        slug = ws.tao(root, "Lặp", None)
        ws.xoa(root, slug)
    assert len(os.listdir(os.path.join(root, "workspaces", "_trash"))) == 2


def test_xoa_roi_tao_lai_dung_lai_slug(root):
    ws.xoa(root, ws.tao(root, "A", None))
    assert ws.tao(root, "A", None) == "a"


# ------------------------------------------------------------------ nhan_ban

def test_nhan_ban_kem_du_lieu(root):
    cfg = {"industry": "event", "rules": {"max_choices": 6}}
    nguon = ws.tao(root, "Gốc", cfg)
    db = ws.duong_dan_db(root, nguon)
    _them_clb(db, "A")
    _them_clb(db, "B", "Cờ vua")

    moi = ws.nhan_ban(root, nguon, "Bản sao", True)

    assert moi == "ban-sao"
    db2 = ws.duong_dan_db(root, moi)
    assert _clb(db2) == _clb(db) == [("A", "Bóng đá"), ("B", "Cờ vua")]
    cfg2 = ch.doc_cau_hinh(db2)
    assert cfg2["name"] == "Bản sao"
    assert cfg2["rules"]["max_choices"] == 6 and cfg2["industry"] == "event"
    # độc lập: sửa bản sao không đụng bản gốc
    _them_clb(db2, "C")
    assert len(_clb(db)) == 2
    assert ch.doc_cau_hinh(db)["name"] == "Gốc"


def test_nhan_ban_khong_kem_du_lieu(root):
    nguon = ws.tao(root, "Gốc", {"rules": {"max_choices": 6, "tiers": ["X", "Y"]}})
    db = ws.duong_dan_db(root, nguon)
    _them_clb(db)

    moi = ws.nhan_ban(root, nguon, "Trống", False)

    db2 = ws.duong_dan_db(root, moi)
    assert _clb(db2) == []
    cfg2 = ch.doc_cau_hinh(db2)
    assert cfg2["name"] == "Trống"
    assert cfg2["rules"]["max_choices"] == 6
    assert cfg2["rules"]["tiers"] == ["X", "Y"]
    assert _clb(db) == [("A", "Bóng đá")]


@pytest.mark.parametrize("kem", [True, False])
def test_nhan_ban_cung_ten_thi_them_hau_to(root, kem):
    nguon = ws.tao(root, "A", None)
    assert ws.nhan_ban(root, nguon, "A", kem) == "a-2"


def test_nhan_ban_ten_rong_khong_de_lai_gi(root):
    nguon = ws.tao(root, "A", None)
    with pytest.raises(ValueError):
        ws.nhan_ban(root, nguon, "", True)
    assert [w["slug"] for w in ws.danh_sach(root)] == ["a"]


# ------------------------------------------------------------------ mẫu

def test_mau_dung_san_luon_co_va_luon_dung_dau(root):
    ds = ws.danh_sach_mau(root)
    assert len(ds) == 1
    m = ds[0]
    assert (m["name"], m["builtin"]) == ("Trường học", True)
    assert m["config"]["rules"] == ch.MAC_DINH_TRUONG_HOC["rules"]
    assert m["config"]["labels"] == ch.MAC_DINH_TRUONG_HOC["labels"]
    # sửa bản trả về không làm hỏng mặc định
    m["config"]["rules"]["tiers"].append("x")
    assert ch.MAC_DINH_TRUONG_HOC["rules"]["tiers"] == []


def test_luu_mau_chi_ghi_cau_hinh(root):
    slug = ws.tao(root, "Công ty", {"industry": "company",
                                    "labels": {"slot": {"vi": "Dự án", "en": "Project"}},
                                    "rules": {"max_choices": 3}})
    _them_clb(ws.duong_dan_db(root, slug))

    duong = ws.luu_mau(root, slug, "Mẫu công ty")

    assert duong == os.path.join(root, "templates", "cong-ty.json")
    noi_dung = open(duong, encoding="utf-8").read()
    assert "Bóng đá" not in noi_dung  # không có dữ liệu
    ds = ws.danh_sach_mau(root)
    assert [m["builtin"] for m in ds] == [True, False]
    m = ds[1]
    assert (m["slug"], m["name"]) == ("cong-ty", "Mẫu công ty")
    assert m["config"]["rules"]["max_choices"] == 3
    assert m["config"]["labels"]["slot"] == {"vi": "Dự án", "en": "Project"}


def test_mau_dung_de_tao_workspace_moi(root):
    nguon = ws.tao(root, "Công ty", {"industry": "company", "rules": {"max_choices": 3}})
    ws.luu_mau(root, nguon, "Mẫu")
    mau = ws.danh_sach_mau(root)[1]
    moi = ws.tao(root, "Chi nhánh", mau["config"])
    cfg = ch.doc_cau_hinh(ws.duong_dan_db(root, moi))
    assert (cfg["name"], cfg["industry"], cfg["rules"]["max_choices"]) == ("Chi nhánh", "company", 3)


def test_luu_lai_mau_tu_cung_workspace_cap_nhat_chu_khong_nhan_doi(root):
    slug = ws.tao(root, "A", None)
    ws.luu_mau(root, slug, "Một")
    ws.luu_mau(root, slug, "Hai")
    ds = ws.danh_sach_mau(root)
    assert [m["name"] for m in ds] == ["Trường học", "Hai"]


def test_mau_hong_bi_bo_qua(root):
    slug = ws.tao(root, "A", None)
    ws.luu_mau(root, slug, "Tốt")
    thu_muc = os.path.join(root, "templates")
    open(os.path.join(thu_muc, "hong.json"), "w").write("{khong phai json")
    open(os.path.join(thu_muc, "sai-luat.json"), "w").write(
        json.dumps({"name": "x", "config": {"rules": {"max_choices": 0}}}))
    open(os.path.join(thu_muc, "thieu.json"), "w").write("{}")
    open(os.path.join(thu_muc, "ghi-chu.txt"), "w").write("x")
    assert [m["name"] for m in ws.danh_sach_mau(root)] == ["Trường học", "Tốt"]


def test_luu_mau_ten_rong(root):
    slug = ws.tao(root, "A", None)
    with pytest.raises(ValueError):
        ws.luu_mau(root, slug, " ")
    assert not os.path.exists(os.path.join(root, "templates"))


# ------------------------------------------------------------------ zip

def test_zip_khu_hoi(root, tmp_path):
    cfg = {"industry": "event", "rules": {"max_choices": 7}}
    slug = ws.tao(root, "Sự kiện", cfg)
    db = ws.duong_dan_db(root, slug)
    _them_clb(db)
    open(os.path.join(os.path.dirname(db), "app.db.bak-20260101"), "wb").write(b"x")
    open(os.path.join(os.path.dirname(db), "ghi-chu.txt"), "w", encoding="utf-8").write("giữ")
    dich = str(tmp_path / "ra" / "su-kien.zip")

    assert ws.xuat_zip(root, slug, dich) == dich

    with zipfile.ZipFile(dich) as z:
        assert sorted(z.namelist()) == ["app.db", "ghi-chu.txt"]

    moi = ws.nhap_zip(root, dich)

    assert moi == "su-kien-2"  # slug cũ đã có: đổi tên như tao()
    db2 = ws.duong_dan_db(root, moi)
    assert _clb(db2) == [("A", "Bóng đá")]
    assert ch.doc_cau_hinh(db2) == ch.doc_cau_hinh(db)
    assert open(os.path.join(os.path.dirname(db2), "ghi-chu.txt"), encoding="utf-8").read() == "giữ"
    # không còn thư mục tạm
    assert _ten_thu_muc(root) == ["su-kien", "su-kien-2"]


def test_nhap_zip_vao_root_khac_giu_nguyen_slug(root, tmp_path):
    slug = ws.tao(root, "Sự kiện", None)
    _them_clb(ws.duong_dan_db(root, slug))
    z = str(tmp_path / "x.zip")
    ws.xuat_zip(root, slug, z)
    root2 = str(tmp_path / "may-khac")
    os.makedirs(root2)
    assert ws.nhap_zip(root2, z) == "su-kien"
    assert _clb(ws.duong_dan_db(root2, "su-kien")) == [("A", "Bóng đá")]


def test_xuat_zip_khi_csdl_dang_mo_ghi_van_nhat_quan(root, tmp_path):
    slug = ws.tao(root, "A", None)
    db = ws.duong_dan_db(root, slug)
    _them_clb(db)
    giu = sqlite3.connect(db)  # một kết nối khác đang mở
    try:
        z = str(tmp_path / "a.zip")
        ws.xuat_zip(root, slug, z)
    finally:
        giu.close()
    assert _clb(ws.duong_dan_db(str(tmp_path / "r2"), ws.nhap_zip(str(tmp_path / "r2"), z))) \
        == [("A", "Bóng đá")]


def _zip_voi(duong, muc):
    with zipfile.ZipFile(duong, "w") as z:
        for ten, noi_dung in muc:
            z.writestr(ten, noi_dung)
    return str(duong)


def _db_bytes(tmp_path):
    p = str(tmp_path / "_mau.db")
    init_db(p)
    return open(p, "rb").read()


@pytest.mark.parametrize("ten", [
    "../evil.txt", "a/../../evil.txt", "..\\evil.txt", "a\\..\\..\\evil.txt",
    "/tmp/evil.txt", "\\evil.txt", "C:\\evil.txt", "C:/evil.txt", "ok/..",
])
def test_nhap_zip_tu_choi_zip_slip(root, tmp_path, ten):
    z = _zip_voi(tmp_path / "xau.zip", [("app.db", _db_bytes(tmp_path)), (ten, "x")])
    with pytest.raises(ValueError, match="không an toàn"):
        ws.nhap_zip(root, z)
    # không workspace nào được tạo, không rác, không tệp thoát ra ngoài
    assert ws.danh_sach(root) == []
    assert _ten_thu_muc(root) == []
    assert not os.path.exists(str(tmp_path / "evil.txt"))
    assert not os.path.exists(os.path.join(root, "evil.txt"))


def test_nhap_zip_tu_choi_lien_ket_tuong_trung(root, tmp_path):
    p = str(tmp_path / "lk.zip")
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("app.db", _db_bytes(tmp_path))
        info = zipfile.ZipInfo("lien-ket")
        info.external_attr = (0o120777) << 16
        z.writestr(info, "/etc/passwd")
    with pytest.raises(ValueError, match="liên kết"):
        ws.nhap_zip(root, p)
    assert _ten_thu_muc(root) == []


def test_nhap_zip_thieu_app_db(root, tmp_path):
    z = _zip_voi(tmp_path / "thieu.zip", [("ghi-chu.txt", "x"), ("con/app.db", "x")])
    with pytest.raises(ValueError, match="app.db"):
        ws.nhap_zip(root, z)
    assert _ten_thu_muc(root) == []


def test_nhap_zip_app_db_khong_phai_sqlite(root, tmp_path):
    z = _zip_voi(tmp_path / "hong.zip", [("app.db", "đây không phải sqlite " * 50)])
    with pytest.raises(ValueError, match="CSDL"):
        ws.nhap_zip(root, z)
    assert _ten_thu_muc(root) == []


def test_nhap_zip_khong_phai_zip_hoac_khong_ton_tai(root, tmp_path):
    p = tmp_path / "gia.zip"
    p.write_text("không phải zip", encoding="utf-8")
    with pytest.raises(ValueError):
        ws.nhap_zip(root, str(p))
    with pytest.raises(ValueError):
        ws.nhap_zip(root, str(tmp_path / "khong-co.zip"))
    assert _ten_thu_muc(root) == []


def test_nhap_zip_khong_co_cau_hinh_lay_ten_theo_tep_zip(root, tmp_path):
    z = _zip_voi(tmp_path / "Bản Cũ.zip", [("app.db", _db_bytes(tmp_path))])
    # init_db đã tạo bảng cấu hình nhưng chưa có hàng 'config'
    slug = ws.nhap_zip(root, z)
    assert slug == "ban-cu"
    assert ch.doc_cau_hinh(ws.duong_dan_db(root, slug))["name"] == "Bản Cũ"


def test_nhap_zip_ho_tro_zip_tu_csdl_cu_chua_co_bang_cau_hinh(root, tmp_path):
    p = str(tmp_path / "cu.db")
    init_db(p)
    with _ket_noi(p) as c:
        c.execute("DROP TABLE workspace_settings")
        c.execute("INSERT INTO clubs (club_id, name, capacity) VALUES ('A','A',3)")
        c.commit()
    z = _zip_voi(tmp_path / "cu.zip", [("app.db", open(p, "rb").read())])
    slug = ws.nhap_zip(root, z)
    db = ws.duong_dan_db(root, slug)
    assert _clb(db) == [("A", "A")]
    assert ch.doc_cau_hinh(db)["name"] == "cu"


# ------------------------------------------------------------------ di trú app.db cũ

def _app_db_cu(root, co_sao_luu=True):
    db = os.path.join(root, "app.db")
    init_db(db)
    _them_clb(db, "A", "Cờ vua")
    if co_sao_luu:
        for ts in ("20260101_000000_000001", "20260102_000000_000002"):
            with _ket_noi(db) as src, _ket_noi(db + ".bak-" + ts) as dst:
                src.backup(dst)
    return db


def test_di_chuyen_db_cu_giu_du_lieu_va_chay_mot_lan(root):
    db_cu = _app_db_cu(root)
    # CSDL cũ: chưa từng có hàng cấu hình
    assert ch.doc_cau_hinh(db_cu)["name"] == ""

    assert ws.di_chuyen_db_cu(root) is True

    moi = os.path.join(root, "workspaces", "truong-hoc")
    assert not os.path.exists(db_cu)
    assert sorted(os.listdir(moi)) == ["app.db", "app.db.bak-20260101_000000_000001",
                                       "app.db.bak-20260102_000000_000002"]
    assert _clb(os.path.join(moi, "app.db")) == [("A", "Cờ vua")]
    assert _clb(os.path.join(moi, "app.db.bak-20260101_000000_000001")) == [("A", "Cờ vua")]
    assert ch.doc_cau_hinh(os.path.join(moi, "app.db"))["name"] == "Trường học"
    assert [w["slug"] for w in ws.danh_sach(root)] == ["truong-hoc"]
    assert ws.danh_sach(root)[0]["name"] == "Trường học"

    ghi_chu = open(os.path.join(root, "DA_CHUYEN_SANG_WORKSPACES.txt"), encoding="utf-8").read()
    assert "workspaces" in ghi_chu and "truong-hoc" in ghi_chu
    assert ghi_chu.count("\n") == 1  # một đoạn ngắn

    # không còn thư mục dựng dở
    assert sorted(os.listdir(root)) == ["DA_CHUYEN_SANG_WORKSPACES.txt", "workspaces"]


def test_di_chuyen_db_cu_chay_hai_lan_an_toan(root):
    _app_db_cu(root)
    assert ws.di_chuyen_db_cu(root) is True
    truoc = sorted(os.listdir(os.path.join(root, "workspaces", "truong-hoc")))
    assert ws.di_chuyen_db_cu(root) is False
    assert ws.di_chuyen_db_cu(root) is False
    assert sorted(os.listdir(os.path.join(root, "workspaces", "truong-hoc"))) == truoc
    assert _clb(os.path.join(root, "workspaces", "truong-hoc", "app.db")) == [("A", "Cờ vua")]


def test_di_chuyen_khong_lam_gi_khi_khong_co_app_db(root):
    assert ws.di_chuyen_db_cu(root) is False
    assert os.listdir(root) == []


def test_di_chuyen_khong_dung_vao_app_db_khi_da_co_workspaces(root):
    os.makedirs(os.path.join(root, "workspaces"))
    db_cu = _app_db_cu(root, co_sao_luu=False)
    assert ws.di_chuyen_db_cu(root) is False
    assert os.path.isfile(db_cu)
    assert not os.path.exists(os.path.join(root, "DA_CHUYEN_SANG_WORKSPACES.txt"))


def test_di_chuyen_chon_ca_tep_nhat_ky_cua_sqlite_nhung_khong_tep_la(root):
    # Gọi thẳng hàm chọn tệp: SQLite tự xoá một app.db-journal giả khi mở CSDL.
    _app_db_cu(root, co_sao_luu=False)
    for t in ("app.db-journal", "app.db-wal", "app.db-shm", "app.db.zip", "app.dbx"):
        open(os.path.join(root, t), "wb").write(b"j")
    os.makedirs(os.path.join(root, "app.db.bak-thu-muc"))
    assert ws._tep_can_chuyen(root) == ["app.db", "app.db-journal", "app.db-shm", "app.db-wal"]


def test_di_chuyen_db_hong_van_dem_di_nguyen_trang(root):
    open(os.path.join(root, "app.db"), "wb").write(b"day khong phai sqlite" * 20)
    assert ws.di_chuyen_db_cu(root) is True
    moi = os.path.join(root, "workspaces", "truong-hoc", "app.db")
    assert open(moi, "rb").read() == b"day khong phai sqlite" * 20


def test_di_chuyen_tiep_tuc_sau_khi_hong_giua_chung(root):
    """Dời app.db xong mà chưa kịp đổi tên thư mục: lần sau phải làm nốt."""
    db_cu = _app_db_cu(root, co_sao_luu=False)
    dang_dung = os.path.join(root, "_workspaces_dang_dung", "truong-hoc")
    os.makedirs(dang_dung)
    os.replace(db_cu, os.path.join(dang_dung, "app.db"))

    assert ws.di_chuyen_db_cu(root) is True

    assert _clb(os.path.join(root, "workspaces", "truong-hoc", "app.db")) == [("A", "Cờ vua")]
    assert not os.path.exists(os.path.join(root, "_workspaces_dang_dung"))


# ------------------------------------------------------------------ main.py

@pytest.fixture
def main_mod(monkeypatch, tmp_path):
    import main

    goc = tmp_path / "goc"
    goc.mkdir()
    monkeypatch.setattr(main, "BASE_DIR", str(goc))
    monkeypatch.setattr(sys, "argv", ["main.py"])
    return main


def test_main_khong_co_gi_thi_dung_truong_hoc_mac_dinh(main_mod, tmp_path):
    goc = Path(main_mod.BASE_DIR)
    db = main_mod.khoi_dong_workspace()[0]
    assert db == str(goc / "workspaces" / "truong-hoc" / "app.db")
    assert ch.doc_cau_hinh(db) == {**ch.MAC_DINH_TRUONG_HOC, "name": "Trường học"}
    assert not (goc / "app.db").exists()  # không còn app.db rải cạnh chương trình
    assert main_mod.khoi_dong_workspace()[0] == db      # lần sau mở lại đúng nó
    assert [w["slug"] for w in ws.danh_sach(str(goc))] == ["truong-hoc"]


def test_main_co_app_db_cu_thi_di_tru_roi_mo_no(main_mod, tmp_path):
    goc = Path(main_mod.BASE_DIR)
    _app_db_cu(str(goc), co_sao_luu=False)
    db = main_mod.khoi_dong_workspace()[0]
    assert db == str(goc / "workspaces" / "truong-hoc" / "app.db")
    assert _clb(db) == [("A", "Cờ vua")]
    assert not (goc / "app.db").exists()


def test_main_dung_mot_workspace_thi_mo_no(main_mod, tmp_path):
    goc = Path(main_mod.BASE_DIR)
    slug = ws.tao(str(goc), "Câu lạc bộ", None)
    assert main_mod.khoi_dong_workspace()[0] == ws.duong_dan_db(str(goc), slug)
    assert [w["slug"] for w in ws.danh_sach(str(goc))] == ["cau-lac-bo"]  # không tạo thêm


def test_main_nhieu_workspace_thi_mo_cai_sua_gan_nhat(main_mod, tmp_path):
    goc = Path(main_mod.BASE_DIR)
    root = str(goc)
    cu = ws.tao(root, "Cũ", None)
    moi = ws.tao(root, "Mới", None)
    os.utime(ws.duong_dan_db(root, cu), (1_000_000_000, 1_000_000_000))
    assert main_mod.khoi_dong_workspace()[0] == ws.duong_dan_db(root, moi)


def test_main_co_duong_dan_argv_thi_giu_hanh_vi_cu(main_mod, monkeypatch, tmp_path):
    goc = Path(main_mod.BASE_DIR)
    db = str(goc / "rieng" / "x.db")
    monkeypatch.setattr(sys, "argv", ["main.py", db])
    assert main_mod.khoi_dong_workspace()[0] == os.path.abspath(db)
    # không đụng gì tới đĩa: không workspaces, không di trú
    assert not (goc / "workspaces").exists()
    assert not (goc / "rieng").exists()


def test_main_co_app_db_canh_chuong_trinh_va_argv_thi_khong_di_tru(main_mod, monkeypatch, tmp_path):
    goc = Path(main_mod.BASE_DIR)
    _app_db_cu(str(goc), co_sao_luu=False)
    monkeypatch.setattr(sys, "argv", ["main.py", str(goc / "app.db")])
    main_mod.khoi_dong_workspace()[0]
    assert (goc / "app.db").exists()
    assert not (goc / "workspaces").exists()


def test_main_mo_man_hinh_chinh_voi_workspace(main_mod, monkeypatch, tmp_path):
    goc = Path(main_mod.BASE_DIR)
    mo = []
    monkeypatch.setattr(main_mod, "_show_ui", lambda title, page, api, **k: mo.append((page, api)))
    main_mod.main()
    assert mo[0][0] == "index.html"
    assert mo[0][1].db_path == str(goc / "workspaces" / "truong-hoc" / "app.db")


def test_main_workspace_hong_thi_mo_man_hinh_phuc_hoi(main_mod, monkeypatch, tmp_path):
    goc = Path(main_mod.BASE_DIR)
    root = str(goc)
    slug = ws.tao(root, "Hỏng", None)
    db = ws.duong_dan_db(root, slug)
    open(db, "wb").write(b"day khong phai sqlite" * 20)
    mo = []
    monkeypatch.setattr(main_mod, "_show_ui", lambda title, page, api, **k: mo.append((page, api)))
    main_mod.main()
    assert mo[0][0] == "recovery.html"
