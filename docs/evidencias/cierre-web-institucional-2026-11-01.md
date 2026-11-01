# Cierre verificable — Flutter Web institucional en CampusMarket

**Fecha de operación:** 2026-11-01 (America/Bogota). **Ámbito:** adenda posterior a S12; no se atribuye retroactivamente a S8–S12 ni se reclama nueva calificación. **Estado:** publicación funcional observada, con riesgos de recuperación todavía abiertos.

## 1. Identidad y cadena de trazabilidad

| Eslabón | Referencia verificable |
|---|---|
| Repositorio oficial | [ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET) |
| PR de promoción | [#77](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/pull/77) |
| Merge a `master` | [`5ef0d6b139138d1260435b1b884240f093904749`](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/commit/5ef0d6b139138d1260435b1b884240f093904749) |
| CI de merge | Ocho checks exitosos en la vista de GitHub del commit de `master` compartida el 1 de noviembre; URL individual de ejecución por check pendiente de consignar |
| Compose productivo | [`deploy/compose.prod.yaml`](../../deploy/compose.prod.yaml) |
| Decisión de topología | [ADR-0025](../adr/0025-servir-flutter-web-con-fastapi-en-servicio-existente.md) |
| Modelo | [arc42 §7](../arc42/07-vista-despliegue.md), [C4 nivel 2](../c4/02-contenedores.md) |
| API | https://campusmarket.iscoutb.dev/health |
| Web | https://campusmarket.iscoutb.dev/app/ |

## 2. Línea de tiempo comprobada

1. Se ensayó un `development/web-ensayo` aislado. Dokploy falló al crear `campusmarket-webensayo-r8fxkr_default` por `all predefined address pools have been fully subnetted`. **No** fue falla de Flutter ni prueba de indisponibilidad de producción. Se abandonó ese camino sin afectar el servicio existente.
2. En Docker local se ejecutaron `api` + `db` saludables y un proxy HTTP en `localhost:8088`. Se comprobó `/app/`, `/health`, creación, edición, cambio de estado, fotos y persistencia después de reiniciar los contenedores. Los volúmenes locales `campusmarket-ensayo-local-20261031_dev_mysql_data` y `..._dev_publication_images` **no son** los de producción.
3. El fork documentó ese ensayo en commit [`52762bd`](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/commit/52762bd). Se creó y fusionó PR #77; `master` aprobó sus ocho checks.
4. Se reconstruyó una imagen de regreso a la revisión `7856416795bb4accdf9d05e01adb470654875e56`. El primer run [`41341503369`](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41341503369) falló por probar `/health` sin MySQL (HTTP 503). Se corrigió el workflow para usar MySQL temporal; el [run `41341824838`](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41341824838) terminó verde y publicó la imagen por digest.
5. Antes del despliegue, `Preview Compose` mostró la red externa `campusmarket-sistema-2zvsxj`, volúmenes `mysql_data`/`publication_images`, etiquetas Traefik y dos servicios con 256 MB cada uno.
6. Se cambió el Compose Path del servicio existente de `./deploy/compose.lab.yaml` a `./deploy/compose.prod.yaml`, con `Autodeploy` desactivado; se usó **Run Command** personalizado para `api`.
7. El log de Dokploy confirmó: `Container campusmarket-sistema-2zvsxj-api-1 Recreate`, `Recreated`, `Starting`, `Started`, y `Docker Compose Deployed: ✅`. No mostró recreación de `db`.
8. Verificación pública posterior: `/health` respondió `status=ok` y `/app/` cargó la interfaz. En capturas se visualizó catálogo, inicio y Mis publicaciones con fotografías. El operador reportó operaciones exitosas de sesión, edición, estado y eliminación.
9. Dokploy Containers: `api-1` ID `899e114bcdeb`, `db-1` ID `baedd6d65e17`; ambos `running/healthy`. `db-1` conservó su ID anterior.

## 3. Artefactos reproducibles y límites

**Imagen Web + API (inmutable):**

```text
ghcr.io/nnigarp/campusmarket-web-candidate@sha256:65d34f2de8d035d5a9672be2e6a81bab759089da2fbe91bdca23a17f2f0463fd
```

**Imagen API de retorno (reconstrucción validada con MySQL sintético):**

```text
ghcr.io/nnigarp/campusmarket-api-rollback@sha256:f1114c208ed47d762fee76306cbd4d5b27134f2c18638475297f7fe8f677696b
```

**Comando ejecutado por Dokploy:**

```bash
docker compose -p campusmarket-sistema-2zvsxj --env-file deploy/.env -f ./deploy/compose.prod.yaml up -d --no-deps --no-build api
```

Se conservan dos contenedores (FastAPI/Flutter y MySQL); el volumen `publication_images` está montado en `/app/backend/uploads`; el volumen `mysql_data` en `/var/lib/mysql`. Los montajes reales se inspeccionaron desde los propios contenedores antes del despliegue, no mediante la lista vacía de montajes adicionales de la interfaz `Advanced`.

La prueba de funcionamiento y el `healthy` **no acreditan** backup independiente, recuperación después de fallo del host, rollback aplicado en el servidor ni persistencia de todos los datos ante borrado de volumen. El frontend ya se publicó, pero la operación sigue teniendo deuda de recuperabilidad.

## 4. Atributos de calidad / escenarios

| Atributo | Estímulo / entorno | Respuesta y observación | Límite |
|---|---|---|---|
| Desplegabilidad | Promover interfaz bajo dominio institucional, con dos servicios | Cambio dirigido `api`, ejecución correcta de Compose | No prueba despliegue sin interrupción |
| Disponibilidad | Abrir `/health` después de promover | Respuesta pública `status: ok`; ambos contenedores healthy | Una observación, no serie de disponibilidad |
| Integridad/persistencia | Reemplazar API sin reemplazar MySQL ni volumen de fotos | ID de MySQL igual antes/después; publicaciones y fotos visibles | No es restauración de backup |
| Funcionalidad | Navegar Web y operar publicaciones | Catálogo, Mis publicaciones, sesión, edición, estados y eliminación reportados/mostrados | No es prueba automatizada de carga o seguridad exhaustiva |

## 5. Matriz transversal CONTRATO.md (estado de este cierre)

| Control | Estado | Evidencia o falta |
|---|---|---|
| Repositorio público en ISCOUTB | Cumple | URL oficial y PR #77 |
| Estructura mínima | Cumple, por rutas inspeccionadas | `docs/arc42/`, `docs/adr/`, `docs/c4/`, `docs/aspectos.md`, `docs/ia.md`, `README.md` |
| Hash evaluable de cierre académico | No verificado | Se conoce merge productivo; falta identificar cierre de actividad específica en SAVIO |
| Convención de nombres ADR | Cumple, por nombres inspeccionados | Secuencia `0001` a `0025`; historial de reescrituras no auditado |
| Inmutabilidad histórica de ADR | No verificado | Nuevas adendas respetan archivos; falta auditoría del historial completo |
| Registro de IA actualizado | Cumple al integrarse este PR | [`docs/ia.md`](../ia.md), nuevas filas del 2026-11-01 |
| Pipeline, SonarCloud y Quality Gate del mismo hash | Parcial / No verificado | Capturas de checks en verde; falta prueba de invocación scanner, run y URL del análisis para el SHA de cierre |
| Ausencia de secretos incluyendo historial | No verificado | No se incluyen credenciales en este cierre; falta auditoría automatizada de HEAD e historial |
| Contribución de los tres integrantes | No verificado | Es necesario consolidar identidades y auditar `git shortlog` |

*Regla:* no convertir «No verificado» en «Cumple» sin logs, hash y URL correspondientes.

## 6. Siguiente operación segura

Mantener `Autodeploy` desactivado y no ejecutar de nuevo `Deploy` de forma innecesaria. Registrar el Run Command personalizado antes de retirarlo: el comando predeterminado de Dokploy incluye `--build --remove-orphans` y no equivale al procedimiento dirigido. Antes de futuros cambios, implementar un backup externo y ensayar restauración controlada. El rollback de imagen no sustituye respaldo de MySQL ni de fotografías.

## 7. Referencias relacionadas

- [Guía de operación GHCR](../operacion/despliegue-ghcr.md)
- [ADR-0024 histórico](../adr/0024-publicar-imagen-verificada-y-condicionar-promocion.md)
- [README e índice de evolución](../../README.md)
- [Contrato transversal oficial](https://github.com/ISCOUTB/AS_202620_feedback/blob/master/CONTRATO.md)
