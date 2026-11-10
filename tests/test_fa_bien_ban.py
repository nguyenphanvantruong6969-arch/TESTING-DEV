"""FA-9: biên bản bốc thăm có người chứng kiến. Dữ liệu là dữ liệu MÔ PHỎNG."""
import re

import pytest

import fa_bien_ban as bb
from _fa import bat_fa, dung_fa_clb, dung_hs_fa, ma
from api import PipelineAPI

CAP = [("s2", 5), ("s1", 9), ("s3", 1)]
DEM = {"thu_3": {"n_hoc_sinh": 3, "n_xep": 3}, "thu_2": {"n_hoc_sinh": 3, "n_xep": 3}}


def _bg(cap=CAP, **kw):
    return bb.tao_ban_ghi("Đợt thử", kw.pop("t", "2026-11-09 10:00:00"), "abc123", 42, cap, DEM, **kw)


def test_ma_bam_khong_phu_thuoc_thu_tu_va_doi_khi_mot_so_doi():
    assert bb.sha256_stb(CAP) == bb.sha256_stb(list(reversed(CAP)))
    assert len(bb.sha256_stb(CAP)) == 64
    for i in range(len(CAP)):
        doi = [(s, n + 1 if k == i else n) for k, (s, n) in enumerate(CAP)]
        assert bb.sha256_stb(doi) != bb.sha256_stb(CAP)
    doi_ma = [("s9" if k == 0 else s, n) for k, (s, n) in enumerate(CAP)]
    assert bb.sha256_stb(doi_ma) != bb.sha256_stb(CAP)


def test_ban_ghi_giong_nhau_tru_thoi_diem():
    a, b = _bg(t="2026-11-09 10:00:00"), _bg(t="2026-11-10 23:59:59")
    assert a != b
    a.pop("thoi_diem"), b.pop("thoi_diem")
    assert a == b


def test_html_co_du_muc_va_khong_co_ma_hoc_sinh():
    h = bb.html_bien_ban(_bg())
    for tu in ("Biên bản bốc thăm", "Đợt thử", "abc123", "42", bb.sha256_stb(CAP), "Giáo viên chứng kiến",
               "Quản trị viên", "thu_2", "Thứ tự buổi lễ"):
        assert tu in h, tu
    for sid, _ in CAP:
        assert not re.search(r"\b%s\b" % sid, h)
    assert "canh-bao\">" not in h


def test_html_canh_bao_khi_du_lieu_da_sua():
    assert 'class="canh-bao"' in bb.html_bien_ban(_bg(ket_qua_con_khop=False))


def test_html_thoat_ky_tu_dac_biet():
    bg = bb.tao_ban_ghi("<b>x</b>", "t", "d", 1, CAP, DEM)
    assert "<b>x</b>" not in bb.html_bien_ban(bg)


# ----------------------------------------------------------------------------- qua API


def _dung(api):
    bat_fa(api)
    dung_fa_clb(api, T=(50, "TU_DO", None, None, 3), G=(2, "GIOI_HAN"))
    dung_hs_fa(api, "s1", "s2", "s3", "s4", nv={s: ["G", "T"] for s in ("s1", "s2", "s3", "s4")})


@pytest.fixture
def api2(tmp_path):
    return PipelineAPI(str(tmp_path / "hai.db"))


def _doc(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def test_chua_chay_thi_bao_loi(api, tmp_path):
    _dung(api)
    ra = api.export_bien_ban_boc_tham(str(tmp_path / "x.html"))
    assert not ra["ok"] and ma(ra["errors"]) == ["bien_ban_chua_boc_tham"]


def test_xuat_qua_api_va_giong_nhau_cung_du_lieu_cung_hat_giong(api, api2, tmp_path):
    _dung(api)
    _dung(api2)
    assert api.run_pipeline(seed=11)["ok"] and api2.run_pipeline(seed=11)["ok"]
    r1 = api.export_bien_ban_boc_tham(str(tmp_path / "a.html"))
    r2 = api2.export_bien_ban_boc_tham(str(tmp_path / "b.html"))
    assert r1["ok"] and r2["ok"], (r1, r2)
    assert r1["data"]["sha256_stb"] == r2["data"]["sha256_stb"]
    assert r1["data"]["hat_giong"] == 11
    h1, h2 = _doc(r1["data"]["path"]), _doc(r2["data"]["path"])
    chuan = lambda h: re.sub(r"Thời điểm xuất: [^<·]*", "T", h)   # noqa: E731
    assert chuan(h1) == chuan(h2)
    for sid in ("s1", "s2", "s3", "s4"):                  # không mã học sinh, không tên
        assert not re.search(r"\b%s\b" % sid, h1)
    assert "Em s1" not in h1
    assert "canh-bao\">" not in h1


def test_doi_so_boc_tham_thi_ma_bam_doi(api, api2, tmp_path):
    _dung(api)
    _dung(api2)
    assert api.run_pipeline(seed=11)["ok"] and api2.run_pipeline(seed=12)["ok"]
    a = api.export_bien_ban_boc_tham(str(tmp_path / "a.html"))["data"]
    b = api2.export_bien_ban_boc_tham(str(tmp_path / "b.html"))["data"]
    assert a["sha256_stb"] != b["sha256_stb"]


def test_sua_du_lieu_sau_khi_chay_thi_co_canh_bao(api, tmp_path):
    _dung(api)
    assert api.run_pipeline(seed=11)["ok"]
    assert api.create_student_if_missing("s9", "Em s9")["ok"]
    ra = api.export_bien_ban_boc_tham(str(tmp_path / "c.html"))
    assert ra["ok"] and ra["data"]["ket_qua_con_khop"] is False
    assert 'class="canh-bao"' in _doc(ra["data"]["path"])


# ----------------------------------------------------------------------------- FA-9b: bản Excel


def _o_xlsx(duong):
    """Mọi ô có giá trị của tệp xlsx, dạng chuỗi (theo thứ tự hàng, cột)."""
    from openpyxl import load_workbook
    wb = load_workbook(duong)
    return [str(c.value) for ws in wb.worksheets for row in ws.iter_rows() for c in row if c.value is not None]


def test_xlsx_co_du_muc_va_khong_co_ma_hoc_sinh(tmp_path):
    d = str(tmp_path / "bb.xlsx")
    bb.ghi_xlsx(_bg(), d)
    o = _o_xlsx(d)
    chung = " | ".join(o)
    for tu in ("Biên bản bốc thăm", "Đợt thử", "abc123", "42", bb.sha256_stb(CAP), "Giáo viên chứng kiến",
               "Quản trị viên", "thu_2", "thu_3"):
        assert tu in chung, tu
    for sid, _ in CAP:
        assert not re.search(r"\b%s\b" % sid, chung)


def test_xlsx_giong_nhau_tru_thoi_diem_va_ma_bam_doi_khi_mot_so_doi(tmp_path):
    a, b, c = (str(tmp_path / n) for n in ("a.xlsx", "b.xlsx", "c.xlsx"))
    bb.ghi_xlsx(_bg(t="2026-11-09 10:00:00"), a)
    bb.ghi_xlsx(_bg(t="2026-11-10 23:59:59"), b)
    oa, ob = _o_xlsx(a), _o_xlsx(b)
    assert oa != ob
    assert [x for x in oa if not x.startswith("2026-")] == [x for x in ob if not x.startswith("2026-")]
    bb.ghi_xlsx(_bg(cap=[("s2", 6)] + CAP[1:]), c)
    assert bb.sha256_stb(CAP) in oa and bb.sha256_stb(CAP) not in _o_xlsx(c)


def test_xlsx_canh_bao_khi_du_lieu_da_sua(tmp_path):
    d1, d2 = str(tmp_path / "1.xlsx"), str(tmp_path / "2.xlsx")
    bb.ghi_xlsx(_bg(), d1)
    bb.ghi_xlsx(_bg(ket_qua_con_khop=False), d2)
    assert "CẢNH BÁO" in _o_xlsx(d2) and "CẢNH BÁO" not in _o_xlsx(d1)


def test_api_xuat_ca_html_va_xlsx_cung_gia_tri(api, tmp_path):
    _dung(api)
    assert api.run_pipeline(seed=11)["ok"]
    ra = api.export_bien_ban_boc_tham(str(tmp_path / "bien_ban.html"))
    assert ra["ok"], ra
    px = ra["data"]["path_xlsx"]
    assert px.endswith(".xlsx") and px != ra["data"]["path"]
    o = _o_xlsx(px)
    assert ra["data"]["sha256_stb"] in o and "11" in o
    assert ra["data"]["sha256_stb"] in _doc(ra["data"]["path"])
    for sid in ("s1", "s2", "s3", "s4"):
        assert not re.search(r"\b%s\b" % sid, " | ".join(o))


def test_api_xlsx_khong_ghi_de_tep_cu(api, tmp_path):
    _dung(api)
    assert api.run_pipeline(seed=11)["ok"]
    r1 = api.export_bien_ban_boc_tham(str(tmp_path / "bien_ban.html"))["data"]
    r2 = api.export_bien_ban_boc_tham(str(tmp_path / "bien_ban.html"))["data"]
    assert r1["path_xlsx"] != r2["path_xlsx"]


# ----------------------------------------------------------------------------- FA-P1: chặn công thức trong bản Excel

TEN_DOC = '=HYPERLINK("http://ke-xau.example","Bấm vào đây")'


def _xml_trang(duong):
    import zipfile
    with zipfile.ZipFile(duong) as z:
        return "".join(z.read(n).decode("utf-8") for n in z.namelist() if n.startswith("xl/worksheets/"))


def test_xlsx_ten_ky_va_ten_buoi_khong_thanh_cong_thuc(tmp_path):
    """FA-P1: tên workspace (ô "Kỳ") và tên buổi do người dùng đặt; `=`, `+`, `-`, `@` ở đầu không được thành công thức
    (như `so_excel.Trang.o`), và chữ giữ nguyên văn."""
    d = str(tmp_path / "bb.xlsx")
    dem = {"=1+1": {"n_hoc_sinh": 1, "n_xep": 1}, "@a": {"n_hoc_sinh": 1, "n_xep": 1},
           "+2": {"n_hoc_sinh": 1, "n_xep": 1}, "-x": {"n_hoc_sinh": 1, "n_xep": 1}}
    bb.ghi_xlsx(bb.tao_ban_ghi(TEN_DOC, "t", "d", 1, CAP, dem), d)
    xml = _xml_trang(d)
    assert "<f>" not in xml and "<f " not in xml
    o = _o_xlsx(d)
    for chu in (TEN_DOC, "=1+1", "@a", "+2", "-x"):
        assert chu in o, chu


def test_api_xlsx_ten_workspace_khong_thanh_cong_thuc(api, tmp_path):
    import cau_hinh_ws as ch
    _dung(api)
    ch.ghi_cau_hinh(api.db_path, {"name": TEN_DOC, "rules": {"fa_daa": True}})
    assert api.run_pipeline(seed=11)["ok"]
    ra = api.export_bien_ban_boc_tham(str(tmp_path / "bien_ban.html"))
    assert ra["ok"], ra
    xml = _xml_trang(ra["data"]["path_xlsx"])
    assert "<f>" not in xml and "<f " not in xml
    assert TEN_DOC in _o_xlsx(ra["data"]["path_xlsx"])


# ----------------------------------------------------------------------------- SM-1: ký tự openpyxl cấm trong bản Excel

TEN_KY_LA = "Kỳ\x01một"


def test_xlsx_bo_ky_tu_dieu_khien_ma_khong_hong(tmp_path):
    """SM-1: tên kỳ / tên buổi có ký tự điều khiển (dán từ Word, tệp .zip) không làm hỏng bản Excel; ký tự cấm bị bỏ
    như `so_excel.lam_sach`, chữ còn lại giữ nguyên, chặn công thức (FA-P1) vẫn chạy."""
    from openpyxl import load_workbook
    d = str(tmp_path / "bb.xlsx")
    dem = {"thu\x02_2": {"n_hoc_sinh": 1, "n_xep": 1}, "=1+1\x03": {"n_hoc_sinh": 1, "n_xep": 1}}
    bb.ghi_xlsx(bb.tao_ban_ghi(TEN_KY_LA, "t", "d", 1, CAP, dem), d)
    load_workbook(d)
    o = _o_xlsx(d)
    assert "Kỳmột" in o and "thu_2" in o and "=1+1" in o
    xml = _xml_trang(d)
    assert "<f>" not in xml and "<f " not in xml


def test_api_ten_workspace_co_ky_tu_dieu_khien_van_xuat_du_hai_tep(api, tmp_path):
    """SM-1 repro: tên workspace `"Kỳ\\x01một"` -> trước đây `error_exporting_csv` và `bb.html` nằm lại. Nay: ok,
    có cả `.html` và `.xlsx`, tệp xlsx mở được bằng openpyxl."""
    import os

    import cau_hinh_ws as ch
    from openpyxl import load_workbook
    _dung(api)
    ch.ghi_cau_hinh(api.db_path, {"name": TEN_KY_LA, "rules": {"fa_daa": True}})
    assert api.run_pipeline(seed=11)["ok"]
    ra = api.export_bien_ban_boc_tham(str(tmp_path / "bb.html"))
    assert ra["ok"], ra
    assert os.path.isfile(ra["data"]["path"]) and os.path.isfile(ra["data"]["path_xlsx"])
    load_workbook(ra["data"]["path_xlsx"])
    assert "Kỳmột" in _o_xlsx(ra["data"]["path_xlsx"])


# ----------------------------------------------------------------------------- FA-P4: buổi theo thứ tự ngày

DEM_CN = {"chu_nhat": {"n_hoc_sinh": 2, "n_xep": 2}, "thu_2": {"n_hoc_sinh": 3, "n_xep": 3}}


def test_bien_ban_buoi_theo_thu_tu_ngay_ca_html_lan_xlsx(tmp_path):
    """FA-P4: `thu_2` đứng TRƯỚC `chu_nhat` (như THU_TU_BUOI), không theo vần; mã băm và số liệu không đổi."""
    g = bb.tao_ban_ghi("Đợt", "t", "d", 1, CAP, DEM_CN)
    assert list(g["dem_theo_buoi"]) == ["thu_2", "chu_nhat"]
    assert g["sha256_stb"] == bb.sha256_stb(CAP) and g["dem_theo_buoi"]["chu_nhat"] == DEM_CN["chu_nhat"]
    h = bb.html_bien_ban(g)
    assert h.index("<td>thu_2</td>") < h.index("<td>chu_nhat</td>")
    d = str(tmp_path / "bb.xlsx")
    bb.ghi_xlsx(g, d)
    o = _o_xlsx(d)
    assert o.index("thu_2") < o.index("chu_nhat")
