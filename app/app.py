import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap
import streamlit as st
from estilo import boton_tema, poner_estilo

RAIZ = Path(__file__).resolve().parent.parent
REPO = "https://github.com/mmartinezvaras/credit-scoring"
st.set_page_config(page_title="Scoring de crédito explicable", page_icon="💳", layout="centered")


# ---------- Estilo y modo claro / oscuro (compartidos con la página «Cómo está hecho») ----------
poner_estilo()


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


# ---------- Botón Claro / Oscuro (funciona en el navegador, al instante) ----------
boton_tema()

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

st.page_link("pages/como_esta_hecho.py", label="Cómo está hecho: pasos, problemas y tecnologías", icon=":material/arrow_forward:")

# ---------- 4. El cliente ----------
seccion(1, "El cliente", "Empieza con un ejemplo. Puedes cambiar cualquier dato y el resultado se actualiza al momento.")
nombre = st.segmented_control("Ejemplo", list(EJEMPLOS), default="Cliente cumplidor", label_visibility="collapsed") or "Cliente cumplidor"
ej = EJEMPLOS[nombre]

with st.container(border=True, key="cliente"):
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
    f'<div class="seg t{i}" style="flex:{(TRAMOS[i + 1] - TRAMOS[i]) * 100:.0f}">{LETRAS[i]}</div>'
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
      <div class="res-tag"><small>Tramo</small><span class="pill t{i_tramo}">{tramo}</span></div>
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
    color = "var(--accent)" if sube else "var(--silver)"
    flecha = "↑ sube el riesgo" if sube else "↓ baja el riesgo"
    html.append(
        f'<div class="why-row"><div class="lbl">{lbl}<span class="val">{val} · {flecha}</span></div>'
        f'<div class="bar"><span class="mid"></span><i style="{pos};background:{color}"></i></div></div>'
    )
st.markdown(
    '<div class="card">' + "".join(html)
    + '<div class="legend"><span><i style="background:var(--silver)"></i>Baja el riesgo</span>'
      '<span><i style="background:var(--accent)"></i>Sube el riesgo</span></div></div>',
    unsafe_allow_html=True,
)

# ---------- 7. Cómo está hecho ----------
seccion(4, "Cómo está hecho", "El proceso completo de un equipo de Riesgo de Crédito, de los datos en bruto a esta demo.")
st.page_link("pages/como_esta_hecho.py", label="Leer la explicación completa", icon=":material/arrow_forward:")
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
