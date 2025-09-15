// Register SW for mock API
async function registerSW() {
  if ("serviceWorker" in navigator) {
    try { await navigator.serviceWorker.register("./sw.js", { scope: "./" }); }
    catch { /* ignore */ }
  }
}

const store = {
  get token() { return localStorage.getItem("shop_token") ?? ""; },
  set token(t) { if (t) localStorage.setItem("shop_token", t); else localStorage.removeItem("shop_token"); },
};

async function api(path, opts = {}) {
  const headers = Object.assign({ "Content-Type": "application/json" }, opts.headers || {});
  if (store.token) headers["Authorization"] = `Bearer ${store.token}`;
  const res = await fetch(path, { ...opts, headers });
  if (res.status === 401) { location.href = "login.html"; return Promise.reject(new Error("Unauthorized")); }
  if (!res.ok) throw new Error("API error");
  return res.json();
}

function qs(name) {
  const u = new URL(location.href); return u.searchParams.get(name);
}

async function refreshCartCount() {
  try {
    const { items } = await api("/api/cart");
    const count = items.reduce((n, i) => n + i.qty, 0);
    document.getElementById("cart-count").textContent = String(count);
  } catch { document.getElementById("cart-count").textContent = "0"; }
}

function updateAccountLink() {
  const el = document.getElementById("account-link");
  if (!el) return;
  if (store.token) { el.textContent = "ログアウト"; el.href = "#"; el.onclick = () => { store.token = ""; location.href = "login.html"; }; }
  else { el.textContent = "ログイン"; el.href = "login.html"; el.onclick = null; }
}

async function pageIndex() {
  const list = document.getElementById("products");
  const data = await api("/api/products");
  list.innerHTML = "";
  for (const p of data) {
    const card = document.createElement("article");
    card.className = "card";
    card.innerHTML = `
      <h3>${p.name}</h3>
      <p class="price">¥${p.price.toLocaleString()}</p>
      <div>
        <a class="btn" href="product.html?id=${p.id}" data-testid="go-detail-${p.id}">詳細</a>
        <button class="btn" data-add="${p.id}" data-testid="add-${p.id}">カートに追加</button>
      </div>
    `;
    list.appendChild(card);
  }
  list.addEventListener("click", async (e) => {
    const t = e.target; if (!(t instanceof HTMLElement)) return;
    const id = t.getAttribute("data-add"); if (!id) return;
    await api("/api/cart", { method: "POST", body: JSON.stringify({ productId: Number(id), qty: 1 }) });
    await refreshCartCount();
  });
}

async function pageProduct() {
  const id = Number(qs("id"));
  const p = (await api("/api/products")).find(x => x.id === id);
  const root = document.getElementById("product");
  if (!p) { root.textContent = "商品が見つかりません"; return; }
  root.innerHTML = `
    <h2>${p.name}</h2>
    <p>${p.description}</p>
    <p class="price">¥${p.price.toLocaleString()}</p>
    <button class="btn" id="add" data-testid="detail-add">カートに追加</button>
  `;
  document.getElementById("add").addEventListener("click", async () => {
    await api("/api/cart", { method: "POST", body: JSON.stringify({ productId: p.id, qty: 1 }) });
    await refreshCartCount();
  });
}

async function pageCart() {
  const root = document.getElementById("cart");
  async function render() {
    const cart = await api("/api/cart");
    root.innerHTML = "";
    for (const item of cart.items) {
      const row = document.createElement("div");
      row.className = "cart-item";
      row.innerHTML = `
        <div>${item.name} × ${item.qty}</div>
        <div class="right price">¥${(item.price * item.qty).toLocaleString()}</div>
        <div class="right"><button class="btn" data-remove="${item.productId}" data-testid="remove-${item.productId}">削除</button></div>
      `;
      root.appendChild(row);
    }
    const total = document.createElement("div");
    total.className = "right";
    total.innerHTML = `<strong>合計: <span class="price">¥${cart.total.toLocaleString()}</span></strong>`;
    root.appendChild(total);
  }
  root.addEventListener("click", async (e) => {
    const t = e.target; if (!(t instanceof HTMLElement)) return;
    const id = t.getAttribute("data-remove"); if (!id) return;
    await api(`/api/cart/${id}`, { method: "DELETE" });
    await render(); await refreshCartCount();
  });
  await render();
}

async function pageCheckout() {
  const form = document.getElementById("checkout-form");
  const result = document.getElementById("checkout-result");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const ok = await api("/api/checkout", { method: "POST", body: JSON.stringify({}) });
    result.textContent = ok.ok ? `注文が確定しました (注文番号: ${ok.orderId})` : "失敗しました";
    await refreshCartCount();
  });
}

async function pageLogin() {
  const form = document.getElementById("login-form");
  const result = document.getElementById("login-result");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const resp = await api("/api/login", { method: "POST", body: JSON.stringify({ email, password }) });
    store.token = resp.token;
    result.textContent = "ログインしました。商品一覧に移動します。";
    setTimeout(()=> location.href = "index.html", 400);
  });
}

window.addEventListener("DOMContentLoaded", async () => {
  await registerSW();
  updateAccountLink();
  refreshCartCount();
  const path = location.pathname.split("/").pop() || "index.html";
  if (path === "index.html") pageIndex();
  if (path === "product.html") pageProduct();
  if (path === "cart.html") pageCart();
  if (path === "checkout.html") pageCheckout();
  if (path === "login.html") pageLogin();
});

