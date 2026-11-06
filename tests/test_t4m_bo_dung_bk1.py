"""T4M-BK1, BK2: bộ dựng sẵn cho IT: định nghĩa cột list, site script, CSV mẫu, bảng kiểm thêm cột, công thức Power Fx.

Kiểm tĩnh, không cần Microsoft 365. Mọi thứ chạm Microsoft vẫn nhãn TH (chưa chạy). Dữ liệu hoàn toàn MÔ PHỎNG.
"""

import csv
import json
import os
import re
import sys
import uuid

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))

import bieu_mau as bm  # noqa: E402
import chuyen_forms_sang_phan_mem as cv  # noqa: E402
import sinh_xuat_lists_gia as lists_gia  # noqa: E402
import tao_mau_forms as tm  # noqa: E402
from bo_dung_t4m import cong_thuc, cot_lists, site_script, sinh_bk1  # noqa: E402

SO_NV = 7
DONG_TH = "TH: chưa chạy trên Power Apps / SharePoint"


@pytest.fixture(scope="module")
def de():
    return bm.doc_de_thi()


@pytest.fixture(scope="module")
def ra(tmp_path_factory, de):
    thu = tmp_path_factory.mktemp("bk1")
    sinh_bk1.ghi_tat_ca(str(thu), de)
    return thu


def _tep_ra(ra):
    out = {}
    for goc, _, tens in os.walk(str(ra)):
        for t in tens:
            p = os.path.join(goc, t)
            out[os.path.relpath(p, str(ra))] = open(p, "rb").read()
    return out


# ---------------------------------------------------------------- cột: một nguồn, khớp ba nguồn khác
def test_cot_eca_khop_cot_csv():
    mong = [c for c in lists_gia.cot_csv(SO_NV, True, True) if c != "Created"]
    assert [c.ten for c in cot_lists.ECA] == mong
    assert len(mong) == 30


def test_cot_clb_khop_tieu_de_ghi_clb_csv(tmp_path, de):
    p = tmp_path / "CLB.csv"
    tm.ghi_clb_csv(de, str(p))
    with open(p, encoding="utf-8-sig", newline="") as f:
        tieu = next(csv.reader(f))
    assert [c.ten for c in cot_lists.CLB] == tieu


def test_doc_lists_doc_tep_dung_cot_eca_khong_canh_bao(tmp_path, de):
    theo_ngay = {}
    for ngay in lists_gia.NGAY:
        buoi = cv._ma_buoi_tu_thu(de, ngay)
        theo_ngay[ngay] = [c["club_id"] for c in de["cau_lac_bo"] if c["buoi"] == buoi]
    co_de = {c["club_id"] for c in bm.clb_co_thi(de)}
    dong = lists_gia.sinh(so_hs=30, seed=11, clb_theo_ngay=theo_ngay, so_nv=SO_NV, co_tick=True, co_wp=True,
                          clb_co_de=co_de)
    ten_cot = [c.ten for c in cot_lists.ECA]
    p = tmp_path / "eca.csv"
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ten_cot, lineterminator="\r\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(dong)
    hs, canh_bao = cv.doc_lists(str(p), de)
    assert hs and canh_bao == []


def _buoi_clb_csv(tmp_path, de):
    p = tmp_path / "CLB.csv"
    tm.ghi_clb_csv(de, str(p))
    with open(p, encoding="utf-8-sig", newline="") as f:
        return {r["Buoi"] for r in csv.DictReader(f)}


def test_buoi_theo_thu_phu_dung_cac_buoi_cua_clb_csv(tmp_path, de):
    anh_xa = cong_thuc.buoi_theo_thu(de)
    assert list(anh_xa) == lists_gia.NGAY
    assert set(anh_xa.values()) == _buoi_clb_csv(tmp_path, de)
    assert len(set(anh_xa.values())) == len(anh_xa)


@pytest.mark.xfail(strict=True, reason="PHÁT HIỆN: CLB.csv ghi Buoi 'Thứ Hai' còn cột Thu của ECA là 'Thứ 2' "
                   "(quyết định 1 của §9 nói 'cùng chữ'); bộ dựng dùng ánh xạ buoi_theo_thu. Hết lệch thì bỏ xfail.")
def test_buoi_clb_csv_bang_thu_cua_lists_thang(tmp_path, de):
    assert _buoi_clb_csv(tmp_path, de) == set(lists_gia.NGAY)


# ---------------------------------------------------------------- GUID cố định
def test_guid_on_dinh_duy_nhat_va_la_uuid5():
    tat_ca = [(l, c) for l, cs in cot_lists.TAT_CA.items() for c in cs]
    ids = [cot_lists.guid_cot(l, c.ten) for l, c in tat_ca]
    assert len(ids) == len(set(ids)) == 30 + 4 + 4 + 4
    assert ids == [cot_lists.guid_cot(l, c.ten) for l, c in tat_ca]
    assert cot_lists.guid_cot("ECA", "NV1") == str(uuid.uuid5(uuid.NAMESPACE_URL, "rbda-t4m/ECA/NV1"))


# ---------------------------------------------------------------- site script
def test_site_script_hop_le_va_ten_trong_cot_hop_dong():
    ss = site_script.tao_site_script()
    ss = json.loads(json.dumps(ss, ensure_ascii=False))
    hop_dong = {(l, c.ten) for l, cs in cot_lists.TAT_CA.items() for c in cs}
    thay = set()
    list_hien_tai = None
    for a in ss["actions"]:
        if a["verb"] == "createSPList":
            assert a["templateType"] == 100
            list_hien_tai = a["listName"]
            assert list_hien_tai in cot_lists.TAT_CA
        elif a["verb"] == "addSPField":
            assert a["internalName"] and (list_hien_tai, a["internalName"]) in hop_dong
            assert a["fieldType"] in ("Text", "Number", "DateTime")
            thay.add((list_hien_tai, a["internalName"]))
        elif a["verb"] == "addSPFieldXml":
            m = re.search(r'StaticName="([^"]+)"', a["schemaXml"])
            assert (list_hien_tai, m.group(1)) in hop_dong
            assert 'Type="Choice"' in a["schemaXml"] and "<CHOICES>" in a["schemaXml"]
            assert re.search(r'ID="\{[0-9a-f-]{36}\}"', a["schemaXml"])
            thay.add((list_hien_tai, m.group(1)))
        else:
            pytest.fail("verb lạ: %s" % a["verb"])
    assert thay == hop_dong


def test_kieu_cot_dung_loai_hanh_dong():
    ss = site_script.tao_site_script()
    xml = {re.search(r'StaticName="([^"]+)"', a["schemaXml"]).group(1)
           for a in ss["actions"] if a["verb"] == "addSPFieldXml"}
    assert xml == {c.ten for c in cot_lists.ECA if c.kieu == "Choice"}
    assert {"Thu", "TrangThai", "CoSo"} <= xml


def test_dem_hanh_dong_in_ra_va_canh_bao_tran(capsys):
    ss = site_script.tao_site_script()
    n = site_script.dem_hanh_dong(ss)
    assert n == 4 + 30 + 4 + 4 + 4
    site_script.kiem_so_hanh_dong(n)
    out = capsys.readouterr().out
    assert str(n) in out and "30" in out          # in số hành động, cảnh báo vượt trần 30 (áp đồng bộ)
    site_script.kiem_so_hanh_dong(30)
    assert "cảnh báo" not in capsys.readouterr().out.lower()
    with pytest.raises(ValueError):
        site_script.kiem_so_hanh_dong(301)


# ---------------------------------------------------------------- CSV mẫu và bảng kiểm cột
def test_csv_mau_tieu_de_va_mot_dong_vi_du_gia(ra):
    for ten in ("ECA", "CLB", "BaiThi", "NHAT_KY_DA_LAM"):
        with open(os.path.join(str(ra), "01_lists", ten + "_mau.csv"), encoding="utf-8-sig", newline="") as f:
            bang = list(csv.reader(f))
        assert [c.ten for c in cot_lists.TAT_CA[ten]] == bang[0]
        assert len(bang) == 2 and len(bang[1]) == len(bang[0])
        assert all(v != "" for v in bang[1]), "ô trống làm Lists đoán sai kiểu"
    with open(os.path.join(str(ra), "01_lists", "ECA_mau.csv"), encoding="utf-8-sig", newline="") as f:
        d = next(csv.DictReader(f))
    assert d["Email"].endswith("example.test") and re.fullmatch(r"\d+", d["WP1"]) and re.fullmatch(r"\d+", d["Khoi"])


def test_kiem_cot_eca_liet_ke_moi_cot_va_chi_them_neu_chua_co(ra):
    nd = open(os.path.join(str(ra), "01_lists", "KIEM_COT_ECA.md"), encoding="utf-8").read()
    for c in cot_lists.ECA:
        assert "`%s`" % c.ten in nd
    assert "chỉ thêm nếu chưa có" in nd.lower()
    for ten in ("Thứ 2", "Đang mở", "Đã khóa"):
        assert ten in nd


# ---------------------------------------------------------------- Power Fx
FILE_FX = ("NguyenVong.txt", "DiemQuyetTam.txt", "ThiTuyen.txt", "Khoa.txt")


def _noi_dung(ra, ten):
    return open(os.path.join(str(ra), "02_app", ten), encoding="utf-8").read()


def test_moi_tep_fx_co_dong_th_va_nguon(ra):
    for ten in FILE_FX:
        dong = _noi_dung(ra, ten).split("\n")
        assert dong[0] == DONG_TH, ten
        assert dong[1].startswith("Nguồn: T4M_DAC_TA_SUA_APP.md"), ten


def test_cong_thuc_khai_trien_du_bay_chi_so_khong_dau_ba_cham(ra):
    for ten in FILE_FX:
        nd = _noi_dung(ra, ten)
        assert "…" not in nd and "/*" not in nd and "..." not in nd, ten
    tat_ca = "\n".join(_noi_dung(ra, t) for t in FILE_FX)
    for k in range(1, SO_NV + 1):
        for ten in ("NV", "THI", "WP"):
            assert "%s%d" % (ten, k) in tat_ca
    assert "NV8" not in tat_ca and "THI8" not in tat_ca and "WP8" not in tat_ca
    nv = _noi_dung(ra, "NguyenVong.txt")
    for ten in ("NV", "THI", "WP"):
        assert all("%s%d" % (ten, k) in nv for k in range(1, SO_NV + 1)), ten
    tt = _noi_dung(ra, "ThiTuyen.txt")
    assert all("NV%d" % k in tt and "THI%d" % k in tt for k in range(1, SO_NV + 1))


def test_nguon_loc_chi_dung_bang_va_khong_dau_cam(ra):
    for ten in FILE_FX:
        nd = _noi_dung(ra, ten)
        loi = cong_thuc.soat_loc_uy_quyen(nd)
        assert loi == [], (ten, loi)
    tat_ca = "\n".join(_noi_dung(ra, t) for t in FILE_FX)
    assert "Lower(User().Email)" in tat_ca
    assert "Filter(ECA, Email = Lower(User().Email))" in tat_ca
    assert "Filter(BaiThi, Email = Lower(User().Email))" in tat_ca
    assert "Filter(CLB, Buoi = " in tat_ca


@pytest.mark.parametrize("xau", [
    "Filter(ECA, Email <> x)",
    "Filter(CLB, ClubId in colChon.Id)",
    "Filter(BaiThi, IsBlank(NopLuc))",
    "Filter(ECA, Not(Thu = x))",
    "Filter(ECA, Email = a, Not(Thu = x))",
    "Filter( ECA , Thu = x And FormUrl <> \"\")",
])
def test_bo_soat_bat_duoc_cau_loc_cam(xau):
    assert cong_thuc.soat_loc_uy_quyen(xau) != []


@pytest.mark.parametrize("xau", [
    "Filter(ECA, Email = Lower(User().Email))",
    "Filter(colCLB, ClubId <> a And !(ClubId in b))",        # lọc cục bộ: được
    "Filter(Table({a: 1}), T = \"Có\")",
    "Filter(CLB, Buoi = \"Thứ Hai\")",
])
def test_bo_soat_khong_bao_nham(xau):
    assert cong_thuc.soat_loc_uy_quyen(xau) == []


def test_bo_soat_nhin_ca_cau_loc_long_nhau():
    assert cong_thuc.soat_loc_uy_quyen("ForAll(x, Filter(ECA, Email = a, Thu <> b))") != []


def test_filter_clb_dung_ten_buoi_cua_de_thi(ra, de):
    tat_ca = "\n".join(_noi_dung(ra, t) for t in FILE_FX)
    for ten in cong_thuc.buoi_theo_thu(de).values():
        assert '"%s"' % ten in tat_ca


def test_quy_tac_diem_trong_cong_thuc(ra):
    dq = _noi_dung(ra, "DiemQuyetTam.txt")
    assert "100" in dq and "IsMatch" in dq                    # bộ đếm /100, ô chỉ nhận số nguyên không âm
    kh = _noi_dung(ra, "Khoa.txt")
    assert "Đã khóa" in kh and "DisplayMode.Disabled" in kh and ">= 5" in kh


# ---------------------------------------------------------------- không dữ liệu thật, sinh lại giống hệt
def test_khong_ten_that_tenant_hay_url(ra):
    for ten, nd in _tep_ra(ra).items():
        van_ban = nd.decode("utf-8")
        assert "http" not in van_ban.lower(), ten
        assert "tenant" not in van_ban.lower(), ten
        for email in re.findall(r"[\w.+-]+@[\w.-]+", van_ban):
            assert email.endswith("example.test"), (ten, email)


def test_moi_tep_van_ban_co_dong_th_hoac_duoc_readme_noi_toi(ra):
    tep = _tep_ra(ra)
    readme = tep["README_BK1.md"].decode("utf-8")
    assert readme.split("\n")[0] == DONG_TH
    for ten, nd in tep.items():
        if ten.endswith((".md", ".txt")):
            assert nd.decode("utf-8").split("\n")[0] == DONG_TH, ten
        else:                                       # .json, .csv: không chèn chú thích được, README nêu rõ
            assert os.path.basename(ten) in readme, ten


def test_sinh_lai_giong_het_tung_byte(ra, de, tmp_path):
    sinh_bk1.ghi_tat_ca(str(tmp_path), de)
    a, b = _tep_ra(ra), _tep_ra(tmp_path)
    assert a.keys() == b.keys() and all(a[k] == b[k] for k in a)
    assert any(k.endswith(".json") for k in a)


def test_de_thi_khac_thi_buoi_khac(de):
    """Công thức theo `de` đưa vào, không dán chết 'Thứ Hai'."""
    de2 = json.loads(json.dumps(de))
    for b in de2["buoi"]:
        b["ten"] = b["ten"].replace("Thứ", "Ngày")
    f = cong_thuc.tao_cong_thuc(de2)
    assert "Ngày Hai" in f["NguyenVong.txt"] and "Thứ Hai" not in f["NguyenVong.txt"]


def test_moi_khoa_nhan_T_co_trong_bang_colNhan(ra):
    """Mọi T("khoa") trong công thức phải có dòng trong bảng nhãn vi/en (không chữ cứng, không khóa thiếu)."""
    tat_ca = "\n".join(_noi_dung(ra, t) for t in FILE_FX)
    dung = set(re.findall(r'T\("([a-z0-9_]+)"\)', tat_ca))
    co = {k for k, _, _ in cong_thuc.NHAN}
    assert dung and dung <= co, dung - co
    assert all(vi and en for _, vi, en in cong_thuc.NHAN)


def test_ngay_gui_mot_patch_ghi_du_ba_nhom_cot(ra):
    nv = _noi_dung(ra, "NguyenVong.txt")
    gui = nv[nv.index("btnGui.OnSelect"):]
    assert gui.count("Patch(ECA") == 1
    for k in range(1, SO_NV + 1):
        assert "NV%d: Dong.ddNV%d" % (k, k) in gui and "THI%d: " % k in gui and "WP%d: " % k in gui


def _cac_khoi(nd):
    """Tách tệp thành các khối 'Điều khiển.Thuộc tính =' + thân thụt lề (bỏ dòng chú thích #)."""
    khoi, hien = [], None
    for d in nd.split("\n"):
        if d.startswith("#") or not d.strip():
            continue
        if not d.startswith(" ") and d.endswith(" =") and "." in d:
            hien = [d[:-2], []]
            khoi.append(hien)
        elif d.startswith("    ") and hien is not None:
            hien[1].append(d[4:])
        elif not d.startswith((DONG_TH[:2], "Nguồn:")):
            pytest.fail("dòng ngoài khối: %r" % d)
    return [(t, "\n".join(th)) for t, th in khoi]


def test_cu_phap_tinh_ngoac_can_va_khong_dinh_lenh(ra):
    tong = 0
    for ten in FILE_FX:
        for tieu, than in _cac_khoi(_noi_dung(ra, ten)):
            tong += 1
            bo = re.sub(r'"[^"]*"', '""', than)
            assert bo.count("(") == bo.count(")"), (ten, tieu)
            assert bo.count("{") == bo.count("}"), (ten, tieu)
            assert than.count('"') % 2 == 0, (ten, tieu)
            assert than.strip(), (ten, tieu)
            if tieu != "App.Formulas":                 # hàm người dùng bắt buộc kết thúc bằng ';'
                assert not than.rstrip().endswith(";"), (ten, tieu)
            sach = re.sub(r"\)\s+(And|Or|in)\b", ") +", bo)           # toán tử giữa hai biểu thức: hợp lệ
            assert not re.search(r"\)[ ]*[A-Za-z]", sach), (ten, tieu, "hai lệnh dính nhau, thiếu ';'")
    assert tong > 140


def test_khong_thuoc_tinh_nao_co_hai_cong_thuc(ra):
    thay = {}
    for ten in FILE_FX:
        for tieu, _ in _cac_khoi(_noi_dung(ra, ten)):
            assert tieu not in thay, (tieu, thay.get(tieu), ten)
            thay[tieu] = ten
