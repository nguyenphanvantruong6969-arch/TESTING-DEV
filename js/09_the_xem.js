/* js/09_the_xem.js — Hai thẻ XEM chỉ đọc (A14): 06 "Thành viên CLB" và 07 "Theo lớp".

   Chỉ kết quả xếp: KHÔNG điểm thi, điểm quyết tâm, số bốc thăm hay diện trúng tuyển. 06 cho người
   phụ trách một CLB (ai ở trong CLB); 07 cho giáo viên chủ nhiệm (từng em của lớp được xếp vào CLB
   nào, mỗi buổi một cột, theo thứ tự NGÀY do backend sắp). Một phần của giao diện chính: script
   thường, dùng chung phạm vi với các tệp js/ khác.
*/
"use strict";

const THE_XEM_CHUA_CHON = "";          // ô chọn CLB: giá trị của dòng nhắc "— Chọn … —"
const THE_XEM_LOP_CHUA_CHON = "__chua_chon__";   // ô chọn lớp ("" là lớp thật: Chưa có lớp)

/* Nội dung rỗng + lý do: hiện dòng chữ, ẩn bảng. */
function theXemBaoRong(oRong, oBang, khoaChu) {
  oRong.textContent = t(khoaChu);
  oRong.hidden = false;
  oBang.hidden = true;
}

function theXemCoKetQua() {
  return callApi("get_trang_thai_ket_qua").then((res) => !!(res.ok && res.data.co_ket_qua));
}

/* ------------------------------------------------------------------ *
 * THẺ 06 — THÀNH VIÊN CLB
 * ------------------------------------------------------------------ */

/* Buổi giữ thứ tự backend (đã theo ngày); trong một buổi sắp theo tên. */
function theXemSapClb(ds) {
  const nhom = new Map();
  ds.forEach((c) => {
    if (!nhom.has(c.buoi)) nhom.set(c.buoi, []);
    nhom.get(c.buoi).push(c);
  });
  const ra = [];
  nhom.forEach((cacClb) => {
    cacClb.sort((a, b) => String(a.name || a.club_id).localeCompare(String(b.name || b.club_id), "vi"));
    ra.push(...cacClb);
  });
  return ra;
}

function loadMembersTab() {
  Promise.all([theXemCoKetQua(), callApi("get_club_fill_stats")]).then(([coKq, clbRes]) => {
    const sel = el("membersClub");
    const giu = sel.value;
    clear(sel);
    themOption(sel, THE_XEM_CHUA_CHON, t("members_chua_chon"));
    const ds = clbRes.ok ? theXemSapClb(clbRes.data) : [];
    const nhieuBuoi = new Set(ds.map((c) => c.buoi)).size > 1;
    ds.forEach((c) => {
      const ten = c.name || c.club_id;
      themOption(sel, c.club_id, nhieuBuoi ? nhanBuoi(c.buoi) + " · " + ten : ten);
    });
    sel.value = Array.from(sel.options).some((o) => o.value === giu) ? giu : THE_XEM_CHUA_CHON;
    sel.disabled = !coKq;
    if (!coKq) { theXemBaoRong(el("membersEmpty"), el("membersTable"), "the_xem_chua_co_ket_qua"); return; }
    el("membersEmpty").hidden = true;
    veMembers();
  });
}

function veMembers() {
  const clubId = el("membersClub").value;
  const bang = el("membersTable");
  if (!clubId) { bang.hidden = true; return Promise.resolve(); }
  return callApiMoiNhat("the_xem_clb", "get_danh_sach_clb", clubId).then((res) => {
    if (!res.ok) { bang.hidden = true; showErrorToast(res.errors); return; }
    const d = res.data;
    const body = el("membersTableBody");
    clear(body);
    el("membersDem").textContent = t("members_dem", { x: d.thanh_vien.length, y: d.capacity });
    d.thanh_vien.forEach((m, i) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td class="num">${i + 1}</td><td>${esc(m.student_id)}</td>` +
        `<td>${esc(m.name || "")}</td><td>${esc(m.class_id || "")}</td>`;
      body.appendChild(tr);
    });
    if (!d.thanh_vien.length) {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td colspan="4" class="o-trong">${esc(t("members_rong"))}</td>`;
      body.appendChild(tr);
    }
    bang.hidden = false;
  });
}

/* ------------------------------------------------------------------ *
 * THẺ 07 — THEO LỚP
 * ------------------------------------------------------------------ */

function loadTheoLopTab() {
  Promise.all([theXemCoKetQua(), layDsLop()]).then(([coKq, d]) => {
    const sel = el("theoLopChon");
    const giu = sel.value;
    clear(sel);
    themOption(sel, THE_XEM_LOP_CHUA_CHON, t("theolop_chua_chon"));
    d.classes.forEach((c) => themOption(sel, c.class_id, c.class_id + " (" + c.n + ")"));
    if (d.n_khong_lop) themOption(sel, "", t("lop_chua_co") + " (" + d.n_khong_lop + ")");
    sel.value = Array.from(sel.options).some((o) => o.value === giu) ? giu : THE_XEM_LOP_CHUA_CHON;
    sel.disabled = !coKq || !d.classes.length;
    if (!coKq) { theXemBaoRong(el("theoLopEmpty"), el("theoLopTable"), "the_xem_chua_co_ket_qua"); return; }
    if (!d.classes.length) { theXemBaoRong(el("theoLopEmpty"), el("theoLopTable"), "theolop_khong_co_lop"); return; }
    el("theoLopEmpty").hidden = true;
    veTheoLop();
  });
}

function veTheoLop() {
  const lop = el("theoLopChon").value;
  const bang = el("theoLopTable");
  if (lop === THE_XEM_LOP_CHUA_CHON) { bang.hidden = true; return Promise.resolve(); }
  return callApiMoiNhat("the_xem_lop", "get_thoi_khoa_bieu", "", lop).then((res) => {
    if (!res.ok) { bang.hidden = true; showErrorToast(res.errors); return; }
    const dsBuoi = res.data.ds_buoi;
    const nhieuBuoi = dsBuoi.length > 1;
    const cot = ["th_stt", "th_student_id", "th_name"].map((k) => t(k))
      .concat(nhieuBuoi ? dsBuoi.map(nhanBuoi) : [t("th_club")]);
    el("theoLopHead").innerHTML = cot.map((c) => `<th>${esc(c)}</th>`).join("");
    const body = el("theoLopBody");
    clear(body);
    let chuaCo = 0;
    res.data.hoc_sinh.forEach((e, i) => {
      const tr = document.createElement("tr");
      if (!e.so_clb) { tr.className = "dong-do"; chuaCo++; }
      const o = (dsBuoi.length ? dsBuoi : []).map((b) => {
        const x = e.theo_buoi[b];
        const ten = x && x.club_id ? (x.club_name || x.club_id) : "";
        return ten ? `<td>${esc(ten)}</td>` : `<td class="o-trong">${esc(t("theolop_o_trong"))}</td>`;
      });
      tr.innerHTML = `<td class="num">${i + 1}</td><td>${esc(e.student_id)}</td><td>${esc(e.name || "")}</td>` +
        o.join("");
      body.appendChild(tr);
    });
    el("theoLopDem").textContent = t("theolop_dem", { n: res.data.hoc_sinh.length, m: chuaCo });
    bang.hidden = false;
  });
}

function initTheXemHandlers() {
  el("membersClub").addEventListener("change", veMembers);
  el("theoLopChon").addEventListener("change", veTheoLop);
}
