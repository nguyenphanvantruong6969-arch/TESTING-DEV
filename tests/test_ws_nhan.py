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
from _wharton import tat_wharton
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
    # FA gaps (GAP-1, GAP-2): điểm danh, mời danh sách chờ.
    "fa_tinh_nang_can_fa", "fa_diem_danh_chua_bat", "diem_danh_gia_tri_sai", "diem_danh_khong_thuoc_clb",
    "moi_khong_con_cho", "gioi_han_gv_sai", "fa_khieu_nai_chua_bat", "khieu_nai_khong_hop_le", "khieu_nai_qua_han",
    "khieu_nai_trung", "khieu_nai_da_xu_ly", "loi_luu_sau_xep",
    "fa_vong_2_chua_bat", "vong_2_lua_chon_sai", "vong_2_da_chay",
    "fa_phan_hoi_chua_bat", "phan_hoi_gia_tri_sai", "phan_hoi_tep_sai",
    # FA-DAA (FA-1): thuộc tính CLB, giữ chỗ, cảnh báo nạp.
    "fa_loai_sai", "fa_diem_san_sai", "fa_toi_thieu_sai", "fa_suc_chua_phong_sai",
    "so_nhap_fa_loai_sai", "so_nhap_fa_diem_san_sai", "so_nhap_fa_toi_thieu_sai",
    "so_nhap_fa_suc_chua_phong_sai", "csv_club_fa_invalid", "fa_cot_bo_qua",
    "fa_giu_cho_bo_qua", "so_nhap_fa_giu_cho_khong_ton_tai",
    # FA-2: kiểm trước khi chạy.
    "fa_thieu_clb_tu_do", "fa_clb_thieu_loai", "fa_clb_thieu_suc_chua", "fa_clb_thieu_diem_san",
    "fa_giu_cho_vuot_suc_chua", "fa_giu_cho_hoc_sinh_la", "fa_giu_cho_khong_xep_clb",
    # FA-N1, FA-N3 (đêm 4).
    "fa_ly_do_thieu_buoi", "fa_can_diem_quyet_tam", "bien_ban_chua_boc_tham",
    # FA-3: huy chương.
    "fa_chua_bat", "fa_huy_chuong_gia_tri_sai", "fa_huy_chuong_trung_gia_tri",
    "fa_huy_chuong_ngoai_nguyen_vong", "fa_huy_chuong_clb_tu_do",
    # FA-4: chạy.
    "fa_diem_bo_qua",
    # FA-5: đóng CLB thiếu người.
    "fa_clb_dong_thieu_nguoi",
    # FA-6: lý do kết quả.
    "fa_chua_co_ly_do",
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
    # T3-L0 (B2): chặn chạy xếp khi chưa có học sinh hoặc CLB.
    "chua_co_du_lieu_de_chay",
    # A13.8: khoá điểm giữ nguyện vọng / ô tick; điểm chấm sai; điểm chuẩn xuất lỗi; phóng hàng loạt.
    "csv_wharton_khoa_giu_nguyen", "xuat_diem_chuan_loi",
    # Vòng 3 (A13.3): khoá, mở khoá, xoá và quản lý điểm Wharton ở thẻ Quản lý.
    "wharton_da_khoa", "wharton_mo_khoa_sai_xac_nhan", "wharton_xoa_sai_xac_nhan",
    "wharton_da_xoa", "wharton_da_mo_khoa", "error_wharton_quan_ly",
    # A13.4: Sổ nhập hai hàng tiêu đề, lệch nhóm cột.
    "so_nhap_cot_lech_nhom", "so_nhap_nhom_thieu_cot",
    # A13.5: lỗi chặn gọn, phóng điểm hàng loạt, khoá xuất khi chưa có kết quả.
    "wharton_tom_tat_chua_hop_le", "wharton_phong_sai_xac_nhan", "wharton_da_phong",
    "xuat_chua_co_ket_qua",
    # A13.9 (stress test): CSDL bận không còn bị báo là cấu hình hỏng.
    "csdl_dang_ban",
    # A13.11 (N1): đường xuất là thư mục có sẵn.
    "xuat_duong_la_thu_muc",
    # Sổ nhập rỗng: ok kèm cảnh báo thay vì lỗi chặn.
    "so_nhap_canh_bao_khong_co_clb", "so_nhap_canh_bao_khong_co_hs",
    # A13.12 (soát nhập 1.2): lỗi HTTP của máy chủ dự phòng có mã (trước đây là chuỗi trần).
    "http_bi_tu_choi", "http_khong_co_dich", "http_khong_co_ham", "http_than_qua_lon",
    # A13.12 (soát nhập 3.1): mã rỗng khi tạo học sinh.
    "student_id_required",
    # A14: lớp của học sinh.
    "error_reading_classes", "error_saving_student_class", "lop_khong_co_trong_danh_sach",
    "so_nhap_canh_bao_thieu_lop",
    # A14 sửa A1: hai danh từ cùng nhãn.
    "nhan_trung_danh_tu", "so_nhap_canh_bao_nhan_trung",
    # A14 sửa A4: giới hạn đầu vào lớp.
    "lop_sai_kieu", "lop_qua_dai", "canh_bao_lop_bi_cat",
}


# Thay đổi CÓ CHỦ Ý sau ảnh chụp (T1/T2, Truong duyệt): đánh số lại thẻ (bảy thành sáu) làm đổi số thẻ
# trong hai chuỗi, và năm khoá giao diện mồ côi của thẻ Kết quả cũ bị bỏ. Mọi chuỗi khác vẫn giống hệt.
KHOA_UI_DA_BO = {"fill_panel_title", "fill_hint", "fill_nhom_tong", "fill_choi", "admin_lich_tuan_title", "admin_lich_tuan_desc", "results_title", "results_desc", "tkb_title", "tkb_desc", "tkb_so_clb",
                 # T3-L1 (Truong duyệt 04/11/2026): bỏ dòng phụ tên thuật toán, ô "đã nộp nguyện vọng",
                 # và hai dòng chữ đơn về số khởi tạo (gộp vào một dòng `stb_locked_label`).
                 "brand_sub", "label_submitted_prefs", "seed_locked_hint", "seed_unlocked_for_redraw",
                 # T3-L2 (T3-07): bỏ hai ô "Từ/đến" ở bộ chọn buổi, chỉ giữ thẻ buổi và "Chọn tất cả".
                 "chon_buoi_tu", "chon_buoi_den",
                 # T3-L2 (T3-04): gộp hai nút kiểm tra thành một (`btn_validate`, đổi chữ).
                 "btn_health_recheck"}

# T3-L1 (Truong duyệt 04/11/2026): đổi chữ có chủ ý theo bảng 5.1-5.3 của nghiên cứu T3. Chuỗi cũ đổi theo
# bảng thay chữ dưới đây; chuỗi viết lại hẳn nằm trong `chu_ui_doi_co_y_t3.json` (giá trị MỚI với mặc định
# trường học). Mọi chuỗi khác vẫn giống hệt ảnh chụp.
THAY_CHU_T3 = [("Nhập tại chỗ", "Nhập nguyện vọng"), ("Kiosk entry", "Enter preferences"),
               ("Vận hành sắp xếp", "Xếp CLB"),
               # T3-L3 (T3-27): chữ giao diện = chữ của Sổ nhập (Chỉ tiêu / Suất ưu tiên / Nhóm ưu tiên);
               # tab 03 và 05 đổi tên (Truong duyệt 04/11/2026).
               ("Quản lý CLB & dự trữ", "Quản lý CLB"), ("Clubs & reserves", "Manage clubs"),
               ("Dữ liệu khác", "Chi tiết và xuất tệp"), ("Other data", "Details and export"),
               ("Suất dự trữ", "Suất ưu tiên"), ("suất dự trữ", "suất ưu tiên"),
               ("Gán nhãn dự trữ", "Gán nhóm ưu tiên"), ("Nhãn dự trữ", "Nhóm ưu tiên"),
               ("nhãn dự trữ", "nhóm ưu tiên"), ("Tổng chỗ", "Chỉ tiêu"), ("tổng chỗ", "chỉ tiêu"),
               ("Reserve seats", "Priority seats"), ("Reserve labels and", "Priority groups and"),
               ("Current reserve label", "Current priority group"),
               ("Reserve label to apply", "Priority group to apply"),
               ("Admitted on a reserved seat", "Admitted on a priority seat"),
               ("Soft reserved seats", "Soft priority seats"), ("Reserved places", "Priority places"),
               ("regular or reserved places", "regular or priority places"),
               ("and total seats.", "and quota."), ("reserves any seats", "has priority seats"),
               ("reserve seat", "priority seat"), ("Reserve seat", "Priority seat"),
               ("reserve label", "priority group"), ("Reserve capacity", "Priority seats"),
               ("reserved seats", "priority seats"), ("Total seats must be", "Quota must be"),
               ("than total seats", "than quota")]
CHU_UI_MOI_T3 = os.path.join(GOC, "tests", "du_lieu_ws", "chu_ui_doi_co_y_t3.json")
SUA_CO_Y = {
    ("ui", "xuat_hint_hoc_sinh"): [("thẻ 03 thì", "thẻ 04 thì"), ("tab 03", "tab 04")],
    ("loi", "so_nhap_canh_bao_clb_ngoai_so"): [("thẻ 04", "thẻ 05"), ("tab 04", "tab 05")],
}


def _sua_co_y(loai, khoa, chuoi):
    for cu, moi in SUA_CO_Y.get((loai, khoa), []):
        chuoi = chuoi.replace(cu, moi)
    return chuoi


def _truoc_da_doi_ten_tham_so(chuoi, ma=None):
    chuoi = _sua_co_y("loi", ma, chuoi)
    chuoi = chuoi.replace("{score}", "{diem_goc}")
    if ma in TRAN_MAC_DINH:
        chuoi, n = re.subn(r"\b%d\b" % TRAN_MAC_DINH[ma], "{tran}", chuoi)
        assert n == 1, (ma, chuoi)
    return chuoi


@pytest.fixture(scope="module")
def anh_chup():
    with open(ANH_CHUP, encoding="utf-8") as f:
        d = json.load(f)
    with open(CHU_UI_MOI_T3, encoding="utf-8") as f:
        moi = json.load(f)["ui"]
    for loai in ("loi", "ui"):
        for lang in ("vi", "en"):
            bang = d[loai][lang] if loai == "ui" else None
            if loai == "ui":
                for k, v in list(bang.items()):
                    for cu, mo in THAY_CHU_T3:
                        v = v.replace(cu, mo)
                    bang[k] = moi[lang].get(k, v)
            else:
                for ma, v in d["loi"].items():
                    for cu, mo in THAY_CHU_T3:
                        v[lang] = v[lang].replace(cu, mo)
    return d


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
            truoc = {**truoc, lang: _sua_co_y("loi", ma, truoc[lang])}
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
            for ten in re.findall(r"\{(person|slot|session|group|score|cohort)\}", d[lang]):
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
    khoa = sorted(set(anh_chup["ui"]["vi"]) - KHOA_UI_DA_BO)
    ra = _chay_js({"khoa": khoa})
    lech = []
    for lang in ("vi", "en"):
        for k in khoa:
            mong = _sua_co_y("ui", k, anh_chup["ui"][lang][k])
            if ra[lang][k] != mong:
                lech.append((lang, k, mong[:70], ra[lang][k][:70]))
    assert not lech, lech[:10]
    assert len(khoa) > 450  # có đọc đủ bảng, không phải bảng rỗng


# 20 chuỗi tiêu biểu: đủ năm danh từ, vi + en, số ít/số nhiều, mạo từ, viết tắt.
MAU_20 = [
    "brand_title", "nav_admin", "nav_scoring", "label_students", "label_clubs",
    "pipeline_desc", "admin_desc", "chua_co_cho_desc", "toast_run_success",
    "feedback_scores_saved", "fallback_step1_hint", "buoi_chua_chia", "fill_tag_khong_ai",
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
        "Nhập sổ nhập, bấm Chạy để xếp nhân viên vào dự án, rồi tải kết quả."


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
    cfg = {"industry": "company", "labels": nhan,
           "rules": {"wharton": False}}   # A13.13: mặc định đã BẬT; test này không có điểm quyết tâm
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
                             "Theo lớp", "Chưa có chỗ", "Thống kê", "Dấu vết (kỹ thuật)"]
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
    # A13.13: mặc định đã BẬT Wharton nên tệp xuất có thêm trang "Điểm chuẩn"; tên trang cũ
    # được giữ nguyên khi tắt RÕ RÀNG, và mặc định mới chỉ thêm đúng trang đó.
    tat_wharton(api)
    api.create_or_update_club("a", "A", 2, 0, "")
    api.import_preferences_csv("student_id,name,pref_1\nHS1,An,a\n")
    assert api.run_pipeline(seed=1)["ok"]
    ra = str(tmp_path / "kq.csv")
    assert api.export_csv(ra)["ok"]
    wb = openpyxl.load_workbook(os.path.splitext(ra)[0] + ".xlsx")
    assert wb.sheetnames == ["Hướng dẫn", "Danh sách học sinh", "Theo CLB",
                             "Theo lớp", "Chưa có chỗ", "Thống kê", "Dấu vết (kỹ thuật)"]
    assert wb["Danh sách học sinh"]["A1"].value == "DANH SÁCH HỌC SINH VÀ CÂU LẠC BỘ"


def test_mac_dinh_moi_them_dung_trang_diem_chuan(api, tmp_path):
    """A13.13: mặc định BẬT Wharton chỉ thêm trang "Điểm chuẩn" so với mặc định cũ."""
    openpyxl = pytest.importorskip("openpyxl")
    api.create_or_update_club("a", "A", 2, 0, "")
    api.import_preferences_csv("student_id,name,pref_1\nHS1,An,a\n")
    assert api.run_pipeline(seed=1)["ok"]
    ra = str(tmp_path / "kq.csv")
    assert api.export_csv(ra)["ok"]
    wb = openpyxl.load_workbook(os.path.splitext(ra)[0] + ".xlsx")
    assert wb.sheetnames == ["Hướng dẫn", "Danh sách học sinh", "Theo CLB", "Theo lớp",
                             "Chưa có chỗ", "Điểm chuẩn", "Thống kê", "Dấu vết (kỹ thuật)"]
