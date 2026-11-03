# Cierre verificable — universidades de Cartagena en CampusMarket

**Fecha de operación:** noche del 2026-11-02 (America/Bogota), con CI y registros de GitHub del 2026-11-03 UTC. **Ámbito:** incremento de producto posterior a S13. No se atribuyen retroactivamente estas evidencias a S8–S13.

## 1. Cadena de trazabilidad

| Eslabón | Evidencia |
|---|---|
| Desarrollo | [PR #81](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/pull/81) — universidades, perfiles, publicaciones y catálogo; fusionado |
| Promoción de imagen | [PR #82](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/pull/82) — actualización dirigida de `api.image`; merge [`b75e5a0`](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/commit/b75e5a0023ab6abd850d400f8d6372b71b034699) |
| Construcción | [GitHub Actions 41569297341](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41569297341), exitosa; fuente `50d9352e5081f8c3e470bd9cda9220d21b14cc0a` |
| Imagen inmutable instalada | `ghcr.io/nnigarp/campusmarket-web-universidades@sha256:384cbd0c08242d4a6d0343f26fab8521fd027908b639f638b2b9653f0f53dde1` |
| Imagen de retorno identificada | `ghcr.io/nnigarp/campusmarket-web-candidate@sha256:65d34f2de8d035d5a9672be2e6a81bab759089da2fbe91bdca23a17f2f0463fd` |
| Ajuste de referencia S10 | [PR #83](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/pull/83); se cambia la revisión esperada a `50d9352e5081f8c3e470bd9cda9220d21b14cc0a`, sin retirar los nueve criterios del experimento |

## 2. Producto implementado

- `GET /universidades` devuelve doce instituciones de Cartagena.
- En registro y perfil, la universidad es **declarada**, no validada mediante un correo institucional.
- `universidad_id` opcional en usuarios y publicaciones; publicaciones antiguas sin institución permanecen visibles en «Toda Cartagena».
- La asociación de una publicación nueva se toma del perfil del propietario al crearla. Cambios posteriores de perfil no la reasignan.
- `GET /catalogo?universidad_id=ID` y filtro Flutter «Mi universidad» se integran con el catálogo anterior.
- Web y API se sirven en un contenedor `api`; MySQL 8.4 permanece en otro `db`.

## 3. Evidencia verificable

El ensayo GHCR de la versión `50d9352` validó Flutter Web, análisis, pruebas, base MySQL 8.4 efímera, `/health`, `/app/`, doce universidades, filtro de catálogo y **igualdad exacta** entre el OpenAPI producido por la imagen y `contracts/openapi-v2.json`.

El despliegue Dokploy del 2026-11-02 registró `Image ... Pulled`, `api-1 Recreate/Recreated/Starting/Started` y `Docker Compose Deployed: ✅`. No registró recreación de `db-1`. En comprobaciones posteriores del navegador se observaron `/health` con `status: ok`, `/universidades` con doce entradas, Flutter Web funcional bajo `/app/` y cuatro publicaciones en el catálogo. Estas observaciones no sustituyen una prueba de restauración de respaldo ni certifican por sí solas la identidad de todos los montajes.

Tras el despliegue, el experimento S10 del [run 41576332272](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41576332272) comprobó **ocho de nueve condiciones**: entre ellas, igualdad del contrato público y versionado. El único criterio falso era `single_expected_runtime_revision`, por referencia fija a la versión previa; la revisión real observada fue `50d9352`. Se preparó la actualización trazable por PR #83. La aceptación final de ese PR y su ejecución verde deben validarse en la página del PR/Actions, no inferirse del cambio documental.

## 4. Topología y riesgo residual

Se mantiene `campusmarket → production → sistema`, Compose `deploy/compose.prod.yaml`, servicios `api` y `db`, red externa `campusmarket-sistema-2zvsxj`, volúmenes `publication_images` y `mysql_data` y presupuesto 256 MiB por servicio. `Autodeploy` quedó desactivado. El comando de promoción incluyó `--no-deps --no-build --pull always api`, sin `down` ni `Fresh Volumes`.

**Limitaciones sin ocultar:** se creó un volcado SQL comprimido de prueba dentro de `db-1` y se verificó su gzip y las seis tablas visibles, pero **no** existe copia externa/restauración acreditada; tampoco consta respaldo independiente de fotografías. El contenido cifrado de una copia se compartió por error en la conversación; proteger futuras copias con nueva clave y transferencia autorizada. No considerar solventado el riesgo T13-10. Los datos presentes se trataban como datos de prueba, sin que ello autorice destrucción de volúmenes.

## 5. Documentos relacionados

- [Diseño de universidades](../diseno/universidades-cartagena-grupo1.md).
- [arc42 §5 — bloques](../arc42/05-bloques-de-construccion.md).
- [arc42 §7 — despliegue](../arc42/07-vista-despliegue.md).
- [arc42 §11 — riesgos](../arc42/11-riesgos-y-deuda-tecnica.md).
- [Cierre institucional anterior](cierre-web-institucional-2026-11-01.md), preservado como evidencia histórica.
