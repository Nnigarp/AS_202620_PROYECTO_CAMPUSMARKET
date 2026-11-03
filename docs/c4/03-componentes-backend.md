# C4 Nivel 3 - Componentes del Backend API de CampusMarket

> El diagrama incorpora el código candidato del Incremento 2. Sus adendas al final identifican capacidades y pruebas nuevas, todavía sin despliegue. Los apartados MVP preservan antecedentes; para el estado institucional vigente se consulta [arc42 §7](../arc42/07-vista-despliegue.md).


Fuente canónica: [03-componentes-backend.puml](03-componentes-backend.puml).
El backend es una sola aplicación FastAPI: monolito modular, cuatro contextos
materializados al nivel MVP y una única base MySQL. Estado de verificación en
[auditoría de continuación](../evidencias/auditoria-mvp-continuacion-2026-10-03.md).

## Componentes y propiedad de datos

| Contexto | Entrada y servicio | Repositorio / datos propios | Estado MVP |
|---|---|---|---|
| Usuarios | `usuarios/router.py`, `service.py`, `dependencies.py`, `security.py` | `usuarios/repository.py`: `usuarios`, `sesiones_usuario`, `intentos_autenticacion` | Registro, login, perfil, sesión y logout |
| Publicaciones | `publicaciones/router.py`, `service.py`, `image_storage.py` | `publicaciones/repository.py`: `publicaciones`, `publicacion_imagenes` | CRUD propio, disponibilidad y galería |
| Catálogo | `catalogo/router.py`, `service.py` | Sin tablas ni SQL propios; lee por el servicio de Publicaciones | Búsqueda, filtros, tarjetas y detalle |
| Administración | `administracion/router.py`, `service.py` | `administracion/repository.py`: `reportes_publicacion` | Reportar, cola de revisión, ocultar o descartar con nota |

Las rutas son relativas a `backend/app/`. `main.py` registra los cuatro routers,
CORS, manejo de errores, límites HTTP, observabilidad, health y lectura pública de
`/uploads`. `db.py` comparte conexión/transacción, sin SQL de dominio.

## Relaciones permitidas

- Cada router delega en su service; cada service persiste mediante su repository.
- Publicaciones obtiene identidad por `usuarios/dependencies.py`; el usuario
  autenticado procede del hash del token vigente en MySQL, no del body o query.
- Catálogo consume `listar_publicaciones`, `listar_imagenes_publicaciones` y
  `listar_imagenes_publicacion` de Publicaciones. La lectura en lote evita una
  conexión por fila y preserva la propiedad de datos (ADR-0019).
- Administración consulta/oculta por el servicio de Publicaciones. Solo escribe
  sus reportes; una revisión bloquea el reporte para impedir decisiones simultáneas.
- Ningún contexto importa un repository ajeno. No hay microservicios ni Shared
  Kernel de entidades. La dirección sigue `router → service → repository → MySQL`.

## Identidad y fotografías

ADR-0012 fija sesiones Bearer opacas revocables y scrypt para contraseñas.
Flutter conserva el token en memoria: reinicio/recarga requiere login.
`propietario_id` es salida y predicado SQL de autorización. Las publicaciones
heredadas quedan sin propietario y fuera del catálogo hasta atribución comprobada.
ADR-0014 habilita moderadores por ID de una cuenta comprobada, en configuración
externa y vacío por defecto; no hay ascenso desde registro o perfil.

Publicaciones guarda el archivo con nombre aleatorio después de decodificar,
orientar, reducir a 2048 px y reencodificar con Pillow. El límite es tres imágenes,
5 MiB y 20 MP de entrada. MySQL conserva metadatos y referencias. Los archivos de
publicaciones visibles se leen públicamente; subir, cambiar principal y eliminar
exigen propietario autenticado. SQL y filesystem no comparten transacción:
compensación y reconciliación de huérfanos siguen ADR-0015.

El directorio se configura con `CAMPUSMARKET_UPLOAD_DIR`. Compose conserva el
directorio en un volumen nombrado (ADR-0018), probado tras recrear contenedores.
El MVP público usa Flutter Web en GitHub Pages y API FastAPI en Dokploy,
https://campusmarket.iscoutb.dev, con /health y /docs operativos (HTTP 200).
El bundle Pages consume esa API. Dokploy conserva fotos en publication_images
y MySQL en mysql_data. El registro público acredita recreación de API con la
muestra intacta; la recreación de MySQL está verificada únicamente en CI.

Backend observado, commit 7856416795bb4accdf9d05e01adb470654875e56; frontend fuente:
c38e0cf36a30dddec39f169b7618b7c6127e0a71; master auditado:
b5f10a2c93836cad539a9a195f6a0911d4b3ca91. El código relevante es idéntico,
pero cada ejecución conserva su hash en el [complemento S9](../evidencias/evidencia-s9-2026-10-01.md#17-complemento-final-de-auditoria-s9--4-de-octubre-de-2026).
Azure corresponde a la línea base histórica S8.

## Contrato y verificación

Contrato vigente: [OpenAPI v2](../../contracts/openapi-v2.json), API 2.0.0.
v1 permanece como evidencia histórica. `test_contrato_openapi.py` exige igualdad
exacta con FastAPI y Bearer en las operaciones protegidas.

Pruebas: `test_propiedad_datos.py`, `test_modularidad_s6.py`,
`test_erosion_s9.py`, `test_usuarios.py`, `test_ec02_autorizacion.py`,
`test_imagenes_seguras.py`, `test_administracion.py`, `test_catalogo.py`.
Las mutaciones comprueban que los tests fallan ante suplantación, password
incorrecto, moderación sin capacidad, archivo disfrazado o erosión de fronteras.

Decisiones aplicadas: ADR-0001/0003/0004/0009 y ADR-0011 a ADR-0019.
El índice de [decisiones](../arc42/09-decisiones.md) mantiene sus estados y enlaces.

## Incremento 2 — Favoritos (2026-11-03)

El diagrama incorpora `Favoritos`: router privado → servicio → repositorio propio (`favoritos`). El router obtiene identidad de Usuarios; el servicio compone únicamente lecturas públicas de Catálogo/Publicaciones por IDs e imágenes en lote. La tabla privada no cambia propietarios ni anuncia disponibilidad de referencias ocultas/eliminadas. Una única API/MySQL y los dos contenedores existentes se conservan; no hay servicio adicional. [Código](../../backend/app/favoritos/) · [pruebas de propiedad](../../backend/tests/test_propiedad_datos.py) · [evidencia](../evidencias/incremento-2-favoritos-2026-11-03.md). Los estados de despliegue de apartados anteriores son históricos; este corte aún no está publicado.

## Incremento 2 — Mensajería (2026-11-03)

Router privado → servicio → repositorio de Mensajería, dueño exclusivo de conversaciones/mensajes. Usa identidad de Usuarios y contexto público de Catálogo; no modifica propietarios ni abre repositorios ajenos. Una transacción propia serializa envío y preview; unicidad de contexto y clave de reintento se apoyan en MySQL. Bandeja/chat comparten HTTP/JSON con Web/Android (ADR-0003), sin brokers o nuevos contenedores. [Código](../../backend/app/mensajeria/) · [Autorización/MySQL](../../backend/tests/test_mensajeria.py) · [evidencia](../evidencias/incremento-2-mensajeria-2026-11-03.md).

## Incremento 2 — Universidad visible (2026-11-03)

La capacidad de Universidades compone instituciones por IDs en lote para Catálogo, que enriquece sus DTOs sin SQL/repositorios ajenos. Usuarios valida por esa capacidad y usa su hook de inicialización antes de crear la FK existente; Universidades sigue siendo el único escritor del catálogo. Se conserva la institución del anuncio al publicar, incluso si el perfil cambia; NULL histórico no se inventa. Flutter muestra declaración, no matrícula verificada. [Código](../../backend/app/universidades/service.py) · [pruebas](../../backend/tests/test_identidad_universitaria_visible.py) · [evidencia](../evidencias/incremento-2-universidad-visible-2026-11-03.md).
