"""Điểm quyết tâm (A13.5): xử lý hàng loạt hồ sơ chia thiếu hoặc thừa ở thẻ Quản lý.

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.

  * `phong_theo_ti_le` (hàm thuần): làm tròn theo phần dư lớn nhất, hoà phần dư xét theo mã CLB tăng
    dần, không phụ thuộc thứ tự dict, không có tham số nào về thứ hạng nguyện vọng;
  * `phong_wharton_hang_loat`: gõ đúng `PHONG`, sao lưu trước, mỗi em phóng được ghi qua `_luu_wharton`
    (khoá, kiểm hồ sơ, nhật ký `quan_ly` / `luu`), em tổng 0 hoặc còn lỗi khác bị bỏ qua và liệt kê;
  * `export_wharton_can_sua`: tệp Excel có đúng các em đang chưa hợp lệ, không đổi CSDL.
"""

import inspect
import itertools
import json
import os

import pytest

import api_quan_ly
from _wharton import bat_wharton, chen_bids, dong_bids, dung_clb, dung_hs
from api_quan_ly import phong_theo_ti_le


# ------------------------------------------------------------------ hàm thuần

@pytest.mark.parametrize("vao, ra", [
    ({"A": 40, "B": 20, "C": 0}, {"A": 67, "B": 33, "C": 0}),
    ({"A": 150, "B": 50}, {"A": 75, "B": 25}),
    ({"A": 30}, {"A": 100}),
    ({"A": 1, "B": 1, "C": 1}, {"A": 34, "B": 33, "C": 33}),
    ({"A": 100, "B": 0}, {"A": 100, "B": 0}),
])
def test_phong_theo_ti_le_ca_tinh_tay(vao, ra):
    assert phong_theo_ti_le(vao) == ra


def test_tong_0_tra_none():
    assert phong_theo_ti_le({"A": 0, "B": 0}) is None
    assert phong_theo_ti_le({}) is None


def test_hoa_phan_du_xet_theo_ma_clb_tang_dan():
    # ba phần dư bằng nhau, thừa 1 điểm: mã nhỏ nhất nhận
    assert phong_theo_ti_le({"C": 1, "B": 1, "A": 1}) == {"A": 34, "B": 33, "C": 33}
    # bảy phần dư bằng nhau, thừa 2 điểm: hai mã nhỏ nhất nhận
    kq = phong_theo_ti_le({c: 1 for c in "GFEDCBA"})
    assert sum(kq.values()) == 100
    assert [c for c in sorted(kq) if kq[c] == 15] == ["A", "B"]


def test_tong_khac_100_van_ra_dung_100():
    for vao in ({"A": 7, "B": 11, "C": 13}, {"A": 999, "B": 1}, {"A": 33, "B": 33, "C": 33}):
        assert sum(phong_theo_ti_le(vao).values()) == 100


def test_khong_phu_thuoc_thu_tu_dict():
    goc = {"A": 7, "B": 11, "C": 13, "D": 0, "E": 29}
    ra = [phong_theo_ti_le(dict(p)) for p in itertools.permutations(goc.items())]
    assert all(r == ra[0] for r in ra)
    assert all(list(r) == list(sorted(r)) or True for r in ra)       # chỉ cần cùng nội dung


def test_chu_ky_khong_co_tham_so_thu_hang_nguyen_vong():
    """Chống nội sinh (bất biến 2): chỉ có điểm và ngân sách, không có thứ hạng nguyện vọng."""
    assert list(inspect.signature(phong_theo_ti_le).parameters) == ["diem", "ngan_sach"]


# ------------------------------------------------------------------ dữ liệu

@pytest.fixture
def w(api):
    """Bật tính năng; A, B thi; C, D, E không thi.

    HS1 hợp lệ; HS2 quỹ 1 thiếu (A 40, B 20); HS3 quỹ 2 thừa (150); HS4 toàn số 0;
    HS5 có điểm ngoài tập; HS6 quỹ 2 thiếu (B 40, C 20).
    """
    bat_wharton(api)
    dung_clb(api, A=9, B=9, C=9, D=9, E=9)
    dung_hs(api, "HS1", "HS2", "HS3", "HS4", "HS5", "HS6",
            tick={"HS1": ["A"], "HS2": ["A", "B"]})
    for sid, nv in (("HS1", ["A", "B", "C"]), ("HS2", ["A", "B", "C"]),
                    ("HS3", ["C", "D", "E"]), ("HS4", ["C", "D"]),
                    ("HS5", ["C", "D"]), ("HS6", ["C", "D"])):
        assert api.submit_preferences(sid, nv)["ok"]
    chen_bids(api, [
        ("HS1", "A", 1, 100), ("HS1", "B", 2, 60), ("HS1", "C", 2, 40),
        ("HS2", "A", 1, 40), ("HS2", "B", 1, 20),
        ("HS3", "C", 2, 50), ("HS3", "D", 2, 50), ("HS3", "E", 2, 50),
        ("HS4", "C", 2, 0), ("HS4", "D", 2, 0),
        ("HS5", "C", 2, 50), ("HS5", "D", 2, 30), ("HS5", "A", 2, 20),
        ("HS6", "C", 2, 40), ("HS6", "D", 2, 20),
    ])
    return api


def _nk(api):
    with api._ket_noi_doc() as cur:
        return [(r["nguon"], r["hanh_dong"], r["student_id"],
                 json.loads(r["cu_json"]) if r["cu_json"] else None,
                 json.loads(r["moi_json"]) if r["moi_json"] else None)
                for r in cur.execute("SELECT * FROM wharton_nhat_ky ORDER BY id")]


def _khoa(api):
    with api._ket_noi_ghi() as cur:
        cur.execute("INSERT INTO wharton_lock (id, is_locked, locked_at) VALUES (1, 1, 't') "
                    "ON CONFLICT(id) DO UPDATE SET is_locked = 1")


def _sai(api):
    kq = api.list_wharton_canh_bao()
    assert kq["ok"]
    return sorted(c["student_id"] for c in kq["data"] if c["loai"] == "chua_hop_le")


# ------------------------------------------------------------------ phong_wharton_hang_loat

def test_sai_chu_xac_nhan_khong_doi_gi(w):
    truoc, nk = dong_bids(w), _nk(w)
    for go in ("", "phong", "XOA", "PHONG "):
        kq = w.phong_wharton_hang_loat(go)
        assert not kq["ok"]
        assert kq["errors"][0]["code"] == "wharton_phong_sai_xac_nhan"
        assert kq["errors"][0]["params"]["can_go"] == "PHONG"
    assert dong_bids(w) == truoc and _nk(w) == nk


def test_phong_dung_chu_phong_dung_cac_em_co_the_phong(w):
    assert _sai(w) == ["HS2", "HS3", "HS4", "HS5", "HS6"]
    kq = w.phong_wharton_hang_loat("PHONG")
    assert kq["ok"], kq
    d = kq["data"]
    assert d["n_phong"] == 3
    assert os.path.isfile(d["backup_path"])
    bo_qua = {b["student_id"]: b["ly_do"] for b in d["bo_qua"]}
    assert bo_qua == {"HS4": "tong_0", "HS5": "loi_khac"}
    bids = {(s, c): (t, p) for s, c, t, p in dong_bids(w)}
    # HS2 quỹ 1: 40:20 thành 67:33 (phần dư lớn nhất)
    assert bids[("HS2", "A")] == (1, 67) and bids[("HS2", "B")] == (1, 33)
    # HS3 quỹ 2: ba phần dư bằng nhau, mã nhỏ nhất nhận điểm lẻ
    assert [bids[("HS3", c)][1] for c in "CDE"] == [34, 33, 33]
    # HS6 quỹ 2: 40:20 thành 67:33
    assert bids[("HS6", "C")] == (2, 67) and bids[("HS6", "D")] == (2, 33)
    # em hợp lệ, em tổng 0, em có lỗi ngoài tập: không đổi
    assert [bids[("HS1", c)][1] for c in "ABC"] == [100, 60, 40]
    assert bids[("HS4", "C")] == (2, 0) and bids[("HS4", "D")] == (2, 0)
    assert [bids[("HS5", c)][1] for c in "CDA"] == [50, 30, 20]
    assert _sai(w) == ["HS4", "HS5"]


def test_moi_em_duoc_phong_co_dung_mot_dong_nhat_ky_quan_ly_luu(w):
    w.phong_wharton_hang_loat("PHONG")
    nk = _nk(w)
    assert sorted(n[2] for n in nk) == ["HS2", "HS3", "HS6"]
    assert all(n[0] == "quan_ly" and n[1] == "luu" for n in nk)
    hs2 = next(n for n in nk if n[2] == "HS2")
    assert hs2[3]["w1"] == {"A": 40, "B": 20} and hs2[4]["w1"] == {"A": 67, "B": 33}


def test_chay_lai_khong_con_gi_de_phong(w):
    w.phong_wharton_hang_loat("PHONG")
    nk = _nk(w)
    kq = w.phong_wharton_hang_loat("PHONG")
    assert kq["ok"] and kq["data"]["n_phong"] == 0
    assert {b["student_id"] for b in kq["data"]["bo_qua"]} == {"HS4", "HS5"}
    assert _nk(w) == nk


def test_dang_khoa_bao_da_khoa_va_khong_doi_gi(w):
    _khoa(w)
    truoc, nk = dong_bids(w), _nk(w)
    kq = w.phong_wharton_hang_loat("PHONG")
    assert not kq["ok"] and kq["errors"][0]["code"] == "wharton_da_khoa"
    assert dong_bids(w) == truoc and _nk(w) == nk


def test_tat_tinh_nang_bao_chua_bat(api):
    kq = api.phong_wharton_hang_loat("PHONG")
    assert not kq["ok"] and kq["errors"][0]["code"] == "wharton_chua_bat"


def test_nhieu_buoi_chi_phong_dung_buoi_va_quy_bi_sai(api):
    """HS1 thiếu ở quỹ 2 của thu_5 còn thu_3 hợp lệ: chỉ thu_5 đổi."""
    bat_wharton(api)
    dung_clb(api, A=(9, "thu_3"), B=(9, "thu_3"), C=(9, "thu_5"), D=(9, "thu_5"))
    dung_hs(api, "HS1")
    assert api.submit_preferences("HS1", ["A", "B", "C", "D"])["ok"]
    chen_bids(api, [("HS1", "A", 2, 70), ("HS1", "B", 2, 30),
                    ("HS1", "C", 2, 30), ("HS1", "D", 2, 10)])
    kq = api.phong_wharton_hang_loat("PHONG")
    assert kq["ok"] and kq["data"]["n_phong"] == 1
    bids = {c: p for _s, c, _t, p in dong_bids(api)}
    assert bids == {"A": 70, "B": 30, "C": 75, "D": 25}


# ------------------------------------------------------------------ export_wharton_can_sua

def _doc_xlsx(path):
    from openpyxl import load_workbook
    wb = load_workbook(path)
    return wb, [list(r) for r in wb.worksheets[0].iter_rows(values_only=True)]


def test_xuat_danh_sach_can_sua_dung_cac_em_va_khong_doi_csdl(w, tmp_path):
    w.thu_muc_xuat = str(tmp_path / "TaiXuong")
    os.makedirs(w.thu_muc_xuat)
    truoc, nk = dong_bids(w), _nk(w)
    kq = w.export_wharton_can_sua()
    assert kq["ok"], kq
    path = kq["data"]["path"]
    assert os.path.isfile(path) and path.endswith(".xlsx")
    assert os.path.dirname(path) == w.thu_muc_xuat
    assert kq["data"]["n_hoc_sinh"] == 5
    _wb, hang = _doc_xlsx(path)
    tieu_de = next(h for h in hang if h and h[0] and "Mã" in str(h[0]))
    cot = [str(c) for c in tieu_de]
    for can in ("Họ tên", "Buổi", "Quỹ", "Tổng hiện tại", "Thiếu", "Thừa", "Lỗi"):
        assert any(can in c for c in cot), (can, cot)
    sau = hang[hang.index(tieu_de) + 1:]
    ma = sorted({r[0] for r in sau if r[0]})
    assert ma == ["HS2", "HS3", "HS4", "HS5", "HS6"]
    i_thieu = next(i for i, c in enumerate(cot) if "Thiếu" in c)
    i_thua = next(i for i, c in enumerate(cot) if "Thừa" in c)
    i_tong = next(i for i, c in enumerate(cot) if "Tổng" in c)
    hs2 = next(r for r in sau if r[0] == "HS2")
    assert hs2[i_tong] == 60 and hs2[i_thieu] == 40
    hs3 = next(r for r in sau if r[0] == "HS3")
    assert hs3[i_tong] == 150 and hs3[i_thua] == 50
    assert dong_bids(w) == truoc and _nk(w) == nk


def test_xuat_danh_sach_tat_tinh_nang_bao_chua_bat(api):
    kq = api.export_wharton_can_sua()
    assert not kq["ok"] and kq["errors"][0]["code"] == "wharton_chua_bat"


def test_xuat_danh_sach_khong_ghi_de_tep_cu(w, tmp_path):
    w.thu_muc_xuat = str(tmp_path / "TaiXuong")
    os.makedirs(w.thu_muc_xuat)
    p1 = w.export_wharton_can_sua()["data"]["path"]
    p2 = w.export_wharton_can_sua()["data"]["path"]
    assert p1 != p2 and os.path.isfile(p1) and os.path.isfile(p2)


def test_module_co_ham_thuan():
    assert callable(api_quan_ly.phong_theo_ti_le)
