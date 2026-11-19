"""Segunda página de la app: cómo está hecho el proyecto (pasos, problemas y tecnologías).

Se abre en /como_esta_hecho y se enlaza desde la portada y desde la sección «Cómo está hecho».
Usa el mismo estilo y el mismo botón Claro / Oscuro que la página principal (estilo.py).
"""

import streamlit as st
from estilo import boton_tema, poner_estilo

REPO = "https://github.com/mmartinezvaras/credit-scoring"

st.set_page_config(page_title="Cómo está hecho · Scoring de crédito", page_icon="💳", layout="centered")
poner_estilo()
boton_tema()
st.page_link("app.py", label="Volver a la demo", icon=":material/arrow_back:")

# ---------- Contenido ----------
STATS = [
    ("20", "problemas de calidad resueltos en los datos"),
    ("0,55", "Gini en clientes que el modelo no vio"),
    ("77 %", "de los impagos evitados revisando al 47 %"),
]

# (paso, cuaderno, qué se hace)
PASOS = [
    ("Limpiar", "02", "Dos extracciones sucias (tarjetas y CRM) unidas en una tabla limpia."),
    ("Explorar", "03", "Quién deja de pagar: el retraso del último mes es la señal más fuerte."),
    ("Variables", "04", "Señales de negocio sin mirar el futuro: retrasos, uso del límite, pagos."),
    ("Regresión logística", "05", "El modelo clásico de los bancos, como punto de partida."),
    ("LightGBM", "06", "Un modelo de árboles más potente, regularizado para no sobreajustar."),
    ("Explicar", "07", "SHAP convierte cada decisión en motivos que se pueden leer."),
    ("Sentido de negocio", "08b", "Restricciones de monotonía: más retraso nunca baja el riesgo."),
    ("Medir como un banco", "08", "Calibración, tramos A–E, punto de corte por coste y trato igual."),
    ("La app", "app", "Esta web en Streamlit: cambias un cliente y ves su riesgo y sus motivos."),
]

MODELOS = [
    ("Regresión logística", "0,511", "0,478", "0,033"),
    ("LightGBM sin regularizar", "0,632", "0,548", "0,084"),
    ("LightGBM regularizado", "0,614", "0,547", "0,067"),
]

# (problema, solución)
PROBLEMAS = [
    (
        "Los datos venían sucios y de dos sistemas distintos: codificación de Windows, números en formato "
        "español, cuatro marcas de «sin dato», la etiqueta de impago escrita de 8 formas y fechas en 4 formatos.",
        "Un cuaderno de limpieza que resuelve los 20 problemas uno a uno, con comprobaciones (<code>assert</code>). "
        "Los registros que no casan entre sistemas van a un fichero de revisión y el resultado se guarda en Parquet.",
    ),
    (
        "Si una variable usa información posterior a la decisión, el modelo parece muy bueno pero no sirve en la realidad.",
        "Todas las variables se calculan solo con el historial anterior. Los huecos se rellenan con la mediana o la "
        "media del propio cliente, y se marca a quién se le rellenó.",
    ),
    (
        "LightGBM sobreajustaba: Gini de 0,632 en entrenamiento frente a 0,548 en prueba.",
        "Parada temprana con un conjunto de validación y regularización (árboles más pequeños, hojas con más "
        "clientes). La diferencia baja de 0,084 a 0,067 sin perder Gini en prueba.",
    ),
    (
        "Un modelo potente puede aprender relaciones sin sentido, como que más retraso baje el riesgo en algún tramo.",
        "Restricciones de monotonía en las variables clave. Las del uso del límite costaban 5 puntos de Gini y se "
        "quitaron; con el resto, el Gini se mantiene.",
    ),
    (
        "Un banco no puede rechazar a un cliente con una «caja negra»: tiene que poder decirle por qué.",
        "SHAP mide cuánto empuja cada dato el riesgo hacia arriba o hacia abajo, y la app lo traduce a motivos "
        "en lenguaje claro.",
    ),
    (
        "Una probabilidad sola no dice qué hacer con el cliente.",
        "Comprobé que la probabilidad coincide con el impago real (calibración), creé tramos A–E y elegí el corte "
        "de menor coste suponiendo que un impago cuesta 5 veces más que un buen cliente perdido: PD ≥ 15 %.",
    ),
    (
        "El modelo podría tratar peor a un grupo de clientes.",
        "El sexo no es variable del modelo. Aparte, comprobé que funciona parecido en hombres y mujeres "
        "(Gini 0,532 y 0,554) y que acierta la tasa de impago de cada grupo.",
    ),
    (
        "La primera versión de la app solo la entendía alguien técnico.",
        "La rediseñé para cualquiera: portada que explica qué hace, clientes de ejemplo, el resultado en grande "
        "y los motivos con barras.",
    ),
    (
        "Streamlit solo permite un tema, y cambiarlo recargaba la página.",
        "Los colores son variables CSS. El botón Claro / Oscuro las cambia en el navegador al instante, sin "
        "volver a ejecutar Python, y recuerda la elección.",
    ),
    (
        "Un modelo guardado con joblib puede no cargar igual con otras versiones de las librerías.",
        "La app fija las versiones exactas con las que se entrenó y guardó el modelo, para que en Streamlit "
        "Cloud funcione igual que en mi ordenador.",
    ),
]

TECNOLOGIAS = [
    ("Python", "Todo el proyecto"),
    ("pandas", "Limpieza, unión de los dos sistemas y variables"),
    ("Parquet (PyArrow)", "Guardar los datos limpios entre cuadernos"),
    ("scikit-learn", "Regresión logística, separación entrenamiento / prueba y métricas (AUC, Gini)"),
    ("LightGBM", "El modelo final, regularizado y monótono"),
    ("SHAP", "Explicar cada decisión"),
    ("matplotlib", "Gráficos del análisis"),
    ("JupyterLab", "Los cuadernos, uno por paso"),
    ("joblib", "Guardar y cargar el modelo"),
    ("Streamlit", "Esta app, publicada en Streamlit Community Cloud"),
]

CSS_PAGINA = """
<style>
.pipe.p3 { grid-template-columns: repeat(3, 1fr); }
.pipe.p3 div { background: var(--sheet); box-shadow: 0 0 0 1px var(--ring); }
.pipe b i { font-style: normal; color: var(--ink-2); font-weight: 600; margin-right: .3rem; font-variant-numeric: tabular-nums; }
.pipe small { display: block; margin-top: .35rem; font-size: .72rem; color: var(--ink-2); }
.prob { display: grid; grid-template-columns: 1fr 1.2fr; gap: 1.2rem; padding: .95rem 0; border-top: 1px solid var(--rule); }
.prob:first-child { border-top: none; padding-top: 0; }
.prob:last-child { padding-bottom: 0; }
.prob small { display: block; font-size: .72rem; letter-spacing: .06em; text-transform: uppercase; font-weight: 600;
  color: var(--ink-2); margin-bottom: .25rem; }
.prob p { margin: 0; font-size: .94rem; line-height: 1.5; color: var(--ink); }
.prob .sol p { color: var(--ink-2); }
.prob code { font-size: .85em; background: var(--paper); padding: .05rem .3rem; border-radius: 4px; }
.tec { display: grid; grid-template-columns: 11rem 1fr; gap: 0 1rem; margin: 0; }
.tec dt, .tec dd { margin: 0; padding: .55rem 0; border-top: 1px solid var(--rule); font-size: .92rem; line-height: 1.4; }
.tec dt { font-weight: 600; color: var(--ink); }
.tec dd { color: var(--ink-2); }
.tec dt:first-of-type, .tec dd:first-of-type { border-top: none; padding-top: 0; }
.chips { margin: 0 0 1rem; }
.chips span { background: var(--sheet); color: var(--ink); }
table.t td:not(:first-child), table.t th:not(:first-child) { text-align: right; white-space: nowrap; }
table.t tr:last-child td { border-bottom: none; }
.card ul { margin: .9rem 0 0; padding-left: 1.1rem; }
.card li { font-size: .94rem; line-height: 1.5; color: var(--ink); margin: .3rem 0; }
.card li b { font-weight: 600; }
@media (max-width: 640px) {
  .stats { grid-template-columns: 1fr; }
  .pipe.p3 { grid-template-columns: 1fr 1fr; }
  .prob { grid-template-columns: 1fr; gap: .5rem; }
  .tec { grid-template-columns: 1fr; }
  .tec dd { border-top: none; padding-top: 0; }
}
</style>
"""


def seccion(n, titulo, pista=None):
    return f'<div class="section"><span class="n">{n:02d}</span><h3>{titulo}</h3></div>' + (
        f'<p class="hint">{pista}</p>' if pista else ""
    )


stats = "".join(f'<div class="stat"><b>{v}</b><span>{t}</span></div>' for v, t in STATS)
pasos = "".join(
    f"<div><b><i>{i}</i>{t}</b>{d}<small>{'cuaderno ' + c if c != 'app' else 'app/app.py'}</small></div>"
    for i, (t, c, d) in enumerate(PASOS, 1)
)
modelos = "".join(f"<tr><td>{m}</td><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for m, a, b, c in MODELOS)
problemas = "".join(
    f'<div class="prob"><div><small>Problema</small><p>{p}</p></div>'
    f'<div class="sol"><small>Solución</small><p>{s}</p></div></div>'
    for p, s in PROBLEMAS
)
chips = "".join(f"<span>{t}</span>" for t, _ in TECNOLOGIAS)
tecnologias = "".join(f"<dt>{t}</dt><dd>{d}</dd>" for t, d in TECNOLOGIAS)

st.html(CSS_PAGINA)
st.html(f"""
<div class="hero">
  <div class="eyebrow">Proyecto de portfolio · Riesgo de crédito</div>
  <h1>Cómo está hecho el scoring de crédito</h1>
  <p class="lead">Un modelo como los que usan los bancos para decidir a quién dar crédito, construido paso a paso:
  desde dos ficheros sucios de sistemas distintos hasta una app que <b>explica cada decisión</b>.
  Aquí cuento los pasos, los problemas que encontré y las tecnologías que he usado.</p>
  <div class="stats">{stats}</div>
</div>
{seccion(1, "La idea, en una frase",
         "Con el historial de pagos de un cliente, el modelo calcula su <b>probabilidad de impago</b> (PD) "
         "para el mes siguiente, le asigna un <b>tramo de riesgo</b> de la A a la E y dice <b>qué datos</b> "
         "han subido o bajado ese riesgo. Datos: 30.000 clientes reales de un banco de Taiwán (UCI, 2005).")}
{seccion(2, "Los pasos", "Un cuaderno de Jupyter por paso; cada uno lee lo que guardó el anterior.")}
<div class="pipe p3">{pasos}</div>
{seccion(3, "Los resultados",
         "Gini medido con el 30 % de clientes que los modelos no vieron al entrenar "
         "(0 = azar, 1 = perfecto). El modelo final, además, es monótono: Gini 0,546.")}
<div class="card">
  <table class="t">
    <tr><th>Modelo</th><th>Entrenamiento</th><th>Prueba</th><th>Diferencia</th></tr>
    {modelos}
  </table>
  <ul>
    <li><b>Ordena mejor:</b> LightGBM supera a la regresión logística en 7 puntos de Gini.</li>
    <li><b>Acierta en la cifra:</b> por deciles, la PD media y el impago real difieren como mucho 4 puntos.</li>
    <li><b>Decide con números:</b> con el corte del 15 % se revisa al 47 % de los clientes y se evita el 77 % de los impagos.</li>
  </ul>
</div>
{seccion(4, "Los problemas y cómo los resolví", "Lo que no salió a la primera, y qué hice para arreglarlo.")}
<div class="card">{problemas}</div>
{seccion(5, "Las tecnologías")}
<div class="chips">{chips}</div>
<div class="card"><dl class="tec">{tecnologias}</dl></div>
<div class="foot">Datos: dataset público <i>Default of Credit Card Clients</i> (UCI, Taiwán 2005), importes en NT$.
Demo educativa, no una decisión de crédito real.<br>
<a href="{REPO}" target="_blank">Ver el código en GitHub →</a></div>
""")
