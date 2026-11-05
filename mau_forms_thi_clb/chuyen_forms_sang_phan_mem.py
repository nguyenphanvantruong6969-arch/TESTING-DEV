"""Chuyển tệp Excel Microsoft Forms xuất ra thành Sổ nhập CLB + bảng điểm.

    python mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py KET_QUA_FORMS.xlsx --ra ./nap

Ghi ra thư mục --ra:

    SO_NHAP_CLB.xlsx    MỘT tệp kéo thẳng vào phần mềm: sheet "1. CLB" dựng từ
                        de_thi.json, sheet "2. Học sinh" có nguyện vọng các buổi
                        và điểm đã chấm ngay cạnh CLB em thi
    BANG_DIEM.xlsx      bảng điểm, chi tiết đúng/sai, thống kê đề, cảnh báo

Điểm được CHẤM LẠI từ đáp án trong de_thi.json, không lấy cột "Points" của
Forms. Có cột Points thì đem ra đối chiếu: lệch nhau nghĩa là đáp án trên
Forms và trong de_thi.json không còn khớp, và phải biết điều đó TRƯỚC khi
dùng điểm để xét tuyển.

Chế độ "chỉ thi" (T4M-Q1): Forms chỉ có bài thi, nguyện vọng nằm ở ứng dụng đăng ký
(SharePoint List, mô hình rộng, "Export to CSV"). Khoá là cột Email Forms tự ghi (chữ
thường), ghép với cột Email của tệp xuất List:

    python mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py KET_QUA_FORMS.xlsx --chi-thi \\
        --lists DANH_SACH_DANG_KY.csv --ra ./nap

Có nhiều biểu mẫu (tách theo buổi vì vượt 200 câu) thì liệt kê nhiều tệp .xlsx. Phiếu trùng
giữ phiếu ĐẦU; email lạ (không có trong List) bị báo và bỏ; thi CLB mà List không có nguyện
vọng CLB đó thì bỏ điểm (vẫn nằm trong BANG_DIEM.xlsx) và báo. Không có bài thi nào thì
SO_NHAP_CLB.xlsx chỉ có nguyện vọng, không điểm.

Tệp xuất thiếu hẳn một câu của mẫu thì dừng, không ghi tệp nào. Một ô sai
lẻ (mã CLB lạ, thi CLB chưa xếp nguyện vọng…) thì bỏ riêng ô đó và báo
đích danh dòng — đúng cách phần mềm xử lý khi nạp.
"""

import argparse
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bieu_mau as bm  # noqa: E402
import so_nhap  # noqa: E402

TIEN_TO_DIEM = "Points - "
TIEN_TO_NHAN_XET = "Feedback - "


class LoiTepXuat(ValueError):
    """Tệp xuất không dùng được — không ghi tệp nào."""


def _o(gia_tri):
    if gia_tri is None:
        return ""
    if isinstance(gia_tri, float) and gia_tri.is_integer():
        return str(int(gia_tri))
    return str(gia_tri).strip()


def doc_tep_xuat(duong_dan):
    """Trả về (tiêu đề, các dòng) của sheet đầu — Forms chỉ xuất một sheet."""
    import openpyxl

    wb = openpyxl.load_workbook(duong_dan, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    dong = [[_o(x) for x in r] for r in ws.iter_rows(values_only=True)]
    wb.close()
    if not dong:
        raise LoiTepXuat("tệp trống")
    return dong[0], dong[1:]


def _doc_cot(tieu_de):
    """{mã câu: [chỉ số cột]} và {mã câu: chỉ số cột Points}."""
    cot, cot_diem = {}, {}
    for i, h in enumerate(tieu_de):
        if h.startswith(TIEN_TO_NHAN_XET):
            continue
        if h.startswith(TIEN_TO_DIEM):
            ma = bm.ma_cua_cau(h[len(TIEN_TO_DIEM):])
            if ma:
                cot_diem[ma] = i
            continue
        ma = bm.ma_cua_cau(h)
        if ma:
            # Nhiều cột cùng mã (Ranking tách mỗi vị trí một cột) thì nối lại
            # theo thứ tự cột.
            cot.setdefault(ma, []).append(i)
    return cot, cot_diem


def _ban_do_cot(de, tieu_de):
    """{mã câu: [chỉ số cột]} và {mã câu: chỉ số cột Points}."""
    cot, cot_diem = _doc_cot(tieu_de)
    can = ["student_id", "name"] + [b["ma"] for b in de["buoi"]]
    for clb in bm.clb_co_thi(de):
        can.append("thi-" + clb["club_id"])
        can += ["%s-%d" % (clb["club_id"], i) for i in range(1, len(clb["de_thi"]) + 1)]
    thieu = [m for m in can if m not in cot]
    if thieu:
        raise LoiTepXuat(
            "tệp xuất thiếu %d câu của mẫu (mã: %s). Câu hỏi trên Forms phải "
            "giữ nguyên phần [mã] ở đầu." % (len(thieu), ", ".join(thieu)))
    la = sorted(set(cot) - set(can))
    return cot, cot_diem, la


def _gia_tri(dong, cac_cot):
    return ";".join(dong[i] for i in cac_cot if i < len(dong) and dong[i])


def _ap_tran_thi(de, theo_ma, nguyen_vong, bai_thi, bao):
    """Mỗi buổi chỉ nạp bài của các CLB em xếp cao nhất, tới đúng trần thi."""
    for b in de["buoi"]:
        # Sổ nhập CHẶN cả sổ khi một em thi quá trần trong một buổi
        # (so_nhap_qua_tran_thi), nên ở đây chỉ nạp bài của các CLB em xếp
        # cao nhất, tới đúng trần; bài còn lại vẫn có trong BANG_DIEM.xlsx.
        xep = nguyen_vong.get(b["ma"], [])
        thi = sorted((t for t in bai_thi
                      if t["nap"] and theo_ma[t["club_id"]]["buoi"] == b["ma"]),
                     key=lambda t: xep.index(t["club_id"]))
        if len(thi) > bm.TRAN_THI_MOI_BUOI:
            bo = thi[bm.TRAN_THI_MOI_BUOI:]
            for t in bo:
                t["nap"] = False
            bao("%s: dự thi %d CLB, vượt trần %d. Chỉ nạp bài của %d CLB xếp "
                "cao nhất; không nạp: %s"
                % (b["ma"], len(thi), bm.TRAN_THI_MOI_BUOI, bm.TRAN_THI_MOI_BUOI,
                   ", ".join(t["club_id"] for t in bo)))


def phan_tich(de, tieu_de, cac_dong):
    """Đọc toàn bộ phản hồi. Không ghi gì — chỉ trả kết quả và cảnh báo."""
    cot, cot_diem, la = _ban_do_cot(de, tieu_de)
    canh_bao = []
    if la:
        canh_bao.append(("", "", "bỏ qua %d câu không thuộc mẫu: %s"
                         % (len(la), ", ".join(la))))

    theo_ma = {c["club_id"]: c for c in de["cau_lac_bo"]}
    theo_ten = {bm._chuan(c["name"]): c for c in de["cau_lac_bo"]}
    hoc_sinh = {}  # student_id -> bản ghi của phiếu ĐẦU TIÊN

    for so_dong, dong in enumerate(cac_dong, 2):
        if not any(dong):
            continue
        sid = _gia_tri(dong, cot["student_id"])
        if not sid:
            canh_bao.append((so_dong, "", "phiếu không có mã học sinh — bỏ cả phiếu"))
            continue

        def bao(noi_dung, so_dong=so_dong, sid=sid):
            canh_bao.append((so_dong, sid, noi_dung))

        nguyen_vong = {}
        for b in de["buoi"]:
            ds = []
            for muc in _gia_tri(dong, cot[b["ma"]]).split(";"):
                muc = muc.strip()
                if not muc:
                    continue
                clb = theo_ma.get(bm.ma_trong_lua_chon(muc)) or theo_ten.get(bm._chuan(muc))
                if clb is None:
                    bao("%s: lựa chọn %r không phải CLB nào trong de_thi.json — bỏ ô này"
                        % (b["ma"], muc))
                elif clb["buoi"] != b["ma"]:
                    bao("%s: %s sinh hoạt %s, không thuộc buổi này — bỏ ô này"
                        % (b["ma"], clb["club_id"], clb["buoi"]))
                elif clb["club_id"] not in ds:
                    ds.append(clb["club_id"])
            if len(ds) > bm.TRAN_CLB_MOI_BUOI:
                bao("%s: %d nguyện vọng, chỉ giữ %d đầu"
                    % (b["ma"], len(ds), bm.TRAN_CLB_MOI_BUOI))
                ds = ds[:bm.TRAN_CLB_MOI_BUOI]
            if ds:
                nguyen_vong[b["ma"]] = ds

        bai_thi = []
        for clb in bm.clb_co_thi(de):
            ma = clb["club_id"]
            if not bm._chuan(_gia_tri(dong, cot["thi-" + ma])).startswith("có"):
                continue
            tra_loi = {i: _gia_tri(dong, cot["%s-%d" % (ma, i)])
                       for i in range(1, len(clb["de_thi"]) + 1)}
            diem, dung = bm.cham_bai(de, clb, tra_loi)
            cot_p = [cot_diem.get("%s-%d" % (ma, i)) for i in tra_loi]
            if all(c is not None for c in cot_p):
                try:
                    diem_forms = sum(float(dong[c] or 0) for c in cot_p)
                except ValueError:
                    diem_forms = None
                if diem_forms is not None and abs(diem_forms - diem) > 1e-9:
                    bao("%s: Forms chấm %s, đáp án de_thi.json chấm %s — đáp án "
                        "trên Forms đã lệch, soát lại trước khi dùng điểm"
                        % (ma, bm.ghi_so(diem_forms), bm.ghi_so(diem)))
            da_xep = ma in nguyen_vong.get(clb["buoi"], [])
            if not da_xep:
                # Điểm cho CLB em không xếp là điểm không dùng tới — phần mềm
                # cũng sẽ bỏ. Giữ trong bảng điểm để giáo viên vẫn thấy bài.
                bao("%s: em làm bài thi nhưng KHÔNG xếp CLB này ở nguyện vọng %s "
                    "— điểm có trong BANG_DIEM.xlsx nhưng không nạp vào phần mềm"
                    % (ma, clb["buoi"]))
            bai_thi.append({"club_id": ma, "diem": diem, "dung": dung,
                            "tra_loi": tra_loi, "nap": da_xep})

        _ap_tran_thi(de, theo_ma, nguyen_vong, bai_thi, bao)

        if sid in hoc_sinh:
            # Giữ phiếu ĐẦU: đây là bài thi, cho nộp lại là cho làm lại tới
            # khi được điểm cao. Muốn đổi nguyện vọng thì giáo viên sửa tay.
            bao("nộp lần nữa — BỎ phiếu này, giữ phiếu đầu ở dòng %d"
                % hoc_sinh[sid]["dong"])
            continue
        hoc_sinh[sid] = {"dong": so_dong, "student_id": sid,
                         "name": _gia_tri(dong, cot["name"]),
                         "nguyen_vong": nguyen_vong, "bai_thi": bai_thi}
        if not nguyen_vong:
            bao("không xếp nguyện vọng buổi nào")

    return list(hoc_sinh.values()), canh_bao


# ------------------------------------------------- chế độ "chỉ thi" (T4M-Q1)

def _ma_buoi_tu_thu(de, gia_tri):
    """'Thứ 2' / 'Thứ Hai' / 'thu_2' -> 'thu_2'. Không nhận ra -> None."""
    g = bm._chuan(gia_tri)
    for b in de["buoi"]:
        if g in (bm._chuan(b["ma"]), bm._chuan(b["ten"])):
            return b["ma"]
    m = re.search(r"(\d+)$", g)
    if m:
        for b in de["buoi"]:
            if b["ma"] == "thu_" + m.group(1):
                return b["ma"]
    return None


def doc_lists(duong_csv, de):
    """Đọc tệp xuất List (mô hình RỘNG: mỗi dòng một em × một ngày, cột NV1..NVn).

    Trả ({email chữ thường: {dong, email, name, nguyen_vong}}, cảnh báo). Cột bắt buộc: Email,
    Thu, NV1; tùy chọn: HoTen (hoặc Name), NV2.. Dòng trùng (em, ngày): giữ dòng ĐẦU.
    """
    with open(duong_csv, encoding="utf-8-sig", newline="") as f:
        bang = list(csv.reader(f))
    if not bang:
        raise LoiTepXuat("tệp List trống")
    tieu = [h.strip().lower() for h in bang[0]]
    i_email = tieu.index("email") if "email" in tieu else None
    i_thu = tieu.index("thu") if "thu" in tieu else None
    i_ten = next((tieu.index(k) for k in ("hoten", "name") if k in tieu), None)
    cot_nv = sorted((int(m.group(1)), i) for i, h in enumerate(tieu)
                    for m in [re.fullmatch(r"nv(\d+)", h)] if m)
    thieu = [k for k, v in (("Email", i_email), ("Thu", i_thu), ("NV1", cot_nv[0][0] if cot_nv else None))
             if v is None]
    if thieu:
        raise LoiTepXuat("tệp List thiếu cột bắt buộc: %s" % ", ".join(thieu))

    theo_ma = {c["club_id"]: c for c in de["cau_lac_bo"]}
    theo_ten = {bm._chuan(c["name"]): c for c in de["cau_lac_bo"]}
    ds, canh_bao = {}, []
    for so_dong, dong in enumerate(bang[1:], 2):
        if not any(x.strip() for x in dong):
            continue
        dong = dong + [""] * (len(tieu) - len(dong))
        email = dong[i_email].strip().lower()
        if not email:
            canh_bao.append((so_dong, "", "dòng List không có email — bỏ dòng"))
            continue

        def bao(noi_dung, so_dong=so_dong, email=email):
            canh_bao.append((so_dong, email, noi_dung))

        buoi = _ma_buoi_tu_thu(de, dong[i_thu])
        if buoi is None:
            bao("ngày %r không khớp buổi nào trong de_thi.json — bỏ dòng" % dong[i_thu])
            continue
        hs = ds.setdefault(email, {"dong": so_dong, "email": email, "name": "",
                                   "nguyen_vong": {}, "_buoi": set()})
        if i_ten is not None and not hs["name"]:
            hs["name"] = dong[i_ten].strip()
        if buoi in hs["_buoi"]:
            bao("%s: dòng trùng (em, ngày) — bỏ dòng này, giữ dòng đầu" % buoi)
            continue
        hs["_buoi"].add(buoi)
        xep = []
        for _so, i in cot_nv:
            muc = dong[i].strip()
            if not muc:
                continue
            clb = (theo_ma.get(muc) or theo_ma.get(bm.ma_trong_lua_chon(muc))
                   or theo_ten.get(bm._chuan(muc)))
            if clb is None:
                bao("%s: lựa chọn %r không phải CLB nào trong de_thi.json — bỏ ô này" % (buoi, muc))
            elif clb["buoi"] != buoi:
                bao("%s: %s sinh hoạt %s, không thuộc buổi này — bỏ ô này"
                    % (buoi, clb["club_id"], clb["buoi"]))
            elif clb["club_id"] not in xep:
                xep.append(clb["club_id"])
        if len(xep) > bm.TRAN_CLB_MOI_BUOI:
            bao("%s: %d nguyện vọng, chỉ giữ %d đầu" % (buoi, len(xep), bm.TRAN_CLB_MOI_BUOI))
            xep = xep[:bm.TRAN_CLB_MOI_BUOI]
        if xep:
            hs["nguyen_vong"][buoi] = xep
    for hs in ds.values():
        del hs["_buoi"]
    return ds, canh_bao


def _cot_chi_thi(de, tieu_de):
    """Cột Email/Name và cột bài thi của MỘT tệp Forms chỉ-thi.

    Trả (i_email, i_ten, cot, cot_diem, các CLB tệp này phủ, mã câu lạ). Một CLB phủ khi tệp có
    câu cổng; có một phần cột của CLB mà thiếu phần khác thì dừng. CLB không có cột nào = tệp này
    là của buổi khác (tách theo buoi), không phải lỗi.
    """
    cot, cot_diem = _doc_cot(tieu_de)
    chuan = [h.strip().lower() for h in tieu_de]
    if "email" not in chuan:
        raise LoiTepXuat("tệp xuất không có cột Email — bật \"Record name\" trong Settings của "
                         "biểu mẫu (và chỉ cho người trong tổ chức làm bài)")
    i_email = chuan.index("email")
    i_ten = chuan.index("name") if "name" in chuan else None
    phu, thieu, can_het = [], [], set()
    for clb in bm.clb_co_thi(de):
        can = ["thi-" + clb["club_id"]] + ["%s-%d" % (clb["club_id"], i)
                                          for i in range(1, len(clb["de_thi"]) + 1)]
        co = [m for m in can if m in cot]
        if not co:
            continue
        thieu += [m for m in can if m not in cot]
        phu.append(clb)
        can_het.update(can)
    if thieu:
        raise LoiTepXuat(
            "tệp xuất thiếu %d câu của mẫu (mã: %s). Câu hỏi trên Forms phải "
            "giữ nguyên phần [mã] ở đầu." % (len(thieu), ", ".join(thieu)))
    if not phu:
        raise LoiTepXuat("tệp xuất không có câu bài thi nào của mẫu (không thấy mã [thi-...])")
    return i_email, i_ten, cot, cot_diem, phu, sorted(set(cot) - can_het)


def phan_tich_chi_thi(de, danh_sach, cac_tep):
    """Ghép các tệp Forms chỉ-thi với danh sách đăng ký. Không ghi gì.

    danh_sach: kết quả doc_lists. cac_tep: [(tên tệp, tiêu đề, các dòng)]. Trả (hoc_sinh theo
    thứ tự List, cảnh báo). Học sinh trong List mà không có bài thi vẫn có mặt (chỉ nguyện vọng).
    """
    canh_bao = []
    theo_ma = {c["club_id"]: c for c in de["cau_lac_bo"]}
    hoc_sinh = {e: {"dong": h["dong"], "student_id": e, "name": h["name"],
                    "nguyen_vong": h["nguyen_vong"], "bai_thi": []}
                for e, h in danh_sach.items()}
    da_phu = set()
    for ten_tep, tieu_de, cac_dong in cac_tep:
        i_email, i_ten, cot, cot_diem, phu, la = _cot_chi_thi(de, tieu_de)
        da_phu.update(c["club_id"] for c in phu)
        if la:
            canh_bao.append(("", "", "%s: bỏ qua %d câu không thuộc bài thi: %s"
                             % (ten_tep, len(la), ", ".join(la))))
        da_thay = {}
        for so_dong, dong in enumerate(cac_dong, 2):
            if not any(dong):
                continue
            dong = dong + [""] * (len(tieu_de) - len(dong))
            email = dong[i_email].strip().lower()
            if not email or email == "anonymous":
                canh_bao.append((so_dong, "", "%s: phiếu không có Email (Record name chưa bật?) "
                                 "— bỏ cả phiếu" % ten_tep))
                continue

            def bao(noi_dung, so_dong=so_dong, email=email):
                canh_bao.append((so_dong, email, noi_dung))

            if email in da_thay:
                # Giữ phiếu ĐẦU: bài thi nộp lại không được thành làm lại.
                bao("nộp lần nữa — BỎ phiếu này, giữ phiếu đầu ở dòng %d" % da_thay[email])
                continue
            da_thay[email] = so_dong
            hs = hoc_sinh.get(email)
            if hs is None:
                bao("email %s không có trong danh sách đăng ký (List) — bỏ cả phiếu" % email)
                continue
            if i_ten is not None and not hs["name"]:
                hs["name"] = dong[i_ten].strip()
            bai_thi = []
            for clb in phu:
                ma = clb["club_id"]
                if not bm._chuan(_gia_tri(dong, cot["thi-" + ma])).startswith("có"):
                    continue
                if any(t["club_id"] == ma for t in hs["bai_thi"]):
                    bao("%s: đã có bài từ tệp khác — giữ bài đầu" % ma)
                    continue
                tra_loi = {i: _gia_tri(dong, cot["%s-%d" % (ma, i)])
                           for i in range(1, len(clb["de_thi"]) + 1)}
                diem, dung = bm.cham_bai(de, clb, tra_loi)
                cot_p = [cot_diem.get("%s-%d" % (ma, i)) for i in tra_loi]
                if all(c is not None for c in cot_p):
                    try:
                        diem_forms = sum(float(dong[c] or 0) for c in cot_p)
                    except ValueError:
                        diem_forms = None
                    if diem_forms is not None and abs(diem_forms - diem) > 1e-9:
                        bao("%s: Forms chấm %s, đáp án de_thi.json chấm %s — đáp án "
                            "trên Forms đã lệch, soát lại trước khi dùng điểm"
                            % (ma, bm.ghi_so(diem_forms), bm.ghi_so(diem)))
                da_xep = ma in hs["nguyen_vong"].get(clb["buoi"], [])
                if not da_xep:
                    bao("%s: em làm bài thi nhưng KHÔNG xếp CLB này ở nguyện vọng %s "
                        "— điểm có trong BANG_DIEM.xlsx nhưng không nạp vào phần mềm"
                        % (ma, clb["buoi"]))
                bai_thi.append({"club_id": ma, "diem": diem, "dung": dung,
                                "tra_loi": tra_loi, "nap": da_xep})
            hs["bai_thi"] += bai_thi

    for e, hs in hoc_sinh.items():
        _ap_tran_thi(de, theo_ma, hs["nguyen_vong"], hs["bai_thi"],
                     lambda nd, e=e, hs=hs: canh_bao.append((hs["dong"], e, nd)))
        if not hs["nguyen_vong"]:
            canh_bao.append((hs["dong"], e, "không xếp nguyện vọng buổi nào"))
    for clb in bm.clb_co_thi(de):
        if clb["club_id"] not in da_phu:
            canh_bao.append(("", "", "%s có đề thi nhưng không tệp Forms nào chứa câu của CLB này "
                             "— không có điểm cho CLB này" % clb["club_id"]))
    return list(hoc_sinh.values()), canh_bao


# ---------------------------------------------------------------- ghi tệp

TEN_SO = "SO_NHAP_CLB.xlsx"


def ghi_tep_phan_mem(de, hoc_sinh, thu_muc):
    """Ghi Sổ nhập CLB. Trả đường dẫn.

    Nguyện vọng các buổi nối thành một danh sách theo thứ tự buổi trong
    de_thi.json; điểm (chỉ bài được nạp) đặt ngay cạnh CLB đó.
    """
    clubs = [{"club_id": c["club_id"], "name": c["name"], "capacity": c["capacity"],
              "reserve_capacity": c["reserve_capacity"],
              "reserve_group": c["reserve_group"], "buoi": c["buoi"]}
             for c in de["cau_lac_bo"]]
    students = []
    for h in hoc_sinh:
        diem = {t["club_id"]: bm.ghi_so(t["diem"]) for t in h["bai_thi"] if t["nap"]}
        thu_tu = [ma for b in de["buoi"] for ma in h["nguyen_vong"].get(b["ma"], [])]
        # Không có nhóm: sổ ghi KHÔNG có cột Nhóm ưu tiên (co_nhom=False bên dưới).
        students.append({
            "student_id": h["student_id"], "name": h["name"], "reserve_group": "",
            "nv": [{"club_id": ma, "thi": ma in diem, "diem": diem.get(ma, "")}
                   for ma in thu_tu],
        })
    duong = os.path.join(thu_muc, TEN_SO)
    # co_nhom=False: Forms không hỏi nhóm ưu tiên. Không có cột thì phần mềm
    # GIỮ nhóm đã gán; có cột mà trống thì phần mềm sẽ BỎ nhóm của em.
    so_nhap.ghi_so_nhap(duong, clubs, students, co_nhom=False)
    return duong


def ghi_bang_diem(de, hoc_sinh, canh_bao, duong):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    dam = Font(bold=True, color="FFFFFF")
    nen = PatternFill("solid", fgColor="1F3A5F")
    co_thi = bm.clb_co_thi(de)

    def dau_bang(ws, tieu_de, rong):
        ws.append(tieu_de)
        for i, w in enumerate(rong, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
            ws.cell(1, i).font, ws.cell(1, i).fill = dam, nen
            ws.cell(1, i).alignment = Alignment(wrap_text=True, vertical="center")
        ws.freeze_panes = "C2"

    wb = Workbook()
    ws = wb.active
    ws.title = "Bảng điểm"
    dau_bang(ws, ["Mã HS", "Họ tên"]
             + ["%s (%s)\n/%s" % (c["name"], c["club_id"], bm.ghi_so(bm.diem_toi_da(de, c)))
                for c in co_thi] + ["Số CLB đã thi"],
             [10, 24] + [14] * len(co_thi) + [10])
    ws.row_dimensions[1].height = 45
    for h in hoc_sinh:
        diem = {t["club_id"]: t["diem"] for t in h["bai_thi"]}
        ws.append([h["student_id"], h["name"]]
                  + [diem.get(c["club_id"]) for c in co_thi] + [len(diem)])

    ws = wb.create_sheet("Chi tiết")
    n_cau = max(len(c["de_thi"]) for c in co_thi)
    dau_bang(ws, ["Mã HS", "Họ tên", "CLB", "Buổi"]
             + ["Câu %d" % i for i in range(1, n_cau + 1)]
             + ["Điểm", "Nạp vào phần mềm"],
             [10, 24, 14, 8] + [7] * n_cau + [7, 16])
    for h in hoc_sinh:
        for t in h["bai_thi"]:
            buoi = next(c["buoi"] for c in co_thi if c["club_id"] == t["club_id"])
            ws.append([h["student_id"], h["name"], t["club_id"], buoi]
                      + ["Đ" if x else "S" for x in t["dung"]]
                      + [""] * (n_cau - len(t["dung"]))
                      + [t["diem"], "Có" if t["nap"] else "Không — chưa xếp nguyện vọng"])

    ws = wb.create_sheet("Thống kê đề")
    dau_bang(ws, ["CLB", "Câu", "Nội dung", "Đáp án", "Số bài", "Số đúng", "Tỉ lệ đúng"],
             [14, 6, 50, 26, 8, 8, 10])
    for c in co_thi:
        bai = [t for h in hoc_sinh for t in h["bai_thi"] if t["club_id"] == c["club_id"]]
        for i, cau in enumerate(c["de_thi"]):
            dung = sum(t["dung"][i] for t in bai)
            ws.append([c["club_id"], i + 1, cau["cau"], cau["lua_chon"][cau["dap_an"]],
                       len(bai), dung, (dung / len(bai)) if bai else None])
            ws.cell(ws.max_row, 7).number_format = "0%"

    ws = wb.create_sheet("Cảnh báo")
    dau_bang(ws, ["Dòng Excel", "Mã HS", "Nội dung"], [10, 10, 100])
    for x in canh_bao:
        ws.append(list(x))
    if not canh_bao:
        ws.append(["", "", "Không có cảnh báo nào."])
    wb.save(duong)


# A13.13: workspace trường học BẬT điểm quyết tâm mặc định, mà biểu mẫu KHÔNG thu điểm đó (và
# không được bịa): sổ ra không có điểm quyết tâm, nên phải tắt tính năng trước khi nạp.
GHI_CHU_DIEM_QUYET_TAM = ("Dữ liệu không có điểm quyết tâm nên cần TẮT \"Dùng điểm quyết tâm\" trong "
                          "cấu hình không gian làm việc trước khi nạp sổ này.")


def chuyen(duong_xlsx, thu_muc_ra, de=None):
    de = de or bm.doc_de_thi()
    tieu_de, cac_dong = doc_tep_xuat(duong_xlsx)
    hoc_sinh, canh_bao = phan_tich(de, tieu_de, cac_dong)
    if not hoc_sinh:
        raise LoiTepXuat("tệp không có phiếu nào có mã học sinh")
    os.makedirs(thu_muc_ra, exist_ok=True)
    ghi_tep_phan_mem(de, hoc_sinh, thu_muc_ra)
    ghi_bang_diem(de, hoc_sinh, canh_bao, os.path.join(thu_muc_ra, "BANG_DIEM.xlsx"))
    return {"n_hoc_sinh": len(hoc_sinh),
            "n_bai_thi": sum(len(h["bai_thi"]) for h in hoc_sinh),
            "canh_bao": canh_bao,
            "ghi_chu": [GHI_CHU_DIEM_QUYET_TAM]}


def chuyen_chi_thi(cac_duong_xlsx, duong_lists, thu_muc_ra, de=None):
    """Chế độ chỉ thi: các tệp Forms (chỉ có bài thi) + tệp xuất List -> Sổ nhập + bảng điểm."""
    de = de or bm.doc_de_thi()
    danh_sach, canh_bao = doc_lists(duong_lists, de)
    if not danh_sach:
        raise LoiTepXuat("tệp List không có học sinh nào")
    cac_tep = []
    for d in cac_duong_xlsx:
        tieu_de, cac_dong = doc_tep_xuat(d)
        cac_tep.append((os.path.basename(d), tieu_de, cac_dong))
    hoc_sinh, canh_bao_thi = phan_tich_chi_thi(de, danh_sach, cac_tep)
    canh_bao += canh_bao_thi
    os.makedirs(thu_muc_ra, exist_ok=True)
    ghi_tep_phan_mem(de, hoc_sinh, thu_muc_ra)
    ghi_bang_diem(de, hoc_sinh, canh_bao, os.path.join(thu_muc_ra, "BANG_DIEM.xlsx"))
    return {"n_hoc_sinh": len(hoc_sinh),
            "n_bai_thi": sum(len(h["bai_thi"]) for h in hoc_sinh),
            "canh_bao": canh_bao,
            "ghi_chu": [GHI_CHU_DIEM_QUYET_TAM]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("tep_xuat", nargs="+",
                    help="tệp .xlsx tải từ Forms (Responses → Open in Excel); "
                         "nhiều tệp chỉ khi --chi-thi và biểu mẫu tách theo buổi")
    ap.add_argument("--ra", required=True, help="thư mục ghi kết quả")
    ap.add_argument("--de", default=bm.DE_THI_MAC_DINH, help="de_thi.json")
    ap.add_argument("--chi-thi", action="store_true",
                    help="Forms chỉ có bài thi, khoá là Email; cần --lists")
    ap.add_argument("--lists", help="tệp CSV xuất từ List đăng ký (chỉ với --chi-thi)")
    a = ap.parse_args(argv)
    if a.chi_thi and not a.lists:
        ap.error("--chi-thi cần --lists (tệp CSV nguyện vọng xuất từ List)")
    if a.lists and not a.chi_thi:
        ap.error("--lists chỉ dùng cùng --chi-thi")
    if len(a.tep_xuat) > 1 and not a.chi_thi:
        ap.error("chế độ mặc định chỉ nhận một tệp .xlsx")
    try:
        if a.chi_thi:
            kq = chuyen_chi_thi(a.tep_xuat, a.lists, a.ra, bm.doc_de_thi(a.de))
        else:
            kq = chuyen(a.tep_xuat[0], a.ra, bm.doc_de_thi(a.de))
    except (bm.LoiDeThi, LoiTepXuat) as e:
        print("KHÔNG GHI TỆP NÀO — %s" % e, file=sys.stderr)
        return 1
    print("Đã chuyển %d học sinh, chấm %d bài thi -> %s"
          % (kq["n_hoc_sinh"], kq["n_bai_thi"], a.ra))
    if kq["canh_bao"]:
        print("\n%d cảnh báo (cũng có trong sheet 'Cảnh báo' của BANG_DIEM.xlsx):"
              % len(kq["canh_bao"]))
        for dong, sid, nd in kq["canh_bao"]:
            print("  dòng %s %s: %s" % (dong, sid, nd))
    for g in kq["ghi_chu"]:
        print("\nℹ %s" % g)
    print("\nKéo %s vào ô nạp ở màn hình Vận hành của phần mềm." % TEN_SO)
    return 0


if __name__ == "__main__":
    sys.exit(main())
