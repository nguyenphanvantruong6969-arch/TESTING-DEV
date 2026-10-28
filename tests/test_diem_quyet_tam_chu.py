"""Tên hiển thị của tính năng (A13.4): "Điểm quyết tâm" / "Preference points". Trong mã vẫn là wharton.

Quyết định của Truong (25/10/2026): chữ NGƯỜI DÙNG NHÌN THẤY không còn "Wharton". Tên hàm, tên biến,
tên bảng, mã lỗi (`wharton_*`), khoá `rules.wharton`, cột CSV `wp_k` và id HTML giữ nguyên.
"""

import os
import re

import pytest

from i18n_errors import MESSAGES
from test_van_phong_tu_nhien import _ui_strings

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Khoá i18n của tính năng: tên khoá giữ nguyên, chỉ câu chữ đổi.
KHOA_UI = [
    "fallback_step3_title", "btn_save_wharton", "feedback_wharton_saved", "wharton_da_khoa_kiosk",
    "wh_ql_title", "wh_ql_desc", "btn_wh_mo_khoa", "toast_wh_xoa_mot", "btn_wh_xoa_tat_ca",
    "wh_xoa_tat_ca_hoi", "ws_r_wharton", "ws_r_wharton_ghi_chu",
]


def test_ui_strings_khong_con_wharton():
    ui = _ui_strings()
    con = [(lang, k) for lang in ("vi", "en") for k, c in ui[lang].items() if "wharton" in c.lower()]
    assert con == [], con


def test_thong_bao_loi_khong_con_wharton():
    con = [(code, lang) for code, b in MESSAGES.items() for lang in ("vi", "en")
           if "wharton" in b[lang].lower()]
    assert con == [], con


def test_i18n_loi_js_da_sinh_lai():
    with open(os.path.join(GOC, "i18n_loi.js"), encoding="utf-8") as f:
        assert "wharton" not in re.sub(r'"wharton_[a-z_]+"|"[a-z_]*wharton[a-z_]*"', "", f.read().lower())


@pytest.mark.parametrize("khoa", KHOA_UI)
def test_cau_ui_dung_ten_moi(khoa):
    ui = _ui_strings()
    assert khoa in ui["vi"], khoa
    if khoa in ("fallback_step3_title", "btn_save_wharton", "wharton_da_khoa_kiosk", "wh_ql_title",
                "btn_wh_mo_khoa", "btn_wh_xoa_tat_ca", "ws_r_wharton"):
        assert "quyết tâm" in ui["vi"][khoa].lower(), khoa
        assert "preference points" in ui["en"][khoa].lower(), khoa


def test_dau_cau_tieng_anh_viet_hoa_dung():
    ui = _ui_strings()
    assert ui["en"]["wh_ql_title"] == "Preference points"
    assert ui["en"]["fallback_step3_title"] == "Step 3. Preference points"
    assert ui["vi"]["wh_ql_title"] == "Điểm quyết tâm"
    assert ui["vi"]["fallback_step3_title"] == "Bước 3. Điểm quyết tâm"


def test_khoa_i18n_va_ma_loi_giu_nguyen():
    ui = _ui_strings()
    for khoa in KHOA_UI:
        assert khoa in ui["vi"] and khoa in ui["en"], khoa
    for ma in ("wharton_chua_dung_het", "wharton_vuot_ngan_sach", "wharton_da_khoa", "wharton_chua_bat",
               "error_saving_wharton"):
        assert ma in MESSAGES, ma


def test_huong_dan_su_dung_khong_con_wharton_cho_nguoi_dung():
    with open(os.path.join(GOC, "HUONG_DAN_SU_DUNG.md"), encoding="utf-8") as f:
        dong = [d for d in f.read().split("\n") if "wharton" in d.lower()]
    # Chỉ được còn dòng ghi chú cho người bảo trì.
    assert all("người bảo trì" in d for d in dong), dong
    assert len(dong) <= 1
