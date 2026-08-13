def test_home_ok_y_muestra_handle(client):
    resp = client.get("/")
    assert resp.status_code == 200
    cuerpo = resp.get_data(as_text=True)
    assert "Manos a la Obra" in cuerpo
    assert "x.com/davidfgonzalezc" in cuerpo
