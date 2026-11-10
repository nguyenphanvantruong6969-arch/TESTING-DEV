"""FA-9: biên bản bốc thăm có người chứng kiến (D5 — không có hạt giống công khai).

Một trang để in/ký (HTML sẵn sàng in ra PDF). Chỉ chứa: kỳ, thời điểm, dấu vân tay dữ liệu, hạt giống, SHA-256
của danh sách (mã học sinh, số bốc thăm) đã sắp xếp, số liệu từng buổi, dòng ký của quản trị viên và giáo viên
chứng kiến. KHÔNG có tên hay mã học sinh. Hàm thuần (không đọc CSDL): `api_xuat.export_bien_ban_boc_tham` đọc rồi gọi.
"""

import hashlib
import html

THU_TU_LE = (
    "Chốt dữ liệu và in dấu vân tay dữ liệu (ô bên dưới) trước khi nhập hạt giống.",
    "Giáo viên chứng kiến chọn hạt giống (ví dụ gieo xúc xắc sáu lần) và tự gõ vào máy.",
    "Chạy xếp. Số bốc thăm được khoá, chạy lại cùng dữ liệu và hạt giống cho đúng các số này.",
    "Quản trị viên và giáo viên chứng kiến cùng ký biên bản này.",
)


def sha256_stb(cap):
    """SHA-256 (hex) của danh sách (student_id, stb_number) sắp theo mã học sinh. Đổi MỘT số là đổi mã băm."""
    h = hashlib.sha256()
    for sid, stb in sorted((str(s), int(n)) for s, n in cap):
        h.update(("%s\t%d\n" % (sid, stb)).encode("utf-8"))
    return h.hexdigest()


def tao_ban_ghi(ky, thoi_diem, dau_van_tay, hat_giong, cap_stb, dem_theo_buoi, ket_qua_con_khop=True, fa_daa=False):
    """Bản ghi (dict) của biên bản. Cùng dữ liệu + hạt giống -> giống hệt nhau, trừ `thoi_diem`."""
    return {
        "ky": ky or "",
        "thoi_diem": thoi_diem,
        "dau_van_tay_du_lieu": dau_van_tay,
        "hat_giong": hat_giong,
        "sha256_stb": sha256_stb(cap_stb),
        "so_hoc_sinh_co_stb": len(cap_stb),
        "dem_theo_buoi": {b: dict(v) for b, v in sorted(dem_theo_buoi.items())},
        "ket_qua_con_khop": bool(ket_qua_con_khop),
        "fa_daa": bool(fa_daa),
    }


def html_bien_ban(bg):
    """HTML một trang từ bản ghi `tao_ban_ghi` (tiếng Việt, dễ in)."""
    e = html.escape
    dong_buoi = "".join(
        "<tr><td>%s</td><td>%d</td><td>%d</td></tr>" % (e(str(b)), v["n_hoc_sinh"], v["n_xep"])
        for b, v in bg["dem_theo_buoi"].items())
    le = "".join("<li>%s</li>" % e(x) for x in THU_TU_LE)
    canh_bao = "" if bg["ket_qua_con_khop"] else (
        '<p class="canh-bao">Dữ liệu đã sửa sau lần chạy này: dấu vân tay hiện tại khác dấu vân tay bên dưới. '
        "Hãy chạy lại xếp rồi xuất biên bản mới.</p>")
    return (
        '<!doctype html>\n<html lang="vi"><head><meta charset="utf-8">'
        "<title>Biên bản bốc thăm</title>"
        "<style>body{font:15px/1.5 sans-serif;max-width:720px;margin:2rem auto;padding:0 1rem}"
        "table{border-collapse:collapse;width:100%%}td,th{border:1px solid #888;padding:.3rem .5rem;text-align:left}"
        "code{word-break:break-all}.ky{display:flex;gap:2rem;margin-top:3rem}.ky div{flex:1;border-top:1px solid #000;"
        "padding-top:.3rem}.canh-bao{border:2px solid #b00;padding:.5rem}@media print{body{margin:0}}</style></head><body>"
        "<h1>Biên bản bốc thăm</h1>"
        "<p>Kỳ: <b>%s</b><br>Thời điểm xuất: %s%s</p>%s"
        "<h2>Thứ tự buổi lễ</h2><ol>%s</ol>"
        "<h2>Số liệu</h2>"
        "<p>Dấu vân tay dữ liệu: <code>%s</code></p>"
        "<p>Hạt giống: <b>%s</b></p>"
        "<p>SHA-256 của danh sách (mã học sinh, số bốc thăm) đã sắp xếp, %d học sinh:<br><code>%s</code></p>"
        "<table><thead><tr><th>Buổi</th><th>Số học sinh</th><th>Số dòng xếp</th></tr></thead><tbody>%s</tbody></table>"
        '<div class="ky"><div>Quản trị viên (ký, ghi họ tên)</div><div>Giáo viên chứng kiến (ký, ghi họ tên)</div></div>'
        "</body></html>\n"
    ) % (e(bg["ky"]), e(bg["thoi_diem"]), " · xếp theo loại CLB và huy chương" if bg["fa_daa"] else "",
         canh_bao, le, e(bg["dau_van_tay_du_lieu"]), e(str(bg["hat_giong"])), bg["so_hoc_sinh_co_stb"],
         bg["sha256_stb"], dong_buoi)


def ghi_xlsx(bg, duong):
    """FA-9b: bản Excel của CÙNG bản ghi (`tao_ban_ghi`): cùng các mục như `html_bien_ban`, không mã/tên học sinh.
    Hàm thuần theo nghĩa không đọc CSDL; chỉ ghi tệp `duong`."""
    from openpyxl import Workbook
    from openpyxl.styles import Font
    from openpyxl.styles import Alignment

    from so_excel import lam_sach

    wb = Workbook()
    ws = wb.active
    # SM-1: ký tự openpyxl cấm (dán từ Word, tệp .zip) bị bỏ như so_excel.Trang.o, không làm hỏng cả lần xuất

    def them(hang):
        ws.append([lam_sach(x) for x in hang])

    ws.title = "Biên bản bốc thăm"
    dam = Font(bold=True)
    them(["Biên bản bốc thăm"])
    ws["A1"].font = Font(bold=True, size=14)
    them(["Kỳ", bg["ky"]])
    them(["Thời điểm xuất", bg["thoi_diem"]])
    if bg["fa_daa"]:
        them(["Chế độ", "xếp theo loại CLB và huy chương"])
    if not bg["ket_qua_con_khop"]:
        them(["CẢNH BÁO", "Dữ liệu đã sửa sau lần chạy này: dấu vân tay hiện tại khác dấu vân tay bên dưới. "
                   "Hãy chạy lại xếp rồi xuất biên bản mới."])
    them([])
    them(["Thứ tự buổi lễ"])
    ws.cell(ws.max_row, 1).font = dam
    for i, x in enumerate(THU_TU_LE, 1):
        them([i, x])
    them([])
    them(["Số liệu"])
    ws.cell(ws.max_row, 1).font = dam
    them(["Dấu vân tay dữ liệu", bg["dau_van_tay_du_lieu"]])
    them(["Hạt giống", bg["hat_giong"]])
    them(["Số học sinh có số bốc thăm", bg["so_hoc_sinh_co_stb"]])
    them(["SHA-256 của danh sách (mã học sinh, số bốc thăm) đã sắp xếp", bg["sha256_stb"]])
    them([])
    them(["Buổi", "Số học sinh", "Số dòng xếp"])
    for c in ws[ws.max_row]:
        c.font = dam
    for b, v in bg["dem_theo_buoi"].items():
        them([str(b), v["n_hoc_sinh"], v["n_xep"]])
    them([])
    them([])
    them(["Quản trị viên (ký, ghi họ tên)", "", "Giáo viên chứng kiến (ký, ghi họ tên)"])
    ws.column_dimensions["A"].width = 46
    ws.column_dimensions["B"].width = 70
    ws.column_dimensions["C"].width = 40
    for row in ws.iter_rows():
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top", horizontal="left")
            # FA-P1: tên kỳ / tên buổi do người dùng đặt; "=..." không được thành công thức (như so_excel.Trang.o)
            if c.data_type == "f":
                c.data_type = "s"
                c.quotePrefix = True
    wb.save(duong)
