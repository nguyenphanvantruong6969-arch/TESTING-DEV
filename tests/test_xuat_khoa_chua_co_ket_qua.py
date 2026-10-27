"""Xuất kết quả khi chưa có kết quả xếp (A13.5, vấn đề #4; áp cho TOÀN ứng dụng).

Dữ liệu dưới đây là dữ liệu MÔ PHỎNG dựng trong test.

  * `export_ket_qua` và `export_csv` từ chối với `xuat_chua_co_ket_qua` và KHÔNG tạo tệp nào;
  * có kết quả thì xuất như cũ;
  * xuất dữ liệu đầu vào, Sổ nhập mẫu và xuất học sinh vẫn dùng được khi chưa có kết quả.
"""

import os

import pytest


@pytest.fixture
def api_chua_chay(api, tmp_path):
    """Có CLB, học sinh, nguyện vọng; CHƯA chạy xếp."""
    api.thu_muc_xuat = str(tmp_path / "TaiXuong")
    os.makedirs(api.thu_muc_xuat)
    assert api.create_or_update_club("A", "CLB A", 2, 0, "")["ok"]
    assert api.create_or_update_club("B", "CLB B", 5, 0, "")["ok"]
    for sid in ("HS1", "HS2", "HS3"):
        assert api.create_student_if_missing(sid, "Em " + sid)["ok"]
        assert api.submit_preferences(sid, ["A", "B"])["ok"]
    return api


def _tep(api):
    return sorted(os.listdir(api.thu_muc_xuat))


def test_chua_co_ket_qua_export_ket_qua_bi_tu_choi_va_khong_tao_tep(api_chua_chay):
    for kem_csv in (False, True):
        kq = api_chua_chay.export_ket_qua("", kem_csv)
        assert not kq["ok"]
        assert [e["code"] for e in kq["errors"]] == ["xuat_chua_co_ket_qua"]
    assert _tep(api_chua_chay) == []


def test_chua_co_ket_qua_export_csv_bi_tu_choi_va_khong_tao_tep(api_chua_chay):
    kq = api_chua_chay.export_csv("")
    assert not kq["ok"]
    assert [e["code"] for e in kq["errors"]] == ["xuat_chua_co_ket_qua"]
    assert _tep(api_chua_chay) == []


def test_duong_tuyet_doi_cung_bi_tu_choi_va_khong_tao_tep(api_chua_chay, tmp_path):
    dich = str(tmp_path / "ra" / "kq.xlsx")
    os.makedirs(os.path.dirname(dich))
    assert not api_chua_chay.export_ket_qua(dich)["ok"]
    assert not api_chua_chay.export_csv(str(tmp_path / "ra" / "kq.csv"))["ok"]
    assert os.listdir(os.path.dirname(dich)) == []


def test_xuat_dau_vao_so_mau_va_hoc_sinh_van_dung_duoc(api_chua_chay):
    a = api_chua_chay
    assert a.export_du_lieu_dau_vao("")["ok"]
    assert a.tao_so_nhap_mau("")["ok"]
    assert a.export_hoc_sinh_csv(["HS1"], "")["ok"]
    assert len(_tep(a)) == 3


def test_co_ket_qua_thi_xuat_nhu_cu(api_chua_chay):
    a = api_chua_chay
    assert a.run_pipeline(seed=1)["ok"]
    kq = a.export_ket_qua("")
    assert kq["ok"], kq
    assert kq["data"]["n_hoc_sinh"] == 3 and os.path.isfile(kq["data"]["path"])
    assert kq["data"]["trang"]
    kq2 = a.export_csv("")
    assert kq2["ok"], kq2


def test_xoa_hoc_sinh_xong_chua_co_ket_qua_thi_lai_bi_khoa(api_chua_chay):
    a = api_chua_chay
    assert a.run_pipeline(seed=1)["ok"]
    assert a.export_ket_qua("")["ok"]
    assert a.reset_data("hoc_sinh", "XOA")["ok"]
    assert not a.get_trang_thai_ket_qua()["data"]["co_ket_qua"]
    kq = a.export_ket_qua("")
    assert not kq["ok"] and kq["errors"][0]["code"] == "xuat_chua_co_ket_qua"
