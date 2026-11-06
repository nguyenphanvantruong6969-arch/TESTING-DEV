"""T4M-DO: bộ đo mô phỏng có / không bài thi tuyển (du_lieu_test/do_t4m_thi.py).

Khoá: kết quả tất định với hạt giống cố định; điều kiện A (không điểm thi) trùng khít từng byte với
`PipelineAPI.run_pipeline` trên CSDL không có điểm; điều kiện B trùng khít với CSDL đầy đủ; không có cặp
phá vỡ; tài liệu sinh ra gắn nhãn MÔ PHỎNG ở mọi tiêu đề bảng và không có phần nhận xét.
"""

import os
import re
import sqlite3
import sys
import tempfile

import pytest

pytest.importorskip("openpyxl")

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ("mau_forms_thi_clb", "du_lieu_test"):
    sys.path.insert(0, os.path.join(GOC, p))

import bieu_mau as bm  # noqa: E402
import do_t4m_thi as dt  # noqa: E402
import rbda_priority_pipeline as loi  # noqa: E402

BO_NHO = [("30 hs", 30, 20261104)]


@pytest.fixture(scope="module")
def bo():
    with tempfile.TemporaryDirectory(prefix="t_do_t4m_") as tam:
        yield dt.dung_bo(40, 20261104, tam)


def _dong_db(duong_db):
    con = sqlite3.connect(duong_db)
    try:
        return sorted(con.execute(
            "SELECT student_id, buoi, club_id, round_num, matched_tier, rank_in_student_pref "
            "FROM match_results").fetchall(), key=lambda r: (r[0], r[1]))
    finally:
        con.close()


def _dong_kq(kq):
    return sorted(kq.cac_dong_ket_qua(), key=lambda r: (r[0], r[1]))


def test_dieu_kien_a_trung_khit_pipeline_khong_diem(bo):
    """A = đường chạy thường trên CSDL đã xoá hết điểm thi."""
    con = sqlite3.connect(bo["db"])
    con.execute("DELETE FROM club_scores")
    con.commit()
    con.close()
    r = bo["api"].run_pipeline(seed=5)
    assert r["ok"], r["errors"]
    kq, pha_vo, _g = dt.chay_mot_lan(bo, "A", 5)
    assert pha_vo == 0
    assert _dong_kq(kq) == _dong_db(bo["db"])


def test_dieu_kien_b_trung_khit_pipeline_day_du():
    with tempfile.TemporaryDirectory(prefix="t_do_t4m_b_") as tam:
        b = dt.dung_bo(40, 20261104, tam)
        r = b["api"].run_pipeline(seed=7)
        assert r["ok"], r["errors"]
        kq, pha_vo, _g = dt.chay_mot_lan(b, "B", 7)
        assert pha_vo == 0
        assert _dong_kq(kq) == _dong_db(b["db"])


def test_hai_dieu_kien_khac_nhau_va_a_phu_thuoc_seed(bo):
    """A không được suy biến (bỏ nhầm danh sách dự tuyển làm kết quả không còn phụ thuộc seed)."""
    a1 = dt.chay_mot_lan(bo, "A", 1)[0].assignment
    a2 = dt.chay_mot_lan(bo, "A", 2)[0].assignment
    b1 = dt.chay_mot_lan(bo, "B", 1)[0].assignment
    assert a1 != a2
    assert a1 != b1
    assert sum(1 for x in a1.values() for c in x.values() if c) > 0


def test_tat_dinh_cung_hat_giong_cung_so(tmp_path):
    def chay():
        dong, tb, tt = dt.chay_luoi(BO_NHO, so_seed=2)
        for d in dong:
            d.pop("giay")
        return dong, tb, tt
    assert chay() == chay()


def test_khong_co_cap_pha_vo_va_chi_so_hop_ly():
    dong, tb, tt = dt.chay_luoi(BO_NHO, so_seed=2)
    assert len(dong) == 4 and len(tt) == 1
    assert all(d["cap_pha_vo"] == 0 for d in dong)
    for d in dong:
        assert 0 <= d["nv1"] <= d["nv3"] <= 100
        assert d["khong_xep"] >= 0
        assert (d["tang1_top"] is None) == (d["dieu_kien"] == "A")
    assert {d["buoi"] for d in tb} and all(d["chua_xep"] >= 0 for d in tb)


def test_nhom_diem_cao_tinh_ca_hoa_diem():
    assert dt._nhom_diem_cao({"a": 9, "b": 8, "c": 8, "d": 1}, 2) == {"a", "b", "c"}
    assert dt._nhom_diem_cao({"a": 9, "b": 8}, 5) == {"a", "b"}
    assert dt._nhom_diem_cao({}, 3) == set()


def test_main_nhanh_ghi_tai_lieu_co_nhan_mo_phong(tmp_path):
    md = tmp_path / "do.md"
    ra = tmp_path / "ra"
    assert dt.main(["--nhanh", "--so-seed", "1", "--ra", str(ra), "--tai-lieu", str(md)]) == 0
    assert sorted(os.listdir(ra)) == ["t4m_theo_buoi.csv", "t4m_tung_lan.csv"]
    nd = md.read_text(encoding="utf-8")
    tieu_de_bang = [m for m in re.findall(r"^## \d+\. (.+)$", nd, flags=re.M) if not m.startswith(("Phương pháp",))]
    bang = [t for t in tieu_de_bang if not t.startswith("Tham số")]
    assert len(bang) >= 5 and all("MÔ PHỎNG" in t for t in bang)
    assert "MÔ PHỎNG" in re.search(r"^## \d+\. Tham số.+$", nd, flags=re.M).group(0)
    assert "python du_lieu_test/do_t4m_thi.py" in nd
    assert not re.search(r"^## .*(Nhận xét|Kết luận|Diễn giải)", nd, flags=re.M)


def test_nhanh_khong_duoc_ghi_de_ket_qua_day_du(capsys):
    assert dt.main(["--nhanh"]) == 2


def test_dieu_kien_b_chi_clb_co_de_thi_la_tang_1(bo):
    """Đúng các CLB có `de_thi` mới có điểm (Tầng 1) trong đầu vào của B; A không có điểm nào."""
    co_de = {c["club_id"] for c in bm.doc_de_thi()["cau_lac_bo"] if c["de_thi"]}
    assert 0 < len(co_de) < len(bo["du_lieu"][1])
    _s, _c, diem_b, uv_b, _n = dt._dau_vao(bo["du_lieu"], "B")
    _s, _c, diem_a, uv_a, _n = dt._dau_vao(bo["du_lieu"], "A")
    assert {c for c, m in diem_b.items() if m} == co_de
    assert not any(diem_a.values()) and uv_a == uv_b
    # Tầng 1 thật sự đứng trước Tầng 2 ở CLB có đề, và CLB không đề chỉ có Tầng 2.
    stb = loi.generate_stb_lottery(list(bo["du_lieu"][0]), seed=1)
    for cid in bo["du_lieu"][1]:
        thu_tu = loi.compute_club_priority(cid, uv_b.get(cid, []), diem_b.get(cid, {}), stb)
        co_diem = [s for s in thu_tu if s in diem_b.get(cid, {})]
        assert (cid in co_de) == bool(co_diem) or not uv_b.get(cid)
        assert thu_tu[:len(co_diem)] == co_diem
    # Bảng 2 dùng đúng con số này.
    tt = dt.chay_luoi(BO_NHO, so_seed=1)[2][0]
    assert tt["n_clb_thi"] == len(co_de) and tt["n_clb"] == 15
