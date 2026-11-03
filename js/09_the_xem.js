/* js/09_the_xem.js — Thẻ 02 "Kết quả": màn XEM chỉ đọc cho Ban giám hiệu, người phụ trách CLB và
   giáo viên chủ nhiệm (gộp thẻ Kết quả cũ, Thành viên CLB và Theo lớp).

   Chỉ kết quả xếp: KHÔNG điểm thi, điểm quyết tâm, số bốc thăm hay diện trúng tuyển. Ba cách xem
   (tầng 1): Theo lớp | Theo CLB | Theo mã học sinh. Tầng 2 là cách sắp hàng: Theo ngày trong
   tuần | Theo mã học sinh | Theo lớp (mục cuối CHỈ có khi tầng 1 = Theo mã học sinh). Lựa chọn
   hai tầng nhớ theo máy (localStorage). Dùng lại các API có sẵn: get_thoi_khoa_bieu,
   get_danh_sach_clb, get_club_fill_stats, list_classes. Một phần của giao diện chính: script
   thường, dùng chung phạm vi với các tệp js/ khác.
*/
"use strict";

const KHOA_KQ_XEM = "rbda_ket_qua_xem_v1";
const KQ_TANG1 = ["lop", "clb", "ma"];
const KQ_TANG2 = ["ngay", "ma", "lop"];
const KQ_KHONG_NGAY = 9999;          // hàng chưa có CLB nào: xếp sau mọi ngày

const kq = {
  tang1: "lop",
  tang2: "ngay",
  lop: null,           // lớp đang chọn ("" là lớp thật: Chưa có lớp); null = chưa chọn
  clb: "",             // mã CLB đang chọn
  coKq: false,
  nLop: 0,
  nClb: 0,
};

/* Nhớ lựa chọn hai tầng. Kho lưu trữ hỏng hay bị chặn thì dùng mặc định, KHÔNG làm hỏng thẻ. */
function docKqXem() {
  try {
    const raw = window.localStorage && window.localStorage.getItem(KHOA_KQ_XEM);
    if (!raw) return;
    const luu = JSON.parse(raw);
    if (luu && KQ_TANG1.includes(luu.tang1)) kq.tang1 = luu.tang1;
    if (luu && KQ_TANG2.includes(luu.tang2)) kq.tang2 = luu.tang2;
  } catch (e) { /* dùng mặc định */ }
}

function luuKqXem() {
  try {
    if (window.localStorage) {
      window.localStorage.setItem(KHOA_KQ_XEM, JSON.stringify({ tang1: kq.tang1, tang2: kq.tang2 }));
    }
  } catch (e) { /* không ghi được thì thôi */ }
}

/* "Theo lớp" ở tầng 2 chỉ có nghĩa khi xem Theo mã học sinh; chỗ khác lùi về "ngày trong tuần". */
function kqTang2HieuLuc() {
  return kq.tang2 === "lop" && kq.tang1 !== "ma" ? "ngay" : kq.tang2;
}

/* ---- Sắp hàng (tầng 2) ---- */

function kqSoMa(a, b) {
  return String(a.student_id).localeCompare(String(b.student_id), undefined,
    { numeric: true, sensitivity: "base" }) || (a.student_id < b.student_id ? -1 : a.student_id > b.student_id ? 1 : 0);
}

/* `dsLopHienCo` (js/04) giữ thứ tự tự nhiên của backend (10H2 trước 10H10); lớp trống xếp cuối. */
function kqHangLop(lop) {
  const i = lop ? dsLopHienCo.indexOf(lop) : -1;
  return i < 0 ? KQ_KHONG_NGAY : i;
}

function kqSapHang(hang, kieu) {
  const so = kieu === "lop" ? (a, b) => kqHangLop(a.class_id) - kqHangLop(b.class_id) || kqSoMa(a, b)
    : kieu === "ngay" ? (a, b) => a.ngay - b.ngay || kqSoMa(a, b)
      : kqSoMa;
  return hang.slice().sort(so);
}

/* ---- Khung chung ---- */

function kqBaoRong(khoaChu, thamSo) {
  el("kqRong").textContent = t(khoaChu, thamSo);
  el("kqRong").hidden = false;
  el("kqBang").hidden = true;
}

function kqDongBoDieuKhien() {
  const tang2 = kqTang2HieuLuc();
  document.querySelectorAll("#kqTang1 .kq-seg-nut").forEach((n) => {
    const on = n.dataset.kq === kq.tang1;
    n.classList.toggle("is-on", on);
    n.setAttribute("aria-pressed", on ? "true" : "false");
  });
  document.querySelectorAll("#kqTang2 .kq-seg-nut").forEach((n) => {
    const on = n.dataset.sx === tang2;
    n.classList.toggle("is-on", on);
    n.setAttribute("aria-pressed", on ? "true" : "false");
  });
  el("kqSxLop").hidden = kq.tang1 !== "ma";
  el("kqChonLopHang").hidden = kq.tang1 !== "lop";
  el("kqChonClbHang").hidden = kq.tang1 !== "clb";
  el("kqTimHang").hidden = kq.tang1 !== "ma";
}

function kqNapOLop(d) {
  const sel = el("kqChonLop");
  clear(sel);
  d.classes.forEach((c) => themOption(sel, c.class_id, c.class_id + " (" + c.n + ")"));
  if (d.n_khong_lop) themOption(sel, "", t("lop_chua_co") + " (" + d.n_khong_lop + ")");
  const co = (v) => Array.from(sel.options).some((o) => o.value === v);
  if (kq.lop === null || !co(kq.lop)) kq.lop = sel.options.length ? sel.options[0].value : null;
  if (kq.lop !== null) sel.value = kq.lop;
  sel.disabled = !d.classes.length;
}

/* Buổi giữ thứ tự backend (đã theo ngày trong tuần); trong một buổi sắp theo tên. */
function kqSapClb(ds) {
  const nhom = new Map();
  ds.forEach((c) => {
    if (!nhom.has(c.buoi)) nhom.set(c.buoi, []);
    nhom.get(c.buoi).push(c);
  });
  const ra = [];
  nhom.forEach((cac) => {
    cac.sort((a, b) => String(a.name || a.club_id).localeCompare(String(b.name || b.club_id), "vi"));
    ra.push(...cac);
  });
  return ra;
}

function kqNapOClb(ds) {
  const sel = el("kqChonClb");
  clear(sel);
  const nhieuBuoi = new Set(ds.map((c) => c.buoi)).size > 1;
  ds.forEach((c) => {
    const ten = c.name || c.club_id;
    themOption(sel, c.club_id, nhieuBuoi ? nhanBuoi(c.buoi) + " · " + ten : ten);
  });
  const co = (v) => Array.from(sel.options).some((o) => o.value === v);
  if (!co(kq.clb)) kq.clb = sel.options.length ? sel.options[0].value : "";
  sel.value = kq.clb;
  sel.disabled = !ds.length;
}

function loadKetQuaTab() {
  Promise.all([callApi("get_trang_thai_ket_qua"), layDsLop(), callApi("get_club_fill_stats")])
    .then(([tt, dsLop, clbRes]) => {
      kq.coKq = !!(tt.ok && tt.data.co_ket_qua);
      el("kqCuBanner").hidden = !(tt.ok && tt.data.ket_qua_cu);
      const dsClb = clbRes.ok ? kqSapClb(clbRes.data) : [];
      kq.nLop = dsLop.classes.length;
      kq.nClb = dsClb.length;
      kqNapOLop(dsLop);
      kqNapOClb(dsClb);
      veKetQua();
    });
}

function veKetQua() {
  kqDongBoDieuKhien();
  el("kqRong").hidden = true;
  if (!kq.coKq) { kqBaoRong("the_xem_chua_co_ket_qua"); return Promise.resolve(); }
  if (kq.tang1 === "lop") return veKqTheoLop();
  if (kq.tang1 === "clb") return veKqTheoClb();
  return veKqTheoMa();
}

/* ---- Bảng ---- */

function kqVeBang(cot, hang, dem) {
  el("kqDau").innerHTML = cot.map((c) => `<th>${esc(c)}</th>`).join("");
  const than = el("kqThan");
  clear(than);
  const manh = document.createDocumentFragment();
  hang.forEach((h, i) => {
    const tr = document.createElement("tr");
    if (h.chuaCo) tr.className = "dong-do";
    tr.innerHTML = `<td class="num">${i + 1}</td><td>${esc(h.student_id)}</td><td>${esc(h.name || "")}</td>` + h.o.join("");
    manh.appendChild(tr);
  });
  than.appendChild(manh);
  el("kqDem").textContent = dem;
  el("kqRong").hidden = true;
  el("kqBang").hidden = false;
}

/* Hàng thời khoá biểu của một em: `ngay` = vị trí buổi sớm nhất (theo ngày) mà em có CLB. */
function kqHangLich(em, dsBuoi, coLop) {
  let ngay = KQ_KHONG_NGAY;
  const oBuoi = dsBuoi.map((b, i) => {
    const x = em.theo_buoi[b];
    const ten = x && x.club_id ? (x.club_name || x.club_id) : "";
    if (ten && ngay === KQ_KHONG_NGAY) ngay = i;
    return ten ? `<td>${esc(ten)}</td>` : `<td class="o-trong">-</td>`;
  });
  return {
    student_id: em.student_id, name: em.name, class_id: em.class_id || "", ngay,
    chuaCo: !em.so_clb,
    o: (coLop ? [`<td>${esc(em.class_id || "")}</td>`] : []).concat(oBuoi),
  };
}

function kqCotLich(dsBuoi, coLop) {
  return [t("th_stt"), t("th_student_id"), t("th_name")]
    .concat(coLop ? [t("th_cohort")] : [])
    .concat(dsBuoi.length > 1 ? dsBuoi.map(nhanBuoi) : [t("th_club")]);
}

function veKqTheoLop() {
  if (!kq.nLop) {
    kqBaoRong("theolop_khong_co_lop", { the: t("nav_admin"), muc: t("ql_tab_hs") });
    return Promise.resolve();
  }
  if (kq.lop === null) { el("kqBang").hidden = true; return Promise.resolve(); }
  return callApiMoiNhat("kq", "get_thoi_khoa_bieu", "", kq.lop).then((res) => {
    if (!res.ok) { el("kqBang").hidden = true; showErrorToast(res.errors); return; }
    const dsBuoi = res.data.ds_buoi;
    const hang = kqSapHang(res.data.hoc_sinh.map((e) => kqHangLich(e, dsBuoi, false)), kqTang2HieuLuc());
    kqVeBang(kqCotLich(dsBuoi, false), hang,
      t("theolop_dem", { n: hang.length, m: hang.filter((h) => h.chuaCo).length }));
  });
}

function veKqTheoClb() {
  if (!kq.nClb) { kqBaoRong("kq_khong_co_clb"); return Promise.resolve(); }
  return callApiMoiNhat("kq", "get_danh_sach_clb", kq.clb).then((res) => {
    if (!res.ok) { el("kqBang").hidden = true; showErrorToast(res.errors); return; }
    const d = res.data;
    const hang = kqSapHang(d.thanh_vien.map((m) => ({
      student_id: m.student_id, name: m.name, class_id: m.class_id || "", ngay: 0, chuaCo: false,
      o: [`<td>${esc(m.class_id || "")}</td>`],
    })), kqTang2HieuLuc());
    if (!hang.length) { kqBaoRong("members_rong"); return; }
    kqVeBang([t("th_stt"), t("th_student_id"), t("th_name"), t("th_cohort")], hang,
      t("members_dem", { x: hang.length, y: d.capacity }));
  });
}

function veKqTheoMa() {
  const tim = (el("kqTimKiem").value || "").trim();
  return callApiMoiNhat("kq", "get_thoi_khoa_bieu", tim).then((res) => {
    if (!res.ok) { el("kqBang").hidden = true; showErrorToast(res.errors); return; }
    const dsBuoi = res.data.ds_buoi;
    const hang = kqSapHang(res.data.hoc_sinh.map((e) => kqHangLich(e, dsBuoi, true)), kqTang2HieuLuc());
    if (!hang.length) { kqBaoRong(tim ? "kq_tim_khong_thay" : "kq_khong_co_hs"); return; }
    kqVeBang(kqCotLich(dsBuoi, true), hang, t("kq_dem_ma", { n: hang.length }));
  });
}

function initKetQuaHandlers() {
  docKqXem();
  document.querySelectorAll("#kqTang1 .kq-seg-nut").forEach((n) => {
    n.addEventListener("click", () => { kq.tang1 = n.dataset.kq; luuKqXem(); veKetQua(); });
  });
  document.querySelectorAll("#kqTang2 .kq-seg-nut").forEach((n) => {
    n.addEventListener("click", () => { kq.tang2 = n.dataset.sx; luuKqXem(); veKetQua(); });
  });
  el("kqChonLop").addEventListener("change", (ev) => { kq.lop = ev.target.value; veKetQua(); });
  el("kqChonClb").addEventListener("change", (ev) => { kq.clb = ev.target.value; veKetQua(); });
  el("kqTimKiem").addEventListener("input", debounce(() => veKetQua(), 250));
  kqDongBoDieuKhien();
}
