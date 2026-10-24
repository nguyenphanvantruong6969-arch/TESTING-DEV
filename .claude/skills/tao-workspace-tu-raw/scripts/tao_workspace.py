# -*- coding: utf-8 -*-
"""Dựng một workspace (không gian làm việc) nạp sẵn dữ liệu từ dữ liệu RAW bất kỳ.

Hai chế độ:

    python tao_workspace.py soi  <tệp> [<tệp> ...] [--json]
    python tao_workspace.py dung --spec spec.json --ra <thư mục NGOÀI kho mã>
                                 [--chap-nhan ma_canh_bao,...] [--json]

`soi`  — đọc từng bảng (mỗi sheet / mỗi CSV), in cột, giá trị mẫu và ĐOÁN vai trò
         từng cột. Không ghi gì. Đây là đầu vào để soạn bản ánh xạ (spec).
`dung` — đọc raw theo bản ánh xạ, soát chặt, và CHỈ KHI KHÔNG CÒN LỖI mới ghi:
             <slug>.zip        workspace đã gắn cấu hình và nạp sẵn dữ liệu
             SO_NHAP_<slug>.xlsx   Sổ nhập theo nhãn workspace (sửa tay rồi nạp lại)
             BAO_CAO_SOAT.md   báo cáo soát: số liệu, giả định, cảnh báo đã chấp nhận

NGUYÊN TẮC (giống skill sinh-du-lieu-clb):
  * Sai một điều là KHÔNG GHI tệp nào. Không tự sửa dữ liệu — sửa giúp là giấu chỗ sai.
    Chỉ chuẩn hoá những thứ phần mềm vốn coi là như nhau (hoa/thường và khoảng trắng
    thừa của tên chỗ xếp, dấu phẩy thập phân).
  * Kiểm bằng PHẦN MỀM THẬT: nạp sổ qua `PipelineAPI.import_so_nhap` của chính workspace,
    đọc báo cáo sức khoẻ dữ liệu, chạy phân bổ thử. Cảnh báo nào cũng chặn, trừ
    `health_oversubscribed_buoi` (sự thật về độ chọi) và mã người dùng đã chấp nhận
    bằng `--chap-nhan`.
  * Raw là dữ liệu NGƯỜI THẬT: từ chối ghi đầu ra vào trong một kho git.
"""

import argparse
import base64
import collections
import csv
import difflib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unicodedata

_DAY = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.normpath(os.path.join(_DAY, "..", "..", "..", ".."))
sys.path.insert(0, GOC)

import so_nhap  # noqa: E402

# Sự thật về độ chọi (ít chỗ hơn người), không phải lỗi dữ liệu: báo trong báo cáo, không chặn.
CANH_BAO_LUON_CHO_QUA = {"health_oversubscribed_buoi", "health_oversubscribed"}
SEED_CHAY_THU = 42
DANG_NV = ("cot_xep_hang", "mot_o", "dong_dai", "ma_tran")


class LoiDung(Exception):
    """Dừng: danh sách lỗi đã đủ để báo, không đi tiếp."""

    def __init__(self, loi):
        super().__init__("%d lỗi" % len(loi))
        self.loi = loi


def _loi(ma, chi_tiet, **vi_tri):
    d = {"ma": ma, "chi_tiet": chi_tiet}
    d.update({k: v for k, v in vi_tri.items() if v not in (None, "")})
    return d


# ---------------------------------------------------------------------------
# Đọc bảng: .xlsx / .xlsm / .csv / .tsv / .txt
# ---------------------------------------------------------------------------
def _gon(chuoi) -> str:
    """Gọn khoảng trắng và đưa về dạng NFC. Raw từ Windows-1258 hay từ macOS mang dấu thanh
    ở dạng TỔ HỢP ("a" + dấu sắc rời): cùng chữ "Hà" mà hai dãy mã khác nhau, so tên sẽ trượt."""
    s = unicodedata.normalize("NFC", str(chuoi if chuoi is not None else ""))
    return " ".join(s.split())


def _giai_ma(du_lieu: bytes) -> str:
    for ma_hoa in ("utf-8-sig", "cp1258", "cp1252"):
        try:
            return du_lieu.decode(ma_hoa)
        except UnicodeDecodeError:
            continue
    return du_lieu.decode("utf-8", errors="replace")


def _doc_csv(duong):
    with open(duong, "rb") as f:
        van_ban = _giai_ma(f.read())
    dong_dau = next((d for d in van_ban.splitlines() if d.strip()), "")
    dau_tach = max([",", ";", "\t", "|"], key=dong_dau.count) if dong_dau else ","
    return [list(o) for o in csv.reader(io.StringIO(van_ban), delimiter=dau_tach)]


def cac_bang(duong):
    """{tên bảng: [hàng thô]}. CSV là một bảng tên '' ; Excel mỗi sheet một bảng."""
    if not os.path.isfile(duong):
        raise LoiDung([_loi("khong_co_tep", "Không thấy tệp.", tep=duong)])
    duoi = os.path.splitext(duong)[1].lower()
    if duoi in (".xlsx", ".xlsm"):
        import openpyxl
        wb = openpyxl.load_workbook(duong, read_only=True, data_only=True)
        try:
            return {ws.title: [[so_nhap.o_thanh_chu(v) for v in hang]
                               for hang in ws.iter_rows(values_only=True)]
                    for ws in wb.worksheets}
        finally:
            wb.close()
    if duoi in (".csv", ".tsv", ".txt"):
        return {"": _doc_csv(duong)}
    raise LoiDung([_loi("dinh_dang_tep", "Chỉ đọc .xlsx, .xlsm, .csv, .tsv, .txt "
                        "(.xls cũ: mở bằng Excel rồi lưu lại thành .xlsx).", tep=duong)])


def doc_bang(nguon, goc_spec=""):
    """nguon = {"tep", "sheet"?, "dong_tieu_de"?} -> (tiêu đề, [(số dòng Excel, ô)])."""
    if not isinstance(nguon, dict) or not nguon.get("tep"):
        raise LoiDung([_loi("spec_nguon", "Thiếu 'tep' trong một mục 'nguon'.")])
    duong = nguon["tep"]
    if not os.path.isabs(duong):
        duong = os.path.join(goc_spec, duong)
    bang = cac_bang(duong)
    ten = nguon.get("sheet")
    if ten is None:
        ten = next(iter(bang))
    if ten not in bang:
        raise LoiDung([_loi("khong_co_sheet", "Không có sheet %r (có: %s)."
                            % (ten, ", ".join(bang)), tep=duong)])
    hang = bang[ten]
    dtd = int(nguon.get("dong_tieu_de") or 1)
    if len(hang) < dtd:
        raise LoiDung([_loi("bang_rong", "Bảng rỗng.", tep=duong, sheet=ten)])
    tieu_de = [_gon(t) for t in hang[dtd - 1]]
    dong = []
    for i, o in enumerate(hang[dtd:], start=dtd + 1):
        o = [_gon(x) for x in o] + [""] * max(0, len(tieu_de) - len(o))
        if any(o):
            dong.append((i, o))
    return {"tep": os.path.basename(duong), "sheet": ten, "tieu_de": tieu_de, "dong": dong}


def _chi_so_cot(bang, ten_cot, loi, bat_buoc=True):
    if ten_cot in (None, ""):
        return None
    ung_vien = [i for i, t in enumerate(bang["tieu_de"]) if t == _gon(ten_cot)]
    if not ung_vien:
        ung_vien = [i for i, t in enumerate(bang["tieu_de"])
                    if so_nhap.khoa_ten(t) == so_nhap.khoa_ten(ten_cot)]
    if len(ung_vien) == 1:
        return ung_vien[0]
    if bat_buoc or ung_vien:
        loi.append(_loi("cot_khong_co" if not ung_vien else "cot_trung",
                        ("Không có cột %r." if not ung_vien else "Cột %r xuất hiện nhiều lần.")
                        % ten_cot, tep=bang["tep"], sheet=bang["sheet"]))
    return None


# ---------------------------------------------------------------------------
# SOI: đoán vai trò cột
# ---------------------------------------------------------------------------
_MAU_THU_TU = re.compile(r"^(?:nv|nguyen vong|lua chon|choice|top|uu tien|thu tu|rank|pref)\s*(\d+)$")
_MAU_NGOAC = re.compile(r"^(.*?)\s*\[(.+)\]\s*$")
_MAU_HANG = re.compile(r"(\d+)")
_TAI_TIENG_ANH = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
                  "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10}
_TACH_O = re.compile(r"\s*(?:;|\n|\|)\s*")


def doc_hang(o):
    """'1', 'Hạng 2', 'Lựa chọn thứ 3', '1st', 'First choice' -> số; không đọc được -> None."""
    o = _gon(o)
    if not o:
        return None
    m = _MAU_HANG.search(o)
    if m:
        return int(m.group(1))
    for chu, so in _TAI_TIENG_ANH.items():
        if chu in o.lower():
            return so
    return None


def tach_o(o, tach=None):
    """Một ô nhiều lựa chọn -> danh sách. Mặc định tách theo ; xuống dòng |, rồi mới tới dấu phẩy."""
    o = str(o or "").strip()
    if not o:
        return []
    if tach:
        phan = o.split(tach)
    elif _TACH_O.search(o):
        phan = _TACH_O.split(o)
    else:
        phan = o.split(",")
    return [_gon(p) for p in phan if _gon(p)]


def doan_cot(tieu_de, gia_tri):
    """Vai trò khả dĩ của một cột (danh sách, có thể rỗng). Chỉ là GỢI Ý cho người soạn spec —
    mọi vai trò vẫn phải được người dùng xác nhận."""
    b = so_nhap.bo_dau(tieu_de)
    co = [g for g in gia_tri if g]
    n, khac = len(co), len(set(co))
    la_so = n and all(re.fullmatch(r"-?\d+(?:[.,]\d+)?", g) for g in co)
    goi_y = []
    m = _MAU_THU_TU.match(b)
    if m:
        goi_y.append("nguyen_vong_thu_%s (dạng cot_xep_hang)" % m.group(1))
    m = _MAU_NGOAC.match(tieu_de)
    if m:
        goi_y.append("ma_tran: chỗ xếp = %r" % m.group(2))
    if re.search(r"\b(ma|id|code|so hieu|msnv|mshs|mssv|ma so)\b", b) and n:
        goi_y.append("ma" + ("" if khac == n else " (CÓ %d giá trị lặp: phiếu trùng, hoặc dạng "
                                                "dong_dai mỗi người nhiều dòng)" % (n - khac)))
    if re.search(r"\b(ho ten|ho va ten|full name|ten)\b", b) and not goi_y:
        goi_y.append("ten")
    if re.search(r"\b(thu tu|thu hang|hang|rank|order|uu tien so)\b", b) and not m:
        goi_y.append("thu_hang (dạng dong_dai)")
    elif re.search(r"\b(buoi|ngay|thu|ca|session|day|shift|dot)\b", b) and not goi_y:
        goi_y.append("buoi")
    if re.search(r"\b(suat|reserve)\b", b):
        goi_y.append("suat_uu_tien (số chỗ dành riêng)")
    elif re.search(r"\b(nhom|dien|doi tuong|cap bac|group|tier|uu tien)\b", b) and khac <= 10:
        goi_y.append("nhom_uu_tien")
    if re.search(r"\b(chi tieu|so cho|suc chua|capacity|quota|so luong|so giuong|slot)\b", b):
        goi_y.append("chi_tieu")
    if re.search(r"\b(diem|score|danh gia|ket qua)\b", b):
        goi_y.append("diem" + (" (một số mỗi người: per_person?)" if la_so else ""))
    if re.search(r"\b(dau thoi gian|timestamp|thoi gian)\b", b):
        goi_y.append("dau_thoi_gian (thứ tự phiếu)")
    if re.search(r"\b(email|e mail|dien thoai|sdt|phone)\b", b):
        goi_y.append("lien_lac (bỏ qua — không đưa vào workspace)")
    if n and sum(1 for g in co if len(tach_o(g)) >= 2) >= max(1, n // 3):
        goi_y.append("mot_o: ô chứa nhiều lựa chọn")
    if not goi_y and n and not la_so and khac <= 10 and n >= 3 * khac:
        goi_y.append("ít giá trị khác nhau: nhóm ưu tiên? buổi? hay tên chỗ (dạng dong_dai)?")
    if not goi_y and n and not la_so and khac < n:
        goi_y.append("tên chỗ xếp (dạng dong_dai)?")
    if not goi_y and n and not la_so and khac == n:
        goi_y.append("tên (người hoặc chỗ xếp)?")
    if not goi_y and la_so:
        goi_y.append("số")
    return goi_y


def soi(duong_dan):
    ket_qua = []
    for duong in duong_dan:
        for ten, hang in cac_bang(duong).items():
            hang = [h for h in hang if any(_gon(x) for x in h)]
            if not hang:
                ket_qua.append({"tep": duong, "sheet": ten, "so_dong": 0, "cot": []})
                continue
            tieu_de = [_gon(t) for t in hang[0]]
            cot = []
            for j, t in enumerate(tieu_de):
                gt = [_gon(h[j]) if j < len(h) else "" for h in hang[1:]]
                co = [g for g in gt if g]
                cot.append({
                    "cot": t, "khong_rong": len(co), "khac_nhau": len(set(co)),
                    "mau": list(dict.fromkeys(co))[:6], "doan": doan_cot(t, gt),
                })
            ket_qua.append({"tep": duong, "sheet": ten, "so_dong": len(hang) - 1,
                            "cot": cot})
    return ket_qua


def in_soi(ket_qua):
    for b in ket_qua:
        print("=== %s%s — %d dòng dữ liệu" % (b["tep"], (" / sheet %r" % b["sheet"]) if b["sheet"] else "",
                                            b["so_dong"]))
        for c in b["cot"]:
            print("  • %-32s %4d ô, %4d khác nhau  %s" % (repr(c["cot"])[:32], c["khong_rong"],
                                                         c["khac_nhau"],
                                                         ("→ " + "; ".join(c["doan"])) if c["doan"] else ""))
            if c["mau"]:
                print("      mẫu: %s" % " | ".join(m[:40] for m in c["mau"]))


# ---------------------------------------------------------------------------
# DỰNG: raw -> (clubs, students) theo spec, soát chặt
# ---------------------------------------------------------------------------
def _goi_y_ten(gia_tri, cac_ten):
    gan = difflib.get_close_matches(gia_tri, cac_ten, n=2, cutoff=0.6)
    return (" Có phải: %s?" % " / ".join(repr(g) for g in gan)) if gan else ""


class BangCho:
    """Danh sách chỗ xếp và cách tra một giá trị thô ra mã chỗ."""

    def __init__(self):
        self.ds = []                       # dict theo thứ tự
        self._theo_khoa = {}

    def them(self, cho):
        self.ds.append(cho)
        for k in {so_nhap.khoa_ten(cho["name"]), so_nhap.khoa_ten(cho["club_id"])}:
            self._theo_khoa.setdefault(k, []).append(cho)

    def tra(self, gia_tri):
        ds = self._theo_khoa.get(so_nhap.khoa_ten(gia_tri), [])
        ds = list({id(c): c for c in ds}.values())
        return ds[0] if len(ds) == 1 else None

    def ten(self):
        return [c["name"] for c in self.ds]


def _so_nguyen(o):
    so = so_nhap.doc_diem(o)
    return int(so) if so is not None and so.is_integer() else None


def doc_cho_xep(spec, goc_spec, loi, ten_tu_nguyen_vong):
    """Danh sách chỗ xếp: từ bảng nguồn nếu có, không thì từ các tên gặp trong nguyện vọng."""
    cx = spec.get("cho_xep") or {}
    chi_tieu_bo_sung = cx.get("chi_tieu") or {}
    buoi_bo_sung = cx.get("buoi") or {}
    uu_tien_bo_sung = cx.get("suat_uu_tien") or {}
    tho = []                                    # (vị trí, tên, mã, buổi, chỉ tiêu, suất, nhóm)
    if cx.get("nguon"):
        bang = doc_bang(cx["nguon"], goc_spec)
        cot = cx.get("cot") or {}
        i_ten = _chi_so_cot(bang, cot.get("ten"), loi)
        idx = {k: _chi_so_cot(bang, cot.get(k), loi) for k in
               ("ma", "buoi", "chi_tieu", "suat_uu_tien", "nhom_uu_tien")}
        if i_ten is None:
            raise LoiDung(loi + [_loi("spec_cho_xep", "Cần cho_xep.cot.ten.")])
        for so_dong, o in bang["dong"]:
            def lay(k, o=o):
                return o[idx[k]] if idx[k] is not None and idx[k] < len(o) else ""
            vt = dict(tep=bang["tep"], sheet=bang["sheet"], dong=so_dong)
            tho.append((vt, o[i_ten], lay("ma"), lay("buoi"), lay("chi_tieu"),
                        lay("suat_uu_tien"), lay("nhom_uu_tien")))
    else:
        # Không có bảng chỗ xếp: chỗ = mọi tên gặp trong nguyện vọng CỘNG mọi chỗ spec khai
        # chỉ tiêu (một chỗ không ai chọn vẫn là một chỗ, chỉ là không xuất hiện trong raw).
        da_co = {so_nhap.khoa_ten(t) for t in ten_tu_nguyen_vong}
        ten_tu_spec = [t for t in chi_tieu_bo_sung if so_nhap.khoa_ten(t) not in da_co]
        for ten in list(ten_tu_nguyen_vong) + ten_tu_spec:
            tho.append(({"nguon": "nguyện vọng"}, ten, "", "", "", "", ""))

    bang_cho = BangCho()
    da_gap_ten, da_gap_ma = {}, {}
    thieu_chi_tieu = []
    co_buoi = []
    for vt, ten, ma, buoi, chi_tieu, suat, nhom in tho:
        ten = _gon(ten)
        if not ten:
            loi.append(_loi("cho_thieu_ten", "Dòng chỗ xếp không có tên.", **vt))
            continue
        k = so_nhap.khoa_ten(ten)
        if k in da_gap_ten:
            loi.append(_loi("cho_trung_ten", "Tên chỗ %r trùng (chỉ khác hoa/thường hoặc khoảng "
                            "trắng với %r)." % (ten, da_gap_ten[k]), **vt))
            continue
        da_gap_ten[k] = ten
        ma = _gon(ma) or so_nhap.tao_ma_clb(ten)
        if ma in da_gap_ma:
            loi.append(_loi("cho_trung_ma", "Mã chỗ %r trùng giữa %r và %r — điền cột mã riêng "
                            "cho từng chỗ." % (ma, da_gap_ma[ma], ten), **vt))
            continue
        da_gap_ma[ma] = ten

        # Chỉ tiêu: ô nguồn, hoặc bảng bổ sung; có cả hai mà khác nhau là lỗi.
        ct_bs = chi_tieu_bo_sung.get(ten)
        ct = _gon(chi_tieu)
        if ct and ct_bs is not None and _so_nguyen(ct) != ct_bs:
            loi.append(_loi("chi_tieu_mau_thuan", "Chỉ tiêu của %r: raw ghi %s, spec ghi %s."
                            % (ten, ct, ct_bs), **vt))
            continue
        if not ct and ct_bs is None:
            thieu_chi_tieu.append(ten)
            continue
        cap = _so_nguyen(ct) if ct else ct_bs
        if not isinstance(cap, int) or isinstance(cap, bool) or cap <= 0:
            loi.append(_loi("chi_tieu_sai", "Chỉ tiêu của %r phải là số nguyên > 0, nhận %r."
                            % (ten, ct or ct_bs), **vt))
            continue

        b = _gon(buoi) or _gon(buoi_bo_sung.get(ten, ""))
        co_buoi.append((ten, bool(b)))

        s_bs = uu_tien_bo_sung.get(ten)
        suat_so, nhom_ten = (_so_nguyen(suat) if _gon(suat) else 0), _gon(nhom)
        if s_bs is not None:
            if not (isinstance(s_bs, list) and len(s_bs) == 2):
                loi.append(_loi("spec_suat_uu_tien", "suat_uu_tien[%r] phải là [số suất, nhóm]." % ten))
                continue
            suat_so, nhom_ten = s_bs[0], _gon(s_bs[1])
        if suat_so is None or not isinstance(suat_so, int) or suat_so < 0 or suat_so > cap:
            loi.append(_loi("suat_uu_tien_sai", "Suất ưu tiên của %r phải là số nguyên từ 0 tới "
                            "chỉ tiêu (%d), nhận %r." % (ten, cap, suat), **vt))
            continue
        if suat_so > 0 and not nhom_ten:
            loi.append(_loi("suat_khong_nhom", "%r có %d suất ưu tiên nhưng không ghi nhóm nào "
                            "được hưởng." % (ten, suat_so), **vt))
            continue
        bang_cho.them({"club_id": ma, "name": ten, "capacity": cap,
                       "reserve_capacity": suat_so, "reserve_group": nhom_ten if suat_so else "",
                       "buoi": so_nhap.ma_buoi(b)})

    if thieu_chi_tieu:
        # Tên gần giống một chỗ đã có chỉ tiêu thì gần như chắc là gõ nhầm trong raw: gợi ý, không gộp.
        co_chi_tieu = [t for t in da_gap_ten.values() if t not in thieu_chi_tieu]
        loi.append(_loi("thieu_chi_tieu", "Chưa có chỉ tiêu cho %d chỗ: %s. HỎI người dùng rồi "
                        "ghi vào cho_xep.chi_tieu — không tự đặt."
                        % (len(thieu_chi_tieu), ", ".join(
                            repr(t) + _goi_y_ten(t, co_chi_tieu) for t in thieu_chi_tieu))))
    if co_buoi and any(c for _, c in co_buoi) and not all(c for _, c in co_buoi):
        thieu = [t for t, c in co_buoi if not c]
        loi.append(_loi("buoi_thieu", "Có chỗ khai buổi, có chỗ không: khai buổi cho MỌI chỗ hoặc "
                        "không chỗ nào. Thiếu: %s." % ", ".join(repr(t) for t in thieu)))
    for ten in set(chi_tieu_bo_sung) | set(buoi_bo_sung) | set(uu_tien_bo_sung):
        if so_nhap.khoa_ten(ten) not in da_gap_ten:
            loi.append(_loi("spec_cho_la", "spec nhắc tới chỗ %r nhưng raw không có chỗ nào tên đó.%s"
                            % (ten, _goi_y_ten(ten, list(da_gap_ten.values())))))
    return bang_cho


def _doc_nguyen_vong_tho(nv_spec, bang, o, idx, so_dong, loi):
    """Một dòng người -> [(giá trị chỗ thô, hạng, ô điểm thô)] theo dạng của spec."""
    dang = nv_spec["dang"]
    vt = dict(tep=bang["tep"], sheet=bang["sheet"], dong=so_dong)
    ra = []
    if dang == "cot_xep_hang":
        for k, (i, i_d) in enumerate(zip(idx["nv"], idx["nv_diem"]), start=1):
            g = o[i] if i is not None else ""
            d = o[i_d] if i_d is not None else ""
            if g:
                ra.append((g, k, d))
            elif d:
                loi.append(_loi("diem_khong_nv", "Có điểm ở cột điểm %d nhưng ô nguyện vọng %d trống."
                                % (k, k), **vt))
    elif dang == "mot_o":
        for k, g in enumerate(tach_o(o[idx["o"]], nv_spec.get("tach")), start=1):
            ra.append((g, k, ""))
    elif dang == "ma_tran":
        for ten_cho, i in idx["ma_tran"]:
            g = o[i]
            if not g:
                continue
            h = doc_hang(g)
            if h is None:
                loi.append(_loi("hang_sai", "Ô xếp hạng %r của %r không đọc được thành số."
                                % (g, ten_cho), cot=bang["tieu_de"][i], **vt))
                continue
            ra.append((ten_cho, h, ""))
    return ra


def doc_nguoi(spec, goc_spec, loi, cfg):
    """-> (danh sách người thô theo thứ tự, ghi chú phiếu trùng, tên chỗ gặp trong nguyện vọng)."""
    ng = spec.get("nguoi") or {}
    nv_spec = ng.get("nguyen_vong") or {}
    dang = nv_spec.get("dang")
    if dang not in DANG_NV:
        raise LoiDung([_loi("spec_dang_nv", "nguoi.nguyen_vong.dang phải là một trong %s."
                            % ", ".join(DANG_NV))])
    bang = doc_bang(ng.get("nguon"), goc_spec)
    cot = ng.get("cot") or {}
    i_ma = _chi_so_cot(bang, cot.get("ma"), loi)
    i_ten = _chi_so_cot(bang, cot.get("ten"), loi, bat_buoc=bool(cot.get("ten")))
    i_nhom = _chi_so_cot(bang, cot.get("nhom"), loi, bat_buoc=bool(cot.get("nhom")))
    i_diem = _chi_so_cot(bang, cot.get("diem"), loi, bat_buoc=bool(cot.get("diem")))
    if i_ma is None:
        raise LoiDung(loi + [_loi("spec_nguoi", "Cần nguoi.cot.ma (cột mã người).")])
    if i_diem is not None and cfg["rules"]["score_scope"] != "per_person":
        loi.append(_loi("spec_diem_ca_nhan", "nguoi.cot.diem chỉ dùng khi rules.score_scope = "
                        "'per_person'."))

    idx = {}
    if dang == "cot_xep_hang":
        ds = nv_spec.get("cot") or []
        dd = nv_spec.get("cot_diem") or [None] * len(ds)
        if len(dd) != len(ds):
            loi.append(_loi("spec_cot_diem", "cot_diem phải dài bằng cot (dùng null cho NV không điểm)."))
            dd = [None] * len(ds)
        idx["nv"] = [_chi_so_cot(bang, c, loi) for c in ds]
        idx["nv_diem"] = [_chi_so_cot(bang, c, loi) if c else None for c in dd]
        # Cột "NVk" có dữ liệu mà spec bỏ sót = mất nguyện vọng trong im lặng. Chặn.
        dung = set(idx["nv"]) | set(idx["nv_diem"])
        for i, t in enumerate(bang["tieu_de"]):
            if i not in dung and (_MAU_THU_TU.match(so_nhap.bo_dau(t))
                                  or (so_nhap.bo_dau(t) and any(
                                      so_nhap.bo_dau(t) == so_nhap.bo_dau(c) + " " + str(k)
                                      for c in ("diem", cfg["labels"]["score"]["vi"])
                                      for k in range(1, 21)))):
                if any(o[i] for _, o in bang["dong"] if i < len(o)):
                    loi.append(_loi("cot_nv_bo_sot", "Cột %r có dữ liệu nhưng spec không liệt kê trong "
                                    "nguyen_vong.cot / cot_diem." % t, tep=bang["tep"], sheet=bang["sheet"]))
    elif dang == "mot_o":
        idx["o"] = _chi_so_cot(bang, nv_spec.get("cot"), loi)
    elif dang == "dong_dai":
        idx["cho"] = _chi_so_cot(bang, nv_spec.get("cot_cho"), loi)
        idx["hang"] = _chi_so_cot(bang, nv_spec.get("cot_hang"), loi,
                                  bat_buoc=bool(nv_spec.get("cot_hang")))
        idx["diem"] = _chi_so_cot(bang, nv_spec.get("cot_diem"), loi,
                                  bat_buoc=bool(nv_spec.get("cot_diem")))
    elif dang == "ma_tran":
        ma_tran = []
        if nv_spec.get("cot"):
            for c, ten_cho in nv_spec["cot"].items():
                i = _chi_so_cot(bang, c, loi)
                if i is not None:
                    ma_tran.append((ten_cho, i))
        elif nv_spec.get("tien_to") is not None:
            tt = so_nhap.khoa_ten(nv_spec["tien_to"])
            for i, t in enumerate(bang["tieu_de"]):
                m = _MAU_NGOAC.match(t)
                if m and so_nhap.khoa_ten(m.group(1)) == tt:
                    ma_tran.append((_gon(m.group(2)), i))
            if not ma_tran:
                loi.append(_loi("ma_tran_rong", "Không có cột nào dạng '%s [Tên chỗ]'." % nv_spec["tien_to"]))
        else:
            loi.append(_loi("spec_ma_tran", "ma_tran cần 'cot' {tiêu đề: tên chỗ} hoặc 'tien_to'."))
        idx["ma_tran"] = ma_tran
    diem_theo_cho = []
    for c, ten_cho in (ng.get("diem_theo_cho") or {}).items():
        i = _chi_so_cot(bang, c, loi)
        if i is not None:
            diem_theo_cho.append((ten_cho, i))
    if diem_theo_cho and cfg["rules"]["score_scope"] == "per_person":
        loi.append(_loi("spec_diem_theo_cho", "diem_theo_cho chỉ dùng khi điểm theo từng chỗ (per_slot)."))
    if loi:
        raise LoiDung(loi)

    nhom_doi = {so_nhap.khoa_ten(k): v for k, v in (ng.get("nhom_doi_ten") or {}).items()}
    phieu_trung = ng.get("phieu_trung")
    if phieu_trung not in (None, "giu_dau", "giu_cuoi"):
        raise LoiDung([_loi("spec_phieu_trung", "phieu_trung là null, 'giu_dau' hoặc 'giu_cuoi'.")])

    theo_ma = collections.OrderedDict()
    ma_dong = {}
    so_phieu_bo = []
    ten_cho_gap = []
    for so_dong, o in bang["dong"]:
        vt = dict(tep=bang["tep"], sheet=bang["sheet"], dong=so_dong)
        ma = o[i_ma]
        if not ma:
            loi.append(_loi("thieu_ma", "Dòng có dữ liệu nhưng không có mã người.", **vt))
            continue
        ten = o[i_ten] if i_ten is not None else ""
        nhom_tho = o[i_nhom] if i_nhom is not None else ""
        nhom = nhom_doi.get(so_nhap.khoa_ten(nhom_tho), nhom_tho) if nhom_tho else ""
        if dang == "dong_dai":
            g = o[idx["cho"]] if idx["cho"] is not None else ""
            h_tho = o[idx["hang"]] if idx["hang"] is not None else ""
            h = doc_hang(h_tho) if h_tho else None
            if h_tho and h is None:
                loi.append(_loi("hang_sai", "Thứ hạng %r không đọc được thành số." % h_tho, **vt))
                continue
            d = o[idx["diem"]] if idx["diem"] is not None else ""
            if ma in theo_ma:
                p = theo_ma[ma]
                if ten and p["name"] and ten != p["name"]:
                    loi.append(_loi("ten_mau_thuan", "Mã %r mang hai tên: %r (dòng %s) và %r."
                                    % (ma, p["name"], ma_dong[ma], ten), **vt))
                    continue
                if nhom != p["nhom"]:
                    loi.append(_loi("nhom_mau_thuan", "Mã %r mang hai nhóm: %r và %r."
                                    % (ma, p["nhom"], nhom), **vt))
                    continue
                diem_cn = o[i_diem] if i_diem is not None else ""
                if diem_cn != p["diem_cn"]:
                    loi.append(_loi("diem_mau_thuan", "Mã %r mang hai %s: %r và %r."
                                    % (ma, cfg["labels"]["score"]["vi"].lower(), p["diem_cn"], diem_cn),
                                    **vt))
                    continue
            else:
                theo_ma[ma] = {"ma": ma, "name": ten, "nhom": nhom, "nv": [], "dong": so_dong,
                               "diem_cn": o[i_diem] if i_diem is not None else "",
                               "diem_cho": [], "vt": vt}
                ma_dong[ma] = so_dong
            if g:
                p = theo_ma[ma]
                p["nv"].append((g, h if h is not None else 10 ** 6 + len(p["nv"]), d, vt))
                ten_cho_gap.append(g)
            continue

        if ma in theo_ma:
            if phieu_trung is None:
                loi.append(_loi("ma_trung", "Mã %r lặp lại (dòng trước: %s). Nếu đây là phiếu nộp lại, "
                                "HỎI người dùng giữ phiếu đầu hay cuối rồi đặt nguoi.phieu_trung."
                                % (ma, ma_dong[ma]), **vt))
                continue
            if phieu_trung == "giu_dau":
                so_phieu_bo.append((ma, so_dong))
                continue
            so_phieu_bo.append((ma, ma_dong[ma]))
            del theo_ma[ma]
        nv = [(g, h, d, vt) for g, h, d in _doc_nguyen_vong_tho(nv_spec, bang, o, idx, so_dong, loi)]
        diem_cho = [(ten_cho, o[i], vt) for ten_cho, i in diem_theo_cho if o[i]]
        theo_ma[ma] = {"ma": ma, "name": ten, "nhom": nhom, "nv": nv, "dong": so_dong,
                       "diem_cn": o[i_diem] if i_diem is not None else "",
                       "diem_cho": diem_cho, "vt": vt}
        ma_dong[ma] = so_dong
        ten_cho_gap.extend(g for g, _, _, _ in nv)

    # Hai mã chỉ khác hoa/thường: phần mềm coi là hai người — gần như chắc là gõ nhầm.
    theo_khoa = collections.defaultdict(list)
    for ma in theo_ma:
        theo_khoa[ma.casefold().strip()].append(ma)
    for ds in theo_khoa.values():
        if len(ds) > 1:
            loi.append(_loi("ma_khac_hoa", "Các mã %s chỉ khác hoa/thường — phần mềm coi là người "
                            "khác nhau. Sửa trong raw." % ", ".join(repr(m) for m in ds)))

    if dang == "ma_tran":
        ten_cho_gap = [t for t, _ in idx["ma_tran"]] + ten_cho_gap
    ten_cho_gap += [t for t, _ in diem_theo_cho]
    # Cùng một chỗ viết khác hoa/thường hay khoảng trắng là MỘT chỗ (phần mềm cũng so như vậy);
    # giữ cách viết gặp đầu tiên.
    ten_theo_khoa = {}
    for t in ten_cho_gap:
        ten_theo_khoa.setdefault(so_nhap.khoa_ten(t), _gon(t))
    return list(theo_ma.values()), so_phieu_bo, list(ten_theo_khoa.values())


def ghep(nguoi, bang_cho, cfg, loi):
    """Người thô + chỗ xếp -> students cho so_nhap.ghi_so_nhap, soát mọi luật."""
    luat = cfg["rules"]
    ca_nhan = luat["score_scope"] == "per_person"
    cung = luat["tier_mode"] == "strict" or luat["priority"] == "tier"
    nhom_cho = {c["reserve_group"] for c in bang_cho.ds if c["reserve_group"]}
    cac_ten = bang_cho.ten()
    students = []
    for p in nguoi:
        vt = p["vt"]
        nv, da_chon = [], {}
        for g, h, d, vt_nv in sorted(p["nv"], key=lambda x: x[1]):
            cho = bang_cho.tra(g)
            if cho is None:
                loi.append(_loi("cho_khong_co", "Nguyện vọng %r của %r không khớp chỗ xếp nào.%s"
                                % (g, p["ma"], _goi_y_ten(g, cac_ten)), **vt_nv))
                continue
            if cho["club_id"] in da_chon:
                loi.append(_loi("nv_trung", "%r xếp %r hai lần." % (p["ma"], cho["name"]), **vt_nv))
                continue
            if h in da_chon.values() and h < 10 ** 6:
                loi.append(_loi("hang_trung", "%r có hai nguyện vọng cùng hạng %d." % (p["ma"], h), **vt_nv))
                continue
            da_chon[cho["club_id"]] = h
            nv.append({"club_id": cho["club_id"], "thi": False, "diem": "", "_d": d, "_vt": vt_nv})
        for ten_cho, d, vt_d in p["diem_cho"]:
            cho = bang_cho.tra(ten_cho)
            x = next((x for x in nv if cho and x["club_id"] == cho["club_id"]), None)
            if x is None:
                loi.append(_loi("diem_khong_nv", "%r có điểm cho %r nhưng không xếp nguyện vọng chỗ đó."
                                % (p["ma"], ten_cho), **vt_d))
                continue
            if x["_d"]:
                loi.append(_loi("diem_hai_nguon", "%r có hai điểm cho %r." % (p["ma"], ten_cho), **vt_d))
                continue
            x["_d"] = d
        for x in nv:
            d = _gon(x.pop("_d"))
            vt_nv = x.pop("_vt")
            if not d:
                continue
            if ca_nhan:
                loi.append(_loi("diem_sai_che_do", "Điểm theo từng chỗ nhưng workspace chấm theo người "
                                "(per_person).", **vt_nv))
                continue
            if d.lower() == so_nhap.TU_DANH_DAU_THI:
                x["thi"] = True
                continue
            so = so_nhap.doc_diem(d)
            if so is None or so < 0:
                loi.append(_loi("diem_sai", "Điểm %r của %r không phải số ≥ 0." % (d, p["ma"]), **vt_nv))
                continue
            x["thi"], x["diem"] = True, d
        diem_cn = _gon(p["diem_cn"])
        if diem_cn and diem_cn.lower() != so_nhap.TU_DANH_DAU_THI:
            so = so_nhap.doc_diem(diem_cn)
            if so is None or so < 0:
                loi.append(_loi("diem_sai", "Điểm %r của %r không phải số ≥ 0." % (diem_cn, p["ma"]), **vt))
        # Trần mỗi buổi
        dem_nv, dem_thi = collections.Counter(), collections.Counter()
        buoi_cua = {c["club_id"]: c["buoi"] for c in bang_cho.ds}
        for x in nv:
            dem_nv[buoi_cua[x["club_id"]]] += 1
            dem_thi[buoi_cua[x["club_id"]]] += x["thi"]
        for b, n in dem_nv.items():
            if n > luat["max_choices"]:
                loi.append(_loi("qua_tran_nv", "%r có %d nguyện vọng ở buổi %s, trần là %d."
                                % (p["ma"], n, so_nhap.nhan_buoi(b) or "-", luat["max_choices"]), **vt))
        if luat["max_tests"] is not None and not ca_nhan:
            for b, n in dem_thi.items():
                if n > luat["max_tests"]:
                    loi.append(_loi("qua_tran_thi", "%r có điểm ở %d chỗ trong buổi %s, trần là %d."
                                    % (p["ma"], n, so_nhap.nhan_buoi(b) or "-", luat["max_tests"]), **vt))
        # Nhóm
        if p["nhom"]:
            if cung and p["nhom"] not in luat["tiers"]:
                loi.append(_loi("nhom_ngoai_tiers", "Nhóm %r của %r không có trong rules.tiers %s."
                                % (p["nhom"], p["ma"], luat["tiers"]), **vt))
            elif not cung and p["nhom"] not in nhom_cho:
                loi.append(_loi("nhom_mo_coi", "Nhóm %r của %r không được chỗ nào dành suất ưu tiên — "
                                "nhãn này không có tác dụng. Thêm suất ưu tiên cho nhóm, đổi tên nhóm qua "
                                "nhom_doi_ten, hoặc bỏ cột nhóm." % (p["nhom"], p["ma"]), **vt))
        students.append({"student_id": p["ma"], "name": p["name"], "reserve_group": p["nhom"],
                         "nv": nv, "diem_ca_nhan": diem_cn if ca_nhan else None})
    return students


# ---------------------------------------------------------------------------
# Kiểm bằng phần mềm thật, rồi mới ghi
# ---------------------------------------------------------------------------
def _trong_kho_git(duong):
    d = os.path.abspath(duong)
    while True:
        if os.path.exists(os.path.join(d, ".git")):
            return d
        cha = os.path.dirname(d)
        if cha == d:
            return None
        d = cha


def _tom_tat(clubs, students):
    nhu_cau = collections.Counter()
    nv1 = collections.Counter()
    nguoi_buoi = collections.defaultdict(set)
    buoi_cua = {c["club_id"]: c["buoi"] for c in clubs}
    for s in students:
        da_nv1 = set()
        for x in s["nv"]:
            nhu_cau[x["club_id"]] += 1
            b = buoi_cua[x["club_id"]]
            nguoi_buoi[b].add(s["student_id"])
            if b not in da_nv1:
                nv1[x["club_id"]] += 1
                da_nv1.add(b)
    return nhu_cau, nv1, nguoi_buoi


def viet_bao_cao(duong, spec, cfg, clubs, students, phieu_bo, canh_bao, nguon_spec):
    from i18n_errors import format_message
    nhan = cfg["labels"]
    L = {k: v["vi"] for k, v in nhan.items()}
    nhu_cau, nv1, nguoi_buoi = _tom_tat(clubs, students)
    ds_buoi = sorted({c["buoi"] for c in clubs})
    d = []
    d.append("# Báo cáo soát — %s\n" % cfg["name"])
    d.append("Tạo bởi skill `tao-workspace-tu-raw` từ `%s`. Dữ liệu là dữ liệu NGƯỜI THẬT: "
             "không đưa tệp này vào kho mã.\n" % os.path.basename(nguon_spec))
    d.append("## Từ vựng và luật\n")
    d.append("| Danh từ | Nhãn (vi) | Nhãn (en) |\n|---|---|---|")
    for k in ("person", "slot", "session", "group", "score"):
        d.append("| `%s` | %s | %s |" % (k, nhan[k]["vi"], nhan[k]["en"]))
    r = cfg["rules"]
    d.append("\nNgành `%s` · tối đa **%s** nguyện vọng / %s · %s · ưu tiên `%s` · nhóm `%s` · "
             "điểm `%s`%s\n" % (
                 cfg["industry"], r["max_choices"], L["session"].lower(),
                 ("tối đa **%s** %s có %s" % (r["max_tests"], L["slot"].lower(), L["score"].lower()))
                 if r["max_tests"] is not None else "không giới hạn số chỗ có điểm",
                 r["priority"], r["tier_mode"], r["score_scope"],
                 (" · tiers: " + ", ".join(r["tiers"])) if r["tiers"] else ""))
    d.append("## Số liệu\n")
    tong_cho = sum(c["capacity"] for c in clubs)
    d.append("- %d %s, %d %s, %d %s; tổng chỉ tiêu %d."
             % (len(students), L["person"].lower(), len(clubs), L["slot"].lower(),
                len(ds_buoi), L["session"].lower(), tong_cho))
    khong_nv = [s["student_id"] for s in students if not s["nv"]]
    d.append("- %s không khai nguyện vọng nào: %d%s." % (
        L["person"], len(khong_nv), (" (" + ", ".join(khong_nv[:20]) + ("…" if len(khong_nv) > 20 else "") + ")")
        if khong_nv else ""))
    if phieu_bo:
        d.append("- Phiếu trùng mã, ĐÃ BỎ theo `phieu_trung = %s`: %s." % (
            spec["nguoi"]["phieu_trung"], ", ".join("%s (dòng %s)" % x for x in phieu_bo)))
    d.append("\n| %s | Chỉ tiêu | Người xếp %s này | Số chỗ | Tỉ lệ chọi |\n|---|---|---|---|---|"
             % (L["session"], L["session"].lower()))
    for b in ds_buoi:
        cho_b = sum(c["capacity"] for c in clubs if c["buoi"] == b)
        n = len(nguoi_buoi.get(b, ()))
        d.append("| %s | %d | %d | %d | %s |" % (so_nhap.nhan_buoi(b) or "(một %s)" % L["session"].lower(),
                                                cho_b, n, sum(1 for c in clubs if c["buoi"] == b),
                                                ("%.2f" % (n / cho_b)) if cho_b else "-"))
    d.append("\n| %s | %s | Chỉ tiêu | Suất ưu tiên | NV1 | Tổng lượt chọn |\n|---|---|---|---|---|---|"
             % (L["slot"], L["session"]))
    for c in sorted(clubs, key=lambda c: (c["buoi"], -nv1[c["club_id"]])):
        d.append("| %s | %s | %d | %s | %d | %d |" % (
            c["name"], so_nhap.nhan_buoi(c["buoi"]) or "-", c["capacity"],
            ("%d (%s)" % (c["reserve_capacity"], c["reserve_group"])) if c["reserve_capacity"] else "-",
            nv1[c["club_id"]], nhu_cau[c["club_id"]]))
    d.append("\n## Giả định đã được người dùng xác nhận\n")
    gd = spec.get("ghi_chu_gia_dinh") or []
    d.extend("- %s" % g for g in gd) if gd else d.append("- (không ghi)")
    d.append("\n## Cảnh báo của phần mềm được cho qua\n")
    if canh_bao:
        for w in canh_bao:
            d.append("- `%s` — %s" % (w["code"], format_message(w["code"], w.get("params"), "vi", nhan)))
    else:
        d.append("- Không có.")
    d.append("\n## Đã kiểm bằng phần mềm thật\n")
    d.append("- Nạp Sổ nhập vào workspace mới qua `import_so_nhap`: thành công, 0 cảnh báo nhập.")
    d.append("- Chạy phân bổ thử (seed %d) trên một bản sao: thành công. Workspace trong zip CHƯA "
             "chạy — số bốc thăm sẽ khoá ở lần chạy đầu của người dùng." % SEED_CHAY_THU)
    with open(duong, "w", encoding="utf-8") as f:
        f.write("\n".join(d) + "\n")


def dung(duong_spec, thu_muc_ra, chap_nhan=()):
    """Toàn bộ quy trình. Trả dict kết quả; lỗi -> ném LoiDung (không ghi tệp nào)."""
    goc_kho = _trong_kho_git(thu_muc_ra)
    if goc_kho:
        raise LoiDung([_loi("ra_trong_kho_git", "Thư mục ra nằm trong kho git %s. Raw là dữ liệu người "
                            "thật — chọn một thư mục NGOÀI kho mã." % goc_kho)])
    with open(duong_spec, encoding="utf-8") as f:
        spec = json.load(f)
    goc_spec = os.path.dirname(os.path.abspath(duong_spec))

    from cau_hinh_ws import chuan_hoa
    ten_ws = _gon(spec.get("ten_workspace"))
    if not ten_ws:
        raise LoiDung([_loi("spec_ten", "Thiếu ten_workspace.")])
    try:
        cfg = chuan_hoa(dict(spec.get("cau_hinh") or {}, name=ten_ws))
    except ValueError as e:
        raise LoiDung([_loi("cau_hinh_sai", str(e))])

    loi = []
    nguoi, phieu_bo, ten_cho_gap = doc_nguoi(spec, goc_spec, loi, cfg)
    bang_cho = doc_cho_xep(spec, goc_spec, loi, ten_cho_gap)
    if loi:
        raise LoiDung(loi)
    students = ghep(nguoi, bang_cho, cfg, loi)
    if loi:
        raise LoiDung(loi)
    clubs = bang_cho.ds

    import workspace as ws
    from api import PipelineAPI

    tam = tempfile.mkdtemp(prefix="tao_ws_")
    try:
        root = os.path.join(tam, "root")
        os.makedirs(root)
        slug = ws.tao(root, ten_ws, cfg)
        ten_so = "SO_NHAP_%s.xlsx" % slug.upper().replace("-", "_")
        so_tam = os.path.join(tam, ten_so)
        so_nhap.ghi_so_nhap(so_tam, clubs, students, cfg=cfg)

        db = ws.duong_dan_db(root, slug)
        api = PipelineAPI(db, thu_muc_xuat=tam)
        with open(so_tam, "rb") as f:
            kq = api.import_so_nhap(base64.b64encode(f.read()).decode())
        from i18n_errors import format_message
        if not kq["ok"]:
            raise LoiDung([_loi("phan_mem_tu_choi", format_message(e["code"], e.get("params"), "vi",
                                                                   cfg["labels"]))
                           for e in kq["errors"]])
        canh_bao = list((kq["data"] or {}).get("warnings") or [])
        canh_bao += api.get_data_health_report()["data"]["warnings"]
        chan = [w for w in canh_bao
                if w["code"] not in CANH_BAO_LUON_CHO_QUA and w["code"] not in chap_nhan]
        if chan:
            raise LoiDung([_loi("canh_bao_phan_mem", "[%s] %s" % (
                w["code"], format_message(w["code"], w.get("params"), "vi", cfg["labels"])))
                for w in chan] + [_loi("goi_y", "Sửa raw/spec; hoặc, nếu người dùng xác nhận cảnh báo "
                                       "là đúng sự thật, chạy lại với --chap-nhan <mã>.")])
        api = None

        # Bản sao lưu lúc nạp không đi theo zip.
        thu_muc_ws = os.path.dirname(db)
        for t in os.listdir(thu_muc_ws):
            if t != ws.TEN_DB:
                p = os.path.join(thu_muc_ws, t)
                shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
        zip_tam = os.path.join(tam, slug + ".zip")
        ws.xuat_zip(root, slug, zip_tam)

        # Chạy thử trên bản sao (zip đã chụp xong, nên số bốc thăm KHÔNG bị khoá trong zip).
        r = PipelineAPI(db, thu_muc_xuat=tam).run_pipeline(seed=SEED_CHAY_THU)
        if not r["ok"]:
            raise LoiDung([_loi("chay_thu_that_bai", format_message(e["code"], e.get("params"), "vi",
                                                                    cfg["labels"]))
                           for e in r["errors"]])

        os.makedirs(thu_muc_ra, exist_ok=True)
        dich = {k: os.path.join(thu_muc_ra, ten) for k, ten in
                (("zip", slug + ".zip"), ("so", ten_so), ("bao_cao", "BAO_CAO_SOAT.md"))}
        da_co = [p for p in dich.values() if os.path.exists(p)]
        if da_co:
            raise LoiDung([_loi("de_tep", "Thư mục ra đã có %s — chọn thư mục khác hoặc xoá tay."
                                % ", ".join(os.path.basename(p) for p in da_co))])
        bao_cao_tam = os.path.join(tam, "BAO_CAO_SOAT.md")
        viet_bao_cao(bao_cao_tam, spec, cfg, clubs, students, phieu_bo,
                     [w for w in canh_bao if w["code"] in chap_nhan or w["code"] in CANH_BAO_LUON_CHO_QUA],
                     duong_spec)
        shutil.copy2(zip_tam, dich["zip"])
        shutil.copy2(so_tam, dich["so"])
        shutil.copy2(bao_cao_tam, dich["bao_cao"])
        return {"slug": slug, "tep": dich, "so_nguoi": len(students), "so_cho": len(clubs),
                "so_buoi": len({c["buoi"] for c in clubs}),
                "canh_bao_da_chap_nhan": sorted({w["code"] for w in canh_bao})}
    finally:
        shutil.rmtree(tam, ignore_errors=True)


def in_loi(ds):
    print("KHÔNG GHI TỆP NÀO — %d lỗi:" % len(ds))
    for e in ds:
        vt = ", ".join("%s %s" % (k, e[k]) for k in ("tep", "sheet", "dong", "cot", "nguon") if k in e)
        print("  ✗ [%s] %s%s" % (e["ma"], e["chi_tiet"], ("  (" + vt + ")") if vt else ""))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="lenh", required=True)
    p_soi = sub.add_parser("soi")
    p_soi.add_argument("tep", nargs="+")
    p_soi.add_argument("--json", action="store_true")
    p_dung = sub.add_parser("dung")
    p_dung.add_argument("--spec", required=True)
    p_dung.add_argument("--ra", required=True)
    p_dung.add_argument("--chap-nhan", default="")
    p_dung.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.lenh == "soi":
            kq = soi(a.tep)
            print(json.dumps(kq, ensure_ascii=False, indent=1)) if a.json else in_soi(kq)
            return 0
        chap_nhan = {m.strip() for m in a.chap_nhan.split(",") if m.strip()}
        kq = dung(a.spec, a.ra, chap_nhan)
    except LoiDung as e:
        print(json.dumps({"ok": False, "loi": e.loi}, ensure_ascii=False, indent=1)) if a.json \
            else in_loi(e.loi)
        return 1
    if a.json:
        print(json.dumps({"ok": True, **kq}, ensure_ascii=False, indent=1))
    else:
        print("Đã dựng workspace %r: %d người, %d chỗ, %d buổi." % (kq["slug"], kq["so_nguoi"],
                                                                 kq["so_cho"], kq["so_buoi"]))
        for t in kq["tep"].values():
            print("   → %s" % t)
    return 0


if __name__ == "__main__":
    sys.exit(main())
