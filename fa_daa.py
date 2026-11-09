"""FA-DAA (mục A13): lớp bọc quanh thuật toán DA — KHÔNG sửa lõi `run_rbda_nhieu_buoi`.

Tầng này chỉ chạy khi `rules.fa_daa` bật (mặc định TẮT). FA-1: kiểu CLB, kiểm thuộc tính, ghi cột
mới và bảng `giu_cho`. Các bước sau (precheck, huy chương một quỹ, chạy, tối thiểu, lý do) thêm
vào cùng tệp này.

Dữ liệu trong test là dữ liệu MÔ PHỎNG.
"""

from __future__ import annotations

from i18n_errors import err
from rbda_priority_pipeline import BUOI_MAC_DINH

# Kiểu CLB và kiểm giá trị sống trong `so_nhap.py` (để skill đóng gói của so_nhap chạy một mình,
# không cần kho mã); module này nhập lại để mọi nơi dùng một tên.
from so_nhap import (  # noqa: E402,F401
    CAC_LOAI, DIEM_SAN_TOI_DA, GIOI_HAN, NHAN_LOAI_HIEN_THI, TU_DO, TUYEN_CHON,
    chuan_hoa_loai, kiem_thuoc_tinh, _la_nguyen,
)


def ghi_thuoc_tinh_clb(cur, club_id, thuoc_tinh: dict) -> None:
    """Ghi các khoá có trong `thuoc_tinh` (loai, diem_san, so_toi_thieu, suc_chua_phong) của CLB.

    Khoá VẮNG = giữ giá trị đang lưu (cột vắng mặt trong tệp nghĩa là "không biết"); khoá có giá
    trị None = xoá về NULL. Gọi trong giao dịch của người gọi.
    """
    cot = [k for k in ("loai", "diem_san", "so_toi_thieu", "suc_chua_phong") if k in thuoc_tinh]
    if not cot:
        return
    cur.execute("UPDATE clubs SET %s WHERE club_id = ?" % ", ".join(c + " = ?" for c in cot),
                [thuoc_tinh[c] for c in cot] + [club_id])


def thay_giu_cho(cur, cap: list) -> list:
    """Thay TOÀN BỘ `giu_cho` bằng `cap` [(club_id, student_id)] hợp lệ; trả các cặp bị bỏ.

    Cặp bỏ = CLB hoặc học sinh không có trong CSDL. Sổ nhập là bản đầy đủ của giữ chỗ.
    """
    co_clb = {r[0] for r in cur.execute("SELECT club_id FROM clubs")}
    co_hs = {r[0] for r in cur.execute("SELECT student_id FROM students")}
    tot, bo = [], []
    for c, s in dict.fromkeys(cap):
        (tot if c in co_clb and s in co_hs else bo).append((c, s))
    cur.execute("DELETE FROM giu_cho")
    cur.executemany("INSERT INTO giu_cho (club_id, student_id) VALUES (?, ?)", tot)
    return bo


def doc_thuoc_tinh_csv(row: dict, cot_co: list):
    """Bốn cột FA của một dòng CSV CLB -> ({khoá: giá trị|None}, tên cột sai | "").

    Chỉ đọc các cột trong `cot_co` (cột có trong tệp). Ô trống = None. Cột sai đầu tiên được
    trả về để người gọi bỏ dòng và báo; không ghi gì khi sai.
    """
    ra = {}
    for khoa in cot_co:
        tho = (row.get(khoa) or "").strip()
        if khoa == "loai":
            try:
                ra[khoa] = chuan_hoa_loai(tho)
            except ValueError:
                return {}, khoa
            continue
        if not tho:
            ra[khoa] = None
            continue
        try:
            f = float(tho)
        except ValueError:
            return {}, khoa
        ra[khoa] = int(f) if f == f and abs(f) != float("inf") and f.is_integer() else tho
    sai = kiem_thuoc_tinh(None, ra.get("diem_san"), ra.get("so_toi_thieu"),
                          ra.get("suc_chua_phong"))
    if sai:
        return {}, {"fa_diem_san_sai": "diem_san", "fa_toi_thieu_sai": "so_toi_thieu",
                    "fa_suc_chua_phong_sai": "suc_chua_phong"}[sai[0]["code"]]
    return ra, ""


# ---------------------------------------------------------------------------
# FA-2 · kiểm trước khi chạy (A5; V§4.2)
# ---------------------------------------------------------------------------
# Hai mã chỉ là CẢNH BÁO (giữ chỗ không dùng được, không tính vào số giữ chỗ); mọi mã `fa_` khác
# trong kết quả của `kiem_truoc_fa` đều CHẶN chạy.
MA_CANH_BAO = frozenset({"fa_giu_cho_hoc_sinh_la", "fa_giu_cho_khong_xep_clb"})


def chi_loi_chan(loi: list) -> list:
    """Bỏ các cảnh báo (`MA_CANH_BAO`), giữ lỗi chặn."""
    return [e for e in loi if e["code"] not in MA_CANH_BAO]


def giu_cho_hop_le(clubs: dict, giu_cho, students: dict, preferences=None) -> set:
    """Các cặp (club_id, student_id) giữ chỗ DÙNG ĐƯỢC: CLB và học sinh có thật, và (khi biết
    `preferences`) em xếp CLB đó trong nguyện vọng. Cặp khác không được tính (D6)."""
    ra = set()
    for c, s in giu_cho:
        if c not in clubs or s not in students:
            continue
        if preferences is not None and c not in (preferences.get(s) or []):
            continue
        ra.add((c, s))
    return ra


def kiem_truoc_fa(clubs: dict, giu_cho, students: dict, preferences=None) -> list:
    """Kiểm dữ liệu FA trước khi chạy; trả danh sách `err(...)` (rỗng = hợp lệ).

    `clubs` {club_id: {buoi, capacity, loai, diem_san, ...}}, `giu_cho` [(club_id, student_id)],
    `students` {student_id: ...}; `preferences` {student_id: [club_id]} (không có thì bỏ kiểm
    "em xếp CLB đó"). Lỗi CHẶN: mỗi buổi cần ít nhất một CLB TU_DO; mọi CLB có `loai`;
    GIOI_HAN / TUYEN_CHON có sức chứa > 0; TUYEN_CHON có điểm sàn; số giữ chỗ dùng được của một
    CLB không quá sức chứa. CẢNH BÁO (`MA_CANH_BAO`): giữ chỗ cho học sinh không có, hoặc em
    không xếp CLB đó — không tính vào số giữ chỗ. Thứ tự lỗi cố định, không phụ thuộc thứ tự dict.
    """
    loi = []
    cac_buoi = sorted({c.get("buoi") or BUOI_MAC_DINH for c in clubs.values()})
    co_tu_do = {c.get("buoi") or BUOI_MAC_DINH for c in clubs.values() if c.get("loai") == TU_DO}
    loi += [err("fa_thieu_clb_tu_do", buoi=b) for b in cac_buoi if b not in co_tu_do]
    for cid in sorted(clubs, key=str):
        c = clubs[cid]
        loai = c.get("loai")
        if loai is None:
            loi.append(err("fa_clb_thieu_loai", club_id=cid))
            continue
        if loai in (GIOI_HAN, TUYEN_CHON):
            cho = c.get("capacity")
            if not (_la_nguyen(cho) and cho > 0):
                loi.append(err("fa_clb_thieu_suc_chua", club_id=cid))
        if loai == TUYEN_CHON and c.get("diem_san") is None:
            loi.append(err("fa_clb_thieu_diem_san", club_id=cid))
    cap = sorted(set(giu_cho), key=lambda p: (str(p[0]), str(p[1])))
    dung_duoc = giu_cho_hop_le(clubs, cap, students, preferences)
    for c, s in cap:
        if c not in clubs:
            continue
        if s not in students:
            loi.append(err("fa_giu_cho_hoc_sinh_la", club_id=c, student_id=s))
        elif (c, s) not in dung_duoc:
            loi.append(err("fa_giu_cho_khong_xep_clb", club_id=c, student_id=s))
    dem: dict = {}
    for c, _ in dung_duoc:
        dem[c] = dem.get(c, 0) + 1
    for cid in sorted(dem, key=str):
        cho = clubs[cid].get("capacity")
        if _la_nguyen(cho) and dem[cid] > cho:
            loi.append(err("fa_giu_cho_vuot_suc_chua", club_id=cid, n=dem[cid], suc_chua=cho))
    return loi


def doc_du_lieu_fa(cur):
    """Đọc dữ liệu FA từ CSDL -> ({club_id: {loai, diem_san, so_toi_thieu, suc_chua_phong}},
    [(club_id, student_id)], {student_id: {club_id: huy_chuong}}).

    Huy chuong = `wharton_bids.points` của chế độ FA (một quỹ; cột `tier` bị bỏ qua)."""
    fa_clb = {r[0]: {"loai": r[1], "diem_san": r[2], "so_toi_thieu": r[3], "suc_chua_phong": r[4]}
              for r in cur.execute("SELECT club_id, loai, diem_san, so_toi_thieu, suc_chua_phong "
                                   "FROM clubs ORDER BY club_id")}
    cap = [(r[0], r[1]) for r in cur.execute(
        "SELECT club_id, student_id FROM giu_cho ORDER BY club_id, student_id")]
    huy = {}
    for sid, cid, diem in cur.execute(
            "SELECT student_id, club_id, points FROM wharton_bids ORDER BY student_id, club_id"):
        huy.setdefault(sid, {})[cid] = diem
    return fa_clb, cap, huy


def doc_clubs_va_nguyen_vong(cur):
    """({club_id: {buoi, capacity, loai, diem_san, so_toi_thieu, suc_chua_phong}}, {student_id: {}},
    {student_id: [club_id theo thứ hạng]}) đọc thẳng từ CSDL cho các hàm kiểm FA."""
    fa_clb, _, _ = doc_du_lieu_fa(cur)
    clubs = {r[0]: {"capacity": r[1], "buoi": r[2] or BUOI_MAC_DINH, **fa_clb[r[0]]}
             for r in cur.execute("SELECT club_id, capacity, buoi FROM clubs ORDER BY club_id")}
    students = {r[0]: {} for r in cur.execute("SELECT student_id FROM students ORDER BY student_id")}
    prefs: dict = {}
    for sid, cid in cur.execute("SELECT student_id, club_id FROM preferences "
                                "ORDER BY student_id, rank, club_id"):
        prefs.setdefault(sid, []).append(cid)
    return clubs, students, prefs


def kiem_fa_tu_csdl(cur) -> list:
    """Mọi kiểm FA trên dữ liệu đang lưu (lỗi chặn lẫn cảnh báo, phân biệt bằng `MA_CANH_BAO`).

    Dùng chung cho lần chạy xếp (bước kiểm dữ liệu) và báo cáo sức khoẻ dữ liệu: cùng số, cùng em."""
    clubs, students, prefs = doc_clubs_va_nguyen_vong(cur)
    _, cap, _ = doc_du_lieu_fa(cur)
    return kiem_truoc_fa(clubs, cap, students, prefs)
