# -*- coding: utf-8 -*-
"""T4M-BK4: sinh `HUONG_DAN_IT.md`: thứ tự dựng, mỗi bước một dòng pass/fail trỏ về R1..R38 và HDT §9.

Nguồn sự thật: `T4M_KET_QUA_TAI_LIEU.md` §8 (cách A/B/C, quyền, nhãn), `T4M_DAC_TA_SUA_APP.md` §7, §10.4, §11 (R1..R38),
`T4M_HUONG_DAN_THU.md` §9 (HDT). Chuỗi dựng: lists -> CLB.FormUrl -> công thức app -> flow -> vòng thử.
Mọi thứ chạm Microsoft nhãn TH; điều không có trong KQ §8 nhãn GĐ/TH. Không dữ liệu thật, tenantId, URL, tên người.
"""

DONG_TH = "TH: chưa chạy trên Power Apps / SharePoint"

# R1..R38: tiêu đề ngắn (tóm tắt cột "Việc" của T4M_DAC_TA_SUA_APP.md §7, §10.4, §11; chi tiết kiểm ở tài liệu đó)
R_NHAN = {
    1: "chỉ thấy dòng của mình, kể cả email viết hoa", 2: "mỗi ngày có min(7, số CLB của ngày) ô NV",
    3: "không chọn trùng CLB trong một ngày", 4: "không ô trống chen giữa", 5: "ngày trống hợp lệ",
    6: "Gửi ghi đủ 5 dòng", 7: "lỗi nửa chừng được báo đúng ngày", 8: "khoá theo TrangThai",
    9: "chỉ phép lọc uỷ quyền được", 10: "hai ngôn ngữ", 11: "điện thoại", 12: "khôi phục phiên bản",
    13: "tệp xuất qua bộ chuyển đổi không cảnh báo (phần Lists)", 14: "không dữ liệu thật trong kho mã",
    15: "Thi tuyển chỉ hiện CLB có đề đã tick", 16: "nút Làm bài mở đúng biểu mẫu", 17: "\"Đã làm\" xuất hiện sau khi nộp",
    18: "không nút khi đã làm hoặc đã khoá", 19: "không hiện điểm", 20: "Thi tuyển chỉ lọc uỷ quyền được",
    21: "mỗi em chỉ thấy bài của mình", 22: "Thi tuyển: hai ngôn ngữ, điện thoại", 23: "màn Thi tuyển trống không lỗi",
    24: "học sinh không ghi được BaiThi", 25: "ô tick Thi chỉ ở CLB có đề", 26: "tối đa 5 tick mỗi ngày",
    27: "đổi/xoá NVk thì xoá THIk, WPk", 28: "hai khung điểm theo tick", 29: "bộ đếm Đã dùng X / 100",
    30: "khung một CLB tự điền 100; khung rỗng không đòi điểm", 31: "chặn Gửi khi khung không rỗng khác 100",
    32: "ô điểm chỉ nhận số nguyên không âm", 33: "một lần Gửi vẫn 5 Patch, đủ ba nhóm cột",
    34: "khoá tắt tick và ô điểm", 35: "thẻ Thi tuyển theo tick", 36: "FormUrl khớp de_thi.json",
    37: "tệp xuất qua bộ chuyển đổi không cảnh báo tick/điểm", 38: "hai ngôn ngữ và điện thoại cho nhãn mới",
}

HOI_IT = [
    "Quản trị SharePoint có đăng ký site script được không (cách B)?",
    "Trường đã có ứng dụng Entra dùng cho PnP PowerShell chưa (cách A)? Ai đăng ký được?",
    "IT có vai trò Environment Maker ở môi trường đích không, và nhập gói flow kiểu cũ có bị chặn không?",
    "Có tài khoản dịch vụ làm chủ flow và chủ biểu mẫu không (chủ rời tổ chức thì flow về hồ sơ Low)?",
    "Chính sách DLP xếp Forms và SharePoint chung nhóm không? Giá trị thật của CoSo, CapDo, Goi, Thu?",
    "Quyền của học sinh với list BaiThi, NHAT_KY_DA_LAM, CLB: chỉ đọc hay không có quyền?",
]


def _pass_fail(L, viec, r=(), hdt=()):
    """Một dòng pass/fail. `r`: số R; `hdt`: dòng HDT §9."""
    tro = []
    if r:
        tro.append("R" + ", R".join(str(x) for x in r))
    if hdt:
        tro.append(", ".join("HDT %s" % h for h in hdt))
    L.append("- ☐ Pass ☐ Fail — %s%s" % (viec, " (" + "; ".join(tro) + ")" if tro else ""))


def _r_chi_tiet(L, nhom):
    """Danh sách R kèm tiêu đề ngắn; mỗi R một dòng pass/fail."""
    for r in nhom:
        L.append("- ☐ Pass ☐ Fail — R%d: %s" % (r, R_NHAN[r]))


def tao(de, n_hanh_dong, hang_flow, tran_dong_bo=30, tran_khong_dong_bo=300):
    n_flow = len(hang_flow)
    clb_co_de = ", ".join("`%s`" % h["ClubId"] for h in hang_flow)
    L = []
    w = L.append
    w(DONG_TH + " / Power Automate. Nguồn: `T4M_KET_QUA_TAI_LIEU.md` §8, `T4M_DAC_TA_SUA_APP.md` §7, §10.4, §11, `T4M_HUONG_DAN_THU.md` §9.")
    w("")
    w("# Hướng dẫn cho IT: dựng hệ thống ECA trên Microsoft từ bộ dựng này (T4M-BK4)")
    w("")
    w("> **Nháp chưa chạy.** Bộ dựng được kiểm trên máy không có Microsoft 365. Mọi bước chạm SharePoint, Power Apps,")
    w("> Power Automate, Forms là **TH** cho tới khi IT chạy; điều không có trong `T4M_KET_QUA_TAI_LIEU.md` §8 mang nhãn **GĐ**.")
    w("> **Làm trên BẢN SAO** list và app, không đụng bản thật. Dữ liệu trong bộ là MÔ PHỎNG, không có tên thật, tenantId, địa chỉ.")
    w("> Chữ trong ngoặc: R1..R38 là mục kiểm của `T4M_DAC_TA_SUA_APP.md`; `HDT x.y` là dòng của bảng kết quả ở `T4M_HUONG_DAN_THU.md` §9")
    w("> (điền Pass/Fail và số đo ở đó).")
    w("")
    w("## Trong thư mục này")
    w("")
    w("| Thư mục / tệp | Nội dung |")
    w("|---|---|")
    w("| `01_lists/` | `site_script_t4m.json` (cách A/B), `<list>_mau.csv` (cách C), `KIEM_COT_ECA.md` (thêm cột tay vào ECA có sẵn) |")
    w("| `02_app/` | Công thức Power Fx từng màn: `NguyenVong.txt`, `DiemQuyetTam.txt`, `ThiTuyen.txt`, `Khoa.txt` (dán vào BẢN SAO app) |")
    w("| `03_flow/` | `BANG_FLOW.md`, `BANG_FLOW.csv`: %d flow `DaLam_<ClubId>` (một flow mỗi CLB có đề: %s) |" % (n_flow, clb_co_de))
    w("| `04_forms/` | `NHAP_FORMS_MOI_CLB_<ClubId>.docx` (Quick Import), `CAI_DAT_FORMS_MOI_CLB.md`, `CLB.csv` (list CLB) |")
    w("")
    w("**Thứ tự dựng:** (0) hỏi và chuẩn bị, (1) lists, (2) list CLB và `FormUrl`, (3) biểu mẫu, (4) công thức app, (5) flow, (6) vòng thử.")
    w("Bước 2 cần địa chỉ biểu mẫu nên làm sau bước 3 khi dán `FormUrl`; tạo list CLB trước, dán địa chỉ sau.")
    w("")
    # ---------------------------------------------------------------- bước 0
    w("## Bước 0. Hỏi và chuẩn bị (HỎI-IT)")
    w("")
    w("Hỏi bộ phận IT và giáo viên ECA trước khi dựng (câu hỏi mở của KQ §8; trả lời quyết định chọn cách A, B hay C):")
    w("")
    for q in HOI_IT:
        w("1. HỎI-IT: " + q)
    w("")
    w("Chuẩn bị: một bản sao list `ECA` (hoặc site thử), một bản sao app, một tài khoản học sinh thử và một tài khoản giáo viên thử.")
    _pass_fail(L, "Đã có câu trả lời cho các câu HỎI-IT trên, ghi lại (không ghi tên người, địa chỉ)")
    _pass_fail(L, "Chỉ làm trên bản sao; không dữ liệu thật trong kho mã", r=(14,))
    w("")
    # ---------------------------------------------------------------- bước 1
    w("## Bước 1. Dựng list (`01_lists/`)")
    w("")
    w("Bốn list: `ECA` (30 cột: Email, HoTen, CoSo, Khoi, Lop, Thu, NV1..NV7, THI1..THI7, WP1..WP7, CapDo, Goi, TrangThai), `CLB`, `BaiThi`,")
    w("`NHAT_KY_DA_LAM`. MỘT định nghĩa cột sinh ra cả ba cách dưới đây. Chọn theo câu trả lời ở bước 0.")
    w("")
    w("| Cách | Quyền cần | Nhãn | Ghi chú |")
    w("|---|---|---|---|")
    w("| **Cách A.** Áp `site_script_t4m.json` bằng `Invoke-PnPSiteScript -Script` | Quyền trên site; **nhưng** PnP PowerShell cần ứng dụng Entra do tổ chức tự đăng ký (bắt buộc từ 09/09/2024); nguồn thứ ba nói vai trò tối thiểu để đăng ký là Cloud Application Administrator | ĐXM (trang lệnh); TT-CXM (vai trò) | Chạy lại không nhân đôi; list cùng tên thì chỉ thêm cột còn thiếu. HỎI-IT: trường có ứng dụng Entra cho PnP chưa |")
    w("| **Cách B (mặc định).** Quản trị SharePoint đăng ký script một lần (`Add-SPOSiteScript`, `Add-SPOSiteDesign`); chủ site áp bằng **Settings > Apply a site template** | Đăng ký: quản trị SharePoint (GĐ: vai trò không ghi rõ). Áp: quyền chủ site (site owner permissions) trở lên | ĐXM / GĐ | Áp không đồng bộ, trần 300 hành động hoặc 100.000 ký tự |")
    w("| **Cách C (lui).** Microsoft Lists > tạo từ bảng tính bằng `<list>_mau.csv` | Chỉ quyền tạo list trên site | ĐXM (trang hỗ trợ, đoạn trích) | Kiểu cột đoán theo dữ liệu, sửa được ở Customize; **không thêm cột vào list có sẵn**: với ECA có sẵn thì làm theo `KIEM_COT_ECA.md` |")
    w("")
    w("**Site script này có %d hành động (đếm cả hành động con), vượt trần %d của kiểu áp đồng bộ.** Vì vậy cách A/B chỉ áp được" % (n_hanh_dong, tran_dong_bo))
    w("theo kiểu **không đồng bộ** (trần %d): dùng **Settings > Apply a site template**, hoặc `Add-SPOSiteDesignTask`. **Không dùng `Invoke-SPOSiteDesign`**" % tran_khong_dong_bo)
    w("(áp đồng bộ, từ chối vì quá %d hành động). Áp xong chờ vài phút rồi mở list kiểm cột (áp không đồng bộ không báo xong ngay; GĐ)." % tran_dong_bo)
    w("Nếu ECA đã có cột `NV1..NV3` tạo tay, thử trên bản sao và chỉ thêm cột chưa có: GUID khác nhau có thể sinh cột trùng tên hiển thị (KQ §8.1, TH).")
    w("")
    _pass_fail(L, "Đủ 4 list, ECA đủ cột, đúng kiểu (Choice của Thu, TrangThai, CoSo), đặt chỉ mục Email và Thu", hdt=("3.1", "3.3"))
    _pass_fail(L, "Nạp thử 1.500 rồi 7.500 dòng giả vào bản sao ECA", hdt=("3.2",))
    _pass_fail(L, "Export to CSV được; tệp xuất đọc được (dòng, tiếng Việt, cột Choice, tên cột)", hdt=("4.1", "4.2"))
    _pass_fail(L, "Chạy `chuyen_forms_sang_phan_mem.py --chi-thi --lists` trên tệp xuất: 0 cảnh báo ở phần Lists", r=(13,), hdt=("4.2",))
    w("")
    # ---------------------------------------------------------------- bước 2
    w("## Bước 2. List `CLB` và `FormUrl` (`04_forms/CLB.csv`)")
    w("")
    w("1. Tạo list `CLB` từ `04_forms/CLB.csv` (cách C) hoặc đã có từ site script. Cột: `ClubId`, `Ten`, `Buoi`, `FormUrl`.")
    w("2. Cột `Buoi` của `CLB.csv` ghi chữ **\"Thứ Hai\"…\"Thứ Sáu\"** còn cột `Thu` của `ECA` ghi **\"Thứ 2\"…\"Thứ 6\"**: công thức trong `02_app/`")
    w("   đã ánh xạ hai cách viết (không sửa tay). Đừng đổi chữ ở một bên.")
    w("3. Sau bước 3 (tạo biểu mẫu), dán địa chỉ biểu mẫu vào `FormUrl` của đúng %d CLB có đề (%s); CLB không đề để trống." % (n_flow, clb_co_de))
    w("")
    _pass_fail(L, "List `CLB` có đủ CLB; `FormUrl` rỗng cho CLB không đề", r=(36,))
    _pass_fail(L, "Mọi CLB có đề trong `de_thi.json` có `FormUrl`; CLB không đề thì rỗng", r=(36,), hdt=("14.5",))
    w("")
    # ---------------------------------------------------------------- bước 3
    w("## Bước 3. Biểu mẫu thi (`04_forms/`, %d biểu mẫu)" % n_flow)
    w("")
    w("1. Mỗi CLB có đề: Forms > tạo từ tệp Quick Import `NHAP_FORMS_MOI_CLB_<ClubId>.docx` (Quick Import **không mang đáp án**).")
    w("2. Làm theo `CAI_DAT_FORMS_MOI_CLB.md`: đáp án đúng và điểm mỗi câu; **Record name BẬT**, **One response per person BẬT**,")
    w("   **Show results TẮT**, chỉ người trong tổ chức, đặt ngày bắt đầu và kết thúc.")
    w("3. Ghi `Form Id` vào `03_flow/BANG_FLOW.csv` (cột `FormId`) và dán địa chỉ biểu mẫu vào `FormUrl` (bước 2).")
    w("")
    _pass_fail(L, "Số biểu mẫu = số CLB có đề (%d); Settings đúng như `CAI_DAT_FORMS_MOI_CLB.md`" % n_flow)
    _pass_fail(L, "Bấm nút Làm bài của mỗi thẻ mở đúng biểu mẫu của CLB đó (đối chiếu tiêu đề)", r=(16,), hdt=("13.1",))
    w("")
    # ---------------------------------------------------------------- bước 4
    w("## Bước 4. Công thức app (`02_app/`)")
    w("")
    w("Dán **từng thuộc tính** vào thanh công thức của BẢN SAO app (tệp liệt kê `Control.Property = công thức`; đã khai triển đủ NV1..NV7,")
    w("THI1..THI7, WP1..WP7). Code view của Studio dán được YAML điều khiển nhưng phải đúng định dạng do Studio sinh, nên bộ dựng **không**")
    w("sinh YAML; `App.OnStart` / `App.Formulas` (App Object) **dán tay** (KQ §8.2, ĐXM). Tên điều khiển trong tệp là tên ví dụ: đặt cho")
    w("trùng hoặc đổi trong công thức.")
    w("")
    w("**Màn nguyện vọng (`NguyenVong.txt`)**")
    _pass_fail(L, "Chỉ thấy dòng của mình, kể cả email viết hoa; chỉ lọc `=` trên nguồn dữ liệu", r=(1, 9), hdt=("5.1",))
    _pass_fail(L, "Số ô, không trùng, không hở, ngày trống hợp lệ", r=(2, 3, 4, 5), hdt=("5.2",))
    _pass_fail(L, "Gửi ghi 5 dòng, lỗi nửa chừng báo đúng ngày", r=(6, 7), hdt=("5.3",))
    _pass_fail(L, "Khoá theo `TrangThai`; điện thoại", r=(8, 11), hdt=("5.4",))
    _pass_fail(L, "Hai ngôn ngữ vi/en; khôi phục phiên bản", r=(10, 12), hdt=("5.5", "5.6"))
    _pass_fail(L, "Tick Thi chỉ ở CLB có đề; tối đa 5 tick mỗi ngày", r=(25, 26), hdt=("14.1",))
    w("")
    w("**Màn điểm quyết tâm (`DiemQuyetTam.txt`)**")
    _pass_fail(L, "Đổi/xoá CLB xoá THIk, WPk; hai khung điểm theo tick", r=(27, 28), hdt=("14.2",))
    _pass_fail(L, "Bộ đếm X/100, khung một CLB tự 100, chặn Gửi khi khác 100, chỉ số nguyên không âm", r=(29, 30, 31, 32), hdt=("14.3",))
    _pass_fail(L, "Một lần Gửi vẫn 5 yêu cầu `Patch`, đủ ba nhóm cột", r=(33,), hdt=("14.4",))
    w("")
    w("**Màn Thi tuyển (`ThiTuyen.txt`)**")
    _pass_fail(L, "Chỉ CLB có đề đã tick; nút mở đúng biểu mẫu", r=(15, 16), hdt=("13.1",))
    _pass_fail(L, "Không điểm trên app; chỉ lọc uỷ quyền được; mỗi em chỉ thấy bài mình", r=(19, 20, 21), hdt=("13.3",))
    _pass_fail(L, "Hai ngôn ngữ, điện thoại, màn trống không lỗi, học sinh không ghi được `BaiThi`", r=(22, 23, 24), hdt=("13.4",))
    _pass_fail(L, "Thẻ theo tick, không quá 5 thẻ mỗi ngày", r=(35,), hdt=("14.4",))
    w("")
    w("**Khoá (`Khoa.txt`)**")
    _pass_fail(L, "`Đã khóa`: tắt Gửi, tick và ô điểm; Thi tuyển hiện \"Đã đóng\"", r=(18, 34, 38), hdt=("14.4",))
    w("")
    # ---------------------------------------------------------------- bước 5
    w("## Bước 5. Flow `DaLam_<ClubId>` (`03_flow/`)")
    w("")
    w("Bộ dựng **không có gói flow** (không tự chế `.zip`, KQ §8.3). Làm: (1) dựng TAY một flow mẫu theo `BANG_FLOW.md` §2 (chỉ connector chuẩn")
    w("Forms và SharePoint, chủ là tài khoản dịch vụ); (2) thử trọn một bài nộp; (3) **Save as** hoặc **Export > Package (.zip)** rồi nhập lại")
    w("(cần vai trò Environment Maker, HỎI-IT; nhập gói kiểu cũ có thể bị chặn); (4) mỗi bản sao đổi đúng hai thứ: `Form Id` và hằng `ClubId`")
    w("theo từng hàng của `BANG_FLOW.csv`. Số flow phải bằng %d." % n_flow)
    w("")
    _pass_fail(L, "Nộp 1 bài thử: đúng 1 dòng `BaiThi` (Email chữ thường, ClubId đúng, NopLuc hợp lý); ghi thời gian trễ và số hành động mỗi bài", r=(17,), hdt=("13.2",))
    _pass_fail(L, "Thẻ chuyển \"Đã làm\" và nút Làm bài ẩn; đã khoá thì hiện \"Đã đóng\"", r=(17, 18), hdt=("13.2",))
    _pass_fail(L, "Mỗi `Form Id` đúng một lần; mỗi `ClubId` đúng một flow; ClubId trùng từng ký tự với list `CLB`")
    _pass_fail(L, "Học sinh thử không ghi trực tiếp được vào `BaiThi`; chỉ thấy bài của mình", r=(21, 24), hdt=("13.3", "13.4"))
    w("")
    # ---------------------------------------------------------------- bước 6
    w("## Bước 6. Vòng thử trọn (trên bản sao)")
    w("")
    w("Một học sinh thử đi hết: chọn tối đa 7 nguyện vọng cho một ngày, tick CLB muốn thi, chia điểm quyết tâm, Gửi, làm bài thi, xem trạng thái.")
    w("Rồi xuất list, chạy bộ chuyển đổi (`T4M_VAN_HANH_MOT_DOT.md` bước 5) và kiểm:")
    w("")
    _pass_fail(L, "Sau Gửi: 5 dòng, đủ NV/THI/WP; lịch sử chạy cho thấy 5 yêu cầu (ghi số yêu cầu thật)", r=(6, 33), hdt=("14.4",))
    _pass_fail(L, "Tệp xuất qua bộ chuyển đổi: 0 cảnh báo về tick (không đề, quá 5) và điểm (khung khác 100, ô không nguyên). Cảnh báo \"vắng thi\" chỉ có khi chạy kèm tệp xuất Forms và hợp lệ khi em tick mà không nộp", r=(37,), hdt=("14.5",))
    _pass_fail(L, "Đối chiếu bài thi: `--bai-thi BaiThi.csv` không báo bài thiếu", r=(17,), hdt=("13.2",))
    _pass_fail(L, "Rà tệp, ảnh chụp trước khi gửi lại cho dự án: không tên, email thật, tenantId, địa chỉ app", r=(14,))
    w("")
    w("## Khi một bước fail")
    w("")
    w("Ghi nguyên văn thông báo lỗi vào cột \"Lý do\" của `T4M_HUONG_DAN_THU.md` §9, không kèm dữ liệu thật. Không nới DLP chỉ cho flow này;")
    w("nếu flow bị chặn thì dùng đường thủ công (`T4M_FLOW_DA_LAM.md` §8: Open in Excel, rồi `--chi-thi`). Phụ lục: toàn bộ R1..R38 kèm tiêu đề để tra nhanh.")
    w("")
    w("## Phụ lục. R1..R38 (tiêu đề ngắn; điều kiện pass đầy đủ ở `T4M_DAC_TA_SUA_APP.md` §7, §10.4, §11)")
    w("")
    _r_chi_tiet(L, range(1, 39))
    w("")
    return "\n".join(L)
