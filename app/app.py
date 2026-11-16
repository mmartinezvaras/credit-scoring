import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap
import streamlit as st

RAIZ = Path(__file__).resolve().parent.parent
REPO = "https://github.com/mmartinezvaras/credit-scoring"
st.set_page_config(page_title="Scoring de crédito explicable", page_icon="💳", layout="centered")


# ---------- Estilo (paleta de Marcos: negro, grafito, plata, índigo suave, blanco) ----------
st.markdown(
    """
<style>
:root {
  --ink: #000000; --ink-2: #555555; --silver: #86868B; --paper: #F5F5F7; --sheet: #FFFFFF;
  --rule: rgba(134,134,139,.35); --ring: rgba(0,0,0,.08);
  --lift: 0 1px 2px rgba(0,0,0,.04), 0 4px 16px -6px rgba(0,0,0,.10);
  --ease-out: cubic-bezier(.23,1,.32,1);
}
html, body, [class*="st-"], .stMarkdown, button, input, textarea {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter", "Helvetica Neue", Arial, sans-serif;
}
[data-testid="stIconMaterial"], [data-testid="stExpanderIcon"], .material-symbols-rounded {
  font-family: "Material Symbols Rounded" !important;
}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainBlockContainer"], .block-container { padding-top: 3rem; padding-bottom: 4rem; max-width: 760px; }

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
           background: var(--ink); color: var(--sheet); font-size: .75rem; margin-right: .4rem; }

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
[data-testid="stVerticalBlockBorderWrapper"] { background: var(--sheet); border-radius: 16px !important;
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
.pill.no { background: var(--ink); color: var(--sheet); }
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

@media (max-width: 640px) {
  .hero h1 { font-size: 2rem; }
  .stats, .pipe { grid-template-columns: 1fr 1fr; }
  .why-row { grid-template-columns: 1fr; gap: .4rem; }
}
</style>
""",
    unsafe_allow_html=True,
)


# ---------- 1. Cargar el modelo (una sola vez) ----------
@st.cache_resource
def cargar():
    modelo = joblib.load(RAIZ / "models" / "modelo_lightgbm.joblib")
    config = json.loads((RAIZ / "models" / "config.json").read_text(encoding="utf-8"))
    return modelo, config, shap.TreeExplainer(modelo)


modelo, config, explicador = cargar()
CORTE = config["corte"]
TRAMOS = config["tramos"]
LETRAS = ["A", "B", "C", "D", "E"]
TONOS = [  # del más claro (A) al más oscuro (E), solo negro con transparencia
    ("rgba(0,0,0,.06)", "#000000"), ("rgba(0,0,0,.14)", "#000000"), ("rgba(0,0,0,.32)", "#000000"),
    ("#555555", "#FFFFFF"), ("#000000", "#FFFFFF"),
]

MESES = ["Septiembre", "Agosto", "Julio", "Junio", "Mayo", "Abril"]
ESTUDIOS = ["postgrado", "universidad", "bachillerato", "otros", "desconocido"]
ESTADOS_CIVILES = ["casado", "soltero", "otros", "desconocido"]
EJEMPLOS = {
    "Cliente cumplidor": dict(
        limite=200_000, edad=38, estudios="universidad", estado_civil="casado",
        estado=[-1, -1, -1, -1, -1, -1],
        factura=[15_000, 14_000, 16_000, 12_000, 13_000, 15_000],
        pagado=[15_000, 14_000, 16_000, 12_000, 13_000, 15_000],
    ),
    "Algún despiste": dict(
        limite=120_000, edad=31, estudios="universidad", estado_civil="soltero",
        estado=[1, 0, 0, 0, -1, -1],
        factura=[70_000, 66_000, 61_000, 55_000, 40_000, 35_000],
        pagado=[2_500, 3_000, 3_000, 2_500, 40_000, 35_000],
    ),
    "Cliente en apuros": dict(
        limite=50_000, edad=27, estudios="bachillerato", estado_civil="soltero",
        estado=[2, 2, 1, 0, 0, 0],
        factura=[49_000, 48_000, 47_500, 45_000, 40_000, 38_000],
        pagado=[0, 0, 1_500, 2_000, 2_000, 1_800],
    ),
}


def pct(x, dec=0):
    return f"{x:.{dec}%}".replace(".", ",").replace("%", " %")


def miles(x):
    return f"{x:,.0f}".replace(",", ".")


def seccion(n, titulo, pista=None):
    st.markdown(
        f'<div class="section"><span class="n">{n:02d}</span><h3>{titulo}</h3></div>'
        + (f'<p class="hint">{pista}</p>' if pista else ""),
        unsafe_allow_html=True,
    )


# ---------- 2. Las mismas variables que en el paso 4 ----------
def calcular_variables(limite, edad, estudios, estado_civil, historial):
    estado = historial["estado"].to_numpy(dtype=float)
    factura = historial["factura"].to_numpy(dtype=float)
    pagado = historial["pagado"].to_numpy(dtype=float)

    fila = {col: 0.0 for col in config["columnas"]}
    fila["retraso_sep"] = np.clip(estado[0], -1, 2)
    fila["meses_con_retraso"] = (estado > 0).sum()
    fila["peor_retraso_6m"] = max(estado.max(), 0)
    fila["limite_credito"] = limite
    fila["uso_limite_sep"] = np.clip(factura[0] / limite, -1, 2)
    fila["uso_medio_6m"] = np.clip((factura / limite).mean(), -1, 2)
    total_facturado = np.clip(factura, 0, None).sum()
    fila["parte_pagada_6m"] = min(pagado.sum() / total_facturado, 1) if total_facturado > 0 else 1
    fila["cambio_uso"] = np.clip((factura[0] - factura[-1]) / limite, -2, 2)
    fila["edad"] = edad
    for col in (f"nivel_estudios_{estudios}", f"estado_civil_{estado_civil}"):
        if col in fila:
            fila[col] = 1
    return pd.DataFrame([fila], columns=config["columnas"])


def describir(col, f):
    """Nombre en lenguaje claro y el valor de este cliente."""
    v = f[col]
    if col == "retraso_sep":
        txt = {-1: "pagó todo", 0: "pagó el mínimo", 1: "1 mes de retraso", 2: "2 meses o más de retraso"}
        return "Pago del último mes", txt.get(int(v), "")
    if col == "meses_con_retraso":
        return "Meses con retraso", f"{int(v)} de los últimos 6"
    if col == "peor_retraso_6m":
        return "Peor retraso reciente", "ninguno" if v == 0 else f"{int(v)} {'mes' if v == 1 else 'meses'}"
    if col == "uso_limite_sep":
        return "Uso de la tarjeta este mes", f"{pct(v)} del límite"
    if col == "uso_medio_6m":
        return "Uso medio de la tarjeta", f"{pct(v)} del límite en 6 meses"
    if col == "parte_pagada_6m":
        return "Cuánto paga de lo que debe", f"{pct(v)} de lo facturado"
    if col == "limite_credito":
        return "Límite de crédito", f"NT$ {miles(v)}"
    if col == "cambio_uso":
        return "Evolución de la deuda", "sube" if v > 0.02 else ("baja" if v < -0.02 else "estable")
    if col == "edad":
        return "Edad", f"{int(v)} años"
    return col, ""


# ---------- 3. Cabecera para quien llega por primera vez ----------
st.markdown(
    """
<div class="hero">
  <div class="eyebrow">Proyecto de portfolio · Riesgo de crédito</div>
  <h1>¿Pagará este cliente su tarjeta el mes que viene?</h1>
  <p class="lead">Un modelo como los que usan los bancos para decidir a quién dar crédito. Mira el historial de pagos
  de un cliente, calcula su <b>probabilidad de impago</b>, le asigna un <b>tramo de riesgo</b> de la A a la E
  y, lo más importante, <b>explica por qué</b>.</p>
  <div class="stats">
    <div class="stat"><b>30.000</b><span>clientes reales para entrenar</span></div>
    <div class="stat"><b>0,55</b><span>Gini en clientes no vistos</span></div>
    <div class="stat"><b>A – E</b><span>tramos de riesgo calibrados</span></div>
  </div>
  <div class="steps"><span><b>1</b>Elige un cliente de ejemplo</span><span><b>2</b>Cambia sus datos si quieres</span><span><b>3</b>Mira el riesgo y los motivos</span></div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------- 4. El cliente ----------
seccion(1, "El cliente", "Empieza con un ejemplo. Puedes cambiar cualquier dato y el resultado se actualiza al momento.")
nombre = st.segmented_control("Ejemplo", list(EJEMPLOS), default="Cliente cumplidor", label_visibility="collapsed") or "Cliente cumplidor"
ej = EJEMPLOS[nombre]

with st.container(border=True):
    c1, c2 = st.columns(2)
    limite = c1.number_input("Límite de crédito (NT$)", 10_000, 1_000_000, ej["limite"], step=10_000, key=f"limite_{nombre}")
    edad = c2.number_input("Edad", 21, 79, ej["edad"], key=f"edad_{nombre}")
    estudios = c1.selectbox("Estudios", ESTUDIOS, ESTUDIOS.index(ej["estudios"]), key=f"estudios_{nombre}")
    estado_civil = c2.selectbox("Estado civil", ESTADOS_CIVILES, ESTADOS_CIVILES.index(ej["estado_civil"]), key=f"civil_{nombre}")

    st.markdown("**Sus últimos 6 meses**")
    historial = st.data_editor(
        pd.DataFrame({"mes": MESES, "estado": ej["estado"], "factura": ej["factura"], "pagado": ej["pagado"]}),
        column_config={
            "mes": st.column_config.TextColumn("Mes", disabled=True),
            "estado": st.column_config.NumberColumn(
                "Retraso", min_value=-2, max_value=8, step=1,
                help="-2 sin consumo · -1 pagó todo · 0 pagó el mínimo · 1 a 8 = meses de retraso",
            ),
            "factura": st.column_config.NumberColumn("Factura (NT$)", step=1_000, format="%d"),
            "pagado": st.column_config.NumberColumn("Pagado (NT$)", min_value=0, step=1_000, format="%d"),
        },
        hide_index=True,
        width="stretch",
        key=f"historial_{nombre}",
    )
    st.caption("En **Retraso**: −1 = pagó todo · 0 = pagó solo el mínimo · 1 a 8 = meses que lleva sin pagar.")

# ---------- 5. El resultado ----------
fila = calcular_variables(limite, edad, estudios, estado_civil, historial.fillna(0))
pd_cliente = float(modelo.predict_proba(fila)[0, 1])
i_tramo = min(int(np.searchsorted(TRAMOS, pd_cliente, side="right")) - 1, 4)
tramo = LETRAS[i_tramo]
deniega = pd_cliente >= CORTE

seccion(2, "El resultado")
segmentos = "".join(
    f'<div class="seg" style="flex:{(TRAMOS[i + 1] - TRAMOS[i]) * 100:.0f};'
    f'background:{TONOS[i][0]};color:{TONOS[i][1]}">{LETRAS[i]}</div>'
    for i in range(5)
)
if deniega:
    decision, clase = "Revisar", "no"
    frase = f"Supera el corte del {pct(CORTE)}: <span>un analista revisaría el caso o le bajaría el límite.</span>"
else:
    decision, clase = "Aprobar", "ok"
    frase = f"Está por debajo del corte del {pct(CORTE)}: <span>el banco le mantendría el crédito.</span>"
st.markdown(
    f"""
<div class="card">
  <div class="res-top">
    <div class="res-pd"><small>Probabilidad de impago</small><b>{pct(pd_cliente, 1)}</b></div>
    <div class="res-tags">
      <div class="res-tag"><small>Tramo</small><span class="pill" style="background:{TONOS[i_tramo][0]};color:{TONOS[i_tramo][1]}">{tramo}</span></div>
      <div class="res-tag"><small>Decisión</small><span class="pill {clase}">{decision}</span></div>
    </div>
  </div>
  <p class="res-text">De cada 100 clientes con este perfil, unos <b>{round(pd_cliente * 100)}</b> dejarían de pagar el mes siguiente.
  {frase}</p>
  <div class="gauge">{segmentos}<div class="mark" style="left:{pd_cliente * 100:.1f}%"></div></div>
  <div class="gauge-axis"><span>0 %</span><span>Riesgo muy bajo → muy alto</span><span>100 %</span></div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------- 6. Los motivos, con SHAP ----------
seccion(3, "Por qué", "Cada barra indica cuánto empuja ese dato el riesgo hacia arriba o hacia abajo, comparado con un cliente medio.")
valores = np.array(explicador(fila).values)
if valores.ndim == 3:  # algunas versiones de SHAP devuelven una columna por clase
    valores = valores[..., 1]
aportes = pd.Series(valores[0], index=config["columnas"])
f0 = fila.iloc[0]
grupos = {"nivel_estudios_": ("Estudios", estudios), "estado_civil_": ("Estado civil", estado_civil)}
filas = {}
for col, v in aportes.items():
    if col in ("limite_desconocido", "edad_desconocida"):
        continue
    g = next((g for p, g in grupos.items() if col.startswith(p)), None)
    clave = g if g else describir(col, f0)
    filas[clave] = filas.get(clave, 0) + v
motivos = sorted(filas.items(), key=lambda kv: -abs(kv[1]))[:6]
escala = max(abs(v) for _, v in motivos) or 1

html = []
for (lbl, val), v in motivos:
    ancho = abs(v) / escala * 50
    sube = v > 0
    pos = f"left:50%;width:{ancho:.1f}%" if sube else f"left:{50 - ancho:.1f}%;width:{ancho:.1f}%"
    color = "#000000" if sube else "#86868B"
    flecha = "↑ sube el riesgo" if sube else "↓ baja el riesgo"
    html.append(
        f'<div class="why-row"><div class="lbl">{lbl}<span class="val">{val} · {flecha}</span></div>'
        f'<div class="bar"><span class="mid"></span><i style="{pos};background:{color}"></i></div></div>'
    )
st.markdown(
    '<div class="card">' + "".join(html)
    + '<div class="legend"><span><i style="background:#86868B"></i>Baja el riesgo</span>'
      '<span><i style="background:#000000"></i>Sube el riesgo</span></div></div>',
    unsafe_allow_html=True,
)

# ---------- 7. Cómo está hecho ----------
seccion(4, "Cómo está hecho", "El proceso completo de un equipo de Riesgo de Crédito, de los datos en bruto a esta demo.")
with st.expander("Ver el proceso, los resultados y la tecnología", expanded=False):
    st.markdown(
        """
<div class="pipe">
  <div><b>1 · Limpiar</b>Dos extracciones sucias (tarjetas y CRM) con 20 problemas de calidad.</div>
  <div><b>2 · Variables</b>Señales de negocio sin mirar el futuro: retrasos, uso del límite, pagos.</div>
  <div><b>3 · Modelar</b>Regresión logística y LightGBM regularizado y monótono.</div>
  <div><b>4 · Explicar</b>SHAP convierte cada decisión en motivos legibles.</div>
  <div><b>5 · Validar</b>Calibración, tramos, corte por coste y trato igual por sexo.</div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
**Lo que mide el modelo** con 8.973 clientes que no vio al entrenar:

<table class="t">
<tr><th>Tramo</th><th>% de clientes</th><th>Probabilidad que da el modelo</th><th>Impago real</th></tr>
<tr><td>A</td><td>33 %</td><td>7,0 %</td><td>7,6 %</td></tr>
<tr><td>B</td><td>34 %</td><td>14,5 %</td><td>15,3 %</td></tr>
<tr><td>C</td><td>15 %</td><td>26,4 %</td><td>28,0 %</td></tr>
<tr><td>D</td><td>7 %</td><td>43,6 %</td><td>44,4 %</td></tr>
<tr><td>E</td><td>11 %</td><td>69,5 %</td><td>65,5 %</td></tr>
</table>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
- **Ordena bien:** Gini de 0,55 (0 = azar, 1 = perfecto), 7 puntos más que la regresión logística.
- **Acierta en la cifra:** lo que predice coincide con lo que pasó (columna de la derecha).
- **Decide con números:** con el corte del 15 % se revisa al 47 % de los clientes y se evita el 77 % de los impagos.
- **Trata igual:** el sexo no entra en el modelo y funciona parecido en hombres y mujeres (Gini 0,53 y 0,55).
- **Tiene sentido de negocio:** más retraso siempre sube el riesgo; más límite o más pago siempre lo baja.
"""
    )
    st.markdown(
        '<div class="chips"><span>Python</span><span>pandas</span><span>scikit-learn</span><span>LightGBM</span>'
        "<span>SHAP</span><span>Streamlit</span><span>Parquet</span></div>",
        unsafe_allow_html=True,
    )

st.markdown(
    f"""<div class="foot">Datos: dataset público <i>Default of Credit Card Clients</i> (UCI, Taiwán 2005), importes en NT$.
Demo educativa, no una decisión de crédito real.<br><a href="{REPO}" target="_blank">Ver el código en GitHub →</a></div>""",
    unsafe_allow_html=True,
)
