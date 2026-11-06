"""T4M-M3: đối chiếu hai lần xuất List (đợt bổ sung) — em mới, em rút, dòng đổi NV / Lớp / CoSo.

kiem_nhan (T4M_MICROSOFT.md §8): hai tệp giống nhau => báo cáo rỗng; thêm / xoá / sửa MỘT dòng => đúng
MỘT mục đúng loại; email khác hoa-thường không phải thay đổi; kiosk không bị đụng.
Dữ liệu hoàn toàn MÔ PHỎNG.
"""

import csv
import os
import sys

import pytest

openpyxl = pytest.importorskip("openpyxl")

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))

import bieu_mau as bm  # noqa: E402
import doi_chieu_lists as dc  # noqa: E402
import sinh_xuat_lists_gia as lists_gia  # noqa: E402

MIEN = "@truong-gia.example.test"
# 3 em × 2 ngày; thu_2: clb_covua, clb_vanhoc, clb_nhiepanh; thu_3: clb_tienganh, clb_mythuat
GOC_DONG = [
    # email, coso, lop, thu, NV1, NV2
    ("a" + MIEN, "CS1", "9A1", "Thứ 2", "clb_covua", "clb_vanhoc"),
    ("a" + MIEN, "CS1", "9A1", "Thứ 3", "clb_tienganh", ""),
    ("b" + MIEN, "CS1", "9A2", "Thứ 2", "clb_vanhoc", ""),
    ("b" + MIEN, "CS1", "9A2", "Thứ 3", "clb_mythuat", "clb_tienganh"),
    ("c" + MIEN, "CS2", "8B1", "Thứ 2", "clb_nhiepanh", ""),
    ("c" + MIEN, "CS2", "8B1", "Thứ 3", "", ""),
]


@pytest.fixture
def de():
    return bm.doc_de_thi()


def _ghi(duong, dong=GOC_DONG, cot=None):
    cot = cot or lists_gia.COT
    with open(duong, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\r\n")
        w.writerow(cot)
        for email, co_so, lop, thu, nv1, nv2 in dong:
            d = {c: "" for c in cot}
            d.update({"Email": email, "HoTen": email[:1].upper(), "CoSo": co_so, "Lop": lop,
                      "Thu": thu, "NV1": nv1, "NV2": nv2})
            w.writerow([d[c] for c in cot])
    return str(duong)


def _hai(tmp_path, moi, cu=GOC_DONG):
    return _ghi(tmp_path / "cu.csv", cu), _ghi(tmp_path / "moi.csv", moi)


def _kinds(kq):
    return [(m["loai"], m["email"], m["thu"]) for m in kq["muc"]]


def test_hai_tep_giong_nhau_bao_cao_rong(tmp_path, de):
    cu, moi = _hai(tmp_path, GOC_DONG)
    kq = dc.doi_chieu(cu, moi, de)
    assert kq["muc"] == []


def test_thu_tu_dong_khong_la_thay_doi(tmp_path, de):
    cu, moi = _hai(tmp_path, list(reversed(GOC_DONG)))
    assert dc.doi_chieu(cu, moi, de)["muc"] == []


def test_em_moi_dung_mot_muc(tmp_path, de):
    them = GOC_DONG + [("d" + MIEN, "CS1", "9A1", "Thứ 2", "clb_covua", ""),
                       ("d" + MIEN, "CS1", "9A1", "Thứ 3", "clb_mythuat", "")]
    kq = dc.doi_chieu(*_hai(tmp_path, them), de)
    assert _kinds(kq) == [("moi", "d" + MIEN, "")]


def test_em_rut_dung_mot_muc(tmp_path, de):
    bot = [d for d in GOC_DONG if not d[0].startswith("c")]
    kq = dc.doi_chieu(*_hai(tmp_path, bot), de)
    assert _kinds(kq) == [("rut", "c" + MIEN, "")]


def test_sua_mot_nguyen_vong_dung_mot_muc(tmp_path, de):
    sua = list(GOC_DONG)
    sua[2] = ("b" + MIEN, "CS1", "9A2", "Thứ 2", "clb_covua", "")
    kq = dc.doi_chieu(*_hai(tmp_path, sua), de)
    assert _kinds(kq) == [("doi_nv", "b" + MIEN, "thu_2")]
    m = kq["muc"][0]
    assert m["cu"] == "clb_vanhoc" and m["moi"] == "clb_covua"


def test_doi_thu_tu_nguyen_vong_la_thay_doi(tmp_path, de):
    sua = list(GOC_DONG)
    sua[0] = ("a" + MIEN, "CS1", "9A1", "Thứ 2", "clb_vanhoc", "clb_covua")
    assert _kinds(dc.doi_chieu(*_hai(tmp_path, sua), de)) == [("doi_nv", "a" + MIEN, "thu_2")]


def test_xoa_mot_dong_cua_em_con_lai_la_doi_nv(tmp_path, de):
    bot = GOC_DONG[:1] + GOC_DONG[2:]          # bỏ dòng (a, Thứ 3)
    kq = dc.doi_chieu(*_hai(tmp_path, bot), de)
    assert _kinds(kq) == [("doi_nv", "a" + MIEN, "thu_3")]
    assert kq["muc"][0]["moi"] == ""


def test_them_dong_ngay_moi_cho_em_cu_la_doi_nv(tmp_path, de):
    cu = GOC_DONG[:-1]                          # c chưa có dòng Thứ 3 (trống) -> vẫn như nhau
    kq = dc.doi_chieu(*_hai(tmp_path, GOC_DONG, cu), de)
    assert kq["muc"] == []                     # dòng trống NV = không nguyện vọng = không đổi
    moi = GOC_DONG + [("a" + MIEN, "CS1", "9A1", "Thứ 4", "clb_robotics", "")]
    kq = dc.doi_chieu(*_hai(tmp_path, moi), de)
    assert _kinds(kq) == [("doi_nv", "a" + MIEN, "thu_4")]


def test_doi_lop_dung_mot_muc_du_nhieu_dong(tmp_path, de):
    sua = [d if d[0] != "b" + MIEN else (d[0], d[1], "9A3") + d[3:] for d in GOC_DONG]
    kq = dc.doi_chieu(*_hai(tmp_path, sua), de)
    assert _kinds(kq) == [("doi_lop", "b" + MIEN, "")]
    assert kq["muc"][0]["cu"] == "9A2" and kq["muc"][0]["moi"] == "9A3"


def test_doi_co_so_dung_mot_muc(tmp_path, de):
    sua = [d if d[0] != "a" + MIEN else (d[0], "CS2") + d[2:] for d in GOC_DONG]
    kq = dc.doi_chieu(*_hai(tmp_path, sua), de)
    assert _kinds(kq) == [("doi_co_so", "a" + MIEN, "")]


def test_email_khac_hoa_thuong_khong_la_thay_doi(tmp_path, de):
    hoa = [(d[0].upper().replace("@TRUONG", "@truong"),) + d[1:] for d in GOC_DONG]
    assert hoa[0][0] != GOC_DONG[0][0]
    assert dc.doi_chieu(*_hai(tmp_path, hoa), de)["muc"] == []


def test_co_so_loc_ca_hai_tep(tmp_path, de):
    sua = list(GOC_DONG)
    sua[4] = ("c" + MIEN, "CS2", "8B1", "Thứ 2", "clb_covua", "")      # c ở CS2 đổi NV
    sua[2] = ("b" + MIEN, "CS1", "9A2", "Thứ 2", "clb_covua", "")       # b ở CS1 đổi NV
    cu, moi = _hai(tmp_path, sua)
    assert _kinds(dc.doi_chieu(cu, moi, de, co_so="CS1")) == [("doi_nv", "b" + MIEN, "thu_2")]
    assert len(dc.doi_chieu(cu, moi, de)["muc"]) == 2


def test_em_chuyen_co_so_khi_loc_la_rut_va_moi(tmp_path, de):
    """Lọc CS1: a sang CS2 -> biến mất khỏi CS1 => 'rut'; ở CS2 thì là 'moi'."""
    sua = [d if d[0] != "a" + MIEN else (d[0], "CS2") + d[2:] for d in GOC_DONG]
    cu, moi = _hai(tmp_path, sua)
    assert _kinds(dc.doi_chieu(cu, moi, de, co_so="CS1")) == [("rut", "a" + MIEN, "")]
    assert _kinds(dc.doi_chieu(cu, moi, de, co_so="CS2")) == [("moi", "a" + MIEN, "")]


def test_thieu_cot_bat_buoc_bao_loi_khong_ghi_tep(tmp_path, de):
    cu, _ = _hai(tmp_path, GOC_DONG)
    xau = tmp_path / "xau.csv"
    xau.write_text("Email,HoTen\nx@y.test,X\n", encoding="utf-8")
    ra = tmp_path / "bc.xlsx"
    assert dc.main([cu, str(xau), "--ra", str(ra)]) == 1
    assert not ra.exists()


def test_dong_lenh_in_tom_tat_va_ghi_xlsx(tmp_path, de, capsys):
    sua = list(GOC_DONG)
    sua[2] = ("b" + MIEN, "CS1", "9A2", "Thứ 2", "clb_covua", "")
    cu, moi = _hai(tmp_path, sua + [("d" + MIEN, "CS1", "9A1", "Thứ 2", "clb_covua", "")])
    ra = tmp_path / "bc.xlsx"
    assert dc.main([cu, moi, "--ra", str(ra)]) == 0
    out = capsys.readouterr().out
    assert "1 em mới" in out and "0 em rút" in out and "1 dòng đổi nguyện vọng" in out
    wb = openpyxl.load_workbook(str(ra), read_only=True)
    dong = list(wb[wb.sheetnames[0]].iter_rows(values_only=True))
    wb.close()
    assert len(dong) == 1 + 2                   # tiêu đề + 2 mục


def test_dong_lenh_khong_doi_gi_van_ghi_bao_cao_rong(tmp_path, de, capsys):
    cu, moi = _hai(tmp_path, GOC_DONG)
    ra = tmp_path / "bc.xlsx"
    assert dc.main([cu, moi, "--ra", str(ra)]) == 0
    assert "Không có thay đổi" in capsys.readouterr().out
    wb = openpyxl.load_workbook(str(ra), read_only=True)
    assert len(list(wb[wb.sheetnames[0]].iter_rows(values_only=True))) == 1
    wb.close()


def test_khong_dung_den_kiosk():
    """kiem_nhan 'không đổi gì ở kiosk': công cụ không nạp lõi / CSDL."""
    src = open(os.path.join(GOC, "mau_forms_thi_clb", "doi_chieu_lists.py"), encoding="utf-8").read()
    for cam in ("import database", "import app_core", "sqlite3", "run_rbda", "import api"):
        assert cam not in src


# ------------------------------------------------------------------ mã CLB lạ không được giấu thay đổi

LA = [
    ("a" + MIEN, "CS1", "9A1", "Thứ 2", "T2-CLB01", "T2-CLB02"),
    ("a" + MIEN, "CS1", "9A1", "Thứ 3", "T3-CLB01", ""),
    ("b" + MIEN, "CS1", "9A2", "Thứ 2", "T2-CLB02", ""),
    ("b" + MIEN, "CS1", "9A2", "Thứ 3", "T3-CLB02", "T3-CLB01"),
]


def test_ma_la_cung_mot_doi_nv_dung_mot_muc(tmp_path, de):
    sua = list(LA)
    sua[0] = ("a" + MIEN, "CS1", "9A1", "Thứ 2", "T2-CLB02", "T2-CLB01")   # đổi chỗ NV1/NV2
    kq = dc.doi_chieu(*_hai(tmp_path, sua, LA), de)
    assert _kinds(kq) == [("doi_nv", "a" + MIEN, "thu_2")]
    assert kq["n_clb_la"] > 0


def test_ma_la_giong_nhau_khong_thay_doi_van_canh_bao(tmp_path, de):
    kq = dc.doi_chieu(*_hai(tmp_path, LA, LA), de)
    assert kq["muc"] == [] and kq["n_clb_la"] > 0


def test_ma_la_xoa_dong_van_thay(tmp_path, de):
    kq = dc.doi_chieu(*_hai(tmp_path, LA[:3], LA), de)
    assert _kinds(kq) == [("doi_nv", "b" + MIEN, "thu_3")]


def test_ma_clb_phan_biet_hoa_thuong(tmp_path, de):
    sua = list(LA)
    sua[2] = ("b" + MIEN, "CS1", "9A2", "Thứ 2", "t2-clb02", "")
    assert len(dc.doi_chieu(*_hai(tmp_path, sua, LA), de)["muc"]) == 1


def test_dong_lenh_canh_bao_dung_dau_khong_in_khong_thay_doi(tmp_path, de, capsys):
    cu, moi = _hai(tmp_path, LA, LA)
    assert dc.main([cu, moi]) == 0
    out = capsys.readouterr().out
    assert out.startswith("CẢNH BÁO: ")
    assert "không có trong de_thi.json" in out.splitlines()[0]
    assert "kiểm trước khi tin kết quả đối chiếu" in out.splitlines()[0]
    assert "Không có thay đổi giữa hai tệp" not in out


def test_dong_lenh_canh_bao_truoc_ca_khi_co_thay_doi(tmp_path, de, capsys):
    sua = list(LA)
    sua[0] = ("a" + MIEN, "CS1", "9A1", "Thứ 2", "T2-CLB02", "T2-CLB01")
    cu, moi = _hai(tmp_path, sua, LA)
    assert dc.main([cu, moi]) == 0
    out = capsys.readouterr().out
    assert out.startswith("CẢNH BÁO: ") and "1 dòng đổi nguyện vọng" in out


def test_khong_ma_la_khong_co_dong_canh_bao(tmp_path, de, capsys):
    cu, moi = _hai(tmp_path, GOC_DONG)
    assert dc.main([cu, moi]) == 0
    assert "CẢNH BÁO" not in capsys.readouterr().out
