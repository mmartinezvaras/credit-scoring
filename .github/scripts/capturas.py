"""Abre la app, comprueba que carga, va a «Cómo está hecho» y guarda capturas en claro y oscuro."""

import time
import urllib.request

from playwright.sync_api import sync_playwright

URL = "http://localhost:8501"

for _ in range(120):
    try:
        urllib.request.urlopen(URL, timeout=2)
        break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit("Streamlit no arrancó")


def tema(page):
    return page.evaluate("document.documentElement.dataset.tema || ''")


def boton(page, nombre):
    """El botón Claro / Oscuro está dentro de un iframe."""
    page.frame_locator("iframe").first.get_by_role("button", name=nombre).click()


with sync_playwright() as p:
    browser = p.chromium.launch()
    # Streamlit desplaza su propio contenedor: una ventana alta permite ver la página entera.
    page = browser.new_page(viewport={"width": 1280, "height": 5200}, color_scheme="light", device_scale_factor=1)
    page.goto(URL)
    page.get_by_text("¿Pagará este cliente su tarjeta el mes que viene?").wait_for(timeout=120_000)
    time.sleep(3)
    page.screenshot(path="app.png")

    page.get_by_role("link", name="Cómo está hecho: pasos, problemas y tecnologías").click()
    page.get_by_text("Cómo está hecho el scoring de crédito").wait_for(timeout=60_000)
    for seccion in ("Los pasos", "Los resultados", "Los problemas y cómo los resolví", "Las tecnologías"):
        assert page.get_by_text(seccion, exact=True).count() == 1, f"Falta la sección: {seccion}"
    time.sleep(2)
    page.screenshot(path="como_esta_hecho.png")

    boton(page, "Oscuro")
    page.wait_for_function("document.documentElement.dataset.tema === 'oscuro'", timeout=10_000)
    time.sleep(1)
    page.screenshot(path="como_esta_hecho_oscuro.png")

    # Al volver, la portada sigue en oscuro
    page.get_by_role("link", name="Volver a la demo").click()
    page.get_by_text("¿Pagará este cliente su tarjeta el mes que viene?").wait_for(timeout=60_000)
    time.sleep(3)
    assert tema(page) == "oscuro", f"Se perdió el modo oscuro al volver ({tema(page)!r})"
    page.screenshot(path="app_oscuro.png")

    page.set_viewport_size({"width": 390, "height": 7000})
    page.goto(URL + "/como_esta_hecho")
    page.get_by_text("Cómo está hecho el scoring de crédito").wait_for(timeout=60_000)
    time.sleep(3)
    page.screenshot(path="como_esta_hecho_movil.png")
    browser.close()

print("✅ La app y la página «Cómo está hecho» funcionan en claro y oscuro")
