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
