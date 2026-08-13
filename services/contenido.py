import logging
import urllib.parse
from pathlib import Path

import yaml

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "contenido.yaml"


def _cargar(path=DATA_PATH):
    """Carga el YAML de contenido. Devuelve {} si falta o esta malformado."""
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        return {}
    except yaml.YAMLError:
        logging.warning("contenido.yaml malformado: %s", path)
        return {}
    return data if isinstance(data, dict) else {}


def _mapa_url(punto):
    if punto.get("mapa_url"):
        return punto["mapa_url"]
    partes = [punto.get("direccion"), punto.get("ciudad"), punto.get("pais")]
    query = ", ".join(str(p) for p in partes if p)
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote_plus(query)


# Rango de prioridad: menor numero = mayor prioridad. Un valor ausente o
# desconocido se trata como "media".
_RANGO_PRIORIDAD = {"alta": 0, "media": 1, "baja": 2}


def _modelos_crudos(path):
    modelos = _cargar(path).get("modelos_3d") or []
    return [m for m in modelos if isinstance(m, dict)]


def _rango_prioridad(modelo):
    return _RANGO_PRIORIDAD.get(modelo.get("prioridad"), _RANGO_PRIORIDAD["media"])


def _coincide_modelo(modelo, destinatario, tamano, ciudad):
    if destinatario and modelo.get("destinatario") != destinatario:
        return False
    if tamano and modelo.get("tamano") != tamano:
        return False
    if ciudad:
        ciudades = modelo.get("ciudades") or []
        # Sin ciudades declaradas => alcance general (coincide con cualquiera).
        if ciudades and ciudad not in ciudades:
            return False
    return True


def listar_modelos3d(destinatario=None, tamano=None, ciudad=None, *, path=DATA_PATH):
    """Modelos 3D filtrados y ordenados por prioridad.

    Devuelve ``{"activos": [...], "cubiertos": [...]}``. Los filtros se combinan
    con AND; ``ciudad`` coincide si el modelo no declara ciudades (alcance
    general) o si la incluye en su lista ``ciudades``. Cada grupo se ordena de
    mayor a menor prioridad (alta, media, baja) de forma estable, conservando el
    orden del contenido en caso de empate.
    """
    filtrados = [
        m
        for m in _modelos_crudos(path)
        if _coincide_modelo(m, destinatario, tamano, ciudad)
    ]
    activos = sorted(
        (m for m in filtrados if not m.get("cubierto")), key=_rango_prioridad
    )
    cubiertos = sorted(
        (m for m in filtrados if m.get("cubierto")), key=_rango_prioridad
    )
    return {"activos": activos, "cubiertos": cubiertos}


def _orden_punto(punto):
    # Orden: Colombia primero, luego alfabético por nombre.
    es_colombia = 0 if punto.get("pais") == "Colombia" else 1
    return (es_colombia, (punto.get("nombre") or "").casefold())


def listar_puntos(pais=None, ciudad=None, *, path=DATA_PATH):
    puntos = _cargar(path).get("puntos_acopio") or []
    resultado = []
    for p in puntos:
        if not isinstance(p, dict):
            continue
        if pais and p.get("pais") != pais:
            continue
        if ciudad and p.get("ciudad") != ciudad:
            continue
        punto = dict(p)
        punto["mapa_url"] = _mapa_url(p)
        resultado.append(punto)
    resultado.sort(key=_orden_punto)
    return resultado


def opciones_filtro(*, path=DATA_PATH):
    puntos = _cargar(path).get("puntos_acopio") or []
    paises = sorted({p.get("pais") for p in puntos if isinstance(p, dict) and p.get("pais")})
    ciudades = sorted({p.get("ciudad") for p in puntos if isinstance(p, dict) and p.get("ciudad")})
    return {"paises": paises, "ciudades": ciudades}


def opciones_filtro_modelos(*, path=DATA_PATH):
    """Opciones de filtro para modelos 3D, derivadas del contenido.

    Devuelve conjuntos ordenados y sin duplicados de ``destinatarios``,
    ``tamanos`` y ``ciudades`` (estas ultimas aplanadas de todos los modelos).
    """
    modelos = _modelos_crudos(path)
    destinatarios = sorted({m.get("destinatario") for m in modelos if m.get("destinatario")})
    tamanos = sorted({m.get("tamano") for m in modelos if m.get("tamano")})
    ciudades = sorted({c for m in modelos for c in (m.get("ciudades") or []) if c})
    return {"destinatarios": destinatarios, "tamanos": tamanos, "ciudades": ciudades}
