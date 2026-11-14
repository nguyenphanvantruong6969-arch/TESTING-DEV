# -*- coding: utf-8 -*-
"""SG-8 (M5, bất biến 6): các câu của bước 1 "Chuẩn bị đợt" đi qua i18n — API trả `{code, params}` + mã loại CLB,
giao diện tự dịch (vi VÀ en). Chữ ghi ra tệp cho giáo viên (Sổ nhập cột "Loại", báo cáo Phiếu .md) giữ nguyên
từng byte. Dữ liệu MÔ PHỎNG."""
import base64
import os
import re

import openpyxl
import pytest

import forms_dot
import so_nhap
from i18n_errors import MESSAGES, format_message

forms_dot.nap_mau_forms()
import chuyen_phieu_clb as pc  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def dong_phieu(ten, buoi="Thứ 2", mo="", cho="", ly_do="", phong="", can_thi="Không", thu_thach="", moc="",
               tieu_chi=""):
    d = dict(zip(pc.TIEU_DE_PHIEU, [ten, buoi, "", "", mo, cho, ly_do, phong, "8", can_thi, thu_thach, moc,
                                    tieu_chi, ""]))
    return [d[h] for h in pc.TIEU_DE_PHIEU]


# Đủ ba Loại + nhiều mã trong NOI_DUNG: thiếu câu 2 (lỗi), Tự do có lý do giới hạn, Giới hạn thiếu lý do,
# Tuyển chọn thiếu tiêu chí + thử thách không trắc nghiệm + chờ duyệt, nộp nhiều lần.
DONG = [
    dong_phieu("CLB Tự do", mo="Có", phong="30", ly_do="Phòng nhỏ"),
    dong_phieu("CLB Giới hạn", buoi="Thứ 3", mo="Không", cho="20"),
    dong_phieu("CLB Tuyển chọn", mo="Không", cho="10", ly_do="Dụng cụ", can_thi="Có", thu_thach="Bài tập", moc="5"),
    dong_phieu("CLB Hỏng", mo=""),
    dong_phieu("CLB Giới hạn", buoi="Thứ 3", mo="Không", cho="20"),
]


def b64_phieu(tmp_path, dong, ten="phieu.xlsx"):
    p = tmp_path / ten
    wb = openpyxl.Workbook()
    wb.active.append(pc.TIEU_DE_PHIEU)
    for r in dong:
        wb.active.append(r)
    wb.save(p)
    return base64.b64encode(p.read_bytes()).decode(), p


@pytest.fixture
def kq(api, tmp_path):
    b64, _ = b64_phieu(tmp_path, DONG)
    r = api.nap_phieu_clb(b64)
    assert r["ok"], r
    return r["data"]


def _dong_bao(d):
    return d["loi"] + d["canh_bao"]


def test_loi_va_canh_bao_la_ma_va_tham_so_khong_con_cau_viet_san(kq):
    ds = _dong_bao(kq)
    assert {x["ma"] for x in ds} >= {"phieu_thieu_cau_2", "phieu_tu_do_co_ly_do_gioi_han", "phieu_thieu_ly_do",
                                      "phieu_thu_thach_khong_tu_cham", "phieu_thieu_tieu_chi",
                                      "phieu_cho_duyet_tuyen_chon", "phieu_nop_nhieu_lan"}
    for x in ds:
        assert "noi_dung" not in x, x
        assert x["code"] in MESSAGES and x["params"]["clb"] == x["clb"], x
        assert MESSAGES[x["code"]].get("vi") and MESSAGES[x["code"]].get("en"), x


def test_moi_ma_noi_dung_co_mot_ma_i18n_vi_giong_chu_cu_va_en_khac_vi():
    """Một nguồn chữ duy nhất: câu vi trong i18n_errors = câu cũ của NOI_DUNG (đứng sau "<CLB>: ")."""
    for ma, cu in pc.NOI_DUNG.items():
        code = "phieu_nd_" + ma
        assert code in MESSAGES, code
        assert format_message(code, {"clb": "X"}, "vi") == "X: " + cu
        en = format_message(code, {"clb": "X"}, "en")
        assert en.startswith("X: ") and en != format_message(code, {"clb": "X"}, "vi")
        assert not re.search(r"[À-ỹ]", en), en            # tiếng Anh không lẫn dấu tiếng Việt


def test_theo_loai_va_bang_clb_tra_ma_loai_khong_tra_nhan_viet(kq):
    assert set(kq["theo_loai"]) == {so_nhap.TU_DO, so_nhap.GIOI_HAN, so_nhap.TUYEN_CHON}
    assert sum(kq["theo_loai"].values()) == 3
    for c in kq["clubs"]:
        assert "loai_nhan" not in c and c["loai"] in so_nhap.NHAN_LOAI_HIEN_THI, c


def test_kiem_truoc_tra_ma_khong_tra_chuoi_da_dich(api, tmp_path):
    """Chỉ một CLB Giới hạn: không buổi nào có CLB Tự do -> lỗi chặn của FA; phải là {code, params}."""
    b64, _ = b64_phieu(tmp_path, [dong_phieu("CLB Giới hạn", mo="Không", cho="20", ly_do="Sân")])
    d = api.nap_phieu_clb(b64)["data"]
    assert d["chan"], d
    for x in d["chan"]:
        assert isinstance(x, dict) and x["code"] in MESSAGES, x


def test_doc_lai_trang_thai_cung_dang_ma(api, kq):
    d = api.get_forms_buoc_12()["data"]["clb"]
    assert d["theo_loai"] == kq["theo_loai"]
    assert all("code" in x and "noi_dung" not in x for x in d["loi"] + d["canh_bao"])
    assert all("loai_nhan" not in c for c in d["clubs"])


def test_khong_clb_hop_le_bao_bang_ma_khong_chen_chu_viet(api, tmp_path):
    b64, _ = b64_phieu(tmp_path, [dong_phieu("CLB Hỏng", mo="")])
    r = api.nap_phieu_clb(b64)
    assert not r["ok"]
    assert r["errors"][0]["code"] == "phieu_clb_tep_sai"
    assert all(set(e) <= {"code", "params"} for e in r["errors"])
    chu = repr(r["errors"])
    assert "chưa trả lời câu 2" not in chu and "không có CLB hợp lệ nào" not in chu
    assert any(e["code"] == "phieu_nd_phieu_thieu_cau_2" for e in r["errors"]), r["errors"]


def test_nhan_loai_trong_giao_dien_vi_giong_chu_ghi_vao_so_nhap():
    """Giao diện vi đọc nhãn Loại từ i18n.js; chữ ghi vào Sổ nhập (người đọc lại) vẫn là NHAN_LOAI_HIEN_THI."""
    with open(os.path.join(GOC, "i18n.js"), encoding="utf-8") as f:
        js = f.read()
    for ma, nhan in so_nhap.NHAN_LOAI_HIEN_THI.items():
        khoa = "fa_loai_" + ma
        vi = re.findall(r'%s: "([^"]*)"' % khoa, js)
        assert len(vi) == 2 and vi[0] == nhan, (khoa, vi)           # [vi, en]
        assert re.fullmatch(r"[A-Za-z ]+", vi[1]), vi


BAO_CAO_GOC = """# Báo cáo Phiếu thiết lập CLB (TH = chưa thử trên Microsoft thật)

CLB hợp lệ: 3 (Giới hạn 1, Tuyển chọn 1, Tự do 1). Giữ chỗ: 0.

## Lỗi (CLB bị bỏ qua)
- CLB Hỏng: chưa trả lời câu 2 (mở thêm nhóm được không): không phân loại được, đã bỏ qua

## Cảnh báo
- CLB Giới hạn: nộp phiếu nhiều lần: lấy phiếu cuối cùng
- CLB Tự do: khai Tự do nhưng có ghi lý do giới hạn; CLB bị giới hạn thật không được khai Tự do, cần admin xem lại
- CLB Giới hạn: CLB giới hạn chưa ghi lý do (phòng/dụng cụ/người hướng dẫn)
- CLB Tuyển chọn: loại thử thách không phải trắc nghiệm: phần mềm không chấm tự động, admin nhập điểm
- CLB Tuyển chọn: CLB Tuyển chọn chưa ghi bảng tiêu chí
- CLB Tuyển chọn: CLB Tuyển chọn: chờ ban quản lý duyệt trước khi mở cổng

## Kiểm trước khi mở cổng
- Buổi "thu_3" chưa có CLB loại Tự do. Mỗi buổi cần ít nhất một CLB Tự do để nhận học sinh chưa có chỗ.
"""


def test_tep_ghi_cho_giao_vien_giu_nguyen_chu_viet(tmp_path):
    """Báo cáo .md của chuyen_phieu (chụp từ mã TRƯỚC SG-8) và cột "Loại" của Sổ nhập vẫn y nguyên tiếng Việt."""
    _, p = b64_phieu(tmp_path, DONG)
    tom = pc.chuyen_phieu(str(p), str(tmp_path / "ra"))
    assert open(tom["bao_cao"], encoding="utf-8").read() == BAO_CAO_GOC
    ws = openpyxl.load_workbook(tom["so_nhap"]).worksheets[0]
    cot = [c.value for c in ws[1]]
    nhan = {r[cot.index("Loại")].value for r in ws.iter_rows(min_row=2)} - {None}
    assert nhan <= set(so_nhap.NHAN_LOAI_HIEN_THI.values()) and nhan, (cot, nhan)


# ---- FIX-1: tệp kết quả lưu TRƯỚC SG-8 (`{ma, clb, noi_dung}`, nhãn Việt, chuỗi trong `chan`) vẫn đọc được ----
CU_LOI = [{"ma": "phieu_thieu_cau_2", "clb": "Cu A", "noi_dung": "chưa trả lời câu 2: đã bỏ qua"},
          {"ma": "ma_la_khong_biet", "clb": "Cu B", "noi_dung": "câu lạ đã lưu"}]


def ghi_ket_qua_cu(api, tmp_path):
    import json
    from api_forms import TEN_TEP_KET_QUA_PHIEU
    b64, _ = b64_phieu(tmp_path, DONG)
    assert api.nap_phieu_clb(b64)["ok"]
    duong = os.path.join(forms_dot.thu_muc_forms(api.db_path), TEN_TEP_KET_QUA_PHIEU)
    with open(duong, "w", encoding="utf-8") as f:
        json.dump({"n_clb": 3, "theo_loai": {"Tự do": 1}, "loi": CU_LOI, "canh_bao": [],
                   "chan": ["Buổi \"thu_3\" chưa có CLB loại Tự do."]}, f, ensure_ascii=False)


def test_tep_ket_qua_cu_duoc_doi_sang_ma_khi_mo_lai(api, tmp_path):
    ghi_ket_qua_cu(api, tmp_path)
    d = api.get_forms_buoc_12()["data"]["clb"]
    a, b = d["loi"]
    assert a["code"] == "phieu_nd_phieu_thieu_cau_2" and a["params"] == {"clb": "Cu A"}
    assert format_message(a["code"], a["params"], "vi") == "Cu A: " + pc.NOI_DUNG["phieu_thieu_cau_2"]
    assert "code" not in b and b["noi_dung"] == "câu lạ đã lưu"          # mã lạ: giữ chữ đã lưu
    assert d["theo_loai"] == {"Tự do": 1} and d["chan"] == ["Buổi \"thu_3\" chưa có CLB loại Tự do."]
