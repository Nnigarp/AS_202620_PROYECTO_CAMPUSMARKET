"""Catálogo inicial de instituciones de educación superior de Cartagena.

Los identificadores son estables y no representan verificación de matrícula.
La lista puede ampliarse conservando los IDs ya publicados.
"""

INSTITUCIONES_CARTAGENA = (
    (1, "Universidad Tecnológica de Bolívar", "UTB"),
    (2, "Universidad de Cartagena", "UdeC"),
    (3, "Universidad del Sinú - Seccional Cartagena", "Unisinú"),
    (4, "Universidad de San Buenaventura - Cartagena", "USB Cartagena"),
    (5, "Universidad Libre - Cartagena", "Unilibre"),
    (6, "Fundación Universitaria Tecnológico Comfenalco", "Comfenalco"),
    (7, "Corporación Universitaria Rafael Núñez", "CURN"),
    (8, "Fundación Universitaria Colombo Internacional", "Unicolombo"),
    (9, "Universidad Antonio de Arévalo", "Unitecnar"),
    (10, "Institución Universitaria Mayor de Cartagena", "UMAYOR"),
    (11, "Institución Universitaria Bellas Artes y Ciencias de Bolívar", "UNIBAC"),
    (12, "Universidad Nacional Abierta y a Distancia", "UNAD"),
)


def listar_instituciones() -> list[dict]:
    return [
        {"id": identificador, "nombre": nombre, "sigla": sigla, "ciudad": "Cartagena"}
        for identificador, nombre, sigla in INSTITUCIONES_CARTAGENA
    ]
