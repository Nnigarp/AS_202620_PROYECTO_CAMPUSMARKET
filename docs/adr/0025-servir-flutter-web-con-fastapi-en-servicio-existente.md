# ADR-0025 — Servir Flutter Web con FastAPI desde el servicio Compose existente

- **Fecha:** 2026-11-01.
- **Estado:** Propuesto para aceptación por el equipo.
- **Ámbito:** Despliegue, operabilidad y entrega Web de CampusMarket.
- **Antecedentes:** [ADR-0001](0001-usar-monolito-modular.md), [ADR-0016](0016-ajustar-recursos-a-la-cuota-del-laboratorio.md), [ADR-0018](0018-ejecutar-el-monolito-en-dokploy-con-volumenes.md) y [ADR-0024](0024-publicar-imagen-verificada-y-condicionar-promocion.md).

## Contexto y problema

El MVP mantenía FastAPI y MySQL en `campusmarket → production → sistema` de Dokploy, mientras Flutter Web se mostraba históricamente desde GitHub Pages. Era necesario publicar la interfaz bajo `https://campusmarket.iscoutb.dev/app/`, sin crear un servicio nuevo, un tercer contenedor, una red adicional o intervenir el almacenamiento de producción. El intento aislado en `development/web-ensayo` falló por agotamiento del pool de subredes del Docker institucional (`all predefined address pools have been fully subnetted`). El ensayo local posterior funcionó, pero no probaba por sí solo la capacidad del host institucional.

El equipo disponía de una imagen inmutable GHCR con Flutter Web y FastAPI, validada localmente con MySQL. La promoción a producción requería separar el artefacto publicado del procedimiento que afecta el contenedor existente, conforme a ADR-0024.

## Alternativas consideradas

| Alternativa | Beneficio | Costo o restricción |
|---|---|---|
| Tercer contenedor/proxy Web en Dokploy | Separación de despliegue del frontend | Contenedor y redes adicionales; no cumple el objetivo y puede agotar cuotas |
| Servicio independiente `development` | Prueba institucional sin tocar `production` | La creación de redes falló en el servidor institucional; no demostró viabilidad |
| GitHub Pages como único frontend | Hosting externo disponible y precedente histórico | No satisface la publicación solicitada bajo `/app/` institucional |
| **Imagen única de aplicación: Flutter estático + FastAPI en `api`** | Un solo dominio y puerto de API; conserva Compose de dos servicios, MySQL y sus volúmenes | Acopla entrega de frontend a la imagen de API; requiere disciplina de promoción y rollback |

## Decisión propuesta

**Incorporar los archivos compilados de Flutter Web a la imagen de FastAPI y servirlos bajo `/app/` desde el contenedor `api` existente.** Mantener `db` como segundo contenedor de MySQL; reutilizar el mismo dominio, la red `campusmarket-sistema-2zvsxj` y los volúmenes persistentes `mysql_data` y `publication_images`.

Publicar la imagen candidata en GHCR y consumirla con digest inmutable en `deploy/compose.prod.yaml`, sin reconstrucción en el servidor. Conservar `deploy/compose.lab.yaml` como referencia histórica de compilación anterior. En Dokploy ejecutar únicamente:

```bash
docker compose -p campusmarket-sistema-2zvsxj --env-file deploy/.env -f ./deploy/compose.prod.yaml up -d --no-deps --no-build api
```

El comando **no es el comando predeterminado** de Dokploy. `--no-deps` evita iniciar/recrear la dependencia `db`, pero no equivale a respaldo de datos y no impide interrupción breve de `api`.

## Evidencia de la aplicación de esta decisión

- [PR #77](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/pull/77), merge `5ef0d6b139138d1260435b1b884240f093904749`; ocho checks exitosos en el push de `master` observados en GitHub.
- Imagen Web: `ghcr.io/nnigarp/campusmarket-web-candidate@sha256:65d34f2de8d035d5a9672be2e6a81bab759089da2fbe91bdca23a17f2f0463fd`.
- El log de Dokploy registró solo `api-1 Recreate/Recreated/Starting/Started` y `Docker Compose Deployed: ✅`.
- En el dominio institucional `/health` devolvió `{"status":"ok","service":"campusmarket-api"}`; `/app/` mostró Flutter y las fotografías. El operador verificó sesión, catálogo, edición y eliminación de publicaciones.
- Dokploy mostró `api-1` `899e114bcdeb` healthy y `db-1` `baedd6d65e17` healthy; este último coincide con el ID previo al despliegue.
- [Evidencia principal de promoción](../evidencias/cierre-web-institucional-2026-11-01.md).

## Consecuencias y riesgos

**Positivas:** despliegue institucional sin tercer contenedor, artefacto inmutable, dos servicios saludables, menor necesidad de crear redes y mayor trazabilidad entre CI/Compose/imagen.

**Costos y límites:** Flutter y FastAPI pasan a actualizarse juntos; el despliegue de la API puede generar una ventana breve de indisponibilidad; no se demostró recuperación de SQL/fotografías desde backup. La imagen de retorno fue probada con MySQL *sintético*, no ejecutada como rollback en Dokploy.

**Revisión:** reevaluar si se modifica la cuota, la gestión de redes, el comportamiento del proxy o los requisitos de continuidad. Este ADR nuevo no reescribe ni reemplaza retroactivamente ADR-0024: documenta una decisión complementaria y su aplicación posterior.
