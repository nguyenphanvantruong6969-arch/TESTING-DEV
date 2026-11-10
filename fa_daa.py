"""FA-DAA (mục A13): lớp bọc quanh thuật toán DA — KHÔNG sửa lõi `run_rbda_nhieu_buoi`.

Tầng này chỉ chạy khi `rules.fa_daa` bật (mặc định TẮT). FA-1: kiểu CLB, kiểm thuộc tính, ghi cột
mới và bảng `giu_cho`. Các bước sau (precheck, huy chương một quỹ, chạy, tối thiểu, lý do) thêm
vào cùng tệp này.

Dữ liệu trong test là dữ liệu MÔ PHỎNG.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable

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
    _, cap, huy = doc_du_lieu_fa(cur)
    return kiem_truoc_fa(clubs, cap, students, prefs) + kiem_ho_so_huy_chuong(prefs, huy, clubs)


# ---------------------------------------------------------------------------
# FA-3 · huy chương, MỘT quỹ (A13; V§6)
# ---------------------------------------------------------------------------
GIA_TRI_HUY_CHUONG = (60, 30, 10)        # vàng, bạc, đồng


def kiem_ho_so_huy_chuong(preferences: dict, bids: dict, clubs: dict) -> list:
    """Kiểm huy chương của mọi học sinh; trả TẤT CẢ lỗi, rỗng = hợp lệ (V§13.8).

    `preferences` {student_id: [club_id]} (mọi buổi), `bids` {student_id: {club_id: điểm}},
    `clubs` {club_id: {buoi, loai, ...}}. Mỗi học sinh, mỗi buổi: giá trị chỉ là 60, 30 hoặc 10 (số
    nguyên thật, không `bool` / `float` / chuỗi), mỗi giá trị tối đa MỘT lần (nên tối đa 3 huy
    chương mỗi buổi); mỗi CLB tối đa một huy chương (khoá `bids[sid]` là club_id); CLB phải nằm
    trong nguyện vọng của em và không phải TU_DO. Ít hơn 3 huy chương là hợp lệ (V§6.1).

    Mỗi ô có tối đa một lỗi. Thứ tự lỗi cố định: học sinh theo mã; trong em, từng CLB theo mã
    (lỗi từng ô), rồi các giá trị trùng theo (buổi, giá trị). Hàm KHÔNG đọc thứ hạng nguyện vọng.
    """
    loi = []
    for sid in sorted(set(preferences) | set(bids), key=str):
        thich = set(preferences.get(sid) or [])
        theo_buoi: dict = {}                     # (buoi, giá trị) -> số CLB hợp lệ
        for cid in sorted(bids.get(sid) or {}, key=str):
            v = bids[sid][cid]
            if cid not in thich or cid not in clubs:
                loi.append(err("fa_huy_chuong_ngoai_nguyen_vong", student_id=sid, club_id=cid))
            elif clubs[cid].get("loai") == TU_DO:
                loi.append(err("fa_huy_chuong_clb_tu_do", student_id=sid, club_id=cid))
            elif type(v) is not int or v not in GIA_TRI_HUY_CHUONG:
                loi.append(err("fa_huy_chuong_gia_tri_sai", student_id=sid, club_id=cid,
                               gia_tri=repr(v)))
            else:
                k = (clubs[cid].get("buoi") or BUOI_MAC_DINH, v)
                theo_buoi[k] = theo_buoi.get(k, 0) + 1
        for (buoi, v), n in sorted(theo_buoi.items(), key=lambda kv: (str(kv[0][0]), -kv[0][1])):
            if n > 1:
                loi.append(err("fa_huy_chuong_trung_gia_tri", student_id=sid, buoi=buoi,
                               gia_tri=v))
    return loi


def diem_huy_chuong_hieu_luc(preferences: dict, bids: dict) -> dict:
    """Điểm huy chương hiệu lực {club_id: {student_id: điểm}} cho `diem_wharton` của
    `run_rbda_nhieu_buoi`: MỘT quỹ (bỏ qua `tier`), 0 cho CLB trong nguyện vọng mà em chưa đặt
    huy chương. Mỗi cặp (học sinh, CLB trong nguyện vọng) có một mục. Chỉ đọc TẬP CLB của em,
    không đọc thứ hạng: hoán vị danh sách nguyện vọng không đổi kết quả (bất biến 2).

    Dùng với `rbda_priority_pipeline.uu_tien_wharton`: CLB TUYEN_CHON → khoá
    `(0, -điểm thi, (), -huy chương, stb, sid)` (em có điểm thi), GIOI_HAN → `(1, -huy chương,
    stb, sid)`; đúng V§8.2 khi chưa có ưu tiên bù (D1)."""
    ra: dict = {}
    for sid in sorted(preferences, key=str):
        cua_em = bids.get(sid) or {}
        for cid in sorted(set(preferences[sid] or []), key=str):
            ra.setdefault(cid, {})[sid] = cua_em.get(cid, 0)
    return ra


# ---------------------------------------------------------------------------
# FA-4 · lớp bọc chạy FA-DAA (A13 + A5; V§8.2, V§8.6, V§8.7)
# ---------------------------------------------------------------------------
@dataclass
class KetQuaFA:
    """Kết quả `chay_fa_daa`: kết quả DA cùng ĐẦU VÀO ĐÃ CHUẨN BỊ (trong bộ nhớ) mà nó đã chạy trên.

    `sanity_check_result` / `verify_stability` phải chạy trên chính các đầu vào này (danh sách nguyện
    vọng đã lọc / tăng cường), KHÔNG phải dữ liệu gốc; không bao giờ ghi chúng vào `preferences`.
    """

    ket_qua: object                                   # KetQuaTuan
    clubs: dict
    tested_scores: dict
    applicants: dict
    preferences: dict
    reserve_fn: Callable
    loai_bo: list = field(default_factory=list)       # [{student_id, club_id, buoi, ly_do}]
    canh_bao: list = field(default_factory=list)      # [err(...)]
    fallback: list = field(default_factory=list)      # [{student_id, buoi, club_id}]
    nhom: list = field(default_factory=list)          # [{buoi, student_id, club_id, group_no}]
    dong_cua: list = field(default_factory=list)      # FA-5: [{club_id, buoi, thieu, thanh_vien, lan}]


def chay_fa_daa(students: dict, clubs: dict, tested_scores: dict, applicants: dict,
                preferences: dict, stb_lottery: dict, fa_clb: dict, giu_cho, huy_chuong: dict,
                seed: int = 0, chi_buoi=None, tier_rank=None, bo_qua_du_tru: bool = False,
                max_rounds: int = 1000, buoc_fallback: bool = True) -> KetQuaFA:
    """Chạy FA-DAA: chuẩn bị đầu vào trong bộ nhớ, gọi `run_rbda_nhieu_buoi` (lõi KHÔNG đổi), rồi
    xử lý sau. Không sửa đối số nào.

    Trước khi chạy: (1) CLB TU_DO có chỉ tiêu bộ nhớ = số học sinh, suất dự trữ 0; (2) TUYEN_CHON:
    bỏ CLB khỏi danh sách em không có điểm (`NOT_ATTEMPTED`) hoặc điểm < điểm sàn (`BELOW_PASS`),
    ghi lại từng lần bỏ; (3) GIOI_HAN: bỏ điểm thi của CLB (cảnh báo `fa_diem_bo_qua`); (4) giữ chỗ
    (D6): suất dự trữ = số em giữ chỗ dùng được, đủ điều kiện = có trong `giu_cho`.
    Sau lượt DA: (5) dự phòng (D10): em chưa có CLB ở một buổi, theo thứ tự STB của buổi, vào CLB
    TU_DO ít người nhất (hoà: club_id nhỏ) bằng cách THÊM CLB đó vào CUỐI danh sách trong bộ nhớ rồi
    chạy DA lại — TU_DO không bao giờ từ chối nên không ai khác bị xê dịch; (6) chia nhóm phòng cho
    CLB TU_DO có `suc_chua_phong`: n = ceil(m / sức chứa), thành viên theo STB, nhóm = i % n + 1.

    `buoc_fallback=False` chỉ để đo/kiểm (tắt bước 5). `fa_clb` {club_id: {loai, diem_san, ...}},
    `giu_cho` [(club_id, student_id)], `huy_chuong` {student_id: {club_id: 60|30|10}}.
    """
    import rbda_priority_pipeline as rp

    def loai(cid):
        return (fa_clb.get(cid) or {}).get("loai")

    n_hs = len(students)
    clubs_fa = {}
    for cid, c in clubs.items():
        c2 = dict(c)
        c2["reserve_capacity"] = 0                     # FA không dùng nhãn dự trữ cũ (D6)
        if loai(cid) == TU_DO:
            c2["capacity"] = max(1, n_hs)
        clubs_fa[cid] = c2

    prefs_fa = {sid: list(preferences.get(sid) or []) for sid in students}
    app_fa = {cid: list(applicants.get(cid, [])) for cid in clubs}
    tested_fa = {cid: dict(tested_scores.get(cid, {})) for cid in clubs}
    canh_bao, loai_bo = [], []

    # (2) TUYEN_CHON: lọc theo điểm sàn
    for sid in sorted(prefs_fa, key=str):
        for cid in list(prefs_fa[sid]):
            if loai(cid) != TUYEN_CHON:
                continue
            diem = tested_fa.get(cid, {}).get(sid)
            san = (fa_clb.get(cid) or {}).get("diem_san") or 0
            ly_do = "NOT_ATTEMPTED" if diem is None else ("BELOW_PASS" if diem < san else None)
            if ly_do:
                prefs_fa[sid].remove(cid)
                if sid in app_fa.get(cid, []):
                    app_fa[cid].remove(sid)
                loai_bo.append({"student_id": sid, "club_id": cid,
                                "buoi": clubs_fa[cid].get("buoi") or BUOI_MAC_DINH,
                                "ly_do": ly_do})
    # (3) GIOI_HAN: bỏ điểm thi
    for cid in sorted(clubs, key=str):
        if loai(cid) == GIOI_HAN and tested_fa.get(cid):
            canh_bao.append(err("fa_diem_bo_qua", club_id=cid, n=len(tested_fa[cid])))
            tested_fa[cid] = {}
    # (4) giữ chỗ bằng suất dự trữ mềm
    dung_duoc = {p for p in giu_cho_hop_le(clubs_fa, giu_cho, students, prefs_fa)
                 if loai(p[0]) != TU_DO}
    dem: dict = {}
    for cid, _ in dung_duoc:
        dem[cid] = dem.get(cid, 0) + 1
    for cid, n in dem.items():
        clubs_fa[cid]["reserve_capacity"] = min(n, clubs_fa[cid]["capacity"])

    def reserve_fn(sid, cid):
        return (cid, sid) in dung_duoc

    def chay():
        return rp.run_rbda_nhieu_buoi(
            students, clubs_fa, tested_fa, app_fa, prefs_fa, stb_lottery, reserve_fn,
            seed=seed, max_rounds=max_rounds, chi_buoi=chi_buoi, tier_rank=tier_rank,
            bo_qua_du_tru=bo_qua_du_tru,
            diem_wharton=diem_huy_chuong_hieu_luc(prefs_fa, huy_chuong))

    ket = chay()
    theo_buoi = rp.nhom_theo_buoi(clubs_fa)

    # FA-5 · đóng CLB thiếu người (D3): MỖI VÒNG đóng MỘT CLB — CLB thiếu nhiều nhất
    # (`so_toi_thieu - thành viên`; hoà: ít thành viên hơn, rồi club_id), bỏ nó khỏi danh sách mọi em,
    # chạy lại với CÙNG số bốc thăm. Đóng tất cả cùng lúc có thể đóng oan một CLB sẽ đủ người sau khi
    # CLB khác đóng. Mỗi vòng đóng một CLB khác nhau nên số vòng <= số CLB (kiểm bằng assert).
    dong_cua, da_dong = [], set()
    gioi_han = [c for c in clubs_fa if loai(c) in (GIOI_HAN, TUYEN_CHON)]
    for lan in range(1, len(gioi_han) + 2):
        ung_vien = []
        for buoi in ket.ds_buoi:
            dem_tv: dict = {}
            for cid in ket.per_buoi[buoi].assignment.values():
                if cid is not None:
                    dem_tv[cid] = dem_tv.get(cid, 0) + 1
            for cid in theo_buoi[buoi]:
                toi = (fa_clb.get(cid) or {}).get("so_toi_thieu")
                if cid in da_dong or loai(cid) not in (GIOI_HAN, TUYEN_CHON) or not toi:
                    continue
                tv = dem_tv.get(cid, 0)
                if tv < toi:
                    ung_vien.append((toi - tv, tv, str(cid), cid, buoi))
        if not ung_vien:
            break
        thieu, tv, _, cid, buoi = min(ung_vien, key=lambda x: (-x[0], x[1], x[2]))
        assert cid not in da_dong
        da_dong.add(cid)
        dong_cua.append({"club_id": cid, "buoi": buoi, "thieu": thieu, "thanh_vien": tv,
                         "lan": lan})
        canh_bao.append(err("fa_clb_dong_thieu_nguoi", club_id=cid, buoi=buoi, thieu=thieu,
                            thanh_vien=tv))
        for sid in sorted(prefs_fa, key=str):
            if cid in prefs_fa[sid]:
                prefs_fa[sid].remove(cid)
                loai_bo.append({"student_id": sid, "club_id": cid, "buoi": buoi,
                                "ly_do": "CLUB_CLOSED"})
        app_fa[cid] = []
        ket = chay()
    else:
        raise AssertionError("FA-5: vong dong CLB thieu nguoi khong hoi tu")

    # (5) phương án dự phòng
    fallback = []
    if buoc_fallback:
        for buoi in ket.ds_buoi:
            tu_do = sorted((c for c in theo_buoi[buoi] if loai(c) == TU_DO), key=str)
            if not tu_do:
                continue
            thanh_vien = {c: 0 for c in tu_do}
            for cid in ket.per_buoi[buoi].assignment.values():
                if cid in thanh_vien:
                    thanh_vien[cid] += 1
            stb_b = ket.stb_theo_buoi[buoi]
            thieu = sorted((sid for sid in students if ket.assignment[sid].get(buoi) is None),
                           key=lambda sid: (stb_b[sid], str(sid)))
            for sid in thieu:
                cid = min(tu_do, key=lambda c: (thanh_vien[c], str(c)))
                thanh_vien[cid] += 1
                prefs_fa[sid].append(cid)
                if sid not in app_fa[cid]:
                    app_fa[cid].append(sid)
                fallback.append({"student_id": sid, "buoi": buoi, "club_id": cid})
        if fallback:
            ket = chay()

    # (6) chia nhóm phòng
    nhom = []
    for buoi in ket.ds_buoi:
        stb_b = ket.stb_theo_buoi[buoi]
        for cid in sorted(theo_buoi[buoi], key=str):
            phong = (fa_clb.get(cid) or {}).get("suc_chua_phong")
            if loai(cid) != TU_DO or not phong:
                continue
            tv = sorted((s for s, c in ket.per_buoi[buoi].assignment.items() if c == cid),
                        key=lambda sid: (stb_b[sid], str(sid)))
            if len(tv) <= phong:
                continue
            n = math.ceil(len(tv) / phong)
            nhom += [{"buoi": buoi, "student_id": sid, "club_id": cid, "group_no": i % n + 1}
                     for i, sid in enumerate(tv)]

    return KetQuaFA(ket_qua=ket, clubs=clubs_fa, tested_scores=tested_fa, applicants=app_fa,
                    preferences=prefs_fa, reserve_fn=reserve_fn, loai_bo=loai_bo,
                    canh_bao=canh_bao, fallback=fallback, nhom=nhom, dong_cua=dong_cua)


# ---------------------------------------------------------------------------
# FA-6 · lý do, điểm chuẩn, danh sách chờ (C3; V§8.2, V§9.1, D4)
# ---------------------------------------------------------------------------
MA_LY_DO_SO_SANH = ("RESERVED", "SCORE", "MEDAL", "LOTTERY")      # thứ tự thành phần của khoá


def ly_do_ket_qua(kq: KetQuaFA, preferences_goc: dict, huy_chuong: dict, fa_clb: dict) -> list:
    """Mỗi (học sinh, buổi): một dòng cho CLB nhận (`ACCEPTED`) hoặc dự phòng (`FALLBACK`), và một
    dòng cho MỖI CLB em xếp CAO hơn CLB cuối cùng trong danh sách GỐC (không phải danh sách tăng cường).

    Dòng bị bỏ trước khi chạy: `BELOW_PASS` / `NOT_ATTEMPTED` (FA-4) và `CLUB_CLOSED` (FA-5), outcome
    `REMOVED`. Dòng thua trong DA (`REJECTED`): so khoá của em với khoá của người nhận CUỐI CÙNG của
    CLB, theo thứ tự (giữ chỗ, điểm, huy chương, bốc thăm); thành phần khác nhau đầu tiên cho
    `RESERVED` / `SCORE` / `MEDAL` / `LOTTERY`. Khoá của em TỐT hơn người nhận cuối là lỗi ổn định:
    ném ValueError (không bao giờ im lặng). Kèm ảnh chụp: điểm chuẩn, huy chương và số bốc thăm của
    người nhận cuối; với LOTTERY còn `n_hoa` (số bạn bằng ở mọi tiêu chí trước bốc thăm) và `k_cho`
    (số chỗ trong nhóm đó). Danh sách chờ (D4): chỉ em thua ở CLB đó (đã xếp CLB đó CAO hơn CLB hiện
    tại); Tuyển chọn = điểm, huy chương, bốc thăm; Giới hạn = huy chương, bốc thăm; `waitlist_pos`
    từ 1. Dòng chỉ nói về một học sinh; không đọc thứ hạng nguyện vọng làm khoá của ai.
    """
    ket = kq.ket_qua

    def loai(cid):
        return (fa_clb.get(cid) or {}).get("loai")

    def buoi_cua(cid):
        return kq.clubs[cid].get("buoi") or BUOI_MAC_DINH

    bi_bo = {(r["student_id"], r["club_id"]): r for r in kq.loai_bo}
    rows = []
    for buoi in ket.ds_buoi:
        stb_b = ket.stb_theo_buoi[buoi]
        asg = ket.per_buoi[buoi].assignment
        thanh_vien: dict = {}
        for sid, cid in asg.items():
            if cid is not None:
                thanh_vien.setdefault(cid, []).append(sid)

        def diem(sid, cid):
            return kq.tested_scores.get(cid, {}).get(sid) if loai(cid) == TUYEN_CHON else None

        def huy(sid, cid):
            return (huy_chuong.get(sid) or {}).get(cid, 0)

        def phan(sid, cid):                       # (giữ chỗ, điểm, huy chương): lớn hơn = tốt hơn
            return (1 if kq.reserve_fn(sid, cid) else 0, diem(sid, cid) or 0, huy(sid, cid))

        def khoa(sid, cid, stb_b=stb_b):          # nhỏ hơn = tốt hơn
            g, d, h = phan(sid, cid)
            return (-g, -d, -h, stb_b[sid])

        goc_ngay, tren, da_de_nghi = {}, {}, set()
        for sid in sorted(asg, key=str):
            ds = [c for c in (preferences_goc.get(sid) or []) if c in kq.clubs
                  and buoi_cua(c) == buoi]
            goc_ngay[sid] = ds
            cuoi = asg[sid]
            tren[sid] = ds[:ds.index(cuoi)] if cuoi in ds else list(ds)
            for c in tren[sid] + ([cuoi] if cuoi in ds else []):
                if (sid, c) not in bi_bo:
                    da_de_nghi.add((sid, c))      # em đã thực sự đề nghị vào CLB c

        thua: dict = {}                           # cid -> [(sid, dong)]
        for sid in sorted(asg, key=str):
            cuoi, ds = asg[sid], goc_ngay[sid]
            if cuoi in ds:
                rows.append({"buoi": buoi, "student_id": sid, "club_id": cuoi,
                             "rank_in_list": ds.index(cuoi) + 1, "outcome": "ACCEPTED",
                             "reason": "ACCEPTED", "cut_score": None, "cut_medal": None,
                             "cut_stb": None, "waitlist_pos": None, "diem_em": diem(sid, cuoi),
                             "n_hoa": None, "k_cho": None})
            elif cuoi is not None:
                rows.append({"buoi": buoi, "student_id": sid, "club_id": cuoi,
                             "rank_in_list": None, "outcome": "FALLBACK",
                             "reason": "HET_NGUYEN_VONG" if ds else "KHONG_DANG_KY",
                             "cut_score": None, "cut_medal": None, "cut_stb": None,
                             "waitlist_pos": None, "diem_em": None, "n_hoa": None, "k_cho": None})
            for hang, cid in enumerate(ds[:len(tren[sid])], start=1):
                dong = {"buoi": buoi, "student_id": sid, "club_id": cid, "rank_in_list": hang,
                        "cut_score": None, "cut_medal": None, "cut_stb": None,
                        "waitlist_pos": None, "diem_em": diem(sid, cid), "n_hoa": None,
                        "k_cho": None}
                if (sid, cid) in bi_bo:
                    b = bi_bo[(sid, cid)]
                    dong.update(outcome="REMOVED", reason=b["ly_do"])
                    if b["ly_do"] == "BELOW_PASS":
                        dong["cut_score"] = (fa_clb.get(cid) or {}).get("diem_san")
                    rows.append(dong)
                    continue
                tv = thanh_vien.get(cid, [])
                if not tv:
                    raise ValueError("FA-6: CLB %s khong co thanh vien nhung %s bi tu choi "
                                     "(loi on dinh)" % (cid, sid))
                cuoi_nhan = max(tv, key=lambda m: khoa(m, cid))
                ks, km = khoa(sid, cid), khoa(cuoi_nhan, cid)
                if ks < km:
                    raise ValueError("FA-6: khoa cua %s tot hon nguoi nhan cuoi o %s (loi on dinh)"
                                     % (sid, cid))
                ma = next(MA_LY_DO_SO_SANH[i] for i in range(4) if ks[i] != km[i])
                dong.update(outcome="REJECTED", reason=ma, cut_stb=stb_b[cuoi_nhan],
                            cut_score=diem(cuoi_nhan, cid), cut_medal=huy(cuoi_nhan, cid))
                if ma == "LOTTERY":
                    nhom = [p for p in asg if (p, cid) in da_de_nghi
                            and phan(p, cid) == phan(sid, cid)]
                    dong["n_hoa"] = len(nhom) - 1
                    dong["k_cho"] = sum(1 for p in nhom if asg[p] == cid)
                rows.append(dong)
                thua.setdefault(cid, []).append((sid, dong))
        for cid, ds in thua.items():              # danh sách chờ (D4)
            if loai(cid) == TUYEN_CHON:
                ds.sort(key=lambda x: (-(diem(x[0], cid) or 0), -huy(x[0], cid), stb_b[x[0]]))
            else:
                ds.sort(key=lambda x: (-huy(x[0], cid), stb_b[x[0]]))
            for vi_tri, (_, dong) in enumerate(ds, start=1):
                dong["waitlist_pos"] = vi_tri
    return rows


# ---------------------------------------------------------------------------
# FA-7 · bảng nhu cầu cho giáo viên (V§4.3) và kiểm "chỉ tăng" (V§4.1)
# ---------------------------------------------------------------------------
def bang_nhu_cau(clubs: dict, preferences: dict, tested_scores: dict, fa_clb: dict, giu_cho,
                 buoi=None, ten_clb=None) -> list:
    """Bảng nhu cầu mỗi CLB, KHÔNG chứa mã hay tên học sinh (V§13.10).

    Mỗi dòng: `buoi, club_id, ten, loai, capacity, nv1` (số em xếp CLB này đầu tiên TRONG BUỔI),
    `so_ghi` (số em có CLB này trong nguyện vọng), `so_dat_san` (TUYEN_CHON: số em đạt điểm sàn;
    CLB khác: None), `so_giu_cho` (số giữ chỗ dùng được). Đây là số liệu báo cáo để giáo viên xét
    chỉ tiêu, KHÔNG phải khoá ưu tiên. `buoi` lọc một buổi; sắp theo (buổi, mã CLB).
    """
    def buoi_cua(cid):
        return clubs[cid].get("buoi") or BUOI_MAC_DINH

    nv1 = {c: 0 for c in clubs}
    so_ghi = {c: 0 for c in clubs}
    dat_san = {c: 0 for c in clubs}
    for sid, ds in preferences.items():
        trong = [c for c in ds if c in clubs]
        thay_buoi = set()
        for c in trong:
            so_ghi[c] += 1
            b = buoi_cua(c)
            if b not in thay_buoi:
                thay_buoi.add(b)
                nv1[c] += 1
            if (fa_clb.get(c) or {}).get("loai") == TUYEN_CHON:
                diem = tested_scores.get(c, {}).get(sid)
                if diem is not None and diem >= ((fa_clb.get(c) or {}).get("diem_san") or 0):
                    dat_san[c] += 1
    hop_le = giu_cho_hop_le(clubs, giu_cho, {sid: {} for sid in preferences}, preferences)
    so_giu = {c: 0 for c in clubs}
    for c, _ in hop_le:
        so_giu[c] += 1
    rows = []
    for cid in sorted(clubs, key=lambda c: (str(buoi_cua(c)), str(c))):
        if buoi is not None and buoi_cua(cid) != buoi:
            continue
        loai = (fa_clb.get(cid) or {}).get("loai")
        rows.append({"buoi": buoi_cua(cid), "club_id": cid, "ten": (ten_clb or {}).get(cid, cid),
                     "loai": loai, "capacity": clubs[cid].get("capacity"), "nv1": nv1[cid],
                     "so_ghi": so_ghi[cid], "so_dat_san": dat_san[cid] if loai == TUYEN_CHON else None,
                     "so_giu_cho": so_giu[cid]})
    return rows


def goi_y_chi_tieu(rows, gioi_han: dict) -> list:
    """GAP-7 (V§10): mỗi dòng bảng nhu cầu thêm `gioi_han` (giới hạn giáo viên khai, None = chưa khai) và
    `goi_y_ky_sau = min(nv1, gioi_han)` (chưa khai -> nv1), `ghi_chu`: khong_co_nv1 | khong_gioi_han |
    chan_boi_gioi_han | "". Số liệu báo cáo cho kỳ SAU, không bao giờ vào khoá ưu tiên. Không sửa đầu vào."""
    ra = []
    for r in rows:
        gh = gioi_han.get(r["club_id"])
        nv1 = r["nv1"]
        goi_y = nv1 if gh is None else min(nv1, gh)
        ghi = ("khong_co_nv1" if nv1 == 0 else "khong_gioi_han" if gh is None
               else "chan_boi_gioi_han" if nv1 > gh else "")
        ra.append({**r, "gioi_han": gh, "goi_y_ky_sau": goi_y, "ghi_chu": ghi})
    return ra


def kiem_tang_tu_goi_y(goi_y: dict, khai: dict) -> list:
    """GAP-7: giáo viên chỉ được TĂNG từ gợi ý ({club_id: n} cả hai): vi phạm `GIAM_SUC_CHUA` của `kiem_chi_tang`.
    CLB không có trong `khai` thì không xét."""
    return [v for v in kiem_chi_tang({c: {"capacity": n} for c, n in goi_y.items() if c in khai},
                                     {c: {"capacity": n} for c, n in khai.items()})
            if v["loi"] == "GIAM_SUC_CHUA"]


def kiem_chi_tang(truoc: dict, sau: dict) -> list:
    """So hai bản khai CLB {club_id: {capacity, loai}}; trả vi phạm: `GIAM_SUC_CHUA` (chỉ tiêu giảm),
    `DOI_LOAI` (loại đổi, hoặc bị bỏ sau khi đã đặt; đặt LẦN ĐẦU thì được), `MAT_CLB` (CLB biến mất).
    Tăng chỉ tiêu và thêm CLB mới thì được. Loại bị khoá từ lúc MỞ đăng ký (V§4.1)."""
    loi = []
    for cid in sorted(truoc, key=str):
        t = truoc[cid]
        if cid not in sau:
            loi.append({"club_id": cid, "loi": "MAT_CLB", "truoc": t.get("capacity"), "sau": None})
            continue
        a = sau[cid]
        if (t.get("capacity") is not None and a.get("capacity") is not None
                and a["capacity"] < t["capacity"]):
            loi.append({"club_id": cid, "loi": "GIAM_SUC_CHUA", "truoc": t["capacity"],
                        "sau": a["capacity"]})
        if t.get("loai") is not None and a.get("loai") != t["loai"]:
            loi.append({"club_id": cid, "loi": "DOI_LOAI", "truoc": t["loai"], "sau": a.get("loai")})
    return loi
