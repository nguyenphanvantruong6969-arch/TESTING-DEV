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

Mỗi CLB một biểu mẫu (T4M-Q4b, tao_mau_forms.py --moi-clb): liệt kê N tệp, mỗi tệp một CLB, không có
câu cổng. CLB nhận diện theo thẻ [clb_x-k]; có phiếu trong tệp của CLB nào thì em đó đã thi CLB ấy
(phiếu để trống mọi câu không tính). Tệp trộn câu của nhiều CLB, hoặc có thẻ lạ, thì dừng. Em không có
dòng trong tệp của một CLB thì chỉ là không có điểm CLB đó. Thêm --bai-thi BaiThi.csv (Email, ClubId,
ResponseId, NopLuc; T4M-Q4c) để đối chiếu list trạng thái của app với các tệp xuất: chỉ báo, không đổi điểm.

Tick chọn thi và điểm quyết tâm (T4M-Q5a/b, chỉ khi List có cột THI1..THIn / WP1..WPn): "thi" trong Sổ nhập đi theo
ô tick (có bài mà không tick thì bỏ điểm và báo), cột "Điểm quyết tâm" lấy từ WPk, hai quỹ 100 điểm mỗi ngày được
soát để BÁO (không sửa). List không có hai nhóm cột này thì chạy y như trước.

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


def doc_lists(duong_csv, de, co_so=None):
    """Đọc tệp xuất List (mô hình RỘNG: mỗi dòng một em × một ngày, cột NV1..NVn).

    Trả ({email chữ thường: {dong, email, name, lop, nguyen_vong}}, cảnh báo). Cột bắt buộc: Email,
    Thu, NV1; tùy chọn: HoTen (hoặc Name), Lop (lớp chủ nhiệm, T4M-Q1b), NV2.. Dòng trùng (em, ngày):
    giữ dòng ĐẦU. `co_so` (T4M-Q1b): chỉ giữ dòng có cột CoSo bằng giá trị này (bỏ khoảng trắng, không
    phân biệt hoa thường); None = không lọc. `lop` là ô Lop không trống đầu tiên của em (chưa chuẩn hoá: so_nhap chuẩn hoá khi đọc).

    Tick chọn thi và điểm quyết tâm (T4M-Q5a/b), TÙY CHỌN: cột THI1..THIn (`Có` hoặc trống; chỉ hợp lệ khi CLB ở
    NVk có đề thi, tối đa TRAN_THI_MOI_BUOI tick mỗi ngày, quá thì giữ các tick đầu theo thứ tự NV) và WP1..WPn
    (số nguyên >= 0, trống = chưa đặt); chỉ số k đi cùng NVk. Có cột THIk thì mỗi em có khoá "tick" (tập club_id đã
    tick); có cột WPk thì có "wp" ({buổi: {club_id: số nguyên hoặc None}}) và "dong_buoi" ({buổi: số dòng}).
    List KHÔNG có hai nhóm cột này thì kết quả y như trước (không thêm khoá nào).
    """
    with open(duong_csv, encoding="utf-8-sig", newline="") as f:
        bang = list(csv.reader(f))
    if not bang:
        raise LoiTepXuat("tệp List trống")
    tieu = [h.strip().lower() for h in bang[0]]
    i_email = tieu.index("email") if "email" in tieu else None
    i_thu = tieu.index("thu") if "thu" in tieu else None
    i_ten = next((tieu.index(k) for k in ("hoten", "name") if k in tieu), None)
    i_lop = next((tieu.index(k) for k in ("lop", "lớp") if k in tieu), None)
    i_co_so = tieu.index("coso") if "coso" in tieu else None
    cot_nv = sorted((int(m.group(1)), i) for i, h in enumerate(tieu)
                    for m in [re.fullmatch(r"nv(\d+)", h)] if m)
    cot_thi = {int(m.group(1)): i for i, h in enumerate(tieu) for m in [re.fullmatch(r"thi(\d+)", h)] if m}
    cot_wp = {int(m.group(1)): i for i, h in enumerate(tieu) for m in [re.fullmatch(r"wp(\d+)", h)] if m}
    cot_nv_theo_k = dict(cot_nv)
    cac_k = sorted(set(cot_nv_theo_k) | set(cot_thi) | set(cot_wp))
    thieu = [k for k, v in (("Email", i_email), ("Thu", i_thu), ("NV1", cot_nv[0][0] if cot_nv else None))
             if v is None]
    if thieu:
        raise LoiTepXuat("tệp List thiếu cột bắt buộc: %s" % ", ".join(thieu))

    if co_so is not None and i_co_so is None:
        raise LoiTepXuat("tệp List thiếu cột CoSo nên không lọc được theo --co-so")
    co_so_can = (co_so or "").strip().lower()
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
        if co_so is not None and dong[i_co_so].strip().lower() != co_so_can:
            continue

        def bao(noi_dung, so_dong=so_dong, email=email):
            canh_bao.append((so_dong, email, noi_dung))

        buoi = _ma_buoi_tu_thu(de, dong[i_thu])
        if buoi is None:
            bao("ngày %r không khớp buổi nào trong de_thi.json — bỏ dòng" % dong[i_thu])
            continue
        hs = ds.setdefault(email, {"dong": so_dong, "email": email, "name": "", "lop": "",
                                   "nguyen_vong": {}, "_buoi": set()})
        if cot_thi:
            hs.setdefault("tick", set())
        if cot_wp:
            hs.setdefault("wp", {})
            hs.setdefault("dong_buoi", {})
        if i_ten is not None and not hs["name"]:
            hs["name"] = dong[i_ten].strip()
        if i_lop is not None and not hs["lop"]:
            hs["lop"] = dong[i_lop].strip()
        if buoi in hs["_buoi"]:
            bao("%s: dòng trùng (em, ngày) — bỏ dòng này, giữ dòng đầu" % buoi)
            continue
        hs["_buoi"].add(buoi)
        xep, o_tick, o_wp = [], {}, {}
        for k in cac_k:
            i = cot_nv_theo_k.get(k)
            muc = dong[i].strip() if i is not None else ""
            tho_thi = dong[cot_thi[k]].strip() if k in cot_thi else ""
            tho_wp = dong[cot_wp[k]].strip() if k in cot_wp else ""
            if not muc:
                if tho_thi and _doc_tick(tho_thi) is not False:
                    bao("%s: THI%d có giá trị mà NV%d trống — bỏ ô tick" % (buoi, k, k))
                if tho_wp:
                    bao("%s: WP%d có giá trị mà NV%d trống — bỏ ô điểm quyết tâm" % (buoi, k, k))
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
                if k in cot_thi:
                    tick = _doc_tick(tho_thi)
                    if tick is None:
                        bao("%s: THI%d=%r không hiểu (chỉ nhận \"Có\" hoặc trống) — coi như không tick"
                            % (buoi, k, tho_thi))
                    o_tick[clb["club_id"]] = bool(tick)
                if k in cot_wp:
                    gia_tri = _doc_diem_quyet_tam(tho_wp)
                    if gia_tri is False:
                        bao("%s: WP%d=%r không phải số nguyên từ 0 trở lên — để trống ô này"
                            % (buoi, k, tho_wp))
                        gia_tri = None
                    o_wp[clb["club_id"]] = gia_tri
        if len(xep) > bm.TRAN_CLB_MOI_BUOI:
            bao("%s: %d nguyện vọng, chỉ giữ %d đầu" % (buoi, len(xep), bm.TRAN_CLB_MOI_BUOI))
            xep = xep[:bm.TRAN_CLB_MOI_BUOI]
        if cot_thi:
            da_tick = [c for c in xep if o_tick.get(c)]
            co_de = [c for c in da_tick if theo_ma[c]["de_thi"]]
            for c in da_tick:
                if c not in co_de:
                    bao("%s: tick thi %s nhưng CLB này không có đề thi — bỏ tick" % (buoi, c))
            if len(co_de) > bm.TRAN_THI_MOI_BUOI:
                bo = co_de[bm.TRAN_THI_MOI_BUOI:]
                bao("%s: tick thi %d CLB, tối đa %d mỗi ngày — chỉ giữ %d CLB đầu theo thứ tự nguyện vọng; "
                    "bỏ tick: %s" % (buoi, len(co_de), bm.TRAN_THI_MOI_BUOI, bm.TRAN_THI_MOI_BUOI, ", ".join(bo)))
                co_de = co_de[:bm.TRAN_THI_MOI_BUOI]
            hs["tick"].update(co_de)
        if cot_wp and xep:
            hs["wp"][buoi] = {c: o_wp.get(c) for c in xep}
            hs["dong_buoi"][buoi] = so_dong
        if xep:
            hs["nguyen_vong"][buoi] = xep
    for hs in ds.values():
        del hs["_buoi"]
    return ds, canh_bao


def _doc_tick(o):
    """Ô THIk của List: True = tick ("Có"), False = không tick (trống, "Không"), None = giá trị lạ."""
    g = bm._chuan(o)
    if g in ("có", "co", "yes", "true", "1"):
        return True
    if g in ("", "không", "khong", "no", "false", "0"):
        return False
    return None


def _doc_diem_quyet_tam(o):
    """Ô WPk: số nguyên >= 0 -> int; trống -> None; còn lại (12.5, -3, abc) -> False."""
    if not o:
        return None
    m = re.fullmatch(r"([0-9]+)(\.0+)?", o)
    return int(m.group(1)) if m else False


def _cot_chi_thi(de, tieu_de):
    """Cột Email/Name và cột bài thi của MỘT tệp Forms chỉ-thi.

    Trả (i_email, i_ten, cot, cot_diem, các CLB tệp này phủ, mã câu lạ). Một CLB phủ khi tệp có
    câu cổng; có một phần cột của CLB mà thiếu phần khác thì dừng. CLB không có cột nào = tệp này
    là của buổi khác (tách theo buoi), không phải lỗi.

    Tệp KHÔNG có câu cổng nào (T4M-Q4b, biểu mẫu của một CLB): phải chứa đủ câu của đúng MỘT CLB có
    đề; trộn nhiều CLB hoặc có thẻ lạ thì dừng.
    """
    cot, cot_diem = _doc_cot(tieu_de)
    chuan = [h.strip().lower() for h in tieu_de]
    if "email" not in chuan:
        raise LoiTepXuat("tệp xuất không có cột Email — bật \"Record name\" trong Settings của "
                         "biểu mẫu (và chỉ cho người trong tổ chức làm bài)")
    i_email = chuan.index("email")
    i_ten = chuan.index("name") if "name" in chuan else None
    if not any(m.startswith("thi-") for m in cot):
        return (i_email, i_ten, cot, cot_diem) + _cot_mot_clb(de, cot)
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


def _cot_mot_clb(de, cot):
    """Tệp không câu cổng: trả ([CLB duy nhất], []). Dừng nếu rỗng, trộn CLB, thẻ lạ hoặc thiếu câu."""
    co_thi = bm.clb_co_thi(de)
    hop_le = {"%s-%d" % (c["club_id"], i) for c in co_thi for i in range(1, len(c["de_thi"]) + 1)}
    la = sorted(m for m in cot if m not in hop_le)
    if la:
        raise LoiTepXuat("tệp xuất có mã câu không thuộc CLB nào có đề thi trong de_thi.json: %s. "
                         "Mỗi tệp chỉ chứa câu của một CLB, giữ nguyên phần [mã] ở đầu câu."
                         % ", ".join(la))
    phu = [c for c in co_thi if any("%s-%d" % (c["club_id"], i) in cot
                                    for i in range(1, len(c["de_thi"]) + 1))]
    if not phu:
        raise LoiTepXuat("tệp xuất không có câu bài thi nào của mẫu (không thấy mã [thi-...] "
                         "hay [<club_id>-1])")
    if len(phu) > 1:
        raise LoiTepXuat("tệp xuất trộn câu của %d CLB (%s) mà không có câu cổng [thi-...]; mỗi tệp "
                         "chỉ được chứa một CLB" % (len(phu), ", ".join(c["club_id"] for c in phu)))
    clb = phu[0]
    thieu = ["%s-%d" % (clb["club_id"], i) for i in range(1, len(clb["de_thi"]) + 1)
             if "%s-%d" % (clb["club_id"], i) not in cot]
    if thieu:
        raise LoiTepXuat(
            "tệp xuất thiếu %d câu của mẫu (mã: %s). Câu hỏi trên Forms phải "
            "giữ nguyên phần [mã] ở đầu." % (len(thieu), ", ".join(thieu)))
    return phu, []


def _da_thi(dong, cot, clb):
    """Phiếu `dong` có bài thi của `clb` không: có câu cổng thì phải chọn Có; không câu cổng (biểu
    mẫu một CLB) thì có ít nhất một câu được trả lời."""
    ma = clb["club_id"]
    if "thi-" + ma in cot:
        return bm._chuan(_gia_tri(dong, cot["thi-" + ma])).startswith("có")
    return any(_gia_tri(dong, cot["%s-%d" % (ma, i)]) for i in range(1, len(clb["de_thi"]) + 1))


def phan_tich_chi_thi(de, danh_sach, cac_tep, co_so=None):
    """Ghép các tệp Forms chỉ-thi với danh sách đăng ký. Không ghi gì.

    danh_sach: kết quả doc_lists. cac_tep: [(tên tệp, tiêu đề, các dòng)]. Trả (hoc_sinh theo
    thứ tự List, cảnh báo). Học sinh trong List mà không có bài thi vẫn có mặt (chỉ nguyện vọng).
    """
    canh_bao = []
    theo_ma = {c["club_id"]: c for c in de["cau_lac_bo"]}
    hoc_sinh = {e: {"dong": h["dong"], "student_id": e, "name": h["name"], "lop": h.get("lop", ""),
                    "nguyen_vong": h["nguyen_vong"], "bai_thi": []}
                for e, h in danh_sach.items()}
    for e, h in danh_sach.items():                    # tick / điểm quyết tâm (Q5a/b): chỉ khi List có cột
        hoc_sinh[e].update({k: h[k] for k in ("tick", "wp", "dong_buoi") if k in h})
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
                if co_so is None:
                    bao("email %s không có trong danh sách đăng ký (List) — bỏ cả phiếu" % email)
                else:
                    bao("email %s ở cơ sở khác hoặc không có trong danh sách (--co-so %s) — bỏ cả phiếu"
                        % (email, co_so))
                continue
            if i_ten is not None and not hs["name"]:
                hs["name"] = dong[i_ten].strip()
            bai_thi = []
            for clb in phu:
                ma = clb["club_id"]
                if not _da_thi(dong, cot, clb):
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
                bai = {"club_id": ma, "diem": diem, "dung": dung, "tra_loi": tra_loi, "nap": da_xep}
                if da_xep and "tick" in hs and ma not in hs["tick"]:
                    bao("%s: em có bài thi nhưng KHÔNG tick thi CLB này — điểm có trong BANG_DIEM.xlsx "
                        "nhưng không nạp vào phần mềm" % ma)
                    bai["nap"], bai["khong_tick"] = False, True
                bai_thi.append(bai)
            hs["bai_thi"] += bai_thi

    for e, hs in hoc_sinh.items():
        _ap_tran_thi(de, theo_ma, hs["nguyen_vong"], hs["bai_thi"],
                     lambda nd, e=e, hs=hs: canh_bao.append((hs["dong"], e, nd)))
        if not hs["nguyen_vong"]:
            canh_bao.append((hs["dong"], e, "không xếp nguyện vọng buổi nào"))
        for buoi, noi_dung in _soat_hai_quy(hs):
            canh_bao.append((hs["dong_buoi"][buoi], e, noi_dung))
    for clb in bm.clb_co_thi(de):
        if clb["club_id"] not in da_phu:
            canh_bao.append(("", "", "%s có đề thi nhưng không tệp Forms nào chứa câu của CLB này "
                             "— không có điểm cho CLB này" % clb["club_id"]))
    return list(hoc_sinh.values()), canh_bao


def tap_thi(hs, buoi):
    """Các CLB của em ở `buoi` mà Sổ nhập sẽ đánh dấu "đã thi" (ô điểm hoặc chữ `thi`): có cột tick thì
    là CLB đã tick; không thì là CLB có bài được nạp. Đây cũng là quỹ 1 của điểm quyết tâm."""
    xep = hs["nguyen_vong"].get(buoi, [])
    if "tick" in hs:
        return [c for c in xep if c in hs["tick"]]
    nap = {t["club_id"] for t in hs["bai_thi"] if t["nap"]}
    return [c for c in xep if c in nap]


def _soat_hai_quy(hs):
    """[(buổi, nội dung)] cho mỗi quỹ điểm quyết tâm không cộng đúng 100 (T4M-Q5b). CHỈ BÁO: không sửa giá trị,
    việc chặn lần chạy là của kiosk. Quỹ 1 = CLB đã thi (`tap_thi`), quỹ 2 = các CLB còn lại. Quỹ rỗng không
    kiểm; quỹ chỉ một CLB mà để trống thì kiosk tự điền 100 trong bộ nhớ nên không báo."""
    ket = []
    for buoi, wp in hs.get("wp", {}).items():
        thi = tap_thi(hs, buoi)
        xep = hs["nguyen_vong"].get(buoi, [])
        for so_quy, tap in ((1, thi), (2, [c for c in xep if c not in thi])):
            if not tap or (len(tap) == 1 and wp.get(tap[0]) is None):
                continue
            tong = sum(wp.get(c) or 0 for c in tap)
            if tong != 100:
                ket.append((buoi, "%s: quỹ %d (%s) cộng %d điểm, phải đúng 100 — Sổ nhập giữ nguyên giá trị, "
                                  "kiosk sẽ chặn lần chạy tới khi sửa" % (buoi, so_quy, ", ".join(tap), tong)))
    return ket


# ------------------------------------------------- đối chiếu list BaiThi (T4M-Q4c)

COT_BAI_THI = ("Email", "ClubId")
CHI_CO_O_BAI_THI = "chi_co_o_bai_thi"
CHI_CO_O_TEP_XUAT = "chi_co_o_tep_xuat"


def doc_bai_thi(duong_csv):
    """Đọc list trạng thái BaiThi (Email, ClubId, ResponseId, NopLuc) -> tập {(email chữ thường, ClubId)}.

    Chỉ Email và ClubId bắt buộc. Dòng trùng (em, CLB) tính một; dòng thiếu Email hoặc ClubId bị bỏ."""
    with open(duong_csv, encoding="utf-8-sig", newline="") as f:
        bang = list(csv.reader(f))
    if not bang:
        raise LoiTepXuat("tệp BaiThi trống")
    tieu = [h.strip().lower() for h in bang[0]]
    thieu = [c for c in COT_BAI_THI if c.lower() not in tieu]
    if thieu:
        raise LoiTepXuat("tệp BaiThi thiếu cột bắt buộc: %s" % ", ".join(thieu))
    i_e, i_c = tieu.index("email"), tieu.index("clubid")
    co = set()
    for dong in bang[1:]:
        dong = dong + [""] * (len(tieu) - len(dong))
        email, ma = dong[i_e].strip().lower(), dong[i_c].strip()
        if email and ma:
            co.add((email, ma))
    return co


def bai_trong_tep_xuat(de, cac_tep):
    """{(email chữ thường, club_id)} của mọi bài đã thi có trong các tệp xuất (cả email không có trong
    List; phiếu trùng tính một). cac_tep: [(tên tệp, tiêu đề, các dòng)] — đã qua phan_tich_chi_thi."""
    co = set()
    for _ten, tieu_de, cac_dong in cac_tep:
        i_email, _i_ten, cot, _cd, phu, _la = _cot_chi_thi(de, tieu_de)
        for dong in cac_dong:
            if not any(dong):
                continue
            dong = dong + [""] * (len(tieu_de) - len(dong))
            email = dong[i_email].strip().lower()
            if not email or email == "anonymous":
                continue
            for clb in phu:
                if _da_thi(dong, cot, clb):
                    co.add((email, clb["club_id"]))
    return co


def doi_chieu_bai_thi(bai_thi, bai_xuat):
    """Hai tập {(email, club_id)} -> [(loại, email, club_id, chi tiết)] theo thứ tự (loại, email, club).
    Chỉ báo; không đụng tới điểm. Khớp hết thì rỗng."""
    ra = []
    for e, c in sorted(bai_thi - bai_xuat):
        ra.append((CHI_CO_O_BAI_THI, e, c, "list BaiThi có bài này nhưng không có phiếu tương ứng trong "
                                           "các tệp xuất — xuất thiếu, hoặc em chưa nộp?"))
    for e, c in sorted(bai_xuat - bai_thi):
        ra.append((CHI_CO_O_TEP_XUAT, e, c, "tệp xuất có bài này nhưng list BaiThi không có dòng — flow "
                                            "chưa chạy, hoặc bài nộp ngoài app"))
    return ra


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
    co_wp = any("wp" in h for h in hoc_sinh)      # List có cột WPk (T4M-Q5b): sổ có cột "Điểm quyết tâm"
    for h in hoc_sinh:
        diem = {t["club_id"]: bm.ghi_so(t["diem"]) for t in h["bai_thi"] if t["nap"]}
        thu_tu = [ma for b in de["buoi"] for ma in h["nguyen_vong"].get(b["ma"], [])]
        tick = h.get("tick")                  # có cột THIk: "thi" đi theo ô tick (ô "thi" khi chưa có điểm)
        wp = {ma: v for d in h.get("wp", {}).values() for ma, v in d.items()}
        # Không có nhóm: sổ ghi KHÔNG có cột Nhóm ưu tiên (co_nhom=False bên dưới).
        students.append({
            "student_id": h["student_id"], "name": h["name"], "reserve_group": "",
            "class_id": h.get("lop") or "",
            "nv": [dict({"club_id": ma, "thi": ma in diem or (tick is not None and ma in tick),
                         "diem": diem.get(ma, "")},
                        **({"diem_w": "" if wp.get(ma) is None else wp[ma]} if co_wp else {}))
                   for ma in thu_tu],
        })
    duong = os.path.join(thu_muc, TEN_SO)
    # co_nhom=False: Forms không hỏi nhóm ưu tiên. Không có cột thì phần mềm
    # GIỮ nhóm đã gán; có cột mà trống thì phần mềm sẽ BỎ nhóm của em.
    # Cột Lớp (T4M-Q1b) CHỈ khi List có lớp cho ít nhất một em; không thì sổ y như trước.
    so_nhap.ghi_so_nhap(duong, clubs, students, co_nhom=False,
                        co_lop=any(s["class_id"] for s in students), luon_co_cot_w=co_wp)
    return duong


def ghi_bang_diem(de, hoc_sinh, canh_bao, duong, doi_chieu=None):
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
                      + [t["diem"], "Có" if t["nap"] else (
                          "Không — chưa tick thi" if t.get("khong_tick") else "Không — chưa xếp nguyện vọng")])

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

    if doi_chieu is not None:                     # chỉ khi có --bai-thi; không thì sổ y như trước
        ws = wb.create_sheet("Đối chiếu BaiThi")
        dau_bang(ws, ["Loại", "Email", "CLB", "Chi tiết"], [20, 34, 16, 90])
        for x in doi_chieu:
            ws.append(list(x))
        if not doi_chieu:
            ws.append(["", "", "", "Khớp hết: list BaiThi và các tệp xuất có cùng tập bài thi."])
    wb.save(duong)


# A13.13: workspace trường học BẬT điểm quyết tâm mặc định, mà biểu mẫu KHÔNG thu điểm đó (và
# không được bịa): sổ ra không có điểm quyết tâm, nên phải tắt tính năng trước khi nạp.
GHI_CHU_CO_DIEM_QUYET_TAM = ("Sổ có cột điểm quyết tâm (thu trên app): giữ BẬT \"Dùng điểm quyết tâm\" khi nạp. "
                            "Mỗi ngày, mỗi quỹ không rỗng phải cộng đúng 100 thì kiosk mới cho chạy.")
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


def chuyen_chi_thi(cac_duong_xlsx, duong_lists, thu_muc_ra, de=None, co_so=None, bai_thi=None):
    """Chế độ chỉ thi: các tệp Forms (chỉ có bài thi) + tệp xuất List -> Sổ nhập + bảng điểm.

    bai_thi (T4M-Q4c): đường dẫn BaiThi.csv; có thì thêm kq["doi_chieu_bai_thi"] và sheet đối chiếu.
    """
    de = de or bm.doc_de_thi()
    co_bai_thi = doc_bai_thi(bai_thi) if bai_thi else None       # lỗi tệp thì dừng trước khi ghi gì
    danh_sach, canh_bao = doc_lists(duong_lists, de, co_so)
    if not danh_sach:
        raise LoiTepXuat("tệp List không có học sinh nào" if co_so is None else
                         "tệp List không có học sinh nào ở cơ sở %r" % co_so)
    cac_tep = []
    for d in cac_duong_xlsx:
        tieu_de, cac_dong = doc_tep_xuat(d)
        cac_tep.append((os.path.basename(d), tieu_de, cac_dong))
    hoc_sinh, canh_bao_thi = phan_tich_chi_thi(de, danh_sach, cac_tep, co_so)
    canh_bao += canh_bao_thi
    doi_chieu = (doi_chieu_bai_thi(co_bai_thi, bai_trong_tep_xuat(de, cac_tep))
                 if co_bai_thi is not None else None)
    os.makedirs(thu_muc_ra, exist_ok=True)
    ghi_tep_phan_mem(de, hoc_sinh, thu_muc_ra)
    ghi_bang_diem(de, hoc_sinh, canh_bao, os.path.join(thu_muc_ra, "BANG_DIEM.xlsx"), doi_chieu)
    kq = {"n_hoc_sinh": len(hoc_sinh),
          "n_bai_thi": sum(len(h["bai_thi"]) for h in hoc_sinh),
          "canh_bao": canh_bao,
          "ghi_chu": [GHI_CHU_CO_DIEM_QUYET_TAM if any("wp" in h for h in hoc_sinh)
                      else GHI_CHU_DIEM_QUYET_TAM]}
    if doi_chieu is not None:
        kq["doi_chieu_bai_thi"] = doi_chieu
    return kq


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
    ap.add_argument("--co-so", help="chỉ lấy học sinh có cột CoSo của List bằng giá trị này, ví dụ CS1 "
                                    "(chỉ với --chi-thi); bỏ trống = không lọc")
    ap.add_argument("--bai-thi", help="CSV xuất từ list BaiThi (Email, ClubId, ResponseId, NopLuc): đối chiếu "
                                      "với các tệp xuất, chỉ báo, không đổi điểm (chỉ với --chi-thi)")
    a = ap.parse_args(argv)
    if a.bai_thi is not None and not a.chi_thi:
        ap.error("--bai-thi chỉ dùng cùng --chi-thi")
    if a.chi_thi and not a.lists:
        ap.error("--chi-thi cần --lists (tệp CSV nguyện vọng xuất từ List)")
    if a.lists and not a.chi_thi:
        ap.error("--lists chỉ dùng cùng --chi-thi")
    if a.co_so is not None and not a.chi_thi:
        ap.error("--co-so chỉ dùng cùng --chi-thi")
    if len(a.tep_xuat) > 1 and not a.chi_thi:
        ap.error("chế độ mặc định chỉ nhận một tệp .xlsx")
    try:
        if a.chi_thi:
            kq = chuyen_chi_thi(a.tep_xuat, a.lists, a.ra, bm.doc_de_thi(a.de), a.co_so, a.bai_thi)
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
    if "doi_chieu_bai_thi" in kq:
        dc = kq["doi_chieu_bai_thi"]
        print("\nĐối chiếu BaiThi: %s" % ("khớp hết." if not dc else "%d chỗ lệch:" % len(dc)))
        for loai, email, ma, nd in dc:
            print("  %s %s %s: %s" % (loai, email, ma, nd))
    for g in kq["ghi_chu"]:
        print("\nℹ %s" % g)
    print("\nKéo %s vào ô nạp ở màn hình Vận hành của phần mềm." % TEN_SO)
    return 0


if __name__ == "__main__":
    sys.exit(main())
