# -*- coding: utf-8 -*-
"""T4M-BK2: công thức Power Fx theo từng màn, khai triển đủ k = 1..7, sinh bằng mã (không gõ tay chỉ số).

Mỗi tệp .txt liệt kê "Điều khiển.Thuộc tính = công thức" để IT dán vào thanh công thức của BẢN SAO app.
Không sinh YAML điều khiển (Code view cần định dạng do Studio sinh; KQ §8.2). Phần App.OnStart / App.Formulas gắn
nhãn "dán tay" (App Object không dán mã được). Tên điều khiển (galNgay, ddNV1, chkThi1, txtWP1…) là TÊN VÍ DỤ.
Bộ lọc trên nguồn dữ liệu (ECA, BaiThi, CLB) chỉ dùng `=`; mọi việc loại trừ, đếm, so sánh khác làm trên collection
cục bộ (đặc tả §5). Nguồn công thức: T4M_DAC_TA_SUA_APP.md §2, §3, §4, §5, §10.3, §11.

TH: chưa chạy trên Power Apps / SharePoint. Mọi công thức là GĐ (giả định, chưa thử).
"""

import re

from . import cot_lists

SO_NV = cot_lists.SO_NV
KS = range(1, SO_NV + 1)
TRAN_TICK = 5                                  # bieu_mau.TRAN_THI_MOI_BUOI; test nhắc đổi cùng chỗ
DONG_TH = "TH: chưa chạy trên Power Apps / SharePoint"
NGUON_DATA = ("ECA", "BaiThi", "CLB")


def buoi_theo_thu(de):
    """{'Thứ 2': tên buổi trong de_thi.json, …} theo cột Thu của ECA.

    PHÁT HIỆN: tiêu đề `CLB.csv` (tao_mau_forms.ghi_clb_csv) ghi tên buổi của de_thi.json ('Thứ Hai') còn cột
    Thu của ECA là 'Thứ 2'; công thức lọc `Filter(CLB, Buoi = …)` phải dùng tên buổi, nên cần ánh xạ này."""
    ma_ten = {b["ma"]: b["ten"] for b in de["buoi"]}
    ket = {}
    for thu in cot_lists.THU:
        ma = "thu_" + thu.split()[-1]
        if ma not in ma_ten:
            raise ValueError("de_thi.json không có buổi %s ứng với %s" % (ma, thu))
        ket[thu] = ma_ten[ma]
    return ket


# ----------------------------------------------------------------- bộ soát lọc uỷ quyền được (dùng cho test)
def _bo_chuoi(s):
    return re.sub(r'"[^"]*"', '""', s)


def _cau_goi(text, bat_dau):
    """Văn bản từ tên hàm tại `bat_dau` đến dấu ')' đóng tương ứng (bỏ qua ngoặc trong chuỗi)."""
    i = text.index("(", bat_dau)
    sau, trong = 0, False
    for j in range(i, len(text)):
        c = text[j]
        if c == '"':
            trong = not trong
        elif not trong:
            if c == "(":
                sau += 1
            elif c == ")":
                sau -= 1
                if sau == 0:
                    return text[bat_dau:j + 1]
    return text[bat_dau:]


def _doi_so_dau(cau):
    """Đối số đầu của lời gọi 'Hàm(a, b, …)': cắt ở dấu phẩy ngoài ngoặc/chuỗi/dấu nhọn."""
    i = cau.index("(") + 1
    sau, trong, dau = 0, False, i
    for j in range(i, len(cau)):
        c = cau[j]
        if c == '"':
            trong = not trong
        elif not trong:
            if c in "({[":
                sau += 1
            elif c in ")}]":
                if sau == 0:
                    return cau[dau:j].strip()
                sau -= 1
            elif c == "," and sau == 0:
                return cau[dau:j].strip()
    return cau[dau:].strip()


_CAM = [(re.compile(r"<>"), "<>"), (re.compile(r"(?<![<>])[<>](?![<>])"), "< hoặc >"),
        (re.compile(r"\bin\b"), "in"), (re.compile(r"\bIsBlank\b"), "IsBlank"),
        (re.compile(r"\bNot\s*\("), "Not("), (re.compile(r"!"), "!")]


def soat_loc_uy_quyen(text):
    """Danh sách lỗi: mỗi lời gọi Filter/LookUp có đối số đầu là ECA, BaiThi hoặc CLB mà dùng toán tử không uỷ quyền
    được (`<>`, `<`, `>`, `in`, IsBlank, Not, `!`). Rỗng = đạt. Lọc trên collection cục bộ (colCLB…) không bị soát."""
    loi = []
    for m in re.finditer(r"\b(Filter|LookUp)\s*\(", text):
        cau = _cau_goi(text, m.start())
        if _doi_so_dau(cau) not in NGUON_DATA:
            continue
        gon = _bo_chuoi(cau)
        for re_cam, ten in _CAM:
            if re_cam.search(gon):
                loi.append("%s: %s" % (ten, " ".join(cau.split())))
    return loi


# ----------------------------------------------------------------- biểu thức khai triển
def _tong(mau, k_ds=KS, noi=" + "):
    return "(" + noi.join(mau.format(k=k) for k in k_ds) + ")"


SEL = "ddNV{k}.Selected.ClubId"
SO_TICK = _tong("If(chkThi{k}.Value, 1, 0)")
SO_CHON = _tong('If(ddNV{k}.Selected.ClubId <> "", 1, 0)')
DIEM = "Coalesce(Value(txtWP{k}.Text), 0)"
TONG_1 = _tong("If(chkThi{k}.Value, %s, 0)" % DIEM)
TONG_2 = _tong('If(ddNV{k}.Selected.ClubId <> "" And !chkThi{k}.Value, %s, 0)' % DIEM)
SO_KHAC = "(%s - %s)" % (SO_CHON, SO_TICK)


def so_khung(k):
    """Số CLB của khung chứa dòng k: khung 1 nếu đã tick, khung 2 nếu không."""
    return "If(chkThi%d.Value, %s, %s)" % (k, SO_TICK, SO_KHAC)


BUOI_CUA_NGAY = "LookUp(colBuoi, Thu = ThisItem.Thu).Buoi"
CLB_NGAY = "Filter(colCLB, Buoi = %s)" % BUOI_CUA_NGAY
XOA_NGAY = 'Filter(colXoa, Thu = ThisItem.Thu, K = %s)'


def _bloc(ten, ct):
    dong = ct.strip("\n").split("\n")
    return "%s =\n%s\n" % (ten, "\n".join("    " + d if d else d for d in dong))


def _dau(nguon, tieu_de, ghi_chu=()):
    L = [DONG_TH, "Nguồn: T4M_DAC_TA_SUA_APP.md " + nguon, "",
         "# " + tieu_de,
         "# Dán từng khối \"Điều khiển.Thuộc tính\" vào thanh công thức của BẢN SAO app. Tên điều khiển là ví dụ.",
         "# Chỉ thư viện chuẩn của Power Fx; bộ lọc trên ECA, BaiThi, CLB chỉ dùng `=`."]
    L += ["# " + g for g in ghi_chu]
    L.append("")
    return "\n".join(L) + "\n"


# ----------------------------------------------------------------- nhãn hai ngôn ngữ (colNhan)
NHAN = [("da_dung", "Đã dùng", "Used"), ("khung_1", "Khung 1 (CLB thi)", "Group 1 (exam clubs)"),
        ("khung_2", "Khung 2 (CLB còn lại)", "Group 2 (other clubs)"), ("thieu", "còn thiếu", "short by"),
        ("thua", "thừa", "over by"), ("loi_luu", "Chưa lưu được:", "Could not save:"),
        ("da_luu", "Đã lưu", "Saved"), ("da_khoa", "Đã khóa / Locked", "Locked / Đã khóa"),
        ("toi_da_5", "Tối đa 5 CLB thi mỗi ngày", "At most 5 exam clubs per day"),
        ("can_chia_lai", "Cần chia lại điểm", "Points must be redistributed"),
        ("thi", "Thi", "Exam"), ("da_lam", "Đã làm", "Done"), ("chua_lam", "Chưa làm", "Not done"),
        ("da_dong", "Đã đóng / Closed", "Closed / Đã đóng"), ("lam_bai", "Làm bài", "Take the test"),
        ("lam_moi", "Làm mới", "Refresh"),
        ("tre_cap_nhat", "Trạng thái cập nhật sau vài giây đến vài phút",
         "Status updates after a few seconds to a few minutes"),
        ("xem_diem", "Xem điểm trong Forms sau khi giáo viên công bố",
         "See your score in Forms after your teacher posts scores"),
        ("khong_co_clb_thi", "Bạn không có CLB cần thi", "You have no clubs to test for")]


def _on_start():
    bang = ", ".join('{Khoa: "%s", Vi: "%s", En: "%s"}' % n for n in NHAN)
    return ("# ---- App.OnStart: DÁN TAY (App Object không dán mã được, KQ §8.2) ----\n"
            + _bloc("App.OnStart",
                    'Set(varNgonNgu, "vi");\nClear(colXoa);\nClearCollect(colNhan, Table(%s))' % bang)
            + "\n# ---- App.Formulas: DÁN TAY (hàm T dùng ở mọi màn; GĐ về cú pháp hàm người dùng) ----\n"
            + _bloc("App.Formulas",
                    'T(khoa: Text): Text = If(varNgonNgu = "en", LookUp(colNhan, Khoa = khoa).En, '
                    'LookUp(colNhan, Khoa = khoa).Vi);'))


# ----------------------------------------------------------------- bốn tệp
def tao_nguyen_vong(de):
    bx = buoi_theo_thu(de)
    ten_buoi = list(bx.values())
    bang_buoi = ", ".join('{Thu: "%s", Buoi: "%s"}' % (t, b) for t, b in bx.items())
    nap = "ClearCollect(colCLB, Filter(CLB, Buoi = \"%s\"));\n" % ten_buoi[0]
    nap += "".join("Collect(colCLB, Filter(CLB, Buoi = \"%s\"));\n" % b for b in ten_buoi[1:])
    t = _dau("§2, §3, §5, §10.3", "Màn nguyện vọng: 7 ô NV, tick Thi, Gửi",
             ["DisplayMode của mọi điều khiển: xem Khoa.txt. Điểm quyết tâm: DiemQuyetTam.txt.",
              "Khi xoá NVk thì các ô SAU nó bị xoá (một trong hai cách của đặc tả §2.4; cách dồn lên không dùng).",
              "Việc loại CLB đã chọn làm trên colCLB (cục bộ), không đẩy `<>` lên SharePoint."])
    t += _bloc("NguyenVong.OnVisible",
               'ClearCollect(colEca, Filter(ECA, Email = Lower(User().Email)));\n'
               'ClearCollect(colBuoi, Table(%s));\n%s;\nClear(colXoa)' % (bang_buoi, nap.rstrip(";\n")))
    t += "\n" + _bloc("galNgay.Items", "Sort(colEca, Thu, SortOrder.Ascending)")
    t += "\n" + _bloc("lblDong.Text", "ThisItem.Thu")
    for k in KS:
        loai = " And ".join("ClubId <> ddNV%d.Selected.ClubId" % j for j in range(1, k))
        loc = "Buoi = %s" % BUOI_CUA_NGAY + (" And " + loai if loai else "")
        t += "\n# ---- Dòng NV%d ----\n" % k
        t += _bloc("ddNV%d.Items" % k, 'SortByColumns(Filter(colCLB, %s), "ClubId", SortOrder.Ascending)' % loc)
        t += _bloc("ddNV%d.Default" % k,
                   "If(!IsEmpty(%s), Blank(), LookUp(colCLB, ClubId = ThisItem.NV%d).Ten)" % (XOA_NGAY % k, k))
        t += _bloc("ddNV%d.Visible" % k, "%d <= Min(%d, CountRows(%s))" % (k, SO_NV, CLB_NGAY))
        sau = "".join(
            "Collect(colXoa, {Thu: ThisItem.Thu, K: %d}); Reset(ddNV%d); Reset(chkThi%d); Reset(txtWP%d);\n"
            % (j, j, j, j) for j in range(k + 1, SO_NV + 1))
        trung = "".join(
            "If(ddNV%d.Selected.ClubId = ddNV%d.Selected.ClubId, Collect(colXoa, {Thu: ThisItem.Thu, K: %d}); "
            "Reset(ddNV%d); Reset(chkThi%d); Reset(txtWP%d));\n" % (j, k, j, j, j, j)
            for j in range(k + 1, SO_NV + 1))
        cau = ["Collect(colXoa, {Thu: ThisItem.Thu, K: %d})" % k, "Reset(chkThi%d)" % k, "Reset(txtWP%d)" % k]
        if sau:
            cau.append("If(ddNV%d.Selected.ClubId = \"\",\n%s)" % (k, sau.rstrip(";\n")))
        cau += [x for x in trung.rstrip(";\n").split(";\n") if x]
        t += _bloc("ddNV%d.OnChange" % k, ";\n".join(cau))
        t += _bloc("chkThi%d.Visible" % k, 'ddNV%d.Selected.FormUrl <> ""' % k)
        t += _bloc("chkThi%d.Default" % k,
                   'If(!IsEmpty(%s), false, ThisItem.THI%d = "Có")' % (XOA_NGAY % k, k))
        t += _bloc("chkThi%d.Text" % k, 'T("thi")')
    cap = "".join(
        "NV%d: Dong.ddNV%d.Selected.ClubId, " % (k, k) for k in KS)
    thi = "".join('THI%d: If(Dong.chkThi%d.Value, "Có", Blank()), ' % (k, k) for k in KS)
    wp = ", ".join('WP%d: If(Dong.txtWP%d.Text = "", Blank(), Value(Dong.txtWP%d.Text))' % (k, k, k) for k in KS)
    t += "\n# ---- Gửi (đặc tả §3): mỗi ngày MỘT Patch ghi đủ 21 cột; lỗi/khóa ghi vào colLoiLuu theo NGÀY ----\n"
    t += _bloc("btnGui.OnSelect",
               "If(\n    CountRows(Filter(galNgay.AllItems, lblLoi.Text <> \"\")) > 0,\n"
               "    Notify(First(Filter(galNgay.AllItems, lblLoi.Text <> \"\")).lblLoi.Text, NotificationType.Error),\n"
               "    Clear(colLoiLuu);\n"
               "    ForAll(galNgay.AllItems As Dong,\n"
               "        If(LookUp(ECA, ID = Dong.ID).TrangThai = \"Đang mở\",\n"
               "            IfError(\n"
               "                Patch(ECA, LookUp(ECA, ID = Dong.ID),\n"
               "                    {%s%s%s}),\n"
               "                Collect(colLoiLuu, {Thu: Dong.Thu, Ly: FirstError.Message})),\n"
               "            Collect(colLoiLuu, {Thu: Dong.Thu, Ly: \"khoa\"})));\n"
               "    If(IsEmpty(colLoiLuu),\n"
               "        Notify(T(\"da_luu\"), NotificationType.Success),\n"
               "        Notify(T(\"loi_luu\") & \" \" & Concat(colLoiLuu, Thu, \", \"), NotificationType.Error)))"
               % (cap, thi, wp))
    t += "\n" + _on_start()
    return t


def tao_diem_quyet_tam(de):
    t = _dau("§2 (điểm 5b, 5c), §11 (R28..R32)", "Điểm quyết tâm: hai khung 100 mỗi ngày",
             ["Khung 1 = các dòng đã tick Thi; khung 2 = các dòng còn lại. Bố cục hai khung là việc dàn trang của IT;",
              "công thức gán mỗi dòng vào khung 1 hoặc 2 và đếm riêng. Khung rỗng không đòi điểm; khung một CLB tự điền 100.",
              "Ô điểm chỉ nhận số nguyên không âm (R32). Giá trị trống tính là 0."])
    for k in KS:
        t += "\n# ---- Dòng %d ----\n" % k
        t += _bloc("txtWP%d.Visible" % k, 'ddNV%d.Selected.ClubId <> ""' % k)
        t += _bloc("txtWP%d.Format" % k, "TextFormat.Number")
        t += _bloc("txtWP%d.Default" % k,
                   'If(%s = 1, "100",\n    If(!IsEmpty(Filter(colXoa, Thu = ThisItem.Thu, K = 0)) '
                   'Or !IsEmpty(%s), "", Text(ThisItem.WP%d)))' % (so_khung(k), XOA_NGAY % k, k))
        t += _bloc("txtWP%d.OnChange" % k,
                   'If(!IsMatch(txtWP%d.Text, "^[0-9]{0,9}$"), Reset(txtWP%d))' % (k, k))
        t += _bloc("lblKhung%d.Text" % k, 'If(chkThi%d.Value, T("khung_1"), T("khung_2"))' % k)
        t += _bloc("chkThi%d.OnCheck" % k, _xoa_diem_ngay())
        t += _bloc("chkThi%d.OnUncheck" % k, _xoa_diem_ngay())
    t += "\n# ---- Bộ đếm và chặn Gửi (một lần mỗi ngày, trong thư viện galNgay) ----\n"
    t += _bloc("lblDem1.Text", 'T("da_dung") & " " & %s & " / 100"' % TONG_1)
    t += _bloc("lblDem1.Visible", "%s > 0" % SO_TICK)
    t += _bloc("lblDem2.Text", 'T("da_dung") & " " & %s & " / 100"' % TONG_2)
    t += _bloc("lblDem2.Visible", "%s > 0" % SO_KHAC)
    t += _bloc("lblCanChia.Text", 'T("can_chia_lai")')
    t += _bloc("lblCanChia.Visible", "!IsEmpty(Filter(colXoa, Thu = ThisItem.Thu, K = 0))")
    t += _bloc("lblLoi.Text",
               'If(%s > 0 And %s <> 100,\n    ThisItem.Thu & ": " & T("khung_1") & " " & '
               'If(%s < 100, T("thieu") & " " & (100 - %s), T("thua") & " " & (%s - 100)) & ". ", "")\n'
               '& If(%s > 0 And %s <> 100,\n    ThisItem.Thu & ": " & T("khung_2") & " " & '
               'If(%s < 100, T("thieu") & " " & (100 - %s), T("thua") & " " & (%s - 100)), "")'
               % (SO_TICK, TONG_1, TONG_1, TONG_1, TONG_1, SO_KHAC, TONG_2, TONG_2, TONG_2, TONG_2))
    return t


def _xoa_diem_ngay():
    return ("Collect(colXoa, {Thu: ThisItem.Thu, K: 0});\n"
            + "\n".join("Reset(txtWP%d);" % k for k in KS)).rstrip(";")


def _tai_collections():
    return ('ClearCollect(colCLB, CLB);\n'
            'ClearCollect(colBaiThi, Filter(BaiThi, Email = Lower(User().Email)));\n'
            'ClearCollect(colEca, Filter(ECA, Email = Lower(User().Email)));\n'
            'Clear(colChon);\n'
            'ForAll(colEca As E, Collect(colChon, Filter(Table(%s), T = "Có")))'
            % ", ".join("{Id: E.NV%d, T: E.THI%d}" % (k, k) for k in KS))


def tao_thi_tuyen(de):
    t = _dau("§10.2, §10.3, §10.4 (R15..R24), R35", "Màn Thi tuyển: thẻ theo tick, Làm bài, Đã làm",
             ["Chỉ CLB đã TICK và có FormUrl hiện thẻ (tối đa 5 mỗi ngày do tick). Không hiện điểm (mức 5a).",
              "Lọc FormUrl và ClubId làm trên collection cục bộ (IsBlank/Not không uỷ quyền được)."])
    t += _bloc("ThiTuyen.OnVisible", _tai_collections())
    t += "\n" + _bloc("galThe.Items", 'Filter(colCLB, ClubId in colChon.Id && FormUrl <> "")')
    chua = "IsEmpty(Filter(colBaiThi, ClubId = ThisItem.ClubId))"
    t += _bloc("lblTrangThai.Text", 'If(!%s, T("da_lam"), T("chua_lam"))' % chua)
    t += _bloc("btnLam.Text", 'T("lam_bai")')
    t += _bloc("btnLam.Visible", '%s And !IsEmpty(Filter(colEca, TrangThai = "Đang mở"))' % chua)
    t += _bloc("btnLam.OnSelect", "Launch(ThisItem.FormUrl)")
    t += _bloc("lblDaDong.Text", 'T("da_dong")')
    t += _bloc("lblDaDong.Visible", '%s And IsEmpty(Filter(colEca, TrangThai = "Đang mở"))' % chua)
    t += _bloc("btnLamMoi.Text", 'T("lam_moi")')
    t += _bloc("btnLamMoi.OnSelect", _tai_collections())
    t += _bloc("lblTreCapNhat.Text", 'T("tre_cap_nhat")')
    t += _bloc("lblDiem.Text", 'T("xem_diem")')
    t += _bloc("lblRong.Text", 'T("khong_co_clb_thi")')
    t += _bloc("lblRong.Visible", "CountRows(galThe.AllItems) = 0")
    return t


def tao_khoa(de):
    khoa = 'ThisItem.TrangThai = "Đã khóa"'
    t = _dau("§2.4, §4, §11 (R8, R26, R34)", "Khóa và DisplayMode của mọi điều khiển",
             ["Mỗi thuộc tính chỉ có MỘT công thức: DisplayMode của NV, tick, điểm gom hết ở tệp này (khóa + quy tắc ô phụ thuộc).",
              "Khóa theo DÒNG (TrangThai của dòng ECA), không theo biến toàn app. Nút Gửi tắt khi bất kỳ dòng nào khóa."])
    for k in KS:
        t += "\n# ---- Dòng %d ----\n" % k
        truoc = ("DisplayMode.Edit" if k == 1 else
                 'If(ddNV%d.Selected.ClubId = "", DisplayMode.Disabled, DisplayMode.Edit)' % (k - 1))
        t += _bloc("ddNV%d.DisplayMode" % k, "If(%s, DisplayMode.Disabled, %s)" % (khoa, truoc))
        t += _bloc("chkThi%d.DisplayMode" % k,
                   "If(%s, DisplayMode.Disabled,\n    If(!chkThi%d.Value And %s >= %d, DisplayMode.Disabled, "
                   "DisplayMode.Edit))" % (khoa, k, SO_TICK, TRAN_TICK))
        t += _bloc("txtWP%d.DisplayMode" % k,
                   "If(%s, DisplayMode.Disabled,\n    If(%s = 1, DisplayMode.Disabled, DisplayMode.Edit))"
                   % (khoa, so_khung(k)))
    t += "\n# ---- Nhãn khóa, giới hạn 5 tick, nút Gửi ----\n"
    t += _bloc("lblKhoa.Text", 'T("da_khoa")')
    t += _bloc("lblKhoa.Visible", khoa)
    t += _bloc("lblToiDa5.Text", 'T("toi_da_5")')
    t += _bloc("lblToiDa5.Visible", "%s >= %d" % (SO_TICK, TRAN_TICK))
    t += _bloc("btnGui.DisplayMode",
               'If(!IsEmpty(Filter(colEca, TrangThai = "Đã khóa")) Or '
               'CountRows(Filter(galNgay.AllItems, lblLoi.Text <> "")) > 0,\n'
               '    DisplayMode.Disabled, DisplayMode.Edit)')
    return t


def tao_cong_thuc(de):
    """{tên tệp: nội dung} của bốn màn. Cùng `de` thì cùng từng byte."""
    return {"NguyenVong.txt": tao_nguyen_vong(de), "DiemQuyetTam.txt": tao_diem_quyet_tam(de),
            "ThiTuyen.txt": tao_thi_tuyen(de), "Khoa.txt": tao_khoa(de)}


def ghi(ra_dir, de):
    import os
    kq = tao_cong_thuc(de)
    for ten, nd in kq.items():
        with open(os.path.join(ra_dir, ten), "w", encoding="utf-8", newline="\n") as f:
            f.write(nd)
    return sorted(kq)
