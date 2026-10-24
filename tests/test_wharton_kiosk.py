"""Điểm Wharton (A13, vòng 2): API kiosk — `get_student_entry_state` có khoá `wharton`, và
`submit_wharton` (kiểm ở SERVER, không tin dữ liệu từ trình duyệt — đặc tả V6).

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.

Điều phải giữ:
  * Wharton TẮT: `get_student_entry_state` trả về y hệt trước vòng 2 (không có khoá mới);
  * hồ sơ hợp lệ thì thay TOÀN BỘ dòng của em; hồ sơ sai thì không đổi gì và trả đúng danh sách
    lỗi của `kiem_ho_so_wharton`;
  * một CLB trong một quỹ thì tự điền 100;
  * hợp đồng {ok, data, errors} (bất biến 6), không ném ngoại lệ ra ngoài.
"""

import pytest

import rbda_priority_pipeline as rp
from _wharton import bat_wharton, chen_bids, dong_bids, dung_clb, dung_hs


@pytest.fixture
def w(api):
    """Bật Wharton; ba CLB một buổi; HS1 tick thi A, nguyện vọng A, B, C."""
    bat_wharton(api)
    dung_clb(api, A=5, B=5, C=5)
    dung_hs(api, "HS1", "HS2", tick={"HS1": ["A"]})
    assert api.submit_preferences("HS1", ["A", "B", "C"])["ok"]
    assert api.submit_preferences("HS2", ["B", "C"])["ok"]
    return api


def _loi(kq):
    assert kq["ok"] is False and kq["data"] is None
    return kq["errors"]


# ------------------------------------------------------------------ get_student_entry_state

def test_tat_wharton_trang_thai_giong_het_truoc(api):
    dung_clb(api, A=5)
    dung_hs(api, "HS1", tick={"HS1": ["A"]})
    assert api.submit_preferences("HS1", ["A"])["ok"]
    chen_bids(api, [("HS1", "A", 1, 100)])           # bảng có dòng nhưng workspace tắt
    st = api.get_student_entry_state("HS1")
    assert st["ok"]
    assert st["data"] == {"student_id": "HS1", "name": "Em HS1",
                          "tested_clubs": ["A"], "ranked_clubs": ["A"]}


def test_bat_wharton_trang_thai_co_khoa_wharton_dung_dang(w):
    chen_bids(w, [("HS1", "A", 1, 100), ("HS1", "B", 2, 60), ("HS1", "C", 2, 40)])
    st = w.get_student_entry_state("HS1")["data"]
    assert st["tested_clubs"] == ["A"] and st["ranked_clubs"] == ["A", "B", "C"]
    assert st["wharton"] == {
        "bat": True, "ngan_sach": 100, "tu_dien_mot_clb": True,
        "w1": {"A": 100}, "w2": {"B": 60, "C": 40},
        "quy_cua_clb": {"A": 1, "B": 2, "C": 2},
        "buoi_cua_clb": {"A": rp.BUOI_MAC_DINH, "B": rp.BUOI_MAC_DINH, "C": rp.BUOI_MAC_DINH},
        "ds_buoi": [rp.BUOI_MAC_DINH],
    }


def test_em_chua_chia_diem_thi_w1_w2_rong(w):
    st = w.get_student_entry_state("HS2")["data"]["wharton"]
    assert st["w1"] == {} and st["w2"] == {}
    assert st["quy_cua_clb"] == {"B": 2, "C": 2}


def test_quy_theo_o_tick_hien_tai_con_dong_da_luu_giu_tier_cu_de_man_hinh_biet_lech(w):
    chen_bids(w, [("HS1", "A", 1, 100), ("HS1", "B", 2, 60), ("HS1", "C", 2, 40)])
    assert w.submit_test_selection("HS1", ["A", "B"])["ok"]            # tick thêm B
    st = w.get_student_entry_state("HS1")["data"]["wharton"]
    assert st["quy_cua_clb"] == {"A": 1, "B": 1, "C": 2}               # theo tick HIỆN TẠI
    assert st["w2"] == {"B": 60, "C": 40}                              # B vẫn nằm ở quỹ đã lưu


def test_trang_thai_nhieu_buoi_co_buoi_cua_tung_clb(api):
    bat_wharton(api)
    dung_clb(api, A=(5, "thu_5"), B=(5, "thu_3"))              # thứ 5 đứng trước trong nguyện vọng
    dung_hs(api, "HS1")
    assert api.submit_preferences("HS1", ["A", "B"])["ok"]
    st = api.get_student_entry_state("HS1")["data"]["wharton"]
    assert st["buoi_cua_clb"] == {"A": "thu_5", "B": "thu_3"}
    assert st["ds_buoi"] == ["thu_3", "thu_5"]                  # đã sắp theo thứ tự ngày


# ------------------------------------------------------------------ submit_wharton: hợp lệ

def test_ho_so_hop_le_thay_toan_bo_dong_cua_em(w):
    chen_bids(w, [("HS2", "B", 2, 100)])                                # em khác: không đụng tới
    kq = w.submit_wharton("HS1", {"A": 100}, {"B": 60, "C": 40})
    assert kq["ok"] and kq["errors"] == []
    assert kq["data"] == {"student_id": "HS1", "n_saved": 3}
    assert dong_bids(w) == [("HS1", "A", 1, 100), ("HS1", "B", 2, 60), ("HS1", "C", 2, 40),
                            ("HS2", "B", 2, 100)]
    kq = w.submit_wharton("HS1", {"A": 100}, {"B": 10, "C": 90})        # lưu lại: thay hẳn
    assert kq["ok"]
    assert [d for d in dong_bids(w) if d[0] == "HS1"] == [
        ("HS1", "A", 1, 100), ("HS1", "B", 2, 10), ("HS1", "C", 2, 90)]


def test_tu_dien_khi_quy_chi_co_mot_clb(w):
    # T1 = {A} chỉ một CLB, em không gửi gì cho quỹ 1: tự điền 100
    kq = w.submit_wharton("HS1", {}, {"B": 70, "C": 30})
    assert kq["ok"], kq["errors"]
    assert dong_bids(w)[:3] == [("HS1", "A", 1, 100), ("HS1", "B", 2, 70), ("HS1", "C", 2, 30)]
    # em chỉ có một CLB mỗi quỹ: gửi rỗng cả hai vẫn hợp lệ
    dung_hs(w, "HS3", tick={"HS3": ["A"]})
    assert w.submit_preferences("HS3", ["A"])["ok"]
    assert w.submit_wharton("HS3", {}, {})["ok"]
    assert [d for d in dong_bids(w) if d[0] == "HS3"] == [("HS3", "A", 1, 100)]


def test_diem_0_la_hop_le_va_duoc_luu(w):
    kq = w.submit_wharton("HS1", {"A": 100}, {"B": 100, "C": 0})
    assert kq["ok"]
    assert ("HS1", "C", 2, 0) in dong_bids(w)


def test_nhieu_buoi_moi_quy_moi_buoi_dung_100(api):
    bat_wharton(api)
    dung_clb(api, A=(5, "thu_3"), B=(5, "thu_3"), C=(5, "thu_5"), D=(5, "thu_5"))
    dung_hs(api, "HS1", tick={"HS1": ["A", "C"]})
    assert api.submit_preferences("HS1", ["A", "B", "C", "D"])["ok"]
    kq = api.submit_wharton("HS1", {"A": 100, "C": 100}, {"B": 100, "D": 100})
    assert kq["ok"], kq["errors"]
    kq = api.submit_wharton("HS1", {"A": 50, "C": 50}, {"B": 100, "D": 100})     # 50 + 50: sai
    assert kq["ok"] is False
    assert [e["code"] for e in kq["errors"]] == ["wharton_chua_dung_het"] * 2


# ------------------------------------------------------------------ submit_wharton: sai thì không đổi gì

@pytest.mark.parametrize("w1,w2,ma", [
    ({"A": 100}, {"B": 50, "C": 40}, ["wharton_chua_dung_het"]),                  # tổng 90
    ({"A": 100}, {"B": 60, "C": 50}, ["wharton_vuot_ngan_sach"]),                 # tổng 110
    ({"A": 100, "Q": 5}, {"B": 60, "C": 40}, ["wharton_ngoai_tap"]),              # khoá ngoài tập
    ({"A": 100}, {"B": 60, "C": 40, "A": 5}, ["wharton_ngoai_tap"]),              # A là quỹ 1
    ({"A": 100}, {"B": 12.5, "C": 40}, ["wharton_diem_khong_hop_le",
                                        "wharton_chua_dung_het"]),                # số lẻ
    ({"A": 100}, {"B": True, "C": 40}, ["wharton_diem_khong_hop_le",
                                        "wharton_chua_dung_het"]),                # bool
    ({"A": 100}, {"B": -5, "C": 105}, ["wharton_diem_khong_hop_le",
                                       "wharton_vuot_ngan_sach"]),                # âm + tổng 105
    ({"A": 100}, {"B": "60", "C": 40}, ["wharton_diem_khong_hop_le", "wharton_chua_dung_het"]),
])
def test_ho_so_sai_khong_doi_csdl_va_tra_dung_loi_cua_kiem_ho_so(w, w1, w2, ma):
    chen_bids(w, [("HS1", "A", 1, 100), ("HS1", "B", 2, 100)])         # đang có hồ sơ cũ
    truoc = dong_bids(w)
    kq = w.submit_wharton("HS1", w1, w2)
    loi = _loi(kq)
    assert [e["code"] for e in loi] == ma
    assert dong_bids(w) == truoc


def test_loi_tra_ve_dung_danh_sach_cua_kiem_ho_so_wharton(w):
    kq = w.submit_wharton("HS1", {"A": 100}, {"B": 50, "C": 40})
    mong_doi = rp.kiem_ho_so_wharton(
        {"HS1": ["A", "B", "C"]}, {"HS1": {"A"}}, {"HS1": {"A": 100}},
        {"HS1": {"B": 50, "C": 40}}, {c: {} for c in "ABC"})
    assert _loi(kq) == mong_doi == [
        {"code": "wharton_chua_dung_het",
         "params": {"student_id": "HS1", "thieu": 10, "quy": 2, "buoi": rp.BUOI_MAC_DINH}}]


def test_o_tick_doi_sau_khi_chia_thi_luu_lai_bang_ho_so_cu_bi_tu_choi(w):
    assert w.submit_wharton("HS1", {"A": 100}, {"B": 60, "C": 40})["ok"]
    assert w.submit_test_selection("HS1", ["A", "B"])["ok"]            # tick thêm B
    kq = w.submit_wharton("HS1", {"A": 100}, {"B": 60, "C": 40})       # B giờ thuộc quỹ 1
    assert "wharton_ngoai_tap" in [e["code"] for e in _loi(kq)]
    # chia lại cho đúng thì được
    assert w.submit_wharton("HS1", {"A": 40, "B": 60}, {"C": 100})["ok"]
    assert dong_bids(w)[:3] == [("HS1", "A", 1, 40), ("HS1", "B", 1, 60), ("HS1", "C", 2, 100)]


def test_em_chua_xep_nguyen_vong_thi_bao_chua_xep_xong(api):
    bat_wharton(api)
    dung_clb(api, A=5)
    dung_hs(api, "HS1")
    kq = api.submit_wharton("HS1", {}, {})
    assert [e["code"] for e in _loi(kq)] == ["wharton_nguyen_vong_chua_xep"]


# ------------------------------------------------------------------ lỗi khác và hợp đồng

def test_wharton_tat_thi_bao_chua_bat_va_khong_ghi_gi(api):
    dung_clb(api, A=5)
    dung_hs(api, "HS1")
    assert api.submit_preferences("HS1", ["A"])["ok"]
    kq = api.submit_wharton("HS1", {}, {"A": 100})
    assert [e["code"] for e in _loi(kq)] == ["wharton_chua_bat"]
    assert dong_bids(api) == []


def test_hoc_sinh_khong_ton_tai(w):
    kq = w.submit_wharton("KHONG_CO", {}, {})
    assert _loi(kq) == [{"code": "student_not_found", "params": {"student_id": "KHONG_CO"}}]


@pytest.mark.parametrize("w1,w2", [(None, {}), ({}, None), ([1], {}), ("A", {}), ({}, 5)])
def test_w1_w2_khong_phai_dict_thi_bao_loi_ro_rang_khong_nem_ngoai_le(w, w1, w2):
    chen_bids(w, [("HS1", "A", 1, 100)])
    kq = w.submit_wharton("HS1", w1, w2)
    assert [e["code"] for e in _loi(kq)] == ["error_saving_wharton"]
    assert dong_bids(w) == [("HS1", "A", 1, 100)]


def test_hop_dong_ok_data_errors(w):
    kq = w.submit_wharton("HS1", {"A": 100}, {"B": 60, "C": 40})
    assert set(kq) == {"ok", "data", "errors"}
    kq = w.submit_wharton("HS1", {}, {"B": 1})
    assert set(kq) == {"ok", "data", "errors"} and all(
        set(e) == {"code", "params"} for e in kq["errors"])


def test_khoa_khong_phai_chuoi_khong_lam_hong_ham(w):
    kq = w.submit_wharton("HS1", {"A": 100}, {1: 60, 2: 40})
    assert kq["ok"] is False and kq["errors"]            # khoá ngoài tập, không ném ngoại lệ
