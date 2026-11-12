"""FA-M9 (TH = CHƯA thử trên Microsoft thật): API nạp tệp Forms / List ở bước 4 của thẻ "Chuẩn bị đợt".

`nhan_dien_tep_forms`, `chuyen_tep_forms`, `get_forms_nap`, `lay_so_nhap_nap`: phân loại tệp, loại tệp sai đường, đoán đề
(R5), luồng xác nhận (R6), bỏ câu, API == CLI trên cùng tệp, lỗi thì không ghi Sổ, nhập qua `import_so_nhap` có sẵn.
Dữ liệu MÔ PHỎNG; dựng tệp bằng các hàm của test_fa_m9_thuan / test_fa_m3_chuyen.
"""
import base64
import json
import os
import shutil

import openpyxl
import pytest

import forms_dot

forms_dot.nap_mau_forms()
import chuyen_forms_sang_phan_mem as cv  # noqa: E402
from test_fa_m3_chuyen import _lc, _tep_dang_ky  # noqa: E402
from test_fa_m9_thuan import (_bo, _bo_lech, _de_3_de, _de_ra_tep, _diem_covua,  # noqa: E402
                              _gia_tri_so_nhap)


def b64(duong, ten=None):
    with open(duong, "rb") as f:
        return {"ten": ten or os.path.basename(duong), "base64": base64.b64encode(f.read()).decode("ascii")}


def dat_dot(api, de, sn, duong="A"):
    """Đặt đường và dựng forms/de_thi.json + forms/SO_NHAP_CLB_CLB.xlsx của đợt."""
    assert api.dat_fa_duong(duong)["ok"]
    with open(forms_dot.duong_de_dot(api.db_path), "w", encoding="utf-8") as f:
        json.dump(de, f, ensure_ascii=False)
    shutil.copyfile(sn, forms_dot.duong_so_nhap_clb_dot(api.db_path))


def nap_dir(api):
    return forms_dot.thu_muc_nap(api.db_path)


def so_nhap_ghi(api):
    return os.path.join(nap_dir(api), cv.TEN_SO)


def tep_dang_ky_b(tmp_path, de):
    return _tep_dang_ky(tmp_path, de, [
        dict(sid="HS1", email="a@x.vn", nv1=_lc(de, "clb_covua"), nv2=_lc(de, "clb_vanhoc")),
        dict(sid="HS2", email="b@x.vn", nv1=_lc(de, "clb_covua"))], ten="dk.xlsx")


def loai_cua(res):
    return {t["ten"]: t["loai"] for t in res["data"]["tep"]}


# ---------------------------------------------------------------- nhận diện
def test_nhan_dien_tung_loai_duong_a(api, tmp_path):
    de = _de_3_de()
    lst, thi, sn = _bo(tmp_path, de, "A")
    dat_dot(api, de, sn, "A")
    dk = tep_dang_ky_b(tmp_path, de)
    sau = tmp_path / "sau.xlsx"
    wb = openpyxl.Workbook()
    wb.active.append(["ID", "Email", "[co_sai] Em có thấy sai không?"])
    wb.save(str(sau))
    la = tmp_path / "la.xlsx"
    wb = openpyxl.Workbook()
    wb.active.append(["ID", "Cột lạ"])
    wb.save(str(la))
    res = api.nhan_dien_tep_forms([b64(lst), b64(thi), b64(dk), b64(str(sau)), b64(str(la))])
    assert res["ok"]
    assert loai_cua(res) == {"list.csv": "lists", "thi.xlsx": "bai_thi", "dk.xlsx": "dang_ky",
                             "sau.xlsx": "sau_ket_qua", "la.xlsx": "khong_ro"}
    loi = {t["ten"]: t["loi"] and t["loi"]["code"] for t in res["data"]["tep"]}
    assert loi == {"list.csv": None, "thi.xlsx": None, "dk.xlsx": "forms_tep_sai_duong",
                   "sau.xlsx": "forms_tep_sau_ket_qua", "la.xlsx": "forms_tep_khong_nhan_ra"}
    assert res["data"]["can_chon_de"] is True


def test_nhan_dien_duong_b_tu_choi_list(api, tmp_path):
    de = _de_3_de()
    lst, thi, sn = _bo(tmp_path, de, "A")
    dat_dot(api, de, sn, "B")
    res = api.nhan_dien_tep_forms([b64(lst), b64(tep_dang_ky_b(tmp_path, de))])
    loi = {t["ten"]: t["loi"] for t in res["data"]["tep"]}
    assert loi["list.csv"] == {"code": "forms_tep_sai_duong", "params": {"ten": "list.csv", "duong": "B"}}
    assert loi["dk.xlsx"] is None


def test_nhan_dien_chua_chon_duong(api, tmp_path):
    lst, _, _ = _bo(tmp_path, _de_3_de(), "A")
    res = api.nhan_dien_tep_forms([b64(lst)])
    assert not res["ok"] and res["errors"][0]["code"] == "forms_duong_chua_chon"


@pytest.mark.parametrize("chu", ["A", "B"])
def test_nhan_dien_doan_de(api, tmp_path, chu):
    de = _de_3_de()
    _, thi, sn = _bo(tmp_path, de, chu)
    dat_dot(api, de, sn)
    res = api.nhan_dien_tep_forms([b64(thi)])
    assert res["data"]["tep"][0]["bien_the_doan"] == chu


def test_nhan_dien_khong_ghi_gi_va_khong_can_de(api, tmp_path):
    _, thi, sn = _bo(tmp_path, _de_3_de(), "A")
    assert api.dat_fa_duong("A")["ok"]                       # chưa có de_thi.json
    res = api.nhan_dien_tep_forms([b64(thi), {"ten": "rong.xlsx", "base64": ""}, {"ten": "hong.xlsx", "base64": "QUJD"}])
    assert res["ok"] and res["data"]["tep"][0]["loai"] == "bai_thi" and res["data"]["tep"][0]["bien_the_doan"] is None
    assert res["data"]["tep"][1]["loi"]["code"] == "xlsx_empty"
    assert res["data"]["tep"][2]["loi"]["code"] == "xlsx_read_failed"
    assert os.listdir(forms_dot.thu_muc_tai_len(api.db_path)) == []


# ---------------------------------------------------------------- chuyển đổi == CLI
@pytest.mark.parametrize("chu", ["A", "B"])
def test_chuyen_api_giong_het_cli(api, tmp_path, chu):
    de = _de_3_de()
    lst, thi, sn = _bo(tmp_path, de, chu)
    dat_dot(api, de, sn)
    cli = tmp_path / "cli"
    assert cv.main(["--fa-daa", "--so-nhap-clb", sn, "--lists", lst, "--de", _de_ra_tep(tmp_path, de),
                    "--bien-the-tep", "thi.xlsx=" + chu, "--ra", str(cli), thi]) == 0
    res = api.chuyen_tep_forms([b64(lst), b64(thi)], {}, None)
    assert res["ok"] and res["data"]["trang_thai"] == "xong", res
    assert res["data"]["n_hoc_sinh"] == 4 and res["data"]["n_bai_thi"] == 4
    assert _gia_tri_so_nhap(nap_dir(api)) == _gia_tri_so_nhap(str(cli))
    with open(os.path.join(nap_dir(api), cv.TEN_EMAIL_MA_HS), "rb") as a, open(cli / cv.TEN_EMAIL_MA_HS, "rb") as b:
        assert a.read() == b.read()
    assert res["data"]["xem_truoc"]["n_hoc_sinh"] == 4 and res["data"]["xem_truoc"]["loi"] == []
    assert res["data"]["ghi_chu"]


def test_chuyen_duong_b_tu_tep_dang_ky(api, tmp_path):
    de = _de_3_de()
    _, thi, sn = _bo(tmp_path, de, "A")
    dat_dot(api, de, sn, "B")
    dk = tep_dang_ky_b(tmp_path, de)
    cli = tmp_path / "cli"
    assert cv.main(["--fa-daa", "--so-nhap-clb", sn, "--de", _de_ra_tep(tmp_path, de), "--dang-ky", dk,
                    "--bien-the-tep", "thi.xlsx=A", "--ra", str(cli), thi]) == 0
    res = api.chuyen_tep_forms([b64(dk), b64(thi)], {"thi.xlsx": "A"}, None)
    assert res["ok"] and res["data"]["n_hoc_sinh"] == 2
    assert _gia_tri_so_nhap(nap_dir(api)) == _gia_tri_so_nhap(str(cli))


def test_chuyen_bien_the_chon_tay_thang_doan(api, tmp_path):
    de = _de_3_de()
    lst, thi, sn = _bo(tmp_path, de, "B")
    dat_dot(api, de, sn)
    res = api.chuyen_tep_forms([b64(lst), b64(thi)], {"thi.xlsx": "A"}, None)          # đoán B, admin ép A
    assert res["ok"] and set(_diem_covua(nap_dir(api)).values()) != {10.0}
    res = api.chuyen_tep_forms(None, {}, None)                                          # dùng đề đoán được = B
    assert res["ok"] and set(_diem_covua(nap_dir(api)).values()) == {10.0}


def test_chuyen_khong_biet_de_thi_bat_chon(api, tmp_path):
    de = _de_3_de()
    lst, thi, sn = _bo(tmp_path, de, "A")
    dat_dot(api, de, sn)
    res = api.chuyen_tep_forms([b64(lst), b64(thi)], {"thi.xlsx": "Z"}, None)
    assert not res["ok"] and res["errors"][0] == {"code": "forms_can_chon_de", "params": {"ten": "thi.xlsx"}}
    assert not os.path.exists(so_nhap_ghi(api))
    wb = openpyxl.load_workbook(thi)                           # đề lạ: đoán None, không chọn thì bắt chọn
    ws = wb.active
    ws.cell(1, 7).value = "[clb_covua-1] một câu lạ hoàn toàn"
    wb.save(thi)
    res = api.chuyen_tep_forms([b64(lst), b64(thi)], {}, None)
    assert not res["ok"] and res["errors"][0]["code"] == "forms_can_chon_de"
    assert api.nhan_dien_tep_forms([b64(thi)])["data"]["tep"][0]["bien_the_doan"] is None


# ---------------------------------------------------------------- xác nhận (R6) và bỏ câu
def test_xac_nhan_roi_lua_chon_thi_ghi_so(api, tmp_path):
    de = _de_3_de()
    lst, thi, sn = _bo_lech(tmp_path, de)
    dat_dot(api, de, sn)
    files = [b64(lst)] + [b64(t) for t in thi]
    bt = {"thi_A.xlsx": "A", "thi_B.xlsx": "B"}
    res = api.chuyen_tep_forms(files, bt, None)
    assert res["ok"] and res["data"]["trang_thai"] == "cho_xac_nhan"
    cx = res["data"]["cho_xac_nhan"]
    assert cx["clb"] == ["clb_covua"] and os.path.isfile(cx["bao_cao"]) and cx["thong_bao"]
    assert not os.path.exists(so_nhap_ghi(api))
    # tệp đã giữ ở tai_len: không cần gửi lại
    assert sorted(os.listdir(forms_dot.thu_muc_tai_len(api.db_path))) == ["list.csv", "thi_A.xlsx", "thi_B.xlsx"]
    res = api.chuyen_tep_forms(None, bt, {"dieu_chinh": "giu"})
    assert res["ok"] and res["data"]["trang_thai"] == "xong"
    d = _diem_covua(nap_dir(api))
    assert d["e0@x.vn"] == 10.0 and d["f0@x.vn"] == 4.0
    res = api.chuyen_tep_forms(None, bt, {"dieu_chinh": "ap_dung"})
    assert res["ok"] and res["data"]["trang_thai"] == "xong"
    d = _diem_covua(nap_dir(api))
    assert d["e0@x.vn"] == 7.0 and d["f0@x.vn"] == 7.0


def test_bo_cau_cham_lai(api, tmp_path):
    de = _de_3_de()
    lst, thi, sn = _bo(tmp_path, de, "A", dung=4)
    dat_dot(api, de, sn)
    res = api.chuyen_tep_forms([b64(lst), b64(thi)], {}, None)
    assert set(_diem_covua(nap_dir(api)).values()) == {8.0}
    assert isinstance(res["data"]["cau_co_co"], list)
    res = api.chuyen_tep_forms(None, {}, {"bo_cau": [["clb_covua", "A", 5]]})
    assert res["ok"] and set(_diem_covua(nap_dir(api)).values()) == {10.0}


# ---------------------------------------------------------------- lỗi: không ghi gì
def test_loi_thieu_de_hoac_clb_hoac_tep(api, tmp_path):
    de = _de_3_de()
    lst, thi, sn = _bo(tmp_path, de, "A")
    assert api.dat_fa_duong("A")["ok"]
    assert api.chuyen_tep_forms([b64(lst)], {}, None)["errors"][0]["code"] == "forms_chua_co_de"
    with open(forms_dot.duong_de_dot(api.db_path), "w", encoding="utf-8") as f:
        json.dump(de, f, ensure_ascii=False)
    assert api.chuyen_tep_forms([b64(lst)], {}, None)["errors"][0]["code"] == "forms_chua_co_clb"
    shutil.copyfile(sn, forms_dot.duong_so_nhap_clb_dot(api.db_path))
    assert api.chuyen_tep_forms([], {}, None)["errors"][0]["code"] == "forms_thieu_tep_nap"
    assert api.chuyen_tep_forms([b64(thi)], {}, None)["errors"][0]["code"] == "forms_thieu_tep_dang_ky"
    assert api.chuyen_tep_forms([b64(lst), b64(lst, "list2.csv")], {}, None)["errors"][0]["code"] == "forms_nhieu_tep_list"
    assert not os.path.exists(so_nhap_ghi(api))


def test_loi_tep_sai_duong_tra_het_loi_va_khong_ghi(api, tmp_path):
    de = _de_3_de()
    lst, thi, sn = _bo(tmp_path, de, "A")
    dat_dot(api, de, sn, "A")
    res = api.chuyen_tep_forms([b64(lst), b64(thi), b64(tep_dang_ky_b(tmp_path, de))], {}, None)
    assert not res["ok"] and [e["code"] for e in res["errors"]] == ["forms_tep_sai_duong"]
    assert not os.path.exists(so_nhap_ghi(api))


def test_loi_bo_chuyen_doi_khong_ghi_so(api, tmp_path):
    de = _de_3_de()
    lst, thi, sn = _bo(tmp_path, de, "A")
    dat_dot(api, de, sn)
    with open(lst, "w", encoding="utf-8-sig") as f:               # List không có em nào
        f.write("Email,HoTen,Thu,NV1,TrangThai\n")
    res = api.chuyen_tep_forms([b64(lst), b64(thi)], {}, None)
    assert not res["ok"] and res["errors"][0]["code"] == "forms_khong_chuyen_duoc"
    assert "học sinh" in res["errors"][0]["params"]["detail"]
    assert not os.path.exists(so_nhap_ghi(api))
    assert api.lay_so_nhap_nap()["errors"][0]["code"] == "forms_chua_chuyen_tep"


def test_ten_tep_nguy_hiem_bi_lam_sach(api, tmp_path):
    de = _de_3_de()
    lst, thi, sn = _bo(tmp_path, de, "A")
    dat_dot(api, de, sn)
    f = b64(lst, "../../x/list.csv")
    assert api.chuyen_tep_forms([f, b64(thi, "thi.xlsx")], {}, None)["ok"]
    assert "list.csv" in os.listdir(forms_dot.thu_muc_tai_len(api.db_path))
    assert not os.path.exists(os.path.join(os.path.dirname(api.db_path), "x"))


# ---------------------------------------------------------------- nhập bằng đường có sẵn
def test_nhap_qua_import_so_nhap_co_san(api, tmp_path):
    de = _de_3_de()
    lst, thi, sn = _bo(tmp_path, de, "A")
    dat_dot(api, de, sn)
    res = api.chuyen_tep_forms([b64(lst), b64(thi)], {}, None)
    so = api.lay_so_nhap_nap()
    assert so["ok"] and so["data"]["ten"] == cv.TEN_SO
    xt = api.xem_truoc_so_nhap(so["data"]["base64"])
    assert xt["data"]["n_hoc_sinh"] == res["data"]["xem_truoc"]["n_hoc_sinh"] == 4
    nap = api.import_so_nhap(so["data"]["base64"])
    assert nap["ok"], nap
    assert nap["data"]["n_hoc_sinh"] == 4


def test_get_forms_nap_nho_tep_da_tai(api, tmp_path):
    de = _de_3_de()
    lst, thi, sn = _bo(tmp_path, de, "A")
    dat_dot(api, de, sn)
    assert api.get_forms_nap()["data"] == {"tep": [], "co_so_nhap": False, "can_chon_de": True}
    api.chuyen_tep_forms([b64(lst), b64(thi)], {}, None)
    d = api.get_forms_nap()["data"]
    assert {t["ten"]: t["loai"] for t in d["tep"]} == {"list.csv": "lists", "thi.xlsx": "bai_thi"}
    assert d["tep"][1]["bien_the_doan"] == "A" and d["co_so_nhap"] is True
