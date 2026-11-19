"""Estilo compartido por las páginas de la app: paleta de Marcos (negro, grafito, plata, índigo
suave, blanco), tipografía, tarjetas y el botón Claro / Oscuro.

El tema se guarda en el navegador (localStorage) y en la página principal, así que se mantiene
al pasar de una página a otra.
"""

import streamlit as st
import streamlit.components.v1 as components

# ---------- Modo claro y oscuro ----------
# El cambio se hace en el navegador, sin recargar ni volver a ejecutar Python: el botón pone
# data-tema="oscuro" en la página y el CSS cambia los colores al instante.
CLARO = """--ink:#000000; --ink-2:#555555; --silver:#86868B; --paper:#F5F5F7; --sheet:#FFFFFF; --accent:#000000;
  --rule:rgba(134,134,139,.35); --ring:rgba(0,0,0,.08); --on-strong:#FFFFFF;
  --lift:0 1px 2px rgba(0,0,0,.04), 0 4px 16px -6px rgba(0,0,0,.10);
  --t0:rgba(0,0,0,.06); --t1:rgba(0,0,0,.14); --t2:rgba(0,0,0,.32); --t3:#555555; --t4:#000000; color-scheme:light;"""
OSCURO = """--ink:#F5F5F7; --ink-2:#86868B; --silver:#86868B; --paper:#000000; --sheet:#141414; --accent:#FFFFFF;
  --rule:rgba(134,134,139,.30); --ring:rgba(255,255,255,.10); --on-strong:#000000;
  --lift:0 1px 2px rgba(0,0,0,.5), 0 6px 20px -8px rgba(0,0,0,.8);
  --t0:rgba(255,255,255,.08); --t1:rgba(255,255,255,.16); --t2:rgba(255,255,255,.32); --t3:#86868B; --t4:#FFFFFF; color-scheme:dark;"""
VARIABLES = f":root {{ {CLARO} }}\nhtml[data-tema='oscuro'] {{ {OSCURO} }}"

# ---------- Estilo (paleta de Marcos: negro, grafito, plata, índigo suave, blanco) ----------

# ---------- Estilo (paleta de Marcos: negro, grafito, plata, índigo suave, blanco) ----------
CSS = """
<style>
__VARS__
:root { --ease-out: cubic-bezier(.23,1,.32,1); }
.t0 { background: var(--t0); color: var(--ink); } .t1 { background: var(--t1); color: var(--ink); }
.t2 { background: var(--t2); color: var(--ink); } .t3 { background: var(--t3); color: var(--on-strong); }
.t4 { background: var(--t4); color: var(--on-strong); }
html, body, [class*="st-"], .stMarkdown, button, input, textarea {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter", "Helvetica Neue", Arial, sans-serif;
}
[data-testid="stIconMaterial"], [data-testid="stExpanderIcon"], .material-symbols-rounded {
  font-family: "Material Symbols Rounded" !important;
}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
[data-testid="stHeader"] { display: none !important; }
[data-testid="stMainBlockContainer"], .block-container { padding-top: 1.5rem; padding-bottom: 4rem; max-width: 760px; }

/* Fondo y textos de Streamlit con nuestras variables */
[data-testid="stApp"] { background: var(--paper); color: var(--ink); }
[data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"] p, [data-testid="stExpander"] summary { color: var(--ink); }
[data-testid="stCaptionContainer"] { color: var(--ink-2); }
[data-testid="stExpander"] details { background: var(--sheet); border-color: var(--rule); }
/* Los controles de Streamlit (y la tabla, que es un dibujo) se ven en oscuro invirtiéndolos:
   con una paleta en blanco y negro, invertir da justo los colores oscuros */
html[data-tema='oscuro'] :is([data-testid="stNumberInput"], [data-testid="stSelectbox"], [data-testid="stDataFrame"],
  [data-testid="stButtonGroup"], [data-baseweb="popover"], [data-testid="stTooltipContent"]) {
  filter: invert(1) hue-rotate(180deg);
}
/* dentro de lo invertido, el texto va en su color de modo claro (al invertirse queda claro) */
html[data-tema='oscuro'] :is([data-testid="stNumberInput"], [data-testid="stSelectbox"], [data-testid="stButtonGroup"])
  :is([data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"] p) { color: #000000; }

/* Cabecera */
.eyebrow { font-size: .78rem; letter-spacing: .08em; text-transform: uppercase; color: var(--ink-2); font-weight: 600; }
.hero h1 { font-size: 2.6rem; line-height: 1.08; letter-spacing: -.025em; font-weight: 700; margin: .4rem 0 .8rem; padding: 0; color: var(--ink); }
.hero p.lead { font-size: 1.12rem; line-height: 1.55; color: var(--ink-2); margin: 0 0 1.4rem; max-width: 40em; }
.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: .75rem; margin-bottom: 1.6rem; }
.stat { background: var(--sheet); border-radius: 14px; padding: .9rem 1rem; box-shadow: 0 0 0 1px var(--ring), var(--lift); }
.stat b { display: block; font-size: 1.45rem; letter-spacing: -.02em; color: var(--ink); }
.stat span { font-size: .85rem; color: var(--ink-2); }
.steps { display: flex; gap: 1.2rem; flex-wrap: wrap; font-size: .92rem; color: var(--ink-2); margin-bottom: .4rem; }
.steps b { display: inline-grid; place-items: center; width: 1.45rem; height: 1.45rem; border-radius: 50%;
           background: var(--ink); color: var(--paper); font-size: .75rem; margin-right: .4rem; }

/* Entrada suave de la cabecera (solo al abrir la página) */
@media (prefers-reduced-motion: no-preference) {
  .hero > * { opacity: 0; transform: translateY(6px); animation: entra 420ms var(--ease-out) forwards; }
  .hero > *:nth-child(2) { animation-delay: 50ms; }
  .hero > *:nth-child(3) { animation-delay: 100ms; }
  .hero > *:nth-child(4) { animation-delay: 150ms; }
  .hero > *:nth-child(5) { animation-delay: 200ms; }
}
@keyframes entra { to { opacity: 1; transform: none; } }

/* Títulos de sección */
.section { display: flex; align-items: baseline; gap: .6rem; margin: 2.2rem 0 .2rem; }
.section .n { font-size: .8rem; font-weight: 600; color: var(--silver); font-variant-numeric: tabular-nums; }
.section h3 { font-size: 1.3rem; letter-spacing: -.015em; margin: 0; padding: 0; font-weight: 650; }
.hint { color: var(--ink-2); font-size: .93rem; margin: .2rem 0 .8rem; }

/* Tarjetas */
[data-testid="stVerticalBlockBorderWrapper"], .st-key-cliente { background: var(--sheet); border-radius: 16px !important;
  border: none !important; box-shadow: 0 0 0 1px var(--ring), var(--lift); }
.card { background: var(--sheet); border-radius: 16px; padding: 1.4rem 1.5rem; box-shadow: 0 0 0 1px var(--ring), var(--lift); }

/* Resultado */
.res-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap; }
.res-pd small, .res-tag small { display: block; font-size: .8rem; color: var(--ink-2); margin-bottom: .2rem; }
.res-pd b { font-size: 3.2rem; line-height: 1; letter-spacing: -.035em; font-variant-numeric: tabular-nums; }
.res-tags { display: flex; gap: .6rem; }
.res-tag { text-align: right; }
.pill { display: inline-block; padding: .35rem .8rem; border-radius: 999px; font-weight: 600; font-size: .95rem; }
.pill.ok { background: var(--paper); color: var(--ink); box-shadow: inset 0 0 0 1px var(--ink); }
.pill.no { background: var(--ink); color: var(--paper); }
.res-text { font-size: 1.02rem; line-height: 1.5; color: var(--ink); margin: 1rem 0 1.2rem; }
.res-text span { color: var(--ink-2); }

.gauge { position: relative; display: flex; gap: 3px; height: 30px; margin-top: .4rem; }
.gauge .seg { display: grid; place-items: center; border-radius: 6px; font-size: .78rem; font-weight: 600; }
.gauge .mark { position: absolute; top: -7px; bottom: -7px; width: 3px; border-radius: 2px; background: var(--ink);
               box-shadow: 0 0 0 2px var(--sheet); transform: translateX(-50%); }
.gauge-axis { display: flex; justify-content: space-between; font-size: .72rem; color: var(--ink-2); margin-top: .5rem; font-variant-numeric: tabular-nums; }

/* Motivos */
.why-row { display: grid; grid-template-columns: 1fr 42%; gap: 1rem; align-items: center; padding: .7rem 0; border-top: 1px solid var(--rule); }
.why-row:first-child { border-top: none; padding-top: 0; }
.why-row .lbl { font-size: .95rem; color: var(--ink); line-height: 1.3; }
.why-row .val { display: block; font-size: .82rem; color: var(--ink-2); margin-top: .15rem; }
.bar { position: relative; height: 10px; background: var(--paper); border-radius: 5px; }
.bar i { position: absolute; top: 0; bottom: 0; border-radius: 5px; }
.bar .mid { position: absolute; left: 50%; top: -4px; bottom: -4px; width: 1px; background: var(--silver); }
.legend { display: flex; gap: 1rem; font-size: .8rem; color: var(--ink-2); margin-top: .9rem; }
.legend i { display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: .35rem; vertical-align: -1px; }

/* Cómo está hecho */
.pipe { display: grid; grid-template-columns: repeat(5, 1fr); gap: .5rem; margin: .4rem 0 1rem; }
.pipe div { background: var(--paper); border-radius: 12px; padding: .7rem .75rem; font-size: .82rem; color: var(--ink-2); line-height: 1.35; }
.pipe b { display: block; color: var(--ink); font-size: .9rem; margin-bottom: .15rem; }
.chips { display: flex; flex-wrap: wrap; gap: .4rem; margin-top: .6rem; }
.chips span { font-size: .78rem; padding: .25rem .65rem; border-radius: 999px; background: var(--paper); box-shadow: inset 0 0 0 1px var(--rule); }
table.t { width: 100%; border-collapse: collapse; font-size: .88rem; font-variant-numeric: tabular-nums; }
table.t th { text-align: left; font-weight: 600; color: var(--ink-2); font-size: .78rem; padding: .4rem .5rem; border-bottom: 1px solid var(--rule); }
table.t td { padding: .45rem .5rem; border-bottom: 1px solid var(--rule); }
.foot { margin-top: 2.5rem; font-size: .85rem; color: var(--ink-2); text-align: center; }
a { color: var(--ink) !important; text-underline-offset: 3px; }

/* Respuesta al pulsar */
button, [role="radio"] { transition: transform 160ms var(--ease-out); }
button:active, [role="radio"]:active { transform: scale(.97); }

/* Enlaces entre páginas (st.page_link): una píldora discreta */
[data-testid="stPageLink"] a { display: inline-flex; width: auto; padding: .3rem .9rem; border-radius: 999px; text-decoration: none;
  background: var(--sheet); box-shadow: 0 0 0 1px var(--ring), var(--lift); transition: transform 160ms var(--ease-out); }
[data-testid="stPageLink"] a p, [data-testid="stPageLink"] a span { color: var(--ink) !important; font-weight: 500; font-size: .9rem; }
[data-testid="stPageLink"] a:active { transform: scale(.97); }

@media (max-width: 640px) {
  .hero h1 { font-size: 2rem; }
  .stats, .pipe { grid-template-columns: 1fr 1fr; }
  .why-row { grid-template-columns: 1fr; gap: .4rem; }
}
</style>
""".replace("__VARS__", VARIABLES)

# ---------- Botón Claro / Oscuro (funciona en el navegador, al instante) ----------
BOTON_TEMA = """
<style>
  body { margin: 0; display: flex; justify-content: flex-end; font: 500 13px -apple-system, BlinkMacSystemFont, "Inter", sans-serif; }
  .sw { display: inline-flex; padding: 3px; border-radius: 999px; gap: 2px; }
  button { border: 0; background: transparent; padding: 6px 12px; border-radius: 999px; cursor: pointer; font: inherit;
           display: inline-flex; align-items: center; gap: 6px; transition: transform 160ms cubic-bezier(.23,1,.32,1); }
  button:active { transform: scale(.97); }
  svg { width: 14px; height: 14px; }
  .claro .sw { background: #FFFFFF; box-shadow: 0 0 0 1px rgba(0,0,0,.08); }
  .claro button { color: #555555; } .claro button[aria-pressed="true"] { background: #000000; color: #FFFFFF; }
  .oscuro .sw { background: #141414; box-shadow: 0 0 0 1px rgba(255,255,255,.10); }
  .oscuro button { color: #86868B; } .oscuro button[aria-pressed="true"] { background: #FFFFFF; color: #000000; }
</style>
<div class="sw" role="group" aria-label="Tema">
  <button data-t="claro"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>Claro</button>
  <button data-t="oscuro"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>Oscuro</button>
</div>
<script>
  const raiz = window.parent.document.documentElement;
  let guardado = null;
  try { guardado = window.parent.localStorage.getItem("tema-scoring"); } catch (e) {}
  const sistema = window.parent.matchMedia("(prefers-color-scheme: dark)").matches ? "oscuro" : "claro";
  function poner(t) {
    raiz.dataset.tema = t;
    document.body.className = t;
    document.querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", b.dataset.t === t));
  }
  poner(guardado || sistema);
  document.querySelectorAll("button").forEach(b => b.addEventListener("click", () => {
    poner(b.dataset.t);
    try { window.parent.localStorage.setItem("tema-scoring", b.dataset.t); } catch (e) {}
  }));
</script>
"""


def poner_estilo():
    """CSS de la app: colores del tema elegido, tipografía y componentes."""
    st.markdown(CSS, unsafe_allow_html=True)


def boton_tema():
    """Botón Claro / Oscuro, arriba a la derecha."""
    _, col_tema = st.columns([5, 2])
    with col_tema:
        components.html(BOTON_TEMA, height=40)
