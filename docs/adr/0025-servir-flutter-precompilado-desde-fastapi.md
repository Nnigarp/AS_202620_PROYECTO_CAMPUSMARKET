# ADR-0025 — Servir Flutter precompilado desde FastAPI

- **Estado:** Propuesta implementada y verificada en CI; aceptación del equipo y promoción institucional pendientes.
- **Fecha:** 2026-10-30.
- **Ámbito:** Distribución del frontend. Conserva el monolito modular, MySQL, contratos y límites existentes.

## Contexto

El [feedback docente](https://github.com/ISCOUTB/AS_202620_feedback/blob/master/revisiones/2026-2/AS_202620_PROYECTO_CAMPUSMARKET/feedback.md)
mantiene cumplimiento parcial: API institucional, Flutter externo en Pages.
La [guía §1](https://github.com/ISCOUTB/iscoutb.dev/blob/main/README.md#1-qué-recibes-y-qué-necesitas)
asigna cuatro contenedores y 512 MB por equipo, con 0,5 CPU por contenedor;
API y MySQL ya declaran 256M cada uno. Compose interpreta esos límites como 256 MiB.
La [política, «Qué puedes desplegar»](https://github.com/ISCOUTB/iscoutb.dev/blob/main/docs/politicas-uso.md#qué-puedes-desplegar)
admite frontend web y Pages o equivalente; la compilación Flutter (~3 GB) debe permanecer fuera del servidor.
No se interpreta esta alternativa como autorización para cambiar producción.

## Alternativas

| Alternativa | Recursos y operación | Resultado |
|---|---|---|
| A. Flutter en Actions y Nginx separado | Tres contenedores; memoria declarada 512 MiB + cualquier límite positivo de Nginx; nueva imagen/ruta | Excede la suma permitida con los límites actuales. No reducir API/MySQL sin medición de su carga real. |
| B. Hosting externo con nombre/enrutamiento institucional | No añade contenedor al proyecto, pero exige destino DNS/proxy y autorización institucional comprobados; HTTPS y rutas dependen del proveedor | No confirmado. No se equipara redirección o iframe con aceptación docente. El wildcard actual no demuestra que Pages pueda recibir ese host. |
| C. Build en Actions y archivos en el contenedor FastAPI | Dos contenedores, 256 MiB + 256 MiB, 0,5 CPU por servicio; ningún proceso adicional; mismo dominio y volúmenes | Seleccionada para preparación: verificada en CI bajo esos límites. Promoción condicionada a los controles siguientes. |

## Decisión propuesta e implementación

Compilar Flutter release en Actions con `--base-href /app/ --pwa-strategy none --no-web-resources-cdn`,
sin `CAMPUSMARKET_API_BASE_URL`: Web obtiene el origen de la página; las llamadas siguen en `/catalogo`, etc.
Los builds Pages con URL explícita y Android conservan su selección anterior.
Copiar el resultado a `backend/web` antes de construir la imagen API en el runner.
El Dockerfile copia archivos compilados, sin SDK Flutter ni build frontend en Dokploy.

`web_frontend.py` monta exclusivamente `/app/` con StaticFiles; no captura la raíz ni rutas API,
no altera OpenAPI y responde 404 para recursos ausentes. `/app` redirige con Location relativa `/app/`,
conservando HTTPS sin confiar en headers de proxy. Se revalidan los estáticos con ETag y `no-cache`,
se añade `nosniff`, y no se siguen symlinks fuera del directorio. No hay volumen para el bundle.
Si no existe `index.html`, la API conserva su comportamiento anterior; un bundle parcial falla explícitamente.

Los primeros ensayos detectaron 503 al cargar iconos: Uvicorn cuenta conexiones keep-alive bajo el límite 6.
La respuesta de estáticos cierra su conexión HTTP/1.1 para liberar esos slots; las rutas API conservan keep-alive.
La corrección pasó dos ensayos sin errores de assets. No se aumentaron concurrencia, memoria ni CPU.
El proxy institucional y su comportamiento bajo carga siguen requiriendo verificación posterior autorizada.

## Evidencia y consecuencias

- [Run final 41094945507](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41094945507),
  commit `a9b6709a67f8036346acb64b9c2b9849ee355cf2`: 15 pruebas backend, 7 Flutter, Chrome real,
  catálogo/detalle/recarga, SQL e imagen sintéticos, identidad y cleanup; 10/10 criterios.
- Picos cgroup CI: API+Web **195796992 bytes (186,73 MiB)**; MySQL **185237504 bytes (176,66 MiB)**;
  límites efectivos **268435456 bytes** y **500000000 NanoCpus** por contenedor, sin OOM ni reinicios.
  Es una carga pequeña y sintética: no acredita holgura productiva ni el escenario EC-01 completo.
- La imagen exportada conserva API y frontend del mismo SHA. Se publicó sin reconstruir en el
  [run 41102641771](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41102641771):
  digest `sha256:65d34f2de8d035d5a9672be2e6a81bab759089da2fbe91bdca23a17f2f0463fd`.
  El [informe canónico](../evidencias/despliegue-publico-mvp-2026-10-04.md#fase-2--frontend-institucional-candidato-probado-en-ci--2026-10-30)
  conserva identidad, hashes, fallos corregidos, artefacto y procedimiento.
- Se acoplan los releases Web/API; rollback de imagen revierte ambos. No se cambian esquema SQL ni archivos persistentes.
- Se conserva Pages como publicación actual. ADR-0006 aceptado no se reescribe: la sustitución de hosting
  solo sería efectiva tras aprobación y comprobación pública. ADR-0016/0018/0024 conservan sus condiciones.

## Condiciones para promover y revisar

Antes de fusionar, resolver el autodeploy de `master` mediante un operador autorizado
([guía §3.6](https://github.com/ISCOUTB/iscoutb.dev/blob/main/README.md#36-desplegar-solo-lo-que-pasó-el-ci-opcional)).
Antes de publicar en Dokploy: respaldo recuperable de SQL/fotos, montajes efectivos, imagen anterior recuperable,
acceso al registro desde servidor, memoria de producción observada y actualización exclusiva de API dentro de cuota.
Publicar el artefacto probado sin reconstruir, fijar su nuevo digest y verificar HTTPS/navegación pública.
El ensayo GHCR anterior de fuente `2154e788...` no contiene esta capacidad ni acredita su despliegue.

El [plan operativo canónico](../operacion/despliegue-ghcr.md) incorpora ahora Compose por digest y un
preflight de solo lectura. El [run 41133683253](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41133683253)
probó los comandos de promoción/rollback exclusivos de API y restauración sintética. El control de rollback
usa el mismo Image ID: no demuestra compatibilidad con la imagen productiva desconocida.
La decisión sigue propuesta y la publicación bloqueada por sus precondiciones productivas.
