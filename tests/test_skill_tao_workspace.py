# -*- coding: utf-8 -*-
"""Canh skill `tao-workspace-tu-raw`: raw bất kỳ -> workspace .zip nạp sẵn dữ liệu.

Phép kiểm chính KHÔNG phải "script chạy không lỗi" mà là: nhập zip nó dựng vào phần mềm
thật, thấy đúng cấu hình và dữ liệu, chạy phân bổ được. Và chiều ngược lại: raw sai thì
KHÔNG một tệp nào được ghi (bộ dữ liệu hỏng trông y như thật — tệ hơn không có).
"""

import csv
import importlib.util
import json
import os
import sqlite3
import sys
import unicodedata

import pytest

openpyxl = pytest.importorskip("openpyxl")

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(GOC, ".claude", "skills", "tao-workspace-tu-raw", "scripts", "tao_workspace.py")
sys.path.insert(0, GOC)

import cau_hinh_ws  # noqa: E402
import workspace as ws  # noqa: E402
from api import PipelineAPI  # noqa: E402

NHAN = {"person": {"vi": "Nhân viên", "en": "Employee"}, "slot": {"vi": "Dự án", "en": "Project"},
        "session": {"vi": "Ngày", "en": "Day"}, "group": {"vi": "Diện ưu tiên", "en": "Priority group"},
        "score": {"vi": "Điểm phỏng vấn", "en": "Interview score"}}
DU_AN = ["Kho hàng số", "App bán hàng", "Website", "Đào tạo"]


@pytest.fixture(scope="module")
def tw():
    spec = importlib.util.spec_from_file_location("tao_workspace", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _csv(duong, hang, ma_hoa="utf-8", tach=","):
    with open(duong, "w", encoding=ma_hoa, newline="") as f:
        csv.writer(f, delimiter=tach).writerows(hang)


def _spec(thu_muc, **ghi_de):
    spec = {
        "ten_workspace": "Công ty Thử",
        "cau_hinh": {"industry": "company", "labels": NHAN, "rules": {"max_choices": 3, "max_tests": 2}},
        "cho_xep": {"chi_tieu": {d: 3 for d in DU_AN}},
        "nguoi": {"nguon": {"tep": "nguoi.csv"}, "cot": {"ma": "Mã", "ten": "Họ tên"},
                  "nguyen_vong": {"dang": "cot_xep_hang", "cot": ["NV1", "NV2"],
                                  "cot_diem": ["Điểm 1", None]}},
    }
    for k, v in ghi_de.items():
        spec[k] = v
    p = os.path.join(thu_muc, "spec.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False)
    return p


def _nguoi_rong(thu_muc, so=8):
    hang = [["Mã", "Họ tên", "NV1", "Điểm 1", "NV2"]]
    for i in range(so):
        hang.append(["NV%02d" % i, "Người %d" % i, DU_AN[i % 4], "7,5" if i % 2 else "",
                     DU_AN[(i + 1) % 4]])
    _csv(os.path.join(thu_muc, "nguoi.csv"), hang)


def _mo_zip(duong_zip, tmp_path):
    root = tmp_path / "goc_nhap"
    root.mkdir(exist_ok=True)
    slug = ws.nhap_zip(str(root), duong_zip)
    return ws.duong_dan_db(str(root), slug)


def _dung(tw, spec, ra, chap_nhan=()):
    return tw.dung(spec, ra, set(chap_nhan))


# ---------------------------------------------------------------- dựng được, cả bốn dạng

def test_cot_xep_hang_dung_zip_nap_va_chay_duoc(tw, tmp_path):
    _nguoi_rong(tmp_path)
    kq = _dung(tw, _spec(tmp_path), str(tmp_path / "ra"))
    assert sorted(os.listdir(tmp_path / "ra")) == sorted(
        [kq["slug"] + ".zip", os.path.basename(kq["tep"]["so"]), "BAO_CAO_SOAT.md"])
    db = _mo_zip(kq["tep"]["zip"], tmp_path)
    cfg = cau_hinh_ws.doc_cau_hinh(db)
    assert cfg["name"] == "Công ty Thử" and cfg["labels"]["slot"]["vi"] == "Dự án"
    c = sqlite3.connect(db)
    assert c.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 8
    assert c.execute("SELECT COUNT(*) FROM clubs").fetchone()[0] == 4
    # Zip chưa chạy lần nào: số bốc thăm khoá ở lần chạy đầu của NGƯỜI DÙNG.
    assert c.execute("SELECT COUNT(*) FROM run_history").fetchone()[0] == 0
    c.close()
    assert PipelineAPI(db, thu_muc_xuat=str(tmp_path)).run_pipeline(seed=1)["ok"]


def test_ma_tran_forms_phieu_trung_va_nhom_cung(tw, tmp_path):
    wb = openpyxl.Workbook()
    s = wb.active
    s.append(["Dấu thời gian", "Mã", "Họ tên", "Năm"] + ["Xếp hạng [%s]" % d for d in DU_AN])
    for i in range(6):
        s.append(["t%d" % i, "SV%d" % i, "Tên %d" % i, "Năm cuối" if i < 3 else "Năm 3",
                  "Lựa chọn 1", "Lựa chọn 2", None, None])
    s.append(["t9", "SV1", "Tên 1", "Năm cuối", None, None, "1st choice", None])
    wb.save(tmp_path / "forms.xlsx")
    nguoi = {"nguon": {"tep": "forms.xlsx"}, "cot": {"ma": "Mã", "ten": "Họ tên", "nhom": "Năm"},
             "nhom_doi_ten": {"năm cuối": "nam_cuoi", "Năm 3": "nam_3"},
             "nguyen_vong": {"dang": "ma_tran", "tien_to": "Xếp hạng"}}
    cau_hinh = {"industry": "custom", "labels": NHAN,
                "rules": {"max_choices": 4, "max_tests": 0, "priority": "tier",
                          "tier_mode": "strict", "tiers": ["nam_cuoi", "nam_3"]}}
    p = _spec(tmp_path, nguoi=nguoi, cau_hinh=cau_hinh)
    with pytest.raises(tw.LoiDung) as e:
        _dung(tw, p, str(tmp_path / "ra"))
    assert [x["ma"] for x in e.value.loi] == ["ma_trung"]
    assert not (tmp_path / "ra").exists()

    nguoi["phieu_trung"] = "giu_cuoi"
    kq = _dung(tw, _spec(tmp_path, nguoi=nguoi, cau_hinh=cau_hinh), str(tmp_path / "ra"))
    db = _mo_zip(kq["tep"]["zip"], tmp_path)
    c = sqlite3.connect(db)
    nv = c.execute("SELECT club_id FROM preferences WHERE student_id='SV1'").fetchall()
    assert [r[0] for r in nv] == ["clb_website"]        # phiếu cuối: chỉ Website
    assert c.execute("SELECT reserve_group FROM students WHERE student_id='SV0'").fetchone()[0] == "nam_cuoi"
    c.close()
    assert "SV1 (dòng 3)" in open(kq["tep"]["bao_cao"], encoding="utf-8").read()


def test_dong_dai_cp1258_diem_ca_nhan_va_chi_tieu_tep_rieng(tw, tmp_path):
    # Windows-1258 mang dấu thanh TỔ HỢP; phải về NFC thì "Phòng Hà" mới khớp tệp phòng UTF-8.
    def to1258(t):
        thanh = (0x300, 0x301, 0x303, 0x309, 0x323)
        ra = []
        for ch in t:
            d = unicodedata.normalize("NFD", ch)
            goc = "".join(c for c in d if ord(c) not in thanh)
            ra.append(unicodedata.normalize("NFC", goc) + "".join(c for c in d if ord(c) in thanh))
        return "".join(ra)
    phong = ["Phòng Hà Nội", "Phòng Huế"]
    _csv(tmp_path / "phong.csv", [["Phòng", "Số giường"]] + [[p, 2] for p in phong], "utf-8-sig")
    hang = [[to1258("MSSV"), to1258("Họ tên"), to1258("Điểm"), to1258("Phòng muốn"), to1258("Thứ tự")]]
    for i in range(4):
        hang += [["K%d" % i, to1258("Lê Hà"), 80 + i, to1258(phong[i % 2]), 2],
                 ["K%d" % i, to1258("Lê Hà"), 80 + i, to1258(phong[(i + 1) % 2]), 1]]
    _csv(tmp_path / "dk.csv", hang, "cp1258", ";")
    p = _spec(tmp_path,
              cau_hinh={"industry": "custom", "labels": NHAN,
                        "rules": {"max_choices": 2, "max_tests": None, "score_scope": "per_person"}},
              cho_xep={"nguon": {"tep": "phong.csv"}, "cot": {"ten": "Phòng", "chi_tieu": "Số giường"}},
              nguoi={"nguon": {"tep": "dk.csv"}, "cot": {"ma": "MSSV", "ten": "Họ tên", "diem": "Điểm"},
                     "nguyen_vong": {"dang": "dong_dai", "cot_cho": "Phòng muốn", "cot_hang": "Thứ tự"}})
    kq = _dung(tw, p, str(tmp_path / "ra"))
    c = sqlite3.connect(_mo_zip(kq["tep"]["zip"], tmp_path))
    assert c.execute("SELECT name, diem_ca_nhan FROM students WHERE student_id='K1'").fetchone() == ("Lê Hà", 81.0)
    # Thứ tự lấy theo cột Thứ tự, không theo thứ tự dòng.
    hang_nv = c.execute("SELECT c.name FROM preferences p JOIN clubs c USING(club_id) "
                        "WHERE student_id='K0' ORDER BY p.rank").fetchall()
    assert [r[0] for r in hang_nv] == ["Phòng Huế", "Phòng Hà Nội"]


def test_mot_o_va_buoi_khai_trong_spec(tw, tmp_path):
    _csv(tmp_path / "nguoi.csv", [["Mã", "Họ tên", "Chọn"]] +
         [["G%d" % i, "Khách %d" % i, "%s; %s" % (DU_AN[i % 2], DU_AN[2 + i % 2])] for i in range(6)])
    p = _spec(tmp_path,
              cho_xep={"chi_tieu": {d: 3 for d in DU_AN},
                       "buoi": {DU_AN[0]: "Thứ 2", DU_AN[1]: "Thứ 2", DU_AN[2]: "Thứ 4", DU_AN[3]: "Thứ 4"}},
              nguoi={"nguon": {"tep": "nguoi.csv"}, "cot": {"ma": "Mã", "ten": "Họ tên"},
                     "nguyen_vong": {"dang": "mot_o", "cot": "Chọn"}})
    kq = _dung(tw, p, str(tmp_path / "ra"))
    assert kq["so_buoi"] == 2
    db = _mo_zip(kq["tep"]["zip"], tmp_path)
    api = PipelineAPI(db, thu_muc_xuat=str(tmp_path))
    assert api.run_pipeline(seed=1)["ok"]
    assert api.get_thoi_khoa_bieu()["data"]["ds_buoi"] == ["thu_2", "thu_4"]


# ---------------------------------------------------------------- sai thì không ghi gì

@pytest.mark.parametrize("sua, ma_loi", [
    (lambda h: h[2].__setitem__(0, h[1][0]), "ma_trung"),
    (lambda h: h[1].__setitem__(4, h[1][2]), "nv_trung"),
    (lambda h: h[1].__setitem__(3, "tám"), "diem_sai"),
    (lambda h: h[1].__setitem__(0, ""), "thieu_ma"),
    (lambda h: h[2].__setitem__(0, h[1][0].lower()), "ma_khac_hoa"),
])
def test_raw_sai_dung_va_khong_ghi_tep(tw, tmp_path, sua, ma_loi):
    _nguoi_rong(tmp_path)
    duong = tmp_path / "nguoi.csv"
    with open(duong, encoding="utf-8") as f:
        hang = list(csv.reader(f))
    sua(hang)
    _csv(duong, hang)
    with pytest.raises(tw.LoiDung) as e:
        _dung(tw, _spec(tmp_path), str(tmp_path / "ra"))
    assert ma_loi in [x["ma"] for x in e.value.loi]
    assert not (tmp_path / "ra").exists()


def test_nguyen_vong_khong_khop_danh_sach_cho(tw, tmp_path):
    _nguoi_rong(tmp_path)
    duong = tmp_path / "nguoi.csv"
    with open(duong, encoding="utf-8") as f:
        hang = list(csv.reader(f))
    hang[1][2] = "Webiste"                              # gõ nhầm
    _csv(duong, hang)
    _csv(tmp_path / "cho.csv", [["Tên", "Chỉ tiêu"]] + [[d, 3] for d in DU_AN])
    p = _spec(tmp_path, cho_xep={"nguon": {"tep": "cho.csv"}, "cot": {"ten": "Tên", "chi_tieu": "Chỉ tiêu"}})
    with pytest.raises(tw.LoiDung) as e:
        _dung(tw, p, str(tmp_path / "ra"))
    loi = [x for x in e.value.loi if x["ma"] == "cho_khong_co"]
    assert len(loi) == 1 and "Có phải: 'Website'" in loi[0]["chi_tiet"]   # gợi ý, KHÔNG tự sửa
    assert not (tmp_path / "ra").exists()


def test_cho_khong_ai_chon_van_co_khi_khai_chi_tieu(tw, tmp_path):
    """Không có tệp chỗ xếp: chỗ lấy từ nguyện vọng CỘNG các chỗ khai chỉ tiêu trong spec —
    một dự án không ai chọn vẫn là một dự án."""
    _csv(tmp_path / "nguoi.csv", [["Mã", "NV1"], ["A", DU_AN[0]], ["B", DU_AN[0]]])
    nguoi = {"nguon": {"tep": "nguoi.csv"}, "cot": {"ma": "Mã"},
             "nguyen_vong": {"dang": "cot_xep_hang", "cot": ["NV1"]}}
    kq = _dung(tw, _spec(tmp_path, nguoi=nguoi), str(tmp_path / "ra"))
    assert kq["so_cho"] == 4


def test_thieu_chi_tieu_phai_hoi_khong_tu_dat(tw, tmp_path):
    _nguoi_rong(tmp_path)
    with pytest.raises(tw.LoiDung) as e:
        _dung(tw, _spec(tmp_path, cho_xep={"chi_tieu": {DU_AN[0]: 3}}), str(tmp_path / "ra"))
    loi = [x for x in e.value.loi if x["ma"] == "thieu_chi_tieu"]
    assert loi and all(d in loi[0]["chi_tiet"] for d in DU_AN[1:])


def test_qua_tran_nguyen_vong(tw, tmp_path):
    _nguoi_rong(tmp_path)
    p = _spec(tmp_path, cau_hinh={"industry": "company", "labels": NHAN, "rules": {"max_choices": 1}})
    with pytest.raises(tw.LoiDung) as e:
        _dung(tw, p, str(tmp_path / "ra"))
    assert "qua_tran_nv" in [x["ma"] for x in e.value.loi]


def test_cot_nv_bo_sot_bi_chan(tw, tmp_path):
    _nguoi_rong(tmp_path)
    nguoi = {"nguon": {"tep": "nguoi.csv"}, "cot": {"ma": "Mã"},
             "nguyen_vong": {"dang": "cot_xep_hang", "cot": ["NV1"], "cot_diem": ["Điểm 1"]}}
    with pytest.raises(tw.LoiDung) as e:
        _dung(tw, _spec(tmp_path, nguoi=nguoi), str(tmp_path / "ra"))
    assert "cot_nv_bo_sot" in [x["ma"] for x in e.value.loi]


def test_nhom_mo_coi_bi_chan(tw, tmp_path):
    _csv(tmp_path / "nguoi.csv", [["Mã", "Nhóm", "NV1"], ["A", "vip", DU_AN[0]], ["B", "", DU_AN[1]]])
    nguoi = {"nguon": {"tep": "nguoi.csv"}, "cot": {"ma": "Mã", "nhom": "Nhóm"},
             "nguyen_vong": {"dang": "cot_xep_hang", "cot": ["NV1"]}}
    p = _spec(tmp_path, nguoi=nguoi, cho_xep={"chi_tieu": {DU_AN[0]: 2, DU_AN[1]: 2}})
    with pytest.raises(tw.LoiDung) as e:
        _dung(tw, p, str(tmp_path / "ra"))
    assert "nhom_mo_coi" in [x["ma"] for x in e.value.loi]


def test_canh_bao_phan_mem_chan_tru_khi_chap_nhan(tw, tmp_path):
    # Một người không khai nguyện vọng nào: phần mềm cảnh báo -> chặn, trừ khi người dùng chấp nhận.
    _csv(tmp_path / "nguoi.csv", [["Mã", "NV1"], ["A", DU_AN[0]], ["B", ""]])
    nguoi = {"nguon": {"tep": "nguoi.csv"}, "cot": {"ma": "Mã"},
             "nguyen_vong": {"dang": "cot_xep_hang", "cot": ["NV1"]}}
    p = _spec(tmp_path, nguoi=nguoi, cho_xep={"chi_tieu": {DU_AN[0]: 2}})
    with pytest.raises(tw.LoiDung) as e:
        _dung(tw, p, str(tmp_path / "ra"))
    assert "health_student_no_preferences" in e.value.loi[0]["chi_tiet"]
    assert not (tmp_path / "ra").exists()
    kq = _dung(tw, p, str(tmp_path / "ra"), ["health_student_no_preferences"])
    assert "health_student_no_preferences" in open(kq["tep"]["bao_cao"], encoding="utf-8").read()


def test_tu_choi_ghi_vao_kho_git(tw, tmp_path):
    _nguoi_rong(tmp_path)
    (tmp_path / "kho" / ".git").mkdir(parents=True)
    with pytest.raises(tw.LoiDung) as e:
        _dung(tw, _spec(tmp_path), str(tmp_path / "kho" / "ra"))
    assert e.value.loi[0]["ma"] == "ra_trong_kho_git"
    assert not (tmp_path / "kho" / "ra").exists()


def test_khong_de_tep_da_co(tw, tmp_path):
    _nguoi_rong(tmp_path)
    _dung(tw, _spec(tmp_path), str(tmp_path / "ra"))
    with pytest.raises(tw.LoiDung) as e:
        _dung(tw, _spec(tmp_path), str(tmp_path / "ra"))
    assert e.value.loi[0]["ma"] == "de_tep"


def test_dong_dai_mot_nguoi_hai_diem_bi_chan(tw, tmp_path):
    _csv(tmp_path / "dk.csv", [["Mã", "Điểm", "Chỗ"], ["A", "80", DU_AN[0]], ["A", "90", DU_AN[1]]])
    p = _spec(tmp_path,
              cau_hinh={"industry": "custom", "labels": NHAN,
                        "rules": {"max_choices": 2, "max_tests": None, "score_scope": "per_person"}},
              nguoi={"nguon": {"tep": "dk.csv"}, "cot": {"ma": "Mã", "diem": "Điểm"},
                     "nguyen_vong": {"dang": "dong_dai", "cot_cho": "Chỗ"}})
    with pytest.raises(tw.LoiDung) as e:
        _dung(tw, p, str(tmp_path / "ra"))
    assert "diem_mau_thuan" in [x["ma"] for x in e.value.loi]


# ---------------------------------------------------------------- soi

def test_soi_doan_vai_tro_cot(tw, tmp_path):
    _csv(tmp_path / "r.csv", [["MSSV", "Họ và tên", "Email", "Phòng mong muốn", "Thứ tự", "Ưu tiên"],
                              ["A", "X", "a@x", "P1", "1", "có"], ["A", "X", "a@x", "P2", "2", "có"],
                              ["B", "Y", "b@x", "P1", "1", "không"]])
    doan = {c["cot"]: c["doan"] for c in tw.soi([str(tmp_path / "r.csv")])[0]["cot"]}
    assert doan["MSSV"][0].startswith("ma (CÓ 1")
    assert doan["Họ và tên"] == ["ten"]
    assert doan["Email"][0].startswith("lien_lac")
    assert doan["Thứ tự"] == ["thu_hang (dạng dong_dai)"]
    assert doan["Ưu tiên"] == ["nhom_uu_tien"]


def test_doc_hang_va_tach_o(tw):
    assert [tw.doc_hang(x) for x in ("1", "Lựa chọn 2", "Hạng 3", "1st", "Second choice", "", "abc")] \
        == [1, 2, 3, 1, 2, None, None]
    assert tw.tach_o("A; B ;C") == ["A", "B", "C"]
    assert tw.tach_o("A, B") == ["A", "B"]
    assert tw.tach_o("Bóng đá, nam; Cờ vua") == ["Bóng đá, nam", "Cờ vua"]
