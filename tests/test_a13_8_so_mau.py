"""A13.8 — sổ mẫu: cột Điểm quyết tâm chỉ khi workspace BẬT ĐƯỢC tính năng (lỗi 2.6); chỗ chèn ghi chú
trong "Hướng dẫn" là dòng đánh dấu, không dò chữ "Bước 5." (lỗi 2.8); hai bản làm tròn phần dư lớn
nhất cho cùng kết quả (lỗi 2.7). Dữ liệu MÔ PHỎNG."""

import importlib.util
import io
import os
import random

import pytest

openpyxl = pytest.importorskip("openpyxl")

import so_nhap  # noqa: E402
from api_quan_ly import phong_theo_ti_le  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEN_COT_W = "Điểm quyết tâm"


def _hang_2(cfg=None, **kw):
    b = io.BytesIO()
    so_nhap.ghi_so_nhap(b, [], [], cfg=cfg, **kw)
    wb = openpyxl.load_workbook(io.BytesIO(b.getvalue()))
    huong = [str(r[0].value) for r in wb["Hướng dẫn"].iter_rows() if r[0].value]
    ten_hs = next(n for n in wb.sheetnames if n.startswith("2."))
    return [c.value for c in wb[ten_hs][2]], huong


# ------------------------------------------------------------------ 2.6

@pytest.mark.parametrize("rules", [
    {"priority": "tier"},
    {"score_scope": "per_person"},
])
def test_workspace_khong_bat_duoc_thi_so_mau_khong_co_cot_w_va_khong_ghi_chu(rules):
    hang, huong = _hang_2({"rules": rules}, luon_co_cot_w=True)
    assert TEN_COT_W not in hang
    assert not any(TEN_COT_W in d for d in huong)


@pytest.mark.parametrize("cfg", [None, {"rules": {"priority": "score"}},
                                 {"rules": {"priority": "score+tier"}}])
def test_workspace_bat_duoc_thi_so_mau_van_co_cot_w_va_ghi_chu(cfg):
    hang, huong = _hang_2(cfg, luon_co_cot_w=True)
    assert hang.count(TEN_COT_W) == hang.count("CLB") > 0
    assert any(TEN_COT_W in d and "CHỈ dùng khi" in d for d in huong)


def test_mac_dinh_khong_co_cot_w():
    hang, _ = _hang_2({"rules": {"priority": "tier"}})
    assert TEN_COT_W not in hang
    hang, _ = _hang_2(None)
    assert TEN_COT_W not in hang


# ------------------------------------------------------------------ 2.8

def _vi_tri(huong, mau):
    return next(i for i, d in enumerate(huong) if d.startswith(mau))


@pytest.mark.parametrize("cfg", [None, {"rules": {"priority": "score"}},
                                 {"labels": {"slot": {"vi": {"l": "dự án", "s": "Dự án",
                                                             "su": "DỰ ÁN"}}}}])
def test_ghi_chu_nam_giua_buoc_4_va_buoc_5_va_dong_trong_van_dung_truoc_buoc_5(cfg):
    _, huong = _hang_2(cfg, luon_co_cot_w=True)
    b4, ghi_chu, b5 = (_vi_tri(huong, "Bước 4."), _vi_tri(huong, "        Cột %s" % TEN_COT_W),
                       _vi_tri(huong, "Bước 5."))
    assert b4 < ghi_chu < b5
    assert so_nhap.CHO_CHEN_GHI_CHU_W not in "\n".join(huong)


def test_dong_danh_dau_nam_truoc_dong_trong_dung_truoc_buoc_5():
    dong = so_nhap.huong_dan(None)
    assert so_nhap.CHO_CHEN_GHI_CHU_W not in dong
    co_dau = so_nhap._huong_dan_co_dau(None)
    i = co_dau.index(so_nhap.CHO_CHEN_GHI_CHU_W)
    assert co_dau[i + 1] == "" and co_dau[i + 2].startswith("Bước 5.")
    assert so_nhap.HUONG_DAN == dong


def test_doi_chu_buoc_5_khong_lam_ghi_chu_roi_xuong_cuoi(monkeypatch):
    """Trước đây dò chữ "Bước 5.": đổi chữ thì ghi chú rơi xuống cuối hướng dẫn, không báo lỗi."""
    co_dau = [d.replace("Bước 5.", "Bước năm.") for d in so_nhap._huong_dan_co_dau(None)]
    monkeypatch.setattr(so_nhap, "_huong_dan_co_dau", lambda cfg=None: list(co_dau))
    dong = so_nhap.huong_dan(None, ghi_chu_cot_w=True)
    ghi_chu = next(i for i, d in enumerate(dong) if d.startswith("        Cột %s" % TEN_COT_W))
    assert ghi_chu < next(i for i, d in enumerate(dong) if d.startswith("Bước năm."))


# ------------------------------------------------------------------ 2.7

def _lam_tron_100_cua_skill():
    duong = os.path.join(GOC, ".claude", "skills", "sinh-du-lieu-clb", "scripts", "sinh_du_lieu.py")
    spec = importlib.util.spec_from_file_location("sinh_du_lieu_skill", duong)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.lam_tron_100


def test_lam_tron_100_cua_skill_trung_phong_theo_ti_le_tren_dau_vao_ngau_nhien():
    lam_tron_100 = _lam_tron_100_cua_skill()
    rnd = random.Random(20261028)
    for _ in range(3000):
        n = rnd.randint(1, 9)
        ma = rnd.sample(["a", "b", "c", "d", "e", "f", "g", "h", "i", "CLB1", "clb2", "Z9"], n)
        tw = {c: rnd.choice([0, 0, 1, 1, 2, 3, 5, 7, 11, 33, 50, 100, 999]) for c in ma}
        if sum(tw.values()) == 0:
            continue
        mong = phong_theo_ti_le(dict(tw))
        assert lam_tron_100(dict(tw)) == mong, tw
        assert sum(mong.values()) == 100
