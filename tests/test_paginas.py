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
