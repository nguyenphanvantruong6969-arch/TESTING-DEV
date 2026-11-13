"""Phần dùng chung của mẫu Microsoft Forms "Đăng ký CLB và thi tuyển".

Một nguồn duy nhất — `de_thi.json` — sinh ra mọi thứ: tệp Quick Import,
bảng cài đặt Forms, tệp xuất mẫu, và là đáp án để chấm lại bài. Tên câu
hỏi cũng chỉ được dựng ở ĐÂY: biểu mẫu và bộ chuyển đổi cùng gọi một hàm,
nên không thể lệch nhau.

Mỗi câu hỏi mở đầu bằng một MÃ trong ngoặc vuông. Forms lấy nguyên văn câu
hỏi làm tên cột khi xuất Excel, nên bộ chuyển đổi chỉ cần đọc phần trong
ngoặc — sửa lời câu hỏi trên Forms không làm hỏng việc đọc tệp.

    [student_id]      mã học sinh
    [name]            họ tên
    [thu_2]           câu Ranking nguyện vọng của buổi thu_2
    [thi-clb_covua]   câu cổng "Em có dự thi CLB Cờ vua không?"
    [clb_covua-3]     câu 3 trong đề thi của CLB Cờ vua
"""

import contextvars
import json
import os
import re
from contextlib import contextmanager

THU_MUC = os.path.dirname(os.path.abspath(__file__))
DE_THI_MAC_DINH = os.path.join(THU_MUC, "de_thi.json")

# Trần của phần mềm (xem BO_CAU_HOI_FORMS.md mục 2). Để biểu mẫu vượt trần
# là dựng sẵn cái bẫy: học sinh điền hợp lệ theo Forms mà phần mềm không nhập.
TRAN_CLB_MOI_BUOI = 10
TRAN_THI_MOI_BUOI = 5
# Trần của Microsoft Forms: 200 câu mỗi biểu mẫu (support.microsoft.com, đọc 05/11/2026;
# T4M_KET_QUA_TAI_LIEU.md mục 7.1). Chế độ "chỉ thi" tách theo buổi khi vượt.
TRAN_CAU_MOI_BIEU_MAU = 200

CO = "Có, em làm bài thi ngay bây giờ"
KHONG = "Không"

_MA_CLB = re.compile(r"^[A-Za-z0-9_]+$")
# Forms đôi khi giữ số thứ tự "3." của Quick Import trong tên câu hỏi.
_MA_CAU = re.compile(r"^\s*(?:\d+[.)]\s*)?\[([^\]]+)\]")
_MA_TRONG_LUA_CHON = re.compile(r"\(([A-Za-z0-9_]+)\)\s*$")
_RE_THE_DAU = re.compile(r"^\s*(?:\d+[.)]\s*)?\[[^\]]+\]\s*")
_RE_SO_THU_TU = re.compile(r"^\s*\d+[.)]\s*")


class LoiDeThi(ValueError):
    """de_thi.json sai — không sinh gì cả."""


# ---- SG-12 (H2): tiêu đề THUẦN cho học sinh, mã chỉ nằm trong bản đồ ----
# Mặc định học sinh KHÔNG thấy `[thu_2-nv1]` hay `(clb_bong_ro)`: bộ sinh ghi tiêu đề thuần và một tệp `MAP_*.json`
# (tiêu đề thuần -> mã, lựa chọn thuần -> mã). Cờ `--giu-ma` của bộ sinh giữ nguyên tiêu đề có mã như trước (đúng từng
# byte). Mọi hàm dựng tên câu / lựa chọn trả về chuỗi `TieuDe` / `LuaChon`: chữ hiển thị tuỳ chế độ, nhưng LUÔN mang
# mã (`.ma`), bản có mã (`.co_ma`) và bản thuần (`.thuan`) — nên mọi nơi bên trong dùng được cả hai mà không đoán.
_GIU_MA = contextvars.ContextVar("rbda_giu_ma", default=False)


def dat_giu_ma(co):
    """Bật / tắt giữ mã trong tiêu đề (mặc định tắt = tiêu đề thuần). Theo ngữ cảnh luồng, không phải biến toàn cục."""
    _GIU_MA.set(bool(co))


def dang_giu_ma():
    return _GIU_MA.get()


@contextmanager
def che_do_giu_ma(co):
    token = _GIU_MA.set(bool(co))
    try:
        yield
    finally:
        _GIU_MA.reset(token)


class TieuDe(str):
    """Tên một câu hỏi: là chuỗi sẽ ghi lên biểu mẫu; `.ma` mã câu, `.co_ma` bản "[mã] …", `.thuan` bản không mã."""
    ma = None
    co_ma = ""
    thuan = ""


class LuaChon(str):
    """Một lựa chọn có mã: `.ma` mã (club_id, hay giá trị 0/1/…), `.co_ma` bản "… (mã)", `.thuan` bản không mã."""
    ma = None
    co_ma = ""
    thuan = ""


def _tieu_de(ma, co_ma, thuan=None):
    thuan = _RE_THE_DAU.sub("", co_ma, count=1) if thuan is None else thuan
    t = TieuDe(co_ma if _GIU_MA.get() else thuan)
    t.ma, t.co_ma, t.thuan = ma, co_ma, thuan
    return t


def _lua_chon(co_ma):
    m = _MA_TRONG_LUA_CHON.search(co_ma.strip())
    thuan = co_ma.strip()[:m.start()].rstrip() if m else co_ma
    t = LuaChon(co_ma if _GIU_MA.get() else thuan)
    t.ma, t.co_ma, t.thuan = (m.group(1) if m else None), co_ma, thuan
    return t


def doc_de_thi(duong_dan=DE_THI_MAC_DINH):
    with open(duong_dan, encoding="utf-8") as f:
        de = json.load(f)
    soat_de_thi(de)
    return de


def soat_de_thi(de):
    """Ném LoiDeThi liệt kê MỌI chỗ sai, không dừng ở chỗ đầu tiên."""
    loi = []
    ma_buoi = [b["ma"] for b in de.get("buoi", [])]
    if not ma_buoi:
        loi.append("chưa khai buổi nào")
    if len(set(ma_buoi)) != len(ma_buoi):
        loi.append("mã buổi bị trùng")
    diem = de.get("diem_moi_cau")
    if not isinstance(diem, (int, float)) or diem <= 0:
        loi.append("diem_moi_cau phải là số dương")

    thay = set()
    for clb in de.get("cau_lac_bo", []):
        ma = clb.get("club_id", "")
        if not _MA_CLB.match(ma):
            loi.append("club_id %r chỉ được có chữ không dấu, số, gạch dưới" % ma)
        if ma in thay:
            loi.append("club_id %r bị trùng" % ma)
        thay.add(ma)
        if clb.get("buoi") not in ma_buoi:
            loi.append("%s: buổi %r không có trong danh sách buổi" % (ma, clb.get("buoi")))
        if ";" in clb.get("name", ""):
            # Forms nối các lựa chọn Ranking bằng dấu chấm phẩy khi xuất.
            loi.append("%s: tên CLB không được chứa dấu ;" % ma)
        cap, du_tru = clb.get("capacity", 0), clb.get("reserve_capacity", 0)
        if not isinstance(cap, int) or cap <= 0:
            loi.append("%s: capacity phải là số nguyên > 0" % ma)
        elif du_tru > cap:
            loi.append("%s: reserve_capacity lớn hơn capacity" % ma)
        if du_tru and not clb.get("reserve_group"):
            loi.append("%s: có suất dự trữ thì phải có reserve_group" % ma)
        for i, cau in enumerate(clb.get("de_thi", []), 1):
            lc = cau.get("lua_chon", [])
            if len(lc) < 2:
                loi.append("%s câu %d: cần ít nhất 2 lựa chọn" % (ma, i))
            if len(set(_chuan(x) for x in lc)) != len(lc):
                # Chấm theo NỘI DUNG lựa chọn — hai lựa chọn giống nhau thì
                # không phân biệt được em chọn cái nào.
                loi.append("%s câu %d: có lựa chọn trùng nhau" % (ma, i))
            if not isinstance(cau.get("dap_an"), int) or not 0 <= cau["dap_an"] < len(lc):
                loi.append("%s câu %d: dap_an phải là số thứ tự lựa chọn, đếm từ 0" % (ma, i))

    for b in ma_buoi:
        o_buoi = [c for c in de.get("cau_lac_bo", []) if c.get("buoi") == b]
        if len(o_buoi) > TRAN_CLB_MOI_BUOI:
            loi.append("buổi %s có %d CLB, vượt trần %d của câu Ranking"
                       % (b, len(o_buoi), TRAN_CLB_MOI_BUOI))
        co_thi = [c for c in o_buoi if c.get("de_thi")]
        if len(co_thi) > TRAN_THI_MOI_BUOI:
            loi.append("buổi %s có %d CLB tổ chức thi, vượt trần %d"
                       % (b, len(co_thi), TRAN_THI_MOI_BUOI))
    if loi:
        raise LoiDeThi("de_thi.json sai:\n  - " + "\n  - ".join(loi))


def _chuan(s):
    return " ".join(str(s or "").split()).casefold()


def ten_buoi(de, ma):
    return next(b["ten"] for b in de["buoi"] if b["ma"] == ma)


def clb_cua_buoi(de, ma_buoi):
    return [c for c in de["cau_lac_bo"] if c["buoi"] == ma_buoi]


def clb_co_thi(de):
    return [c for c in de["cau_lac_bo"] if c["de_thi"]]


def lua_chon_clb(clb):
    """Ghi cả tên lẫn mã — người xử lý không phải tra ngược tên ra mã."""
    return _lua_chon("%s (%s)" % (clb["name"], clb["club_id"]))


# ---- Tên câu hỏi: nguồn duy nhất cho cả biểu mẫu lẫn bộ chuyển đổi ----

def cau_ma_hoc_sinh():
    return _tieu_de("student_id", "[student_id] Mã học sinh của em (ghi đúng như trên thẻ học sinh)")


def cau_ho_ten():
    return _tieu_de("name", "[name] Họ và tên của em")


def cau_xep_hang(de, ma_buoi):
    return _tieu_de(ma_buoi, "[%s] %s — em muốn vào câu lạc bộ nào? Kéo thả, câu lạc bộ em "
                    "thích nhất lên đầu. Bận buổi này thì bỏ qua câu này."
                    % (ma_buoi, ten_buoi(de, ma_buoi)))


def cau_cong_thi(de, clb, chi_thi=False):
    if chi_thi:
        # Chế độ chỉ thi: nguyện vọng nằm ở ứng dụng đăng ký, không ở biểu mẫu này.
        return _tieu_de("thi-" + clb["club_id"],
                        "[thi-%s] %s · Em có dự thi %s không? Chỉ chọn Có nếu em đã xếp "
                        "câu lạc bộ này ở nguyện vọng %s trong ứng dụng đăng ký."
                        % (clb["club_id"], ten_buoi(de, clb["buoi"]), clb["name"],
                           ten_buoi(de, clb["buoi"])))
    return _tieu_de("thi-" + clb["club_id"],
                    "[thi-%s] %s · Em có dự thi %s không? Chỉ chọn Có nếu em đã xếp "
                    "câu lạc bộ này ở câu nguyện vọng %s."
                    % (clb["club_id"], ten_buoi(de, clb["buoi"]), clb["name"],
                       ten_buoi(de, clb["buoi"])))


def _cac_de_cua_clb(clb):
    """[đề A, đề B, đề C…]: đề A là `de_thi`, đề B, C là `de_thi_bien_the` (nếu có)."""
    return [clb.get("de_thi") or []] + list(clb.get("de_thi_bien_the") or [])


def _ma_theo_chu_cau(de):
    """{chữ câu (đã gộp khoảng trắng): {mã câu}} cho mọi câu của mọi đề (kể cả đề B, C)."""
    ra = {}
    for c in de.get("cau_lac_bo", []):
        for qs in _cac_de_cua_clb(c):
            for i, q in enumerate(qs, 1):
                ra.setdefault(_khoa(q["cau"]), set()).add("%s-%d" % (c["club_id"], i))
    return ra


def cau_de_thi(clb, so_thu_tu, de=None):
    """Tên câu đề thi `[<club_id>-<k>] <chữ câu>`. Tiêu đề thuần = chữ câu; hai câu KHÁC mã mà cùng chữ (trong `de`)
    thì thêm "(tên CLB, câu k)" để tiêu đề không trùng. Không truyền `de` = không xét trùng."""
    cau = clb["de_thi"][so_thu_tu - 1]["cau"]
    ma = "%s-%d" % (clb["club_id"], so_thu_tu)
    thuan = cau
    if de is not None and len(_ma_theo_chu_cau(de).get(_khoa(cau), ())) > 1:
        thuan = "%s (%s, câu %d)" % (cau, clb["name"], so_thu_tu)
    return _tieu_de(ma, "[%s-%d] %s" % (clb["club_id"], so_thu_tu, cau), thuan)


def _khoa(chu):
    """Khoá so khớp tiêu đề / lựa chọn thuần: gộp khoảng trắng, GIỮ hoa thường (khớp CHÍNH XÁC chữ trên biểu mẫu)."""
    return " ".join(str(chu or "").split())


def ma_cua_cau(tieu_de, ban_do=None):
    """'[thu_2] Thứ Hai — …' -> 'thu_2'. Không phải câu của mẫu -> None.

    Tiêu đề do bộ sinh dựng (`TieuDe`) thì trả thẳng `.ma`. Chuỗi từ tệp xuất: thẻ "[mã]" ở đầu (tệp cũ) trước; không có
    thẻ thì khớp CHÍNH XÁC chữ thuần qua `ban_do` (từ `ban_do_chung(de)` hoặc tệp MAP_*.json), có chấp nhận số thứ tự
    "3." Forms đôi khi giữ ở đầu."""
    if isinstance(tieu_de, TieuDe):
        return tieu_de.ma
    chu = str(tieu_de or "")
    m = _MA_CAU.match(chu)
    if m:
        return m.group(1).strip()
    if ban_do:
        cau = ban_do.get("cau") or {}
        return cau.get(_khoa(chu)) or cau.get(_khoa(_RE_SO_THU_TU.sub("", chu, count=1)))
    return None


def ma_trong_lua_chon(chu, ban_do=None, ma_cau=None):
    """'CLB Cờ vua (clb_covua)' -> 'clb_covua'.

    Có `ban_do` và `ma_cau` (mã của câu chứa lựa chọn): khớp CHÍNH XÁC chữ thuần của lựa chọn trong câu đó trước (tệp
    mới, 'Có' -> '1'); không khớp thì đọc "(mã)" cuối chữ (tệp cũ). `LuaChon` do bộ sinh dựng thì trả `.ma`."""
    if isinstance(chu, LuaChon):
        return chu.ma
    if ban_do and ma_cau:
        gia_tri = (ban_do.get("lua_chon") or {}).get(ma_cau, {}).get(_khoa(chu))
        if gia_tri is not None:
            return gia_tri
    m = _MA_TRONG_LUA_CHON.search(str(chu or "").strip())
    return m.group(1) if m else None


def cac_phan(de, chi_thi=False, buoi=None):
    """Bố cục biểu mẫu: [(tên phần, [(tiêu đề câu, loại, lựa chọn, bắt buộc)])].

    Loại: 'text', 'ranking', 'choice'. Thứ tự phần CHÍNH LÀ luồng mặc định
    của Forms: làm xong đề thi CLB X thì tự sang câu cổng của CLB kế tiếp,
    nên chỉ đáp án "Không" của câu cổng là cần rẽ nhánh.

    chi_thi=True (T4M-Q2): biểu mẫu chỉ có bài thi. Không có ô gõ mã HS/họ tên
    (Forms tự ghi Name + Email khi bật "Record name") và không có câu Ranking
    (nguyện vọng nằm ở ứng dụng đăng ký). buoi: chỉ các buổi này (None = tất cả).
    """
    phan = [] if chi_thi else [("Thông tin học sinh", [
        (cau_ma_hoc_sinh(), "text", [], True),
        (cau_ho_ten(), "text", [], True),
    ])]
    for b in de["buoi"]:
        if buoi is not None and b["ma"] not in buoi:
            continue
        o_buoi = clb_cua_buoi(de, b["ma"])
        if not chi_thi:
            # Ranking KHÔNG bắt buộc: bỏ trống = em bận buổi đó. Đặt bắt buộc
            # là ép em khai một buổi em không rảnh (BO_CAU_HOI_FORMS.md mục 4).
            phan.append(("%s · Nguyện vọng" % b["ten"], [
                (cau_xep_hang(de, b["ma"]), "ranking",
                 [lua_chon_clb(c) for c in o_buoi], False),
            ]))
        for clb in o_buoi:
            if not clb["de_thi"]:
                continue
            phan.append(("%s · Dự thi %s" % (b["ten"], clb["name"]), [
                (cau_cong_thi(de, clb, chi_thi), "choice", [CO, KHONG], True),
            ]))
            phan.append(("%s · Đề thi %s" % (b["ten"], clb["name"]), [
                (cau_de_thi(clb, i, de), "choice", cau["lua_chon"], True)
                for i, cau in enumerate(clb["de_thi"], 1)
            ]))
    return phan


# ---- FA-M2 (TH): biểu mẫu đăng ký đường B, một biểu mẫu MỖI NGÀY (`tao_mau_forms.py --fa-daa`) ----
# Quyết định D12: không câu Ranking; ba câu chọn riêng bắt buộc; hai câu huy chương tuỳ chọn. Forms không
# bỏ chọn được một đáp án đã chọn, nên mỗi câu tuỳ chọn có đáp án "giữ mặc định" rõ ràng (bộ chuyển đổi, FA-M3,
# đổi nó thành ô trống rồi mới gọi `dat_huy_chuong_duong_b`).
CAU_HUONG_DAN_DANG_KY = ("Xếp đúng thứ tự em thích. Xếp CLB khó vào lên đầu không làm em mất cơ hội ở CLB sau.")
SO_NGUYEN_VONG_FA = 3
GIU_MAC_DINH_VANG = "Giữ mặc định"
DOI_CO = "Có"
DOI_KHONG = "Không, giữ mặc định"


def cau_nguyen_vong_fa(de, ma_buoi, k):
    return _tieu_de("%s-nv%d" % (ma_buoi, k), "[%s-nv%d] %s — Nguyện vọng %d" % (ma_buoi, k, ten_buoi(de, ma_buoi), k))


# SG-5 (H3): một dòng mô tả dưới phần huy chương, nói đúng luật thật của `fa_daa`: huy chương KHÔNG đổi thứ tự
# nguyện vọng; nó chỉ là tiêu chí ưu tiên ở từng CLB — CLB Tuyển chọn: điểm thi trước, huy chương khi bằng điểm;
# CLB Giới hạn (không xét điểm): huy chương trước bốc thăm. Mặc định (`dat_huy_chuong_duong_b`): vàng, bạc, đồng cho
# ba CLB không Tự do đầu tiên theo thứ tự nguyện vọng. Cố ý KHÔNG hứa "để mặc định không bao giờ thiệt".
MO_TA_HUY_CHUONG = ("Huy chương giúp em được ưu tiên hơn bạn khác ở CLB đó: CLB có xét điểm thi thì chỉ dùng khi "
                    "bằng điểm thi, CLB không xét điểm thi thì dùng trước khi bốc thăm. Em không chọn gì thì hệ "
                    "thống tự đặt vàng cho nguyện vọng 1, bạc cho nguyện vọng 2, đồng cho nguyện vọng 3 "
                    "(CLB Tự do không có huy chương nên được bỏ qua).")
SO_CLB_TOI_THIEU_CAU_DOI = 3          # đổi chỗ bạc và đồng chỉ có nghĩa khi có >= 3 CLB nhận huy chương


def so_clb_nhan_huy_chuong(de, ma_buoi):
    """Số CLB của ngày đủ điều kiện nhận huy chương (không Tự do; chưa biết `loai` thì tính là có)."""
    return sum(1 for c in clb_cua_buoi(de, ma_buoi) if c.get("loai") != "TU_DO")


def cau_vang_fa(de, ma_buoi):
    return _tieu_de(ma_buoi + "-vang",
                    "[%s-vang] %s — Đặt huy chương vàng vào CLB khác NV1? Chọn \"%s\" nếu không đổi. %s"
                    % (ma_buoi, ten_buoi(de, ma_buoi), GIU_MAC_DINH_VANG, MO_TA_HUY_CHUONG))


def cau_doi_fa(de, ma_buoi):
    return _tieu_de(ma_buoi + "-doi", "[%s-doi] %s — Đổi chỗ huy chương bạc và đồng? Chọn \"%s\" nếu không đổi."
                    % (ma_buoi, ten_buoi(de, ma_buoi), DOI_KHONG))


def cac_phan_fa(de, ma_buoi):
    """FA-M2: bố cục biểu mẫu đăng ký của MỘT ngày: [(tên phần, [(tiêu đề, loại, lựa chọn, bắt buộc)])].

    Không có câu Ranking. Số câu nguyện vọng = min(3, số CLB của ngày). Câu vàng chỉ liệt kê CLB không Tự do
    khi `de_thi.json` có khoá `loai` ở CLB (chưa có thì liệt kê hết; bộ chuyển đổi bỏ CLB Tự do và báo).
    """
    o_buoi = clb_cua_buoi(de, ma_buoi)
    ds = [lua_chon_clb(c) for c in o_buoi]
    khong_tu_do = [lua_chon_clb(c) for c in o_buoi if c.get("loai") != "TU_DO"]
    cau_huy_chuong = [(cau_vang_fa(de, ma_buoi), "choice", [GIU_MAC_DINH_VANG] + khong_tu_do, False)]
    if len(khong_tu_do) >= SO_CLB_TOI_THIEU_CAU_DOI:          # SG-5: ngày < 3 CLB nhận huy chương không có câu đổi
        cau_huy_chuong.append((cau_doi_fa(de, ma_buoi), "choice", [DOI_KHONG, DOI_CO], False))
    return [
        ("Thông tin học sinh", [(cau_ma_hoc_sinh(), "text", [], True), (cau_ho_ten(), "text", [], True)]),
        ("%s · Nguyện vọng" % ten_buoi(de, ma_buoi), [
            (cau_nguyen_vong_fa(de, ma_buoi, k), "choice", list(ds), True)
            for k in range(1, min(SO_NGUYEN_VONG_FA, len(ds)) + 1)]),
        ("%s · Huy chương (không bắt buộc)" % ten_buoi(de, ma_buoi), cau_huy_chuong),
    ]


def cac_phan_fa_gop(de):
    """FA-M2b (TH): MỘT biểu mẫu đăng ký cho mọi ngày: phần thông tin một lần, rồi mỗi ngày (theo thứ tự `de["buoi"]`)
    phần Nguyện vọng và phần Huy chương. Chữ từng câu giống hệt `cac_phan_fa` (thẻ `[<buổi>-nvK]` ... không đổi)."""
    phan = [cac_phan_fa(de, de["buoi"][0]["ma"])[0]] if de["buoi"] else []
    for b in de["buoi"]:
        phan += cac_phan_fa(de, b["ma"])[1:]
    return phan


def dem_cau_fa_gop(de):
    """Tổng số câu của biểu mẫu đăng ký gộp (Forms tính cả câu thông tin)."""
    return sum(len(c) for _, c in cac_phan_fa_gop(de))


# ------------------------------------------- GAP-5 (TH): ba câu phản hồi sau khi xem kết quả (V§9.1)
# Mã trong "[…]" và "(…)" khớp `fa_sau_xep.MA_CAU_PHAN_HOI` / `KHO_NHAT` (bộ nhập của kiosk đọc theo mã).
# SG-12: các hằng này là TÊN CÂU / LỰA CHỌN, nên chữ hiển thị phụ thuộc chế độ giữ mã (xem đầu tệp) -> dựng khi đọc
# (`__getattr__` ở cuối tệp), không đóng băng lúc nạp mô-đun. `bm.CAU_HAI_LONG` vẫn dùng như trước.
def _cau_hai_long():
    return _tieu_de("hai_long", "[hai_long] Em hài lòng với kết quả xếp CLB đến mức nào?")


def _cau_hieu_ly_do():
    return _tieu_de("hieu_ly_do", "[hieu_ly_do] Em có hiểu vì sao mình được xếp như vậy không?")


def _cau_kho_nhat():
    return _tieu_de("kho_nhat", "[kho_nhat] Phần nào khó nhất với em?")


def _lua_chon_hai_long():
    return [_lua_chon(x) for x in ["1 — Rất không hài lòng (1)", "2 (2)", "3 (3)", "4 (4)", "5 — Rất hài lòng (5)"]]


def _lua_chon_co_khong():
    return [_lua_chon(x) for x in ["Có (1)", "Không (0)"]]


def _lua_chon_kho_nhat():
    return [_lua_chon(x) for x in ["Chọn CLB (chon_clb)", "Xếp thứ tự nguyện vọng (xep_thu_tu)",
                                   "Đặt huy chương (huy_chuong)", "Bài thử thách (thu_thach)",
                                   "Không có phần nào khó (khong_co)"]]


def cac_phan_phan_hoi():
    """GAP-5 (TH): bố cục biểu mẫu phản hồi: mã học sinh + 3 câu một chạm, đều bắt buộc."""
    return [("Phản hồi sau khi xem kết quả", [
        (cau_ma_hoc_sinh(), "text", [], True),
        (_cau_hai_long(), "choice", _lua_chon_hai_long(), True),
        (_cau_hieu_ly_do(), "choice", _lua_chon_co_khong(), True),
        (_cau_kho_nhat(), "choice", _lua_chon_kho_nhat(), True)])]


# ------------------------------------------- FA-M6b (TH): MỘT biểu mẫu "Sau khi xem kết quả" = 3 câu phản hồi + nhánh khiếu nại
# Mã `[co_sai]`, `[kn_buoi]`, `[kn_ghi_chu]` khớp `fa_sau_xep.doc_tep_forms_khieu_nai`; lựa chọn kết thúc bằng "(mã)".
def _cau_co_sai():
    return _tieu_de("co_sai", "[co_sai] Em có thấy thông tin của em trong kết quả bị sai không? "
                              "(ví dụ sai mã, sai điểm, thiếu nguyện vọng)")


def _lua_chon_co_sai():
    return [_lua_chon(x) for x in ["Không (0)", "Có (1)"]]


def _cau_kn_buoi():
    return _tieu_de("kn_buoi", "[kn_buoi] Buổi nào có thông tin bị sai?")


def _cau_kn_ghi_chu():
    return _tieu_de("kn_ghi_chu", "[kn_ghi_chu] Em mô tả ngắn chỗ sai")


def cac_phan_sau_ket_qua(de):
    """FA-M6b (TH): bố cục biểu mẫu "Sau khi xem kết quả": phần 1 = mã học sinh + 3 câu phản hồi + `[co_sai]` (bắt buộc);
    phần 2 (chỉ khi `[co_sai]` = Có, rẽ nhánh cài tay) = `[kn_buoi]` (hộp chọn nhiều, mọi buổi) + `[kn_ghi_chu]`.
    Loại 'checkbox' chỉ để mô tả: Quick Import không phân biệt, hướng dẫn bảo bật "Multiple answers"."""
    p1 = cac_phan_phan_hoi()[0][1] + [(_cau_co_sai(), "choice", _lua_chon_co_sai(), True)]
    return [
        ("Phản hồi sau khi xem kết quả", p1),
        ("Báo lỗi dữ liệu (khiếu nại, chỉ lỗi dữ liệu)", [
            (_cau_kn_buoi(), "checkbox", [_lua_chon("%s (%s)" % (b["ten"], b["ma"])) for b in de["buoi"]], True),
            (_cau_kn_ghi_chu(), "text", [], True)]),
    ]


# ------------------------------------------- GAP-6 (TH): khảo sát tuần 3 (V§9.3)
def _cau_con_di():
    return _tieu_de("con_di", "[con_di] Em còn đi sinh hoạt CLB của mình không?")


def _cau_muon_doi():
    return _tieu_de("muon_doi", "[muon_doi] Em có muốn đổi sang CLB khác không?")


def cac_phan_tuan_3():
    """GAP-6 (TH): bố cục khảo sát tuần 3: mã học sinh + 2 câu có/không, đều bắt buộc."""
    return [("Khảo sát tuần 3", [
        (cau_ma_hoc_sinh(), "text", [], True),
        (_cau_con_di(), "choice", _lua_chon_co_khong(), True),
        (_cau_muon_doi(), "choice", _lua_chon_co_khong(), True)])]


# ------------------------------------------- FA-M8 / R9 (TH): phiếu thiết lập CLB (PHIEU_THIET_LAP_CLB.md §1)
# Tên câu hỏi GIỮ ĐÚNG TỪNG CHỮ: `chuyen_phieu_clb.doc_phieu_clb` đọc theo tiêu đề cột (test so với `TIEU_DE_PHIEU` của nó).
TIEU_DE_PHIEU_CLB = [
    "Tên CLB", "Buổi", "Giờ", "Địa điểm",
    "Mở thêm nhóm được nếu đông không? (Có/Không)", "Số chỗ tối đa", "Lý do giới hạn",
    "Sức chứa mỗi nhóm", "Số thành viên tối thiểu",
    "Cần kỹ năng tối thiểu không? (Có/Không)", "Loại thử thách", "Mốc tối thiểu (thang 10)",
    "Bảng tiêu chí", "Giữ chỗ (mã học sinh, cách nhau dấu phẩy)",
]
BUOI_PHIEU_CLB = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6"]
LOAI_THU_THACH_PHIEU_CLB = ["Trắc nghiệm", "Video", "Ảnh"]


def cac_phan_phieu_clb():
    """Bố cục phiếu thiết lập CLB: bảy phần; hai chỗ rẽ nhánh (sau câu "Mở thêm nhóm…" và sau câu "Cần kỹ năng…").

    [(tên phần, [(tiêu đề, loại, lựa chọn, bắt buộc)])]; loại 'text' hoặc 'choice'. Kiểu thật trong Forms
    (Số, Văn bản dài) do hướng dẫn nêu, vì Quick Import chỉ tạo câu văn bản và câu lựa chọn."""
    t = dict(zip(["ten", "buoi", "gio", "dia_diem", "mo", "cho", "ly_do", "phong", "toi_thieu", "can", "loai",
                  "moc", "tieu_chi", "giu"], TIEU_DE_PHIEU_CLB))
    co_khong = ["Có", "Không"]
    return [
        ("Thông tin CLB", [(t["ten"], "text", [], True), (t["buoi"], "choice", list(BUOI_PHIEU_CLB), True),
                           (t["gio"], "text", [], False), (t["dia_diem"], "text", [], False)]),
        ("Mở thêm nhóm", [(t["mo"], "choice", list(co_khong), True)]),
        ("Nhánh Có — sức chứa mỗi nhóm", [(t["phong"], "text", [], True)]),
        ("Nhánh Không — số chỗ tối đa", [(t["cho"], "text", [], True), (t["ly_do"], "text", [], True)]),
        ("Thành viên và kỹ năng", [(t["toi_thieu"], "text", [], True), (t["can"], "choice", list(co_khong), True)]),
        ("Thử thách đầu vào", [(t["loai"], "choice", list(LOAI_THU_THACH_PHIEU_CLB), True),
                               (t["moc"], "text", [], True), (t["tieu_chi"], "text", [], True)]),
        ("Giữ chỗ", [(t["giu"], "text", [], False)]),
    ]


def cac_phan_moi_clb(de, clb):
    """T4M-Q4a: bố cục biểu mẫu của MỘT CLB: một phần, các câu đề thi, KHÔNG câu cổng.

    Thẻ câu vẫn là [<club_id>-<k>] như biểu mẫu chung, để bộ chuyển đổi nhận ra CLB.
    """
    return [("Đề thi %s" % clb["name"], [
        (cau_de_thi(clb, i, de), "choice", cau["lua_chon"], True)
        for i, cau in enumerate(clb["de_thi"], 1)])]


def dem_cau(de, chi_thi=False, buoi=None):
    """Tổng số câu hỏi của biểu mẫu (Forms tính cả câu cổng và câu thông tin)."""
    return sum(len(c) for _, c in cac_phan(de, chi_thi, buoi))


def chia_theo_buoi(de, chi_thi=False, tran=TRAN_CAU_MOI_BIEU_MAU):
    """Chia các buổi thành các biểu mẫu, mỗi biểu mẫu <= `tran` câu.

    Giữ thứ tự buổi trong de_thi.json, xếp tham lam từ đầu. Trả [[mã buổi, ...], ...];
    vừa một biểu mẫu thì chỉ có một nhóm. Một buổi một mình đã vượt trần, hoặc không
    CLB nào có đề, thì ném LoiDeThi (không có cách chia theo buổi).
    """
    co_dinh = dem_cau(de, chi_thi, buoi=[])
    nhom, hien, tong = [], [], co_dinh
    for b in de["buoi"]:
        n = dem_cau(de, chi_thi, [b["ma"]]) - co_dinh
        if n == 0:
            continue                      # buổi không CLB nào thi: không có gì để đưa lên biểu mẫu
        if co_dinh + n > tran:
            raise LoiDeThi("buổi %s một mình đã có %d câu, vượt trần %d câu của một biểu mẫu "
                           "Forms — giảm số CLB thi hoặc số câu của buổi này"
                           % (b["ma"], co_dinh + n, tran))
        if hien and tong + n > tran:
            nhom.append(hien)
            hien, tong = [], co_dinh
        hien.append(b["ma"])
        tong += n
    if hien:
        nhom.append(hien)
    if not nhom:
        raise LoiDeThi("không CLB nào có đề thi — không có gì để dựng biểu mẫu")
    return nhom


def re_nhanh(de, chi_thi=False, buoi=None):
    """[(câu cổng, đáp án 'Không' đi tới đâu)] — đúng những gì phải cài tay."""
    ten_phan = [p[0] for p in cac_phan(de, chi_thi, buoi)]
    kq = []
    for clb in clb_co_thi(de):
        if buoi is not None and clb["buoi"] not in buoi:
            continue
        de_phan = "%s · Đề thi %s" % (ten_buoi(de, clb["buoi"]), clb["name"])
        i = ten_phan.index(de_phan)
        toi = ten_phan[i + 1] if i + 1 < len(ten_phan) else "End of the form"
        kq.append((clb, toi))
    return kq


def cham_bai(de, clb, tra_loi):
    """tra_loi: {số thứ tự câu: nội dung em chọn}. Trả (điểm, [đúng/sai])."""
    diem_cau = de["diem_moi_cau"]
    dung = []
    for i, cau in enumerate(clb["de_thi"], 1):
        dap_an = cau["lua_chon"][cau["dap_an"]]
        dung.append(_chuan(tra_loi.get(i)) == _chuan(dap_an))
    return diem_cau * sum(dung), dung


def diem_toi_da(de, clb):
    return de["diem_moi_cau"] * len(clb["de_thi"])


def ghi_so(x):
    """8.0 -> '8', 9.5 -> '9.5' — đúng dạng phần mềm đọc."""
    x = float(x)
    return str(int(x)) if x.is_integer() else ("%g" % x)


# ------------------------------------------- SG-12 (H2): bản đồ tiêu đề thuần -> mã, MỘT hàm cho bộ sinh và bộ đọc
BAN_DO_PHIEN_BAN = 1


def _moi_cau_hoi(de):
    """Mọi câu hỏi mà bộ sinh có thể ghi cho `de` (mọi chế độ, mọi đề A/B/C): [(TieuDe, loại, [lựa chọn])].
    `de` None: chỉ các câu không phụ thuộc đề (mã học sinh, họ tên, phản hồi, khảo sát tuần 3, khiếu nại)."""
    phan = list(cac_phan_phan_hoi()) + list(cac_phan_tuan_3())
    if de is None:
        phan += [("", [(cau_ma_hoc_sinh(), "text", [], True), (cau_ho_ten(), "text", [], True)]),
                 ("", [(_cau_co_sai(), "choice", _lua_chon_co_sai(), True),
                       (_cau_kn_buoi(), "checkbox", [], True), (_cau_kn_ghi_chu(), "text", [], True)])]
    else:
        phan += cac_phan(de) + cac_phan(de, chi_thi=True) + cac_phan_sau_ket_qua(de)
        if de.get("buoi"):
            phan += cac_phan_fa_gop(de)
        for clb in clb_co_thi(de):
            for qs in _cac_de_cua_clb(clb):
                if qs:
                    phan += cac_phan_moi_clb(de, dict(clb, de_thi=qs))
    return [c for _ten, cac in phan for c in cac]


def xay_ban_do(cac_cau_hoi):
    """Dựng bản đồ từ [(TieuDe, loại, [lựa chọn])]:
    {"phien_ban": 1, "cau": {tiêu đề thuần: mã câu}, "lua_chon": {mã câu: {lựa chọn thuần: mã/giá trị}}}.

    Khoá đã gộp khoảng trắng. Hai câu KHÁC mã trùng tiêu đề thuần, hai lựa chọn khác giá trị trùng chữ trong cùng
    một câu, hoặc tiêu đề thuần mở đầu bằng "[…]" (đọc nhầm thành thẻ mã) -> LoiDeThi (liệt kê hết)."""
    cau, lua, loi = {}, {}, []
    chuan_lua = {}
    for td, _loai, lcs, *_ in cac_cau_hoi:
        if not isinstance(td, TieuDe):
            loi.append("câu %r không phải tiêu đề do bộ sinh dựng" % str(td)[:60])
            continue
        k = _khoa(td.thuan)
        if _MA_CAU.match(td.thuan):
            loi.append("tiêu đề %r mở đầu bằng [..] nên bị đọc nhầm thành thẻ mã" % k[:60])
        if cau.setdefault(k, td.ma) != td.ma:
            loi.append("hai câu %r và %r có cùng tiêu đề %r" % (cau[k], td.ma, k[:60]))
        cua_cau = lua.setdefault(td.ma, {})
        chuan_cua_cau = chuan_lua.setdefault(td.ma, {})
        for lc in lcs:
            if isinstance(lc, LuaChon) and lc.ma is not None:
                kl = _khoa(lc.thuan)
                if cua_cau.setdefault(kl, lc.ma) != lc.ma:
                    loi.append("câu %s: hai lựa chọn %r và %r có cùng chữ %r" % (td.ma, cua_cau[kl], lc.ma, kl))
                # chỉ khác hoa/thường hay khoảng trắng: bộ đọc có thể đọc nhầm (tìm theo tên đã gộp) -> từ chối ngay
                elif chuan_cua_cau.setdefault(_chuan(kl), kl) != kl:
                    loi.append("câu %s: hai lựa chọn %r và %r chỉ khác hoa/thường hay khoảng trắng" % (
                        td.ma, chuan_cua_cau[_chuan(kl)], kl))
    if loi:
        raise LoiDeThi("tiêu đề trùng hoặc không dùng được (đổi tên CLB / buổi / câu hỏi trong de_thi.json):\n  - "
                       + "\n  - ".join(sorted(set(loi))))
    return {"phien_ban": BAN_DO_PHIEN_BAN, "cau": cau, "lua_chon": {m: v for m, v in lua.items() if v}}


def ban_do_chung(de):
    """Bản đồ cho MỌI biểu mẫu có thể sinh từ `de` (bộ đọc không cần biết tệp thuộc chế độ nào). `de` None: chỉ các
    câu không phụ thuộc đề. Cùng `de` thì cho ra cùng bản đồ."""
    return xay_ban_do(_moi_cau_hoi(de))


def ban_do_bieu_mau(phan):
    """Bản đồ của MỘT biểu mẫu = các phần `[(tên phần, [(tiêu đề, loại, lựa chọn, bắt buộc)])]` mà bộ sinh ghi.
    Bộ sinh ghi nó thành `MAP_<tên biểu mẫu>.json` cạnh biểu mẫu."""
    return xay_ban_do([c for _ten, cac in phan for c in cac])


def ban_do_ra_json(ban_do):
    """Chuỗi JSON xác định (khoá sắp, UTF-8, không giờ), kết thúc bằng một dòng mới."""
    return json.dumps(ban_do, ensure_ascii=False, sort_keys=True, indent=1) + "\n"


def doc_ban_do(duong_dan):
    """Đọc tệp MAP_*.json -> bản đồ. Hỏng / sai dạng -> LoiDeThi."""
    try:
        with open(duong_dan, encoding="utf-8") as f:
            bd = json.load(f)
        if not isinstance(bd, dict) or not isinstance(bd.get("cau"), dict) or not isinstance(bd.get("lua_chon"), dict):
            raise ValueError("thiếu khoá cau / lua_chon")
    except (OSError, ValueError) as e:
        raise LoiDeThi("tệp bản đồ %s không đọc được: %s" % (duong_dan, e)) from e
    return bd


def gop_ban_do(*cac_ban_do):
    """Gộp nhiều bản đồ (nhiều tệp MAP) thành một; hai bản đồ cho cùng tiêu đề hai mã khác nhau -> LoiDeThi."""
    cau, lua = {}, {}
    for bd in cac_ban_do:
        for k, m in (bd.get("cau") or {}).items():
            if cau.setdefault(k, m) != m:
                raise LoiDeThi("các tệp bản đồ cho tiêu đề %r hai mã khác nhau (%s, %s)" % (k[:60], cau[k], m))
        for m, v in (bd.get("lua_chon") or {}).items():
            cua = lua.setdefault(m, {})
            for kl, gt in v.items():
                if cua.setdefault(kl, gt) != gt:
                    raise LoiDeThi("các tệp bản đồ cho lựa chọn %r của câu %s hai giá trị khác nhau" % (kl[:60], m))
    return {"phien_ban": BAN_DO_PHIEN_BAN, "cau": cau, "lua_chon": lua}


_HANG_DONG = {
    "CAU_HAI_LONG": _cau_hai_long, "CAU_HIEU_LY_DO": _cau_hieu_ly_do, "CAU_KHO_NHAT": _cau_kho_nhat,
    "LUA_CHON_HAI_LONG": _lua_chon_hai_long, "LUA_CHON_CO_KHONG": _lua_chon_co_khong,
    "LUA_CHON_KHO_NHAT": _lua_chon_kho_nhat, "CAU_CO_SAI": _cau_co_sai, "LUA_CHON_CO_SAI": _lua_chon_co_sai,
    "CAU_KN_BUOI": _cau_kn_buoi, "CAU_KN_GHI_CHU": _cau_kn_ghi_chu, "CAU_CON_DI": _cau_con_di,
    "CAU_MUON_DOI": _cau_muon_doi,
}


def __getattr__(ten):
    """Các hằng tên câu / lựa chọn (xem SG-12 ở đầu tệp) được dựng theo chế độ giữ mã lúc đọc."""
    f = _HANG_DONG.get(ten)
    if f is None:
        raise AttributeError("module %r has no attribute %r" % (__name__, ten))
    return f()
