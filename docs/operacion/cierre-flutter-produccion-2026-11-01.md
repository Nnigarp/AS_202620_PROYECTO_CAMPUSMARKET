# Cierre operativo — Flutter Web en producción (2026-11-01)

## Alcance y trazabilidad

- Proyecto: CampusMarket, UTB.
- Servicio existente: `campusmarket → production → sistema` (Dokploy).
- Sitio: https://campusmarket.iscoutb.dev/app/
- API: https://campusmarket.iscoutb.dev/health
- Repositorio oficial: `ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET`.
- PR de preparación #77, fusionado a `master`, commit de merge `5ef0d6b139138d1260435b1b884240f093904749`; 8 checks en verde en `master` según GitHub.
- Compose de despliegue: `./deploy/compose.prod.yaml`.
- Imagen fijada: `ghcr.io/nnigarp/campusmarket-web-candidate@sha256:65d34f2de8d035d5a9672be2e6a81bab759089da2fbe91bdca23a17f2f0463fd`.
- Comando ejecutado en Dokploy:
  `docker compose -p campusmarket-sistema-2zvsxj --env-file deploy/.env -f ./deploy/compose.prod.yaml up -d --no-deps --no-build api`.
- El log finalizó con `Docker Compose Deployed: ✅`; solo registra `api-1 Recreate/Recreated/Starting/Started`. No registra recreación de `db-1`.

## Verificaciones posteriores aportadas por el operador

- `GET /health` devolvió `{"status":"ok","service":"campusmarket-api"}`.
- `/app/` cargó Flutter Web en el dominio institucional.
- Navegación y catálogo visibles; se muestran productos y fotos.
- El operador verificó inicio de sesión, edición y eliminación de publicaciones, y visualizó `Mis publicaciones` en producción.
- Captura de Dokploy: `api-1` running/healthy (ID `899e114bcdeb`); `db-1` running/healthy (ID `baedd6d65e17`, sin cambio respecto a comprobaciones anteriores).
- Se conservaron en Compose `mysql_data` y `publication_images`, con red externa `campusmarket-sistema-2zvsxj`.
- Se mantiene el servicio `sistema` con dos contenedores, FastAPI+Flutter y MySQL.

## Referencia de recuperación

- Imagen de retorno compilada desde la revisión productiva previa `7856416795bb4accdf9d05e01adb470654875e56`:
  `ghcr.io/nnigarp/campusmarket-api-rollback@sha256:f1114c208ed47d762fee76306cbd4d5b27134f2c18638475297f7fe8f677696b`
- Evidencia de compilación/prueba con MySQL sintético y publicación:
  https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41341824838
- **Alcance de la recuperación:** imagen de API reconstruida y probada, no copia exacta del contenedor reemplazado ni respaldo de MySQL/fotografías. No se ha ejecutado rollback real en Dokploy.

## Riesgos y recomendaciones posteriores

- No hay respaldo externo recuperable de MySQL ni de fotografías acreditado. Configurar y probar respaldo antes de futuras operaciones que afecten datos.
- Conservar Autodeploy desactivado hasta definir la política de publicación.
- Mientras el comando personalizado esté configurado, conservarlo documentado y **no volver a ejecutar Deploy innecesariamente**.
- Si se retira Run Command para volver al predeterminado, el predeterminado incluye `--build --remove-orphans` y no es equivalente al despliegue dirigido. No usarlo accidentalmente.
- Confirmar la continuidad de `/health`, `/app/`, los contenedores y las publicaciones después de cada cambio futuro.
- Este documento se basa en logs y capturas del operador; no pretende acreditar pruebas no ejecutadas (por ejemplo, restauración real desde backup o rollback efectivo en el servidor).
