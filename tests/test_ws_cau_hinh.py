"""Cấu hình workspace (cau_hinh_ws.py): mặc định, vòng đọc-ghi, kiểm đầu vào, nhãn."""

import copy
import json
import sqlite3

import pytest

import cau_hinh_ws as ch
from rbda_priority_pipeline import (
    TRAN_CLB_THI_MOI_BUOI,
    TRAN_NGUYEN_VONG_MOI_BUOI,
    connect_db,
    init_db,
)


def _co_bang(db):
    conn = sqlite3.connect(db)
    try:
        return conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='workspace_settings'"
        ).fetchone() is not None
    finally:
        conn.close()


def _ghi_tho(db, gia_tri):
    """Ghi thẳng hàng 'config' (bỏ qua ghi_cau_hinh) để dựng dữ liệu hỏng/thiếu."""
    conn = connect_db(db)
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS workspace_settings (key TEXT PRIMARY KEY, value TEXT)")
        conn.execute("INSERT OR REPLACE INTO workspace_settings VALUES ('config', ?)", (gia_tri,))
        conn.commit()
    finally:
        conn.close()


@pytest.fixture
def db(tmp_path):
    p = str(tmp_path / "app.db")
    init_db(p)
    return p


@pytest.fixture
def db_cu(tmp_path):
    """CSDL dựng bằng bản cũ: có bảng nghiệp vụ nhưng CHƯA có workspace_settings."""
    p = str(tmp_path / "cu.db")
    init_db(p)
    conn = sqlite3.connect(p)
    conn.execute("DROP TABLE workspace_settings")
    conn.commit()
    conn.close()
    return p


# ---------------------------------------------------------------- mặc định

def test_mac_dinh_lay_tran_tu_thuat_toan():
    luat = ch.MAC_DINH_TRUONG_HOC["rules"]
    assert luat["max_choices"] == TRAN_NGUYEN_VONG_MOI_BUOI == 10
    assert luat["max_tests"] == TRAN_CLB_THI_MOI_BUOI == 5
    assert (luat["priority"], luat["tier_mode"], luat["score_scope"], luat["tiers"]) == (
        "score", "reserve", "per_slot", [])
    assert ch.MAC_DINH_TRUONG_HOC["industry"] == "school"
    assert set(ch.MAC_DINH_TRUONG_HOC["labels"]) == set(ch.DANH_TU)


def test_csdl_moi_cho_mac_dinh(db):
    assert _co_bang(db)
    assert ch.doc_cau_hinh(db) == ch.MAC_DINH_TRUONG_HOC


def test_csdl_cu_chua_co_bang_cho_mac_dinh_va_khong_tao_bang(db_cu):
    assert not _co_bang(db_cu)
    assert ch.doc_cau_hinh(db_cu) == ch.MAC_DINH_TRUONG_HOC
    assert not _co_bang(db_cu)  # đọc không đụng tới CSDL


def test_init_db_them_bang_vao_csdl_cu(db_cu):
    init_db(db_cu)
    assert _co_bang(db_cu)
    init_db(db_cu)  # chạy lại không hỏng
    assert ch.doc_cau_hinh(db_cu) == ch.MAC_DINH_TRUONG_HOC


def test_tep_chua_ton_tai_cho_mac_dinh_va_khong_tao_tep(tmp_path):
    p = tmp_path / "khong_co.db"
    assert ch.doc_cau_hinh(str(p)) == ch.MAC_DINH_TRUONG_HOC
    assert not p.exists()


def test_doc_tra_ban_sao_khong_dong_vao_mac_dinh(db):
    cfg = ch.doc_cau_hinh(db)
    cfg["rules"]["tiers"].append("x")
    cfg["labels"]["person"]["vi"] = "Sửa"
    assert ch.MAC_DINH_TRUONG_HOC["rules"]["tiers"] == []
    assert ch.MAC_DINH_TRUONG_HOC["labels"]["person"]["vi"] == "Học sinh"
    assert ch.doc_cau_hinh(db) == ch.MAC_DINH_TRUONG_HOC


# ------------------------------------------------------------ vòng đọc-ghi

def test_ghi_roi_doc_giong_nhau(db):
    cfg = copy.deepcopy(ch.MAC_DINH_TRUONG_HOC)
    cfg.update(name="Công ty ABC", industry="company")
    cfg["labels"]["person"] = {"vi": "Nhân viên", "en": "Employee"}
    cfg["rules"].update(max_choices=3, max_tests=None, priority="score+tier",
                        tier_mode="strict", score_scope="per_person",
                        tiers=["Cấp cao", "Cấp thấp"])
    ghi = ch.ghi_cau_hinh(db, cfg)
    assert ghi == cfg
    doc = ch.doc_cau_hinh(db)
    assert doc == cfg
    assert doc["rules"]["max_tests"] is None  # None sống sót qua JSON, không rơi về 5


def test_ghi_de_len_lan_truoc(db):
    ch.ghi_cau_hinh(db, {"name": "A"})
    ch.ghi_cau_hinh(db, {"name": "B"})
    assert ch.doc_cau_hinh(db)["name"] == "B"
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT COUNT(*) FROM workspace_settings").fetchone()[0] == 1
    conn.close()


def test_ghi_vao_csdl_cu_tu_dung_bang(db_cu):
    ch.ghi_cau_hinh(db_cu, {"name": "Cũ"})
    assert _co_bang(db_cu)
    assert ch.doc_cau_hinh(db_cu)["name"] == "Cũ"


def test_ghi_luu_ban_day_du_de_doi_mac_dinh_khong_doi_luat(db):
    ch.ghi_cau_hinh(db, {"name": "A"})
    conn = sqlite3.connect(db)
    luu = json.loads(conn.execute("SELECT value FROM workspace_settings").fetchone()[0])
    conn.close()
    assert luu["rules"]["max_choices"] == TRAN_NGUYEN_VONG_MOI_BUOI
    assert set(luu["labels"]) == set(ch.DANH_TU)


# --------------------------------------------------------- trộn một phần

def test_cau_hinh_mot_phan_tron_voi_mac_dinh(db):
    _ghi_tho(db, json.dumps({"name": "X", "rules": {"max_choices": 4}}))
    cfg = ch.doc_cau_hinh(db)
    assert cfg["name"] == "X"
    assert cfg["rules"]["max_choices"] == 4
    assert cfg["rules"]["max_tests"] == TRAN_CLB_THI_MOI_BUOI
    assert cfg["rules"]["priority"] == "score"
    assert cfg["labels"] == ch.MAC_DINH_TRUONG_HOC["labels"]
    assert cfg["industry"] == "school"


def test_nhan_mot_phan_chi_doi_danh_tu_duoc_nhac_toi(db):
    _ghi_tho(db, json.dumps({"labels": {"slot": {"vi": "Dự án", "en": "Project"}}}))
    cfg = ch.doc_cau_hinh(db)
    assert cfg["labels"]["slot"] == {"vi": "Dự án", "en": "Project"}
    assert cfg["labels"]["person"] == ch.MAC_DINH_TRUONG_HOC["labels"]["person"]


def test_chi_dat_vi_thi_en_roi_ve_vi_khong_phai_en_mac_dinh(db):
    _ghi_tho(db, json.dumps({"labels": {"person": {"vi": "Nhân viên"}}}))
    assert ch.doc_cau_hinh(db)["labels"]["person"] == {"vi": "Nhân viên", "en": "Nhân viên"}
    cfg = ch.ghi_cau_hinh(db, {"labels": {"person": {"vi": "Khách"}}})
    assert cfg["labels"]["person"] == {"vi": "Khách", "en": "Khách"}


def test_max_tests_null_trong_json_la_khong_gioi_han(db):
    _ghi_tho(db, json.dumps({"rules": {"max_tests": None}}))
    assert ch.doc_cau_hinh(db)["rules"]["max_tests"] is None


# ------------------------------------------------------------ dữ liệu hỏng

@pytest.mark.parametrize("hong", [
    "{khong phai json",
    "",
    "[]",
    "123",
    '"chuoi"',
    "null",
    json.dumps({"rules": {"max_choices": "abc"}}),       # JSON đúng, giá trị sai
    json.dumps({"rules": {"priority": "bậy"}}),
    json.dumps({"rules": []}),
])
def test_json_hong_cho_mac_dinh(db, hong):
    _ghi_tho(db, hong)
    assert ch.doc_cau_hinh(db) == ch.MAC_DINH_TRUONG_HOC


def test_gia_tri_null_trong_hang_cho_mac_dinh(db):
    _ghi_tho(db, None)
    assert ch.doc_cau_hinh(db) == ch.MAC_DINH_TRUONG_HOC


# ------------------------------------------------------------------- kiểm

def _sua(**luat):
    cfg = copy.deepcopy(ch.MAC_DINH_TRUONG_HOC)
    cfg["rules"].update(luat)
    return cfg


@pytest.mark.parametrize("gia_tri", [0, -1, 21, 100, "5", 5.0, None, True, [3]])
def test_max_choices_sai(db, gia_tri):
    with pytest.raises(ValueError, match="max_choices"):
        ch.ghi_cau_hinh(db, _sua(max_choices=gia_tri))


@pytest.mark.parametrize("gia_tri", [1, 10, 20])
def test_max_choices_dung(db, gia_tri):
    assert ch.ghi_cau_hinh(db, _sua(max_choices=gia_tri))["rules"]["max_choices"] == gia_tri


@pytest.mark.parametrize("gia_tri", [-1, 21, "5", 2.5, True])
def test_max_tests_sai(db, gia_tri):
    with pytest.raises(ValueError, match="max_tests"):
        ch.ghi_cau_hinh(db, _sua(max_tests=gia_tri))


@pytest.mark.parametrize("gia_tri", [0, 5, 20, None])
def test_max_tests_dung(db, gia_tri):
    assert ch.ghi_cau_hinh(db, _sua(max_tests=gia_tri))["rules"]["max_tests"] == gia_tri


@pytest.mark.parametrize("khoa, gia_tri", [
    ("priority", "rank"), ("priority", ""), ("priority", None),
    ("tier_mode", "soft"), ("tier_mode", "Strict"),
    ("score_scope", "global"), ("score_scope", 1),
])
def test_gia_tri_liet_ke_sai(db, khoa, gia_tri):
    with pytest.raises(ValueError, match=khoa):
        ch.ghi_cau_hinh(db, _sua(**{khoa: gia_tri}))


@pytest.mark.parametrize("khoa, gia_tri", [
    ("priority", "tier"), ("priority", "score+tier"),
    ("tier_mode", "strict"), ("score_scope", "per_person"),
])
def test_gia_tri_liet_ke_dung(db, khoa, gia_tri):
    assert ch.ghi_cau_hinh(db, _sua(**{khoa: gia_tri}))["rules"][khoa] == gia_tri


def test_industry_sai(db):
    with pytest.raises(ValueError, match="industry"):
        ch.ghi_cau_hinh(db, {"industry": "bệnh viện"})


@pytest.mark.parametrize("vi", ["", "   ", None, 5])
def test_nhan_vi_rong_hoac_sai_kieu(db, vi):
    cfg = copy.deepcopy(ch.MAC_DINH_TRUONG_HOC)
    cfg["labels"]["group"]["vi"] = vi
    with pytest.raises(ValueError, match=r"labels\.group\.vi"):
        ch.ghi_cau_hinh(db, cfg)


def test_nhan_thieu_vi_khi_chi_gui_en(db):
    # Gửi riêng en cho danh từ: vi mặc định còn nguyên, nên không lỗi.
    cfg = ch.ghi_cau_hinh(db, {"labels": {"score": {"en": "Points"}}})
    assert cfg["labels"]["score"] == {"vi": "Điểm", "en": "Points"}


def test_nhan_en_sai_kieu(db):
    with pytest.raises(ValueError, match=r"labels\.slot\.en"):
        ch.ghi_cau_hinh(db, {"labels": {"slot": {"vi": "Dự án", "en": 3}}})


def test_danh_tu_la(db):
    with pytest.raises(ValueError, match="labels"):
        ch.ghi_cau_hinh(db, {"labels": {"banana": {"vi": "Chuối", "en": "Banana"}}})


def test_khoa_la_o_cap_tren_va_trong_luat(db):
    with pytest.raises(ValueError, match="max_choice"):
        ch.ghi_cau_hinh(db, {"rules": {"max_choice": 3}})  # gõ sai tên khoá
    with pytest.raises(ValueError, match="bogus"):
        ch.ghi_cau_hinh(db, {"bogus": 1})


@pytest.mark.parametrize("sai", ["abc", ["A", ""], ["A", 3], ["A", "A"], ["A", " A "]])
def test_tiers_sai(db, sai):
    with pytest.raises(ValueError, match="tiers"):
        ch.ghi_cau_hinh(db, _sua(tiers=sai))


def test_tiers_giu_thu_tu_va_cat_khoang_trang(db):
    cfg = ch.ghi_cau_hinh(db, _sua(tiers=["  Khối 12 ", "Khối 11"]))
    assert cfg["rules"]["tiers"] == ["Khối 12", "Khối 11"]


@pytest.mark.parametrize("sai", [None, [], "x", 3])
def test_cau_hinh_khong_phai_dict(db, sai):
    with pytest.raises(ValueError):
        ch.ghi_cau_hinh(db, sai)


def test_mat_hieu_luc_khi_loi_khong_ghi_gi(db):
    ch.ghi_cau_hinh(db, {"name": "Giữ"})
    with pytest.raises(ValueError):
        ch.ghi_cau_hinh(db, {"name": "Mất", "rules": {"max_choices": 0}})
    assert ch.doc_cau_hinh(db)["name"] == "Giữ"


def test_ghi_khong_sua_dict_cua_nguoi_goi(db):
    cfg = {"labels": {"person": {"vi": "  Khách  "}}}
    goc = copy.deepcopy(cfg)
    ch.ghi_cau_hinh(db, cfg)
    assert cfg == goc


# ------------------------------------------------------------- nhan()

def test_nhan_theo_ngon_ngu():
    cfg = ch.MAC_DINH_TRUONG_HOC
    assert ch.nhan(cfg, "person", "vi") == "Học sinh"
    assert ch.nhan(cfg, "person", "en") == "Student"
    assert ch.nhan(cfg, "group", "en") == "Priority group"


def test_nhan_en_rong_roi_ve_vi_khi_ghi(db):
    cfg = copy.deepcopy(ch.MAC_DINH_TRUONG_HOC)
    cfg["labels"]["slot"] = {"vi": "Phòng", "en": ""}
    ch.ghi_cau_hinh(db, cfg)
    doc = ch.doc_cau_hinh(db)
    assert doc["labels"]["slot"] == {"vi": "Phòng", "en": "Phòng"}
    assert ch.nhan(doc, "slot", "en") == "Phòng"


def test_nhan_en_rong_roi_ve_vi_khi_tra_cuu():
    cfg = {"labels": {"slot": {"vi": "Phòng", "en": ""}, "person": {"vi": "Khách"}}}
    assert ch.nhan(cfg, "slot", "en") == "Phòng"
    assert ch.nhan(cfg, "person", "en") == "Khách"


def test_nhan_ngon_ngu_la_roi_ve_vi():
    assert ch.nhan(ch.MAC_DINH_TRUONG_HOC, "session", "fr") == "Buổi"


def test_nhan_cau_hinh_thieu_nhan_roi_ve_mac_dinh():
    assert ch.nhan({}, "score", "en") == "Score"
    assert ch.nhan({"labels": {}}, "score", "vi") == "Điểm"


def test_nhan_danh_tu_la():
    with pytest.raises(ValueError):
        ch.nhan(ch.MAC_DINH_TRUONG_HOC, "banana", "vi")
