"""T4M-M3: đối chiếu hai lần xuất List đăng ký (đợt bổ sung) — chỉ đọc, không đụng kiosk.

    python mau_forms_thi_clb/doi_chieu_lists.py CU.csv MOI.csv [--co-so CS1] [--ra bao_cao.xlsx] [--de de_thi.json]

Liệt kê: em MỚI (có ở MOI, không có ở CU), em RÚT (có ở CU, không có ở MOI), dòng ĐỔI nguyện vọng
(NV1..NVn của một em ở một ngày, kể cả thứ tự), đổi Lớp, đổi CoSo. Khoá: Email chữ thường + Thu
(cùng cách đọc với bộ chuyển đổi: dùng lại `doc_lists`). Thứ tự dòng và hoa/thường của email không phải
thay đổi. Ngày không có nguyện vọng và ngày không có dòng là như nhau.

So sánh nguyện vọng dùng giá trị THÔ của NV1..NVn (bỏ khoảng trắng, phân biệt hoa/thường), không lọc
theo de_thi.json: mã CLB gõ sai hoặc thiếu trong de_thi.json không được giấu thay đổi. Các ô đó chỉ
được ĐẾM và báo ở dòng đầu ("CẢNH BÁO: ..."), kèm cảnh báo của `doc_lists`.

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


def _doc_tho(duong, de, co_so=None):
    """{email chữ thường: {name, lop, co_so, nv: {buoi: [giá trị thô NV1..NVn không trống]}}}.

    Cùng luật khoá với `doc_lists` (email chữ thường, dòng trùng (em, ngày) giữ dòng ĐẦU, `co_so`
    lọc theo ô CoSo) nhưng KHÔNG kiểm mã CLB. Cột bắt buộc đã được `doc_lists` kiểm trước."""
    with open(duong, encoding="utf-8-sig", newline="") as f:
        bang = list(csv.reader(f))
    tieu = [h.strip().lower() for h in bang[0]]
    i_e, i_t = tieu.index("email"), tieu.index("thu")
    i_ten = next((tieu.index(k) for k in ("hoten", "name") if k in tieu), None)
    i_lop = next((tieu.index(k) for k in ("lop", "lớp") if k in tieu), None)
    i_cs = tieu.index("coso") if "coso" in tieu else None
    cot_nv = [i for _n, i in sorted((int(h[2:]), i) for i, h in enumerate(tieu)
                                    if h.startswith("nv") and h[2:].isdigit())]
    ket = {}
    for dong in bang[1:]:
        dong = [x.strip() for x in dong] + [""] * (len(tieu) - len(dong))
        email = dong[i_e].lower()
        if not email:
            continue
        if co_so is not None and dong[i_cs].lower() != co_so.strip().lower():
            continue
        buoi = cv._ma_buoi_tu_thu(de, dong[i_t]) or dong[i_t]
        hs = ket.setdefault(email, {"name": "", "lop": "", "co_so": "", "nv": {}})
        if i_ten is not None and not hs["name"]:
            hs["name"] = dong[i_ten]
        if i_lop is not None and not hs["lop"]:
            hs["lop"] = dong[i_lop]
        if i_cs is not None and not hs["co_so"]:
            hs["co_so"] = dong[i_cs]
        if buoi in hs["nv"]:
            continue
        hs["nv"][buoi] = [dong[i] for i in cot_nv if dong[i]]
    return ket


def _chuan(s):
    return " ".join((s or "").split()).casefold()


def doi_chieu(duong_cu, duong_moi, de=None, co_so=None):
    """Trả {"muc": [...], "canh_bao": [...], "n_clb_la": số ô mã CLB lạ ở cả hai tệp}. Mỗi mục: loai, email, ten, thu, cu, moi.

    Ném `cv.LoiTepXuat` nếu một tệp thiếu cột bắt buộc (không ghi gì)."""
    de = de or bm.doc_de_thi()
    # doc_lists: kiểm cột bắt buộc / --co-so (ném LoiTepXuat) và sinh cảnh báo; KHÔNG dùng để so sánh.
    _, canh_cu = cv.doc_lists(duong_cu, de, co_so)
    _, canh_moi = cv.doc_lists(duong_moi, de, co_so)
    cu, moi = _doc_tho(duong_cu, de, co_so), _doc_tho(duong_moi, de, co_so)
    n_la = sum(1 for c in canh_cu + canh_moi if "không phải CLB nào" in c[2])
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
        for buoi in sorted(set(a["nv"]) | set(b["nv"])):
            x, y = a["nv"].get(buoi, []), b["nv"].get(buoi, [])
            if x != y:
                them("doi_nv", email, ten, buoi, ", ".join(x), ", ".join(y))
        if _chuan(a["lop"]) != _chuan(b["lop"]):
            them("doi_lop", email, ten, "", a["lop"], b["lop"])
        if _chuan(a["co_so"]) != _chuan(b["co_so"]):
            them("doi_co_so", email, ten, "", a["co_so"], b["co_so"])
    muc.sort(key=lambda m: (LOAI.index(m["loai"]), m["email"], m["thu"]))
    canh_bao = [("CU",) + c for c in canh_cu] + [("MOI",) + c for c in canh_moi]
    return {"muc": muc, "canh_bao": canh_bao, "n_clb_la": n_la}


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
    if kq["n_clb_la"]:
        ws2.append(["", "", "", "CẢNH BÁO: %d ô có mã CLB không có trong de_thi.json — kiểm trước khi "
                    "tin kết quả đối chiếu" % kq["n_clb_la"]])
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
    if kq["n_clb_la"]:
        print("CẢNH BÁO: %d ô có mã CLB không có trong de_thi.json — kiểm trước khi tin kết quả đối chiếu"
              % kq["n_clb_la"])
        print("(nguyện vọng vẫn được so sánh theo giá trị thô; xem danh sách cảnh báo bên dưới)\n")
    if not kq["muc"]:
        print("Không có thay đổi giữa hai tệp." if not kq["n_clb_la"] else
              "Không thấy thay đổi nguyện vọng, em rút hay em mới trong giá trị thô của hai tệp.")
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
