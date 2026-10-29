/* js/076_cai_dat.js — Hộp Cài đặt (A13.14): bánh răng ở thanh trái, mở được từ mọi tab.

   Bốn nhóm: (a) Điểm quyết tâm bật / tắt, (b) luật xếp của không gian làm việc đang mở,
   (c) giao diện (ngôn ngữ, hiệu ứng, cỡ chữ), (d) dữ liệu và sao lưu.
   Phần (a) và (b) đi qua get_cai_dat / save_cai_dat (backend kiểm bằng cau_hinh_ws.chuan_hoa);
   phần (d) dùng lại export_workspace, import_workspace, reset_data, mo_thu_muc.
   Script thường như các tệp js/ khác: dùng chung phạm vi với 075_workspace.js (wsEl, wsChon...).
*/
"use strict";

const KHOA_CO_CHU = "rbda_co_chu";
const CO_CHU = ["vua", "lon", "rat_lon"];

let cdDuLieu = null;        // trả lời của get_cai_dat
let cdLuat = null;          // luật đang sửa trong form (chưa lưu)
let cdNutMo = null;         // phần tử giữ tiêu điểm trước khi mở, để trả lại khi đóng
let cdResetPhamVi = null;   // phạm vi xoá đang chờ xác nhận

/* ------------------------------------------------------------------ *
 * CỠ CHỮ (lưu localStorage; kho lỗi thì vẫn đổi được trong phiên này)
 * ------------------------------------------------------------------ */

function cdDocCoChu() {
  try {
    const v = window.localStorage && window.localStorage.getItem(KHOA_CO_CHU);
    return CO_CHU.includes(v) ? v : "vua";
  } catch (e) { return "vua"; }
}

function cdApDungCoChu(co) {
  CO_CHU.forEach((c) => document.documentElement.classList.toggle("co-chu-" + c, c === co));
  document.querySelectorAll("[data-cd-co]").forEach((n) =>
    n.setAttribute("aria-pressed", n.dataset.cdCo === co ? "true" : "false"));
}

/* ------------------------------------------------------------------ *
 * MỞ / ĐÓNG
 * ------------------------------------------------------------------ */

function cdDangMo() { return !el("caiDatOverlay").hidden; }

function cdMo() {
  cdNutMo = document.activeElement;
  cdResetPhamVi = null;
  el("cdResetXn").hidden = true;
  el("caiDatOverlay").hidden = false;
  cdCapNhatNutGiaoDien();
  cdTai();
  el("caiDatTieuDe").focus();
}

function cdDong() {
  el("caiDatOverlay").hidden = true;
  const nut = el("btnCaiDat");
  if (cdNutMo && document.contains(cdNutMo) && !cdNutMo.hidden) cdNutMo.focus();
  else if (nut) nut.focus();
  cdNutMo = null;
}

/* Tab / Shift+Tab không rời hộp khi đang mở (hộp là cửa sổ phụ chặn phần còn lại). */
function cdGiuTieuDiem(ev) {
  if (ev.key !== "Tab") return;
  const ds = Array.from(el("caiDatHop").querySelectorAll(
    "button, input, select, textarea, [tabindex]:not([tabindex='-1'])"))
    .filter((n) => !n.disabled && n.offsetParent !== null);
  if (!ds.length) return;
  const dau = ds[0], cuoi = ds[ds.length - 1];
  if (ev.shiftKey && (document.activeElement === dau || document.activeElement === el("caiDatTieuDe"))) {
    ev.preventDefault(); cuoi.focus();
  } else if (!ev.shiftKey && document.activeElement === cuoi) {
    ev.preventDefault(); dau.focus();
  }
}

/* ------------------------------------------------------------------ *
 * NHÓM (a) + (b): LUẬT
 * ------------------------------------------------------------------ */

function cdTai() {
  return callApi("get_cai_dat").then((res) => {
    if (!res.ok) { showErrorToast(res.errors); return; }
    cdDuLieu = res.data;
    cdLuat = JSON.parse(JSON.stringify(res.data.rules));
    cdVeForm();
    cdVeNhomDuLieu();
  });
}

/* Dạng của `wsChoPhepWharton` / `wsDungThuTuNhom` (075_workspace.js) nhưng trên khoá của backend. */
function cdChoPhepDqt(l) { return l.priority !== "tier" && l.score_scope === "per_slot"; }
function cdDungNhom(l) { return l.tier_mode === "strict" || l.priority === "tier"; }

function cdGomForm() {
  const l = cdLuat;
  const lay = (id) => el(id);
  if (!lay("cdPriority")) return;
  l.priority = lay("cdPriority").value;
  l.tier_mode = lay("cdTierMode").value;
  l.score_scope = lay("cdScoreScope").value;
  l.wharton = lay("cdWharton").checked;
  const mc = parseInt(lay("cdMaxChoices").value, 10);
  l.max_choices = Number.isNaN(mc) ? lay("cdMaxChoices").value : mc;
  if (lay("cdKhongGioiHan").checked) l.max_tests = null;
  else {
    const mt = parseInt(lay("cdMaxTests").value, 10);
    l.max_tests = Number.isNaN(mt) ? lay("cdMaxTests").value : mt;
  }
  l.tiers = lay("cdTiers").value.split("\n").map((s) => s.trim()).filter(Boolean);
}

function cdCapNhatRangBuoc() {
  cdGomForm();
  const l = cdLuat;
  const cho = cdChoPhepDqt(l);
  const oDqt = el("cdWharton");
  oDqt.disabled = !cho;
  if (!cho) { oDqt.checked = false; l.wharton = false; }
  el("cdTiers").disabled = !cdDungNhom(l);
  el("cdMaxTests").disabled = el("cdKhongGioiHan").checked;
}

function cdVeForm() {
  const form = el("cdForm");
  const l = cdLuat;
  const tt = cdDuLieu;
  clear(form);
  const oDqt = wsEl("input", { type: "checkbox", id: "cdWharton", checked: l.wharton === true,
    disabled: !cdChoPhepDqt(l) });
  const oPri = wsChon("cdPriority", l.priority, [
    ["score", t("ws_r_priority_score")], ["tier", t("ws_r_priority_tier")],
    ["score+tier", t("ws_r_priority_both")]]);
  const oTm = wsChon("cdTierMode", l.tier_mode, [
    ["reserve", t("ws_r_tm_reserve")], ["strict", t("ws_r_tm_strict")]]);
  const oSs = wsChon("cdScoreScope", l.score_scope, [
    ["per_slot", t("ws_r_ss_per_slot")], ["per_person", t("ws_r_ss_per_person")]]);
  const oMc = wsEl("input", { type: "number", id: "cdMaxChoices", class: "text-input ws-so",
    min: "1", max: String(tt.toi_da.max_choices), step: "1", value: String(l.max_choices) });
  const oMt = wsEl("input", { type: "number", id: "cdMaxTests", class: "text-input ws-so",
    min: "0", max: String(tt.toi_da.max_tests), step: "1",
    value: l.max_tests === null ? "" : String(l.max_tests), disabled: l.max_tests === null });
  const oKhong = wsEl("input", { type: "checkbox", id: "cdKhongGioiHan", checked: l.max_tests === null });
  const oTiers = wsEl("textarea", { id: "cdTiers", class: "text-input ws-tiers", rows: "3",
    value: (l.tiers || []).join("\n"), disabled: !cdDungNhom(l), placeholder: t("ws_r_tiers_ph") });
  form.append(
    wsEl("h3", { class: "cd-ten-nhom", id: "cdTenDqt", text: t("cd_nhom_dqt") }),
    wsEl("div", { class: "cd-hang" },
      wsEl("label", { class: "cd-nhan cd-nhan-hop", for: "cdWharton" }, oDqt, " ", t("ws_r_wharton")),
      wsGoiYNgan("cdWharton", t("ws_r_wharton_ngan"), t("ws_r_wharton_ghi_chu"))),
    wsEl("h3", { class: "cd-ten-nhom", id: "cdTenLuat", text: t("cd_nhom_luat") }),
    wsEl("p", { class: "hint-text", text: t("cd_luat_ghi_chu") }),
    wsTruong("cdPriority", "ws_r_priority", oPri),
    wsTruong("cdTierMode", "ws_r_tier_mode", oTm),
    wsTruong("cdMaxChoices", "ws_r_max_choices", oMc),
    wsTruong("cdMaxTests", "ws_r_max_tests", wsEl("div", { class: "ws-hang" }, oMt,
      wsEl("label", { class: "ws-kem" }, oKhong, " ", t("ws_r_khong_gioi_han")))),
    wsTruong("cdScoreScope", "ws_r_score_scope", oSs),
    wsTruong("cdTiers", "ws_r_tiers", oTiers, t("ws_r_tiers_chi_strict")),
    wsEl("div", { class: "ws-loi", id: "cdLoi", role: "alert", hidden: true }),
    wsEl("div", { class: "cd-xac-nhan", id: "cdXacNhan", role: "alertdialog",
      "aria-labelledby": "cdXacNhanTieuDe", hidden: true },
      wsEl("strong", { id: "cdXacNhanTieuDe", text: t("cd_xn_tieu_de") }),
      wsEl("p", { class: "cd-xac-nhan-chu", id: "cdXacNhanChu" }),
      wsEl("div", { class: "cd-nhom-nut" },
        wsEl("button", { type: "button", class: "btn btn-primary", id: "cdXacNhanDongY",
          text: t("cd_xn_dong_y"), onclick: (ev) => khiBan(ev.currentTarget, () => cdLuu(true)) }),
        wsEl("button", { type: "button", class: "btn btn-secondary", id: "cdXacNhanHuy",
          text: t("btn_cancel"), onclick: cdAnXacNhan }))),
    wsEl("p", { class: "hint-text", id: "cdKhoa", hidden: !tt.khoa_stb,
      text: t("cd_dang_khoa", { dqt: tt.khoa_diem_quyet_tam ? t("cd_dang_khoa_dqt") : "" }) }),
    wsEl("div", { class: "cd-nhom-nut" },
      wsEl("button", { type: "submit", class: "btn btn-primary", id: "cdLuu", text: t("cd_luu") })));
  ["cdPriority", "cdTierMode", "cdScoreScope", "cdWharton", "cdKhongGioiHan"].forEach((id) =>
    el(id).addEventListener("change", cdCapNhatRangBuoc));
  ["cdMaxChoices", "cdMaxTests", "cdTiers"].forEach((id) => el(id).addEventListener("input", cdGomForm));
  cdCapNhatRangBuoc();
}

function cdHienLoi(errors) {
  const o = el("cdLoi");
  if (!o) return;
  o.textContent = trErrs(errors).join(" ");
  o.hidden = false;
}

function cdAnXacNhan() {
  const o = el("cdXacNhan");
  if (o) o.hidden = true;
  const b = el("cdLuu");
  if (b) b.focus();
}

function cdLuu(xacNhan) {
  cdGomForm();
  const o = el("cdLoi");
  if (o) o.hidden = true;
  return callApi("save_cai_dat", cdLuat, xacNhan === true).then((res) => {
    if (!res.ok) {
      const can = (res.errors || []).find((e) => e.code === "cai_dat_can_xac_nhan");
      if (can && !xacNhan) {
        el("cdXacNhanChu").textContent = t("cd_xn_noi_dung", { n: can.params.n_lan_chay });
        el("cdXacNhan").hidden = false;
        el("cdXacNhanDongY").focus();
        return;
      }
      el("cdXacNhan").hidden = true;
      cdHienLoi(res.errors);
      return;
    }
    el("cdXacNhan").hidden = true;
    if (!res.data.da_doi) { showToast(t("cd_khong_doi"), "success"); return; }
    showToast(res.data.sao_luu ? t("cd_da_luu_sao_luu", { ten: res.data.sao_luu }) : t("cd_da_luu"),
      "success");
    cdSauKhiDoiLuat(res.data.config);
  });
}

/* Luật mới vào giao diện (trần nhập liệu, khối Điểm quyết tâm...) rồi làm tươi các thẻ. */
function cdSauKhiDoiLuat(cfg) {
  if (typeof wsTrangThai !== "undefined" && wsTrangThai) wsTrangThai.config = cfg;
  wsApDungCauHinh(cfg);
  loadAdminTab();
  loadHealthReport();
  refreshDashboardStats();
  refreshSidebarStatus();
  cdTai();
}

/* ------------------------------------------------------------------ *
 * NHÓM (c): GIAO DIỆN
 * ------------------------------------------------------------------ */

function cdCapNhatNutGiaoDien() {
  const ngon = window.I18N.getLang();
  document.querySelectorAll("[data-cd-ngon]").forEach((n) =>
    n.setAttribute("aria-pressed", n.dataset.cdNgon === ngon ? "true" : "false"));
  cdApDungCoChu(cdDocCoChu());
}

/* ------------------------------------------------------------------ *
 * NHÓM (d): DỮ LIỆU VÀ SAO LƯU
 * ------------------------------------------------------------------ */

function cdVeNhomDuLieu() {
  const d = cdDuLieu;
  el("cdThuMucXuat").textContent = d.thu_muc_xuat;
  el("cdThuMucSaoLuu").textContent = d.thu_muc_sao_luu;
  el("cdXuatZip").disabled = !d.che_do_ws;
  el("cdNhapZip").disabled = !d.che_do_ws;
  el("cdChiWs").hidden = d.che_do_ws;
}

function cdMoThuMuc(duong) {
  callApi("mo_thu_muc", duong).then((res) => { if (!res.ok) showErrorToast(res.errors); });
}

function cdHoiXoa(phamVi) {
  cdResetPhamVi = phamVi;
  el("cdResetXn").hidden = false;
  el("cdResetDongY").focus();
}

function cdXoa() {
  const phamVi = cdResetPhamVi;
  if (!phamVi) return Promise.resolve();
  return callApi("reset_data", phamVi, "XOA").then((res) => {
    el("cdResetXn").hidden = true;
    cdResetPhamVi = null;
    if (!res.ok) { showErrorToast(res.errors); return; }
    showToast(t("cd_dat_lai_xong", { ten: res.data.backup_name }), "success");
    /* Mọi thẻ đều có thể đang giữ dữ liệu đã xoá (em đã chọn, danh sách đang mở...). Tải lại trang
       là cách chắc nhất; ngôn ngữ, hiệu ứng và cỡ chữ đã lưu nên không mất. */
    setTimeout(() => window.location.reload(), 900);
  });
}

/* ------------------------------------------------------------------ *
 * KHỞI ĐỘNG
 * ------------------------------------------------------------------ */

function initCaiDat() {
  cdApDungCoChu(cdDocCoChu());
  el("btnCaiDat").addEventListener("click", cdMo);
  el("caiDatDong").addEventListener("click", cdDong);
  el("caiDatOverlay").addEventListener("keydown", (ev) => {
    if (ev.key === "Escape") { ev.stopPropagation(); cdDong(); }
    else cdGiuTieuDiem(ev);
  });
  /* Bấm ra ngoài hộp (vào nền mờ) cũng đóng. */
  el("caiDatOverlay").addEventListener("mousedown", (ev) => {
    if (ev.target === el("caiDatOverlay")) cdDong();
  });
  el("cdForm").addEventListener("submit", (ev) => {
    ev.preventDefault();
    khiBan(el("cdLuu"), () => cdLuu(false));
  });
  document.querySelectorAll("[data-cd-ngon]").forEach((n) =>
    n.addEventListener("click", () => window.I18N.setLang(n.dataset.cdNgon)));
  document.querySelectorAll("[data-cd-co]").forEach((n) =>
    n.addEventListener("click", () => {
      try { if (window.localStorage) window.localStorage.setItem(KHOA_CO_CHU, n.dataset.cdCo); }
      catch (e) { /* không ghi được thì thôi */ }
      cdApDungCoChu(n.dataset.cdCo);
    }));
  el("cdMoXuat").addEventListener("click", () => cdDuLieu && cdMoThuMuc(cdDuLieu.thu_muc_xuat));
  el("cdMoSaoLuu").addEventListener("click", () => cdDuLieu && cdMoThuMuc(cdDuLieu.thu_muc_sao_luu));
  el("cdXuatZip").addEventListener("click", () => cdDuLieu && cdDuLieu.slug && wsXuat({ slug: cdDuLieu.slug }));
  el("cdNhapZip").addEventListener("click", () => el("cdTepZip").click());
  el("cdTepZip").addEventListener("change", (ev) => wsNhapZip(ev.target));
  document.querySelectorAll("[data-cd-reset]").forEach((n) =>
    n.addEventListener("click", () => cdHoiXoa(n.dataset.cdReset)));
  el("cdResetHuy").addEventListener("click", () => { cdResetPhamVi = null; el("cdResetXn").hidden = true; });
  el("cdResetDongY").addEventListener("click", (ev) => khiBan(ev.currentTarget, cdXoa));
  window.addEventListener("langchange", () => {
    cdCapNhatNutGiaoDien();
    if (!cdDangMo() || !cdDuLieu) return;
    cdGomForm();           // chữ đang sửa dở không mất khi đổi ngôn ngữ
    cdVeForm();
  });
}
