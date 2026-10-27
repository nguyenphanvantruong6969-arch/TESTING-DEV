# -*- coding: utf-8 -*-
"""Sinh và soát bộ dữ liệu đầu vào cho phần mềm phân bổ câu lạc bộ (RB-DA).

Ba chế độ:

    python sinh_du_lieu.py tao   --spec truong.json --ra ./bo_moi
    python sinh_du_lieu.py ngau  --ra ./bo_moi  --hoc-sinh 180 --buoi thu_2,thu_4,thu_6
    python sinh_du_lieu.py soat  ./bo_moi

`tao`  — dựng từ một bản khai báo JSON tường minh (bạn nắm toàn quyền).
`ngau` — dựng một trường ngẫu nhiên nhưng HỢP LỆ, tất định theo `--seed`.
`soat` — soát một bộ đã có, không sửa gì.
`ap`   — áp Điểm quyết tâm (mục A13; trong mã là `wharton`) lên một sổ đã có.

`ngau`, `tao` và `ap` nhận thêm `--diem-quyet-tam {khong,hop_le,co_loi,trong}` và
`--kieu-chia {tron,don_dau,deu,all_in,ngau_nhien}`. Mặc định `khong` = hành vi cũ, đầu ra
không đổi một ô nào.

Đầu ra là MỘT tệp: `SO_NHAP_CLB.xlsx` — Sổ nhập CLB, đúng tệp phần mềm nhận
(xem `so_nhap.py` ở gốc kho mã). `soat` đọc được cả sổ lẫn bộ ba CSV cũ.

NGUYÊN TẮC: sổ luôn đi ra từ MỘT nguồn trong bộ nhớ, và mọi phép soát chạy
TRƯỚC khi ghi. Sai một điều là không ghi gì — sinh ra một bộ dữ liệu hỏng
còn tệ hơn không sinh gì, vì nó trông y như thật.

Đoạn mã này KHÔNG tự sửa dữ liệu sai. Sửa giúp là giấu mất chỗ sai.
"""

import argparse
import csv
import io
import json
import os
import random
import sys

# so_nhap.py (định nghĩa Sổ nhập CLB) nằm ở gốc kho mã; bản đóng gói (.zip)
# để một bản sao ngay cạnh script này — ưu tiên bản cạnh script.
_DAY = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(_DAY, "..", "..", "..", "..")))
sys.path.insert(0, _DAY)
import so_nhap  # noqa: E402

# Trần do chính phần mềm áp, không phải do đoạn mã này nghĩ ra.
# Xem `rbda_priority_pipeline.TRAN_NGUYEN_VONG_MOI_BUOI` / `TRAN_CLB_THI_MOI_BUOI`.
TRAN_NGUYEN_VONG_MOI_BUOI = 10   # = giới hạn câu hỏi Ranking của Microsoft Forms
TRAN_CLB_THI_MOI_BUOI = 5

# Tệp ghi ra.
TEN_SO = "SO_NHAP_CLB.xlsx"

# Điểm quyết tâm (mục A13): mỗi em có HAI quỹ cho MỖI buổi — quỹ 1 chia cho các CLB em có tick
# thi, quỹ 2 chia cho các CLB còn lại — mỗi quỹ đúng NGAN_SACH_DQT điểm. Hằng này là bản sao của
# `rbda_priority_pipeline.WHARTON_NGAN_SACH` (kỹ năng không nhập mã thuật toán, để đóng gói
# riêng được); test `test_du_lieu_mau_diem_quyet_tam.py` canh hai số luôn bằng nhau.
NGAN_SACH_DQT = 100
CHE_DO_DQT = ("khong", "hop_le", "co_loi", "trong")
KIEU_CHIA = ("don_dau", "deu", "all_in", "ngau_nhien")
LOAI_LOI_DQT = ("thieu", "thua", "ngoai_nguyen_vong", "tang_lech", "toan_0")
# Cấu hình workspace bật điểm quyết tâm; chỉ để `so_nhap.ghi_so_nhap` vẽ thêm cột.
CFG_DQT = {"rules": {"wharton": True, "max_choices": TRAN_NGUYEN_VONG_MOI_BUOI,
                     "max_tests": TRAN_CLB_THI_MOI_BUOI, "score_scope": "per_slot"}}

# Bộ ba tệp CSV cũ — chỉ còn để `soat` đọc các bộ đã có.
TEN_TEP = {
    "clb": "01_danh_sach_CLB.csv",
    "thi": "02_chon_CLB_muon_thi.csv",
    "nv": "03_xep_hang_nguyen_vong.csv",
}

# Nhãn buổi phần mềm nhận ra được (còn nhận nhiều cách viết khác; đây là
# cách viết chuẩn nên dùng khi sinh mới).
BUOI_CHUAN = ["thu_2", "thu_3", "thu_4", "thu_5", "thu_6", "thu_7", "chu_nhat"]


# ---------------------------------------------------------------------------
# SOÁT — dùng chung cho cả sinh mới lẫn kiểm bộ đã có
# ---------------------------------------------------------------------------

def soat(clb, hs):
    """Trả về danh sách lỗi. Rỗng = hợp lệ.

    `clb`: [{club_id, name, capacity, reserve_capacity, reserve_group, buoi}]
    `hs` : [{student_id, name, reserve_group, nguyen_vong: {buoi: [club_id]},
             diem: {club_id: float|str}}]
    """
    loi = []

    ma = [c["club_id"] for c in clb]
    if len(ma) != len(set(ma)):
        loi.append("có mã câu lạc bộ bị trùng trong danh sách")
    tap_ma = set(ma)
    buoi_cua = {c["club_id"]: (c.get("buoi") or "") for c in clb}

    for c in clb:
        if not c["club_id"]:
            loi.append("có câu lạc bộ thiếu mã")
        try:
            suc = int(c["capacity"])
        except (TypeError, ValueError):
            loi.append("%s: sức chứa không phải số" % c["club_id"])
            continue
        if suc <= 0:
            loi.append("%s: sức chứa phải lớn hơn 0" % c["club_id"])
        du = int(c.get("reserve_capacity") or 0)
        if du < 0:
            loi.append("%s: chỉ tiêu dự trữ âm" % c["club_id"])
        if du > suc:
            loi.append("%s: chỉ tiêu dự trữ (%d) lớn hơn sức chứa (%d)"
                       % (c["club_id"], du, suc))
        if du > 0 and not (c.get("reserve_group") or "").strip():
            loi.append("%s: có chỉ tiêu dự trữ nhưng không ghi nhóm dự trữ"
                       % c["club_id"])

    # Khai buổi thì phải khai cho MỌI câu lạc bộ. Khai một nửa thì những câu
    # lạc bộ bỏ trống bị gom chung một buổi, và học sinh chỉ vào được một
    # trong số chúng — phần mềm cảnh báo đúng chuyện này.
    co_buoi = [c["club_id"] for c in clb if (c.get("buoi") or "").strip()]
    if co_buoi and len(co_buoi) != len(clb):
        loi.append("chỉ %d/%d câu lạc bộ khai buổi — khai thì phải khai hết, "
                   "hoặc bỏ trống hết" % (len(co_buoi), len(clb)))

    ma_hs = [h["student_id"] for h in hs]
    if len(ma_hs) != len(set(ma_hs)):
        loi.append("có mã học sinh bị trùng")

    for h in hs:
        sid = h["student_id"]
        if not sid:
            loi.append("có học sinh thiếu mã")
            continue

        for b, ds in (h.get("nguyen_vong") or {}).items():
            if len(ds) != len(set(ds)):
                loi.append("%s · %s: nguyện vọng trùng nhau" % (sid, b))
            if len(ds) > TRAN_NGUYEN_VONG_MOI_BUOI:
                loi.append("%s · %s: %d nguyện vọng, vượt trần %d mỗi buổi"
                           % (sid, b, len(ds), TRAN_NGUYEN_VONG_MOI_BUOI))
            for cid in ds:
                if cid not in tap_ma:
                    loi.append("%s · %s: mã '%s' không có trong danh sách câu lạc bộ"
                               % (sid, b, cid))
                elif buoi_cua[cid] != b:
                    loi.append("%s: %s nằm ở cột buổi %s nhưng sinh hoạt %s"
                               % (sid, cid, b, buoi_cua[cid] or "(không khai)"))

        theo_buoi = {}
        for cid in (h.get("diem") or {}):
            if cid not in tap_ma:
                loi.append("%s: chấm điểm cho mã '%s' không có thật" % (sid, cid))
                continue
            b = buoi_cua[cid]
            theo_buoi.setdefault(b, []).append(cid)
            # Diem cho mot CLB em khong xep nguyen vong la diem khong dung
            # toi — va gan nhu chac chan la go lech cot.
            if cid not in (h.get("nguyen_vong") or {}).get(b, []):
                loi.append("%s: dự thi %s nhưng không xếp nguyện vọng câu lạc bộ đó"
                           % (sid, cid))
        for b, ds in theo_buoi.items():
            if len(ds) > TRAN_CLB_THI_MOI_BUOI:
                loi.append("%s · %s: dự thi %d câu lạc bộ, vượt trần %d mỗi buổi"
                           % (sid, b, len(ds), TRAN_CLB_THI_MOI_BUOI))

    # Canh bao muc do "khong hong nhung nen biet" — van tra ve de nguoi dung
    # thay, nhung khong chan viec ghi.
    return loi


def canh_bao_men(clb, hs):
    """Những điều không sai nhưng nên biết trước khi chạy."""
    ra = []

    # Hai phia phai chuan hoa nhan buoi GIONG NHAU. Truong mot buoi thi cau
    # lac bo mang nhan rong con nguyen vong cung mang nhan rong; doi mot phia
    # thanh "__mac_dinh__" la hai ben khong con gap nhau, va bang canh bao noi
    # "0 em / 69 cho" — mot cau vo nghia, va vo nghia theo kieu nghe rat that.
    def nhan(b):
        return b or "__mac_dinh__"

    tong_cho = {}
    for c in clb:
        b = nhan(c.get("buoi"))
        tong_cho[b] = tong_cho.get(b, 0) + int(c["capacity"])
    muon = {}
    for h in hs:
        for b, ds in (h.get("nguyen_vong") or {}).items():
            if ds:
                muon[nhan(b)] = muon.get(nhan(b), 0) + 1
    for b in sorted(set(tong_cho) | set(muon)):
        cho, em = tong_cho.get(b, 0), muon.get(b, 0)
        if cho and em / cho > 3:
            ra.append("buổi %s chọi %.1f lần (%d em / %d chỗ) — sẽ có nhiều "
                      "em trượt buổi đó" % (b, em / cho, em, cho))
        if cho and em < cho * 0.5:
            ra.append("buổi %s thừa chỗ (%d em / %d chỗ)" % (b, em, cho))
    khong_nv = [h["student_id"] for h in hs
                if not any((h.get("nguyen_vong") or {}).values())]
    if khong_nv:
        ra.append("%d em không khai nguyện vọng nào cả tuần — các em đó chắc "
                  "chắn trắng tay" % len(khong_nv))
    return ra


def cac_quy(clb, h):
    """{(buoi, quy): [club_id theo thứ tự nguyện vọng]} của một em.

    Quỹ 1 = CLB em có tick thi (có trong `diem`), quỹ 2 = các CLB còn lại. Mỗi buổi tách riêng,
    cùng cách chia với `rbda_priority_pipeline.kiem_ho_so_wharton`. Chỉ nhìn TẬP CLB, không nhìn
    thứ hạng để làm khoá của bất cứ thứ gì.
    """
    buoi_cua = {c["club_id"]: (c.get("buoi") or "") for c in clb}
    thi = h.get("diem") or {}
    ra = {}
    for b, ds in (h.get("nguyen_vong") or {}).items():
        for cid in ds:
            ra.setdefault((buoi_cua.get(cid, b), 1 if cid in thi else 2), []).append(cid)
    return ra


def soat_diem_quyet_tam(clb, hs):
    """Soát hồ sơ Điểm quyết tâm trong bộ nhớ; rỗng = hợp lệ.

    Chỉ chạy khi chế độ là `hop_le` (hoặc khi `soat` thấy sổ có điểm). Luật: mỗi quỹ của mỗi
    buổi có CLB thì điểm là số nguyên >= 0, khoá nằm trong đúng tập CLB của quỹ, tổng đúng
    `NGAN_SACH_DQT`.
    """
    loi = []
    for h in hs:
        sid = h["student_id"]
        w = h.get("diem_quyet_tam") or {}
        quy = cac_quy(clb, h)
        trong_quy = {cid for ds in quy.values() for cid in ds}
        for cid in sorted(w):
            if cid not in trong_quy:
                loi.append("%s: điểm quyết tâm cho %s ngoài nguyện vọng" % (sid, cid))
        for (b, q), ds in sorted(quy.items()):
            gia_tri = [w.get(c) for c in ds]
            if any(v is not None and (isinstance(v, bool) or not isinstance(v, int) or v < 0)
                   for v in gia_tri):
                loi.append("%s · %s · quỹ %d: điểm không phải số nguyên >= 0" % (sid, b, q))
                continue
            tong = sum(v for v in gia_tri if v is not None)
            if tong != NGAN_SACH_DQT:
                loi.append("%s · %s · quỹ %d: tổng điểm quyết tâm %d, phải đúng %d"
                           % (sid, b or "(một buổi)", q, tong, NGAN_SACH_DQT))
        if h.get("dqt_mo_coi"):
            loi.append("%s: có điểm quyết tâm ở ô nguyện vọng trống" % sid)
    return loi


# ---------------------------------------------------------------------------
# GHI
# ---------------------------------------------------------------------------

def thanh_so(clb, hs):
    """(clb, hs) của skill -> (clubs, students) cho `so_nhap.ghi_so_nhap`.

    Nguyện vọng các buổi nối thành MỘT danh sách theo thứ tự buổi: sổ nhập
    không chia cột theo buổi, phần mềm tự chia theo buổi của từng CLB.
    Điểm đặt ngay cạnh nguyện vọng của CLB đó.
    """
    ds_buoi = []
    for c in clb:                      # giu thu tu xuat hien, khong sap lai
        b = c.get("buoi") or ""
        if b not in ds_buoi:
            ds_buoi.append(b)
    clubs = [{
        "club_id": c["club_id"], "name": c.get("name") or c["club_id"],
        "capacity": int(c["capacity"]),
        "reserve_capacity": int(c.get("reserve_capacity") or 0),
        "reserve_group": c.get("reserve_group") or "", "buoi": c.get("buoi") or "",
    } for c in clb]
    students = []
    for h in hs:
        nv = h.get("nguyen_vong") or {}
        diem = h.get("diem") or {}
        thu_tu = [cid for b in ds_buoi + [b for b in nv if b not in ds_buoi]
                  for cid in nv.get(b, [])]
        w = h.get("diem_quyet_tam")
        nv_ra = []
        for cid in thu_tu:
            x = {"club_id": cid, "thi": cid in diem, "diem": diem.get(cid, "")}
            if w is not None and cid in w:
                x["diem_w"] = w[cid]
            nv_ra.append(x)
        # Điểm đặt cạnh một ô nguyện vọng TRỐNG (chỉ biến thể CO_LOI cố ý làm vậy).
        nv_ra += [{"club_id": "", "thi": False, "diem": "", "diem_w": v}
                  for v in (h.get("dqt_mo_coi") or [])]
        students.append({
            "student_id": h["student_id"], "name": h.get("name") or "",
            "reserve_group": h.get("reserve_group") or "", "nv": nv_ra,
        })
    return clubs, students


def ghi_bo(thu_muc, clb, hs, cfg=None, ten_tep=TEN_SO):
    """Ghi Sổ nhập CLB. GỌI SAU KHI soát() đã trả về rỗng. Trả [đường dẫn].

    `cfg=CFG_DQT` thì sổ có thêm cột "Điểm quyết tâm" (ô trống nếu em không có điểm)."""
    os.makedirs(thu_muc, exist_ok=True)
    p = os.path.join(thu_muc, ten_tep)
    clubs, students = thanh_so(clb, hs)
    so_nhap.ghi_so_nhap(p, clubs, students, cfg=cfg)
    return [p]


# ---------------------------------------------------------------------------
# ĐỌC LẠI một bộ đã có (cho chế độ `soat`)
# ---------------------------------------------------------------------------

def doc_so(duong):
    """Đọc một Sổ nhập CLB về đúng dạng (clb, hs) mà `soat` dùng."""
    import openpyxl

    wb = openpyxl.load_workbook(duong, read_only=True, data_only=True)
    try:
        if not so_nhap.la_so_nhap(wb.sheetnames):
            raise SystemExit("%s không phải Sổ nhập CLB" % duong)
        du = so_nhap.doc_so_nhap(wb)
    finally:
        wb.close()
    if du["loi"]:
        import i18n_errors
        raise SystemExit("Sổ nhập có lỗi:\n" + "\n".join(
            "   ✗ " + d for d in i18n_errors.format_all(du["loi"])))
    clb = [{k: c[k] for k in ("club_id", "name", "capacity", "reserve_capacity",
                              "reserve_group", "buoi")} for c in du["clubs"]]
    buoi_cua = {c["club_id"]: c["buoi"] for c in clb}
    hs = []
    for s in du["students"]:
        nv, diem, w = {}, {}, {}
        for x in s["nv"]:
            nv.setdefault(buoi_cua.get(x["club_id"], ""), []).append(x["club_id"])
            if x["thi"]:
                diem[x["club_id"]] = x["diem"]
            o_w = str(x.get("diem_w") or "").strip()
            if o_w:
                w[x["club_id"]] = int(o_w) if o_w.isdigit() else o_w
        em = {"student_id": s["student_id"], "name": s["name"],
              "reserve_group": s["reserve_group"] or "", "nguyen_vong": nv, "diem": diem}
        if w:
            em["diem_quyet_tam"] = w
        if s.get("diem_w_mo_coi"):
            em["dqt_mo_coi"] = list(s["diem_w_mo_coi"])
        hs.append(em)
    return clb, hs


def doc_bo(thu_muc):
    """Đọc Sổ nhập CLB (tệp .xlsx, hoặc thư mục có SO_NHAP_CLB.xlsx), hoặc
    bộ ba CSV cũ trong thư mục."""
    if thu_muc.lower().endswith((".xlsx", ".xlsm")):
        return doc_so(thu_muc)
    if os.path.exists(os.path.join(thu_muc, TEN_SO)):
        return doc_so(os.path.join(thu_muc, TEN_SO))

    def doc(ten):
        p = os.path.join(thu_muc, ten)
        if not os.path.exists(p):
            raise SystemExit("Không thấy %s" % p)
        with io.open(p, encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))

    clb = []
    for r in doc(TEN_TEP["clb"]):
        clb.append({
            "club_id": (r.get("club_id") or "").strip(),
            "name": (r.get("name") or "").strip(),
            "capacity": (r.get("capacity") or "0").strip(),
            "reserve_capacity": (r.get("reserve_capacity") or "0").strip() or 0,
            "reserve_group": (r.get("reserve_group") or "").strip(),
            "buoi": (r.get("buoi") or "").strip(),
        })

    hs = {}
    for r in doc(TEN_TEP["nv"]):
        sid = (r.get("student_id") or "").strip()
        em = hs.setdefault(sid, {"student_id": sid,
                                 "name": (r.get("name") or "").strip(),
                                 "reserve_group": (r.get("reserve_group") or "").strip(),
                                 "nguyen_vong": {}, "diem": {}})
        for k, v in r.items():
            if not k or not v or "_pref_" not in k:
                continue
            b = k.rsplit("_pref_", 1)[0]
            em["nguyen_vong"].setdefault(b, []).append(v.strip())

    for r in doc(TEN_TEP["thi"]):
        sid = (r.get("student_id") or "").strip()
        em = hs.setdefault(sid, {"student_id": sid, "name": "", "reserve_group": "",
                                 "nguyen_vong": {}, "diem": {}})
        for k, v in r.items():
            if k and k.startswith("test_club_") and v:
                so = k[len("test_club_"):]
                em["diem"][v.strip()] = (r.get("score_" + so) or "").strip()

    return clb, list(hs.values())


# ---------------------------------------------------------------------------
# SINH NGẪU NHIÊN nhưng HỢP LỆ
# ---------------------------------------------------------------------------

_HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Vũ", "Đỗ", "Bùi", "Ngô",
       "Dương", "Lý", "Hồ", "Đặng", "Phan", "Trịnh", "Mai", "Chu", "Tạ"]
_DEM = ["Văn", "Thị", "Minh", "Gia", "Bảo", "Khánh", "Hoài", "Quốc", "Thanh", "Anh"]
_TEN = ["An", "Bình", "Chi", "Dũng", "Giang", "Hà", "Huy", "Khanh", "Lan",
        "Mai", "Nam", "Ngân", "Nhi", "Phúc", "Quân", "Sương", "Tuấn", "Uyên",
        "Việt", "Xuân", "Yến", "Linh", "Thảo", "Vy"]

_CHU_DE = [
    ("clb_bongro", "CLB Bóng rổ"), ("clb_bongda", "CLB Bóng đá"),
    ("clb_covua", "CLB Cờ vua"), ("clb_vanhoc", "CLB Văn học"),
    ("clb_tinhoc", "CLB Tin học"), ("clb_robotics", "CLB Robotics"),
    ("clb_mythuat", "CLB Mỹ thuật"), ("clb_amnhac", "CLB Âm nhạc"),
    ("clb_nauan", "CLB Nấu ăn"), ("clb_lamvuon", "CLB Làm vườn"),
    ("clb_tienganh", "CLB Tiếng Anh"), ("clb_khoahoc", "CLB Khoa học"),
    ("clb_nhiepanh", "CLB Nhiếp ảnh"), ("clb_khieuvu", "CLB Khiêu vũ"),
    ("clb_tranhbien", "CLB Tranh biện"), ("clb_tinhnguyen", "CLB Tình nguyện"),
    ("clb_dangian", "CLB Trò chơi dân gian"), ("clb_thuvien", "CLB Thư viện"),
    ("clb_bcs", "CLB Báo chí"), ("clb_coking", "CLB Cờ tướng"),
]


def sinh_ngau_nhien(n_hs, ds_buoi, clb_moi_buoi, seed, do_choi=1.15,
                    ti_le_du_tru=0.35, ti_le_co_thi=0.34):
    """Một trường ngẫu nhiên nhưng luôn hợp lệ. Tất định theo `seed`.

    `do_choi` — tổng chỗ so với số học sinh. 1.15 nghĩa là chỗ nhiều hơn nhu
    cầu 15%, đủ chật để kết quả có ý nghĩa, đủ rộng để không quá nửa trường
    trắng tay.
    """
    rnd = random.Random(seed)
    if clb_moi_buoi * len(ds_buoi) > len(_CHU_DE):
        raise SystemExit("Chỉ có %d chủ đề câu lạc bộ sẵn, không đủ cho %d câu lạc bộ"
                         % (len(_CHU_DE), clb_moi_buoi * len(ds_buoi)))

    chu_de = _CHU_DE[:]
    rnd.shuffle(chu_de)
    nhom_du_tru = ["chinh_sach", "khoi_10"]

    clb, k = [], 0
    for b in ds_buoi:
        # Tong cho moi buoi ~ n_hs * do_choi / so buoi, chia deu cho cac CLB
        cho_buoi = max(clb_moi_buoi, int(round(n_hs * do_choi / len(ds_buoi))))
        phan = [cho_buoi // clb_moi_buoi] * clb_moi_buoi
        for i in range(cho_buoi - sum(phan)):
            phan[i] += 1
        for i in range(clb_moi_buoi):
            cid, ten = chu_de[k]; k += 1
            suc = max(2, phan[i])
            co_du = rnd.random() < ti_le_du_tru
            clb.append({
                "club_id": cid, "name": ten, "capacity": suc,
                "reserve_capacity": max(1, int(suc * 0.2)) if co_du else 0,
                "reserve_group": rnd.choice(nhom_du_tru) if co_du else "",
                "buoi": b,
            })

    theo_buoi = {}
    for c in clb:
        theo_buoi.setdefault(c["buoi"], []).append(c["club_id"])
    co_thi = {c["club_id"] for c in clb if rnd.random() < ti_le_co_thi}

    # CHI GAN NHOM MA CO CAU LAC BO THAT SU DANH SUAT CHO.
    #
    # Gan bua tu bang `nhom_du_tru` thi gap truong hop khong cau lac bo nao
    # dat suat cho "khoi_10" — luc do nhung em mang nhan do co mot cai nhan
    # khong dem lai gi o bat ky dau. Phan mem goi do la "nhom mo coi" va
    # canh bao muc CAO, dung. Do duoc: truong 3 cau lac bo, 40 em -> 9 em
    # mang nhan mo coi va 2 canh bao khi nhap.
    nhom_co_that = sorted({c["reserve_group"] for c in clb if c["reserve_group"]})

    hs = []
    for i in range(1, n_hs + 1):
        sid = "HS%03d" % i
        ten = "%s %s %s" % (rnd.choice(_HO), rnd.choice(_DEM), rnd.choice(_TEN))
        nhom = (rnd.choice(nhom_co_that)
                if nhom_co_that and rnd.random() < 0.22 else "")
        nv, diem = {}, {}
        for b, ds in theo_buoi.items():
            # Mot so em bo trong ca mot buoi — ngay do em ban. Day la du lieu
            # HOP LE, khong phai thieu sot.
            if rnd.random() < 0.12:
                nv[b] = []
                continue
            k_nv = min(len(ds), rnd.randint(1, min(3, len(ds))))
            chon = rnd.sample(ds, k_nv)
            nv[b] = chon
            # Chi cham diem cho CLB em CO khai nguyen vong va CLB do co thi
            for cid in chon:
                if cid in co_thi and rnd.random() < 0.8:
                    if len([c for c in diem if c in theo_buoi[b]]) < TRAN_CLB_THI_MOI_BUOI:
                        # Dau phay thap phan — dung cach Excel ban tieng Viet luu
                        diem[cid] = "%.1f" % rnd.uniform(4.0, 10.0).__round__(1)
                        diem[cid] = diem[cid].replace(".", ",")

        # MOI EM PHAI KHAI IT NHAT MOT NGUYEN VONG CA TUAN.
        #
        # Bo trong MOT buoi la "ngay do em ban" — hop le. Bo trong MOI buoi
        # la "em khong dang ky gi ca", va phan mem canh bao dung: em do chac
        # chan trang tay, khong phai vi thua ai ma vi chua bao gio vao cuoc.
        # O truong mot buoi, xac suat 12% ay ap len ca "tuan", nen khong chan
        # thi cu 100 em lai co ~12 em nhu vay.
        if not any(nv.values()):
            b = rnd.choice(list(theo_buoi))
            nv[b] = [rnd.choice(theo_buoi[b])]

        hs.append({"student_id": sid, "name": ten, "reserve_group": nhom,
                   "nguyen_vong": nv, "diem": diem})

    # VA CHIEU NGUOC LAI: moi nhom co cau lac bo dat suat thi phai co NGUOI.
    #
    # Day la mat guong cua khoi tren. Mot cau lac bo giu 1 cho cho
    # "chinh_sach" ma ca truong khong em nao thuoc dien do thi cho ay khong
    # ai nhan duoc — phan mem canh bao `health_club_group_no_students`, dung.
    # Truong it hoc sinh moi gap: 20 em, moi em 22% co nhom, boc ra toan
    # "khoi_10" la chuyen binh thuong. Do duoc: 1 tren 90 cau hinh da thu.
    for g in nhom_co_that:
        if any(h["reserve_group"] == g for h in hs):
            continue
        # Uu tien em CHUA co nhom de khong cuop nhan cua nhom khac.
        chua = [h for h in hs if not h["reserve_group"]] or hs
        rnd.choice(chua)["reserve_group"] = g

    return clb, hs


# ---------------------------------------------------------------------------
# ĐIỂM QUYẾT TÂM (mục A13) — dữ liệu MÔ PHỎNG
# ---------------------------------------------------------------------------

def lam_tron_100(trong_so):
    """{club_id: trọng số nguyên >= 0} -> {club_id: điểm nguyên}, tổng ĐÚNG `NGAN_SACH_DQT`.

    Phần dư lớn nhất được cộng thêm 1 điểm; hoà thì theo mã CLB. Toàn số nguyên nên không có
    sai số làm tròn, và cùng đầu vào luôn ra cùng đầu ra. Trọng số toàn 0 thì chia đều.
    """
    ma = sorted(trong_so)
    tong = sum(trong_so.values())
    if tong <= 0:
        trong_so, tong = {c: 1 for c in ma}, len(ma)
    nen = {c: NGAN_SACH_DQT * trong_so[c] // tong for c in ma}
    du = {c: NGAN_SACH_DQT * trong_so[c] % tong for c in ma}
    thieu = NGAN_SACH_DQT - sum(nen.values())
    for c in sorted(ma, key=lambda c: (-du[c], c))[:thieu]:
        nen[c] += 1
    return nen


def chia_mot_quy(ds, kieu, rnd):
    """Chia `NGAN_SACH_DQT` điểm cho danh sách CLB `ds` (đã theo thứ tự nguyện vọng)."""
    if len(ds) == 1:
        return {ds[0]: NGAN_SACH_DQT}
    n = len(ds)
    if kieu == "don_dau":                  # dồn vào nguyện vọng đầu, giảm dần theo thứ hạng
        tr = {c: 2 ** (n - 1 - i) for i, c in enumerate(ds)}
    elif kieu == "deu":
        tr = {c: 1 for c in ds}
    elif kieu == "all_in":                 # toàn bộ vào MỘT CLB (chọn ngẫu nhiên, không nhất thiết đầu)
        dich = rnd.randrange(n)
        tr = {c: (1 if i == dich else 0) for i, c in enumerate(ds)}
    elif kieu == "ngau_nhien":
        tr = {c: rnd.randint(1, 100) for c in ds}
    else:
        raise ValueError("kiểu chia lạ: %r" % (kieu,))
    return lam_tron_100(tr)


def _quy_theo_thu_tu(clb, h):
    """`cac_quy` nhưng theo thứ tự ổn định (buổi theo thứ tự câu lạc bộ, rồi quỹ 1, quỹ 2)."""
    ds_buoi = []
    for c in clb:
        b = c.get("buoi") or ""
        if b not in ds_buoi:
            ds_buoi.append(b)
    q = cac_quy(clb, h)
    return sorted(q.items(), key=lambda kv: (ds_buoi.index(kv[0][0]), kv[0][1]))


def ap_diem_quyet_tam(clb, hs, seed, che_do="hop_le", kieu_chia="tron", so_em_moi_loai=3):
    """Áp Điểm quyết tâm lên danh sách học sinh `hs`, SỬA TẠI CHỖ. Tất định theo `seed`.

    Trả `(kieu, bang_loi)`: `kieu` {student_id: kiểu chia}, `bang_loi` danh sách em lỗi (rỗng
    nếu không phải `co_loi`). Không đụng nguyện vọng hay điểm thi của em.

    `che_do`:
      * `khong`  — không làm gì (hành vi cũ);
      * `trong`  — không đặt điểm nào; sổ vẫn có cột (xem `ghi_bo(cfg=CFG_DQT)`);
      * `hop_le` — mọi quỹ của mọi buổi đủ 100 cho đúng tập CLB;
      * `co_loi` — như `hop_le`, rồi cố ý làm sai `so_em_moi_loai` em cho MỖI loại trong
        `LOAI_LOI_DQT`; mỗi em chỉ sai một loại, ghi trong `bang_loi`.

    `kieu_chia`: `tron` (mỗi em một kiểu bốc ngẫu nhiên trong `KIEU_CHIA`) hoặc đúng một kiểu
    cho cả trường. Em có quỹ một CLB thì luôn 100 bất kể kiểu.
    """
    if che_do not in CHE_DO_DQT:
        raise ValueError("chế độ lạ: %r" % (che_do,))
    if kieu_chia != "tron" and kieu_chia not in KIEU_CHIA:
        raise ValueError("kiểu chia lạ: %r" % (kieu_chia,))
    if che_do in ("khong", "trong"):
        for h in hs:
            h.pop("diem_quyet_tam", None)
            h.pop("dqt_mo_coi", None)
        return {}, []

    rnd = random.Random(seed)
    kieu = {}
    for h in hs:
        k = rnd.choice(KIEU_CHIA) if kieu_chia == "tron" else kieu_chia
        kieu[h["student_id"]] = k
        h["diem_quyet_tam"] = {}
        for (_b, _q), ds in _quy_theo_thu_tu(clb, h):
            h["diem_quyet_tam"].update(chia_mot_quy(ds, k, rnd))
    if che_do == "hop_le":
        return kieu, []
    return kieu, _lam_loi(clb, hs, rnd, so_em_moi_loai)


def _lam_loi(clb, hs, rnd, moi_loai):
    """Cố ý làm sai hồ sơ của `moi_loai` em cho mỗi loại lỗi. Trả bảng lỗi.

    Mỗi dòng: student_id, loai, mo_ta, `loi_pipeline` (mã lỗi, quỹ, buổi mà bước Kiểm tra dữ
    liệu phải báo) và `canh_bao_nhap` (cảnh báo lúc nạp sổ). Sổ chỉ có MỘT ô điểm cạnh mỗi
    nguyện vọng, và tầng của ô do tick thi quyết định, nên hai loại lỗi được thể hiện như sau:
      * `ngoai_nguyen_vong`: điểm nằm ở ô cạnh một ô nguyện vọng TRỐNG; phần mềm bỏ ô đó (cảnh
        báo lúc nạp) và quỹ còn lại thiếu đúng số điểm ấy;
      * `tang_lech`: em chia MỘT quỹ chung cho cả CLB có thi lẫn không thi của một buổi; mỗi
        quỹ vì thế thiếu điểm.
    """
    thu_tu = list(range(len(hs)))
    rnd.shuffle(thu_tu)
    da_dung = set()
    bang = []

    def lay(dieu_kien):
        for i in thu_tu:
            if i not in da_dung and dieu_kien(hs[i]):
                da_dung.add(i)
                return hs[i]
        raise SystemExit("Không đủ học sinh để cài lỗi")

    def chon_quy(h, can_hai_clb=False):
        q = [kv for kv in _quy_theo_thu_tu(clb, h) if len(kv[1]) >= (2 if can_hai_clb else 1)]
        return q[rnd.randrange(len(q))] if q else None

    def mot(loai, mo_ta, loi_pipeline, h, canh_bao_nhap=()):
        bang.append({"student_id": h["student_id"], "loai": loai, "mo_ta": mo_ta,
                     "loi_pipeline": [{"code": c, "quy": q, "buoi": b} for c, q, b in loi_pipeline],
                     "canh_bao_nhap": list(canh_bao_nhap)})

    for _ in range(moi_loai):
        h = lay(lambda h: bool(cac_quy(clb, h)))
        (b, q), ds = chon_quy(h)
        w = h["diem_quyet_tam"]
        cid = max(ds, key=lambda c: (w[c], c))
        d = rnd.randint(1, min(30, w[cid]))
        w[cid] -= d
        mot("thieu", "quỹ %d buổi %s thiếu %d điểm (tổng %d)" % (q, b, d, NGAN_SACH_DQT - d),
            [("wharton_chua_dung_het", q, b)], h)

    for _ in range(moi_loai):
        h = lay(lambda h: bool(cac_quy(clb, h)))
        (b, q), ds = chon_quy(h)
        w = h["diem_quyet_tam"]
        cid = ds[rnd.randrange(len(ds))]
        d = rnd.randint(1, 30)
        w[cid] += d
        mot("thua", "quỹ %d buổi %s thừa %d điểm (tổng %d)" % (q, b, d, NGAN_SACH_DQT + d),
            [("wharton_vuot_ngan_sach", q, b)], h)

    for _ in range(moi_loai):
        h = lay(lambda h: bool(cac_quy(clb, h)))
        (b, q), ds = chon_quy(h)
        w = h["diem_quyet_tam"]
        cid = max(ds, key=lambda c: (w[c], c))
        d = rnd.randint(1, min(25, w[cid]))
        w[cid] -= d
        h["dqt_mo_coi"] = [d]
        mot("ngoai_nguyen_vong",
            "%d điểm đặt ở ô cạnh nguyện vọng trống; quỹ %d buổi %s còn thiếu %d" % (d, q, b, d),
            [("wharton_chua_dung_het", q, b)], h, ["csv_wp_khong_co_nguyen_vong"])

    def co_hai_tang(h):
        q = cac_quy(clb, h)
        return any((b0, 1) in q and (b0, 2) in q for (b0, _q) in q)

    for _ in range(moi_loai):
        h = lay(co_hai_tang)
        q_h = cac_quy(clb, h)
        b = next(b0 for (b0, _q) in sorted(q_h) if (b0, 1) in q_h and (b0, 2) in q_h)
        ds = q_h[(b, 1)] + q_h[(b, 2)]
        h["diem_quyet_tam"].update(lam_tron_100({c: 1 for c in ds}))
        mot("tang_lech",
            "một quỹ chung %d điểm cho cả CLB có thi và không thi của buổi %s" % (NGAN_SACH_DQT, b),
            [("wharton_chua_dung_het", 1, b), ("wharton_chua_dung_het", 2, b)], h)

    for _ in range(moi_loai):
        h = lay(lambda h: bool(cac_quy(clb, h)))
        for c in h["diem_quyet_tam"]:
            h["diem_quyet_tam"][c] = 0
        mot("toan_0", "mọi ô điểm quyết tâm bằng 0",
            [("wharton_chua_dung_het", q, b) for (b, q), _ds in _quy_theo_thu_tu(clb, h)], h)
    return bang


def ap_len_so_co_san(duong_vao, thu_muc_ra, ten_tep, seed, che_do, kieu_chia,
                     so_em_moi_loai=3):
    """Đọc một sổ đã có, giữ nguyên CLB, nguyện vọng, điểm thi; thêm Điểm quyết tâm; ghi tệp mới.

    Trả `(đường dẫn, kiểu chia, bảng lỗi)`. Sổ gốc phải qua `soat` trước, và (ở chế độ
    `hop_le`) hồ sơ điểm phải qua `soat_diem_quyet_tam`; sai thì ném SystemExit, không ghi gì.
    """
    clb, hs = doc_bo(duong_vao)
    loi = soat(clb, hs)
    if loi:
        raise SystemExit("Sổ gốc không hợp lệ:\n   ✗ " + "\n   ✗ ".join(loi))
    kieu, bang = ap_diem_quyet_tam(clb, hs, seed, che_do, kieu_chia, so_em_moi_loai)
    if che_do == "hop_le":
        loi = soat_diem_quyet_tam(clb, hs)
        if loi:
            raise SystemExit("Điểm quyết tâm không hợp lệ:\n   ✗ " + "\n   ✗ ".join(loi))
    cfg = CFG_DQT if che_do != "khong" else None
    return ghi_bo(thu_muc_ra, clb, hs, cfg, ten_tep)[0], kieu, bang


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _in_ket_qua(clb, hs, loi, canh_bao):
    if loi:
        print("KHÔNG HỢP LỆ — %d lỗi:" % len(loi), file=sys.stderr)
        for e in loi:
            print("   ✗", e, file=sys.stderr)
        return 1
    print("Hợp lệ: %d câu lạc bộ · %d buổi · %d học sinh · %d ô điểm"
          % (len(clb), len({c.get("buoi") or "" for c in clb}), len(hs),
             sum(len(h.get("diem") or {}) for h in hs)))
    for w in canh_bao:
        print("   ⚠", w)
    return 0


def _them_tuy_chon_dqt(parser, mac_dinh="khong"):
    parser.add_argument("--diem-quyet-tam", choices=CHE_DO_DQT, default=mac_dinh,
                        help="sinh Điểm quyết tâm (mục A13); khong = như cũ")
    parser.add_argument("--kieu-chia", choices=("tron",) + KIEU_CHIA, default="tron",
                        help="kiểu chia điểm; tron = mỗi em một kiểu")


def _ghi_json_dqt(thu_muc, ten_tep, kieu, bang, che_do):
    """Ghi DQT_KIEU_CHIA.json (và DQT_BANG_LOI.json khi co_loi): {tên tệp: ...}."""
    cac = [("DQT_KIEU_CHIA.json", kieu)] + (
        [("DQT_BANG_LOI.json", bang)] if che_do == "co_loi" else [])
    for ten, noi_dung in cac:
        with io.open(os.path.join(thu_muc, ten), "w", encoding="utf-8") as f:
            json.dump({ten_tep: noi_dung}, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write("\n")


def main(argv=None):
    # Cua so lenh / ong dan tren Windows mac dinh la cp1252: in tieng Viet
    # se nem UnicodeEncodeError va script thoat voi ma 1.
    for _luong in (sys.stdout, sys.stderr):
        if hasattr(_luong, "reconfigure"):
            _luong.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="lenh", required=True)

    a = sub.add_parser("tao", help="dựng từ bản khai báo JSON")
    a.add_argument("--spec", required=True)
    a.add_argument("--ra", required=True)
    _them_tuy_chon_dqt(a)

    b = sub.add_parser("ngau", help="dựng một trường ngẫu nhiên nhưng hợp lệ")
    b.add_argument("--ra", required=True)
    b.add_argument("--hoc-sinh", type=int, default=120)
    b.add_argument("--buoi", default="", help="vd thu_2,thu_4,thu_6 — bỏ trống = một buổi")
    b.add_argument("--clb-moi-buoi", type=int, default=3)
    b.add_argument("--seed", type=int, default=42)
    b.add_argument("--do-choi", type=float, default=1.15)
    _them_tuy_chon_dqt(b)

    d = sub.add_parser("ap", help="áp Điểm quyết tâm lên một sổ đã có (giữ nguyên nguyện vọng và điểm thi)")
    d.add_argument("so", help="tệp .xlsx gốc")
    d.add_argument("--ra", required=True)
    d.add_argument("--ten-tep", default=TEN_SO)
    d.add_argument("--seed", type=int, default=42)
    _them_tuy_chon_dqt(d, mac_dinh="hop_le")

    c = sub.add_parser("soat", help="soát một sổ nhập (hoặc bộ ba CSV cũ), không sửa gì")
    c.add_argument("thu_muc", help="tệp SO_NHAP_CLB.xlsx, hoặc thư mục chứa nó / bộ ba CSV")

    ns = p.parse_args(argv)

    if ns.lenh == "ap":
        if ns.diem_quyet_tam == "khong":
            print("--diem-quyet-tam khong: không có gì để áp.", file=sys.stderr)
            return 1
        duong, kieu, bang = ap_len_so_co_san(ns.so, ns.ra, ns.ten_tep, ns.seed,
                                             ns.diem_quyet_tam, ns.kieu_chia)
        _ghi_json_dqt(ns.ra, ns.ten_tep, kieu, bang, ns.diem_quyet_tam)
        print("   →", duong)
        return 0

    if ns.lenh == "soat":
        clb, hs = doc_bo(ns.thu_muc)
        loi = soat(clb, hs)
        if any(h.get("diem_quyet_tam") or h.get("dqt_mo_coi") for h in hs):
            loi += soat_diem_quyet_tam(clb, hs)   # sổ có Điểm quyết tâm thì soát luôn hồ sơ điểm
        return _in_ket_qua(clb, hs, loi, canh_bao_men(clb, hs))

    if ns.lenh == "tao":
        with io.open(ns.spec, encoding="utf-8") as f:
            spec = json.load(f)
        clb, hs = spec["cau_lac_bo"], spec["hoc_sinh"]
    else:
        ds_buoi = [x.strip() for x in ns.buoi.split(",") if x.strip()] or [""]
        la = [b for b in ds_buoi if b and b not in BUOI_CHUAN]
        if la:
            print("Nhãn buổi lạ: %s (nên dùng: %s)" % (", ".join(la),
                  ", ".join(BUOI_CHUAN)), file=sys.stderr)
        clb, hs = sinh_ngau_nhien(ns.hoc_sinh, ds_buoi, ns.clb_moi_buoi,
                                  ns.seed, ns.do_choi)

    kieu, bang = ap_diem_quyet_tam(clb, hs, ns.seed if ns.lenh == "ngau" else 42,
                                   ns.diem_quyet_tam, ns.kieu_chia)
    loi = soat(clb, hs)
    if ns.diem_quyet_tam == "hop_le":
        loi += soat_diem_quyet_tam(clb, hs)       # co_loi: lỗi là CỐ Ý, bảng lỗi ghi lại
    ma = _in_ket_qua(clb, hs, loi, canh_bao_men(clb, hs))
    if ma:
        print("\nKhông ghi tệp nào.", file=sys.stderr)
        return ma
    cfg = CFG_DQT if ns.diem_quyet_tam != "khong" else None
    for d in ghi_bo(ns.ra, clb, hs, cfg):
        print("   →", d)
    if cfg:
        _ghi_json_dqt(ns.ra, TEN_SO, kieu, bang, ns.diem_quyet_tam)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
