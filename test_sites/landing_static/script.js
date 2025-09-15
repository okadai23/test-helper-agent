(() => {
  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  // Mobile nav toggle
  const toggle = document.querySelector(".nav-toggle");
  const navList = document.getElementById("nav-list");
  toggle?.addEventListener("click", () => {
    const open = navList?.classList.toggle("open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });

  // Carousel controls
  const slides = Array.from(document.querySelectorAll(".slide"));
  let idx = 0;
  const show = (i) => {
    slides.forEach((s, si) => {
      const active = si === i;
      s.classList.toggle("active", active);
      s.setAttribute("aria-hidden", active ? "false" : "true");
    });
  };
  document.getElementById("prev")?.addEventListener("click", () => {
    idx = (idx - 1 + slides.length) % slides.length;
    show(idx);
  });
  document.getElementById("next")?.addEventListener("click", () => {
    idx = (idx + 1) % slides.length;
    show(idx);
  });
  if (slides.length) setInterval(() => { idx = (idx + 1) % slides.length; show(idx); }, 5000);

  // Contact form fake submit with validation
  const form = document.getElementById("contact-form");
  const result = document.getElementById("contact-result");
  form?.addEventListener("submit", (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    const name = String(fd.get("name") ?? "").trim();
    const email = String(fd.get("email") ?? "").trim();
    const message = String(fd.get("message") ?? "").trim();
    if (!name || !email.includes("@") || !message) {
      result.textContent = "入力内容をご確認ください。";
      result.style.color = "#fca5a5";
      return;
    }
    result.textContent = "送信が完了しました。担当者よりご連絡いたします。";
    result.style.color = "#94a3b8";
    form.reset();
  });
})();

