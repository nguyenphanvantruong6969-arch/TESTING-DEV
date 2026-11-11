"""FA-M6 (TH = chưa thử trên Microsoft thật): tài liệu `docs/he_sinh_thai/FA_SAU_XEP.md` (chỉ tài liệu, không mã).

Kiểm những thứ máy kiểm được: cột `ket_qua_ly_do.csv` trong tài liệu khớp mã xuất của kiosk, các list/biểu mẫu/flow đủ tên,
phép tính hạn mức 6.000, nhãn TH, không dữ liệu thật, không nói đường nào nên chọn (D8 còn mở). Dữ liệu MÔ PHỎNG.
"""
import os
import re

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = os.path.join(GOC, "docs", "he_sinh_thai", "FA_SAU_XEP.md")


def _doc():
    return open(TL, encoding="utf-8").read()


def _cot_csv_that():
    """Hàng tiêu đề thật của ket_qua_ly_do.csv, đọc từ mã xuất."""
    src = open(os.path.join(GOC, "api_xuat.py"), encoding="utf-8").read()
    i = src.index("def _export_ly_do_da_khoa")
    m = re.search(r"w\.writerow\(\[([^\]]+)\]\)", src[i:])
    return re.findall(r'"([a-z_]+)"', m.group(1))


def test_cot_csv_trong_tai_lieu_khop_ma_xuat():
    cot = _cot_csv_that()
    assert cot[:3] == ["student_id", "buoi", "club"] and len(cot) == 8
    d = _doc()
    for c in cot:
        assert "`%s`" % c in d, c


def test_du_ten_list_form_flow_va_man_hinh():
    d = _doc()
    for ten in ("KetQua", "PhanHoi", "DiemDanh", "CanNhac", "ket_qua_ly_do.csv", "T4M_FLOW_GUI_GVCN.md",
                "Khiếu nại", "Khảo sát tuần 3", "3 ngày", "DRAFT", "SUBMITTED"):
        assert ten in d, ten
    for nhac in ("-2 ngày", "-3 giờ", "dưới 50 %", "NOT_ATTEMPTED"):
        assert nhac in d, nhac


def test_ba_nut_phan_hoi_dung_y_vision():
    d = _doc()
    for cau in ("Em có hiểu vì sao được xếp như vậy?", "Phần nào khó nhất?", "chọn CLB", "xếp thứ tự", "huy chương", "thử thách"):
        assert cau in d, cau


def test_phep_tinh_han_muc_6000():
    d = _doc()
    assert "6.000" in d and "NC-13" in d
    assert "3.000" in d                                                    # 3 lần nhắc x 1.000 em, mỗi em một thao tác
    assert re.search(r"3 × 1\.000", d)
    assert "Bcc" in d                                                      # cách giảm: thư nhóm, không mỗi em một thư


def test_nhan_th_va_khong_chon_duong_d8():
    d = _doc()
    assert d.startswith("# ")
    assert "TH" in d[:800] and "chưa thử" in d[:800]
    assert "D8" in d
    assert "khuyến nghị" not in d.lower() and "nên chọn" not in d.lower()


def test_khong_du_lieu_that_va_khong_ten_gia_cho_nguoi_that():
    d = _doc()
    assert "@" not in d.replace("@odata", "")
    assert "https://" not in d and not re.search(r"tenantId\s*[:=]\s*\S", d)


def test_fa_ui_5_huong_dan_su_dung_co_muc_xep_theo_loai_clb():
    """FA-UI-5: HUONG_DAN_SU_DUNG.md có MỘT mục FA: bật, Sổ nhập có Loại, huy chương, đọc lý do, bảng nhu cầu."""
    van = open(os.path.join(GOC, "HUONG_DAN_SU_DUNG.md"), encoding="utf-8").read()
    tieu_de = "## 15. Xếp theo loại CLB và huy chương (tuỳ chọn)"
    assert van.count(tieu_de) == 1
    assert "[Xếp theo loại CLB và huy chương (tuỳ chọn)](#15-" in van              # có trong mục lục
    muc = van[van.index(tieu_de):]
    for tu in ("Xếp theo loại CLB và huy chương", "Dùng điểm quyết tâm", "Loại", "Điểm sàn", "Tối thiểu",
               "Sức chứa phòng", "Giữ chỗ", "Tự do", "Giới hạn", "Tuyển chọn", "Vàng (60)", "Bạc (30)", "Đồng (10)",
               "Lý do", "Xuất lý do kết quả (CSV)", "ket_qua_ly_do.csv", "Xuất bảng nhu cầu (CSV)", "bang_nhu_cau.csv"):
        assert tu in muc, tu
    assert "FA-DAA" not in muc and "Wharton" not in muc
