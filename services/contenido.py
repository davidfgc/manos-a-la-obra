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


def listar_modelos3d(*, path=DATA_PATH):
    modelos = _cargar(path).get("modelos_3d") or []
    return [m for m in modelos if isinstance(m, dict)]


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
    return resultado


def opciones_filtro(*, path=DATA_PATH):
    puntos = _cargar(path).get("puntos_acopio") or []
    paises = sorted({p.get("pais") for p in puntos if isinstance(p, dict) and p.get("pais")})
    ciudades = sorted({p.get("ciudad") for p in puntos if isinstance(p, dict) and p.get("ciudad")})
    return {"paises": paises, "ciudades": ciudades}
