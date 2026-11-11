"""GAP-13 (V§8.8; Erdil & Ergin 2008): chu trình cải thiện ổn định CHỈ vượt thứ tự bốc thăm, chế độ ĐO (không ghi gì,
nhãn "không bảo đảm ổn định"). Dữ liệu là dữ liệu MÔ PHỎNG."""
import random

import cau_hinh_ws as ch
import fa_vong_doi_cho as vd
from _fa import dung_fa_clb, dung_hs_fa, ma
from test_fa_gap1_diem_danh import api_ws  # noqa: F401 (fixture)


def test_hoan_doi_hai_em_bang_khoa():
    asg = {"a": "X", "b": "Y"}
    prefs = {"a": ["Y", "X"], "b": ["X", "Y"]}
    khoa = {"X": {"a": (1, -30), "b": (1, -30)}, "Y": {"a": (1, -60), "b": (1, -60)}}
    ct = vd.tim_chu_trinh(asg, prefs, khoa)
    assert sorted(ct) == [("a", "X", "Y"), ("b", "Y", "X")]
    moi, ds = vd.chay_chu_trinh(asg, prefs, khoa)
    assert moi == {"a": "Y", "b": "X"} and len(ds) == 1
    assert asg == {"a": "X", "b": "Y"}                                    # không sửa đầu vào


def test_khong_vuot_em_co_khoa_tot_hon():
    """a và b muốn đổi chỗ, nhưng c (điểm cao hơn a ở Y) cũng muốn Y: a không được vượt c -> không có chu trình."""
    asg = {"a": "X", "b": "Y", "c": "Z"}
    prefs = {"a": ["Y", "X"], "b": ["X", "Y"], "c": ["Y", "Z"]}
    khoa = {"X": {"a": (1, -30), "b": (1, -30)}, "Y": {"a": (1, -5), "b": (1, -9), "c": (1, -8)},
            "Z": {"c": (1, 0)}}
    assert vd.tim_chu_trinh(asg, prefs, khoa) == []
    assert vd.chay_chu_trinh(asg, prefs, khoa) == (asg, [])


def _da(prefs, cap, khoa, stb):
    """DA đề xuất phía học sinh, ưu tiên chặt (khoá thô, bốc thăm) — chỉ để dựng ca thử."""
    tu_do, asg, ke = sorted(prefs), {}, {s: 0 for s in prefs}
    giu = {c: [] for c in cap}
    while tu_do:
        s = tu_do.pop(0)
        if ke[s] >= len(prefs[s]):
            asg[s] = None
            continue
        c = prefs[s][ke[s]]
        ke[s] += 1
        giu[c].append(s)
        giu[c].sort(key=lambda x: (khoa[c][x], stb[x]))
        if len(giu[c]) > cap[c]:
            tu_do.append(giu[c].pop())
    for c, ds in giu.items():
        for s in ds:
            asg[s] = c
    return {s: asg.get(s) for s in prefs}


def _hang(prefs, s, c):
    return prefs[s].index(c) if c in prefs[s] else len(prefs[s])


def test_ngau_nhien_van_on_dinh_theo_khoa_tho_va_ai_doi_cung_loi():
    r = random.Random(13)
    so_doi = 0
    for _ in range(200):
        clbs = ["C%d" % i for i in range(r.randint(2, 4))]
        hs = ["s%d" % i for i in range(r.randint(3, 7))]
        cap = {c: r.randint(1, 2) for c in clbs}
        prefs = {s: r.sample(clbs, r.randint(1, len(clbs))) for s in hs}
        khoa = {c: {s: (r.randint(0, 1), -r.choice((0, 10, 30))) for s in hs} for c in clbs}
        stb = {s: i for i, s in enumerate(r.sample(hs, len(hs)))}
        asg = _da(prefs, cap, khoa, stb)
        moi, ds = vd.chay_chu_trinh(asg, prefs, khoa)
        so_doi += len(ds)
        for c in clbs:
            assert sum(1 for s in hs if moi[s] == c) == sum(1 for s in hs if asg[s] == c)
        for s in hs:
            assert _hang(prefs, s, moi[s]) <= _hang(prefs, s, asg[s])          # không ai thiệt
            for c in prefs[s]:
                if _hang(prefs, s, c) < _hang(prefs, s, moi[s]):              # s muốn c hơn chỗ mới
                    assert not any(moi[t] == c and khoa[c][s] < khoa[c][t] for t in hs), (s, c)
    assert so_doi > 0                                                         # có ca thật sự đổi chỗ


def _dung(api, bat=True):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True, "fa_vong_doi_cho": bat}})
    dung_fa_clb(api, X=(1, "GIOI_HAN"), Y=(1, "GIOI_HAN"), T=(9, "TU_DO"))
    dung_hs_fa(api, "a", "b", nv={"a": ["X", "Y", "T"], "b": ["X", "Y", "T"]})


def test_co_mac_dinh_tat_can_fa_va_api_chi_doc(api_ws):  # noqa: F811
    assert ch.MAC_DINH_TRUONG_HOC["rules"]["fa_vong_doi_cho"] is False
    ra = api_ws.update_workspace_config({"rules": {"fa_vong_doi_cho": True}})
    assert ma(ra["errors"]) == ["fa_tinh_nang_can_fa"]
    _dung(api_ws, bat=False)
    assert api_ws.get_vong_doi_cho()["data"] == {"bat": False}
    _dung(api_ws)
    assert api_ws.run_pipeline(seed=2)["ok"]
    with api_ws._ket_noi_doc() as cur:
        truoc = (cur.execute("SELECT * FROM match_results ORDER BY student_id, buoi").fetchall(),
                 cur.execute("SELECT COUNT(*) FROM fa_dieu_chinh").fetchone()[0])
    kq = api_ws.get_vong_doi_cho()
    assert kq["ok"], kq
    d = kq["data"]
    assert d["bat"] is True and d["nhan"] == "không bảo đảm ổn định"
    assert isinstance(d["chu_trinh"], list)
    assert d["so_em_loi"] == len({x["student_id"] for c in d["chu_trinh"] for x in c})
    with api_ws._ket_noi_doc() as cur:
        sau = (cur.execute("SELECT * FROM match_results ORDER BY student_id, buoi").fetchall(),
               cur.execute("SELECT COUNT(*) FROM fa_dieu_chinh").fetchone()[0])
    assert sau == truoc


def test_bang_mo_phong_che_do_do():
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "du_lieu_test"))
    import mo_phong_fa_daa as mp
    kq = mp.vong_doi_cho_theo_loai(n=40, so_seed=2)["vong_doi_cho_theo_loai"]
    assert [d["hanh_vi"] for d in kq] == list(mp.HANH_VI_DAY_DU)
    assert all(d["che_do"] == "không bảo đảm ổn định" and d["nhan"] == "SỐ LIỆU MÔ PHỎNG" for d in kq)
    assert all(0 <= d["pt_em_loi"] <= 100 for d in kq)
    assert mp.vong_doi_cho_theo_loai(n=40, so_seed=2)["vong_doi_cho_theo_loai"] == kq
