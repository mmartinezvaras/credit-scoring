import json
from pathlib import Path

import altair as alt
import joblib
import numpy as np
import pandas as pd
import shap
import streamlit as st

RAIZ = Path(__file__).resolve().parent.parent
st.set_page_config(page_title="Scoring de crédito", page_icon="💳", layout="centered")


# ---------- 1. Cargar el modelo (una sola vez) ----------
@st.cache_resource
def cargar():
    modelo = joblib.load(RAIZ / "models" / "modelo_lightgbm.joblib")
    config = json.loads((RAIZ / "models" / "config.json").read_text(encoding="utf-8"))
    return modelo, config, shap.TreeExplainer(modelo)


modelo, config, explicador = cargar()

MESES = ["Septiembre", "Agosto", "Julio", "Junio", "Mayo", "Abril"]
LETRAS = ["A", "B", "C", "D", "E"]
NOMBRES = {
    "retraso_sep": "Retraso en el pago de septiembre",
    "meses_con_retraso": "Meses con retraso en el último medio año",
    "peor_retraso_6m": "Peor retraso de los últimos meses",
    "uso_limite_sep": "Uso del límite en septiembre",
    "uso_medio_6m": "Uso medio del límite en 6 meses",
    "parte_pagada_6m": "Parte pagada de lo facturado",
    "limite_credito": "Límite de crédito",
    "cambio_uso": "Evolución de la deuda",
    "edad": "Edad",
}
EJEMPLOS = {
    "Cliente cumplidor": dict(
        limite=200_000, edad=38, estudios="universidad", estado_civil="casado",
        estado=[-1, -1, -1, -1, -1, -1],
        factura=[15_000, 14_000, 16_000, 12_000, 13_000, 15_000],
        pagado=[15_000, 14_000, 16_000, 12_000, 13_000, 15_000],
    ),
    "Cliente en apuros": dict(
        limite=50_000, edad=27, estudios="bachillerato", estado_civil="soltero",
        estado=[2, 2, 1, 0, 0, 0],
        factura=[49_000, 48_000, 47_500, 45_000, 40_000, 38_000],
        pagado=[0, 0, 1_500, 2_000, 2_000, 1_800],
    ),
}
ESTUDIOS = ["postgrado", "universidad", "bachillerato", "otros", "desconocido"]
ESTADOS_CIVILES = ["casado", "soltero", "otros", "desconocido"]


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


# ---------- 3. Los datos del cliente ----------
st.title("Scoring de crédito explicable")
st.caption("Cambia los datos de un cliente de tarjeta y mira qué riesgo le da el modelo y por qué.")

nombre = st.segmented_control("Empezar con un ejemplo", list(EJEMPLOS), default="Cliente cumplidor") or "Cliente cumplidor"
ej = EJEMPLOS[nombre]

c1, c2 = st.columns(2)
limite = c1.number_input("Límite de crédito (NT$)", 10_000, 1_000_000, ej["limite"], step=10_000, key=f"limite_{nombre}")
edad = c2.number_input("Edad", 21, 79, ej["edad"], key=f"edad_{nombre}")
estudios = c1.selectbox("Estudios", ESTUDIOS, ESTUDIOS.index(ej["estudios"]), key=f"estudios_{nombre}")
estado_civil = c2.selectbox("Estado civil", ESTADOS_CIVILES, ESTADOS_CIVILES.index(ej["estado_civil"]), key=f"civil_{nombre}")

st.markdown("**Los últimos 6 meses** (puedes editar la tabla)")
historial = st.data_editor(
    pd.DataFrame({"mes": MESES, "estado": ej["estado"], "factura": ej["factura"], "pagado": ej["pagado"]}),
    column_config={
        "mes": st.column_config.TextColumn("Mes", disabled=True),
        "estado": st.column_config.NumberColumn(
            "Estado de pago", min_value=-2, max_value=8, step=1,
            help="-2 sin consumo · -1 pagó todo · 0 pagó el mínimo · 1 a 8 = meses de retraso",
        ),
        "factura": st.column_config.NumberColumn("Factura (NT$)", step=1_000, format="%d"),
        "pagado": st.column_config.NumberColumn("Pagado (NT$)", min_value=0, step=1_000, format="%d"),
    },
    hide_index=True,
    width="stretch",
    key=f"historial_{nombre}",
)

# ---------- 4. La predicción ----------
fila = calcular_variables(limite, edad, estudios, estado_civil, historial.fillna(0))
pd_cliente = modelo.predict_proba(fila)[0, 1]
tramo = LETRAS[min(np.searchsorted(config["tramos"], pd_cliente, side="right") - 1, 4)]
deniega = pd_cliente >= config["corte"]

st.divider()
m1, m2, m3 = st.columns(3)
m1.metric("Probabilidad de impago", f"{pd_cliente:.1%}")
m2.metric("Tramo de riesgo", tramo, help="De la A (muy bajo) a la E (muy alto)")
m3.metric("Decisión", "Revisar" if deniega else "Aprobar",
          help=f"Se revisa (o se baja el límite) si la probabilidad de impago es ≥ {config['corte']:.0%}")

# ---------- 5. Los motivos, con SHAP ----------
valores = np.array(explicador(fila).values)
if valores.ndim == 3:  # algunas versiones de SHAP devuelven una columna por clase
    valores = valores[..., 1]
aportes = pd.Series(valores[0], index=config["columnas"])
# las columnas 0/1 de estudios y estado civil se suman en un solo motivo con el valor real del cliente
grupos = {"nivel_estudios_": f"Estudios: {estudios}", "estado_civil_": f"Estado civil: {estado_civil}"}
nombres = [next((g for p, g in grupos.items() if c.startswith(p)), NOMBRES.get(c, c)) for c in aportes.index]
aportes = aportes.groupby(nombres, sort=False).sum()
aportes = aportes.drop(["limite_desconocido", "edad_desconocida"], errors="ignore")
principales = aportes.reindex(aportes.abs().sort_values(ascending=False).index).head(8)

st.subheader("Por qué")
suben = principales[principales > 0].head(3)
bajan = principales[principales < 0].head(2)
if len(suben):
    st.markdown("**Suben el riesgo:** " + " · ".join(suben.index))
if len(bajan):
    st.markdown("**Lo bajan:** " + " · ".join(bajan.index))

grafico = pd.DataFrame({
    "variable": principales.index,
    "aporte": principales.values,
    "efecto": np.where(principales.values > 0, "Sube el riesgo", "Baja el riesgo"),
})
st.altair_chart(
    alt.Chart(grafico).mark_bar().encode(
        x=alt.X("aporte:Q", title="Aporte al riesgo (SHAP)"),
        y=alt.Y("variable:N", sort=list(principales.index), title=None, axis=alt.Axis(labelLimit=300)),
        color=alt.Color("efecto:N", scale=alt.Scale(domain=["Sube el riesgo", "Baja el riesgo"],
                                                    range=["#000000", "#86868B"]), title=None),
        tooltip=["variable", alt.Tooltip("aporte:Q", format=".3f")],
    ).properties(height=300),
    width="stretch",
)
st.caption(
    "Modelo LightGBM entrenado con 30.000 clientes de tarjeta (dataset público de la UCI, Taiwán 2005). "
    "Es una demo con fines educativos, no una decisión de crédito real."
)
