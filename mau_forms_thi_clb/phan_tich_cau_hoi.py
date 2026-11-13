"""FA-M4 (TH = CHƯA thử trên Microsoft thật): đề biến thể, phân tích câu hỏi (V§7.5) và cân bằng điểm giữa các đề (D11).

Phần tính toán thuần (không đọc tệp Forms): bộ chuyển đổi `chuyen_forms_sang_phan_mem.py --fa-daa` gọi vào đây.

  * `chon_bien_the(email, n)`: đề của một em = crc32(email) % n (`zlib.crc32`, KHÔNG dùng `hash()`).
  * `phan_tich_cau(bai)`: mỗi câu % đúng và độ phân biệt (1/3 điểm cao - 1/3 điểm thấp); cờ PHAN_BIET_AM (< 0),
    QUA_DE (> 90 %), QUA_KHO (< 20 %).
  * `so_sanh_bien_the(diem)` (D11, không bao giờ chặn): ngưỡng z*sqrt(s_v²/n_v + s_o²/n_o) với z = 1,96 (2 đề) hoặc
    2,39 (3 đề); đề n < 5 chỉ báo, không chỉnh; vượt ngưỡng thì dịch (trung bình chung - trung bình đề).
    Admin xác nhận bằng `--ap-dung-dieu-chinh` hoặc `--giu-diem-goc` của bộ chuyển đổi.
  * `do_lech_cham(rows)` (GAP-9, V§7.4): độ lệch tuyệt đối trung bình giữa hai người chấm theo câu và theo CLB;
    trung bình >= 1,5 điểm -> cờ LECH_CHAM (nên sửa thang chấm). Lệnh `lech TEP.csv --ra BAO_CAO.xlsx`.

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
NGUONG_LECH_CHAM = 1.5                    # GAP-9 (V§7.4): độ lệch 2 người chấm phải < 1,5 điểm


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


def cat_mot_chu_so_le(x):
    """FA-D7L: kẹp `x` (Fraction) vào 0-10 rồi CẮT BỚT về một chữ số lẻ (không làm tròn). Số nguyên -> int, không thì
    float một chữ số lẻ (7.5), để Sổ nhập ghi "7.5" như mọi điểm khác.

    Vì sao cắt bớt mà không làm tròn: với x >= 0 và t = floor(10x)/10 thì floor(t + 1/2) == floor(x + 1/2) — mọi
    nửa-nguyên n − 1/2 là bội của 1/10, nên x >= n − 1/2 <=> t >= n − 1/2. Nên so t với điểm sàn SAU KHI làm tròn nửa
    lên (`fa_daa.dat_diem_san`) cho đúng tập em đạt như điểm nguyên (D7). Làm tròn tới 0,1 thì hỏng: 4,45 -> 4,5 -> 5,
    nhưng điểm nguyên của 4,45 là 4."""
    from fractions import Fraction
    x = min(Fraction(10), max(Fraction(0), x))
    t = Fraction((x * 10) // 1, 10)
    return int(t) if t.denominator == 1 else float(t)


def diem_dieu_chinh_le(diem_tho, dich):
    """FA-D7L: như `diem_dieu_chinh` nhưng giữ một chữ số lẻ: cắt bớt (điểm chưa tròn + dịch), kẹp 0-10.
    Làm tròn nửa lên của kết quả == `diem_dieu_chinh(diem_tho, dich)` (xem `cat_mot_chu_so_le`)."""
    from fractions import Fraction
    return cat_mot_chu_so_le(Fraction(str(diem_tho)) + Fraction(str(round(dich, 9))))


def _so(x):
    """Điểm đọc được (số hoặc chữ số) -> float; rỗng / None / không đọc được -> None."""
    if x is None or isinstance(x, bool):
        return None
    try:
        v = float(str(x).strip().replace(",", "."))
    except ValueError:
        return None
    return v if math.isfinite(v) else None


def do_lech_cham(rows):
    """GAP-9. `rows`: [{club_id, cau, diem_1, diem_2}]; dòng thiếu một trong hai điểm bị bỏ. Trả
    {"theo_cau": [{club_id, cau, n, lech_tb, co}], "theo_clb": [{club_id, n, lech_tb, co}]}, sắp theo mã;
    co = "LECH_CHAM" khi lech_tb >= NGUONG_LECH_CHAM, không thì "". Hàm thuần."""
    cau, clb = {}, {}
    for r in rows:
        a, b = _so(r.get("diem_1")), _so(r.get("diem_2"))
        if a is None or b is None:
            continue
        d = abs(a - b)
        cau.setdefault((str(r["club_id"]), str(r["cau"])), []).append(d)
        clb.setdefault(str(r["club_id"]), []).append(d)

    def dong(x):
        tb = _tb(x)
        return {"n": len(x), "lech_tb": tb, "co": "LECH_CHAM" if tb >= NGUONG_LECH_CHAM else ""}
    return {"theo_cau": [{"club_id": k[0], "cau": k[1], **dong(v)} for k, v in sorted(cau.items())],
            "theo_clb": [{"club_id": k, **dong(v)} for k, v in sorted(clb.items())]}


def ghi_bao_cao(duong, hang_cau=None, so_sanh_theo_clb=None, do_lech=None):
    """Ghi xlsx: sheet "Câu hỏi" (V§7.5), "Cân bằng đề" (D11) và/hoặc "Độ lệch chấm" (GAP-9). Cờ viết bằng mã, người
    đọc xem hướng dẫn."""
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
    if do_lech is not None:
        ws = wb.create_sheet("Độ lệch chấm")
        ws.append(["CLB", "Câu", "Số bài", "Lệch trung bình", "Cờ"])
        for r in do_lech["theo_cau"]:
            ws.append([r["club_id"], r["cau"], r["n"], round(r["lech_tb"], 3), r["co"]])
        for r in do_lech["theo_clb"]:
            ws.append([r["club_id"], "(cả CLB)", r["n"], round(r["lech_tb"], 3), r["co"]])
    wb.save(duong)


def main(argv=None):
    """`python phan_tich_cau_hoi.py chia DANH_SACH.csv --so-bien-the 2 --ra DE_CUA_EM.csv`: cột Email -> Email, DeGiao,
    DeThiLai (A/B/C), để gửi đúng đường dẫn biểu mẫu cho từng em.
    `python phan_tich_cau_hoi.py lech CHAM.csv --ra BAO_CAO.xlsx` (GAP-9): cột ClubId, Cau, Diem1, Diem2 -> sheet
    "Độ lệch chấm"."""
    import argparse
    import csv
    ap = argparse.ArgumentParser(description=main.__doc__.split("\n")[0])
    ap.add_argument("lenh", choices=["chia", "lech"])
    ap.add_argument("tep", help="CSV có cột Email (chia) hoặc ClubId, Cau, Diem1, Diem2 (lech)")
    ap.add_argument("--so-bien-the", type=int, default=2, choices=[1, 2, 3])
    ap.add_argument("--ra", required=True)
    a = ap.parse_args(argv)
    with open(a.tep, encoding="utf-8-sig", newline="") as f:
        dong = list(csv.DictReader(f))
    if a.lenh == "lech":
        thieu = [c for c in ("ClubId", "Cau", "Diem1", "Diem2") if not dong or c not in dong[0]]
        if thieu:
            print("tệp thiếu cột: %s" % ", ".join(thieu), file=sys.stderr)
            return 1
        kq = do_lech_cham([{"club_id": r["ClubId"], "cau": r["Cau"], "diem_1": r["Diem1"], "diem_2": r["Diem2"]}
                           for r in dong])
        ghi_bao_cao(a.ra, do_lech=kq)
        n_co = sum(1 for r in kq["theo_cau"] if r["co"])
        print("Độ lệch chấm: %d câu, %d câu lệch >= %s điểm -> %s" % (len(kq["theo_cau"]), n_co, NGUONG_LECH_CHAM, a.ra))
        return 0
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
