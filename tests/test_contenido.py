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
    assert [m["nombre"] for m in modelos["activos"]] == ["Ferula A", "Ferula B"]
    assert modelos["cubiertos"] == []


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
    assert contenido.listar_modelos3d(path=faltante) == {"activos": [], "cubiertos": []}
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
    assert [m["nombre"] for m in contenido.listar_modelos3d(path=p)["activos"]] == ["Valido"]
    assert [x["nombre"] for x in contenido.listar_puntos(path=p)] == ["P1"]
    assert contenido.opciones_filtro(path=p) == {"paises": ["Colombia"], "ciudades": ["Bogota"]}


def test_yaml_malformado_devuelve_vacio(tmp_path):
    p = tmp_path / "contenido.yaml"
    p.write_text("modelos_3d: [unclosed\n", encoding="utf-8")
    assert contenido.listar_modelos3d(path=p) == {"activos": [], "cubiertos": []}
    assert contenido.listar_puntos(path=p) == []


def test_listar_puntos_filtra_solo_por_ciudad(tmp_path):
    p = _escribir_yaml(tmp_path, """
        puntos_acopio:
          - {nombre: P1, pais: Colombia, ciudad: Bogota, direccion: c1}
          - {nombre: P2, pais: Ecuador, ciudad: Bogota, direccion: c2}
          - {nombre: P3, pais: Colombia, ciudad: Medellin, direccion: c3}
    """)
    assert [x["nombre"] for x in contenido.listar_puntos(ciudad="Bogota", path=p)] == ["P1", "P2"]


# --- modelos 3D: prioridad, cubiertos y filtros -------------------------------


def test_modelos_ordenados_por_prioridad(tmp_path):
    p = _escribir_yaml(tmp_path, """
        modelos_3d:
          - {nombre: Baja, url: u, prioridad: baja}
          - {nombre: Alta, url: u, prioridad: alta}
          - {nombre: Media, url: u, prioridad: media}
    """)
    activos = contenido.listar_modelos3d(path=p)["activos"]
    assert [m["nombre"] for m in activos] == ["Alta", "Media", "Baja"]


def test_desempate_estable_por_orden_de_contenido(tmp_path):
    p = _escribir_yaml(tmp_path, """
        modelos_3d:
          - {nombre: A1, url: u, prioridad: alta}
          - {nombre: A2, url: u, prioridad: alta}
    """)
    activos = contenido.listar_modelos3d(path=p)["activos"]
    assert [m["nombre"] for m in activos] == ["A1", "A2"]


def test_prioridad_ausente_se_trata_como_media(tmp_path):
    p = _escribir_yaml(tmp_path, """
        modelos_3d:
          - {nombre: SinPrioridad, url: u}
          - {nombre: Baja, url: u, prioridad: baja}
          - {nombre: Alta, url: u, prioridad: alta}
    """)
    activos = contenido.listar_modelos3d(path=p)["activos"]
    assert [m["nombre"] for m in activos] == ["Alta", "SinPrioridad", "Baja"]


def test_separa_cubiertos_de_activos(tmp_path):
    p = _escribir_yaml(tmp_path, """
        modelos_3d:
          - {nombre: Activo, url: u, prioridad: alta}
          - {nombre: Cubierto, url: u, prioridad: alta, cubierto: true}
    """)
    modelos = contenido.listar_modelos3d(path=p)
    assert [m["nombre"] for m in modelos["activos"]] == ["Activo"]
    assert [m["nombre"] for m in modelos["cubiertos"]] == ["Cubierto"]


def test_filtro_por_destinatario(tmp_path):
    p = _escribir_yaml(tmp_path, """
        modelos_3d:
          - {nombre: Persona, url: u, destinatario: personas}
          - {nombre: Mascota, url: u, destinatario: mascotas}
    """)
    activos = contenido.listar_modelos3d(destinatario="mascotas", path=p)["activos"]
    assert [m["nombre"] for m in activos] == ["Mascota"]


def test_filtro_por_tamano(tmp_path):
    p = _escribir_yaml(tmp_path, """
        modelos_3d:
          - {nombre: Peq, url: u, tamano: pequeno}
          - {nombre: Gra, url: u, tamano: grande}
    """)
    activos = contenido.listar_modelos3d(tamano="pequeno", path=p)["activos"]
    assert [m["nombre"] for m in activos] == ["Peq"]


def test_filtro_por_ciudad_multi_ciudad_y_general(tmp_path):
    p = _escribir_yaml(tmp_path, """
        modelos_3d:
          - {nombre: MultiCiudad, url: u, ciudades: [Bogota, Cali]}
          - {nombre: General, url: u}
          - {nombre: OtraCiudad, url: u, ciudades: [Medellin]}
    """)
    activos = contenido.listar_modelos3d(ciudad="Bogota", path=p)["activos"]
    # multi-ciudad que incluye Bogota + modelo sin ciudades (general); OtraCiudad se oculta
    assert [m["nombre"] for m in activos] == ["MultiCiudad", "General"]


def test_filtros_combinados_and(tmp_path):
    p = _escribir_yaml(tmp_path, """
        modelos_3d:
          - {nombre: Match, url: u, destinatario: personas, tamano: pequeno, ciudades: [Bogota]}
          - {nombre: OtroTamano, url: u, destinatario: personas, tamano: grande, ciudades: [Bogota]}
          - {nombre: OtraCiudad, url: u, destinatario: personas, tamano: pequeno, ciudades: [Cali]}
          - {nombre: Mascota, url: u, destinatario: mascotas, tamano: pequeno, ciudades: [Bogota]}
    """)
    activos = contenido.listar_modelos3d(
        destinatario="personas", tamano="pequeno", ciudad="Bogota", path=p
    )["activos"]
    assert [m["nombre"] for m in activos] == ["Match"]


def test_modelo_heredado_sin_campos_nuevos_es_activo_media(tmp_path):
    p = _escribir_yaml(tmp_path, """
        modelos_3d:
          - {nombre: Heredado, url: u, material: PLA, categoria: ferula}
    """)
    modelos = contenido.listar_modelos3d(path=p)
    assert [m["nombre"] for m in modelos["activos"]] == ["Heredado"]
    assert modelos["cubiertos"] == []
    # sin prioridad declarada se ubica como media: va despues de una alta
    p2 = _escribir_yaml(tmp_path, """
        modelos_3d:
          - {nombre: Heredado, url: u}
          - {nombre: Alta, url: u, prioridad: alta}
    """)
    activos = contenido.listar_modelos3d(path=p2)["activos"]
    assert [m["nombre"] for m in activos] == ["Alta", "Heredado"]


def test_opciones_filtro_modelos_unicas_ordenadas(tmp_path):
    p = _escribir_yaml(tmp_path, """
        modelos_3d:
          - {nombre: A, url: u, destinatario: personas, tamano: pequeno, ciudades: [Medellin, Bogota]}
          - {nombre: B, url: u, destinatario: mascotas, tamano: grande, ciudades: [Bogota]}
          - {nombre: C, url: u, destinatario: personas, tamano: pequeno}
    """)
    opciones = contenido.opciones_filtro_modelos(path=p)
    assert opciones["destinatarios"] == ["mascotas", "personas"]
    assert opciones["tamanos"] == ["grande", "pequeno"]
    assert opciones["ciudades"] == ["Bogota", "Medellin"]


def test_opciones_filtro_modelos_archivo_inexistente(tmp_path):
    faltante = tmp_path / "no_existe.yaml"
    assert contenido.opciones_filtro_modelos(path=faltante) == {
        "destinatarios": [],
        "tamanos": [],
        "ciudades": [],
    }
