const STORAGE_KEY = "mini_tasks_v1";

const state = {
  tasks: [],
  filter: "all", // all | active | completed
  search: "",
  sort: "created", // created | priority | title
  editingId: null,
};

function save() { localStorage.setItem(STORAGE_KEY, JSON.stringify(state.tasks)); }
function load() {
  try { state.tasks = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "[]"); }
  catch (e) { console.warn("Corrupted tasks data in localStorage:", e); state.tasks = []; }
}

function uid() { return Math.random().toString(36).slice(2, 10); }
function now() { return Date.now(); }

function render() {
  const list = document.getElementById("task-list");
  if (!list) return;
  list.innerHTML = "";

  let items = [...state.tasks];
  if (state.filter === "active") items = items.filter(t => !t.done);
  if (state.filter === "completed") items = items.filter(t => t.done);
  if (state.search) items = items.filter(t => t.title.toLowerCase().includes(state.search));
  if (state.sort === "priority") {
    const rank = { high: 0, medium: 1, low: 2 };
    items.sort((a,b)=> rank[a.priority]-rank[b.priority]);
  } else if (state.sort === "title") {
    items.sort((a,b)=> a.title.localeCompare(b.title));
  } else {
    items.sort((a,b)=> a.createdAt - b.createdAt);
  }

  for (const t of items) {
    const li = document.createElement("li");
    li.className = "task-item";
    li.dataset.testid = `task-${t.id}`;

    const chk = document.createElement("input");
    chk.type = "checkbox"; chk.checked = !!t.done; chk.setAttribute("data-testid", `task-done-${t.id}`);
    chk.addEventListener("change", () => { t.done = chk.checked; save(); render(); });

    const title = document.createElement("div");
    title.className = "task-title" + (t.done ? " done" : "");
    title.textContent = t.title;

    const meta = document.createElement("span");
    meta.className = `badge ${t.priority}`;
    meta.textContent = t.priority;

    const left = document.createElement("div");
    left.appendChild(title); left.appendChild(document.createTextNode(" ")); left.appendChild(meta);

    const actions = document.createElement("div");
    actions.className = "actions";

    const editBtn = document.createElement("button");
    editBtn.textContent = "編集"; editBtn.setAttribute("data-testid", `task-edit-${t.id}`);
    editBtn.addEventListener("click", () => startEdit(t.id));

    const delBtn = document.createElement("button");
    delBtn.textContent = "削除"; delBtn.setAttribute("data-testid", `task-delete-${t.id}`);
    delBtn.addEventListener("click", () => confirmDelete(t.id));

    actions.appendChild(editBtn); actions.appendChild(delBtn);

    li.appendChild(chk);
    li.appendChild(left);
    li.appendChild(actions);
    list.appendChild(li);
  }
}

function startEdit(id) {
  const t = state.tasks.find(x => x.id === id); if (!t) return;
  const title = document.getElementById("task-title");
  const priority = document.getElementById("task-priority");
  title.value = t.title; priority.value = t.priority; state.editingId = id;
  title.focus();
}

function confirmDelete(id) {
  const dialog = document.getElementById("confirm-dialog");
  dialog.showModal();
  const onClose = (e) => {
    dialog.removeEventListener("close", onClose);
    if (dialog.returnValue === "ok") {
      state.tasks = state.tasks.filter(t => t.id !== id); save(); render();
    }
  };
  dialog.addEventListener("close", onClose);
}

function handleRoute() {
  const hash = location.hash || "#/all";
  document.querySelectorAll(".tabs a").forEach(a => a.classList.remove("active"));
  const link = document.querySelector(`.tabs a[href='${hash}']`);
  link?.classList.add("active");
  state.filter = hash.replace("#/", "");
  render();
}

function applyFixturesFromQuery() {
  const u = new URL(location.href);
  const fixture = u.searchParams.get("fixture"); // empty|few|many
  const corrupt = u.searchParams.get("corrupt");
  if (corrupt === "1") {
    localStorage.setItem(STORAGE_KEY, "{invalid json]");
  } else if (fixture) {
    if (fixture === "empty") {
      localStorage.setItem(STORAGE_KEY, JSON.stringify([]));
    } else if (fixture === "few") {
      localStorage.setItem(STORAGE_KEY, JSON.stringify([
        { id: "a1", title: "メール確認", priority: "medium", done: false, createdAt: now()-3000 },
        { id: "a2", title: "資料ドラフト作成", priority: "high", done: false, createdAt: now()-2000 },
        { id: "a3", title: "レビュー", priority: "low", done: true, createdAt: now()-1000 },
      ]));
    } else if (fixture === "many") {
      const arr = [];
      for (let i=1;i<=25;i++) arr.push({ id: uid(), title: `タスク${i}`, priority: i%3===0?"high":(i%3===1?"medium":"low"), done: i%4===0, createdAt: now()-i*1000 });
      localStorage.setItem(STORAGE_KEY, JSON.stringify(arr));
    }
  }
}

window.addEventListener("DOMContentLoaded", () => {
  applyFixturesFromQuery();
  load();

  document.getElementById("task-form")?.addEventListener("submit", (e) => {
    e.preventDefault();
    const title = document.getElementById("task-title");
    const priority = document.getElementById("task-priority");
    const t = title.value.trim(); if (!t) return;

    if (state.editingId) {
      const item = state.tasks.find(x => x.id === state.editingId);
      if (item) { item.title = t; item.priority = priority.value; }
      state.editingId = null;
    } else {
      state.tasks.push({ id: uid(), title: t, priority: priority.value, done: false, createdAt: now() });
    }
    save(); title.value = ""; render();
  });

  document.getElementById("search")?.addEventListener("input", (e) => {
    state.search = e.target.value.toLowerCase(); render();
  });
  document.getElementById("sort")?.addEventListener("change", (e) => { state.sort = e.target.value; render(); });
  window.addEventListener("hashchange", handleRoute);
  const initialHash = new URL(location.href).searchParams.get("route");
  if (initialHash) location.hash = initialHash;
  handleRoute();
});
