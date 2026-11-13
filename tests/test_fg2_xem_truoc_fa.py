"""FG-2 (STEP0, spec §3): sổ không dành cho FA nạp vào không gian FA — cảnh báo gom nhóm ở bước xem trước, mẫu sổ cho
chế độ FA, và một sổ mẫu hợp lệ. Dữ liệu MÔ PHỎNG.

Giả định ghi rõ (người làm FG-2 có thể mở rộng, không được bỏ): mỗi nhóm cảnh báo là MỘT phần tử `canh_bao` mang
chính mã lỗi gốc (`fa_clb_thieu_loai`, `fa_huy_chuong_gia_tri_sai`) và `params["n"]` = số mục trong nhóm.
"""
import base64
import hashlib
import json
import os

import cau_hinh_ws as ch
import so_nhap
from _so_nhap_dump import chup

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAU_FA = os.path.join(GOC, "du_lieu_test", "SO_NHAP_FA_MAU_120HS.xlsx")
# sha256 của `chup()` sổ mẫu mặc định (không FA): chụp trên f5e8a41, cập nhật ở SG-2 (câu "ô trống tính là 0" của Hướng dẫn).
BAM_SO_MAU_MAC_DINH = "54d4bc37342a8a25a35089b7aae2e762a6edd4bfe1e587d0fafa681d9b837559"


def _b64(duong):
    with open(duong, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def _bat_fa(api):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True}})


def _so_khong_fa(tmp_path, n_clb=4, n_hs=5):
    """Sổ kiểu cũ: CLB không có Loại; mỗi em 2 ô "Điểm quyết tâm" kiểu điểm thường (77, 55) — không phải 60/30/10."""
    clubs = [{"club_id": "C%d" % i, "name": "CLB %d" % i, "capacity": 10, "reserve_capacity": 0,
              "reserve_group": "", "buoi": ""} for i in range(n_clb)]
    hs = [{"student_id": "h%d" % i, "name": "Em %d" % i, "reserve_group": "",
           "nv": [{"club_id": "C0", "thi": False, "diem": "", "diem_w": 77},
                  {"club_id": "C1", "thi": False, "diem": "", "diem_w": 55},
                  {"club_id": "C2", "thi": False, "diem": ""}]} for i in range(n_hs)]
    p = str(tmp_path / "khong_fa.xlsx")
    so_nhap.ghi_so_nhap(p, clubs, hs, luon_co_cot_w=True)
    return p


def _canh_bao(ra, ma):
    return [w for w in ra["data"]["canh_bao"] if w["code"] == ma]


def test_xem_truoc_gom_canh_bao_fa_theo_ma_co_so_dem(api, tmp_path):
    _bat_fa(api)
    ra = api.xem_truoc_so_nhap(_b64(_so_khong_fa(tmp_path)))
    assert ra["ok"], ra
    a = _canh_bao(ra, "fa_clb_thieu_loai")
    assert len(a) == 1 and a[0]["params"]["n"] == 4                    # 4 CLB chưa có Loại -> MỘT dòng
    b = _canh_bao(ra, "fa_huy_chuong_gia_tri_sai")
    assert len(b) == 1 and b[0]["params"]["n"] == 10                   # 5 em x 2 ô sai -> MỘT dòng
    assert ra["data"]["loi"] == []                                     # vẫn được nhập (sửa CLB ở Quản lý)


def test_xem_truoc_khong_fa_khong_co_canh_bao_fa(api, tmp_path):
    ra = api.xem_truoc_so_nhap(_b64(_so_khong_fa(tmp_path)))
    assert ra["ok"], ra
    assert [w["code"] for w in ra["data"]["canh_bao"] if w["code"].startswith("fa_")] == []


def test_so_mau_mac_dinh_giu_nguyen(api, tmp_path):
    ra = api.tao_so_nhap_mau(str(tmp_path / "m.xlsx"))
    assert ra["ok"], ra
    chuoi = json.dumps(chup(ra["data"]["path"]), sort_keys=True, default=str)
    assert hashlib.sha256(chuoi.encode()).hexdigest() == BAM_SO_MAU_MAC_DINH


def test_so_mau_che_do_fa_co_cot_loai_va_nhan_huy_chuong(api, tmp_path):
    _bat_fa(api)
    ra = api.tao_so_nhap_mau(str(tmp_path / "fa.xlsx"))
    assert ra["ok"], ra
    c = chup(ra["data"]["path"])
    clb, hs = c["sheets"][0], c["sheets"][1]
    tieu_clb = [v for k, v in c["trang"][clb]["o"].items() if k.endswith("1") and k[:-1].isalpha()]
    assert "Loại" in tieu_clb
    chu_hs = " | ".join(str(v) for v in c["trang"][hs]["o"].values())
    assert "Huy chương (60/30/10)" in chu_hs
    assert "Điểm quyết tâm" not in chu_hs


def test_bo_doc_nhan_huy_chuong_nhu_cot_diem_quyet_tam(api, tmp_path):
    """Sổ có cột "Huy chương (60/30/10)" (mẫu FA) nạp ra y như cột "Điểm quyết tâm": cùng `wharton_bids`."""
    import openpyxl

    from _wharton import dong_bids
    _bat_fa(api)
    p = _so_khong_fa(tmp_path, n_clb=3, n_hs=2)
    wb = openpyxl.load_workbook(p)
    ws = wb[wb.sheetnames[1]]
    doi = 0
    for hang in ws.iter_rows(min_row=1, max_row=2):
        for o in hang:
            if o.value == so_nhap.TEN_COT_QUYET_TAM:
                o.value, doi = "Huy chương (60/30/10)", doi + 1
    assert doi > 0
    for hang in ws.iter_rows(min_row=3):
        for o in hang:
            if o.value == 77:
                o.value = 60
            elif o.value == 55:
                o.value = 30
    wb.save(p)
    ra = api.import_so_nhap(_b64(p))
    assert ra["ok"], ra
    assert sorted(x[3] for x in dong_bids(api)) == [30, 30, 60, 60]


def test_so_mau_fa_120hs_hop_le_xem_truoc_sach_va_chay_duoc(api):
    assert os.path.exists(MAU_FA), "thiếu du_lieu_test/SO_NHAP_FA_MAU_120HS.xlsx"
    _bat_fa(api)
    ra = api.xem_truoc_so_nhap(_b64(MAU_FA))
    assert ra["ok"], ra
    assert ra["data"]["loi"] == [] and ra["data"]["n_hoc_sinh"] == 120
    assert [w for w in ra["data"]["canh_bao"] if w["code"].startswith("fa_")] == []
    assert api.import_so_nhap(_b64(MAU_FA))["ok"]
    assert api.run_pipeline(seed=3)["ok"]


def test_canh_bao_gom_nhom_co_cau_chu_va_dong_chan_chay(api, tmp_path):
    """Mỗi nhóm đọc được bằng cả hai ngôn ngữ (có số đếm), và có MỘT dòng nói lần chạy sẽ bị chặn."""
    from i18n_errors import format_message
    _bat_fa(api)
    ra = api.xem_truoc_so_nhap(_b64(_so_khong_fa(tmp_path)))
    canh_bao = ra["data"]["canh_bao"]
    b = _canh_bao(ra, "fa_huy_chuong_gia_tri_sai")[0]
    assert b["params"]["nhom"] is True
    assert "10 ô huy chương không phải 60/30/10" in format_message(b["code"], b["params"], "vi")
    assert "10 medal" in format_message(b["code"], b["params"], "en")
    a = _canh_bao(ra, "fa_clb_thieu_loai")[0]
    assert format_message(a["code"], a["params"], "vi").startswith("4 CLB chưa có Loại")
    assert len(_canh_bao(ra, "so_nhap_canh_bao_fa_se_loi")) == 1
    assert canh_bao[-1]["code"] == "so_nhap_canh_bao_fa_se_loi"


def test_xem_truoc_khong_ghi_gi_va_van_nhap_duoc(api, tmp_path):
    p = _so_khong_fa(tmp_path)
    _bat_fa(api)
    api.xem_truoc_so_nhap(_b64(p))
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM clubs").fetchone()[0] == 0
    assert api.import_so_nhap(_b64(p))["ok"]            # cảnh báo không chặn nhập


def test_so_mau_fa_ghi_ro_mo_phong_va_tat_dinh():
    import openpyxl

    from du_lieu_test import tao_so_nhap_fa_mau as t
    wb = openpyxl.load_workbook(MAU_FA)
    chu = " ".join(str(r[0]) for r in wb[so_nhap.SHEET_HD].iter_rows(values_only=True) if r[0])
    assert "MÔ PHỎNG" in chu
    c1, s1 = t.dung_so(7)
    c2, s2 = t.dung_so(7)
    assert (c1, s1) == (c2, s2)
    assert t.dung_so(8)[1] != s1


def test_so_mau_fa_huong_dan_noi_ve_huy_chuong_khong_ve_quy(api, tmp_path):
    _bat_fa(api)
    ra = api.tao_so_nhap_mau(str(tmp_path / "fa.xlsx"))
    c = chup(ra["data"]["path"])
    hd = " ".join(str(v) for v in c["trang"][c["sheets"][-1]]["o"].values())
    assert "Huy chương (60/30/10)" in hd and "quỹ" not in hd and "Điểm quyết tâm" not in hd
