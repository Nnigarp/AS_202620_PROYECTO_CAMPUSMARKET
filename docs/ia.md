# Uso de Inteligencia Artificial - CampusMarket

Este documento registra el uso de herramientas de IA como apoyo al proyecto. Todo resultado se revisa antes de incorporarse y las decisiones finales corresponden al equipo.

## Evidencia S1

| Fecha | Herramienta | Uso realizado | Verificación del equipo | Qué se rechazó y por qué |
|---|---|---|---|---|
| 08/08/2026 | ChatGPT | Apoyo para analizar ideas y estructurar problema, objetivo y alcance inicial. | Se contrastó con el alcance acordado por el equipo. | Se descartaron funcionalidades de pagos y envíos porque excedían el alcance del semestre. |
| 08/08/2026 | ChatGPT | Apoyo para organizar documentación inicial y mantenibilidad. | Se revisó antes de subir al repositorio. | Se descartó ampliar el prototipo con funciones no necesarias para S1. |

## Evidencia S2

| Fecha | Herramienta | Uso realizado | Verificación del equipo | Qué se rechazó y por qué |
|---|---|---|---|---|
| 16/08/2026 | ChatGPT | Apoyo para estructurar arc42 1–3 y restricciones. | Se contrastó con la actividad de S2. | Se rechazaron restricciones que eran requisitos funcionales y no restricciones arquitectónicas. |
| 16/08/2026 | ChatGPT | Apoyo para formular escenarios y árbol de utilidad. | Se verificó que cada escenario tuviera las seis partes y medida numérica. | Se descartaron medidas no verificables o formuladas de manera subjetiva. |
| 16/08/2026 | ChatGPT | Apoyo para C4 Nivel 1 mediante PlantUML. | Se verificaron actores, relaciones, leyenda y alcance. | Se descartaron actores o integraciones que no pertenecían al alcance actual. |

## Evidencia S3

| Fecha | Herramienta | Uso realizado | Verificación del equipo | Qué se rechazó y por qué |
|---|---|---|---|---|
| 17-23/08/2026 | ChatGPT | Comparación de arquitectura en capas, hexagonal y monolito modular. | Se contrastó con EC-01 a EC-04 y las restricciones del proyecto. | Se descartó recomendar microservicios porque no era una alternativa solicitada y añadía complejidad innecesaria. |
| 17-23/08/2026 | ChatGPT | Apoyo para redactar ADR-0001 y tácticas. | El equipo revisó contexto, alternativas, decisión y consecuencias. | Se descartó arquitectura hexagonal como decisión actual por su mayor costo de abstracción para el alcance. |
| 23/08/2026 | ChatGPT | Apoyo para organizar el esqueleto FastAPI, prueba de salud y documentación. | Se comprobó mediante GitHub Actions. | Se descartó implementar lógica de negocio completa porque S3 pedía únicamente el esqueleto ejecutable. |

## Evidencia S4

| Fecha | Herramienta | Uso realizado | Verificación del equipo | Qué se rechazó y por qué |
|---|---|---|---|---|
| 25/08/2026 | ChatGPT | Auditoría de CampusMarket contra la ficha oficial de S4 y el feedback del curso. | Se contrastaron los 10 criterios uno por uno con el repositorio. | Se descartó crear C4 Nivel 3 porque la actividad lo pospone a Semana 6. |
| 25/08/2026 | ChatGPT | Apoyo para diseñar el corte vertical crear publicación: Flutter → FastAPI → SQLite. | Se revisó que atraviese interfaz, lógica y persistencia y que corresponda con ADR-0001. | Se descartó documentar MySQL como persistencia implementada porque todavía no existe en el código. |
| 25/08/2026 | ChatGPT | Apoyo para arc42 5, 6, 9, 12, C4 Nivel 2 y trazabilidad. | Se verificó que la documentación describa únicamente elementos presentes en la propuesta de implementación S4. | Se descartó copiar el contenido del ADR dentro de la sección 9; se mantiene un enlace al ADR. |
| 28/08/2026 | ChatGPT | Revisión de la retroalimentación provisional de S4 y apoyo para ajustar arc42 sección 3, coherencia entre C4 Nivel 1 y Nivel 2, correspondencia con el código y trazabilidad. | El equipo contrastó los ajustes con la ficha S4, el estado real del repositorio y las evidencias existentes antes de incorporarlos. | Se rechazó incluir routers, servicios, repositorios y otros detalles internos dentro del C4 Nivel 2 porque ese nivel de detalle corresponde al C4 Nivel 3 y no era requerido para S4. |
| 29/08/2026 | GitHub Copilot | Generación automática de sugerencias para mensajes y descripciones de commits durante la actualización documental del repositorio. | El equipo revisó las sugerencias antes de confirmar los cambios y mantuvo únicamente las que resultaban coherentes con el cambio realizado. | Se rechazaron mensajes genéricos sugeridos automáticamente y se reemplazaron por mensajes específicos como `Completar README con evidencia verificable de S4`, para mantener mayor trazabilidad en el historial del repositorio. |
| 29/08/2026 | ChatGPT | Auditoría final de la Evidencia S4 y apoyo para completar el README con arranque, corte vertical, pruebas, GitHub Actions, arc42, C4 y trazabilidad. | Se verificó en `master` que el README estuviera completo y que el pipeline ejecutara correctamente las pruebas del backend. | Se rechazó introducir SonarCloud apresuradamente en este cierre y modificar nuevamente el ADR-0001, porque no eran cambios necesarios para resolver los hallazgos principales de la ficha S4 y podían introducir inconsistencias innecesarias. |
| 30/08/2026 | ChatGPT | Revisión de la última retroalimentación automática de S4 y apoyo para hacer explícitas en el README las evidencias que el agente no había podido verificar: glosario de dominio y trazabilidad ASP-05. | El equipo comprobó que `docs/arc42/12-glosario.md` y `docs/aspectos.md` ya contenían la información requerida y expuso esa evidencia en el README sin modificar la arquitectura ni el código. | Se rechazó alterar nuevamente los documentos arquitectónicos solo para satisfacer la extracción del agente; se mantuvo la información original y únicamente se hizo más visible y navegable desde el README. |

## Evidencia S5

| Fecha | Herramienta | Uso realizado | Verificación del equipo | Qué se rechazó y por qué |
|---|---|---|---|---|
| 04/09/2026 | ChatGPT | Apoyo para revisar la retroalimentación S1-S4, organizar `correcciones.md`, verificar la trazabilidad de ADR-0001 y revisar el arranque reproducible del sistema. | El equipo contrastó los cambios con el feedback oficial, verificó el PR #5 y el commit `4dd857a`, y ejecutó el arranque con FastAPI, Flutter Web y `/health`. | Se rechazó marcar elementos como saneados sin evidencia y modificar ADR-0001 únicamente para agregar trazabilidad posterior. |
| 05/09/2026 | ChatGPT | Apoyo para revisar SonarQube Cloud y definir el reto arquitectónico S5 a partir del estado real de CampusMarket. | Se verificó el proyecto oficial de SonarQube Cloud y se midió la línea base del bloqueo SQLite: HTTP `500`, `7.323 s`, sin escritura parcial y recuperación HTTP `201`. | Se rechazó usar el monolito modular como nueva restricción y agregar PostgreSQL, colas, cachés o nuevos servicios sin evidencia que lo justificara. |
| 06/09/2026 | ChatGPT | Apoyo para comparar alternativas, definir ADR-0002, implementar la degradación controlada ante bloqueo SQLite y revisar la trazabilidad de S5. | El equipo obtuvo `3 passed`, `flutter analyze` sin errores y una medición formal de HTTP `503` en `1.283 s`, sin escritura parcial y con recuperación HTTP `201`. | Se rechazó migrar la persistencia o agregar infraestructura porque R-07 exige mantener SQLite y conservar el backend como una única aplicación monolítica modular, sin crear nuevos servicios desplegables. También se descartó el reintento automático por su impacto potencial en el umbral de `≤ 2 s`. |

## Evidencia S6

**Fecha:** 12/09/2026

| Herramienta | Uso realizado | Verificación del equipo | Qué se rechazó y por qué |
|---|---|---|---|
| ChatGPT | Apoyo para interpretar la Evidencia S6, identificar los contextos delimitados de CampusMarket y estructurar el lenguaje ubicuo, mapa de contextos y propiedad de datos. | Se contrastó la propuesta con los módulos reales `usuarios`, `publicaciones`, `catalogo` y `administracion`, y con el estado actual del código. | Se rechazó declarar como implementadas capacidades de Usuarios, Catálogo y Administración que todavía no están materializadas en el repositorio. |
| ChatGPT | Apoyo para auditar la modularidad del backend y localizar operaciones de persistencia relacionadas con `publicaciones`. | Se revisaron `backend/app/publicaciones/`, `backend/app/usuarios/`, `backend/app/catalogo/`, `backend/app/administracion/`, pruebas y scripts. Se confirmó que el escritor productivo de `publicaciones` se encuentra en `backend/app/publicaciones/repository.py`. | Se rechazó afirmar que existían escrituras compartidas sin evidencia. Los accesos SQLite de pruebas y medición se clasificaron como instrumentación y no como módulos de dominio propietarios. |
| ChatGPT | Apoyo para documentar los riesgos MOD-01 a MOD-04 y definir reglas preventivas de comunicación entre contextos. | Los riesgos se contrastaron con el mapa de contextos y con la regla de dueño único de datos de S6. | Se rechazó crear nuevos microservicios, bases de datos o infraestructura únicamente para demostrar separación entre contextos. |
| ChatGPT | Apoyo para actualizar la trazabilidad de S6 en `docs/aspectos.md` y revisar si era necesario modificar C4 Nivel 3 o generar un nuevo ADR. | Se verificó que S6 mantiene los límites principales del monolito modular definidos anteriormente y que no introduce un nuevo estilo arquitectónico. | Se descartó crear un ADR nuevo o modificar artificialmente los límites solo para aumentar la documentación, porque la actividad los exige únicamente si los límites cambian respecto al corte anterior. |

### Actualización S6 — 13/09/2026

| Herramienta | Uso realizado | Verificación del equipo | Qué se rechazó y por qué |
|---|---|---|---|
| ChatGPT | Apoyo para completar el C4 Nivel 3 del Backend y revisar su correspondencia con la implementación real. | Se contrastó el diagrama con `main.py`, `router.py`, `service.py`, `repository.py` y SQLite. | Se rechazó presentar Usuarios, Catálogo y Administración como funcionalidades ya implementadas. |
| ChatGPT | Apoyo para incorporar `backend/tests/test_modularidad_s6.py` y reforzar la auditoría de propiedad de datos. | Se verificó que la prueba controle el escritor único de `publicaciones`, las dependencias entre módulos y el acceso a SQLite. GitHub Actions finalizó con las pruebas en verde. | Se rechazó crear pruebas sobre capacidades que todavía no existen en el código. |
| ChatGPT | Apoyo para actualizar la trazabilidad documental de S6 en README, `docs/aspectos.md` y arc42. | Se revisó que los documentos apunten a C4 Nivel 3, auditoría, propiedad de datos y prueba automática sin contradecir ADR-0001. | Se rechazó crear un nuevo ADR porque los límites definidos en el primer corte no cambiaron. |
| ChatGPT | Apoyo para la revisión final de S6 contra los criterios de la actividad. | Se contrastaron los artefactos con el estado actual de `master`, las pruebas de GitHub Actions y el Quality Gate de SonarQube Cloud. | Se rechazó agregar microservicios, nueva infraestructura o documentación artificial que no correspondiera con el repositorio. |

## Evidencia S7

**Fecha:** 15/09/2026

| Herramienta | Uso realizado | Verificación del equipo | Qué se rechazó y por qué |
|---|---|---|---|
| ChatGPT | Apoyo para contrastar la ficha S7 con la API realmente implementada y definir el alcance del contrato. | Se localizaron `GET /health`, `GET /publicaciones` y `POST /publicaciones` en FastAPI y se comprobaron sus consumidores y pruebas existentes. | Se rechazó inventar endpoints, mensajería o eventos porque no existen en el código actual y no corresponden al alcance de S7. |
| ChatGPT | Apoyo para estructurar OpenAPI 3.1, la prueba de correspondencia y el escenario EC-06. | Se ejecutaron las 11 pruebas y se confirmó la igualdad entre el contrato `1.0.0` y el esquema del proveedor, además de las necesidades del consumidor Flutter. | Se rechazó considerar la documentación automática de Swagger como prueba suficiente; por sí sola no bloquea cambios incompatibles. |
| OpenAPI Generator | Generación reproducible de un cliente Dart a partir de `contracts/openapi-v1.json`. | OpenAPI Generator 7.25.0 produjo las operaciones `crearPublicacion`, `listarPublicaciones` y `consultarSalud` a partir de los `operationId` del contrato. | Se rechazó incorporar un segundo cliente productivo al frontend porque `publicaciones_api.dart` ya cubre el corte actual y mantener ambos duplicaría responsabilidades. |
| ChatGPT | Apoyo para comparar integración síncrona y asíncrona y redactar ADR-0003. | La decisión se contrastó con el flujo Flutter-FastAPI, EC-05, EC-06 y la ausencia de infraestructura de mensajería. | Se descartó la integración asíncrona para crear/listar publicaciones porque eliminaría la confirmación inmediata y obligaría a diseñar estados pendientes, reintentos, idempotencia y consistencia eventual sin evidencia que lo justifique. |
| ChatGPT | Apoyo para diseñar y documentar la mutación incompatible `titulo` → `nombre`. | La prueba de contrato produjo `exit code 1` con `1 failed, 2 passed`; tras restaurar `titulo`, el conjunto completo volvió a verde. | Se rechazó conservar el cambio incompatible o debilitar la prueba para hacerla pasar, porque rompería al consumidor Flutter. |
| ChatGPT | Apoyo para hacer explícita la prueba de contrato en el pipeline, diseñar la mutación controlada de `operationId`, consolidar la evidencia real y auditar el cierre de S7. | Se verificó la ejecución roja con `1 failed, 10 passed` y `exit code 1`; después de restaurar `crearPublicacion`, las ejecuciones del fork y del PR #38 finalizaron en verde con las pruebas funcionales y de contrato separadas. SonarQube Cloud reportó Quality Gate aprobado y cero problemas nuevos. | Se rechazó conservar el cambio incompatible `registrarPublicacion`, debilitar la comparación entre OpenAPI y FastAPI, o declarar cerrado el trabajo sin comprobar las ejecuciones reales de GitHub Actions. |

### Actualización S7 — 16/09/2026

| Herramienta | Uso realizado | Verificación del equipo | Qué se rechazó y por qué |
|---|---|---|---|
| ChatGPT | Apoyo para revisar la observación docente sobre persistencia y planear la migración de SQLite a MySQL sin modificar las fronteras del monolito modular. | Se contrastó la propuesta con `repository.py`, la arquitectura vigente y las pruebas. Se implementó MySQL mediante PyMySQL encapsulado en el repositorio de Publicaciones. | Se rechazó mantener SQLite como persistencia vigente y se evitó alterar los límites del monolito modular por un cambio exclusivamente tecnológico de persistencia. |
| ChatGPT | Apoyo para redactar ADR-0004 y alinear C4, arc42 y la trazabilidad arquitectónica con la persistencia MySQL, preservando SQLite únicamente donde corresponde como evidencia histórica. | Se revisaron ADR-0004, C4 Niveles 1, 2 y 3, arc42 y `docs/aspectos.md` contra la implementación actual. | Se rechazó reescribir las evidencias históricas de S4 y S5 como si MySQL hubiera sido utilizado originalmente en esos cortes. |
| ChatGPT | Apoyo para adaptar GitHub Actions a una base MySQL de CI y revisar las pruebas funcionales, de modularidad y de contrato. | Se ejecutó `python -m pytest backend/tests -q` y se verificó el pipeline con MySQL, pruebas del backend, SonarCloud y análisis de código. | Se rechazó incorporar credenciales locales o reales dentro del repositorio o del workflow. |
| ChatGPT | Apoyo para revisar la coherencia entre el contrato OpenAPI, FastAPI, la persistencia vigente y la documentación del proyecto. | Se contrastaron `contracts/openapi-v1.json`, FastAPI, C4, ADR-0003, ADR-0004, README y pruebas automatizadas. | Se rechazó presentar SQLite como tecnología vigente o confundir las decisiones históricas con el estado arquitectónico actual. |
| ChatGPT | Auditoría de cierre documental de S7. | Se corrigió el formato de `docs/aspectos.md`, se aclaró el estado histórico de ADR-0002 en `docs/arc42/09-decisiones.md`, se revisaron referencias SQLite/MySQL y se mejoró el script de arranque para validar la disponibilidad de MySQL. | Se rechazó eliminar ADR, mediciones, scripts o evidencias históricas únicamente por contener referencias a SQLite, ya que forman parte de la trazabilidad real del proyecto. |

### Saneamiento posterior a revisión automática S7 — 17/09/2026

| Herramienta | Uso realizado | Verificación del equipo | Qué se rechazó y por qué |
|---|---|---|---|
| ChatGPT | Apoyo para revisar los hallazgos de la pasada temprana del agente y localizar la evidencia real de S7. | Se contrastaron `contracts/openapi-v1.json`, FastAPI, `test_contrato_openapi.py`, el workflow, `docs/aspectos.md`, README y los runs de GitHub Actions. | Se rechazó modificar arquitectura, endpoints o contrato solo para mejorar el resultado del revisor; los hallazgos principales requerían hacer visible evidencia ya existente. |
| ChatGPT | Apoyo para sanear la evidencia S7 y hacer explícitos schemas, correspondencia contrato ↔ código, historial Git, ejecución contractual en CI y fallo ante incompatibilidad. | Se verificaron OpenAPI `3.1.0`, API `1.0.0`, `POST /publicaciones`, `GET /publicaciones`, `GET /health`, commit `485249a`, Run #93 verde y un run rojo real por cambio incompatible. | Se rechazó declarar cumplimiento únicamente mediante texto; se utilizaron rutas, commits y ejecuciones reproducibles. |
| ChatGPT | Apoyo para reforzar la trazabilidad en `docs/aspectos.md`, README, arc42 sección 6 y C4 Nivel 2. | Se comprobó ASP-07, se corrigió el formato Markdown de la vista de ejecución y se repararon los enlaces hacia ADR-0004 sin modificar código, contrato ni ADR aceptados. | Se rechazó modificar ADR-0003 o introducir cambios arquitectónicos innecesarios durante el saneamiento documental. |
| ChatGPT | Apoyo para revisar el estado de SonarQube Cloud y la configuración oficial del proyecto. | Se verificó el proyecto `ISCOUTB_AS_202620_PROYECTO_CAMPUSMARKET`, Quality Gate aprobado y análisis público. El workflow aún no invoca explícitamente el scanner. | Se rechazó restaurar una configuración personal, duplicar mecanismos de análisis o declarar cerrado Sonar sin scanner en CI y un run exitoso asociado. |

### Cierre documental S7 — 18/09/2026

| Herramienta | Uso realizado | Verificación del equipo | Qué se rechazó y por qué |
|---|---|---|---|
| ChatGPT | Apoyo para realizar la auditoría final de S7, actualizar la evidencia consolidada y alinear README con el estado real de `master`, GitHub Actions y SonarQube Cloud. | Se verificó el proyecto oficial `ISCOUTB_AS_202620_PROYECTO_CAMPUSMARKET`, la organización `isco-utb`, Quality Gate `Passed`, la configuración `.sonarcloud.properties` y el pipeline estable de `master`. GitHub Actions volvió a finalizar correctamente después de los ajustes documentales. | Se rechazó declarar como cumplida la integración del scanner sin un run exitoso que lo ejecutara y se rechazó conservar en `master` una configuración conocida como fallida únicamente para aparentar cumplimiento. |
| ChatGPT | Apoyo para evaluar una integración explícita del scanner de SonarQube Cloud desde GitHub Actions y determinar la causa de su imposibilidad actual. | La validación controlada permitió comprobar que la ejecución del scanner sobre el proyecto oficial requiere una credencial con autorización para ejecutar análisis en la organización `isco-utb`. Después de la comprobación se preservó el workflow estable de `master`. | Se rechazó utilizar el proyecto personal de SonarQube Cloud como sustituto del proyecto oficial del curso y se rechazó mantener una integración que dejara el pipeline principal en rojo por falta de autorización. |

---

## Evidencia S8

**Fecha:** 21-27/09/2026

| Herramienta | Uso realizado | Verificación del equipo | Qué se rechazó y por qué |
|---|---|---|---|
| ChatGPT | Apoyo para interpretar literalmente la ficha oficial de S8 y separar los criterios de despliegue reproducible, CI, health check, observabilidad, secretos, costos y documentación arquitectónica. | El equipo contrastó cada criterio contra la ficha oficial, el repositorio y resultados reales de ejecución antes de declararlo cumplido. | Se rechazó considerar un criterio cumplido únicamente porque existiera un archivo o una configuración. Se exigió requisito → implementación → ejecución real → evidencia verificable. |
| ChatGPT | Apoyo para revisar el estado inicial de S8 y organizar una matriz de cumplimiento antes de modificar el sistema. | Se contrastaron código, documentación, workflows, persistencia vigente y arquitectura real antes de implementar cambios. | Se rechazó reutilizar evidencia histórica de SQLite como si describiera el estado vigente de MySQL. |
| ChatGPT | Apoyo para diseñar e implementar un health check dependiente de la disponibilidad real de MySQL. | Se verificó `GET /health` con MySQL disponible obteniendo HTTP `200`; con la base detenida se obtuvo HTTP `503`; al restablecerla volvió a HTTP `200`. | Se rechazó utilizar un health check que comprobara únicamente que FastAPI estuviera ejecutándose, porque no evidenciaría el estado de la dependencia principal. |
| ChatGPT | Apoyo para estructurar logs HTTP en formato estructurado con campos operativos verificables. | En la ejecución real de Azure App Service se observaron campos como `timestamp`, `level`, `event`, `request_id`, `method`, `path`, `status_code` y `duration_ms`. | Se rechazó considerar mensajes libres de consola como evidencia equivalente a logs estructurados. |
| ChatGPT | Apoyo para implementar una métrica operacional consultable mediante `GET /ops/metrics/ec01`. | Se generaron solicitudes reales y se observaron 10 de 10 dentro del objetivo de `2000 ms`, con un máximo aproximado de `164.41 ms` y `meets_backend_target: true`. | Se rechazó presentar esta medición como validación completa extremo a extremo de EC-01, porque mide principalmente el comportamiento del backend y no toda la experiencia desde Flutter Web. |
| ChatGPT | Apoyo para incorporar Ruff al pipeline y revisar el workflow de GitHub Actions junto con MySQL 8.4 y las pruebas automatizadas. | El workflow ejecutó análisis estático, servicio MySQL, pruebas funcionales, arquitectónicas y de contrato. Después del merge S8, el job `test` sobre `master` terminó en `success`. | Se rechazó declarar el pipeline cerrado utilizando solamente ejecuciones de la rama de trabajo; se verificó nuevamente el estado del merge en `master`. |
| ChatGPT | Apoyo para preparar FastAPI para Azure App Service mediante configuración por entorno, TLS hacia MySQL y CORS para el frontend público. | Se comprobó el backend público, `/health`, la preflight `OPTIONS /publicaciones` desde `https://nnigarp.github.io` y posteriormente un `POST /publicaciones` real desde Flutter Web. | Se rechazó desactivar TLS, hardcodear credenciales o utilizar una política CORS más abierta de la necesaria. |
| ChatGPT | Apoyo para desplegar FastAPI en Azure App Service y MySQL en Azure Database for MySQL Flexible Server. | Se verificó que el backend público accede realmente a MySQL y que una publicación creada desde la interfaz pública queda persistida y puede recuperarse posteriormente. | Se rechazó considerar una captura del portal de Azure como evidencia suficiente del despliegue. La validación se realizó mediante URL pública y comportamiento funcional. |
| ChatGPT | Apoyo para versionar la infraestructura de Azure mediante `infra/main.bicep`. | La plantilla fue compilada con `az bicep build` y validada mediante `az deployment group validate`, obteniendo `provisioningState: Succeeded` y `error: null`. | Se rechazó documentar solamente comandos manuales de creación de recursos como si fueran infraestructura reproducible. |
| ChatGPT | Apoyo para proteger secretos mediante parámetros seguros de Bicep, App Settings y variables de entorno. | Se revisó que la contraseña real de MySQL no quedara almacenada en el código, Bicep ni documentación versionada. | Se rechazó escribir credenciales reales en archivos del repositorio o evidencias. |
| ChatGPT | Apoyo para hacer configurable la URL del backend en Flutter mediante `CAMPUSMARKET_API_BASE_URL` y preparar el build Web de producción. | Se ejecutó `flutter analyze`, se generó el build con la URL pública de Azure y se comprobó posteriormente desde navegador. | Se rechazó mantener `localhost:8000` como backend fijo para el frontend de producción. |
| ChatGPT | Apoyo para publicar Flutter Web mediante GitHub Pages. | El build fue publicado en la rama `gh-pages`, el workflow de Pages finalizó correctamente y la aplicación quedó accesible públicamente. | Se rechazó considerar el build local como evidencia de publicación mientras todavía no existiera una URL pública verificable. |
| ChatGPT | Apoyo para detectar una inconsistencia documental en la interfaz que todavía indicaba `Flutter → FastAPI → SQLite`. | Se verificó el código fuente, se corrigió el texto a `CampusMarket S8: Flutter Web → FastAPI → MySQL en Azure.`, se reconstruyó y republicó el frontend, y después se comprobó visualmente la versión pública corregida. | Se rechazó dejar una interfaz públicamente desplegada que contradijera la arquitectura vigente. |
| ChatGPT | Apoyo para actualizar arc42 sección 7 con la vista de despliegue real y sección 2 con restricciones operativas de S8. | La documentación se contrastó con GitHub Pages, Azure App Service, Azure MySQL, Bicep, health check y observabilidad realmente ejecutados. | Se rechazó conservar la descripción histórica en la que el proveedor cloud aparecía todavía como pendiente. |
| ChatGPT | Apoyo para redactar ADR-0005 y documentar las consecuencias de distribuir frontend, backend y persistencia entre GitHub Pages y Azure. | Se contrastó la decisión con la topología realmente desplegada y con la continuidad del monolito modular. | Se rechazó describir el despliegue como una migración a microservicios, porque las fronteras de dominio del backend no cambiaron. |
| ChatGPT | Apoyo para documentar costo mensual, supuestos y punto de ruptura. | Se utilizó la configuración realmente observada: App Service F1 y Azure MySQL `Standard_B1ms`, 1 vCore, 2 GiB y 32 GiB; la estimación aproximada observada para MySQL fue `USD 14.71/mes` antes de beneficios académicos. | Se rechazó presentar los créditos académicos como garantía permanente de costo cero o inventar una factura no observada. |
| ChatGPT | Apoyo para definir un procedimiento de rollback reproducible a partir de un commit conocido. | Se documentó el uso de `git archive` y `az webapp deploy` para backend y la republicación de un `build/web` conocido para frontend. | Se rechazó definir rollback únicamente como “volver a una versión anterior” sin pasos ejecutables. |
| ChatGPT | Apoyo para consolidar la evidencia S8 en `docs/evidencias/evidencia-s8-2026-09-27.md` y actualizar el README con el estado de operación real. | Se contrastaron URLs, infraestructura, CI, health, observabilidad, costos, rollback y documentación con los artefactos y resultados ejecutados durante S8. | Se rechazó utilizar solamente capturas de paneles de proveedor como sustituto de evidencia reproducible. |
| ChatGPT | Auditoría final del PR #43 y del estado de `master`. | El PR `S8 - Despliegue y operación de CampusMarket` fue integrado al repositorio oficial. El merge commit `bea2412082b0acb2dc37262376622d63fccff5df` produjo un job `test` exitoso y SonarQube Cloud reportó `Quality Gate passed`. | Se rechazó cerrar S8 usando únicamente el hash de la rama `S8-despliegue-operacion`; la referencia de cierre debía corresponder a `master`. |

### Evidencias verificables de S8

La validación realizada durante S8 utilizó, entre otros, los siguientes
artefactos:

- `infra/main.bicep`;
- `.github/workflows/backend-tests.yml`;
- `backend/app/main.py`;
- `backend/app/publicaciones/repository.py`;
- `backend/tests/test_health.py`;
- `backend/tests/test_publicaciones_vertical.py`;
- `backend/tests/test_contrato_openapi.py`;
- `docs/arc42/02-restricciones.md`;
- `docs/arc42/07-vista-despliegue.md`;
- `docs/arc42/ARC42.md`;
- `docs/adr/0005-desplegar-campusmarket-en-azure-y-github-pages.md`;
- `docs/evidencias/evidencia-s8-2026-09-27.md`;
- `README.md`.

### Estado de cierre revisado con apoyo de IA

```text
Repositorio:
ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET

PR:
#43 - S8 - Despliegue y operación de CampusMarket

Merge commit:
bea2412082b0acb2dc37262376622d63fccff5df

Rama:
master

GitHub Actions:
success

SonarQube Cloud:
Quality Gate passed

Frontend:
https://nnigarp.github.io/AS_202620_PROYECTO_CAMPUSMARKET/

Backend:
https://campusmarket-s8-api-nilver.azurewebsites.net

Health:
https://campusmarket-s8-api-nilver.azurewebsites.net/health
```

## Evidencia S9

**Fecha:** 01/10/2026

| Herramienta | Uso realizado | Verificación del equipo | Qué se rechazó y por qué |
|---|---|---|---|
| ChatGPT | Apoyo para identificar una porción real de CampusMarket que permitiera materializar ASP-01 y EC-01 sin romper el monolito modular. Se propuso implementar Catálogo con búsqueda, filtros y detalle consumiendo una capacidad de lectura de Publicaciones. | El equipo contrastó la propuesta con ADR-0001, la propiedad de datos definida en S6 y el riesgo MOD-01. Se verificó que `publicaciones` permanezca como único propietario de persistencia. | Se rechazó que `catalogo` accediera directamente a MySQL o importara `backend/app/publicaciones/repository.py`, porque eso introduciría un segundo módulo acoplado a la persistencia y erosionaría la frontera definida en S6. |
| ChatGPT | Apoyo para redactar ADR-0009 y estructurar alternativas: acceso directo a MySQL, servicio independiente y consumo de una capacidad explícita de lectura de Publicaciones. | El equipo mantuvo el monolito modular, descartó nuevos servicios desplegables y dejó ADR-0009 en estado `Propuesto` hasta completar implementación, pruebas y medición. | Se rechazó introducir microservicios para Catálogo porque no existe evidencia de escalado o aislamiento que justifique esa complejidad. |
| ChatGPT | Apoyo para implementar `backend/app/catalogo/service.py`, `router.py` y registrar el nuevo router en FastAPI. | Se ejecutaron pruebas funcionales del catálogo, pruebas de contrato OpenAPI y pruebas de modularidad. El contrato versionado se regeneró desde `app.openapi()` y volvió a coincidir con el proveedor. | Se rechazó editar manualmente partes aisladas del contrato OpenAPI porque el contrato versionado debe corresponder exactamente con el esquema generado por FastAPI. |
| ChatGPT | Apoyo para diseñar pruebas funcionales del Catálogo con datos controlados mediante `monkeypatch`. | `backend/tests/test_catalogo.py` verificó listado, búsqueda por texto, filtros por modalidad, estado y precio, detalle y errores controlados. Resultado: `8 passed`. | Se corrigió una primera versión de pruebas que dependía de una instancia MySQL local sin credenciales cargadas. Se evitó confundir una falla de infraestructura con una falla de lógica del Catálogo. |
| ChatGPT | Apoyo para diseñar `backend/tests/test_erosion_s9.py` como regla ejecutable de arquitectura. | La prueba verificó que Catálogo no importe el repositorio de Publicaciones, no use PyMySQL y no ejecute escrituras SQL directas. Resultado normal: `3 passed`. | Se rechazó dejar la restricción únicamente documentada. Se exigió una prueba automática capaz de detectar una violación real. |
| ChatGPT | Apoyo para realizar una mutación controlada agregando temporalmente `from backend.app.publicaciones import repository` dentro de Catálogo. | La ejecución produjo `1 failed, 2 passed` y falló específicamente `test_catalogo_no_importa_repository_de_publicaciones`. Tras retirar la mutación, la prueba volvió a `3 passed`. | Se rechazó conservar la importación directa del repositorio o debilitar la prueba para hacerla pasar, porque esa dependencia viola la frontera acordada. |
| ChatGPT | Apoyo para diseñar la medición controlada de EC-01 con 1.000 publicaciones y 10 búsquedas consecutivas. | `backend/tests/test_ec01_catalogo.py` obtuvo `10/10` ejecuciones bajo 2 segundos, promedio `0.020482 s` y máximo `0.050431 s`. La prueba terminó con `1 passed`. | Se rechazó declarar esta medición como validación productiva completa porque usa publicaciones controladas mediante `monkeypatch` y no incluye latencia real de MySQL ni red. |
| ChatGPT | Apoyo para corregir el manejo de indisponibilidad de persistencia en la consulta de publicaciones. | `listar_publicaciones()` traduce `PersistenceUnavailableError` a `PublicationPersistenceUnavailableError`, y el router de Catálogo responde con HTTP `503` controlado. | Se rechazó permitir que la excepción de PyMySQL escapara directamente hasta la capa HTTP, porque expondría detalles internos y produciría comportamiento no controlado. |

---

## Actualización de producto — 02–03/10/2026

| Herramienta | Uso realizado | Verificación del equipo | Qué se corrigió o rechazó y por qué |
|---|---|---|---|
| ChatGPT | Apoyo para evolucionar la interfaz Flutter hacia una experiencia de marketplace responsive con Inicio, Catálogo, detalle, Publicar y Mis publicaciones. | Se ejecutó la aplicación en Android y se recorrieron flujos reales contra FastAPI y MySQL. `flutter analyze` terminó con `No issues found!`. | Se rechazó copiar de referencias visuales funciones que no existen en el backend, como favoritos, mensajería, vendedor verificado, ubicación, perfil, reservas o contacto. Mostrar controles falsos habría hecho divergir la interfaz de las capacidades reales. |
| ChatGPT | Apoyo para diseñar la carga de hasta tres imágenes por publicación y mantener la propiedad del dato dentro de Gestión de Publicaciones. | Se verificó creación real con tres imágenes, lectura desde Catálogo, visualización de imagen principal y galería, y respuesta de imágenes en Mis publicaciones. La suite backend terminó con `36 passed`. | Se rechazó almacenar imágenes como BLOB/Base64 dentro de `publicaciones` y se rechazó que Catálogo accediera directamente a la persistencia. La decisión quedó formalizada en ADR-0011. |
| ChatGPT | Apoyo para implementar Mis publicaciones: listar, editar, cambiar estado y eliminar. | En Android se creó una publicación real, se comprobó su aparición en Catálogo y Mis publicaciones y se probaron edición, cambio de estado y eliminación. | Se corrigió la interpretación de identidad: `propietario_id = 1` se conserva únicamente como mecanismo temporal y no se presenta como autenticación implementada. |
| ChatGPT | Apoyo para detectar y corregir overflows de tarjetas responsive en Catálogo e Inicio. | Los defectos fueron observados en ejecución Android mediante `RenderFlex overflowed`; después de los ajustes y hot restart la interfaz dejó de mostrar la franja de overflow. `flutter analyze` permaneció limpio. | Se rechazó ocultar el error visual o considerarlo irrelevante solo porque el flujo funcional continuaba operando. |
| ChatGPT | Apoyo para sincronizar el contrato OpenAPI después de ampliar la respuesta de `/publicaciones/mias` con imágenes. | `backend/tests/test_contrato_openapi.py` terminó con `3 passed`; la suite completa terminó con `36 passed`. | Se rechazó restaurar el snapshot anterior para forzar las pruebas a verde. El contrato se actualizó para representar el proveedor real. |
| ChatGPT | Auditoría final de modularidad y trazabilidad antes del cierre. | Se revisó `test_modularidad_s6.py`, la dirección `router → service → repository → MySQL`, la dependencia Catálogo → servicio de Publicaciones y el working tree limpio antes del bloque documental. | Se rechazó declarar EC-02 como completamente cumplido porque el escenario exige usuarios autenticados distintos y esa capacidad todavía no existe. También se corrigió la duplicación de numeración ADR: la gestión de imágenes pasó a ADR-0011 y ADR-0010 permanece como la decisión S9 sobre no incorporar un componente generativo. |

### Resultado de verificación del 03/10/2026

```text
backend completo:
36 passed, 2 warnings

contrato OpenAPI:
3 passed

Flutter:
No issues found!

git diff --check:
sin errores
```

La generación asistida no se considera evidencia suficiente por sí sola. Los
cambios anteriores fueron contrastados con ejecución real, pruebas automáticas,
análisis estático y las fronteras arquitectónicas vigentes.

## Criterio de uso

La IA se utiliza como apoyo para análisis, documentación, organización, comparación de alternativas y revisión técnica.

El equipo mantiene la responsabilidad de:

- revisar cada propuesta antes de incorporarla;
- ejecutar directamente las pruebas y mediciones;
- contrastar las recomendaciones con el estado real del repositorio;
- aceptar, corregir o rechazar las propuestas de IA con justificación técnica;
- tomar y defender las decisiones arquitectónicas finales.

Las propuestas generadas por IA no se consideran evidencia por sí mismas. La evidencia utilizada por el proyecto corresponde a resultados verificables del repositorio, pruebas ejecutadas, mediciones, documentación trazable y decisiones revisadas por el equipo.
## 2026-10-03 — MVP bloque 1: identidad real y propiedad

| Propuesta IA | Decisión del equipo | Motivo / verificación |
|---|---|---|
| Sesión opaca revocable, scrypt estándar | Aceptado | ADR-0012; prueba real de registro/login, expiración y reutilización tras logout |
| Derivar propietario de sesión; no aceptar ID en body | Aceptado | Dos cuentas reales, EC-02 10/10; datos revisados después de cada intento |
| Allowlist de moderadores por correo sin verificar | Rechazado y corregido | Permite registrar un correo privilegiado; ADR-0014 usa IDs de cuentas comprobadas fuera del flujo público |
| Asignar datos heredados al primer usuario | Rechazado | Propiedad no demostrada; preservar filas en cuarentena sin propietario |
| Considerar rowcount=0 como falta de permiso | Corregido | MySQL cuenta filas cambiadas: PUT/PATCH idénticos son válidos; comprobar lectura acotada por propietario |
| Repetir contraseña en error de validación | Rechazado | Respuesta de validación solo contiene loc/msg/type; nunca input |
| Añadir JWT, OAuth, recuperación o roles amplios | Rechazado | No necesarios para el MVP; no se añadieron dependencias de producto |
| Instalar httpx2 para eliminar aviso de deprecación | Rechazado en este bloque | httpx existente pasa las pruebas; aviso documentado, sin añadir dependencia por estética |

Herramienta: Codex. Revisado con Ruff, pruebas sobre MySQL 8.0.46 aislado,
contrato v2 y mutaciones en copias temporales. Las tres mutaciones (autoría SQL,
contraseña ignorada y acceso a repository ajeno) hacen fallar una aserción;
no se consideran detectadas por errores de colección. No se exponen tokens,
contraseñas ni hashes reales en documentación.

## 2026-10-03 — MVP bloque 2: imágenes y administración

| Propuesta IA | Decisión | Motivo / verificación |
|---|---|---|
| Validar imágenes solo por extensión o firma manual | Rechazado | No asegura decodificación ni retiro de metadatos |
| Pillow 12.3.0 como única dependencia nueva del backend | Aceptado | PyPI oficial: Python >=3.10, CPython 3.12 Linux/Windows, licencia MIT-CMU, código python-pillow; ADR-0015 |
| pytest-cov como dependencia del proyecto | Rechazado | No es necesario para este bloque; pruebas reales y mutaciones verifican el defecto |
| Reportes reales y moderación por ID de cuenta comprobada | Aceptado | ADR-0013 y 0014; registro/perfil no pueden conceder capacidad |
| Panel de métricas o botones ficticios | Rechazado | No hay requisito ni contrato ejecutable que justifique esa interfaz |
| Resolver reportes sin exclusión mutua | Corregido | Mantener la fila de reporte bloqueada durante la revisión; ocultado de publicación idempotente por servicio |
| Elegir principal y retirar fotos desde el router/SQL ajeno | Rechazado | Router→service→repository; único escritor y propiedad comprobados |
| Limitar imágenes solo desde Flutter | Rechazado | Límite tres bajo lock en MySQL; cuatro subidas concurrentes producen 3×201 + 1×400 |

Verificación: 66 pruebas pasan sobre MySQL real; imágenes decodificadas,
metadatos retirados, autorización y concurrencia; pruebas AST de propiedad
por tabla y de imports. No se alteraron ADR aceptados.

## MVP — sesión real en Flutter (2026-10-03)

- **Aceptado:** controlador de sesión con token opaco exclusivamente en memoria,
  registro, login, consulta de usuario, edición de nombre y logout contra la API.
  Se aplica ADR-0012; no se agrega ninguna dependencia de ejecución.
- **Corregido:** el cliente enviaba propietario fijo y lo incluía en parámetros de
  gestión. Ahora obtiene autorización de la sesión y no suministra propietario.
- **Corregido:** cambiar de cuenta conserva potencialmente vistas privadas en
  IndexedStack. La navegación descarta las vistas de la identidad anterior y
  construye pantallas privadas únicamente con sesión autenticada.
- **Corregido:** reintentar una subida fallida creaba otra publicación; se conserva
  el identificador ya creado y el progreso de las imágenes confirmadas.
- **Corregido:** precio con coma pasaba validación pero fallaba al guardarse. Se
  normaliza la coma y se respetan precio finito, máximo y dos decimales.
- **Rechazado:** guardar tokens en localStorage, añadir shared_preferences o un
  gestor global adicional. La memoria y ChangeNotifier del SDK cubren el MVP.
- **Rechazado:** afirmar Web/Android funcional por revisión de código. Se agrega
  workflow de análisis, pruebas y compilación; la ejecución del flujo real se
  documentará cuando exista.
- **Verificación pendiente:** las pruebas Flutter y los builds se ejecutan en CI
  porque el entorno local perdió transporte de terminal y la ejecución anterior
  de Flutter recibió rechazo automático por una solicitud inesperada a metadata.
  No se reintenta ese acceso local.
- **Herramientas de CI:** flutter-action mantenido por subosito, referencia v2
  verificada y fijada a 1a449444c387b1966244ae4d4f8c696479add0b2, SDK oficial
  3.47.3. actions/setup-java y upload-artifact pertenecen a GitHub. Estas
  herramientas preparan/verifican el entorno; no incorporan paquetes al producto.

### Correcciones y extensión de producto del cliente

- **Corregido:** CI detectó prefer_interpolation_to_compose_strings y
  use_super_parameters. Se corrigió el código sin desactivar reglas. Analyze,
  seis pruebas y builds Web/Android quedaron aprobados en 1aefd452.
- **Aceptado:** lockfile y analysis_options emitidos por Flutter 3.47.3. El SDK
  ajustó cuatro dependencias ya existentes de sus pruebas; no se amplía pubspec.
- **Aceptado:** galería propia editable (subir, eliminar, elegir principal);
  disponibilidad visible y detalle que consulta datos actuales.
- **Aceptado:** reporte real desde detalle y cola real de pendientes para la
  capacidad configurada por IDs del ADR-0014. Sin panel ni estadísticas ficticias.
- **Rechazado:** botón de contacto deshabilitado y mensajes sobre contratos backend
  en el detalle. Se sustituyen por información útil y un reporte que sí funciona.
- **Aceptado:** portada con fotografía de una publicación real cuando existe.
  No se insertan productos ni fotografías ficticias en datos de producción.
- **Verificación:** dos mutaciones del cliente verifican que las pruebas detectan
  propietario fijo y contaminación de sesión entre respuestas de cuentas distintas.
  Su ejecución quedará registrada en la CI del bloque siguiente.

### Flujo real y sincronización de contrato

- **Corregido:** contrato generado fuera del intérprete contenía default null que
  FastAPI omite. La igualdad de OpenAPI detectó la discrepancia; se corrigió y
  todas las verificaciones quedaron verdes en d94cc62, sin relajar la prueba.
- **Aceptado:** integration_test del SDK para pruebas con backend/MySQL en Chrome
  y Android; necesidad, mantenimiento y compatibilidad documentados.
- **Aceptado:** archivos sintéticos controlados y puente del selector real, sin
  modificar cuentas, almacenamiento ni datos de producción.
- **Rechazado:** declarar Android funcional únicamente por compilar o sustituir
  file_picker por un mock que evitaría demostrar lectura/subida de archivos.
- **Verificación pendiente:** los resultados y capturas del flujo se registrarán
  después de ejecutar el workflow, sin anticipar que está aprobado.

### Correcciones del arnés tras su primera ejecución real

- **Corregido:** esperar el título del campo de edición adelantaba la consulta de
  Mis publicaciones. Ahora se exige la pantalla propia cargada tras guardar y subir.
- **Corregido:** el redimensionado externo de Chrome podía ser sobrescrito por el
  driver del SDK. Se usa browser-dimension oficial y se comprueba el ancho real.
- **Corregido:** las tarjetas del grid se crean al entrar al viewport. La prueba
  desplaza la sección de resultados antes de comprobar su contenido.
- **Corregido:** Android API 35 rechazó la copia directa a Download. La imagen
  sintética se escribe por MediaStore y se verifica byte a byte antes del selector.
  Fuente: Android 15 Content.java (insert/query/write/read), sin nuevos paquetes.
- **Rechazado:** aceptar capturas de escritorio como evidencia de Web móvil o
  relajar las aserciones de persistencia por una carrera de sincronización.
- **Verificación pendiente:** repetir los tres flujos; los fallos anteriores y su
  hash permanecen disponibles en Actions 37134391642.

- **Corregido:** el flujo de 390 px detectó 8,5 px de desbordamiento en
  "Información del producto"; se permite envolver el título dentro de su fila.
- **Corregido:** el arnés Android espera almacenamiento desbloqueado y conserva
  los errores públicos de MediaStore del emulador para diagnosticar la preparación.

- **Corregido:** el arnés tocaba inmediatamente después de ensureVisible; el
  cambio de scroll no había recalculado la posición del control. Ahora espera
  un frame, comprueba hitTestable y confirma entrada de texto con booleanos
  (sin imprimir valores que podrían ser contraseñas). Se mantiene la validación
  real del rango y se registra captura ante fallo.

- **Aceptado:** los dos flujos Web pasaron en 78dd5edf; diez denegaciones de
  modificaciones ajenas y estado intacto después de cada intento por plataforma.
- **Corregido:** boot_completed y ce_available no garantizan que MediaStore
  haya registrado external_primary. Se espera ese volumen ante el error
  observado, con plazo de 60 s, sin reintentar errores de la aplicación.
- **Aceptado:** resultado sanitizado en el log y artefacto JSON con hash,
  viewport, comprobaciones y nombres de capturas; sin contraseñas ni tokens.

- **Corregido:** analyze señaló avoid_print en el driver de evidencia. Se usa stdout del proceso del driver; no se desactiva la regla del cliente.

- **Corregido:** fuente oficial AndroidPlatform FilePickerAndroid 2.0.0
  configura pickFiles con allowMultiple true. El puente ahora confirma
  OPEN/SELECT/DONE después de elegir el archivo y permite tocar el texto
  Downloads aunque su TextView delegue el click a su padre.
- **Aceptado:** plazo externo de 12 minutos y diagnóstico del selector del
  emulador aislado; los fallos nativos ya no pueden bloquear indefinidamente.
- **Rechazado:** sustituir el selector Android por bytes inyectados en el plugin.
  Continúa usando DocumentsUI, URI real, lectura del archivo y subida HTTP.

- **Corregido:** dump escribía /data/local/tmp mientras cat aún leía /sdcard. Se unifica la ruta en una constante; ese error del arnés impedía observar y operar DocumentsUI.

- **Verificado:** flujo completo aprobado en los tres jobs del run 37139056153,
  hash 30e109137c26634bb77add3ff07a71ab0ea08f50; 19 capturas por plataforma,
  diez intentos ajenos rechazados en cada una, galerías y logout reales.

### Presupuesto del laboratorio y coherencia de migración

- **Aceptado:** ADR-0016 conserva scrypt y los límites de entrada de imágenes,
  serializa trabajo intensivo y normaliza a 2048 px para la cuota oficial de
  512 MB por equipo. Sin dependencias nuevas.
- **Aceptado:** orientación de cámara antes de retirar EXIF, cuerpos acotados
  también sin Content-Length, no-store privado y request IDs UUID.
- **Aceptado:** ADR-0017 coordina inicialización/migración con GET_LOCK de MySQL,
  porque DDL confirma implícitamente y un Lock de Python no coordina procesos.
- **Rechazado:** reducir scrypt para ocultar exceso de memoria; declarar una
  imagen bien orientada solo porque se retiró metadata; dar por atómica una
  secuencia DDL/DML sin coordinación entre inicializadores.
- **Verificación pendiente:** pruebas con MySQL, OpenAPI y cuatro mutaciones
  nuevas; medición posterior del Compose bajo los límites reales.

- **Corregido:** Ruff detectó una separación faltante entre imports estándar y
  del proyecto en security.py al compartir la guardia. Se aplica su corrección;
  se conservan las reglas y la ejecución de todas las pruebas.

### Infraestructura reproducible y cuota efectiva

- **Aceptado:** ADR-0018 prepara el backend monolítico y MySQL 8.4 con dos
  volúmenes nombrados y límites efectivos de 256 MiB/0,5 CPU cada uno.
  Python 3.12.15-slim-bookworm existe en la imagen oficial mantenida por
  docker-library. No se incorpora una biblioteca al producto.
- **Aceptado:** CI genera credenciales efímeras en RUNNER_TEMP con permisos
  0600, prueba HTTP real, hashes concurrentes, una fotografía de 12 MP,
  memory.peak, ausencia de OOM y recreación de API/MySQL conservando sesiones,
  publicaciones y fotos. No imprime inspect/config completos ni secretos.
- **Aceptado:** REVISION y etiqueta OCI comparadas con el hash de CI;
  X-CampusMarket-Revision permite verificar /health sin revelar secretos.
- **Rechazado:** atribuir EC-01 a una prueba con repositorios simulados;
  la nueva medición usa 1000 filas reales, diez búsquedas HTTP y cuota real.
- **Rechazado:** declarar desplegado el Compose por construirlo en CI.
  No se aprovisiona Azure ni se opera Dokploy antes del cierre del MVP.
- **Verificación pendiente:** ejecución de Compose, mediciones y persistencia.

- **Verificado:** bloque de recursos 0eba3f4: Ruff, 76 pruebas backend/contrato,
  nueve mutaciones detectadas, Flutter analyze/seis pruebas/dos mutaciones/builds,
  flujo real en los tres jobs del run 37140687994. La cuota de Docker todavía
  requiere su propia medición; los runners sin límites no acreditan esa cuota.

- **Corregido:** el verificador Compose convertía HTTPMessage a dict y perdía
  la búsqueda de headers sin distinción de mayúsculas. Health respondía pero
  la comparación del hash fallaba. Se conserva HTTPMessage y se repite toda
  la ejecución; no se relaja la comprobación de revisión.

### Corrección de rendimiento bajo cuota

- **Corregido:** Compose d473b1f superó 60 s en la primera búsqueda de 1000
  filas. La consulta de imágenes repetía inicialización/conexiones por fila.
  ADR-0019 incorpora lectura en lote mediante servicio de Publicaciones.
- **Aceptado:** prueba MySQL con dos galerías/propietarios y 52 filas visibles,
  sin mezclas ni filas ocultas/heredadas y conexiones constantes. Una mutación
  reincorpora N consultas; debe ser detectada.
- **Corregido:** el verificador de rendimiento envía q (nombre del contrato),
  en lugar de texto. Los filtros de modalidad/estado/precios siguen activos.
- **Rechazado:** aumentar cuotas del laboratorio, importar un repository ajeno
  o retirar el objetivo de dos segundos para conseguir un resultado verde.
- **Verificación pendiente:** diez muestras reales tras la corrección,
  recreación de contenedores y detección de la nueva mutación.


## 2026-10-03 — continuación desde checkpoint fda3897

- **Herramienta:** ChatGPT/Codex; ejecución directa sobre el fork, sin acceso al clon Windows.
- **Aceptado:** verificar SHA/working tree, repetir backend del mismo SHA en MySQL CI, comparar artefactos/capturas y sincronizar C4, arc42 y aspectos con cuatro contextos, identidad real y OpenAPI v2.
- **Aceptado:** separar pytest/httpx existentes a requirements-dev; conservar runtime y Pillow 12.3.0, sin nuevas dependencias del producto. Textos de Inicio orientados a búsqueda/detalles/gestión.
- **Corregido:** Ruff ampliado a backend/scripts detectó espaciado de imports histórico y la ausencia de check=False explícito en subprocess del verificador Flutter. Se corrigieron y CI incorpora ese alcance.
- **Rechazado:** rehacer autenticación o catálogo sin defecto demostrado, atribuir resultados de otro SHA al HEAD actual, presentar un 403 de acceso a SonarCloud como gate aprobado, cambiar ADR aceptados o efectuar despliegue en esta fase.
- **Verificación:** backend fda3897 relanzado: Ruff, 73+4 pruebas y diez mutaciones aprobadas; contrato/modularidad/erosión/propiedad ejecutados aquí con 15 pruebas aprobadas. MySQL local no arrancó por restricción de socket; no se sustituyó por mocks/SQLite. Gitleaks escanea historial de fase y working tree. Validación del nuevo HEAD se registra en docs/evidencias/auditoria-mvp-continuacion-2026-10-03.md.
- **Corregido:** Android 266a08d completó los nueve checks pero falló por SemanticsHandle al cerrar. Se limita UiAutomation al selector DocumentsUI, se espera recuperar los handles iniciales y el helper de campos espera hit-test. La ejecución fallida permanece documentada y se exige repetir CI.
- **Bloqueo comprobado:** el conector rechaza con 403 crear el PR oficial; SonarCloud del HEAD no puede declararse verde. No se efectuó despliegue ni merge.
- **Verificado:** 094eaaa aprobó cuatro workflows/seis jobs: Ruff backend/scripts, 73+4 pruebas, diez mutaciones backend, analyze, seis tests Flutter, dos mutaciones cliente y builds Web/APK debug. Chrome escritorio/móvil y Android API 35 completan nueve checks/19 capturas; Android registra semantics_handles_restored=true. Compose pasa persistencia, cuotas, EC-02 10/10 y EC-01 10/10.
- **Persistencia ante interrupción:** el entorno devolvió 409 environment_offline al descargar artefactos. Los cambios de cierre se reconstruyen contra 094eaaa mediante GitHub y se añade Gitleaks fijado por checksum y comprobación de checkout CI limpio. El status del scratch desconectado no se presenta como verificado.
- **Integración de trabajo remoto:** se conserva 7c73279 y sus mejoras del selector. Se pausa UiAutomation cuando CampusMarket es la actividad resumida para conservar la liberación demostrada en 094eaaa, sin retirar el manejo nativo de DocumentsUI/ANR. El flujo combinado requiere CI del HEAD final.


## 2026-10-04 — verificación y publicación pública con Codex

- **Herramienta:** ChatGPT/Codex, GitHub Actions y navegador público.
- **Propósito:** terminar despliegue y contrastar evidencia con guía oficial y contrato.
- **Aceptado:** reutilizar ADR-0016/0018 sin modificar archivos ADR; publicar Flutter en Pages desde c38e0cf, con API Dokploy y marcador de revisión; registrar 23 pruebas HTTP y observación de Inicio/detalle.
- **Corregido:** frontend Pages todavía apuntaba a Azure; se recompiló con API https://campusmarket.iscoutb.dev.
- **Rechazado:** usar terminal para evadir permiso Docker denegado, eliminar volúmenes, declarar persistencia por un redeploy que no recrea contenedores, presentar diez muestras internas como EC-01 extremo a extremo o equiparar Quality Gate automático con scanner CI.
- **Verificación:** [evidencia pública](./evidencias/despliegue-publico-mvp-2026-10-04.md) cita SHA, cuatro runs CI, publicación Pages, respuestas HTTP, guía y límites. Persistencia pública, administración pública y scanner permanecen pendientes. No se alteraron ADR existentes.

## S9 — criterio y verificacion del catalogo

Fecha de revisión documental: 3 de octubre de 2026, America/Bogota.
Herramienta: ChatGPT/Codex. Propósito: hacer navegable la evidencia S9 y contrastar
el alcance literal de la ficha con el estado oficial `7856416795bb4accdf9d05e01adb470654875e56`.

| Propuesta revisada | Resultado | Motivo técnico / destino comprobable |
|---|---|---|
| Centrar la entrega S9 en Catálogo y composición de imágenes | Aceptada | Porción real del periodo; [cadena y matriz](./evidencias/evidencia-s9-2026-10-01.md) |
| Presentar despliegue como demostración suficiente de S9 | Rechazada | No prueba erosión, criterio sobre IA ni detección del defecto |
| Reducir ADR fusionando archivos ya aceptados | Rechazada | CONTRATO §4 y hallazgo previo; [índice agrupado](./arc42/09-decisiones.md) conserva registros |
| Reutilizar ASP-10 para identidad y operación | Corregida | ASP-10 queda operación; ASP-12 identifica sesiones de manera consistente |
| «Sin nuevas dependencias» para todo S9 | Corregida | Era cierto solo en Catálogo inicial; [auditoría ampliada](./evidencias/auditoria-s9-dependencias-secretos-2026-10-01.md) verifica cuatro incorporaciones del periodo |
| Marcar EC-01 público cerrado por CI loopback | Rechazada | Clientes, dataset y red diferentes; se preserva el contraste y límite |
| Declarar todo verde por cuatro workflows success | Rechazada | CONTRATO §8 también exige scanner CI y Quality Gate asociado; falta scanner |
| Atribuir las cifras de fda3897 al último commit | Rechazada | Cada medición pertenece a su SHA; CI actual acredita el gate y guarda sus propias muestras |
| Cambiar código funcional para ampliar texto | Rechazada | No hay defecto nuevo demostrado; esta rama corrige documentación y enlaces |

Se releen y conservan las decisiones técnicas ya registradas: lectura de
Publicaciones por su service aceptada; N+1 corregido a lote; SQL/repository ajeno,
aumentar la cuota y retirar el umbral rechazados por modularidad y rendimiento.
La verificación del 4 de octubre a las 03:27 UTC confirma recreación API y foto
persistente; no acredita recreación pública de MySQL ni moderación pública.
El equipo debe revisar y entender este complemento antes de integrarlo;
la asistencia de IA no constituye aceptación automática por todos sus miembros.

## S10 - Segundo corte: consumidor incompatible con el contrato v2 (2026-10-11)

Responsable de la solicitud: Nilver García Pimentel. Herramienta: ChatGPT/Codex.
Se añade este registro conservando íntegro el contenido anterior y los ADR aceptados.

- **Para qué:** seleccionar un solo escenario operativo, ejecutar un experimento nuevo sobre la API pública y documentar hipótesis, línea base, decisión, resultados y trazabilidad.
- **Aceptado y verificado:** S10-CT-01, consumidor que envía `sale` donde OpenAPI v2 admite `venta`/`alquiler`; tres repeticiones de línea base, incompatibilidad y adaptación explícita del consumidor. La corrida conservó 58 respuestas HTTP: 15/15 válidas con 200, 15/15 incompatibles con 422, 15/15 adaptadas con 200; nueve health 200/ok y 58/58 request IDs correlacionados. Se conservaron plan previo, script de la corrida, JSONL y resumen calculado.
- **Aceptado y verificado:** ADR-0020 nuevo, pruebas que comprueban rechazo antes del servicio y logs correlacionados, adendas arc42/C4 y workflow adicional. Pruebas locales: 8 passed; Ruff sobre backend/scripts: sin hallazgos. Estos resultados locales no sustituyen la ejecución posterior de CI.
- **Rechazado y motivo:** inducir fallo de MySQL sin control de contenedores del despliegue; reutilizar N+1/S9 como reto nuevo; ampliar automáticamente el enum del proveedor; modificar ADR aceptados; presentar un PDF cuando la revisión docente lo excluye; inventar resultados, logs privados, recuperación de MySQL o una nota de sustentación.
- **Límites:** un consumidor serial y un catálogo público pequeño; métricas del observador HTTP, no CPU/memoria ni tiempo exclusivo del backend. Sonar en CI y deudas históricas de ADR no se declaran corregidos.

Registro detallado: [complemento IA S10](ia-s10.md).
Cadena revisable: [evidencia S10](evidencias/evidencia-s10-corte2-2026-10-11.md), [ADR-0020](adr/0020-preservar-contrato-v2-y-adaptar-consumidor-incompatible.md), [pruebas](../backend/tests/test_s10_contrato_cliente.py), [corrida pública](evidencias/s10/ejecucion-20261012T0419Z/).

## S11 — Fallos parciales y decisión de extracción (2026-10-18)

Fecha de revisión: 18 de octubre de 2026 (America/Bogota). Herramienta: ChatGPT, con verificación humana de la integración y contrastación mediante GitHub. Se conserva el registro cronológico de S1–S10.

| Propuesta revisada | Resultado | Motivo técnico / destino comprobable |
|---|---|---|
| Analizar `POST /publicaciones` en Flutter → FastAPI → MySQL como integración principal | Aceptada | [Evidencia S11 §1–2](evidencias/evidencia-s11-2026-10-18.md) y [router real](../backend/app/publicaciones/router.py) |
| Tratar no respuesta, respuesta tardía y solicitudes repetidas como fallos parciales distintos | Aceptada | Tabla F11-01–F11-03, mitigaciones actuales y pendientes, sin atribuir pruebas no realizadas |
| Diseñar `Idempotency-Key` transaccional por usuario/operación | Aceptada como diseño, **no implementada** | [Evidencia S11 §3](evidencias/evidencia-s11-2026-10-18.md); T1–T7 pendientes |
| Declarar protección contra duplicados ya implementada | Rechazada | Ni router ni tabla SQL contienen aún clave/índice de deduplicación |
| Reintentar automáticamente `POST` tras timeout | Rechazada | Puede crear publicaciones duplicadas; primero se necesita idempotencia y recuperación del estado |
| Extraer Catálogo como microservicio para evidenciar S11 | Rechazada | Introduce frontera remota sin escalamiento independiente demostrado; [ADR-0021](adr/0021-mantener-catalogo-en-el-monolito-modular.md) adopta **no extraer** |
| Presentar CI verde como prueba de fallos parciales inyectados o de despliegue nuevo | Rechazada | CI comprueba regresión general; las pruebas de resiliencia y paridad de SHA público siguen pendientes |
| Consolidar registro S11 en arc42, aspectos y evidencia existente | Aceptada y fusionada | [PR #56](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/pull/56) y [PR #58](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/pull/58) |

**Comprobación por revisión:** [`master` f2e9497](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/commit/f2e94972f0327cd11f2c956fd894f66d779cede6) obtuvo ocho comprobaciones satisfactorias, incluida Android tras el [PR #57](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/pull/57). Estas comprobaciones no sustituyen T1–T7 ni acreditan desplegar esa revisión.

**Cadena revisable:** [evidencia S11](evidencias/evidencia-s11-2026-10-18.md) → [ADR-0021](adr/0021-mantener-catalogo-en-el-monolito-modular.md) → [arc42 §11](arc42/11-riesgos-y-deuda-tecnica.md) → [aspectos ASP-13/14](aspectos.md) → [código Flutter y FastAPI](../backend/app/publicaciones/) → CI. La evaluación oficial corresponde al docente.


## Evidencia S12 — Arquitecturas de datos y eventos (2026-10-25)

| Fecha | Herramienta | Uso realizado | Verificación del equipo | Qué se rechazó y por qué |
|---|---|---|---|---|
| 25/10/2026 | ChatGPT + conector GitHub | Ayuda a contrastar la ficha oficial S12/CONTRATO con los repositorios de Publicaciones, Catálogo y Administración; redactar la tabla operación→garantía, ADR-0022 y política de caché. | Revisión estática de `create_publication`, `buscar_publicaciones`, `create_report`, `open_review` y de la topología C4; la aceptación funcional y CI del commit final quedan por verificar. | Se rechazó introducir Redis o Kafka solo por apariencia: el MVP no demuestra necesidad y sería inconsistente con la topología. Se rechazó afirmar consistencia distribuida fuerte entre SQL y archivos. |
| 25/10/2026 | ChatGPT | Preparación de evidencias, enlaces y ampliaciones de arc42/C4/aspectos sin borrar el trabajo histórico. | Requiere revisión humana de enlaces, pruebas y hash `master` elegible al cierre de SAVIO. | Se rechazó modificar ADR aceptados o presentar el prototipo del taller como broker productivo; el taller se evalúa aparte. |


### Verificación correctiva S12 — Android (25/10/2026)

| Fecha | Herramienta | Uso realizado | Verificación del equipo | Qué se rechazó y por qué |
|---|---|---|---|---|
| 25/10/2026 | ChatGPT / GitHub Actions | Se investigó el fallo del [job Android PR #61](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/40249803106/job/121339008849): la aserción `Portada usa publicación existente`. Se modificó la transición de navegación a Inicio en `frontend/campusmarket/lib/app/marketplace_shell.dart` para recargar publicaciones al regresar desde otras vistas. | El error original y su ubicación se verificaron en logs; la hipótesis de datos obsoletos se basa en inspección del código. **La corrección NO está validada hasta obtener un nuevo run exitoso.** | Se rechazó suprimir la aserción, declarar el fallo intermitente sin prueba o aumentar tiempos de espera arbitrariamente; ninguna opción corrige la frescura de la portada. |


## S12 — Auditoría correctiva posterior al PR #61 (25/10/2026)

| Fecha | Herramienta | Uso realizado | Verificación del equipo | Qué se rechazó y por qué |
|---|---|---|---|---|
| 25/10/2026 | ChatGPT + GitHub | Contraste de la evidencia S12 fusionada con nueve criterios y contrato transversal; elaboración de adenda nueva de cierre por hash y corrección de nota obsoleta del diagrama C4 L2. | Se comprobó el merge original `14ab852` y el éxito del reintento S10; el hash de la corrección y otros enlaces CI requieren corroboración tras fusionar. | Se rechazó reescribir el ADR aceptado, atribuir pruebas específicas de caché inexistentes o declarar 5/5 sin resultado docente. Se rechazó borrar el fallo histórico S10: se conserva junto al reintento exitoso. |


## Corrección de verificabilidad Android posterior a S12 — 25/10/2026

| Herramienta | Evidencia del error | Hipótesis y modificación | Estado y alternativas rechazadas |
|---|---|---|---|
| ChatGPT + GitHub Actions | [Job 121353733617](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/40254634092/job/121353733617) falla en `mvp_flow_test.dart`: `Portada usa publicación existente` a pesar de la recarga de Inicio. | `InicioPage` sitúa la cuadrícula debajo de un hero largo y emplea `GridView.builder` en una pantalla móvil. Se ajustó el test para desplazar el `Scrollable` de Inicio hasta la tarjeta y validar que el texto real sea alcanzable. | Hipótesis pendiente de CI: no se afirma que el error esté resuelto hasta un run verde. No se alteran backend, timeout, datos ni aserción sustantiva; el error de S10 público es independiente. |


### Diagnóstico mediante artefacto real Android — 25/10/2026 (PR #63)

- Evidencia: [run 40260246299](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/40260246299), artefacto `12624208957` (capturas `android-fallo.png`, `android-1-inicio-vacio.png`, `backend.log`, `resultado.json` y estado ADB).
- Hechos comprobados: API `/catalogo` respondió 200 y devolvió el objeto requerido antes de la aserción; inmediatamente al cargar Inicio el servidor CI devolvió **dos 503** acompañados de `Exceeded concurrency limit`. El workflow configuraba `uvicorn --limit-concurrency 6`, también compartido con solicitudes de imágenes. La captura de fallo muestra el hero de Inicio sin publicación destacada; la excepción fue `Inicio terminó de cargar publicaciones`.
- Corrección acotada: elevar el límite artificial del backend **solo en E2E** de 6 a 40 conexiones, sin modificar reglas de negocio, y desplazar primero al encabezado antes de comprobar el `LayoutBuilder` bajo el viewport Android. Se mantiene la aserción de publicación realmente visible. El límite aumentado no demuestra por sí solo disponibilidad bajo carga ni reemplaza pruebas de desempeño.
- Validación pendiente: no afirmar éxito sin CI verde del commit correctivo. Se rechazó borrar la prueba, simular publicaciones o reemplazar el 503 por una respuesta ficticia.


## Taller aplicado S12 — Mensajes y consistencia (2026-10-25)

| Herramienta | Uso | Aceptado y verificable | Rechazado y motivo |
|---|---|---|---|
| ChatGPT + GitHub | Diseñar simulador Python de `PublicacionCreada.v1`, JSON Schema, pruebas con `unittest`, ADR-0023 y workflow independiente | Aceptado como **prototipo aislado** con `message_id`, correlación, deduplicación transaccional SQLite, reintento y DLQ; verificar run del commit final antes de afirmar éxito | Kafka/RabbitMQ en MVP sin caso de calidad medido: agrega operación innecesaria. No simular broker productivo. No eliminar pruebas previas ni sobrescribir ADR-0022. No declarar retardo real cuando backoff es tiempo lógico. |


### Adenda correctiva Taller S12 — backoff ejecutable

- Uso de ChatGPT/GitHub: revisión del requisito de reintentos y corrección aislada del simulador; adopción de `time.sleep` real por defecto, con inyección de función de espera en `unittest` para probar 2 y 4 segundos programados sin retrasar CI.
- Se aceptó preservar tres intentos, DLQ, deduplicación y trazas; se añadieron comprobaciones explícitas de argumentos del sleeper.
- Se rechazó conservar exclusivamente el log de espera lógica porque no demuestra aplicación de backoff, y también se rechazó insertar `sleep` obligatorio en todas las pruebas por ser innecesariamente lento. No se reescribieron ADR aceptados ni se modificó producción.


### Índice de cierre documental — Taller S12 (sin validación anticipada)

- Cambio incremental: [README](../README.md), [S12-MSG-01 / S12-MSG-02 en aspectos](aspectos.md), [evidencia](evidencias/taller-mensajes-s12-2026-10-25.md), [contrato JSON](../contracts/messages/publicacion-creada-v1.schema.json), [test](../backend/tests/test_taller_mensajes_s12.py), [workflow](../.github/workflows/s12-taller-mensajes.yml).
- Resultado previo y verificable: [CI taller del PR #64, run 40265066306](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/40265066306) fue exitoso **antes** de esta corrección. No sustituye el run nuevo.
- Cierre pendiente: URL de PR correctivo, SHA del merge y CI específico del último `master`. Se evita presentar estados de una rama anterior como validación del nuevo código.


## GHCR — Publicación, ensayo aislado y cierre documental (2026-10-30)

Este es el registro canónico de IA para GHCR. Se consolidan los dos anexos
anteriores sin modificar los registros S1–S12 que preceden a esta sección.
Las decisiones corresponden al equipo; la IA propuso contenido y comandos.
La columna de verificación distingue hechos comprobados de los límites de
cada etapa. La revisión humana de este cambio corresponde al PR documental.

### Publicación y auditoría previas

Las seis entradas siguientes proceden del anexo inicial. Se conserva su
alcance temporal: publicar y verificar una imagen no acreditaba desplegarla.

| Fecha | Herramienta | Uso realizado | Verificación del equipo | Qué se rechazó y por qué |
|---|---|---|---|---|
| 29–30/10/2026 | ChatGPT | Diagnóstico de discrepancia entre versión configurada y commits; propuesta de cadena commit → imagen probada → GHCR | Se compararon commits, Dockerfile, Compose y resultados visibles de GitHub Actions | No se afirmó que el encabezado público fuera incorrecto: el cliente de auditoría obtuvo 403 y no pudo comprobarlo |
| 30/10/2026 | ChatGPT | Propuesta e iteraciones de workflows de exportación y publicación con comprobaciones de SHA, checks y origen | Se comprobaron YAML, nombres reales de checks de GitHub y se ejecutó ensayo `publicar: false` en [run 41025785578](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41025785578) | Se descartó publicar sin comprobar identidad, usar nombres supuestos de checks y confundir el SHA del merge con el del artefacto |
| 30/10/2026 | ChatGPT | Propuesta de publicación manual y verificación de digest remoto | [Run 41026286264](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41026286264), con verificación de identidad de imagen y revisión | No se dio por desplegada la imagen por el simple hecho de publicar en GHCR |
| 30/10/2026 | ChatGPT | Propuesta de Compose alternativo y plan de despliegue/rollback | Se comparó la estructura con Compose de laboratorio y se validó localmente con `docker compose config --quiet` | No se sustituyó el Compose activo ni se realizaron cambios sobre MySQL o sus volúmenes |
| 30/10/2026 | ChatGPT Work | Auditoría exclusivamente de lectura del servicio Dokploy, autodeploy, contenedores, nombres de volúmenes y limitaciones de acceso | Informes de Work y consulta visual del panel; API y DB reportados saludables | No se inventaron montajes RW, credenciales GHCR, respaldos recuperables ni una imagen anterior efectiva ante inspectores inaccesibles |
| 30/10/2026 | ChatGPT / equipo | Evaluación de alternativas: migrar de inmediato o preservar producción y documentar bloqueantes | [ADR-0024](adr/0024-publicar-imagen-verificada-y-condicionar-promocion.md), [decisión operativa](operacion/decision-migracion-ghcr.md) | Se rechazó la migración inmediata sin autenticación, respaldo, imagen para rollback ni verificación de montajes |

Límites conservados del registro inicial: los resultados procedían de Actions,
Compose local y auditorías de lectura; el análisis sintáctico de YAML no
sustituía ejecutar el pipeline. El `device offline` de Android y el PNG inválido
se contrastaron con logs y un reintento exitoso del
[run 41029797678](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41029797678),
sin atribuirlos a una reparación de código o al despliegue GHCR. No se publicaron
contraseñas MySQL, PAT ni secretos. Acceso Internal desde Dokploy, respaldo
restaurable, migración y rollback continuaban sin probarse; el ensayo posterior
en Actions no acredita esas condiciones del servidor.

### Preparación del ensayo: propuestas y correcciones históricas

Estas decisiones se tomaron antes de ejecutar el ensayo. Los futuros y estados
pendientes en sus verificaciones describen esa etapa; el cierre real se
registra después. La aceptación de «usar digest publicado» no oculta la
transcripción incorrecta que se detectó y corrigió posteriormente.

| Fecha | Herramienta | Uso realizado | Verificación del equipo | Qué se rechazó y por qué |
|---|---|---|---|---|
| 30/10/2026 | ChatGPT + conector GitHub | Aceptada: Crear rama del fork desde upstream actualizado | Ambos master coinciden en `0971b2b0c229c25d4ebefd5c90bf1b8625656932`; se usa ese commit, no una base personal divergente | No consta otro rechazo en esta entrada; se conserva el límite de verificación. |
| 30/10/2026 | ChatGPT + conector GitHub | Aceptada: Workflow manual y verificador separado, sin cambiar workflows anteriores | Permisos contents/packages de lectura; dependencias existentes de la imagen y Python estandar en el runner | No consta otro rechazo en esta entrada; se conserva el límite de verificación. |
| 30/10/2026 | ChatGPT + conector GitHub | Aceptada: Usar digest publicado y SHA fuente independiente de GITHUB_SHA | Preflight rechaza otro digest; OCI, archivo, encabezado e Image ID se comprobaran en el run real | No consta otro rechazo en esta entrada; se conserva el límite de verificación. |
| 30/10/2026 | ChatGPT + conector GitHub | Aceptada para el ensayo: Crear MySQL y uploads sinteticos; probar fallo de DB y recreacion | Solo proyecto unico del runner alojado, sin conexiones Docker remotas ni endpoints publicos; ejecucion real pendiente | No consta otro rechazo en esta entrada; se conserva el límite de verificación. |
| 30/10/2026 | ChatGPT + conector GitHub | Corregida: Definir runner.temp en env del job | Actionlint lo rechazo por contexto no permitido. Se genera DOCKER_CONFIG mediante GITHUB_ENV en un paso del runner | Definir runner.temp en env del job: Actionlint lo rechazo por contexto no permitido. Se genera DOCKER_CONFIG mediante GITHUB_ENV en un paso del runner |
| 30/10/2026 | ChatGPT + conector GitHub | Corregida: Capturar cualquier Exception para ocultar stderr | Ruff rechazo la captura ciega; se enumeran errores esperados y solo se publican mensajes propios/tipos, nunca stdout/stderr completos | Capturar cualquier Exception para ocultar stderr: Ruff rechazo la captura ciega; se enumeran errores esperados y solo se publican mensajes propios/tipos, nunca stdout/stderr completos |
| 30/10/2026 | ChatGPT + conector GitHub | Rechazada: Dar CUMPLE a persistencia o cleanup por tener codigo | Las pruebas unitarias de control no se presentan como Docker real. Matriz previa PARCIAL/BLOQUEADO; matriz del run se genera con hechos medidos | Dar CUMPLE a persistencia o cleanup por tener codigo: Las pruebas unitarias de control no se presentan como Docker real. Matriz previa PARCIAL/BLOQUEADO; matriz del run se genera con hechos medidos |
| 30/10/2026 | ChatGPT + conector GitHub | Rechazada: Ejecutar el nuevo workflow desde la rama del fork como si estuviera registrado | workflow_dispatch requiere presencia en rama predeterminada; el job requiere contexto oficial. No se altera master ni se hace merge para sortearlo | Ejecutar el nuevo workflow desde la rama del fork como si estuviera registrado: workflow_dispatch requiere presencia en rama predeterminada; el job requiere contexto oficial. No se altera master ni se hace merge para sortearlo |
| 30/10/2026 | ChatGPT + conector GitHub | Rechazada: Usar pull_request_target, PAT o ampliar permisos para forzar una prueba | No son necesarios ni estan autorizados; un 403 se documenta como bloqueo | Usar pull_request_target, PAT o ampliar permisos para forzar una prueba: No son necesarios ni estan autorizados; un 403 se documenta como bloqueo |
| 30/10/2026 | ChatGPT + conector GitHub | Rechazada: Copiar produccion a development o tocar recursos del laboratorio | El ensayo se prepara en Actions. No modifica Dokploy ni consume la cuota compartida del equipo | Copiar produccion a development o tocar recursos del laboratorio: El ensayo se prepara en Actions. No modifica Dokploy ni consume la cuota compartida del equipo |

### Evidencia, incidente del digest y cierre

| Fecha | Herramienta | Uso realizado | Verificación del equipo | Qué se rechazó y por qué |
|---|---|---|---|---|
| 30/10/2026 | ChatGPT + conector GitHub | Validación estática inicial del ensayo y entrega desde el fork. | Compose standalone 5.6.1, Actionlint 1.7.12 sin ShellCheck, Ruff 0.16.9, Gitleaks 8.30.1, sintaxis Python/Bash, 14 casos negativos y cuatro pruebas unitarias de control sin daemon. El entorno de implementación no tenía Docker Engine. | Se rechazó presentar esas validaciones locales como descarga GHCR, arranque, persistencia o cleanup real; el run anterior de publicación tampoco los sustituía. |
| 30/10/2026 | ChatGPT + conector GitHub | Rama `ci/ensayo-ghcr-20261030-0971b2b` desde `0971b2b0c229c25d4ebefd5c90bf1b8625656932`; implementación `80152f17d175409f0d171ac39e5f96108d4ee4ff`. | Inicialmente la integración devolvió 403, `Resource not accessible by integration`, al crear el PR; no había un PR abierto de esa rama. La incorporación posterior se acredita en [PR #73](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/pull/73), merge `1068764ba84095b93fe0d643cf401503131473ec`. | No ampliar permisos, fingir un PR/run, alterar master directamente ni eludir el registro de workflow_dispatch en la rama predeterminada. |
| 30/10/2026 | ChatGPT + conector GitHub | Error detectado y corregido con apoyo de IA: se conservó un digest proporcionado sin contrastarlo con el log original de publicación. | [Publicador 41026286264](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41026286264) y [ensayo fallido 41046842362](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41046842362), intentos 1 y 2: diferencias hex 18 (`c → e`) y 24 (`d → 0`). La rama `fix/diagnostico-pull-ghcr-20261030-1068764` partió de `1068764...`; corrigió Compose, verificador y cinco referencias documentales, manteniendo el SHA fuente `2154e7880e5111537256206a29f4f4c29a8c86c4`. [PR #74](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/pull/74), merge `669368894d583406c7610e8c735f686c02931de3`. | No ocultar la transcripción incorrecta ni atribuir el éxito del publicador a los intentos fallidos del ensayo; no reconstruir ni republicar otra imagen. |
| 30/10/2026 | ChatGPT + conector GitHub | Clasificación segura del error de pull por lista cerrada de categorías y exit real; UNKNOWN conserva un fallo no reconocido. | Cinco pruebas unitarias, incluidos 20 mensajes de clasificación, supresión de stdout/stderr privados, timeout, fallo ordinario y éxito; Ruff, Compose config y Gitleaks locales. Son controles sin descargar la imagen. | Se rechazó imprimir/archivar stderr/stdout o redactarlos parcialmente por riesgo de exponer secretos; se conservaron solo categoría y exit_code. |
| 30/10/2026 | ChatGPT + conector GitHub | Contraste de permisos declarados, login y límite del diagnóstico antiguo. | Los dos intentos fallidos acreditaron login y packages: read; el usuario comprobó Actions access Admin. El stderr y el exit de Docker no quedaron preservados, por lo que no se atribuyó un 403/404 concreto. | Se rechazó declarar un fallo de permisos sin evidencia, añadir PAT, cambiar visibilidad/runner/workflow/permisos/credenciales/Dokploy o repetir automáticamente el ensayo. |
| 30/10/2026 | ChatGPT + conector GitHub | Comprobación del ensayo real exitoso de la imagen corregida, sin reconstruir el backend. | [Run 41051624793](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41051624793), commit `669368894d583406c7610e8c735f686c02931de3`: job/logs y ZIP `ensayo-ghcr-41051624793-1`, ID `12975600016`, contrastados con SHA-256 `5e45714e318b78f50d08b651aa149cc27fd198082996b65d748f2d3b3bd0daad`; resultado `passed: true`, 10/10 CUMPLE. MySQL real 8.4.13, SQL/HTTP, identidad, recuperación, persistencia SQL/PNG y cleanup vacío. [Detalles](operacion/ensayo-ghcr.md). | No extrapolar el éxito del runner a acceso GHCR desde Dokploy, respaldos productivos, HTTPS, migración o rollback. No atribuir el SHA documental a la imagen fuente. |
| 30/10/2026 | ChatGPT + conector GitHub | Consolidación de los dos anexos en este archivo canónico; actualización del informe y de la matriz GHCR existente. | Rama documental desde `ISCOUTB/master` `6693688...`; conservación byte por byte del contenido previo de este registro, enlaces comprobados, evidencia del ZIP contrastada y corrección mecánica UTF-8 de ADR-0024 y trazabilidad. | Se rechazó crear otro documento/matriz o un tercer anexo de IA, reescribir ADR aceptados, cambiar resultados S1–S12, modificar código/Compose/workflows/producción o ejecutar otro ensayo. |

### Procedencia y referencias del registro consolidado

Los anexos retirados siguen disponibles en el historial anterior a esta
consolidación: [registro de publicación](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/blob/669368894d583406c7610e8c735f686c02931de3/docs/evidencias/uso-ia-ghcr-2026-10-30.md)
y [registro del ensayo](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/blob/669368894d583406c7610e8c735f686c02931de3/docs/evidencias/uso-ia-ensayo-ghcr-2026-10-30.md).
Esas referencias inmutables permiten auditar el traslado, no mantener registros
activos separados. El objetivo, la configuración y el resultado operativo
permanecen en el [informe del ensayo](operacion/ensayo-ghcr.md); la cadena
arquitectónica permanece en la [matriz existente](evidencias/trazabilidad-ghcr-2026-10-30.md)
y la publicación en la [evidencia de cierre](operacion/evidencia-ghcr-cierre.md).

## Fase 2 — frontend institucional preparado y probado en CI — 2026-10-30

Este registro amplía el archivo canónico después de verificar la implementación. La revisión humana y la
autorización de publicación siguen pendientes; «Verificación del equipo» distingue las comprobaciones
automáticas realizadas con apoyo de IA de una aprobación que no se ha recibido.

| Fecha | Herramienta | Uso realizado | Verificación del equipo | Qué se rechazó y por qué |
|---|---|---|---|---|
| 30/10/2026 | ChatGPT / Codex y conector GitHub | Lectura de `ISCOUTB/master` `40be256...` (PR #75 fusionado), guía §1–3/5, políticas, feedback, URL Flutter, Dockerfiles y workflows; inspección de Dokploy solo lectura. Comparación de Nginx, routing externo y estáticos en FastAPI. | Límites existentes suman 256M + 256M; UI confirmó dos contenedores healthy y routing HTTPS `/` → api:8000. Monitoring mostró ceros no interpretables. La [decisión propuesta](adr/0025-servir-flutter-precompilado-desde-fastapi.md) queda pendiente de aceptación humana. | Se rechazó añadir Nginx sobre la cuota, reducir límites sin medición, suponer DNS externo autorizado, presentar redirección como sitio institucional o confundir ceros de Monitoring con memoria libre. |
| 30/10/2026 | ChatGPT / Codex, Python y GitHub Actions | Implementación mínima de StaticFiles opcional en `/app/`, API Web del mismo origen, copia del build en Docker y workflow aislado; sin modificar Compose ni workflows anteriores. | [Run 41094945507](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41094945507), fuente `a9b6709a67f8036346acb64b9c2b9849ee355cf2`: 15 pruebas backend, análisis Flutter y 7 pruebas Flutter, compilación release, Chrome con UI real, MySQL 8.4.13 y 10/10 criterios. La descarga local del SDK recibió 403; se verificó la compilación real en el runner. | Se rechazó sustituir la raíz API, usar HTML de prueba como aceptación, compilar Flutter en Dokploy, añadir dependencias de runtime, desactivar seguridad de Chrome o atribuir resultados de la fuente GHCR antigua a este cambio. |
| 30/10/2026 | ChatGPT / Codex y logs CI | Corrección de fallos encontrados durante la implementación y refuerzo de la prueba OpenAPI. | Run 41092034860 detectó comparación de cabecera sensible a mayúsculas en el verificador; se normalizó. Runs 41092575249/41093459043 detectaron assets 503; se conservaron paths/status sin datos sensibles y se cerraron conexiones de estáticos bajo concurrencia 6. Runs 41094232876 y 41094945507 pasaron. Se invalidó la caché OpenAPI en el test para comparar el esquema tras montar la Web. | Se rechazó ocultar los fallos, aceptar UI con assets 503, aumentar concurrencia/recursos para taparlos o considerar suficiente una prueba que reutilizaba el esquema cacheado. Los errores y sus correcciones quedan vinculados a sus runs. |
| 30/10/2026 | ChatGPT / Codex, Docker en runner y verificación Python del artefacto descargado | Medición cgroup, comprobación OCI/REVISION/SHA Web, exportación y hashes; limpieza por proyecto efímero exclusivo con SQL/fotos sintéticos. | Run final: API 195796992 bytes, MySQL 185237504 bytes, límites 268435456 bytes y 500000000 NanoCpus cada uno, sin OOM/reinicios; inventarios vacíos y credenciales efímeras retiradas. ZIP, tar e identidad de configuración contrastados; [evidencia](evidencias/despliegue-publico-mvp-2026-10-04.md#fase-2--frontend-institucional-candidato-probado-en-ci--2026-10-30). | Se rechazó confundir imagen ID, checksum del tar y digest GHCR; publicar/reconstruir otra imagen, consultar usuarios reales o extrapolar una carga sintética a producción. No se publicaron imágenes ni se alteró Dokploy. |
| 30/10/2026 | ChatGPT / Codex y Git | Actualización de README, arc42, fila ASP-15 en la tabla existente y evidencia pública canónica; nuevo ADR por la decisión real de hosting, sin reescribir los aceptados. | Se preservan los registros previos de IA y evidencia y las filas históricas; se validan UTF-8, enlaces locales, cinco/ocho columnas y alcance del diff. El commit documental posterior no se presenta como fuente del run. | Se rechazó crear anexos paralelos de IA o otra matriz de aspectos, modificar S1–S12, anunciar frontend institucional ya publicado o fusionar con autodeploy activo. Se mantienen explícitos los bloqueantes de respaldo, montajes, registro y rollback. |


## Mecanismo de despliegue Web seguro — 2026-10-30

| Fecha | Herramienta | Uso realizado | Verificación del equipo | Qué se rechazó y por qué |
|---|---|---|---|---|
| 30/10/2026 | Codex, conector GitHub, Docker Compose y Actions | Rama de trabajo del fork desde `fd7a3cc…`; digest Flutter en Compose alternativo, override mínimo, preflight de solo lectura y plan de rollback exclusivo API. | [Commit 61a9171](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/commit/61a9171a6fff1ebfd53b869fc1b37aeb7d405461), [run 41133683253](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41133683253): 14 pruebas en runner, siete criterios operativos; artefacto descargado y hash contrastado. Dump/PNG sintéticos restaurados en otro proyecto; MySQL sin reemplazo/reinicio al promover y revertir API. 21 regresiones locales, Ruff, Actionlint y Gitleaks. Documentación actualizada después del éxito del ensayo. | No reconstruir/republicar el candidato, repetir los seis workflows previos, contactar al docente, escribir en upstream ni operar Dokploy. El rollback con el mismo Image ID no demuestra compatibilidad con la versión productiva desconocida; backups, montajes, acceso desde servidor e imagen previa siguen bloqueando la publicación. |
