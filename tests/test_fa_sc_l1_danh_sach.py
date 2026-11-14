"""FA-SC L1 (TH): danh sách học sinh của trường làm đầu vào cho bộ chuyển đổi FA-DAA (đường B).

Dữ liệu MÔ PHỎNG (đợt giả của du_lieu_test/su_co/chung.py). Mọi tuỳ chọn mới mặc định TẮT: không có danh sách thì
đầu ra như cũ (bất biến 1; so sánh byte nằm ở bước soát của phiên, test này kiểm không phát sinh tệp/khoá mới).
"""
import copy
import csv
import os
import sys

import openpyxl
import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (GOC, os.path.join(GOC, "mau_forms_thi_clb"), os.path.join(GOC, "du_lieu_test", "su_co")):
    sys.path.insert(0, _p)

import chung as c  # noqa: E402
import chuyen_forms_sang_phan_mem as cv  # noqa: E402
import so_nhap  # noqa: E402

SO_HS = 24


def _lop(i):
    return "10A%d" % (i % 3 + 1)


def _ghi_danh_sach(duong, dot, them=(), co_email=True):
    cot = ["student_id", "class_id"] + (["email"] if co_email else [])
    with open(duong, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(cot)
        for i, h in enumerate(dot["hs"], 1):
            w.writerow([h["sid"], _lop(i)] + ([h["email"]] if co_email else []))
        for r in them:
            w.writerow(r if co_email else r[:2])
    return duong


def _chuyen(thu_muc, dot, **kw):
    de, loai = c.de_fa()
    so_clb, tep_dk, tep_thi = c.ghi_tep(dot, str(thu_muc), de, loai)
    return cv.chuyen_fa_daa(os.path.join(str(thu_muc), "nap"), de, so_clb, dang_ky_xlsx=tep_dk, quiz_xlsx=[tep_thi], **kw)


def _lop_trong_so(thu_muc):
    wb = openpyxl.load_workbook(os.path.join(str(thu_muc), "nap", cv.TEN_SO), data_only=True)
    ws = wb[so_nhap.SHEET_HS]
    hang = [[o.value for o in r] for r in ws.iter_rows()]
    for k, h in enumerate(hang):
        if so_nhap.nhan_lop() in h:
            i = h.index(so_nhap.nhan_lop())
            return {str(r[0]): r[i] for r in hang[k + 1:] if r[0]}
    return {}


@pytest.fixture
def dot():
    return c.sinh_dot(SO_HS, 42)


def _dong(kq, chuoi):
    return [x[2] for x in kq["canh_bao"] if chuoi in x[2]]


def _moi(kq_co, kq_khong):
    cu = [x[2] for x in kq_khong["canh_bao"]]
    return [x[2] for x in kq_co["canh_bao"] if x[2] not in cu]


def test_khong_co_danh_sach_dau_ra_nhu_cu(tmp_path, dot):
    kq = _chuyen(tmp_path / "a", dot)
    assert "bao_cao_danh_sach" not in kq
    assert not os.path.exists(os.path.join(str(tmp_path / "a"), "nap", cv.TEN_CHUA_DANG_KY))
    assert _lop_trong_so(tmp_path / "a") == {}                       # không có lớp -> không có cột lớp, như cũ


def test_du_lieu_sach_khong_co_dong_moi_va_dien_lop(tmp_path, dot):
    cu = _chuyen(tmp_path / "a", dot)
    ds = _ghi_danh_sach(tmp_path / "ds.csv", dot)
    moi = _chuyen(tmp_path / "b", dot, danh_sach_truong=ds)
    assert _moi(moi, cu) == []
    assert moi["bao_cao_danh_sach"] == {"chua_dang_ky": [], "thieu_ngay": []}
    lop = _lop_trong_so(tmp_path / "b")
    assert len(lop) == SO_HS and all(lop[h["sid"]] == _lop(i) for i, h in enumerate(dot["hs"], 1))
    assert moi["n_hoc_sinh"] == cu["n_hoc_sinh"]


def _dot_loi(dot):
    """Bốn lỗi: (a) HS003 gõ mã của HS004; (b) HS005 gõ mã lạ; (c) HS900 trong danh sách trường không đăng ký;
    (d) HS006 sót ngày thu_4."""
    loi = copy.deepcopy(dot)
    c.em(loi, "HS003")["sid"] = "HS004"
    c.em(loi, "HS005")["sid"] = "HS05O"
    h = c.em(loi, "HS006")
    del h["nv"]["thu_4"]
    h["thi"] = {k: v for k, v in h["thi"].items() if k in [x for xs in h["nv"].values() for x in xs]}
    return loi


def test_bon_loi_moi_loi_dung_mot_dong_co_email(tmp_path, dot):
    loi = _dot_loi(dot)
    cu = _chuyen(tmp_path / "a", loi)
    ds = _ghi_danh_sach(tmp_path / "ds.csv", dot, them=[["HS900", "10A9", "hs900@truong.example"]])
    moi = _chuyen(tmp_path / "b", loi, danh_sach_truong=ds)
    dong = _moi(moi, cu)
    assert len(dong) == 4, dong
    assert len(_dong(moi, "hs003@truong.example")) == 1 and "HS003" in _dong(moi, "hs003@truong.example")[0]
    assert len(_dong(moi, "HS05O")) == 1                              # mã lạ
    assert len(_dong(moi, "HS900")) == 1                              # chưa đăng ký
    assert len(_dong(moi, "HS006")) == 1                              # thiếu ngày
    # đã thay mã gõ nhầm bằng mã trong danh sách: HS003 có mã đúng, không còn mã trùng
    lop = _lop_trong_so(tmp_path / "b")
    assert "HS003" in lop and lop["HS003"] == _lop(3) and lop["HS004"] == _lop(4)
    assert moi["bao_cao_danh_sach"]["chua_dang_ky"] == [("10A9", "HS900")]
    assert [(x[0], x[2]) for x in moi["bao_cao_danh_sach"]["thieu_ngay"]] == [("HS006", ["thu_4"])]
    assert os.path.exists(os.path.join(str(tmp_path / "b"), "nap", cv.TEN_CHUA_DANG_KY))


def test_khong_co_cot_email_trung_ma_bao_hai_email_mot_dong(tmp_path, dot):
    loi = copy.deepcopy(dot)
    c.em(loi, "HS003")["sid"] = "HS004"
    cu = _chuyen(tmp_path / "a", loi)
    ds = _ghi_danh_sach(tmp_path / "ds.csv", dot, co_email=False)
    moi = _chuyen(tmp_path / "b", loi, danh_sach_truong=ds)
    dong = _dong(moi, "được dùng bởi")
    assert len(dong) == 1 and "hs003@truong.example" in dong[0] and "hs004@truong.example" in dong[0]
    # hệ quả thật: HS003 không còn mã nào đăng ký -> thêm đúng một dòng "chưa đăng ký", không dòng nào khác
    assert len(_moi(moi, cu)) == 2 and len(_dong(moi, "chưa đăng ký ngày nào")) == 1


def test_tep_chua_dang_ky_nhom_theo_lop_va_chi_co_ma_va_lop(tmp_path, dot):
    ds = _ghi_danh_sach(tmp_path / "ds.csv", dot, them=[["HS902", "10A2", ""], ["HS901", "10A1", ""],
                                                         ["HS903", "10A1", ""]])
    kq = _chuyen(tmp_path / "b", dot, danh_sach_truong=ds)
    assert kq["bao_cao_danh_sach"]["chua_dang_ky"] == [("10A1", "HS901"), ("10A1", "HS903"), ("10A2", "HS902")]
    wb = openpyxl.load_workbook(os.path.join(str(tmp_path / "b"), "nap", cv.TEN_CHUA_DANG_KY))
    assert wb.sheetnames == ["Chưa đăng ký", "Thiếu ngày"]
    hang = [[o.value for o in r] for r in wb["Chưa đăng ký"].iter_rows()]
    assert [r[0] for r in hang[1:]] == ["10A1", "10A1", "10A2"]
    toan = " ".join(str(o) for r in hang for o in r if o)
    assert "HS001" not in toan                                        # em đã đăng ký không nằm trong tệp này


def test_danh_sach_rong_hoac_thieu_cot_bi_chan_truoc_khi_ghi(tmp_path, dot):
    ds = tmp_path / "ds.csv"
    ds.write_text("student_id,class_id\n", encoding="utf-8")
    with pytest.raises(cv.LoiTepXuat):
        _chuyen(tmp_path / "a", dot, danh_sach_truong=str(ds))
    ds.write_text("ma,lop\nHS001,10A1\n", encoding="utf-8")
    with pytest.raises(cv.LoiTepXuat):
        _chuyen(tmp_path / "b", dot, danh_sach_truong=str(ds))
    assert not os.path.exists(os.path.join(str(tmp_path / "a"), "nap", cv.TEN_SO))


def test_ma_hoc_sinh_co_dau_tieng_viet_va_ma_lap_trong_danh_sach(tmp_path, dot):
    ds = _ghi_danh_sach(tmp_path / "ds.csv", dot, them=[["HS001", "10A1", "khac@truong.example"]])
    kq = _chuyen(tmp_path / "a", dot, danh_sach_truong=ds)
    assert len(_dong(kq, "xuất hiện hơn một lần")) == 1
    ds2 = tmp_path / "ds2.csv"
    ds2.write_text("student_id,class_id\nĐức01,10Â\n", encoding="utf-8-sig")
    kq2 = _chuyen(tmp_path / "b", dot, danh_sach_truong=str(ds2))
    assert kq2["bao_cao_danh_sach"]["chua_dang_ky"] == [("10Â", "Đức01")]
