import textwrap
from services import contenido


def _escribir_yaml(tmp_path, texto):
    p = tmp_path / "contenido.yaml"
    p.write_text(textwrap.dedent(texto), encoding="utf-8")
    return p


def test_listar_modelos3d_devuelve_todos(tmp_path):
    p = _escribir_yaml(tmp_path, """
        modelos_3d:
          - nombre: "Ferula A"
            url: "https://ejemplo/a"
          - nombre: "Ferula B"
            url: "https://ejemplo/b"
    """)
    modelos = contenido.listar_modelos3d(path=p)
    assert [m["nombre"] for m in modelos] == ["Ferula A", "Ferula B"]


def test_listar_puntos_filtra_por_pais_y_ciudad(tmp_path):
    p = _escribir_yaml(tmp_path, """
        puntos_acopio:
          - nombre: "P1"
            pais: "Colombia"
            ciudad: "Bogota"
            direccion: "Calle 1"
          - nombre: "P2"
            pais: "Colombia"
            ciudad: "Medellin"
            direccion: "Calle 2"
          - nombre: "P3"
            pais: "Ecuador"
            ciudad: "Quito"
            direccion: "Calle 3"
    """)
    assert [x["nombre"] for x in contenido.listar_puntos(path=p)] == ["P1", "P2", "P3"]
    assert [x["nombre"] for x in contenido.listar_puntos(pais="Colombia", path=p)] == ["P1", "P2"]
    assert [x["nombre"] for x in contenido.listar_puntos(pais="Colombia", ciudad="Bogota", path=p)] == ["P1"]


def test_mapa_url_se_genera_cuando_falta(tmp_path):
    p = _escribir_yaml(tmp_path, """
        puntos_acopio:
          - nombre: "P1"
            pais: "Colombia"
            ciudad: "Bogota"
            direccion: "Calle 53 13-20"
    """)
    punto = contenido.listar_puntos(path=p)[0]
    assert punto["mapa_url"].startswith("https://www.google.com/maps/search/?api=1&query=")
    assert "Calle" in punto["mapa_url"]
    assert "Bogota" in punto["mapa_url"]
    assert "Colombia" in punto["mapa_url"]


def test_mapa_url_respeta_override(tmp_path):
    p = _escribir_yaml(tmp_path, """
        puntos_acopio:
          - nombre: "P1"
            pais: "Colombia"
            ciudad: "Bogota"
            direccion: "Calle 1"
            mapa_url: "https://maps.example/p1"
    """)
    assert contenido.listar_puntos(path=p)[0]["mapa_url"] == "https://maps.example/p1"


def test_opciones_filtro_valores_unicos_ordenados(tmp_path):
    p = _escribir_yaml(tmp_path, """
        puntos_acopio:
          - {nombre: P1, pais: Colombia, ciudad: Medellin, direccion: c1}
          - {nombre: P2, pais: Colombia, ciudad: Bogota, direccion: c2}
          - {nombre: P3, pais: Ecuador, ciudad: Quito, direccion: c3}
    """)
    opciones = contenido.opciones_filtro(path=p)
    assert opciones["paises"] == ["Colombia", "Ecuador"]
    assert opciones["ciudades"] == ["Bogota", "Medellin", "Quito"]


def test_archivo_inexistente_devuelve_vacio(tmp_path):
    faltante = tmp_path / "no_existe.yaml"
    assert contenido.listar_modelos3d(path=faltante) == []
    assert contenido.listar_puntos(path=faltante) == []
    assert contenido.opciones_filtro(path=faltante) == {"paises": [], "ciudades": []}


def test_entrada_no_dict_se_ignora_sin_error(tmp_path):
    p = _escribir_yaml(tmp_path, """
        modelos_3d:
          - "texto suelto"
          - nombre: "Valido"
            url: "https://x/y"
        puntos_acopio:
          - "otra cosa"
          - nombre: "P1"
            pais: "Colombia"
            ciudad: "Bogota"
            direccion: "Calle 1"
    """)
    assert [m["nombre"] for m in contenido.listar_modelos3d(path=p)] == ["Valido"]
    assert [x["nombre"] for x in contenido.listar_puntos(path=p)] == ["P1"]
    assert contenido.opciones_filtro(path=p) == {"paises": ["Colombia"], "ciudades": ["Bogota"]}


def test_yaml_malformado_devuelve_vacio(tmp_path):
    p = tmp_path / "contenido.yaml"
    p.write_text("modelos_3d: [unclosed\n", encoding="utf-8")
    assert contenido.listar_modelos3d(path=p) == []
    assert contenido.listar_puntos(path=p) == []


def test_listar_puntos_filtra_solo_por_ciudad(tmp_path):
    p = _escribir_yaml(tmp_path, """
        puntos_acopio:
          - {nombre: P1, pais: Colombia, ciudad: Bogota, direccion: c1}
          - {nombre: P2, pais: Ecuador, ciudad: Bogota, direccion: c2}
          - {nombre: P3, pais: Colombia, ciudad: Medellin, direccion: c3}
    """)
    assert [x["nombre"] for x in contenido.listar_puntos(ciudad="Bogota", path=p)] == ["P1", "P2"]
