# Árbol de utilidad - CampusMarket

El árbol de utilidad permite organizar los atributos de calidad de CampusMarket y relacionarlos con escenarios concretos.

# Utilidad

## 1. Seguridad

### Refinamiento: Control de acceso a publicaciones

**Escenario relacionado:** [EC-02](10-escenarios-de-calidad.md#ec-02---protección-de-publicaciones) - Protección de publicaciones.

Un estudiante que no sea propietario de una publicación no podrá modificarla ni eliminarla.

**Impacto en el negocio:** Alto.

**Riesgo técnico:** Alto.

**Prioridad:** Alta.

---

## 2. Mantenibilidad

### Refinamiento: Facilidad de modificación

**Escenario relacionado:** [EC-03](10-escenarios-de-calidad.md#ec-03---modificación-del-sistema) - Modificación del sistema.

El equipo debe poder agregar nuevas características relacionadas con los productos sin tener que modificar funciones no relacionadas.

**Impacto en el negocio:** Alto.

**Riesgo técnico:** Alto.

**Prioridad:** Alta.

---

## 3. Rendimiento

### Refinamiento: Tiempo de respuesta de búsquedas

**Escenario relacionado:** [EC-01](10-escenarios-de-calidad.md#ec-01---consulta-de-productos) - Consulta de productos.

El sistema debe responder adecuadamente cuando un estudiante busque o filtre productos.

**Impacto en el negocio:** Alto.

**Riesgo técnico:** Medio.

**Prioridad:** Alta.

---

## 4. Disponibilidad

### Refinamiento: Recuperación ante fallas

**Escenario relacionado:** [EC-04](10-escenarios-de-calidad.md#ec-04---recuperación-del-prototipo) - Recuperación del prototipo.

Si CampusMarket deja de responder, el equipo debe poder recuperar el funcionamiento en un tiempo razonable.

**Impacto en el negocio:** Medio.

**Riesgo técnico:** Medio.

**Prioridad:** Media.

---

# Resumen de prioridades

| Atributo | Refinamiento | Escenario | Impacto | Riesgo | Prioridad |
|---|---|---|---|---|---|
| Seguridad | Control de acceso | [EC-02](10-escenarios-de-calidad.md#ec-02---protección-de-publicaciones) | Alto | Alto | Alta |
| Mantenibilidad | Facilidad de modificación | [EC-03](10-escenarios-de-calidad.md#ec-03---modificación-del-sistema) | Alto | Alto | Alta |
| Rendimiento | Tiempo de respuesta | [EC-01](10-escenarios-de-calidad.md#ec-01---consulta-de-productos) | Alto | Medio | Alta |
| Disponibilidad | Recuperación | [EC-04](10-escenarios-de-calidad.md#ec-04---recuperación-del-prototipo) | Medio | Medio | Media |

## Conclusión

La seguridad y la mantenibilidad reciben la mayor atención debido a que CampusMarket debe proteger correctamente las publicaciones de los estudiantes y permitir que el sistema pueda evolucionar durante el semestre.

El rendimiento también tiene una prioridad alta porque afecta directamente la experiencia del estudiante al consultar productos.




La disponibilidad se considera importante, aunque durante el prototipo académico se acepta un tiempo de recuperación mayor al que podría exigirse en un sistema comercial.
