"""Điểm Wharton (A13.3, Bước 2): sửa hai chỗ lệch "cách A" của vòng 2.

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.

Cách A (Truong đã chốt): quỹ chỉ có MỘT CLB mà để trống được tự điền 100 TRONG BỘ NHỚ, không ghi
CSDL. Pipeline, báo cáo sức khoẻ dữ liệu, kiosk và cảnh báo sau khi nạp phải nói cùng một điều:
  * (a) `submit_wharton` chỉ ghi ô người dùng đã GỬI (không ghi ô 100 tự điền);
  * (b) `_soat_ho_so_wharton` tự điền trên bản sao trước khi kiểm.
"""

import pytest

from _wharton import bat_wharton, canh_bao, dong_bids, dung_clb, dung_hs


@pytest.fixture
def w(api):
    """Bật Wharton; HS1 tick thi A, nguyện vọng A, B, C (quỹ 1 = {A}, quỹ 2 = {B, C})."""
    bat_wharton(api)
    dung_clb(api, A=5, B=5, C=5)
    dung_hs(api, "HS1", tick={"HS1": ["A"]})
    assert api.submit_preferences("HS1", ["A", "B", "C"])["ok"]
    return api


def test_submit_khong_ghi_o_tu_dien_nhung_hop_le(w):
    kq = w.submit_wharton("HS1", {}, {"B": 70, "C": 30})
    assert kq["ok"], kq["errors"]
    assert dong_bids(w) == [("HS1", "B", 2, 70), ("HS1", "C", 2, 30)]     # KHÔNG có dòng A
    assert kq["data"]["n_saved"] == 2


def test_o_nguoi_dung_gui_thi_duoc_ghi(w):
    assert w.submit_wharton("HS1", {"A": 100}, {"B": 70, "C": 30})["ok"]
    assert ("HS1", "A", 1, 100) in dong_bids(w)


def test_them_clb_thu_hai_vao_quy_da_tu_dien_thi_bao_cao_nhac_chia_lai(api):
    """Hậu quả cũ: ô 100 đã ghi nên thêm CLB thứ hai vào quỹ vẫn 'hợp lệ' (100 + 0)."""
    bat_wharton(api)
    dung_clb(api, A=5, B=5, C=5, D=5)
    dung_hs(api, "HS1", tick={"HS1": ["A"]})
    assert api.submit_preferences("HS1", ["A", "B", "C"])["ok"]
    assert api.submit_wharton("HS1", {}, {"B": 70, "C": 30})["ok"]       # quỹ 1 = {A}: tự điền
    assert api.submit_preferences("HS1", ["A", "B", "C", "D"])["ok"]
    assert api.submit_test_selection("HS1", ["A", "D"])["ok"]            # quỹ 1 nay có A và D
    ma = [x["code"] for x in api.get_data_health_report()["data"]["warnings"]]
    assert "health_wharton_chua_hop_le" in ma


def test_em_chi_co_mot_clb_moi_quy_gui_rong_van_hop_le_va_khong_ghi_gi(w):
    dung_hs(w, "HS3", tick={"HS3": ["A"]})
    assert w.submit_preferences("HS3", ["A"])["ok"]
    kq = w.submit_wharton("HS3", {}, {})
    assert kq["ok"], kq["errors"]
    assert [d for d in dong_bids(w) if d[0] == "HS3"] == []
    assert kq["data"]["n_saved"] == 0


def test_nap_tep_quy_mot_clb_de_trong_khong_canh_bao_chua_dung_het(w):
    kq = w.import_preferences_csv("student_id,name,pref_1,wp_1,pref_2,wp_2,pref_3,wp_3\n"
                                  "HS1,An,A,,B,60,C,40\n")
    assert kq["ok"], kq["errors"]
    assert canh_bao(kq, "wharton_chua_dung_het") == []
    assert dong_bids(w) == [("HS1", "B", 2, 60), ("HS1", "C", 2, 40)]


def test_nap_tep_quy_nhieu_clb_chua_chia_van_canh_bao(w):
    kq = w.import_preferences_csv("student_id,name,pref_1,wp_1,pref_2,wp_2,pref_3,wp_3\n"
                                  "HS1,An,A,100,B,60,C,\n")
    assert [e["params"]["quy"] for e in canh_bao(kq, "wharton_chua_dung_het")] == [2]
