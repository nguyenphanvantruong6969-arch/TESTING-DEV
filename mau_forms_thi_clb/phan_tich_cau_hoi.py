"""FA-M4 (TH = CHƯA thử trên Microsoft thật): đề biến thể, phân tích câu hỏi (V§7.5) và cân bằng điểm giữa các đề (D11).

Phần tính toán thuần (không đọc tệp Forms): bộ chuyển đổi `chuyen_forms_sang_phan_mem.py --fa-daa` gọi vào đây.

  * `chon_bien_the(email, n)`: đề của một em = crc32(email) % n (`zlib.crc32`, KHÔNG dùng `hash()`).
  * `phan_tich_cau(bai)`: mỗi câu % đúng và độ phân biệt (1/3 điểm cao - 1/3 điểm thấp); cờ PHAN_BIET_AM (< 0),
    QUA_DE (> 90 %), QUA_KHO (< 20 %).
  * `so_sanh_bien_the(diem)` (D11, không bao giờ chặn): ngưỡng z*sqrt(s_v²/n_v + s_o²/n_o) với z = 1,96 (2 đề) hoặc
    2,39 (3 đề); đề n < 5 chỉ báo, không chỉnh; vượt ngưỡng thì dịch (trung bình chung - trung bình đề).
    Admin xác nhận bằng `--ap-dung-dieu-chinh` hoặc `--giu-diem-goc` của bộ chuyển đổi.

Dữ liệu trong test là MÔ PHỎNG.
"""
import math
import sys
import zlib

CHU_BIEN_THE = "ABC"
TRAN_BIEN_THE = 3
N_TOI_THIEU = 5                           # D11: đề ít hơn 5 bài chỉ báo
Z_THEO_SO_DE = {2: 1.96, 3: 2.39}         # 3 đề: Bonferroni cho 3 phép so sánh
NGUONG_QUA_DE, NGUONG_QUA_KHO = 0.9, 0.2


def chon_bien_the(email, n):
    """Đề (chỉ số từ 0) của một em: crc32 của email chuẩn hoá, chia lấy dư n."""
    if n <= 1:
        return 0
    return zlib.crc32(str(email).strip().lower().encode("utf-8")) % n


def chon_bien_the_thi_lai(email, n):
    """Đề khi em được mời thi lại (bị gắn cờ làm quá nhanh): luôn KHÁC đề đã giao."""
    return (chon_bien_the(email, n) + 1) % n if n > 1 else 0


def cac_bien_the(clb):
    """[đề A (= `de_thi`), đề B, đề C] — đề B, C nằm ở `de_thi_bien_the` của CLB trong de_thi.json."""
    return [clb["de_thi"]] + list(clb.get("de_thi_bien_the") or [])


def kiem_bien_the(clb):
    """Danh sách lỗi (chuỗi) của các đề của một CLB: tối đa 3 đề, cùng số câu, cùng cơ cấu độ khó (nếu có `do_kho`)."""
    ma, loi = clb.get("club_id", "?"), []
    de = cac_bien_the(clb)
    if len(de) > TRAN_BIEN_THE:
        loi.append("%s: có %d đề, tối đa %d" % (ma, len(de), TRAN_BIEN_THE))
    for i, d in enumerate(de[1:], 1):
        if len(d) != len(de[0]):
            loi.append("%s: đề %s có %d câu, đề A có %d — số câu phải bằng nhau" % (ma, CHU_BIEN_THE[i], len(d), len(de[0])))
        kho_a = sorted(c.get("do_kho", "") for c in de[0])
        kho_b = sorted(c.get("do_kho", "") for c in d)
        if any(kho_a) and kho_a != kho_b:
            loi.append("%s: đề %s khác đề A về cơ cấu độ khó" % (ma, CHU_BIEN_THE[i]))
    return loi


def phan_tich_cau(bai):
    """`bai`: [{sid, club_id, bien_the, dung: [bool]}] -> các dòng {club_id, bien_the, cau, so_bai, ti_le_dung, phan_biet, co}.

    Độ phân biệt = % đúng của 1/3 nhóm điểm cao nhất - % đúng của 1/3 nhóm thấp nhất (n // 3 em mỗi nhóm; xếp theo tổng câu
    đúng giảm dần, cùng tổng thì theo mã); ít hơn 3 bài thì None."""
    nhom = {}
    for b in bai:
        nhom.setdefault((b["club_id"], b["bien_the"]), []).append(b)
    ra = []
    for (clb, bt), ds in sorted(nhom.items()):
        n = len(ds)
        theo_diem = sorted(ds, key=lambda b: (-sum(b["dung"]), str(b["sid"])))
        k = n // 3
        for j in range(len(ds[0]["dung"])):
            ti_le = sum(b["dung"][j] for b in ds) / n
            pb = None
            if k:
                pb = (sum(b["dung"][j] for b in theo_diem[:k]) - sum(b["dung"][j] for b in theo_diem[-k:])) / k
            co = []
            if pb is not None and pb < 0:
                co.append("PHAN_BIET_AM")
            if ti_le > NGUONG_QUA_DE:
                co.append("QUA_DE")
            if ti_le < NGUONG_QUA_KHO:
                co.append("QUA_KHO")
            ra.append({"club_id": clb, "bien_the": bt, "cau": j + 1, "so_bai": n, "ti_le_dung": ti_le,
                       "phan_biet": pb, "co": co})
    return ra


def diem_10_sau_bo_cau(dung, bo):
    """Điểm thang 10 (chưa làm tròn) sau khi admin bỏ các câu `bo` (số thứ tự từ 1): mọi câu còn lại cùng điểm."""
    giu = [d for i, d in enumerate(dung, 1) if i not in bo]
    return 10.0 * sum(giu) / len(giu) if giu else 0.0


def _tb(x):
    return sum(x) / len(x)


def _sd(x):
    if len(x) < 2:
        return 0.0
    m = _tb(x)
    return math.sqrt(sum((v - m) ** 2 for v in x) / (len(x) - 1))


def so_sanh_bien_the(diem):
    """D11. `diem`: {đề: [điểm thang 10 chưa làm tròn]} của MỘT CLB.

    Trả {co_lech, trung_binh_chung, bien_the: {đề: {n, trung_binh, trung_binh_con_lai, chenh_lech, nguong, ly_do, dich}}}.
    ly_do: MOT_DE (chỉ một đề), N_NHO (đề này hoặc phần còn lại n < 5: chỉ báo), TRONG_NGUONG, NGOAI_NGUONG. `dich` (0 nếu không chỉnh) cộng vào điểm
    chưa làm tròn của đề đó (xem `diem_dieu_chinh`). Quá 3 đề: ValueError (bảng z chỉ có 2 và 3 đề)."""
    k = len(diem)
    if k > TRAN_BIEN_THE:
        raise ValueError("tối đa %d đề" % TRAN_BIEN_THE)
    moi = [v for x in diem.values() for v in x]
    chung = _tb(moi) if moi else 0.0
    ra = {}
    for bt, x in diem.items():
        khac = [v for b2, y in diem.items() if b2 != bt for v in y]
        o = {"n": len(x), "trung_binh": _tb(x) if x else None, "trung_binh_con_lai": _tb(khac) if khac else None,
             "chenh_lech": None, "nguong": None, "ly_do": "MOT_DE", "dich": 0.0}
        if k > 1 and x and khac:
            o["chenh_lech"] = o["trung_binh"] - o["trung_binh_con_lai"]
            o["nguong"] = Z_THEO_SO_DE[k] * math.sqrt(_sd(x) ** 2 / len(x) + _sd(khac) ** 2 / len(khac))
            if len(x) < N_TOI_THIEU or len(khac) < N_TOI_THIEU:   # FA-S3: một phía nhỏ -> chỉ báo
                o["ly_do"] = "N_NHO"
            elif abs(o["chenh_lech"]) > o["nguong"]:
                o["ly_do"], o["dich"] = "NGOAI_NGUONG", chung - o["trung_binh"]
            else:
                o["ly_do"] = "TRONG_NGUONG"
        ra[bt] = o
    return {"co_lech": any(o["ly_do"] == "NGOAI_NGUONG" for o in ra.values()), "trung_binh_chung": chung, "bien_the": ra}


def diem_dieu_chinh(diem_tho, dich):
    """Điểm nguyên sau cân bằng: làm tròn nửa lên của (điểm chưa tròn + dịch), kẹp vào 0-10 (D7)."""
    from fractions import Fraction
    x = Fraction(str(diem_tho)) + Fraction(str(round(dich, 9)))
    return int(min(10, max(0, (x + Fraction(1, 2)) // 1)))


def ghi_bao_cao(duong, hang_cau=None, so_sanh_theo_clb=None):
    """Ghi xlsx: sheet "Câu hỏi" (V§7.5) và/hoặc sheet "Cân bằng đề" (D11). Cờ viết bằng mã, người đọc xem hướng dẫn."""
    from openpyxl import Workbook
    wb = Workbook()
    wb.remove(wb.active)
    if hang_cau is not None:
        ws = wb.create_sheet("Câu hỏi")
        ws.append(["CLB", "Đề", "Câu", "Số bài", "% đúng", "Độ phân biệt", "Cờ"])
        for r in hang_cau:
            ws.append([r["club_id"], r["bien_the"], r["cau"], r["so_bai"], round(100 * r["ti_le_dung"], 1),
                       None if r["phan_biet"] is None else round(r["phan_biet"], 3), ", ".join(r["co"])])
    if so_sanh_theo_clb is not None:
        ws = wb.create_sheet("Cân bằng đề")
        ws.append(["CLB", "Đề", "Số bài", "Trung bình", "Trung bình đề còn lại", "Chênh lệch", "Ngưỡng", "Kết luận",
                   "Dịch điểm (nếu áp dụng)"])
        for clb, kq in so_sanh_theo_clb.items():
            for bt, o in kq["bien_the"].items():
                ws.append([clb, bt, o["n"]] + [None if o[k] is None else round(o[k], 3) for k in
                                                ("trung_binh", "trung_binh_con_lai", "chenh_lech", "nguong")]
                          + [o["ly_do"], round(o["dich"], 3)])
    wb.save(duong)


def main(argv=None):
    """`python phan_tich_cau_hoi.py chia DANH_SACH.csv --so-bien-the 2 --ra DE_CUA_EM.csv`: cột Email -> Email, DeGiao,
    DeThiLai (A/B/C), để gửi đúng đường dẫn biểu mẫu cho từng em."""
    import argparse
    import csv
    ap = argparse.ArgumentParser(description=main.__doc__.split("\n")[0])
    ap.add_argument("lenh", choices=["chia"])
    ap.add_argument("tep", help="CSV có cột Email")
    ap.add_argument("--so-bien-the", type=int, default=2, choices=[1, 2, 3])
    ap.add_argument("--ra", required=True)
    a = ap.parse_args(argv)
    with open(a.tep, encoding="utf-8-sig", newline="") as f:
        dong = list(csv.DictReader(f))
    if not dong or "Email" not in dong[0]:
        print("tệp phải có cột Email", file=sys.stderr)
        return 1
    with open(a.ra, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Email", "DeGiao", "DeThiLai"])
        for r in dong:
            e = r["Email"].strip().lower()
            w.writerow([e, CHU_BIEN_THE[chon_bien_the(e, a.so_bien_the)], CHU_BIEN_THE[chon_bien_the_thi_lai(e, a.so_bien_the)]])
    print("Đã chia %d em thành %d đề -> %s" % (len(dong), a.so_bien_the, a.ra))
    return 0


if __name__ == "__main__":
    sys.exit(main())
