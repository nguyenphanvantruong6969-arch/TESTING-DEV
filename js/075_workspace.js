/* js/075_workspace.js — Workspace: màn chọn, nút đổi ở thanh bên, trình hướng dẫn tạo mới.

   Một phần của giao diện chính. Các tệp js/ là SCRIPT THƯỜNG (không phải ES
   module) nạp theo đúng thứ tự trong index.html và dùng chung một phạm vi.

   Backend: api_workspace.py. Chạy với đường dẫn CSDL riêng (argv) thì
   `get_workspace_state().enabled` là false: nút đổi ẩn, màn chọn không bao giờ
   hiện — giao diện y như trước khi có workspace.

   ĐỔI WORKSPACE = TẢI LẠI TRANG. Mỗi thẻ có trạng thái riêng trong các biến
   `let` ở đầu js/02…06 (hàng chờ nạp tệp, em đang nhập tại chỗ, CLB đang chấm
   điểm, dải chọn buổi…), mà tất cả đều thuộc về CSDL CŨ. Dọn từng biến là
   một danh sách sẽ lạc hậu ngay khi có biến mới; tải lại là chạy đúng
   init() của js/08_khoi_dong.js — con đường khởi động DUY NHẤT — nên không
   thể sót thứ gì. Ngôn ngữ đã chọn nằm trong localStorage nên được giữ.
*/
"use strict";

const WS_DANH_TU = ["person", "slot", "session", "group", "score"];
const WS_NGANH = ["school", "company", "event", "custom"];
const WS_TONG_BUOC = 4;

let wsTrangThai = null;     // data của get_workspace_state
let wsDanhSach = [];        // data.workspaces của list_workspaces
let wsMau = [];             // data.templates của list_templates
let wsSuaDong = null;       // {slug, kieu: "doi_ten" | "nhan_ban" | "luu_mau"}
let wsWizard = null;        // null = đang ở màn danh sách
let wsCoTheDong = false;    // đã có workspace để quay lại thì mới đóng được màn chọn

/* Tải lại trang sau khi đổi workspace. Cờ báo cho cầu nối trình duyệt
   (browser_host.py) rằng đây KHÔNG phải đóng cửa sổ — nếu không, sự kiện
   pagehide báo "đã đóng" và nó tắt máy chủ ngay dưới chân trang. */
function wsTaiLaiTrang() {
  window.__DANG_TAI_LAI = true;
  window.location.reload();
}

/* ------------------------------------------------------------------ *
 * TIỆN ÍCH DỰNG DOM
 * ------------------------------------------------------------------ */

/* Dựng phần tử: wsEl("button", {class: "btn", text: "…", onclick: fn}, ...con). */
function wsEl(tag, thuocTinh, ...con) {
  const e = document.createElement(tag);
  Object.entries(thuocTinh || {}).forEach(([k, v]) => {
    if (v === null || v === undefined || v === false) return;
    if (k === "class") e.className = v;
    else if (k === "text") e.textContent = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
    else if (k === "value") e.value = v;
    else if (k === "checked") e.checked = true;
    else if (k === "disabled") e.disabled = true;
    else e.setAttribute(k, v === true ? "" : v);
  });
  con.flat().forEach((c) => {
    if (c === null || c === undefined || c === false) return;
    e.append(c.nodeType ? c : document.createTextNode(String(c)));
  });
  return e;
}

function wsTenNganh(nganh) {
  return t("ws_loai_" + (WS_NGANH.includes(nganh) ? nganh : "custom"));
}

/* Backend trả "YYYY-MM-DD HH:MM:SS". Tiếng Việt đọc ngày trước tháng: "15/10/2026 12:19:20";
   tiếng Anh, hoặc chuỗi không đúng mẫu, giữ nguyên. */
function wsDinhDangNgay(chuoi) {
  const m = /^(\d{4})-(\d{2})-(\d{2})([ T]\d{2}:\d{2}(?::\d{2})?)$/.exec(String(chuoi || ""));
  if (!m || window.I18N.getLang() !== "vi") return chuoi;
  return m[3] + "/" + m[2] + "/" + m[1] + m[4].replace("T", " ");
}

/* Tên mẫu: mẫu dựng sẵn do backend đặt tên cố định bằng tiếng Việt, nên dịch ở đây theo
   ngôn ngữ đang chọn. Mẫu người dùng tự lưu là tên họ đặt, giữ nguyên. */
function wsTenMau(m) {
  return m.builtin ? t("ws_mau_truong_hoc") : m.name;
}

/* ------------------------------------------------------------------ *
 * KHỞI ĐỘNG VÀ NÚT Ở THANH BÊN
 * ------------------------------------------------------------------ */

function initWorkspace() {
  const nut = el("btnWorkspace");
  if (nut) nut.addEventListener("click", () => wsMoManChon(true));
  el("wsOverlay").addEventListener("keydown", (ev) => {
    if (ev.key === "Escape" && wsCoTheDong) wsDongManChon();
  });
  window.addEventListener("langchange", () => {
    wsCapNhatTieuDe();
    if (el("wsOverlay").hidden) return;
    if (wsWizard) wsGomBuoc();   // chữ đang gõ dở không được mất khi đổi ngôn ngữ
    wsVe();
  });
  callApi("get_workspace_state").then((res) => {
    if (!res.ok) return;
    wsTrangThai = res.data;
    /* Nhãn từ vựng của workspace (xem nhan_ws.py / I18N.applyLabels): chỉ vẽ lại
       khi KHÁC mặc định trường học, nên trường học thường không thấy gì đổi. Lấy từ
       get_workspace_state chứ không get_workspace_config vì hàm sau tắt khi chạy với
       đường dẫn CSDL riêng, mà nhãn của CSDL đó vẫn phải áp. */
    wsApDungCauHinh(wsTrangThai.config);
    wsVeTenHienTai();
    wsCapNhatTieuDe();
    /* Chưa chọn (có nhiều workspace lúc khởi động) thì màn chọn hiện ngay,
       đè lên trên và KHÔNG đóng được cho tới khi mở một workspace. */
    if (wsTrangThai.enabled && !wsTrangThai.chon) wsMoManChon(false);
  });
}

/* Tiêu đề cửa sổ: "<tên danh từ chỗ xếp> — <tên workspace>". Trình duyệt dự phòng lấy
   từ document.title; cửa sổ gốc pywebview thì phải nhờ backend đổi (dat_tieu_de_cua_so).
   Chạy với đường dẫn CSDL riêng thì giữ tiêu đề cũ, không đụng gì. */
function wsCapNhatTieuDe() {
  if (!wsTrangThai || !wsTrangThai.enabled) return;
  const tieuDe = window.I18N.nounText("slot", "", window.I18N.getLang()) + " — " +
    (wsTrangThai.name || wsTrangThai.slug || "");
  document.title = tieuDe;
  callApi("dat_tieu_de_cua_so", tieuDe);
}

/* Nhãn VÀ luật của workspace vào giao diện: chữ (I18N), hai trần nhập liệu ở thẻ 03, và
   câu gợi ý "tối đa N" (không giới hạn thì dùng câu riêng). Lấy từ get_workspace_state
   nên chạy được cả khi mở bằng đường dẫn CSDL riêng. */
function wsApDungCauHinh(cfg) {
  if (!cfg) return;
  const luat = cfg.rules || {};
  TRAN_NGUYEN_VONG_MOI_BUOI = Number.isInteger(luat.max_choices) ? luat.max_choices : 10;
  TRAN_CLB_THI_MOI_BUOI = luat.max_tests === null ? Infinity
    : (Number.isInteger(luat.max_tests) ? luat.max_tests : 5);
  const goiY = el("fallbackStep1Hint");
  if (goiY) {
    goiY.setAttribute("data-i18n", luat.max_tests === null
      ? "fallback_step1_hint_khong_gioi_han" : "fallback_step1_hint");
  }
  apDungLuatChamDiem(luat);
  window.I18N.applyConfig(cfg);
}

function wsVeTenHienTai() {
  const nut = el("btnWorkspace");
  if (!nut || !wsTrangThai) return;
  nut.hidden = !wsTrangThai.enabled;
  el("wsTenHienTai").textContent = wsTrangThai.name || wsTrangThai.slug || "";
}

/* ------------------------------------------------------------------ *
 * MÀN CHỌN
 * ------------------------------------------------------------------ */

function wsMoManChon(coTheDong) {
  wsCoTheDong = coTheDong;
  wsSuaDong = null;
  wsWizard = null;
  el("wsOverlay").hidden = false;
  wsLamMoiDanhSach();
}

function wsDongManChon() {
  el("wsOverlay").hidden = true;
  const nut = el("btnWorkspace");
  if (nut && !nut.hidden) nut.focus();
}

function wsLamMoiDanhSach() {
  return Promise.all([callApi("list_workspaces"), callApi("list_templates")]).then(([ds, mau]) => {
    if (!ds.ok) { showErrorToast(ds.errors); return; }
    wsDanhSach = ds.data.workspaces;
    wsMau = mau.ok ? mau.data.templates : [];
    wsVe();
  });
}

function wsVe() {
  if (wsWizard) wsVeWizard();
  else wsVeDanhSach();
}

function wsVeDanhSach() {
  const hop = el("wsHop");
  clear(hop);
  hop.append(
    wsEl("h2", { id: "wsTieuDe", class: "ws-tieu-de", tabindex: "-1", text: t("ws_chon_title") }),
    wsEl("p", { class: "hint-text", text: t("ws_chon_hint") }),
  );

  if (!wsDanhSach.length) {
    hop.append(wsEl("p", { class: "ws-rong", text: t("ws_rong") }));
  } else {
    const thead = wsEl("thead", null, wsEl("tr", null,
      wsEl("th", { text: t("ws_cot_ten") }),
      wsEl("th", { text: t("ws_cot_loai") }),
      wsEl("th", { text: t("ws_cot_sua") }),
      wsEl("th", { text: t("th_thao_tac") })));
    const tbody = wsEl("tbody");
    wsDanhSach.forEach((w) => {
      tbody.append(wsDongWorkspace(w));
      if (wsSuaDong && wsSuaDong.slug === w.slug) tbody.append(wsDongSua(w));
    });
    hop.append(wsEl("div", { class: "ws-bang-boc" },
      wsEl("table", { class: "data-table ws-bang", id: "wsBang" }, thead, tbody)));
  }

  const chan = wsEl("div", { class: "ws-chan" },
    wsEl("button", { type: "button", class: "btn btn-primary", id: "wsBtnMoi",
      "data-i18n": "ws_btn_moi", text: t("ws_btn_moi"), onclick: wsBatDauWizard }),
    wsEl("button", { type: "button", class: "btn btn-secondary", id: "wsBtnNhap",
      "data-i18n": "ws_btn_nhap_zip", text: t("ws_btn_nhap_zip"),
      onclick: () => el("wsFileZip").click() }),
    wsEl("input", { type: "file", id: "wsFileZip", accept: ".zip", hidden: true,
      onchange: (ev) => wsNhapZip(ev.target) }),
    wsCoTheDong ? wsEl("button", { type: "button", class: "btn btn-ghost ws-dong", id: "wsBtnDong",
      "data-i18n": "ws_btn_dong", text: t("ws_btn_dong"), onclick: wsDongManChon }) : null,
  );
  hop.append(chan);
  const tieuDe = el("wsTieuDe");
  if (tieuDe) tieuDe.focus();
}

function wsDongWorkspace(w) {
  const nutXoa = wsEl("button", { type: "button", class: "btn btn-ghost btn-nho ws-xoa",
    "data-i18n": "ws_btn_xoa", "data-slug": w.slug, text: t("ws_btn_xoa"),
    disabled: w.dang_mo, title: w.dang_mo ? t("ws_khong_xoa_dang_mo") : null });
  if (!w.dang_mo) {
    armTwoStepConfirm(nutXoa, () => t("ws_btn_xoa_xn"), () => wsXoa(w), 4000);
  }
  const hanhDong = (khoa, ham, lop) => wsEl("button", {
    type: "button", class: "btn btn-ghost btn-nho " + (lop || ""),
    "data-slug": w.slug, "data-hanh-dong": khoa,
    text: t("ws_btn_" + khoa), onclick: ham });
  return wsEl("tr", { "data-slug": w.slug, class: w.dang_mo ? "ws-dang-mo" : null },
    wsEl("td", { class: "ws-ten" },
      wsEl("div", { class: "ws-ten-chinh", text: w.name }),
      wsEl("div", { class: "ws-slug", text: w.slug }),
      w.dang_mo ? wsEl("span", { class: "ws-badge", text: t("ws_dang_mo_nhan") }) : null),
    wsEl("td", { text: wsTenNganh(w.industry) }),
    wsEl("td", { class: "ws-sua", text: wsDinhDangNgay(w.modified) }),
    /* <td> phải giữ kiểu table-cell: đặt display:flex thẳng lên nó làm nền hàng và
       đường kẻ chỉ phủ một phần ô. Hộp flex nằm ở <div> bên trong. */
    wsEl("td", { class: "ws-cot-hanh-dong" }, wsEl("div", { class: "ws-hanh-dong" },
      wsEl("button", { type: "button", class: "btn btn-secondary btn-nho",
        "data-slug": w.slug, "data-hanh-dong": "mo", text: t("ws_btn_mo"),
        disabled: w.dang_mo, onclick: () => wsMo(w) }),
      hanhDong("doi_ten", () => wsBatSua(w, "doi_ten")),
      hanhDong("nhan_ban", () => wsBatSua(w, "nhan_ban")),
      hanhDong("luu_mau", () => wsBatSua(w, "luu_mau")),
      hanhDong("xuat", () => wsXuat(w)),
      nutXoa)));
}

function wsBatSua(w, kieu) {
  wsSuaDong = wsSuaDong && wsSuaDong.slug === w.slug && wsSuaDong.kieu === kieu
    ? null : { slug: w.slug, kieu };
  wsVeDanhSach();
  const o = document.querySelector("#wsBang .ws-sua-ten");
  if (o) { o.focus(); o.select(); }
}

/* Dòng sửa nhanh mở ngay dưới workspace: đổi tên / nhân bản / lưu thành mẫu. */
function wsDongSua(w) {
  const kieu = wsSuaDong.kieu;
  const macDinh = kieu === "nhan_ban" ? t("ws_nhan_ban_ten_mac_dinh", { ten: w.name }) : w.name;
  const o = wsEl("input", { type: "text", class: "text-input ws-sua-ten", value: macDinh,
    "aria-label": t(kieu === "luu_mau" ? "ws_ten_mau" : "ws_ten_moi") });
  const kem = kieu === "nhan_ban"
    ? wsEl("label", { class: "ws-kem" },
        wsEl("input", { type: "checkbox", id: "wsKemDuLieu", checked: true }),
        " ", t("ws_nhan_ban_kem"))
    : null;
  const luu = wsEl("button", { type: "button", class: "btn btn-primary btn-nho", id: "wsBtnLuuSua",
    text: t("ws_btn_luu") });
  const lam = () => khiBan(luu, () => wsLuuSua(w, kieu, o.value.trim(),
    kem ? el("wsKemDuLieu").checked : true));
  luu.addEventListener("click", lam);
  o.addEventListener("keydown", (ev) => { if (ev.key === "Enter") lam(); });
  return wsEl("tr", { class: "ws-dong-sua" },
    wsEl("td", { colspan: "4" }, wsEl("div", { class: "ws-sua-hop" },
      wsEl("span", { class: "ws-sua-nhan",
        text: t(kieu === "luu_mau" ? "ws_ten_mau" : "ws_ten_moi") }),
      o, kem, luu,
      wsEl("button", { type: "button", class: "btn btn-ghost btn-nho",
        text: t("btn_cancel"), onclick: () => { wsSuaDong = null; wsVeDanhSach(); } }))));
}

function wsLuuSua(w, kieu, ten, kemDuLieu) {
  if (!ten) { showToast(t("ws_v_ten"), "error"); return Promise.resolve(); }
  const goi = kieu === "doi_ten" ? callApi("rename_workspace", w.slug, ten)
    : kieu === "nhan_ban" ? callApi("duplicate_workspace", w.slug, ten, kemDuLieu)
    : callApi("save_as_template", w.slug, ten);
  return goi.then((res) => {
    if (!res.ok) { showErrorToast(res.errors); return; }
    showToast(t(kieu === "doi_ten" ? "ws_da_doi_ten" : kieu === "nhan_ban" ? "ws_da_nhan_ban"
      : "ws_da_luu_mau", { ten }), "success");
    wsSuaDong = null;
    if (kieu === "doi_ten" && wsTrangThai && wsTrangThai.slug === w.slug) {
      wsTrangThai.name = ten;
      wsVeTenHienTai();
      wsCapNhatTieuDe();
    }
    return wsLamMoiDanhSach();
  });
}

/* ------------------------------------------------------------------ *
 * HÀNH ĐỘNG TRÊN MỘT WORKSPACE
 * ------------------------------------------------------------------ */

/* Chuyển workspace: thẻ 03 còn thay đổi chưa lưu thì bấm hai lần mới đi
   (cùng luật với đổi thẻ — xem roiDiNeuDuoc). */
function wsMo(w) {
  const di = () => callApi("open_workspace", w.slug).then((res) => {
    if (!res.ok) { showErrorToast(res.errors); return; }
    showToast(t("ws_da_mo", { ten: res.data.name || w.slug }), "success");
    wsTaiLaiTrang();
  });
  if (currentTabName() === "fallback" && typeof roiDiNeuDuoc === "function") {
    roiDiNeuDuoc(di, "ws:" + w.slug);
  } else {
    di();
  }
}

function wsXoa(w) {
  callApi("delete_workspace", w.slug, "XOA").then((res) => {
    if (!res.ok) { showErrorToast(res.errors); return; }
    showToast(t("ws_da_xoa", { ten: w.name }), "success");
    wsLamMoiDanhSach();
  });
}

function wsXuat(w) {
  callApi("export_workspace", w.slug).then((res) => {
    if (!res.ok) { showErrorToast(res.errors); return; }
    showToast(t("ws_da_xuat", { path: res.data.path }), "success");
    callApi("mo_thu_muc", res.data.path);
  });
}

function wsNhapZip(oFile) {
  const file = oFile.files && oFile.files[0];
  oFile.value = "";
  if (!file) return;
  if (!/\.zip$/i.test(file.name)) { showToast(t("ws_chi_nhan_zip"), "error"); return; }
  const reader = new FileReader();
  reader.onload = () => {
    callApi("import_workspace", bufferSangBase64(reader.result), file.name).then((res) => {
      if (!res.ok) { showErrorToast(res.errors); return; }
      showToast(t("ws_da_nhap", { ten: res.data.name }), "success");
      wsLamMoiDanhSach();
    });
  };
  reader.onerror = () => showToast(String(reader.error || ""), "error");
  reader.readAsArrayBuffer(file);
}

/* ------------------------------------------------------------------ *
 * TRÌNH HƯỚNG DẪN TẠO WORKSPACE (4 bước)
 * ------------------------------------------------------------------ */

/* Điền sẵn MỌI bước từ một mẫu (giữ nguyên tên người dùng đã gõ). */
function wsWizardTuMau(mau, ten, buoc) {
  const c = mau.config;
  const labels = {};
  WS_DANH_TU.forEach((dt) => { labels[dt] = { vi: c.labels[dt].vi, en: c.labels[dt].en }; });
  return {
    buoc: buoc || 1,
    ten: ten || "",
    nganh: c.industry,
    mau: mau.slug,
    labels,
    maxChoices: String(c.rules.max_choices),
    maxTests: c.rules.max_tests === null ? "" : String(c.rules.max_tests),
    khongGioiHan: c.rules.max_tests === null,
    priority: c.rules.priority,
    tierMode: c.rules.tier_mode,
    scoreScope: c.rules.score_scope,
    wharton: c.rules.wharton === true,
    tiersText: (c.rules.tiers || []).join("\n"),
  };
}

function wsBatDauWizard() {
  const mau = wsMau.find((m) => m.builtin) || wsMau[0];
  if (!mau) return;
  wsWizard = wsWizardTuMau(mau, "", 1);
  wsVeWizard();
}

/* Gom các ô của bước đang mở vào trạng thái (gọi trước khi đổi bước). */
function wsGomBuoc() {
  const w = wsWizard;
  const lay = (id) => { const o = el(id); return o ? o : null; };
  if (w.buoc === 1) {
    w.ten = lay("wzTen").value;
    w.nganh = lay("wzNganh").value;
  } else if (w.buoc === 2) {
    document.querySelectorAll("#wsHop .wz-nhan").forEach((o) => {
      w.labels[o.dataset.noun][o.dataset.ngon] = o.value;
    });
  } else if (w.buoc === 3) {
    w.maxChoices = lay("wzMaxChoices").value;
    w.maxTests = lay("wzMaxTests").value;
    w.khongGioiHan = lay("wzKhongGioiHan").checked;
    w.priority = lay("wzPriority").value;
    w.tierMode = lay("wzTierMode").value;
    w.scoreScope = lay("wzScoreScope").value;
    w.wharton = lay("wzWharton").checked;
    w.tiersText = lay("wzTiers").value;
  }
}

/* Thứ tự nhóm có tác dụng khi nhóm xếp CỨNG: chế độ "nghiêm ngặt", HOẶC ưu tiên "chỉ theo
   nhóm" (thuật toán coi đó là xếp cứng bất kể chế độ nhóm — rbda_priority_pipeline.tham_so_luat).
   Chỉ xét chế độ mà bỏ qua ưu tiên thì "chỉ theo nhóm" + "suất dự trữ mềm" lặng lẽ mất danh
   sách nhóm, và mọi người ngang nhau, chỉ còn bốc thăm. */
function wsDungThuTuNhom(w) {
  return w.tierMode === "strict" || w.priority === "tier";
}

/* Điểm Wharton (mục A13) chỉ dùng được khi cách xếp ưu tiên CÓ điểm (không phải "chỉ theo
   nhóm") VÀ điểm tính riêng cho từng chỗ — cùng luật với cau_hinh_ws.py. */
function wsChoPhepWharton(w) {
  return w.priority !== "tier" && w.scoreScope === "per_slot";
}

function wsTiers(w) {
  return wsDungThuTuNhom(w)
    ? w.tiersText.split("\n").map((s) => s.trim()).filter(Boolean) : [];
}

/* Lỗi của MỘT bước ([] = hợp lệ). Cùng luật với cau_hinh_ws.py — backend vẫn
   kiểm lại, nhưng ở đây báo bằng tiếng người dùng, đúng ô sai. */
function wsLoiBuoc(w, buoc) {
  const loi = [];
  if (buoc === 1 && !w.ten.trim()) loi.push(t("ws_v_ten"));
  if (buoc === 2) {
    WS_DANH_TU.forEach((dt) => {
      if (!w.labels[dt].vi.trim()) loi.push(t("ws_v_vi", { muc: t("ws_dt_" + dt) }));
    });
  }
  if (buoc === 3) {
    const mc = Number(w.maxChoices);
    if (w.maxChoices.trim() === "" || !Number.isInteger(mc) || mc < 1 || mc > 20) {
      loi.push(t("ws_v_max_choices"));
    }
    if (!w.khongGioiHan) {
      const mt = Number(w.maxTests);
      if (w.maxTests.trim() === "" || !Number.isInteger(mt) || mt < 0 || mt > 20) {
        loi.push(t("ws_v_max_tests"));
      }
    }
    const tiers = wsTiers(w);
    if (new Set(tiers).size !== tiers.length) loi.push(t("ws_v_tiers"));
  }
  return loi;
}

function wsCfgTuWizard(w) {
  const labels = {};
  WS_DANH_TU.forEach((dt) => {
    labels[dt] = { vi: w.labels[dt].vi.trim(), en: w.labels[dt].en.trim() };
  });
  return {
    name: w.ten.trim(),
    industry: w.nganh,
    labels,
    rules: {
      max_choices: Number(w.maxChoices),
      max_tests: w.khongGioiHan ? null : Number(w.maxTests),
      priority: w.priority,
      tier_mode: w.tierMode,
      score_scope: w.scoreScope,
      wharton: w.wharton === true && wsChoPhepWharton(w),
      tiers: wsTiers(w),
    },
  };
}

function wsChuyenBuoc(moi) {
  wsGomBuoc();
  if (moi > wsWizard.buoc) {
    const loi = wsLoiBuoc(wsWizard, wsWizard.buoc);
    if (loi.length) { wsHienLoiBuoc(loi); return; }
  }
  wsWizard.buoc = moi;
  wsVeWizard();
}

function wsHienLoiBuoc(loi) {
  const o = el("wzLoi");
  clear(o);
  loi.forEach((cau) => o.append(wsEl("div", { text: cau })));
  o.hidden = false;
}

/* Ô nhập có nhãn: trả {nhan, o} để ghép vào lưới. */
function wsTruong(id, nhanKhoa, oNhap, goiY) {
  return wsEl("div", { class: "ws-truong" },
    wsEl("label", { for: id, class: "ws-truong-nhan", text: t(nhanKhoa) }),
    oNhap,
    goiY ? (goiY.nodeType ? goiY : wsEl("div", { class: "ws-truong-goi-y", text: goiY })) : null);
}

/* Gợi ý của một ô luật: MỘT dòng ngắn luôn hiện, câu giải thích dài nằm sau nút (i) (A13.4). */
function wsGoiYNgan(id, ngan, dai) {
  const ghiChu = wsEl("div", { class: "ws-truong-goi-y", id: id + "GhiChu", hidden: true, text: dai });
  const nutI = wsEl("button", { type: "button", class: "nut-i", id: id + "I", "aria-expanded": "false",
    "aria-controls": id + "GhiChu", "aria-label": t("wh_ql_giai_thich"), text: "i" });
  nutI.addEventListener("click", () => {
    ghiChu.hidden = !ghiChu.hidden;
    nutI.setAttribute("aria-expanded", ghiChu.hidden ? "false" : "true");
  });
  return wsEl("div", { class: "ws-goi-y-ngan" },
    wsEl("div", { class: "ws-truong-goi-y ws-goi-y-dong" }, ngan, " ", nutI), ghiChu);
}

function wsChon(id, giaTri, luaChon) {
  return wsEl("select", { id, class: "text-input" },
    luaChon.map(([v, nhan]) => wsEl("option", { value: v, text: nhan,
      selected: v === giaTri ? true : null })));
}

function wsVeWizard() {
  const w = wsWizard;
  const hop = el("wsHop");
  clear(hop);
  const tenBuoc = t("ws_wz_b" + w.buoc);
  hop.append(
    wsEl("h2", { id: "wsTieuDe", class: "ws-tieu-de", tabindex: "-1", text: t("ws_wz_title") }),
    wsEl("ol", { class: "ws-buoc", "aria-label": t("ws_wz_buoc", { n: w.buoc, tong: WS_TONG_BUOC }) },
      [1, 2, 3, 4].map((n) => wsEl("li", {
        class: "ws-buoc-muc" + (n === w.buoc ? " is-hien-tai" : n < w.buoc ? " is-xong" : ""),
        "aria-current": n === w.buoc ? "step" : null,
        text: n + ". " + t("ws_wz_b" + n) }))),
    wsEl("p", { class: "ws-buoc-ten", text: t("ws_wz_buoc", { n: w.buoc, tong: WS_TONG_BUOC }) + " — " + tenBuoc }),
  );

  const noiDung = wsEl("div", { class: "ws-wz-noi-dung", id: "wzNoiDung" });
  if (w.buoc === 1) wsBuoc1(noiDung);
  else if (w.buoc === 2) wsBuoc2(noiDung);
  else if (w.buoc === 3) wsBuoc3(noiDung);
  else wsBuoc4(noiDung);
  hop.append(noiDung, wsEl("div", { class: "ws-loi", id: "wzLoi", role: "alert", hidden: true }));

  hop.append(wsEl("div", { class: "ws-chan" },
    w.buoc > 1 ? wsEl("button", { type: "button", class: "btn btn-secondary", id: "wzLui",
      text: t("ws_btn_quay_lai"), onclick: () => wsChuyenBuoc(w.buoc - 1) }) : null,
    w.buoc < WS_TONG_BUOC ? wsEl("button", { type: "button", class: "btn btn-primary", id: "wzTiep",
      text: t("ws_btn_tiep"), onclick: () => wsChuyenBuoc(w.buoc + 1) })
      : wsEl("button", { type: "button", class: "btn btn-primary", id: "wzTao",
          text: t("ws_btn_tao"), onclick: (ev) => khiBan(ev.currentTarget, wsTaoWorkspace) }),
    wsEl("button", { type: "button", class: "btn btn-ghost ws-dong", id: "wzHuy",
      text: t("btn_cancel"), onclick: () => { wsWizard = null; wsVeDanhSach(); } })));
  const tieuDe = el("wsTieuDe");
  if (tieuDe) tieuDe.focus();
}

/* --- Bước 1: tên, loại, mẫu --- */
function wsBuoc1(hop) {
  const w = wsWizard;
  const oMau = wsChon("wzMau", w.mau, wsMau.map((m) => [m.slug, wsTenMau(m)]));
  hop.append(
    wsTruong("wzTen", "ws_wz_ten", wsEl("input", { type: "text", id: "wzTen", class: "text-input",
      value: w.ten, placeholder: t("ws_wz_ten_ph"), maxlength: "80" })),
    wsTruong("wzNganh", "ws_wz_loai", wsChon("wzNganh", w.nganh,
      WS_NGANH.map((n) => [n, wsTenNganh(n)]))),
    wsTruong("wzMau", "ws_wz_mau", oMau, t("ws_wz_mau_hint")),
  );
  /* Chọn mẫu = điền lại CẢ BỐN BƯỚC; chỉ tên đang gõ được giữ. */
  oMau.addEventListener("change", (ev) => {
    wsGomBuoc();
    const mau = wsMau.find((m) => m.slug === ev.target.value);
    if (mau) wsWizard = wsWizardTuMau(mau, wsWizard.ten, 1);
    wsVeWizard();
  });
}

/* --- Bước 2: năm danh từ --- */
function wsBuoc2(hop) {
  const w = wsWizard;
  hop.append(wsEl("p", { class: "hint-text", text: t("ws_wz_tu_vung_hint") }));
  const luoi = wsEl("div", { class: "ws-luoi-tu-vung" },
    wsEl("div", { class: "ws-luoi-dau" }),
    wsEl("div", { class: "ws-luoi-dau", text: t("ws_wz_vi") }),
    wsEl("div", { class: "ws-luoi-dau", text: t("ws_wz_en") }));
  WS_DANH_TU.forEach((dt) => {
    luoi.append(
      wsEl("div", { class: "ws-dt" },
        wsEl("div", { class: "ws-dt-ten", text: t("ws_dt_" + dt) }),
        wsEl("div", { class: "ws-dt-mo-ta", text: t("ws_dt_" + dt + "_mo_ta") })),
      wsEl("input", { type: "text", class: "text-input wz-nhan", "data-noun": dt, "data-ngon": "vi",
        id: "wzNhan_" + dt + "_vi", value: w.labels[dt].vi, maxlength: "40",
        "aria-label": t("ws_dt_" + dt) + " — " + t("ws_wz_vi") }),
      wsEl("input", { type: "text", class: "text-input wz-nhan", "data-noun": dt, "data-ngon": "en",
        id: "wzNhan_" + dt + "_en", value: w.labels[dt].en, maxlength: "40",
        placeholder: t("ws_wz_en_ph"),
        "aria-label": t("ws_dt_" + dt) + " — " + t("ws_wz_en") }));
  });
  hop.append(luoi);
}

/* --- Bước 3: luật --- */
function wsBuoc3(hop) {
  const w = wsWizard;
  const oMaxTests = wsEl("input", { type: "number", id: "wzMaxTests", class: "text-input ws-so",
    min: "0", max: "20", step: "1", value: w.maxTests, disabled: w.khongGioiHan });
  const oKhong = wsEl("input", { type: "checkbox", id: "wzKhongGioiHan", checked: w.khongGioiHan,
    onchange: (ev) => { oMaxTests.disabled = ev.target.checked; } });
  const oTiers = wsEl("textarea", { id: "wzTiers", class: "text-input ws-tiers", rows: "4",
    value: w.tiersText, disabled: !wsDungThuTuNhom(w), placeholder: t("ws_r_tiers_ph") });
  const oTierMode = wsChon("wzTierMode", w.tierMode, [
    ["reserve", t("ws_r_tm_reserve")], ["strict", t("ws_r_tm_strict")]]);
  const oPriority = wsChon("wzPriority", w.priority, [
    ["score", t("ws_r_priority_score")], ["tier", t("ws_r_priority_tier")],
    ["score+tier", t("ws_r_priority_both")]]);
  const oScope = wsChon("wzScoreScope", w.scoreScope, [
    ["per_slot", t("ws_r_ss_per_slot")], ["per_person", t("ws_r_ss_per_person")]]);
  /* Điểm Wharton: khoá — và tự bỏ chọn — khi tổ hợp không dùng được, để không lưu một cấu
     hình mà backend sẽ từ chối. Không tự bật lại khi tổ hợp dùng được trở lại. */
  const oWharton = wsEl("input", { type: "checkbox", id: "wzWharton", checked: w.wharton === true,
    disabled: !wsChoPhepWharton(w) });
  const capNhatOWharton = () => {
    const cho = wsChoPhepWharton({ priority: oPriority.value, scoreScope: oScope.value });
    oWharton.disabled = !cho;
    if (!cho) oWharton.checked = false;
  };
  const capNhatODanhSachNhom = () => {
    oTiers.disabled = !(oTierMode.value === "strict" || oPriority.value === "tier");
  };
  oTierMode.addEventListener("change", capNhatODanhSachNhom);
  oPriority.addEventListener("change", capNhatODanhSachNhom);
  oPriority.addEventListener("change", capNhatOWharton);
  oScope.addEventListener("change", capNhatOWharton);

  hop.append(
    wsTruong("wzMaxChoices", "ws_r_max_choices", wsEl("input", { type: "number", id: "wzMaxChoices",
      class: "text-input ws-so", min: "1", max: "20", step: "1", value: w.maxChoices })),
    wsTruong("wzMaxTests", "ws_r_max_tests", wsEl("div", { class: "ws-hang" }, oMaxTests,
      wsEl("label", { class: "ws-kem" }, oKhong, " ", t("ws_r_khong_gioi_han")))),
    wsTruong("wzPriority", "ws_r_priority", oPriority),
    wsTruong("wzTierMode", "ws_r_tier_mode", oTierMode),
    wsTruong("wzScoreScope", "ws_r_score_scope", oScope),
    wsTruong("wzWharton", "ws_r_wharton", oWharton, wsGoiYNgan(
      "wzWharton", t("ws_r_wharton_ngan"), t("ws_r_wharton_ghi_chu"))),
    wsTruong("wzTiers", "ws_r_tiers", oTiers, t("ws_r_tiers_chi_strict")),
  );
}

/* --- Bước 4: xem lại --- */
function wsBuoc4(hop) {
  const cfg = wsCfgTuWizard(wsWizard);
  const r = cfg.rules;
  const hang = (nhan, giaTri, id) => wsEl("tr", null,
    wsEl("th", { scope: "row", text: nhan }), wsEl("td", { id, text: giaTri }));
  const nhanHienThi = (dt) => cfg.labels[dt].vi + " / " + (cfg.labels[dt].en || cfg.labels[dt].vi);
  const dong = [
    hang(t("ws_wz_ten"), cfg.name, "rvTen"),
    hang(t("ws_wz_loai"), wsTenNganh(cfg.industry), "rvLoai"),
    ...WS_DANH_TU.map((dt) => hang(t("ws_dt_" + dt), nhanHienThi(dt), "rvNhan_" + dt)),
    hang(t("ws_r_max_choices"), String(r.max_choices), "rvMaxChoices"),
    hang(t("ws_r_max_tests"), r.max_tests === null ? t("ws_r_khong_gioi_han") : String(r.max_tests), "rvMaxTests"),
    hang(t("ws_r_priority"), t({ score: "ws_r_priority_score", tier: "ws_r_priority_tier",
      "score+tier": "ws_r_priority_both" }[r.priority]), "rvPriority"),
    hang(t("ws_r_tier_mode"), t(r.tier_mode === "strict" ? "ws_r_tm_strict" : "ws_r_tm_reserve"), "rvTierMode"),
    hang(t("ws_r_score_scope"), t(r.score_scope === "per_person" ? "ws_r_ss_per_person" : "ws_r_ss_per_slot"), "rvScoreScope"),
    hang(t("ws_r_wharton"), t(r.wharton ? "ws_r_wharton_bat" : "ws_r_wharton_tat"), "rvWharton"),
    hang(t("ws_r_tiers"), r.tiers.length ? r.tiers.join(" › ") : "—", "rvTiers"),
  ];
  hop.append(
    wsEl("p", { class: "hint-text", text: t("ws_wz_xem_lai_hint") }),
    wsEl("table", { class: "data-table ws-xem-lai" }, wsEl("tbody", null, dong)));
  /* Chỉ "nhóm trước, rồi đến điểm" mà để suất dự trữ mềm mới bỏ thứ tự nhóm; "chỉ theo
     nhóm" luôn xếp cứng nên dùng danh sách nhóm. */
  if (r.priority === "score+tier" && r.tier_mode !== "strict") {
    hop.append(wsEl("p", { class: "ws-canh-bao", text: t("ws_r_canh_bao_nhom") }));
  }
}

function wsTaoWorkspace() {
  wsGomBuoc();
  /* Soát lại cả ba bước: quay lại sửa rồi nhảy thẳng tới cuối vẫn lọt được. */
  for (let b = 1; b <= 3; b++) {
    const loi = wsLoiBuoc(wsWizard, b);
    if (loi.length) {
      wsWizard.buoc = b;
      wsVeWizard();
      wsHienLoiBuoc(loi);
      return Promise.resolve();
    }
  }
  const cfg = wsCfgTuWizard(wsWizard);
  return callApi("create_workspace", cfg.name, cfg).then((res) => {
    if (!res.ok) { showErrorToast(res.errors); return; }
    showToast(t("ws_da_tao", { ten: cfg.name }), "success");
    return callApi("open_workspace", res.data.slug).then((mo) => {
      if (!mo.ok) { showErrorToast(mo.errors); return; }
      wsTaiLaiTrang();
    });
  });
}
