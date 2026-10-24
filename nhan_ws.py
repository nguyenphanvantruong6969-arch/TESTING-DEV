"""
nhan_ws.py
==========
Từ vựng của workspace: điền nhãn (Học sinh / Câu lạc bộ / Buổi / Nhóm ưu tiên /
Điểm, hay "Nhân viên / Dự án / …") vào câu chữ có chỗ giữ `{person}`, `{slot}`…

KHÔNG phụ thuộc gì (không import cau_hinh_ws, không import rbda_priority_pipeline)
vì i18n_errors.py — mà rbda_priority_pipeline.py import — cũng dùng nó. Bản đối
xứng ở phía giao diện là `nounText` trong i18n.js; hai bản PHẢI cho cùng kết quả
(tests/test_ws_nhan.py so từng ca).

Cú pháp chỗ giữ:  {danh_tu}  hoặc  {danh_tu_<cờ>}  với danh_tu thuộc DANH_TU
và <cờ> là một hay nhiều chữ trong "lpsacuv", ví dụ {slot_sl}:
    l  chữ thường                   {person_l}  -> "học sinh"
    p  số nhiều (chỉ tiếng Anh)     {person_p}  -> "Students"
    s  dạng viết tắt                {slot_s}    -> "CLB" (chỉ khi nhãn đúng là
                                                  "Câu lạc bộ"; nhãn khác không
                                                  có dạng viết tắt nên giữ nguyên)
    a  kèm mạo từ a/an (chỉ tiếng Anh)  {slot_la} -> "a club", "an employee"
    c  viết hoa chữ đầu của kết quả     {person_lac} -> "A student"
    u  VIẾT HOA TOÀN BỘ                 {slot_u}    -> "CÂU LẠC BỘ" (tiêu đề in hoa)
    v  luôn lấy nhãn TIẾNG VIỆT         {score_v}   -> "Điểm" (cả trong câu tiếng Anh)
       — dùng khi câu nhắc đến chữ có thật trên một tệp tiếng Việt (tiêu đề cột, tên
       sheet của Sổ nhập), vì tệp luôn viết bằng nhãn `vi`.
Cờ ghép được ({slot_sl}), áp theo thứ tự s -> l -> p -> a -> c -> u. Chữ viết tắt (toàn
chữ HOA, như "CLB", "HR") không bị hạ thường.

Vì sao có cờ `s`: tiếng Việt của trường học viết "CLB" ở rất nhiều chỗ, nhưng nhãn
chuẩn là "Câu lạc bộ". Không có dạng viết tắt thì chữ hiện lên màn hình đổi đi
so với trước khi có workspace — và quy tắc của dự án là với mặc định trường học
mọi chuỗi phải GIỐNG HỆT.
"""

from __future__ import annotations

import copy
import re

DANH_TU = ("person", "slot", "session", "group", "score")

# Nhãn MẶC ĐỊNH của trường học — nguồn duy nhất; cau_hinh_ws.py lấy từ đây.
NHAN_MAC_DINH = {
    "person": {"vi": "Học sinh", "en": "Student"},
    "slot": {"vi": "Câu lạc bộ", "en": "Club"},
    "session": {"vi": "Buổi", "en": "Session"},
    "group": {"vi": "Nhóm ưu tiên", "en": "Priority group"},
    "score": {"vi": "Điểm", "en": "Score"},
}

# Dạng viết tắt đã quen dùng (vi). Chỉ áp cho ĐÚNG nhãn này.
_VIET_TAT = {("slot", "Câu lạc bộ"): "CLB"}

_RE_CHO_GIU = re.compile(r"\{(person|slot|session|group|score)(?:_([lpsacuv]+))?\}")


def nhan_ngon_ngu(nhan: dict | None, danh_tu: str, lang: str = "vi") -> str:
    """Nhãn của `danh_tu` theo `lang`; en trống hoặc thiếu thì rơi về vi.

    Danh từ không khai (hoặc khai rỗng) thì lấy NGUYÊN cặp mặc định trường học.
    Khai `vi` mà bỏ `en` thì `en` = `vi` đó (không phải `en` mặc định: "Student"
    đứng cạnh "Nhân viên" là sai).
    """
    cap = ((nhan or {}).get(danh_tu)) or NHAN_MAC_DINH[danh_tu]
    vi = str(cap.get("vi") or "").strip() or NHAN_MAC_DINH[danh_tu]["vi"]
    if lang == "vi":
        return vi
    return str(cap.get(lang) or "").strip() or vi


def _so_nhieu(chu: str, lang: str) -> str:
    """Tiếng Anh thêm s/es/ies; tiếng Việt không có số nhiều."""
    if lang != "en" or not chu or not _la_chu_anh(chu):
        return chu
    thuong = chu.lower()
    if re.search(r"(s|x|z|ch|sh)$", thuong):
        return chu + "es"
    if re.search(r"[^aeiou]y$", thuong):
        return chu[:-1] + "ies"
    return chu + "s"


def _ha_thuong(chu: str) -> str:
    # Chữ viết tắt (CLB, HR) giữ nguyên: "clb" không phải một từ.
    if chu.isupper():
        return chu
    return chu.lower()


_RE_LATIN_DON = re.compile(r"[A-Za-z][A-Za-z '\-]*")


def _la_chu_anh(chu: str) -> bool:
    """Nhãn có đúng là chữ Anh (chỉ chữ cái Latin không dấu) không?

    Nhãn `en` để trống thì rơi về nhãn tiếng Việt; thêm "s" hay "a/an" vào chữ
    Việt đó ("nhân viêns", "a nhân viên") là sai. Nhãn tiếng Anh thật gần như
    luôn là chữ Latin không dấu, nên chỉ chúng được chia số nhiều / thêm mạo từ.
    """
    return bool(_RE_LATIN_DON.fullmatch(chu))


def dang_chu(nhan: dict | None, danh_tu: str, co: str = "", lang: str = "vi") -> str:
    """Một chỗ giữ đã giải: nhãn + cờ ("l", "p", "s", "a", "c" hoặc ghép, vd "sl")."""
    if "v" in co:
        lang = "vi"
    chu = nhan_ngon_ngu(nhan, danh_tu, lang)
    if "s" in co and lang == "vi":
        chu = _VIET_TAT.get((danh_tu, chu), chu)
    # Hạ thường TRƯỚC khi chia số nhiều: "HR" giữ nguyên rồi mới thành "HRs".
    if "l" in co:
        chu = _ha_thuong(chu)
    if "p" in co:
        chu = _so_nhieu(chu, lang)
    if "a" in co and lang == "en" and chu and _la_chu_anh(chu):
        # Chọn a/an theo CHỮ CÁI đầu ("an employee", "a user"): đủ cho nhãn ngắn
        # người ta đặt; các ngoại lệ về âm ("an hour") không đáng thêm luật.
        chu = ("an " if chu[0].lower() in "aeiou" else "a ") + chu
    if "c" in co and chu:
        chu = chu[0].upper() + chu[1:]
    if "u" in co:
        chu = chu.upper()
    return chu


def dien(mau: str, nhan: dict | None = None, lang: str = "vi",
         thoat_ngoac: bool = False) -> str:
    """Thay mọi `{person}`, `{slot_l}`… trong `mau` bằng nhãn.

    Chỉ chạm tới chỗ giữ danh từ: mọi `{tham_so}` khác để nguyên cho `str.format`
    hay bộ điền của giao diện. `nhan` None = mặc định trường học.

    `thoat_ngoac`: gấp đôi `{` `}` TRONG nhãn đã điền (`{{`, `}}`) — dùng khi chuỗi
    kết quả còn phải đi qua `str.format`, để nhãn người dùng đặt có ngoặc nhọn thì
    không bị coi là tham số.
    """
    if not isinstance(mau, str) or "{" not in mau:
        return mau

    def doi(m):
        chu = dang_chu(nhan, m.group(1), m.group(2) or "", lang)
        return chu.replace("{", "{{").replace("}", "}}") if thoat_ngoac else chu

    return _RE_CHO_GIU.sub(doi, mau)


def sao_nhan_mac_dinh() -> dict:
    return copy.deepcopy(NHAN_MAC_DINH)
