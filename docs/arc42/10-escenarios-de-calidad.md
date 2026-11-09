# Escenarios de calidad - CampusMarket

Los siguientes escenarios convierten los atributos de calidad de CampusMarket
en condiciones observables y verificables.

Los escenarios fueron definidos y verificados en diferentes momentos de la
evolución del proyecto.

Por esta razón, la documentación distingue entre:

- escenarios todavía previstos;
- escenarios materializados actualmente;
- escenarios históricos verificados bajo una arquitectura anterior.

---

## Tensiones entre atributos de calidad

### Mantenibilidad vs rapidez de desarrollo

Una mayor separación entre módulos, responsabilidades y contratos internos
favorece la mantenibilidad porque permite realizar cambios con menor impacto
sobre funcionalidades no relacionadas.

Sin embargo, introducir más abstracciones, validaciones y fronteras requiere un
mayor esfuerzo inicial.

CampusMarket prioriza mantener fronteras claras entre capacidades del negocio
aunque esto implique un costo inicial moderado.

---

### Rendimiento vs mantenibilidad

Índices, cachés o lógica especializada pueden mejorar el rendimiento.

Sin embargo, también incrementan la complejidad del sistema.

En el estado actual se prioriza una implementación sencilla y modular mientras
se satisfagan los umbrales definidos.

Las optimizaciones futuras deberán justificarse mediante mediciones.

---

### Disponibilidad vs simplicidad operativa

Agregar infraestructura especializada puede aumentar la tolerancia ante
determinados fallos.

También incrementa:

- complejidad;
- operación;
- despliegue;
- mantenimiento.

Durante S5 se priorizó mantener SQLite debido a la restricción R-07 del primer
corte.

Ese contexto corresponde a una etapa histórica del proyecto.

Posteriormente, por observación del docente, la persistencia evolucionó hacia
MySQL mediante ADR-0004.

---

# EC-01 - Consulta de productos

**Atributo de calidad:** Rendimiento.

**Fuente:** Estudiante.

**Estímulo:** El estudiante realiza una búsqueda o aplica un filtro sobre el
catálogo.

**Artefacto:** Funcionalidad de consulta de productos.

**Entorno:** Operación normal con un catálogo de hasta 1.000 publicaciones.

**Respuesta:** El sistema procesa la consulta y muestra los productos que
coinciden con los criterios seleccionados.

**Medida verificable:** En una prueba de 10 búsquedas consecutivas, por lo menos
9 deben mostrar resultados en un máximo de 2 segundos.

**Prioridad:** Alta.

**Estado:** Materializado; medición CI/Compose verificada. El escenario completo
con resultados mostrados en navegador público y 1000 filas no está verificado.

La primera [medición S9](../evidencias/evidencia-ec01-catalogo-s9-2026-10-01.md)
utiliza publicaciones controladas y no incluye MySQL/red pública.
La medición posterior del commit b5f10a2c93836cad539a9a195f6a0911d4b3ca91
usa 1000 filas MySQL reales, HTTP loopback y Compose bajo cuota:
[run 37175935055](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/37175935055),
10/10 en <=2000 ms (umbral exigido >=9/10), rango 255,65–299,32 ms.
Las muestras y límites están en el [complemento final S9](../evidencias/evidencia-s9-2026-10-01.md#17-complemento-final-de-auditoria-s9--4-de-octubre-de-2026).
No se atribuyen a este SHA valores históricos ni latencia de navegador público.

[Evaluación S14 de la imagen vigente](../evidencias/evidencia-s14-ec01-2026-11-05.md): HTTP/MySQL con 1.000 filas verificado en CI; experiencia completa en navegador NO CONCLUYENTE. Se conserva el umbral original y la distinción de entorno.

---

# EC-02 - Protección de publicaciones

**Atributo de calidad:** Seguridad.

**Fuente:** Usuario autenticado.

**Estímulo:** El usuario intenta editar o eliminar una publicación que
pertenece a otro estudiante.

**Artefacto:** Gestión de publicaciones.

**Entorno:** Operación normal con dos usuarios diferentes.

**Respuesta:** CampusMarket rechaza la operación y mantiene la publicación sin
modificaciones.

**Medida verificable:** 10 de 10 intentos realizados por un usuario no
propietario deben ser rechazados.

**Prioridad:** Alta.

**Estado:** Materializado y verificado al nivel MVP.

Usuarios registra/autentica A y B mediante sesiones reales. Publicaciones usa el
ID del token en predicados SQL; no acepta propietario de entrada. Diez ataques
de B (edición, estado, borrado y galería) son rechazados y el dato de A se comprueba
tras cada intento. Web de escritorio, Web móvil y Android ejecutan el mismo flujo.
Pruebas: `test_ec02_autorizacion.py`, `test_imagenes_seguras.py` y mutación del
predicado de propietario. [Evidencia por hash](../evidencias/auditoria-mvp-continuacion-2026-10-03.md).

---

# EC-03 - Modificación del sistema

**Atributo de calidad:** Mantenibilidad.

**Fuente:** Equipo de desarrollo.

**Estímulo:** Se solicita agregar un nuevo estado de producto, por ejemplo:

`reacondicionado`

**Artefacto:** Gestión de Publicaciones.

**Entorno:** Desarrollo normal.

**Respuesta:** El equipo incorpora la nueva opción sin modificar
funcionalidades no relacionadas.

**Medida verificable:** El cambio debe realizarse modificando como máximo dos
módulos principales y sin requerir cambios en autenticación o búsqueda.

**Prioridad:** Alta.

**Decisión relacionada:**

[ADR-0001 - Monolito modular](../adr/0001-usar-monolito-modular.md)

**Estado:** Verificado durante la evolución del corte vertical.

**Alcance de la declaración anterior — revisión documental del 8/nov/2026:** el
estado histórico se conserva, pero no se localizó un commit/medición enlazado
que contabilice el cambio EC-03 frente al máximo de dos módulos. Admitir
`reacondicionado` en código o pasar CI no mide por sí solo ese esfuerzo. La
[auditoría S1–S14](../evidencias/auditoria-documental-s1-s14-2026-11-08.md)
mantiene esa brecha; no se modifica el escenario ni su umbral.

---

# EC-04 - Recuperación del prototipo

**Atributo de calidad:** Disponibilidad / recuperación.

**Fuente:** Administrador o equipo de desarrollo.

**Estímulo:** La aplicación deja de responder durante una prueba o demostración.

**Artefacto:** CampusMarket.

**Entorno:** Ejecución del prototipo.

**Respuesta:** El equipo recupera el servicio y vuelve a permitir el acceso sin
perder información almacenada correctamente antes de la falla.

**Medida verificable:** El prototipo debe volver a estar disponible en un
máximo de 10 minutos después de detectar la falla.

**Prioridad:** Media.

---

# EC-05 - Degradación ante bloqueo temporal de persistencia

> **Estado histórico:** escenario definido y verificado durante S5, cuando
> SQLite era la tecnología de persistencia vigente.

**Atributo de calidad:** Disponibilidad / resiliencia.

**Fuente:** Estudiante que intenta crear una publicación.

**Estímulo histórico:** SQLite se encuentra temporalmente bloqueada cuando el
estudiante intenta crear una nueva publicación.

**Artefacto:** Corte vertical de creación de publicaciones.

**Entorno histórico:** Aplicación utilizando SQLite durante el primer corte,
con un bloqueo de escritura provocado de forma reproducible.

**Respuesta esperada durante S5:** CampusMarket rechaza temporalmente la
operación de forma controlada, no produce una escritura parcial y recupera la
creación normal después de liberar la base de datos.

**Medida verificable de S5:**

- HTTP `503`;
- tiempo máximo de 2 segundos;
- ninguna escritura parcial;
- después de liberar SQLite, una nueva creación responde HTTP `201`.

**Prioridad:** Alta durante S5.

**Restricción relacionada:**

[R-07 - Persistencia sin nueva infraestructura durante el primer corte](02-restricciones.md#r-07-persistencia-sin-nueva-infraestructura-durante-el-primer-corte)

**Decisión histórica relacionada:**

[ADR-0002 - Manejo de bloqueo temporal de SQLite](../adr/0002-manejo-bloqueo-sqlite.md)

---

## Línea base histórica de EC-05

La medición del 05/09/2026 obtuvo:

| Métrica | Línea base |
|---|---:|
| HTTP durante bloqueo | `500` |
| Tiempo durante bloqueo | `7.323 s` |
| Escritura parcial | `No` |
| HTTP después de liberar SQLite | `201` |
| Tiempo de recuperación | `0.007 s` |

La implementación preservaba la integridad de los datos y recuperaba la
operación normal.

Sin embargo:

- respondía HTTP `500`;
- tardaba `7.323 s`;
- superaba el umbral de 2 segundos.

Evidencia:

[Medición antes del cambio](../evidencias/linea-base-bloqueo-sqlite-2026-09-05.md)

---

## Respuesta arquitectónica histórica de EC-05

Durante S5 se adoptó ADR-0002.

La solución aplicó:

- timeout SQLite de `0.5 s`;
- detección de `SQLITE_BUSY`;
- detección de `SQLITE_LOCKED`;
- traducción controlada de indisponibilidad;
- HTTP `503 Service Unavailable`;
- ausencia de reintentos automáticos;
- preservación de transacciones;
- cierre explícito de conexiones;
- recuperación posterior.

La arquitectura de ese momento era:

```text
Flutter
   ↓
FastAPI
   ↓
Gestión de Publicaciones
   ↓
SQLite
```

Esta arquitectura **no representa la persistencia vigente**.

---

## Resultado histórico de EC-05

La medición formal del 06/09/2026 produjo:

| Métrica                        | Línea base | Después de ADR-0002 |      Umbral |
| ------------------------------ | ---------: | ------------------: | ----------: |
| HTTP durante bloqueo           |      `500` |               `503` |       `503` |
| Tiempo durante bloqueo         |  `7.323 s` |           `1.283 s` |     `≤ 2 s` |
| Escritura parcial              |       `No` |                `No` |        `No` |
| HTTP después de liberar SQLite |      `201` |               `201` |       `201` |
| Tiempo de recuperación         |  `0.007 s` |           `0.006 s` | Informativo |

Por tanto, EC-05 fue satisfecho durante S5.

Una ejecución posterior obtuvo además:

* HTTP `503`;
* `1.138 s`;
* ninguna escritura parcial;
* recuperación HTTP `201`.

Evidencia:

[Medición posterior](../evidencias/medicion-bloqueo-sqlite-2026-09-06.md)

---

## Evolución posterior de EC-05

Después del primer corte, el docente indicó que la persistencia debía
evolucionar hacia MySQL.

La decisión se registró mediante:

[ADR-0004 - Migrar persistencia a MySQL](../adr/0004-migrar-persistencia-a-mysql.md)

Por esta razón:

* EC-05 conserva valor como evidencia histórica;
* las mediciones de SQLite no se reinterpretan como mediciones de MySQL;
* `SQLITE_BUSY` y `SQLITE_LOCKED` no describen el comportamiento vigente;
* la prueba actual `test_publicaciones_vertical.py` ya utiliza MySQL.

La arquitectura vigente es:

```text
Flutter
   ↓ HTTP/JSON
FastAPI
   ↓
Gestión de Publicaciones
   ↓ PyMySQL
MySQL
```

Actualmente se conserva el comportamiento general de degradación controlada:

* si la persistencia no está disponible;
* el backend traduce el fallo;
* el consumidor recibe HTTP `503`.

El mecanismo técnico concreto ya no depende de bloqueos SQLite.

---

# EC-06 - Compatibilidad del contrato de API

**Atributo de calidad:** Compatibilidad / mantenibilidad.

**Fuente:** Equipo de desarrollo o proveedor de API.

**Estímulo:** Se elimina, renombra o modifica de forma incompatible una ruta,
operación, campo o respuesta utilizada por el frontend.

**Artefacto:** Contrato OpenAPI y proveedor FastAPI.

**Entorno:** Integración continua antes de fusionar cambios a la rama
principal.

**Respuesta:** La prueba compara la especificación versionada con la superficie
OpenAPI generada por FastAPI y detecta la incompatibilidad.

**Medida verificable:** Los cambios incompatibles utilizados durante la
demostración S7 deben hacer fallar la prueba; después de restaurar el contrato,
el conjunto completo debe volver a verde.

**Prioridad:** Alta.

**Decisión relacionada:**

[ADR-0003 - Integración síncrona HTTP/JSON](../adr/0003-usar-integracion-sincrona-http-json.md)

**Contrato:**

[`contracts/openapi-v2.json`](../../contracts/openapi-v2.json); v1 se conserva como historia S7.

**Prueba:**

[`backend/tests/test_contrato_openapi.py`](../../backend/tests/test_contrato_openapi.py)

**Evidencia:**

[Demostración de cambio incompatible S7](../evidencias/fallo-contrato-s7-2026-09-15.md)

---

# Resumen de estado

| Escenario | Estado                                                    |
| --------- | --------------------------------------------------------- |
| EC-01     | Materializado y verificado en S9                          |
| EC-02     | MVP: dos cuentas reales, 10/10 denegaciones y datos intactos |
| EC-03     | Materializado y utilizado para verificar mantenibilidad   |
| EC-04     | Materializado mediante recuperación del prototipo         |
| EC-05     | Verificado históricamente en S5 con SQLite                |
| EC-06     | Materializado en S7 mediante OpenAPI y prueba de contrato |

La documentación conserva los resultados históricos sin confundirlos con la
arquitectura vigente.
