"""Sau khi xếp (FA gaps, V§9.2–9.3): nhật ký điều chỉnh, điểm danh, mời danh sách chờ.

Kết quả DA của một lần chạy (`match_results`) KHÔNG BAO GIỜ bị sửa tại chỗ, `run_history` chỉ ghi thêm (bất biến 4).
Mọi lần đổi chỗ sau khi công bố là MỘT dòng ghi thêm trong `fa_dieu_chinh`; chỗ hiện tại = kết quả lần chạy gốc của
buổi + các dòng điều chỉnh phát lại theo `id` (`vi_tri_hien_tai`, hàm thuần). Điểm danh, khiếu nại, phản hồi không bao
giờ đi vào `compute_club_priority` (bất biến 2).
"""

import datetime

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
