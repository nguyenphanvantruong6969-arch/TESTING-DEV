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
import copy
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


class LoiChoXacNhan(LoiTepXuat):
    """FA-M4 (D11): có chênh lệch giữa các đề; đã ghi báo cáo, chưa ghi Sổ nhập tới khi admin chọn một cờ."""


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


_COT_HE_THONG = {"id", "start time", "completion time", "last modified time", "email", "name", "total points",
                 "quiz feedback", "thời gian bắt đầu", "thời gian hoàn thành"}


def _doc_cot(tieu_de, ban_do=None):
    """{mã câu: [chỉ số cột]} và {mã câu: chỉ số cột Points}.

    SG-12: tiêu đề có thẻ "[mã]" (tệp cũ) đọc theo thẻ; không có thẻ thì khớp CHÍNH XÁC chữ thuần qua `ban_do`
    (`bm.ban_do_chung(de)` hoặc tệp MAP_*.json)."""
    cot, cot_diem = {}, {}
    for i, h in enumerate(tieu_de):
        if h.startswith(TIEN_TO_NHAN_XET):
            continue
        if h.startswith(TIEN_TO_DIEM):
            ma = bm.ma_cua_cau(h[len(TIEN_TO_DIEM):], ban_do)
            if ma:
                cot_diem[ma] = i
            continue
        ma = bm.ma_cua_cau(h, ban_do)
        if ma:
            # Nhiều cột cùng mã (Ranking tách mỗi vị trí một cột) thì nối lại
            # theo thứ tự cột.
            cot.setdefault(ma, []).append(i)
    return cot, cot_diem


def cot_la(tieu_de, ban_do):
    """SG-12: các cột KHÔNG phải cột hệ thống của Forms mà cũng không nhận ra là câu nào của mẫu (không thẻ "[mã]",
    không có trong bản đồ) — để BÁO, không lặng lẽ bỏ."""
    ra = []
    for h in tieu_de:
        h = str(h or "").strip()
        if not h or h.startswith((TIEN_TO_NHAN_XET, TIEN_TO_DIEM)) or h.lower() in _COT_HE_THONG:
            continue
        if bm.ma_cua_cau(h, ban_do) is None:
            ra.append(h if len(h) <= 60 else h[:57] + "...")
    return ra


def _ban_do_cot(de, tieu_de):
    """{mã câu: [chỉ số cột]} và {mã câu: chỉ số cột Points}."""
    ban_do = bm.ban_do_chung(de)
    cot, cot_diem = _doc_cot(tieu_de, ban_do)
    can = ["student_id", "name"] + [b["ma"] for b in de["buoi"]]
    for clb in bm.clb_co_thi(de):
        can.append("thi-" + clb["club_id"])
        can += ["%s-%d" % (clb["club_id"], i) for i in range(1, len(clb["de_thi"]) + 1)]
    thieu = [m for m in can if m not in cot]
    if thieu:
        raise LoiTepXuat(
            "tệp xuất thiếu %d câu của mẫu (mã: %s). Câu hỏi trên Forms phải giữ nguyên chữ tiêu đề "
            "(tệp cũ: giữ phần [mã] ở đầu)." % (len(thieu), ", ".join(thieu)))
    la = sorted(set(cot) - set(can)) + cot_la(tieu_de, ban_do)
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
    ban_do = bm.ban_do_chung(de)
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
                clb = theo_ma.get(bm.ma_trong_lua_chon(muc, ban_do, b["ma"])) or theo_ten.get(bm._chuan(muc))
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


def doc_lists(duong_csv, de, co_so=None, fa=False, nhan_ban_nhap=False):
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

    `fa=True` (FA-M3, TH): chế độ FA-DAA đường A. Lần lưu CUỐI của (em, ngày) được tính (V§5.1; không phải dòng đầu);
    dòng có TrangThai = DRAFT bị bỏ và báo, trừ khi `nhan_ban_nhap`; có thêm khoá "hc" ({buổi: bool}) = ô HC_TuChinh
    của dòng được giữ. `fa=False` giữ nguyên hành vi cũ.
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
    hc_fa = {}
    if fa:
        bang, hc_fa, canh_bao = _loc_dong_fa(de, bang, tieu, i_email, i_thu, nhan_ban_nhap)
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
        if fa:
            hs.setdefault("hc", {})
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
        if fa:
            hs["hc"][buoi] = hc_fa.get((email, buoi), False)
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


HUY_CHUONG_DIEM = (60, 30, 10)  # vàng, bạc, đồng (FA-DAA V§6)


def dat_huy_chuong_duong_b(nguyen_vong, tu_do, vang="", doi_bac_dong="", so_clb_nhan=None):
    """Huy chương MỘT em MỘT ngày trên đường B (chỉ Forms; FA-M3, quyết định D2/D12 của Truong 08/11/2026).

    Mặc định: vàng/bạc/đồng cho ba CLB KHÔNG Tự do đầu tiên theo thứ tự nguyện vọng (ngoại lệ bất biến 2 trong
    CLAUDE.md — chỉ hợp lệ vì hai câu tuỳ chọn dưới đây cho em đổi được MỌI cách đặt):
      * `vang`: CLB em muốn đặt vàng (trống = giữ mặc định); bạc, đồng đi theo thứ tự nguyện vọng ở các CLB còn lại.
      * `doi_bac_dong`: "Có" thì đổi chỗ bạc và đồng; trống = giữ.
    Giá trị không dùng được (vàng vào CLB Tự do / ngoài danh sách, ô đổi lạ, đổi khi chỉ còn một CLB) thì giữ mặc
    định và báo. Trả `({club_id: 60|30|10}, [cảnh báo])`. Nguyện vọng trùng chỉ tính một lần.
    `so_clb_nhan` (SG-5): số CLB của ngày nhận được huy chương; < 3 thì câu đổi bạc/đồng vô nghĩa (biểu mẫu mới không
    có câu đó, tệp cũ vẫn có) nên ô đổi bị bỏ qua, KHÔNG báo. None = không biết, giữ cách cũ.
    """
    canh_bao = []
    if so_clb_nhan is not None and so_clb_nhan < bm.SO_CLB_TOI_THIEU_CAU_DOI:
        doi_bac_dong = ""
    ds = [c for c in dict.fromkeys(_o(c) for c in nguyen_vong) if c and c not in tu_do]
    if not ds:
        return {}, canh_bao
    vang = _o(vang)
    vang_dat = ds[0]
    if vang:
        if vang in ds:
            vang_dat = vang
        else:
            canh_bao.append("Huy chương vàng: %s không phải CLB Giới hạn/Tuyển chọn trong nguyện vọng của em "
                            "— giữ mặc định" % vang)
    con_lai = [c for c in ds if c != vang_dat][:2]
    doi = bm._chuan(_o(doi_bac_dong))
    if doi in ("có", "co"):
        if len(con_lai) == 2:
            con_lai.reverse()
        else:
            canh_bao.append("Đổi chỗ bạc và đồng: chỉ còn %d CLB nhận huy chương — giữ mặc định" % len(con_lai))
    elif doi:
        canh_bao.append("Đổi chỗ bạc và đồng: %r không hiểu (chỉ nhận \"Có\" hoặc trống) — giữ mặc định"
                        % doi_bac_dong)
    return dict(zip([vang_dat] + con_lai, HUY_CHUONG_DIEM)), canh_bao


def _cot_chi_thi(de, tieu_de, ban_do=None):
    """Cột Email/Name và cột bài thi của MỘT tệp Forms chỉ-thi.

    Trả (i_email, i_ten, cot, cot_diem, các CLB tệp này phủ, mã câu lạ). Một CLB phủ khi tệp có
    câu cổng; có một phần cột của CLB mà thiếu phần khác thì dừng. CLB không có cột nào = tệp này
    là của buổi khác (tách theo buoi), không phải lỗi.

    Tệp KHÔNG có câu cổng nào (T4M-Q4b, biểu mẫu của một CLB): phải chứa đủ câu của đúng MỘT CLB có
    đề; trộn nhiều CLB hoặc có thẻ lạ thì dừng.

    SG-12: `ban_do` (từ `bm.ban_do_chung` của đề GỐC) để nhận tiêu đề thuần; không truyền thì dựng từ `de`.
    """
    ban_do = bm.ban_do_chung(de) if ban_do is None else ban_do
    cot, cot_diem = _doc_cot(tieu_de, ban_do)
    chuan = [h.strip().lower() for h in tieu_de]
    if "email" not in chuan:
        raise LoiTepXuat("tệp xuất không có cột Email — bật \"Record name\" trong Settings của "
                         "biểu mẫu (và chỉ cho người trong tổ chức làm bài)")
    i_email = chuan.index("email")
    i_ten = chuan.index("name") if "name" in chuan else None
    if not any(m.startswith("thi-") for m in cot):
        return (i_email, i_ten, cot, cot_diem) + _cot_mot_clb(de, cot, cot_la(tieu_de, ban_do))
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
            "tệp xuất thiếu %d câu của mẫu (mã: %s). Câu hỏi trên Forms phải giữ nguyên chữ tiêu đề "
            "(tệp cũ: giữ phần [mã] ở đầu)." % (len(thieu), ", ".join(thieu)))
    if not phu:
        raise LoiTepXuat("tệp xuất không có câu bài thi nào của mẫu (không thấy mã [thi-...])")
    return i_email, i_ten, cot, cot_diem, phu, sorted(set(cot) - can_het) + cot_la(tieu_de, ban_do)


def _cot_mot_clb(de, cot, cot_khong_nhan=()):
    """Tệp không câu cổng: trả ([CLB duy nhất], []). Dừng nếu rỗng, trộn CLB, thẻ lạ hoặc thiếu câu.
    `cot_khong_nhan`: tiêu đề cột không nhận ra là câu nào (SG-12) — cũng là "thẻ lạ", dừng."""
    co_thi = bm.clb_co_thi(de)
    hop_le = {"%s-%d" % (c["club_id"], i) for c in co_thi for i in range(1, len(c["de_thi"]) + 1)}
    la = sorted(m for m in cot if m not in hop_le) + list(cot_khong_nhan)
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
            "tệp xuất thiếu %d câu của mẫu (mã: %s). Câu hỏi trên Forms phải giữ nguyên chữ tiêu đề "
            "(tệp cũ: giữ phần [mã] ở đầu)." % (len(thieu), ", ".join(thieu)))
    return phu, []


def _da_thi(dong, cot, clb):
    """Phiếu `dong` có bài thi của `clb` không: có câu cổng thì phải chọn Có; không câu cổng (biểu
    mẫu một CLB) thì có ít nhất một câu được trả lời."""
    ma = clb["club_id"]
    if "thi-" + ma in cot:
        return bm._chuan(_gia_tri(dong, cot["thi-" + ma])).startswith("có")
    return any(_gia_tri(dong, cot["%s-%d" % (ma, i)]) for i in range(1, len(clb["de_thi"]) + 1))


def phan_tich_chi_thi(de, danh_sach, cac_tep, co_so=None, fa=False, theo_tep=None):
    """Ghép các tệp Forms chỉ-thi với danh sách đăng ký. Không ghi gì.

    danh_sach: kết quả doc_lists. cac_tep: [(tên tệp, tiêu đề, các dòng)]. Trả (hoc_sinh theo
    thứ tự List, cảnh báo). Học sinh trong List mà không có bài thi vẫn có mặt (chỉ nguyện vọng).
    `fa=True` (FA-M3): không soát hai quỹ 100 điểm của điểm quyết tâm (huy chương FA là MỘT quỹ 60/30/10).
    `theo_tep` (FA-M4) {tên tệp: (chữ đề, de_thi của đề đó)}: tệp ghi trong đó được chấm bằng đề ấy và mỗi bài có
    khoá "bien_the"; tệp không ghi là đề A. None = hành vi cũ (không khoá "bien_the").
    """
    canh_bao = []
    theo_ma = {c["club_id"]: c for c in de["cau_lac_bo"]}
    hoc_sinh = {e: {"dong": h["dong"], "student_id": e, "name": h["name"], "lop": h.get("lop", ""),
                    "nguyen_vong": h["nguyen_vong"], "bai_thi": []}
                for e, h in danh_sach.items()}
    for e, h in danh_sach.items():                    # tick / điểm quyết tâm (Q5a/b): chỉ khi List có cột
        hoc_sinh[e].update({k: h[k] for k in ("tick", "wp", "dong_buoi") if k in h})
    da_phu = set()
    de_goc = de
    ban_do_goc = bm.ban_do_chung(de_goc)         # SG-12: tiêu đề thuần của MỌI đề (A, B, C) tính từ đề gốc
    for ten_tep, tieu_de, cac_dong in cac_tep:
        chu_de, de = (theo_tep or {}).get(ten_tep, ("A", de_goc))
        i_email, i_ten, cot, cot_diem, phu, la = _cot_chi_thi(de, tieu_de, ban_do_goc)
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
                if not fa and any(t["club_id"] == ma for t in hs["bai_thi"]):
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
                if fa:
                    bai["tep"] = ten_tep
                if theo_tep is not None:
                    bai["bien_the"] = chu_de
                if da_xep and "tick" in hs and ma not in hs["tick"]:
                    bao("%s: em có bài thi nhưng KHÔNG tick thi CLB này — điểm có trong BANG_DIEM.xlsx "
                        "nhưng không nạp vào phần mềm" % ma)
                    bai["nap"], bai["khong_tick"] = False, True
                bai_thi.append(bai)
            hs["bai_thi"] += bai_thi

    de = de_goc
    if fa:
        for e, hs in hoc_sinh.items():
            _tach_lan_dau(theo_ma, e, hs)
    for e, hs in hoc_sinh.items():
        _ap_tran_thi(de, theo_ma, hs["nguyen_vong"], hs["bai_thi"],
                     lambda nd, e=e, hs=hs: canh_bao.append((hs["dong"], e, nd)))
        if not hs["nguyen_vong"]:
            canh_bao.append((hs["dong"], e, "không xếp nguyện vọng buổi nào"))
        for buoi, noi_dung in ([] if fa else _soat_hai_quy(hs)):
            canh_bao.append((hs["dong_buoi"][buoi], e, noi_dung))
    for clb in bm.clb_co_thi(de):
        if clb["club_id"] not in da_phu:
            canh_bao.append(("", "", "%s có đề thi nhưng không tệp Forms nào chứa câu của CLB này "
                             "— không có điểm cho CLB này" % clb["club_id"]))
    return list(hoc_sinh.values()), canh_bao


def _doc_bo_cau(x):
    """CLI `--bo-cau`: "CLB-DE-SO" (ví dụ C3-B-4) -> (CLB, đề, số); "CLB-SO" -> (CLB, số)."""
    import phan_tich_cau_hoi as pt
    phan = x.rsplit("-", 2)
    if len(phan) == 3 and phan[1] in pt.CHU_BIEN_THE:
        return phan[0], phan[1], int(phan[2])
    ma, so = x.rsplit("-", 1)
    return ma, int(so)


def _chuan_bo_cau(bo_cau, theo_ma):
    """FA-S2: {(CLB, đề, số)}. Dạng cũ (CLB, số) chỉ nhận khi CLB có MỘT đề (-> đề A), nếu không là lỗi nêu các đề."""
    import phan_tich_cau_hoi as pt
    ra = set()
    for x in bo_cau or ():
        if len(x) == 3:
            ra.add(tuple(x))
            continue
        ma, so = x
        n = _so_de(theo_ma[ma]) if ma in theo_ma else 1
        if n > 1:
            raise LoiTepXuat("--bo-cau %s-%d: CLB %s có %d đề (%s) — ghi rõ đề, ví dụ %s-%s-%d"
                             % (ma, so, ma, n, ", ".join(pt.CHU_BIEN_THE[:n]), ma, pt.CHU_BIEN_THE[0], so))
        ra.add((ma, "A", so))
    return ra


def _so_de(clb):
    import phan_tich_cau_hoi as pt
    return len(pt.cac_bien_the(clb)) if clb.get("de_thi") else 1


def _de_giao(email, clb, thi_lai=False):
    """Chữ đề giao cho em (FA-M4): `chon_bien_the`, hoặc `chon_bien_the_thi_lai` khi thi lại."""
    import phan_tich_cau_hoi as pt
    n = _so_de(clb)
    return pt.CHU_BIEN_THE[(pt.chon_bien_the_thi_lai if thi_lai else pt.chon_bien_the)(email, n)]


def _tach_lan_dau(theo_ma, email, hs):
    """FA-S1: mỗi CLB giữ MỘT "bài lần đầu" trong hs["bai_thi"], các bài khác sang hs["bai_khac"].

    Bài lần đầu = bài làm đúng đề giao (`chon_bien_the`), không phụ thuộc thứ tự tệp trên dòng lệnh; không có bài
    nào đúng đề giao thì lấy theo (khác đề thi lại, chữ đề, tên tệp)."""
    nhom = {}
    for bai in hs["bai_thi"]:
        nhom.setdefault(bai["club_id"], []).append(bai)
    giu, khac = [], []
    for ma, ds in nhom.items():
        clb = theo_ma[ma]
        giao, lai = _de_giao(email, clb), _de_giao(email, clb, thi_lai=True)
        ds = sorted(ds, key=lambda b: (b.get("bien_the", "A") != giao, b.get("bien_the", "A") != lai,
                                       b.get("bien_the", "A"), b["tep"]))
        giu.append(ds[0])
        khac += ds[1:]
    hs["bai_thi"] = [b for b in hs["bai_thi"] if any(b is g for g in giu)]
    hs["bai_khac"] = khac


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


def ghi_tep_phan_mem(de, hoc_sinh, thu_muc, clb_fa=None, giu_cho=None):
    """Ghi Sổ nhập CLB. Trả đường dẫn.

    Nguyện vọng các buổi nối thành một danh sách theo thứ tự buổi trong
    de_thi.json; điểm (chỉ bài được nạp) đặt ngay cạnh CLB đó. FA-M3: `clb_fa` {club_id: {loai, capacity, ...}}
    ghi đè chỉ tiêu và thêm cột FA cho sheet CLB; `giu_cho` [(club_id, student_id)] thêm sheet "Giữ chỗ"; bài có khoá
    "diem_so_nhap" (điểm nguyên thang 10, D7) thì ghi giá trị đó thay vì "diem".
    """
    clubs = [{"club_id": c["club_id"], "name": c["name"], "capacity": c["capacity"],
              "reserve_capacity": c["reserve_capacity"],
              "reserve_group": c["reserve_group"], "buoi": c["buoi"]}
             for c in de["cau_lac_bo"]]
    for c in clubs:
        c.update((clb_fa or {}).get(c["club_id"], {}))
    students = []
    co_wp = any("wp" in h for h in hoc_sinh)      # List có cột WPk (T4M-Q5b): sổ có cột "Điểm quyết tâm"
    for h in hoc_sinh:
        diem = {t["club_id"]: bm.ghi_so(t.get("diem_so_nhap", t["diem"])) for t in h["bai_thi"] if t["nap"]}
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
                        co_lop=any(s["class_id"] for s in students), luon_co_cot_w=co_wp, giu_cho=giu_cho or None)
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


# ------------------------------------------------- FA-DAA (FA-M3, TH = chưa thử trên Microsoft thật)

def quy_diem_10(diem, toi_da):
    """D7: điểm nguyên 0-10 = làm tròn nửa lên của diem / toi_da x 10 (tính bằng phân số, không sai số số thực)."""
    from fractions import Fraction
    x = Fraction(str(diem)) / Fraction(str(toi_da)) * 10
    return int((x + Fraction(1, 2)) // 1) if x >= 0 else 0


def co_nhanh_qua(thoi_gian):
    """D9: {khoá: số giây} -> tập khoá làm bài trong thời gian < 1/3 TRUNG VỊ của cả nhóm."""
    if not thoi_gian:
        return set()
    v = sorted(thoi_gian.values())
    n = len(v)
    trung_vi = v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2
    return {k for k, t in thoi_gian.items() if t < trung_vi / 3}


def _loc_dong_fa(de, bang, tieu, i_email, i_thu, nhan_ban_nhap):
    """Lọc dòng List cho `doc_lists(fa=True)`: bỏ DRAFT, giữ lần lưu CUỐI của (em, ngày). Dòng bỏ thành dòng trống
    (giữ số dòng gốc để cảnh báo đúng). Trả (bảng mới, {(email, buổi): HC_TuChinh bool}, cảnh báo)."""
    i_tt = tieu.index("trangthai") if "trangthai" in tieu else None
    i_hc = tieu.index("hc_tuchinh") if "hc_tuchinh" in tieu else None
    moi, canh_bao, cuoi = [bang[0]], [], {}
    for so_dong, dong in enumerate(bang[1:], 2):
        dong = list(dong) + [""] * (len(tieu) - len(dong))
        email = dong[i_email].strip().lower()
        buoi = _ma_buoi_tu_thu(de, dong[i_thu])
        if any(x.strip() for x in dong) and i_tt is not None and dong[i_tt].strip().upper() == "DRAFT" \
                and not nhan_ban_nhap:
            canh_bao.append((so_dong, email, "bản nháp (DRAFT) chưa nộp — bỏ dòng (dùng --nhan-ban-nhap để giữ)"))
            dong = [""] * len(tieu)
        elif email and buoi:
            if (email, buoi) in cuoi:
                canh_bao.append((cuoi[(email, buoi)], email, "%s: lần lưu cuối được tính — bỏ dòng này, giữ dòng %d"
                                 % (buoi, so_dong)))
                moi[cuoi[(email, buoi)] - 1] = [""] * len(tieu)
            cuoi[(email, buoi)] = so_dong
        moi.append(dong)
    hc = {}
    for (email, buoi), so_dong in cuoi.items():
        if i_hc is not None:
            hc[(email, buoi)] = _doc_tick(moi[so_dong - 1][i_hc]) is True
    return moi, hc, canh_bao


def ap_huy_chuong_duong_a(danh_sach, tu_do):
    """Đường A (V§6.1, D2): ngày nào mọi ô huy chương trống và HC_TuChinh không đặt thì điền huy chương MẶC ĐỊNH theo
    thứ tự nguyện vọng (`dat_huy_chuong_duong_b` không có ghi đè); còn lại giữ nguyên giá trị em đặt. Sửa `danh_sach`."""
    for hs in danh_sach.values():
        for buoi, xep in hs["nguyen_vong"].items():
            wp = hs.get("wp", {}).get(buoi) or {}
            if any(v is not None for v in wp.values()) or hs.get("hc", {}).get(buoi):
                continue
            huy_chuong, _ = dat_huy_chuong_duong_b(xep, tu_do)
            hs.setdefault("wp", {})[buoi] = {c: huy_chuong.get(c) for c in xep}
            hs.setdefault("dong_buoi", {})[buoi] = hs["dong"]
    return []


def doc_dang_ky_fa_forms(de, tieu_de, cac_dong, tu_do, danh_sach=None):
    """Đường B: tệp Forms đăng ký của FA-M2 (một biểu mẫu mỗi ngày) -> {email: hồ sơ}, cảnh báo.

    Tệp có thể chứa nhiều ngày; gọi nhiều lần với cùng `danh_sach` để gộp các tệp. Khoá là Email (chữ thường; không
    có Email thì mã học sinh). Nguyện vọng trùng bị bỏ và báo; nộp nhiều lần: phiếu CUỐI được tính (V§5.1). Huy chương:
    "Giữ mặc định" / "Không, giữ mặc định" đổi thành ô trống rồi gọi `dat_huy_chuong_duong_b` (đã có test).
    Hồ sơ như của `doc_lists` (nguyen_vong, wp, dong_buoi) cộng "student_id" là mã học sinh em gõ.
    """
    ban_do = bm.ban_do_chung(de)
    cot, _ = _doc_cot(tieu_de, ban_do)
    ma_buoi = {b["ma"] for b in de["buoi"]}
    nv_cot = {}
    for ma, cac in cot.items():
        m = re.fullmatch(r"(.+)-nv(\d+)", ma)
        if m and m.group(1) in ma_buoi:
            nv_cot.setdefault(m.group(1), {})[int(m.group(2))] = cac[0]
    if not nv_cot or "student_id" not in cot:
        raise LoiTepXuat("tệp đăng ký thiếu câu của biểu mẫu FA-DAA (cần câu mã học sinh và câu Nguyện vọng 1..3 của "
                         "từng buổi); giữ nguyên chữ tiêu đề câu hỏi (tệp cũ: phần [mã] ở đầu câu)")
    chuan = [h.strip().lower() for h in tieu_de]
    i_email = chuan.index("email") if "email" in chuan else None
    danh_sach = {} if danh_sach is None else danh_sach
    canh_bao = []
    theo_ma = {c["club_id"]: c for c in de["cau_lac_bo"]}
    theo_ten = {bm._chuan(c["name"]): c for c in de["cau_lac_bo"]}

    def tim_clb(chu):
        return theo_ma.get(bm.ma_trong_lua_chon(chu)) or theo_ma.get(chu) or theo_ten.get(bm._chuan(chu))

    for h in cot_la(tieu_de, ban_do):                          # SG-12: báo, không lặng lẽ bỏ
        canh_bao.append(("", "", "bỏ qua cột %r: không khớp câu nào của biểu mẫu đăng ký" % h))

    for so_dong, dong in enumerate(cac_dong, 2):
        if not any(dong):
            continue
        dong = list(dong) + [""] * (len(tieu_de) - len(dong))
        sid = _gia_tri(dong, cot["student_id"])
        email = dong[i_email].strip().lower() if i_email is not None else ""
        khoa = email if email and email != "anonymous" else sid.lower()
        if not sid:
            canh_bao.append((so_dong, khoa, "phiếu không có mã học sinh — bỏ cả phiếu"))
            continue

        def bao(nd, so_dong=so_dong, khoa=khoa):
            canh_bao.append((so_dong, khoa, nd))

        hs = danh_sach.get(khoa)
        if hs is None:
            hs = danh_sach[khoa] = {"dong": so_dong, "email": khoa, "student_id": sid,
                                    "name": _gia_tri(dong, cot["name"]) if "name" in cot else "",
                                    "lop": "", "nguyen_vong": {}, "wp": {}, "dong_buoi": {}}
        elif hs["student_id"] != sid:
            bao("mã học sinh %r khác %r đã ghi trước cho cùng email — giữ mã đầu" % (sid, hs["student_id"]))
        for buoi, cac_k in sorted(nv_cot.items()):
            xep = []
            for k, i in sorted(cac_k.items()):
                muc = dong[i].strip()
                if not muc:
                    continue
                clb = tim_clb(muc)
                if clb is None:
                    bao("%s: Nguyện vọng %d %r không phải CLB nào trong de_thi.json — bỏ ô này" % (buoi, k, muc))
                elif clb["buoi"] != buoi:
                    bao("%s: %s sinh hoạt %s, không thuộc buổi này — bỏ ô này" % (buoi, clb["club_id"], clb["buoi"]))
                elif clb["club_id"] in xep:
                    bao("%s: Nguyện vọng %d trùng %s — bỏ ô này (CLB chỉ tính một lần)" % (buoi, k, clb["club_id"]))
                else:
                    xep.append(clb["club_id"])
            if not xep:
                continue
            if buoi in hs["nguyen_vong"]:
                bao("%s: nộp lần nữa — phiếu CUỐI cùng được tính, bỏ phiếu dòng %d" % (buoi, hs["dong_buoi"][buoi]))
            tho_vang = _gia_tri(dong, cot[buoi + "-vang"]) if buoi + "-vang" in cot else ""
            tho_doi = _gia_tri(dong, cot[buoi + "-doi"]) if buoi + "-doi" in cot else ""
            clb_vang = None if tho_vang in ("", bm.GIU_MAC_DINH_VANG) else tim_clb(tho_vang)
            vang = clb_vang["club_id"] if clb_vang else ""
            if tho_vang not in ("", bm.GIU_MAC_DINH_VANG) and not vang:
                bao("%s: huy chương vàng %r không phải CLB nào — giữ mặc định" % (buoi, tho_vang))
            huy_chuong, canh_bao_hc = dat_huy_chuong_duong_b(
                xep, tu_do, vang, "" if tho_doi in ("", bm.DOI_KHONG) else tho_doi,
                so_clb_nhan=sum(1 for c in de["cau_lac_bo"] if c["buoi"] == buoi and c["club_id"] not in tu_do))
            for nd in canh_bao_hc:
                bao("%s: %s" % (buoi, nd))
            hs["nguyen_vong"][buoi] = xep
            hs["wp"][buoi] = {c: huy_chuong.get(c) for c in xep}
            hs["dong_buoi"][buoi] = so_dong
    return danh_sach, canh_bao


def doc_clb_fa(duong_so_nhap, de):
    """Sổ nhập CLB của FA-M1 -> ({club_id của de_thi.json: {loai, capacity, diem_san?, so_toi_thieu?,
    suc_chua_phong?}}, giữ chỗ [(club_id, mã HS)], cảnh báo). CLB khớp theo mã, rồi theo tên."""
    import openpyxl
    du = so_nhap.doc_so_nhap(openpyxl.load_workbook(duong_so_nhap, data_only=True))
    if du["loi"]:
        from i18n_errors import format_all
        raise LoiTepXuat("Sổ nhập CLB (%s) có lỗi: %s" % (os.path.basename(duong_so_nhap),
                                                           "; ".join(format_all(du["loi"][:3]))))
    theo_ma = {c["club_id"]: c for c in de["cau_lac_bo"]}
    theo_ten = {so_nhap.khoa_ten(c["name"]): c for c in de["cau_lac_bo"]}
    clb_fa, doi_ma, canh_bao = {}, {}, []
    for c in du["clubs"]:
        goc = theo_ma.get(c["club_id"]) or theo_ten.get(so_nhap.khoa_ten(c["name"]))
        if goc is None:
            canh_bao.append(("", "", "Sổ nhập CLB có %r nhưng de_thi.json không có CLB này — bỏ" % c["name"]))
            continue
        doi_ma[c["club_id"]] = goc["club_id"]
        clb_fa[goc["club_id"]] = {k: c[k] for k in ("loai", "capacity", "diem_san", "so_toi_thieu", "suc_chua_phong")
                                  if c.get(k) is not None}
    for ma in theo_ma:
        if ma not in clb_fa:
            canh_bao.append(("", "", "%s có trong de_thi.json nhưng không có trong Sổ nhập CLB — không biết Loại, "
                                     "coi như không phải CLB Tự do" % ma))
    giu_cho = [(doi_ma[c], s) for c, s in du.get("giu_cho", []) if c in doi_ma]
    return clb_fa, giu_cho, canh_bao


def _thoi_gian_lam_bai(tieu_de, cac_dong):
    """({email: giây}, số phiếu không đọc được giờ) từ cột Start time / Completion time của tệp Forms.

    FA-S4: nhận ô `datetime` và chữ ISO (2026-11-09 08:00:00 hoặc có "T"); dạng khác (11/9/26 08:00:00) KHÔNG đoán
    thứ tự ngày/tháng mà đếm vào số phiếu không đọc được. Thiếu cột: ({}, 0)."""
    from datetime import datetime
    chuan = [h.strip().lower() for h in tieu_de]
    if "start time" not in chuan or "completion time" not in chuan or "email" not in chuan:
        return {}, 0
    i_b, i_x, i_e = chuan.index("start time"), chuan.index("completion time"), chuan.index("email")

    def gio(o):
        return o if isinstance(o, datetime) else datetime.fromisoformat(str(o).strip())

    ra, n_loi = {}, 0
    for dong in cac_dong:
        if not any(dong):
            continue
        dong = list(dong) + [""] * (len(tieu_de) - len(dong))
        try:
            t = (gio(dong[i_x]) - gio(dong[i_b])).total_seconds()
        except ValueError:
            n_loi += 1
            continue
        ra.setdefault(str(dong[i_e]).strip().lower(), t)          # phiếu đầu của mỗi email (như phan_tich_chi_thi)
    return ra, n_loi


def chuyen_fa_daa(thu_muc_ra, de, so_nhap_clb, dang_ky_xlsx=(), lists=None, quiz_xlsx=(), nhan_ban_nhap=False,
                  co_so=None, bien_the_tep=None, ap_dung_dieu_chinh=False, giu_diem_goc=False, bo_cau=()):
    """FA-M3 (TH): đăng ký (đường B: Forms `dang_ky_xlsx`, hoặc đường A: CSV `lists`) + bài thi -> Sổ nhập FA.

    Loại CLB, chỉ tiêu, điểm sàn, giữ chỗ lấy từ Sổ nhập CLB của FA-M1 (`so_nhap_clb`). Huy chương MỘT quỹ 60/30/10
    vào cột "Điểm quyết tâm". Điểm thi quy về nguyên 0-10 (D7); em xếp CLB Tuyển chọn mà chưa thi: báo NOT_ATTEMPTED
    (kiosk cũng lọc theo điểm sàn); làm bài trong < 1/3 trung vị của CLB đó: gắn cờ (D9), chỉ báo. Soát huy chương
    bằng `fa_daa.kiem_ho_so_huy_chuong`. Không ghi gì nếu có lỗi chặn (LoiTepXuat).

    FA-M4: `bien_the_tep` {tên tệp: chữ đề "A"/"B"/"C"} cho các tệp bài thi của đề biến thể (đề B, C ở `de_thi_bien_the` của
    CLB trong de_thi.json); tệp không ghi là đề A. Mỗi CLB có từ hai đề trở lên được so sánh điểm giữa các đề (D11); có
    chênh lệch ngoài ngưỡng thì ghi DIEU_CHINH_BAN_DE.xlsx và dừng bằng LoiChoXacNhan TRỪ KHI admin chọn đúng một cờ:
    `ap_dung_dieu_chinh` (dịch về trung bình chung) hoặc `giu_diem_goc`. Không lệch thì không cần cờ. `bo_cau`
    {(club_id, đề, số câu)} (FA-S2; (club_id, số câu) chỉ khi CLB có một đề): câu admin đã xác nhận bỏ (V§7.5), chấm
    lại cho mọi học sinh làm đề đó. Luôn ghi PHAN_TICH_CAU_HOI.xlsx."""
    import fa_daa
    import phan_tich_cau_hoi as pt
    from fractions import Fraction
    from i18n_errors import format_all

    if ap_dung_dieu_chinh and giu_diem_goc:
        raise LoiTepXuat("chỉ chọn MỘT trong --ap-dung-dieu-chinh và --giu-diem-goc")
    theo_tep = None
    if bien_the_tep:
        theo_tep = {}
        loi_de = [x for c in de["cau_lac_bo"] for x in pt.kiem_bien_the(c)]
        if loi_de:
            raise LoiTepXuat("de_thi.json: " + "; ".join(loi_de))
        for ten, chu in bien_the_tep.items():
            if chu not in pt.CHU_BIEN_THE:
                raise LoiTepXuat("đề %r không hợp lệ (A, B hoặc C)" % chu)
            k = pt.CHU_BIEN_THE.index(chu)
            de_t = copy.deepcopy(de)
            for c in de_t["cau_lac_bo"]:
                if c["de_thi"] and k < len(pt.cac_bien_the(c)):
                    c["de_thi"] = pt.cac_bien_the(c)[k]
                elif c["de_thi"] and len(pt.cac_bien_the(c)) > 1:
                    raise LoiTepXuat("tệp %s là đề %s nhưng CLB %s chỉ có %d đề" % (ten, chu, c["club_id"], len(pt.cac_bien_the(c))))
            theo_tep[ten] = (chu, de_t)

    if not so_nhap_clb:
        raise LoiTepXuat("chế độ FA-DAA cần Sổ nhập CLB (--so-nhap-clb) để biết Loại của từng CLB")
    if bool(dang_ky_xlsx) == bool(lists):
        raise LoiTepXuat("chọn đúng MỘT nguồn đăng ký: tệp Forms đăng ký (đường B) hoặc CSV List (đường A)")
    clb_fa, giu_cho, canh_bao = doc_clb_fa(so_nhap_clb, de)
    tu_do = {c for c, v in clb_fa.items() if v.get("loai") == so_nhap.TU_DO}
    if lists:
        danh_sach, cb = doc_lists(lists, de, co_so, fa=True, nhan_ban_nhap=nhan_ban_nhap)
        canh_bao += cb
        ap_huy_chuong_duong_a(danh_sach, tu_do)
    else:
        danh_sach = {}
        for d in dang_ky_xlsx:
            tieu_de, cac_dong = doc_tep_xuat(d)
            danh_sach, cb = doc_dang_ky_fa_forms(de, tieu_de, cac_dong, tu_do, danh_sach)
            canh_bao += cb
    if not danh_sach:
        raise LoiTepXuat("không có học sinh nào trong dữ liệu đăng ký")
    cac_tep = []
    for d in quiz_xlsx:
        tieu_de, cac_dong = doc_tep_xuat(d)
        cac_tep.append((os.path.basename(d), tieu_de, cac_dong))
    hoc_sinh, cb = phan_tich_chi_thi(de, danh_sach, cac_tep, co_so, fa=True, theo_tep=theo_tep)
    if not cac_tep:
        cb = [x for x in cb if "có đề thi nhưng không tệp Forms" not in x[2]]
    canh_bao += cb
    theo_ma = {c["club_id"]: c for c in de["cau_lac_bo"]}
    bo_cau = _chuan_bo_cau(bo_cau, theo_ma)
    # D7 + D9: trung vị chỉ tính trên bài lần đầu (FA-S1)
    t_tep = {}
    for ten, tieu_de, cac_dong in cac_tep:
        t_tep[ten], n_loi = _thoi_gian_lam_bai(tieu_de, cac_dong)
        if n_loi:                                                  # FA-S4: một cảnh báo mỗi tệp
            canh_bao.append(("", "", "%s: %d phiếu không đọc được Start time / Completion time (cần dạng "
                             "2026-11-09 08:00:00) — các phiếu đó không xét cờ làm quá nhanh" % (ten, n_loi)))
    gio = {}
    for hs in hoc_sinh:
        for bai in hs["bai_thi"]:
            t = t_tep.get(bai["tep"], {}).get(hs["student_id"])
            if t is not None:
                gio.setdefault(bai["club_id"], {})[hs["student_id"]] = t
    nhanh = {ma: co_nhanh_qua(t) for ma, t in gio.items()}
    # FA-S1 (V§7.2): bài lần hai chỉ thay bài lần đầu khi lần đầu bị gắn cờ quá nhanh VÀ là đề thi lại của em.
    for hs in hoc_sinh:
        e = hs["student_id"]
        for bai2 in sorted(hs.pop("bai_khac", []), key=lambda b: b["tep"]):
            i = next(k for k, b in enumerate(hs["bai_thi"]) if b["club_id"] == bai2["club_id"])
            bai1, clb = hs["bai_thi"][i], theo_ma[bai2["club_id"]]
            if (not bai1.get("thi_lai") and e in nhanh.get(clb["club_id"], ()) and _so_de(clb) > 1
                    and bai2.get("bien_the") == _de_giao(e, clb, thi_lai=True)):
                bai2.update(nap=bai1["nap"], thi_lai=True)
                if bai1.get("khong_tick"):
                    bai2["khong_tick"] = True
                hs["bai_thi"][i] = bai2
                canh_bao.append((hs["dong"], e, "%s: lần đầu bị gắn cờ làm quá nhanh — dùng bài thi lại (đề %s, tệp %s)"
                                 % (clb["club_id"], bai2.get("bien_the", "A"), bai2["tep"])))
            else:
                canh_bao.append((hs["dong"], e, "%s: bài lần hai (tệp %s) không tính — giữ bài lần đầu (tệp %s); "
                                 "chỉ tính thi lại khi lần đầu bị gắn cờ làm quá nhanh và em làm đúng đề thi lại"
                                 % (clb["club_id"], bai2["tep"], bai1["tep"])))
    if theo_tep is not None:                                       # FA-S5: làm sai đề giao -> báo, giữ điểm
        for hs in hoc_sinh:
            for bai in hs["bai_thi"]:
                clb = theo_ma[bai["club_id"]]
                giao = _de_giao(hs["student_id"], clb, thi_lai=bool(bai.get("thi_lai")))
                if _so_de(clb) > 1 and bai.get("bien_the", "A") != giao:
                    canh_bao.append((hs["dong"], hs["student_id"], "%s: email %s làm đề %s nhưng đề giao %s — vẫn giữ "
                                     "điểm, admin quyết định" % (clb["club_id"], hs["student_id"],
                                                                bai.get("bien_the", "A"), giao)))
    bai_cua = {}                                                   # club_id -> [(bài, khoá email)]
    for hs in hoc_sinh:
        e = hs["student_id"]                                        # lúc này là khoá email (như doc_lists)
        for bai in hs["bai_thi"]:
            clb = theo_ma[bai["club_id"]]
            bo = {k for c, b, k in bo_cau if c == bai["club_id"] and b == bai.get("bien_the", "A")}
            bai["diem_10_tho"] = (Fraction(10 * sum(d for i, d in enumerate(bai["dung"], 1) if i not in bo),
                                           len(bai["dung"]) - len(bo)) if len(bai["dung"]) > len(bo) else Fraction(0)) \
                if bo else Fraction(str(bai["diem"])) / Fraction(str(bm.diem_toi_da(de, clb))) * 10
            bai["diem_so_nhap"] = pt.diem_dieu_chinh(bai["diem_10_tho"], 0)
            bai_cua.setdefault(bai["club_id"], []).append((bai, e))
            if e in nhanh.get(bai["club_id"], ()) and not bai.get("thi_lai"):
                bai["nhanh_qua"] = True
                if _so_de(theo_ma[bai["club_id"]]) > 1:
                    canh_bao.append((hs["dong"], e, "%s: làm bài quá nhanh (dưới 1/3 thời gian trung vị của CLB này) "
                                     "— gắn cờ, cho thi lại một lần bằng đề khác nếu admin đồng ý" % bai["club_id"]))
                else:                                              # FA-N4: thi lại cần đề khác
                    canh_bao.append((hs["dong"], e, "%s: làm bài quá nhanh (dưới 1/3 thời gian trung vị của CLB này) "
                                     "— gắn cờ, nhưng CLB chỉ có một đề nên không có đề thi lại; giữ điểm bài đầu"
                                     % bai["club_id"]))
    so_sanh = {}
    if cac_tep:
        for ma, ds in bai_cua.items():
            theo_de = {}
            for bai, _ in ds:
                if bai["nap"]:
                    theo_de.setdefault(bai.get("bien_the", "A"), []).append(float(bai["diem_10_tho"]))
            if len(theo_de) > 1:
                so_sanh[ma] = pt.so_sanh_bien_the(theo_de)
        hang_cau = pt.phan_tich_cau([{"sid": e, "club_id": b["club_id"], "bien_the": b.get("bien_the", "A"), "dung": b["dung"]}
                                     for ds in bai_cua.values() for b, e in ds])
        os.makedirs(thu_muc_ra, exist_ok=True)
        pt.ghi_bao_cao(os.path.join(thu_muc_ra, "PHAN_TICH_CAU_HOI.xlsx"), hang_cau=hang_cau)
        for r in hang_cau:
            for co in r["co"]:
                canh_bao.append(("", "", "%s đề %s câu %d: %s (%.0f%% đúng) — xem PHAN_TICH_CAU_HOI.xlsx"
                                 % (r["club_id"], r["bien_the"], r["cau"], co, 100 * r["ti_le_dung"])))
    if so_sanh:
        pt.ghi_bao_cao(os.path.join(thu_muc_ra, "DIEU_CHINH_BAN_DE.xlsx"), so_sanh_theo_clb=so_sanh)
        lech = [ma for ma, kq in so_sanh.items() if kq["co_lech"]]
        if lech and not (ap_dung_dieu_chinh or giu_diem_goc):
            raise LoiChoXacNhan(
                "CLB %s: điểm giữa các đề lệch ngoài ngưỡng ngẫu nhiên (xem DIEU_CHINH_BAN_DE.xlsx). Chưa ghi %s. Chạy lại với "
                "--ap-dung-dieu-chinh (dịch điểm mỗi đề về trung bình chung) hoặc --giu-diem-goc (giữ điểm đã chấm)."
                % (", ".join(lech), TEN_SO))
        if ap_dung_dieu_chinh:
            for ma in [m for m, kq in so_sanh.items() if kq["co_lech"]]:
                for bai, e in bai_cua[ma]:
                    dich = so_sanh[ma]["bien_the"].get(bai.get("bien_the", "A"), {}).get("dich", 0.0)
                    if dich:
                        bai["diem_so_nhap"] = pt.diem_dieu_chinh(bai["diem_10_tho"], dich)
                canh_bao.append(("", "", "%s: đã dịch điểm các đề về trung bình chung (admin xác nhận --ap-dung-dieu-chinh)" % ma))
    if cac_tep:
        for hs in hoc_sinh:
            nap = {b["club_id"] for b in hs["bai_thi"] if b["nap"]}
            for xep in hs["nguyen_vong"].values():
                for c in xep:
                    if clb_fa.get(c, {}).get("loai") == so_nhap.TUYEN_CHON and c not in nap:
                        canh_bao.append((hs["dong"], hs["student_id"], "%s: NOT_ATTEMPTED — em xếp CLB Tuyển chọn "
                                         "nhưng chưa có bài thi, sẽ không được xét CLB này" % c))
    # soát huy chương (một quỹ)
    pref, bids = {}, {}
    for hs in hoc_sinh:
        sid = hs["student_id"]
        pref[sid] = [c for xep in hs["nguyen_vong"].values() for c in xep]
        bids[sid] = {c: v for wp in hs.get("wp", {}).values() for c, v in wp.items() if v is not None}
    cac_clb = {c: {"buoi": theo_ma[c]["buoi"], "loai": clb_fa.get(c, {}).get("loai")} for c in theo_ma}
    loi_hc = fa_daa.kiem_ho_so_huy_chuong(pref, bids, cac_clb)
    for loi, nd in zip(loi_hc, format_all(loi_hc)):
        canh_bao.append(("", loi["params"].get("student_id", ""), nd))
    # mã học sinh em gõ (đường B) làm mã trong Sổ nhập
    for hs in hoc_sinh:
        goc = danh_sach.get(hs["student_id"], {})
        hs["email"] = hs["student_id"]
        hs["student_id"] = goc.get("student_id", hs["student_id"])
    os.makedirs(thu_muc_ra, exist_ok=True)
    ghi_tep_phan_mem(de, hoc_sinh, thu_muc_ra, clb_fa=clb_fa, giu_cho=giu_cho)
    # FA-S11: email <-> mã học sinh để IT ghép kết quả vào list KetQua (ghep_ket_qua_email.py). Dữ liệu cá nhân.
    with open(os.path.join(thu_muc_ra, TEN_EMAIL_MA_HS), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Email", "student_id"])
        w.writerows([h["email"], h["student_id"]] for h in hoc_sinh)
    if cac_tep:
        ghi_bang_diem(de, hoc_sinh, canh_bao, os.path.join(thu_muc_ra, "BANG_DIEM.xlsx"))
    return {"n_hoc_sinh": len(hoc_sinh), "n_bai_thi": sum(len(h["bai_thi"]) for h in hoc_sinh),
            "canh_bao": canh_bao, "ghi_chu": [GHI_CHU_FA_DAA],
            "cau_co_co": [{"club_id": r["club_id"], "bien_the": r["bien_the"], "cau": r["cau"], "co": list(r["co"]),
                           "ti_le_dung": r["ti_le_dung"]}
                          for r in (hang_cau if cac_tep else []) if r["co"]]}


TEN_EMAIL_MA_HS = "EMAIL_MA_HS.csv"
GHI_CHU_FA_DAA = ("FA-DAA (TH, chưa thử trên Microsoft thật): huy chương là MỘT quỹ 60/30/10 ở cột \"Điểm quyết "
                  "tâm\"; điểm thi là số nguyên 0-10 (D7). Cờ \"làm quá nhanh\" chỉ để admin xem.")


_BO_QUA_TIEU_DE = (TIEN_TO_DIEM, TIEN_TO_NHAN_XET)
_MA_KHAI_NAI = {"co_sai", "kn_buoi", "kn_ghi_chu"}
_RE_MA_DANG_KY = re.compile(r".+-nv\d+")
_RE_MA_BAI_THI = re.compile(r"(?!thi-).+-\d+")
_RE_THE_DAU = re.compile(r"^\s*(?:\d+[.)]\s*)?\[[^\]]+\]\s*")


def _ma_cac_cot(tieu_de, ban_do=None):
    return {m for h in tieu_de or () if not str(h).startswith(_BO_QUA_TIEU_DE)
            for m in [bm.ma_cua_cau(h, ban_do)] if m}


def nhan_dien_tep(ten, tieu_de, de=None):
    """FA-M9 (TH): loại tệp người dùng thả vào, chỉ nhìn tên tệp và dòng tiêu đề (không đọc dữ liệu, không ghi gì).

    "sau_ket_qua" = biểu mẫu "Sau khi xem kết quả" (có `[co_sai]`, `[kn_buoi]` hoặc `[kn_ghi_chu]`); "lists" = CSV xuất
    từ List đường A (có đủ cột Email, Thu, NV1); "dang_ky" = Forms đăng ký (có `[<buổi>-nvK]`); "bai_thi" = Forms bài thi
    (có `[<club_id>-<số>]`); tệp trộn đăng ký với bài thi, tệp .csv không phải List, hoặc không nhận ra gì = "khong_ro".

    SG-12: tiêu đề thuần (không thẻ `[mã]`) được nhận qua bản đồ dựng từ `de`; không có `de` thì chỉ nhận được các câu không
    phụ thuộc đề (mã học sinh, phản hồi, khiếu nại)."""
    ma = _ma_cac_cot(tieu_de, bm.ban_do_chung(de))
    if ma & _MA_KHAI_NAI:
        return "sau_ket_qua"
    cot = {str(h).strip().lower() for h in tieu_de or ()}
    if {"email", "thu", "nv1"} <= cot:
        return "lists"
    if str(ten or "").lower().endswith(".csv"):
        return "khong_ro"
    co_dk = any(_RE_MA_DANG_KY.fullmatch(m) for m in ma)
    co_thi = any(_RE_MA_BAI_THI.fullmatch(m) for m in ma)
    if co_dk and not co_thi:
        return "dang_ky"
    if co_thi and not co_dk:
        return "bai_thi"
    return "khong_ro"


def _chuan_cau(h):
    return " ".join(_RE_THE_DAU.sub("", str(h), count=1).split())


def doan_bien_the(de, tieu_de):
    """FA-M9 (R5, TH): đoán tệp bài thi là đề "A", "B" hay "C" bằng cách so chữ của từng câu (sau thẻ `[...]`) với các đề.

    Với mỗi CLB có câu trong tệp: các đề khớp TẤT CẢ câu của CLB đó (so từng số câu, bỏ khoảng trắng thừa). CLB chỉ có
    một đề khớp với mọi chữ cái. Giao các tập đề của các CLB: đúng một đề -> trả chữ đó; còn lại (lẫn, mơ hồ, không khớp,
    không có câu bài thi) -> None, UI bắt chọn tay. CLB lạ không có trong `de` bị bỏ qua. Không đổi gì ở CLI `--bien-the-tep`."""
    import phan_tich_cau_hoi as pt
    theo_ma = {c["club_id"]: c for c in de["cau_lac_bo"] if c.get("de_thi")}
    ban_do = bm.ban_do_chung(de)
    cau = {}                                                  # {club_id: {số câu: (chữ câu, có thẻ mã không)}}
    for h in tieu_de or ():
        if str(h).startswith(_BO_QUA_TIEU_DE):
            continue
        ma = bm.ma_cua_cau(h, ban_do)
        m = _RE_MA_BAI_THI.fullmatch(ma) if ma else None
        if m:
            clb, so = ma.rsplit("-", 1)
            if clb in theo_ma:
                cau.setdefault(clb, {})[int(so)] = (_chuan_cau(h), bool(_RE_THE_DAU.match(str(h))))
    if not cau:
        return None

    def khop_cau(clb, de_k, so, chu_cau, co_the):
        """Chữ câu của tệp khớp câu `so` của đề `de_k`? Tệp cũ (có thẻ): so chữ câu; tệp mới (tiêu đề thuần): so với
        tiêu đề thuần mà bộ sinh ghi cho câu đó (có thể kèm "(tên CLB, câu k)" khi trùng chữ giữa các CLB)."""
        if not 0 < so <= len(de_k):
            return False
        if _chuan_cau(de_k[so - 1]["cau"]) == chu_cau:
            return True
        if co_the:
            return False
        return bm._khoa(bm.cau_de_thi(dict(theo_ma[clb], de_thi=de_k), so, de).thuan) == bm._khoa(chu_cau)

    chung, co_nhieu_de = set(pt.CHU_BIEN_THE), False
    for clb, theo_so in cau.items():
        cac_de = pt.cac_bien_the(theo_ma[clb])
        khop = set()
        for chu, de_k in zip(pt.CHU_BIEN_THE, cac_de):
            if all(khop_cau(clb, de_k, so, chu_cau, co_the) for so, (chu_cau, co_the) in theo_so.items()):
                khop.add(chu)
        if len(cac_de) == 1 and khop:
            khop = set(pt.CHU_BIEN_THE)                       # một đề: chữ nào cũng được, converter giữ đề A
        else:
            co_nhieu_de = True
        chung &= khop
    if not co_nhieu_de:
        return "A" if chung else None                         # mọi CLB chỉ có một đề: chỉ có đề A
    return next(iter(chung)) if len(chung) == 1 else None


def chuyen_fa_daa_du_lieu(thu_muc_ra, de, so_nhap_clb, dang_ky_xlsx=(), lists=None, quiz_xlsx=(), bien_the_tep=None,
                          lua_chon=None, nhan_ban_nhap=False, co_so=None):
    """FA-M9 (TH): bọc `chuyen_fa_daa` để trả DỮ LIỆU thay vì in ra hay ném lỗi (CLI `main` không đổi).

    `lua_chon` (admin chọn ở UI, None = chưa chọn gì): {"dieu_chinh": "ap_dung" | "giu", "bo_cau": [(clb, đề, số)]}.
    Trả {"trang_thai": "xong", **kết quả của chuyen_fa_daa} | {"trang_thai": "cho_xac_nhan", "thong_bao", "clb": [mã CLB lệch],
    "bao_cao": đường dẫn DIEU_CHINH_BAN_DE.xlsx} | {"trang_thai": "loi", "thong_bao"} (lỗi bm.LoiDeThi / LoiTepXuat: không ghi Sổ)."""
    lc = lua_chon or {}
    try:
        kq = chuyen_fa_daa(thu_muc_ra, de, so_nhap_clb, dang_ky_xlsx=dang_ky_xlsx, lists=lists, quiz_xlsx=quiz_xlsx,
                           nhan_ban_nhap=nhan_ban_nhap, co_so=co_so, bien_the_tep=bien_the_tep or None,
                           ap_dung_dieu_chinh=lc.get("dieu_chinh") == "ap_dung",
                           giu_diem_goc=lc.get("dieu_chinh") == "giu",
                           bo_cau={tuple(x) for x in lc.get("bo_cau") or ()})
    except LoiChoXacNhan as e:
        m = re.match(r"CLB ([^:]+):", str(e))
        return {"trang_thai": "cho_xac_nhan", "thong_bao": str(e),
                "clb": [x.strip() for x in m.group(1).split(",")] if m else [],
                "bao_cao": os.path.join(thu_muc_ra, "DIEU_CHINH_BAN_DE.xlsx")}
    except (bm.LoiDeThi, LoiTepXuat) as e:
        return {"trang_thai": "loi", "thong_bao": str(e)}
    return {"trang_thai": "xong", **kq}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("tep_xuat", nargs="*",
                    help="tệp .xlsx tải từ Forms (Responses → Open in Excel); "
                         "nhiều tệp chỉ khi --chi-thi (hoặc --fa-daa) và biểu mẫu tách theo buổi")
    ap.add_argument("--ra", required=True, help="thư mục ghi kết quả")
    ap.add_argument("--de", default=bm.DE_THI_MAC_DINH, help="de_thi.json")
    ap.add_argument("--chi-thi", action="store_true",
                    help="Forms chỉ có bài thi, khoá là Email; cần --lists")
    ap.add_argument("--lists", help="tệp CSV xuất từ List đăng ký (chỉ với --chi-thi)")
    ap.add_argument("--co-so", help="chỉ lấy học sinh có cột CoSo của List bằng giá trị này, ví dụ CS1 "
                                    "(chỉ với --chi-thi); bỏ trống = không lọc")
    ap.add_argument("--bai-thi", help="CSV xuất từ list BaiThi (Email, ClubId, ResponseId, NopLuc): đối chiếu "
                                      "với các tệp xuất, chỉ báo, không đổi điểm (chỉ với --chi-thi)")
    ap.add_argument("--fa-daa", action="store_true",
                    help="FA-DAA (TH): đăng ký + bài thi -> Sổ nhập có Loại CLB, huy chương một quỹ, điểm nguyên 0-10; "
                         "cần --so-nhap-clb và đúng một trong --dang-ky (đường B) / --lists (đường A); "
                         "tệp đặt ở vị trí bắt buộc là bài thi (có thể không có)")
    ap.add_argument("--so-nhap-clb", help="Sổ nhập CLB do chuyen_phieu_clb.py sinh (chỉ với --fa-daa)")
    ap.add_argument("--dang-ky", nargs="+", help="tệp Forms đăng ký (FA-M2), mỗi ngày một tệp (chỉ với --fa-daa)")
    ap.add_argument("--bien-the-tep", nargs="+", metavar="TEN_TEP=DE",
                    help="tệp bài thi của đề biến thể, ví dụ thi_B.xlsx=B; tệp không ghi là đề A (chỉ với --fa-daa)")
    ap.add_argument("--ap-dung-dieu-chinh", action="store_true",
                    help="admin xác nhận: dịch điểm mỗi đề về trung bình chung khi các đề lệch (chỉ với --fa-daa)")
    ap.add_argument("--giu-diem-goc", action="store_true",
                    help="admin xác nhận: giữ điểm đã chấm dù các đề lệch (chỉ với --fa-daa)")
    ap.add_argument("--bo-cau", nargs="+", metavar="CLB-DE-SO",
                    help="câu admin xác nhận bỏ, ví dụ clb_covua-B-3 (đề B câu 3); CLB chỉ có một đề: clb_covua-3; "
                         "chấm lại cho mọi học sinh làm đề đó (chỉ với --fa-daa)")
    ap.add_argument("--nhan-ban-nhap", action="store_true",
                    help="giữ cả dòng TrangThai = DRAFT của List (chỉ với --fa-daa, đường A)")
    a = ap.parse_args(argv)
    if a.fa_daa:
        if not a.so_nhap_clb:
            ap.error("--fa-daa cần --so-nhap-clb")
        if bool(a.dang_ky) == bool(a.lists):
            ap.error("--fa-daa cần đúng một nguồn đăng ký: --dang-ky (Forms, đường B) hoặc --lists (CSV, đường A)")
        if a.chi_thi:
            ap.error("--fa-daa không dùng chung với --chi-thi")
        if a.ap_dung_dieu_chinh and a.giu_diem_goc:
            ap.error("chỉ chọn MỘT trong --ap-dung-dieu-chinh và --giu-diem-goc")
    elif (a.so_nhap_clb or a.dang_ky or a.nhan_ban_nhap or a.bien_the_tep or a.ap_dung_dieu_chinh or a.giu_diem_goc
          or a.bo_cau):
        ap.error("--so-nhap-clb, --dang-ky, --nhan-ban-nhap, --bien-the-tep, --ap-dung-dieu-chinh, --giu-diem-goc và "
                 "--bo-cau chỉ dùng cùng --fa-daa")
    if not a.tep_xuat and not a.fa_daa:
        ap.error("cần ít nhất một tệp .xlsx")
    if a.bai_thi is not None and not a.chi_thi:
        ap.error("--bai-thi chỉ dùng cùng --chi-thi")
    if a.chi_thi and not a.lists:
        ap.error("--chi-thi cần --lists (tệp CSV nguyện vọng xuất từ List)")
    if a.lists and not a.chi_thi and not a.fa_daa:
        ap.error("--lists chỉ dùng cùng --chi-thi")
    if a.co_so is not None and not a.chi_thi and not a.fa_daa:
        ap.error("--co-so chỉ dùng cùng --chi-thi")
    if len(a.tep_xuat) > 1 and not a.chi_thi and not a.fa_daa:
        ap.error("chế độ mặc định chỉ nhận một tệp .xlsx")
    try:
        if a.fa_daa:
            kq = chuyen_fa_daa(a.ra, bm.doc_de_thi(a.de), a.so_nhap_clb, dang_ky_xlsx=a.dang_ky or (), lists=a.lists,
                               quiz_xlsx=a.tep_xuat, nhan_ban_nhap=a.nhan_ban_nhap, co_so=a.co_so,
                               bien_the_tep=dict(x.split("=", 1) for x in a.bien_the_tep or []) or None,
                               ap_dung_dieu_chinh=a.ap_dung_dieu_chinh, giu_diem_goc=a.giu_diem_goc,
                               bo_cau={_doc_bo_cau(x) for x in a.bo_cau or []})
        elif a.chi_thi:
            kq = chuyen_chi_thi(a.tep_xuat, a.lists, a.ra, bm.doc_de_thi(a.de), a.co_so, a.bai_thi)
        else:
            kq = chuyen(a.tep_xuat[0], a.ra, bm.doc_de_thi(a.de))
    except LoiChoXacNhan as e:
        print("CHỜ ADMIN XÁC NHẬN — %s" % e, file=sys.stderr)
        return 3
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
