# Aspectos del proyecto - CampusMarket

Este documento mantiene la trazabilidad de los aspectos de CampusMarket desde
los requisitos y decisiones arquitectónicas hasta su implementación y evidencia
verificable.

La cadena general de trazabilidad utilizada es:

**Aspecto → Requisito → C4 → ADR → Código → Pruebas → Evidencia**

A partir de S6, la trazabilidad de dominio se complementa con:

**Aspecto → Contexto delimitado → Propietario del dato → C4 Nivel 3 → Código → Auditoría → Prueba automática**

A partir de S7, la trazabilidad de integración incorpora además:

**Aspecto → Contrato OpenAPI → Proveedor FastAPI → Prueba de contrato**

La evolución de persistencia se registra mediante:

**Observación docente → ADR-0004 → C4 → Código → MySQL → Pruebas**

---

## Matriz general de trazabilidad

| ID | Aspecto | Requisito | C4 | ADR | Código | Pruebas | Evidencia |
|---|---|---|---|---|---|---|---|
| ASP-01 | Consulta y búsqueda de productos | [EC-01](./arc42/10-escenarios-de-calidad.md#ec-01---consulta-de-productos) | [C4 L2](./c4/02-contenedores.md) / [C4 L3](./c4/03-componentes-backend.md) | [ADR-0009](./adr/0009-materializar-catalogo-sin-romper-fronteras.md) / [ADR-0019](./adr/0019-consultar-imagenes-en-lote-a-traves-de-publicaciones.md) | [router Catálogo](../backend/app/catalogo/router.py), [service Catálogo](../backend/app/catalogo/service.py), [service Publicaciones](../backend/app/publicaciones/service.py) | [Funcionales y conexiones](../backend/tests/test_catalogo.py), [erosión](../backend/tests/test_erosion_s9.py), [propiedad](../backend/tests/test_propiedad_datos.py), [mutaciones](../scripts/verificar_mutaciones_mvp.py), [medición real](../scripts/verificar_compose_mvp.py) | [Cadena y matriz S9](./evidencias/evidencia-s9-2026-10-01.md#16-lectura-de-cierre-s9--trazabilidad-vigente-al-3-de-octubre-de-2026), [CI backend](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/37173110650), [CI Compose](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/37173110759) |
| ASP-02 | Gestión segura de publicaciones | [EC-02 - Protección de publicaciones](./arc42/10-escenarios-de-calidad.md#ec-02---protección-de-publicaciones) | [C4 Nivel 1](./c4/01-contexto.md) / [C4 Nivel 3](./c4/03-componentes-backend.md) | [ADR-0012](./adr/0012-autenticar-con-sesiones-opacas-revocables.md) | [`backend/app/publicaciones/`](../backend/app/publicaciones/) | [`test_gestion_publicaciones.py`](../backend/tests/test_gestion_publicaciones.py) | [EC-02, sesiones y evidencia por hash](./evidencias/auditoria-mvp-continuacion-2026-10-03.md) |
| ASP-03 | Evolución de la gestión de productos | [EC-03 - Modificación del sistema](./arc42/10-escenarios-de-calidad.md#ec-03---modificación-del-sistema) | [C4 Nivel 2](./c4/02-contenedores.md) / [C4 Nivel 3](./c4/03-componentes-backend.md) | [ADR-0001 - Monolito modular](./adr/0001-usar-monolito-modular.md) | [`backend/app/publicaciones/`](../backend/app/publicaciones/) | [`test_publicaciones_vertical.py`](../backend/tests/test_publicaciones_vertical.py) | Evidencia S3/S4 y profundización modular S6 |
| ASP-04 | Recuperación del prototipo | [EC-04 - Recuperación del prototipo](./arc42/10-escenarios-de-calidad.md#ec-04---recuperación-del-prototipo) | [C4 Nivel 1](./c4/01-contexto.md) | [ADR-0001](./adr/0001-usar-monolito-modular.md) | [`scripts/run_s4.ps1`](../scripts/run_s4.ps1) | [`test_health.py`](../backend/tests/test_health.py) | [Evidencia de arranque](./evidencias/arranque-un-comando-2026-09-04.md) |
| ASP-05 | Creación y gestión de publicaciones | [Alcance funcional](./arc42/ARC42.md#32-alcance-funcional) | [C4 Nivel 2](./c4/02-contenedores.md) / [C4 Nivel 3](./c4/03-componentes-backend.md) | [ADR-0001](./adr/0001-usar-monolito-modular.md) / [ADR-0004](./adr/0004-migrar-persistencia-a-mysql.md) | [`router.py`](../backend/app/publicaciones/router.py), [`service.py`](../backend/app/publicaciones/service.py), [`repository.py`](../backend/app/publicaciones/repository.py) | [`test_publicaciones_vertical.py`](../backend/tests/test_publicaciones_vertical.py) / [`test_gestion_publicaciones.py`](../backend/tests/test_gestion_publicaciones.py) | Corte vertical vigente con MySQL; listar, editar, estado y eliminar publicaciones propias |
| ASP-06 | Degradación controlada de persistencia | [EC-05](./arc42/10-escenarios-de-calidad.md#ec-05---degradación-ante-bloqueo-temporal-de-persistencia) | [C4 Nivel 2](./c4/02-contenedores.md) / [Vista de ejecución](./arc42/06-vista-ejecucion.md) | [ADR-0002](./adr/0002-manejo-bloqueo-sqlite.md) histórico / [ADR-0004](./adr/0004-migrar-persistencia-a-mysql.md) vigente | [`repository.py`](../backend/app/publicaciones/repository.py), [`service.py`](../backend/app/publicaciones/service.py), [`router.py`](../backend/app/publicaciones/router.py) | [`test_publicaciones_vertical.py`](../backend/tests/test_publicaciones_vertical.py) | Evidencia histórica SQLite + verificación vigente MySQL |
| ASP-07 | Contrato ejecutable de API | [EC-06 - Compatibilidad del contrato](./arc42/10-escenarios-de-calidad.md#ec-06---compatibilidad-del-contrato-de-api) | [C4 Nivel 2](./c4/02-contenedores.md) / [Vista de ejecución](./arc42/06-vista-ejecucion.md) | [ADR-0003](./adr/0003-usar-integracion-sincrona-http-json.md) | [`openapi-v2.json`](../contracts/openapi-v2.json), [`main.py`](../backend/app/main.py), [`router.py`](../backend/app/publicaciones/router.py) | [`test_contrato_openapi.py`](../backend/tests/test_contrato_openapi.py) / [`backend-tests.yml`](../.github/workflows/backend-tests.yml) | [Evidencia S7](./evidencias/evidencia-s7-2026-09-15.md) / [Fallo incompatible](./evidencias/fallo-contrato-s7-2026-09-15.md) / [Run #93 verde](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/35115585642) / [Run rojo](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/34934077733) |
| ASP-08 | Migración de persistencia a MySQL | Observación docente sobre persistencia vigente | [C4 Nivel 2](./c4/02-contenedores.md) / [C4 Nivel 3](./c4/03-componentes-backend.md) | [ADR-0004 - Migrar persistencia a MySQL](./adr/0004-migrar-persistencia-a-mysql.md) | [`repository.py`](../backend/app/publicaciones/repository.py), [`requirements.txt`](../backend/requirements.txt), [`.gitignore`](../.gitignore) | [`test_publicaciones_vertical.py`](../backend/tests/test_publicaciones_vertical.py), [`test_modularidad_s6.py`](../backend/tests/test_modularidad_s6.py) | Implementación vigente MySQL/PyMySQL |
| ASP-09 | Imágenes de publicaciones | Experiencia visual del marketplace y gestión de recursos de una publicación | [C4 Nivel 2](./c4/02-contenedores.md) / [C4 Nivel 3](./c4/03-componentes-backend.md) | [ADR-0011 - Gestionar imágenes de publicaciones](./adr/0011-gestionar-imagenes-de-publicaciones.md) | [`image_storage.py`](../backend/app/publicaciones/image_storage.py), [`router.py`](../backend/app/publicaciones/router.py), [`service.py`](../backend/app/publicaciones/service.py), [`repository.py`](../backend/app/publicaciones/repository.py) | [`test_gestion_publicaciones.py`](../backend/tests/test_gestion_publicaciones.py) / [`test_catalogo.py`](../backend/tests/test_catalogo.py) / [`test_contrato_openapi.py`](../backend/tests/test_contrato_openapi.py) | Verificación funcional local y Android; contrato y suite backend en verde |
| ASP-10 | Despliegue reproducible y operación pública | [Normas del laboratorio](https://github.com/ISCOUTB/iscoutb.dev/blob/main/README.md#5-evidencia-para-tus-entregas) / [EC-04](./arc42/10-escenarios-de-calidad.md#ec-04---recuperación-del-prototipo) | [C4 Nivel 2](./c4/02-contenedores.md) / [Despliegue vigente](./arc42/07-vista-despliegue.md) | [ADR-0016](./adr/0016-ajustar-recursos-a-la-cuota-del-laboratorio.md) / [ADR-0018](./adr/0018-ejecutar-el-monolito-en-dokploy-con-volumenes.md) | [Compose](../deploy/compose.lab.yaml), [Dockerfile](../backend/Dockerfile), [Publicación Pages](../.github/workflows/publicar-mvp-aprobado.yml) | [CI Compose](../.github/workflows/compose-mvp.yml), [health](../backend/tests/test_health.py), [flujo Web/Android](../.github/workflows/mvp-flujo-real.yml) | [Pruebas públicas, SHA, guía y pendientes](./evidencias/despliegue-publico-mvp-2026-10-04.md) |
| ASP-11 | Reportes y moderación | [Alcance funcional](./arc42/ARC42.md#32-alcance-funcional) / [propiedad y autorización](./arc42/08-conceptos-transversales.md) | [C4 L3](./c4/03-componentes-backend.md) | [ADR-0013](./adr/0013-materializar-reportes-y-moderacion-minima.md) / [ADR-0014](./adr/0014-habilitar-moderadores-por-identificador-interno.md) | [Administración](../backend/app/administracion/) / [dependencias Usuarios](../backend/app/usuarios/dependencies.py) | [Moderación](../backend/tests/test_administracion.py) / [propiedad](../backend/tests/test_propiedad_datos.py) | [Auditoría MVP](./evidencias/auditoria-mvp-continuacion-2026-10-03.md) / [CI backend](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/37173110650) |
| ASP-12 | Identidad y sesiones | [EC-02](./arc42/10-escenarios-de-calidad.md#ec-02---protección-de-publicaciones) | [C4 L3](./c4/03-componentes-backend.md) | [ADR-0012](./adr/0012-autenticar-con-sesiones-opacas-revocables.md) / [ADR-0017](./adr/0017-serializar-inicializacion-y-migracion-de-identidad.md) | [Usuarios](../backend/app/usuarios/) / [Publicaciones](../backend/app/publicaciones/) | [Usuarios](../backend/tests/test_usuarios.py), [EC-02](../backend/tests/test_ec02_autorizacion.py), [migración](../backend/tests/test_migracion_identidad.py) | [Auditoría MVP](./evidencias/auditoria-mvp-continuacion-2026-10-03.md) / [CI backend](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/37173110650) |
| ASP-13 | Fallos parciales e idempotencia de creación | [Evidencia S11 §2-3](./evidencias/evidencia-s11-2026-10-18.md) / [EC-02](./arc42/10-escenarios-de-calidad.md) | [C4 L2](./c4/02-contenedores.md) / [vista ejecución](./arc42/06-vista-ejecucion.md) | [ADR-0003](./adr/0003-usar-integracion-sincrona-http-json.md) / [ADR-0021](./adr/0021-mantener-catalogo-en-el-monolito-modular.md) | [Cliente Flutter](../frontend/campusmarket/lib/publicaciones/publicaciones_api.dart) / [router](../backend/app/publicaciones/router.py) / [repository](../backend/app/publicaciones/repository.py) | [Prueba de publicaciones existente](../backend/tests/test_gestion_publicaciones.py); **pruebas de duplicado/timeout S11 pendientes** (ver plan de §3) | [Análisis real + diseño + deuda](./evidencias/evidencia-s11-2026-10-18.md) |
| ASP-14 | Decisión de no extraer Catálogo y consistencia | [Evidencia S11 §4](./evidencias/evidencia-s11-2026-10-18.md) / [EC-01](./arc42/10-escenarios-de-calidad.md) | [C4 L2](./c4/02-contenedores.md) / [C4 L3](./c4/03-componentes-backend.md) | [ADR-0021](./adr/0021-mantener-catalogo-en-el-monolito-modular.md) | [Catálogo service](../backend/app/catalogo/service.py) / [Publicaciones service](../backend/app/publicaciones/service.py) | [Modularidad existente](../backend/tests/test_modularidad_s6.py), [erosión existente](../backend/tests/test_erosion_s9.py); ejecución nueva pendiente de CI | [Evaluación de alternativas](./adr/0021-mantener-catalogo-en-el-monolito-modular.md) / [riesgos arc42](./arc42/11-riesgos-y-deuda-tecnica.md) |
| ASP-15 | Frontend institucional sin otro contenedor; preparación 2026-10-30 | [Observación docente](https://github.com/ISCOUTB/AS_202620_feedback/blob/master/revisiones/2026-2/AS_202620_PROYECTO_CAMPUSMARKET/feedback.md) / [cuota](./arc42/02-restricciones.md#restricción-institucional-para-la-fase-2--2026-10-30) | [C4 L2 existente](./c4/02-contenedores.md) / [candidato de despliegue](./arc42/07-vista-despliegue.md#713-candidato-web-institucional-verificado-en-ci--2026-10-30) | [ADR-0025 propuesto](./adr/0025-servir-flutter-precompilado-desde-fastapi.md), sin sustituir aún ADR-0006 | [StaticFiles](../backend/app/web_frontend.py), [URL Flutter](../frontend/campusmarket/lib/shared/api_configuration.dart), [Dockerfile](../backend/Dockerfile), [Compose por digest](../deploy/compose.prod.yaml), [preflight](../scripts/preparar_despliegue_web.py) | [Montaje y contrato](../backend/tests/test_web_frontend.py), [Chrome/MySQL/recursos](../scripts/verificar_web_institucional.py), [workflow](../.github/workflows/web-institucional.yml), [prueba de despliegue/rollback](../scripts/ensayar_despliegue_web.py) | [Run 41094945507](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41094945507), fuente `a9b6709...`, 10/10 CI; [identidad, límites y promoción pendiente](./evidencias/despliegue-publico-mvp-2026-10-04.md#fase-2--frontend-institucional-candidato-probado-en-ci--2026-10-30). [Mecanismo 7/7](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41133683253); [condiciones productivas](./operacion/despliegue-ghcr.md). **Interfaz institucional aún no publicada.** |

---

## Alcance de materialización

El aspecto **ASP-01 - Consulta y búsqueda de productos** se encuentra
materializado y verificado desde S9 mediante el contexto `catalogo`, ADR-0009,
pruebas funcionales, reglas automáticas de erosión arquitectónica y la medición
de EC-01.

El aspecto **ASP-02 - Gestión segura de publicaciones** se encuentra
**materializado al nivel MVP**: identidad de sesión resuelta en Usuarios y
propiedad server-side en Publicaciones. EC-02 verifica dos cuentas reales, diez
ataques rechazados y datos intactos tras cada intento, en backend y Web/Android.
Véase la [auditoría](./evidencias/auditoria-mvp-continuacion-2026-10-03.md).

No se asocian pruebas artificialmente a capacidades que aún no están
implementadas.

La materialización vigente se concentra principalmente en:

- Usuarios: registro/login/perfil/logout con sesión;
- Administración: reportes y moderación;
- Gestión de Publicaciones;
- creación, edición, cambio de estado y eliminación de publicaciones;
- hasta tres imágenes por publicación;
- Catálogo con búsqueda, filtros y detalle;
- integración Flutter → FastAPI;
- persistencia MySQL;
- contrato OpenAPI;
- modularidad y propiedad única de datos;
- degradación controlada ante indisponibilidad.

---

# Trazabilidad histórica S4

Durante S4 se materializó el primer corte vertical funcional.

En ese momento, la arquitectura utilizada era:

```text
Flutter
   ↓
FastAPI
   ↓
Gestión de Publicaciones
   ↓
SQLite
```

Esta referencia se conserva como historia arquitectónica.

La creación de publicaciones permitió demostrar:

* formulario Flutter;
* solicitud HTTP;
* lógica de backend;
* persistencia;
* consulta posterior.

La arquitectura de S4 no representa el estado actual de persistencia.

---

## Verificación histórica de EC-03 en S4

Durante S4 se incorporó el estado:

`reacondicionado`

como modificación verificable dentro del módulo Publicaciones.

El cambio se mantuvo dentro de:

`backend/app/publicaciones/`

sin modificar:

* autenticación;
* catálogo;
* administración;
* fronteras del monolito modular.

En aquel momento la prueba utilizaba SQLite.

Actualmente la misma prueba ha evolucionado y utiliza MySQL.

Por tanto, la referencia a SQLite debe interpretarse exclusivamente dentro del
contexto histórico de S4.

---

# Trazabilidad histórica S5

Durante S5 se trabajó el aspecto:

**ASP-06 - Degradación controlada ante bloqueo de persistencia**

La cadena histórica fue:

```text
ASP-06
   ↓
R-07 / EC-05
   ↓
C4 Nivel 2
   ↓
ADR-0002
   ↓
Código
   ↓
Prueba
   ↓
Medición
   ↓
Evidencia
```

Durante ese corte se mantenía SQLite.

La restricción R-07 indicaba no incorporar nueva infraestructura para resolver
el reto.

ADR-0002 implementó:

* espera SQLite acotada;
* detección de `SQLITE_BUSY`;
* detección de `SQLITE_LOCKED`;
* respuesta HTTP `503`;
* ausencia de escritura parcial;
* recuperación posterior.

### Línea base histórica

* HTTP durante bloqueo: `500`;
* tiempo durante bloqueo: `7.323 s`;
* escritura parcial: `No`;
* recuperación posterior: `201`.

### Resultado histórico posterior

* HTTP durante bloqueo: `503`;
* tiempo durante bloqueo: `1.283 s`;
* escritura parcial: `No`;
* recuperación posterior: `201`;
* tiempo de recuperación: `0.006 s`.

Estas mediciones permanecen como evidencia histórica.

No representan el comportamiento técnico vigente de MySQL.

Evidencias:

* [Línea base](./evidencias/linea-base-bloqueo-sqlite-2026-09-05.md)
* [Medición posterior](./evidencias/medicion-bloqueo-sqlite-2026-09-06.md)
* [ADR-0002](./adr/0002-manejo-bloqueo-sqlite.md)

---

# Trazabilidad S6 — Dominio y modularidad

Durante S6 se hicieron explícitos los límites de dominio del monolito modular y
la propiedad de los datos.

Los contextos definidos son:

| Contexto delimitado      | Responsabilidad                | Estado actual                                   |
| ------------------------ | ------------------------------ | ----------------------------------------------- |
| Gestión de Usuarios      | Identidad y autenticación      | MVP: registro, login, perfil, sesiones y logout |
| Gestión de Publicaciones | Ciclo de vida de publicaciones | Materializado                                   |
| Catálogo                 | Consulta, búsqueda y filtrado  | Materializado                                   |
| Administración           | Moderación y supervisión       | MVP: reportes y revisión con nota |

---

## Propiedad de datos

CampusMarket adopta la regla:

> Cada dato de dominio tiene un único módulo responsable de escribirlo.

La entidad materializada principal es:

`publicaciones`

Su propietario es:

**Gestión de Publicaciones**

El escritor productivo es:

`backend/app/publicaciones/repository.py`

La correspondencia vigente es:

| Dato / entidad  | Contexto propietario     | Componente escritor                       | Otros contextos con escritura |
| --------------- | ------------------------ | ----------------------------------------- | ----------------------------- |
| `publicaciones` | Gestión de Publicaciones | `backend/app/publicaciones/repository.py` | Ninguno                       |
| `publicacion_imagenes` | Gestión de Publicaciones | `backend/app/publicaciones/repository.py` | Ninguno                  |

Los campos principales de `publicaciones` incluyen actualmente:

* `id`;
* `titulo`;
* `descripcion`;
* `precio`;
* `modalidad`;
* `estado`;
* `propietario_id`;
* `estado_publicacion`.

Las imágenes se modelan por separado mediante `publicacion_imagenes`, de acuerdo
con ADR-0011.

---

## Auditoría de modularidad

La auditoría de S6 se mantiene en:

[Auditoría de modularidad S6](./evidencias/auditoria-modularidad-s6-2026-09-12.md)

En S6 se inspeccionaron:

* `INSERT`;
* `UPDATE`;
* `DELETE`;
* repositorios;
* servicios;
* accesos a `publicaciones`;
* uso de SQLite existente en ese momento.

El resultado fue:

**No se detectaron escrituras compartidas entre módulos de dominio.**

La evolución posterior hacia MySQL, Catálogo e imágenes mantiene la misma regla
arquitectónica.

---

## Riesgos vigentes

| ID     | Riesgo                                                          | Tratamiento                                              |
| ------ | --------------------------------------------------------------- | -------------------------------------------------------- |
| MOD-01 | Catálogo podría acceder directamente a la tabla `publicaciones` | Consumir capacidades de Publicaciones mediante contratos |
| MOD-02 | Administración podría modificar directamente `publicaciones`    | Solicitar operaciones mediante Gestión de Publicaciones  |
| MOD-03 | Suplantación de propietario o privilegios | Sesión real, predicados SQL y capacidad por ID; tests EC-02 y moderación |
| MOD-04 | Tests o scripts podrían acoplarse al motor de persistencia      | Mantener esos accesos fuera del código productivo        |

---

## C4 Nivel 3 vigente

La materialización actual sigue:

```text
Flutter
     ↓ HTTP/JSON
FastAPI
     ├── Catálogo
     │      ↓ capacidad de lectura
     └── Publicaciones
              ↓
          Servicio de Publicaciones
              ↓
          Repositorio de Publicaciones
              ↓
             MySQL
```

Correspondencia:

| Elemento C4 Nivel 3          | Código                                    |
| ---------------------------- | ----------------------------------------- |
| Entrada de aplicación        | `backend/app/main.py`                     |
| API de Catálogo              | `backend/app/catalogo/router.py`          |
| Servicio de Catálogo         | `backend/app/catalogo/service.py`         |
| API de Publicaciones         | `backend/app/publicaciones/router.py`     |
| Servicio de Publicaciones    | `backend/app/publicaciones/service.py`    |
| Repositorio de Publicaciones | `backend/app/publicaciones/repository.py` |
| Persistencia                 | MySQL                                     |

---

## Verificación automática de modularidad

La prueba:

[`backend/tests/test_modularidad_s6.py`](../backend/tests/test_modularidad_s6.py)

verifica actualmente que:

* `repository.py` sea el único escritor productivo de `publicaciones`;
* routers/services no usen SQL y cada repository escriba solo sus tablas;
* otros contextos no importen el repositorio de Publicaciones;
* la dirección se mantenga:

```text
router → service → repository → MySQL
```

S9 añade además reglas explícitas de erosión para impedir que `catalogo`
atraviese directamente la frontera de persistencia.

---

# Trazabilidad S7 — API-first y evolución MVP

Durante S7 se formalizó HTTP/JSON síncrono con ADR-0003 y OpenAPI v1.
La [evidencia S7](./evidencias/evidencia-s7-2026-09-15.md) y el
[fallo incompatible](./evidencias/fallo-contrato-s7-2026-09-15.md) conservan esos
resultados históricos. La evolución de identidad del ADR-0012 requiere API 2.0.0.

## Correspondencia contrato ↔ implementación

Contrato vigente: [openapi-v2.json](../contracts/openapi-v2.json).
Proveedor: FastAPI `main.py` y los routers de los cuatro contextos.
Prueba: [test_contrato_openapi.py](../backend/tests/test_contrato_openapi.py), que
compara el proveedor exacto, el consumidor Flutter y Bearer/ausencia de propietario
de entrada. CI separa prueba contractual de suite funcional/arquitectónica.
El archivo v1 es historia y ya no es el snapshot exigido por la prueba actual.

Cadena: ASP-07 → EC-06 → C4/arc42 ejecución → ADR-0003/0012 → OpenAPI v2 →
proveedor → prueba → CI por hash → [auditoría MVP](./evidencias/auditoria-mvp-continuacion-2026-10-03.md).

# Trazabilidad de migración MySQL — ADR-0004

La evolución de persistencia se origina en una observación realizada por el
docente después del primer corte.

La observación indicó que la persistencia debía evolucionar de SQLite hacia
MySQL.

Por tanto, la migración no corresponde únicamente a una preferencia técnica del
equipo.

La decisión se registra mediante:

[ADR-0004 - Migrar persistencia a MySQL](./adr/0004-migrar-persistencia-a-mysql.md)

---

## Persistencia vigente

La tecnología actual es:

**MySQL**

El mecanismo de acceso es:

**PyMySQL**

Cada contexto persiste solo sus tablas en su repository. Publicaciones conserva
su único escritor; Usuarios y Administración incorporan los suyos. `db.py`
comparte conexión/transacción sin entidades de dominio.

La dirección vigente es:

```text
router.py
   ↓
service.py
   ↓
repository.py
   ↓
PyMySQL
   ↓
MySQL
```

---

## Consecuencias de la migración

La migración modifica:

* motor de persistencia;
* driver de acceso;
* configuración de conexión;
* pruebas de integración;
* documentación C4 y arc42.

No modifica:

* monolito modular;
* propietario de `publicaciones`;
* límites de contexto;
* comunicación Flutter → FastAPI;
* contrato OpenAPI;
* dirección router → service → repository.

---

## Verificación vigente de MySQL

La prueba:

[`backend/tests/test_publicaciones_vertical.py`](../backend/tests/test_publicaciones_vertical.py)

verifica actualmente:

* `POST /publicaciones`;
* HTTP `201`;
* persistencia real en MySQL;
* `GET /publicaciones`;
* recuperación del dato;
* respuesta `503` cuando la persistencia no está disponible.

La migración también se verifica mediante:

[`backend/tests/test_modularidad_s6.py`](../backend/tests/test_modularidad_s6.py)

para comprobar que la sustitución tecnológica no rompa las fronteras del
monolito modular.

---

## Cadena de trazabilidad de ADR-0004

```text
Observación docente
        ↓
ADR-0004
        ↓
C4 Nivel 2
        ↓
C4 Nivel 3
        ↓
arc42
        ↓
repository.py
        ↓
PyMySQL
        ↓
MySQL
        ↓
test_publicaciones_vertical.py
```

---

# Estado arquitectónico vigente del MVP

Los cuatro contextos están materializados y conservan router → service → repository
→ MySQL. Catálogo consume lecturas del service de Publicaciones; Administración
solicita ocultamiento por el mismo service. Usuarios posee sesiones e identidad.

| Aspecto MVP | Decisiones | Pruebas / evidencia |
|---|---|---|
| ASP-01 catálogo | ADR-0009/0019 | `test_catalogo.py`, `test_erosion_s9.py`, EC-01 Compose |
| ASP-02 propiedad | ADR-0012/0017 | `test_ec02_autorizacion.py`, mutación SQL, flujo Web/Android |
| ASP-07 contrato | ADR-0003/0012 | `openapi-v2.json`, `test_contrato_openapi.py` |
| ASP-09 fotos | ADR-0011/0015/0016/0018 | `test_imagenes_seguras.py`, selector real y persistencia Compose |
| ASP-12 identidad | ADR-0012/0014 | `test_usuarios.py`, tests de sesión Flutter y logout revocado |
| ASP-11 moderación | ADR-0013/0014 | `test_administracion.py`, flujo reporte/revisión |

Propiedad de datos: Usuarios (`usuarios`, `sesiones_usuario`, `intentos_autenticacion`),
Publicaciones (`publicaciones`, `publicacion_imagenes`), Administración
(`reportes_publicacion`); Catálogo sin SQL/tablas. Prueba global:
`test_propiedad_datos.py`. [C4 Nivel 3](./c4/03-componentes-backend.md) y
[conceptos transversales](./arc42/08-conceptos-transversales.md) detallan componentes.

[Auditoría de continuación](./evidencias/auditoria-mvp-continuacion-2026-10-03.md)
vincula requisito → implementación → ejecución → prueba → evidencia por hash.
La documentación histórica permanece fechada; no valida automáticamente el HEAD
MVP. Los ADR aceptados no se reescriben. El despliegue público está contrastado en la evidencia operativa; la recreación API posterior al PR #51 se registra en el complemento del índice arc42. EC-01 público completo y scanner continúan abiertos.


## Ampliación de trazabilidad — Evidencia S12 (2026-10-25)

Se añaden aspectos sin sustituir las filas históricas. Estado inicial: evidencia documental y contraste estático; los resultados de CI y el commit final de `master` deben completarse en la auditoría de cierre.

| ID | Aspecto | Requisito | C4 | ADR | Código | Pruebas | Evidencia |
|---|---|---|---|---|---|---|---|
| S12-DAT-01 | Garantías de consistencia en escrituras y lecturas | [Operaciones reales y garantía](./evidencias/evidencia-s12-2026-10-25.md#2-tabla-operación--garantía-de-consistencia) | [C4 L2](./c4/02-contenedores.md) | [ADR-0022](./adr/0022-mantener-mysql-como-fuente-de-verdad-y-evitar-proyecciones-asincronas.md) | [repository Publicaciones](../backend/app/publicaciones/repository.py), [Catálogo](../backend/app/catalogo/service.py), [repository Administración](../backend/app/administracion/repository.py) | [gestión](../backend/tests/test_gestion_publicaciones.py), [Catálogo](../backend/tests/test_catalogo.py) | [Matriz y límites](./evidencias/evidencia-s12-2026-10-25.md#7-matriz-de-los-nueve-criterios-específicos) |
| S12-DAT-02 | Evitar lecturas obsoletas por caché injustificada | [Política de caché e invalidación](./evidencias/evidencia-s12-2026-10-25.md#3-diseño-de-caché-e-invalidación) | [C4 L2](./c4/02-contenedores.md) | [ADR-0022](./adr/0022-mantener-mysql-como-fuente-de-verdad-y-evitar-proyecciones-asincronas.md) | [Catálogo directo al servicio](../backend/app/catalogo/service.py) | [test_catalogo.py](../backend/tests/test_catalogo.py) (verificación funcional previa; no prueba nueva de caché) | [Decisión y alternativa no implementada](./evidencias/evidencia-s12-2026-10-25.md#3-diseño-de-caché-e-invalidación) |


### Cierre auditable S12 — referencia incremental

Las filas S12-DAT-01 y S12-DAT-02 anteriores permanecen como trazabilidad original. Su [adenda de auditoría por hash](evidencias/cierre-s12-2026-10-25.md) contrasta las operaciones, la ausencia justificada de caché, el ADR-0022, C4 y arc42, y separa evidencias verificadas de CI y controles transversales aún no verificados. Los enlaces históricos de pruebas funcionales no se presentan como pruebas nuevas de invalidación.


## Taller S12 — Mensajes y consistencia (prototipo aislado)

| ID | Aspecto | Requisito | C4 | ADR | Código | Pruebas | Evidencia |
|---|---|---|---|---|---|---|---|
| S12-MSG-01 | Entrega tolerante a duplicados de notificación simulada | Taller aplicado S12: contrato, at-least-once, deduplicación, backoff, DLQ y correlación | [C4 L2 sin broker](c4/02-contenedores.md), sin cambio productivo | [ADR-0023](adr/0023-probar-mensajes-aislados-sin-introducir-broker-productivo.md) | [Prototipo](../scripts/taller_mensajes_s12.py), [contrato](../contracts/messages/publicacion-creada-v1.schema.json) | [Duplicados y reintentos](../backend/tests/test_taller_mensajes_s12.py) | [Evidencia y límites](evidencias/taller-mensajes-s12-2026-10-25.md), [workflow](../.github/workflows/s12-taller-mensajes.yml) |


### S12-MSG-02 — Validación explícita de backoff, sin romper S12-MSG-01

| ID | Requisito | Implementación | Prueba verificable | Evidencia | Decisión |
|---|---|---|---|---|---|
| S12-MSG-02 | Reintentos con espera progresiva y fallidos a DLQ | [`BrokerSimulator.consume`](../scripts/taller_mensajes_s12.py) invoca `sleep_fn(2)` y `sleep_fn(4)`; por defecto `time.sleep` | [Test fallo recuperable y DLQ](../backend/tests/test_taller_mensajes_s12.py): sleeper inyectado y verificación de `[2]` y `[2,4]` | [Adenda de backoff y límites](evidencias/taller-mensajes-s12-2026-10-25.md#adenda-posterior--backoff-temporal-verificable) | [ADR-0023](adr/0023-probar-mensajes-aislados-sin-introducir-broker-productivo.md), sin modificación histórica |

El test con sleeper falso demuestra que la ruta de reintento **invoca las demoras correctas**; no mide el tiempo real del scheduler. La demostración ejecutada sin inyección sí aplica esperas temporales. El CI de la corrección deberá comprobarse con el SHA posterior al PR correctivo, sin reutilizar el verde de PR #64 como si fuese validación de este cambio.
