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


def doc_tep_forms_phan_hoi(hang) -> list:
    """Các dòng của tệp xuất Forms (hàng 1 = tiêu đề) -> [{student_id, loai, hai_long, ...}]. Cột nhận theo MÃ trong
    "[mã]" của tiêu đề; giá trị theo "(mã)" cuối lựa chọn. Dòng thiếu mã học sinh bị bỏ. Không có cột câu hỏi nào
    của mẫu -> ValueError."""
    hang = list(hang)
    if not hang:
        raise ValueError("tep rong")
    cot = {}
    for i, o in enumerate(hang[0]):
        m = _MA_CAU.match(str(o or ""))
        if m:
            cot[m.group(1).strip()] = i
    loai_co = {MA_CAU_PHAN_HOI[m] for m in cot if m in MA_CAU_PHAN_HOI}
    if "student_id" not in cot or not loai_co:
        raise ValueError("khong co cot cau hoi phan hoi")

    def lay(d, ma):
        if ma not in cot or cot[ma] >= len(d) or d[cot[ma]] in (None, ""):
            return None
        m = _MA_LUA_CHON.search(str(d[cot[ma]]).strip())
        return m.group(1) if m else None

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
                    dong[ma] = v if ma == "kho_nhat" else (int(v) if v is not None and v.isdigit() else None)
            ra.append(dong)
    return ra
