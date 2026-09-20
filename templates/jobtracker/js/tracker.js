(function () {
  "use strict";

  const CFG = window.TRACKER_CONFIG;
  const { apiRequest, requireAuth, logout } = window.Auth;

  requireAuth();

  // Status/round choices + status colors are kept here client-side (the API
  // returns status/round as plain values + a *_display label, not colors —
  // presentation is a frontend concern). Keep these in sync with
  // apps/jobtracker/choices.py if that ever changes.
  const STATUS_CHOICES = [
    ["applied", "Applied"], ["interviewing", "Interviewing"],
    ["final_round", "Final Round"], ["offer", "Offer"],
    ["rejected", "Rejected"], ["withdrawn", "Withdrawn"],
  ];
  const STATUS_COLORS = {
    applied: { bg: "#94a3b8", fg: "#1e293b" },
    interviewing: { bg: "#fde68a", fg: "#78350f" },
    final_round: { bg: "#a5f3fc", fg: "#164e63" },
    offer: { bg: "#86efac", fg: "#14532d" },
    rejected: { bg: "#fca5a5", fg: "#7f1d1d" },
    withdrawn: { bg: "#e5e7eb", fg: "#374151" },
  };
  const ROUND_CHOICES = [
    ["na", "NA"], ["1", "1st round"], ["2", "2nd round"], ["3", "3rd round"],
    ["4", "4th round"], ["5", "5th round"], ["6", "6th round"], ["final", "Final round"],
  ];

  const state = { boards: [], activeBoardId: null, page: 1, pageSize: 10, lastResult: null };

  function boardUrl(id) { return CFG.urls.boardItem.replace("__id__", id); }
  function applicationUrl(id) { return CFG.urls.applicationItem.replace("__id__", id); }
  function debounce(fn, wait) {
    let t;
    return function (...args) { clearTimeout(t); t = setTimeout(() => fn.apply(this, args), wait); };
  }
  function fmtMoney(v) {
    if (v === "" || v === null || v === undefined) return "";
    const n = Number(v);
    return Number.isNaN(n) ? v : n.toLocaleString(undefined, { maximumFractionDigits: 0 });
  }

  async function loadBoards() {
    const boards = await apiRequest(CFG.urls.boards);
    state.boards = boards;
    if (!state.activeBoardId || !boards.find((b) => b.id === state.activeBoardId)) {
      state.activeBoardId = boards.length ? boards[0].id : null;
    }
    renderTabs();
  }

  async function loadApplications() {
    if (!state.activeBoardId) {
      document.getElementById("subtitle").textContent = "No boards yet — create one to get started.";
      document.getElementById("stats").innerHTML = "";
      renderTable({ results: [] });
      renderPagination(null);
      return;
    }
    const params = new URLSearchParams({ board: state.activeBoardId, page: state.page, page_size: state.pageSize });
    const data = await apiRequest(`${CFG.urls.applications}?${params.toString()}`);
    state.lastResult = data;
    renderTable(data);
    renderPagination(data);
    renderStats(data);
  }

  async function renderStats(data) {
    document.getElementById("subtitle").textContent =
      `${data.count} application${data.count === 1 ? "" : "s"} on this tab`;
    const counts = { active: 0, offers: 0, rejected: 0 };
    for (const status of ["interviewing", "final_round", "offer", "rejected"]) {
      const params = new URLSearchParams({ board: state.activeBoardId, page_size: 1, status });
      const res = await apiRequest(`${CFG.urls.applications}?${params.toString()}`);
      if (status === "interviewing" || status === "final_round") counts.active += res.count;
      if (status === "offer") counts.offers += res.count;
      if (status === "rejected") counts.rejected += res.count;
    }
    const el = document.getElementById("stats");
    el.innerHTML = "";
    const cards = [
      { label: "Total", value: data.count, bg: "#fff", color: "#0f172a" },
      { label: "Active", value: counts.active, bg: "#fde68a", color: "#78350f" },
      { label: "Offers", value: counts.offers, bg: "#86efac", color: "#14532d" },
      { label: "Rejected", value: counts.rejected, bg: "#fca5a5", color: "#7f1d1d" },
    ];
    for (const c of cards) {
      const div = document.createElement("div");
      div.className = "stat-card";
      div.style.background = c.bg;
      div.innerHTML = `<div class="value" style="color:${c.color}">${c.value}</div><div class="label" style="color:${c.bg === "#fff" ? "#64748b" : c.color}">${c.label}</div>`;
      el.appendChild(div);
    }
  }

  function renderTable(data) {
    const body = document.getElementById("table-body");
    body.innerHTML = "";
    if (!data.results.length) {
      body.innerHTML = '<tr><td colspan="7" class="empty-cell">No applications yet — add your first row below.</td></tr>';
      return;
    }
    for (const row of data.results) body.appendChild(renderRow(row));
  }

  function renderRow(row) {
    const tr = document.createElement("tr");
    tr.dataset.id = row.id;
    tr.appendChild(textCell(row, "company", "Company"));
    tr.appendChild(textCell(row, "position", "Position"));
    tr.appendChild(statusCell(row));
    tr.appendChild(salaryCell(row));
    tr.appendChild(roundCell(row));
    tr.appendChild(textCell(row, "notes", "Notes"));
    tr.appendChild(deleteCell(row));
    return tr;
  }

  function textCell(row, field, placeholder) {
    const td = document.createElement("td");
    const input = document.createElement("input");
    input.type = "text"; input.className = "cell-input"; input.placeholder = placeholder;
    input.value = row[field] || "";
    input.addEventListener("input", debounce(() => patchApplication(row.id, { [field]: input.value }), 400));
    td.appendChild(input);
    return td;
  }

  function salaryCell(row) {
    const td = document.createElement("td");
    const input = document.createElement("input");
    input.type = "text"; input.className = "cell-input"; input.placeholder = "$0";
    input.value = row.salary ? fmtMoney(row.salary) : "";
    input.addEventListener("focus", () => { input.value = row.salary || ""; });
    input.addEventListener("blur", () => { input.value = input.value ? fmtMoney(input.value) : ""; });
    input.addEventListener("input", debounce(() => {
      const raw = input.value.replace(/[^0-9.]/g, "");
      patchApplication(row.id, { salary: raw || null });
    }, 400));
    td.appendChild(input);
    return td;
  }

  function roundCell(row) {
    const td = document.createElement("td");
    const select = document.createElement("select");
    select.className = "round-select";
    for (const [value, label] of ROUND_CHOICES) {
      const opt = document.createElement("option");
      opt.value = value; opt.textContent = label;
      if (value === row.round) opt.selected = true;
      select.appendChild(opt);
    }
    select.addEventListener("change", () => patchApplication(row.id, { round: select.value }));
    td.appendChild(select);
    return td;
  }

  function deleteCell(row) {
    const td = document.createElement("td");
    const btn = document.createElement("button");
    btn.className = "delete-btn"; btn.innerHTML = "&#10005;"; btn.title = "Delete";
    btn.addEventListener("click", async () => {
      await apiRequest(applicationUrl(row.id), { method: "DELETE" });
      await loadApplications();
      await loadBoards();
    });
    td.appendChild(btn);
    return td;
  }

  // --------------------------------------------- status dropdown (fix) --
  function statusCell(row) {
    const td = document.createElement("td");
    const trigger = document.createElement("button");
    trigger.type = "button"; trigger.className = "status-trigger";
    const colors = STATUS_COLORS[row.status] || STATUS_COLORS.applied;
    trigger.style.background = colors.bg; trigger.style.color = colors.fg;
    trigger.innerHTML = `<span>${row.status_display}</span><span class="chev">&#9662;</span>`;
    trigger.addEventListener("click", () => openStatusMenu(trigger, row));
    td.appendChild(trigger);
    return td;
  }

  function closeStatusMenu() { document.getElementById("status-dropdown-portal").innerHTML = ""; }

  function openStatusMenu(trigger, row) {
    const portal = document.getElementById("status-dropdown-portal");
    portal.innerHTML = "";
    const backdrop = document.createElement("div");
    backdrop.className = "status-menu-backdrop";
    backdrop.addEventListener("click", closeStatusMenu);
    portal.appendChild(backdrop);

    const rect = trigger.getBoundingClientRect();
    const menu = document.createElement("div");
    menu.className = "status-menu";
    menu.style.top = `${rect.bottom + 4}px`;
    menu.style.left = `${rect.left}px`;
    menu.style.minWidth = `${Math.max(rect.width, 150)}px`;

    for (const [value, label] of STATUS_CHOICES) {
      const colors = STATUS_COLORS[value];
      const item = document.createElement("div");
      item.className = "status-menu-item"; item.textContent = label; item.style.color = colors.fg;
      item.style.background = value === row.status ? colors.bg : "#fff";
      item.addEventListener("mouseenter", () => (item.style.background = colors.bg));
      item.addEventListener("mouseleave", () => (item.style.background = value === row.status ? colors.bg : "#fff"));
      item.addEventListener("click", async () => {
        closeStatusMenu();
        await patchApplication(row.id, { status: value });
        await loadApplications();
      });
      menu.appendChild(item);
    }
    portal.appendChild(menu);

    const menuRect = menu.getBoundingClientRect();
    if (menuRect.bottom > window.innerHeight) menu.style.top = `${rect.top - menuRect.height - 4}px`;
  }

  async function patchApplication(id, patch) {
    await apiRequest(applicationUrl(id), { method: "PATCH", body: JSON.stringify(patch) });
  }

  // ---------------------------------------------------------- pagination --
  function renderPagination(data) {
    const el = document.getElementById("pagination");
    el.innerHTML = "";
    if (!data || data.count === 0) return;

    const prev = document.createElement("button");
    prev.textContent = "Prev"; prev.disabled = !data.has_previous;
    prev.addEventListener("click", () => { state.page = data.current_page - 1; loadApplications(); });
    el.appendChild(prev);

    const maxButtons = 7;
    let start = Math.max(1, data.current_page - Math.floor(maxButtons / 2));
    let end = Math.min(data.num_pages, start + maxButtons - 1);
    start = Math.max(1, end - maxButtons + 1);
    for (let p = start; p <= end; p++) {
      const btn = document.createElement("button");
      btn.textContent = p;
      if (p === data.current_page) btn.classList.add("active");
      btn.addEventListener("click", () => { state.page = p; loadApplications(); });
      el.appendChild(btn);
    }

    const next = document.createElement("button");
    next.textContent = "Next"; next.disabled = !data.has_next;
    next.addEventListener("click", () => { state.page = data.current_page + 1; loadApplications(); });
    el.appendChild(next);

    const info = document.createElement("span");
    info.className = "page-info";
    info.textContent = `Page ${data.current_page} of ${data.num_pages} · ${data.count} total`;
    el.appendChild(info);

    const sizeSelect = document.createElement("select");
    for (const size of [10, 25, 50, 100]) {
      const opt = document.createElement("option");
      opt.value = size; opt.textContent = `${size} / page`;
      if (size === state.pageSize) opt.selected = true;
      sizeSelect.appendChild(opt);
    }
    sizeSelect.addEventListener("change", () => {
      state.pageSize = Number(sizeSelect.value); state.page = 1; loadApplications();
    });
    el.appendChild(sizeSelect);
  }



  // --------------------------------------------------------------- tabs --
  function updateAddRowButton() {
  const btn = document.getElementById("add-row-btn");
    if (state.boards.length === 0) {
      btn.disabled = true;
      btn.textContent = "Create a board above to start adding applications";
    } else {
      btn.disabled = false;
      btn.textContent = "+ Add application";
    }
  }

  function renderTabs() {
    updateAddRowButton();
    const el = document.getElementById("tabs");
    el.innerHTML = "";

    for (const board of state.boards) {
      const tab = document.createElement("div");
      tab.className = "tab" + (board.id === state.activeBoardId ? " active" : "");

      const nameSpan = document.createElement("span");
      nameSpan.className = "tab-name"; nameSpan.textContent = board.name;
      nameSpan.addEventListener("click", () => {
        if (state.activeBoardId === board.id) return;
        state.activeBoardId = board.id; state.page = 1;
        renderTabs(); loadApplications();
      });
      nameSpan.addEventListener("dblclick", (e) => { e.stopPropagation(); startRename(tab, board); });
      tab.appendChild(nameSpan);

      if (state.boards.length > 1) {
        const close = document.createElement("span");
        close.className = "tab-close"; close.innerHTML = "&#10005;";
        close.addEventListener("click", async (e) => {
          e.stopPropagation();
          try {
            await apiRequest(boardUrl(board.id), { method: "DELETE" });
          } catch (err) { alert(err.message); return; }
          if (state.activeBoardId === board.id) state.activeBoardId = null;
          state.page = 1;
          await loadBoards(); await loadApplications();
        });
        tab.appendChild(close);
      }
      el.appendChild(tab);
    }

    const addBtn = document.createElement("button");
    addBtn.className = "tab-add"; addBtn.textContent = "+ New tab";
    addBtn.addEventListener("click", openBoardModal);
    el.appendChild(addBtn);
  }

  function startRename(tabEl, board) {
    tabEl.innerHTML = "";
    const input = document.createElement("input");
    input.className = "tab-rename-input"; input.value = board.name;
    tabEl.appendChild(input); input.focus(); input.select();

    const commit = async () => {
      const name = input.value.trim() || board.name;
      await apiRequest(boardUrl(board.id), { method: "PATCH", body: JSON.stringify({ name }) });
      await loadBoards();
    };
    input.addEventListener("blur", commit);
    input.addEventListener("keydown", (e) => { if (e.key === "Enter") input.blur(); });
  }

  // ------------------------------------------------------- new board modal --
  const boardModal = {};

  function initBoardModal() {
    boardModal.backdrop = document.getElementById("board-modal-backdrop");
    boardModal.input = document.getElementById("board-modal-input");
    boardModal.error = document.getElementById("board-modal-error");
    boardModal.submitBtn = document.getElementById("board-modal-submit");

    document.getElementById("board-modal-cancel").addEventListener("click", closeBoardModal);
    boardModal.backdrop.addEventListener("click", (e) => { if (e.target === boardModal.backdrop) closeBoardModal(); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !boardModal.backdrop.hidden) closeBoardModal(); });
    boardModal.submitBtn.addEventListener("click", submitBoardModal);
    boardModal.input.addEventListener("keydown", (e) => { if (e.key === "Enter") submitBoardModal(); });
  }

  function openBoardModal() {
    boardModal.input.value = ""; boardModal.error.hidden = true;
    boardModal.backdrop.hidden = false; boardModal.input.focus();
  }
  function closeBoardModal() { boardModal.backdrop.hidden = true; }

  async function submitBoardModal() {
    boardModal.error.hidden = true; boardModal.submitBtn.disabled = true;
    try {
      const created = await apiRequest(CFG.urls.boards, {
        method: "POST",
        body: JSON.stringify({ name: boardModal.input.value.trim() }),
      });
      closeBoardModal();
      state.activeBoardId = created.id; state.page = 1;
      await loadBoards(); await loadApplications();
    } catch (err) {
      boardModal.error.textContent = err.message; boardModal.error.hidden = false;
    } finally {
      boardModal.submitBtn.disabled = false;
    }
  }

  // ------------------------------------------------------------- add row --
  document.getElementById("add-row-btn").addEventListener("click", async () => {
    if (!state.activeBoardId) return;
    await apiRequest(CFG.urls.applications, {
      method: "POST",
      body: JSON.stringify({ board: state.activeBoardId, status: "applied", round: "na" }),
    });
    const params = new URLSearchParams({ board: state.activeBoardId, page: 1, page_size: state.pageSize });
    const peek = await apiRequest(`${CFG.urls.applications}?${params.toString()}`);
    state.page = peek.num_pages;
    await loadApplications(); await loadBoards();
  });

  document.getElementById("logout-btn").addEventListener("click", logout);

  (async function init() {
    initBoardModal();
    await loadBoards();
    await loadApplications();
  })();
})();