"""Sau khi xếp (FA gaps, V§9.2–9.3): nhật ký điều chỉnh, điểm danh, mời danh sách chờ.

Kết quả DA của một lần chạy (`match_results`) KHÔNG BAO GIỜ bị sửa tại chỗ, `run_history` chỉ ghi thêm (bất biến 4).
Mọi lần đổi chỗ sau khi công bố là MỘT dòng ghi thêm trong `fa_dieu_chinh`; chỗ hiện tại = kết quả lần chạy gốc của
buổi + các dòng điều chỉnh phát lại theo `id` (`vi_tri_hien_tai`, hàm thuần). Điểm danh, khiếu nại, phản hồi không bao
giờ đi vào `compute_club_priority` (bất biến 2).
"""

import datetime
import re

# GAP-0 ---------------------------------------------------------------------------------------------------------------
KIND = ("release", "invite_offer", "invite_accept", "invite_decline", "invite_expire", "round2", "appeal_rerun")
KIND_DOI_CHO = ("release", "invite_accept", "round2")        # chỉ ba loại này làm đổi chỗ
COT_DIEU_CHINH = ("id", "created_at", "run_id_base", "buoi", "student_id", "club_from", "club_to", "kind", "actor",
                  "note")


def vi_tri_hien_tai(ket_qua: dict, run_goc: dict, dieu_chinh) -> tuple:
    """(vi_tri, lech): chỗ hiện tại {(sid, buoi): club_id|None} sau khi phát lại `dieu_chinh` theo `id`.

    `ket_qua` {(sid, buoi): club_id|None} của `match_results`; `run_goc` {buoi: run_id} (lần chạy gốc của buổi);
    `dieu_chinh` các dòng (dict theo cột `fa_dieu_chinh`). Dòng của lần chạy khác lần gốc -> không áp dụng, `lech`
    ghi `run_cu`. Dòng đổi chỗ mà `club_from` khác chỗ hiện tại (hay em không có trong kết quả) -> không áp dụng,
    `lech` ghi `khong_khop`. Không sửa đầu vào, không ném lỗi."""
    vi_tri = dict(ket_qua)
    lech = []
    for d in sorted(dieu_chinh, key=lambda x: x["id"]):
        if d["run_id_base"] != run_goc.get(d["buoi"]):
            lech.append({"id": d["id"], "ly_do": "run_cu"})
            continue
        if d["kind"] not in KIND_DOI_CHO:
            continue
        k = (d["student_id"], d["buoi"])
        if k not in vi_tri or vi_tri[k] != d["club_from"]:
            lech.append({"id": d["id"], "ly_do": "khong_khop"})
            continue
        vi_tri[k] = None if d["kind"] == "release" else d["club_to"]
    return vi_tri, lech


def run_goc_theo_buoi(cur) -> dict:
    """{buoi: run_id}: lần chạy MỚI NHẤT có chạy buổi đó (`buoi_da_chay` rỗng = mọi buổi), như
    `api_xuat._doc_ly_do_moi_nhat`."""
    runs = cur.execute("SELECT run_id, buoi_da_chay FROM run_history ORDER BY run_id DESC").fetchall()
    ra = {}
    for (buoi,) in cur.execute("SELECT DISTINCT buoi FROM match_results").fetchall():
        for run_id, da_chay in runs:
            ds = [x for x in (da_chay or "").split(",") if x]
            if not ds or buoi in ds:
                ra[buoi] = run_id
                break
    return ra


def doc_dieu_chinh(cur) -> list:
    return [dict(zip(COT_DIEU_CHINH, r)) for r in cur.execute(
        "SELECT %s FROM fa_dieu_chinh ORDER BY id" % ", ".join(COT_DIEU_CHINH))]


def doc_vi_tri(cur) -> tuple:
    """(vi_tri, lech, run_goc) đọc từ CSDL (`match_results` + `fa_dieu_chinh`)."""
    ket_qua = {(r[0], r[1]): r[2] for r in cur.execute("SELECT student_id, buoi, club_id FROM match_results")}
    run_goc = run_goc_theo_buoi(cur)
    vi_tri, lech = vi_tri_hien_tai(ket_qua, run_goc, doc_dieu_chinh(cur))
    return vi_tri, lech, run_goc


def ghi_dieu_chinh(cur, run_id_base, buoi, student_id, club_from, club_to, kind, actor="", note="") -> int:
    """Cách DUY NHẤT ghi `fa_dieu_chinh`: chỉ INSERT. Loại lạ -> ValueError."""
    if kind not in KIND:
        raise ValueError("fa_dieu_chinh: loai dieu chinh khong hop le %r" % (kind,))
    cur.execute(
        "INSERT INTO fa_dieu_chinh (created_at, run_id_base, buoi, student_id, club_from, club_to, kind, actor, note) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), run_id_base, buoi, student_id, club_from, club_to,
         kind, actor or "", note or ""))
    return cur.lastrowid


# GAP-1 ---------------------------------------------------------------------------------------------------------------
TRANG_THAI_DIEM_DANH = ("CO_MAT", "VANG_CO_PHEP", "VANG_KHONG_PHEP")
NGUONG_VANG = 2                 # vắng KHÔNG PHÉP từ 2 trong 3 buổi đầu -> giải phóng chỗ (V§9.3)


def can_giai_phong(trang_thai_theo_buoi: dict) -> bool:
    """{buoi_so: trang_thai} -> có phải giải phóng chỗ không."""
    return sum(1 for v in trang_thai_theo_buoi.values() if v == "VANG_KHONG_PHEP") >= NGUONG_VANG


def da_giai_phong_khoi(dieu_chinh, run_goc: dict, buoi: str, club_id: str) -> set:
    """Học sinh đã bị giải phóng khỏi `club_id` ở `buoi` trong lần chạy gốc hiện tại."""
    return {d["student_id"] for d in dieu_chinh
            if d["kind"] == "release" and d["buoi"] == buoi and d["club_from"] == club_id
            and d["run_id_base"] == run_goc.get(buoi)}


def ten_trang_xlsx(ten: str, da_dung: set) -> str:
    """Tên trang Excel hợp lệ: bỏ ký tự cấm, tối đa 31 ký tự, không trùng (thêm " (2)")."""
    from so_excel import lam_sach
    goc = "".join(ch for ch in (lam_sach(str(ten or "")) or "") if ch not in '/\\?*[]:').strip("' ") or "CLB"
    goc = goc[:31]
    ten_moi, n = goc, 2
    while ten_moi.lower() in da_dung:
        hau = " (%d)" % n
        ten_moi = goc[:31 - len(hau)] + hau
        n += 1
    da_dung.add(ten_moi.lower())
    return ten_moi


# GAP-2 ---------------------------------------------------------------------------------------------------------------
LOAI_CO_DANH_SACH_CHO = ("GIOI_HAN", "TUYEN_CHON")       # CLB Tự do không từ chối ai nên không có danh sách chờ
KIND_TRA_LOI = {"nhan": "invite_accept", "tu_choi": "invite_decline", "het_han": "invite_expire"}
COT_LY_DO = ("run_id", "buoi", "student_id", "club_id", "outcome", "rank_in_list", "waitlist_pos")


def _khoa_moi(d):
    return (d["run_id_base"], d["buoi"], d["student_id"], d["club_to"])


def moi_dang_cho(dieu_chinh, run_goc: dict) -> dict:
    """{offer_id: dòng}: lời mời (`invite_offer`) của lần chạy gốc hiện tại chưa có dòng nhận / từ chối / hết hạn
    nào SAU nó cho cùng (lần chạy, buổi, học sinh, CLB)."""
    dang = {}
    for d in sorted(dieu_chinh, key=lambda x: x["id"]):
        if d["run_id_base"] != run_goc.get(d["buoi"]):
            continue
        if d["kind"] == "invite_offer":
            dang[d["id"]] = d
        elif d["kind"] in ("invite_accept", "invite_decline", "invite_expire"):
            for i, m in list(dang.items()):
                if _khoa_moi(m) == _khoa_moi(d):
                    del dang[i]
    return dang


def trang_thai_moi(dieu_chinh) -> dict:
    """{offer_id: "CHO" | "NHAN" | "TU_CHOI" | "HET_HAN"} cho mọi lời mời (mọi lần chạy)."""
    ten = {"invite_accept": "NHAN", "invite_decline": "TU_CHOI", "invite_expire": "HET_HAN"}
    ra, mo = {}, {}
    for d in sorted(dieu_chinh, key=lambda x: x["id"]):
        if d["kind"] == "invite_offer":
            ra[d["id"]] = "CHO"
            mo[d["id"]] = d
        elif d["kind"] in ten:
            for i, m in list(mo.items()):
                if _khoa_moi(m) == _khoa_moi(d):
                    ra[i] = ten[d["kind"]]
                    del mo[i]
    return ra


def hang_cho(ly_do_rows, vi_tri: dict, run_goc: dict, dieu_chinh, buoi: str, club_id: str) -> list:
    """Danh sách chờ CÒN mời được của `club_id` ở `buoi`, theo `waitlist_pos` (D4, đã tính trong `fa_ly_do`).

    Giữ em khi: dòng `REJECTED` ở CLB đó trong lần chạy gốc; em không đang ở CLB đó; CLB đó xếp CAO hơn CLB hiện tại
    của em (`rank_in_list` nhỏ hơn; chưa có CLB thì giữ); em không có lời mời nào đang chờ ở buổi đó; em chưa từ chối
    / để hết hạn lời mời của CLB này trong lần chạy gốc. Hàm thuần."""
    run = run_goc.get(buoi)
    hang_cua = {}
    for r in ly_do_rows:
        if r["run_id"] == run and r["buoi"] == buoi:
            hang_cua.setdefault(r["student_id"], {})[r["club_id"]] = r["rank_in_list"]
    dang = moi_dang_cho(dieu_chinh, run_goc)
    co_moi = {d["student_id"] for d in dang.values() if d["buoi"] == buoi}
    da_bo = {d["student_id"] for d in dieu_chinh
             if d["kind"] in ("invite_decline", "invite_expire") and d["run_id_base"] == run
             and d["buoi"] == buoi and d["club_to"] == club_id}
    ung_vien = sorted((r for r in ly_do_rows if r["run_id"] == run and r["buoi"] == buoi
                       and r["club_id"] == club_id and r["outcome"] == "REJECTED" and r["waitlist_pos"]),
                      key=lambda r: (r["waitlist_pos"], r["student_id"]))
    ra = []
    for r in ung_vien:
        sid = r["student_id"]
        hien = vi_tri.get((sid, buoi))
        if hien == club_id or sid in co_moi or sid in da_bo:
            continue
        if hien is not None:
            hang_hien = hang_cua.get(sid, {}).get(hien)
            if hang_hien is not None and not (r["rank_in_list"] < hang_hien):
                continue
        ra.append(sid)
    return ra


def moi_tiep(cur, buoi: str, club_id: str) -> list:
    """Mời người kế tiếp vào `club_id` ở `buoi` khi còn chỗ (thành viên + lời mời đang chờ < chỉ tiêu). Chỉ CLB
    Giới hạn / Tuyển chọn của lần chạy gốc có lý do FA. Ghi `invite_offer`; trả các id đã ghi."""
    if not club_id:
        return []
    clb = cur.execute("SELECT loai, capacity FROM clubs WHERE club_id = ?", (club_id,)).fetchone()
    if not clb or clb[0] not in LOAI_CO_DANH_SACH_CHO:
        return []
    vi_tri, _, run_goc = doc_vi_tri(cur)
    run = run_goc.get(buoi)
    ly_do = [dict(zip(COT_LY_DO, r)) for r in cur.execute(
        "SELECT %s FROM fa_ly_do WHERE run_id = ? AND buoi = ?" % ", ".join(COT_LY_DO), (run, buoi))]
    if not ly_do:
        return []
    da_ghi = []
    while True:
        dc = doc_dieu_chinh(cur)
        dang = [d for d in moi_dang_cho(dc, run_goc).values() if d["buoi"] == buoi and d["club_to"] == club_id]
        so_tv = sum(1 for (_, b), c in vi_tri.items() if b == buoi and c == club_id)
        if so_tv + len(dang) >= clb[1]:
            break
        ds = hang_cho(ly_do, vi_tri, run_goc, dc, buoi, club_id)
        if not ds:
            break
        sid = ds[0]
        da_ghi.append(ghi_dieu_chinh(cur, run, buoi, sid, vi_tri.get((sid, buoi)), club_id, "invite_offer",
                                     actor="moi_cho"))
    return da_ghi


# GAP-3 ---------------------------------------------------------------------------------------------------------------
SO_NGAY_KHIEU_NAI = 3          # V§9.2: nhận khiếu nại trong 3 ngày từ lúc công bố (rules.fa_khieu_nai_so_ngay đổi được)


def bay_gio() -> datetime.datetime:
    """Đồng hồ của phần khiếu nại (test thay hàm này; không bao giờ sửa `run_history`)."""
    return datetime.datetime.now()


def _doc_gio(chu: str) -> datetime.datetime:
    return datetime.datetime.strptime(str(chu)[:19].replace("T", " "), "%Y-%m-%d %H:%M:%S")


def trong_han_khieu_nai(run_at: str, luc: datetime.datetime, so_ngay: int) -> bool:
    """Còn trong hạn khiếu nại: `luc` không quá `so_ngay` ngày sau `run_at` (lúc công bố = lúc chạy). Tính cả mốc."""
    return luc - _doc_gio(run_at) <= datetime.timedelta(days=so_ngay)


def anh_huong_sau_chay_lai(khieu_nai, run_goc: dict, dieu_chinh) -> dict:
    """{id khiếu nại đã chấp nhận: {da_chay_lai, dieu_chinh_cu}}: buổi đó đã có lần chạy gốc MỚI hơn lần lúc khiếu nại
    chưa, và các dòng điều chỉnh của lần chạy cũ (nay không còn áp dụng, phải xem lại). Hàm thuần."""
    ra = {}
    for k in khieu_nai:
        if k["trang_thai"] != "CHAP_NHAN":
            continue
        moi = run_goc.get(k["buoi"])
        da = moi is not None and moi != k["run_id_base"]
        cu = sorted(d["id"] for d in dieu_chinh
                    if d["run_id_base"] == k["run_id_base"] and d["buoi"] == k["buoi"]) if da else []
        ra[k["id"]] = {"da_chay_lai": da, "dieu_chinh_cu": cu}
    return ra


# GAP-4 ---------------------------------------------------------------------------------------------------------------
def can_vong_2(vi_tri: dict, nguyen_vong: dict, buoi: str) -> list:
    """Học sinh của `buoi` chưa có CLB mong muốn: chưa có chỗ, hoặc chỗ hiện tại không nằm trong nguyện vọng của chính
    em (dự phòng). Sắp theo mã. Hàm thuần."""
    return sorted(sid for (sid, b), cid in vi_tri.items()
                  if b == buoi and (cid is None or cid not in (nguyen_vong.get(sid) or [])))


def cho_con_lai(vi_tri: dict, suc_chua: dict, dang_moi: dict, buoi: str, clb_cua_buoi) -> dict:
    """{club_id: số chỗ còn} của các CLB thuộc `buoi`: chỉ tiêu − thành viên hiện tại − lời mời đang chờ; chỉ CLB còn
    chỗ (> 0). Hàm thuần."""
    dem: dict = {}
    for (_, b), cid in vi_tri.items():
        if b == buoi and cid:
            dem[cid] = dem.get(cid, 0) + 1
    ra = {}
    for cid in sorted(clb_cua_buoi):
        con = (suc_chua.get(cid) or 0) - dem.get(cid, 0) - dang_moi.get(cid, 0)
        if con > 0:
            ra[cid] = con
    return ra


def chay_vong_2(thu_tu, chon: dict, con_lai: dict) -> list:
    """Vòng 2, MỘT lượt (độc tài tuần tự): theo `thu_tu` (thứ tự bốc thăm của buổi), mỗi em lấy CLB đầu tiên trong
    `chon[em]` còn chỗ. Em không có lựa chọn dùng được thì bỏ qua. Trả [(em, club_id)]. Không sửa đầu vào."""
    con = dict(con_lai)
    ra = []
    for sid in thu_tu:
        for cid in chon.get(sid) or []:
            if con.get(cid, 0) > 0:
                con[cid] -= 1
                ra.append((sid, cid))
                break
    return ra


# GAP-5 / GAP-6 -------------------------------------------------------------------------------------------------------
KHO_NHAT = ("chon_clb", "xep_thu_tu", "huy_chuong", "thu_thach", "khong_co")
COT_PHAN_HOI = ("id", "created_at", "student_id", "nguon", "loai", "hai_long", "hieu_ly_do", "kho_nhat", "con_di",
                "muon_doi")
# Mã câu hỏi trong mẫu Forms (`mau_forms_thi_clb/bieu_mau.py` dựng tiêu đề "[mã] …"; lựa chọn kết thúc "(mã)").
MA_CAU_PHAN_HOI = {"hai_long": "ket_qua", "hieu_ly_do": "ket_qua", "kho_nhat": "ket_qua",
                   "con_di": "tuan_3", "muon_doi": "tuan_3"}
_MA_CAU = re.compile(r"^\s*(?:\d+[.)]\s*)?\[([^\]]+)\]")
_MA_LUA_CHON = re.compile(r"\(([A-Za-z0-9_]+)\)\s*$")
# Miền hợp lệ của từng câu; mã ngoài miền (tệp bị sửa tay) đọc thành None, không ghi số sai.
MIEN_PHAN_HOI = {"hai_long": {1, 2, 3, 4, 5}, "hieu_ly_do": {0, 1}, "con_di": {0, 1}, "muon_doi": {0, 1},
                 "kho_nhat": set(KHO_NHAT)}


def _ty_le(ds):
    ds = [x for x in ds if x is not None]
    return (sum(ds) / len(ds)) if ds else None


def tong_hop_phan_hoi(rows, loai: str) -> dict:
    """Tổng hợp phản hồi loại `loai` ("ket_qua" | "tuan_3"): lần trả lời SAU CÙNG (id lớn nhất) của mỗi em. Không có
    mã học sinh trong kết quả. Rỗng -> n 0, các tỉ lệ None. Hàm thuần."""
    cuoi = {}
    for r in sorted(rows, key=lambda x: x["id"]):
        if r["loai"] == loai:
            cuoi[r["student_id"]] = r
    ds = list(cuoi.values())
    hl = [r["hai_long"] for r in ds if r["hai_long"] is not None]
    return {
        "n": len(ds),
        "hai_long_tb": (sum(hl) / len(hl)) if hl else None,
        "hai_long_dem": {k: sum(1 for x in hl if x == k) for k in range(1, 6)},
        "hieu_ly_do_ty_le": _ty_le([r["hieu_ly_do"] for r in ds]),
        "kho_nhat_dem": {k: sum(1 for r in ds if r["kho_nhat"] == k) for k in KHO_NHAT},
        "con_di_ty_le": _ty_le([r["con_di"] for r in ds]),
        "muon_doi_ty_le": _ty_le([r["muon_doi"] for r in ds]),
    }


def khop_ma_hoc_sinh(ma_go, tat_ca_ma):
    """FG-5: mã học sinh gõ trong Forms -> mã đã lưu. Khớp đúng thắng; không thì khớp `strip().casefold()` nếu đúng MỘT
    học sinh khớp; còn lại None (không có / mơ hồ). Mã đã lưu không bao giờ bị đổi. Hàm thuần."""
    ma_go = "" if ma_go is None else str(ma_go)
    tat_ca_ma = list(tat_ca_ma)
    if ma_go in tat_ca_ma:
        return ma_go
    khoa = ma_go.strip().casefold()
    if not khoa:
        return None
    ung = [m for m in tat_ca_ma if str(m).strip().casefold() == khoa]
    return ung[0] if len(ung) == 1 else None


class ThieuBanDo(ValueError):
    """SG-12: tệp có tiêu đề / lựa chọn THUẦN (không "[mã]") mà không có bản đồ để đọc chúng (không có đề của đợt và
    không có tệp MAP_*.json). Không đoán: dừng để báo."""


# Cột hệ thống của Forms (không phải câu hỏi của mẫu): không báo là "cột lạ".
_COT_HE_THONG_FORMS = {"id", "start time", "completion time", "last modified time", "email", "name", "total points",
                       "quiz feedback", "thời gian bắt đầu", "thời gian hoàn thành"}


def ban_do_tinh():
    """Bản đồ của các câu KHÔNG phụ thuộc đề (mã học sinh, phản hồi, tuần 3, `[co_sai]`, `[kn_ghi_chu]`) — đọc được tiêu đề
    thuần của biểu mẫu phản hồi mà không cần `de_thi.json`. Nạp `bieu_mau` muộn (cùng cách `forms_dot.nap_mau_forms`)."""
    import forms_dot
    forms_dot.nap_mau_forms()
    import bieu_mau
    return bieu_mau.ban_do_chung(None)


def _khoa(chu):
    return " ".join(str(chu or "").split())


def _ma_cua_cot(o, ban_do):
    """Tiêu đề cột -> (mã câu, có thẻ không). Thẻ "[mã]" (tệp cũ) trước, rồi khớp CHÍNH XÁC chữ thuần qua bản đồ."""
    chu = str(o or "")
    m = _MA_CAU.match(chu)
    if m:
        return m.group(1).strip(), True
    cau = ban_do.get("cau") or {}
    ma = cau.get(_khoa(chu)) or cau.get(_khoa(re.sub(r"^\s*\d+[.)]\s*", "", chu, count=1)))
    return ma, False


def _ma_lua_chon(ma_cau, v, ban_do):
    """Ô lựa chọn -> giá trị mã: chữ thuần khớp bản đồ của câu đó trước (tệp mới), rồi "(mã)" cuối chữ (tệp cũ)."""
    gt = (ban_do.get("lua_chon") or {}).get(ma_cau, {}).get(_khoa(v))
    if gt is not None:
        return gt
    m = _MA_LUA_CHON.search(str(v).strip())
    return m.group(1) if m else None


def doc_tep_forms_phan_hoi(hang, ban_do=None, cot_la=None) -> list:
    """Các dòng của tệp xuất Forms (hàng 1 = tiêu đề) -> [{student_id, loai, hai_long, ...}]. Cột nhận theo MÃ trong
    "[mã]" của tiêu đề (tệp cũ) hoặc theo chữ thuần của tiêu đề qua `ban_do` (SG-12; mặc định `ban_do_tinh()`); giá trị
    theo "(mã)" cuối lựa chọn hoặc chữ thuần của lựa chọn. Dòng thiếu mã học sinh bị bỏ. Không có cột câu hỏi nào
    của mẫu -> ValueError. `cot_la` (danh sách, tuỳ chọn): nhận các tiêu đề không phải cột hệ thống mà không nhận ra."""
    hang = list(hang)
    if not hang:
        raise ValueError("tep rong")
    if ban_do is None:
        ban_do = ban_do_tinh()
    cot = {}
    for i, o in enumerate(hang[0]):
        ma, _co_the = _ma_cua_cot(o, ban_do)
        if ma:
            cot[ma] = i
        elif cot_la is not None and str(o or "").strip() and str(o).strip().lower() not in _COT_HE_THONG_FORMS:
            cot_la.append(str(o).strip())
    loai_co = {MA_CAU_PHAN_HOI[m] for m in cot if m in MA_CAU_PHAN_HOI}
    if "student_id" not in cot or not loai_co:
        raise ValueError("khong co cot cau hoi phan hoi")

    def lay(d, ma):
        if ma not in cot or cot[ma] >= len(d) or d[cot[ma]] in (None, ""):
            return None
        return _ma_lua_chon(ma, d[cot[ma]], ban_do)

    ra = []
    for d in hang[1:]:
        sid = str(d[cot["student_id"]] or "").strip() if cot["student_id"] < len(d) else ""
        if not sid:
            continue
        for loai in sorted(loai_co):
            dong = {"student_id": sid, "loai": loai, "hai_long": None, "hieu_ly_do": None, "kho_nhat": None,
                    "con_di": None, "muon_doi": None}
            for ma, l in MA_CAU_PHAN_HOI.items():
                if l == loai:
                    v = lay(d, ma)
                    if ma != "kho_nhat":
                        v = int(v) if v is not None and v.isdigit() else None
                    dong[ma] = v if v in MIEN_PHAN_HOI[ma] else None
            ra.append(dong)
    return ra


# FA-M6b ---------------------------------------------------------------------------------------------------------------
# Biểu mẫu gộp "Sau khi xem kết quả": phần phản hồi đọc bằng `doc_tep_forms_phan_hoi` (cột thừa bị bỏ qua), phần khiếu nại
# đọc bằng hàm dưới đây. Lý do bỏ dòng là MÃ (không phải câu chữ) để kiosk dịch ở một nơi.
LY_DO_BO_QUA_THIEU_MA = "thieu_ma_hoc_sinh"
LY_DO_BO_QUA_BUOI_LA = "buoi_la"
LY_DO_BO_QUA_KHONG_CO_BUOI = "khong_co_buoi"
_TEN_COT_GIO_XONG = ("completion time", "thời gian hoàn thành")
_TEN_COT_GIO_BAT_DAU = ("start time", "thời gian bắt đầu")


def _doc_gio_forms(v):
    """Ô giờ của tệp xuất Forms -> datetime, hoặc None nếu trống / không đọc được (không đoán định dạng ngày/tháng)."""
    if isinstance(v, datetime.datetime):
        return v.replace(microsecond=0, tzinfo=None)
    if isinstance(v, str) and v.strip():
        try:
            return _doc_gio(v.strip())
        except ValueError:
            return None
    return None


def doc_tep_forms_khieu_nai(hang, ma_buoi_hop_le, ban_do=None) -> tuple:
    """Các dòng của tệp xuất biểu mẫu gộp (hàng 1 = tiêu đề) -> (yeu_cau, bo_qua). Hàm thuần.

    Cột nhận theo MÃ "[mã]" của tiêu đề, giá trị theo "(mã)" cuối lựa chọn; ô hộp chọn nhiều = các lựa chọn cách nhau ";".
    Chỉ dòng có `[co_sai]` = 1. Mỗi (học sinh, buổi) một yêu cầu `{student_id, buoi, ghi_chu, luc}`; `luc` là giờ hoàn thành
    của Forms (cột "Completion time" / "Thời gian hoàn thành"; thiếu thì dùng "Start time") hoặc None. Mã buổi lạ, danh
    sách buổi rỗng, thiếu mã học sinh -> `bo_qua` = (số dòng trong tệp, mã học sinh, mã lý do). Không có cột `[co_sai]`
    (hoặc mã học sinh) -> ValueError.

    SG-12: tiêu đề thuần đọc qua `ban_do` (mặc định `ban_do_tinh()`). Lựa chọn buổi của `[kn_buoi]` ghi bằng chữ thuần
    ("Thứ Hai") chỉ đọc được khi `ban_do` có lựa chọn của câu đó (dựng từ đề của đợt): thiếu mà gặp ô như vậy thì ném
    `ThieuBanDo` (ô còn mã "(thu_2)" của tệp cũ vẫn đọc được không cần bản đồ)."""
    hang = list(hang)
    if not hang:
        raise ValueError("tep rong")
    if ban_do is None:
        ban_do = ban_do_tinh()
    cot, gio_xong, gio_dau = {}, None, None
    cot_the = {}
    for i, o in enumerate(hang[0]):
        ma, co_the = _ma_cua_cot(o, ban_do)
        if ma:
            cot[ma] = i
            cot_the[ma] = co_the
            continue
        ten = str(o or "").strip().lower()
        if ten in _TEN_COT_GIO_XONG and gio_xong is None:
            gio_xong = i
        elif ten in _TEN_COT_GIO_BAT_DAU and gio_dau is None:
            gio_dau = i
    if "co_sai" not in cot or "student_id" not in cot:
        raise ValueError("khong co cot co_sai")
    thieu_ban_do = ("kn_buoi" in cot and not cot_the["kn_buoi"]
                    and not (ban_do.get("lua_chon") or {}).get("kn_buoi"))
    hop_le = set(ma_buoi_hop_le)

    def o_(d, i):
        return d[i] if i is not None and i < len(d) else None

    def ma_lua_chon(v, ma_cau=None):
        if v in (None, ""):
            return None
        if ma_cau:
            return _ma_lua_chon(ma_cau, v, ban_do)
        m = _MA_LUA_CHON.search(str(v).strip())
        return m.group(1) if m else None

    yeu_cau, bo_qua = [], []
    for so_dong, d in enumerate(hang[1:], 2):
        d = list(d)
        if ma_lua_chon(o_(d, cot["co_sai"]), "co_sai") != "1":
            continue
        sid = str(o_(d, cot["student_id"]) or "").strip()
        if not sid:
            bo_qua.append((so_dong, "", LY_DO_BO_QUA_THIEU_MA))
            continue
        cac = [x for x in str(o_(d, cot.get("kn_buoi")) or "").split(";") if x.strip()]
        if not cac:
            bo_qua.append((so_dong, sid, LY_DO_BO_QUA_KHONG_CO_BUOI))
            continue
        ghi_chu = str(o_(d, cot.get("kn_ghi_chu")) or "").strip()
        luc = _doc_gio_forms(o_(d, gio_xong)) or _doc_gio_forms(o_(d, gio_dau))
        da = set()
        for x in cac:
            buoi = ma_lua_chon(x, "kn_buoi")
            if buoi is None and thieu_ban_do:         # chữ thuần mà không có bản đồ: không đoán, dừng
                raise ThieuBanDo("kn_buoi")
            if buoi not in hop_le:
                bo_qua.append((so_dong, sid, LY_DO_BO_QUA_BUOI_LA))
            elif buoi not in da:
                da.add(buoi)
                yeu_cau.append({"student_id": sid, "buoi": buoi, "ghi_chu": ghi_chu, "luc": luc})
    return yeu_cau, bo_qua


# GAP-8 ---------------------------------------------------------------------------------------------------------------
# Bảng điều khiển quản trị (V§11). CHỈ ĐỌC; mọi chỉ số là số liệu báo cáo, không bao giờ vào khoá ưu tiên (bất biến 2).
# `gia_tri` None = chưa có dữ liệu (không bao giờ thay bằng 0). `muc_tieu` là mã (nhãn trong MUC_TIEU_DASHBOARD / i18n).
LY_DO_SO_SANH = ("RESERVED", "SCORE", "MEDAL", "LOTTERY")
MUC_TIEU_DASHBOARD = {
    "bang_0": "0", "tang_so_ky_truoc": "Tăng so với kỳ trước", "theo_doi_giam": "Theo dõi; mục tiêu giảm",
    "theo_doi": "Theo dõi", "it_nhat_50": "≥ 50 %", "tren_90": "> 90 %", "duoi_1_5": "< 1,5 điểm",
    "tren_85": "> 85 %", "it_nhat_3_5": "≥ 3,5/5", "theo_doi_tang_manh": "Theo dõi (tăng mạnh → xem lại cơ chế)",
}
TEN_CHI_SO_DASHBOARD = {
    "khong_co_clb": "Học sinh không có CLB", "ty_le_nv1": "Vào NV1", "ty_le_top2": "Vào 1 trong 2 NV đầu",
    "ty_le_boc_tham": "Tỷ lệ quyết định bằng bốc thăm", "thua_boc_tham_1_lan": "Học sinh từng thua bốc thăm ≥ 1 lần",
    "ty_le_dang_ky_3_ngay": "Tỷ lệ đăng ký sau 3 ngày", "ty_le_thu_thach_nghiem_tuc": "Làm thử thách nghiêm túc",
    "do_lech_cham": "Độ lệch 2 người chấm", "ty_le_di_du_3_buoi": "Đi đủ 3 buổi đầu",
    "hai_long_tb": "Hài lòng trung bình", "ty_le_hieu_ly_do": "Hiểu lý do kết quả",
    "ty_le_doi_huy_chuong": "Tỷ lệ đổi huy chương khỏi mặc định",
}


def huy_chuong_mac_dinh(nguyen_vong, clubs: dict) -> dict:
    """D2: {club_id: 60|30|10} cho ba CLB KHÔNG Tự do đầu tiên MỖI buổi theo thứ tự nguyện vọng. Chỉ để ĐO tỉ lệ đổi
    (GAP-8, báo cáo), không bao giờ là khoá ưu tiên."""
    ra, dem = {}, {}
    for cid in dict.fromkeys(nguyen_vong or []):
        c = clubs.get(cid)
        if not c or c.get("loai") == "TU_DO":
            continue
        k = dem.get(c.get("buoi"), 0)
        if k < 3:
            ra[cid] = (60, 30, 10)[k]
            dem[c.get("buoi")] = k + 1
    return ra


def chi_so_dashboard(du) -> list:
    """`du` (xem `doc_du_lieu_dashboard`) -> [{ma, gia_tri, muc_tieu, dat, nguon}] theo thứ tự V§11. Hàm thuần."""
    def chi_so(ma, gia_tri, muc_tieu, nguon, dat=None):
        return {"ma": ma, "gia_tri": gia_tri, "muc_tieu": muc_tieu, "dat": None if gia_tri is None else dat,
                "nguon": nguon}

    khong = len({sid for (sid, _), cid in du["vi_tri"].items() if cid is None}) if du["vi_tri"] else None
    co_cho = [r for r in du["ket_qua"] if r["club_id"]]
    nv1 = _ty_le([1 if r["rank"] == 1 else 0 for r in co_cho])
    top2 = _ty_le([1 if r["rank"] is not None and r["rank"] <= 2 else 0 for r in co_cho])
    thua = [r for r in du["ly_do"] if r["outcome"] == "REJECTED" and r["reason"] in LY_DO_SO_SANH]
    boc = _ty_le([1 if r["reason"] == "LOTTERY" else 0 for r in thua])
    thua_boc = len({r["student_id"] for r in thua if r["reason"] == "LOTTERY"}) if du["ket_qua"] else None
    dd: dict = {}
    for r in du["diem_danh"]:
        dd.setdefault((r["club_id"], r["student_id"], r["buoi"]), {})[r["buoi_so"]] = r["trang_thai"]
    du_3 = [all(v == "CO_MAT" for v in m.values()) for m in dd.values() if len(m) == 3]
    di_du = _ty_le([1 if x else 0 for x in du_3])
    ph = tong_hop_phan_hoi(du["phan_hoi"], "ket_qua")
    co_hc = [sid for sid, hc in du["huy_chuong"].items() if hc]
    doi = _ty_le([1 if du["huy_chuong"][sid] != huy_chuong_mac_dinh(du["nguyen_vong"].get(sid), du["clubs"]) else 0
                  for sid in sorted(co_hc)])
    return [
        chi_so("khong_co_clb", khong, "bang_0", "vi_tri", khong == 0),
        chi_so("ty_le_nv1", nv1, "tang_so_ky_truoc", "match_results"),
        chi_so("ty_le_top2", top2, "tang_so_ky_truoc", "match_results"),
        chi_so("ty_le_boc_tham", boc, "theo_doi_giam", "fa_ly_do"),
        chi_so("thua_boc_tham_1_lan", thua_boc, "theo_doi", "fa_ly_do"),
        chi_so("ty_le_dang_ky_3_ngay", None, "it_nhat_50", "ngoai_kiosk"),
        chi_so("ty_le_thu_thach_nghiem_tuc", None, "tren_90", "ngoai_kiosk"),
        chi_so("do_lech_cham", None, "duoi_1_5", "ngoai_kiosk"),
        chi_so("ty_le_di_du_3_buoi", di_du, "tren_85", "fa_diem_danh", di_du is not None and di_du > 0.85),
        chi_so("hai_long_tb", ph["hai_long_tb"], "it_nhat_3_5", "fa_phan_hoi",
               ph["hai_long_tb"] is not None and ph["hai_long_tb"] >= 3.5),
        chi_so("ty_le_hieu_ly_do", ph["hieu_ly_do_ty_le"], "theo_doi", "fa_phan_hoi"),
        chi_so("ty_le_doi_huy_chuong", doi, "theo_doi_tang_manh", "wharton_bids"),
    ]


def doc_du_lieu_dashboard(cur) -> dict:
    """Đọc mọi nguồn cho `chi_so_dashboard`. Lý do và điểm danh chỉ của LẦN CHẠY GỐC mới nhất mỗi buổi. Chỉ SELECT."""
    vi_tri, _, run_goc = doc_vi_tri(cur)
    ket_qua = [{"student_id": r[0], "buoi": r[1], "club_id": r[2], "rank": r[3]} for r in cur.execute(
        "SELECT student_id, buoi, club_id, rank_in_student_pref FROM match_results ORDER BY student_id, buoi")]
    ly_do = [{"student_id": r[0], "outcome": r[1], "reason": r[2]} for r in cur.execute(
        "SELECT student_id, outcome, reason, run_id, buoi FROM fa_ly_do ORDER BY run_id, buoi, student_id")
        if run_goc.get(r[4]) == r[3]]
    diem_danh = [{"club_id": r[0], "student_id": r[1], "buoi": r[2], "buoi_so": r[3], "trang_thai": r[4]}
                 for r in cur.execute("SELECT club_id, student_id, buoi, buoi_so, trang_thai, run_id_base "
                                      "FROM fa_diem_danh") if run_goc.get(r[2]) == r[5]]
    phan_hoi = [dict(zip(COT_PHAN_HOI, r)) for r in cur.execute(
        "SELECT %s FROM fa_phan_hoi ORDER BY id" % ", ".join(COT_PHAN_HOI))]
    huy_chuong: dict = {}
    for sid, cid, p in cur.execute("SELECT student_id, club_id, points FROM wharton_bids"):
        huy_chuong.setdefault(sid, {})[cid] = p
    nguyen_vong: dict = {}
    for sid, cid in cur.execute("SELECT student_id, club_id FROM preferences ORDER BY student_id, rank"):
        nguyen_vong.setdefault(sid, []).append(cid)
    clubs = {r[0]: {"buoi": r[1] or "", "loai": r[2]} for r in cur.execute("SELECT club_id, buoi, loai FROM clubs")}
    return {"vi_tri": vi_tri, "ket_qua": ket_qua, "ly_do": ly_do, "diem_danh": diem_danh, "phan_hoi": phan_hoi,
            "huy_chuong": huy_chuong, "nguyen_vong": nguyen_vong, "clubs": clubs}
