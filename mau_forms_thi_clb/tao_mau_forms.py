"""Sinh toàn bộ mẫu Microsoft Forms từ de_thi.json.

    python mau_forms_thi_clb/tao_mau_forms.py

Ghi ra, cạnh tệp này:

    NHAP_FORMS_THI_CLB.docx   đem nhập bằng Quick Import của Forms
    CAI_DAT_FORMS.md          những gì Quick Import KHÔNG mang theo: đổi
                              câu Ranking, rẽ nhánh, đáp án + điểm, cài đặt
    MAU_XUAT_TU_FORMS.xlsx    tệp Forms xuất ra, dựng giả 60 học sinh — để
                              chạy thử bộ chuyển đổi trước khi có dữ liệu thật

Sửa đề, thêm CLB, đổi buổi: sửa de_thi.json rồi chạy lại. Không sửa tay ba
tệp trên — lần sinh sau sẽ ghi đè, và sửa tay là cách biểu mẫu lệch khỏi
đáp án dùng để chấm.

Chế độ "chỉ thi" (T4M-Q2) — Forms chỉ có bài thi, nguyện vọng nằm ở ứng dụng đăng ký:

    python mau_forms_thi_clb/tao_mau_forms.py --chi-thi [--ra THƯ_MỤC]

Ghi CAI_DAT_FORMS_CHI_THI.md và NHAP_FORMS_CHI_THI.docx (hoặc NHAP_FORMS_CHI_THI_1.docx,
_2.docx… khi tổng số câu vượt 200 và phải tách theo buổi). Sinh lại từ de_thi.json không
đổi cho ra tệp giống hệt từng byte. Chế độ mặc định vẫn như trên và không đổi.

Chế độ "mỗi CLB một biểu mẫu" (T4M-Q4a) — cổng thi trong app ECA, mỗi CLB có đề một biểu mẫu riêng:

    python mau_forms_thi_clb/tao_mau_forms.py --moi-clb [--ra THƯ_MỤC]

Ghi NHAP_FORMS_MOI_CLB_<club_id>.docx (mỗi CLB có đề một tệp, không câu cổng), CLB.csv (ClubId, Ten,
Buoi, FormUrl để trống: đem tạo list CLB bằng "Create a list from Excel/CSV" rồi dán địa chỉ từng
biểu mẫu vào FormUrl) và CAI_DAT_FORMS_MOI_CLB.md. Sinh lại cho ra tệp giống hệt từng byte.

Cần python-docx (requirements-dev.txt) để ghi .docx; thiếu thì bỏ qua riêng
tệp đó, hai tệp kia vẫn sinh.
"""

import argparse
import copy
import csv
import io
import os
import random
import sys
import zipfile
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bieu_mau as bm  # noqa: E402

THU_MUC = bm.THU_MUC
CHU_CAI = "abcdefghijklmnopqrstuvwxyz"


# ------------------------------------------------------------ Quick Import

def ghi_docx(de, duong):
    """Bố cục giống KHAO_SAT_NHAP_FORMS.docx — dạng Quick Import đọc tốt:
    tiêu đề phần in đậm, câu hỏi đánh số, lựa chọn 'a. …' thụt lề."""
    from docx import Document
    from docx.shared import Pt

    doc = Document()
    st = doc.styles["Normal"]
    st.font.name, st.font.size = "Calibri", Pt(11)

    def dong(chu, co=11, dam=False, truoc=0, sau=4, thut=0):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_before, pf.space_after = Pt(truoc), Pt(sau)
        if thut:
            pf.left_indent = Pt(thut)
        r = p.add_run(chu)
        r.bold, r.font.size = dam, Pt(co)

    dong(de["tieu_de"], co=16, dam=True, sau=10)
    so = 0
    for i, (ten, cac_cau) in enumerate(bm.cac_phan(de), 1):
        dong("PHẦN %d — %s" % (i, ten), co=14, dam=True, truoc=18, sau=8)
        for tieu_de, _loai, lua_chon, _bb in cac_cau:
            so += 1
            dong("%d. %s" % (so, tieu_de), co=12, dam=True, truoc=12, sau=4)
            for j, lc in enumerate(lua_chon):
                dong("%s. %s" % (CHU_CAI[j], lc), thut=18, sau=2)
    doc.save(duong)


# -------------------------------------------------------- bảng cài đặt tay

def _bang_dap_an(w, de, cac_clb):
    for clb in cac_clb:
        w("**%s** (`%s`, %s)" % (clb["name"], clb["club_id"], bm.ten_buoi(de, clb["buoi"])))
        w("")
        w("| Câu | Đáp án đúng |")
        w("|---|---|")
        for i, cau in enumerate(clb["de_thi"], 1):
            w("| `[%s-%d]` %s | %s. %s |" % (clb["club_id"], i, cau["cau"].replace("|", "\\|"),
                                          CHU_CAI[cau["dap_an"]], cau["lua_chon"][cau["dap_an"]]))
        w("")


def ghi_cai_dat(de):
    phan = bm.cac_phan(de)
    so_cau = sum(len(c) for _, c in phan)
    n_thi = len(bm.clb_co_thi(de))
    L = []
    w = L.append
    w("# Cài đặt Microsoft Forms cho mẫu \"%s\"" % de["tieu_de"])
    w("")
    w("> **Tệp này do `tao_mau_forms.py` sinh từ `de_thi.json`.** Đừng sửa tay —")
    w("> sửa `de_thi.json` rồi chạy lại. Hướng dẫn đầy đủ: `README.md` cùng thư mục.")
    w("")
    w("Biểu mẫu có **%d phần, %d câu hỏi**: %d buổi, %d CLB, trong đó **%d CLB "
      "tổ chức thi** (mỗi đề %d câu × %s điểm = %s điểm)."
      % (len(phan), so_cau, len(de["buoi"]), len(de["cau_lac_bo"]), n_thi,
         len(bm.clb_co_thi(de)[0]["de_thi"]), bm.ghi_so(de["diem_moi_cau"]),
         bm.ghi_so(bm.diem_toi_da(de, bm.clb_co_thi(de)[0]))))
    w("")
    w("## 1. Bố cục — thứ tự phần CHÍNH LÀ luồng đi của học sinh")
    w("")
    w("| Phần | Tên phần | Câu hỏi | Loại | Bắt buộc |")
    w("|---|---|---|---|---|")
    so = 0
    for i, (ten, cac_cau) in enumerate(phan, 1):
        for j, (td, loai, _lc, bb) in enumerate(cac_cau):
            so += 1
            ma = bm.ma_cua_cau(td)
            w("| %s | %s | %d · `[%s]` | %s | %s |" % (
                i if j == 0 else "", ten if j == 0 else "", so, ma,
                {"text": "Text", "ranking": "**Ranking**", "choice": "Choice"}[loai],
                "✅" if bb else "—"))
    w("")
    w("## 2. Đổi %d câu nguyện vọng sang Ranking" % len(de["buoi"]))
    w("")
    w("Quick Import không biết loại **Ranking** — các câu `[thu_…]` về tới Forms")
    w("sẽ là câu Choice. Với từng câu: bấm **+ Add new → ⌄ → Ranking** ngay dưới")
    w("nó, **dán nguyên văn** tiêu đề và các lựa chọn (giữ cả phần `[mã]` và phần")
    w("`(club_id)`), để **không bắt buộc**, rồi xoá câu Choice cũ.")
    w("")
    w("## 3. Rẽ nhánh — chỉ %d chỗ" % n_thi)
    w("")
    w("Chọn câu cổng → **…** → **Add branching**. Đáp án **\"%s\"** để nguyên "
      "(đi tiếp sang phần đề thi ngay sau). Đáp án **\"%s\"** đặt **Go to**:" % (bm.CO, bm.KHONG))
    w("")
    w("| Câu cổng | \"%s\" → Go to |" % bm.KHONG)
    w("|---|---|")
    for clb, toi in bm.re_nhanh(de):
        w("| `[thi-%s]` %s | **%s** |" % (clb["club_id"], clb["name"], toi))
    w("")
    w("Làm xong đề thi CLB này thì Forms **tự** sang phần kế tiếp — đúng là câu")
    w("cổng của CLB sau, hoặc nguyện vọng của buổi sau. Không cần đặt thêm nhánh.")
    w("")
    w("## 4. Đáp án và điểm (chế độ Quiz)")
    w("")
    w("Chỉ cần nếu tạo dạng **Quiz**. Mỗi câu đề thi: bấm vào đáp án đúng →")
    w("dấu ✔ **Correct answer**, ô **Points** = **%s**. Câu cổng, câu nguyện vọng,"
      % bm.ghi_so(de["diem_moi_cau"]))
    w("mã và tên học sinh: **không** cho điểm.")
    w("")
    w("Bộ chuyển đổi **chấm lại** theo chính bảng này, và báo nếu điểm Forms")
    w("chấm lệch — tức là có câu tick nhầm đáp án trên Forms.")
    w("")
    _bang_dap_an(w, de, bm.clb_co_thi(de))
    w("## 5. Settings")
    w("")
    w("| Cài đặt | Giá trị | Vì sao |")
    w("|---|---|---|")
    w("| Who can fill out this form | **Only people in my organization** | Học sinh đăng nhập tài khoản trường |")
    w("| **One response per person** | **BẬT** | Đây là bài thi: nộp lại là làm lại tới khi được điểm cao. Bộ chuyển đổi cũng chỉ giữ phiếu **đầu** của mỗi mã học sinh |")
    w("| Shuffle questions | **TẮT** | Xáo câu là hỏng rẽ nhánh |")
    w("| Shuffle options (từng câu đề thi) | Bật được | Chấm theo nội dung lựa chọn, không theo vị trí |")
    w("| Show results automatically (Quiz) | **TẮT** | Bật là em làm trước biết đáp án, chuyền cho em làm sau |")
    w("| Start date / End date | Đặt đủ cả hai | Hết giờ tự khoá, không phải canh |")
    w("")
    return "\n".join(L)


# ------------------------------------------------ tệp Forms xuất ra, dựng giả

HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Vũ", "Đặng", "Bùi", "Đỗ", "Ngô"]
DEM = ["Văn", "Thị", "Minh", "Thu", "Gia", "Quốc", "Ngọc", "Hải", "Bảo", "Khánh"]
TEN = ["An", "Bình", "Châu", "Dũng", "Hà", "Khoa", "Linh", "Nam", "Phúc",
       "Quân", "Trang", "Vy", "Yến", "Tùng", "Mai", "Long"]


def ghi_mau_xuat(de, duong, so_hoc_sinh=60, hat_giong=2026):
    """Giả đúng hình dạng Forms xuất ở chế độ Quiz: cột hệ thống trước, mỗi
    câu một cột; câu có điểm kèm cột 'Points - …' và 'Feedback - …'.
    Ranking và Choice nhiều lựa chọn là MỘT ô, nối bằng dấu chấm phẩy."""
    from openpyxl import Workbook

    rd = random.Random(hat_giong)
    phan = bm.cac_phan(de)
    co_diem = {bm.cau_de_thi(c, i) for c in bm.clb_co_thi(de)
               for i in range(1, len(c["de_thi"]) + 1)}

    tieu_de = ["ID", "Start time", "Completion time", "Email", "Name",
               "Total points", "Quiz feedback"]
    for _ten, cac_cau in phan:
        for td, *_ in cac_cau:
            tieu_de.append(td)
            if td in co_diem:
                tieu_de += ["Points - " + td, "Feedback - " + td]

    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(tieu_de)
    gio = datetime(2026, 9, 7, 7, 30)
    for n in range(1, so_hoc_sinh + 1):
        o = {"ID": n, "Email": "anonymous", "Name": ""}
        o[bm.cau_ma_hoc_sinh()] = "HS%03d" % n
        o[bm.cau_ho_ten()] = "%s %s %s" % (rd.choice(HO), rd.choice(DEM), rd.choice(TEN))
        nang_luc = rd.uniform(0.7, 0.95)
        tong = 0
        # Mỗi em xếp 2–4 buổi; buổi còn lại bỏ trống = em bận.
        buoi_ranh = rd.sample(de["buoi"], rd.randint(2, 4))
        for b in de["buoi"]:
            o_buoi = bm.clb_cua_buoi(de, b["ma"])
            xep = []
            if b in buoi_ranh:
                # Ranking của Forms bắt xếp ĐỦ mọi lựa chọn.
                xep = rd.sample(o_buoi, len(o_buoi))
                o[bm.cau_xep_hang(de, b["ma"])] = "".join(bm.lua_chon_clb(c) + ";" for c in xep)
            for clb in o_buoi:
                if not clb["de_thi"]:
                    continue
                thi = clb in xep[:2] and rd.random() < 0.75
                o[bm.cau_cong_thi(de, clb)] = bm.CO if thi else bm.KHONG
                if not thi:
                    continue
                dung_ca = [rd.random() < nang_luc for _ in clb["de_thi"]]
                # Ít nhất 2 câu đúng: bài 0–2 điểm là THẬT với đề 5 câu, nhưng
                # phần mềm báo "điểm lạ" khi dưới 1/3 trung vị (README mục 5).
                # Tệp mẫu phải nạp sạch để người đọc không lẫn cảnh báo cố ý.
                for k in rd.sample(range(len(dung_ca)), len(dung_ca)):
                    if sum(dung_ca) >= 2:
                        break
                    dung_ca[k] = True
                for i, cau in enumerate(clb["de_thi"], 1):
                    dung = dung_ca[i - 1]
                    sai = [x for k, x in enumerate(cau["lua_chon"]) if k != cau["dap_an"]]
                    td = bm.cau_de_thi(clb, i)
                    o[td] = cau["lua_chon"][cau["dap_an"]] if dung else rd.choice(sai)
                    o["Points - " + td] = de["diem_moi_cau"] if dung else 0
                    tong += o["Points - " + td]
        o["Total points"] = tong
        bat_dau = gio + timedelta(minutes=3 * n + rd.randint(0, 2))
        o["Start time"] = bat_dau
        o["Completion time"] = bat_dau + timedelta(minutes=rd.randint(6, 25))
        ws.append([o.get(c) for c in tieu_de])
    wb.save(duong)


def ghi_mau_xuat_chi_thi(de, duong, danh_sach, hat_giong=2026):
    """T4M-DEMO: tệp Forms chỉ-thi GIẢ (Email + cột câu + cột 'Points - …', không Ranking, không mã HS),
    khớp tệp Lists giả: `danh_sach` là kết quả `chuyen_forms_sang_phan_mem.doc_lists` ({email chữ thường:
    {name, nguyen_vong}}). Em chỉ thi CLB đã xếp, trừ một em cố ý thi CLB không xếp. Cùng seed -> cùng ô.

    Cố ý gài ba cảnh báo (cộng email viết HOA, bộ chuyển đổi hạ chữ thường nên không báo gì):
    một phiếu nộp lần hai, một email không có trong Lists, một bài thi CLB không xếp nguyện vọng.
    Trả {email_trung, email_la, khong_xep: (email, club_id), n_phieu}. Dữ liệu MÔ PHỎNG.

    T4M-Q5c: nếu `danh_sach` có khoá "tick" (List có cột THIk) thì em chỉ nộp bài cho CLB đã tick (mỗi bài
    nộp với xác suất 0,85, nên có em tick mà vắng), và gài thêm hai trường hợp, báo trong kết quả:
    `tick_vang` = (email, club_id) tick mà KHÔNG nộp bài; `nop_khong_tick` = (email, club_id) nộp bài mà KHÔNG tick."""
    from openpyxl import Workbook

    rd = random.Random(hat_giong)
    clb_thi = bm.clb_co_thi(de)
    if not clb_thi:
        raise ValueError("de_thi.json không có CLB nào có đề thi")
    tieu_de = ["ID", "Start time", "Completion time", "Email", "Name", "Total points"]
    for clb in clb_thi:
        tieu_de.append(bm.cau_cong_thi(de, clb, chi_thi=True))
        for i in range(1, len(clb["de_thi"]) + 1):
            td = bm.cau_de_thi(clb, i)
            tieu_de += [td, "Points - " + td]

    def phieu(email, ten, cac_clb, nang_luc):
        """Một dòng Forms: các CLB trong `cac_clb` thi, còn lại 'Không'."""
        o, tong = {"Email": email, "Name": ten}, 0
        for clb in clb_thi:
            if clb["club_id"] not in cac_clb:
                o[bm.cau_cong_thi(de, clb, chi_thi=True)] = bm.KHONG
                continue
            o[bm.cau_cong_thi(de, clb, chi_thi=True)] = bm.CO
            for i, cau in enumerate(clb["de_thi"], 1):
                dung = rd.random() < nang_luc
                sai = [x for k, x in enumerate(cau["lua_chon"]) if k != cau["dap_an"]]
                td = bm.cau_de_thi(clb, i)
                o[td] = cau["lua_chon"][cau["dap_an"]] if dung else rd.choice(sai)
                o["Points - " + td] = de["diem_moi_cau"] if dung else 0
                tong += o["Points - " + td]
        o["Total points"] = tong
        return o

    co_de = {c["club_id"] for c in clb_thi}
    co_tick = any("tick" in h for h in danh_sach.values())
    dong, thi_cua = [], {}
    for n, (email, hs) in enumerate(danh_sach.items(), 1):
        xep = {m for ds in hs["nguyen_vong"].values() for m in ds}
        if co_tick:
            thi = {m for m in sorted(hs["tick"] & co_de) if rd.random() < 0.85}
        else:
            thi = {m for m in sorted(xep & co_de) if rd.random() < 0.7}
        nang_luc = rd.uniform(0.55, 0.95)
        if rd.random() < 0.15:                       # có em chưa làm bài nào: không có phiếu
            continue
        hien = email.upper() if n % 7 == 3 else email  # Forms ghi email đúng như tài khoản
        thi_cua[email] = thi
        dong.append((email, phieu(hien, hs["name"], thi, nang_luc), nang_luc))
    if not dong:
        raise ValueError("danh sách đăng ký quá nhỏ để dựng phiếu")

    # 1) phiếu nộp lần hai của một em đã có bài thi (bộ chuyển đổi giữ phiếu đầu)
    email_trung = next((e for e, o, _ in dong if thi_cua[e]), dong[0][0])
    # 2) email không có trong Lists
    email_la = "la0001@khac.example.test"
    # 3) một em thi CLB có đề mà em KHÔNG xếp nguyện vọng
    khong_xep = None
    for e, hs in danh_sach.items():
        if e == email_trung or e not in thi_cua:
            continue
        xep = {m for ds in hs["nguyen_vong"].values() for m in ds}
        thieu = [c["club_id"] for c in clb_thi if c["club_id"] not in xep
                 and len(hs["nguyen_vong"].get(c["buoi"], [])) < bm.TRAN_CLB_MOI_BUOI]
        if thieu:
            khong_xep = (e, thieu[0])
            break
    if khong_xep is None:
        raise ValueError("không có em nào để gài bài thi CLB không xếp nguyện vọng")
    sua = {khong_xep[0]: thi_cua[khong_xep[0]] | {khong_xep[1]}}
    gai_tick = {}
    if co_tick:
        da_dung = {email_trung, khong_xep[0]}
        # 4) tick mà KHÔNG nộp bài: lấy em đã nộp một CLB đã tick và bỏ bài đó đi
        e_vang = next(((e, c) for e in thi_cua if e not in da_dung for c in sorted(thi_cua[e])), None)
        if e_vang is None:
            raise ValueError("không có em nào để gài trường hợp tick mà vắng thi")
        da_dung.add(e_vang[0])
        sua[e_vang[0]] = thi_cua[e_vang[0]] - {e_vang[1]}
        # 5) nộp bài mà KHÔNG tick: CLB có đề em đã xếp nhưng chưa tick
        def chua_tick(e):
            xep_e = {m for ds in danh_sach[e]["nguyen_vong"].values() for m in ds}
            return sorted((xep_e & co_de) - danh_sach[e]["tick"])

        e_khong = next(((e, c) for e in thi_cua if e not in da_dung for c in chua_tick(e)), None)
        if e_khong is None:
            raise ValueError("không có em nào để gài trường hợp nộp bài mà không tick")
        sua[e_khong[0]] = thi_cua[e_khong[0]] | {e_khong[1]}
        gai_tick = {"tick_vang": e_vang, "nop_khong_tick": e_khong}
    for k, (e, o, nl) in enumerate(dong):
        if e in sua:
            dong[k] = (e, phieu(o["Email"], danh_sach[e]["name"], sua[e], nl), nl)
    them = [phieu(email_trung.upper(), danh_sach[email_trung]["name"], thi_cua[email_trung], 0.2),
            phieu(email_la, "Tài khoản lạ", {clb_thi[0]["club_id"]}, 0.8)]

    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(tieu_de)
    gio = datetime(2026, 9, 7, 7, 30)
    for n, o in enumerate([x[1] for x in dong] + them, 1):
        bat_dau = gio + timedelta(minutes=3 * n + rd.randint(0, 2))
        o.update({"ID": n, "Start time": bat_dau,
                  "Completion time": bat_dau + timedelta(minutes=rd.randint(6, 25))})
        ws.append([o.get(c) for c in tieu_de])
    wb.save(duong)
    return dict({"email_trung": email_trung, "email_la": email_la, "khong_xep": khong_xep,
                 "n_phieu": len(dong) + len(them)}, **gai_tick)


# ------------------------------------------------------ chế độ "chỉ thi" (T4M-Q2)

TEN_DOCX_CHI_THI = "NHAP_FORMS_CHI_THI"
TEN_CAI_DAT_CHI_THI = "CAI_DAT_FORMS_CHI_THI.md"
# Giờ cố định trong zip: python-docx để zipfile ghi giờ hiện tại vào từng mục nên hai lần
# sinh cách nhau vài giây cho hai tệp khác byte.
_GIO_ZIP = (2026, 1, 1, 0, 0, 0)


def ghi_docx_chi_thi(de, duong, buoi=None, phan=None, hau_to=" — bài thi"):
    """Quick Import cho chế độ chỉ thi; giống hệt từng byte khi đầu vào không đổi."""
    from docx import Document
    from docx.shared import Pt

    doc = Document()
    st = doc.styles["Normal"]
    st.font.name, st.font.size = "Calibri", Pt(11)

    def dong(chu, co=11, dam=False, truoc=0, sau=4, thut=0):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_before, pf.space_after = Pt(truoc), Pt(sau)
        if thut:
            pf.left_indent = Pt(thut)
        r = p.add_run(chu)
        r.bold, r.font.size = dam, Pt(co)

    dong(de["tieu_de"] + hau_to, co=16, dam=True, sau=10)
    so = 0
    for i, (ten, cac_cau) in enumerate(bm.cac_phan(de, chi_thi=True, buoi=buoi) if phan is None else phan, 1):
        dong("PHẦN %d — %s" % (i, ten), co=14, dam=True, truoc=18, sau=8)
        for tieu_de, _loai, lua_chon, _bb in cac_cau:
            so += 1
            dong("%d. %s" % (so, tieu_de), co=12, dam=True, truoc=12, sau=4)
            for j, lc in enumerate(lua_chon):
                dong("%s. %s" % (CHU_CAI[j], lc), thut=18, sau=2)
    # Thuộc tính tài liệu cũng cố định (mặc định python-docx giữ giờ của tệp mẫu, nhưng ghi
    # rõ để không phụ thuộc phiên bản thư viện).
    cp = doc.core_properties
    cp.author = cp.last_modified_by = "RB-DA"
    cp.created = cp.modified = datetime(2026, 1, 1)
    cp.title = de["tieu_de"]
    bo_nho = io.BytesIO()
    doc.save(bo_nho)
    bo_nho.seek(0)
    with zipfile.ZipFile(bo_nho) as zin, zipfile.ZipFile(duong, "w", zipfile.ZIP_DEFLATED) as zout:
        for ten in sorted(zin.namelist()):
            zi = zipfile.ZipInfo(ten, date_time=_GIO_ZIP)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o600 << 16
            zout.writestr(zi, zin.read(ten))


def ghi_cai_dat_chi_thi(de, nhom):
    """CAI_DAT_FORMS_CHI_THI.md. nhom: kết quả bm.chia_theo_buoi."""
    tong = bm.dem_cau(de, chi_thi=True)
    n_thi = len(bm.clb_co_thi(de))
    L = []
    w = L.append
    w("# Cài đặt Microsoft Forms (chế độ chỉ thi) cho \"%s\"" % de["tieu_de"])
    w("")
    w("> **Tệp này do `tao_mau_forms.py --chi-thi` sinh từ `de_thi.json`.** Đừng sửa tay —")
    w("> sửa `de_thi.json` rồi chạy lại. Ghi chú cho giáo viên: `GHI_CHU_GIAO_VIEN.md`.")
    w("")
    w("Biểu mẫu chỉ có **bài thi**: không có câu Ranking (nguyện vọng nằm ở ứng dụng đăng ký) và")
    w("không có ô gõ mã học sinh (Forms tự ghi **Name** và **Email** khi bật *Record name*).")
    w("")
    w("Tổng **%d câu** (%d CLB có thi, mỗi CLB một câu cổng + các câu đề), trần Forms là %d câu "
      "mỗi biểu mẫu → **%d biểu mẫu**." % (tong, n_thi, bm.TRAN_CAU_MOI_BIEU_MAU, len(nhom)))
    w("")
    for k, ma_buoi in enumerate(nhom, 1):
        n = bm.dem_cau(de, chi_thi=True, buoi=ma_buoi)
        ten_tep = TEN_DOCX_CHI_THI + (".docx" if len(nhom) == 1 else "_%d.docx" % k)
        w("## Biểu mẫu %d — %s (%d câu)" % (k, ", ".join(bm.ten_buoi(de, m) for m in ma_buoi), n)
          if len(nhom) > 1 else "## Biểu mẫu — %s (%d câu)"
          % (", ".join(bm.ten_buoi(de, m) for m in ma_buoi), n))
        w("")
        w("Tệp Quick Import: `%s`." % ten_tep)
        w("")
        w("### Bố cục")
        w("")
        w("| Phần | Tên phần | Câu hỏi | Loại | Bắt buộc |")
        w("|---|---|---|---|---|")
        so = 0
        for i, (ten, cac_cau) in enumerate(bm.cac_phan(de, chi_thi=True, buoi=ma_buoi), 1):
            for j, (td, loai, _lc, bb) in enumerate(cac_cau):
                so += 1
                w("| %s | %s | %d · `[%s]` | Choice | %s |" % (
                    i if j == 0 else "", ten if j == 0 else "", so, bm.ma_cua_cau(td),
                    "✅" if bb else "—"))
        w("")
        w("### Rẽ nhánh")
        w("")
        w("Chọn câu cổng → **…** → **Add branching**. Đáp án **\"%s\"** để nguyên; đáp án "
          "**\"%s\"** đặt **Go to**:" % (bm.CO, bm.KHONG))
        w("")
        w("| Câu cổng | \"%s\" → Go to |" % bm.KHONG)
        w("|---|---|")
        for clb, toi in bm.re_nhanh(de, chi_thi=True, buoi=ma_buoi):
            w("| `[thi-%s]` %s | **%s** |" % (clb["club_id"], clb["name"], toi))
        w("")
        w("### Đáp án và điểm (chế độ Quiz)")
        w("")
        w("Quick Import **không mang đáp án**. Mỗi câu đề thi: bấm vào đáp án đúng → **Correct answer**,")
        w("ô **Points** = **%s**. Câu cổng: không cho điểm. Bộ chuyển đổi **chấm lại** theo bảng này và"
          % bm.ghi_so(de["diem_moi_cau"]))
        w("báo nếu điểm Forms lệch (tick nhầm).")
        w("")
        _bang_dap_an(w, de, [c for c in bm.clb_co_thi(de) if c["buoi"] in ma_buoi])
    w("## Settings (mọi biểu mẫu)")
    w("")
    w("| Cài đặt | Giá trị | Vì sao |")
    w("|---|---|---|")
    w("| Who can fill out this form | **Only people in my organization** | Học sinh đăng nhập tài khoản trường |")
    w("| **Record name** | **BẬT** | Cột **Email** của tệp xuất là khoá ghép với danh sách đăng ký; không bật thì không biết bài của ai |")
    w("| **One response per person** | **BẬT** | Đây là bài thi: nộp lại là làm lại. Bộ chuyển đổi cũng chỉ giữ phiếu **đầu** của mỗi email |")
    w("| Shuffle questions | **TẮT** | Xáo câu là hỏng rẽ nhánh |")
    w("| Shuffle options (từng câu đề thi) | Bật được | Chấm theo nội dung lựa chọn, không theo vị trí |")
    w("| Show results automatically (Quiz) | **TẮT** | Bật là em làm trước biết đáp án, chuyền cho em làm sau |")
    w("| Start date / End date | Đặt đủ cả hai | Hết giờ tự khoá, không phải canh |")
    w("")
    return "\n".join(L)


def sinh_chi_thi(de, thu_muc):
    """Ghi các tệp chế độ chỉ thi vào `thu_muc`. Trả danh sách đường dẫn đã ghi.

    Tệp NHAP_FORMS_CHI_THI*.docx cũ bị xoá trước (lần trước có thể đã tách, lần này không).
    """
    nhom = bm.chia_theo_buoi(de, chi_thi=True)         # LoiDeThi ở đây thì chưa ghi gì
    os.makedirs(thu_muc, exist_ok=True)
    for ten in os.listdir(thu_muc):
        if ten.startswith(TEN_DOCX_CHI_THI) and ten.endswith(".docx"):
            os.remove(os.path.join(thu_muc, ten))
    ra = []
    duong = os.path.join(thu_muc, TEN_CAI_DAT_CHI_THI)
    with open(duong, "w", encoding="utf-8", newline="\n") as f:
        f.write(ghi_cai_dat_chi_thi(de, nhom))
    ra.append(duong)
    for k, ma_buoi in enumerate(nhom, 1):
        duong = os.path.join(thu_muc, TEN_DOCX_CHI_THI + (".docx" if len(nhom) == 1 else "_%d.docx" % k))
        ghi_docx_chi_thi(de, duong, ma_buoi)
        ra.append(duong)
    return ra


# ------------------------------------------- chế độ "mỗi CLB một biểu mẫu" (T4M-Q4a)

TIEN_TO_DOCX_MOI_CLB = "NHAP_FORMS_MOI_CLB_"
TEN_CAI_DAT_MOI_CLB = "CAI_DAT_FORMS_MOI_CLB.md"
TEN_CLB_CSV = "CLB.csv"


def _kiem_moi_clb(de):
    """Kiểm trước khi ghi bất cứ gì: có CLB có đề, và mỗi CLB không vượt trần câu của Forms."""
    co_thi = bm.clb_co_thi(de)
    if not co_thi:
        raise bm.LoiDeThi("không CLB nào có đề thi — không có gì để dựng biểu mẫu")
    loi = ["CLB %s có %d câu, vượt trần %d câu của một biểu mẫu Forms"
           % (c["club_id"], len(c["de_thi"]), bm.TRAN_CAU_MOI_BIEU_MAU)
           for c in co_thi if len(c["de_thi"]) > bm.TRAN_CAU_MOI_BIEU_MAU]
    if loi:
        raise bm.LoiDeThi("de_thi.json sai:\n  - " + "\n  - ".join(loi))
    return co_thi


def ghi_docx_moi_clb(de, clb, duong):
    """Quick Import của một CLB; giống hệt từng byte khi đầu vào không đổi."""
    from docx import Document
    from docx.shared import Pt

    doc = Document()
    st = doc.styles["Normal"]
    st.font.name, st.font.size = "Calibri", Pt(11)

    def dong(chu, co=11, dam=False, truoc=0, sau=4, thut=0):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_before, pf.space_after = Pt(truoc), Pt(sau)
        if thut:
            pf.left_indent = Pt(thut)
        r = p.add_run(chu)
        r.bold, r.font.size = dam, Pt(co)

    dong("%s — %s — bài thi" % (de["tieu_de"], clb["name"]), co=16, dam=True, sau=10)
    so = 0
    for ten, cac_cau in bm.cac_phan_moi_clb(de, clb):
        dong(ten, co=14, dam=True, truoc=18, sau=8)
        for tieu_de, _loai, lua_chon, _bb in cac_cau:
            so += 1
            dong("%d. %s" % (so, tieu_de), co=12, dam=True, truoc=12, sau=4)
            for j, lc in enumerate(lua_chon):
                dong("%s. %s" % (CHU_CAI[j], lc), thut=18, sau=2)
    cp = doc.core_properties
    cp.author = cp.last_modified_by = "RB-DA"
    cp.created = cp.modified = datetime(2026, 1, 1)
    cp.title = "%s — %s" % (de["tieu_de"], clb["name"])
    bo_nho = io.BytesIO()
    doc.save(bo_nho)
    bo_nho.seek(0)
    with zipfile.ZipFile(bo_nho) as zin, zipfile.ZipFile(duong, "w", zipfile.ZIP_DEFLATED) as zout:
        for ten in sorted(zin.namelist()):
            zi = zipfile.ZipInfo(ten, date_time=_GIO_ZIP)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o600 << 16
            zout.writestr(zi, zin.read(ten))


def ghi_clb_csv(de, duong):
    """CLB.csv cho "Create a list based on a spreadsheet": mọi CLB, FormUrl để trống."""
    with open(duong, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\r\n")
        w.writerow(["ClubId", "Ten", "Buoi", "FormUrl"])
        for c in de["cau_lac_bo"]:
            w.writerow([c["club_id"], c["name"], bm.ten_buoi(de, c["buoi"]), ""])


def ghi_cai_dat_moi_clb(de):
    """CAI_DAT_FORMS_MOI_CLB.md: những gì Quick Import không mang theo, cho từng biểu mẫu."""
    co_thi = bm.clb_co_thi(de)
    L = []
    w = L.append
    w("# Cài đặt Microsoft Forms (mỗi CLB một biểu mẫu) cho \"%s\"" % de["tieu_de"])
    w("")
    w("> **Tệp này do `tao_mau_forms.py --moi-clb` sinh từ `de_thi.json`.** Đừng sửa tay —")
    w("> sửa `de_thi.json` rồi chạy lại. Ghi chú cho giáo viên: `GHI_CHU_GIAO_VIEN.md`.")
    w("")
    w("Mỗi CLB có đề thi có **một biểu mẫu riêng** (không câu cổng, không câu Ranking, không ô mã học sinh):")
    w("app ECA mở đúng biểu mẫu của CLB em đã chọn. **%d biểu mẫu**, tệp Quick Import tương ứng:" % len(co_thi))
    w("")
    w("| CLB | Mã | Buổi | Số câu | Tệp Quick Import |")
    w("|---|---|---|---|---|")
    for c in co_thi:
        w("| %s | `%s` | %s | %d | `%s%s.docx` |" % (c["name"], c["club_id"], bm.ten_buoi(de, c["buoi"]),
                                                   len(c["de_thi"]), TIEN_TO_DOCX_MOI_CLB, c["club_id"]))
    w("")
    w("`%s` liệt kê **mọi** CLB (cả CLB không thi), cột `FormUrl` để trống: tạo list `CLB` từ tệp này, rồi dán" % TEN_CLB_CSV)
    w("địa chỉ biểu mẫu vào `FormUrl` của các CLB có đề.")
    w("")
    w("## Đáp án và điểm (chế độ Quiz)")
    w("")
    w("Quick Import **không mang đáp án**. Mỗi câu: bấm vào đáp án đúng → **Correct answer**, ô **Points** =")
    w("**%s**. Bộ chuyển đổi **chấm lại** theo bảng này và báo nếu điểm Forms lệch (tick nhầm)."
      % bm.ghi_so(de["diem_moi_cau"]))
    w("")
    _bang_dap_an(w, de, co_thi)
    w("## Settings (mọi biểu mẫu)")
    w("")
    w("| Cài đặt | Giá trị | Vì sao |")
    w("|---|---|---|")
    w("| Who can fill out this form | **Only people in my organization** | Học sinh đăng nhập tài khoản trường |")
    w("| **Record name** | **BẬT** | Cột **Email** của tệp xuất là khoá ghép với danh sách đăng ký; không bật thì không biết bài của ai |")
    w("| **One response per person** | **BẬT** | Đây là bài thi: nộp lại là làm lại. Bộ chuyển đổi cũng chỉ giữ phiếu **đầu** của mỗi email |")
    w("| Shuffle questions | Bật được | Mỗi biểu mẫu một CLB, không có rẽ nhánh để hỏng |")
    w("| Shuffle options (từng câu) | Bật được | Chấm theo nội dung lựa chọn, không theo vị trí |")
    w("| Show results automatically (Quiz) | **TẮT** | Bật là em làm trước biết đáp án, chuyền cho em làm sau. Giáo viên bấm **Post scores** khi hết đợt |")
    w("| Timer | Tuỳ chọn | Hẹn giờ áp cho cả biểu mẫu, tức đúng một đề |")
    w("| Start date / End date | Đặt đủ cả hai | Hết giờ tự khoá, không phải canh |")
    w("| Customize thank you message | Nên ghi liên kết quay về app | Em quay lại app bấm Làm mới để thấy \"Đã làm\" |")
    w("")
    return "\n".join(L)


def sinh_moi_clb(de, thu_muc):
    """Ghi các tệp chế độ mỗi-CLB-một-biểu-mẫu vào `thu_muc`. Trả danh sách đường dẫn đã ghi.

    Kiểm đề trước khi ghi: lỗi thì không ghi gì. Tệp NHAP_FORMS_MOI_CLB_*.docx cũ bị xoá trước
    (CLB nào đó có thể không còn đề); tệp của chế độ khác không đụng tới.
    """
    co_thi = _kiem_moi_clb(de)
    os.makedirs(thu_muc, exist_ok=True)
    for ten in os.listdir(thu_muc):
        if ten.startswith(TIEN_TO_DOCX_MOI_CLB) and ten.endswith(".docx"):
            os.remove(os.path.join(thu_muc, ten))
    ra = []
    duong = os.path.join(thu_muc, TEN_CAI_DAT_MOI_CLB)
    with open(duong, "w", encoding="utf-8", newline="\n") as f:
        f.write(ghi_cai_dat_moi_clb(de))
    ra.append(duong)
    duong = os.path.join(thu_muc, TEN_CLB_CSV)
    ghi_clb_csv(de, duong)
    ra.append(duong)
    for c in co_thi:
        duong = os.path.join(thu_muc, "%s%s.docx" % (TIEN_TO_DOCX_MOI_CLB, c["club_id"]))
        ghi_docx_moi_clb(de, c, duong)
        ra.append(duong)
    return ra


# ------------------------------------------- FA-M2 (TH): đăng ký đường B, mỗi ngày một biểu mẫu

TIEN_TO_DOCX_DANG_KY = "NHAP_FORMS_DANG_KY_"
TEN_CAI_DAT_DANG_KY = "CAI_DAT_FORMS_DANG_KY.md"
TEN_DOCX_DANG_KY_TAT_CA = TIEN_TO_DOCX_DANG_KY + "TAT_CA.docx"      # FA-M2b: một biểu mẫu cho mọi ngày


def de_theo_so_nhap_clb(de, duong_so_nhap):
    """FA-S6: bản sao `de` có `loai` của từng CLB lấy từ Sổ nhập CLB của FA-M1 (`doc_clb_fa` của bộ chuyển đổi).
    Trả (de mới, cảnh báo); `de` gốc không đổi."""
    import chuyen_forms_sang_phan_mem as cv
    clb_fa, _giu, canh_bao = cv.doc_clb_fa(duong_so_nhap, de)
    de2 = copy.deepcopy(de)
    for c in de2["cau_lac_bo"]:
        if clb_fa.get(c["club_id"], {}).get("loai"):
            c["loai"] = clb_fa[c["club_id"]]["loai"]
    de2["_loai_tu_so_nhap"] = True
    return de2, canh_bao


def ghi_cai_dat_dang_ky(de, mot_bieu_mau=False):
    """CAI_DAT_FORMS_DANG_KY.md: hướng dẫn dựng tay biểu mẫu đăng ký đường B (TH: chưa thử trên Forms thật).

    `mot_bieu_mau=True` (FA-M2b): một biểu mẫu cho mọi ngày. False: đúng như trước (mỗi ngày một biểu mẫu)."""
    L = []
    w = L.append
    w("# Biểu mẫu đăng ký nguyện vọng — đường B, Microsoft Forms (FA-M2)")
    w("")
    w("> **TH = CHƯA thử trên Microsoft thật.** Tệp này do `tao_mau_forms.py --fa-daa` sinh từ `de_thi.json`; đừng sửa tay.")
    w("> Forms không có cách tạo biểu mẫu bằng chương trình: dựng tay theo tệp này. Chưa có quyết định D8")
    w("> (Power Apps hay Forms); đường nào được chọn, tài liệu này chỉ mô tả đường B.")
    w("")
    if mot_bieu_mau:
        w("MỘT biểu mẫu cho mọi ngày (%d ngày). Không có câu Ranking: mỗi ngày ba câu chọn riêng, bắt buộc," % len(de["buoi"]))
    else:
        w("Mỗi ngày một biểu mẫu (%d biểu mẫu). Không có câu Ranking: mỗi ngày ba câu chọn riêng, bắt buộc," % len(de["buoi"]))
    w("tên \"Nguyện vọng 1\", \"Nguyện vọng 2\", \"Nguyện vọng 3\" (ngày có ít hơn ba CLB thì ít câu hơn). Hai câu huy")
    w("chương không bắt buộc; mặc định huy chương theo thứ tự nguyện vọng (vàng NV1, bạc NV2, đồng NV3, CLB Tự do không nhận).")
    w("")
    w("## Mô tả biểu mẫu (dán một dòng này vào ô Description)")
    w("")
    w("> %s" % bm.CAU_HUONG_DAN_DANG_KY)
    w("")
    if mot_bieu_mau:
        w("## Một biểu mẫu cho mọi buổi — tệp `%s`" % TEN_DOCX_DANG_KY_TAT_CA)
        w("")
        w("- Học sinh chỉ nhận MỘT đường dẫn. Phần thông tin học sinh xuất hiện một lần, sau đó mỗi ngày có phần Nguyện vọng")
        w("  và phần Huy chương (thẻ câu vẫn là `[<buổi>-nv1..3]`, `[<buổi>-vang]`, `[<buổi>-doi]`).")
        w("- Ba câu Nguyện vọng của MỌI ngày đều bắt buộc.")
        w("- Nộp lại: phiếu mới thay toàn bộ phiếu cũ của em, cho mọi ngày (bộ chuyển đổi giữ phiếu CUỐI của mỗi ngày).")
        w("- Bật \"Allow respondents to edit their responses\" nếu tổ chức của em cho phép (TH: chưa thử).")
        w("- Xuất MỘT tệp Excel (Responses → Open in Excel) rồi đưa tệp đó cho `--dang-ky` của bộ chuyển đổi.")
        w("")
        w("| Phần | Tên phần | Câu hỏi | Kiểu | Bắt buộc |")
        w("|---|---|---|---|---|")
        so = 0
        for i, (ten, cac_cau) in enumerate(bm.cac_phan_fa_gop(de), 1):
            for j, (td, loai, lc, bb) in enumerate(cac_cau):
                so += 1
                w("| %s | %s | %d · `[%s]` | %s | %s |" % (
                    i if j == 0 else "", ten if j == 0 else "", so, bm.ma_cua_cau(td),
                    "Text" if loai == "text" else "Choice (%d lựa chọn)" % len(lc), "✅" if bb else "—"))
        w("")
    else:
        for b in de["buoi"]:
            w("## %s — tệp `%s%s.docx`" % (b["ten"], TIEN_TO_DOCX_DANG_KY, b["ma"]))
            w("")
            w("| Phần | Tên phần | Câu hỏi | Kiểu | Bắt buộc |")
            w("|---|---|---|---|---|")
            so = 0
            for i, (ten, cac_cau) in enumerate(bm.cac_phan_fa(de, b["ma"]), 1):
                for j, (td, loai, lc, bb) in enumerate(cac_cau):
                    so += 1
                    w("| %s | %s | %d · `[%s]` | %s | %s |" % (
                        i if j == 0 else "", ten if j == 0 else "", so, bm.ma_cua_cau(td),
                        "Text" if loai == "text" else "Choice (%d lựa chọn)" % len(lc), "✅" if bb else "—"))
            w("")
    w("Sau khi Quick Import, kiểm lại từng câu: câu nguyện vọng chọn **Required**, hai câu huy chương **tắt** Required.")
    w("")
    w("## Settings (mọi biểu mẫu)")
    w("")
    w("| Cài đặt | Giá trị | Vì sao |")
    w("|---|---|---|")
    w("| Who can fill out this form | **Only people in my organization** | Học sinh đăng nhập tài khoản trường |")
    w("| **Record name** | **BẬT** | Cột **Email** của tệp xuất là khoá của học sinh |")
    w("| One response per person | **TẮT** | Em được nộp lại đến hết hạn; bộ chuyển đổi lấy phiếu **cuối cùng** của mỗi email |")
    w("| Shuffle questions | **TẮT** | Thứ tự \"Nguyện vọng 1, 2, 3\" phải giữ nguyên |")
    w("| Shuffle options (câu nguyện vọng) | **BẬT** nếu Forms cho (TH) | Mỗi em thấy thứ tự CLB khác nhau, giảm thiên lệch vị trí |")
    w("| Start date / End date | Đặt đủ cả hai | Hết hạn tự khoá; hạn đăng ký mở ít nhất 5 ngày |")
    w("")
    w("## Giới hạn của đường B (so với ứng dụng)")
    w("")
    w("- Không tự lưu nháp; không có nút ▲▼; Forms không chặn chọn trùng CLB giữa ba câu (bộ chuyển đổi bỏ trùng và báo).")
    w("- Forms không bỏ chọn được đáp án: câu huy chương có sẵn đáp án \"%s\" / \"%s\"; bộ chuyển đổi đổi chúng thành ô trống." % (bm.GIU_MAC_DINH_VANG, bm.DOI_KHONG))
    if de.get("_loai_tu_so_nhap"):
        w("- Loại CLB lấy từ Sổ nhập CLB (`--so-nhap-clb`): câu vàng không liệt kê CLB Tự do.")
    else:
        w("- Nếu `de_thi.json` chưa ghi `loai` của CLB, câu vàng liệt kê cả CLB Tự do; chọn nhầm thì bộ chuyển đổi giữ mặc định và báo.")
    w("")
    return "\n".join(L)


def sinh_dang_ky(de, thu_muc, mot_bieu_mau=False):
    """Ghi hướng dẫn và .docx Quick Import vào `thu_muc`. Trả danh sách đường dẫn đã ghi.

    Mặc định: mỗi ngày một .docx. `mot_bieu_mau=True` (FA-M2b): MỘT .docx cho mọi ngày; vượt trần câu của Forms thì
    ném LoiDeThi và không ghi gì. Mỗi chế độ xoá tệp .docx cũ của chế độ kia."""
    if mot_bieu_mau and bm.dem_cau_fa_gop(de) > bm.TRAN_CAU_MOI_BIEU_MAU:
        raise bm.LoiDeThi("biểu mẫu đăng ký gộp có %d câu, vượt trần %d câu của một biểu mẫu Forms — "
                          "bỏ --mot-bieu-mau (mỗi ngày một biểu mẫu) hoặc giảm số ngày/CLB"
                          % (bm.dem_cau_fa_gop(de), bm.TRAN_CAU_MOI_BIEU_MAU))
    os.makedirs(thu_muc, exist_ok=True)
    for ten in os.listdir(thu_muc):
        if ten.startswith(TIEN_TO_DOCX_DANG_KY) and ten.endswith(".docx"):
            os.remove(os.path.join(thu_muc, ten))
    ra = []
    duong = os.path.join(thu_muc, TEN_CAI_DAT_DANG_KY)
    with open(duong, "w", encoding="utf-8", newline="\n") as f:
        f.write(ghi_cai_dat_dang_ky(de, mot_bieu_mau=True) if mot_bieu_mau else ghi_cai_dat_dang_ky(de))
    ra.append(duong)
    if mot_bieu_mau:
        duong = os.path.join(thu_muc, TEN_DOCX_DANG_KY_TAT_CA)
        ghi_docx_chi_thi(de, duong, phan=bm.cac_phan_fa_gop(de), hau_to=" — đăng ký tất cả các buổi")
        ra.append(duong)
        return ra
    for b in de["buoi"]:
        duong = os.path.join(thu_muc, "%s%s.docx" % (TIEN_TO_DOCX_DANG_KY, b["ma"]))
        ghi_docx_chi_thi(de, duong, phan=bm.cac_phan_fa(de, b["ma"]), hau_to=" — đăng ký %s" % b["ten"])
        ra.append(duong)
    return ra


# ------------------------------------------- FA-M4 (TH): mỗi CLB Tuyển chọn có 2-3 đề biến thể

TIEN_TO_DOCX_BIEN_THE = "NHAP_FORMS_BIEN_THE_"
TEN_CAI_DAT_BIEN_THE = "CAI_DAT_FORMS_BIEN_THE.md"


def ghi_cai_dat_bien_the(de, co):
    """CAI_DAT_FORMS_BIEN_THE.md (TH: chưa thử trên Forms thật). `co`: các CLB có `de_thi_bien_the`."""
    import phan_tich_cau_hoi as pt
    L = []
    w = L.append
    w("# Đề biến thể cho CLB Tuyển chọn trên Microsoft Forms (FA-M4)")
    w("")
    w("> **TH = CHƯA thử trên Microsoft thật.** Tệp do `tao_mau_forms.py --bien-the` sinh từ `de_thi.json` (khoá `de_thi_bien_the`"
      " của CLB: các đề B, C; đề A là `de_thi`). Đừng sửa tay.")
    w("")
    w("Mỗi CLB có 2 đề (3 đề chỉ khi rất nhiều em thi) **cùng số câu và cùng cơ cấu độ khó**. Mỗi đề là MỘT biểu mẫu riêng, "
      "không câu cổng (như chế độ `--moi-clb`); thẻ câu vẫn là `[<club_id>-<số câu>]` ở mọi đề.")
    w("")
    w("## Chia đề cho học sinh")
    w("")
    w("Đề của một em = `crc32(email) % số đề` (`zlib.crc32`, chữ thường). Lập bảng đề cho từng em, gồm cả đề khi thi lại:")
    w("")
    w("```bash")
    w("python mau_forms_thi_clb/phan_tich_cau_hoi.py chia DANH_SACH.csv --so-bien-the 2 --ra DE_CUA_EM.csv")
    w("```")
    w("")
    w("`DANH_SACH.csv` có cột Email; kết quả có Email, DeGiao, DeThiLai. Gửi mỗi em đường dẫn đúng đề của em.")
    w("")
    w("## Từng biểu mẫu")
    w("")
    w("| CLB | Đề | Số câu | Tệp Quick Import |")
    w("|---|---|---|---|")
    for c in co:
        for k, qs in enumerate(pt.cac_bien_the(c)):
            w("| %s | %s | %d | `%s%s_%s.docx` |" % (c["name"], pt.CHU_BIEN_THE[k], len(qs), TIEN_TO_DOCX_BIEN_THE,
                                                     c["club_id"], pt.CHU_BIEN_THE[k]))
    w("")
    w("Sau Quick Import, đặt đáp án đúng và điểm **%s** mỗi câu như hướng dẫn của `CAI_DAT_FORMS_CHI_THI.md`." % bm.ghi_so(de["diem_moi_cau"]))
    w("")
    w("## Settings (mọi biểu mẫu đề thi)")
    w("")
    w("| Cài đặt | Giá trị | Vì sao |")
    w("|---|---|---|")
    w("| Time limit | **BẬT** (đặt số phút cho cả bài) | Hết giờ Forms tự nộp (D9); thay cho giới hạn từng câu mà Forms không có |")
    w("| Shuffle questions | **BẬT** | Mỗi em một thứ tự câu; biểu mẫu này không rẽ nhánh nên không hỏng gì |")
    w("| Shuffle options | **BẬT** | Chấm theo nội dung lựa chọn, không theo vị trí |")
    w("| Record name | **BẬT** | Cột Email là khoá ghép với danh sách đăng ký |")
    w("| One response per person | **BẬT** | Chỉ một lần làm; thi lại là một biểu mẫu KHÁC (đề khác) |")
    w("| Show results automatically | **TẮT** | Tránh em làm trước chuyền đáp án |")
    w("")
    w("## Sau khi thi")
    w("")
    w("```bash")
    w("python mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py --fa-daa --so-nhap-clb SO_NHAP_CLB.xlsx \\")
    w("    --lists DANH_SACH_DANG_KY.csv --ra ra/ THI_clb_A.xlsx THI_clb_B.xlsx --bien-the-tep THI_clb_B.xlsx=B")
    w("```")
    w("")
    w("- `PHAN_TICH_CAU_HOI.xlsx`: mỗi câu % đúng và độ phân biệt (1/3 điểm cao - 1/3 điểm thấp). Cờ `PHAN_BIET_AM` (< 0), "
      "`QUA_DE` (> 90 %), `QUA_KHO` (< 20 %). Admin xác nhận bỏ một câu lỗi thì chạy lại với `--bo-cau <club_id>-<đề>-<số câu>` (ví dụ `clb_covua-B-3`; CLB chỉ có một đề: `clb_covua-3`): chấm lại cho mọi em làm đề đó.")
    w("- `DIEU_CHINH_BAN_DE.xlsx` (D11): so trung bình từng đề với các đề còn lại trên thang 0-10 chưa làm tròn. Ngưỡng "
      "= z × √(s²/n + s²/n), z = 1,96 (2 đề) hoặc 2,39 (3 đề). Đề dưới 5 bài chỉ báo, không bao giờ chỉnh. Chỉ khi vượt ngưỡng thì "
      "đề đó được dịch (trung bình chung − trung bình đề), rồi làm tròn nửa lên và kẹp 0-10.")
    w("- Khi có chênh lệch, bộ chuyển đổi **không** ghi Sổ nhập tới khi admin chọn: `--ap-dung-dieu-chinh` (dịch điểm) hoặc "
      "`--giu-diem-goc` (giữ điểm đã chấm). Luôn có cách đi tiếp, không có gì chặn cứng. Không lệch thì không cần cờ.")
    w("- Em làm bài dưới 1/3 thời gian trung vị của CLB bị gắn cờ (chỉ báo); admin cho thi lại bằng đề `DeThiLai`.")
    w("- CLB chỉ có MỘT đề (không có đề B) thì em bị gắn cờ không thi lại được: thi lại phải bằng đề khác. "
      "Bộ chuyển đổi báo \"không có đề thi lại\" và giữ điểm bài đầu; muốn cho thi lại thì thêm đề B cho CLB đó.")
    w("")
    return "\n".join(L)


def sinh_bien_the(de, thu_muc):
    """Ghi hướng dẫn và mỗi (CLB, đề) một .docx Quick Import. Lỗi đề (số câu, độ khó, quá 3 đề) hoặc không CLB nào có đề
    biến thể thì ném LoiDeThi và không ghi gì."""
    import phan_tich_cau_hoi as pt
    co = [c for c in de["cau_lac_bo"] if c.get("de_thi_bien_the")]
    if not co:
        raise bm.LoiDeThi("de_thi.json không CLB nào có de_thi_bien_the (các đề B, C của CLB)")
    loi = [x for c in co for x in pt.kiem_bien_the(c)]
    if loi:
        raise bm.LoiDeThi("de_thi.json sai:\n  - " + "\n  - ".join(loi))
    os.makedirs(thu_muc, exist_ok=True)
    for ten in os.listdir(thu_muc):
        if ten.startswith(TIEN_TO_DOCX_BIEN_THE) and ten.endswith(".docx"):
            os.remove(os.path.join(thu_muc, ten))
    ra = []
    duong = os.path.join(thu_muc, TEN_CAI_DAT_BIEN_THE)
    with open(duong, "w", encoding="utf-8", newline="\n") as f:
        f.write(ghi_cai_dat_bien_the(de, co))
    ra.append(duong)
    for c in co:
        for k, qs in enumerate(pt.cac_bien_the(c)):
            duong = os.path.join(thu_muc, "%s%s_%s.docx" % (TIEN_TO_DOCX_BIEN_THE, c["club_id"], pt.CHU_BIEN_THE[k]))
            ghi_docx_chi_thi(de, duong, phan=bm.cac_phan_moi_clb(de, dict(c, de_thi=qs)),
                             hau_to=" — %s, đề %s" % (c["name"], pt.CHU_BIEN_THE[k]))
            ra.append(duong)
    return ra


# ------------------------------------------- GAP-5 / GAP-6 (TH): biểu mẫu khảo sát học sinh sau khi xếp

def _ghi_khao_sat(de, thu_muc, ten_docx, ten_md, phan, hau_to, tieu_de_md, cau_md):
    """Ghi một biểu mẫu khảo sát (.docx Quick Import + hướng dẫn .md). Sinh lại cho ra tệp giống hệt từng byte."""
    os.makedirs(thu_muc, exist_ok=True)
    duong_md = os.path.join(thu_muc, ten_md)
    dong = ["# %s" % tieu_de_md, "",
            "> **TH — chưa thử trên Microsoft Forms thật.** Sinh từ `tao_mau_forms.py`; đừng sửa tay.", "",
            "## Cài đặt", "",
            "- Nhập `%s` bằng Quick Import." % ten_docx,
            "- Settings: chỉ một lần trả lời mỗi người; mọi câu bắt buộc.",
            "- Xuất kết quả: Responses → Open in Excel; đem tệp đó nạp ở kiosk (khung Phản hồi, nút Nạp từ Forms).",
            "- Câu hỏi giữ nguyên phần mã trong ngoặc vuông và ngoặc tròn: kiosk đọc theo mã đó.", "",
            "## Câu hỏi", ""] + ["- %s" % c for c in cau_md] + [""]
    with open(duong_md, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(dong))
    duong_docx = os.path.join(thu_muc, ten_docx)
    ghi_docx_chi_thi(de, duong_docx, phan=phan, hau_to=hau_to)
    return [duong_md, duong_docx]


def sinh_phan_hoi(de, thu_muc):
    """GAP-5 (TH): biểu mẫu 3 câu phản hồi."""
    return _ghi_khao_sat(de, thu_muc, "NHAP_FORMS_PHAN_HOI.docx", "CAI_DAT_FORMS_PHAN_HOI.md",
                         bm.cac_phan_phan_hoi(), " — phản hồi sau khi xem kết quả",
                         "Biểu mẫu phản hồi sau khi xem kết quả (3 câu)",
                         [bm.CAU_HAI_LONG, bm.CAU_HIEU_LY_DO, bm.CAU_KHO_NHAT])


def sinh_tuan_3(de, thu_muc):
    """GAP-6 (TH): biểu mẫu khảo sát tuần 3."""
    return _ghi_khao_sat(de, thu_muc, "NHAP_FORMS_TUAN_3.docx", "CAI_DAT_FORMS_TUAN_3.md",
                         bm.cac_phan_tuan_3(), " — khảo sát tuần 3", "Khảo sát tuần 3 (2 câu)",
                         [bm.CAU_CON_DI, bm.CAU_MUON_DOI])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--chi-thi", action="store_true",
                    help="chế độ chỉ thi: bỏ câu Ranking và ô mã HS (nguyện vọng ở ứng dụng đăng ký)")
    ap.add_argument("--moi-clb", action="store_true",
                    help="mỗi CLB có đề một biểu mẫu riêng, không câu cổng (+ CLB.csv cho list CLB)")
    ap.add_argument("--fa-daa", action="store_true",
                    help="FA-DAA đường B (TH): mỗi ngày một biểu mẫu đăng ký, ba câu Nguyện vọng + hai câu huy chương")
    ap.add_argument("--mot-bieu-mau", action="store_true",
                    help="chỉ với --fa-daa (FA-M2b, TH): MỘT biểu mẫu đăng ký cho mọi ngày thay vì mỗi ngày một biểu mẫu")
    ap.add_argument("--bien-the", action="store_true",
                    help="FA-DAA (TH): mỗi CLB có de_thi_bien_the sinh một biểu mẫu cho từng đề (A, B, C) + hướng dẫn")
    ap.add_argument("--phan-hoi", action="store_true",
                    help="GAP-5 (TH): biểu mẫu 3 câu phản hồi sau khi xem kết quả")
    ap.add_argument("--tuan-3", action="store_true",
                    help="GAP-6 (TH): biểu mẫu khảo sát tuần 3 (còn đi CLB? muốn đổi?)")
    ap.add_argument("--so-nhap-clb", metavar="SO_NHAP_CLB.xlsx",
                    help="chỉ với --fa-daa: Sổ nhập CLB (FA-M1) để biết Loại; CLB Tự do không có trong câu vàng")
    ap.add_argument("--ra", default=THU_MUC, help="thư mục ghi (mặc định: cạnh tệp này)")
    ap.add_argument("--de", default=bm.DE_THI_MAC_DINH, help="de_thi.json")
    a = ap.parse_args(argv)
    if a.moi_clb and a.chi_thi:
        ap.error("--moi-clb và --chi-thi là hai chế độ khác nhau, chọn một")
    if a.fa_daa and (a.moi_clb or a.chi_thi):
        ap.error("--fa-daa là một chế độ riêng, không dùng chung với --chi-thi hay --moi-clb")
    if a.bien_the and (a.fa_daa or a.moi_clb or a.chi_thi):
        ap.error("--bien-the là một chế độ riêng, không dùng chung với --fa-daa, --chi-thi hay --moi-clb")
    if a.tuan_3 and (a.phan_hoi or a.fa_daa or a.moi_clb or a.chi_thi or a.bien_the):
        ap.error("--tuan-3 là một chế độ riêng, không dùng chung với chế độ khác")
    if a.phan_hoi and (a.fa_daa or a.moi_clb or a.chi_thi or a.bien_the):
        ap.error("--phan-hoi là một chế độ riêng, không dùng chung với chế độ khác")
    if a.mot_bieu_mau and not a.fa_daa:
        ap.error("--mot-bieu-mau chỉ dùng cùng --fa-daa")
    if a.so_nhap_clb and not a.fa_daa:
        ap.error("--so-nhap-clb chỉ dùng cùng --fa-daa")
    try:
        de = bm.doc_de_thi(a.de)
        if a.tuan_3:
            ra = sinh_tuan_3(de, a.ra)
            print("Đã sinh mẫu Forms khảo sát tuần 3 (TH): %s." % ", ".join(os.path.basename(x) for x in ra))
            return 0
        if a.phan_hoi:
            ra = sinh_phan_hoi(de, a.ra)
            print("Đã sinh mẫu Forms phản hồi (TH): %s." % ", ".join(os.path.basename(x) for x in ra))
            return 0
        if a.bien_the:
            ra = sinh_bien_the(de, a.ra)
            print("Đã sinh mẫu Forms đề biến thể (TH): %d tệp (%s)." % (len(ra), ", ".join(os.path.basename(x) for x in ra)))
            return 0
        if a.fa_daa:
            if a.so_nhap_clb:
                import chuyen_forms_sang_phan_mem as cv
                try:
                    de, canh_bao = de_theo_so_nhap_clb(de, a.so_nhap_clb)
                except cv.LoiTepXuat as e:
                    print("KHÔNG GHI TỆP NÀO — %s" % e, file=sys.stderr)
                    return 1
                for _d, _e, nd in canh_bao:
                    print("CẢNH BÁO: " + nd, file=sys.stderr)
            ra = sinh_dang_ky(de, a.ra, mot_bieu_mau=a.mot_bieu_mau)
            print("Đã sinh mẫu Forms đăng ký FA-DAA (TH): %d biểu mẫu (%s)."
                  % (1 if a.mot_bieu_mau else len(de["buoi"]), ", ".join(os.path.basename(x) for x in ra)))
            return 0
        if a.moi_clb:
            ra = sinh_moi_clb(de, a.ra)
            print("Đã sinh mẫu Forms mỗi CLB một biểu mẫu: %d biểu mẫu (%s)."
                  % (len(bm.clb_co_thi(de)), ", ".join(os.path.basename(x) for x in ra)))
            return 0
        if a.chi_thi:
            ra = sinh_chi_thi(de, a.ra)
            nhom = bm.chia_theo_buoi(de, chi_thi=True)
            print("Đã sinh mẫu Forms chỉ thi: %d câu, %d biểu mẫu (%s)."
                  % (bm.dem_cau(de, chi_thi=True), len(nhom),
                     ", ".join(os.path.basename(x) for x in ra)))
            return 0
    except bm.LoiDeThi as e:
        print("KHÔNG GHI TỆP NÀO — %s" % e, file=sys.stderr)
        return 1
    with open(os.path.join(THU_MUC, "CAI_DAT_FORMS.md"), "w", encoding="utf-8") as f:
        f.write(ghi_cai_dat(de))
    ghi_mau_xuat(de, os.path.join(THU_MUC, "MAU_XUAT_TU_FORMS.xlsx"))
    try:
        ghi_docx(de, os.path.join(THU_MUC, "NHAP_FORMS_THI_CLB.docx"))
    except ImportError:
        print("Thiếu python-docx — BỎ QUA NHAP_FORMS_THI_CLB.docx "
              "(pip install -r requirements-dev.txt)", file=sys.stderr)
    print("Đã sinh mẫu Forms: %d phần, %d câu hỏi."
          % (len(bm.cac_phan(de)), sum(len(c) for _, c in bm.cac_phan(de))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
