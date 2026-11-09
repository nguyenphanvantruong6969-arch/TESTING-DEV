/* js/04_nhap_tai_cho.js — Thẻ 04 — Nhập tại chỗ (kiosk): chọn học sinh, tick thi, xếp nguyện vọng.

   Một phần của giao diện chính, tách từ app.js cũ. Các tệp js/ là SCRIPT
   THƯỜNG (không phải ES module) nạp theo đúng thứ tự trong index.html và
   dùng chung một phạm vi — như một tệp duy nhất trước đây. Không dùng ES
   module vì mở trang bằng file:// thì trình duyệt chặn chúng.
*/
"use strict";

/* ------------------------------------------------------------------ *
 * 5. TAB 3 — NHẬP TẠI CHỖ (KIOSK FALLBACK)
 * ------------------------------------------------------------------ */

let currentFallbackStudent = null;
let currentClubs = [];
/* Bảng tra club_id -> buổi, nạp cùng danh sách CLB ở màn nhập tại chỗ.
   Giữ riêng thay vì hỏi lại backend mỗi lần bấm, vì chỉ báo phủ buổi
   phải cập nhật ngay theo từng cú bấm xếp hạng. */
let buoiCuaClb = {};
let currentRanking = [];
let fallbackStudentPage = 1;
const FALLBACK_PAGE_SIZE = 8;

/* ---- Thay doi CHUA LUU o the 03 ----
   Bam o tick / xep nguyen vong chi doi MAN HINH; phai bam Luu moi vao
   CSDL. Truoc day bam sang em khac la thay doi bi bo di IM LANG — cach
   de mat du lieu nhat o kiosk. Nay: danh dau "Chua luu" canh nut Luu, va
   roi di (em khac / tao em moi / doi the) phai bam HAI lan. */
let whartonState = null;   // state cua em dang mo (co khoa `wharton`); null = workspace chua bat Wharton
let daLuuWharton = "";     // dang chuoi cua diem Wharton DA LUU, theo tung o nhap (xem whartonChuoi)
let daLuuThi = [];   // o tick thi da luu, da sap
let daLuuNv = [];    // thu tu nguyen vong da luu
let daLuuLop = "";   // lop cua em DA LUU ("" = chua co); o chon lop khac gia tri nay la "chua luu" (A14)
let choRoiDi = null; // hen gio cua lan bam roi di thu nhat
let khoaRoiDi = null; // lan bam thu nhat la DI DAU (xac nhan phai cung cho)

/* ---- A14: LỚP của học sinh ----
   Chỉ để hiển thị / lọc / sắp / xuất cho giáo viên chủ nhiệm; thuật toán không đọc lớp.
   `list_classes` trả {classes:[{class_id,n}], n_khong_lop}. Ba nơi dùng chung: bộ lọc ở thẻ Quản lý
   và thẻ Kết quả, và ô chọn CỐ ĐỊNH ở kiosk. */
const LOP_TAT_CA = "__tat_ca__";     // giá trị ô lọc "tất cả"; "" = chưa có lớp
let dsLopHienCo = [];                // [class_id] lần nạp gần nhất

function layDsLop() {
  return callApi("list_classes").then((res) => {
    const d = res.ok ? res.data : { classes: [], n_khong_lop: 0 };
    dsLopHienCo = d.classes.map((c) => c.class_id);
    return d;
  });
}

function themOption(sel, value, text) {
  const o = document.createElement("option");
  o.value = value;
  o.textContent = text;
  sel.appendChild(o);
}

/* Ô LỌC: Tất cả / từng lớp / Chưa có lớp. Giữ giá trị đang chọn nếu lớp đó còn. */
function napOLocLop(sel, d) {
  if (!sel) return;
  const cu = sel.options.length ? sel.value : LOP_TAT_CA;   // "" là lựa chọn thật (Chưa có lớp)
  clear(sel);
  themOption(sel, LOP_TAT_CA, t("lop_tat_ca"));
  d.classes.forEach((c) => themOption(sel, c.class_id, c.class_id + " (" + c.n + ")"));
  if (d.n_khong_lop) themOption(sel, "", t("lop_chua_co") + " (" + d.n_khong_lop + ")");
  sel.value = Array.from(sel.options).some((o) => o.value === cu) ? cu : LOP_TAT_CA;
}

/* Tham số `class_id` gửi lên: null = không lọc; "" = chưa có lớp; còn lại là tên lớp. */
function lopLocThamSo(sel) {
  return !sel || !sel.options.length || sel.value === LOP_TAT_CA ? null : sel.value;
}

/* Ô CHỌN ở kiosk: danh sách CỐ ĐỊNH từ list_classes (không gõ tự do). Không có lớp nào thì ẩn. */
function napOChonLopKiosk(sel, lopHienTai) {
  clear(sel);
  themOption(sel, "", t("kiosk_lop_chon"));
  dsLopHienCo.forEach((c) => themOption(sel, c, c));
  sel.value = dsLopHienCo.indexOf(lopHienTai) !== -1 ? lopHienTai : "";
}

/* Ô chọn lớp của form "Tạo học sinh mới": ẩn khi chưa có lớp nào. */
function napOChonLopTaoMoi() {
  const sel = el("newStudentLop");
  const giu = sel.value;
  sel.hidden = dsLopHienCo.length === 0;
  napOChonLopKiosk(sel, giu);
}

function veOLopKiosk(lopHienTai) {
  const coLop = dsLopHienCo.length > 0;
  el("kioskLopHang").hidden = !coLop;
  el("kioskLopNhac").hidden = true;
  if (coLop) napOChonLopKiosk(el("kioskLop"), lopHienTai || "");
  /* T3-33: da co lop thi phieu chi HIEN lop (bam "Doi" moi sua); chua co lop thi hien o chon (bat buoc). */
  const daCo = coLop && !!el("kioskLop").value;
  el("kioskLop").hidden = daCo;
  el("kioskLopChu").hidden = !daCo;
  el("kioskLopChu").textContent = daCo ? el("kioskLop").value : "";
  el("btnKioskLopSua").hidden = !daCo;
}

/* Lớp gửi kèm khi Lưu: null = ô ẩn (không có lớp nào) nên không đụng; undefined = BẮT BUỘC mà chưa chọn. */
function lopKioskDeGui() {
  if (el("kioskLopHang").hidden) return null;
  const v = el("kioskLop").value;
  if (!v) {
    el("kioskLopNhac").hidden = false;
    el("kioskLop").focus();
    return undefined;
  }
  el("kioskLopNhac").hidden = true;
  return v;
}

function thiDangTick() {
  return Array.from(document.querySelectorAll("#testSelectionGrid .option-row.is-checked"))
    .map((r) => r.dataset.clubId).sort();
}

function thiChuaLuu() {
  return !!currentFallbackStudent && thiDangTick().join("|") !== daLuuThi.join("|");
}

function nvChuaLuu() {
  return !!currentFallbackStudent && currentRanking.join("|") !== daLuuNv.join("|");
}

/* A14: o lop dang hien (khong bi an) khac lop da luu. */
function lopChuaLuu() {
  return !!currentFallbackStudent && !el("kioskLopHang").hidden && el("kioskLop").value !== daLuuLop;
}

function whartonChuaLuu() {
  return !!currentFallbackStudent && !!whartonState && whartonChuoi() !== daLuuWharton;
}

function veDauChuaLuu() {
  el("chuaLuuThi").hidden = !thiChuaLuu();
  el("chuaLuuNv").hidden = !nvChuaLuu();
  el("chuaLuuWharton").hidden = !whartonChuaLuu();
  el("kioskLopChuaLuu").hidden = !lopChuaLuu();
}

/* Chay `hanhDong` neu khong con gi chua luu; neu con, lan bam dau chi
   canh bao, lan bam thu hai — vao CUNG cho (`khoa`), trong 4 giay — moi
   bo thay doi va di tiep. Cung cho la bat buoc: bam em khac roi bam sang
   the khac khong phai la "xac nhan bo thay doi" cho viec doi the. */
function roiDiNeuDuoc(hanhDong, khoa) {
  if (!thiChuaLuu() && !nvChuaLuu() && !whartonChuaLuu() && !lopChuaLuu()) {
    hanhDong();
    return;
  }
  if (choRoiDi && khoaRoiDi === khoa) {
    clearTimeout(choRoiDi);
    choRoiDi = null;
    khoaRoiDi = null;
    hanhDong();
    return;
  }
  clearTimeout(choRoiDi);
  showToast(t("fallback_chua_luu_canh_bao", { student_id: currentFallbackStudent }), "error");
  khoaRoiDi = khoa;
  choRoiDi = setTimeout(() => { choRoiDi = null; khoaRoiDi = null; }, 4000);
}

function loadFallbackTab() {
  layDsLop().then(() => napOChonLopTaoMoi());
  fallbackStudentPage = 1;
  loadFallbackStudentList();
  /* Em dang mo co the da bi xoa o noi khac (vung nguy hiem, xoa hoc
     sinh...). Hoi lai; khong con thi dong vung lam viec, dung de lai
     mot em khong ton tai tren man hinh. */
  if (currentFallbackStudent) {
    callApi("get_student_entry_state", currentFallbackStudent).then((res) => {
      if (!res.ok) boChonHocSinhDuPhong();
    });
  }
}

function boChonHocSinhDuPhong() {
  currentFallbackStudent = null;
  hcNhacSid = null;
  currentRanking = [];
  daLuuThi = [];
  daLuuNv = [];
  daLuuLop = "";
  if (choRoiDi) { clearTimeout(choRoiDi); choRoiDi = null; khoaRoiDi = null; }
  renderWhartonStep(null);
  el("fallbackWorkArea").hidden = true;
  danhDauTheDangChon();
}

function initFallbackHandlers() {
  /* Bước 3 (Wharton) là chữ do JS ghi nên applyStaticText() không dịch được; đổi ngôn ngữ thì vẽ
     lại từ trạng thái đang có, giữ điểm đã gõ (không nạp lại CSDL, để không mất thao tác chưa lưu).
     Nghe ở ĐÂY chứ không sửa reapplyDynamicTextForLangChange: tệp đó ngoài phạm vi của mục A13. */
  window.addEventListener("langchange", () => {
    if (currentFallbackStudent && whartonState) {
      renderWhartonStep(whartonState, whartonGiuTam());
      veDauChuaLuu();
    }
  });
  el("btnStudentSearch").addEventListener("click", () => {
    fallbackStudentPage = 1;
    loadFallbackStudentList();
  });
  el("studentSearchInput").addEventListener(
    "input",
    debounce(() => {
      fallbackStudentPage = 1;
      loadFallbackStudentList();
    }, 250)
  );
  el("btnFallbackPrevPage").addEventListener("click", () => {
    if (fallbackStudentPage > 1) {
      fallbackStudentPage -= 1;
      loadFallbackStudentList();
    }
  });
  el("btnFallbackNextPage").addEventListener("click", () => {
    fallbackStudentPage += 1;
    loadFallbackStudentList();
  });
  el("btnKioskLopSua").addEventListener("click", () => {
    el("kioskLop").hidden = false;
    el("kioskLopChu").hidden = true;
    el("btnKioskLopSua").hidden = true;
    el("kioskLop").focus();
  });
  el("kioskLop").addEventListener("change", () => {
    if (el("kioskLop").value) el("kioskLopNhac").hidden = true;
    veDauChuaLuu();
  });
  el("btnCreateStudent").addEventListener("click", () => {
    const id = el("newStudentId").value.trim();
    const name = el("newStudentName").value.trim();
    if (!id || !name) {
      showToast(t("toast_need_id_and_name"), "error");
      return;
    }
    /* A14: có lớp trong danh sách thì em mới cũng phải chọn lớp. */
    const lopMoi = el("newStudentLop").hidden ? null : el("newStudentLop").value;
    if (lopMoi === "") {
      showToast(t("kiosk_lop_nhac"), "error");
      el("newStudentLop").focus();
      return;
    }
    roiDiNeuDuoc(() => khiBan(el("btnCreateStudent"), () => callApi("create_student_if_missing", id, name, lopMoi)).then((res) => {
      if (!res.ok) {
        showErrorToast(res.errors);
        return;
      }
      showToast(res.data.created ? t("toast_student_created") : t("toast_student_exists"), "success");
      el("newStudentId").value = "";
      el("newStudentName").value = "";
      el("newStudentLop").value = "";
      layDsLop().then(() => napOChonLopTaoMoi());
      loadFallbackStudentList();
      selectFallbackStudent(id);
    }), "tao:" + id);
  });

  el("btnSubmitTestSelection").addEventListener("click", () => {
    if (!currentFallbackStudent) return;
    /* Chụp em và danh sách LÚC BẤM: phản hồi về muộn thì người dùng có thể đã sang em khác, và mốc
       "đã lưu" / dòng thông báo của em kia không được ghi đè lên em đang mở (A13.12, 1.7). */
    const sid = currentFallbackStudent;
    const checked = Array.from(document.querySelectorAll("#testSelectionGrid .option-row.is-checked")).map(
      (row) => row.dataset.clubId
    );
    const lop = lopKioskDeGui();
    if (lop === undefined) { feedback(el("testSelectionFeedback"), t("kiosk_lop_nhac"), true); return; }
    khiBan(el("btnSubmitTestSelection"), () => callApi("submit_test_selection", sid, checked, lop)).then((res) => {
      const conMo = sid === currentFallbackStudent;
      if (res.ok) {
        /* Bo tick CLB da cham diem la xoa diem do (api
           _xoa_diem_khong_con_tick) — phai NOI RA, xoa diem giao vien
           da cham ma im lang la mat du lieu khong ai hay. */
        if (conMo) {
          daLuuThi = checked.slice().sort();
          if (lop !== null) daLuuLop = lop;
          veDauChuaLuu();
          lamMoiBuoc3(true);          /* doi o tick la doi quy cua tung CLB o Buoc 3 */
          const m = res.data.n_scores_removed || 0;
          feedback(
            el("testSelectionFeedback"),
            m
              ? t("feedback_test_selection_saved_removed", { n: res.data.n_selected, m })
              : t("feedback_test_selection_saved", { n: res.data.n_selected }),
            false
          );
        }
        loadFallbackStudentList(); // cap nhat the "n CLB thi" trong danh sach
      } else if (conMo) {
        feedbackErrors(el("testSelectionFeedback"), res.errors);
      }
    });
  });

  el("btnSubmitWharton").addEventListener("click", () => {
    if (!currentFallbackStudent || !whartonState) return;
    const sid = currentFallbackStudent;
    const { w1, w2 } = whartonThuThap();
    khiBan(el("btnSubmitWharton"), () => callApi("submit_wharton", sid, w1, w2)).then((res) => {
      if (sid !== currentFallbackStudent) return;   /* da sang em khac: khong de dong chu cua em nay len em kia */
      if (res.ok) {
        feedback(el("whartonFeedback"), t("feedback_wharton_saved"), false);
        lamMoiBuoc3(false);         /* ve lai tu trang thai DA LUU */
      } else {
        /* Server moi la noi quyet dinh (V6): chi nhac loi, khong sua gia tri o day. */
        feedbackErrors(el("whartonFeedback"), res.errors);
      }
    });
  });

  el("btnSubmitHuyChuong").addEventListener("click", () => {
    if (!currentFallbackStudent || !huyChuongState) return;
    const sid = currentFallbackStudent;
    khiBan(el("btnSubmitHuyChuong"), () => callApi("submit_huy_chuong", sid, hcThuThap())).then((res) => {
      if (sid !== currentFallbackStudent) return;
      if (res.ok) {
        feedback(el("huyChuongFeedback"), t("feedback_huy_chuong_saved"), false);
        lamMoiBuoc3(false);
      } else {
        /* Server moi la noi quyet dinh: chi bao loi, khong sua lua chon o day. */
        feedbackErrors(el("huyChuongFeedback"), res.errors);
      }
    });
  });

  el("btnClearRanking").addEventListener("click", () => {
    currentRanking = [];
    renderRankingList();
  });

  el("btnSubmitPreferences").addEventListener("click", () => {
    if (!currentFallbackStudent) return;
    if (!currentRanking.length) {
      feedback(el("preferencesFeedback"), trErr({ code: "must_rank_at_least_one", params: {} }), true);
      return;
    }
    /* Mốc "đã lưu" là bản chụp LÚC BẤM, không phải xếp hạng lúc phản hồi về: bấm thêm CLB trong
       lúc chờ thì CLB đó vẫn là "chưa lưu" (A13.12, soát nhập 2.3). */
    const sid = currentFallbackStudent;
    const chup = currentRanking.slice();
    const nvTruoc = daLuuNv.slice();                       /* FA-N2: thu tu da luu TRUOC lan luu nay */
    const hcTruoc = huyChuongState ? huyChuongState.huy_chuong : null;
    const lop = lopKioskDeGui();
    if (lop === undefined) { feedback(el("preferencesFeedback"), t("kiosk_lop_nhac"), true); return; }
    khiBan(el("btnSubmitPreferences"), () => callApi("submit_preferences", sid, chup, lop)).then((res) => {
      const conMo = sid === currentFallbackStudent;
      if (res.ok) {
        if (conMo) {
          daLuuNv = chup;
          if (lop !== null) daLuuLop = lop;
          veDauChuaLuu();
          if (hcTruoc && hcTruoc.bat && !hcTruoc.khoa) {
            hcTheoNguyenVong(sid, nvTruoc, chup, hcTruoc);   /* FA-N2 (V§6.1, D2) */
          } else {
            lamMoiBuoc3(true);        /* bo mot CLB khoi nguyen vong la xoa diem Wharton cua no */
          }
          feedback(el("preferencesFeedback"), t("feedback_preferences_saved", { n: res.data.n_ranked }), false);
        }
        loadFallbackStudentList(); // cap nhat the "n nguyen vong" trong danh sach
      } else if (conMo) {
        feedbackErrors(el("preferencesFeedback"), res.errors);
      }
    });
  });

  /* Xuat ho so em DANG MO — dung cho nguoi dung dang dung. Xuat theo
     du lieu DA LUU: con thay doi chua luu thi nhac luu truoc. */
  el("btnXuatEmNay").addEventListener("click", () => {
    if (!currentFallbackStudent) return;
    if (thiChuaLuu() || nvChuaLuu() || whartonChuaLuu() || lopChuaLuu()) {
      showToast(t("fallback_xuat_chua_luu"), "error");
      return;
    }
    chayXuat([["xuat_muc_hoc_sinh", "export_hoc_sinh_csv", [[currentFallbackStudent], ""],
      (d) => t("xuat_kq_hoc_sinh", { n: d.n_hoc_sinh, n_dong: d.n_dong, path: d.path })]],
      el("fallbackXuatFeedback"));
  });

  armTwoStepConfirm(el("btnResetStudentEntry"), () => t("confirm_reset_entry"), () => {
    if (!currentFallbackStudent) return;
    callApi("reset_student_entry", currentFallbackStudent).then((res) => {
      if (res.ok) {
        const m = res.data.n_scores_removed || 0;
        showToast(m ? t("toast_reset_done_removed", { m }) : t("toast_reset_done"), "success");
        selectFallbackStudent(currentFallbackStudent);
        loadFallbackStudentList();
      } else {
        showErrorToast(res.errors);
      }
    });
  });

  armTwoStepConfirm(el("btnDeleteStudent"), () => t("confirm_delete_student"), () => {
    if (!currentFallbackStudent) return;
    const studentId = currentFallbackStudent;
    callApi("delete_student", studentId).then((res) => {
      if (res.ok) {
        showToast(t("toast_student_deleted", { student_id: studentId }), "success");
        hsDaChon.delete(studentId);
        boChonHocSinhDuPhong();     /* MỘT đường dọn: xếp hạng, Bước 3, mốc "đã lưu", hẹn giờ (A13.12, 1.9) */
        el("studentSearchInput").value = "";
        loadFallbackStudentList();
      } else {
        showErrorToast(res.errors);
      }
    });
  });
}

/* Moi lan go phim la mot lan goi; tra ve lech thu tu thi ket qua CU de
   len ket qua MOI. Chi ve lan goi moi nhat. */
let fallbackListReq = 0;

function loadFallbackStudentList() {
  const q = el("studentSearchInput").value.trim();
  const req = ++fallbackListReq;
  Promise.all([
    callApi("list_students_admin", q, fallbackStudentPage, FALLBACK_PAGE_SIZE),
    callApi("get_danh_sach_buoi"),
  ]).then(([res, buoiRes]) => {
    if (req !== fallbackListReq) return;
    const box = el("studentSearchResults");
    const pagination = el("fallbackStudentPagination");
    clear(box);
    if (!res.ok || !res.data.rows.length) {
      box.innerHTML = '<div class="empty-state"></div>';
      box.firstChild.textContent = t("search_no_students_found");
      pagination.hidden = true;
      return;
    }
    fallbackStudentPage = res.data.page;   /* máy chủ kẹp trang vượt tổng về trang cuối (A13.12, 1.6) */
    const nhieuBuoi = !!(buoiRes.ok && buoiRes.data.nhieu_buoi);
    const thuTuBuoi = nhieuBuoi ? buoiRes.data.ds_buoi : [];
    res.data.rows.forEach((s) => box.appendChild(veTheHocSinh(s, nhieuBuoi, thuTuBuoi)));
    pagination.hidden = false;
    el("fallbackPaginationLabel").textContent = t("pagination_label", {
      page: res.data.page, total_pages: res.data.total_pages, total: res.data.total,
    });
    el("btnFallbackPrevPage").disabled = res.data.page <= 1;
    el("btnFallbackNextPage").disabled = res.data.page >= res.data.total_pages;
  });
}

/* The ket qua tim kiem: ten + ma, trang thai nhap lieu, roi HAI dong co
   nhan noi ro em da chon NHUNG CLB nao — de nguoi van hanh khong phai
   bam vao tung em moi biet. */
function trangThaiNhap(s) {
  const coThi = (s.tested_clubs || []).length > 0;
  const coNv = (s.ranked_clubs || []).length > 0;
  if (coThi && coNv) return { lop: "is-du", khoa: "hs_trang_thai_du" };
  if (!coThi && !coNv) return { lop: "is-trong", khoa: "hs_trang_thai_trong" };
  return { lop: "is-thieu", khoa: coThi ? "hs_trang_thai_thieu_nv" : "hs_trang_thai_thieu_thi" };
}

function veChipCLB(ds, coHang) {
  return ds.map((c) =>
    `<span class="hs-chip">` +
    (coHang ? `<span class="hs-chip-hang">${esc(c.rank)}</span>` : "") +
    `${esc(c.name || c.club_id)}</span>`
  ).join("");
}

function veDongCLB(khoaNhan, ds, coHang, nhieuBuoi, thuTuBuoi) {
  let noiDung;
  if (!ds.length) {
    noiDung = `<span class="hs-chua-chon">${esc(t("hs_the_chua_chon"))}</span>`;
  } else if (!nhieuBuoi) {
    noiDung = veChipCLB(ds, coHang);
  } else {
    /* Nhom theo buoi, dung thu tu buoi cua truong; buoi la (CLB da bi
       xoa, buoi khong con) xep cuoi. */
    const nhom = {};
    ds.forEach((c) => { (nhom[c.buoi] = nhom[c.buoi] || []).push(c); });
    const cacBuoi = thuTuBuoi.filter((b) => nhom[b])
      .concat(Object.keys(nhom).filter((b) => thuTuBuoi.indexOf(b) === -1));
    /* Giu hang CHUNG nhu da luu (1..n ca tuan), khong danh so lai trong
       tung buoi: vung lam viec ben duoi cung dem nhu vay, hai noi phai
       noi cung mot con so. */
    noiDung = cacBuoi.map((b) =>
      `<span class="hs-buoi-nhom"><span class="hs-buoi-nhan">${esc(nhanBuoi(b))}</span>` +
      veChipCLB(nhom[b], coHang) + `</span>`
    ).join("");
  }
  return `<div class="hs-card-dong"><span class="hs-card-nhan">${esc(t(khoaNhan))}</span>` +
         `<span class="hs-card-chips">${noiDung}</span></div>`;
}

function veTheHocSinh(s, nhieuBuoi, thuTuBuoi) {
  const the = document.createElement("div");
  the.className = "hs-card" + (s.student_id === currentFallbackStudent ? " is-selected" : "");
  the.dataset.studentId = s.student_id;
  the.setAttribute("role", "button");
  the.tabIndex = 0;
  const tt = trangThaiNhap(s);
  the.innerHTML =
    `<div class="hs-card-head">` +
      `<span class="hs-card-ten">${esc(s.name)}</span>` +
      `<span class="hs-card-ma">${esc(s.student_id)}</span>` +
      `<span class="hs-trang-thai ${tt.lop}">${esc(t(tt.khoa))}</span>` +
    `</div>` +
    veDongCLB("hs_nhan_clb_thi", s.tested_clubs || [], false, nhieuBuoi, thuTuBuoi) +
    veDongCLB("hs_nhan_nguyen_vong", s.ranked_clubs || [], true, nhieuBuoi, thuTuBuoi);
  /* Doi hoc sinh khi con thay doi chua luu: phai bam hai lan (xem
     roiDiNeuDuoc). */
  const chon = () => {
    if (s.student_id === currentFallbackStudent) return;
    roiDiNeuDuoc(() => selectFallbackStudent(s.student_id), "hs:" + s.student_id);
  };
  the.addEventListener("click", chon);
  the.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter" || ev.key === " ") {
      ev.preventDefault();
      chon();
    }
  });
  return the;
}

function danhDauTheDangChon() {
  document.querySelectorAll("#studentSearchResults .hs-card").forEach((c) => {
    c.classList.toggle("is-selected", c.dataset.studentId === currentFallbackStudent);
  });
}

function selectFallbackStudent(studentId) {
  const luotChon = (luotGoiMoiNhat.chon_hs = (luotGoiMoiNhat.chon_hs || 0) + 1);
  buoiTaiCho = null;
  Promise.all([callApi("get_student_entry_state", studentId), callApi("list_clubs"), layDsLop()]).then(([stateRes, clubsRes]) => {
    /* Bam nhanh hai em: chi lan bam CUOI duoc ve, xem callApiMoiNhat. */
    if (luotChon !== luotGoiMoiNhat.chon_hs) return;
    if (!stateRes.ok) {
      showErrorToast(stateRes.errors);
      return;
    }
    currentFallbackStudent = studentId;
    currentClubs = clubsRes.ok ? clubsRes.data : [];
    buoiCuaClb = {};
    currentClubs.forEach((c) => { buoiCuaClb[c.club_id] = c.buoi; });
    currentRanking = stateRes.data.ranked_clubs.slice();
    daLuuThi = stateRes.data.tested_clubs.slice().sort();
    daLuuNv = stateRes.data.ranked_clubs.slice();
    if (choRoiDi) { clearTimeout(choRoiDi); choRoiDi = null; khoaRoiDi = null; }
    el("fallbackXuatFeedback").textContent = "";
    /* Dòng "Đã lưu n nguyện vọng" của em trước không được còn dưới màn hình em này (A13.12, 2.5). */
    ["testSelectionFeedback", "preferencesFeedback"].forEach((id) => feedback(el(id), "", false));

    el("fallbackWorkArea").hidden = false;
    veOLopKiosk(stateRes.data.class_id);
    daLuuLop = el("kioskLopHang").hidden ? "" : el("kioskLop").value;
    const nhan = el("currentStudentLabel");
    nhan.innerHTML =
      `<span class="hs-dang-chon-ten">${esc(stateRes.data.name)}</span>` +
      `<span class="hs-card-ma">${esc(stateRes.data.student_id)}</span>`;
    danhDauTheDangChon();

    renderTestSelectionGrid(stateRes.data.tested_clubs);
    renderRankingSourceGrid();
    renderRankingList();
    el("whartonFeedback").textContent = "";
    renderWhartonStep(stateRes.data);
    veDauChuaLuu();
    /* T3-32: chon hoac tao xong thi cuon thang toi phieu, khoi tu cuon 900 px. */
    const phieu = el("fallbackWorkArea");
    if (phieu.scrollIntoView) phieu.scrollIntoView({ block: "start", behavior: "auto" });
  });
}

/* ------------------------------------------------------------------ *
 * BUOC 3 — DIEM WHARTON (muc A13). Chi hien khi workspace bat Wharton.
 *
 * Moi buoi hai khung: CLB em DA THI (quy 1, chi pha hoa khi bang diem thi) va CLB KHONG
 * THI (quy 2, tieu chi chinh cua tang 2). Moi CLB mot o so; bo dem "Da dung X / 100".
 * Hoc sinh chi thay diem cua CHINH MINH: khong co diem chuan, do dong hay diem nguoi khac
 * (backend chi tra du lieu cua em dang mo).
 *
 * Gia tri o nhap KHONG bi lam tron hay sua o day: server moi la noi quyet dinh (V6).
 * ------------------------------------------------------------------ */

/* {"quy|club_id": chuoi o nhap} cua mot trang thai — dung de biet con gi CHUA LUU. */
function whartonChuoiTuMap(m) {
  return JSON.stringify(Object.keys(m).sort().map((k) => [k, m[k]]));
}

/* Nhu `whartonChuoiTuMap` nhung doc thang cac o `input.wh-diem` ben trong `goc`. */
function whartonChuoiTu(goc) {
  const m = {};
  goc.querySelectorAll("input.wh-diem").forEach((o) => {
    m[o.dataset.quy + "|" + o.dataset.clb] = o.value.trim();
  });
  return whartonChuoiTuMap(m);
}

function whartonChuoi() {
  return whartonChuoiTu(el("fbWhartonBody"));
}

/* Cac o dang co chu (ke ca o bi khoa): giu lai khi ve lai Buoc 3, de doi ngon ngu hay luu
   Buoc 1/2 khong lam mat diem vua go. */
function whartonGiuTamTu(goc) {
  const m = {};
  goc.querySelectorAll("input.wh-diem").forEach((o) => {
    if (!o.disabled) m[o.dataset.quy + "|" + o.dataset.clb] = o.value;
  });
  return m;
}

function whartonGiuTam() {
  return whartonGiuTamTu(el("fbWhartonBody"));
}

/* {w1, w2} gui len server, doc tu cac o `input.wh-diem` ben trong `goc`. O trong = khong dat diem.
   Khong lam tron: "60.5" di nguyen la 60.5. Dung chung cho kiosk (Buoc 3) va the Quan ly. */
function whartonThuThapTu(goc) {
  const ra = { w1: {}, w2: {} };
  goc.querySelectorAll("input.wh-diem").forEach((o) => {
    /* Ô bị khoá là ô TỰ ĐIỀN 100 (cách A: máy chủ tự điền khi kiểm và khi xếp, không ghi): bỏ qua,
       nếu không "100" đi vào CSDL và về sau thêm CLB cùng quỹ thì CLB mới nhận 0 điểm mà không ai
       nhắc (A13.12, soát nhập 2.2). */
    if (o.disabled) return;
    const v = o.value.trim();
    if (v === "") return;
    ra[o.dataset.quy === "1" ? "w1" : "w2"][o.dataset.clb] = Number(v);
  });
  return ra;
}

function whartonThuThap() {
  return whartonThuThapTu(el("fbWhartonBody"));
}

function whartonCapNhatDem(khung, tong) {
  let x = 0;
  khung.querySelectorAll("input.wh-diem").forEach((o) => {
    const v = o.value.trim();
    if (/^[0-9]+$/.test(v)) x += parseInt(v, 10);
  });
  const dem = khung.querySelector(".wh-dem");
  dem.textContent = t("wharton_da_dung", { x, tong });
  dem.classList.toggle("is-du", x === tong);
  dem.classList.toggle("is-vuot", x > tong);
  /* Thanh tiến độ 0 đến 100 và lỗi NGAY TẠI CHỖ (A13.4): ô không phải số nguyên từ 0 trở lên
     tô đỏ; thừa điểm là lỗi; còn thiếu chỉ là nhắc nhẹ (chưa chia xong thì đâu có sai). Thanh
     đổi màu khi đủ (xanh) hoặc thừa (đỏ). Không đổi hành vi lưu: server vẫn là nơi quyết định. */
  const thanh = khung.querySelector(".wh-thanh");
  if (thanh) {
    thanh.setAttribute("aria-valuenow", String(Math.min(x, tong)));
    thanh.classList.toggle("is-du", x === tong);
    thanh.classList.toggle("is-vuot", x > tong);
    thanh.querySelector(".wh-thanh-day").style.width = Math.min(100, tong ? (x / tong) * 100 : 0) + "%";
  }
  let sai = 0;
  let coGo = false;
  khung.querySelectorAll("input.wh-diem").forEach((o) => {
    const v = o.value.trim();
    const hopLe = v === "" || /^[0-9]+$/.test(v);
    o.classList.toggle("is-sai", !hopLe);
    o.setAttribute("aria-invalid", hopLe ? "false" : "true");
    if (!hopLe) sai += 1;
    else if (v !== "") coGo = true;
  });
  const loi = khung.querySelector(".wh-loi");
  if (loi) {
    let chu = "";
    let nang = true;
    if (sai) chu = t("wharton_loi_so");
    else if (x > tong) chu = t("wharton_loi_vuot", { n: x - tong, tong });
    else if (coGo && x < tong) { chu = t("wharton_loi_thieu", { n: tong - x, tong }); nang = false; }
    loi.textContent = chu;
    loi.hidden = !chu;
    loi.classList.toggle("is-nhe", !nang);
  }
}

let whDemKhung = 0;

/* Ve cac khung Wharton (moi buoi hai khung: da thi / khong thi; moi CLB mot o so; bo dem
   "Da dung X / 100") vao `goc` tu `w` (khoa `wharton` cua get_student_entry_state).

   Dung chung cho kiosk (Buoc 3) va the Quan ly: KHONG dung bien toan cuc cua tab kiosk.
   `tuyChon`:
     ranked  — danh sach club_id theo thu tu nguyen vong cua em;
     ten     — ham club_id -> ten hien thi;
     giu     — {"quy|club_id": chu da go} can giu lai, hoac null;
     chiDoc  — true: moi o chi doc (vd dang khoa);
     khiDoi  — ham goi moi khi mot o doi gia tri (cap nhat dau "Chua luu"), hoac null.
   Tra ve chuoi "DA LUU" (xem whartonChuoiTuMap) de ben goi biet con gi chua luu. */
function whartonVeKhung(goc, w, tuyChon) {
  const { ranked, ten: tenClb, giu, chiDoc, khiDoi } = tuyChon;
  clear(goc);
  const nhieuBuoi = w.ds_buoi.length > 1;
  const daLuu = {};
  w.ds_buoi.forEach((buoi) => {
    if (nhieuBuoi) {
      const tieuDe = document.createElement("div");
      tieuDe.className = "wh-buoi-ten";
      tieuDe.textContent = nhanBuoi(buoi);
      tieuDe.dataset.buoi = buoi;
      goc.appendChild(tieuDe);
    }
    /* Hai khung của một buổi nằm CẠNH NHAU (màn hẹp thì xếp dọc); chỉ có một khung thì rộng cả hàng. */
    const cap = document.createElement("div");
    cap.className = "wh-cap";
    goc.appendChild(cap);
    [1, 2].forEach((quy) => {
      const ds = ranked.filter(
        (c) => w.buoi_cua_clb[c] === buoi && w.quy_cua_clb[c] === quy);
      if (!ds.length) return;                         // khung rong thi khong hien
      const luu = quy === 1 ? w.w1 : w.w2;
      const quyKia = quy === 1 ? w.w2 : w.w1;
      const khung = document.createElement("div");
      khung.className = "wh-khung";
      khung.dataset.quy = String(quy);
      khung.dataset.buoi = buoi;
      const idKhung = "whK" + (++whDemKhung);
      const dau = document.createElement("div");
      dau.className = "wh-khung-dau";
      const ten = document.createElement("span");
      ten.className = "wh-khung-ten";
      ten.textContent = t(quy === 1 ? "wharton_khung_thi" : "wharton_khung_khong_thi");
      /* Câu giải thích dài nằm sau nút (i): bấm mới hiện. */
      const nutI = document.createElement("button");
      nutI.type = "button";
      nutI.className = "nut-i wh-i";
      nutI.textContent = "i";
      nutI.setAttribute("aria-expanded", "false");
      nutI.setAttribute("aria-controls", idKhung + "G");
      nutI.setAttribute("aria-label", t("wharton_giai_thich"));
      const dem = document.createElement("span");
      dem.className = "wh-dem";
      const trai = document.createElement("span");
      trai.className = "wh-khung-trai";
      trai.append(ten, nutI);
      dau.append(trai, dem);
      const thanh = document.createElement("div");
      thanh.className = "wh-thanh";
      thanh.setAttribute("role", "progressbar");
      thanh.setAttribute("aria-valuemin", "0");
      thanh.setAttribute("aria-valuemax", String(w.ngan_sach));
      thanh.setAttribute("aria-valuenow", "0");
      thanh.setAttribute("aria-label", ten.textContent);
      const day = document.createElement("span");
      day.className = "wh-thanh-day";
      thanh.appendChild(day);
      const ghiChu = document.createElement("p");
      ghiChu.className = "wh-ghi-chu";
      ghiChu.id = idKhung + "G";
      ghiChu.hidden = true;
      ghiChu.textContent = t(quy === 1 ? "wharton_khung_thi_ghi_chu" : "wharton_khung_khong_thi_ghi_chu");
      nutI.addEventListener("click", () => {
        ghiChu.hidden = !ghiChu.hidden;
        nutI.setAttribute("aria-expanded", ghiChu.hidden ? "false" : "true");
      });
      khung.append(dau, thanh, ghiChu);
      /* Dong da luu o quy KIA = em doi o tick sau khi chia diem: nhac chia lai, khong tu chuyen. */
      if (ds.some((c) => c in quyKia)) {
        const lech = document.createElement("p");
        lech.className = "wh-lech";
        lech.setAttribute("role", "status");
        lech.textContent = t("wharton_can_chia_lai");
        khung.appendChild(lech);
      }
      /* Mot CLB trong khung thi tu dien 100 va khoa o (neu chua co diem khac 100 da luu). */
      const motClb = ds.length === 1;
      ds.forEach((cid) => {
        const dong = document.createElement("div");
        dong.className = "wh-dong";
        const tenO = document.createElement("span");
        tenO.className = "wh-dong-ten";
        tenO.textContent = tenClb(cid);
        const o = document.createElement("input");
        o.type = "number";
        o.min = "0";
        o.step = "1";
        o.setAttribute("inputmode", "numeric");
        o.className = "text-input text-input-sm wh-diem";
        o.dataset.quy = String(quy);
        o.dataset.clb = cid;
        o.setAttribute("aria-label", tenClb(cid) + ": " + ten.textContent);
        o.setAttribute("aria-describedby", idKhung + "L");
        const daCo = cid in luu ? String(luu[cid]) : "";
        const khoa = !!w.tu_dien_mot_clb && motClb && (daCo === "" || daCo === String(w.ngan_sach));
        /* Ô tự điền (khoá) KHÔNG ghi vào CSDL (cách A): mốc "đã lưu" của nó là chính giá trị tự điền,
           để vừa chọn em đã báo "Chưa lưu" là báo giả (A13.12, soát nhập 1.8 / 2.4). */
        daLuu[quy + "|" + cid] = khoa ? String(w.ngan_sach) : daCo;
        const go = giu && (quy + "|" + cid) in giu ? giu[quy + "|" + cid] : null;
        o.value = khoa ? String(w.ngan_sach) : (go !== null ? go : daCo);
        o.disabled = khoa || !!chiDoc;
        o.addEventListener("input", () => {
          whartonCapNhatDem(khung, w.ngan_sach);
          if (khiDoi) khiDoi();
        });
        dong.append(tenO, o);
        khung.appendChild(dong);
      });
      const loiKhung = document.createElement("p");
      loiKhung.className = "wh-loi";
      loiKhung.id = idKhung + "L";
      loiKhung.setAttribute("role", "alert");
      loiKhung.hidden = true;
      khung.appendChild(loiKhung);
      cap.appendChild(khung);
      whartonCapNhatDem(khung, w.ngan_sach);
    });
    if (!cap.children.length) cap.remove();
    else if (cap.children.length === 1) cap.classList.add("is-mot");
  });
  return whartonChuoiTuMap(daLuu);
}

/* Diem quyet tam dang khoa va em nay DA co diem: server khong cho doi tick thi / nguyen vong
   (`wharton_da_khoa`). Vo hieu hoa hai nut luu o Buoc 1-2 va hien ghi chu, thay vi de bam roi bi tu choi. */
function capNhatKhoaNguyenVong(w) {
  const co = (m) => !!m && Object.keys(m).length > 0;
  const giu = !!(w && w.bat && w.khoa && (co(w.w1) || co(w.w2)));
  el("btnSubmitTestSelection").disabled = giu;
  el("btnSubmitPreferences").disabled = giu;
  el("testSelectionKhoa").hidden = !giu;
  el("preferencesKhoa").hidden = !giu;
}

/* Ve Buoc 3 tu `state` (ket qua get_student_entry_state); `giu` = chu da go can giu lai. */
function renderWhartonStep(state, giu) {
  const hop = el("fbWhartonStep");
  const body = el("fbWhartonBody");
  const w = state && state.wharton;
  clear(body);
  capNhatKhoaNguyenVong(w);
  /* FA-UI-3: workspace bật xếp theo loại CLB và huy chương -> bước "Huy chương" thay bước này. */
  if (renderHuyChuongStep(state) || !w || !w.bat) {
    whartonState = null;
    daLuuWharton = "";
    hop.hidden = true;
    return;
  }
  whartonState = state;
  daLuuWharton = whartonVeKhung(body, w, {
    ranked: state.ranked_clubs,
    ten: (cid) => {
      const club = currentClubs.find((c) => c.club_id === cid);
      return club ? club.name : cid;
    },
    giu,
    chiDoc: !!w.khoa,
    khiDoi: veDauChuaLuu,
  });
  /* Dang khoa (da chay xep): chi doc, kem cau nhac mo khoa o the Quan ly. */
  el("fbWhartonKhoa").hidden = !w.khoa;
  el("btnSubmitWharton").disabled = !!w.khoa;
  hop.hidden = !body.querySelector(".wh-khung");
}

/* ------------------------------------------------------------------ *
 * FA-UI-3: BUOC 3 "HUY CHUONG" (vang 60, bac 30, dong 10 moi ngay)
 * ------------------------------------------------------------------ */
const HC_DIEM = [60, 30, 10];
let huyChuongState = null;   // state cua em dang mo khi FA bat; null = FA tat

/* Mac dinh D2 (chi o lop dang ky, em doi duoc): theo thu tu nguyen vong, bo CLB Tu do. */
function hcMacDinh(dsClb) {
  const ra = {};
  dsClb.slice(0, 3).forEach((cid, i) => { ra[HC_DIEM[i]] = cid; });
  return ra;
}

/* Ve buoc huy chuong; tra true khi FA bat (da ve), false khi tat (an buoc). */
function renderHuyChuongStep(state) {
  const hop = el("fbHuyChuongStep");
  const body = el("fbHuyChuongBody");
  const hc = state && state.huy_chuong;
  clear(body);
  if (!hc || !hc.bat) {
    huyChuongState = null;
    hop.hidden = true;
    return false;
  }
  huyChuongState = state;
  const ten = (cid) => {
    const club = currentClubs.find((c) => c.club_id === cid);
    return club ? club.name : cid;
  };
  (hc.ds_buoi || []).forEach((buoi) => {
    const dsClb = (state.ranked_clubs || []).filter((cid) =>
      hc.buoi_cua_clb[cid] === buoi && hc.loai_cua_clb[cid] !== "TU_DO");
    if (!dsClb.length) return;
    const daLuu = {};
    dsClb.forEach((cid) => { if (cid in hc.da_luu) daLuu[hc.da_luu[cid]] = cid; });
    const dat = Object.keys(daLuu).length ? daLuu : hcMacDinh(dsClb);
    const khung = document.createElement("div");
    khung.className = "hc-khung";
    khung.dataset.buoi = buoi;
    if ((hc.ds_buoi || []).length > 1) {
      const h = document.createElement("h4");
      h.textContent = nhanBuoi(buoi);
      khung.appendChild(h);
    }
    HC_DIEM.forEach((diem) => {
      const nhan = document.createElement("label");
      nhan.className = "hc-dong";
      const chu = document.createElement("span");
      chu.textContent = t("hc_ten_" + diem);
      const chon = document.createElement("select");
      chon.className = "hc-chon text-input";
      chon.dataset.diem = String(diem);
      chon.dataset.buoi = buoi;
      chon.disabled = !!hc.khoa;
      [["", t("hc_khong_dat")], ...dsClb.map((cid) => [cid, ten(cid)])].forEach(([v, txt]) => {
        const o = document.createElement("option");
        o.value = v;
        o.textContent = txt;
        chon.appendChild(o);
      });
      chon.value = dat[diem] || "";
      chon.dataset.cu = chon.value;
      chon.addEventListener("change", () => hcDoi(khung, chon));
      nhan.append(chu, chon);
      khung.appendChild(nhan);
    });
    body.appendChild(khung);
  });
  el("fbHuyChuongKhoa").hidden = !hc.khoa;
  el("btnSubmitHuyChuong").disabled = !!hc.khoa;
  hcCapNhatNhac();
  hop.hidden = !body.querySelector(".hc-khung");
  return true;
}

/* Chon mot CLB dang co huy chuong khac (cung ngay) thi hai huy chuong doi cho. */
function hcDoi(khung, chon) {
  const moi = chon.value;
  if (moi) {
    khung.querySelectorAll("select.hc-chon").forEach((o) => {
      if (o !== chon && o.value === moi) {
        o.value = chon.dataset.cu;
        o.dataset.cu = o.value;
      }
    });
  }
  chon.dataset.cu = moi;
  hcCapNhatNhac();
}

/* FA-N2 (V§6.1, D2): sau khi LUU nguyen vong, giu huy chuong khop thu tu. Moi ngay:
   - chua co huy chuong nao da luu (em luoi)            -> luu mac dinh cua thu tu MOI;
   - huy chuong da luu = mac dinh cua thu tu CU (chua chinh tay) va thu tu doi -> luu mac dinh moi;
   - da chinh tay va thu tu doi                         -> giu nguyen, hien cau nhac nhe.
   Chi goi submit_huy_chuong (may chu van kiem moi thu); khong suy dien o may chu. */
let hcNhacSid = null;   // em dang can cau nhac "da chinh tay"

function hcDanhSachNgay(nv, hc, buoi) {
  return nv.filter((cid) => hc.buoi_cua_clb[cid] === buoi && hc.loai_cua_clb[cid] !== "TU_DO");
}

function hcCoDatNhu(daLuu, macDinh, dsClb) {
  /* daLuu {cid: diem} so voi macDinh {diem: cid}, chi xet cac CLB cua ngay (dsClb). */
  const a = {};
  dsClb.forEach((cid) => { if (cid in daLuu) a[cid] = daLuu[cid]; });
  const b = {};
  Object.keys(macDinh).forEach((d) => { b[macDinh[d]] = Number(d); });
  const ka = Object.keys(a).sort();
  const kb = Object.keys(b).sort();
  return ka.length === kb.length && ka.every((k, i) => k === kb[i] && a[k] === b[k]);
}

function hcTheoNguyenVong(sid, nvTruoc, nvMoi, hcTruoc) {
  callApi("get_student_entry_state", sid).then((res) => {
    if (!res.ok || sid !== currentFallbackStudent) return;
    const hc = res.data.huy_chuong;
    if (!hc || !hc.bat || hc.khoa) { lamMoiBuoc3(true); return; }
    /* Ban do ngay/loai chi co CLB dang trong nguyen vong: gop ban CU de loc dung ca danh sach cu. */
    const gop = {
      buoi_cua_clb: Object.assign({}, hcTruoc.buoi_cua_clb, hc.buoi_cua_clb),
      loai_cua_clb: Object.assign({}, hcTruoc.loai_cua_clb, hc.loai_cua_clb),
    };
    const dsBuoi = Array.from(new Set([...(hcTruoc.ds_buoi || []), ...(hc.ds_buoi || [])]));
    const moi = Object.assign({}, hc.da_luu);              /* sau khi luu, may chu da bo CLB bi go */
    let nhac = false;
    dsBuoi.forEach((buoi) => {
      const dsMoi = hcDanhSachNgay(nvMoi, gop, buoi);
      const dsCu = hcDanhSachNgay(nvTruoc, gop, buoi);
      const daLuuCu = hcTruoc.da_luu || {};
      const coLuuCu = dsCu.some((cid) => cid in daLuuCu);
      const doiThuTu = dsMoi.join(",") !== dsCu.join(",");
      let macDinhMoi = false;
      if (!coLuuCu) macDinhMoi = dsMoi.length > 0 && !dsMoi.some((cid) => cid in moi);
      else if (doiThuTu) {
        if (hcCoDatNhu(daLuuCu, hcMacDinh(dsCu), dsCu)) macDinhMoi = true;
        else nhac = true;
      }
      if (macDinhMoi) {
        dsMoi.forEach((cid) => { delete moi[cid]; });
        const md = hcMacDinh(dsMoi);
        Object.keys(md).forEach((d) => { moi[md[d]] = Number(d); });
      }
    });
    hcNhacSid = nhac ? sid : null;
    const doi = JSON.stringify(Object.entries(moi).sort()) !== JSON.stringify(Object.entries(hc.da_luu).sort());
    if (!doi) { lamMoiBuoc3(true); return; }
    callApi("submit_huy_chuong", sid, moi).then(() => lamMoiBuoc3(true));
  });
}

/* V§6.1: vang o CLB Tuyen chon thi nhac huy chuong chi dung khi bang diem va da vuot diem san. */
function hcCapNhatNhac() {
  const hc = huyChuongState && huyChuongState.huy_chuong;
  const co = !!hc && Array.from(document.querySelectorAll('#fbHuyChuongBody select.hc-chon[data-diem="60"]'))
    .some((o) => o.value && hc.loai_cua_clb[o.value] === "TUYEN_CHON");
  el("hcNhacTuyenChon").hidden = !co;
  el("hcNhacDaChinh").hidden = hcNhacSid !== currentFallbackStudent || !currentFallbackStudent;
}

function hcThuThap() {
  const ra = {};
  document.querySelectorAll("#fbHuyChuongBody select.hc-chon").forEach((o) => {
    if (o.value) ra[o.value] = Number(o.dataset.diem);
  });
  return ra;
}

/* Hoi lai server roi ve lai Buoc 3: sau khi luu Buoc 1 / 2 / 3. `giuGoDo` = giu chu dang go. */
function lamMoiBuoc3(giuGoDo) {
  if (!currentFallbackStudent || (!whartonState && !huyChuongState)) return;
  const sid = currentFallbackStudent;
  callApi("get_student_entry_state", sid).then((res) => {
    if (!res.ok || sid !== currentFallbackStudent) return;
    renderWhartonStep(res.data, giuGoDo ? whartonGiuTam() : null);
    veDauChuaLuu();
  });
}

function renderTestSelectionGrid(testedClubIds) {
  const grid = el("testSelectionGrid");
  clear(grid);
  currentClubs.forEach((c) => {
    const row = document.createElement("div");
    row.className = "option-row" + (testedClubIds.includes(c.club_id) ? " is-checked" : "");
    row.dataset.clubId = c.club_id;
    row.innerHTML = `<span class="option-hop" aria-hidden="true"></span>` +
      `<span class="option-ten">${esc(c.name)}</span><span class="cb-club-id">${esc(phuBuoiCLB(c))}</span>`;
    row.addEventListener("click", () => {
      /* Bo tick thi luon cho; chi CHAN khi dang bat them. */
      if (!row.classList.contains("is-checked")) {
        const buoiNay = c.buoi || BUOI_MAC_DINH;
        const daCo = Array.from(
          document.querySelectorAll("#testSelectionGrid .option-row.is-checked")
        ).filter(
          (r) => (clubBuoi(r.dataset.clubId) || BUOI_MAC_DINH) === buoiNay
        ).length;
        if (daCo >= TRAN_CLB_THI_MOI_BUOI) {
          showToast(
            trErr({
              code: "max_thi_moi_buoi",
              params: { buoi: nhanBuoi(buoiNay), tran: TRAN_CLB_THI_MOI_BUOI },
            }),
            "error"
          );
          return;
        }
      }
      row.classList.toggle("is-checked");
      veDauChuaLuu();
    });
    choBamDuoc(row, true);
    grid.appendChild(row);
  });
}

/* T3-35: ben phai moi CLB chi hien BUOI (khi co), khong bao gio hien ma tho kieu `clb_coking`. */
function phuBuoiCLB(c) {
  return c && c.buoi && c.buoi !== BUOI_MAC_DINH ? nhanBuoi(c.buoi) : "";
}

function renderRankingSourceGrid() {
  const grid = el("rankingSourceGrid");
  clear(grid);
  currentClubs.forEach((c) => {
    const row = document.createElement("div");
    row.className = "option-row";
    row.dataset.clubId = c.club_id;
    /* Hien BUOI thay vi ma CLB khi truong dung nhieu buoi: o buoc nay
       hoc sinh dang quyet dinh "tuan minh kin chua", va buoi la thong
       tin giup quyet dinh — ma CLB thi khong. */
    const phu = phuBuoiCLB(c);
    row.innerHTML = `<span class="option-hang" aria-hidden="true"></span>` +
      `<span class="option-ten">${esc(c.name)}</span><span class="cb-club-id">${esc(phu)}</span>`;
    row.addEventListener("click", () => {
      if (currentRanking.includes(c.club_id)) {
        showToast(trErr({ code: "duplicate_preference_in_list", params: {} }), "error");
        return;
      }
      /* Dem theo BUOI cua chinh CLB dang bam, khong dem tong ca tuan.
         Tong 10 la tran cua truong MOT buoi; voi sau buoi thi em nao chon
         2 CLB moi buoi da cham tran o CLB thu 11 va khong hieu vi sao. */
      const buoiNay = c.buoi || BUOI_MAC_DINH;
      const daCo = currentRanking.filter(
        (id) => (clubBuoi(id) || BUOI_MAC_DINH) === buoiNay
      ).length;
      if (daCo >= TRAN_NGUYEN_VONG_MOI_BUOI) {
        showToast(
          trErr({
            code: "max_pref_moi_buoi",
            params: { buoi: nhanBuoi(buoiNay), tran: TRAN_NGUYEN_VONG_MOI_BUOI },
          }),
          "error"
        );
        return;
      }
      currentRanking.push(c.club_id);
      renderRankingList();
    });
    choBamDuoc(row, false);
    grid.appendChild(row);
  });
}

function renderRankingList() {
  const list = el("rankingList");
  clear(list);
  veChiBaoPhuBuoi(currentRanking);
  if (el("chuaLuuNv")) veDauChuaLuu();
  /* Danh dau ngay tren luoi nguon CLB nao da xep, thu may — de khong
     phai doi chieu qua lai voi danh sach ben duoi. */
  document.querySelectorAll("#rankingSourceGrid .option-row").forEach((row) => {
    const vt = currentRanking.indexOf(row.dataset.clubId);
    row.classList.toggle("is-ranked", vt !== -1);
    const o = row.querySelector(".option-hang");
    if (o) o.textContent = vt !== -1 ? String(vt + 1) : "";
  });
  currentRanking.forEach((cid, idx) => {
    const club = currentClubs.find((c) => c.club_id === cid);
    const li = document.createElement("li");
    const hang = document.createElement("span");
    hang.className = "hs-chip-hang";
    hang.textContent = String(idx + 1);
    li.appendChild(hang);
    const label = document.createElement("span");
    label.className = "ranking-ten";
    label.textContent = club ? club.name : cid;
    const phu = document.createElement("span");
    phu.className = "hs-card-ma";
    phu.textContent = club ? phuBuoiCLB(club) : "";
    label.appendChild(document.createTextNode(" "));
    label.appendChild(phu);
    const removeBtn = document.createElement("button");
    removeBtn.textContent = t("btn_remove_ranked");
    removeBtn.addEventListener("click", () => {
      currentRanking.splice(idx, 1);
      renderRankingList();
    });
    li.appendChild(label);
    li.appendChild(removeBtn);
    list.appendChild(li);
  });
}
