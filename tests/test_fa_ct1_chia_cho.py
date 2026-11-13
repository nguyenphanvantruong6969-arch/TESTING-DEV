"""FA-CT1: chia lại số chỗ MỘT buổi theo nhu cầu (`fa_daa.chia_cho_theo_nhu_cau`) — chỉ là GỢI Ý,
không ghi `clubs.capacity`. Dữ liệu là dữ liệu MÔ PHỎNG.

Ví dụ tay (kiem_nhan 6), kiểm từng số:
- 3 CLB, 30 chỗ, nhu cầu 20/8/2, sàn 1 -> hạn ngạch 30·20/30 = 20, 30·8/30 = 8, 30·2/30 = 2 -> 20/8/2.
- Như trên, trần 15 ở CLB đầu: hạn ngạch 20 > 15 -> cố định 15; còn 15 chỗ chia 8:2 ->
  15·8/10 = 12, 15·2/10 = 3 -> 15/12/3.
- Nhu cầu 29/1/0, sàn 1: CLB thứ ba nhu cầu 0 -> sàn 1; còn 29 chỗ chia 29:1 -> 28,03 và 0,97 < 1 ->
  CLB thứ hai lên sàn 1; còn 28 chỗ cho CLB đầu -> 28/1/1.
"""
import random
from fractions import Fraction

import pytest

import fa_daa


def _r(cid, nv1, cap=10, loai="GIOI_HAN", dat=None, giu=0, buoi="b1"):
    return {"buoi": buoi, "club_id": cid, "ten": cid, "loai": loai, "capacity": cap, "nv1": nv1,
            "so_ghi": nv1, "so_dat_san": dat, "so_giu_cho": giu}


def _goi_y(ra):
    return {r["club_id"]: r["goi_y"] for r in ra}


def test_vi_du_tay():
    rows = [_r("A", 20), _r("B", 8), _r("C", 2)]
    assert _goi_y(fa_daa.chia_cho_theo_nhu_cau(rows, 30, {})) == {"A": 20, "B": 8, "C": 2}
    ra = {r["club_id"]: r for r in fa_daa.chia_cho_theo_nhu_cau(rows, 30, {"A": 15})}
    assert {c: r["goi_y"] for c, r in ra.items()} == {"A": 15, "B": 12, "C": 3}
    assert ra["A"]["ghi_chu"] == "cham_gioi_han" and ra["B"]["ghi_chu"] == ""
    rows = [_r("A", 29), _r("B", 1), _r("C", 0)]
    ra = {r["club_id"]: r for r in fa_daa.chia_cho_theo_nhu_cau(rows, 30, {})}
    assert {c: r["goi_y"] for c, r in ra.items()} == {"A": 28, "B": 1, "C": 1}
    assert ra["C"]["ghi_chu"] == "khong_nhu_cau"
    assert ra["A"]["chenh"] == 18 and ra["B"]["chenh"] == -9


def _ngau_nhien(rng, n=None):
    n = n or rng.randint(1, 8)
    rows, gh = [], {}
    for i in range(n):
        cid = "C%02d" % i
        loai = rng.choice(["GIOI_HAN", "TUYEN_CHON"])
        nv1 = rng.randint(0, 60)
        rows.append(_r(cid, nv1, cap=rng.randint(1, 40), loai=loai,
                       dat=rng.randint(0, 60) if loai == "TUYEN_CHON" else None,
                       giu=rng.choice([0, 0, 0, rng.randint(0, 5)])))
        if rng.random() < 0.3:
            gh[cid] = rng.randint(max(1, rows[-1]["so_giu_cho"]), 40)
    return rows, gh


def _d(r):
    return min(r["nv1"], r["so_dat_san"]) if r["loai"] == "TUYEN_CHON" else r["nv1"]


def _san(r):
    return max(1, r["so_giu_cho"])


@pytest.mark.parametrize("seed", range(60))
def test_tong_va_can(seed):
    rng = random.Random(seed)
    rows, gh = _ngau_nhien(rng)
    tong = rng.randint(sum(_san(r) for r in rows), 300)
    ra = fa_daa.chia_cho_theo_nhu_cau(rows, tong, gh)
    du = ra[0]["du"]
    assert du >= 0 and all(r["du"] == du for r in ra)
    assert sum(r["goi_y"] for r in ra) == tong - du
    for r in ra:
        assert _san(r) <= r["goi_y"] and (r["club_id"] not in gh or r["goi_y"] <= gh[r["club_id"]])
        assert r["goi_y"] >= r["so_giu_cho"]
    if du:                                       # chỗ thừa chỉ khi mọi CLB có nhu cầu đã chạm trần
        co_nhu_cau = any(_d(x) for x in ra)
        for r in ra:
            if _d(r) > 0 or not co_nhu_cau:
                assert r["goi_y"] == gh[r["club_id"]]


@pytest.mark.parametrize("seed", range(40))
def test_ti_le_khi_khong_can_nao_rang_buoc(seed):
    rng = random.Random(1000 + seed)
    rows = [_r("C%d" % i, rng.randint(5, 50)) for i in range(rng.randint(2, 7))]
    tong = sum(r["nv1"] for r in rows) * rng.randint(1, 3) + rng.randint(0, 9)
    ra = fa_daa.chia_cho_theo_nhu_cau(rows, tong, {})
    tong_d = sum(r["nv1"] for r in rows)
    for r in ra:
        q = Fraction(tong * r["nv1"], tong_d)
        if q > 1:                                # sàn 1 không ràng buộc
            assert abs(r["goi_y"] - q) < 1
    assert sum(r["goi_y"] for r in ra) == tong


def test_tat_dinh_khi_doi_thu_tu():
    rng = random.Random(7)
    rows, gh = _ngau_nhien(rng, n=7)
    tong = 150
    a = fa_daa.chia_cho_theo_nhu_cau(rows, tong, gh)
    rows2 = list(reversed(rows))
    gh2 = dict(reversed(list(gh.items())))
    b = fa_daa.chia_cho_theo_nhu_cau(rows2, tong, gh2)
    assert a == b
    # Hoà phần lẻ: CLB nhu cầu lớn hơn được chỗ dư trước, rồi club_id.
    ra = _goi_y(fa_daa.chia_cho_theo_nhu_cau([_r("B", 1), _r("A", 1), _r("C", 1)], 4, {}))
    assert ra == {"A": 2, "B": 1, "C": 1}


def test_giu_cho_va_tong_qua_nho():
    rows = [_r("A", 0, giu=6), _r("B", 40)]
    ra = {r["club_id"]: r for r in fa_daa.chia_cho_theo_nhu_cau(rows, 20, {})}
    assert ra["A"]["goi_y"] == 6 and ra["B"]["goi_y"] == 14
    rows = [_r("A", 1, giu=3), _r("B", 40)]
    ra = {r["club_id"]: r for r in fa_daa.chia_cho_theo_nhu_cau(rows, 20, {})}
    assert (ra["A"]["goi_y"], ra["A"]["ghi_chu"]) == (3, "san_giu_cho")
    with pytest.raises(fa_daa.LoiChiaCho) as e:
        fa_daa.chia_cho_theo_nhu_cau([_r("A", 5, giu=8), _r("B", 5, giu=4)], 10, {})
    assert e.value.loi == {"code": "chia_cho_tong_qua_nho",
                           "params": {"buoi": "b1", "tong": 10, "can": 12}}


def test_tu_do_khong_doi_nhu_cau_ghi_de_va_tuyen_chon():
    rows = [_r("F", 99, cap=500, loai="TU_DO"), _r("S", 30, loai="TUYEN_CHON", dat=10), _r("G", 10)]
    ra = {r["club_id"]: r for r in fa_daa.chia_cho_theo_nhu_cau(rows, 40, {})}
    assert ra["F"]["goi_y"] is None and ra["F"]["chenh"] is None and ra["F"]["capacity"] == 500
    assert ra["S"]["goi_y"] == 20 and ra["G"]["goi_y"] == 20            # S: min(30, 10) = 10
    ra = _goi_y(fa_daa.chia_cho_theo_nhu_cau(rows, 40, {}, nhu_cau={"S": 30, "G": 10}))
    assert ra == {"F": None, "S": 30, "G": 10}
    assert rows[1] == _r("S", 30, loai="TUYEN_CHON", dat=10)             # không sửa đầu vào


def test_moi_nhu_cau_bang_0_chia_deu_va_cho_thua():
    ra = _goi_y(fa_daa.chia_cho_theo_nhu_cau([_r("A", 0), _r("B", 0), _r("C", 0)], 10, {}))
    assert ra == {"A": 4, "B": 3, "C": 3}
    ra = fa_daa.chia_cho_theo_nhu_cau([_r("A", 5), _r("B", 5)], 30, {"A": 8, "B": 12})
    assert _goi_y(ra) == {"A": 8, "B": 12} and ra[0]["du"] == 10
