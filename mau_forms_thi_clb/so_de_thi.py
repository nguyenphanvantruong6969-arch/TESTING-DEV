"""so_de_thi.py — Excel đề thi của kiosk <-> dict dạng `de_thi.json` (FA-M7; TH = chưa thử trên Microsoft/Google thật).

Một nguồn: CLB nhập MỘT lần (Phiếu thiết lập CLB, bước 1), đề thi nhập trong MỘT tệp Excel (bước 2); không ai sửa tay
`de_thi.json`. Dạng tệp theo `MAU_DE_THI.xlsx` của Google (trang `Cai_dat`, `CLB`, `De_thi`) cộng cột `de` (A/B/C,
trống = A) cho đề biến thể.

  * `ghi_mau_kiosk(duong, clubs, de=None)`  tệp mẫu: `CLB` điền sẵn từ bước 1; `De_thi` trống (hoặc điền từ `de`);
  * `doc_so_de_thi(duong, clubs)`           -> (de, loi): `de` cùng dạng `de_thi.json`, hoặc None kèm MỌI lỗi;
  * `doc_clb_dot(duong_so_nhap)`            CLB của bước 1 đọc lại từ `SO_NHAP_CLB_CLB.xlsx`.
Không nhập gì từ `.claude/skills/` (đường Google giữ nguyên). Dữ liệu trong test là MÔ PHỎNG.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bieu_mau  # noqa: E402
import phan_tich_cau_hoi  # noqa: E402
import so_nhap  # noqa: E402

TIEU_DE_MAC_DINH = "Đăng ký CLB và thi tuyển"
DIEM_MOI_CAU_MAC_DINH = 2
COT_DE_THI = ["club_id", "de", "cau_hoi", "lua_chon_a", "lua_chon_b", "lua_chon_c", "lua_chon_d", "dap_an"]
COT_BAT_BUOC = [c for c in COT_DE_THI if c != "de"]
COT_CLB = ["buoi", "ten_buoi", "club_id", "ten_clb"]
CHU_LUA_CHON = "abcd"
CHU_DE = phan_tich_cau_hoi.CHU_BIEN_THE          # "ABC"
_HUONG_DAN = [
    "CÁCH ĐIỀN TỆP NÀY",
    "",
    "Trang Cai_dat: tiêu đề biểu mẫu (tieu_de) và điểm mỗi câu (diem_moi_cau).",
    "Trang CLB: danh sách CLB lấy từ bước 1, CHỈ ĐỂ ĐỌC. Muốn đổi CLB thì làm lại bước 1, không sửa ở đây.",
    "Trang De_thi: mỗi câu hỏi một dòng, 4 lựa chọn (lua_chon_a..d) đều phải điền.",
    "  club_id   mã CLB đúng như trang CLB (CLB không có dòng nào = không tổ chức thi)",
    "  de        A, B hoặc C; để trống = đề A. Đề B, C (nếu có) phải cùng số câu với đề A",
    "  dap_an    một chữ a, b, c hoặc d",
]


def _o(v):
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


def _thu_tu_buoi(ma):
    ds = [m for _, m in so_nhap.NHAN_BUOI]
    return (ds.index(ma), "") if ma in ds else (len(ds), ma)


def _buoi_tu_clb(clubs):
    """Các buổi có CLB, theo thứ tự trong tuần (buổi lạ xếp sau), kèm nhãn hiển thị."""
    ma = sorted({c.get("buoi", "") for c in clubs if c.get("buoi", "")}, key=_thu_tu_buoi)
    return [{"ma": m, "ten": so_nhap.nhan_buoi(m)} for m in ma]


def ghi_mau_kiosk(duong, clubs, de=None):
    """Ghi tệp Excel đề thi. `clubs`: [{club_id, name, buoi, ...}] (bước 1). `de` (tuỳ chọn): dict dạng
    `de_thi.json` để điền sẵn tiêu đề, điểm và các câu hỏi (dùng cho thử khứ hồi và cho người muốn sửa đề cũ)."""
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Cai_dat"
    ws.append(["khoa", "gia_tri"])
    ws.append(["tieu_de", (de or {}).get("tieu_de", TIEU_DE_MAC_DINH)])
    ws.append(["diem_moi_cau", (de or {}).get("diem_moi_cau", DIEM_MOI_CAU_MAC_DINH)])
    ws = wb.create_sheet("CLB")
    ws.append(COT_CLB)
    for c in clubs:
        ws.append([c.get("buoi", ""), so_nhap.nhan_buoi(c.get("buoi", "")), c["club_id"], c.get("name", "")])
    ws = wb.create_sheet("De_thi")
    ws.append(COT_DE_THI)
    for c in (de or {}).get("cau_lac_bo", []):
        for i, bai in enumerate(phan_tich_cau_hoi.cac_bien_the(c)):
            for q in bai:
                lc = list(q["lua_chon"])[:4]
                lc += [""] * (4 - len(lc))
                ws.append([c["club_id"], CHU_DE[i], q["cau"], *lc, CHU_LUA_CHON[q["dap_an"]]])
    ws = wb.create_sheet("Huong_dan")
    for dong in _HUONG_DAN:
        ws.append([dong])
    os.makedirs(os.path.dirname(os.path.abspath(duong)), exist_ok=True)
    wb.save(duong)
    return duong


def doc_clb_dot(duong_so_nhap):
    """CLB của bước 1 (`forms/SO_NHAP_CLB_CLB.xlsx`). Thiếu tệp -> FileNotFoundError."""
    import openpyxl
    if not os.path.isfile(duong_so_nhap):
        raise FileNotFoundError(duong_so_nhap)
    wb = openpyxl.load_workbook(duong_so_nhap, read_only=True, data_only=True)
    try:
        du = so_nhap.doc_so_nhap(wb)
    finally:
        wb.close()
    return [{k: c.get(k) for k in ("club_id", "name", "buoi", "capacity", "reserve_capacity", "reserve_group", "loai")}
            for c in du["clubs"]]


def _doc_cai_dat(wb, loi):
    ten, diem = TIEU_DE_MAC_DINH, DIEM_MOI_CAU_MAC_DINH
    if "Cai_dat" not in wb.sheetnames:
        return ten, diem
    for r in wb["Cai_dat"].iter_rows(min_row=2, values_only=True):
        khoa, gt = _o(r[0]), (r[1] if len(r) > 1 else None)
        if khoa == "tieu_de" and _o(gt):
            ten = _o(gt)
        elif khoa == "diem_moi_cau":
            try:
                diem = float(str(gt).replace(",", "."))
                diem = int(diem) if diem.is_integer() else diem
                if diem <= 0:
                    raise ValueError
            except ValueError:
                loi.append("trang Cai_dat: diem_moi_cau phải là số dương, đang là %r" % _o(gt))
                diem = DIEM_MOI_CAU_MAC_DINH
    return ten, diem


def _doc_de_thi_sheet(ws, theo_ma, loi):
    """-> {club_id: {chữ đề: [câu]}}; thêm lỗi vào `loi`. Dòng có lỗi KHÔNG vào kết quả."""
    dong = [[_o(x) for x in r] for r in ws.iter_rows(values_only=True)]
    if not dong:
        loi.append("trang De_thi trống")
        return {}, set()
    tieu = dong[0]
    thieu = [c for c in COT_BAT_BUOC if c not in tieu]
    if thieu:
        loi.append("trang De_thi thiếu cột: %s" % ", ".join(thieu))
        return {}, set()
    vt = {c: tieu.index(c) for c in COT_DE_THI if c in tieu}

    def o(r, c):
        return r[vt[c]] if c in vt and vt[c] < len(r) else ""

    bai, co_loi, clb_la = {}, set(), set()
    for so_dong, r in enumerate(dong[1:], 2):
        if not any(r):
            continue
        ma = o(r, "club_id")
        sai = []
        if not ma:
            loi.append("dòng %d: thiếu club_id" % so_dong)
            continue
        if ma not in theo_ma:                           # đối chiếu với bước 1: CLB phải đã có ở đó
            if ma not in clb_la:
                loi.append("dòng %d: CLB %r có trong trang De_thi nhưng không có trong bước 1 "
                           "(danh sách CLB đã nạp); sửa mã hoặc làm lại bước 1" % (so_dong, ma))
                clb_la.add(ma)
            continue
        chu_de = o(r, "de").upper() or "A"
        if chu_de not in CHU_DE:
            sai.append("dòng %d (%s): cột de là %r, chỉ được A, B, C (trống = A)" % (so_dong, ma, o(r, "de")))
        if not o(r, "cau_hoi"):
            sai.append("dòng %d (%s): thiếu nội dung câu hỏi (cau_hoi)" % (so_dong, ma))
        lc = []
        for ch in CHU_LUA_CHON:
            v = o(r, "lua_chon_" + ch)
            if not v:
                sai.append("dòng %d (%s): lua_chon_%s để trống" % (so_dong, ma, ch))
            lc.append(v)
        dap = o(r, "dap_an").lower()
        if dap not in tuple(CHU_LUA_CHON):
            sai.append("dòng %d (%s): dap_an %r phải là một chữ a, b, c hoặc d" % (so_dong, ma, o(r, "dap_an")))
        if sai:
            loi.extend(sai)
            co_loi.add(ma)
            continue
        bai.setdefault(ma, {}).setdefault(chu_de, []).append(
            {"cau": o(r, "cau_hoi"), "lua_chon": lc, "dap_an": CHU_LUA_CHON.index(dap)})
    return bai, co_loi


def doc_so_de_thi(duong, clubs):
    """Đọc tệp đề -> (de, loi). `clubs`: CLB của bước 1 (`doc_clb_dot`). `de` cùng dạng `de_thi.json` (không có
    `_ghi_chu`); có lỗi thì `de` là None và `loi` liệt kê MỌI lỗi (không dừng ở lỗi đầu). CLB không có câu nào = không thi."""
    import openpyxl
    loi = []
    try:
        wb = openpyxl.load_workbook(duong, read_only=True, data_only=True)
    except Exception as e:                               # không phải xlsx, hỏng zip...
        return None, ["không đọc được tệp Excel: %s" % e]
    try:
        if "De_thi" not in wb.sheetnames:
            return None, ["tệp không có trang De_thi (dùng đúng tệp mẫu của bước 2)"]
        ten, diem = _doc_cai_dat(wb, loi)
        theo_ma = {c["club_id"]: c for c in clubs}
        bai, co_loi = _doc_de_thi_sheet(wb["De_thi"], theo_ma, loi)
    finally:
        wb.close()
    cau_lac_bo = []
    for c in clubs:
        ma = c["club_id"]
        moi = {"club_id": ma, "name": c["name"], "buoi": c.get("buoi") or "",
               "capacity": c["capacity"], "reserve_capacity": c.get("reserve_capacity") or 0,
               "reserve_group": c.get("reserve_group") or "", "de_thi": []}
        theo_de = bai.get(ma, {})
        co = [d for d in CHU_DE if d in theo_de]
        if ma not in co_loi and co:
            if co != list(CHU_DE[:len(co)]):
                loi.append("%s: có đề %s nhưng thiếu đề trước đó (đề A, rồi B, rồi C, không bỏ đề giữa)"
                           % (ma, ", ".join(co)))
            else:
                moi["de_thi"] = theo_de["A"]
                if len(co) > 1:
                    moi["de_thi_bien_the"] = [theo_de[d] for d in co[1:]]
                loi.extend(phan_tich_cau_hoi.kiem_bien_the(moi))
        cau_lac_bo.append(moi)
    de = {"tieu_de": ten, "diem_moi_cau": diem, "buoi": _buoi_tu_clb(clubs), "cau_lac_bo": cau_lac_bo}
    try:
        bieu_mau.soat_de_thi(de)
    except bieu_mau.LoiDeThi as e:
        loi.extend(d.strip()[2:].strip() for d in str(e).splitlines()[1:] if d.strip())
    return (None if loi else de), loi
