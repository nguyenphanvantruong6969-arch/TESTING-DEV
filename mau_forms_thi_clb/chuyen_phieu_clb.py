"""FA-M1 (TH = CHƯA thử trên Microsoft thật): Phiếu thiết lập CLB (Forms) -> Sổ nhập, phân loại tự động.

Đọc tệp Excel xuất từ Microsoft Forms "Phiếu thiết lập CLB" (5 câu hỏi của V§4.1, xem
PHIEU_THIET_LAP_CLB.md), phân loại mỗi CLB theo V§4.1:
  câu 2 (mở thêm nhóm được?) = Có               -> TU_DO   (chỉ tiêu = sức chứa mỗi nhóm)
  câu 2 = Không, câu 4 (cần kỹ năng?) = Không   -> GIOI_HAN
  câu 2 = Không, câu 4 = Có                     -> TUYEN_CHON (cần ban quản lý duyệt)
rồi ghi một Sổ nhập có sheet CLB đủ cột FA (Loại, Điểm sàn, Tối thiểu, Sức chứa phòng) và sheet
"Giữ chỗ", cùng báo cáo kiểm trước (`fa_daa.kiem_truoc_fa`). Không đoán: thiếu số liệu bắt buộc thì
loại CLB đó và báo lỗi; điều đáng nghi (khai Tự do mà có lý do giới hạn...) là cảnh báo.
Dữ liệu trong test là MÔ PHỎNG. Dùng: python chuyen_phieu_clb.py phieu.xlsx --ra thu_muc
"""
import argparse
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fa_daa  # noqa: E402
import so_nhap  # noqa: E402
from i18n_errors import format_all  # noqa: E402

TIEU_DE_PHIEU = [
    "Tên CLB", "Buổi", "Giờ", "Địa điểm",
    "Mở thêm nhóm được nếu đông không? (Có/Không)", "Số chỗ tối đa", "Lý do giới hạn",
    "Sức chứa mỗi nhóm", "Số thành viên tối thiểu",
    "Cần kỹ năng tối thiểu không? (Có/Không)", "Loại thử thách", "Mốc tối thiểu (thang 10)",
    "Bảng tiêu chí", "Giữ chỗ (mã học sinh, cách nhau dấu phẩy)",
]
(C_TEN, C_BUOI, C_GIO, C_DIA_DIEM, C_MO_NHOM, C_CHO, C_LY_DO, C_PHONG, C_TOI_THIEU, C_CAN_THI,
 C_THU_THACH, C_MOC, C_TIEU_CHI, C_GIU) = range(len(TIEU_DE_PHIEU))
CAC_NHAN_BAT_BUOC = (C_TEN, C_BUOI, C_MO_NHOM)


class LoiPhieu(ValueError):
    """Tệp phiếu không dùng được (thiếu cột): không ghi tệp nào."""


def _o(v):
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


def _co_khong(v):
    """'Có'/'Yes'/'x' -> True; 'Không'/'No' -> False; trống hoặc lạ -> None."""
    k = so_nhap.bo_dau(v)
    if k in ("co", "yes", "true", "1"):
        return True
    if k in ("khong", "no", "false", "0"):
        return False
    return None


def _nguyen_duong(v):
    try:
        f = float(str(v).replace(",", "."))
    except ValueError:
        return None
    return int(f) if f.is_integer() and f > 0 else None


def doc_tep(duong_xlsx):
    import openpyxl
    wb = openpyxl.load_workbook(duong_xlsx, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    dong = [[_o(x) for x in r] for r in ws.iter_rows(values_only=True)]
    wb.close()
    if not dong:
        raise LoiPhieu("tệp trống")
    thieu = [h for h in TIEU_DE_PHIEU if h not in dong[0]]
    if thieu:
        raise LoiPhieu("tệp thiếu cột: %s. Giữ nguyên tên câu hỏi như hướng dẫn." % "; ".join(thieu))
    vt = [dong[0].index(h) for h in TIEU_DE_PHIEU]
    return [[r[i] if i < len(r) else "" for i in vt] for r in dong[1:] if any(r)]


def _phan_loai(p, ten, loi, canh_bao):
    """Một phiếu -> dict CLB hoặc None (đã ghi lỗi). Ghi `loi`/`canh_bao` theo {ma, clb, ...}."""
    def bao(ds, ma, **kw):
        ds.append({"ma": ma, "clb": ten, **kw})

    mo = _co_khong(p[C_MO_NHOM])
    if mo is None:
        bao(loi, "phieu_thieu_cau_2")
        return None
    toi_thieu = _nguyen_duong(p[C_TOI_THIEU]) if p[C_TOI_THIEU] else None
    if p[C_TOI_THIEU] and toi_thieu is None:
        bao(canh_bao, "phieu_toi_thieu_sai", gia_tri=p[C_TOI_THIEU])
    clb = {"name": ten, "buoi": so_nhap.ma_buoi(p[C_BUOI]), "reserve_capacity": 0}
    if toi_thieu:
        clb["so_toi_thieu"] = toi_thieu
    if mo:
        phong = _nguyen_duong(p[C_PHONG])
        if phong is None:
            bao(loi, "phieu_thieu_phong")
            return None
        if p[C_LY_DO]:
            bao(canh_bao, "phieu_tu_do_co_ly_do_gioi_han", ly_do=p[C_LY_DO])
        clb.update(loai=so_nhap.TU_DO, capacity=phong, suc_chua_phong=phong)
        return clb
    cho = _nguyen_duong(p[C_CHO])
    if cho is None:
        bao(loi, "phieu_thieu_cho")
        return None
    if not p[C_LY_DO]:
        bao(canh_bao, "phieu_thieu_ly_do")
    clb["capacity"] = cho
    thi = _co_khong(p[C_CAN_THI])
    if thi is None:
        bao(canh_bao, "phieu_thieu_cau_4")
    if not thi:
        clb["loai"] = so_nhap.GIOI_HAN
        return clb
    moc = _nguyen_duong(p[C_MOC])
    if moc is None or moc > so_nhap.DIEM_SAN_TOI_DA or not re.fullmatch(r"\d+(\.0+)?", p[C_MOC]):
        bao(loi, "phieu_moc_sai", gia_tri=p[C_MOC])
        return None
    if so_nhap.bo_dau(p[C_THU_THACH]) not in ("trac nghiem",):
        bao(canh_bao, "phieu_thu_thach_khong_tu_cham", thu_thach=p[C_THU_THACH])
    if not p[C_TIEU_CHI]:
        bao(canh_bao, "phieu_thieu_tieu_chi")
    bao(canh_bao, "phieu_cho_duyet_tuyen_chon")
    clb.update(loai=so_nhap.TUYEN_CHON, diem_san=moc)
    return clb


def doc_phieu_clb(duong_xlsx, ky_truoc=None):
    """-> {clubs, giu_cho, loi, canh_bao, kiem_truoc}. `ky_truoc` [{name, buoi, capacity}]: CLB kỳ
    trước chưa nộp phiếu -> GIOI_HAN với chỉ tiêu kỳ trước (V§4.1), kèm cảnh báo."""
    cac_dong = doc_tep(duong_xlsx)
    loi, canh_bao = [], []
    cuoi = {}                                   # tên CLB (không dấu) -> phiếu cuối
    for p in cac_dong:
        if not p[C_TEN]:
            continue
        k = so_nhap.khoa_ten(p[C_TEN])
        if k in cuoi:
            canh_bao.append({"ma": "phieu_nop_nhieu_lan", "clb": p[C_TEN]})
        cuoi[k] = p
    clubs, giu_cho = [], []
    for p in cuoi.values():
        clb = _phan_loai(p, p[C_TEN], loi, canh_bao)
        if clb is None:
            continue
        clb["club_id"] = so_nhap.tao_ma_clb(p[C_TEN])
        clubs.append(clb)
        for s in re.split(r"[,;\s]+", p[C_GIU]):
            if s and (clb["club_id"], s) not in giu_cho:
                giu_cho.append((clb["club_id"], s))
    da_co = {so_nhap.khoa_ten(c["name"]) for c in clubs} | set(cuoi)
    for cu in ky_truoc or []:
        if so_nhap.khoa_ten(cu["name"]) in da_co:
            continue
        clubs.append({"name": cu["name"], "buoi": so_nhap.ma_buoi(cu.get("buoi", "")),
                      "capacity": int(cu["capacity"]), "reserve_capacity": 0,
                      "loai": so_nhap.GIOI_HAN, "club_id": so_nhap.tao_ma_clb(cu["name"])})
        canh_bao.append({"ma": "phieu_mac_dinh_ky_truoc", "clb": cu["name"]})
    dict_clb = {c["club_id"]: c for c in clubs}
    kiem = fa_daa.kiem_truoc_fa(dict_clb, giu_cho, {s for _, s in giu_cho})
    return {"clubs": clubs, "giu_cho": giu_cho, "loi": loi, "canh_bao": canh_bao,
            "kiem_truoc": fa_daa.chi_loi_chan(kiem)}


NOI_DUNG = {
    "phieu_thieu_cau_2": "chưa trả lời câu 2 (mở thêm nhóm được không): không phân loại được, đã bỏ qua",
    "phieu_thieu_phong": "CLB mở thêm nhóm được nhưng chưa ghi sức chứa mỗi nhóm: đã bỏ qua",
    "phieu_thieu_cho": "CLB không mở thêm nhóm nhưng chưa ghi số chỗ tối đa hợp lệ: đã bỏ qua",
    "phieu_moc_sai": "mốc tối thiểu phải là số nguyên từ 1 đến 10: đã bỏ qua",
    "phieu_toi_thieu_sai": "số thành viên tối thiểu không hợp lệ: không ghi",
    "phieu_tu_do_co_ly_do_gioi_han": "khai Tự do nhưng có ghi lý do giới hạn; CLB bị giới hạn thật không được khai Tự do, cần admin xem lại",
    "phieu_thieu_ly_do": "CLB giới hạn chưa ghi lý do (phòng/dụng cụ/người hướng dẫn)",
    "phieu_thieu_cau_4": "chưa trả lời câu 4: coi là không cần kỹ năng (Giới hạn)",
    "phieu_thu_thach_khong_tu_cham": "loại thử thách không phải trắc nghiệm: phần mềm không chấm tự động, admin nhập điểm",
    "phieu_thieu_tieu_chi": "CLB Tuyển chọn chưa ghi bảng tiêu chí",
    "phieu_cho_duyet_tuyen_chon": "CLB Tuyển chọn: chờ ban quản lý duyệt trước khi mở cổng",
    "phieu_nop_nhieu_lan": "nộp phiếu nhiều lần: lấy phiếu cuối cùng",
    "phieu_mac_dinh_ky_truoc": "chưa nộp phiếu: mặc định Giới hạn với chỉ tiêu kỳ trước",
}


def viet_bao_cao(kq, duong):
    dong = ["# Báo cáo Phiếu thiết lập CLB (TH = chưa thử trên Microsoft thật)", ""]
    dem = {}
    for c in kq["clubs"]:
        dem[c["loai"]] = dem.get(c["loai"], 0) + 1
    dong.append("CLB hợp lệ: %d (%s). Giữ chỗ: %d." % (
        len(kq["clubs"]), ", ".join("%s %d" % (so_nhap.NHAN_LOAI_HIEN_THI[k], v) for k, v in sorted(dem.items())),
        len(kq["giu_cho"])))
    for tieu_de, ds in (("Lỗi (CLB bị bỏ qua)", kq["loi"]), ("Cảnh báo", kq["canh_bao"])):
        dong += ["", "## " + tieu_de] + ["- %s: %s" % (x["clb"], NOI_DUNG.get(x["ma"], x["ma"])) for x in ds]
    dong += ["", "## Kiểm trước khi mở cổng"] + (
        ["- " + m for m in format_all(kq["kiem_truoc"])] or ["- không có lỗi chặn"])
    with open(duong, "w", encoding="utf-8") as f:
        f.write("\n".join(dong) + "\n")


def chuyen_phieu(duong_xlsx, thu_muc_ra, ky_truoc=None):
    kq = doc_phieu_clb(duong_xlsx, ky_truoc=ky_truoc)
    os.makedirs(thu_muc_ra, exist_ok=True)
    so = os.path.join(thu_muc_ra, "SO_NHAP_CLB.xlsx")
    so_nhap.ghi_so_nhap(so, clubs=kq["clubs"], giu_cho=kq["giu_cho"] or None)
    bao_cao = os.path.join(thu_muc_ra, "BAO_CAO_PHIEU_CLB.md")
    viet_bao_cao(kq, bao_cao)
    return {"so_nhap": so, "bao_cao": bao_cao, "n_clb": len(kq["clubs"]), "n_loi": len(kq["loi"]),
            "n_canh_bao": len(kq["canh_bao"]), "n_chan": len(kq["kiem_truoc"])}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("tep_xuat", help="Excel xuất từ Phiếu thiết lập CLB")
    ap.add_argument("--ra", required=True, help="thư mục ghi SO_NHAP_CLB.xlsx và BAO_CAO_PHIEU_CLB.md")
    ap.add_argument("--ky-truoc", help="CSV (name,buoi,capacity): CLB kỳ trước, dùng khi chưa nộp phiếu")
    a = ap.parse_args(argv)
    ky = None
    if a.ky_truoc:
        with open(a.ky_truoc, encoding="utf-8-sig", newline="") as f:
            ky = list(csv.DictReader(f))
    try:
        tom = chuyen_phieu(a.tep_xuat, a.ra, ky)
    except LoiPhieu as e:
        print("Lỗi:", e)
        return 2
    print("Xong: %(n_clb)d CLB, %(n_loi)d lỗi, %(n_canh_bao)d cảnh báo, %(n_chan)d lỗi chặn mở cổng." % tom)
    return 1 if tom["n_loi"] or tom["n_chan"] else 0


if __name__ == "__main__":
    sys.exit(main())
