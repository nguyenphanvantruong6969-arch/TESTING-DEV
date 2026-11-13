"""FA-M10 (TH = CHƯA thử trên Microsoft thật): ba nút sau khi xếp (bước 5 thẻ "Chuẩn bị đợt").

`xuat_ket_qua_list`, `ai_chua_dang_ky`, `doi_chieu_hai_lan`: đầu ra của API == đầu ra của dòng lệnh trên cùng tệp; thiếu đầu vào
-> mã lỗi, không ghi gì. Dữ liệu MÔ PHỎNG; dựng bằng test_fa_ly_do / test_fa_m9_*.
"""
import csv
import json
import os

import pytest

import forms_dot

forms_dot.nap_mau_forms()
import danh_sach_chua_dang_ky as ds  # noqa: E402
import doi_chieu_lists as dc  # noqa: E402
import ghep_ket_qua_email as gk  # noqa: E402
from test_fa_ly_do import _dung  # noqa: E402
from test_fa_m9_nap_tep_forms import b64, dat_dot, tep_dang_ky_b  # noqa: E402
from test_fa_m9_thuan import _bo, _de_3_de  # noqa: E402
from test_fa_m10_thuan import _bang, _csv  # noqa: E402


@pytest.fixture
def ra(api, tmp_path):
    """Thư mục Tải xuống giả: mọi đầu ra của B rơi vào đây."""
    d = tmp_path / "tai_ve"
    d.mkdir()
    api.thu_muc_xuat = str(d)
    return d


def _email(api, hs=("s1", "s2", "s3")):
    with open(forms_dot.duong_email_ma_hs(api.db_path), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Email", "student_id"])
        for s in hs:
            w.writerow(["%s@X.vn" % s, s])


def _dung_da_xep(api):
    _dung(api)
    assert api.run_pipeline(seed=9)["ok"]
    assert api.dat_fa_duong("A")["ok"]


def _doc(p):
    with open(p, "rb") as f:
        return f.read()


# ---------------------------------------------------------------- xuat_ket_qua_list
def test_xuat_ket_qua_list_bang_cli_cung_tep(api, ra, tmp_path):
    _dung_da_xep(api)
    _email(api)
    kq = api.xuat_ket_qua_list()
    assert kq["ok"], kq
    p = kq["data"]["path"]
    assert os.path.dirname(p) == str(ra) and os.path.basename(p) == "KETQUA_NHAP_LIST.csv"
    # CLI trên cùng hai tệp: export_ly_do_csv (kiosk) rồi ghep_ket_qua_email
    ly_do = api.export_ly_do_csv(str(tmp_path / "ly_do.csv"))["data"]["path"]
    cli = str(tmp_path / "cli.csv")
    assert gk.main([ly_do, forms_dot.duong_email_ma_hs(api.db_path), "--ra", cli]) == 0
    assert _doc(p) == _doc(cli)
    dong = list(csv.DictReader(open(p, encoding="utf-8-sig")))
    assert len(dong) == kq["data"]["n_rows"] > 0 and dong[0]["Email"].endswith("@x.vn")
    assert any("s4" in c for c in kq["data"]["canh_bao"])           # s4 không có trong tệp email
    assert sorted(os.listdir(ra)) == ["KETQUA_NHAP_LIST.csv"]       # không để lại ket_qua_ly_do.csv


def test_xuat_ket_qua_list_khong_ghi_de_lan_truoc(api, ra):
    _dung_da_xep(api)
    _email(api)
    p1 = api.xuat_ket_qua_list()["data"]["path"]
    p2 = api.xuat_ket_qua_list()["data"]["path"]
    assert p1 != p2 and os.path.isfile(p1) and os.path.isfile(p2)


def test_xuat_ket_qua_list_thieu_email(api, ra):
    _dung_da_xep(api)
    kq = api.xuat_ket_qua_list()
    assert not kq["ok"] and kq["errors"][0]["code"] == "forms_thieu_email"
    assert os.listdir(ra) == []


def test_xuat_ket_qua_list_chua_chay_xep_hoac_chua_chon_duong(api, ra):
    assert api.xuat_ket_qua_list()["errors"][0]["code"] == "forms_duong_chua_chon"
    assert api.dat_fa_duong("A")["ok"]
    _email(api)
    kq = api.xuat_ket_qua_list()
    assert not kq["ok"] and kq["errors"][0]["code"] == "fa_chua_co_ly_do"
    assert os.listdir(ra) == []


# ---------------------------------------------------------------- ai_chua_dang_ky
def _lop(tmp_path, hs):
    return _csv(tmp_path / "lop.csv", ["student_id", "class_id"], [[s, c] for s, c in hs])


def test_ai_chua_dang_ky_bang_cli_cung_tep(api, ra, tmp_path):
    de = _de_3_de()
    _, thi, sn = _bo(tmp_path, de, "A", so_em=2)
    dat_dot(api, de, sn, "B")
    dk = tep_dang_ky_b(tmp_path, de)
    assert api.chuyen_tep_forms([b64(dk), b64(thi)], {"thi.xlsx": "A"}, {})["ok"]
    lop = _lop(tmp_path, [("HS1", "10A1"), ("HS2", "10A1"), ("HS7", "10A1"), ("HS8", "10A2")])
    kq = api.ai_chua_dang_ky(b64(lop)["base64"])
    assert kq["ok"], kq
    d = kq["data"]
    assert sorted(d["tep"]) == ["chua_dang_ky_10A1.csv", "chua_dang_ky_10A2.csv", "tong_hop.csv"]
    assert (d["n_lop"], d["n_email"]) == (2, 2)
    assert os.path.dirname(d["thu_muc"]) == str(ra)
    cli = str(tmp_path / "cli")
    assert ds.main([lop, forms_dot.duong_email_ma_hs(api.db_path), "--ra", cli]) == 0
    assert sorted(os.listdir(cli)) == sorted(os.listdir(d["thu_muc"]))
    for ten in os.listdir(cli):
        assert _doc(os.path.join(cli, ten)) == _doc(os.path.join(d["thu_muc"], ten))
    chua = list(csv.DictReader(open(os.path.join(d["thu_muc"], "chua_dang_ky_10A1.csv"), encoding="utf-8-sig")))
    assert [r["student_id"] for r in chua] == ["HS7"]


def test_ai_chua_dang_ky_loi(api, ra, tmp_path):
    assert api.ai_chua_dang_ky("")["errors"][0]["code"] == "forms_duong_chua_chon"
    assert api.dat_fa_duong("B")["ok"]
    lop = _lop(tmp_path, [("HS1", "10A1")])
    assert api.ai_chua_dang_ky(b64(lop)["base64"])["errors"][0]["code"] == "forms_thieu_email"
    _email(api, ("HS1",))
    assert api.ai_chua_dang_ky("")["errors"][0]["code"] == "xlsx_empty"
    sai = _csv(tmp_path / "sai.csv", ["a", "b"], [["1", "2"]])
    kq = api.ai_chua_dang_ky(b64(sai)["base64"])
    assert kq["errors"][0]["code"] == "forms_thieu_danh_sach_lop"
    assert os.listdir(ra) == []


# ---------------------------------------------------------------- doi_chieu_hai_lan
def _dat_de(api, de):
    assert api.dat_fa_duong("A")["ok"]
    with open(forms_dot.duong_de_dot(api.db_path), "w", encoding="utf-8") as f:
        json.dump(de, f, ensure_ascii=False)


def test_doi_chieu_hai_lan_bang_cli_cung_tep(api, ra, tmp_path):
    de = _de_3_de()
    _dat_de(api, de)
    dau = ["Email", "HoTen", "Thu", "NV1", "NV2", "Lop", "CoSo"]
    cu = _csv(tmp_path / "cu.csv", dau, [["a@x.vn", "A", "thu_2", "clb_covua", "clb_vanhoc", "10A1", "CS1"],
                                         ["b@x.vn", "B", "thu_2", "clb_covua", "", "10A2", "CS1"]])
    moi = _csv(tmp_path / "moi.csv", dau, [["a@x.vn", "A", "thu_2", "clb_vanhoc", "clb_covua", "10A1", "CS1"],
                                           ["c@x.vn", "C", "thu_2", "clb_covua", "", "10A3", "CS1"]])
    kq = api.doi_chieu_hai_lan(b64(cu)["base64"], b64(moi)["base64"])
    assert kq["ok"], kq
    d = kq["data"]
    assert d["dem"] == {"moi": 1, "rut": 1, "doi_nv": 1, "doi_lop": 0, "doi_co_so": 0}
    assert os.path.dirname(d["path"]) == str(ra) and d["path"].endswith(".xlsx")
    cli = str(tmp_path / "cli.xlsx")
    de_tep = forms_dot.duong_de_dot(api.db_path)
    assert dc.main([cu, moi, "--ra", cli, "--de", de_tep]) == 0
    assert _bang(d["path"]) == _bang(cli)


def test_doi_chieu_hai_lan_loi_khong_ghi_gi(api, ra, tmp_path):
    assert api.doi_chieu_hai_lan("", "")["errors"][0]["code"] == "forms_duong_chua_chon"
    assert api.dat_fa_duong("A")["ok"]
    assert api.doi_chieu_hai_lan("", "")["errors"][0]["code"] == "forms_chua_co_de"
    _dat_de(api, _de_3_de())
    assert api.doi_chieu_hai_lan("", "")["errors"][0]["code"] == "xlsx_empty"
    thieu = _csv(tmp_path / "t.csv", ["Email", "HoTen"], [["a@x.vn", "A"]])
    kq = api.doi_chieu_hai_lan(b64(thieu)["base64"], b64(thieu)["base64"])
    assert not kq["ok"] and kq["errors"][0]["code"] == "forms_khong_chuyen_duoc"
    assert os.listdir(ra) == []
