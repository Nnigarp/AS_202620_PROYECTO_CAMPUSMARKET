# CampusMarket — auditoría previa a promoción Flutter Web

Fecha de registro: 2026-11-01. Entorno: `campusmarket / production / sistema`.
Registro documental de observaciones; **no acredita despliegue de Flutter ni autoriza modificar producción**.

## Estado observado

- Dominio: `https://campusmarket.iscoutb.dev`.
- `GET /health` respondió `{"status":"ok","service":"campusmarket-api"}`.
- `GET /app/` respondió `{"detail":"Not Found"}`; Flutter Web aún no se publicó en la URL institucional.
- Dos contenedores en estado healthy: `campusmarket-sistema-2zvsxj-api-1` y `campusmarket-sistema-2zvsxj-db-1`.
- Dokploy General: fuente GitHub institucional, rama `master`, ruta `./deploy/compose.lab.yaml`; Autodeploy se observó desactivado en la última captura.
- El PR [#77](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/pull/77) continúa Draft sin merge; diez checks de GitHub se verificaron como exitosos, incluidos `test`, `compose`, `configuration`, frontend y flujos Web/Android.

## Identidad anterior y reconstrucción posible

- Dentro del contenedor `api`, el archivo `/app/REVISION` contiene `7856416795bb4accdf9d05e01adb470654875e56`.
- El log del último despliegue exitoso leído desde Dokploy registró `docker compose -p campusmarket-sistema-2zvsxj --env-file deploy/.env -f ./deploy/compose.lab.yaml up -d --build --remove-orphans`.
- Ese log registró construcción de la imagen local `campusmarket-sistema-2zvsxj-api:latest` y configuración `sha256:0e1542b2f9ef4cb711476ad2220234217f8738d9403a134893ae79ab5572c1e1` (config de esa construcción, **no** Image ID actual verificado mediante Docker inspect).
- En el repositorio institucional se pudo recuperar `backend/Dockerfile` y `deploy/compose.lab.yaml` a la revisión indicada: [Dockerfile](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/blob/7856416795bb4accdf9d05e01adb470654875e56/backend/Dockerfile), [Compose](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/blob/7856416795bb4accdf9d05e01adb470654875e56/deploy/compose.lab.yaml).
- Hay **ruta candidata de reconstrucción** de la API previa, pero no existe prueba de reconstrucción reproducida para esa revisión ni confirmación de disponibilidad de la imagen previa en el host. Restaurar la referencia `master` a un commit moderno no necesariamente reconstruye los mismos bytes.

## Persistencia realmente inspeccionada

- En `api`, `/proc/self/mountinfo` muestra el volumen `campusmarket-sistema-2zvsxj_publication_images` montado en `/app/backend/uploads`.
- En `db`, `/proc/self/mountinfo` muestra `campusmarket-sistema-2zvsxj_mysql_data` montado en `/var/lib/mysql`.
- `Backups`: el panel mostró `No backups configured`.
- `Volume Backups`: el panel mostró `No volume backups`; el selector de destino del formulario no presentó opciones.
- Montajes no equivalen a respaldos recuperables. No hay una restauración SQL ni de fotografías verificada.

## Restricciones y acciones prohibidas durante la preparación

- Mantener servicio Compose `sistema`, `api` y `db`, la red institucional existente y los nombres de volúmenes actuales.
- No ejecutar `Fresh Volumes`, `down -v`, `prune`, acciones de borrado o sustitución de base de datos.
- No modificar directamente `ISCOUTB/master`, fusionar PR ni hacer Deploy sin aprobación explícita.
- El servicio experimental `development/web-ensayo` falló por `all predefined address pools have been fully subnetted`; no reutilizar redes ajenas para sortearlo.
- La terminal de Dokploy se ejecuta **dentro** de los contenedores, no ofrece inspección autorizada de imágenes Docker del host.

## Gates pendientes antes de promoción

1. Identificar y conservar una opción de rollback de API verificable (imagen previa recuperable o reconstrucción comprobada a la revisión exacta), y documentar el tiempo de interrupción esperado.
2. Decidir explícitamente el nivel aceptado de riesgo de pérdida de datos: actualmente no hay copia SQL ni de fotografías recuperable. Aceptar pérdida de publicaciones **no** equivale a evidencia de recuperación.
3. Verificar que el candidato `deploy/compose.prod.yaml` no cambia nombres de volúmenes, base de datos, red ni servicios efectivos del sistema, incluidas las etiquetas añadidas por Dokploy.
4. Confirmar el procedimiento de promoción y rollback desde la UI disponible, sin asumir acceso SSH ni Docker del host.
5. Tras aprobación explícita, verificar dominio, `/health`, `/app/`, flujos de catálogo y estado de MySQL; registrar los hashes y resultados reales.

**Situación al cierre de este registro:** Flutter Web disponible solo en pruebas locales; publicación institucional pendiente.

## Actualización posterior: diagnóstico y recreación de API (2026-11-01)

1. Desde Dokploy **Advanced → Run Command** se ejecutó mediante Deploy la consulta `docker compose -p campusmarket-sistema-2zvsxj --env-file deploy/.env -f ./deploy/compose.lab.yaml images -q api`. Resultado: `b4db758f7769c12e5850e43605d4d9486725e6f0ef4dab0650cac9c480f5d9ff`. Esta referencia es **anterior** a la recreación que sigue.
2. Tras restaurar el comando predeterminado, se efectuó un Deploy adicional. El registro muestra `up -d --build --remove-orphans`, reconstrucción de `campusmarket-sistema-2zvsxj-api:latest`, `exporting config sha256:6b42c15f7f28aa634e529ed7fc1cd3f122658856f6928c1d48ce098a27ac702a`, recreación de `api-1`, `db-1 Running/Healthy`, y resultado final exitoso. **No equivale a la promoción Web**.
3. Capturas posteriores: `/health` devolvió `ok`; `api-1` healthy con un nuevo Container ID, `db-1` continuó healthy con su ID anterior `baedd6d65e17`; Autodeploy OFF y Run Command otra vez vacío.
4. El ID anterior `b4db…` **no debe utilizarse como si fuera el ID actual**; la config `6b42…` es evidencia del build, no prueba de rollback utilizable. Sigue faltando conservar una referencia de retorno y comprobar su ejecución.
5. En el PR #77, el último commit documental registrado antes de esta actualización era `1cd648d` y GitHub mostró los checks completados con éxito; el PR seguía Draft. Cualquier commit posterior exige comprobar de nuevo los checks pertinentes.

**Control de cambios:** no volver a pulsar Deploy con el Run Command predeterminado para inspecciones. No ejecutar ningún comando de borrado de volúmenes, ni un despliegue de Flutter, hasta acordar la promoción y la recuperación.

## Imagen de rollback verificada por GitHub Actions (2026-11-01)

- Rama de implementación y prueba: `ops/rollback-api-78564167-20261101` en el fork `Nnigarp`.
- Commit del workflow corregido: `2af811617997bccc356373e09d33bfdfe44dee85`.
- Run exitoso: https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41341824838
- Revisión de código comprobada: `7856416795bb4accdf9d05e01adb470654875e56`.
- Imagen publicada **por digest**, extraído del log del paso `Publicar imagen validada por digest`:
  `ghcr.io/nnigarp/campusmarket-api-rollback@sha256:f1114c208ed47d762fee76306cbd4d5b27134f2c18638475297f7fe8f677696b`.
- La compilación `linux/amd64` y el test integrado de `/health` con MySQL sintético finalizaron exitosos. El run previo `41341503369` falló por verificar `/health` sin MySQL; se corrigió y se ejecutó de nuevo.
- **Límite de esta evidencia:** es reconstrucción verificada del código anterior, no copia exacta del contenedor actual ni copia de SQL/fotos. Para usarla en rollback hay que comprobar permisos de lectura GHCR en Dokploy y sustituir solo `api.image`; no hacerlo en producción sin el plan aprobado y comprobación del Compose efectivo.
