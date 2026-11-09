"""FA-DAA (mục A13): lớp bọc quanh thuật toán DA — KHÔNG sửa lõi `run_rbda_nhieu_buoi`.

Tầng này chỉ chạy khi `rules.fa_daa` bật (mặc định TẮT). FA-1: kiểu CLB, kiểm thuộc tính, ghi cột
mới và bảng `giu_cho`. Các bước sau (precheck, huy chương một quỹ, chạy, tối thiểu, lý do) thêm
vào cùng tệp này.

Dữ liệu trong test là dữ liệu MÔ PHỎNG.
"""

from __future__ import annotations

import unicodedata

from i18n_errors import err  # noqa: F401  (các bước sau dùng)

# Ba kiểu CLB (vision V§2): không giới hạn / giới hạn chỗ / giới hạn chỗ có bài thi chọn lọc.
TU_DO, GIOI_HAN, TUYEN_CHON = "TU_DO", "GIOI_HAN", "TUYEN_CHON"
CAC_LOAI = (TU_DO, GIOI_HAN, TUYEN_CHON)

# Nhãn người dùng gõ -> mã. So sau khi bỏ dấu, chữ thường, gạch dưới thành khoảng trắng.
_NHAN_LOAI = {
    "tu do": TU_DO, "free": TU_DO,
    "gioi han": GIOI_HAN, "limited": GIOI_HAN,
    "tuyen chon": TUYEN_CHON, "selective": TUYEN_CHON,
}
NHAN_LOAI_HIEN_THI = {TU_DO: "Tự do", GIOI_HAN: "Giới hạn", TUYEN_CHON: "Tuyển chọn"}

DIEM_SAN_TOI_DA = 10


def _khong_dau(chuoi) -> str:
    s = unicodedata.normalize("NFD", str(chuoi))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("đ", "d").replace("Đ", "D")
    return " ".join(s.lower().replace("_", " ").split())


def chuan_hoa_loai(nhan):
    """Nhãn (`Tự do`, `Giới hạn`, `Tuyển chọn`, hoặc mã) -> mã; trống/None -> None.

    Nhãn lạ ném ValueError: tệp nhập phải báo lỗi chứ không đoán.
    """
    if nhan is None or not str(nhan).strip():
        return None
    k = _khong_dau(nhan)
    if k in _NHAN_LOAI:
        return _NHAN_LOAI[k]
    for ma in CAC_LOAI:
        if k == _khong_dau(ma):
            return ma
    raise ValueError("Loại CLB không hợp lệ: %r" % (nhan,))


def _la_nguyen(v) -> bool:
    if isinstance(v, bool):
        return False
    if isinstance(v, int):
        return True
    return isinstance(v, float) and v.is_integer()


def kiem_thuoc_tinh(loai, diem_san, so_toi_thieu, suc_chua_phong, **ngu_canh) -> list:
    """Kiểm bốn thuộc tính FA của MỘT CLB (None = không đặt). Trả danh sách lỗi `err(...)`.

    Chỉ kiểm giá trị từng ô; ràng buộc giữa các CLB (mỗi buổi có CLB tự do, TUYEN_CHON có điểm
    sàn...) là việc của `kiem_truoc_fa` (FA-2). `ngu_canh` (vd dong=, club_id=) gắn vào lỗi.
    """
    loi = []
    if loai is not None and loai not in CAC_LOAI:
        loi.append(err("fa_loai_sai", loai=str(loai), **ngu_canh))
    if diem_san is not None and not (_la_nguyen(diem_san) and 0 <= diem_san <= DIEM_SAN_TOI_DA):
        loi.append(err("fa_diem_san_sai", diem_san=str(diem_san), **ngu_canh))
    if so_toi_thieu is not None and not (_la_nguyen(so_toi_thieu) and so_toi_thieu >= 0):
        loi.append(err("fa_toi_thieu_sai", so_toi_thieu=str(so_toi_thieu), **ngu_canh))
    if suc_chua_phong is not None and not (_la_nguyen(suc_chua_phong) and suc_chua_phong > 0):
        loi.append(err("fa_suc_chua_phong_sai", suc_chua_phong=str(suc_chua_phong), **ngu_canh))
    return loi


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
