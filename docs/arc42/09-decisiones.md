# 9. Decisiones arquitectónicas

CampusMarket mantiene las decisiones arquitectónicas mediante ADR independientes. Esta sección funciona como índice vigente y evita duplicar dentro de arc42 el contenido completo de cada decisión.

Las decisiones históricas se conservan; una evolución posterior no reescribe el contexto original de un ADR aceptado.

## Índice de decisiones

[ADR-0021 — No extraer Catálogo](../adr/0021-mantener-catalogo-en-el-monolito-modular.md) es la decisión S11, consistente con ADR-0001 y ADR-0009.


| ADR | Estado | Decisión | Alcance |
|---|---|---|---|
| [ADR-0001](../adr/0001-usar-monolito-modular.md) | Aceptado | Mantener un monolito modular. | Arquitectura general |
| [ADR-0002](../adr/0002-manejo-bloqueo-sqlite.md) | Histórico - primer corte | Degradación controlada ante bloqueo temporal de SQLite. | Persistencia histórica / EC-05 |
| [ADR-0003](../adr/0003-usar-integracion-sincrona-http-json.md) | Aceptado | Integración síncrona HTTP/JSON protegida por contrato OpenAPI. | Frontend → Backend |
| [ADR-0004](../adr/0004-migrar-persistencia-a-mysql.md) | Aceptado | Migrar la persistencia vigente a MySQL. | Persistencia vigente |
| [ADR-0005](../adr/0005-desplegar-campusmarket-en-azure-y-github-pages.md) | Aceptado histórico; elección de backend sustituida por ADR-0018 | Desplegar CampusMarket mediante GitHub Pages y Azure. | Despliegue S8 |
| [ADR-0006](../adr/0006-publicar-frontend-flutter-web-en-github-pages.md) | Aceptado | Publicar Flutter Web en GitHub Pages. | Frontend |
| [ADR-0007](../adr/0007-desplegar-api-fastapi-en-azure-app-service.md) | Aceptado histórico; entorno principal sustituido por ADR-0018 | Desplegar FastAPI en Azure App Service. | Backend S8 |
| [ADR-0008](../adr/0008-desplegar-mysql-en-azure-flexible-server.md) | Aceptado histórico; entorno principal sustituido por ADR-0018 | Desplegar MySQL en Azure Database for MySQL Flexible Server. | Persistencia S8 |
| [ADR-0009](../adr/0009-materializar-catalogo-sin-romper-fronteras.md) | Aceptado | Materializar Catálogo mediante capacidad explícita de lectura de Publicaciones. | Modularidad / EC-01 |
| [ADR-0010](../adr/0010-no-incorporar-componente-generativo-en-campusmarket.md) | Aceptado | No incorporar actualmente un componente generativo dentro del producto. | IA en runtime |
| [ADR-0011](../adr/0011-gestionar-imagenes-de-publicaciones.md) | Aceptado | Gestionar hasta tres imágenes por publicación separando metadatos relacionales y archivo físico. | Publicaciones / imágenes |
| [ADR-0012](../adr/0012-autenticar-con-sesiones-opacas-revocables.md) | Aceptado | Sesiones opacas revocables e identidad real. | Usuarios / EC-02 |
| [ADR-0013](../adr/0013-materializar-reportes-y-moderacion-minima.md) | Aceptado; habilitación de moderadores sustituida por ADR-0014 | Reportes y moderación mínima. | Administración |
| [ADR-0014](../adr/0014-habilitar-moderadores-por-identificador-interno.md) | Aceptado | Moderadores por ID de cuenta comprobada. | Autorización |
| [ADR-0015](../adr/0015-validar-y-reencodificar-imagenes-con-pillow.md) | Aceptado | Decodificar y sanitizar contenido real con Pillow. | Seguridad de imágenes |
| [ADR-0016](../adr/0016-ajustar-recursos-a-la-cuota-del-laboratorio.md) | Aceptado | Acotar memoria, concurrencia y cuerpos HTTP. | Recursos |
| [ADR-0017](../adr/0017-serializar-inicializacion-y-migracion-de-identidad.md) | Aceptado | Lock MySQL y migración de identidad única. | Persistencia |
| [ADR-0018](../adr/0018-ejecutar-el-monolito-en-dokploy-con-volumenes.md) | Aceptado para preparación; implementación pública posterior acreditada | Compose con volúmenes y backend principal Dokploy. | Operación vigente |
| [ADR-0019](../adr/0019-consultar-imagenes-en-lote-a-traves-de-publicaciones.md) | Aceptado | Lectura de imágenes en lote por el service propietario. | Catálogo / rendimiento |

## Composición vigente

```text
ADR-0001  Monolito modular
        ↓
Flutter Web / Android
        ↓
ADR-0003  HTTP/JSON síncrono + OpenAPI
        ↓
FastAPI
   ├── Catálogo
   │      ↓ capacidad explícita de lectura
   └── Publicaciones
          ↓
       repository
          ↓
ADR-0004  MySQL
```

La materialización de Catálogo sigue ADR-0009: `catalogo` no accede directamente a `publicaciones.repository`, no usa PyMySQL y no escribe los datos cuyo propietario es Gestión de Publicaciones.

La gestión de imágenes sigue ADR-0011/0015/0016. MySQL conserva metadatos;
Compose usa un volumen nombrado (ADR-0018). Azure requiere almacenamiento durable.
Usuarios y Administración persisten sus tablas en sus repositories; Catálogo
consume el service de Publicaciones. Los cuatro contextos están materializados.

## Estado de identidad

Usuarios resuelve sesiones opacas revocables; Publicaciones usa el ID autenticado
en los predicados SQL. EC-02 se verifica con dos cuentas y 10/10 ataques rechazados.
Registro/perfil no conceden moderación: se habilita externamente por ID comprobado.
Véase la [auditoría de continuación](../evidencias/auditoria-mvp-continuacion-2026-10-03.md).

## Decisiones históricas

ADR-0002 conserva la evidencia del comportamiento con SQLite durante el primer corte. ADR-0004 define la persistencia actual con MySQL; no se reinterpretan las mediciones históricas de SQLite como resultados de MySQL.

## Verificación

Las decisiones se contrastan con artefactos ejecutables y evidencia:

- `backend/tests/test_modularidad_s6.py` — propiedad de datos y dirección de dependencias;
- `backend/tests/test_erosion_s9.py` — frontera Catálogo → Publicaciones;
- `backend/tests/test_catalogo.py` — comportamiento de Catálogo;
- `backend/tests/test_ec01_catalogo.py` — medición de EC-01;
- `backend/tests/test_contrato_openapi.py` — contrato OpenAPI ↔ FastAPI;
- `backend/tests/test_gestion_publicaciones.py` — gestión propia e imágenes;
- `docs/evidencias/evidencia-s9-2026-10-01.md` — cadena verificable de S9.

La arquitectura vigente se describe además en:

- [C4 Nivel 2](../c4/02-contenedores.md);
- [C4 Nivel 3](../c4/03-componentes-backend.md);
- [Escenarios de calidad](10-escenarios-de-calidad.md);
- [Trazabilidad de aspectos](../aspectos.md).

## Lectura agrupada de las decisiones vigentes

Esta explicación facilita la revisión sin fusionar, renumerar ni modificar los
archivos aceptados. Un ADR describe por qué se eligió una alternativa; su número
no representa un paso del tutorial. Operación, resultados y enlaces posteriores
se actualizan aquí y en evidencias.

| Tema y problema | Decisiones relacionadas | Consecuencia y comprobación |
|---|---|---|
| Estructura y propiedad de datos | [0001](../adr/0001-usar-monolito-modular.md), [0003](../adr/0003-usar-integracion-sincrona-http-json.md), [0004](../adr/0004-migrar-persistencia-a-mysql.md) | Una API, HTTP/JSON, MySQL; [C4 L3](../c4/03-componentes-backend.md) y [propiedad](../../backend/tests/test_propiedad_datos.py) |
| Catálogo y costo de composición | [0009](../adr/0009-materializar-catalogo-sin-romper-fronteras.md), [0019](../adr/0019-consultar-imagenes-en-lote-a-traves-de-publicaciones.md) | Lectura por service propietario y en lote; evita SQL ajeno/N+1; [prueba](../../backend/tests/test_catalogo.py), [mutación](../../scripts/verificar_mutaciones_mvp.py), [medición](../../scripts/verificar_compose_mvp.py) |
| Identidad y migración segura | [0012](../adr/0012-autenticar-con-sesiones-opacas-revocables.md), [0017](../adr/0017-serializar-inicializacion-y-migracion-de-identidad.md) | Revocación cuesta consulta SQL; lock coordina procesos y evita reasignar datos heredados; [sesiones](../../backend/tests/test_usuarios.py), [migración](../../backend/tests/test_migracion_identidad.py) |
| Moderación y habilitación | [0013](../adr/0013-materializar-reportes-y-moderacion-minima.md), [0014](../adr/0014-habilitar-moderadores-por-identificador-interno.md) | Reportes/ocultado por servicios; 0014 sustituye solo correo privilegiado por ID comprobado, porque no se verifica correo; [test](../../backend/tests/test_administracion.py) |
| Ciclo de vida de fotografías | [0011](../adr/0011-gestionar-imagenes-de-publicaciones.md), [0015](../adr/0015-validar-y-reencodificar-imagenes-con-pillow.md), [0016](../adr/0016-ajustar-recursos-a-la-cuota-del-laboratorio.md) | Metadatos SQL/binarios separados, decodificación y retiro EXIF; 0016 sustituye concurrencia intensiva por guardia compartida bajo cuota; [test](../../backend/tests/test_imagenes_seguras.py) |
| Infraestructura y recursos | [0016](../adr/0016-ajustar-recursos-a-la-cuota-del-laboratorio.md), [0018](../adr/0018-ejecutar-el-monolito-en-dokploy-con-volumenes.md) | Dos contenedores de 256 MiB y volúmenes; Dokploy principal, Pages frontend; Azure conserva su historia, sin afirmar validación actual; [Compose](../../deploy/compose.lab.yaml) y [evidencia pública](../evidencias/despliegue-publico-mvp-2026-10-04.md) |
| Uso de IA dentro del producto | [0010](../adr/0010-no-incorporar-componente-generativo-en-campusmarket.md) | No hay necesidad demostrada de runtime generativo; evita costo/latencia/proveedor adicionales. IA de desarrollo sí se audita en [registro](../ia.md) |

### Aclaraciones históricas y de presentación

- ADR-0009 tiene un bloque Markdown sin cerrar desde «La dirección conceptual»,
  por lo que GitHub presenta parte del texto posterior como código. Su cabecera
  dice Aceptado y su apartado 14 conserva el estado inicial Propuesto. La
  [evidencia S9](../evidencias/evidencia-s9-2026-10-01.md) aporta implementación,
  mutación y medición posteriores. Se registra la incoherencia; no se corrige
  silenciosamente un archivo aceptado.
- ADR-0013/0014 y 0015/0016 contienen sustituciones parciales. La lectura vigente
  debe seguir esas relaciones y no usar correo para moderadores ni permitir dos
  trabajos intensivos bajo la cuota actual.
- El revisor señaló ediciones históricas de ADR-0002/0003/0005 sin reemplazo.
  Este índice no borra el hallazgo ni afirma que mantener intactos los archivos
  hoy arregle el historial. Su tratamiento requiere una declaración documentada
  del equipo; no inventar fechas de aprobación ni reescribir commits.
- No se crea otro ADR por complementar evidencia o cambiar el valor operativo
  CAMPUSMARKET_REVISION: la elección arquitectónica ya existe.

### Estado operativo posterior a ADR-0018

El 4 de octubre de 2026 a las 03:27 UTC, Dokploy reconstruyó REVISION con
`7856416795bb4accdf9d05e01adb470654875e56` y recreó API. Containers mostró API
`ec92894c809c` y MySQL `baedd6d65e17`, ambos running/healthy. Isolated Deployment
se observó activado. GET /health y /catalogo/1 devolvieron 200 y ese mismo SHA.
La publicación reservada de prueba mantuvo precio 16000 e imagen; GET de la
imagen devolvió 70 bytes y SHA-256
`d5a51b6aed15684ec8c123e30fe5703155359d6543b6d7b47cb5766ef44939de`,
idéntico al previo. No se usó Fresh Volumes. MySQL no fue recreado públicamente:
ese límite se conserva y no se atribuye el ensayo de CI a la producción.

Estas observaciones amplían el estado de operación; no convierten el despliegue
en la porción académica S9 ni acreditan el scanner Sonar pendiente.


## Adenda de decisiones posterior a S12 — 2026-11-01

- **[ADR-0025 — Servir Flutter Web con FastAPI desde el servicio Compose existente](../adr/0025-servir-flutter-web-con-fastapi-en-servicio-existente.md)** — *Propuesto para aceptación del equipo*. Complementa ADR-0018 (Dokploy/volúmenes) y ADR-0024 (imagen verificada por digest). A diferencia del ADR-0024 histórico, incorpora la decisión de hospedar `/app/` en el contenedor `api` existente, sin tercer contenedor ni red nueva. El despliegue y la observación pública del 1 de noviembre se registran en [cierre Web institucional](../evidencias/cierre-web-institucional-2026-11-01.md). No se reescribe un ADR aceptado.
