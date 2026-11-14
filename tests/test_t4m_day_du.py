"""T4M-Q5a/b/c: Top 7, tick chọn thi (tối đa 5 CLB/ngày) và điểm quyết tâm (hai quỹ 100) trong chuỗi Lists -> Sổ nhập.

  Q5a  List có cột THIk: "thi" trong Sổ nhập đi theo ô tick (tick + có bài -> điểm; tick + vắng -> ô "thi";
       có bài mà không tick -> bỏ điểm, báo; tick CLB không đề -> bỏ tick, báo; quá 5 tick/ngày -> giữ 5 đầu).
  Q5b  List có cột WPk: ghi điểm quyết tâm theo từng nguyện vọng; soát hai quỹ (đúng 100) chỉ để BÁO, không sửa.
  Q5c  bộ sinh Lists giả (NV tới 7, THIk, WPk), phiếu Forms giả theo tick, demo_t4m.py --day-du.

Bất biến: List KHÔNG có THIk/WPk thì Sổ nhập và BANG_DIEM y như trước (dấu băm so với bản trước khi đổi đã
chạy tay một lần; ở đây giữ các kiểm tra cấu trúc). Dữ liệu hoàn toàn MÔ PHỎNG.
"""

import copy
import csv
import os
import sys

import pytest

openpyxl = pytest.importorskip("openpyxl")

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))

import bieu_mau as bm  # noqa: E402
import chuyen_forms_sang_phan_mem as cv  # noqa: E402
import demo_t4m  # noqa: E402
import sinh_xuat_lists_gia as lists_gia  # noqa: E402
import so_nhap  # noqa: E402
import tao_mau_forms as tm  # noqa: E402

MIEN = "@truong-gia.example.test"
SO_NV = 7


@pytest.fixture
def de():
    return bm.doc_de_thi()


def nv(club, tick=False, wp=None):
    return (club, tick, wp)


# ------------------------------------------------------------------ dựng tệp giả

def _ghi_lists(duong, hs, de, thi=True, wp=True):
    """hs: [(email, tên, {buổi: [nv(club, tick, wp)]})] -> CSV Lists rộng, NV1..NV7 (+THI1..7, WP1..7)."""
    ten_thu = {b["ma"]: "Thứ " + b["ma"][-1] for b in de["buoi"]}
    tieu = ["Email", "HoTen", "CoSo", "Khoi", "Lop", "Thu"] + ["NV%d" % k for k in range(1, SO_NV + 1)]
    if thi:
        tieu += ["THI%d" % k for k in range(1, SO_NV + 1)]
    if wp:
        tieu += ["WP%d" % k for k in range(1, SO_NV + 1)]
    tieu += ["CapDo", "Goi", "TrangThai", "Created"]
    with open(duong, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\r\n")
        w.writerow(tieu)
        for email, ten, ngay in hs:
            for b in de["buoi"]:
                ds = (ngay.get(b["ma"], []) + [("", "", "")] * SO_NV)[:SO_NV]
                dong = [email, ten, "CS1", 9, "9A1", ten_thu[b["ma"]]] + [x[0] for x in ds]
                if thi:
                    dong += [("Có" if x[1] is True else (x[1] or "")) for x in ds]
                if wp:
                    dong += ["" if x[2] is None else str(x[2]) for x in ds]
                w.writerow(dong + ["", "", "Đã khóa", "2026-11-02T07:00:00Z"])


def _ghi_xuat_thi(de, duong, phieu):
    """phieu: [(email, {club_id: số câu đúng})] -> tệp Forms xuất chỉ-thi (có câu cổng)."""
    tieu = ["ID", "Start time", "Completion time", "Email", "Name"]
    for clb in bm.clb_co_thi(de):
        tieu.append(bm.cau_cong_thi(de, clb, chi_thi=True))
        tieu += [bm.cau_de_thi(clb, i) for i in range(1, len(clb["de_thi"]) + 1)]
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(tieu)
    for n, (email, thi) in enumerate(phieu, 1):
        o = {}
        for clb in bm.clb_co_thi(de):
            g = bm.cau_cong_thi(de, clb, chi_thi=True)
            if clb["club_id"] not in thi:
                o[g] = bm.KHONG
                continue
            o[g] = bm.CO
            for i, cau in enumerate(clb["de_thi"], 1):
                k = cau["dap_an"] if i <= thi[clb["club_id"]] else (cau["dap_an"] + 1) % len(cau["lua_chon"])
                o[bm.cau_de_thi(clb, i)] = cau["lua_chon"][k]
        ws.append([n, None, None, email, "Tên Forms " + str(n)] + [o.get(c) for c in tieu[5:]])
    wb.save(duong)


def _chay(de, tmp_path, hs, phieu, thi=True, wp=True):
    _ghi_lists(str(tmp_path / "lists.csv"), hs, de, thi=thi, wp=wp)
    _ghi_xuat_thi(de, str(tmp_path / "forms.xlsx"), phieu)
    ra = tmp_path / "nap"
    kq = cv.chuyen_chi_thi([str(tmp_path / "forms.xlsx")], str(tmp_path / "lists.csv"), str(ra), de)
    return kq, ra


def _doc_so(ra):
    wb = openpyxl.load_workbook(str(ra / "SO_NHAP_CLB.xlsx"), read_only=True)
    du = so_nhap.doc_so_nhap(wb)
    wb.close()
    assert du["loi"] == [], du["loi"]
    return du


def _hs(du, sid):
    return next(s for s in du["students"] if s["student_id"] == sid)


def _nv(du, sid):
    return {x["club_id"]: x for x in _hs(du, sid)["nv"]}


def _tieu_de_hs(ra):
    wb = openpyxl.load_workbook(str(ra / "SO_NHAP_CLB.xlsx"), read_only=True)
    hang = [[c for c in r] for r in wb["2. Học sinh"].iter_rows(min_row=1, max_row=2, values_only=True)]
    wb.close()
    return hang


E1 = "a1" + MIEN


# ------------------------------------------------------------------ Q5a: tick

def test_q5a_tick_co_bai_thi_thi_nap_diem(de, tmp_path):
    hs = [(E1, "An", {"thu_2": [nv("clb_covua", True), nv("clb_nhiepanh")]})]
    kq, ra = _chay(de, tmp_path, hs, [(E1, {"clb_covua": 3})], wp=False)
    x = _nv(_doc_so(ra), E1)
    assert x["clb_covua"]["thi"] is True and x["clb_covua"]["diem"] != ""
    assert x["clb_nhiepanh"]["thi"] is False
    assert kq["canh_bao"] == []


def test_q5a_tick_ma_vang_thi_ghi_o_thi_chua_co_diem(de, tmp_path):
    hs = [(E1, "An", {"thu_2": [nv("clb_covua", True), nv("clb_vanhoc", True)]})]
    kq, ra = _chay(de, tmp_path, hs, [(E1, {"clb_covua": 2})], wp=False)
    x = _nv(_doc_so(ra), E1)
    assert x["clb_covua"]["diem"] != ""
    assert x["clb_vanhoc"]["thi"] is True and x["clb_vanhoc"]["diem"] == ""      # tick, chưa có bài
    assert kq["canh_bao"] == []                                                    # vắng thi không phải lỗi


def test_q5a_em_khong_co_phieu_nao_van_giu_o_thi_theo_tick(de, tmp_path):
    hs = [(E1, "An", {"thu_2": [nv("clb_covua", True)]}),
          ("a2" + MIEN, "Bình", {"thu_2": [nv("clb_covua", True)]})]
    _kq, ra = _chay(de, tmp_path, hs, [("a2" + MIEN, {"clb_covua": 4})], wp=False)
    x = _nv(_doc_so(ra), E1)
    assert x["clb_covua"]["thi"] is True and x["clb_covua"]["diem"] == ""


def test_q5a_co_bai_thi_nhung_khong_tick_bo_diem_va_bao(de, tmp_path):
    hs = [(E1, "An", {"thu_2": [nv("clb_covua"), nv("clb_vanhoc", True)]})]
    kq, ra = _chay(de, tmp_path, hs, [(E1, {"clb_covua": 4, "clb_vanhoc": 4})], wp=False)
    x = _nv(_doc_so(ra), E1)
    assert x["clb_covua"]["thi"] is False and x["clb_covua"]["diem"] == ""
    assert x["clb_vanhoc"]["diem"] != ""
    bao = [nd for _d, e, nd in kq["canh_bao"] if e == E1]
    assert len(bao) == 1 and "clb_covua" in bao[0] and "tick" in bao[0]
    # điểm VẪN nằm trong BANG_DIEM, cột "Nạp" nói rõ vì sao không nạp
    wb = openpyxl.load_workbook(str(ra / "BANG_DIEM.xlsx"), read_only=True)
    chi_tiet = [r for r in wb["Chi tiết"].iter_rows(min_row=2, values_only=True) if r[2] == "clb_covua"]
    wb.close()
    assert len(chi_tiet) == 1 and chi_tiet[0][-1] == "Không — chưa tick thi"
    assert chi_tiet[0][-2] == 4 * de["diem_moi_cau"]


def test_q5a_tick_clb_khong_co_de_bi_bo_va_bao(de, tmp_path):
    hs = [(E1, "An", {"thu_2": [nv("clb_nhiepanh", True), nv("clb_covua", True)]})]
    kq, ra = _chay(de, tmp_path, hs, [(E1, {"clb_covua": 1})], wp=False)
    x = _nv(_doc_so(ra), E1)
    assert x["clb_nhiepanh"]["thi"] is False
    assert x["clb_covua"]["thi"] is True
    bao = [nd for _d, e, nd in kq["canh_bao"] if e == E1]
    assert len(bao) == 1 and "clb_nhiepanh" in bao[0] and "không có đề thi" in bao[0]


def _de_nhieu_clb(de, them=6):
    d = copy.deepcopy(de)
    mau = next(c for c in d["cau_lac_bo"] if c["club_id"] == "clb_covua")
    for i in range(them):
        c = copy.deepcopy(mau)
        c["club_id"], c["name"] = "clb_x%d" % i, "CLB thêm %d" % i
        d["cau_lac_bo"].append(c)
    return d


@pytest.mark.giu_ma
def test_q5a_qua_nam_tick_mot_ngay_giu_nam_dau_theo_thu_tu_nv(de, tmp_path):
    d = _de_nhieu_clb(de)
    ds = ["clb_x%d" % i for i in range(6)] + ["clb_covua"]          # 7 CLB có đề, đều tick
    hs = [(E1, "An", {"thu_2": [nv(c, True) for c in ds]})]
    kq, ra = _chay(d, tmp_path, hs, [(E1, {"clb_x0": 1})], wp=False)
    x = _nv(_doc_so(ra), E1)
    assert [c for c in ds if x[c]["thi"]] == ds[:5]
    bao = [nd for _d, e, nd in kq["canh_bao"] if e == E1]
    assert len(bao) == 1 and "tối đa 5" in bao[0] and "clb_x5" in bao[0] and "clb_covua" in bao[0]


def test_q5a_tick_khong_co_nv_bao_va_bo(de, tmp_path):
    _ghi_lists(str(tmp_path / "lists.csv"), [(E1, "An", {"thu_2": [nv("clb_covua", True)]})], de)
    # sửa tay: tick ở ô THI3 trong khi NV3 trống
    p = tmp_path / "lists.csv"
    dong = list(csv.reader(open(p, encoding="utf-8-sig", newline="")))
    i_thi3 = dong[0].index("THI3")
    dong[1][i_thi3] = "Có"
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f, lineterminator="\r\n").writerows(dong)
    ds, canh_bao = cv.doc_lists(str(p), de)
    assert ds[E1]["tick"] == {"clb_covua"}
    assert any("THI3" in nd and "NV3 trống" in nd for _d, _e, nd in canh_bao)


def test_q5a_gia_tri_tick_co_khong_la(de, tmp_path):
    hs = [(E1, "An", {"thu_2": [nv("clb_covua", " có "), nv("clb_vanhoc", "Không")]}),
          ("a2" + MIEN, "Bình", {"thu_2": [nv("clb_covua", "abc")]})]
    _ghi_lists(str(tmp_path / "lists.csv"), hs, de)
    ds, canh_bao = cv.doc_lists(str(tmp_path / "lists.csv"), de)
    assert ds[E1]["tick"] == {"clb_covua"}
    assert ds["a2" + MIEN]["tick"] == set()
    bao = [(e, nd) for _d, e, nd in canh_bao]
    assert len(bao) == 1 and bao[0][0] == "a2" + MIEN and "abc" in bao[0][1]


def test_q5a_list_khong_co_cot_thi_giu_hanh_vi_cu(de, tmp_path):
    hs = [(E1, "An", {"thu_2": [nv("clb_covua", True), nv("clb_vanhoc")]})]
    kq, ra = _chay(de, tmp_path, hs, [(E1, {"clb_covua": 3, "clb_vanhoc": 2})], thi=False, wp=False)
    ds, _ = cv.doc_lists(str(tmp_path / "lists.csv"), de)
    assert "tick" not in ds[E1] and "wp" not in ds[E1]
    x = _nv(_doc_so(ra), E1)
    assert x["clb_covua"]["diem"] != "" and x["clb_vanhoc"]["diem"] != ""        # điểm theo bài thi, không theo tick
    tieu = _tieu_de_hs(ra)
    assert "Điểm quyết tâm" not in [c for r in tieu for c in r]
    assert kq["ghi_chu"] == [cv.GHI_CHU_DIEM_QUYET_TAM]


# ------------------------------------------------------------------ Q5b: điểm quyết tâm

def _hs_day_du(wp1=(60, 40), wp2=(100,)):
    """Một em, thu_2: covua + vanhoc đã tick (quỹ 1), nhiepanh không thi (quỹ 2)."""
    return [(E1, "An", {"thu_2": [nv("clb_covua", True, wp1[0]), nv("clb_vanhoc", True, wp1[1]),
                                  nv("clb_nhiepanh", False, wp2[0])]})]


def test_q5b_ghi_diem_quyet_tam_theo_tung_nv_va_giu_nguyen_gia_tri(de, tmp_path):
    kq, ra = _chay(de, tmp_path, _hs_day_du(), [(E1, {"clb_covua": 3})])
    du = _doc_so(ra)
    x = _nv(du, E1)
    assert (x["clb_covua"]["diem_w"], x["clb_vanhoc"]["diem_w"], x["clb_nhiepanh"]["diem_w"]) == ("60", "40", "100")
    assert "Điểm quyết tâm" in [c for r in _tieu_de_hs(ra) for c in r]
    assert kq["canh_bao"] == []
    assert cv.GHI_CHU_DIEM_QUYET_TAM not in kq["ghi_chu"]      # sổ CÓ điểm quyết tâm: không bảo người dùng tắt


def test_q5b_quy_1_khong_du_100_chi_bao_khong_sua(de, tmp_path):
    kq, ra = _chay(de, tmp_path, _hs_day_du(wp1=(60, 30)), [(E1, {"clb_covua": 3})])
    bao = [nd for _d, e, nd in kq["canh_bao"] if e == E1]
    assert len(bao) == 1 and "quỹ 1" in bao[0] and "90" in bao[0] and "100" in bao[0] and "thu_2" in bao[0]
    assert _nv(_doc_so(ra), E1)["clb_vanhoc"]["diem_w"] == "30"            # giá trị KHÔNG bị sửa


def test_q5b_quy_2_khong_du_100_bao(de, tmp_path):
    hs = [(E1, "An", {"thu_2": [nv("clb_covua", True, 100), nv("clb_nhiepanh", False, 80),
                                nv("clb_vanhoc", False, 10)]})]
    kq, _ra = _chay(de, tmp_path, hs, [(E1, {"clb_covua": 3})])
    bao = [nd for _d, e, nd in kq["canh_bao"] if e == E1]
    assert len(bao) == 1 and "quỹ 2" in bao[0] and "90" in bao[0]


def test_q5b_dong_bao_la_dong_cua_dung_ngay(de, tmp_path):
    hs = [(E1, "An", {"thu_4": [nv("clb_robotics", True, 50), nv("clb_khoahoc", True, 40)]})]
    kq, _ra = _chay(de, tmp_path, hs, [(E1, {"clb_robotics": 3})])
    (dong, _e, nd), = [x for x in kq["canh_bao"] if x[1] == E1]
    # dòng 1 là tiêu đề, mỗi em 5 dòng (thu_2..thu_6): thu_4 là dòng 2 + 2 = 4
    assert dong == 4 and "thu_4" in nd


def test_q5b_o_khong_phai_so_nguyen_bo_trong_va_bao(de, tmp_path):
    for sai in ("12.5", "-3", "abc"):
        hs = [(E1, "An", {"thu_2": [nv("clb_covua", True, 70), nv("clb_vanhoc", True, sai),
                                    nv("clb_nhiepanh", False, 100)]})]
        sub = tmp_path / ("s" + str(abs(hash(sai)) % 10 ** 6))
        sub.mkdir()
        kq, ra = _chay(de, sub, hs, [(E1, {"clb_covua": 3})])
        assert _nv(_doc_so(ra), E1)["clb_vanhoc"]["diem_w"] == ""                       # ô để trống
        bao = [nd for _d, e, nd in kq["canh_bao"] if e == E1]
        assert any(sai in nd and "số nguyên" in nd for nd in bao), (sai, bao)


def test_q5b_so_nguyen_dang_thap_phan_khong_nhu_12_0_van_nhan(de, tmp_path):
    kq, ra = _chay(de, tmp_path, _hs_day_du(wp1=("60.0", 40)), [(E1, {"clb_covua": 3})])
    assert _nv(_doc_so(ra), E1)["clb_covua"]["diem_w"] == "60" and kq["canh_bao"] == []


def test_q5b_quy_chi_mot_clb_de_trong_khong_bao(de, tmp_path):
    # quỹ 2 chỉ có nhiepanh: kiosk tự điền 100 trong bộ nhớ (cách A) nên không phải lỗi
    hs = [(E1, "An", {"thu_2": [nv("clb_covua", True, 60), nv("clb_vanhoc", True, 40), nv("clb_nhiepanh")]})]
    kq, _ra = _chay(de, tmp_path, hs, [(E1, {"clb_covua": 3})])
    assert kq["canh_bao"] == []


def test_q5b_quy_rong_khong_kiem(de, tmp_path):
    # mọi CLB đều tick: quỹ 2 rỗng, không cần điểm
    hs = [(E1, "An", {"thu_2": [nv("clb_covua", True, 100)]})]
    kq, _ra = _chay(de, tmp_path, hs, [(E1, {"clb_covua": 3})])
    assert kq["canh_bao"] == []


def test_q5b_quy_hai_clb_de_trong_het_bao_thieu(de, tmp_path):
    hs = [(E1, "An", {"thu_2": [nv("clb_covua", True, 100), nv("clb_vanhoc"), nv("clb_nhiepanh")]})]
    kq, _ra = _chay(de, tmp_path, hs, [(E1, {"clb_covua": 3})])
    bao = [nd for _d, e, nd in kq["canh_bao"] if e == E1]
    assert len(bao) == 1 and "quỹ 2" in bao[0] and "0" in bao[0]


def test_q5b_diem_quyet_tam_o_nv_trong_bao_mo_coi(de, tmp_path):
    _ghi_lists(str(tmp_path / "lists.csv"), _hs_day_du(), de)
    p = tmp_path / "lists.csv"
    dong = list(csv.reader(open(p, encoding="utf-8-sig", newline="")))
    dong[1][dong[0].index("WP5")] = "7"
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f, lineterminator="\r\n").writerows(dong)
    _ds, canh_bao = cv.doc_lists(str(p), de)
    assert any("WP5" in nd and "NV5 trống" in nd for _d, _e, nd in canh_bao)


def test_q5b_co_wp_ma_khong_co_thi_quy_1_la_clb_co_diem(de, tmp_path):
    # không có cột THIk: "đã thi" = CLB có bài được nạp
    hs = [(E1, "An", {"thu_2": [nv("clb_covua", False, 100), nv("clb_vanhoc", False, 60),
                                nv("clb_nhiepanh", False, 40)]})]
    kq, ra = _chay(de, tmp_path, hs, [(E1, {"clb_covua": 3})], thi=False)
    assert kq["canh_bao"] == []                                # quỹ 1 = {covua} = 100; quỹ 2 = {vanhoc, nhiepanh} = 100
    assert _nv(_doc_so(ra), E1)["clb_nhiepanh"]["diem_w"] == "40"


def test_q5b_tick_dung_voi_ghi_o_thi_cho_quy_1(de, tmp_path):
    # tick + vắng thi: vẫn thuộc quỹ 1 (kiosk sẽ báo wharton_vang_thi), nên bộ chuyển đổi tính quỹ 1 = 100
    hs = [(E1, "An", {"thu_2": [nv("clb_covua", True, 100), nv("clb_nhiepanh", False, 100)]})]
    kq, _ra = _chay(de, tmp_path, hs, [("khac" + MIEN, {"clb_covua": 1})])
    assert [x for x in kq["canh_bao"] if x[1] == E1] == []


# ------------------------------------------------------------------ Q5c: dữ liệu giả

def _lists_gia(tmp_path, so_hs=60, seed=3, **kw):
    p = str(tmp_path / "g.csv")
    lists_gia.ghi_csv(p, so_hs=so_hs, seed=seed, **kw)
    with open(p, encoding="utf-8-sig", newline="") as f:
        return p, list(csv.DictReader(f))


def test_q5c_mac_dinh_khong_doi_cot_va_byte(tmp_path):
    a, b = str(tmp_path / "a.csv"), str(tmp_path / "b.csv")
    lists_gia.ghi_csv(a, so_hs=40, seed=9)
    lists_gia.ghi_csv(b, so_hs=40, seed=9, so_nv=3, co_tick=False, co_wp=False)
    assert open(a, "rb").read() == open(b, "rb").read()
    assert open(a, encoding="utf-8-sig").readline().strip().split(",") == lists_gia.COT


def test_q5c_nv_toi_7_thik_wpk_hop_le(de, tmp_path):
    theo_ngay = {}
    for ngay in lists_gia.NGAY:
        buoi = cv._ma_buoi_tu_thu(de, ngay)
        theo_ngay[ngay] = [c["club_id"] for c in de["cau_lac_bo"] if c["buoi"] == buoi]
    co_de = {c["club_id"] for c in bm.clb_co_thi(de)}
    _p, dong = _lists_gia(tmp_path, so_hs=80, seed=4, clb_theo_ngay=theo_ngay, so_nv=7,
                          co_tick=True, co_wp=True, clb_co_de=co_de)
    assert all("NV7" in d and "THI7" in d and "WP7" in d for d in dong)
    thay_tick = thay_wp = False
    for d in dong:
        ds = [d["NV%d" % k] for k in range(1, 8)]
        n = len([x for x in ds if x])
        assert ds[:n] == [x for x in ds if x]                      # NV liền nhau, không hở
        assert n <= len(theo_ngay[d["Thu"]]) and len(set(x for x in ds if x)) == n
        tick = [ds[k - 1] for k in range(1, 8) if d["THI%d" % k] == "Có"]
        assert all(d["THI%d" % k] in ("", "Có") for k in range(1, 8))
        assert set(tick) <= co_de and len(tick) <= bm.TRAN_THI_MOI_BUOI
        assert all(d["THI%d" % k] == "" for k in range(1, 8) if not d["NV%d" % k])
        assert all(d["WP%d" % k] == "" for k in range(1, 8) if not d["NV%d" % k])
        thay_tick |= bool(tick)
        q1 = sum(int(d["WP%d" % k] or 0) for k in range(1, 8) if d["NV%d" % k] and d["THI%d" % k] == "Có")
        q2 = sum(int(d["WP%d" % k] or 0) for k in range(1, 8) if d["NV%d" % k] and d["THI%d" % k] != "Có")
        n1 = len(tick)
        assert q1 == (100 if n1 else 0) and q2 == (100 if n - n1 else 0), d
        thay_wp |= q1 + q2 > 0
    assert thay_tick and thay_wp


def test_q5c_xac_dinh_va_khong_doi_nv_khi_bat_tick_wp(de, tmp_path):
    a = _lists_gia(tmp_path, so_hs=30, seed=5, so_nv=3, co_tick=True, co_wp=True)[1]
    b = _lists_gia(tmp_path, so_hs=30, seed=5, so_nv=3, co_tick=True, co_wp=True)[1]
    c = _lists_gia(tmp_path, so_hs=30, seed=5)[1]
    assert a == b
    # bật tick/WP không được làm đổi nguyện vọng đã sinh
    assert [[d["NV%d" % k] for k in (1, 2, 3)] for d in a] == [[d["NV%d" % k] for k in (1, 2, 3)] for d in c]


def test_q5c_gai_quy_khong_du_100(de, tmp_path):
    rows = lists_gia.sinh(so_hs=40, seed=6, so_nv=7, co_tick=True, co_wp=True)
    gai = lists_gia.gai_quy_khong_du(rows, so_nv=7)
    d = next(r for r in rows if r["Email"] == gai["email"] and r["Thu"] == gai["thu"])
    quy = sum(int(d["WP%d" % k] or 0) for k in range(1, 8)
              if d["NV%d" % k] and (d["THI%d" % k] == "Có") == (gai["quy"] == 1))
    assert quy == 100 - gai["thieu"] and gai["thieu"] > 0


def test_q5c_phieu_forms_chi_cho_clb_da_tick_va_gai_ba_truong_hop(de, tmp_path):
    co_de = {c["club_id"] for c in bm.clb_co_thi(de)}
    theo_ngay = {ng: [c["club_id"] for c in de["cau_lac_bo"] if c["buoi"] == cv._ma_buoi_tu_thu(de, ng)]
                 for ng in lists_gia.NGAY}
    p = str(tmp_path / "l.csv")
    lists_gia.ghi_csv(p, so_hs=60, seed=7, clb_theo_ngay=theo_ngay, so_nv=7, co_tick=True, co_wp=True,
                      clb_co_de=co_de)
    ds, _ = cv.doc_lists(p, de)
    x = str(tmp_path / "f.xlsx")
    gai = tm.ghi_mau_xuat_chi_thi(de, x, ds, hat_giong=7)
    e_vang, c_vang = gai["tick_vang"]
    e_khong, c_khong = gai["nop_khong_tick"]
    assert c_vang in ds[e_vang]["tick"] and c_khong not in ds[e_khong]["tick"]
    tieu, cac_dong = cv.doc_tep_xuat(x)
    cong = {c["club_id"]: tieu.index(bm.cau_cong_thi(de, c, chi_thi=True)) for c in bm.clb_co_thi(de)}
    i_email = tieu.index("Email")
    dau = {}
    for dong in cac_dong:
        e = str(dong[i_email]).lower()
        if e in dau or e == gai["email_la"]:
            continue
        dau[e] = {m for m, i in cong.items() if dong[i] == bm.CO}
    for e, bai in dau.items():
        phep = set(ds[e]["tick"]) if e in ds else set()
        phep |= {c_khong} if e == e_khong else set()
        phep |= {gai["khong_xep"][1]} if e == gai["khong_xep"][0] else set()       # trường hợp gài cũ
        assert bai <= phep, (e, bai - phep)
    assert c_vang not in dau.get(e_vang, set())
    assert c_khong in dau[e_khong]
    kq = cv.chuyen_chi_thi([x], p, str(tmp_path / "ra"), de)
    nd = [t for _d, e, t in kq["canh_bao"] if e == e_khong]
    assert any(c_khong in t and "tick" in t for t in nd)


def test_q5c_phieu_forms_khong_co_tick_giu_cach_cu(de, tmp_path):
    p = str(tmp_path / "l.csv")
    theo_ngay = {ng: [c["club_id"] for c in de["cau_lac_bo"] if c["buoi"] == cv._ma_buoi_tu_thu(de, ng)]
                 for ng in lists_gia.NGAY}
    lists_gia.ghi_csv(p, so_hs=40, seed=8, clb_theo_ngay=theo_ngay)
    ds, _ = cv.doc_lists(p, de)
    gai = tm.ghi_mau_xuat_chi_thi(de, str(tmp_path / "f.xlsx"), ds, hat_giong=8)
    assert set(gai) == {"email_trung", "email_la", "khong_xep", "n_phieu"}


# ------------------------------------------------------------------ Q5c: demo --day-du

def test_demo_mac_dinh_in_diem_quyet_tam_tat(tmp_path, capsys):
    assert demo_t4m.main(["--ra", str(tmp_path / "ra"), "--so-hs", "30", "--seed", "11"]) == 0
    assert "Điểm quyết tâm: TẮT" in capsys.readouterr().out


def test_demo_moi_clb_cung_in_dong_diem_quyet_tam(tmp_path, capsys):
    assert demo_t4m.main(["--ra", str(tmp_path / "ra"), "--so-hs", "30", "--seed", "11", "--moi-clb"]) == 0
    assert "Điểm quyết tâm: TẮT" in capsys.readouterr().out


def test_demo_day_du_bat_diem_quyet_tam_va_gai_ba_truong_hop(tmp_path, capsys):
    ra = tmp_path / "ra"
    kq = demo_t4m.chay_demo(str(ra), so_hs=40, seed=11, day_du=True)
    assert kq["diem_quyet_tam"] is True and kq["ket_qua"]
    assert kq["n_bai_thi"] > 0
    gai = kq["gai"]
    assert not any(e == gai["tick_vang"][0] for _d, e, _t in kq["canh_bao"])   # tick mà vắng: bộ chuyển đổi không báo
    assert any(gai["nop_khong_tick"][0] == e and "tick" in t for _d, e, t in kq["canh_bao"])
    quy = gai["quy_sai"]
    assert any(quy["email"] == e and "quỹ %d" % quy["quy"] in t for _d, e, t in kq["canh_bao"])
    demo_t4m.in_tom_tat(kq)
    ra_txt = capsys.readouterr().out
    assert "Điểm quyết tâm: BẬT" in ra_txt


def test_demo_day_du_kiosk_chan_roi_cho_chay_sau_khi_sua_quy_sai(tmp_path):
    kq = demo_t4m.chay_demo(str(tmp_path / "ra"), so_hs=40, seed=11, day_du=True)
    assert kq["bi_chan_lan_dau"] is True                 # quỹ sai làm kiosk CHẶN lần chạy đầu
    assert kq["ket_qua"]                                  # sau khi sửa ở "Bước 3" thì chạy được


def test_demo_day_du_xac_dinh_va_ket_hop_moi_clb(tmp_path):
    a = demo_t4m.chay_demo(str(tmp_path / "a"), so_hs=40, seed=11, day_du=True)
    b = demo_t4m.chay_demo(str(tmp_path / "b"), so_hs=40, seed=11, day_du=True)
    c = demo_t4m.chay_demo(str(tmp_path / "c"), so_hs=40, seed=11, day_du=True, moi_clb=True)
    assert a["ket_qua"] == b["ket_qua"] == c["ket_qua"]
    assert c["n_bieu_mau"] > 0 and c["diem_quyet_tam"] is True


def test_demo_day_du_sinh_so_nhap_co_cot_diem_quyet_tam(tmp_path):
    ra = tmp_path / "ra"
    demo_t4m.chay_demo(str(ra), so_hs=30, seed=11, day_du=True)
    assert "Điểm quyết tâm" in [c for r in _tieu_de_hs(ra) for c in r]
    ra2 = tmp_path / "ra2"
    demo_t4m.chay_demo(str(ra2), so_hs=30, seed=11)
    assert "Điểm quyết tâm" not in [c for r in _tieu_de_hs(ra2) for c in r]


def test_demo_main_co_co_day_du(tmp_path, capsys):
    assert demo_t4m.main(["--ra", str(tmp_path / "ra"), "--so-hs", "30", "--seed", "11", "--day-du"]) == 0
    ra = capsys.readouterr().out
    assert "Điểm quyết tâm: BẬT" in ra and "tick" in ra
