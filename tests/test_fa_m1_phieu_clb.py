"""FA-M1 (TH = chưa thử trên Microsoft thật): chuyển tệp Excel của Phiếu thiết lập CLB (Forms) sang Sổ nhập.

Phân loại tự động theo V§4.1: câu 2 = có -> TU_DO; câu 2 = không và câu 4 = không -> GIOI_HAN;
câu 2 = không và câu 4 = có -> TUYEN_CHON. Dữ liệu MÔ PHỎNG.
"""
import os
import sys

import openpyxl
import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))
sys.path.insert(0, GOC)

import chuyen_phieu_clb as pc  # noqa: E402
import so_nhap  # noqa: E402

TIEU_DE = pc.TIEU_DE_PHIEU


def _phieu(ten, buoi="Thứ 2", mo_nhom="", cho="", ly_do="", phong="", toi_thieu="8",
           can_thi="Không", thu_thach="", moc="", tieu_chi="", giu=""):
    d = dict(zip(TIEU_DE, [ten, buoi, "15:30", "Phòng A", mo_nhom, cho, ly_do, phong, toi_thieu,
                           can_thi, thu_thach, moc, tieu_chi, giu]))
    return [d[h] for h in TIEU_DE]


def _tep(tmp_path, dong):
    p = tmp_path / "phieu.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(TIEU_DE)
    for r in dong:
        ws.append(r)
    wb.save(p)
    return str(p)


def _doc(tmp_path, dong, **kw):
    return pc.doc_phieu_clb(_tep(tmp_path, dong), **kw)


def test_ba_loai_phan_theo_cau_2_va_cau_4(tmp_path):
    kq = _doc(tmp_path, [
        _phieu("CLB Cờ vua", mo_nhom="Có", phong="30"),
        _phieu("CLB Bóng rổ", mo_nhom="Không", cho="20", ly_do="Sân nhỏ"),
        _phieu("CLB Robot", mo_nhom="Không", cho="12", ly_do="Bộ lắp ráp", can_thi="Có",
               thu_thach="Trắc nghiệm", moc="6", tieu_chi="Đúng 6/10 câu"),
    ])
    theo = {c["name"]: c for c in kq["clubs"]}
    assert theo["CLB Cờ vua"]["loai"] == so_nhap.TU_DO
    assert theo["CLB Cờ vua"]["suc_chua_phong"] == 30
    assert theo["CLB Bóng rổ"]["loai"] == so_nhap.GIOI_HAN
    assert theo["CLB Bóng rổ"]["capacity"] == 20
    assert theo["CLB Robot"]["loai"] == so_nhap.TUYEN_CHON
    assert theo["CLB Robot"]["diem_san"] == 6
    assert theo["CLB Robot"]["so_toi_thieu"] == 8
    assert not kq["loi"]


def test_khai_tu_do_nhung_co_ly_do_gioi_han_bi_canh_bao(tmp_path):
    """V§4.1: CLB bị giới hạn thật bởi phòng/dụng cụ không được khai là Tự do."""
    kq = _doc(tmp_path, [_phieu("CLB Vẽ", mo_nhom="Có", phong="25", ly_do="Chỉ có 10 giá vẽ")])
    assert any(c["ma"] == "phieu_tu_do_co_ly_do_gioi_han" for c in kq["canh_bao"])


def test_gioi_han_thieu_cho_hoac_ly_do(tmp_path):
    kq = _doc(tmp_path, [_phieu("CLB A", mo_nhom="Không", cho="", ly_do="Phòng"),
                         _phieu("CLB B", mo_nhom="Không", cho="10", ly_do="")])
    assert [c["name"] for c in kq["clubs"]] == ["CLB B"]            # CLB A thiếu chỗ: loại, báo lỗi
    assert any(e["ma"] == "phieu_thieu_cho" and e["clb"] == "CLB A" for e in kq["loi"])
    assert any(c["ma"] == "phieu_thieu_ly_do" and c["clb"] == "CLB B" for c in kq["canh_bao"])


def test_cau_2_trong_khong_phan_loai_duoc(tmp_path):
    kq = _doc(tmp_path, [_phieu("CLB A", mo_nhom="")])
    assert kq["clubs"] == []
    assert any(e["ma"] == "phieu_thieu_cau_2" for e in kq["loi"])


@pytest.mark.parametrize("moc", ["", "0", "11", "abc", "5.5"])
def test_tuyen_chon_moc_sai(tmp_path, moc):
    kq = _doc(tmp_path, [_phieu("CLB A", mo_nhom="Không", cho="10", can_thi="Có",
                                thu_thach="Trắc nghiệm", moc=moc, tieu_chi="x")])
    assert kq["clubs"] == []
    assert any(e["ma"] == "phieu_moc_sai" for e in kq["loi"])


def test_thu_thach_video_anh_khong_cham_tu_dong(tmp_path):
    kq = _doc(tmp_path, [_phieu("CLB A", mo_nhom="Không", cho="10", can_thi="Có",
                                thu_thach="Video", moc="5", tieu_chi="x")])
    assert kq["clubs"][0]["loai"] == so_nhap.TUYEN_CHON
    assert any(c["ma"] == "phieu_thu_thach_khong_tu_cham" for c in kq["canh_bao"])


def test_nop_hai_lan_lay_phieu_cuoi(tmp_path):
    kq = _doc(tmp_path, [_phieu("CLB A", mo_nhom="Không", cho="10", ly_do="x"),
                         _phieu("CLB A", mo_nhom="Không", cho="14", ly_do="x")])
    assert [c["capacity"] for c in kq["clubs"]] == [14]
    assert any(c["ma"] == "phieu_nop_nhieu_lan" for c in kq["canh_bao"])


def test_khong_nop_phieu_mac_dinh_gioi_han_voi_cho_ky_truoc(tmp_path):
    ky_truoc = [{"name": "CLB Cũ", "buoi": "Thứ 3", "capacity": 15}]
    kq = _doc(tmp_path, [_phieu("CLB A", mo_nhom="Có", phong="30")], ky_truoc=ky_truoc)
    cu = next(c for c in kq["clubs"] if c["name"] == "CLB Cũ")
    assert (cu["loai"], cu["capacity"]) == (so_nhap.GIOI_HAN, 15)
    assert any(c["ma"] == "phieu_mac_dinh_ky_truoc" for c in kq["canh_bao"])


def test_giu_cho_tach_ma_hoc_sinh(tmp_path):
    kq = _doc(tmp_path, [_phieu("CLB A", mo_nhom="Không", cho="10", ly_do="x", giu="HS001, HS002;HS001")])
    assert kq["giu_cho"] == [("clb_a", "HS001"), ("clb_a", "HS002")]


def test_kiem_truoc_fa_chan_khi_buoi_khong_co_clb_tu_do(tmp_path):
    kq = _doc(tmp_path, [_phieu("CLB A", mo_nhom="Không", cho="10", ly_do="x")])
    assert any(e["code"] == "fa_thieu_clb_tu_do" for e in kq["kiem_truoc"])


def test_tuyen_chon_nhac_cho_ban_quan_ly_duyet(tmp_path):
    kq = _doc(tmp_path, [_phieu("CLB A", mo_nhom="Không", cho="10", can_thi="Có",
                                thu_thach="Trắc nghiệm", moc="5", tieu_chi="x")])
    assert any(c["ma"] == "phieu_cho_duyet_tuyen_chon" for c in kq["canh_bao"])


def test_chuyen_ghi_so_nhap_doc_lai_duoc(tmp_path):
    p = _tep(tmp_path, [_phieu("CLB Cờ vua", mo_nhom="Có", phong="30", giu="HS001"),
                        _phieu("CLB Bóng rổ", mo_nhom="Không", cho="20", ly_do="Sân")])
    ra = tmp_path / "ra"
    tom = pc.chuyen_phieu(p, str(ra))
    assert os.path.exists(tom["so_nhap"]) and os.path.exists(tom["bao_cao"])
    wb = openpyxl.load_workbook(tom["so_nhap"])
    du = so_nhap.doc_so_nhap(wb)
    assert not du.get("loi"), du.get("loi")
    loai = {c["name"]: c["loai"] for c in du["clubs"]}
    assert loai == {"CLB Cờ vua": so_nhap.TU_DO, "CLB Bóng rổ": so_nhap.GIOI_HAN}
    assert "Giữ chỗ" in wb.sheetnames
    bao_cao = open(tom["bao_cao"], encoding="utf-8").read()
    assert "TH" in bao_cao                    # nhãn chưa thử trên Microsoft thật


def test_tieu_de_thieu_cot_bao_loi_ro(tmp_path):
    p = tmp_path / "x.xlsx"
    wb = openpyxl.Workbook()
    wb.active.append(["Tên CLB", "Buổi"])
    wb.save(p)
    with pytest.raises(pc.LoiPhieu):
        pc.doc_phieu_clb(str(p))
