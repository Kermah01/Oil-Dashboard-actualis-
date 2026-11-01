/* AMONT·CI — utilitaires partagés (thèmes clair & sombre) */
const D = JSON.parse(document.getElementById("bundle").textContent);
const DARK_S = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"];
const LIGHT_S = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"];
const THEMES = {
  light: { text: "#0f172a", text2: "#475569", muted: "#64748b", line: "rgba(15,23,42,.08)", surface: "#ffffff", accent: "#e8750f", amber: "#e8750f",
    libre: "#b4bdca", surface2: "#e8edf4", tip: "rgba(255,255,255,.97)", tipBorder: "rgba(15,23,42,.12)", pointer: "rgba(15,23,42,.25)",
    seq: ["#fde7cf", "#f9c48d", "#f29a45", "#d9700f", "#9a4a06"], blues: ["#eaf2fd", "#9cc7ff", "#3987e5", "#1e4a8a"], land: "#eef2f6", land2: "#f8fafc", landLine: "#c3ccd8" },
  dark: { text: "#f1f5fb", text2: "#b6c2d6", muted: "#8a97ad", line: "rgba(203,213,225,.10)", surface: "#1f2a43", accent: "#f59a3c", amber: "#ffb766",
    libre: "#56627a", surface2: "#2e3b5a", tip: "rgba(31,42,67,.97)", tipBorder: "rgba(203,213,225,.22)", pointer: "rgba(255,255,255,.3)",
    seq: ["#3d3324", "#6e4a1f", "#a8661e", "#de8a2b", "#ffc277"], blues: ["#22304d", "#1e4a8a", "#3987e5", "#9cc7ff"], land: "#24314d", land2: "#1d2840", landLine: "#3c4b6c" },
};
const C = { s: [] };
const STATUT = {
  production: { l: "En production" }, exploration: { l: "En exploration" }, nouveau: { l: "Attribué en 2025-2026" },
  libre: { l: "Libre" }, evaluation: { l: "En évaluation" },
};
let CHAMP_COL = {};
D.champs.forEach(c => c._c = c.couleur);
D.acteurs.forEach(a => a._c = a.couleur);
const themeColor = hex => { const i = DARK_S.indexOf(hex); return i < 0 ? hex : C.s[i]; };
const _themeCbs = [];
function onTheme(fn) { _themeCbs.push(fn); }
function applyTheme(t) {
  document.documentElement.dataset.theme = t;
  Object.assign(C, THEMES[t], { s: t === "dark" ? DARK_S : LIGHT_S, mode: t, gas: t === "dark" ? "#38bdf8" : "#0284c7" });
  Object.assign(STATUT.production, { c: C.s[1] }); Object.assign(STATUT.exploration, { c: C.s[0] });
  Object.assign(STATUT.nouveau, { c: C.s[2] }); Object.assign(STATUT.libre, { c: C.libre }); Object.assign(STATUT.evaluation, { c: C.s[6] });
  D.champs.forEach(c => c.couleur = themeColor(c._c));
  D.acteurs.forEach(a => a.couleur = themeColor(a._c));
  CHAMP_COL = Object.fromEntries(D.champs.map(c => [c.nom, c.couleur]));
}
applyTheme(document.documentElement.dataset.theme === "dark" ? "dark" : "light");
document.getElementById("theme-btn")?.addEventListener("click", () => {
  const t = C.mode === "dark" ? "light" : "dark";
  try { localStorage.setItem("amont-theme", t); } catch (e) {}
  applyTheme(t);
  _themeCbs.forEach(fn => fn(t));
});
const MOIS = ["Janv.", "Févr.", "Mars", "Avr.", "Mai", "Juin", "Juil.", "Août", "Sept.", "Oct.", "Nov.", "Déc."];

const nf = (v, d = 0) => v == null || isNaN(v) ? "—" : Number(v).toLocaleString("fr-FR", { minimumFractionDigits: d, maximumFractionDigits: d });
const big = (v, d = 1) => {
  const a = Math.abs(v);
  if (a >= 1e9) return nf(v / 1e9, d) + " Md";
  if (a >= 1e6) return nf(v / 1e6, d) + " M";
  if (a >= 1e3) return nf(v / 1e3, d) + " k";
  return nf(v, 0);
};
const pct = (v, d = 1, sign = true) => v == null ? "—" : (sign && v > 0 ? "+" : "") + nf(v, d) + " %";
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = s => String(s ?? "").replace(/[&<>"]/g, m => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[m]));

/* ---------- ECharts : thème commun (relu à chaque rendu) ---------- */
const axisBase = () => ({
  axisLine: { lineStyle: { color: C.line } }, axisTick: { show: false },
  axisLabel: { color: C.muted, fontSize: 11 }, splitLine: { lineStyle: { color: C.line } },
  nameTextStyle: { color: C.muted, fontSize: 11 },
});
const tooltipBase = () => ({
  backgroundColor: C.tip, borderColor: C.tipBorder, borderWidth: 1,
  textStyle: { color: C.text, fontSize: 12 }, extraCssText: "border-radius:10px;box-shadow:0 10px 30px rgba(0,0,0,.18);",
});
const CHARTS = [];
function chart(id, option) {
  const el = typeof id === "string" ? document.getElementById(id) : id;
  if (!el) return null;
  const ch = echarts.getInstanceByDom(el) || echarts.init(el, null, { renderer: "canvas" });
  const ax = axisBase();
  const base = {
    backgroundColor: "transparent", textStyle: { fontFamily: "Inter, system-ui, sans-serif", color: C.text2 },
    grid: { left: 8, right: 16, top: 36, bottom: 8, containLabel: true },
    legend: { top: 0, left: 0, icon: "roundRect", itemWidth: 10, itemHeight: 10, textStyle: { color: C.text2, fontSize: 12 } },
    tooltip: { ...tooltipBase(), trigger: "axis", axisPointer: { type: "line", lineStyle: { color: C.pointer } } },
    animationDuration: 700,
  };
  const opt = Object.assign({}, base, option);
  ["xAxis", "yAxis"].forEach(k => {
    if (!opt[k]) return;
    const apply = a => Object.assign({}, ax, a, {
      axisLabel: Object.assign({}, ax.axisLabel, a.axisLabel || {}),
      splitLine: Object.assign({}, ax.splitLine, a.splitLine || {}),
    });
    opt[k] = Array.isArray(opt[k]) ? opt[k].map(apply) : apply(opt[k]);
  });
  if (option.tooltip) opt.tooltip = Object.assign({}, base.tooltip, option.tooltip);
  if (option.legend === false) opt.legend = { show: false };
  else if (option.legend) opt.legend = Object.assign({}, base.legend, option.legend);
  if (option.grid) opt.grid = Object.assign({}, base.grid, option.grid);
  if (innerWidth < 640) {                      /* mobile : légende défilante, police compacte */
    if (opt.legend && opt.legend.show !== false) Object.assign(opt.legend, { type: "scroll", pageIconColor: C.accent, pageTextStyle: { color: C.muted } });
    opt.tooltip = Object.assign({}, opt.tooltip, { confine: true });
  }
  ch.setOption(opt, true);
  if (!CHARTS.includes(ch)) CHARTS.push(ch);
  return ch;
}
window.addEventListener("resize", () => CHARTS.forEach(c => c.resize()));

/* barre empilée : extrémité arrondie seulement sur le segment du haut, liseré de séparation */
const barStyle = (color, top = true) => ({ color, borderRadius: top ? [4, 4, 0, 0] : 0, borderColor: C.surface, borderWidth: 1 });

function sparkline(el, values, color) {
  color = color || C.amber;
  return chart(el, {
    grid: { left: 0, right: 0, top: 4, bottom: 0, containLabel: false }, legend: false,
    tooltip: { trigger: "axis", formatter: p => `${p[0].name} : <b>${big(p[0].value)}</b>` },
    xAxis: { type: "category", data: D.annees, show: false, boundaryGap: false },
    yAxis: { type: "value", show: false, min: 0 },
    series: [{ type: "line", data: values, smooth: true, symbol: "none", lineStyle: { width: 2, color },
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: color + "55" }, { offset: 1, color: color + "00" }]) } }],
  });
}

function legendHTML(items) {
  return '<div class="legend">' + items.map(([c, l]) => `<span><i style="background:${c}"></i>${esc(l)}</span>`).join("") + "</div>";
}
