"""GAP-10 (TH = CHƯA thử trên Microsoft thật): danh sách học sinh CHƯA đăng ký, theo lớp, cho GVCN (V§5.2).

    python danh_sach_chua_dang_ky.py DANH_SACH.csv DANG_KY.xlsx --ra THU_MUC

* `DANH_SACH.csv`: cột `student_id`, `class_id` (cột `homeroom_email` có thì bỏ qua ở đây; flow gửi đọc nó).
* `DANG_KY.xlsx|csv`: tệp xuất đăng ký bất kỳ có cột tiêu đề "[student_id] …" (mẫu `bieu_mau.cau_ma_hoc_sinh`) hoặc
  cột `student_id`.
* Ghi `chua_dang_ky_<lớp>.csv` (chỉ `student_id`, `class_id` của em chưa đăng ký; lớp đã đủ thì không có tệp) và
  `tong_hop.csv` (`class_id, n, da_dang_ky, ty_le, co`; `co = DUOI_50` khi tỉ lệ < 50 %).
* In số email một lần gửi GVCN cần (mỗi lớp còn em chưa đăng ký một email) và cảnh báo khi vượt 6.000 yêu cầu mỗi
  người mỗi ngày (giới hạn Power Automate, `docs/he_sinh_thai/T4M_FLOW_NHAC_HAN.md`).

Không đọc điểm, không đọc tên. Dữ liệu trong test là MÔ PHỎNG.
"""
import csv
import os
import re
import sys

NGUONG_DANG_KY = 0.5               # V§5.2: < 50 % sau 3 ngày -> gửi danh sách cho GVCN
GIOI_HAN_YEU_CAU_NGAY = 6000       # Power Automate: 6.000 yêu cầu / người / ngày (ĐXM, T4M_KET_QUA_TAI_LIEU.md)
_KY_TU_CAM = '<>:"/\\|?*'
_TEN_DANH_RIENG = frozenset(["CON", "PRN", "AUX", "NUL"] + ["COM%d" % i for i in range(1, 10)]
                            + ["LPT%d" % i for i in range(1, 10)])
_COT_MA = re.compile(r"^\s*(?:\d+[.)]\s*)?\[student_id\]")
# SG-12: biểu mẫu mới ghi tiêu đề THUẦN (không "[student_id]"); câu mã học sinh không phụ thuộc đề nên nhận thẳng chữ thuần.
_TIEU_DE_MA_THUAN = re.compile(r"^\s*(?:\d+[.)]\s*)?Mã học sinh của em\b")


def _ten_tep(lop):
    """Tên tệp an toàn cho một lớp (cùng luật với `api_xuat._ten_file_an_toan`), tối đa 100 ký tự."""
    ten = "".join("_" if (c in _KY_TU_CAM or ord(c) < 32) else c for c in str(lop or "")).strip(" .")[:100]
    if not ten or ten in (".", ".."):
        return "lop"
    return "_" + ten if ten.split(".")[0].upper() in _TEN_DANH_RIENG else ten


def ty_le_dang_ky(roster, da_dang_ky):
    """roster [{student_id, class_id}], da_dang_ky: tập mã -> [{class_id, n, da_dang_ky, ty_le, co, chua}] sắp theo
    lớp; `chua` là mã em chưa đăng ký (sắp). Mã đăng ký không có trong danh sách bị bỏ. Hàm thuần."""
    lop = {}
    for r in roster:
        lop.setdefault(str(r["class_id"]), []).append(str(r["student_id"]))
    ra = []
    for c in sorted(lop):
        ds = sorted(set(lop[c]))
        co = [s for s in ds if s in da_dang_ky]
        ty_le = len(co) / len(ds)
        ra.append({"class_id": c, "n": len(ds), "da_dang_ky": len(co), "ty_le": ty_le,
                   "co": "DUOI_50" if ty_le < NGUONG_DANG_KY else "", "chua": [s for s in ds if s not in da_dang_ky]})
    return ra


def _hang_cua(duong):
    if duong.lower().endswith((".xlsx", ".xlsm")):
        from openpyxl import load_workbook
        wb = load_workbook(duong, read_only=True, data_only=True)
        return [list(r) for r in wb.worksheets[0].iter_rows(values_only=True)]
    with open(duong, encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def _chu(x):
    if x is None:
        return ""
    if isinstance(x, float) and x.is_integer():
        x = int(x)
    return str(x).strip()


def _la_cot_ma(tieu_de):
    return tieu_de == "student_id" or bool(_COT_MA.match(tieu_de) or _TIEU_DE_MA_THUAN.match(tieu_de))


def doc_da_dang_ky(duong):
    """Tập mã học sinh đã đăng ký trong tệp xuất (xlsx/csv). Không có cột mã -> ValueError."""
    hang = _hang_cua(duong)
    if not hang:
        raise ValueError("tệp rỗng: cần cột [student_id] hoặc student_id")
    i = next((k for k, o in enumerate(hang[0]) if _la_cot_ma(_chu(o))), None)
    if i is None:
        raise ValueError("không thấy cột [student_id] hoặc student_id")
    return {_chu(d[i]) for d in hang[1:] if i < len(d) and _chu(d[i])}


def _ghi(duong, dau, dong):
    with open(duong, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(dau)
        w.writerows(dong)


class LoiDanhSach(ValueError):
    """Danh sách lớp thiếu cột student_id, class_id (khác lỗi của tệp đăng ký)."""


def chua_dang_ky(duong_danh_sach, duong_dang_ky, thu_muc_ra):
    """FA-M10 (TH): làm đúng việc của `main` nhưng trả DỮ LIỆU: {"lop": ty_le_dang_ky(...), "tep": [đường dẫn đã ghi],
    "n_email": số lớp còn em chưa đăng ký, "n_duoi": số lớp dưới ngưỡng, "vuot_gioi_han": bool}.

    Danh sách thiếu cột -> `LoiDanhSach`; tệp đăng ký không đọc được -> ValueError (chưa ghi gì)."""
    with open(duong_danh_sach, encoding="utf-8-sig", newline="") as f:
        roster = [r for r in csv.DictReader(f) if _chu(r.get("student_id"))]
    if not roster or "class_id" not in roster[0]:
        raise LoiDanhSach("danh sách phải có cột student_id, class_id")
    roster = [{"student_id": _chu(r["student_id"]), "class_id": _chu(r["class_id"])} for r in roster]
    try:
        da = doc_da_dang_ky(duong_dang_ky)
    except OSError as e:                                  # như CLI cũ: chỉ lỗi tệp ĐĂNG KÝ được báo gọn
        raise ValueError(str(e)) from e
    kq = ty_le_dang_ky(roster, da)
    os.makedirs(thu_muc_ra, exist_ok=True)
    da_dung, tep = set(), []
    for r in kq:
        if not r["chua"]:
            continue
        ten = _ten_tep(r["class_id"])
        goc, k = ten, 2
        while ten.lower() in da_dung:
            ten, k = "%s_%d" % (goc, k), k + 1
        da_dung.add(ten.lower())
        tep.append(os.path.join(thu_muc_ra, "chua_dang_ky_%s.csv" % ten))
        _ghi(tep[-1], ["student_id", "class_id"], [[s, r["class_id"]] for s in r["chua"]])
    tep.append(os.path.join(thu_muc_ra, "tong_hop.csv"))
    _ghi(tep[-1], ["class_id", "n", "da_dang_ky", "ty_le", "co"],
         [[r["class_id"], r["n"], r["da_dang_ky"], round(r["ty_le"], 3), r["co"]] for r in kq])
    n_email = sum(1 for r in kq if r["chua"])
    return {"lop": kq, "tep": tep, "n_email": n_email, "n_duoi": sum(1 for r in kq if r["co"]),
            "vuot_gioi_han": n_email > GIOI_HAN_YEU_CAU_NGAY}


def main(argv=None):
    """Danh sách chưa đăng ký theo lớp + bảng tổng hợp tỉ lệ (GAP-10, TH)."""
    import argparse
    ap = argparse.ArgumentParser(description=main.__doc__)
    ap.add_argument("danh_sach", help="CSV: student_id, class_id[, homeroom_email]")
    ap.add_argument("dang_ky", help="tệp xuất đăng ký (.xlsx hoặc .csv) có cột [student_id]")
    ap.add_argument("--ra", required=True, help="thư mục ghi")
    a = ap.parse_args(argv)
    try:
        kq = chua_dang_ky(a.danh_sach, a.dang_ky, a.ra)
    except LoiDanhSach as e:
        print(e, file=sys.stderr)
        return 1
    except ValueError as e:
        print("tệp đăng ký: %s" % e, file=sys.stderr)
        return 1
    print("%d lớp, %d lớp dưới 50 %%; gửi GVCN cần %d email -> %s" % (len(kq["lop"]), kq["n_duoi"], kq["n_email"], a.ra))
    if kq["vuot_gioi_han"]:
        print("CẢNH BÁO: VƯỢT %d yêu cầu/người/ngày của Power Automate: chia làm nhiều ngày hoặc gộp theo khối "
              "(xem T4M_FLOW_NHAC_HAN.md)." % GIOI_HAN_YEU_CAU_NGAY)
    return 0


if __name__ == "__main__":
    sys.exit(main())
