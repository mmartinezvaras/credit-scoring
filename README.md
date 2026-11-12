# Scoring de crédito explicable

Modelo de **probabilidad de impago (PD)** para clientes de tarjeta de crédito, construido paso a paso como en un equipo de Riesgo de Crédito: desde ficheros sucios de dos sistemas del banco hasta un modelo que se pueda explicar a cada cliente.

> 🚧 En construcción. Hechos: limpieza y exploración. Siguientes: variables, regresión logística, LightGBM, explicaciones con SHAP y métricas de banca (AUC, Gini, calibración, trato igual entre grupos).

## Los datos

Parten del dataset público [Default of Credit Card Clients](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients) de la UCI: 30.000 clientes de un banco de Taiwán (2005), con su límite, sus pagos de 6 meses y si pagaron al mes siguiente.

Para practicar la limpieza como en un caso real, el original se convirtió en dos extracciones «sucias» de sistemas distintos:

| Fichero | Sistema | Contenido |
| --- | --- | --- |
| `data/raw/extracto_tarjetas_2005-09.csv` | Tarjetas | Límite, estado de pago, facturas, pagos e impago |
| `data/raw/clientes_crm.json` | CRM | Sexo, fecha de nacimiento, estado civil y estudios |

## Lo que se ha hecho

**`notebooks/02_limpieza.ipynb`** resuelve 20 problemas de calidad de datos:
- codificación Windows, separador `;`, líneas de comentario y de control, filas partidas por notas manuales;
- números en formato español, prefijos de moneda, cuatro marcas distintas de «sin dato», valores imposibles y errores de signo;
- etiqueta escrita de 8 formas, duplicados exactos y versiones antiguas de clientes;
- JSON anidado, IDs con formatos distintos entre sistemas y fechas en 4 formatos;
- unión de los dos sistemas, apartando en un fichero de revisión los registros que no casan;
- comprobaciones con `assert` y guardado en **Parquet**.

**`notebooks/03_explorar.ipynb`** analiza quién deja de pagar. El retraso en el último mes es la señal más fuerte: con 2 meses de retraso, la tasa de impago pasa de alrededor del 15 % a cerca del 70 %.

## Cómo ejecutarlo

```bash
conda create -y -n credito python=3.12 && conda activate credito
pip install -r requirements.txt
jupyter lab
```

Ejecuta los cuadernos en orden: `02_limpieza` crea `data/clean/clientes_modelo.parquet`, que usa `03_explorar`.
