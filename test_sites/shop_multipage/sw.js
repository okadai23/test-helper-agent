/* Mock API Service Worker for Acme Shop */
const PRODUCTS = [
  { id: 1, name: "Acme Keyboard", price: 5980, description: "打鍵感にこだわったキーボード" },
  { id: 2, name: "Acme Mouse", price: 2980, description: "精密センサー搭載のマウス" },
  { id: 3, name: "Acme Headset", price: 7980, description: "ノイズキャンセリング対応ヘッドセット" },
  { id: 4, name: "Acme Monitor", price: 25800, description: "27インチ高解像度ディスプレイ" },
  { id: 5, name: "Acme USB Hub", price: 1980, description: "高速USBハブ" },
  { id: 6, name: "Acme Webcam", price: 4980, description: "高画質ウェブカメラ" },
];

// In-memory session storage: token -> { cart: {productId, name, price, qty}[] }
const SESSIONS = new Map();
const DEBUG = { force401: false, failCart: false, delay: 0 };

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));

function json(data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: { "Content-Type": "application/json" } });
}

async function readBody(req) { try { return await req.clone().json(); } catch { return {}; } }
function getToken(req) { const a = req.headers.get("Authorization") || ""; const m = a.match(/^Bearer\s+(.+)/); return m ? m[1] : null; }

function getSession(token) {
  if (!token) return null;
  if (!SESSIONS.has(token)) SESSIONS.set(token, { cart: [] });
  return SESSIONS.get(token);
}

function requireAuth(req) {
  const token = getToken(req); const sess = getSession(token);
  if (!token || !sess) return { error: true, res: json({ error: "Unauthorized" }, 401) };
  return { error: false, sess };
}

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (!url.pathname.startsWith("/api/")) return; // let network handle others

  event.respondWith((async () => {
    // Simulate network latency for E2E timing
    const delay = (ms) => new Promise(r => setTimeout(r, ms));
    await delay(80 + Math.random()*120 + (DEBUG.delay||0));

    if (url.pathname === "/api/__debug" && event.request.method === "POST") {
      const body = await readBody(event.request);
      DEBUG.force401 = !!body.force401;
      DEBUG.failCart = !!body.failCart;
      DEBUG.delay = Number(body.delay || 0);
      return json({ ok: true, DEBUG });
    }

    if (url.pathname === "/api/login" && event.request.method === "POST") {
      const body = await readBody(event.request);
      // Accept any non-empty email/password and issue a simple token
      if (!body.email || !body.password) return json({ error: "Invalid" }, 400);
      const token = `tok_${Math.random().toString(36).slice(2,10)}`;
      getSession(token); // init
      return json({ token });
    }

    if (url.pathname === "/api/products" && event.request.method === "GET") {
      return json(PRODUCTS);
    }

    if (url.pathname === "/api/cart" && event.request.method === "GET") {
      if (DEBUG.force401) return json({ error: "Unauthorized" }, 401);
      if (DEBUG.failCart) return json({ error: "Cart Failure" }, 500);
      const a = requireAuth(event.request); if (a.error) return a.res;
      const items = a.sess.cart;
      const total = items.reduce((n, i) => n + i.price * i.qty, 0);
      return json({ items, total });
    }

    if (url.pathname === "/api/cart" && event.request.method === "POST") {
      if (DEBUG.force401) return json({ error: "Unauthorized" }, 401);
      if (DEBUG.failCart) return json({ error: "Cart Failure" }, 500);
      const a = requireAuth(event.request); if (a.error) return a.res;
      const body = await readBody(event.request);
      const p = PRODUCTS.find(x => x.id === Number(body.productId));
      if (!p) return json({ error: "Not Found" }, 404);
      const exist = a.sess.cart.find(x => x.productId === p.id);
      if (exist) exist.qty += Number(body.qty || 1);
      else a.sess.cart.push({ productId: p.id, name: p.name, price: p.price, qty: Number(body.qty || 1) });
      const total = a.sess.cart.reduce((n, i) => n + i.price * i.qty, 0);
      return json({ items: a.sess.cart, total });
    }

    if (url.pathname.startsWith("/api/cart/") && event.request.method === "DELETE") {
      if (DEBUG.force401) return json({ error: "Unauthorized" }, 401);
      if (DEBUG.failCart) return json({ error: "Cart Failure" }, 500);
      const a = requireAuth(event.request); if (a.error) return a.res;
      const id = Number(url.pathname.split("/").pop());
      a.sess.cart = a.sess.cart.filter(i => i.productId !== id);
      const total = a.sess.cart.reduce((n, i) => n + i.price * i.qty, 0);
      return json({ items: a.sess.cart, total });
    }

    if (url.pathname === "/api/checkout" && event.request.method === "POST") {
      if (DEBUG.force401) return json({ error: "Unauthorized" }, 401);
      if (DEBUG.failCart) return json({ error: "Cart Failure" }, 500);
      const a = requireAuth(event.request); if (a.error) return a.res;
      const orderId = `ORD-${Math.random().toString(36).slice(2,7).toUpperCase()}`;
      a.sess.cart = [];
      return json({ ok: true, orderId });
    }

    return json({ error: "Not Found" }, 404);
  })());
});
