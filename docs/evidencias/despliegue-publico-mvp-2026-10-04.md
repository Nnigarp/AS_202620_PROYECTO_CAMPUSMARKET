# CampusMarket — prueba funcional de producción S9

Ejecución UTC: 20261004T021640Z
Destino: https://campusmarket.iscoutb.dev

## Alcance y criterios
Pruebas HTTP reales contra producción. Se verifican códigos HTTP, identidad, propiedad, valores editados, imagen pública y revocación de sesión. Esto valida el flujo probado; no constituye una auditoría completa de seguridad ni el cierre de toda S9.
Fuentes consultadas: bienvenida del curso, CONTRATO (1)(1).md, S08-despliegue-y-operacion.pdf, guía oficial https://github.com/ISCOUTB/iscoutb.dev/blob/main/README.md y políticas https://github.com/ISCOUTB/iscoutb.dev/blob/main/docs/politicas-uso.md. Las normas oficiales del laboratorio se contrastaron con el Compose del repositorio, no solo con la vista que Dokploy genera.

## Resultados
| Prueba | HTTP esperado | HTTP real | Resultado |
|---|---:|---:|---|
| Salud | 200 | 200 | PASS |
| Contrato OpenAPI | 200 | 200 | PASS |
| Registro a | 201 | 201 | PASS |
| Login a | 200 | 200 | PASS |
| Identidad a | 200 | 200 | PASS |
| Registro b | 201 | 201 | PASS |
| Login b | 200 | 200 | PASS |
| Identidad b | 200 | 200 | PASS |
| Autenticacion requerida | 401 | 401 | PASS |
| Catalogo publico | 200 | 200 | PASS |
| Crear publicacion A | 201 | 201 | PASS |
| Publicaciones propias A | 200 | 200 | PASS |
| Aislamiento listado B | 200 | 200 | PASS |
| Detalle publico | 200 | 200 | PASS |
| Subir imagen A | 201 | 201 | PASS |
| Imagen accesible | 200 | 200 | PASS |
| Editar publicacion A | 200 | 200 | PASS |
| Aislamiento editar B | 404 | 404 | PASS |
| Aislamiento eliminar B | 404 | 404 | PASS |
| Verificar integridad tras B | 200 | 200 | PASS |
| Reservar publicacion prueba | 200 | 200 | PASS |
| Cerrar sesion B | 204 | 204 | PASS |
| Sesion B revocada | 401 | 401 | PASS |

## Datos para persistencia
Publicación de prueba: **1**.
Detalle: https://campusmarket.iscoutb.dev/catalogo/1
Título esperado: PRUEBA S9 EDITADA 20261004T021640Z
Precio esperado: 16000. Estado: reservado. Una imagen asociada.
Imagen: /uploads/publicaciones/1/9dc8079ae3aa4b14aa2df5c9c3062792.png
Se conservaron dos cuentas de prueba con correo example.com y esta publicación para comprobar persistencia. La publicación está marcada como prueba y reservada. No se alteraron publicaciones ajenas. No se hizo reinicio ni redeploy.

## Pendientes y hallazgos
1. Persistencia después de restart/redeploy: BLOQUEADA/PENDIENTE. Intento de Restart de API rechazado por Dokploy: unauthorized to access resource docker (captura image(20261004-022754).png). No hubo reinicio. Después del intento fallido /health y /catalogo/1 devolvieron 200; eso no demuestra persistencia tras reiniciar.
2. Evidencia de commit del despliegue: captura image(20261004-022958).png muestra Done y commit c38e0cf36a30dddec39f169b7618b7c6127e0a71. Log adjunto Markdown pegado(2).md incluye escritura de ese hash a REVISION, construcción de la imagen y Docker Compose Deployed. Esto vincula el registro del despliegue al commit; no sustituye una lectura de REVISION en runtime.
3. OpenAPI anuncia http://localhost:8000 como servidor. Las pruebas usaron el dominio real explícitamente. Falta verificar Try it out en producción antes de concluir su impacto.
4. Prueba de frontend/UI: PENDIENTE. Este reporte cubre API.
5. Normas oficiales de laboratorio revisadas; ver comprobaciones siguientes. Rúbrica actual completa de la actividad Moodle no disponible.

## Procedimiento pendiente
En Dokploy identificar los contenedores de sistema y revisar volumen de base de datos e imágenes y commit desplegado. Registrar estado previo; realizar restart del servicio correcto sin eliminar volúmenes; esperar salud OK; volver a consultar la publicación y descargar imagen; comparar identificador, título, precio, estado e imagen. Reinicio y redeploy no son pruebas equivalentes: documentar cuál se ejecutó.

## Respuestas verificables (sin contraseñas ni tokens)

### Salud
GET /health — HTTP 200
```json
{
  "status": "ok",
  "service": "campusmarket-api"
}
```

### Contrato OpenAPI
GET /openapi.json — HTTP 200
```json
{
  "title": "CampusMarket API",
  "version": "2.0.0",
  "servers": [
    {
      "url": "http://localhost:8000",
      "description": "Entorno local"
    }
  ]
}
```

### Registro a
POST /usuarios/registro — HTTP 201
```json
{
  "id": 1,
  "nombre": "Prueba S9 A",
  "correo": "smoke.s9.20261004t021640z.a@example.com",
  "es_admin": false
}
```

### Login a
POST /usuarios/login — HTTP 200
```json
{
  "access_token": "[REDACTADO]",
  "token_type": "bearer",
  "expira_en": "2026-10-04T14:17:00.365972Z",
  "usuario": {
    "id": 1,
    "nombre": "Prueba S9 A",
    "correo": "smoke.s9.20261004t021640z.a@example.com",
    "es_admin": false
  }
}
```

### Identidad a
GET /usuarios/me — HTTP 200
```json
{
  "id": 1,
  "nombre": "Prueba S9 A",
  "correo": "smoke.s9.20261004t021640z.a@example.com",
  "es_admin": false
}
```

### Registro b
POST /usuarios/registro — HTTP 201
```json
{
  "id": 2,
  "nombre": "Prueba S9 B",
  "correo": "smoke.s9.20261004t021640z.b@example.com",
  "es_admin": false
}
```

### Login b
POST /usuarios/login — HTTP 200
```json
{
  "access_token": "[REDACTADO]",
  "token_type": "bearer",
  "expira_en": "2026-10-04T14:17:17.550194Z",
  "usuario": {
    "id": 2,
    "nombre": "Prueba S9 B",
    "correo": "smoke.s9.20261004t021640z.b@example.com",
    "es_admin": false
  }
}
```

### Identidad b
GET /usuarios/me — HTTP 200
```json
{
  "id": 2,
  "nombre": "Prueba S9 B",
  "correo": "smoke.s9.20261004t021640z.b@example.com",
  "es_admin": false
}
```

### Autenticacion requerida
GET /usuarios/me — HTTP 401
```json
{
  "detail": "Inicia sesión para continuar."
}
```

### Catalogo publico
GET /catalogo — HTTP 200
```json
[]
```

### Crear publicacion A
POST /publicaciones — HTTP 201
```json
{
  "titulo": "PRUEBA S9 20261004T021640Z",
  "descripcion": "Publicacion de prueba automatica S9. No corresponde a una oferta real. Reservada para verificar persistencia.",
  "precio": 15000.0,
  "modalidad": "venta",
  "estado": "usado",
  "estado_publicacion": "disponible",
  "id": 1,
  "propietario_id": 1,
  "visible": true
}
```

### Publicaciones propias A
GET /publicaciones/mias — HTTP 200
```json
[
  {
    "titulo": "PRUEBA S9 20261004T021640Z",
    "descripcion": "Publicacion de prueba automatica S9. No corresponde a una oferta real. Reservada para verificar persistencia.",
    "precio": 15000.0,
    "modalidad": "venta",
    "estado": "usado",
    "estado_publicacion": "disponible",
    "id": 1,
    "propietario_id": 1,
    "visible": true,
    "imagenes": []
  }
]
```

### Aislamiento listado B
GET /publicaciones/mias — HTTP 200
```json
[]
```

### Detalle publico
GET /catalogo/1 — HTTP 200
```json
{
  "id": 1,
  "titulo": "PRUEBA S9 20261004T021640Z",
  "descripcion": "Publicacion de prueba automatica S9. No corresponde a una oferta real. Reservada para verificar persistencia.",
  "precio": 15000.0,
  "modalidad": "venta",
  "estado": "usado",
  "propietario_id": 1,
  "estado_publicacion": "disponible",
  "imagenes": []
}
```

### Subir imagen A
POST /publicaciones/1/imagenes — HTTP 201
```json
{
  "id": 1,
  "publicacion_id": 1,
  "imagen_url": "/uploads/publicaciones/1/9dc8079ae3aa4b14aa2df5c9c3062792.png",
  "orden": 1,
  "es_principal": true
}
```

### Imagen accesible
GET https://campusmarket.iscoutb.dev/uploads/publicaciones/1/9dc8079ae3aa4b14aa2df5c9c3062792.png — HTTP 200
```json
{
  "content_type": "image/png",
  "bytes": 70
}
```

### Editar publicacion A
PUT /publicaciones/1 — HTTP 200
```json
{
  "titulo": "PRUEBA S9 EDITADA 20261004T021640Z",
  "descripcion": "Publicacion de prueba automatica S9. No corresponde a una oferta real. Reservada para verificar persistencia.",
  "precio": 16000.0,
  "modalidad": "venta",
  "estado": "usado",
  "estado_publicacion": "disponible",
  "id": 1,
  "propietario_id": 1,
  "visible": true
}
```

### Aislamiento editar B
PUT /publicaciones/1 — HTTP 404
```json
{
  "detail": "La publicación no existe o no pertenece al propietario."
}
```

### Aislamiento eliminar B
DELETE /publicaciones/1 — HTTP 404
```json
{
  "detail": "La publicación no existe o no pertenece al propietario."
}
```

### Verificar integridad tras B
GET /catalogo/1 — HTTP 200
```json
{
  "id": 1,
  "titulo": "PRUEBA S9 EDITADA 20261004T021640Z",
  "descripcion": "Publicacion de prueba automatica S9. No corresponde a una oferta real. Reservada para verificar persistencia.",
  "precio": 16000.0,
  "modalidad": "venta",
  "estado": "usado",
  "propietario_id": 1,
  "estado_publicacion": "disponible",
  "imagenes": [
    {
      "id": 1,
      "publicacion_id": 1,
      "imagen_url": "/uploads/publicaciones/1/9dc8079ae3aa4b14aa2df5c9c3062792.png",
      "orden": 1,
      "es_principal": true
    }
  ]
}
```

### Reservar publicacion prueba
PATCH /publicaciones/1/estado — HTTP 200
```json
{
  "titulo": "PRUEBA S9 EDITADA 20261004T021640Z",
  "descripcion": "Publicacion de prueba automatica S9. No corresponde a una oferta real. Reservada para verificar persistencia.",
  "precio": 16000.0,
  "modalidad": "venta",
  "estado": "usado",
  "estado_publicacion": "reservado",
  "id": 1,
  "propietario_id": 1,
  "visible": true
}
```

### Cerrar sesion B
POST /usuarios/logout — HTTP 204
```json
""
```

### Sesion B revocada
GET /usuarios/me — HTTP 401
```json
{
  "detail": "Sesión inválida o expirada."
}
```

## Evidencia de volúmenes del despliegue inicial
El log adjunto registra creación de los volúmenes campusmarket-sistema-2zvsxj_mysql_data y campusmarket-sistema-2zvsxj_publication_images, DB Healthy y API Started. La existencia de volúmenes no prueba por sí sola persistencia después de recreación. No se verificaron aún sus puntos de montaje.


## Redeploy del mismo commit — resultado y límite
Fuentes: capturas image(20261004-023458).png e image(20261004-023526).png y log Markdown pegado(3).md.
El registro más reciente terminó Done con c38e0cf36a30dddec39f169b7618b7c6127e0a71. El log muestra construcción usando caché, API Running, DB Running, DB Healthy y Docker Compose Deployed. No muestra recreación ni reinicio de los contenedores.
Después de ese redeploy se ejecutaron consultas reales: /health 200 con status ok; /catalogo/1 200 conserva título PRUEBA S9 EDITADA 20261004T021640Z, precio 16000, estado reservado, propietario 1 e imagen 1. La imagen devolvió 200, 70 bytes y SHA-256 d5a51b6aed15684ec8c123e30fe5703155359d6543b6d7b47cb5766ef44939de, idéntico al contenido previo.
Conclusión: redeploy sin pérdida observado, pero persistencia tras reinicio o recreación sigue SIN DEMOSTRAR. No se considera cerrado ese criterio. El restart directo fue rechazado por permisos y requiere intervención autorizada del administrador.
Compose suministrado por el usuario declara mysql_data:/var/lib/mysql y publication_images:/app/backend/uploads. Son montajes configurados; no sustituyen la prueba de ciclo de vida.


## Contraste con guía oficial del laboratorio — 2026-10-04

Fuente versionada: guía README blob b1b220cc58d5a51118700864b8e06b59b6513350 y políticas blob 9d671f7ef1e6b64b4c9d99a8b025099605b83239.

| Regla | Evidencia observada | Estado |
|---|---|---|
| Máximo 4 contenedores, 512 MB total, 0,5 CPU cada uno | Compose versionado: API y DB, 256M y 0.50 CPU cada uno | Configuración cumple; consumo runtime no medido |
| Sin puertos publicados, bind mounts, privilegios o Docker socket | deploy/compose.lab.yaml blob 14903e37655005335a35ba4bda65b64a6ac53124 | Cumple en archivo versionado |
| Sin redes externas añadidas por el equipo | El Compose versionado no declara networks ni labels; Dokploy añade red del servicio y labels al renderizar | Cumple en archivo; verificar Isolated Deployment en panel |
| Volúmenes nombrados para DB y archivos | mysql_data y publication_images configurados; log registra creación | Cumple configuración; ciclo de vida público pendiente |
| Secretos fuera del repo | Compose usa sustitución obligatoria MYSQL_PASSWORD y MYSQL_ROOT_PASSWORD; Environment mantiene valores | Cumple Compose; auditoría histórica basada en CI, no nueva inspección completa local |
| Flutter fuera del laboratorio | API + MySQL únicamente en Compose; frontend GitHub Pages | Cumple ubicación |
| Dominio del equipo y HTTPS | campusmarket.iscoutb.dev, pruebas urllib con validación TLS | Cumple prueba HTTP externa |
| CI del hash publicado | Cuatro runs terminados success para c38e0cf36a30dddec39f169b7618b7c6127e0a71 | Cumple los runs citados |
| CORS para frontend Pages | GET /publicaciones con Origin https://nnigarp.github.io devuelve 200 y Access-Control-Allow-Origin igual | Cumple prueba de respuesta |
| Health con DB no disponible | /health 200 con DB activa; no se detuvo DB en producción | Pendiente de ejecución pública; existe prueba previa/CI |
| Logs JSON | Implementación y evidencia CI disponibles; captura de Logs de producción aún no recogida | Pendiente evidencia runtime |
| Métrica consultable | /ops/metrics/ec01 devuelve 200; muestra inicial vacía (evaluation_available false) | URL cumple; no prueba rendimiento por sí sola |
| Publicar 24h antes del cierre | Deploy inicial 2026-10-04 UTC; fecha/hora oficial de Moodle por confirmar | No verificado contra actividad actual |

Runs actuales:
- Compose y persistencia: https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/37156541579
- Backend: https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/37156541480
- Flutter: https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/37156541605
- Web y Android: https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/37156541600

### Frontend publicado
La URL histórica https://nnigarp.github.io/AS_202620_PROYECTO_CAMPUSMARKET/ y main.dart.js responden 200. El bundle consultado todavía incluye campusmarket-s8-api-nilver.azurewebsites.net y no campusmarket.iscoutb.dev. Se inició publicación reproducible del mismo hash aprobado con API Dokploy:
https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/37172016525
Estado al redactar este apartado: en curso. No se considera frontend MVP verificado hasta terminar publicación y comprobar flujo en navegador.

### Contrato transversal y Sonar
El contrato del curso exige configuración, invocación del scanner en workflow, run exitoso y Quality Gate público. El árbol actual tiene cuatro workflows y backend-tests.yml no invoca scanner. Los cuatro pipelines en verde no demuestran esa exigencia; un análisis automático de Sonar no sustituye la invocación pedida. Falta corregir/verificar esta evidencia antes de afirmar cumplimiento integral. No se editó ningún ADR aceptado durante este trabajo.


## Resultado posterior de frontend y medición pública

Publicación del frontend: run 37172016525 terminado success. Ejecutó flutter analyze, flutter test y build web release con Flutter 3.47.3, base href /AS_202620_PROYECTO_CAMPUSMARKET/ y CAMPUSMARKET_API_BASE_URL=https://campusmarket.iscoutb.dev. Fuente exacta c38e0cf36a30dddec39f169b7618b7c6127e0a71. Commit de artefactos gh-pages 4626e11 (no es el hash del código fuente).

Comprobación HTTP posterior: source-revision.txt 200 contiene el SHA fuente; main.dart.js 200 contiene campusmarket.iscoutb.dev y no contiene la URL antigua de Azure. Navegador real: Inicio muestra la publicación 1; Ver detalles abre título esperado, COP $16.000, Reservado, Usado, Venta y Fotografías 1. La imagen de prueba es un PNG de un píxel, por lo que la superficie visual resulta blanca; no se usó como prueba de calidad fotográfica. Captura local campusmarket-detalle-1791082096671.jpg. La sesión y formularios autenticados del navegador público permanecen pendientes; no se confunden con los tests HTTP ni con los tests de Web/Android en CI.

Se enviaron diez GET /publicaciones secuenciales, todos 200. Métrica del servidor: diez muestras, diez dentro de 2000 ms, duración interna entre 57.15 y 97.58 ms, meets_backend_target true, ec01_fully_verified false. Los tiempos observados desde este cliente remoto fueron 3273.10–4709.98 ms, incluyendo red/TLS: esta muestra externa supera 2 s y no demuestra cumplimiento extremo a extremo. No se sembraron 1000 publicaciones en producción; la prueba con ese volumen pertenece a CI.

Respuesta de la métrica:
```json
{
  "scenario_id": "EC-01",
  "quality_attribute": "rendimiento",
  "measurement_scope": "backend GET /publicaciones",
  "window_size": 10,
  "threshold_ms": 2000.0,
  "required_within_threshold": 9,
  "observed_requests": 10,
  "within_threshold": 10,
  "evaluation_available": true,
  "meets_backend_target": true,
  "ec01_fully_verified": false,
  "samples": [
    {
      "status_code": 200,
      "duration_ms": 59.71
    },
    {
      "status_code": 200,
      "duration_ms": 58.09
    },
    {
      "status_code": 200,
      "duration_ms": 57.98
    },
    {
      "status_code": 200,
      "duration_ms": 84.41
    },
    {
      "status_code": 200,
      "duration_ms": 92.74
    },
    {
      "status_code": 200,
      "duration_ms": 58.38
    },
    {
      "status_code": 200,
      "duration_ms": 57.52
    },
    {
      "status_code": 200,
      "duration_ms": 57.15
    },
    {
      "status_code": 200,
      "duration_ms": 57.85
    },
    {
      "status_code": 200,
      "duration_ms": 97.58
    }
  ]
}
```


## Integración documental preparada

Rama del fork Nnigarp: deploy-pages-mvp-2026-10-04. Incluye evidencia, README con URLs vigentes, fila ASP-10 de ocho columnas, vista de despliegue vigente y registro IA, además del workflow de publicación Pages. Comparación con c38e0cf confirma cero archivos docs/adr/ modificados. Las decisiones aceptadas se conservan íntegramente.

El intento de crear PR hacia ISCOUTB/master fue rechazado por GitHub: HTTP 403 Resource not accessible by integration. No se hizo merge y estas actualizaciones todavía no están en la rama oficial evaluada. Hace falta abrir/integrar el PR desde una cuenta autorizada. No se considera la documentación integrada por existir en el fork.

Comparación: https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/compare/c38e0cf36a30dddec39f169b7618b7c6127e0a71...deploy-pages-mvp-2026-10-04

## Fase 2 — frontend institucional candidato probado en CI — 2026-10-30

Esta ampliación conserva íntegro el registro anterior de S9. **No es un nuevo despliegue productivo.**
Objetivo: ejecutar la interfaz Flutter real con FastAPI/MySQL en una imagen que pueda servir `/app/`
bajo el dominio institucional, sin añadir contenedores ni compilar Flutter en el laboratorio.

### Referencias, base y diagnóstico de solo lectura

- [Guía oficial](https://github.com/ISCOUTB/iscoutb.dev/blob/main/README.md): §1 (cuota y compilación Flutter),
  §2 (dominio del equipo), §3.2 (límites/volúmenes), §3.3 (salud), §3.5 (routing HTTPS/autodeploy),
  §3.6 (rama de publicación) y §5 (evidencia).
- [Políticas](https://github.com/ISCOUTB/iscoutb.dev/blob/main/docs/politicas-uso.md): «Qué puedes desplegar»,
  «Qué está prohibido» y «Datos y disponibilidad». No garantizan respaldos.
- [Feedback docente](https://github.com/ISCOUTB/AS_202620_feedback/blob/master/revisiones/2026-2/AS_202620_PROYECTO_CAMPUSMARKET/feedback.md)
  y [seguimiento 29/10](https://github.com/ISCOUTB/AS_202620_feedback/blob/master/revisiones/2026-2/seguimiento-despliegues-2026-10-29.md):
  API institucional, frontend Pages, cumplimiento parcial. Un CI verde no es aceptación pública.
- Base upstream: `40be256f52d74ad8c9148886f040845658a38855`, PR #75 fusionado.
  Se creó en el fork `feat/web-institucional-20261030-40be256` desde esa revisión, sin usar su master antiguo.
- Fuente final probada: **`a9b6709a67f8036346acb64b9c2b9849ee355cf2`**.
  Los documentos añadidos después no se presentan como código ejecutado por ese run.

Dokploy v0.30.10 mostró `campusmarket → production → sistema`, proyecto Compose `campusmarket-sistema-2zvsxj`,
Provider GitHub oficial, ruta `./deploy/compose.lab.yaml`, autodeploy por push activo y dos contenedores healthy:
API `bd294e94091a`, MySQL `baedd6d65e17`. Dominio `campusmarket.iscoutb.dev`, Path `/`, servicio `api`,
puerto 8000, HTTPS y Let's Encrypt. No se abrió Environment ni se ejecutó terminal/inspect del servidor.
Los indicadores Monitoring `Used 0 / Limit 0` y CPU 0 no constituyen una medición de capacidad.

El navegador de la sesión mostró `{"status":"ok","service":"campusmarket-api"}` en
`https://campusmarket.iscoutb.dev/health`, y `{"detail":"Not Found"}` tanto en `/` como en `/app/`.
Se registró el contenido observado, no un código HTTP que esa vista no mostraba.
Las consultas HTTP desde el ejecutor local recibieron 403; no se atribuye ese resultado a un fallo de la API.
No se consultaron cuentas, publicaciones ni otros datos productivos.

### Propuesta e implementación

[ADR-0025](../adr/0025-servir-flutter-precompilado-desde-fastapi.md) compara las tres alternativas:
Nginx separado excedería `512 MiB + límite Nginx`; hosting/routing externo no tiene autorización/destino comprobados;
servir archivos en FastAPI mantiene **dos contenedores y 256M + 256M**, sin bajar límites.
La política admite frontend web y hosting equivalente; la compilación se mantiene fuera del servidor.
Esta justificación técnica no sustituye la autorización para intervenir producción.

Se implementaron el [montaje opcional](../../backend/app/web_frontend.py), su registro en
[main.py](../../backend/app/main.py), la copia de `backend/web` en el [Dockerfile](../../backend/Dockerfile)
y la selección de mismo origen en [Flutter](../../frontend/campusmarket/lib/shared/api_configuration.dart).
`/health`, `/docs`, OpenAPI, catálogo, autenticación y uploads conservan sus rutas; no se captura la raíz API.
No se modificaron Compose, workflows existentes, dependencias backend, esquema SQL ni volúmenes.
El bundle está ignorado por Git; `.gitkeep` permite construir una API sin frontend desde el checkout ordinario.
**Ni fusionar la rama ni seleccionar el compose.prod actual publican este bundle.**

El [workflow nuevo](../../.github/workflows/web-institucional.yml) usa `contents: read`, runner GitHub efímero,
Python 3.12, Flutter 3.47.3 y acciones fijadas por SHA. Puede ejecutarse manualmente; el push de esta rama
y los PR de código lo prueban automáticamente. No tiene credenciales ni operaciones de Dokploy/GHCR.
Compila con `--release --base-href /app/ --pwa-strategy none --no-web-resources-cdn`, copia el resultado,
escribe el SHA real y construye/prueba la imagen en el runner. No usa una imagen vieja como si contuviera esta Web.

Reutiliza `compose.lab.yaml` y el override **local** para API en `127.0.0.1:8000`; MySQL no publica puerto.
El verificador rechaza Docker remoto, otros repositorios/checkout y proyectos reutilizados.
Proyecto `campusmarket-web-41094945507-1`; base `campusmarket_web_41094945507_1_test`, credenciales aleatorias
en archivo 0600 fuera de Git, enmascaradas y retiradas al finalizar. Volúmenes nuevos del proyecto efímero,
sin bind mounts ni montajes productivos. La semilla registra una cuenta `example.com`, publicación e imagen sintéticas.
Se reutiliza el PROBE del ensayo GHCR para SQL/semilla, no su clase ni su referencia fija de imagen.

### Ejecución real y fallos corregidos

[Run final 41094945507](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41094945507),
intento 1, job [124198168754](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41094945507/job/124198168754),
terminó **success** el 30/10/2026; logs de PASS entre 17:02:00 y 17:03:07 UTC.
15 pruebas backend (montaje, contrato y modularidad), `flutter analyze` sin incidencias y 7 pruebas Flutter aprobadas.
Los diez criterios del verificador resultaron CUMPLE: config, identity, sql, routes, cors, browser, navigation,
resources, export y cleanup.

Chrome real renderizó Inicio → Catálogo → detalle → atrás → recarga. La captura de detalle muestra título,
precio e imagen sintéticos de MySQL; los eventos de red registraron `/catalogo` y `/catalogo/1` con 200.
Los 24 eventos de recursos `/app/` registrados fueron 200, incluidos JS, CanvasKit, fuentes, manifiesto e iconos.
No se sustituyó la interfaz por HTML de prueba. Capturas `01-inicio.png`, `02-catalogo.png`, `03-detalle.png`
y `04-ultimo-estado.png` están en el artefacto. Se revisaron visualmente catálogo y detalle.

Se preserva la historia de implementación:

- [41092034860](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41092034860),
  fuente `5c0e384...`: falló el verificador al comparar una cabecera con capitalización distinta; se normalizó.
- [41092575249](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41092575249),
  fuente `665672d...`: Flutter navegó, pero falló la comprobación de recursos. Se amplió el diagnóstico seguro.
- [41093459043](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41093459043),
  fuente `b941c1c...`: identificó 503 en favicon/icono bajo el límite de seis conexiones Uvicorn.
  Se añadió `Connection: close` exclusivamente a estáticos para no retener slots; no se cambió concurrencia ni cuota.
- [41094232876](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41094232876),
  fuente `a95103b...`: 10/10 y exportación aprobadas. El run final reforzó además el test que recalcula OpenAPI
  después del montaje. Todos los intentos retiraron los recursos de sus propios proyectos.

### Identidad del artefacto y recursos medidos

El SHA de checkout, etiqueta OCI, `/app/REVISION`, cabecera HTTP y `source-revision.txt` del frontend
coincidieron con `a9b6709a67f8036346acb64b9c2b9849ee355cf2`.

- **Image ID/config:** `sha256:15a6fee324bc315d27ab85674781dfd1bded727243cb6ff752370e70b5d6fd19`.
- **SHA-256 de api-web.tar:** `8edab5dca0c28063970c0183e8b8df458df302d7721c07a972203648cb3dc940`.
- [Artefacto 12996575905](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41094945507/artifacts/12996575905):
  `web-institucional-a9b6709a67f8036346acb64b9c2b9849ee355cf2-1`, ZIP de 73797651 bytes.
- **SHA-256 ZIP:** `e51664f3e6a6833b541f9143e5ea18d607f6f8b93f258fd409e7be3f99796113`.
  Metadatos GitHub: expiración **2026-11-06 17:03:07 UTC**, retención de siete días.

Se descargó el ZIP para contrastar su hash, `resultado.json`, checksum del tar, manifest/config de la imagen
y etiqueta OCI. Los hashes anteriores identifican objetos diferentes; **ninguno es un digest de manifiesto GHCR**.
La imagen se exportó, no se publicó. La imagen GHCR previamente ensayada de fuente `2154e788...`
es otro artefacto y no contiene esta implementación.

| Contenedor CI | Límite efectivo | Pico cgroup memory.peak | CPU efectiva | Salud / OOM / reinicios |
|---|---:|---:|---:|---|
| api (FastAPI + Flutter estático) | 268435456 bytes (256 MiB) | 195796992 bytes (186,73 MiB) | 500000000 NanoCpus (0,5) | healthy / false / 0 |
| db (MySQL 8.4.13) | 268435456 bytes (256 MiB) | 185237504 bytes (176,66 MiB) | 500000000 NanoCpus (0,5) | healthy / false / 0 |

La suma de límites es 512 MiB; la suma de picos individuales es 363,38 MiB y no se presenta como una muestra simultánea.
No se midió utilización de CPU ni se ensayó una carga equivalente a producción. Los límites y la carga sintética
sí se verificaron; la memoria de producción permanece sin medición válida.
El cleanup `always()` dejó inventarios vacíos de contenedores, volúmenes y redes del proyecto y eliminó el envfile.

### Matriz de aceptación de esta fase

En esta tabla `a9b6709...` identifica únicamente la fuente probada; [run Web] es el run final anterior.
Los CUMPLE de CI no se trasladan a producción.

| Criterio | Estado | Código/archivo | Commit | Run | URL pública | Evidencia real |
|---|---|---|---|---|---|---|
| Build Flutter fuera del laboratorio | CUMPLE | [workflow](../../.github/workflows/web-institucional.yml) | `a9b6709...` | [run Web] | — (runner) | Compilación release y 7 pruebas Flutter; no SDK en imagen runtime |
| Interfaz real, catálogo, detalle y recarga | CUMPLE | [verificador](../../scripts/verificar_web_institucional.py) | `a9b6709...` | [run Web] | — (loopback CI) | Chrome, cuatro capturas, API 200, 24 eventos assets 200 |
| FastAPI conectado a MySQL | CUMPLE | Verificador y PROBE existente | `a9b6709...` | [run Web] | — (runner) | /health 200 y SELECT en base exclusiva, MySQL 8.4.13, semilla sintética |
| Contratos y aislamiento de rutas | CUMPLE | [tests](../../backend/tests/test_web_frontend.py) y contrato existente | `a9b6709...` | [run Web] | — (runner) | 15 pruebas; /health, /docs, OpenAPI y catálogo preservados, raíz/asset ausente 404 |
| Mismo origen y CORS | CUMPLE | [config Flutter](../../frontend/campusmarket/lib/shared/api_configuration.dart) | `a9b6709...` | [run Web] | — (runner) | Llamadas al mismo servidor; preflight origen institucional aprobado |
| Identidad API/Web/imagen exportada | CUMPLE | Dockerfile y verificador | `a9b6709...` | [run Web] | — | OCI, REVISION, cabeceras y SHA Web coinciden; tar/config contrastados |
| Cuota y limpieza del ensayo | CUMPLE | Compose existente y verificador | `a9b6709...` | [run Web] | — | Dos contenedores, límites 512 MiB, sin OOM, inventarios finales vacíos |
| HTTPS del nuevo frontend detrás de Traefik | PARCIAL | Redirección relativa y routing observado | `a9b6709...` | [run Web] | https://campusmarket.iscoutb.dev/app/ | HTTPS actual y redirect unitario observados; bundle solo probado con HTTP loopback |
| Capacidad con carga productiva | BLOQUEADO | Monitoring / medición administrativa pendiente | — | — | — | Ceros de UI no son medición; CI pequeño no extrapolable |
| Imagen nueva publicada y descargable desde Dokploy | BLOQUEADO | Publisher GHCR a adaptar/revisar antes de promover | — | — | — | Solo tar exportado; permiso de pull del servidor no confirmado |
| Recuperabilidad productiva y actualización exclusiva API | BLOQUEADO | Procedimiento siguiente | — | — | — | Faltan backup/restore acreditados, montajes efectivos y anterior imagen recuperable |
| Frontend institucional públicamente aceptado | NO CUMPLE | Publicación pendiente | — | — | https://campusmarket.iscoutb.dev/app/ | Navegador muestra Not Found; no se desplegó ni se hizo aceptación pública |

[run Web]: https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41094945507

### Reproducción y publicación segura pendiente

La reproducción aislada se realiza con el workflow de esta rama, en runner GitHub alojado, revisando
que el SHA del run sea el checkout esperado. Sus pasos compilan, prueban, exportan y limpian;
no necesitan PAT ni secretos de laboratorio. Un run posterior genera otra identidad trazable, no hereda estos resultados.
El artefacto expira: conservarlo en un destino autorizado o repetir el ensayo de una revisión aprobada si ya no está disponible.

Las acciones siguientes **no se ejecutaron** y requieren autorización explícita antes de intervenir producción:

1. **Antes de fusionar**, acordar el control del autodeploy. El operador puede preparar/proteger una rama de publicación
   en upstream y seleccionarla en Dokploy según guía §3.6. No cambiarlo desde esta rama ni asumir que un merge documental es inocuo.
   La integración del PR se revisa y realiza manualmente; nunca se fuerza un push ni se fusiona automáticamente.
2. Acreditar backup externo recuperable de MySQL y archivos y una recuperación ensayada fuera de producción.
   Registrar Image/Config.Image y referencia inmutable recuperable de API anterior, límites/carga, salud y montajes efectivos.
   Los nombres físicos previamente identificados son `campusmarket-sistema-2zvsxj_mysql_data` y
   `campusmarket-sistema-2zvsxj_publication_images`; comprobar Name/Destination/RW antes de proceder.
   Un ID de contenedor no sustituye una imagen recuperable. No solicitar privilegios adicionales para suplir un inspector ausente.
3. Publicar **la imagen ya exportada** desde CI autorizado, verificando checksum, Image ID y OCI, sin reconstruirla.
   Harían falta permisos `packages: write` para ese job y acceso al artefacto; la autenticación efímera GITHUB_TOKEN
   debe ser la del repositorio autorizado. Este workflow tiene solo `contents: read` y no publica.
   El publisher existente exige un run `compose-mvp.yml` de `master`: **no acepta sin cambios este artefacto**.
   Su adaptación mínima debe conservar controles de procedencia/checks y revisarse antes de ejecutarse.
   Obtener el digest remoto real y comprobarlo descargando la imagen publicada. No inventar el digest a partir del tar.
4. El administrador debe confirmar un mecanismo permitido para pull de GHCR Internal desde el servidor,
   sin copiar el token efímero del runner a Dokploy ni añadir PAT al código. El login exitoso de Actions anterior
   no acredita acceso del servidor. Si no existe acceso permitido, la promoción sigue bloqueada.
5. Preparar y revisar un cambio **solo de `api.image`** de `compose.prod.yaml` al nuevo digest confirmado.
   Mantener exactamente proyecto `campusmarket-sistema-2zvsxj`, servicio db, volúmenes, límites y variables actuales.
   Conservar la configuración Environment de Dokploy: guía §3.5 genera el `.env` del servidor al desplegar;
   no se presupone un `deploy/.env` en Git ni se imprime `docker compose config` con valores sensibles.
   Validar la resolución de Compose por un operador autorizado sin revelar variables.
6. Autorizar una actualización **exclusivamente de api** sobre el proyecto existente. Un operador con acceso permitido
   podría usar el equivalente de `docker compose -p campusmarket-sistema-2zvsxj -f <compose-resuelto> up -d --no-deps --no-build api`
   tras descargar/verificar la referencia. Confirmar primero el archivo/entorno que Dokploy realmente genera y la capacidad
   de actualizar un servicio; esta auditoría no comprobó un botón UI para ello. Si el panel solo ofrece actualización global,
   no asumir equivalencia ni usarla. Sin solapamiento temporal de APIs: 256+256+256 excedería cuota; contemplar breve corte.
   No usar `down`, Fresh Volumes, borrado de volúmenes ni recreación de db. Ninguno de esos comandos se ejecutó aquí.
7. Con autorización, comprobar `https://campusmarket.iscoutb.dev/app/` en navegador público: Inicio, catálogo, detalle,
   imágenes, atrás/recarga, JS sin errores ni contenido mixto, y tráfico real hacia FastAPI. Verificar `/health`, `/docs`,
   OpenAPI y SHA de API/Web contra la imagen promovida. Registrar HTTPS, hora y evidencias sin consultar usuarios privados.
   Solo entonces cambiar el estado de despliegue institucional/aceptación; el run local no los cierra.

### Rollback previsto, todavía sin ensayo productivo

Antes de promover, registrar y asegurar la disponibilidad de la imagen anterior (no solo un tag local sujeto a limpieza).
Ante fallo de salud, assets, rutas o límites, detener la promoción y devolver **solo `api.image`** a esa referencia,
con el mismo proyecto, Environment y montajes. Actualizar solo api con `--no-deps --no-build`, sin iniciar otra API simultánea,
sin tocar MySQL ni borrar/crear volúmenes. Comprobar salud, contratos, ID de contenedor db sin cambio y montajes originales;
la integridad de fotos/datos se verifica con un mecanismo administrativo autorizado que no exponga contenido de usuarios.
El cambio no introduce migraciones SQL. Pages permanece como interfaz actual/fallback documentado.
Si falta imagen anterior, backup recuperable o mecanismo exclusivo de API, **no comenzar la promoción**.

No se ejecutó migración, rollback, publicación GHCR, cambios DNS, cambios de variables ni operaciones sobre producción.
El [registro IA canónico](../ia.md#fase-2--frontend-institucional-preparado-y-probado-en-ci--2026-10-30)
identifica las propuestas aceptadas para implementación, errores corregidos y alternativas rechazadas.


### Actualización verificada: imagen publicada y mecanismo aislado — 2026-10-30

Esta actualización sustituye los pendientes de publicación GHCR y preparación técnica del procedimiento
anterior; mantiene **BLOQUEADA** la publicación institucional. No se repitieron los seis workflows del PR #76,
que permanece Draft en `fd7a3cc3903c773330cfa6ba9345872932f9000b`.

La imagen del run `41094945507` / artefacto `12996575905` fue publicada sin reconstruir por el
[run 41102641771](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41102641771):
`ghcr.io/nnigarp/campusmarket-web-candidate@sha256:65d34f2de8d035d5a9672be2e6a81bab759089da2fbe91bdca23a17f2f0463fd`.
Conserva el Image ID `sha256:15a6fee324bc315d27ab85674781dfd1bded727243cb6ff752370e70b5d6fd19`
y la fuente `a9b6709a67f8036346acb64b9c2b9849ee355cf2`. La copia íntegra del ZIP original quedó conservada
fuera de la retención temporal de Actions. El digest GHCR anterior `f9eaabdb…` identifica otra imagen;
no constituye por sí solo una referencia de rollback de la API actualmente desplegada.

El [run nuevo 41133683253](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41133683253),
commit de mecanismo `61a9171a6fff1ebfd53b869fc1b37aeb7d405461`, terminó **success**.
Se contrastaron logs y el ZIP del artefacto `13013499875`, SHA-256
`546d3e791d713e307433599a42da310deec566f1e423926cdd43dd682588efc0`: `passed: true`, siete criterios CUMPLE.
Docker 28.0.4 y Compose 2.38.2; 14 pruebas unitarias/Compose reales en el job.
Se verificaron equivalencia de configuración, pull del digest e Image ID, dump/TAR sintéticos restaurados
en otro proyecto, preflight, promoción/rollback solo de API y cleanup del proyecto principal sin recursos.
MySQL mantuvo ID y StartedAt durante ambos reemplazos de API; SQL e imagen conservaron su identidad.
No se recompiló Flutter, no se construyó ni se republicó la imagen.

El control de rollback utiliza el **mismo Image ID**, primero por ID y luego por digest; acredita los
comandos y la preservación, no compatibilidad entre versiones distintas. El resultado conserva
`production_recovery_verified: false` y `production_deployment_blocked: true`.
Solo se sube el JSON de resultados: no Environment, dump, TAR de datos ni copias de credenciales.
Ruff, Actionlint, Gitleaks y 21 regresiones locales (incluido el publicador afectado por imports) pasaron.

Los nombres de volúmenes escritos en el procedimiento previo son nombres **esperados por Compose**,
no montajes físicos acreditados. Los mensajes `Detected: 0 mounts` y la ausencia de montajes en la UI
no resuelven esa incertidumbre. El log de `up -d --build --remove-orphans` confirma riesgo de reconstrucción
por autodeploy; su REVISION antigua y cacheada no identifica suficientemente el código desplegado.
Los datos de Dokploy de esta revisión fueron aportados por el usuario; no se accedió al panel en esta tarea.

No hay respaldo/restauración productivos ni imagen anterior recuperable acreditados. Tampoco se ha
probado el pull desde el servidor, ni se controló autodeploy. Se conserva todo ello como precondición,
sin contacto docente ni operaciones productivas. El procedimiento vigente es únicamente el
[plan operativo canónico](../operacion/despliegue-ghcr.md); esta sección registra evidencia y sus límites.
