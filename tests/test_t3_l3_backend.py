"""T3-L3 (T3-19) — `export_bang_dang_xem`: tệp Excel của đúng bảng đang xem ở thẻ 02 Kết quả.

Một trang, cùng cột với màn hình (mã, họ tên, [lớp], CLB/buổi), KHÔNG điểm thi, điểm quyết tâm hay
số bốc thăm. Dữ liệu MÔ PHỎNG."""

import os

import pytest
from _wharton import tat_wharton
from openpyxl import load_workbook


@pytest.fixture
def api(api):
    tat_wharton(api)
    return api


def _nap(api):
    """6 em, CLB 'a' chỉ 1 chỗ (nên có em chưa có chỗ). Lớp: 10A2, 10A10, 10A2, 10A1, 10A1, (trống)."""
    api.create_or_update_club("a", "CLB A", 1, 0, "")
    api.create_or_update_club("b", "CLB B", 5, 0, "")
    cot = "student_id,name,pref_1,pref_2\n"
    dong = "".join("HS00%d,Em %d,a,b\n" % (i, i) for i in range(1, 7))
    dong = dong.replace("HS006,Em 6,a,b", "HS006,Em 6,a,")
    assert api.import_preferences_csv(cot + dong)["ok"]
    with api._ket_noi_ghi() as cur:
        for sid, lop in (("HS001", "10A2"), ("HS002", "10A10"), ("HS003", "10A2"),
                         ("HS004", "10A1"), ("HS005", "10A1")):
            cur.execute("UPDATE students SET class_id = ? WHERE student_id = ?", (lop, sid))
    assert api.run_pipeline(seed=7)["ok"]


def _o(path):
    ws = load_workbook(path).active
    return [[c.value for c in r] for r in ws.iter_rows()]


def _dong_du_lieu(o, dau):
    i = next(k for k, r in enumerate(o) if r[0] == dau)
    return o[i], [r for r in o[i + 1:] if r[0]]


def test_xuat_mot_lop_dung_cot_va_dung_em(api, tmp_path):
    _nap(api)
    r = api.export_bang_dang_xem("lop", "10A2", str(tmp_path / "l.xlsx"))
    assert r["ok"], r["errors"]
    assert r["data"]["n_dong"] == 2 and os.path.isfile(r["data"]["path"])
    dau, dong = _dong_du_lieu(_o(r["data"]["path"]), "Mã học sinh")
    assert dau[:2] == ["Mã học sinh", "Họ tên"]
    assert sorted(d[0] for d in dong) == ["HS001", "HS003"]
    assert all(len(d) == len(dau) for d in dong)


def test_xuat_khong_co_diem_hay_so_boc_tham(api, tmp_path):
    _nap(api)
    for kieu, gia in (("lop", "10A1"), ("clb", "b"), ("ma", "")):
        r = api.export_bang_dang_xem(kieu, gia, str(tmp_path / (kieu + ".xlsx")))
        assert r["ok"], r["errors"]
        chu = " ".join(str(c).lower() for row in _o(r["data"]["path"]) for c in row if c)
        for cam in ("điểm", "bốc thăm", "số bốc", "diện", "score", "draw"):
            assert cam not in chu, (kieu, cam)


def test_xuat_clb_chi_gom_thanh_vien(api, tmp_path):
    _nap(api)
    r = api.export_bang_dang_xem("clb", "a", str(tmp_path / "c.xlsx"))
    assert r["ok"], r["errors"]
    thanh_vien = api.get_danh_sach_clb("a")["data"]["thanh_vien"]
    dau, dong = _dong_du_lieu(_o(r["data"]["path"]), "Mã học sinh")
    assert dau[2] == "Lớp"
    assert sorted(d[0] for d in dong) == sorted(m["student_id"] for m in thanh_vien)


def test_xuat_theo_ma_co_tim_va_lop(api, tmp_path):
    _nap(api)
    r = api.export_bang_dang_xem("ma", "Em 4", str(tmp_path / "m.xlsx"))
    assert r["ok"], r["errors"]
    dau, dong = _dong_du_lieu(_o(r["data"]["path"]), "Mã học sinh")
    assert dau[2] == "Lớp" and [d[0] for d in dong] == ["HS004"] and dong[0][2] == "10A1"


def test_xuat_chua_co_lop(api, tmp_path):
    _nap(api)
    r = api.export_bang_dang_xem("lop", "", str(tmp_path / "x.xlsx"))
    assert r["ok"], r["errors"]
    _, dong = _dong_du_lieu(_o(r["data"]["path"]), "Mã học sinh")
    assert [d[0] for d in dong] == ["HS006"]


def test_chua_chay_thi_tu_choi_va_kieu_la_thi_loi(api, tmp_path):
    r = api.export_bang_dang_xem("ma", "", str(tmp_path / "k.xlsx"))
    assert not r["ok"] and r["errors"][0]["code"] == "xuat_chua_co_ket_qua"
    _nap(api)
    r = api.export_bang_dang_xem("la", "", str(tmp_path / "k2.xlsx"))
    assert not r["ok"] and not os.path.exists(str(tmp_path / "k2.xlsx"))


def test_khong_ghi_de_tep_co_san(api, tmp_path):
    _nap(api)
    p = str(tmp_path / "t.xlsx")
    a = api.export_bang_dang_xem("ma", "", p)
    b = api.export_bang_dang_xem("ma", "", p)
    assert a["ok"] and b["ok"] and a["data"]["path"] != b["data"]["path"]


def test_xuat_theo_thu_tu_man_hinh_thu_tu(api, tmp_path):
    """T3-L4: `thu_tu` = mã em theo thứ tự đang hiện trên màn hình; tệp xuất đi đúng thứ tự đó
    (mã không có trong danh sách xếp cuối, giữ thứ tự cũ)."""
    _nap(api)
    thu_tu = ["HS005", "HS003", "HS001"]
    r = api.export_bang_dang_xem("ma", "", str(tmp_path / "t.xlsx"), thu_tu)
    assert r["ok"], r["errors"]
    _, dong = _dong_du_lieu(_o(r["data"]["path"]), "Mã học sinh")
    ma = [d[0] for d in dong]
    assert ma[:3] == thu_tu and ma[3:] == ["HS002", "HS004", "HS006"], ma
    r2 = api.export_bang_dang_xem("ma", "", str(tmp_path / "u.xlsx"))
    _, dong2 = _dong_du_lieu(_o(r2["data"]["path"]), "Mã học sinh")
    assert [d[0] for d in dong2] == sorted(d[0] for d in dong2)
