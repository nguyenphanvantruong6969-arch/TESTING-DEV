"""FA-M3 (TH = chưa thử trên Microsoft thật): bộ chuyển đổi chế độ FA-DAA.

Đường A: tệp List (SharePoint) có WPk / HC_TuChinh / TrangThai. Đường B: Forms đăng ký (FA-M2). Cộng bài thi (điểm
nguyên 0-10 theo D7, NOT_ATTEMPTED, cờ làm quá nhanh theo D9). Dữ liệu MÔ PHỎNG.
"""
import copy
import os
import sys

import openpyxl
import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))
sys.path.insert(0, GOC)

import bieu_mau as bm  # noqa: E402
import chuyen_forms_sang_phan_mem as cv  # noqa: E402
import so_nhap  # noqa: E402

TU_DO = {"clb_nhiepanh"}
LOAI = {"clb_covua": so_nhap.TUYEN_CHON, "clb_vanhoc": so_nhap.GIOI_HAN, "clb_nhiepanh": so_nhap.TU_DO}


@pytest.fixture
def de():
    return bm.doc_de_thi()


# ---------------------------------------------------------------- D7 và D9
@pytest.mark.parametrize("diem,toi_da,mong", [(0, 10, 0), (10, 10, 10), (5, 10, 5), (1, 3, 3), (1, 4, 3),
                                              (3, 4, 8), (5, 12, 4), (7, 12, 6), (1.5, 3, 5)])
def test_quy_diem_10_lam_tron_nua_len(diem, toi_da, mong):
    assert cv.quy_diem_10(diem, toi_da) == mong
    assert type(cv.quy_diem_10(diem, toi_da)) is int


def test_co_nhanh_qua_duoi_mot_phan_ba_trung_vi():
    t = {"a": 600, "b": 620, "c": 610, "d": 150, "e": 200}          # trung vị 600 -> ngưỡng 200 (nghiêm ngặt)
    assert cv.co_nhanh_qua(t) == {"d"}
    assert cv.co_nhanh_qua({"a": 600, "b": 600}) == set()
    assert cv.co_nhanh_qua({}) == set()


# ---------------------------------------------------------------- đường B
def _tep_dang_ky(tmp_path, de, dong, ten="dk.xlsx", buoi="thu_2"):
    phan = bm.cac_phan_fa(de, buoi)
    tieu = ["ID", "Start time", "Completion time", "Email", "Name"] + [c[0] for _, cs in phan for c in cs]
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(tieu)
    for r in dong:
        o = {"Email": r.get("email", ""), "Name": r.get("ten", "")}
        o[bm.cau_ma_hoc_sinh()] = r["sid"]
        o[bm.cau_ho_ten()] = r.get("ten", "")
        for k in (1, 2, 3):
            o[bm.cau_nguyen_vong_fa(de, buoi, k)] = r.get("nv%d" % k, "")
        o[bm.cau_vang_fa(de, buoi)] = r.get("vang", bm.GIU_MAC_DINH_VANG)
        o[bm.cau_doi_fa(de, buoi)] = r.get("doi", bm.DOI_KHONG)
        wb_row = [o.get(h, "") for h in tieu]
        ws.append(wb_row)
    p = str(tmp_path / ten)
    wb.save(p)
    return p


def _lc(de, club_id):
    return bm.lua_chon_clb(next(c for c in de["cau_lac_bo"] if c["club_id"] == club_id))


def _doc_b(tmp_path, de, dong):
    tieu, cac = cv.doc_tep_xuat(_tep_dang_ky(tmp_path, de, dong))
    return cv.doc_dang_ky_fa_forms(de, tieu, cac, TU_DO)


def test_duong_b_huy_chuong_mac_dinh_theo_thu_tu_va_clb_tu_do_khong_nhan(de, tmp_path):
    ds, cb = _doc_b(tmp_path, de, [dict(sid="HS1", email="a@x.vn", nv1=_lc(de, "clb_nhiepanh"),
                                        nv2=_lc(de, "clb_covua"), nv3=_lc(de, "clb_vanhoc"))])
    h = ds["a@x.vn"]
    assert h["nguyen_vong"]["thu_2"] == ["clb_nhiepanh", "clb_covua", "clb_vanhoc"]
    assert h["wp"]["thu_2"] == {"clb_nhiepanh": None, "clb_covua": 60, "clb_vanhoc": 30}
    assert h["student_id"] == "HS1" and not cb


def test_duong_b_vang_va_doi_bac_dong(de, tmp_path):
    tieu, cac = cv.doc_tep_xuat(_tep_dang_ky(tmp_path, de, [dict(
        sid="HS1", email="a@x.vn", nv1=_lc(de, "clb_covua"), nv2=_lc(de, "clb_vanhoc"),
        nv3=_lc(de, "clb_nhiepanh"), vang=_lc(de, "clb_nhiepanh"), doi=bm.DOI_CO)]))
    ds, cb = cv.doc_dang_ky_fa_forms(de, tieu, cac, set())          # không CLB Tự do: cả ba nhận huy chương
    assert ds["a@x.vn"]["wp"]["thu_2"] == {"clb_nhiepanh": 60, "clb_vanhoc": 30, "clb_covua": 10}
    assert not cb


def test_duong_b_nguyen_vong_trung_bi_bo_va_bao(de, tmp_path):
    ds, cb = _doc_b(tmp_path, de, [dict(sid="HS1", email="a@x.vn", nv1=_lc(de, "clb_covua"),
                                        nv2=_lc(de, "clb_covua"), nv3=_lc(de, "clb_vanhoc"))])
    assert ds["a@x.vn"]["nguyen_vong"]["thu_2"] == ["clb_covua", "clb_vanhoc"]
    assert any("trùng" in nd for _, _, nd in cb)


def test_duong_b_nop_nhieu_lan_lay_phieu_cuoi(de, tmp_path):
    ds, cb = _doc_b(tmp_path, de, [
        dict(sid="HS1", email="a@x.vn", nv1=_lc(de, "clb_covua"), nv2=_lc(de, "clb_vanhoc")),
        dict(sid="HS1", email="a@x.vn", nv1=_lc(de, "clb_vanhoc"), nv2=_lc(de, "clb_covua")),
    ])
    assert ds["a@x.vn"]["nguyen_vong"]["thu_2"] == ["clb_vanhoc", "clb_covua"]
    assert any("CUỐI" in nd for _, _, nd in cb)


def test_duong_b_vang_vao_clb_tu_do_giu_mac_dinh_va_bao(de, tmp_path):
    ds, cb = _doc_b(tmp_path, de, [dict(sid="HS1", email="a@x.vn", nv1=_lc(de, "clb_covua"),
                                        nv2=_lc(de, "clb_vanhoc"), nv3=_lc(de, "clb_nhiepanh"),
                                        vang=_lc(de, "clb_nhiepanh"))])
    assert ds["a@x.vn"]["wp"]["thu_2"]["clb_covua"] == 60
    assert any("Huy chương vàng" in nd for _, _, nd in cb)


def test_duong_b_thieu_cot_nguyen_vong_thi_dung(de):
    with pytest.raises(cv.LoiTepXuat):
        cv.doc_dang_ky_fa_forms(de, ["Email", "Name"], [], TU_DO)


# ---------------------------------------------------------------- đường A
def _csv_list(tmp_path, dong, cot_them=("TrangThai", "HC_TuChinh", "WP1", "WP2", "WP3")):
    p = tmp_path / "list.csv"
    tieu = ["Email", "HoTen", "Thu", "NV1", "NV2", "NV3"] + list(cot_them)
    import csv
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(tieu)
        for r in dong:
            w.writerow([r.get(h, "") for h in tieu])
    return str(p)


def test_duong_a_ban_nhap_bi_bo_va_lan_luu_cuoi_duoc_tinh(de, tmp_path):
    p = _csv_list(tmp_path, [
        dict(Email="a@x.vn", HoTen="A", Thu="Thứ 2", NV1="clb_covua", NV2="clb_vanhoc", TrangThai="SUBMITTED"),
        dict(Email="a@x.vn", HoTen="A", Thu="Thứ 2", NV1="clb_vanhoc", NV2="clb_covua", TrangThai="SUBMITTED"),
        dict(Email="b@x.vn", HoTen="B", Thu="Thứ 2", NV1="clb_covua", TrangThai="DRAFT"),
    ])
    ds, cb = cv.doc_lists(p, de, fa=True)
    assert ds["a@x.vn"]["nguyen_vong"]["thu_2"] == ["clb_vanhoc", "clb_covua"]
    assert "b@x.vn" not in ds or not ds["b@x.vn"]["nguyen_vong"]
    assert any("nháp" in nd for _, _, nd in cb)


def test_duong_a_giu_nhap_khi_nhan_ban_nhap(de, tmp_path):
    p = _csv_list(tmp_path, [dict(Email="b@x.vn", Thu="Thứ 2", NV1="clb_covua", TrangThai="DRAFT")])
    ds, _ = cv.doc_lists(p, de, fa=True, nhan_ban_nhap=True)
    assert ds["b@x.vn"]["nguyen_vong"]["thu_2"] == ["clb_covua"]


def test_duong_a_huy_chuong_mac_dinh_khi_trong_va_khong_tu_chinh(de, tmp_path):
    p = _csv_list(tmp_path, [dict(Email="a@x.vn", Thu="Thứ 2", NV1="clb_nhiepanh", NV2="clb_covua",
                                  NV3="clb_vanhoc", TrangThai="SUBMITTED")])
    ds, _ = cv.doc_lists(p, de, fa=True)
    cv.ap_huy_chuong_duong_a(ds, TU_DO)
    assert ds["a@x.vn"]["wp"]["thu_2"] == {"clb_nhiepanh": None, "clb_covua": 60, "clb_vanhoc": 30}


def test_duong_a_hc_tu_chinh_giu_nguyen_gia_tri_em_dat(de, tmp_path):
    p = _csv_list(tmp_path, [dict(Email="a@x.vn", Thu="Thứ 2", NV1="clb_covua", NV2="clb_vanhoc",
                                  TrangThai="SUBMITTED", HC_TuChinh="Có", WP1="10", WP2="60")])
    ds, _ = cv.doc_lists(p, de, fa=True)
    cv.ap_huy_chuong_duong_a(ds, TU_DO)
    assert ds["a@x.vn"]["wp"]["thu_2"] == {"clb_covua": 10, "clb_vanhoc": 60}


def test_duong_a_co_wp_nhung_khong_co_hc_tu_chinh_van_giu_wp(de, tmp_path):
    """Ô huy chương đã có giá trị thì không ghi đè dù HC_TuChinh trống (em có đặt thật)."""
    p = _csv_list(tmp_path, [dict(Email="a@x.vn", Thu="Thứ 2", NV1="clb_covua", NV2="clb_vanhoc",
                                  TrangThai="SUBMITTED", WP1="30", WP2="60")])
    ds, _ = cv.doc_lists(p, de, fa=True)
    cv.ap_huy_chuong_duong_a(ds, TU_DO)
    assert ds["a@x.vn"]["wp"]["thu_2"] == {"clb_covua": 30, "clb_vanhoc": 60}


def test_che_do_cu_doc_lists_khong_doi(de, tmp_path):
    p = _csv_list(tmp_path, [
        dict(Email="a@x.vn", Thu="Thứ 2", NV1="clb_covua", TrangThai="DRAFT", WP1="5"),
        dict(Email="a@x.vn", Thu="Thứ 2", NV1="clb_vanhoc")], cot_them=("TrangThai", "WP1"))
    ds, _ = cv.doc_lists(p, de)                                    # không fa: giữ dòng ĐẦU, không lọc nháp
    assert ds["a@x.vn"]["nguyen_vong"]["thu_2"] == ["clb_covua"]
    assert "hc" not in ds["a@x.vn"]


# ---------------------------------------------------------------- toàn luồng
def _so_nhap_clb(tmp_path, de):
    clubs = [{"club_id": c["club_id"], "name": c["name"], "capacity": 40 if LOAI.get(c["club_id"]) else 30,
              "reserve_capacity": 0, "reserve_group": "", "buoi": c["buoi"], "loai": LOAI.get(c["club_id"], so_nhap.GIOI_HAN),
              **({"diem_san": 5} if LOAI.get(c["club_id"]) == so_nhap.TUYEN_CHON else {})}
             for c in de["cau_lac_bo"]]
    for c in clubs:
        if c["club_id"] in ("clb_nhiepanh",):
            c["loai"] = so_nhap.TU_DO
    p = str(tmp_path / "clb.xlsx")
    so_nhap.ghi_so_nhap(p, clubs=clubs, giu_cho=[("clb_covua", "HS9")])
    return p


def _tep_thi(tmp_path, de, dong, ten="thi.xlsx"):
    clb_thi = [c for c in bm.clb_co_thi(de) if c["buoi"] == "thu_2"]
    tieu = ["ID", "Start time", "Completion time", "Email", "Name"]
    for clb in clb_thi:
        tieu.append(bm.cau_cong_thi(de, clb, chi_thi=True))
        tieu += [bm.cau_de_thi(clb, i) for i in range(1, len(clb["de_thi"]) + 1)]
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(tieu)
    for email, bat, xong, cac in dong:                  # cac: {club_id: so_cau_dung}
        o = {"Email": email, "Name": email, "Start time": bat, "Completion time": xong}
        for clb in clb_thi:
            td = bm.cau_cong_thi(de, clb, chi_thi=True)
            if clb["club_id"] not in cac:
                o[td] = bm.KHONG
                continue
            o[td] = bm.CO
            for i, cau in enumerate(clb["de_thi"], 1):
                dung = i <= cac[clb["club_id"]]
                o[bm.cau_de_thi(clb, i)] = cau["lua_chon"][cau["dap_an"] if dung else (cau["dap_an"] + 1) % len(cau["lua_chon"])]
        ws.append([o.get(h, "") for h in tieu])
    p = str(tmp_path / ten)
    wb.save(p)
    return p


def test_chuyen_fa_toan_luong_duong_b(de, tmp_path):
    de2 = copy.deepcopy(de)
    de2["diem_moi_cau"] = 3                                         # CLB cờ vua: 5 câu x 3 = 15 điểm, quy về thang 10
    dk = _tep_dang_ky(tmp_path, de2, [
        dict(sid="HS1", email="a@x.vn", nv1=_lc(de, "clb_nhiepanh"), nv2=_lc(de, "clb_covua"), nv3=_lc(de, "clb_vanhoc")),
        dict(sid="HS2", email="b@x.vn", nv1=_lc(de, "clb_covua"), nv2=_lc(de, "clb_vanhoc")),
        dict(sid="HS3", email="c@x.vn", nv1=_lc(de, "clb_covua")),
    ])
    thi = _tep_thi(tmp_path, de2, [("a@x.vn", "2026-11-09 10:00:00", "2026-11-09 10:10:00", {"clb_covua": 4}),
                                   ("b@x.vn", "2026-11-09 10:00:00", "2026-11-09 10:01:40", {"clb_covua": 5}),
                                   ("d@x.vn", "2026-11-09 10:00:00", "2026-11-09 10:09:30", {"clb_covua": 5})])
    ra = tmp_path / "ra"
    kq = cv.chuyen_fa_daa(str(ra), de2, _so_nhap_clb(tmp_path, de2), dang_ky_xlsx=[dk], quiz_xlsx=[thi])
    du = so_nhap.doc_so_nhap(openpyxl.load_workbook(str(ra / cv.TEN_SO)))
    assert not du["loi"], du["loi"]
    hs = {s["student_id"]: s for s in du["students"]}
    assert set(hs) == {"HS1", "HS2", "HS3"}
    a = {n["club_id"]: n for n in hs["HS1"]["nv"]}
    b = {n["club_id"]: n for n in hs["HS2"]["nv"]}
    assert str(a["clb_covua"]["diem"]) in ("8", "8.0")              # 12/15 x 10 = 8
    assert str(b["clb_covua"]["diem"]) in ("10", "10.0")
    assert {c["club_id"]: c.get("loai") for c in du["clubs"]}["clb_covua"] == so_nhap.TUYEN_CHON
    assert du["giu_cho"] == [("clb_covua", "HS9")]
    nd = [x[2] for x in kq["canh_bao"]]
    assert any("NOT_ATTEMPTED" in x and "clb_covua" in x for x in nd)     # HS3 xếp CLB Tuyển chọn, chưa thi
    assert any("quá nhanh" in x for x in nd)                               # HS2: 100 giây, trung vị 350 giây
    assert not any("quỹ" in x for x in nd)                                 # không soát hai quỹ 100 điểm cũ
    assert kq["n_hoc_sinh"] == 3


def test_chuyen_fa_thieu_loai_clb_thi_dung(de, tmp_path):
    dk = _tep_dang_ky(tmp_path, de, [dict(sid="HS1", email="a@x.vn", nv1=_lc(de, "clb_covua"))])
    with pytest.raises(cv.LoiTepXuat):
        cv.chuyen_fa_daa(str(tmp_path / "ra"), de, None, dang_ky_xlsx=[dk])


def test_main_fa_daa_can_so_nhap_clb_va_mot_duong(de, tmp_path):
    with pytest.raises(SystemExit):
        cv.main(["x.xlsx", "--fa-daa", "--ra", str(tmp_path)])
    with pytest.raises(SystemExit):
        cv.main(["x.xlsx", "--so-nhap-clb", "c.xlsx", "--ra", str(tmp_path)])    # --so-nhap-clb chỉ với --fa-daa
