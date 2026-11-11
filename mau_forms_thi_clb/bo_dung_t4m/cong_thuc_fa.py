# -*- coding: utf-8 -*-
"""GAP-11 (TH): công thức Power Fx của màn đăng ký FA-DAA, đường A (đặc tả T4M_DAC_TA_SUA_APP.md §12, R39–R54).

Chỉ sinh khi `tao_bo_dung_t4m.py --fa-daa` (tệp `02_app/DangKyFA.txt`); bộ dựng thường không đổi. Không chọn D8 (Power
Apps hay Forms): đây chỉ là bộ dựng sẵn cho đường A.

Mô hình: list `ECA` một dòng mỗi (học sinh, ngày) với `NV1..NV7`, `WP1..WP7` (huy chương 60/30/10), `HC_TuChinh`,
`TrangThai` (Choice: DRAFT / SUBMITTED / Đã khóa). Trong app: `colEca` (dòng của em), `colCLBTat` (mọi CLB của các
ngày), `colCLBNgau` (CLB của ngày đang mở, đã xáo), `colXep` (danh sách của em: Thu, ViTri, ClubId, Loai, HC).
Mọi việc loại trừ / đếm / sắp làm trên collection cục bộ; lọc trên ECA, CLB chỉ dùng `=` (đặc tả §5).
Tên điều khiển (galCLBNgay, galXep, btnLen…) là TÊN VÍ DỤ. Mọi công thức là GĐ (giả định, chưa chạy).
"""

from . import cong_thuc

TEN_TEP = "DangKyFA.txt"
SO_NV = cong_thuc.SO_NV
KS = cong_thuc.KS
TU_DO, GIOI_HAN, TUYEN_CHON = "Tự do", "Giới hạn", "Tuyển chọn"
XEP_NGAY = "Filter(colXep, Thu = varThu)"
DONG_NGAY = "LookUp(colEca, Thu = varThu)"

NHAN_FA = [
    ("huong_dan", "Xếp đúng thứ tự em thích. Xếp CLB khó vào lên đầu không làm em mất cơ hội ở CLB sau.",
     "Rank clubs in the order you really like. Putting a hard club first never costs you a later club."),
    ("toi_thieu_3", "Cần ít nhất 3 nguyện vọng mỗi ngày (hoặc tất cả nếu ngày có ít hơn 3 CLB).",
     "Pick at least 3 clubs per day (or all of them if the day has fewer than 3)."),
    ("thieu_tu_do", "Thêm một CLB Tự do để chắc chắn có chỗ.", "Add a Free club to be sure of a place."),
    ("nhac_vang_tc", "Huy chương ở CLB Tuyển chọn chỉ dùng khi bằng điểm, và chỉ khi em vượt mốc.",
     "A medal at a Selective club only counts on equal scores, and only above the pass mark."),
    ("hc_da_chinh", "Huy chương không tự đổi theo thứ tự vì em đã tự chỉnh.",
     "Medals no longer follow the order because you set them yourself."),
    ("da_nop", "Đã nộp", "Submitted"), ("da_khoa_fa", "Đã khóa / Locked", "Locked / Đã khóa"),
    ("vang", "Vàng", "Gold"), ("bac", "Bạc", "Silver"), ("dong", "Đồng", "Bronze"),
]

# Khối tự lưu (R44): MỘT Patch ghi đủ NV1..NV7, WP1..WP7, HC_TuChinh và TrangThai = DRAFT của dòng ngày đang mở;
# dòng đã khóa thì chỉ báo (đọc lại TrangThai trên ECA trước khi ghi, R46).
_NV = ",\n".join("        NV%d: LookUp(%s, ViTri = %d).ClubId" % (k, XEP_NGAY, k) for k in KS)
_WP = ",\n".join("        WP%d: If(LookUp(%s, ViTri = %d).HC > 0, LookUp(%s, ViTri = %d).HC, Blank())"
                 % (k, XEP_NGAY, k, XEP_NGAY, k) for k in KS)
TU_LUU = (
    "If(LookUp(ECA, ID = %s.ID).TrangThai.Value = \"Đã khóa\",\n"
    "    Notify(T(\"da_khoa_fa\"), NotificationType.Error),\n"
    "    Patch(ECA, LookUp(ECA, ID = %s.ID), {\n%s,\n%s,\n"
    "        HC_TuChinh: %s.HC_TuChinh,\n"
    "        TrangThai: {Value: \"DRAFT\"}}))" % (DONG_NGAY, DONG_NGAY, _NV, _WP, DONG_NGAY))

# Huy chương mặc định (R48, R49): khi CHƯA tự chỉnh, vàng / bạc / đồng cho ba CLB KHÔNG Tự do xếp cao nhất; thừa thì
# để trống. Đã tự chỉnh (HC_TuChinh = "Có") thì giữ nguyên.
CAP_NHAT_HC = (
    "If(%s.HC_TuChinh <> \"Có\",\n"
    "    With({ds: Sort(Filter(colXep, Thu = varThu And Loai <> \"%s\"), ViTri)},\n"
    "        UpdateIf(colXep, Thu = varThu, {HC: 0});\n"
    "        If(CountRows(ds) >= 1, UpdateIf(colXep, Thu = varThu And ClubId = Index(ds, 1).ClubId, {HC: 60}));\n"
    "        If(CountRows(ds) >= 2, UpdateIf(colXep, Thu = varThu And ClubId = Index(ds, 2).ClubId, {HC: 30}));\n"
    "        If(CountRows(ds) >= 3, UpdateIf(colXep, Thu = varThu And ClubId = Index(ds, 3).ClubId, {HC: 10}))))"
    % (DONG_NGAY, TU_DO))

# Số nguyện vọng tối thiểu của MỘT ngày (R42): 3, hoặc mọi CLB nếu ngày có ít hơn 3.
def _toi_thieu(thu):
    return "Min(3, CountRows(Filter(colCLBTat, Buoi = LookUp(colBuoi, Thu = %s).Buoi)))" % thu


def _du_ngay(thu):
    return "CountRows(Filter(colXep, Thu = %s)) >= %s" % (thu, _toi_thieu(thu))


def _sau_thao_tac():
    return CAP_NHAT_HC + ";\n" + TU_LUU


def _on_visible(de):
    bx = cong_thuc.buoi_theo_thu(de)
    bang_buoi = ", ".join('{Thu: "%s", Buoi: "%s"}' % (t, b) for t, b in bx.items())
    ten_buoi = list(bx.values())
    nap = "ClearCollect(colCLBTat, Filter(CLB, Buoi = \"%s\"))" % ten_buoi[0]
    nap += "".join(";\nCollect(colCLBTat, Filter(CLB, Buoi = \"%s\"))" % b for b in ten_buoi[1:])
    doc = ";\n".join(
        "    If(!IsBlank(Dong.NV%d), Collect(colXep, {Thu: Dong.Thu, ViTri: %d, ClubId: Dong.NV%d, "
        "Loai: LookUp(colCLBTat, ClubId = Dong.NV%d).Loai, HC: Coalesce(Dong.WP%d, 0)}))" % (k, k, k, k, k)
        for k in KS)
    return cong_thuc._bloc(
        "DangKyFA.OnVisible",
        "ClearCollect(colEca, Filter(ECA, Email = Lower(User().Email)));\n"
        "ClearCollect(colBuoi, Table(%s));\n%s;\n"
        "Clear(colXep);\n"
        "ForAll(colEca As Dong,\n%s)" % (bang_buoi, nap, doc))


def tao_dang_ky_fa(de):
    """Toàn bộ nội dung `02_app/DangKyFA.txt`. Cùng `de` thì cùng từng byte."""
    t = cong_thuc._dau(
        "§12 (R39–R54)", "Màn đăng ký FA-DAA (đường A): xáo thứ tự, ▲▼, tự lưu DRAFT, tối thiểu 3, huy chương",
        ["Chỉ dùng cho workspace FA (bộ dựng --fa-daa). D8 (Power Apps hay Forms) CHƯA quyết: đây chỉ là bản dựng sẵn.",
         "TrangThai là cột Choice: ghi {Value: \"DRAFT\"}, đọc .TrangThai.Value (GĐ: kiểu cột thật HỎI-IT).",
         "Mọi thao tác (thêm, bỏ, ▲, ▼, đổi huy chương) kết thúc bằng MỘT Patch tự lưu (R44); sửa sau khi nộp thì dòng "
         "về DRAFT và phải nộp lại."])
    t += _on_visible(de)
    t += "\n# ---- Thẻ ngày: xáo thứ tự CLB MỘT lần mỗi lần mở ngày (R39) ----\n"
    t += cong_thuc._bloc("galNgayFA.Items", "Sort(colEca, Thu, SortOrder.Ascending)")
    t += cong_thuc._bloc("galNgayFA.OnSelect",
                         "Set(varThu, ThisItem.Thu);\n"
                         "ClearCollect(colCLBNgau, Shuffle(Filter(colCLBTat, Buoi = LookUp(colBuoi, Thu = varThu).Buoi)))")
    t += cong_thuc._bloc("lblHuongDan.Text", 'T("huong_dan")')
    t += "\n# ---- Khu \"Các CLB của ngày\": CLB đã vào danh sách thì biến khỏi khu này (R41) ----\n"
    t += cong_thuc._bloc("galCLBNgay.Items", "Filter(colCLBNgau, Not(ClubId in %s.ClubId))" % XEP_NGAY)
    t += cong_thuc._bloc("lblLoai.Text",
                         'Switch(ThisItem.Loai, "%s", T("nhan_tu_do"), "%s", T("nhan_gioi_han"), T("nhan_tuyen_chon"))'
                         % (TU_DO, GIOI_HAN))
    t += cong_thuc._bloc("btnThem.DisplayMode",
                         "If(%s.TrangThai.Value = \"Đã khóa\" Or CountRows(%s) >= %d, DisplayMode.Disabled, "
                         "DisplayMode.Edit)" % (DONG_NGAY, XEP_NGAY, SO_NV))
    t += cong_thuc._bloc("btnThem.OnSelect",
                         "If(CountRows(%s) < 7,\n"
                         "    Collect(colXep, {Thu: varThu, ViTri: CountRows(%s) + 1, ClubId: ThisItem.ClubId, "
                         "Loai: ThisItem.Loai, HC: 0}));\n%s" % (XEP_NGAY, XEP_NGAY, _sau_thao_tac()))
    t += "\n# ---- Khu \"Danh sách của em\": ▲ ▼ đổi chỗ với dòng kề, Bỏ (R40, R41) ----\n"
    t += cong_thuc._bloc("galXep.Items", "Sort(%s, ViTri, SortOrder.Ascending)" % XEP_NGAY)
    t += cong_thuc._bloc("btnLen.Text", '"▲"')
    t += cong_thuc._bloc("btnXuong.Text", '"▼"')
    t += cong_thuc._bloc("btnLen.DisplayMode", "If(ThisItem.ViTri = 1, DisplayMode.Disabled, DisplayMode.Edit)")
    t += cong_thuc._bloc("btnXuong.DisplayMode",
                         "If(ThisItem.ViTri = CountRows(%s), DisplayMode.Disabled, DisplayMode.Edit)" % XEP_NGAY)
    for nut, d in (("btnLen", -1), ("btnXuong", 1)):
        dau = "-" if d < 0 else "+"
        nguoc = "+" if d < 0 else "-"
        t += cong_thuc._bloc(
            nut + ".OnSelect",
            "With({a: ThisItem, b: LookUp(colXep, Thu = varThu And ViTri = ThisItem.ViTri %s 1)},\n"
            "    Patch(colXep, a, {ViTri: a.ViTri %s 1});\n"
            "    Patch(colXep, b, {ViTri: b.ViTri %s 1}));\n%s" % (dau, dau, nguoc, _sau_thao_tac()))
    t += cong_thuc._bloc(
        "btnBo.OnSelect",
        "With({vt: ThisItem.ViTri},\n"
        "    Remove(colXep, ThisItem);\n"
        "    ClearCollect(colTam, Filter(colXep, Thu = varThu And ViTri > vt));\n"
        "    ForAll(colTam, Patch(colXep, LookUp(colXep, Thu = varThu And ClubId = ThisRecord.ClubId), "
        "{ViTri: ThisRecord.ViTri - 1})));\n%s" % _sau_thao_tac())
    t += "\n# ---- Widget huy chương (R48–R52): mỗi CLB tối đa một; không đặt vào Tự do; hoán đổi đủ 6 cách ----\n"
    t += cong_thuc._bloc("ddHC.Items", '["", T("vang"), T("bac"), T("dong")]')
    t += cong_thuc._bloc("ddHC.Default",
                         'Switch(ThisItem.HC, 60, T("vang"), 30, T("bac"), 10, T("dong"), "")')
    t += cong_thuc._bloc("ddHC.DisplayMode",
                         'If(ThisItem.Loai = "%s", DisplayMode.Disabled, DisplayMode.Edit)' % TU_DO)
    t += cong_thuc._bloc(
        "ddHC.OnChange",
        "With({moi: Switch(ddHC.Selected.Value, T(\"vang\"), 60, T(\"bac\"), 30, T(\"dong\"), 10, 0), cu: ThisItem.HC},\n"
        "    If(moi > 0, UpdateIf(colXep, Thu = varThu And HC = moi And ClubId <> ThisItem.ClubId, {HC: cu}));\n"
        "    Patch(colXep, ThisItem, {HC: moi}));\n"
        "Patch(colEca, %s, {HC_TuChinh: \"Có\"});\n%s" % (DONG_NGAY, TU_LUU))
    t += cong_thuc._bloc("lblHCDaChinh.Text", 'T("hc_da_chinh")')
    t += cong_thuc._bloc("lblHCDaChinh.Visible", '%s.HC_TuChinh = "Có"' % DONG_NGAY)
    t += cong_thuc._bloc("lblNhacVang.Text", 'T("nhac_vang_tc")')
    t += cong_thuc._bloc("lblNhacVang.Visible",
                         '!IsEmpty(Filter(colXep, Thu = varThu And HC = 60 And Loai = "%s"))' % TUYEN_CHON)
    t += "\n# ---- Cảnh báo thiếu CLB Tự do (R43, vẫn nộp được) và tối thiểu 3 (R42) ----\n"
    t += cong_thuc._bloc("lblThieuTuDo.Text", 'T("thieu_tu_do")')
    t += cong_thuc._bloc("lblThieuTuDo.Visible",
                         '!IsEmpty(%s) And IsEmpty(Filter(colXep, Thu = varThu And Loai = "%s"))' % (XEP_NGAY, TU_DO))
    t += cong_thuc._bloc("lblToiThieu.Text", 'T("toi_thieu_3")')
    t += cong_thuc._bloc("lblToiThieu.Visible", "Not(%s)" % _du_ngay("varThu"))
    t += "\n# ---- Nộp (R45, R46): SUBMITTED cho từng ngày đủ điều kiện; đọc lại TrangThai trên ECA trước mỗi Patch ----\n"
    t += cong_thuc._bloc(
        "btnNop.DisplayMode",
        "If(IsEmpty(Filter(colEca, %s)), DisplayMode.Disabled, DisplayMode.Edit)" % _du_ngay("ThisRecord.Thu"))
    t += cong_thuc._bloc(
        "btnNop.OnSelect",
        "Clear(colLoiLuu);\n"
        "ForAll(Filter(colEca, %s) As Dong,\n"
        "    If(LookUp(ECA, ID = Dong.ID).TrangThai.Value = \"Đã khóa\",\n"
        "        Collect(colLoiLuu, {Thu: Dong.Thu, Ly: \"khoa\"}),\n"
        "        Patch(ECA, LookUp(ECA, ID = Dong.ID), {TrangThai: {Value: \"SUBMITTED\"}})));\n"
        "If(IsEmpty(colLoiLuu), Navigate(ManXacNhan), "
        "Notify(T(\"da_khoa_fa\") & \" \" & Concat(colLoiLuu, Thu, \", \"), NotificationType.Error))"
        % _du_ngay("ThisRecord.Thu"))
    t += "\n# ---- App.Formulas: DÁN TAY, thêm các dòng sau vào bảng Nhan của bộ thường (Khoa, Vi, En) ----\n"
    t += "".join('#   {Khoa: "%s", Vi: "%s", En: "%s"}\n' % n for n in NHAN_FA)
    t += "#   nhan_tu_do / nhan_gioi_han / nhan_tuyen_chon: ba câu nhãn thẻ CLB của đặc tả §12.2 mục 4 (R47).\n"
    return t


def ghi_fa(ra_dir, de):
    """Ghi `02_app/DangKyFA.txt`; trả [tên tệp]."""
    import os
    with open(os.path.join(ra_dir, TEN_TEP), "w", encoding="utf-8", newline="\n") as f:
        f.write(tao_dang_ky_fa(de))
    return [TEN_TEP]
