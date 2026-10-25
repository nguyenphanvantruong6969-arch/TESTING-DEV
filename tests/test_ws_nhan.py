"""Từ vựng của workspace trong câu chữ (TASK 4): nhan_ws.py, i18n.js, i18n_errors.py.

Lời hứa lớn nhất: với MẶC ĐỊNH TRƯỜNG HỌC, mọi chuỗi hiện ra GIỐNG HỆT trước khi có
workspace. `tests/du_lieu_ws/chuoi_truoc_khi_co_nhan.json` là ảnh chụp TOÀN BỘ chuỗi
(giao diện vi/en + bảng lỗi) NGAY TRƯỚC khi đưa chỗ giữ `{person}`, `{slot}`… vào. Test
dưới đây dựng lại từng chuỗi bằng mã THẬT và so với ảnh chụp — không phải mẫu thử.
"""

import json
import os
import re
import shutil
import subprocess

import pytest

import nhan_ws
from i18n_errors import MESSAGES, format_all, format_message

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANH_CHUP = os.path.join(GOC, "tests", "du_lieu_ws", "chuoi_truoc_khi_co_nhan.json")

# Công ty: hai danh từ người dùng đặt trong yêu cầu, ba còn lại tự chọn.
CONG_TY = {
    "person": {"vi": "Nhân viên", "en": "Employee"},
    "slot": {"vi": "Dự án", "en": "Project"},
    "session": {"vi": "Ca", "en": "Shift"},
    "group": {"vi": "Nhóm dự án", "en": "Project team"},
    "score": {"vi": "Điểm", "en": "Score"},
}

node = shutil.which("node")
can_node = pytest.mark.skipif(not node, reason="node is not available in this environment")


# Hai thay đổi có chủ ý ngoài chỗ giữ danh từ (đều không đổi chữ hiện ra với mặc định):
#   1. tham số `score` (giá trị ô điểm người dùng gõ) -> `diem_goc`, vì `{score}` nay là nhãn
#      "Điểm" và một tham số trùng tên sẽ che mất nó;
#   2. con số trần ghi cứng trong bốn thông báo -> tham số `{tran}` (trần nay do workspace đặt).
TRAN_MAC_DINH = {"pref_too_many": 10, "pref_too_many_buoi": 10,
                 "thi_too_many": 5, "thi_too_many_buoi": 5}


# Mã thêm SAU ảnh chụp ngoài nhóm ws_*: điểm theo người ở Sổ nhập (TASK 5); luật xếp, chấm
# điểm theo người và cảnh báo sức khoẻ dữ liệu của chúng (TASK 6). Chỉ THÊM mã, không đổi mã cũ.
MA_MOI_SAU_ANH_CHUP = {
    "so_nhap_diem_ca_nhan_sai", "scoring_not_per_person", "health_person_score_none",
    "health_person_score_missing", "health_tier_missing", "health_tiers_empty",
    # Vòng sửa lỗi cuối: điểm theo CLB sai chế độ (chấm tay, CSV, cột trong sổ).
    "scoring_not_per_slot", "csv_score_ignored_mode", "so_nhap_diem_sai_che_do",
    # Điểm Wharton (mục A13, vòng 1): lỗi kiểm hồ sơ và cảnh báo vắng thi.
    "wharton_nguyen_vong_chua_xep", "wharton_chua_dung_het", "wharton_vuot_ngan_sach",
    "wharton_diem_khong_hop_le", "wharton_ngoai_tap", "wharton_tang_lech",
    "wharton_vang_thi",
    # Vòng 2: nhập CSV / Sổ, kiosk, chặn chạy xếp, sức khoẻ dữ liệu.
    "csv_wp_khong_hop_le", "csv_wp_khong_co_nguyen_vong", "csv_wp_bo_qua", "wharton_chua_bat",
    "wharton_ho_so_chua_hop_le", "health_wharton_chua_hop_le", "health_wharton_vang_thi",
    "error_saving_wharton",
    # Vòng 3 (A13.3): khoá, mở khoá, xoá và quản lý điểm Wharton ở thẻ Quản lý.
    "wharton_da_khoa", "wharton_mo_khoa_sai_xac_nhan", "wharton_xoa_sai_xac_nhan",
    "wharton_da_xoa", "wharton_da_mo_khoa", "error_wharton_quan_ly",
}


def _truoc_da_doi_ten_tham_so(chuoi, ma=None):
    chuoi = chuoi.replace("{score}", "{diem_goc}")
    if ma in TRAN_MAC_DINH:
        chuoi, n = re.subn(r"\b%d\b" % TRAN_MAC_DINH[ma], "{tran}", chuoi)
        assert n == 1, (ma, chuoi)
    return chuoi


@pytest.fixture(scope="module")
def anh_chup():
    with open(ANH_CHUP, encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------ nhan_ws.py

@pytest.mark.parametrize("mau, vi, en", [
    ("{person}", "Học sinh", "Student"),
    ("{person_l}", "học sinh", "student"),
    ("{person_p}", "Học sinh", "Students"),
    ("{person_pl}", "học sinh", "students"),
    ("{slot}", "Câu lạc bộ", "Club"),
    ("{slot_l}", "câu lạc bộ", "club"),
    ("{slot_s}", "CLB", "Club"),            # viết tắt chỉ có ở tiếng Việt
    ("{slot_sl}", "CLB", "club"),           # "CLB" không bị hạ thành "clb"
    ("{slot_la}", "câu lạc bộ", "a club"),  # mạo từ chỉ có ở tiếng Anh
    ("{slot_lac}", "Câu lạc bộ", "A club"),
    ("{session_pl}", "buổi", "sessions"),
    ("{group}", "Nhóm ưu tiên", "Priority group"),
    ("{group_pl}", "nhóm ưu tiên", "priority groups"),
    ("{score_l}", "điểm", "score"),
])
def test_cho_giu_voi_mac_dinh_truong_hoc(mau, vi, en):
    assert nhan_ws.dien(mau, None, "vi") == vi
    assert nhan_ws.dien(mau, None, "en") == en


def test_cong_ty_vi_va_en():
    assert nhan_ws.dien("{person} / {person_l} / {person_pl}", CONG_TY, "vi") == \
        "Nhân viên / nhân viên / nhân viên"
    assert nhan_ws.dien("{person} / {person_l} / {person_pl}", CONG_TY, "en") == \
        "Employee / employee / employees"
    assert nhan_ws.dien("Mã {slot_sl}", CONG_TY, "vi") == "Mã dự án"   # không viết tắt: hạ thường
    assert nhan_ws.dien("Mã {slot_s}", None, "vi") == "Mã CLB"          # mặc định: viết tắt
    assert nhan_ws.dien("{group_pl}", CONG_TY, "en") == "project teams"
    assert nhan_ws.dien("Add {person_la} to {slot_la}", CONG_TY, "en") == \
        "Add an employee to a project"


def test_en_trong_hay_thieu_roi_ve_vi():
    nhan = {"person": {"vi": "Nhân viên", "en": ""}, "slot": {"vi": "Dự án"}}
    assert nhan_ws.dien("{person_pl} / {slot}", nhan, "en") == "nhân viên / Dự án"
    # và nhãn không khai thì lấy mặc định trường học
    assert nhan_ws.dien("{score}", nhan, "en") == "Score"
    assert nhan_ws.dien("{score}", {}, "vi") == "Điểm"


@pytest.mark.parametrize("danh_tu, so_it, so_nhieu", [
    ("Student", "student", "students"),
    ("Company", "company", "companies"),    # phụ âm + y
    ("Day", "day", "days"),                 # nguyên âm + y
    ("Class", "class", "classes"),
    ("Branch", "branch", "branches"),
    ("Box", "box", "boxes"),
    ("Priority group", "priority group", "priority groups"),
])
def test_so_nhieu_tieng_anh(danh_tu, so_it, so_nhieu):
    nhan = {"person": {"vi": "x", "en": danh_tu}}
    assert nhan_ws.dien("{person_l}", nhan, "en") == so_it
    assert nhan_ws.dien("{person_pl}", nhan, "en") == so_nhieu


def test_chu_viet_tat_cua_nhan_khong_bi_ha_thuong():
    nhan = {"group": {"vi": "HR", "en": "HR"}}
    assert nhan_ws.dien("{group_l}", nhan, "vi") == "HR"
    assert nhan_ws.dien("{group_pl}", nhan, "en") == "HRs"


def test_chi_cham_cho_giu_danh_tu_con_lai_de_nguyen():
    mau = "{n} {person_l} ở {club_id} {unknown} {person_x} {{person}}"
    kq = nhan_ws.dien(mau, None, "vi")
    assert kq == "{n} học sinh ở {club_id} {unknown} {person_x} {học sinh}" \
        or kq == "{n} học sinh ở {club_id} {unknown} {person_x} {Học sinh}"
    assert nhan_ws.dien("khong co gi", None) == "khong co gi"
    assert nhan_ws.dien(None, None) is None


def test_nhan_co_dau_ngoac_khong_pha_str_format():
    nhan = {"person": {"vi": "A{b}", "en": "A{b}"}}
    # format_message chạy str.format SAU khi điền nhãn; ngoặc trong nhãn phải sống sót
    assert MESSAGES["student_not_found"]["vi"]
    kq = format_message("student_not_found", {"student_id": "S1"}, "vi", nhan)
    assert kq == "Không tìm thấy a{b} S1."


def test_mac_dinh_la_mot_nguon_duy_nhat():
    import cau_hinh_ws
    assert cau_hinh_ws.MAC_DINH_TRUONG_HOC["labels"] == nhan_ws.NHAN_MAC_DINH
    assert cau_hinh_ws.DANH_TU == nhan_ws.DANH_TU


# ------------------------------------------------------------------ bảng lỗi (Python)

def test_moi_ma_loi_mac_dinh_giong_het_anh_chup(anh_chup):
    """Điền nhãn mặc định vào MESSAGES rồi so với bản chụp TRƯỚC khi có chỗ giữ."""
    lech = []
    for ma, truoc in anh_chup["loi"].items():
        assert ma in MESSAGES, ma
        for lang in ("vi", "en"):
            sau = nhan_ws.dien(MESSAGES[ma][lang], None, lang)
            if sau != _truoc_da_doi_ten_tham_so(truoc[lang], ma):
                lech.append((ma, lang, truoc[lang][:80], sau[:80]))
    assert not lech, lech
    # và không thêm/bớt mã nào ngoài các mã workspace đã ghi sau ảnh chụp
    moi = set(MESSAGES) - set(anh_chup["loi"])
    assert all(m.startswith("ws_") or m in MA_MOI_SAU_ANH_CHUP for m in moi), moi


def test_format_message_mac_dinh_khong_doi(anh_chup):
    for ma, truoc in anh_chup["loi"].items():
        for lang in ("vi", "en"):
            mong_doi = _truoc_da_doi_ten_tham_so(truoc[lang], ma)
            tham_so = {k: "X" for k in re.findall(r"\{(\w+)\}", mong_doi)}
            if ma in TRAN_MAC_DINH:   # hiện lại đúng con số cũ
                tham_so["tran"] = TRAN_MAC_DINH[ma]
                mong_doi = truoc[lang]
            try:
                mong_doi = mong_doi.format(**tham_so)
            except Exception:
                pass
            assert format_message(ma, tham_so, lang) == mong_doi, (ma, lang)


def test_format_message_cong_ty():
    kq = format_message("student_not_found", {"student_id": "NV01"}, "vi", CONG_TY)
    assert kq == "Không tìm thấy nhân viên NV01."
    kq = format_message("student_not_found", {"student_id": "NV01"}, "en", CONG_TY)
    assert kq == "Employee NV01 not found." or "employee" in kq.lower()
    loi = [{"code": "club_not_found", "params": {"club_id": "P1"}}, "chuoi tho"]
    ra = format_all(loi, "vi", CONG_TY)
    assert ra[0] == "Không tìm thấy dự án P1." and ra[1] == "chuoi tho"


def test_tham_so_diem_goc_khong_dung_ten_danh_tu():
    """Tham số tên `score` sẽ che chỗ giữ `{score}` của nhãn — nên đã đổi tên."""
    for ma in ("score_negative", "score_not_a_number", "csv_score_negative",
               "csv_score_not_a_number"):
        for lang in ("vi", "en"):
            assert "{diem_goc}" in MESSAGES[ma][lang], (ma, lang)
    import re
    for ma, d in MESSAGES.items():
        for lang in ("vi", "en"):
            for ten in re.findall(r"\{(person|slot|session|group|score)\}", d[lang]):
                # được phép: là DANH TỪ, và không có lời gọi err() nào truyền tham số trùng tên
                assert ten in nhan_ws.DANH_TU


def test_khong_co_loi_goi_err_nao_truyen_tham_so_trung_ten_danh_tu():
    import glob
    import re
    for tep in glob.glob(os.path.join(GOC, "api*.py")) + [
            os.path.join(GOC, "rbda_priority_pipeline.py"), os.path.join(GOC, "so_nhap.py")]:
        nguon = open(tep, encoding="utf-8").read()
        for m in re.finditer(r"err\(\s*[\"'](\w+)[\"']([^)]*)\)", nguon):
            for ten in nhan_ws.DANH_TU:
                assert not re.search(r"[,\s]%s\s*=" % ten, m.group(2)), (tep, m.group(0))


# ------------------------------------------------------------------ i18n.js (qua node)

_HAM_CHAY = r"""
global.window = {};
require(process.argv[1]);                 // i18n_loi.js
require(process.argv[2]);                 // i18n.js
window.dispatchEvent = () => {};
const I = window.I18N;
const lenh = JSON.parse(process.argv[3]);
const kq = {};
(lenh.nhan ? I.setLabels(lenh.nhan) : null);
for (const lang of lenh.langs || ["vi", "en"]) {
  I.setLang(lang);
  kq[lang] = {};
  for (const khoa of lenh.khoa || []) kq[lang][khoa] = I.t(khoa, lenh.tham_so || {});
  kq[lang]._fill = (lenh.mau || []).map((m) => I.fill(m, lenh.tham_so || {}));
  kq[lang]._loi = (lenh.loi || []).map((e) => I.translateError(e));
}
process.stdout.write(JSON.stringify(kq));
"""

# Không có document/localStorage: i18n.js phải chạy được ở đây (nó đã tự bọc try/catch).
_STUB = ("global.document = {getElementById: () => null, querySelectorAll: () => [],"
         " documentElement: {}}; global.localStorage = undefined;")


def _chay_js(lenh):
    ra = subprocess.run(
        [node, "-e", _STUB + _HAM_CHAY, "--", os.path.join(GOC, "i18n_loi.js"),
         os.path.join(GOC, "i18n.js"), json.dumps(lenh)],
        capture_output=True, text=True, check=True, encoding="utf-8")
    return json.loads(ra.stdout)


@can_node
def test_moi_chuoi_giao_dien_mac_dinh_giong_het_anh_chup(anh_chup):
    """TOÀN BỘ UI_STRINGS (vi + en) với mặc định trường học == ảnh chụp trước thay đổi."""
    khoa = sorted(anh_chup["ui"]["vi"])
    ra = _chay_js({"khoa": khoa})
    lech = []
    for lang in ("vi", "en"):
        for k in khoa:
            if ra[lang][k] != anh_chup["ui"][lang][k]:
                lech.append((lang, k, anh_chup["ui"][lang][k][:70], ra[lang][k][:70]))
    assert not lech, lech[:10]
    assert len(khoa) > 450  # có đọc đủ bảng, không phải bảng rỗng


# 20 chuỗi tiêu biểu: đủ năm danh từ, vi + en, số ít/số nhiều, mạo từ, viết tắt.
MAU_20 = [
    "brand_title", "nav_admin", "nav_scoring", "label_students", "label_clubs",
    "pipeline_desc", "admin_desc", "chua_co_cho_desc", "toast_run_success",
    "feedback_scores_saved", "fallback_step1_hint", "buoi_chua_chia", "tkb_desc",
    "th_score", "th_student_id", "th_club_id", "xuat_opt_ket_qua",
    "scoring_desc", "toast_reset_done_removed", "page_title",
]


@can_node
def test_mau_20_chuoi_mac_dinh_giong_het_truoc_day(anh_chup):
    assert len(set(MAU_20)) == 20
    tham_so = {"n": 3, "m": 2, "n_matched": 8, "n_total": 9, "rounds": 2,
               "student_id": "HS01", "club_id": "A", "p": 40}
    ra = _chay_js({"khoa": MAU_20, "tham_so": tham_so})
    for lang in ("vi", "en"):
        for k in MAU_20:
            mong_doi = anh_chup["ui"][lang][k]
            for ten, gia_tri in tham_so.items():
                mong_doi = mong_doi.replace("{%s}" % ten, str(gia_tri))
            assert ra[lang][k] == mong_doi, (lang, k)


@can_node
def test_giao_dien_cong_ty(anh_chup):
    ra = _chay_js({"khoa": ["label_students", "nav_scoring", "toast_run_success", "th_score",
                            "admin_desc", "fallback_step0_title", "pipeline_desc"],
                   "tham_so": {"n_matched": 8, "n_total": 9, "rounds": 2},
                   "nhan": CONG_TY})
    assert ra["vi"]["label_students"] == "nhân viên"
    assert ra["en"]["label_students"] == "employees"
    assert ra["vi"]["th_score"] == "Điểm" and ra["en"]["th_score"] == "Score"
    assert ra["vi"]["toast_run_success"] == "Sắp xếp xong: 8/9 nhân viên có dự án, sau 2 vòng."
    assert ra["en"]["toast_run_success"] == \
        "Allocation finished: 8/9 employees placed in 2 round(s)."
    assert ra["en"]["fallback_step0_title"] == "Find or create an employee"   # a -> an
    assert "học sinh" not in ra["vi"]["pipeline_desc"] and "CLB" not in ra["vi"]["pipeline_desc"]
    assert ra["vi"]["pipeline_desc"] == \
        "Kiểm tra dữ liệu, bốc thăm, xếp nhân viên vào dự án và xuất kết quả."


@can_node
def test_giao_dien_en_trong_roi_ve_vi():
    nhan = {"person": {"vi": "Nhân viên", "en": ""}, "slot": {"vi": "Dự án", "en": "  "}}
    ra = _chay_js({"khoa": ["label_students", "label_clubs"], "nhan": nhan})
    assert ra["en"]["label_students"] == "nhân viên"
    assert ra["en"]["label_clubs"] == "dự án"
    assert ra["vi"]["label_students"] == "nhân viên"


@can_node
def test_js_va_python_dien_nhu_nhau():
    mau = ["{person}", "{person_l}", "{person_p}", "{person_pl}", "{slot_s}", "{slot_sl}",
           "{slot_la}", "{slot_lac}", "{session_pl}", "{group_l}", "{score_pl}",
           "x {n} {person_pl}, {unknown}"]
    for nhan in (None, CONG_TY, {"person": {"vi": "Khách", "en": "Company"}}):
        ra = _chay_js({"mau": mau, "nhan": nhan, "tham_so": {"n": 4}})
        for lang in ("vi", "en"):
            mong_doi = [nhan_ws.dien(m, nhan, lang).replace("{n}", "4") for m in mau]
            assert ra[lang]["_fill"] == mong_doi, (nhan, lang)


@can_node
def test_tham_so_thang_cho_giu_danh_tu_va_khong_bi_dien_lai():
    # Dữ liệu người dùng (tên học sinh…) chứa "{person}" thì KHÔNG được thành nhãn.
    ra = _chay_js({"mau": ["Chào {ten}, {person_l}"], "tham_so": {"ten": "{person}"},
                   "nhan": CONG_TY})
    assert ra["vi"]["_fill"] == ["Chào {person}, nhân viên"]


@can_node
def test_loi_dich_theo_nhan(anh_chup):
    loi = [{"code": "student_not_found", "params": {"student_id": "NV01"}},
           {"code": "score_negative", "params": {"student_id": "NV01", "diem_goc": "-3"}}, "tho"]
    mac_dinh = _chay_js({"loi": loi})
    assert mac_dinh["vi"]["_loi"][0] == "Không tìm thấy học sinh NV01."
    assert mac_dinh["vi"]["_loi"][2] == "tho"
    ct = _chay_js({"loi": loi, "nhan": CONG_TY})
    assert ct["vi"]["_loi"][0] == "Không tìm thấy nhân viên NV01."
    assert ct["vi"]["_loi"][1] == "NV01: điểm “-3” là số âm, có thể do gõ thừa dấu trừ. Điểm này chưa được lưu."
    assert ct["en"]["_loi"][0].lower().startswith("employee nv01")


@can_node
def test_dat_nhan_hai_lan_va_dat_lai_mac_dinh():
    ra = _chay_js({"khoa": ["label_students"], "nhan": CONG_TY})
    assert ra["vi"]["label_students"] == "nhân viên"
    # nhãn None/rỗng = mặc định
    ra = _chay_js({"khoa": ["label_students"], "nhan": {}})
    assert ra["vi"]["label_students"] == "học sinh"


# ------------------------------------------------------------------ tệp xuất (Python)

def _api_cong_ty(tmp_path, nhan=CONG_TY):
    """Một workspace công ty có dữ liệu và đã chạy sắp xếp."""
    import cau_hinh_ws
    import workspace
    from api import PipelineAPI

    goc = str(tmp_path / "goc")
    os.makedirs(goc)
    cfg = {"industry": "company", "labels": nhan}
    slug = workspace.tao(goc, "Công ty ABC", cfg)
    api = PipelineAPI(workspace.duong_dan_db(goc, slug), thu_muc_xuat=str(tmp_path / "xuat"),
                      thu_muc_goc_ws=goc)
    os.makedirs(str(tmp_path / "xuat"), exist_ok=True)
    api.create_or_update_club("du_an_a", "Dự án A", 1, 0, "")
    api.create_or_update_club("du_an_b", "Dự án B", 5, 0, "")
    api.import_preferences_csv(
        "student_id,name,pref_1,pref_2\n"
        "NV001,Nguyễn Văn An,du_an_a,du_an_b\n"
        "NV002,Trần Thị Bình,du_an_a,du_an_b\n")
    assert api.run_pipeline(seed=42)["ok"]
    return api, cau_hinh_ws


def test_so_excel_cong_ty_dung_tu_cua_workspace(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    api, _ = _api_cong_ty(tmp_path)
    ra = str(tmp_path / "kq.csv")
    res = api.export_csv(ra)
    assert res["ok"], res["errors"]
    wb = openpyxl.load_workbook(os.path.splitext(ra)[0] + ".xlsx")
    assert wb.sheetnames == ["Hướng dẫn", "Danh sách nhân viên", "Theo dự án",
                             "Chưa có chỗ", "Thống kê", "Dấu vết (kỹ thuật)"]
    ds = wb["Danh sách nhân viên"]
    dau = [c.value for c in ds[4]]
    assert dau[:2] == ["Mã nhân viên", "Họ tên"] and "Mã dự án" in dau and "Tên dự án" in dau
    assert ds["A1"].value == "DANH SÁCH NHÂN VIÊN VÀ DỰ ÁN"
    theo = wb["Theo dự án"]
    chu = [str(c.value) for hang in theo.iter_rows() for c in hang if c.value is not None]
    assert any(c.startswith("Dự án A") and "Mã dự án: du_an_a" in c for c in chu)
    assert "DANH SÁCH TỪNG DỰ ÁN" in chu
    # Không còn từ vựng của trường học ở chữ của phần mềm (dữ liệu người dùng thì giữ nguyên).
    toan = " ".join(str(c.value) for w in wb.worksheets for hang in w.iter_rows()
                    for c in hang if c.value is not None)
    for tu in ("học sinh", "CLB", "câu lạc bộ", "HỌC SINH", "CÂU LẠC BỘ", "{", "}"):
        assert tu not in toan, (tu, toan[:300])
    # Mục lục bấm được phải nhảy tới đúng tên trang mới.
    hd = wb["Hướng dẫn"]
    lien_ket = [c.hyperlink.location for hang in hd.iter_rows() for c in hang if c.hyperlink]
    assert "'Danh sách nhân viên'!A1" in lien_ket and "'Theo dự án'!A1" in lien_ket


def test_csv_cong_ty_dung_tu_cua_workspace(tmp_path):
    import csv
    api, _ = _api_cong_ty(tmp_path)
    ra = str(tmp_path / "kq.csv")
    assert api.export_csv(ra)["ok"]
    with open(ra, encoding="utf-8-sig", newline="") as f:
        dau = next(csv.reader(f))
    assert dau[0] == "Mã nhân viên" and "Mã dự án" in dau and "Tên dự án" in dau
    with open(os.path.splitext(ra)[0] + "_tong_hop.csv", encoding="utf-8-sig", newline="") as f:
        noi_dung = f.read()
    assert "TỔNG HỢP KẾT QUẢ PHÂN BỔ DỰ ÁN (RB-DA)" in noi_dung
    assert "học sinh" not in noi_dung and "CLB" not in noi_dung


def test_du_lieu_nguoi_dung_giong_cho_giu_khong_bi_dien(tmp_path):
    """Tên CLB đặt đúng là "{slot}" phải hiện nguyên văn trong tệp xuất."""
    openpyxl = pytest.importorskip("openpyxl")
    api, _ = _api_cong_ty(tmp_path)
    api.create_or_update_club("la", "{slot} {person_l}", 3, 0, "")
    ra = str(tmp_path / "la.csv")
    assert api.export_csv(ra)["ok"]
    wb = openpyxl.load_workbook(os.path.splitext(ra)[0] + ".xlsx")
    chu = [str(c.value) for hang in wb["Theo dự án"].iter_rows() for c in hang
           if c.value is not None]
    assert any("{slot} {person_l}" in c for c in chu), chu[:20]


def test_so_excel_ten_trang_khong_hop_le_van_ghi_duoc(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    nhan = dict(CONG_TY, slot={"vi": "Dự án/Phòng: lớn?", "en": "Project"},
                person={"vi": "Nhân viên rất rất rất rất rất rất rất dài", "en": "Employee"})
    api, _ = _api_cong_ty(tmp_path, nhan)
    ra = str(tmp_path / "kq.csv")
    assert api.export_csv(ra)["ok"]
    wb = openpyxl.load_workbook(os.path.splitext(ra)[0] + ".xlsx")
    for ten in wb.sheetnames:
        assert len(ten) <= 31 and not any(c in ten for c in "[]:*?/\\"), ten
    assert "Theo dự án-phòng- lớn-" in wb.sheetnames


def test_trang_en_trong_xuat_ra_tieng_viet_nhu_truoc(tmp_path):
    """Tệp xuất luôn là tiếng Việt: nhãn en không ảnh hưởng."""
    openpyxl = pytest.importorskip("openpyxl")
    api, _ = _api_cong_ty(tmp_path, dict(CONG_TY, person={"vi": "Nhân viên", "en": ""}))
    ra = str(tmp_path / "kq.csv")
    assert api.export_csv(ra)["ok"]
    wb = openpyxl.load_workbook(os.path.splitext(ra)[0] + ".xlsx")
    assert "Danh sách nhân viên" in wb.sheetnames


def test_mac_dinh_truong_hoc_ten_trang_excel_khong_doi(api, tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    api.create_or_update_club("a", "A", 2, 0, "")
    api.import_preferences_csv("student_id,name,pref_1\nHS1,An,a\n")
    assert api.run_pipeline(seed=1)["ok"]
    ra = str(tmp_path / "kq.csv")
    assert api.export_csv(ra)["ok"]
    wb = openpyxl.load_workbook(os.path.splitext(ra)[0] + ".xlsx")
    assert wb.sheetnames == ["Hướng dẫn", "Danh sách học sinh", "Theo CLB",
                             "Chưa có chỗ", "Thống kê", "Dấu vết (kỹ thuật)"]
    assert wb["Danh sách học sinh"]["A1"].value == "DANH SÁCH HỌC SINH VÀ CÂU LẠC BỘ"
