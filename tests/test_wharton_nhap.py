"""Điểm Wharton (A13, vòng 2): nạp CSV nguyện vọng có cột điểm Wharton (`wp_k`).

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.

Điều phải giữ:
  * ghép `wp_k` với `pref_k` theo HẬU TỐ SỐ (cả cột theo buổi `<buoi>_wp_k` và dạng dài `wp`);
  * `tier` lấy từ ô tick HIỆN TẠI lúc ghi; nạp lại cho một em thì thay MỌI dòng Wharton cũ của em;
  * Wharton tắt: cột `wp` chỉ bị bỏ qua kèm cảnh báo, nguyện vọng nạp y như tệp không có cột đó;
  * nạp KHÔNG bị chặn vì hồ sơ chưa hợp lệ — chỉ cảnh báo (chặn là việc của pipeline).
"""

import pytest

from _wharton import (bat_wharton, canh_bao, chen_bids, dong_bids, dung_clb, dung_hs, ma_loi)


@pytest.fixture
def w(api):
    """Workspace bật Wharton, ba CLB một buổi (A thi), HS1 đã có ô tick A."""
    bat_wharton(api)
    dung_clb(api, A=5, B=5, C=5)
    dung_hs(api, "HS1", tick={"HS1": ["A"]})
    return api


def _nap(api, csv_text):
    kq = api.import_preferences_csv(csv_text)
    assert kq["ok"], kq["errors"]
    return kq


# ------------------------------------------------------------------ ghép cột

def test_dang_rong_ghep_wp_k_voi_pref_k_va_tier_theo_o_tick(w):
    kq = _nap(w, "student_id,name,pref_1,wp_1,pref_2,wp_2\nHS1,An,A,100,B,100\n")
    assert dong_bids(w) == [("HS1", "A", 1, 100), ("HS1", "B", 2, 100)]
    assert canh_bao(kq, "wharton_chua_dung_het") == []


def test_ghep_theo_hau_to_so_khong_theo_vi_tri(w):
    # cột wp đặt ngược thứ tự và pref_2 để trống: wp_2 KHÔNG được gán nhầm cho pref_3
    kq = _nap(w, "student_id,name,wp_3,pref_3,wp_2,pref_2,wp_1,pref_1\n"
                 "HS1,An,40,C,0,,100,A\n")
    assert dong_bids(w) == [("HS1", "A", 1, 100), ("HS1", "C", 2, 40)]
    # wp_2 = 0 mà không có pref_2: cảnh báo không có nguyện vọng
    assert [e["params"]["cot"] for e in canh_bao(kq, "csv_wp_khong_co_nguyen_vong")] == ["wp_2"]


def test_cot_theo_buoi_ghep_dung(api):
    bat_wharton(api)
    dung_clb(api, A=(5, "thu_3"), B=(5, "thu_3"), C=(5, "thu_5"), D=(5, "thu_5"))
    dung_hs(api, "HS1", tick={"HS1": ["A", "B"]})          # thứ 3 thi cả A, B; thứ 5 không thi
    kq = _nap(api, "student_id,name,thu_3_pref_1,thu_3_wp_1,thu_3_pref_2,thu_3_wp_2,"
                   "thu_5_pref_1,thu_5_wp_1,thu_5_pref_2,thu_5_wp_2\n"
                   "HS1,An,A,70,B,30,D,25,C,75\n")
    assert dong_bids(api) == [("HS1", "A", 1, 70), ("HS1", "B", 1, 30),
                              ("HS1", "C", 2, 75), ("HS1", "D", 2, 25)]
    # mỗi quỹ mỗi buổi đủ 100: không cảnh báo hồ sơ
    assert [m for m in ma_loi(kq) if m.startswith("wharton_")] == []


def test_dang_dai_ghep_cot_wp(w):
    kq = _nap(w, "student_id,name,club_id,rank,wp\nHS1,An,A,1,100\nHS1,An,B,2,60\nHS1,An,C,3,40\n")
    assert dong_bids(w) == [("HS1", "A", 1, 100), ("HS1", "B", 2, 60), ("HS1", "C", 2, 40)]
    assert [m for m in ma_loi(kq) if m.startswith("wharton_")] == []


# ------------------------------------------------------------------ thay thế

def test_nap_lai_thay_moi_dong_cu_cua_em_va_giu_em_khong_co_trong_tep(w):
    dung_hs(w, "HS2")
    chen_bids(w, [("HS2", "B", 2, 100)])
    _nap(w, "student_id,name,pref_1,wp_1,pref_2,wp_2\nHS1,An,A,100,B,100\n")
    _nap(w, "student_id,name,pref_1,wp_1,pref_2,wp_2\nHS1,An,A,100,C,100\n")
    assert dong_bids(w) == [("HS1", "A", 1, 100), ("HS1", "C", 2, 100), ("HS2", "B", 2, 100)]


# ------------------------------------------------------------------ ô sai / trống

@pytest.mark.parametrize("o", ['"12,5"', "-3", "abc", "30.0", '"30,0"', "+5", "1e2"])
def test_o_wp_khong_phai_so_nguyen_thi_canh_bao_va_khong_luu_o_do(w, o):
    kq = _nap(w, "student_id,name,pref_1,wp_1,pref_2,wp_2\nHS1,An,A,100,B,%s\n" % o)
    assert dong_bids(w) == [("HS1", "A", 1, 100)]          # ô khác vẫn lưu
    ds = canh_bao(kq, "csv_wp_khong_hop_le")
    assert len(ds) == 1 and ds[0]["params"]["student_id"] == "HS1"
    assert ds[0]["params"]["club_id"] == "B"
    assert ds[0]["params"]["gia_tri"] == o.strip('"')


def test_o_wp_trong_thi_khong_co_dong_nao(w):
    _nap(w, "student_id,name,pref_1,wp_1,pref_2,wp_2\nHS1,An,A,100,B,\n")
    assert dong_bids(w) == [("HS1", "A", 1, 100)]


def test_diem_0_la_gia_tri_hop_le_va_duoc_luu(w):
    _nap(w, "student_id,name,pref_1,wp_1,pref_2,wp_2,pref_3,wp_3\nHS1,An,A,100,B,0,C,100\n")
    assert dong_bids(w) == [("HS1", "A", 1, 100), ("HS1", "B", 2, 0), ("HS1", "C", 2, 100)]


def test_wp_k_ma_pref_k_trong_thi_canh_bao_khong_co_nguyen_vong(w):
    kq = _nap(w, "student_id,name,pref_1,wp_1,pref_2,wp_2\nHS1,An,A,100,,50\n")
    assert dong_bids(w) == [("HS1", "A", 1, 100)]
    ds = canh_bao(kq, "csv_wp_khong_co_nguyen_vong")
    assert [(e["params"]["student_id"], e["params"]["cot"]) for e in ds] == [("HS1", "wp_2")]


# ------------------------------------------------------------------ Wharton tắt

def test_wharton_tat_cot_wp_bi_bo_qua_kem_canh_bao_va_nguyen_vong_y_nhu_khong_co_cot(api):
    dung_clb(api, A=5, B=5)
    dung_hs(api, "HS1", "HS2")
    kq = _nap(api, "student_id,name,pref_1,wp_1,pref_2,wp_2\nHS1,An,A,100,B,50\nHS2,Bo,B,,A,7\n")
    assert dong_bids(api) == []
    ds = canh_bao(kq, "csv_wp_bo_qua")
    assert len(ds) == 1 and ds[0]["params"]["n"] == 3          # 3 ô wp có chữ (ô trống không đếm)
    # đối chứng: tệp không có cột wp cho cùng nguyện vọng
    with api._ket_noi_doc() as cur:
        co_wp = [tuple(r) for r in cur.execute(
            "SELECT student_id, club_id, rank FROM preferences ORDER BY 1, 3")]
    kq2 = _nap(api, "student_id,name,pref_1,pref_2\nHS1,An,A,B\nHS2,Bo,B,A\n")
    with api._ket_noi_doc() as cur:
        khong_wp = [tuple(r) for r in cur.execute(
            "SELECT student_id, club_id, rank FROM preferences ORDER BY 1, 3")]
    assert co_wp == khong_wp
    assert canh_bao(kq2, "csv_wp_bo_qua") == []
    assert [m for m in ma_loi(kq) if m.startswith("wharton_")] == []   # không kiểm hồ sơ khi tắt


def test_wharton_tat_khong_co_o_wp_nao_co_chu_thi_khong_canh_bao(api):
    dung_clb(api, A=5)
    kq = _nap(api, "student_id,name,pref_1,wp_1\nHS1,An,A,\n")
    assert canh_bao(kq, "csv_wp_bo_qua") == []


def test_wharton_tat_dang_dai_va_theo_buoi_cung_bi_bo_qua(api):
    dung_clb(api, A=(5, "thu_3"))
    kq = _nap(api, "student_id,name,club_id,rank,wp\nHS1,An,A,1,100\n")
    assert dong_bids(api) == [] and canh_bao(kq, "csv_wp_bo_qua")[0]["params"]["n"] == 1
    kq = _nap(api, "student_id,name,thu_3_pref_1,thu_3_wp_1\nHS2,Bo,A,100\n")
    assert dong_bids(api) == [] and canh_bao(kq, "csv_wp_bo_qua")[0]["params"]["n"] == 1


# ------------------------------------------------------------------ tệp không có cột wp

def test_tep_khong_co_cot_wp_khi_bat_thi_xoa_dong_cua_clb_bi_bo_khoi_nguyen_vong(w):
    _nap(w, "student_id,name,pref_1,wp_1,pref_2,wp_2,pref_3,wp_3\nHS1,An,A,100,B,60,C,40\n")
    assert len(dong_bids(w)) == 3
    kq = _nap(w, "student_id,name,pref_1,pref_2\nHS1,An,A,B\n")        # bỏ C, không có cột wp
    assert dong_bids(w) == [("HS1", "A", 1, 100), ("HS1", "B", 2, 60)]
    assert canh_bao(kq, "csv_wp_bo_qua") == []


# ------------------------------------------------------------------ cảnh báo hồ sơ

def test_phan_hoi_co_canh_bao_ho_so_chi_cho_em_vua_nap(w):
    dung_hs(w, "HS2")
    chen_bids(w, [("HS2", "B", 2, 10)])               # HS2 sai nhưng KHÔNG có trong tệp
    with w._ket_noi_ghi() as cur:
        cur.execute("INSERT INTO preferences VALUES ('HS2', 'B', 1)")
    kq = _nap(w, "student_id,name,pref_1,wp_1,pref_2,wp_2\nHS1,An,A,100,B,90\n")
    ds = canh_bao(kq, "wharton_chua_dung_het")
    assert [(e["params"]["student_id"], e["params"]["thieu"], e["params"]["quy"])
            for e in ds] == [("HS1", 10, 2)]
    assert all(e["params"]["student_id"] == "HS1" for e in kq["data"]["warnings"]
               if e["code"].startswith("wharton_"))


def test_ho_so_sai_khong_chan_viec_nap(w):
    kq = _nap(w, "student_id,name,pref_1,wp_1,pref_2,wp_2\nHS1,An,A,100,B,90\n")
    assert kq["data"]["n_students_with_preferences_written"] == 1
    assert dong_bids(w) == [("HS1", "A", 1, 100), ("HS1", "B", 2, 90)]


# ------------------------------------------------------------------ nhận loại tệp

@pytest.mark.parametrize("csv_text,fmt", [
    ("student_id,name,pref_1,wp_1\nHS1,An,A,100\n", "wide"),
    ("student_id,name,thu_3_pref_1,thu_3_wp_1\nHS1,An,A,100\n", "wide_theo_buoi"),
    ("student_id,name,club_id,rank,wp\nHS1,An,A,1,100\n", "long"),
])
def test_nhan_dung_loai_tep_khi_co_cot_wp(api, csv_text, fmt):
    kq = api.detect_csv_kind(csv_text)
    assert kq["ok"] and kq["data"]["kind"] == "preferences" and kq["data"]["format"] == fmt
    assert kq["data"]["confident"] is True
    pv = api.preview_import_csv(csv_text, "preferences")
    assert pv["ok"] and pv["data"]["n_students_detected"] == 1
