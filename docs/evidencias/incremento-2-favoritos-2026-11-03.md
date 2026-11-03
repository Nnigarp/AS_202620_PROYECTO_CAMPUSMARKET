# Incremento 2 — Favoritos privados (2026-11-03)

## Alcance y revisión

Rama del fork: `feat/incremento-2-20261103`, base oficial/fork comprobada `c7f15748a9a9dfd8b1160ab04fb8ee544a374437`. PR oficial todavía no abierto; requiere autorización. Este corte no despliega, publica imagen ni modifica Dokploy.

Implementación: `backend/app/favoritos/{repository,service,router}.py`; lectura pública por IDs en Publicaciones y composición en Catálogo; DTOs en `catalogo/schemas.py`; `main.py` registra el router. Flutter: `lib/favoritos/`, corazones en tarjeta/detalle y destino privado en `marketplace_shell.dart`. Contrato aditivo `contracts/openapi-v2.json`. CI existente habilitado para esta rama, sin crear servicios productivos.

## Requisitos y decisiones

- GET `/favoritos`: solo usuario autenticado; no-store y ninguna identidad de entrada.
- PUT/DELETE `/favoritos/{publicacion_id}`: idempotentes; PK compuesta evita duplicados aun con concurrencia.
- MySQL conserva referencias al cerrar sesión; no son preferencias locales. No se alteran tablas heredadas.
- Las lecturas resuelven únicamente anuncios públicos vigentes, sin N+1 de fotografías. Ocultos/eliminados se omiten; reservado/vendido conserva su estado. Referencias huérfanas privadas pueden permanecer; no se publican ni se reasignan.
- Flutter vacía caché al cambiar token y descarta respuestas atrasadas; no invalida la sesión nueva ante un 401 anterior. Mis favoritos, carga/error/vacío/actualizar y corazones comparten estado.
- Reutiliza ADR-0001/0003/0012/0019/0022; no hay infraestructura, dependencias ni ADR nuevos. La propiedad de datos se verifica incluyendo el nuevo módulo.

## Verificación inicial

- Ruff: `ruff check backend scripts`, aprobado.
- Pytest local: `test_favoritos.py` (sin los tres casos que requieren MySQL), contrato, propiedad de datos y modularidad: **18 passed, 3 deselected**. Los tres casos excluidos se ejecutan en MySQL 8.4 de GitHub Actions; no se presentan como aprobados localmente.
- Actionlint de los cuatro workflows modificados: aprobado. `git diff --check`: aprobado.
- Flutter no está instalado y no hay daemon Docker local: analyze, tests y flujos reales Chrome escritorio/móvil y Android se ejecutarán en el fork. `test_favoritos.py` cubre concurrencia, sesión, privacidad, logout, estados y exclusión; `favoritos_test.dart` cubre peticiones, caché, errores, respuestas tardías y anchos 320/390/800/1440. Flujo real existente ampliado, sin sustituir sus controles anteriores.
- S10 diferencia candidato (`app.openapi()`/snapshot) de producción (contrato y revisión fija `50d9352e5081f8c3e470bd9cda9220d21b14cc0a`). No exige rutas nuevas en una versión sin promover.

## CI, commits y límites

El primer commit de este corte inicia CI. Sus SHA/runs y correcciones se registrarán aquí tras la ejecución. **Integración MySQL y Flutter: PENDIENTE hasta disponer del resultado.** No hay revisión humana o aprobación institucional afirmada. Favoritos no se declara desplegado. Mensajería comienza tras completar este corte; promoción productiva requiere proceso y autorización separados.

### Primera ejecución y corrección de fixtures

Commit de implementación/documentación: [`62b9844`](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/commit/62b984418c2d1be3f097564eef4f571bf5da1600). [Flutter run 41583438336](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41583438336): analyze aprobado; 15 tests aprobados y cuatro de layout fallaron por temporizador de sesión pendiente al verificar invariantes del test. Corrección limitada al fixture: desmontar widgets y disponer sesión/controlador en finally antes de terminar el test, conservando todas las aserciones y la expiración real de sesión. Se repite Flutter sobre el commit de corrección.

Corrección de fixtures: [`32472bd`](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/commit/32472bd2e21dac3890484dcb19c0ca0becd07172). [Flutter run 41583603859](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41583603859) aprobó analyze, **19 tests** y dos mutaciones; el control de diff detectó una línea vacía al final del DTO extraído. Se retira esa línea, sin modificar el contrato, y se habilita S10 en la rama para validar expresamente la separación candidato/producción.

### Cierre verificable del corte Favoritos

- Backend MySQL 8.4: [41583438384](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41583438384), **107 pruebas + 4 de contrato**, mutaciones y checkout limpio, sobre `62b9844`.
- Recorrido real: [41583438341](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41583438341), **Chrome 1440×1000, Chrome 390×844 y Android**, los tres aprobados sobre `62b9844`; diez criterios por plataforma, incluido Favoritos privado, corazón, pantalla, logout/login y quitar. Capturas e informe JSON en los artefactos del run.
- Corrección final: [`c701c9b`](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/commit/c701c9b794b0a9bae7793789f6b0a20f80eeb710). [Flutter 41583754499](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41583754499): analyze, **19 tests**, dos mutaciones, builds Web/APK y artefacto aprobados. [Backend 41583754152](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41583754152) aprobado. [S10 41583754549](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41583754549) aprobado con separación candidato/producción.
- Contrato aditivo: todas las rutas/esquemas anteriores conservados. Enlaces nuevos y ocho columnas de aspectos verificados localmente.

Favoritos queda implementado y probado; **no desplegado**. Los fallos intermedios anteriores permanecen registrados. Mensajería continúa como corte siguiente de la misma rama.

### Revalidación de disponibilidad al volver a la pantalla

La revisión conjunta detectó que IndexedStack conservaba la pantalla ya visitada: el listado podía quedar obsoleto después de una eliminación/ocultamiento externo. El shell ahora pide revalidación cada vez que se entra a Favoritos; la pantalla oculta resultados antiguos durante carga o error y los muestra tras la consulta vigente. Se añade test de widget con respuesta retenida: durante revalidación no se presenta la tarjeta anterior y, cuando el servidor devuelve lista vacía, desaparece definitivamente. No cambia autenticación, persistencia ni idempotencia. Se valida en el siguiente CI conjunto.
