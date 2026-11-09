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
