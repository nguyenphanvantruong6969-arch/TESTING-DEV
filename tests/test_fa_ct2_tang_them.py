"""FA-CT2: "được thêm X chỗ thì thêm vào CLB nào" (`fa_daa.goi_y_tang_them`) và tệp cho giáo viên
`chia_cho_theo_nhu_cau.xlsx` (`export_chia_cho`). Chỉ báo cáo, chỉ đọc app.db. Dữ liệu MÔ PHỎNG.

Ví dụ tay: chỗ hiện tại 10/10/10, nhu cầu 18/13/4 -> thừa cầu 8/3/0. Thêm 6 chỗ, mỗi lần một chỗ cho
CLB còn thừa cầu nhiều nhất: A 8->7->6->5->4->3 (5 chỗ), rồi A 3 = B 3, hoà: NV1 A 18 > B 13 -> A. Kết quả A 6, B 0.
Trần 13 ở A: A nhận 3 (10 -> 13), 3 chỗ còn lại cho B.
"""
import base64
import hashlib
import random

import pytest
from openpyxl import load_workbook

import fa_daa
from _fa import bat_fa, dung_fa_clb, dung_hs_fa, giu_cho, ma


def _r(cid, nv1, cap, loai="GIOI_HAN", dat=None, buoi="b1"):
    return {"buoi": buoi, "club_id": cid, "ten": cid, "loai": loai, "capacity": cap, "nv1": nv1,
            "so_ghi": nv1, "so_dat_san": dat, "so_giu_cho": 0}


def _tv(ra):
    return {r["club_id"]: r["them_vao"] for r in ra}


def test_vi_du_tay_va_tran():
    rows = [_r("A", 18, 10), _r("B", 13, 10), _r("C", 4, 10)]
    ra = fa_daa.goi_y_tang_them(rows, 6, {})
    assert _tv(ra) == {"A": 6, "B": 0, "C": 0} and ra[0]["du"] == 0
    assert {r["club_id"]: r["capacity_moi"] for r in ra} == {"A": 16, "B": 10, "C": 10}
    ra = fa_daa.goi_y_tang_them(rows, 6, {"A": 13})                 # trần 13: A nhận 3, B nhận 3
    assert _tv(ra) == {"A": 3, "B": 3, "C": 0}
    ra = fa_daa.goi_y_tang_them(rows, 20, {})                       # thừa cầu chỉ 11 -> dư 9
    assert _tv(ra) == {"A": 8, "B": 3, "C": 0} and all(r["du"] == 9 for r in ra)
    ra = fa_daa.goi_y_tang_them([_r("T", 99, 5, loai="TU_DO"), _r("S", 30, 10, loai="TUYEN_CHON", dat=12)], 9, {})
    assert _tv(ra) == {"T": 0, "S": 2} and ra[0]["du"] == 7          # S: min(30, 12) - 10 = 2


@pytest.mark.parametrize("seed", range(50))
def test_ngau_nhien_tong_tran_chi_tang(seed):
    rng = random.Random(seed)
    rows, gh = [], {}
    for i in range(rng.randint(1, 8)):
        cid = "C%d" % i
        loai = rng.choice(["GIOI_HAN", "TUYEN_CHON", "TU_DO"])
        rows.append(_r(cid, rng.randint(0, 60), rng.randint(1, 40), loai=loai,
                       dat=rng.randint(0, 60) if loai == "TUYEN_CHON" else None))
        if rng.random() < 0.4:
            gh[cid] = rng.randint(1, 50)
    them = rng.randint(0, 80)
    ra = fa_daa.goi_y_tang_them(rows, them, gh)
    du = ra[0]["du"]
    assert sum(r["them_vao"] for r in ra) == them - du and du >= 0
    for r in ra:
        assert r["them_vao"] >= 0 and r["capacity_moi"] == r["capacity"] + r["them_vao"]
        if r["them_vao"]:
            d = min(r["nv1"], r["so_dat_san"]) if r["loai"] == "TUYEN_CHON" else r["nv1"]
            assert r["loai"] != "TU_DO" and d > r["capacity"]
            assert r["capacity_moi"] <= d and r["capacity_moi"] <= gh.get(r["club_id"], 10 ** 9)
    truoc = {r["club_id"]: {"capacity": r["capacity"], "loai": r["loai"]} for r in rows}
    sau = {r["club_id"]: {"capacity": r["capacity_moi"], "loai": r["loai"]} for r in ra}
    assert fa_daa.kiem_chi_tang(truoc, sau) == []


# ---------------------------------------------------------------- tệp cho giáo viên
def _dung(api):
    bat_fa(api)
    dung_fa_clb(api, G=(2, "GIOI_HAN", None, None, None, "Thu2"), S=(2, "TUYEN_CHON", 5, None, None, "Thu2"),
                T=(50, "TU_DO", None, None, None, "Thu2"), H=(3, "GIOI_HAN", None, None, None, "Thu3"),
                K=(3, "GIOI_HAN", None, None, None, "Thu3"))
    nv = {"s1": ["G", "T", "H"], "s2": ["G", "T", "H"], "s3": ["G", "T", "H"], "s4": ["S", "G", "K"],
          "s5": ["S", "T", "H"], "s6": ["T", "G", "K"]}
    dung_hs_fa(api, *nv, nv=nv)
    for s in ("s4", "s5"):
        assert api.submit_test_selection(s, ["S"])["ok"]
    assert api.submit_club_scores("S", [{"student_id": "s4", "score": 8}, {"student_id": "s5", "score": 3}])["ok"]
    giu_cho(api, ("K", "s6"))


def _o(path):
    wb = load_workbook(path)
    return wb, [[c for c in row] for ws in wb.worksheets for row in ws.iter_rows(values_only=True)]


def _md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def test_xuat_mot_trang_moi_buoi_khong_co_hoc_sinh_chi_doc(api, tmp_path):
    _dung(api)
    trc = _md5(api.db_path)
    kq = api.export_chia_cho(str(tmp_path / "chia.xlsx"), "", None, 2)
    assert kq["ok"], kq
    assert _md5(api.db_path) == trc                                     # chỉ đọc
    d = kq["data"]
    assert d["path"].endswith("chia.xlsx") and set(d["du_theo_buoi"]) == {"thu_2", "thu_3"}
    wb, o = _o(d["path"])
    assert wb.sheetnames == ["Thứ 2", "Thứ 3"]
    with api._ket_noi_doc() as cur:
        hs = [x for r in cur.execute("SELECT student_id, name FROM students") for x in r]
    van = [str(c) for row in o for c in row if c is not None]
    assert not any(h in v for h in hs for v in van), "có dữ liệu học sinh trong tệp"
    assert any("thầy cô tự quyết" in v for v in van)
    ws = wb["Thứ 2"]
    hang = [r for r in ws.iter_rows(values_only=True)]
    tieu_de = next(r for r in hang if r and r[0] == "Tên CLB")
    bang = {r[0]: dict(zip(tieu_de, r)) for r in hang[hang.index(tieu_de) + 1:] if r and r[0]}
    # Thu2: G nhu cầu 3 (s1..s3), S min(NV1 2, đạt sàn 1) = 1; tổng 4 chỗ -> G 3, S 1. Thêm 2: G thừa cầu 1 -> 1, dư 1.
    assert bang["CLB G"]["Chỗ gợi ý"] == 3 and bang["CLB S"]["Chỗ gợi ý"] == 1
    assert bang["CLB G"]["Chỗ thêm"] == 1 and bang["CLB S"]["Chỗ thêm"] == 0
    assert bang["CLB T"]["Chỗ gợi ý"] in (None, "")
    assert d["du_theo_buoi"]["thu_2"] == {"chia": 0, "them": 1}
    # Thu3: tổng 6, H nhu cầu 4 (s1,s2,s3,s5), K nhu cầu 2 (s4, s6), sàn K = 1 (giữ chỗ 1) -> 4/2.
    b3 = {r[0]: r for r in wb["Thứ 3"].iter_rows(values_only=True) if r and r[0] in ("CLB H", "CLB K")}
    assert b3["CLB H"][tieu_de.index("Chỗ gợi ý")] == 4 and b3["CLB K"][tieu_de.index("Chỗ gợi ý")] == 2


def test_mac_dinh_mot_buoi_tong_va_khong_them(api, tmp_path):
    _dung(api)
    kq = api.export_chia_cho(str(tmp_path / "a.xlsx"), "thu_3", 10)
    assert kq["ok"], kq
    wb, o = _o(kq["data"]["path"])
    assert wb.sheetnames == ["Thứ 3"]
    assert not any(c == "Chỗ thêm" for row in o for c in row)
    assert kq["data"]["du_theo_buoi"] == {"thu_3": {"chia": 0, "them": None}}


def test_tep_nhu_cau_ghi_de_va_ma_la(api, tmp_path):
    _dung(api)
    p = tmp_path / "nhu_cau.csv"
    p.write_text("club_id,nhu_cau\nH,1\nK,5\nZZ,4\n", encoding="utf-8")
    kq = api.export_chia_cho(str(tmp_path / "b.xlsx"), "thu_3", None, None, str(p))
    assert kq["ok"], kq
    assert ma(kq["data"]["canh_bao"]) == ["chia_cho_ma_clb_la"]
    assert kq["data"]["canh_bao"][0]["params"]["club_ids"] == "ZZ"
    wb, _ = _o(kq["data"]["path"])
    hang = list(wb["Thứ 3"].iter_rows(values_only=True))
    tieu_de = next(r for r in hang if r and r[0] == "Tên CLB")
    b = {r[0]: r[tieu_de.index("Chỗ gợi ý")] for r in hang if r and r[0] in ("CLB H", "CLB K")}
    assert b == {"CLB H": 1, "CLB K": 5}
    # Giao diện gửi tệp dạng {ten, base64}; xlsx cũng nhận.
    from openpyxl import Workbook
    wbx = Workbook()
    wbx.active.append(["club_id", "nhu_cau"])
    wbx.active.append(["H", 3])
    wbx.active.append(["K", 3])
    px = tmp_path / "nc.xlsx"
    wbx.save(px)
    kq = api.export_chia_cho(str(tmp_path / "c.xlsx"), "thu_3", None, None,
                             {"ten": "nc.xlsx", "base64": base64.b64encode(px.read_bytes()).decode()})
    assert kq["ok"], kq
    assert kq["data"]["canh_bao"] == []


@pytest.mark.parametrize("tep", ["club_id,nhu_cau\nH,abc\n", "ma,so\nH,1\n", "club_id,nhu_cau\nH,-2\n"])
def test_tep_nhu_cau_sai(api, tmp_path, tep):
    _dung(api)
    p = tmp_path / "x.csv"
    p.write_text(tep, encoding="utf-8")
    assert ma(api.export_chia_cho(str(tmp_path / "x.xlsx"), "", None, None, str(p))["errors"]) == \
        ["chia_cho_tep_nhu_cau_sai"]


@pytest.mark.parametrize("tong,them", [(0, None), (-3, None), ("abc", None), (None, -1), (True, None)])
def test_so_sai(api, tmp_path, tong, them):
    _dung(api)
    assert ma(api.export_chia_cho(str(tmp_path / "x.xlsx"), "", tong, them)["errors"]) == ["chia_cho_so_sai"]


def test_tong_qua_nho_va_fa_tat(api, tmp_path):
    _dung(api)
    assert ma(api.export_chia_cho(str(tmp_path / "x.xlsx"), "thu_3", 1)["errors"]) == ["chia_cho_tong_qua_nho"]
    bat_fa(api, False)
    assert ma(api.export_chia_cho(str(tmp_path / "y.xlsx"))["errors"]) == ["fa_chua_bat"]
