"""T4M-BK3, BK4: bảng cấu hình flow DaLam_<ClubId> + lệnh gộp tao_bo_dung_t4m.py (thư mục "nhập là dựng" cho IT).

Kiểm tĩnh, không cần Microsoft 365. Mọi thứ chạm Microsoft vẫn nhãn TH (chưa chạy). Dữ liệu hoàn toàn MÔ PHỎNG.
"""

import csv
import json
import os
import re
import sys
import zipfile

import pytest

pytest.importorskip("docx", reason="bộ dựng gọi tao_mau_forms --moi-clb (cần python-docx)")
GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))

import bieu_mau as bm  # noqa: E402
import tao_mau_forms as tm  # noqa: E402
import tao_bo_dung_t4m as bd  # noqa: E402
from bo_dung_t4m import bang_flow, site_script  # noqa: E402

DOCS = os.path.join(GOC, "docs", "he_sinh_thai")
TTH = "TH: chưa chạy trên Power Apps / SharePoint"


def _doc(ten):
    with open(os.path.join(DOCS, ten), encoding="utf-8") as f:
        return f.read()


def _doc_tep(duong):
    with open(duong, encoding="utf-8") as f:
        return f.read()


def _tat_ca_tep(thu_muc):
    kq = {}
    for goc, _d, tep in os.walk(thu_muc):
        for t in tep:
            p = os.path.join(goc, t)
            kq[os.path.relpath(p, thu_muc).replace(os.sep, "/")] = p
    return kq


@pytest.fixture(scope="module")
def de():
    return bm.doc_de_thi()


@pytest.fixture(scope="module")
def ra(tmp_path_factory, de):
    thu = tmp_path_factory.mktemp("bk34") / "bo_dung"
    bd.tao_bo_dung(de, str(thu), in_ra=lambda *_: None)
    return thu


# ---------------------------------------------------------------- BK3: bảng flow
def test_so_hang_flow_bang_so_clb_co_de(de):
    hang = bang_flow.hang_flow(de)
    co_de = [c["club_id"] for c in bm.clb_co_thi(de)]
    assert [h["ClubId"] for h in hang] == co_de
    assert len(hang) == len(co_de) >= 2
    assert [h["Flow"] for h in hang] == ["DaLam_" + x for x in co_de]
    assert len({h["Flow"] for h in hang}) == len(hang)


def test_o_cua_it_de_trong_va_co_tep_quick_import(de):
    for h in bang_flow.hang_flow(de):
        assert h["FormId"] == "" and h["ChuBieuMau"] == "" and h["DaThuNgay"] == ""
        assert h["TepQuickImport"] == "%s%s.docx" % (tm.TIEN_TO_DOCX_MOI_CLB, h["ClubId"])


def test_csv_flow_doc_duoc_va_khop_hang(de, ra):
    with open(ra / "03_flow" / "BANG_FLOW.csv", encoding="utf-8-sig", newline="") as f:
        dong = list(csv.DictReader(f))
    assert list(dong[0].keys()) == bang_flow.TIEU_DE_CSV
    assert dong == bang_flow.hang_flow(de)


def test_moi_clbid_cua_flow_co_trong_clb_csv(de, ra):
    with open(ra / "04_forms" / "CLB.csv", encoding="utf-8-sig", newline="") as f:
        clb = {d["ClubId"] for d in csv.DictReader(f)}
    with open(ra / "03_flow" / "BANG_FLOW.csv", encoding="utf-8-sig", newline="") as f:
        flow = [d["ClubId"] for d in csv.DictReader(f)]
    assert flow and set(flow) <= clb


def test_bang_flow_md_co_bieu_thuc_va_nhan(de, ra):
    md = _doc_tep(ra / "03_flow" / "BANG_FLOW.md")
    assert md.startswith(TTH)
    assert "toLower(" in md and "ResponseId eq '" in md
    for h in bang_flow.hang_flow(de):
        assert "`%s`" % h["Flow"] in md and "`%s`" % h["ClubId"] in md
    assert "không có gói" in md.lower() or "không tự chế" in md.lower()   # quyết định 3: không .zip của flow
    assert "GĐ" in md and "HỎI-IT" in md


# ---------------------------------------------------------------- BK4: lệnh gộp
def test_mot_lenh_sinh_du_bon_thu_muc_va_huong_dan(de, ra):
    tep = _tat_ca_tep(str(ra))
    for thu_muc in ("01_lists", "02_app", "03_flow", "04_forms"):
        assert any(k.startswith(thu_muc + "/") for k in tep), thu_muc
    assert "HUONG_DAN_IT.md" in tep
    assert "01_lists/site_script_t4m.json" in tep
    assert {"02_app/NguyenVong.txt", "02_app/DiemQuyetTam.txt", "02_app/ThiTuyen.txt", "02_app/Khoa.txt"} <= set(tep)
    assert "04_forms/CLB.csv" in tep and "04_forms/CAI_DAT_FORMS_MOI_CLB.md" in tep
    n_docx = [k for k in tep if k.startswith("04_forms/NHAP_FORMS_MOI_CLB_")]
    assert len(n_docx) == len(bm.clb_co_thi(de))


def test_04_forms_la_dau_ra_cua_tao_mau_forms_khong_viet_lai(de, ra, tmp_path):
    truc_tiep = tmp_path / "truc_tiep"
    tm.sinh_moi_clb(de, str(truc_tiep))
    a, b = _tat_ca_tep(str(truc_tiep)), _tat_ca_tep(str(ra / "04_forms"))
    assert set(a) == set(b)
    for k in a:
        assert open(a[k], "rb").read() == open(b[k], "rb").read(), k


def test_sinh_lai_giong_het_tung_byte_ca_zip(de, tmp_path):
    out = []
    for ten in ("a", "b"):
        thu = tmp_path / ten / "bd"
        z = bd.tao_bo_dung(de, str(thu), tao_zip=True, in_ra=lambda *_: None)
        out.append((thu, z))
    a, b = (_tat_ca_tep(str(x[0])) for x in out)
    assert set(a) == set(b)
    for k in a:
        assert open(a[k], "rb").read() == open(b[k], "rb").read(), k
    za, zb = out[0][1], out[1][1]
    assert za and open(za, "rb").read() == open(zb, "rb").read()


def test_sinh_lai_len_thu_muc_da_co_van_giong_het(de, tmp_path):
    thu = tmp_path / "bd"
    bd.tao_bo_dung(de, str(thu), tao_zip=True, in_ra=lambda *_: None)
    lan1 = {k: open(p, "rb").read() for k, p in _tat_ca_tep(str(thu)).items()}
    z1 = open(str(thu) + ".zip", "rb").read()
    bd.tao_bo_dung(de, str(thu), tao_zip=True, in_ra=lambda *_: None)
    lan2 = {k: open(p, "rb").read() for k, p in _tat_ca_tep(str(thu)).items()}
    assert lan1 == lan2 and z1 == open(str(thu) + ".zip", "rb").read()


def test_zip_khop_thu_muc_thu_tu_va_gio_co_dinh(de, tmp_path):
    thu = tmp_path / "bd"
    z = bd.tao_bo_dung(de, str(thu), tao_zip=True, in_ra=lambda *_: None)
    tep = _tat_ca_tep(str(thu))
    with zipfile.ZipFile(z) as zf:
        ten = zf.namelist()
        assert ten == sorted(tep)
        assert all(not n.endswith(".zip") for n in ten)
        assert {i.date_time for i in zf.infolist()} == {bd.GIO_ZIP}
        for n in ten:
            assert zf.read(n) == open(tep[n], "rb").read(), n
    assert not str(z).startswith(str(thu) + os.sep)         # zip nằm ngoài thư mục đã nén, không tự nuốt mình


def test_khong_tao_zip_neu_khong_xin(de, tmp_path):
    thu = tmp_path / "bd"
    assert bd.tao_bo_dung(de, str(thu), in_ra=lambda *_: None) is None
    assert not os.path.exists(str(thu) + ".zip")


def test_khong_co_clb_co_de_thi_loi_va_khong_ghi_gi(de, tmp_path):
    import copy
    de2 = copy.deepcopy(de)
    for c in de2["cau_lac_bo"]:
        c["de_thi"] = []
    thu = tmp_path / "bd"
    with pytest.raises(bm.LoiDeThi):
        bd.tao_bo_dung(de2, str(thu), in_ra=lambda *_: None)
    assert not thu.exists()


def test_them_clb_co_de_thi_thi_them_mot_flow(de):
    import copy
    de2 = copy.deepcopy(de)
    ung = next(c for c in de2["cau_lac_bo"] if not c["de_thi"])
    ung["de_thi"] = copy.deepcopy(bm.clb_co_thi(de2)[0]["de_thi"])
    assert len(bang_flow.hang_flow(de2)) == len(bang_flow.hang_flow(de)) + 1
    assert ung["club_id"] in [h["ClubId"] for h in bang_flow.hang_flow(de2)]


def test_main_va_co_zip(de, tmp_path, capsys):
    thu = tmp_path / "bd"
    assert bd.main(["--ra", str(thu), "--zip"]) == 0
    assert (tmp_path / "bd.zip").exists()
    assert "HUONG_DAN_IT.md" in capsys.readouterr().out
    assert bd.main(["--ra", str(tmp_path / "x"), "--de-thi", str(tmp_path / "khong_co.json")]) != 0


# ---------------------------------------------------------------- HUONG_DAN_IT.md
def test_huong_dan_nhac_moi_R1_den_R38(ra):
    spec = _doc("T4M_DAC_TA_SUA_APP.md")
    ma = re.findall(r"^\| (R\d+) \|", spec, flags=re.M)
    assert len(ma) == 38 and ma[0] == "R1" and ma[-1] == "R38"
    hd = _doc_tep(ra / "HUONG_DAN_IT.md")
    thieu = [m for m in ma if not re.search(r"\b%s\b" % m, hd)]
    assert not thieu, thieu


def test_huong_dan_tro_den_hang_hdt_co_that(ra):
    hdt = _doc("T4M_HUONG_DAN_THU.md")
    co = set(re.findall(r"^\| (\d+\.\d+) \|", hdt, flags=re.M))
    hd = _doc_tep(ra / "HUONG_DAN_IT.md")
    dung = set(re.findall(r"HDT (\d+\.\d+)", hd))
    assert dung and dung <= co, dung - co
    for dong in ("3.1", "4.1", "5.1", "13.2", "14.4", "14.5"):
        assert dong in dung


def test_huong_dan_moi_buoc_co_dong_pass_fail(ra):
    hd = _doc_tep(ra / "HUONG_DAN_IT.md")
    buoc = re.findall(r"^## Bước (\d+)", hd, flags=re.M)
    assert buoc[:2] == ["0", "1"] and len(buoc) >= 6
    for i, phan in enumerate(re.split(r"^## Bước ", hd, flags=re.M)[1:]):
        assert "☐ Pass" in phan and "☐ Fail" in phan, "bước %s" % buoc[i]


def test_huong_dan_thu_tu_dung(ra):
    hd = _doc_tep(ra / "HUONG_DAN_IT.md")
    mốc = ["Bước 1", "FormUrl", "Công thức", "Flow", "Vòng thử"]
    pos = [hd.index(m) for m in ("## Bước 1", "## Bước 2", "## Bước 4", "## Bước 5", "## Bước 6")]
    assert pos == sorted(pos)
    assert mốc  # tiêu đề các bước dùng đúng thứ tự lists -> CLB FormUrl -> công thức -> flow -> vòng thử
    for tu in ("lists", "FormUrl", "ông thức", "low", "thử"):
        assert tu.lower() in hd.lower()


def test_huong_dan_ba_cach_a_b_c_quyen_va_hoi_it(ra):
    hd = _doc_tep(ra / "HUONG_DAN_IT.md")
    for cach in ("Cách A", "Cách B", "Cách C"):
        assert cach in hd
    assert "site owner permissions" in hd or "quyền chủ site" in hd
    assert "Cloud Application Administrator" in hd        # vai trò tối thiểu, nhãn TT-CXM
    assert "HỎI-IT" in hd and "TT-CXM" in hd and "ĐXM" in hd
    assert "Environment Maker" in hd


def test_huong_dan_ap_khong_dong_bo_va_khong_dung_invoke_spositedesign(de, ra):
    hd = _doc_tep(ra / "HUONG_DAN_IT.md")
    n = site_script.dem_hanh_dong(site_script.tao_site_script())
    assert n > site_script.TRAN_DONG_BO and ("%d hành động" % n) in hd
    assert "Settings > Apply a site template" in hd and "Add-SPOSiteDesignTask" in hd
    # Invoke-SPOSiteDesign chỉ được nhắc để CẤM: mỗi lần xuất hiện đứng ngay sau "không dùng"/"đừng dùng"
    ds = [m.start() for m in re.finditer(r"Invoke-SPOSiteDesign", hd)]
    assert ds
    for v in ds:
        assert re.search(r"(không|đừng|cấm)\s+(dùng|chạy|gọi)\s+`$", hd[max(0, v - 25):v], flags=re.I), hd[max(0, v - 40):v + 30]
    assert "không đồng bộ" in hd


def test_huong_dan_nhan_flow_khong_zip_va_nhan_th(ra):
    hd = _doc_tep(ra / "HUONG_DAN_IT.md")
    assert hd.startswith(TTH)
    assert "Save as" in hd or "Export" in hd
    assert "BANG_FLOW" in hd


# ---------------------------------------------------------------- không dữ liệu thật
def test_khong_ten_that_tenantid_url_trong_dau_ra_van_ban(ra):
    cam = re.compile(r"sharepoint\.com|\.onmicrosoft\.|forms\.office\.com|forms\.cloud\.microsoft|powerapps\.com|"
                     r"flow\.microsoft\.com|make\.powerapps|tenantId\s*[:=]\s*\S|tenant id\s*[:=]\s*\S", re.I)
    for k, p in _tat_ca_tep(str(ra)).items():
        if k.endswith((".md", ".txt", ".csv")):
            nd = _doc_tep(p) if not k.endswith(".csv") else open(p, encoding="utf-8-sig").read()
            assert not cam.search(nd), k
            assert not re.search(r"\b[\w.+-]+@(?!truong-gia\.example\.test)[\w-]+\.\w+", nd), k


def test_moi_tep_van_ban_cua_bk34_co_dong_th(ra):
    for k in ("03_flow/BANG_FLOW.md", "HUONG_DAN_IT.md"):
        assert _doc_tep(ra / k).startswith(TTH), k


def test_tai_lieu_huong_dan_ve_lenh_moi():
    for ten in ("README.md", "T4M_VAN_HANH_MOT_DOT.md"):
        duong = os.path.join(GOC, "mau_forms_thi_clb", ten) if ten == "README.md" else os.path.join(DOCS, ten)
        assert "tao_bo_dung_t4m.py" in _doc_tep(duong), ten


def test_site_script_trong_bo_van_la_json_hop_le(ra):
    with open(ra / "01_lists" / "site_script_t4m.json", encoding="utf-8") as f:
        ss = json.load(f)
    assert site_script.dem_hanh_dong(ss) == site_script.dem_hanh_dong(site_script.tao_site_script())
