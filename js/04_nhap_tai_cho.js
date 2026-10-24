/* js/04_nhap_tai_cho.js — Thẻ 03 — Nhập tại chỗ (kiosk): chọn học sinh, tick thi, xếp nguyện vọng.

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
let choRoiDi = null; // hen gio cua lan bam roi di thu nhat
let khoaRoiDi = null; // lan bam thu nhat la DI DAU (xac nhan phai cung cho)

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

function whartonChuaLuu() {
  return !!currentFallbackStudent && !!whartonState && whartonChuoi() !== daLuuWharton;
}

function veDauChuaLuu() {
  el("chuaLuuThi").hidden = !thiChuaLuu();
  el("chuaLuuNv").hidden = !nvChuaLuu();
  el("chuaLuuWharton").hidden = !whartonChuaLuu();
}

/* Chay `hanhDong` neu khong con gi chua luu; neu con, lan bam dau chi
   canh bao, lan bam thu hai — vao CUNG cho (`khoa`), trong 4 giay — moi
   bo thay doi va di tiep. Cung cho la bat buoc: bam em khac roi bam sang
   the khac khong phai la "xac nhan bo thay doi" cho viec doi the. */
function roiDiNeuDuoc(hanhDong, khoa) {
  if (!thiChuaLuu() && !nvChuaLuu() && !whartonChuaLuu()) {
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
  currentRanking = [];
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
  el("btnCreateStudent").addEventListener("click", () => {
    const id = el("newStudentId").value.trim();
    const name = el("newStudentName").value.trim();
    if (!id || !name) {
      showToast(t("toast_need_id_and_name"), "error");
      return;
    }
    roiDiNeuDuoc(() => khiBan(el("btnCreateStudent"), () => callApi("create_student_if_missing", id, name)).then((res) => {
      if (!res.ok) {
        showErrorToast(res.errors);
        return;
      }
      showToast(res.data.created ? t("toast_student_created") : t("toast_student_exists"), "success");
      el("newStudentId").value = "";
      el("newStudentName").value = "";
      loadFallbackStudentList();
      selectFallbackStudent(id);
    }), "tao:" + id);
  });

  el("btnSubmitTestSelection").addEventListener("click", () => {
    if (!currentFallbackStudent) return;
    const checked = Array.from(document.querySelectorAll("#testSelectionGrid .option-row.is-checked")).map(
      (row) => row.dataset.clubId
    );
    khiBan(el("btnSubmitTestSelection"), () => callApi("submit_test_selection", currentFallbackStudent, checked)).then((res) => {
      if (res.ok) {
        /* Bo tick CLB da cham diem la xoa diem do (api
           _xoa_diem_khong_con_tick) — phai NOI RA, xoa diem giao vien
           da cham ma im lang la mat du lieu khong ai hay. */
        daLuuThi = checked.slice().sort();
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
        loadFallbackStudentList(); // cap nhat the "n CLB thi" trong danh sach
      } else {
        feedbackErrors(el("testSelectionFeedback"), res.errors);
      }
    });
  });

  el("btnSubmitWharton").addEventListener("click", () => {
    if (!currentFallbackStudent || !whartonState) return;
    const sid = currentFallbackStudent;
    const { w1, w2 } = whartonThuThap();
    khiBan(el("btnSubmitWharton"), () => callApi("submit_wharton", sid, w1, w2)).then((res) => {
      if (res.ok) {
        feedback(el("whartonFeedback"), t("feedback_wharton_saved"), false);
        lamMoiBuoc3(false);         /* ve lai tu trang thai DA LUU */
      } else {
        /* Server moi la noi quyet dinh (V6): chi nhac loi, khong sua gia tri o day. */
        feedbackErrors(el("whartonFeedback"), res.errors);
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
    khiBan(el("btnSubmitPreferences"), () => callApi("submit_preferences", currentFallbackStudent, currentRanking)).then((res) => {
      if (res.ok) {
        daLuuNv = currentRanking.slice();
        veDauChuaLuu();
        lamMoiBuoc3(true);          /* bo mot CLB khoi nguyen vong la xoa diem Wharton cua no */
        feedback(el("preferencesFeedback"), t("feedback_preferences_saved", { n: res.data.n_ranked }), false);
        loadFallbackStudentList(); // cap nhat the "n nguyen vong" trong danh sach
      } else {
        feedbackErrors(el("preferencesFeedback"), res.errors);
      }
    });
  });

  /* Xuat ho so em DANG MO — dung cho nguoi dung dang dung. Xuat theo
     du lieu DA LUU: con thay doi chua luu thi nhac luu truoc. */
  el("btnXuatEmNay").addEventListener("click", () => {
    if (!currentFallbackStudent) return;
    if (thiChuaLuu() || nvChuaLuu() || whartonChuaLuu()) {
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
        currentFallbackStudent = null;
        el("fallbackWorkArea").hidden = true;
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
  Promise.all([callApi("get_student_entry_state", studentId), callApi("list_clubs")]).then(([stateRes, clubsRes]) => {
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

    el("fallbackWorkArea").hidden = false;
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

function whartonChuoi() {
  const m = {};
  document.querySelectorAll("#fbWhartonBody input.wh-diem").forEach((o) => {
    m[o.dataset.quy + "|" + o.dataset.clb] = o.value.trim();
  });
  return whartonChuoiTuMap(m);
}

/* Cac o dang co chu (ke ca o bi khoa): giu lai khi ve lai Buoc 3, de doi ngon ngu hay luu
   Buoc 1/2 khong lam mat diem vua go. */
function whartonGiuTam() {
  const m = {};
  document.querySelectorAll("#fbWhartonBody input.wh-diem").forEach((o) => {
    if (!o.disabled) m[o.dataset.quy + "|" + o.dataset.clb] = o.value;
  });
  return m;
}

/* {w1, w2} gui len server. O trong = khong dat diem. Khong lam tron: "60.5" di nguyen la 60.5. */
function whartonThuThap() {
  const ra = { w1: {}, w2: {} };
  document.querySelectorAll("#fbWhartonBody input.wh-diem").forEach((o) => {
    const v = o.value.trim();
    if (v === "") return;
    ra[o.dataset.quy === "1" ? "w1" : "w2"][o.dataset.clb] = Number(v);
  });
  return ra;
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
}

/* Ve Buoc 3 tu `state` (ket qua get_student_entry_state); `giu` = chu da go can giu lai. */
function renderWhartonStep(state, giu) {
  const hop = el("fbWhartonStep");
  const body = el("fbWhartonBody");
  const w = state && state.wharton;
  clear(body);
  if (!w || !w.bat) {
    whartonState = null;
    daLuuWharton = "";
    hop.hidden = true;
    return;
  }
  whartonState = state;
  const nhieuBuoi = w.ds_buoi.length > 1;
  const daLuu = {};
  w.ds_buoi.forEach((buoi) => {
    if (nhieuBuoi) {
      const tieuDe = document.createElement("div");
      tieuDe.className = "wh-buoi-ten";
      tieuDe.textContent = nhanBuoi(buoi);
      tieuDe.dataset.buoi = buoi;
      body.appendChild(tieuDe);
    }
    [1, 2].forEach((quy) => {
      const ds = state.ranked_clubs.filter(
        (c) => w.buoi_cua_clb[c] === buoi && w.quy_cua_clb[c] === quy);
      if (!ds.length) return;                         // khung rong thi khong hien
      const luu = quy === 1 ? w.w1 : w.w2;
      const quyKia = quy === 1 ? w.w2 : w.w1;
      const khung = document.createElement("div");
      khung.className = "wh-khung";
      khung.dataset.quy = String(quy);
      khung.dataset.buoi = buoi;
      const dau = document.createElement("div");
      dau.className = "wh-khung-dau";
      const ten = document.createElement("span");
      ten.className = "wh-khung-ten";
      ten.textContent = t(quy === 1 ? "wharton_khung_thi" : "wharton_khung_khong_thi");
      const dem = document.createElement("span");
      dem.className = "wh-dem";
      dau.append(ten, dem);
      const ghiChu = document.createElement("p");
      ghiChu.className = "wh-ghi-chu";
      ghiChu.textContent = t(quy === 1 ? "wharton_khung_thi_ghi_chu" : "wharton_khung_khong_thi_ghi_chu");
      khung.append(dau, ghiChu);
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
        const club = currentClubs.find((c) => c.club_id === cid);
        const dong = document.createElement("div");
        dong.className = "wh-dong";
        const tenClb = document.createElement("span");
        tenClb.className = "wh-dong-ten";
        tenClb.textContent = club ? club.name : cid;
        const o = document.createElement("input");
        o.type = "number";
        o.min = "0";
        o.step = "1";
        o.setAttribute("inputmode", "numeric");
        o.className = "text-input text-input-sm wh-diem";
        o.dataset.quy = String(quy);
        o.dataset.clb = cid;
        o.setAttribute("aria-label", (club ? club.name : cid) + " — " + ten.textContent);
        const daCo = cid in luu ? String(luu[cid]) : "";
        daLuu[quy + "|" + cid] = daCo;
        const khoa = !!w.tu_dien_mot_clb && motClb && (daCo === "" || daCo === String(w.ngan_sach));
        const go = giu && (quy + "|" + cid) in giu ? giu[quy + "|" + cid] : null;
        o.value = khoa ? String(w.ngan_sach) : (go !== null ? go : daCo);
        o.disabled = khoa;
        o.addEventListener("input", () => {
          whartonCapNhatDem(khung, w.ngan_sach);
          veDauChuaLuu();
        });
        dong.append(tenClb, o);
        khung.appendChild(dong);
      });
      body.appendChild(khung);
      whartonCapNhatDem(khung, w.ngan_sach);
    });
  });
  daLuuWharton = whartonChuoiTuMap(daLuu);
  hop.hidden = !body.querySelector(".wh-khung");
}

/* Hoi lai server roi ve lai Buoc 3: sau khi luu Buoc 1 / 2 / 3. `giuGoDo` = giu chu dang go. */
function lamMoiBuoc3(giuGoDo) {
  if (!currentFallbackStudent || !whartonState) return;
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
      `<span class="option-ten">${esc(c.name)}</span><span class="cb-club-id">${esc(c.club_id)}</span>`;
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
    const phu = c.buoi && c.buoi !== BUOI_MAC_DINH ? nhanBuoi(c.buoi) : c.club_id;
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
    phu.textContent = club && club.buoi && club.buoi !== "__mac_dinh__" ? nhanBuoi(club.buoi) : cid;
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
