"""T4M-M3: đối chiếu hai lần xuất List đăng ký (đợt bổ sung) — chỉ đọc, không đụng kiosk.

    python mau_forms_thi_clb/doi_chieu_lists.py CU.csv MOI.csv [--co-so CS1] [--ra bao_cao.xlsx] [--de de_thi.json]

Liệt kê: em MỚI (có ở MOI, không có ở CU), em RÚT (có ở CU, không có ở MOI), dòng ĐỔI nguyện vọng
(NV1..NVn của một em ở một ngày, kể cả thứ tự), đổi Lớp, đổi CoSo. Khoá: Email chữ thường + Thu
(cùng cách đọc với bộ chuyển đổi: dùng lại `doc_lists`). Thứ tự dòng và hoa/thường của email không phải
thay đổi. Ngày không có nguyện vọng và ngày không có dòng là như nhau.

Dùng trước khi chạy lại: biết em nào bị ảnh hưởng, rồi mới xuất lại → chuyển đổi → nạp → chạy lại
(T4M_VAN_HANH_MOT_DOT.md bước 8). Công cụ này không nạp lõi, không mở CSDL, không ghi vào kiosk.
"""

import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bieu_mau as bm  # noqa: E402
import chuyen_forms_sang_phan_mem as cv  # noqa: E402

LOAI = ("moi", "rut", "doi_nv", "doi_lop", "doi_co_so")
NHAN_LOAI = {"moi": "Em mới", "rut": "Em rút", "doi_nv": "Đổi nguyện vọng",
             "doi_lop": "Đổi lớp", "doi_co_so": "Đổi cơ sở"}


def _co_so_theo_email(duong):
    """{email chữ thường: CoSo} (ô CoSo không trống đầu tiên); {} nếu tệp không có cột CoSo."""
    with open(duong, encoding="utf-8-sig", newline="") as f:
        bang = list(csv.reader(f))
    if not bang:
        return {}
    tieu = [h.strip().lower() for h in bang[0]]
    if "email" not in tieu or "coso" not in tieu:
        return {}
    i_e, i_c = tieu.index("email"), tieu.index("coso")
    ket = {}
    for dong in bang[1:]:
        dong = dong + [""] * (len(tieu) - len(dong))
        email, cs = dong[i_e].strip().lower(), dong[i_c].strip()
        if email and cs and email not in ket:
            ket[email] = cs
    return ket


def _chuan(s):
    return " ".join((s or "").split()).casefold()


def doi_chieu(duong_cu, duong_moi, de=None, co_so=None):
    """Trả {"muc": [...], "canh_bao": [...]}. Mỗi mục: loai, email, ten, thu, cu, moi.

    Ném `cv.LoiTepXuat` nếu một tệp thiếu cột bắt buộc (không ghi gì)."""
    de = de or bm.doc_de_thi()
    cu, canh_cu = cv.doc_lists(duong_cu, de, co_so)
    moi, canh_moi = cv.doc_lists(duong_moi, de, co_so)
    cs_cu, cs_moi = _co_so_theo_email(duong_cu), _co_so_theo_email(duong_moi)
    muc = []

    def them(loai, email, ten, thu="", truoc="", sau=""):
        muc.append({"loai": loai, "email": email, "ten": ten, "thu": thu, "cu": truoc, "moi": sau})

    for email in sorted(set(moi) - set(cu)):
        them("moi", email, moi[email]["name"])
    for email in sorted(set(cu) - set(moi)):
        them("rut", email, cu[email]["name"])
    for email in sorted(set(cu) & set(moi)):
        a, b = cu[email], moi[email]
        ten = b["name"] or a["name"]
        for buoi in sorted(set(a["nguyen_vong"]) | set(b["nguyen_vong"])):
            x, y = a["nguyen_vong"].get(buoi, []), b["nguyen_vong"].get(buoi, [])
            if x != y:
                them("doi_nv", email, ten, buoi, ", ".join(x), ", ".join(y))
        if _chuan(a["lop"]) != _chuan(b["lop"]):
            them("doi_lop", email, ten, "", a["lop"], b["lop"])
        if _chuan(cs_cu.get(email, "")) != _chuan(cs_moi.get(email, "")):
            them("doi_co_so", email, ten, "", cs_cu.get(email, ""), cs_moi.get(email, ""))
    muc.sort(key=lambda m: (LOAI.index(m["loai"]), m["email"], m["thu"]))
    canh_bao = [("CU",) + c for c in canh_cu] + [("MOI",) + c for c in canh_moi]
    return {"muc": muc, "canh_bao": canh_bao}


def ghi_bao_cao(kq, duong):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Đối chiếu"
    ws.append(["Loại", "Email", "Họ tên", "Buổi", "Cũ", "Mới"])
    for m in kq["muc"]:
        ws.append([NHAN_LOAI[m["loai"]], m["email"], m["ten"], m["thu"], m["cu"], m["moi"]])
    ws2 = wb.create_sheet("Cảnh báo")
    ws2.append(["Tệp", "Dòng", "Email", "Nội dung"])
    for c in kq["canh_bao"]:
        ws2.append(list(c))
    for w in (ws, ws2):
        for i in range(1, w.max_column + 1):
            w.column_dimensions[get_column_letter(i)].width = 30 if i > 1 else 18
            w.cell(1, i).font = Font(bold=True, color="FFFFFF")
            w.cell(1, i).fill = PatternFill("solid", fgColor="1F3A5F")
        w.freeze_panes = "A2"
    wb.save(duong)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cu", help="tệp CSV xuất List lần trước")
    ap.add_argument("moi", help="tệp CSV xuất List lần này")
    ap.add_argument("--co-so", help="chỉ đối chiếu em có cột CoSo bằng giá trị này, ví dụ CS1")
    ap.add_argument("--ra", help="ghi báo cáo .xlsx (sheet 'Đối chiếu' và 'Cảnh báo')")
    ap.add_argument("--de", default=bm.DE_THI_MAC_DINH, help="de_thi.json")
    a = ap.parse_args(argv)
    try:
        kq = doi_chieu(a.cu, a.moi, bm.doc_de_thi(a.de), a.co_so)
    except (bm.LoiDeThi, cv.LoiTepXuat) as e:
        print("KHÔNG GHI TỆP NÀO — %s" % e, file=sys.stderr)
        return 1
    dem = {k: sum(1 for m in kq["muc"] if m["loai"] == k) for k in LOAI}
    if not kq["muc"]:
        print("Không có thay đổi giữa hai tệp.")
    else:
        print("%d em mới, %d em rút, %d dòng đổi nguyện vọng, %d đổi lớp, %d đổi cơ sở."
              % (dem["moi"], dem["rut"], dem["doi_nv"], dem["doi_lop"], dem["doi_co_so"]))
        for m in kq["muc"]:
            print("  %-16s %s %s %s -> %s" % (NHAN_LOAI[m["loai"]], m["email"], m["thu"],
                                             m["cu"] or "(trống)", m["moi"] or "(trống)"))
    if kq["canh_bao"]:
        print("\n%d cảnh báo khi đọc:" % len(kq["canh_bao"]))
        for t, dong, email, nd in kq["canh_bao"]:
            print("  [%s] dòng %s %s: %s" % (t, dong, email, nd))
    if a.ra:
        ghi_bao_cao(kq, a.ra)
        print("\nĐã ghi %s" % a.ra)
    return 0


if __name__ == "__main__":
    sys.exit(main())
