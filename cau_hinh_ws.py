"""
cau_hinh_ws.py
==============
Cấu hình của một không gian làm việc (workspace): TỪ VỰNG (6 danh từ, mỗi
danh từ có nhãn vi/en) và LUẬT XẾP. Lưu TRONG app.db của chính workspace đó,
bảng `workspace_settings(key, value)`, một hàng khoá 'config' chứa JSON.

Giá trị mặc định là của TRƯỜNG HỌC (`MAC_DINH_TRUONG_HOC`). Thiếu hàng, hỏng
JSON, hay thiếu một khoá đều cho ra mặc định — nên CSDL cũ và mọi test cũ chạy
y như trước khi có module này.

Module này CHỈ đọc/ghi/kiểm cấu hình; việc dùng nó nằm ở chỗ khác. Các luật xếp
(`priority`, `tier_mode`, `score_scope`, `tiers`) được rbda_priority_pipeline.py
đọc (qua `luat_xep_cua`, `tham_so_luat`) và thật sự đổi AI ĐƯỢC SUẤT, dấu vân tay
kết quả và `run_history.luat_xep`; `max_choices`/`max_tests` là trần nhập liệu của
api_*.py; nhãn đi vào giao diện, sổ nhập và tệp xuất. Sửa cấu hình là sửa kết quả:
nơi quyết định (chạy xếp, trần nhập) phải đọc bằng `doc_cau_hinh(nghiem=True)`.
"""

from __future__ import annotations

import copy
import json
import os
import sqlite3

from nhan_ws import DANH_TU, NHAN_MAC_DINH
from rbda_priority_pipeline import (
    TRAN_CLB_THI_MOI_BUOI,
    TRAN_NGUYEN_VONG_MOI_BUOI,
    connect_db,
)

KHOA_CAU_HINH = "config"

# Đọc cấu hình chỉ chờ khoá ngắn (mặc định của kết nối là 3 s từ A13.11): thao tác nào cũng đọc nó ở đầu,
# nên CSDL đang bị tiến trình khác giữ thì báo "đang bận" sau vài giây chứ không đứng hình.
CHO_KHOA_DOC_CAU_HINH_MS = 2500

# Sáu danh từ (DANH_TU, nguồn duy nhất ở nhan_ws.py): mọi nhãn hiển thị đều đi qua
# chúng, nên tập này là cố định — gõ sai tên danh từ phải báo lỗi chứ không được
# lặng lẽ thành một nhãn mồ côi.

NGANH = ("school", "company", "event", "custom")
UU_TIEN = ("score", "tier", "score+tier")
CHE_DO_NHOM = ("reserve", "strict")
PHAM_VI_DIEM = ("per_slot", "per_person")

# Trần hợp lệ của hai con số luật (khoảng đóng).
_MAX_CHOICES_TOI_DA = 20
_MAX_TESTS_TOI_DA = 20

# max_choices / max_tests lấy từ hai hằng của thuật toán — KHÔNG gõ lại con số
# lần thứ hai ở đây, để đổi trần ở một nơi thì mặc định đổi theo.
MAC_DINH_TRUONG_HOC = {
    "name": "",
    "industry": "school",
    "labels": copy.deepcopy(NHAN_MAC_DINH),
    "rules": {
        "max_choices": TRAN_NGUYEN_VONG_MOI_BUOI,
        "max_tests": TRAN_CLB_THI_MOI_BUOI,
        "priority": "score",
        "tier_mode": "reserve",
        "score_scope": "per_slot",
        "tiers": [],
        # Điểm Wharton (mục A13): mặc định BẬT (A13.13, Truong duyệt — ngoại lệ bất biến 1).
        # Xem `_chuan_hoa` về điều kiện bật; tổ hợp không cho phép mà không ghi rõ
        # `wharton` thì tự tắt.
        "wharton": True,
        # FA-DAA (mục A13, FA-1): mặc định TẮT ở mọi nơi. Bật cần `wharton` (huy chương dùng
        # `wharton_bids`), priority score / score+tier và per_slot.
        "fa_daa": False,
        # FA gaps (sau khi xếp): mặc định TẮT, chỉ dùng được khi `fa_daa` bật. KHÔNG thuộc luật xếp
        # (`LUAT_XEP_MAC_DINH`), nên không bao giờ vào `run_history.luat_xep` hay dấu vân tay kết quả.
        "fa_diem_danh": False,      # GAP-1/GAP-2: điểm danh 3 buổi đầu + mời danh sách chờ
    },
}

# Các cờ sau khi xếp (FA gaps): bool, chỉ bật được khi `fa_daa` bật (`FaTinhNangCanFa`).
CO_SAU_XEP = ("fa_diem_danh",)


def _tron_sau(mac_dinh: dict, ghi_de: dict) -> dict:
    """Trộn `ghi_de` lên bản sao của `mac_dinh`; dict trộn đệ quy, còn lại thay hẳn.

    Danh sách (`tiers`) và `None` (`max_tests` = không giới hạn) THAY chứ không
    trộn: `None` là một giá trị có nghĩa, không phải "thiếu".
    """
    kq = copy.deepcopy(mac_dinh)
    for khoa, gia_tri in ghi_de.items():
        if isinstance(gia_tri, dict) and isinstance(kq.get(khoa), dict):
            kq[khoa] = _tron_sau(kq[khoa], gia_tri)
        else:
            kq[khoa] = copy.deepcopy(gia_tri)
    return kq


def _nhan_thieu_en_lay_vi(goc: dict, da_tron: dict) -> None:
    """Danh từ mà `goc` có `vi` nhưng không có `en` thì `en` = `vi`.

    Trộn đệ quy sẽ lấp chỗ trống đó bằng `en` MẶC ĐỊNH ("Student" cạnh
    "Nhân viên") — sai. Nhãn là một cặp đi cùng nhau; đã đặt `vi` mới thì
    `en` không đặt phải rơi về chính `vi` đó, đúng như quy tắc ghi.
    """
    nhan_goc = goc.get("labels")
    if not isinstance(nhan_goc, dict):
        return
    for dt, cap in nhan_goc.items():
        if (isinstance(cap, dict) and dt in da_tron["labels"]
                and "vi" in cap and not cap.get("en")):
            da_tron["labels"][dt]["en"] = da_tron["labels"][dt]["vi"]


class FaCanDiemQuyetTam(ValueError):
    """FA-N3: bật `fa_daa` khi `wharton` (điểm quyết tâm) đang tắt hoặc không dùng được."""


class FaTinhNangCanFa(ValueError):
    """FA gaps: bật một cờ sau khi xếp (`khoa`, xem `CO_SAU_XEP`) khi `fa_daa` chưa bật."""

    def __init__(self, khoa):
        super().__init__("%s chỉ dùng được khi fa_daa bật." % khoa)
        self.khoa = khoa


class NhanTrung(ValueError):
    """Hai danh từ có CÙNG nhãn (sau strip + casefold, riêng vi và riêng en).

    Cột của Sổ nhập đọc theo TÊN: hai danh từ trùng nhãn thì hai cột trùng tên và sổ bị đọc
    nhầm (vd nhóm ưu tiên đặt tên "Lớp" cạnh cột Lớp). Mang `a`, `b` (khoá danh từ) và `nhan`."""

    def __init__(self, a, b, nhan):
        super().__init__("Hai danh từ %s và %s đang cùng nhãn %r; mỗi danh từ cần một nhãn riêng."
                         % (a, b, nhan))
        self.a, self.b, self.nhan = a, b, nhan


def cac_cap_nhan_trung(labels: dict) -> list:
    """[(a, b, nhãn)] — mọi cặp danh từ cùng nhãn trong `labels` (đã chuẩn hoá), theo thứ tự
    DANH_TU; vi và en xét riêng. Cùng một cặp chỉ nêu một lần."""
    ra, da_co = [], set()
    for ngon in ("vi", "en"):
        thay: dict = {}
        for dt in DANH_TU:
            nhan = str((labels.get(dt) or {}).get(ngon) or "").strip()
            khoa = nhan.casefold()
            if not khoa:
                continue
            if khoa in thay and (thay[khoa], dt) not in da_co:
                da_co.add((thay[khoa], dt))
                ra.append((thay[khoa], dt, nhan))
            thay.setdefault(khoa, dt)
    return ra


def _cap_trung_day_du(labels: dict) -> list:
    """[(ngôn ngữ, a, b, nhãn)] — MỌI cặp danh từ cùng nhãn (a đứng trước b trong DANH_TU), vi và
    en riêng. Khác `cac_cap_nhan_trung` (mỗi danh từ chỉ ghép với người giữ nhãn ĐẦU TIÊN): ba danh
    từ cùng nhãn cho ba cặp. Dùng để so với cấu hình cũ khi lưu (T1b)."""
    ra = []
    for ngon in ("vi", "en"):
        for i, a in enumerate(DANH_TU):
            na = str((labels.get(a) or {}).get(ngon) or "").strip()
            if not na:
                continue
            for b in DANH_TU[i + 1:]:
                nb = str((labels.get(b) or {}).get(ngon) or "").strip()
                if nb and nb.casefold() == na.casefold():
                    ra.append((ngon, a, b, nb))
    return ra


def _la_so_nguyen(v) -> bool:
    # bool là lớp con của int: True không được lọt qua như "1".
    return isinstance(v, int) and not isinstance(v, bool)


def _ghi_ro_wharton(cfg) -> bool:
    """`cfg` (thô) có ghi khoá `rules.wharton` không?"""
    return isinstance(cfg, dict) and isinstance(cfg.get("rules"), dict) \
        and "wharton" in cfg["rules"]


def _chuan_hoa(cfg, kiem_trung: bool = True) -> dict:
    """Trộn `cfg` lên mặc định, kiểm, và trả bản ĐẦY ĐỦ đã chuẩn hoá.

    Ném ValueError với câu nói rõ trường nào sai. Không sửa `cfg` của người gọi.
    """
    if not isinstance(cfg, dict):
        raise ValueError("Cấu hình phải là một từ điển (dict).")

    la_khoa_la = set(cfg) - set(MAC_DINH_TRUONG_HOC)
    if la_khoa_la:
        raise ValueError("Khoá cấu hình không hợp lệ: %s." % ", ".join(sorted(map(str, la_khoa_la))))

    for muc in ("labels", "rules"):
        if muc in cfg and not isinstance(cfg[muc], dict):
            raise ValueError("'%s' phải là một từ điển (dict)." % muc)

    kq = _tron_sau(MAC_DINH_TRUONG_HOC, cfg)
    _nhan_thieu_en_lay_vi(cfg, kq)

    # --- tên, ngành ---
    if not isinstance(kq["name"], str):
        raise ValueError("name phải là chuỗi.")
    kq["name"] = kq["name"].strip()
    if kq["industry"] not in NGANH:
        raise ValueError("industry phải là một trong %s, nhận %r." % (list(NGANH), kq["industry"]))

    # --- nhãn ---
    la_dt = set(kq["labels"]) - set(DANH_TU)
    if la_dt:
        raise ValueError("Danh từ không hợp lệ trong labels: %s (chỉ có %s)."
                         % (", ".join(sorted(map(str, la_dt))), list(DANH_TU)))
    for dt in DANH_TU:
        cap = kq["labels"][dt]
        if not isinstance(cap, dict):
            raise ValueError("labels.%s phải là {'vi': ..., 'en': ...}." % dt)
        vi, en = cap.get("vi"), cap.get("en")
        if not isinstance(vi, str) or not vi.strip():
            raise ValueError("labels.%s.vi không được để trống." % dt)
        if en is not None and not isinstance(en, str):
            raise ValueError("labels.%s.en phải là chuỗi." % dt)
        vi = vi.strip()
        en = (en or "").strip()
        # Nhãn thành tiêu đề cột / tên sheet của Sổ nhập và tệp xuất. Chữ mở đầu bằng = + - @
        # bị Excel hiểu thành công thức (openpyxl ghi "=..." thành ô công thức thật), mà nhãn
        # có thể đến từ zip nhập vào. Không chấp nhận; đọc cấu hình hỏng thì rơi về mặc định.
        for ngon, chu in (("vi", vi), ("en", en)):
            if chu[:1] in ("=", "+", "-", "@"):
                raise ValueError("labels.%s.%s không được bắt đầu bằng '%s' "
                                 "(Excel sẽ hiểu là công thức)." % (dt, ngon, chu[0]))
        kq["labels"][dt] = {"vi": vi, "en": en or vi}
    # Hai danh từ cùng nhãn làm Sổ nhập đọc nhầm cột (A14). Chỉ chặn khi GHI / kiểm cấu hình mới;
    # cấu hình ĐÃ LƯU từ trước mà trùng vẫn đọc được (`doc_cau_hinh` truyền kiem_trung=False).
    if kiem_trung:
        trung = cac_cap_nhan_trung(kq["labels"])
        if trung:
            raise NhanTrung(*trung[0])

    # --- luật ---
    luat = kq["rules"]
    la_luat = set(luat) - set(MAC_DINH_TRUONG_HOC["rules"])
    if la_luat:
        raise ValueError("Luật không hợp lệ: %s." % ", ".join(sorted(map(str, la_luat))))

    mc = luat["max_choices"]
    if not _la_so_nguyen(mc) or not 1 <= mc <= _MAX_CHOICES_TOI_DA:
        raise ValueError("max_choices phải là số nguyên từ 1 đến %d, nhận %r."
                         % (_MAX_CHOICES_TOI_DA, mc))

    mt = luat["max_tests"]
    if mt is not None and (not _la_so_nguyen(mt) or not 0 <= mt <= _MAX_TESTS_TOI_DA):
        raise ValueError("max_tests phải là số nguyên từ 0 đến %d hoặc None (không giới hạn), nhận %r."
                         % (_MAX_TESTS_TOI_DA, mt))

    for khoa, cho_phep in (("priority", UU_TIEN), ("tier_mode", CHE_DO_NHOM),
                           ("score_scope", PHAM_VI_DIEM)):
        if luat[khoa] not in cho_phep:
            raise ValueError("%s phải là một trong %s, nhận %r." % (khoa, list(cho_phep), luat[khoa]))

    bat_wharton = luat["wharton"]
    if not isinstance(bat_wharton, bool):
        raise ValueError("wharton phải là true hoặc false, nhận %r." % (bat_wharton,))
    cho_phep_wharton = (luat["priority"] in ("score", "score+tier")
                        and luat["score_scope"] == "per_slot")
    if bat_wharton and not cho_phep_wharton and not _ghi_ro_wharton(cfg):
        # Mặc định bật (A13.13): cấu hình đổi priority / score_scope mà không nhắc tới
        # `wharton` thì thừa hưởng True rồi bị từ chối — nên tự tắt. Chỉ ghi RÕ true mới lỗi.
        bat_wharton = luat["wharton"] = False
    if bat_wharton and not cho_phep_wharton:
        raise ValueError(
            "wharton chỉ dùng được khi priority là score hoặc score+tier và score_scope là "
            "per_slot (điểm Wharton cần biết em có thi CLB nào).")

    bat_fa = luat["fa_daa"]
    if not isinstance(bat_fa, bool):
        raise ValueError("fa_daa phải là true hoặc false, nhận %r." % (bat_fa,))
    if bat_fa and not bat_wharton:
        raise FaCanDiemQuyetTam(
            "fa_daa chỉ dùng được khi wharton bật (huy chương dùng bảng điểm Wharton) và "
            "priority là score hoặc score+tier, score_scope là per_slot.")

    for khoa in CO_SAU_XEP:
        if not isinstance(luat[khoa], bool):
            raise ValueError("%s phải là true hoặc false, nhận %r." % (khoa, luat[khoa]))
        if luat[khoa] and not bat_fa:
            raise FaTinhNangCanFa(khoa)

    tiers = luat["tiers"]
    if not isinstance(tiers, list) or not all(isinstance(t, str) and t.strip() for t in tiers):
        raise ValueError("tiers phải là danh sách tên nhóm (chuỗi không rỗng).")
    luat["tiers"] = [t.strip() for t in tiers]
    if len(set(luat["tiers"])) != len(luat["tiers"]):
        raise ValueError("tiers có tên nhóm trùng nhau.")

    return kq


def tron_len(da_luu: dict, moi: dict) -> dict:
    """Trộn cấu hình `moi` (có thể chỉ một phần) lên cấu hình `da_luu` của workspace.

    Khác `chuan_hoa` (trộn lên mặc định trường học): đây là cho CẬP NHẬT — phần `moi` không
    nhắc tới thì giữ nguyên như đã lưu. `labels`: thay nguyên CẶP vi/en của danh từ nào được
    nhắc tới (nhãn là một cặp đi cùng nhau, xem `_nhan_thieu_en_lay_vi`); `rules`: thay từng
    khoá; khoá cấp trên (name, industry...): thay. Không sửa đầu vào, không kiểm — người gọi
    đưa kết quả qua `ghi_cau_hinh`.
    """
    kq = copy.deepcopy(da_luu)
    if not isinstance(moi, dict):
        return kq
    for khoa, gia_tri in moi.items():
        if khoa in ("labels", "rules") and isinstance(gia_tri, dict) \
                and isinstance(kq.get(khoa), dict):
            kq[khoa].update(copy.deepcopy(gia_tri))
        else:
            kq[khoa] = copy.deepcopy(gia_tri)
    # Đổi priority / score_scope sang tổ hợp không dùng được Wharton mà không nhắc tới
    # `wharton` (A13.13): tắt nó, vì giá trị đã lưu (True) không còn hợp. Ghi rõ thì giữ nguyên
    # để `ghi_cau_hinh` báo lỗi.
    luat_moi = moi.get("rules")
    luat = kq.get("rules")
    if isinstance(luat_moi, dict) and isinstance(luat, dict) and "wharton" not in luat_moi \
            and luat.get("wharton") is True \
            and (luat.get("priority") not in ("score", "score+tier")
                 or luat.get("score_scope") != "per_slot"):
        luat["wharton"] = False
    return kq


def chuan_hoa(cfg: dict, kiem_trung: bool = True) -> dict:
    """Kiểm `cfg` (có thể thiếu khoá) và trả bản đầy đủ đã chuẩn hoá — không ghi gì.

    Cho nơi khác cần biết một cấu hình có hợp lệ không TRƯỚC khi làm việc tốn
    kém (vd dựng thư mục workspace). Ném ValueError như `ghi_cau_hinh`.
    `kiem_trung=False`: bỏ riêng phép kiểm nhãn trùng (nhân bản workspace cũ, T1b).
    """
    return _chuan_hoa(cfg, kiem_trung=kiem_trung)


def doc_cau_hinh(db_path: str, nghiem: bool = False) -> dict:
    """Cấu hình của workspace ở `db_path`, trộn lên mặc định trường học.

    Mặc định không bao giờ ném: tệp chưa có, bảng chưa có (CSDL cũ), hàng chưa có, JSON
    hỏng, hay giá trị không qua được kiểm đều cho ra mặc định. Đọc KHÔNG tạo
    tệp hay bảng — chỉ ghi mới làm vậy. Luôn trả bản sao mới.

    `nghiem=True` dành cho nơi ĐỌC RỒI GHI LẠI cấu hình (đổi tên, nhân bản, lưu mẫu):
    "mặc định" thay cho một cấu hình hiện có mà đọc không được (JSON hỏng, khoá lạ do bản
    phần mềm mới hơn ghi, CSDL đang bị khoá…) rồi được ghi đè lên chính nó là xoá lặng lẽ
    nhãn và luật của workspace. Ở chế độ này, CHỈ ba trường hợp "chưa có cấu hình" (tệp,
    bảng, hàng chưa có) cho ra mặc định; còn lại ném ValueError / sqlite3.Error.
    """
    mac_dinh = copy.deepcopy(MAC_DINH_TRUONG_HOC)
    if not os.path.isfile(db_path):
        return mac_dinh
    try:
        conn = connect_db(db_path, CHO_KHOA_DOC_CAU_HINH_MS)
        try:
            co_bang = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'workspace_settings'"
            ).fetchone()
            if not co_bang:
                return mac_dinh
            dong = conn.execute(
                "SELECT value FROM workspace_settings WHERE key = ?", (KHOA_CAU_HINH,)
            ).fetchone()
        finally:
            conn.close()
        if not dong or dong[0] is None:
            return mac_dinh
        return _chuan_hoa(json.loads(dong[0]), kiem_trung=False)
    except (sqlite3.Error, ValueError):
        # json.JSONDecodeError là con của ValueError, nên một câu bắt đủ cả
        # JSON hỏng lẫn giá trị sai.
        if nghiem:
            raise
        return mac_dinh


def ghi_cau_hinh(db_path: str, cfg: dict, nhan_goc: dict | None = None) -> dict:
    """Kiểm rồi ghi cấu hình. Trả về bản đầy đủ đã chuẩn hoá và đã ghi.

    `cfg` có thể thiếu khoá (trộn lên mặc định). Ghi BẢN ĐẦY ĐỦ chứ không ghi
    phần thiếu: luật là thứ làm ra kết quả đã công bố, nên đổi mặc định trong
    mã sau này không được lặng lẽ đổi luật của một workspace đã tạo.

    `nhan_goc`: nhãn (`labels`) dùng làm mốc so cặp trùng thay cho nhãn đang lưu (nhân bản workspace
    cũ). None = so với nhãn đang lưu ở `db_path`.

    Raises:
        ValueError: `cfg` sai — chưa ghi gì.
    """
    day_du = _chuan_hoa(cfg, kiem_trung=False)
    # T1b: chỉ chặn cặp danh từ trùng nhãn MỚI so với cấu hình đang lưu. Workspace cũ đã trùng
    # từ trước vẫn đổi tên / đổi luật được; sửa nhãn cho hết trùng thì đương nhiên qua.
    goc = nhan_goc if nhan_goc is not None else doc_cau_hinh(db_path)["labels"]
    # Khoá gồm cả nhãn (casefold): đổi một cặp trùng sang nhãn khác mà vẫn trùng là cặp MỚI (C1 trên main).
    da_co = {(ngon, a, b, n.casefold()) for ngon, a, b, n in _cap_trung_day_du(goc)}
    moi = [x for x in _cap_trung_day_du(day_du["labels"])
           if (x[0], x[1], x[2], x[3].casefold()) not in da_co]
    if moi:
        moi.sort(key=lambda x: (DANH_TU.index(x[1]), DANH_TU.index(x[2]), x[0] != "vi"))
        raise NhanTrung(moi[0][1], moi[0][2], moi[0][3])
    conn = connect_db(db_path)
    try:
        # Tự dựng bảng: workspace dựng từ CSDL cũ chưa qua init_db vẫn ghi được.
        conn.execute(
            "CREATE TABLE IF NOT EXISTS workspace_settings (key TEXT PRIMARY KEY, value TEXT)")
        conn.execute(
            "INSERT OR REPLACE INTO workspace_settings (key, value) VALUES (?, ?)",
            (KHOA_CAU_HINH, json.dumps(day_du, ensure_ascii=False)),
        )
        conn.commit()
    finally:
        conn.close()
    return day_du


def nhan(cfg: dict, noun: str, lang: str) -> str:
    """Nhãn của danh từ `noun` theo ngôn ngữ `lang`; thiếu hay rỗng thì rơi về vi."""
    if noun not in DANH_TU:
        raise ValueError("Danh từ không hợp lệ: %r (chỉ có %s)." % (noun, list(DANH_TU)))
    cap = (cfg.get("labels") or {}).get(noun) or MAC_DINH_TRUONG_HOC["labels"][noun]
    return cap.get(lang) or cap.get("vi") or MAC_DINH_TRUONG_HOC["labels"][noun]["vi"]
