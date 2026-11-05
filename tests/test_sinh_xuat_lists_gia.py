"""T4M-NC GĐ3: bộ sinh tệp xuất "Export to CSV" giả của SharePoint List (mô hình RỘNG).

Một dòng = một (học sinh, ngày); cột NV1..NV3. Dữ liệu hoàn toàn bịa. Test này viết
TRƯỚC bộ sinh (CLAUDE.md, quy tắc 2).
"""

import csv
import importlib.util
import io
import os

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUONG_SINH = os.path.join(GOC, "du_lieu_test", "sinh_xuat_lists_gia.py")
DUONG_HUONG_DAN = os.path.join(GOC, "docs", "he_sinh_thai", "T4M_HUONG_DAN_THU.md")


def _nap():
    spec = importlib.util.spec_from_file_location("sinh_xuat_lists_gia", DUONG_SINH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _doc(duong):
    with open(duong, "rb") as f:
        tho = f.read()
    return tho, list(csv.DictReader(io.StringIO(tho.decode("utf-8-sig"))))


def test_xac_dinh_cung_seed_cung_byte(tmp_path):
    m = _nap()
    a, b, c = (str(tmp_path / n) for n in ("a.csv", "b.csv", "c.csv"))
    m.ghi_csv(a, so_hs=60, seed=7)
    m.ghi_csv(b, so_hs=60, seed=7)
    m.ghi_csv(c, so_hs=60, seed=8)
    assert open(a, "rb").read() == open(b, "rb").read()
    assert open(a, "rb").read() != open(c, "rb").read()


def test_mac_dinh_1500_hoc_sinh_va_so_dong_bang_hs_nhan_ngay(tmp_path):
    m = _nap()
    p = str(tmp_path / "mac_dinh.csv")
    m.ghi_csv(p)
    _, dong = _doc(p)
    assert m.SO_HS_MAC_DINH == 1500
    assert len(m.NGAY) == 5
    assert len(dong) == 1500 * len(m.NGAY) == 7500
    p2 = str(tmp_path / "nho.csv")
    m.ghi_csv(p2, so_hs=37, seed=3)
    assert len(_doc(p2)[1]) == 37 * len(m.NGAY)


def test_utf8_co_bom_va_giu_dau_tieng_viet(tmp_path):
    m = _nap()
    p = str(tmp_path / "bom.csv")
    m.ghi_csv(p, so_hs=30, seed=1)
    tho, dong = _doc(p)
    assert tho.startswith(b"\xef\xbb\xbf")
    assert not tho[3:].startswith(b"\xef\xbb\xbf")
    van_ban = tho.decode("utf-8-sig")
    assert "Thứ" in van_ban
    assert any(ord(ch) > 127 for d in dong for ch in d["HoTen"])


def test_khong_trung_nguyen_vong_trong_mot_dong(tmp_path):
    m = _nap()
    p = str(tmp_path / "trung.csv")
    m.ghi_csv(p, so_hs=400, seed=11)
    _, dong = _doc(p)
    for d in dong:
        nv = [d[c] for c in ("NV1", "NV2", "NV3") if d[c]]
        assert len(nv) == len(set(nv)), d
        # không có ô trống nằm TRƯỚC ô có giá trị (NV2 chỉ có khi có NV1)
        co = [bool(d[c]) for c in ("NV1", "NV2", "NV3")]
        assert co == sorted(co, reverse=True), d


def test_cot_dung_nhu_da_ghi_trong_huong_dan(tmp_path):
    m = _nap()
    p = str(tmp_path / "cot.csv")
    m.ghi_csv(p, so_hs=20, seed=2)
    tho = open(p, "rb").read().decode("utf-8-sig")
    dau = next(csv.reader(io.StringIO(tho)))
    assert dau == m.COT
    assert {"Email", "HoTen", "CoSo", "Khoi", "Lop", "Thu", "NV1", "NV2", "NV3"} <= set(m.COT)
    with open(DUONG_HUONG_DAN, encoding="utf-8") as f:
        huong_dan = f.read()
    for ten in m.COT:
        assert "`%s`" % ten in huong_dan, "cột %s chưa được ghi trong hướng dẫn" % ten


def test_email_gia_co_chu_hoa_nhung_khong_trung_khi_ha_thuong(tmp_path):
    m = _nap()
    p = str(tmp_path / "email.csv")
    m.ghi_csv(p, so_hs=500, seed=5)
    _, dong = _doc(p)
    emails = {d["Email"] for d in dong}
    assert all("@" in e and e.lower().endswith(m.MIEN_GIA) for e in emails)
    assert any(e != e.lower() for e in emails)          # có email viết hoa
    assert len({e.lower() for e in emails}) == 500      # không trùng sau khi hạ chữ thường
    # mỗi email giữ nguyên cách viết ở mọi dòng của em đó
    theo_em = {}
    for d in dong:
        theo_em.setdefault(d["Email"].lower(), set()).add(d["Email"])
    assert all(len(v) == 1 for v in theo_em.values())


def test_co_ngay_trong_va_dong_tieng_nhat_va_khong_dung_du_lieu_that(tmp_path):
    m = _nap()
    p = str(tmp_path / "dac_biet.csv")
    m.ghi_csv(p, so_hs=600, seed=9)
    _, dong = _doc(p)
    trong = [d for d in dong if not (d["NV1"] or d["NV2"] or d["NV3"])]
    assert 0 < len(trong) < len(dong)
    tn = [d for d in dong if d["CapDo"]]
    assert 0 < len(tn) < len(dong) * 0.2
    goi = [d for d in tn if d["Goi"]]
    assert goi and all(not (d["NV1"] or d["NV2"] or d["NV3"]) for d in goi)
    assert {d["Thu"] for d in goi} <= set(m.NGAY_GOI)
    assert {d["Thu"] for d in dong} == set(m.NGAY)
    assert all(d["Email"].lower().endswith(m.MIEN_GIA) for d in dong)
