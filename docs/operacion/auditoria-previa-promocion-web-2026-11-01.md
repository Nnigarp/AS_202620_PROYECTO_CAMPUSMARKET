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
