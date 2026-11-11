"""FA-M7 (TH = CHƯA thử trên Microsoft / Google thật): CLB nhập MỘT lần, đề thi trong MỘT Excel.

  * thuần: `so_de_thi.ghi_mau_kiosk` -> `doc_so_de_thi` khứ hồi; dict đọc ra == `de_thi.json` mặc định;
    biến thể (cột `de`) -> `de_thi_bien_the`; mọi loại lỗi báo MỘT LẦN; CLB chỉ có trong `De_thi` -> lỗi nêu tên;
  * API: `nap_phieu_clb`, `tai_mau_de_thi`, `nap_de_thi`; không ghi gì vào app.db; lỗi thì không ghi `de_thi.json`.
Dữ liệu MÔ PHỎNG.
"""
import base64
import copy
import json
import os
import sqlite3

import openpyxl
import pytest

import forms_dot

forms_dot.nap_mau_forms()
import bieu_mau  # noqa: E402
import chuyen_phieu_clb as pc  # noqa: E402
import phan_tich_cau_hoi  # noqa: E402
import so_de_thi  # noqa: E402

TIEU_DE = pc.TIEU_DE_PHIEU
DE_MAC_DINH = bieu_mau.doc_de_thi()
TRUONG = ("club_id", "name", "buoi", "capacity", "reserve_capacity", "reserve_group", "de_thi", "de_thi_bien_the")


def _clb(club_id, ten, buoi="thu_2", cho=12):
    return {"club_id": club_id, "name": ten, "buoi": buoi, "capacity": cho, "reserve_capacity": 0, "reserve_group": ""}


def _cau(i, dap_an="a"):
    return {"cau": "Câu %d?" % i, "lua_chon": ["đáp A", "đáp B", "đáp C", "đáp D"],
            "dap_an": "abcd".index(dap_an)}


def _mau(tmp_path, clubs, de=None, ten="de.xlsx"):
    p = str(tmp_path / ten)
    so_de_thi.ghi_mau_kiosk(p, clubs, de=de)
    return p


def _them_dong(p, dong, sheet="De_thi"):
    wb = openpyxl.load_workbook(p)
    for r in dong:
        wb[sheet].append(r)
    wb.save(p)


def _dong(club, cau="Câu?", a="a1", b="b1", c="c1", d="d1", dap="a", de=None):
    return [club, de, cau, a, b, c, d, dap]


# ---------------------------------------------------------------- thuần
def test_mau_khu_hoi_ghi_roi_doc_bang_de_mac_dinh(tmp_path):
    clubs = [{k: c[k] for k in TRUONG[:6]} for c in DE_MAC_DINH["cau_lac_bo"]]
    p = _mau(tmp_path, clubs, de=DE_MAC_DINH)
    de, loi = so_de_thi.doc_so_de_thi(p, clubs)
    assert loi == []
    assert de["tieu_de"] == DE_MAC_DINH["tieu_de"] and de["diem_moi_cau"] == DE_MAC_DINH["diem_moi_cau"]
    assert [b["ma"] for b in de["buoi"]] == [b["ma"] for b in DE_MAC_DINH["buoi"]]
    for moi, goc in zip(de["cau_lac_bo"], DE_MAC_DINH["cau_lac_bo"]):
        for k in TRUONG:
            assert moi.get(k, []) == goc.get(k, []), (goc["club_id"], k)
    bieu_mau.soat_de_thi(de)                       # cùng hình dạng, bộ sinh dùng được


def test_mau_chi_co_clb_va_de_thi_rong(tmp_path):
    clubs = [_clb("clb_a", "CLB A"), _clb("clb_b", "CLB B", "thu_3")]
    p = _mau(tmp_path, clubs)
    wb = openpyxl.load_workbook(p)
    assert {"Cai_dat", "CLB", "De_thi"} <= set(wb.sheetnames)
    assert [c.value for c in wb["De_thi"][1]] == [
        "club_id", "de", "cau_hoi", "lua_chon_a", "lua_chon_b", "lua_chon_c", "lua_chon_d", "dap_an"]
    assert wb["De_thi"].max_row == 1
    ds = [tuple(c.value for c in r) for r in wb["CLB"].iter_rows(min_row=2)]
    assert [(r[2], r[3], r[0]) for r in ds] == [("clb_a", "CLB A", "thu_2"), ("clb_b", "CLB B", "thu_3")]
    de, loi = so_de_thi.doc_so_de_thi(p, clubs)          # CLB không câu hỏi = không thi: cho phép
    assert loi == [] and all(c["de_thi"] == [] for c in de["cau_lac_bo"])


def test_cot_de_thanh_de_thi_bien_the(tmp_path):
    clubs = [_clb("clb_a", "CLB A")]
    p = _mau(tmp_path, clubs)
    _them_dong(p, [_dong("clb_a", "A1", dap="a"), _dong("clb_a", "A2", dap="b", de="A"),
                   _dong("clb_a", "B1", dap="c", de="B"), _dong("clb_a", "B2", dap="d", de="b"),
                   _dong("clb_a", "C1", dap="a", de="C"), _dong("clb_a", "C2", dap="a", de="C")])
    de, loi = so_de_thi.doc_so_de_thi(p, clubs)
    assert loi == []
    c = de["cau_lac_bo"][0]
    assert [q["cau"] for q in c["de_thi"]] == ["A1", "A2"]
    assert [[q["cau"] for q in d] for d in c["de_thi_bien_the"]] == [["B1", "B2"], ["C1", "C2"]]
    assert c["de_thi_bien_the"][0][1]["dap_an"] == 3
    assert phan_tich_cau_hoi.kiem_bien_the(c) == []


def test_moi_loai_loi_bao_mot_lan(tmp_path):
    clubs = [_clb("clb_a", "CLB A"), _clb("clb_b", "CLB B")]
    p = _mau(tmp_path, clubs)
    _them_dong(p, [
        _dong("clb_a", "ok"),
        _dong("clb_a", "dap an sai", dap="e"),
        _dong("clb_a", "thieu lua chon", b=""),
        _dong("clb_a", "", dap="a"),
        _dong("clb_a", "de la", dap="a", de="Z"),
        _dong("clb_b", "A1"), _dong("clb_b", "A2"), _dong("clb_b", "B1", de="B"),    # đề B thiếu câu
        _dong("clb_la", "clb ngoai"),
    ])
    de, loi = so_de_thi.doc_so_de_thi(p, clubs)
    nhat = "\n".join(loi)
    assert de is None
    for mau in ("clb_la", "dap_an", "lua_chon_b", "cau_hoi", "'Z'", "số câu phải bằng nhau"):
        assert mau in nhat, (mau, nhat)
    assert len(loi) >= 6


def test_clb_chi_o_de_thi_khong_o_buoc_1_bao_loi_neu_ten(tmp_path):
    """Đột biến: bỏ phép đối chiếu CLB với bước 1 -> test này đỏ."""
    clubs = [_clb("clb_a", "CLB A")]
    p = _mau(tmp_path, clubs)
    _them_dong(p, [_dong("clb_a", "ok"), _dong("clb_chi_o_de", "x")])
    de, loi = so_de_thi.doc_so_de_thi(p, clubs)
    assert de is None
    assert any("clb_chi_o_de" in x and "bước 1" in x for x in loi), loi


def test_thieu_trang_hoac_cot_la_loi_chung(tmp_path):
    p = str(tmp_path / "x.xlsx")
    wb = openpyxl.Workbook()
    wb.active.title = "De_thi"
    wb.active.append(["club_id", "cau_hoi"])
    wb.save(p)
    de, loi = so_de_thi.doc_so_de_thi(p, [_clb("clb_a", "CLB A")])
    assert de is None and any("lua_chon_a" in x for x in loi)


def test_doc_clb_so_nhap_dot_khong_co_tep_nem_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        so_de_thi.doc_clb_dot(str(tmp_path / "khong_co.xlsx"))


# ---------------------------------------------------------------- API
def _phieu(ten, buoi="Thứ 2", mo_nhom="", cho="", ly_do="", phong="", toi_thieu="8",
           can_thi="Không", thu_thach="", moc="", tieu_chi="", giu=""):
    d = dict(zip(TIEU_DE, [ten, buoi, "15:30", "Phòng A", mo_nhom, cho, ly_do, phong, toi_thieu,
                           can_thi, thu_thach, moc, tieu_chi, giu]))
    return [d[h] for h in TIEU_DE]


def _b64_phieu(tmp_path, dong, ten="phieu.xlsx"):
    p = tmp_path / ten
    wb = openpyxl.Workbook()
    wb.active.append(TIEU_DE)
    for r in dong:
        wb.active.append(r)
    wb.save(p)
    return base64.b64encode(p.read_bytes()).decode()


def _b64(p):
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode()


DONG_PHIEU = [_phieu("CLB Cờ vua", mo_nhom="Có", phong="30"),
              _phieu("CLB Bóng rổ", buoi="Thứ 3", mo_nhom="Không", cho="20", ly_do="Sân nhỏ")]


@pytest.fixture
def api_b1(api, tmp_path):
    """API đã làm xong bước 1 (hai CLB)."""
    api.thu_muc_xuat = str(tmp_path / "tai_ve")
    os.makedirs(api.thu_muc_xuat)
    kq = api.nap_phieu_clb(_b64_phieu(tmp_path, DONG_PHIEU))
    assert kq["ok"], kq
    return api


def _so_dong_clb(api):
    with sqlite3.connect(api.db_path) as c:
        return c.execute("select count(*) from clubs").fetchone()[0]


def test_nap_phieu_clb_ghi_tep_dot_va_khong_dong_toi_app_db(api, tmp_path):
    kq = api.nap_phieu_clb(_b64_phieu(tmp_path, DONG_PHIEU))
    assert kq["ok"], kq
    d = kq["data"]
    assert d["n_clb"] == 2 and d["loi"] == [] and sum(d["theo_loai"].values()) == 2
    assert os.path.isfile(forms_dot.duong_so_nhap_clb_dot(api.db_path))
    assert _so_dong_clb(api) == 0
    assert {c["name"] for c in d["clubs"]} == {"CLB Cờ vua", "CLB Bóng rổ"}
    assert {c["chi_tieu"] for c in d["clubs"]} == {30, 20}


def test_nap_phieu_clb_loi_trong_bao_cao_van_ok_nhung_co_loi(api, tmp_path):
    kq = api.nap_phieu_clb(_b64_phieu(tmp_path, DONG_PHIEU + [_phieu("CLB Hỏng", mo_nhom="")]))
    assert kq["ok"] and kq["data"]["n_clb"] == 2
    assert kq["data"]["loi"] and "CLB Hỏng" in kq["data"]["loi"][0]["clb"]


def test_nap_phieu_clb_tep_sai_khong_ghi_gi(api, tmp_path):
    p = tmp_path / "x.xlsx"
    wb = openpyxl.Workbook()
    wb.active.append(["cot", "la"])
    wb.save(p)
    kq = api.nap_phieu_clb(_b64(p))
    assert not kq["ok"] and kq["errors"][0]["code"] == "phieu_clb_tep_sai"
    assert not os.path.exists(forms_dot.duong_so_nhap_clb_dot(api.db_path))
    kq = api.nap_phieu_clb("khong phai xlsx")
    assert not kq["ok"]
    assert not os.path.exists(forms_dot.duong_so_nhap_clb_dot(api.db_path))


def test_nap_lai_phieu_thay_clb_va_khong_de_tep_cu_neu_loi(api_b1, tmp_path):
    truoc = open(forms_dot.duong_so_nhap_clb_dot(api_b1.db_path), "rb").read()
    p = tmp_path / "x.xlsx"
    wb = openpyxl.Workbook()
    wb.active.append(["cot"])
    wb.save(p)
    assert not api_b1.nap_phieu_clb(_b64(p))["ok"]
    assert open(forms_dot.duong_so_nhap_clb_dot(api_b1.db_path), "rb").read() == truoc


def test_tai_mau_de_thi_can_buoc_1(api, tmp_path):
    api.thu_muc_xuat = str(tmp_path)
    kq = api.tai_mau_de_thi()
    assert not kq["ok"] and kq["errors"][0]["code"] == "forms_chua_co_clb"


def test_tai_mau_de_thi_dien_san_clb_buoc_1(api_b1):
    kq = api_b1.tai_mau_de_thi()
    assert kq["ok"], kq
    assert os.path.basename(kq["data"]["path"]) == "MAU_DE_THI_KIOSK.xlsx"
    assert os.path.dirname(kq["data"]["path"]) == api_b1.thu_muc_xuat and kq["data"]["n_clb"] == 2
    wb = openpyxl.load_workbook(kq["data"]["path"])
    ten = {r[3].value for r in wb["CLB"].iter_rows(min_row=2)}
    assert ten == {"CLB Cờ vua", "CLB Bóng rổ"}
    assert wb["De_thi"].max_row == 1


def _dien_de(api, tmp_path, dong, ten="de_dien.xlsx"):
    kq = api.tai_mau_de_thi()
    p = str(tmp_path / ten)
    os.replace(kq["data"]["path"], p)
    _them_dong(p, dong)
    return p


def _ma(api, ten):
    return next(c["club_id"] for c in api.get_forms_buoc_12()["data"]["clb"]["clubs"] if c["name"] == ten)


def test_nap_de_thi_can_buoc_1(api, tmp_path):
    p = _mau(tmp_path, [_clb("clb_a", "CLB A")])
    kq = api.nap_de_thi(_b64(p))
    assert not kq["ok"] and kq["errors"][0]["code"] == "forms_chua_co_clb"


def test_nap_de_thi_loi_thi_khong_ghi_de_thi_json(api_b1, tmp_path):
    cv = _ma(api_b1, "CLB Cờ vua")
    p = _dien_de(api_b1, tmp_path, [_dong(cv, "ok"), _dong(cv, "x", dap="z"), _dong("clb_la", "y")])
    kq = api_b1.nap_de_thi(_b64(p))
    assert not kq["ok"]
    assert {e["code"] for e in kq["errors"]} == {"de_thi_tep_sai"}
    assert len(kq["errors"]) >= 2
    assert not os.path.exists(forms_dot.duong_de_dot(api_b1.db_path))


def test_nap_de_thi_ghi_de_thi_json_cho_bo_sinh(api_b1, tmp_path):
    cv, br = _ma(api_b1, "CLB Cờ vua"), _ma(api_b1, "CLB Bóng rổ")
    p = _dien_de(api_b1, tmp_path, [_dong(cv, "Q1", dap="b"), _dong(cv, "Q2", dap="c"), _dong(cv, "Q3 B", de="B")])
    kq = api_b1.nap_de_thi(_b64(p))
    assert not kq["ok"]                                  # đề B 1 câu, đề A 2 câu
    p = _dien_de(api_b1, tmp_path, [_dong(cv, "Q1", dap="b"), _dong(cv, "Q2", dap="c"),
                                    _dong(cv, "B1", de="B"), _dong(cv, "B2", de="B")], ten="de2.xlsx")
    kq = api_b1.nap_de_thi(_b64(p))
    assert kq["ok"], kq
    assert kq["data"]["n_clb"] == 2 and kq["data"]["n_clb_thi"] == 1 and kq["data"]["n_cau"] == 4
    de = forms_dot.doc_de_dot(api_b1.db_path)             # cùng tệp CLI đọc được
    theo = {c["club_id"]: c for c in de["cau_lac_bo"]}
    assert len(theo[cv]["de_thi"]) == 2 and len(theo[cv]["de_thi_bien_the"]) == 1
    assert theo[br]["de_thi"] == [] and theo[br]["capacity"] == 20 and theo[cv]["capacity"] == 30
    assert _so_dong_clb(api_b1) == 0


def test_trang_thai_buoc_1_2(api, tmp_path):
    t = api.get_forms_buoc_12()
    assert t["ok"] and t["data"]["clb"]["co"] is False and t["data"]["de"]["co"] is False
    api.thu_muc_xuat = str(tmp_path / "tv")
    os.makedirs(api.thu_muc_xuat)
    api.nap_phieu_clb(_b64_phieu(tmp_path, DONG_PHIEU))
    cv = _ma(api, "CLB Cờ vua")
    api.nap_de_thi(_b64(_dien_de(api, tmp_path, [_dong(cv, "Q1")])))
    t = api.get_forms_buoc_12()["data"]
    assert t["clb"]["co"] and t["clb"]["n_clb"] == 2 and t["clb"]["loi"] == []
    assert t["de"]["co"] and t["de"]["khop"] and t["de"]["n_clb_thi"] == 1
    # nạp lại bước 1 với CLB khác -> đề cũ không khớp
    api.nap_phieu_clb(_b64_phieu(tmp_path, [_phieu("CLB Khác", mo_nhom="Có", phong="9")], ten="p2.xlsx"))
    assert api.get_forms_buoc_12()["data"]["de"]["khop"] is False


def test_de_thi_json_dot_giong_mac_dinh_khi_cung_noi_dung(api, tmp_path):
    """Dựng Excel từ de_thi.json mặc định, nạp qua API, so với tệp mặc định."""
    clubs = [{k: c[k] for k in TRUONG[:6]} for c in DE_MAC_DINH["cau_lac_bo"]]
    so_nhap_ = __import__("so_nhap")
    so_nhap_.ghi_so_nhap(forms_dot.duong_so_nhap_clb_dot(api.db_path), clubs=[
        dict(c, loai=so_nhap_.GIOI_HAN) for c in clubs])
    p = _mau(tmp_path, clubs, de=DE_MAC_DINH)
    kq = api.nap_de_thi(_b64(p))
    assert kq["ok"], kq
    moi = forms_dot.doc_de_dot(api.db_path)
    assert all("loai" in c for c in moi["cau_lac_bo"])       # loại của bước 1 đi theo sang de_thi.json
    assert json.dumps([{k: v for k, v in c.items() if k != "loai"} for c in moi["cau_lac_bo"]],
                      sort_keys=True) == json.dumps(
        copy.deepcopy(DE_MAC_DINH["cau_lac_bo"]), sort_keys=True)


def test_nap_de_thi_giu_loai_clb_va_tu_do_khong_vao_cau_vang_fa(api, tmp_path):
    """`loai` của bước 1 phải sang de_thi.json: bieu_mau.cac_phan_fa dựa vào nó để loại CLB Tự do khỏi câu huy chương vàng."""
    so_nhap_ = __import__("so_nhap")
    clubs = [dict(_clb("clb_td", "CLB Tự do"), loai=so_nhap_.TU_DO),
             dict(_clb("clb_gh", "CLB Giới hạn"), loai=so_nhap_.GIOI_HAN),
             dict(_clb("clb_tc", "CLB Tuyển chọn"), loai=so_nhap_.TUYEN_CHON, diem_san=5)]
    so_nhap_.ghi_so_nhap(forms_dot.duong_so_nhap_clb_dot(api.db_path), clubs=clubs)
    kq = api.nap_de_thi(_b64(_mau(tmp_path, clubs)))
    assert kq["ok"], kq
    de = forms_dot.doc_de_dot(api.db_path)
    assert {c["club_id"]: c.get("loai") for c in de["cau_lac_bo"]} == {
        "clb_td": so_nhap_.TU_DO, "clb_gh": so_nhap_.GIOI_HAN, "clb_tc": so_nhap_.TUYEN_CHON}
    cau_vang = next(c for ten, ds in bieu_mau.cac_phan_fa(de, "thu_2") for c in ds if "-vang]" in c[0])
    lua_chon = " | ".join(cau_vang[2])               # câu vàng chỉ liệt kê CLB không Tự do
    assert "clb_td" not in lua_chon
    assert "clb_gh" in lua_chon and "clb_tc" in lua_chon


def test_clb_khong_co_loai_thi_de_thi_khong_them_khoa_loai(tmp_path):
    clubs = [_clb("clb_a", "CLB A")]
    de, loi = so_de_thi.doc_so_de_thi(_mau(tmp_path, clubs), clubs)
    assert loi == [] and "loai" not in de["cau_lac_bo"][0]
