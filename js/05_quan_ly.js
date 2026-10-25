/* js/05_quan_ly.js — Thẻ 04 — Quản lý CLB & dự trữ, cùng phần nhiều buổi dùng chung (chọn buổi,
   lịch tuần, bảng tải, thời khoá biểu, độ phủ).

   Một phần của giao diện chính, tách từ app.js cũ. Các tệp js/ là SCRIPT
   THƯỜNG (không phải ES module) nạp theo đúng thứ tự trong index.html và
   dùng chung một phạm vi — như một tệp duy nhất trước đây. Không dùng ES
   module vì mở trang bằng file:// thì trình duyệt chặn chúng.
*/
"use strict";

/* ------------------------------------------------------------------ *
 * 6. TAB 4 — QUẢN LÝ CLUB & DỰ TRỮ
 * ------------------------------------------------------------------ */

let adminStudentPage = 1;
const ADMIN_PAGE_SIZE = 50;

/* Da co ket qua chay chua — quyet dinh nhan xac nhan cua hai nut xoa
   noi ro "mat ca ket qua da chay" hay khong. Doc mot lan luc mo tab
   vi armTwoStepConfirm goi nhan dong bo, khong cho duoc promise. */
let adminCoKetQua = false;

/* ------------------------------------------------------------------ *
 * 8b. NHIỀU BUỔI SINH HOẠT TRONG TUẦN
 * ------------------------------------------------------------------ *
 * Toàn bộ phần này TỰ ẨN khi trường chưa khai buổi nào. Một trường chỉ
 * tổ chức một buổi phải thấy đúng màn hình như trước — không ai bị bắt
 * học một khái niệm mình chưa dùng tới.
 * ------------------------------------------------------------------ */

/* Giu dung con so phia Python (rbda_priority_pipeline.py). Hai noi cung
   mot tran, va test canh chung khop nhau. Day la tran MAC DINH cua truong hoc;
   workspace dat tran khac thi js/075_workspace.js ghi de luc khoi dong
   (rules.max_choices / rules.max_tests; max_tests null = khong gioi han = Infinity). */
let TRAN_NGUYEN_VONG_MOI_BUOI = 10;
let TRAN_CLB_THI_MOI_BUOI = 5;

/* Buoi cua mot CLB, tra tu danh sach da nap san — khong goi them API. */
/* Tra bang, khong quet mang: ham nay chay cho MOI o da tick o moi cu
   bam, nen `find` tren ca danh sach CLB thanh binh phuong. */
function clubBuoi(clubId) {
  return clubId in buoiCuaClb ? buoiCuaClb[clubId] : null;
}

function nhanBuoi(buoi) {
  if (!buoi || buoi === BUOI_MAC_DINH) return t("buoi_chua_chia");
  return buoi;
}

/* Ba mức tải, cùng ngưỡng dùng cho cả bảng lẫn lịch tuần.
   Mốc nằm ở 1,0 vì tỉ lệ chọi là SỐ EM trên SỐ CHỖ: trên 1 là chắc chắn
   có em trượt, dưới 1 là chắc chắn có chỗ bỏ không. Dải 0,95–1,05 gọi là
   "vừa đủ" để một buổi cân bằng không bị tô cảnh báo chỉ vì lệch vài em.

   Ngưỡng đầu tiên viết là 0,8 — sai: một buổi 0,88× (12% số chỗ bỏ
   trống) bị gán nhãn "Vừa đủ", đúng lúc nó là buổi nên dời CLB sang. */
function mucTai(tiLe) {
  if (tiLe === null || tiLe === undefined) return null;
  if (tiLe > 1.05) return { lop: "is-qua-tai", nhan: t("tai_buoi_qua_tai") };
  if (tiLe >= 0.95) return { lop: "is-vua-du", nhan: t("tai_buoi_vua_du") };
  return { lop: "is-con-trong", nhan: t("tai_buoi_con_trong") };
}

function loadBuoiOptions() {
  callApiDocChung("get_danh_sach_buoi").then((res) => {
    const list = el("buoiOptions");
    if (!list) return;
    clear(list);
    if (!res.ok) return;
    res.data.ds_buoi
      .filter((b) => b !== res.data.buoi_mac_dinh)
      .forEach((b) => {
        const opt = document.createElement("option");
        opt.value = b;
        list.appendChild(opt);
      });
  });
}

function loadTaiTheoBuoi() {
  const panel = el("taiBuoiPanel");
  if (!panel) return;
  callApiDocChung("get_tai_theo_buoi").then((res) => {
    const body = el("taiBuoiBody");
    clear(body);
    /* Một buổi thì bảng này không nói được gì: cả trường chỉ có một
       dòng, và "dời CLB sang buổi vắng" không còn là lời khuyên nào. */
    if (!res.ok || res.data.length < 2) {
      panel.hidden = true;
      return;
    }
    panel.hidden = false;
    res.data.forEach((r) => {
      const muc = mucTai(r.ti_le_choi);
      const tr = document.createElement("tr");
      tr.innerHTML =
        `<td>${esc(nhanBuoi(r.buoi))}</td>` +
        `<td class="num">${esc(r.so_clb)}</td>` +
        `<td class="num">${esc(r.tong_cho)}</td>` +
        `<td class="num">${esc(r.so_hoc_sinh)}</td>` +
        `<td class="num">${r.ti_le_choi === null ? "—" : esc(r.ti_le_choi) + "×"}</td>` +
        `<td>${muc ? `<span class="chip-tai ${muc.lop}">${esc(muc.nhan)}</span>` : ""}</td>`;
      body.appendChild(tr);
    });
  });
}

function loadLichTuan() {
  const panel = el("lichTuanPanel");
  if (!panel) return;
  Promise.all([
    callApiDocChung("get_tai_theo_buoi"),
    callApiDocChung("get_club_fill_stats"),
  ]).then(([tai, fill]) => {
    const box = el("lichTuan");
    clear(box);
    if (!tai.ok || tai.data.length < 2 || !fill.ok) {
      panel.hidden = true;
      return;
    }
    panel.hidden = false;

    const theoBuoi = {};
    fill.data.forEach((c) => {
      (theoBuoi[c.buoi] = theoBuoi[c.buoi] || []).push(c);
    });

    tai.data.forEach((b) => {
      const muc = mucTai(b.ti_le_choi);
      const cot = document.createElement("div");
      cot.className = "lich-cot";
      cot.innerHTML =
        `<div class="lich-dau ${muc && muc.lop === "is-qua-tai" ? "is-qua-tai" : ""}">` +
        `<span class="lich-buoi">${esc(nhanBuoi(b.buoi))}</span>` +
        `<span class="lich-phu">${esc(b.tong_cho)} · ${b.ti_le_choi === null ? "—" : esc(b.ti_le_choi) + "×"}</span>` +
        `</div>`;
      (theoBuoi[b.buoi] || []).forEach((c) => {
        const phanTram = c.capacity > 0
          ? Math.min(100, (c.matched / c.capacity) * 100)
          : 0;
        const o = document.createElement("div");
        o.className = "lich-o";
        o.innerHTML =
          `<span class="lich-ten">${esc(c.name || c.club_id)}</span>` +
          `<span class="lich-thanh"><span style="width:${phanTram}%"></span></span>`;
        o.title = `${c.matched}/${c.capacity}`;
        cot.appendChild(o);
      });
      box.appendChild(cot);
    });
  });
}

/* ---- Chọn buổi sẽ xếp (thẻ Vận hành) ----

   Hai cách chọn cho hai thói quen khác nhau, cùng sửa một tập:
     · bấm từng chip  -> chọn đúng một buổi, hoặc một tập rời rạc
     · Từ ... đến ... -> chọn một dải liên tiếp trong tuần

   Buổi không chọn GIỮ NGUYÊN kết quả lần xếp trước — đó là lý do tính
   năng này tồn tại, nên dòng nhắc phải nằm ngay đây chứ không nằm trong
   tài liệu. */

let dsBuoiCoThe = [];
let buoiDangChon = new Set();

/* `datLai: true` = chon lai TAT CA buoi (dung sau khi nhap tep). Mac
   dinh thi GIU lua chon cu neu danh sach buoi khong doi: truoc day moi
   lan quay lai the nay (vd. xem the Ket qua roi quay ve) lua chon bi dat
   lai thanh ca tuan, va bam Chay luc do se ghi de ca nhung buoi nguoi
   dung da co y giu nguyen. */
function loadChonBuoi({ datLai = false } = {}) {
  const box = el("chonBuoiBox");
  if (!box) return;
  callApiDocChung("get_danh_sach_buoi").then((res) => {
    /* Một buổi thì không có gì để chọn — bộ chọn chỉ làm rối một màn
       hình vốn đã chạy đúng. */
    if (!res.ok || !res.data.nhieu_buoi) {
      box.hidden = true;
      dsBuoiCoThe = [];
      buoiDangChon = new Set();
      return;
    }
    box.hidden = false;
    const dsMoi = res.data.ds_buoi;
    const giuLuaChon = !datLai
      && dsMoi.length === dsBuoiCoThe.length
      && dsMoi.every((b, i) => b === dsBuoiCoThe[i])
      && buoiDangChon.size > 0;
    dsBuoiCoThe = dsMoi;
    if (giuLuaChon) {
      // Danh sach khong doi: ve lai nhung giu nguyen lua chon va hai o dai.
      veLaiDaiGiuGiaTri();
      veChonBuoi();
      return;
    }
    /* Mặc định chọn HẾT: bấm Chạy mà không để ý bộ chọn thì phải ra
       đúng hành vi cũ. Mặc định chọn một buổi là lặng lẽ đổi nghĩa của
       nút Chạy. Danh sách buổi vừa đổi thì đây cũng là hướng an toàn. */
    buoiDangChon = new Set(dsBuoiCoThe);
    veChonBuoiDai();
    /* Hai o "Tu/Den" vua duoc dung lai nen deu dang o buoi DAU TIEN, trong
       khi moi the deu bat. Bo chon noi hai dieu khac nhau ve cung mot thu,
       va o dieu sai lai hep hon dieu dung. */
    dongBoDaiVoiChip();
    veChonBuoi();
  });
}

/* Dung lai hai o "Tu/Den" ma KHONG doi gia tri dang chon: veChonBuoiDai()
   goi clear() nen phai chup truoc va tra lai sau. */
function veLaiDaiGiuGiaTri() {
  const oTu = el("chonBuoiTu");
  const oDen = el("chonBuoiDen");
  const giuTu = oTu && oTu.value;
  const giuDen = oDen && oDen.value;
  veChonBuoiDai();
  if (oTu && giuTu) oTu.value = giuTu;
  if (oDen && giuDen) oDen.value = giuDen;
}

function veChonBuoiDai() {
  ["chonBuoiTu", "chonBuoiDen"].forEach((id) => {
    const sel = el(id);
    if (!sel) return;
    clear(sel);
    dsBuoiCoThe.forEach((b) => {
      const o = document.createElement("option");
      o.value = b;
      o.textContent = nhanBuoi(b);
      sel.appendChild(o);
    });
  });
}

/* Doi lua chon buoi khi thanh xac nhan dang treo thi cau hua tren thanh
   do khong con dung nua. Go no di, buoc nguoi dung bam Chay lai va doc
   lai cau hua moi — re hon nhieu so voi de ho xac nhan mot pham vi khac
   voi pham vi se chay. */
function goThanhXacNhanNeuCo() {
  const thanh = el("runConfirmBar");
  if (thanh) {
    thanh.remove();
    datVeLai(false);
    capNhatKhoaVanHanh(); // thanh xac nhan dong -> nut Chay mo lai
  }
}

function veChonBuoi() {
  const box = el("chonBuoiChip");
  if (!box) return;
  clear(box);
  dsBuoiCoThe.forEach((b) => {
    const nut = document.createElement("button");
    nut.type = "button";
    nut.className = "buoi-chip" + (buoiDangChon.has(b) ? " is-chon" : "");
    nut.textContent = nhanBuoi(b);
    nut.setAttribute("aria-pressed", buoiDangChon.has(b) ? "true" : "false");
    nut.addEventListener("click", () => {
      if (buoiDangChon.has(b)) buoiDangChon.delete(b);
      else buoiDangChon.add(b);
      goThanhXacNhanNeuCo();
      dongBoDaiVoiChip();
      veChonBuoi();
    });
    box.appendChild(nut);
  });
  capNhatKhoaVanHanh(); // the vua dung lai: ap dung trang thai khoa

  /* Nhắc đúng tình huống đang xảy ra, không nhắc chung chung. Chọn hết
     thì không có buổi nào bị giữ lại, nói câu đó là thừa và gây phân vân. */
  const nhac = el("chonBuoiNhac");
  if (nhac) {
    const duoc = dsBuoiCoThe.filter((b) => !buoiDangChon.has(b));
    nhac.textContent = duoc.length
      ? t("chon_buoi_nhac_giu").replace("{buoi}", duoc.map(nhanBuoi).join(", "))
      : t("chon_buoi_nhac_het");
  }
}

function dongBoDaiVoiChip() {
  /* Dải chỉ có nghĩa khi tập đang chọn là một đoạn LIỀN NHAU. Rời rạc
     thì để nguyên hai ô, đừng ép nó nói một điều không đúng. */
  const chon = dsBuoiCoThe.filter((b) => buoiDangChon.has(b));
  if (!chon.length) return;
  const dau = dsBuoiCoThe.indexOf(chon[0]);
  const cuoi = dsBuoiCoThe.indexOf(chon[chon.length - 1]);
  if (cuoi - dau + 1 !== chon.length) return;
  if (el("chonBuoiTu")) el("chonBuoiTu").value = chon[0];
  if (el("chonBuoiDen")) el("chonBuoiDen").value = chon[chon.length - 1];
}

function apDungDaiBuoi() {
  const tu = dsBuoiCoThe.indexOf(el("chonBuoiTu").value);
  const den = dsBuoiCoThe.indexOf(el("chonBuoiDen").value);
  if (tu < 0 || den < 0) return;
  const [a, b] = tu <= den ? [tu, den] : [den, tu];
  buoiDangChon = new Set(dsBuoiCoThe.slice(a, b + 1));
  goThanhXacNhanNeuCo();
  veChonBuoi();
}

/* Trả về null khi chọn HẾT: null là "chạy cả tuần" ở phía API, và đó
   đúng là điều người dùng đang nói. */
function buoiGuiDi() {
  if (!dsBuoiCoThe.length) return null;
  if (buoiDangChon.size === dsBuoiCoThe.length) return null;
  return dsBuoiCoThe.filter((b) => buoiDangChon.has(b));
}

/* ---- Số bốc thăm theo buổi (thẻ Kết quả) ----

   Phần mềm xáo lại thứ tự ở MỖI buổi, nên sẽ có phụ huynh hỏi đúng câu
   "vì sao con tôi thứ Ba đứng thứ 30 mà thứ Sáu đứng thứ 120". Bảng này
   là câu trả lời — và nó không phá tính minh bạch: trường vẫn chỉ công bố
   MỘT bộ số đã khoá cộng hạt giống, thứ tự từng buổi suy ra tất định từ
   hai thứ đó nên ai cũng tính lại được. */

function loadSoBocTham(search) {
  const panel = el("thamPanel");
  if (!panel) return;
  callApiMoiNhat("so_tham", "get_so_boc_tham_theo_buoi", search || "").then((res) => {
    /* Một buổi thì bảng này không nói thêm gì so với bộ số đã khoá; chưa
       chạy lần nào thì chưa có hạt giống nào để suy ra thứ tự. */
    if (!res.ok || !res.data.nhieu_buoi || !res.data.da_chay) {
      panel.hidden = true;
      return;
    }
    panel.hidden = false;
    const d = res.data;

    const canhBao = el("thamCachCu");
    if (canhBao) canhBao.hidden = !d.cach_cu;

    const head = el("thamHead");
    clear(head);
    head.innerHTML =
      `<th>${esc(t("th_student_id"))}</th><th>${esc(t("th_name"))}</th>` +
      d.ds_buoi.map((b) => `<th class="num">${esc(nhanBuoi(b))}</th>`).join("");

    const body = el("thamBody");
    clear(body);
    /* Dung ca bang trong mot DocumentFragment roi gan MOT lan: gan tung
       dong vao bang dang hien la trinh duyet tinh lai bo cuc moi dong —
       voi 400-800 dong va moi lan go phim tim kiem, do la cai giat. */
    const manh = document.createDocumentFragment();
    d.hoc_sinh.forEach((em) => {
      const tr = document.createElement("tr");
      tr.innerHTML =
        `<td>${esc(em.student_id)}</td><td>${esc(em.name || "")}</td>` +
        d.ds_buoi
          .map((b) => `<td class="num">${esc(em.so[b])}</td>`)
          .join("");
      manh.appendChild(tr);
    });
    body.appendChild(manh);
    veDemMuc("thamPanel", "dem_hoc_sinh", d.hoc_sinh.length);
  });
}

/* ---- Thời khoá biểu + độ phủ (thẻ Kết quả) ---- */

function loadThoiKhoaBieu(search) {
  const panel = el("tkbPanel");
  if (!panel) return;
  callApiMoiNhat("tkb", "get_thoi_khoa_bieu", search || "").then((res) => {
    if (!res.ok || res.data.ds_buoi.length < 2 || !res.data.hoc_sinh.length) {
      panel.hidden = true;
      return;
    }
    panel.hidden = false;
    const dsBuoi = res.data.ds_buoi;

    const head = el("tkbHead");
    clear(head);
    head.innerHTML =
      `<th>${esc(t("th_student_id"))}</th><th>${esc(t("th_name"))}</th>` +
      dsBuoi.map((b) => `<th>${esc(nhanBuoi(b))}</th>`).join("") +
      `<th class="num">${esc(t("tkb_so_clb"))}</th>`;

    const body = el("tkbBody");
    clear(body);
    /* Dung ca bang trong mot DocumentFragment roi gan MOT lan: gan tung
       dong vao bang dang hien la trinh duyet tinh lai bo cuc moi dong —
       voi 400-800 dong va moi lan go phim tim kiem, do la cai giat. */
    const manh = document.createDocumentFragment();
    res.data.hoc_sinh.forEach((em) => {
      const o = dsBuoi.map((b) => {
        const c = em.theo_buoi[b];
        if (!c || !c.club_id) {
          return `<td><span class="tkb-trong">—</span></td>`;
        }
        const lop = c.matched_tier === "reserve" ? " is-du-tru" : "";
        return `<td><span class="tkb-o${lop}">${esc(c.club_name || c.club_id)}</span></td>`;
      }).join("");
      const tr = document.createElement("tr");
      tr.innerHTML =
        `<td>${esc(em.student_id)}</td><td>${esc(em.name)}</td>` + o +
        `<td class="num">${esc(em.so_clb)}</td>`;
      manh.appendChild(tr);
    });
    body.appendChild(manh);
    veDemMuc("tkbPanel", "dem_hoc_sinh", res.data.hoc_sinh.length);
  });
}

function loadDoPhu() {
  const panel = el("doPhuPanel");
  if (!panel) return;
  callApiDocChung("get_do_phu").then((res) => {
    if (!res.ok || res.data.ds_buoi.length < 2 || !res.data.tong_hoc_sinh) {
      panel.hidden = true;
      return;
    }
    panel.hidden = false;
    const d = res.data;
    el("doPhuTb").textContent = soThapPhan(d.trung_binh_clb);
    el("doPhuTrangTay").textContent = d.so_em_trang_tay;
    veDemMuc("doPhuPanel", "dem_hoc_sinh", d.tong_hoc_sinh);

    const box = el("doPhuCot");
    clear(box);
    const lonNhat = Math.max(1, ...d.phan_bo.map((p) => p.so_em));
    d.phan_bo.forEach((p) => {
      const nhan =
        p.so_clb === 0 ? t("do_phu_0_clb")
        : p.so_clb === 1 ? t("do_phu_1_clb")
        : t("do_phu_x_clb", { n: p.so_clb });
      const ti_le = phanTramTron(p.so_em, d.tong_hoc_sinh);
      const dong = document.createElement("div");
      dong.className = "do-phu-dong" + (p.so_clb === 0 ? " is-trang-tay" : "");
      dong.tabIndex = 0;
      /* Hàng "không CLB nào" mang màu trạng thái đỏ, nên PHẢI kèm ký hiệu:
         màu một mình không đủ cho người mù màu hay bản in trắng đen. */
      dong.innerHTML =
        `<span class="do-phu-nhan">${p.so_clb === 0 && p.so_em > 0
          ? '<span class="ky-hieu-nguy" aria-hidden="true">⚠</span> ' : ""}${esc(nhan)}</span>` +
        `<span class="do-phu-track"><span class="do-phu-bar" ` +
        `style="width:${(p.so_em / lonNhat) * 100}%"></span></span>` +
        `<span class="do-phu-so-em">${esc(p.so_em)}` +
        `<span class="nv-ti-le"> · ${esc(ti_le)}%</span></span>`;
      ganTooltip(dong, () => ({
        tieu_de: nhan,
        dong: [[t("tt_so_em"), String(p.so_em)],
               [t("tt_ti_le"), ti_le + "%"]],
      }));
      box.appendChild(dong);
    });
  });
}

/* ---- Chỉ báo phủ buổi ở màn nhập tại chỗ ---- */

let buoiTaiCho = null;

function veChiBaoPhuBuoi(dsClbDaXep) {
  const box = el("fallbackPhuBuoi");
  const hint = el("fallbackBuoiHint");
  if (!box) return;
  /* Ham nay chay o MOI cu bam xep hang. Danh sach buoi khong doi trong
     luc xep cho mot em, nen hoi backend mot lan roi dung lai; chon em
     khac thi hoi lai (selectFallbackStudent xoa bo nho nay). */
  if (!buoiTaiCho) {
    buoiTaiCho = callApiDocChung("get_danh_sach_buoi").then((res) => {
      if (!res.ok) buoiTaiCho = null;
      return res;
    });
  }
  buoiTaiCho.then((res) => {
    if (!res.ok || !res.data.nhieu_buoi) {
      box.hidden = true;
      if (hint) hint.hidden = true;
      return;
    }
    box.hidden = false;
    if (hint) hint.hidden = false;

    const dsBuoi = res.data.ds_buoi;
    const daCo = new Set(
      (dsClbDaXep || [])
        .map((cid) => buoiCuaClb[cid])
        .filter((b) => b !== undefined)
    );
    clear(box);
    dsBuoi.forEach((b) => {
      const chip = document.createElement("span");
      chip.className = "phu-buoi-chip" + (daCo.has(b) ? " is-co" : "");
      chip.textContent = nhanBuoi(b);
      box.appendChild(chip);
    });
    const tom = document.createElement("span");
    tom.className = "phu-buoi-tom";
    tom.textContent = t("fallback_phu_buoi", { n: daCo.size, tong: dsBuoi.length });
    box.appendChild(tom);
  });
}


/* `giuTrang`: doi ngon ngu thi ve lai NHUNG giu trang dang xem — nguoi
   dung dang o trang 4 danh sach hoc sinh khong duoc bi day ve trang 1.
   Tra ve Promise cua danh sach hoc sinh de ben goi tick lai o da chon. */
function loadAdminTab(giuTrang) {
  loadAdminClubs();
  loadReserveGroupOptions();
  loadBuoiOptions();
  loadTaiTheoBuoi();
  loadLichTuan();
  if (!giuTrang) adminStudentPage = 1;
  callApi("get_last_run_info").then((res) => {
    adminCoKetQua = !!(res.ok && res.data);
  });
  loadAdminWharton(giuTrang);
  loadAdminDiemChuan();
  return loadAdminStudents();
}

function loadAdminClubs() {
  callApi("list_clubs_admin").then((res) => {
    const body = el("adminClubTableBody");
    const emptyState = el("adminClubEmptyState");
    clear(body);
    if (!res.ok || !res.data.length) {
      emptyState.hidden = false;
      return;
    }
    emptyState.hidden = true;
    const nhieuBuoi = new Set(res.data.map((c) => c.buoi || BUOI_MAC_DINH)).size > 1;
    document.querySelectorAll("#view-admin .cot-buoi").forEach((o) => {
      o.hidden = !nhieuBuoi;
    });
    res.data.forEach((c) => {
      const tr = document.createElement("tr");
      tr.innerHTML =
        `<td>${esc(c.club_id)}</td><td>${esc(c.name)}</td><td>${esc(c.capacity)}</td>` +
        `<td>${esc(c.reserve_capacity)}</td><td>${esc(c.reserve_group || "—")}</td>` +
        `<td class="cot-buoi">${esc(nhanBuoi(c.buoi))}</td><td></td>`;
      const delBtn = document.createElement("button");
      delBtn.className = "btn-icon-danger";
      delBtn.dataset.originalLabel = t("btn_delete");
      delBtn.textContent = delBtn.dataset.originalLabel;
      armTwoStepConfirm(delBtn, () => t("confirm_delete_generic"), () => {
        callApi("delete_club", c.club_id).then((delRes) => {
          if (delRes.ok) {
            showToast(t("toast_club_deleted", { club_id: c.club_id }), "success");
            loadAdminClubs();
            loadReserveGroupOptions();
          } else {
            showErrorToast(delRes.errors);
          }
        });
      });
      tr.lastElementChild.appendChild(delBtn);
      body.appendChild(tr);
    });
  });
}

function loadReserveGroupOptions() {
  callApi("list_reserve_groups_in_use").then((res) => {
    const list = el("reserveGroupOptions");
    clear(list);
    if (res.ok) {
      res.data.forEach((g) => {
        const opt = document.createElement("option");
        opt.value = g;
        list.appendChild(opt);
      });
    }
  });
}

function loadAdminStudents() {
  const search = el("adminStudentSearch").value.trim();
  return callApiMoiNhat("ds_hs_quan_ly", "list_students_admin", search, adminStudentPage, ADMIN_PAGE_SIZE).then((res) => {
    const body = el("adminStudentTableBody");
    const emptyState = el("adminStudentEmptyState");
    const pagination = el("adminStudentPagination");
    clear(body);
    el("adminChonTatCa").checked = false; // trang moi -> chua em nao duoc tick
    el("adminDemDanhDau").textContent = "";

    if (!res.ok || !res.data.rows.length) {
      emptyState.hidden = false;
      pagination.hidden = true;
      return;
    }
    emptyState.hidden = true;
    pagination.hidden = false;

    res.data.rows.forEach((s) => {
      const tr = document.createElement("tr");
      const tdCheck = document.createElement("td");
      const cb = document.createElement("input");
      cb.type = "checkbox";
      cb.className = "admin-row-checkbox";
      cb.dataset.studentId = s.student_id;
      tdCheck.appendChild(cb);
      tr.appendChild(tdCheck);
      /* insertAdjacentHTML, khong `innerHTML +=`: cach sau phan tich lai
         ca dong va thay o tick vua tao bang mot ban sao. */
      tr.insertAdjacentHTML("beforeend",
        `<td>${esc(s.student_id)}</td><td>${esc(s.name)}</td><td>${esc(s.reserve_group || "—")}</td>`);
      body.appendChild(tr);
    });

    el("adminPaginationLabel").textContent = t("pagination_label", {
      page: res.data.page,
      total_pages: res.data.total_pages,
      total: res.data.total,
    });
    el("btnAdminPrevPage").disabled = res.data.page <= 1;
    el("btnAdminNextPage").disabled = res.data.page >= res.data.total_pages;
  });
}

/* So em dang danh dau o the 04 — dung chung cho nut Gan va nut Xuat. */
function demDanhDauAdmin() {
  const n = document.querySelectorAll(".admin-row-checkbox:checked").length;
  el("adminDemDanhDau").textContent = n ? t("admin_dem_danh_dau", { n }) : "";
}

/* ------------------------------------------------------------------ *
 * KHỐI "ĐIỂM WHARTON" (A13.3)
 * ------------------------------------------------------------------ *
 * Chỉ hiện khi workspace bật điểm Wharton: các API đọc trả `wharton_chua_bat`
 * thì khối ẩn hẳn và thẻ Quản lý y như trước. Màn sửa dùng chung phần vẽ hai
 * khung với kiosk (`whartonVeKhung` ở js/04) và gọi `admin_save_wharton`, lõi
 * lưu cũng là lõi của `submit_wharton`.
 * ------------------------------------------------------------------ */

const WH_TRANG = 25;
const WH_NK_TRANG = 10;
const WH_NGAN_SACH = 100;      // ngân sách mỗi quỹ mỗi buổi (WHARTON_NGAN_SACH ở backend)
const whQl = { trang: 1, khoa: false, sid: null, nkTrang: 1, daLuu: "", ten: {} };

/* Khoá `<tien_to><gia_tri>` chưa có trong bảng chữ thì giữ nguyên giá trị thô. */
function whNhan(tienTo, gia) {
  const khoa = tienTo + gia;
  const chu = t(khoa);
  return chu === khoa ? gia : chu;
}

function loadAdminWharton(giuTrang) {
  if (!giuTrang) whQl.trang = 1;
  /* Chu dang go trong man sua duoc giu lai khi ve lai (vd doi ngon ngu). */
  const giu = whQl.sid && giuTrang ? whartonGiuTamTu(el("whQlSuaKhung")) : null;
  return callApi("list_wharton_canh_bao").then((res) => {
    const khoi = el("adminWhartonBlock");
    if (!res.ok) {
      khoi.hidden = true;
      whQl.sid = null;
      return null;
    }
    khoi.hidden = false;
    veCanhBaoWharton(res.data);
    return Promise.all([loadWhKhoa(), loadWhLoc(), loadWhBang()]).then(() => {
      if (whQl.sid) return moManSuaWharton(whQl.sid, giu);
      el("whQlSua").hidden = true;
      return null;
    });
  });
}

function loadWhKhoa() {
  return callApi("get_wharton_lock_status").then((res) => {
    if (!res.ok) return;
    whQl.khoa = !!res.data.is_locked;
    const chu = el("whQlKhoa");
    chu.textContent = whQl.khoa
      ? t("wh_ql_dang_khoa", { luc: (res.data.locked_at || "").replace("T", " ") })
      : t("wh_ql_dang_mo");
    chu.classList.toggle("is-khoa", whQl.khoa);
    el("btnWhMoKhoa").hidden = !whQl.khoa;
    el("whMoKhoaChuaKhoa").hidden = whQl.khoa;
    if (!whQl.khoa) el("whMoKhoaHop").hidden = true;
    if (!el("whMoKhoaHop").hidden) {
      el("whMoKhoaHoi").textContent = t("wh_mo_khoa_hoi", { can_go: "MO" });
    }
  });
}

function veCanhBaoWharton(ds) {
  const goc = el("whCanhBao");
  clear(goc);
  if (!ds.length) {
    const p = document.createElement("p");
    p.className = "hint-text";
    p.textContent = t("wh_cb_rong");
    goc.appendChild(p);
    return;
  }
  [["chua_hop_le", "wh_cb_chua_hop_le"], ["vang_thi", "wh_cb_vang_thi"]].forEach(([loai, khoaChu]) => {
    const nhom = ds.filter((c) => c.loai === loai);
    if (!nhom.length) return;
    const div = document.createElement("div");
    div.className = "wh-cb-nhom";
    div.dataset.loai = loai;
    const ten = document.createElement("div");
    ten.className = "wh-cb-nhom-ten";
    ten.textContent = t(khoaChu) + " (" + nhom.length + ")";
    div.appendChild(ten);
    nhom.forEach((c) => {
      const nut = document.createElement("button");
      nut.type = "button";
      nut.className = "wh-cb-dong";
      nut.dataset.studentId = c.student_id;
      nut.textContent = c.name + " (" + c.student_id + ")";
      nut.addEventListener("click", () => {
        moManSuaWharton(c.student_id).then(() => {
          el("whQlSua").scrollIntoView({ block: "nearest" });
        });
      });
      div.appendChild(nut);
    });
    goc.appendChild(div);
  });
}

/* Ba o loc buoi / CLB lay tu danh sach CLB; giu lua chon dang co neu con. */
function loadWhLoc() {
  return callApi("list_clubs").then((res) => {
    if (!res.ok) return;
    whQl.ten = {};
    res.data.forEach((c) => { whQl.ten[c.club_id] = c.name; });
    const dsBuoi = Array.from(new Set(res.data.map((c) => c.buoi || BUOI_MAC_DINH)));
    const dien = (sel, muc) => {
      const cu = sel.value;
      clear(sel);
      muc.forEach(([gt, chu]) => {
        const o = document.createElement("option");
        o.value = gt;
        o.textContent = chu;
        sel.appendChild(o);
      });
      if (muc.some(([gt]) => gt === cu)) sel.value = cu;
    };
    dien(el("whLocBuoi"), [["", t("wh_loc_tat_ca")]].concat(dsBuoi.map((b) => [b, nhanBuoi(b)])));
    dien(el("whLocClb"), [["", t("wh_loc_tat_ca")]].concat(res.data.map((c) => [c.club_id, c.name])));
    el("whLocBuoiNhan").hidden = dsBuoi.length < 2;
  });
}

function loadWhBang() {
  return callApiMoiNhat("wh_bang", "list_wharton_admin",
    el("whQlTim").value.trim(), el("whLocQuy").value || null, el("whLocBuoi").value || null,
    el("whLocClb").value || null, el("whLocChiLoi").checked, whQl.trang, WH_TRANG).then((res) => {
    const body = el("whQlBody");
    clear(body);
    if (!res.ok || !res.data.rows.length) {
      el("whQlRong").hidden = false;
      el("whQlPhanTrang").hidden = true;
      return;
    }
    el("whQlRong").hidden = true;
    el("whQlPhanTrang").hidden = false;
    res.data.rows.forEach((r) => body.appendChild(dongBangWharton(r)));
    el("whQlNhanTrang").textContent = t("pagination_label", {
      page: res.data.page, total_pages: res.data.total_pages, total: res.data.total,
    });
    el("btnWhTruoc").disabled = res.data.page <= 1;
    el("btnWhSau").disabled = res.data.page >= res.data.total_pages;
  });
}

function dongBangWharton(r) {
  const tr = document.createElement("tr");
  const coVanDe = r.loi.length > 0 || r.vang_thi.length > 0;
  tr.className = "wh-ql-dong" + (coVanDe ? " wh-ql-loi" : "");
  tr.dataset.studentId = r.student_id;
  tr.insertAdjacentHTML("beforeend", `<td>${esc(r.student_id)}</td><td>${esc(r.name)}</td>`);

  const tdDiem = document.createElement("td");
  tdDiem.className = "wh-ql-diem";
  const theoBuoi = new Map();
  r.diem.forEach((c) => {
    if (!theoBuoi.has(c.buoi)) theoBuoi.set(c.buoi, { 1: [], 2: [] });
    theoBuoi.get(c.buoi)[c.quy].push(c);
  });
  const nhieuBuoi = theoBuoi.size > 1;
  theoBuoi.forEach((q, buoi) => {
    if (nhieuBuoi) {
      const tenBuoi = document.createElement("div");
      tenBuoi.className = "wh-ql-nhom-buoi";
      tenBuoi.textContent = nhanBuoi(buoi);
      tdDiem.appendChild(tenBuoi);
    }
    [1, 2].forEach((quy) => {
      if (!q[quy].length) return;
      const hang = document.createElement("div");
      hang.className = "wh-ql-quy";
      hang.dataset.quy = String(quy);
      hang.dataset.buoi = buoi;
      const tenQuy = document.createElement("span");
      tenQuy.className = "wh-ql-quy-ten";
      tenQuy.textContent = t("wh_quy_ngan", { q: quy });
      hang.appendChild(tenQuy);
      q[quy].forEach((c) => {
        const o = document.createElement("span");
        o.className = "wh-ql-o";
        o.dataset.clb = c.club_id;
        o.textContent = c.ten_clb + ": " + (c.diem === null ? "—" : c.diem);
        if (c.tu_dien) {
          const td = document.createElement("span");
          td.className = "wh-ql-tu-dien";
          td.textContent = " (" + t("wh_o_tu_dien") + ")";
          o.appendChild(td);
        }
        hang.appendChild(o);
      });
      const tong = (r.tong[buoi] || {})[String(quy)] || 0;
      const chuTong = document.createElement("span");
      chuTong.className = "wh-ql-tong" + (tong === WH_NGAN_SACH ? "" : " is-sai");
      chuTong.textContent = t("wh_tong", { x: tong });
      hang.appendChild(chuTong);
      tdDiem.appendChild(hang);
    });
  });
  tr.appendChild(tdDiem);

  const tdTt = document.createElement("td");
  const them = (lop, khoa) => {
    const s = document.createElement("div");
    s.className = "wh-ql-tt " + lop;
    s.textContent = t(khoa);
    tdTt.appendChild(s);
  };
  if (r.loi.length) them("is-loi", "wh_tt_loi");
  if (r.vang_thi.length) them("is-vang", "wh_tt_vang");
  if (r.lech_tick) them("is-lech", "wh_tt_lech");
  if (!tdTt.children.length) them("is-ok", "wh_tt_ok");
  tr.appendChild(tdTt);

  tr.addEventListener("click", () => {
    moManSuaWharton(r.student_id).then(() => {
      el("whQlSua").scrollIntoView({ block: "nearest" });
    });
  });
  return tr;
}

/* ---- Man sua diem cua mot em ---- */

function capNhatChuaLuuWh() {
  el("whQlChuaLuu").hidden = whartonChuoiTu(el("whQlSuaKhung")) === whQl.daLuu;
}

function moManSuaWharton(sid, giu) {
  whQl.sid = sid;
  return callApi("get_student_entry_state", sid).then((res) => {
    if (sid !== whQl.sid) return null;
    if (!res.ok || !res.data.wharton) {
      /* Em da bi xoa o noi khac thi dong man sua im lang; loi khac thi bao. */
      if (!res.ok && !res.errors.some((e) => e.code === "student_not_found")) showErrorToast(res.errors);
      whQl.sid = null;
      el("whQlSua").hidden = true;
      return null;
    }
    veManSuaWharton(res.data, giu || null);
    return loadWhNhatKy(false);
  });
}

function veManSuaWharton(state, giu) {
  const w = state.wharton;
  const khung = el("whQlSuaKhung");
  el("whQlSua").hidden = false;
  el("whQlSuaTen").textContent = t("wh_sua_title", {
    name: (state.name || state.student_id) + " (" + state.student_id + ")",
  });
  whQl.daLuu = whartonVeKhung(khung, w, {
    ranked: state.ranked_clubs,
    ten: (cid) => whQl.ten[cid] || cid,
    giu,
    chiDoc: !!w.khoa,
    khiDoi: capNhatChuaLuuWh,
  });
  const coKhung = !!khung.querySelector(".wh-khung");
  el("whQlSuaRong").hidden = coKhung;
  el("whQlSuaKhoa").hidden = !w.khoa;
  el("btnWhLuu").disabled = !!w.khoa || !coKhung;
  el("btnWhXoaMot").disabled = !!w.khoa;
  capNhatChuaLuuWh();
}

function loadWhNhatKy(them) {
  const sid = whQl.sid;
  el("whNkChonEm").hidden = !!sid;
  if (!sid) return Promise.resolve(null);
  if (!them) whQl.nkTrang = 1;
  return callApi("get_wharton_nhat_ky", sid, whQl.nkTrang, WH_NK_TRANG).then((res) => {
    if (!res.ok || sid !== whQl.sid) return;
    const ds = el("whQlNhatKy");
    if (!them) clear(ds);
    const dang = (d) => {
      if (!d || d.so_dong !== undefined) return "";
      const phan = ["w1", "w2"].map((k) => Object.entries(d[k] || {})
        .map(([c, v]) => (whQl.ten[c] || c) + ": " + v).join(", ")).filter(Boolean);
      return phan.join(" | ");
    };
    res.data.rows.forEach((r) => {
      const li = document.createElement("li");
      li.dataset.hanhDong = r.hanh_dong;
      li.dataset.nguon = r.nguon;
      const dongChu = t("wh_nk_dong", {
        luc: r.luc.replace("T", " "),
        nguon: whNhan("wh_nk_", r.nguon),
        nguoi: r.nguoi ? " (" + r.nguoi + ")" : "",
        hanh_dong: whNhan("wh_nk_", r.hanh_dong),
      });
      const cu = dang(r.cu), moi = dang(r.moi);
      li.textContent = dongChu + (cu || moi ? " [" + (cu || "—") + " → " + (moi || "—") + "]" : "");
      ds.appendChild(li);
    });
    el("whQlNhatKyRong").hidden = ds.children.length > 0;
    el("btnWhNkThem").hidden = res.data.page >= res.data.total_pages;
  });
}

function initWhartonQuanLy() {
  const veLaiBang = () => { whQl.trang = 1; loadWhBang(); };
  el("whQlTim").addEventListener("input", debounce(veLaiBang, 250));
  ["whLocQuy", "whLocBuoi", "whLocClb", "whLocChiLoi"].forEach((id) => {
    el(id).addEventListener("change", veLaiBang);
  });
  el("btnWhTruoc").addEventListener("click", () => { whQl.trang = Math.max(1, whQl.trang - 1); loadWhBang(); });
  el("btnWhSau").addEventListener("click", () => { whQl.trang += 1; loadWhBang(); });
  el("btnWhDongSua").addEventListener("click", () => {
    whQl.sid = null;
    el("whQlSua").hidden = true;
    clear(el("whQlNhatKy"));
    el("whQlNhatKyRong").hidden = true;
    el("btnWhNkThem").hidden = true;
    el("whNkChonEm").hidden = false;
  });
  /* Nút (i) và "Xem nhật ký": câu giải thích dài và nhật ký chỉ hiện khi bấm. */
  el("btnWhThongTin").addEventListener("click", () => {
    const mo = el("whQlMoTa").hidden;
    el("whQlMoTa").hidden = !mo;
    el("btnWhThongTin").setAttribute("aria-expanded", mo ? "true" : "false");
  });
  el("btnWhXemNhatKy").addEventListener("click", () => {
    const mo = el("whNkHop").hidden;
    el("whNkHop").hidden = !mo;
    el("btnWhXemNhatKy").setAttribute("aria-expanded", mo ? "true" : "false");
    el("whNkChonEm").hidden = !!whQl.sid;
  });
  el("btnWhNkThem").addEventListener("click", () => { whQl.nkTrang += 1; loadWhNhatKy(true); });

  el("btnWhLuu").addEventListener("click", () => {
    const sid = whQl.sid;
    if (!sid) return;
    const { w1, w2 } = whartonThuThapTu(el("whQlSuaKhung"));
    khiBan(el("btnWhLuu"), () => callApi("admin_save_wharton", sid, w1, w2)).then((res) => {
      if (res.ok) {
        feedback(el("whQlSuaPhanHoi"), t("feedback_wharton_saved"), false);
        loadAdminWharton(true);
      } else {
        feedbackErrors(el("whQlSuaPhanHoi"), res.errors);
      }
    });
  });

  armTwoStepConfirm(el("btnWhXoaMot"), () => t("confirm_wh_xoa_mot"), () => {
    const sid = whQl.sid;
    if (!sid) return;
    callApi("clear_wharton", sid).then((res) => {
      if (res.ok) {
        showToast(t("toast_wh_xoa_mot", { student_id: sid }), "success");
        loadAdminWharton(true);
      } else {
        showErrorToast(res.errors);
      }
    });
  });

  /* Mo khoa: bam nut -> hop xac nhan -> go dung chu MO. */
  el("btnWhMoKhoa").addEventListener("click", () => {
    el("whMoKhoaHoi").textContent = t("wh_mo_khoa_hoi", { can_go: "MO" });
    el("whMoKhoaGo").value = "";
    el("whMoKhoaHop").hidden = false;
    el("whMoKhoaGo").focus();
  });
  el("btnWhMoKhoaHuy").addEventListener("click", () => { el("whMoKhoaHop").hidden = true; });
  el("btnWhMoKhoaXn").addEventListener("click", () => {
    khiBan(el("btnWhMoKhoaXn"), () => callApi("mo_khoa_wharton", el("whMoKhoaGo").value.trim())).then((res) => {
      if (res.ok) {
        el("whMoKhoaHop").hidden = true;
        showToast(trErr({ code: "wharton_da_mo_khoa", params: {} }), "success");
        loadAdminWharton(true);
      } else {
        showErrorToast(res.errors);
      }
    });
  });

  /* Xoa diem cua tat ca: bam nut -> hop xac nhan -> go dung chu XOA (server kiem lai). */
  el("btnWhXoaTatCa").addEventListener("click", () => {
    el("whXoaTatCaHoi").textContent = t("wh_xoa_tat_ca_hoi", { can_go: "XOA" });
    el("whXoaTatCaGo").value = "";
    el("whXoaTatCaHop").hidden = false;
    el("whXoaTatCaGo").focus();
  });
  el("btnWhXoaTatCaHuy").addEventListener("click", () => { el("whXoaTatCaHop").hidden = true; });
  el("btnWhXoaTatCaXn").addEventListener("click", () => {
    khiBan(el("btnWhXoaTatCaXn"), () => callApi("clear_wharton", null, el("whXoaTatCaGo").value.trim())).then((res) => {
      if (res.ok) {
        el("whXoaTatCaHop").hidden = true;
        showToast(trErr({ code: "wharton_da_xoa", params: { n: res.data.n_students } }), "success");
        loadAdminWharton(true);
      } else {
        showErrorToast(res.errors);
      }
    });
  });
}

function initAdminHandlers() {
  el("btnSaveClub").addEventListener("click", () => {
    const id = el("clubFormId").value.trim();
    const name = el("clubFormName").value.trim();
    const capacity = el("clubFormCapacity").value;
    const reserveCapacity = el("clubFormReserveCapacity").value || 0;
    const reserveGroup = el("clubFormReserveGroup").value.trim();
    const buoi = el("clubFormBuoi") ? el("clubFormBuoi").value.trim() : "";
    if (!id || !name || !capacity) {
      feedback(el("clubFormFeedback"), t("feedback_club_form_required"), true);
      return;
    }
    khiBan(el("btnSaveClub"), () => callApi("create_or_update_club", id, name, capacity, reserveCapacity, reserveGroup, buoi)).then((res) => {
      if (res.ok) {
        feedback(el("clubFormFeedback"), t("feedback_club_saved", { club_id: id }), false);
        el("clubFormId").value = "";
        if (el("clubFormBuoi")) el("clubFormBuoi").value = "";
        el("clubFormName").value = "";
        el("clubFormCapacity").value = "";
        el("clubFormReserveCapacity").value = "0";
        el("clubFormReserveGroup").value = "";
        loadAdminClubs();
        loadReserveGroupOptions();
      } else {
        feedbackErrors(el("clubFormFeedback"), res.errors);
      }
    });
  });

  el("adminStudentSearch").addEventListener(
    "input",
    debounce(() => {
      adminStudentPage = 1;
      loadAdminStudents();
    }, 250)
  );

  el("btnAdminPrevPage").addEventListener("click", () => {
    if (adminStudentPage > 1) {
      adminStudentPage -= 1;
      loadAdminStudents();
    }
  });
  el("btnAdminNextPage").addEventListener("click", () => {
    adminStudentPage += 1;
    loadAdminStudents();
  });

  /* Cung tap o tick voi nut "Gan" ben canh — mot cach chon, hai viec. */
  el("btnAdminXuatHs").addEventListener("click", () => {
    const ids = Array.from(document.querySelectorAll(".admin-row-checkbox:checked")).map(
      (cb) => cb.dataset.studentId
    );
    if (!ids.length) {
      showToast(t("toast_no_students_ticked"), "error");
      return;
    }
    chayXuat([["xuat_muc_hoc_sinh", "export_hoc_sinh_csv", [ids, ""],
      (d) => t("xuat_kq_hoc_sinh", { n: d.n_hoc_sinh, n_dong: d.n_dong, path: d.path })]],
      el("adminXuatFeedback"));
  });

  el("adminChonTatCa").addEventListener("change", (ev) => {
    document.querySelectorAll(".admin-row-checkbox").forEach((cb) => { cb.checked = ev.target.checked; });
    demDanhDauAdmin();
  });
  el("adminStudentTableBody").addEventListener("change", (ev) => {
    if (ev.target.classList && ev.target.classList.contains("admin-row-checkbox")) demDanhDauAdmin();
  });

  el("btnBulkAssign").addEventListener("click", () => {
    const ids = Array.from(document.querySelectorAll(".admin-row-checkbox:checked")).map(
      (cb) => cb.dataset.studentId
    );
    const group = el("bulkReserveGroupInput").value.trim();
    if (!ids.length) {
      showToast(t("toast_no_students_ticked"), "error");
      return;
    }
    khiBan(el("btnBulkAssign"), () => callApi("bulk_set_reserve_group", ids, group)).then((res) => {
      if (res.ok) {
        showToast(t("toast_bulk_assign_success", { n: res.data.n_updated }), "success");
        loadAdminStudents();
        loadReserveGroupOptions();
      } else {
        showErrorToast(res.errors);
      }
    });
  });

  /* --- Vung nguy hiem: xoa du lieu de lam lai tu dau --------------- *
     Chuoi "XOA" la xac nhan bat buoc o phia Python. No KHONG phai thu
     nguoi dung go — nut da co xac nhan hai buoc roi. No de mot lenh
     goi API nham (vd tu console) khong xoa duoc gi. */
  /* Du lieu da xoa thi moi thu dang TRO toi du lieu cu cung phai di:
     o tim kiem con chu, em dang mo o the Nhap tai cho, danh sach CLB
     dang mo, CLB dang cham. Bo sot thi quay sang the kia van thay dung
     em vua tim — mot em khong con ton tai. */
  function donSachSauKhiXoaDuLieu() {
    ["studentSearchInput", "newStudentId", "newStudentName", "adminStudentSearch",
     "resultsSearch", "tkbSearch", "thamSearch"].forEach((id) => {
      if (el(id)) el(id).value = "";
    });
    boChonHocSinhDuPhong();
    currentClubs = [];
    fallbackStudentPage = 1;
    adminStudentPage = 1;
    clear(el("studentSearchResults"));
    el("fallbackStudentPagination").hidden = true;
    dongDanhSachCLB();
    currentScoringClub = null;
    if (el("scoringWorkArea")) el("scoringWorkArea").hidden = true;
    /* Man sua diem Wharton dang tro toi mot em khong con ton tai. */
    whQl.sid = null;
    el("whQlSua").hidden = true;
  }

  function noiNutXoa(idNut, phamVi, khoaNhanThuong, khoaNhanCoKetQua, khoaToast) {
    armTwoStepConfirm(
      el(idNut),
      () => t(adminCoKetQua ? khoaNhanCoKetQua : khoaNhanThuong),
      () => {
        /* Dang nhap tep hay dang chay thi chuoi do van ghi tiep sau khi xoa:
           cac tep con lai nap vao CSDL vua xoa, roi ghi "Da nhap xong" de
           len the Van hanh vua don sach. Nut "Bo danh sach" bi khoa luc nay
           cung vi ly do do. */
        if (khoa.dangNhap || khoa.dangChay) {
          showToast(t("toast_reset_blocked_busy"), "error");
          return;
        }
        callApi("reset_data", phamVi, "XOA").then((res) => {
          if (!res.ok) {
            showErrorToast(res.errors);
            return;
          }
          showToast(
            t(khoaToast, {
              n_students: res.data.n_students,
              n_clubs: res.data.n_clubs,
              n_clubs_left: res.data.n_clubs_con_lai,
              backup_name: res.data.backup_name,
            }),
            "success"
          );
          /* Phai lam moi CA nhung thu KHONG nam tren tab nay. Thanh ben
             luon hien, va sau khi xoa no van noi "Chay gan nhat: 6/6 xep
             duoc" cho mot lan chay ma du lieu da khong con — man hinh noi
             mot dieu khong dung, ngay sau thao tac nguy hiem nhat. */
          /* Hoc sinh da bi xoa -> tap em da chon o the 02 khong con nghia.
             Giu lai thi lan xuat ho so sau hong ca lo (student_not_found). */
          hsDaChon.clear();
          donSachSauKhiXoaDuLieu();
          donSachTheVanHanh();
          loadAdminTab();
          loadHealthReport();
          refreshDashboardStats();
          refreshSidebarStatus();
        });
      }
    );
  }

  noiNutXoa("btnResetStudents", "hoc_sinh",
            "confirm_reset_students", "confirm_reset_students_has_results",
            "toast_reset_students_done");
  noiNutXoa("btnResetAll", "tat_ca",
            "confirm_reset_all", "confirm_reset_all_has_results",
            "toast_reset_all_done");

  initWhartonQuanLy();
  initDiemChuan();
}


/* ==========================================================================
   Điểm chuẩn từng CLB (A13.4)

   Chỉ cho quản trị, chỉ khi workspace bật điểm quyết tâm và đã có kết quả. Số liệu do
   `get_diem_chuan` (tổng quan) và `get_diem_chuan_clb` (từng em) trả; ở đây chỉ VẼ.

   Ba biểu đồ, SVG thuần (chạy ngoại tuyến, không thư viện, không tải gì từ mạng):
     (a) veCotPhanBoQuyetTam   cột phân bố điểm quyết tâm tầng 2 của MỘT CLB;
     (b) veDaiChamQuyetTam     mỗi em một chấm, cùng thang;
     (c) veTongQuanDiemChuan   bảng tổng quan mọi CLB, mỗi dòng một thanh.
   Màu: xanh `--chart-general` cho "được nhận", xám `--chart-khong-nhan` cho "không được
   nhận"; kênh phụ không dựa vào màu là gạch chéo (cột) và chấm rỗng (dải chấm).
   ========================================================================== */

const DC_NS = "http://www.w3.org/2000/svg";
const dc = { rows: null, ct: null, chon: "", moKq: false };
let dcUid = 0;

function dcSvg(ten, thuocTinh, cha) {
  const n = document.createElementNS(DC_NS, ten);
  Object.keys(thuocTinh || {}).forEach((k) => n.setAttribute(k, String(thuocTinh[k])));
  if (cha) cha.appendChild(n);
  return n;
}

function dcSo(x) {
  /* Tối đa hai chữ số thập phân, dấu phẩy kiểu Việt: 8,25. */
  return soThapPhan(Math.round(x * 100) / 100);
}

/* Chữ trong một ô của bảng hai tầng x hai mức. */
function dcChuoiMuc(muc, tang) {
  if (!muc) return "—";
  if (muc.con_cho) return t("dc_con_cho", { n: muc.con_cho });
  if (tang === 1) return t("dc_tang1_cell", { thi: dcSo(muc.diem_thi), qt: dcSo(muc.diem_quyet_tam) });
  return dcSo(muc.diem_quyet_tam);
}

function dcTenDong(r, nhieuBuoi) {
  return (nhieuBuoi && r.buoi ? "[" + r.buoi + "] " : "") + r.ten;
}

function dcChuGiai(goc, muc) {
  const ul = document.createElement("ul");
  ul.className = "dc-chu-giai";
  muc.forEach(([lop, khoa]) => {
    const li = document.createElement("li");
    const o = document.createElement("span");
    o.className = "dc-mau " + lop;
    o.setAttribute("aria-hidden", "true");
    li.appendChild(o);
    li.appendChild(document.createTextNode(t(khoa)));
    ul.appendChild(li);
  });
  goc.appendChild(ul);
}

/* (c) Bảng tổng quan. Mỗi dòng: tên, thanh điểm chuẩn tầng 2 (thang 0 đến 100), số đơn / số
   chỗ, và chấm "nóng" khi số đơn lớn hơn số chỗ. Dòng nào chưa có ai ở tầng 2 thì ghi "—". */
function veTongQuanDiemChuan(goc, ds) {
  clear(goc);
  if (!ds || !ds.length) {
    const p = document.createElement("p");
    p.className = "hint-text";
    p.textContent = t("dc_chua_co_ket_qua");
    goc.appendChild(p);
    return;
  }
  const nhieuBuoi = new Set(ds.map((r) => r.buoi)).size > 1;
  const cuon = document.createElement("div");
  cuon.className = "scroll-x";
  const bang = document.createElement("table");
  bang.className = "data-table dc-tq";
  const cap = document.createElement("caption");
  cap.className = "dc-an-chu";
  cap.textContent = t("dc_tong_quan_tieu_de");
  bang.appendChild(cap);
  const dau = bang.createTHead().insertRow();
  [["dc_cot_ten", ""], ["dc_cot_chuan", ""], ["dc_cot_don", "num"]].forEach(([khoa, lop]) => {
    const th = document.createElement("th");
    th.scope = "col";
    th.className = lop;
    th.textContent = t(khoa);
    dau.appendChild(th);
  });
  const tb = bang.createTBody();
  ds.forEach((r) => {
    const tr = tb.insertRow();
    tr.dataset.clubId = r.club_id;
    const ten = tr.insertCell();
    const tenTxt = document.createElement("span");
    tenTxt.className = "dc-ten";
    tenTxt.textContent = dcTenDong(r, nhieuBuoi);
    ten.appendChild(tenTxt);
    if (r.tang1.thuong || r.tang1.du_tru) {
      const phu = document.createElement("span");
      phu.className = "dc-phu";
      phu.textContent = t("dc_tang1") + ": " + dcChuoiMuc(r.tang1.thuong || r.tang1.du_tru, 1);
      ten.appendChild(phu);
    }

    const o = tr.insertCell();
    const m = r.tang2.thuong || r.tang2.du_tru;
    if (m) {
      const x = Math.max(0, Math.min(100, m.diem_quyet_tam));
      const W = 200, H = 14, rong = (x / 100) * W;
      const nhan = t("dc_thanh_nhan", { ten: r.ten, x: dcChuoiMuc(m, 2) });
      const svg = dcSvg("svg", { class: "dc-thanh", viewBox: `0 0 ${W} ${H}`, role: "img",
                                 preserveAspectRatio: "none" });
      dcSvg("title", {}, svg).textContent = nhan;
      dcSvg("rect", { class: "dc-thanh-nen", x: 0, y: 0, width: W, height: H, rx: 4 }, svg);
      if (rong >= 8) {
        dcSvg("path", { class: "dc-thanh-do", "data-diem": x,
                        d: `M0 0H${rong - 4}a4 4 0 0 1 4 4v6a4 4 0 0 1-4 4H0z` }, svg);
      } else if (rong > 0) {
        dcSvg("rect", { class: "dc-thanh-do", "data-diem": x, x: 0, y: 0, width: rong, height: H }, svg);
      }
      o.appendChild(svg);
      const g = document.createElement("span");
      g.className = "dc-gtri";
      g.textContent = dcChuoiMuc(m, 2);
      o.appendChild(g);
    } else {
      o.textContent = "—";
      o.title = t("dc_khong_ai");
    }

    const d = tr.insertCell();
    d.className = "num";
    d.appendChild(document.createTextNode(r.so_don + " / " + r.suc_chua));
    if (r.so_don > r.suc_chua) {
      const nong = document.createElement("span");
      nong.className = "dc-nong";
      nong.setAttribute("role", "img");
      nong.setAttribute("aria-label", t("dc_nong"));
      nong.title = t("dc_nong");
      d.appendChild(nong);
    }
  });
  cuon.appendChild(bang);
  goc.appendChild(cuon);
  const ghi = document.createElement("p");
  ghi.className = "hint-text";
  ghi.textContent = t("dc_chu_giai_thanh");
  goc.appendChild(ghi);
  dcChuGiai(goc, [["is-nong", "dc_nong"]]);
}

/* Thang ngang 0 đến 100 dùng chung cho (a) và (b). */
function dcThangX(svg, W, L, R, yTren, yDuoi) {
  const x = (v) => L + (v / 100) * (W - L - R);
  for (let v = 0; v <= 100; v += 20) {
    dcSvg("text", { x: x(v), y: yDuoi + 16, "text-anchor": "middle" }, svg).textContent = String(v);
  }
  dcSvg("text", { x: (L + W - R) / 2, y: yDuoi + 32, "text-anchor": "middle" }, svg)
    .textContent = t("dc_truc_x");
  return x;
}

function dcVachChuan(svg, x, chuan, yTren, yDuoi, W) {
  if (!chuan) return;
  const m = chuan.tang2.thuong || chuan.tang2.du_tru;
  if (!m) return;
  const px = x(Math.max(0, Math.min(100, m.diem_quyet_tam)));
  dcSvg("line", { class: "dc-chuan-vach", x1: px, x2: px, y1: yTren, y2: yDuoi,
                  "data-diem": m.diem_quyet_tam }, svg);
  const chu = dcSvg("text", { class: "dc-chuan-nhan", x: px, y: yTren - 6,
                              "text-anchor": px > W - 90 ? "end" : (px < 60 ? "start" : "middle") }, svg);
  chu.textContent = t("dc_vach_chuan", { x: m.con_cho ? dcChuoiMuc(m, 2) : dcSo(m.diem_quyet_tam) });
}

function dcChuGiaiDuoiKhong(goc, laCham) {
  dcChuGiai(goc, laCham
    ? [["is-cham-duoc", "dc_duoc"], ["is-cham-khong", "dc_khong"]]
    : [["is-duoc", "dc_duoc"], ["is-khong", "dc_khong"]]);
  const ul = goc.querySelector(".dc-chu-giai:last-child");
  const li = document.createElement("li");
  const o = document.createElement("span");
  o.className = "dc-mau is-vach";
  o.setAttribute("aria-hidden", "true");
  li.appendChild(o);
  li.appendChild(document.createTextNode(t("dc_vach_chuan", { x: "" }).trim()));
  ul.appendChild(li);
}

/* Bảng chữ cho người đọc màn hình: cùng số liệu với hình, không phụ thuộc màu. */
function dcBangAn(goc, tieuDe, cot, dong) {
  const bang = document.createElement("table");
  bang.className = "dc-an-chu";
  const cap = document.createElement("caption");
  cap.textContent = tieuDe;
  bang.appendChild(cap);
  const h = bang.createTHead().insertRow();
  cot.forEach((c) => { const th = document.createElement("th"); th.scope = "col"; th.textContent = c; h.appendChild(th); });
  const tb = bang.createTBody();
  dong.forEach((d) => {
    const tr = tb.insertRow();
    d.forEach((v) => { tr.insertCell().textContent = String(v); });
  });
  goc.appendChild(bang);
}

/* (a) Cột phân bố: trục ngang 0 đến 100, nhóm 10 điểm, mỗi cột chia hai màu. */
function veCotPhanBoQuyetTam(goc, d) {
  clear(goc);
  const cap = document.createElement("figcaption");
  cap.textContent = t("dc_cot_tieu_de", { ten: d.ten });
  goc.appendChild(cap);
  if (!d.em.length) {
    const p = document.createElement("p");
    p.className = "hint-text";
    p.textContent = t("dc_rong_bieu_do");
    goc.appendChild(p);
    return;
  }
  const nhom = [];
  for (let i = 0; i < 10; i++) nhom.push({ tu: i * 10, den: i * 10 + 9, duoc: 0, khong: 0 });
  nhom[9].den = 100;
  d.em.forEach((e) => {
    const i = Math.min(9, Math.floor(e.diem / 10));
    nhom[i][e.ket_qua === "duoc" ? "duoc" : "khong"] += 1;
  });
  const cao = Math.max(1, ...nhom.map((g) => g.duoc + g.khong));
  const nac = cao <= 5 ? 1 : Math.ceil(cao / 5);
  const tran = Math.ceil(cao / nac) * nac;

  const W = 560, H = 270, L = 44, R = 12, yTren = 30, yDuoi = 210;
  const id = "dcGach" + (++dcUid);
  const svg = dcSvg("svg", { class: "dc-svg", viewBox: `0 0 ${W} ${H}`, role: "img",
                             "aria-labelledby": id + "T", "data-bieu-do": "cot" });
  dcSvg("title", { id: id + "T" }, svg).textContent = t("dc_cot_tieu_de", { ten: d.ten });
  const defs = dcSvg("defs", {}, svg);
  const pat = dcSvg("pattern", { id: id, width: 6, height: 6, patternUnits: "userSpaceOnUse",
                                 patternTransform: "rotate(45)" }, defs);
  dcSvg("rect", { class: "dc-gach-nen", width: 6, height: 6 }, pat);
  dcSvg("line", { class: "dc-gach-net", x1: 0, y1: 0, x2: 0, y2: 6 }, pat);

  const y = (n) => yDuoi - (n / tran) * (yDuoi - yTren);
  for (let n = 0; n <= tran; n += nac) {
    dcSvg("line", { class: "dc-luoi", x1: L, x2: W - R, y1: y(n), y2: y(n) }, svg);
    dcSvg("text", { x: L - 6, y: y(n) + 4, "text-anchor": "end" }, svg).textContent = String(n);
  }
  dcSvg("text", { x: 4, y: 14 }, svg).textContent = t("dc_truc_y");
  const x = dcThangX(svg, W, L, R, yTren, yDuoi);
  const bang = (W - L - R) / 10;
  const DAY = 24, KHE = 2, BAN_KINH = 4;
  nhom.forEach((g, i) => {
    const x0 = L + i * bang + (bang - DAY) / 2;
    const hDuoc = (g.duoc / tran) * (yDuoi - yTren);
    const hKhong = (g.khong / tran) * (yDuoi - yTren);
    const grp = dcSvg("g", { "data-tu": g.tu, "data-duoc": g.duoc, "data-khong": g.khong }, svg);
    let yTop = yDuoi;
    if (g.duoc) {
      const co = g.khong > 0;
      const r = co ? 0 : BAN_KINH;
      const cao1 = hDuoc;
      dcSvg("path", { class: "dc-duoc dc-cot-duoc",
                      d: dcCotTronTren(x0, yDuoi - cao1, DAY, cao1, r) }, grp);
      yTop = yDuoi - cao1 - KHE;
    }
    if (g.khong) {
      const cao2 = Math.max(0, hKhong - (g.duoc ? KHE : 0));
      dcSvg("path", { class: "dc-khong dc-cot-khong", fill: `url(#${id})`,
                      d: dcCotTronTren(x0, yTop - cao2, DAY, cao2, BAN_KINH) }, grp);
    }
    const hit = dcSvg("rect", { class: "dc-vung-chi", x: L + i * bang, y: yTren, width: bang,
                                height: yDuoi - yTren, tabindex: 0, role: "img",
                                "aria-label": `${g.tu} - ${g.den}: ${t("dc_duoc")} ${g.duoc}, ${t("dc_khong")} ${g.khong}` }, grp);
    ganTooltip(hit, () => ({
      tieu_de: t("dc_tooltip_khoang") + " " + g.tu + " - " + g.den,
      dong: [[t("dc_duoc"), String(g.duoc)], [t("dc_khong"), String(g.khong)]],
    }));
  });
  dcSvg("line", { class: "dc-luoi", x1: L, x2: W - R, y1: yDuoi, y2: yDuoi }, svg);
  dcVachChuan(svg, x, d.chuan, yTren, yDuoi, W);
  goc.appendChild(svg);
  dcChuGiaiDuoiKhong(goc, false);
  dcBangAn(goc, t("dc_cot_tieu_de", { ten: d.ten }),
           [t("dc_tooltip_khoang"), t("dc_duoc"), t("dc_khong")],
           nhom.map((g) => [g.tu + " - " + g.den, g.duoc, g.khong]));
}

/* Đường bao một cột: góc trên bo `r`, đáy vuông (đứng trên đường nền). */
function dcCotTronTren(x, y, w, h, r) {
  if (h <= 0) return "M0 0";
  r = Math.min(r, h, w / 2);
  if (!r) return `M${x} ${y}h${w}v${h}h${-w}z`;
  return `M${x} ${y + h}V${y + r}a${r} ${r} 0 0 1 ${r} ${-r}h${w - 2 * r}a${r} ${r} 0 0 1 ${r} ${r}V${y + h}z`;
}

/* (b) Dải chấm: mỗi em một chấm theo điểm quyết tâm đã đặt. Chấm đặc xanh = được nhận,
   chấm rỗng xám = không được nhận. Chạm hay di chuột vào chấm: hiện mã và điểm. */
function veDaiChamQuyetTam(goc, d) {
  clear(goc);
  const cap = document.createElement("figcaption");
  cap.textContent = t("dc_cham_tieu_de", { ten: d.ten });
  goc.appendChild(cap);
  if (!d.em.length) {
    const p = document.createElement("p");
    p.className = "hint-text";
    p.textContent = t("dc_rong_bieu_do");
    goc.appendChild(p);
    return;
  }
  const W = 560, L = 20, R = 20, BK = 4.5;
  const em = d.em.slice().sort((a, b) => a.diem - b.diem || (a.student_id < b.student_id ? -1 : 1));
  const xv = (v) => L + (v / 100) * (W - L - R);
  /* Xếp chồng: chấm nào chạm chấm trước thì nhích lên một bậc. */
  const cot = [];
  const vitri = em.map((e) => {
    const px = xv(e.diem);
    let bac = 0;
    while (cot.some((c) => c.bac === bac && Math.abs(c.px - px) < 2 * BK + 2)) bac += 1;
    cot.push({ px, bac });
    return { e, px, bac };
  });
  const toiDa = Math.max(...vitri.map((v) => v.bac));
  const BUOC = Math.max(5, Math.min(11, 200 / (toiDa + 1)));
  const yTren = 34, yDuoi = yTren + 16 + (toiDa + 1) * BUOC, H = yDuoi + 44;
  const id = "dcCham" + (++dcUid);
  const svg = dcSvg("svg", { class: "dc-svg", viewBox: `0 0 ${W} ${H}`, role: "img",
                             "aria-labelledby": id + "T", "data-bieu-do": "cham" });
  dcSvg("title", { id: id + "T" }, svg).textContent = t("dc_cham_tieu_de", { ten: d.ten });
  for (let v = 0; v <= 100; v += 20) {
    dcSvg("line", { class: "dc-luoi", x1: xv(v), x2: xv(v), y1: yTren, y2: yDuoi }, svg);
  }
  dcSvg("line", { class: "dc-luoi", x1: L, x2: W - R, y1: yDuoi, y2: yDuoi }, svg);
  const x = dcThangX(svg, W, L, R, yTren, yDuoi);
  vitri.forEach(({ e, px, bac }) => {
    const py = yDuoi - 10 - bac * BUOC;
    const nhan = (e.ket_qua === "duoc" ? t("dc_duoc") : t("dc_khong"));
    dcSvg("circle", { class: e.ket_qua === "duoc" ? "dc-cham dc-cham-duoc" : "dc-cham dc-cham-khong",
                      cx: px, cy: py, r: BK, "data-student-id": e.student_id,
                      "data-diem": e.diem, "data-ket-qua": e.ket_qua }, svg);
    /* Vùng chạm lớn hơn chấm nhiều (24px), tới được bằng bàn phím. */
    const hit = dcSvg("circle", { class: "dc-vung-chi dc-cham-hit", cx: px, cy: py, r: 12, tabindex: 0,
                                  role: "img", "data-student-id": e.student_id,
                                  "aria-label": `${e.student_id} ${e.ho_ten}: ${dcSo(e.diem)}, ${nhan}` }, svg);
    ganTooltip(hit, () => ({
      tieu_de: e.student_id + (e.ho_ten ? " · " + e.ho_ten : ""),
      dong: [[t("dc_tooltip_diem"), dcSo(e.diem)], [t("dc_tooltip_kq"), nhan]],
    }));
  });
  dcVachChuan(svg, x, d.chuan, yTren, yDuoi, W);
  goc.appendChild(svg);
  dcChuGiaiDuoiKhong(goc, true);
  dcBangAn(goc, t("dc_cham_tieu_de", { ten: d.ten }),
           [t("th_student_id"), t("dc_tooltip_diem"), t("dc_tooltip_kq")],
           em.map((e) => [e.student_id, dcSo(e.diem), e.ket_qua === "duoc" ? t("dc_duoc") : t("dc_khong")]));
}

/* Bảng hai tầng x hai mức của MỘT CLB. */
function veBangHaiTang(goc, d) {
  clear(goc);
  const r = d.chuan;
  if (!r) return;
  const bang = document.createElement("table");
  bang.className = "data-table dc-bang-hai-tang";
  const cap = document.createElement("caption");
  cap.textContent = t("dc_bang_tieu_de", { ten: d.ten });
  bang.appendChild(cap);
  const h = bang.createTHead().insertRow();
  ["", "dc_thuong", "dc_du_tru"].forEach((k) => {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = k ? t(k) : "";
    h.appendChild(th);
  });
  const tb = bang.createTBody();
  [["dc_tang2", r.tang2, 2], ["dc_tang1", r.tang1, 1]].forEach(([khoa, muc, tang]) => {
    const tr = tb.insertRow();
    const th = document.createElement("th");
    th.scope = "row";
    th.textContent = t(khoa);
    tr.appendChild(th);
    [muc.thuong, muc.du_tru].forEach((m) => {
      const td = tr.insertCell();
      td.textContent = dcChuoiMuc(m, tang);
      if (!m) td.title = t("dc_khong_ai");
      td.dataset.tang = tang;
    });
  });
  goc.appendChild(bang);
  const tom = document.createElement("p");
  tom.className = "hint-text";
  tom.textContent = t("dc_tom_tat", { nhan: r.so_nhan, cho: r.suc_chua, don: r.so_don });
  goc.appendChild(tom);
}

/* ---- Tab Quản lý ---- */
function loadAdminDiemChuan() {
  return callApi("get_diem_chuan").then((res) => {
    const khoi = el("adminDiemChuanBlock");
    if (!khoi) return null;
    if (!res.ok) {
      khoi.hidden = true;
      dc.rows = null;
      return null;
    }
    khoi.hidden = false;
    dc.rows = res.data.rows;
    el("dcQlCu").hidden = !res.data.ket_qua_cu;
    el("dcQlRong").hidden = res.data.co_ket_qua;
    el("dcChonHop").hidden = !res.data.co_ket_qua;
    veTongQuanDiemChuan(el("dcQlTongQuan"), res.data.co_ket_qua ? dc.rows : []);
    el("dcQlTongQuan").hidden = !res.data.co_ket_qua;
    const sel = el("dcChonClb");
    const nhieu = res.data.nhieu_buoi;
    clear(sel);
    dc.rows.forEach((r) => {
      const o = document.createElement("option");
      o.value = r.club_id;
      o.textContent = dcTenDong(r, nhieu);
      sel.appendChild(o);
    });
    if (!dc.rows.some((r) => r.club_id === dc.chon)) dc.chon = dc.rows.length ? dc.rows[0].club_id : "";
    sel.value = dc.chon;
    return loadChiTietDiemChuan();
  });
}

function loadChiTietDiemChuan() {
  const hop = el("dcChiTiet");
  if (!dc.chon || !dc.rows || !dc.rows.length) {
    hop.hidden = true;
    return Promise.resolve(null);
  }
  return callApi("get_diem_chuan_clb", dc.chon).then((res) => {
    if (!res.ok) {
      hop.hidden = true;
      return null;
    }
    dc.ct = res.data;
    hop.hidden = false;
    veBangHaiTang(el("dcBang"), res.data);
    veCotPhanBoQuyetTam(el("dcCot"), res.data);
    veDaiChamQuyetTam(el("dcCham"), res.data);
    const kx = el("dcKhongXet");
    kx.hidden = !res.data.so_khong_xet;
    kx.textContent = res.data.so_khong_xet ? t("dc_khong_xet", { n: res.data.so_khong_xet }) : "";
    return res.data;
  });
}

function initDiemChuan() {
  const chon = el("dcChonClb");
  if (chon) {
    chon.addEventListener("change", () => {
      dc.chon = chon.value;
      loadChiTietDiemChuan();
    });
  }
  const i = el("btnDcThongTin");
  if (i) {
    i.addEventListener("click", () => {
      const mo = el("dcThongTin").hidden;
      el("dcThongTin").hidden = !mo;
      i.setAttribute("aria-expanded", mo ? "true" : "false");
    });
  }
  initDiemChuanKetQua();
}

/* ---- Tab Kết quả: mục "Điểm chuẩn" LUÔN đóng mỗi lần vào thẻ ----
   Khác các mục thu gọn khác (`MUC_KET_QUA`): trạng thái mở KHÔNG được ghi nhớ, vì bảng này có
   điểm của người đã đặt và không nên hiện sẵn trên màn hình dùng chung. Rời thẻ là đóng ngay
   (theo dõi lớp `is-active` của thẻ, nên đi bằng nút hay bằng mã đều đóng). Đổi ngôn ngữ không
   đổi thẻ nên không đóng. */
function dongDiemChuanKq() {
  dc.moKq = false;
  const than = el("dcKqBody");
  const nut = el("btnDcKqMo");
  if (!than || !nut) return;
  than.hidden = true;
  nut.setAttribute("aria-expanded", "false");
  nut.textContent = t("dc_xem");
  clear(el("dcKqTongQuan"));
}

function veDiemChuanKetQua() {
  const panel = el("dcKqPanel");
  if (!panel) return Promise.resolve(null);
  return callApi("get_diem_chuan").then((res) => {
    if (!res.ok || !res.data.co_ket_qua) {
      panel.hidden = true;
      dc.rowsKq = null;
      dongDiemChuanKq();
      return null;
    }
    panel.hidden = false;
    dc.rowsKq = res.data.rows;
    el("dcKqCu").hidden = !res.data.ket_qua_cu;
    if (dc.moKq) veTongQuanDiemChuan(el("dcKqTongQuan"), dc.rowsKq);
    el("btnDcKqMo").textContent = t(dc.moKq ? "dc_an" : "dc_xem");
    return res.data;
  });
}

function initDiemChuanKetQua() {
  const nut = el("btnDcKqMo");
  if (!nut) return;
  nut.addEventListener("click", () => {
    dc.moKq = !dc.moKq;
    el("dcKqBody").hidden = !dc.moKq;
    nut.setAttribute("aria-expanded", dc.moKq ? "true" : "false");
    nut.textContent = t(dc.moKq ? "dc_an" : "dc_xem");
    if (dc.moKq) veTongQuanDiemChuan(el("dcKqTongQuan"), dc.rowsKq || []);
    else clear(el("dcKqTongQuan"));
  });
  const view = el("view-results");
  if (view && window.MutationObserver) {
    new MutationObserver(() => {
      if (!view.classList.contains("is-active")) dongDiemChuanKq();
    }).observe(view, { attributes: true, attributeFilter: ["class"] });
  }
}
