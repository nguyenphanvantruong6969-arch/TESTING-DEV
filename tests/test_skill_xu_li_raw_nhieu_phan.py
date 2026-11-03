# -*- coding: utf-8 -*-
"""T4-K3: skill `xu-li-raw-forms` đọc MỘT THƯ MỤC gồm nhiều phần CSV
(RAW_PHIEU_<ky>_<giờ>_p01.csv, p02, ...) do bước xuất theo phần tạo ra.

Kiểm: ghép đúng và cho cùng Sổ như một tệp; thứ tự tự nhiên (p2 trước p10);
từ chối (không ghi tệp nào) khi thiếu phần, tiêu đề lệch, hai bộ xuất lẫn nhau,
một phiếu nằm ở hai phần, hoặc thư mục không có phần nào. Tệp đơn: như cũ.
"""

import csv
import io
import os

import pytest

openpyxl = pytest.importorskip("openpyxl")

import test_skill_xu_li_raw as goc  # noqa: E402
from test_skill_xu_li_raw import Raw, ghi_dap_an, ghi_clb  # noqa: E402

# Dùng lại hai fixture của tệp gốc (nạp script skill, dữ liệu đề của biểu mẫu).
xr = pytest.fixture(scope="module", name="xr")(goc.xr.__wrapped__)
de = pytest.fixture(scope="module", name="de")(goc.de.__wrapped__)


def _ghi_csv(duong, tieu_de, dong):
    with io.open(duong, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(tieu_de)
        for r in dong:
            w.writerow([str(x) for x in r])


def _raw(xr, de, n):
    r = Raw(xr, de)
    T2 = [c["id"] for c in de[0]["clubs"]]
    for i in range(1, n + 1):
        r.phieu("HS%03d" % i, "Học sinh %d" % i,
                {"thu_2": {"tick": [T2[0]], "lam": {T2[0]: i % 3}}})
    return r


def _chia(r, so_phan):
    """Chia các dòng theo phiếu thành so_phan phần, không cắt ngang phiếu."""
    theo_phieu = {}
    for d in r.rows:
        theo_phieu.setdefault(d[0], []).append(d)
    so = sorted(theo_phieu)
    co = -(-len(so) // so_phan)
    return [[d for p in so[k:k + co] for d in theo_phieu[p]] for k in range(0, len(so), co)]


def _thu_muc(tmp_path, xr, r, so_phan, tien_to="RAW_PHIEU_ky1_0900"):
    tm = tmp_path / "phan"
    tm.mkdir()
    for k, dong in enumerate(_chia(r, so_phan), 1):
        _ghi_csv(str(tm / ("%s_p%02d.csv" % (tien_to, k))), xr.COT_RAW, dong)
    return tm


def _chay(xr, tmp_path, de, raw, ra):
    ghi_dap_an(de, str(tmp_path / "DAP_AN.xlsx"))
    ghi_clb(de, str(tmp_path / "01.xlsx"))
    return xr.main(["--raw", str(raw), "--dap-an", str(tmp_path / "DAP_AN.xlsx"),
                    "--clb", str(tmp_path / "01.xlsx"), "--ra", str(ra)])


def _bang_so(duong):
    wb = openpyxl.load_workbook(str(duong), read_only=True)
    out = {ten: [tuple(r) for r in wb[ten].iter_rows(values_only=True)] for ten in wb.sheetnames}
    wb.close()
    return out


def test_thu_muc_nhieu_phan_cho_cung_so_nhu_mot_tep(tmp_path, xr, de):
    r = _raw(xr, de, 12)
    _ghi_csv(str(tmp_path / "RAW_PHIEU.csv"), xr.COT_RAW, r.rows)
    tm = _thu_muc(tmp_path, xr, r, 3)
    assert _chay(xr, tmp_path, de, tmp_path / "RAW_PHIEU.csv", tmp_path / "ra1") == 0
    assert _chay(xr, tmp_path, de, tm, tmp_path / "ra2") == 0
    assert _bang_so(tmp_path / "ra1" / "SO_NHAP_CLB.xlsx") == \
        _bang_so(tmp_path / "ra2" / "SO_NHAP_CLB.xlsx")
    assert (tmp_path / "ra1" / "BAO_CAO_BAT_THUONG.md").read_text(encoding="utf-8") == \
        (tmp_path / "ra2" / "BAO_CAO_BAT_THUONG.md").read_text(encoding="utf-8")


def test_thu_tu_tu_nhien_p2_truoc_p10(tmp_path, xr, de):
    r = _raw(xr, de, 11)
    tm = _thu_muc(tmp_path, xr, r, 11)
    td, dong = xr.doc_raw(str(tm))
    assert td == xr.COT_RAW
    so = [int(d["phieu_so"]) for d in dong]
    assert so == sorted(so) and so[0] == 1 and so[-1] == 11


def test_tep_don_nhu_cu(tmp_path, xr, de):
    r = _raw(xr, de, 3)
    _ghi_csv(str(tmp_path / "RAW_PHIEU.csv"), xr.COT_RAW, r.rows)
    assert xr.doc_raw(str(tmp_path / "RAW_PHIEU.csv")) == xr.doc_bang(str(tmp_path / "RAW_PHIEU.csv"))


def _tu_choi(xr, tmp_path, de, tm, chu):
    ra = tmp_path / "ra"
    assert _chay(xr, tmp_path, de, tm, ra) == 1
    assert not ra.exists()
    with pytest.raises(xr.LoiDauVao, match=chu):
        xr.doc_raw(str(tm))


def test_thieu_phan_thi_tu_choi(tmp_path, xr, de):
    tm = _thu_muc(tmp_path, xr, _raw(xr, de, 6), 3)
    os.remove(str(tm / "RAW_PHIEU_ky1_0900_p02.csv"))
    _tu_choi(xr, tmp_path, de, tm, "thiếu phần")


def test_tieu_de_lech_thi_tu_choi(tmp_path, xr, de):
    r = _raw(xr, de, 4)
    tm = _thu_muc(tmp_path, xr, r, 2)
    _ghi_csv(str(tm / "RAW_PHIEU_ky1_0900_p02.csv"), xr.COT_RAW + ["lop"], _chia(r, 2)[1])
    _tu_choi(xr, tmp_path, de, tm, "tiêu đề")


def test_hai_bo_xuat_lan_nhau_thi_tu_choi(tmp_path, xr, de):
    r = _raw(xr, de, 4)
    tm = _thu_muc(tmp_path, xr, r, 2)
    _ghi_csv(str(tm / "RAW_PHIEU_ky1_1400_p01.csv"), xr.COT_RAW, r.rows)
    _tu_choi(xr, tmp_path, de, tm, "nhiều bộ")


def test_mot_phieu_o_hai_phan_thi_tu_choi(tmp_path, xr, de):
    r = _raw(xr, de, 4)
    tm = _thu_muc(tmp_path, xr, r, 2)
    # phần 2 đánh số lại từ 1 (lỗi xuất): phiếu 1 nằm ở hai phần
    p2 = [[1 if d[0] == 3 else 2] + d[1:] for d in _chia(r, 2)[1]]
    _ghi_csv(str(tm / "RAW_PHIEU_ky1_0900_p02.csv"), xr.COT_RAW, p2)
    _tu_choi(xr, tmp_path, de, tm, "hai phần")


def test_thu_muc_khong_co_phan_nao(tmp_path, xr, de):
    tm = tmp_path / "rong"
    tm.mkdir()
    (tm / "ghi_chu.txt").write_text("x", encoding="utf-8")
    _tu_choi(xr, tmp_path, de, tm, "không có phần")
