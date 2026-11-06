# -*- coding: utf-8 -*-
"""T4M-BK3: bảng cấu hình flow `DaLam_<ClubId>` (một hàng mỗi CLB CÓ đề thi) + biểu thức để dán.

Nguồn: `de_thi.json` (qua `bieu_mau.clb_co_thi`), thiết kế flow: `T4M_FLOW_DA_LAM.md` §3, §4.
Không sinh gói flow `.zip` (quyết định 3 của `T4M_KE_HOACH_TU_DONG.md` §9, KQ §8.3): IT dựng tay một flow mẫu,
xuất gói, nhân bản; bộ dựng chỉ giao bảng cần đổi hai thứ mỗi bản sao (Form Id, hằng ClubId).

TH: chưa chạy trên Power Apps / SharePoint / Power Automate.
"""

import csv
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bieu_mau as bm  # noqa: E402

TIEN_TO_DOCX = "NHAP_FORMS_MOI_CLB_"          # = tao_mau_forms.TIEN_TO_DOCX_MOI_CLB (test so khớp)
DONG_TH = "TH: chưa chạy trên Power Apps / SharePoint"
TIEU_DE_CSV = ["Flow", "ClubId", "Ten", "Buoi", "FormId", "ChuBieuMau", "DaThuNgay", "TepQuickImport"]


def hang_flow(de):
    """Một hàng mỗi CLB có đề; các ô của IT (FormId, ChuBieuMau, DaThuNgay) để trống."""
    return [{"Flow": "DaLam_" + c["club_id"], "ClubId": c["club_id"], "Ten": c["name"],
             "Buoi": bm.ten_buoi(de, c["buoi"]), "FormId": "", "ChuBieuMau": "", "DaThuNgay": "",
             "TepQuickImport": "%s%s.docx" % (TIEN_TO_DOCX, c["club_id"])}
            for c in bm.clb_co_thi(de)]


def tao_csv(de):
    """CSV UTF-8 có BOM, CRLF (như CLB.csv) để mở thẳng bằng Excel."""
    bo_nho = io.StringIO(newline="")
    w = csv.DictWriter(bo_nho, fieldnames=TIEU_DE_CSV, lineterminator="\r\n")
    w.writeheader()
    w.writerows(hang_flow(de))
    return bo_nho.getvalue()


def tao_md(de):
    hang = hang_flow(de)
    L = []
    w = L.append
    w(DONG_TH + " (Power Automate). Nguồn: `T4M_FLOW_DA_LAM.md` §3, §4; `de_thi.json`.")
    w("")
    w("# Bảng cấu hình flow `DaLam_<ClubId>` (T4M-BK3)")
    w("")
    w("> **Nháp chưa chạy.** Tên hành động và biểu thức nhãn **GĐ**; mọi bước dựng nhãn **TH**. Dữ liệu là MÔ PHỎNG.")
    w("> Bộ dựng **không có gói flow `.zip`** và **không tự chế** định dạng gói (quyết định 3): IT dựng tay MỘT flow mẫu,")
    w("> thử trọn, **Save as** hoặc **Export > Package (.zip)** rồi nhập lại cho từng CLB trong bảng dưới. Mỗi bản sao")
    w("> đổi đúng **hai thứ**: `Form Id` (bước 1 và 2) và hằng `ClubId` (bước 5). Có quyền Environment Maker và")
    w("> nhập gói kiểu cũ có bị chặn không: **HỎI-IT** (KQ §8.3).")
    w("")
    w("## 1. Bảng flow: %d flow = %d CLB có đề thi" % (len(hang), len(hang)))
    w("")
    w("Cùng nội dung ở `BANG_FLOW.csv`. Ba cột trống là của IT (không đưa vào kho mã).")
    w("")
    w("| Flow | ClubId | Tên | Buổi | Form Id | Chủ biểu mẫu | Đã thử (ngày) | Tệp Quick Import |")
    w("|---|---|---|---|---|---|---|---|")
    for h in hang:
        w("| `%s` | `%s` | %s | %s | | | | `%s` |" % (h["Flow"], h["ClubId"], h["Ten"], h["Buoi"], h["TepQuickImport"]))
    w("")
    w("Soát sau khi nhân: mỗi `Form Id` xuất hiện **đúng một lần**; mỗi `ClubId` có **đúng một** flow (hai flow cùng")
    w("biểu mẫu sẽ ghi dòng trùng). `ClubId` phải trùng **từng ký tự** với cột `ClubId` của list `CLB` (R17).")
    w("")
    w("## 2. Biểu thức và cấu hình để dán (GĐ)")
    w("")
    w("Chọn giá trị **từ bảng Dynamic content** của Power Automate khi có thể; tên hành động trong biểu thức phụ thuộc tên")
    w("IT đặt cho bước (GĐ). Tên trường `responder`, `submitDate` theo `T4M_FLOW_DA_LAM.md` §3 (GĐ, kiểm khi dựng).")
    w("")
    w("| # | Hành động | Ô | Giá trị (GĐ) |")
    w("|---|---|---|---|")
    w("| 1 | Forms **When a new response is submitted** | Form Id | `Form Id` của hàng CLB (biểu mẫu nhóm/Teams: dán tay) |")
    w("| 2 | Forms **Get response details** | Form Id; Response Id | `Form Id` như bước 1; `Response Id` từ trigger |")
    w("| 3 | SharePoint **Get items** (list `BaiThi`), tuỳ chọn | Filter Query; Top Count | `ResponseId eq '<Response Id của bước 2>'`; `1` |")
    w("| 4 | Điều kiện, tuỳ chọn | | số mục của bước 3 bằng 0; ngược lại dừng |")
    w("| 5 | SharePoint **Create item** (list `BaiThi`) | `Email` | `toLower(<responder của bước 2>)` |")
    w("| 5 | | `ClubId` | **hằng chữ cố định** = cột `ClubId` của hàng CLB (vd. `%s`) |" % (hang[0]["ClubId"] if hang else ""))
    w("| 5 | | `ResponseId` | `Response Id` của bước 2 |")
    w("| 5 | | `NopLuc` | `submitDate` của bước 2 |")
    w("| 6 | Nhánh lỗi (Run after: has failed) của bước 2, 5 | list `NHAT_KY_DA_LAM` | `ClubId` (hằng), `ResponseId`, `Gio`, `KetQua` = `loi`; không ghi email hay nội dung bài |")
    w("")
    w("Không đọc câu trả lời, không lưu điểm (mức 5a). Chủ flow: tài khoản dịch vụ của IT; có hay không: **HỎI-IT**.")
    w("Hạn mức 6.000 yêu cầu mỗi ngày của chủ flow cộng dồn mọi flow (`T4M_FLOW_DA_LAM.md` §5, ƯL).")
    w("")
    w("## 3. Thử (TH)")
    w("")
    w("Một biểu mẫu thử, list `BaiThi_THU`, tài khoản thử: nộp 1 bài thì **đúng 1 dòng** `BaiThi` với `Email` chữ thường,")
    w("`ClubId` đúng, `NopLuc` hợp lý (HDT 13.2, R17). Chỉ sau khi mẫu qua thử mới nhân bản.")
    w("")
    return "\n".join(L)


def ghi(d_flow, de):
    """Ghi BANG_FLOW.md và BANG_FLOW.csv vào `d_flow`; trả danh sách tên tệp."""
    os.makedirs(d_flow, exist_ok=True)
    with open(os.path.join(d_flow, "BANG_FLOW.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(tao_md(de))
    with open(os.path.join(d_flow, "BANG_FLOW.csv"), "w", encoding="utf-8-sig", newline="") as f:
        f.write(tao_csv(de))
    return ["BANG_FLOW.csv", "BANG_FLOW.md"]
