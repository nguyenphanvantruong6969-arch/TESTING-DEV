"""Tìm Chromium cho các test giao diện (Playwright).

Trước đây mười một tệp test tự ghi cứng một đường dẫn chỉ có trên máy phát
triển (`/opt/pw-browsers/chromium-1194/...`). Máy khác — kể cả máy CI — không
có đúng đường dẫn đó, nên TOÀN BỘ test giao diện lặng lẽ bị bỏ qua mà bộ test
vẫn báo xanh. Giờ tìm theo thứ tự:

  1. biến môi trường RBDA_TEST_CHROMIUM (chỉ định thẳng);
  2. bất kỳ bản Chromium nào trong /opt/pw-browsers (máy phát triển): `chromium-N/chrome-linux64/
     chrome`, `chromium-N/chrome-linux/chrome`, hoặc tệp/liên kết `chromium` chạy được;
  3. trình duyệt Playwright tự tải (`playwright install chromium`, như CI).

Không tìm thấy thì CHROMIUM là None và test giao diện tự bỏ qua.
"""

import glob
import os


_GOC_MAC_DINH = "/opt/pw-browsers"

# Bố cục Playwright đã gặp: bản cũ `chromium-N/chrome-linux/chrome`, bản mới
# `chromium-N/chrome-linux64/chrome`, và một đường dẫn/liên kết `chromium` chạy được thẳng.
_MAU_TRONG_GOC = ("chromium-*/chrome-linux64/chrome", "chromium-*/chrome-linux/chrome")


def _chay_duoc(duong: str) -> bool:
    return os.path.isfile(duong) and os.access(duong, os.X_OK)


def _tim(goc: str = _GOC_MAC_DINH) -> "str | None":
    tu_chon = os.environ.get("RBDA_TEST_CHROMIUM", "")
    if tu_chon and os.path.exists(tu_chon):
        return tu_chon
    for mau in _MAU_TRONG_GOC:
        for duong in sorted(glob.glob(os.path.join(goc, mau)), reverse=True):
            if os.path.exists(duong):
                return duong
    truc_tiep = os.path.join(goc, "chromium")
    if _chay_duoc(truc_tiep):
        return truc_tiep
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            duong = pw.chromium.executable_path
        return duong if duong and os.path.exists(duong) else None
    except Exception:
        return None


CHROMIUM = _tim()
