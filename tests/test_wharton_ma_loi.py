"""Điểm Wharton (A13, vòng 2): mã lỗi song ngữ cho nhập liệu, kiosk, pipeline và sức khoẻ dữ liệu.

Bảy mã của kiểm hồ sơ (`wharton_nguyen_vong_chua_xep`…) đã được `tests/test_wharton.py` canh;
tệp này canh tám mã thêm ở vòng 2.
"""

import re

import pytest

from i18n_errors import MESSAGES, format_message

MA_VONG_2 = [
    "csv_wp_khong_hop_le", "csv_wp_khong_co_nguyen_vong", "csv_wp_bo_qua", "wharton_chua_bat",
    "wharton_ho_so_chua_hop_le", "health_wharton_chua_hop_le", "health_wharton_vang_thi",
    "error_saving_wharton",
]

# Tham số mà câu cần (ngoài các chỗ giữ nhãn); các bước sau gọi err() đúng những tên này.
THAM_SO = {
    "csv_wp_khong_hop_le": {"student_id", "club_id", "gia_tri"},
    "csv_wp_khong_co_nguyen_vong": {"student_id", "cot"},
    "csv_wp_bo_qua": {"n"},
    "wharton_chua_bat": set(),
    "wharton_ho_so_chua_hop_le": {"n"},
    "health_wharton_chua_hop_le": {"n"},
    "health_wharton_vang_thi": {"n"},
    "error_saving_wharton": set(),
}

NHAN_CONG_TY = {
    "person": {"vi": "Nhân viên", "en": "Employee"},
    "slot": {"vi": "Dự án", "en": "Project"},
    "session": {"vi": "Ca", "en": "Shift"},
    "group": {"vi": "Cấp bậc", "en": "Level"},
    "score": {"vi": "Điểm", "en": "Score"},
}


@pytest.mark.parametrize("ma", MA_VONG_2)
def test_co_du_vi_va_en(ma):
    assert MESSAGES[ma].get("vi") and MESSAGES[ma].get("en")


@pytest.mark.parametrize("ma", MA_VONG_2)
def test_khong_viet_cung_nhan_trong_cau(ma):
    vi = re.sub(r"\{\w+\}", "", MESSAGES[ma]["vi"]).lower()
    en = re.sub(r"\{\w+\}", "", MESSAGES[ma]["en"]).lower()
    for tu in ("học sinh", "câu lạc bộ", "clb"):
        assert tu not in vi, (ma, tu)
    for tu in ("student", "club"):
        assert tu not in en, (ma, tu)


@pytest.mark.parametrize("ma", MA_VONG_2)
@pytest.mark.parametrize("nhan", [None, NHAN_CONG_TY], ids=["truong_hoc", "cong_ty"])
@pytest.mark.parametrize("lang", ["vi", "en"])
def test_dien_duoc_tham_so_va_nhan(ma, nhan, lang):
    tham_so = {ten: "X" for ten in THAM_SO[ma]}
    cau = format_message(ma, tham_so, lang, nhan)
    assert cau != ma
    assert "{" not in cau and "}" not in cau, cau
    assert cau.count("X") >= len(THAM_SO[ma])
    if nhan is NHAN_CONG_TY:
        assert "học sinh" not in cau.lower() and "câu lạc bộ" not in cau.lower()


@pytest.mark.parametrize("ma", MA_VONG_2)
def test_chi_dung_tham_so_da_khai_bao(ma):
    """Câu không đòi tham số nào ngoài danh sách mà chỗ gọi err() sẽ truyền."""
    for lang in ("vi", "en"):
        dung = set(re.findall(r"\{(\w+?)(?:_[lpsacuv]+)?\}", MESSAGES[ma][lang]))
        nhan = {"person", "slot", "session", "group", "score"}
        assert dung - nhan <= THAM_SO[ma], (ma, lang, dung)
