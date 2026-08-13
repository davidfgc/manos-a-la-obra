def test_home_ok_y_muestra_handle(client):
    resp = client.get("/")
    assert resp.status_code == 200
    cuerpo = resp.get_data(as_text=True)
    assert "Manos a la Obra" in cuerpo
    assert "x.com/davidfgonzalezc" in cuerpo


def test_impresion_3d_ok_lista_modelos(client):
    resp = client.get("/impresion-3d")
    assert resp.status_code == 200
    cuerpo = resp.get_data(as_text=True)
    assert "Archivos 3D para imprimir" in cuerpo
    # Se renderiza al menos un modelo con su indicador de prioridad (estable ante renombrados).
    assert 'aria-label="Prioridad alta"' in cuerpo


def test_puntos_ok(client):
    resp = client.get("/puntos-acopio")
    assert resp.status_code == 200
    assert "Puntos de acopio" in resp.get_data(as_text=True)


def test_puntos_filtro_sin_resultados(client):
    resp = client.get("/puntos-acopio?pais=Narnia")
    assert resp.status_code == 200
    assert "No hay puntos de acopio para ese filtro." in resp.get_data(as_text=True)


def test_puntos_muestra_donaciones(client):
    # Al menos un punto real declara donaciones monetarias -> se renderiza el bloque.
    cuerpo = client.get("/puntos-acopio").get_data(as_text=True)
    assert "Donaciones monetarias" in cuerpo


# --- compartir en redes (Open Graph / Twitter) ------------------------------

import re

from config import SITE_URL


def _og(cuerpo, prop):
    m = re.search(r'(?:property|name)="' + re.escape(prop) + r'" content="([^"]*)"', cuerpo)
    return m.group(1) if m else None


def test_home_expone_metadatos_base(client):
    b = client.get("/").get_data(as_text=True)
    assert _og(b, "og:title")
    assert _og(b, "og:description")
    assert _og(b, "twitter:card") == "summary_large_image"
    assert _og(b, "og:image:width") == "1200"
    assert _og(b, "og:image:height") == "630"


def test_og_url_absoluta_sin_doble_slash(client):
    b = client.get("/puntos-acopio").get_data(as_text=True)
    assert _og(b, "og:url") == f"{SITE_URL}/puntos-acopio"
    assert "app//" not in b


def test_og_image_absoluta_por_seccion(client):
    home = client.get("/").get_data(as_text=True)
    imp = client.get("/impresion-3d").get_data(as_text=True)
    assert _og(home, "og:image") == f"{SITE_URL}/static/og/home.png"
    assert _og(imp, "og:image") == f"{SITE_URL}/static/og/impresion.png"


def test_og_title_distinto_por_seccion(client):
    titulos = {
        _og(client.get(u).get_data(as_text=True), "og:title")
        for u in ("/", "/impresion-3d", "/puntos-acopio")
    }
    assert len(titulos) == 3  # cada seccion tiene su propio titulo
    imp = _og(client.get("/impresion-3d").get_data(as_text=True), "og:title")
    assert "férula" in imp.lower()


def test_favicon_declarado_y_servido(client):
    b = client.get("/").get_data(as_text=True)
    assert 'rel="icon"' in b
    assert client.get("/static/favicon.svg").status_code == 200


def _png_size(data):
    import struct

    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", data[16:24])  # ancho, alto (IHDR)


def test_og_images_existen_1200x630(client):
    for seccion in ("home", "impresion", "puntos"):
        r = client.get(f"/static/og/{seccion}.png")
        assert r.status_code == 200
        assert _png_size(r.data) == (1200, 630)


def test_og_image_apunta_a_archivo_servido(client):
    b = client.get("/impresion-3d").get_data(as_text=True)
    ruta = _og(b, "og:image").removeprefix(SITE_URL)
    assert client.get(ruta).status_code == 200
