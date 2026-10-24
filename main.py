"""
main.py
=======
Điểm khởi động ứng dụng kiosk. Tạo cửa sổ pywebview, gắn PipelineAPI
làm js_api để index.html và js/*.js gọi qua window.pywebview.api.*

Cách chạy:
    python3 main.py                    # mở một workspace trong workspaces/ cạnh main.py
    python3 main.py /duong/dan/khac.db # chỉ định DB khác (một DB, không workspace)
"""

import os
import sys
import traceback

import browser_host
import cau_hinh_ws
import chan_doan
import nhan_ws
import workspace
from api import PipelineAPI
from rbda_priority_pipeline import init_db
from recovery import RecoveryAPI

APP_TITLE = "Sắp xếp Câu lạc bộ — RB-DA"

# QUAN TRỌNG khi đóng gói bằng PyInstaller: __file__ của main.py KHÔNG
# trỏ tới thư mục chứa file .exe thật — nó trỏ vào thư mục tài nguyên
# tạm (_internal/ ở chế độ onedir, hoặc thư mục giải nén tạm ở chế độ
# onefile). Nếu dùng __file__ để tính đường dẫn app.db, DB sẽ bị ghi
# nhầm vào bên trong _internal/ (đã tự phát hiện bug này bằng cách
# build thật và chạy thử).
#
#   BASE_DIR      -> nơi ĐẶT app.db (phải là thư mục chứa .exe thật,
#                     để dữ liệu không bị mất khi build lại/cập nhật app)
#   RESOURCE_DIR  -> nơi ĐỌC tài nguyên đã đóng gói (index.html,
#                     style.css, js/*.js, assets/fonts/) — ở chế độ đóng
#                     gói, đây là _internal/ (hoặc thư mục tạm), khác
#                     với BASE_DIR; ở chế độ chạy thường (python3
#                     main.py), cả hai trùng nhau.
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
    RESOURCE_DIR = getattr(sys, "_MEIPASS", BASE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RESOURCE_DIR = BASE_DIR


def resolve_db_path() -> str:
    if len(sys.argv) > 1:
        return os.path.abspath(sys.argv[1])
    return os.path.join(BASE_DIR, "app.db")


class WorkspaceKhoiDongHong(Exception):
    """Không workspace nào mở được lúc khởi động. `db_path` là tệp hỏng cần đưa ra màn phục hồi."""

    def __init__(self, db_path: str, loi: Exception):
        super().__init__(str(loi))
        self.db_path = db_path


def khoi_dong_workspace() -> tuple:
    """(db_path, thu_muc_goc_ws, da_chon) — app.db sẽ mở lúc khởi động.

    Có đường dẫn trong argv: y như trước — MỘT CSDL, không workspace
    (`thu_muc_goc_ws` None).

    Không có: dùng workspace trong `BASE_DIR/workspaces/`. `app.db` cũ cạnh
    chương trình (bản trước khi có workspace) được dời vào workspace "Trường
    học" trước. Chưa có workspace nào thì dựng "Trường học" mặc định. Có đúng
    một thì mở luôn (trường chỉ dùng một workspace không phải chọn gì). Có
    nhiều thì `da_chon` False: giao diện hiện màn chọn, còn CSDL trả về là
    cái sửa gần nhất MỞ ĐƯỢC — chỉ để đối tượng API có chỗ đứng cho tới khi chọn.
    Workspace hỏng không được chiếm chỗ đó: nó làm cả chương trình rơi vào màn phục hồi
    trong khi các workspace lành vẫn dùng được. Chỉ khi KHÔNG cái nào mở được mới ném
    `WorkspaceKhoiDongHong` (mang đường dẫn tệp hỏng gần nhất, cho màn phục hồi).
    """
    if len(sys.argv) > 1:
        return resolve_db_path(), None, True
    workspace.di_chuyen_db_cu(BASE_DIR)
    ds = workspace.danh_sach(BASE_DIR)
    if not ds:
        slug = workspace.tao(BASE_DIR, workspace.TEN_TRUONG_HOC, None)
        return workspace.duong_dan_db(BASE_DIR, slug), BASE_DIR, True
    loi_dau = None
    for w in sorted(ds, key=lambda w: w["modified"], reverse=True):
        try:
            init_db(w["path"])           # đúng điều PipelineAPI(db_path) đòi
        except Exception as e:
            loi_dau = loi_dau or (w["path"], e)
            continue
        return w["path"], BASE_DIR, len(ds) == 1
    raise WorkspaceKhoiDongHong(*loi_dau)


def _db_phuc_hoi_du_phong(db_cu: str) -> str:
    """Tệp cho màn phục hồi khi lỗi khởi động KHÔNG nêu rõ tệp nào hỏng.

    `app.db` cạnh chương trình chỉ còn khi chưa di trú; sau di trú nó không còn, và bắt đầu lại
    trên đường dẫn đó đẻ ra một app.db mồ côi không ai đọc. Lúc đó dùng workspace sửa gần nhất."""
    if os.path.exists(db_cu):
        return db_cu
    try:
        ds = workspace.danh_sach(BASE_DIR)
    except Exception:
        return db_cu
    return max(ds, key=lambda w: w["modified"])["path"] if ds else db_cu


def tieu_de_cua_so(db_path: str, goc_ws) -> str:
    """Tiêu đề cửa sổ lúc mở: "<tên danh từ chỗ xếp> — <tên workspace>".

    Chạy với đường dẫn CSDL riêng (không workspace) thì giữ APP_TITLE như trước.
    Giao diện đổi lại theo ngôn ngữ đang chọn và khi đổi workspace
    (`PipelineAPI.dat_tieu_de_cua_so`); ở đây chưa biết ngôn ngữ nên dùng tiếng Việt.
    """
    if not goc_ws:
        return APP_TITLE
    try:
        cfg = cau_hinh_ws.doc_cau_hinh(db_path)
        return "%s — %s" % (nhan_ws.nhan_ngon_ngu(cfg["labels"], "slot", "vi"),
                            cfg["name"] or os.path.basename(os.path.dirname(db_path)))
    except Exception:
        return APP_TITLE


def _show_ui(title: str, page: str, js_api, width: int, height: int,
             min_size: tuple) -> None:
    """
    Hiện giao diện `page` với backend `js_api`, THỬ HAI CÁCH theo thứ tự:

      1. Cửa sổ pywebview (ưu tiên — cửa sổ gốc của hệ điều hành).
      2. NẾU pywebview hỏng: máy chủ cục bộ + một CỬA SỔ RIÊNG của trình
         duyệt nhân Chromium (Edge/Chrome), mở bằng cờ `--app=` nên KHÔNG
         có thanh địa chỉ, KHÔNG có tab — nhìn và dùng như ứng dụng
         desktop. Chỉ khi máy không có trình duyệt Chromium nào thì mới
         đành mở tab thường (xem browser_host.py).

    VÌ SAO CẦN CÁCH 2: trên Windows, pywebview bắt buộc đi qua
    pythonnet -> .NET Framework, và mắt xích này đã hỏng thật trên máy
    người dùng sau khi đóng gói bằng PyInstaller:

        RuntimeError: Failed to resolve Python.Runtime.Loader.Initialize
        from ...\\_internal\\pythonnet\\runtime\\Python.Runtime.dll

    Trước đây lỗi đó làm cả tiến trình chết kèm hộp thoại khó hiểu, app
    hoàn toàn không dùng được. Giờ nó chỉ khiến app đổi cách vẽ cửa sổ —
    TOÀN BỘ tính năng giữ nguyên, vì js/*.js/recovery.js vẫn gọi backend
    qua đúng `window.pywebview.api.*` như cũ (browser_host dựng sẵn cầu
    nối giả lập). Với cờ `--app=`, người dùng vẫn thấy MỘT CỬA SỔ ỨNG
    DỤNG RIÊNG, không phải một tab lẫn trong trình duyệt.
    """
    # Gỡ dấu "tải từ Internet" TRƯỚC khi nạp webview. Windows gắn dấu đó
    # vào mọi tệp giải nén từ .zip tải về, và .NET Framework từ chối nạp
    # assembly mang dấu — khớp đúng triệu chứng: lỗi nêu rõ đường dẫn tới
    # Python.Runtime.dll, tức tệp CÓ đó, .NET tìm thấy nhưng không nạp.
    if getattr(sys, "frozen", False):
        ket = chan_doan.go_dau_tai_ve(RESOURCE_DIR)
        chan_doan.ghi(BASE_DIR, "go dau tai-ve trong %s: %r" % (RESOURCE_DIR, ket))

    try:
        import webview

        window = webview.create_window(
            title, os.path.join(RESOURCE_DIR, page), js_api=js_api,
            width=width, height=height, min_size=min_size,
        )
        if hasattr(js_api, "_set_window"):
            # Cho phép các tính năng dùng hộp thoại gốc của hệ điều hành
            # sau này (hiện chưa tính năng nào bắt buộc phải có window ref).
            #
            # TEN PHAI CO DAU GACH DUOI. Doc chu thich trong
            # PipelineAPI._set_window — de ten cong khai thi pywebview de quy
            # vao chinh cua so cua no va TREO HAN app.
            js_api._set_window(window)
        # KHONG duoc ghi "THANH CONG" o day. webview.start() ben duoi moi la
        # cho that su mo cua so, va no da tung TREO ngay tai do — luc ay nhat
        # ky van ghi "THANH CONG", tuc noi doi dung luc can su that nhat.
        chan_doan.ghi(BASE_DIR, "dang mo cua so goc (pywebview)...")
        webview.start()
        chan_doan.ghi(BASE_DIR, "cua so goc (pywebview) da dong binh thuong")
        return
    except (KeyboardInterrupt, SystemExit):
        # Nguoi dung CHU DONG dung (Ctrl+C, dong tien trinh) — khong phai
        # pywebview hong. Truoc day nhanh duoi nuot ca hai va mo luon che do
        # trinh duyet: bam Ctrl+C de tat thi app lai bat len cua so khac.
        raise
    except BaseException:
        # Nuot MOI loai loi con lai (ke ca khong phai Exception) roi thu
        # cach 2 — con mot duong chay duoc van hon la chet kem stack trace.
        #
        # NHUNG PHAI GHI LAI VET LOI VAO TEP. Truoc day cho ra sys.stderr,
        # ma ban build console=False khong co stderr nao — vet loi bi vut
        # di dung luc no xay ra, va ba phien lam viec phai DOAN nguyen
        # nhan. Ghi ra tep canh app.db thi lan sau doc duoc nguyen van.
        chan_doan.ghi_ngoai_le(
            BASE_DIR, "cua so goc (pywebview) HONG, chuyen sang trinh duyet:")
        # Ban dong goi console=False: PyInstaller dat sys.stderr = None. Goi
        # .write() tren None se nem AttributeError NGAY TRONG khoi except nay
        # va chan luon duong du phong ben duoi — dung luc can no nhat.
        if sys.stderr is not None:
            sys.stderr.write(
                "pywebview khong khoi dong duoc, chuyen sang che do trinh duyet:\n"
                + traceback.format_exc()
            )

    chan_doan.ghi(BASE_DIR, "dang chay bang CHE DO TRINH DUYET (du phong)")
    browser_host.serve(js_api, RESOURCE_DIR, page, width=width, height=height)


def main() -> None:
    # Đường dẫn cũ làm chỗ dựa cho màn phục hồi nếu chính việc chọn workspace
    # hỏng (khoi_dong_workspace nằm trong try ngay dưới).
    db_path = resolve_db_path()

    # KHÔNG BAO GIỜ được chết ngầm: nếu app.db hỏng/mất, PipelineAPI(...)
    # (gọi init_db bên trong) ném exception NGAY TẠI ĐÂY — TRƯỚC khi có
    # bất kỳ cửa sổ nào được tạo. Không bọc try/except thì tiến trình
    # thoát với exit code 1 và KHÔNG cửa sổ nào hiện ra — đặc biệt
    # nghiêm trọng trên bản build Windows console=False (kiosk), nơi
    # không có terminal nào để người vận hành thấy lỗi (xem
    # kế hoạch kiểm thử mất dữ liệu — artifact, xem BAN_GIAO.md mục 8, nhóm B). Thay vào đó: mở màn hình PHỤC HỒI
    # (recovery.html/recovery.py) cho phép khôi phục từ bản sao lưu tự
    # động (xem PipelineAPI._backup_db trong api.py) hoặc bắt đầu lại
    # với DB trống.
    try:
        db_path, goc_ws, da_chon = khoi_dong_workspace()
        api = PipelineAPI(db_path, thu_muc_goc_ws=goc_ws, ws_da_chon=da_chon)
    except Exception as e:
        # Lỗi nêu rõ tệp hỏng thì phục hồi đúng tệp đó; không thì tệp dự phòng (xem hàm).
        db_phuc_hoi = getattr(e, "db_path", None) or (
            _db_phuc_hoi_du_phong(db_path) if len(sys.argv) <= 1 else db_path)
        _show_ui(
            APP_TITLE + " — Phục hồi dữ liệu",
            "recovery.html",
            RecoveryAPI(db_phuc_hoi, f"{e}\n\n{traceback.format_exc()}"),
            width=900, height=700, min_size=(700, 560),
        )
        return

    _show_ui(
        tieu_de_cua_so(db_path, goc_ws), "index.html", api,
        width=1280, height=800, min_size=(1024, 640),
    )


if __name__ == "__main__":
    main()
