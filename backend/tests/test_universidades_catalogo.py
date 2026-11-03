from backend.app.universidades.catalogo import listar_instituciones


def test_catalogo_cartagena_tiene_ids_unicos_y_nombres():
    instituciones = listar_instituciones()
    assert len(instituciones) >= 10
    assert len({item["id"] for item in instituciones}) == len(instituciones)
    assert len({item["nombre"] for item in instituciones}) == len(instituciones)
    assert all(item["ciudad"] == "Cartagena" for item in instituciones)
    assert all(item["nombre"].strip() and item["sigla"].strip() for item in instituciones)


def test_catalogo_incluye_universidades_principales():
    nombres = {item["nombre"] for item in listar_instituciones()}
    assert "Universidad Tecnológica de Bolívar" in nombres
    assert "Universidad de Cartagena" in nombres


def test_listar_instituciones_no_expone_datos_mutables_globales():
    primera = listar_instituciones()
    primera[0]["nombre"] = "Modificado"
    assert listar_instituciones()[0]["nombre"] == "Universidad Tecnológica de Bolívar"
