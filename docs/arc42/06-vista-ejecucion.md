# 6. Vista de ejecución

## 6.1 Autenticar y crear una publicación

1. Flutter registra la cuenta y solicita login a Usuarios. El service aplica
   presupuesto de intentos y verifica scrypt; el repository guarda solo el digest
   de un token aleatorio con expiración de 12 horas.
2. Flutter conserva el token en memoria y envía `POST /publicaciones` con Bearer.
3. La dependencia de Usuarios consulta la sesión vigente en MySQL. El router
   valida PublicacionCreate; el body no admite propietario.
4. El service recibe el ID de identidad resuelta y delega en el repository.
   La transacción inserta y devuelve la publicación con propietario real, HTTP 201.
5. Un logout elimina la sesión; volver a presentar el mismo token devuelve 401.

## 6.2 Autorizar una mutación / EC-02

| Situación | Recorrido y respuesta |
|---|---|
| Sin token, inventado o expirado | Dependencia de Usuarios rechaza con 401; no llega a escritura |
| A modifica su publicación | Router → service → repository; predicado ID + propietario A |
| B intenta editar/eliminar/cambiar estado/fotos de A | SQL restringido por propietario B; 404 y datos de A intactos |
| B suplanta propietario por body/query | Campo body rechazado; query no determina identidad |
| Usuario sin capacidad intenta moderar | Dependencia exige `es_admin`; 403 |

EC-02 verifica diez ataques con dos cuentas reales y comprueba el dato tras cada
uno. `test_ec02_autorizacion.py` y el flujo Web/Android lo ejecutan; una mutación
que elimina el predicado de propietario debe hacer fallar el test.

## 6.3 Subir una fotografía

El router recibe multipart y delega al servicio. Antes de guardar se exige
propiedad; Pillow decodifica formato real, verifica bytes/píxeles, conserva la
orientación, reduce a 2048 px y reencodifica sin EXIF. El servicio guarda bajo UUID
y registra metadatos con bloqueo del propietario/publicación. Una cuarta imagen
se rechaza aun con subidas concurrentes. Si falla el registro, compensa retirando
el archivo. El borrado retira metadatos y archivo. Un crash puede requerir
reconciliación de huérfanos: SQL y filesystem no son una transacción conjunta.

## 6.4 Catálogo y detalle

Catálogo consulta al service de Publicaciones, que excluye ocultas y heredadas sin
propietario. Aplica filtros y pide las imágenes de los IDs resultantes en lote.
Publicaciones ejecuta SQL parametrizado y devuelve galerías agrupadas. Catálogo
compone DTOs sin abrir MySQL ni importar repositories. El detalle vuelve a consultar
la publicación para reflejar edición, disponibilidad u ocultamiento recientes.

## 6.5 Reportar y moderar

B registra motivo sobre la publicación visible de A. Administración valida por el
service de Publicaciones y persiste su reporte. Un moderador con ID habilitado lee
pendientes; su repository bloquea el reporte durante la revisión. Para ocultar,
el service solicita la capacidad a Publicaciones y después resuelve con nota.
La publicación desaparece del catálogo; A conserva gestión propia y puede eliminar.
La operación usa dos transacciones MySQL: si falla completar el reporte
tras ocultar, la revisión queda pendiente y admite reintento (ADR-0013).

## 6.6 Errores y recursos

MySQL no disponible se traduce a 503; health devuelve degraded. No se permite
acceso por ausencia de persistencia. JSON supera 64 KiB o multipart supera 6 MiB:
413 antes del parser, incluyendo streaming sin Content-Length. Scrypt y procesamiento
de imágenes comparten una guardia de trabajo intensivo en el único worker del
Compose de laboratorio (ADR-0016); API y MySQL tienen 256 MiB cada uno.

## 6.7 Contrato, pruebas e historia

[OpenAPI v2](../../contracts/openapi-v2.json), API 2.0.0, coincide exactamente con
FastAPI. Pruebas de usuarios, EC-02, galería, administración, catálogo, límites,
modularidad y contrato se complementan con mutaciones. El integration_test ejecuta
registro/login, selector real, CRUD, ataques, reporte/moderación, eliminación y
logout en Chrome de escritorio, Chrome móvil y Android emulado.

[Auditoría y resultados](../evidencias/auditoria-mvp-continuacion-2026-10-03.md).
SQLite/ADR-0002 y OpenAPI v1 corresponden a revisiones históricas del primer corte
y S7. Los resultados de esas revisiones no validan por sí solos el MVP actual.

## 6.8 Incremento 2 — Guardar y recuperar favoritos

Flutter exige sesión y carga la lista privada antes de decidir PUT/DELETE `/favoritos/{publicacion_id}`. El router obtiene el usuario autenticado; el servicio valida visibilidad mediante Catálogo y su repositorio inserta con clave compuesta/idempotencia SQL. DELETE restringe por ambos IDs y admite reintentos, incluso si el anuncio desapareció. GET `/favoritos` devuelve solo referencias públicas resueltas en lote y `Cache-Control: no-store`. Logout revoca la sesión, sin borrar favoritos; login recupera los datos desde MySQL. El controlador descarta lecturas y escrituras atrasadas tras un cambio de sesión. Pruebas y estado de CI en [evidencia](../evidencias/incremento-2-favoritos-2026-11-03.md).

## 6.9 Incremento 2 — Contacto, conversación y reintento

B selecciona «Contactar al vendedor» en la publicación de A; POST `/conversaciones` deriva comprador de la sesión y vendedor de la publicación vigente. MySQL devuelve la conversación única aun ante solicitudes concurrentes. GET bandeja/detalle/mensajes restringe a participante; una conversación ajena devuelve el mismo 404 que una inexistente. POST mensajes obtiene al remitente de la sesión y bloquea la fila de conversación durante inserción y actualización de preview. La clave de reintento es única por conversación/remitente; reutilizarla con otro texto devuelve 409.

El chat recibe texto JSON de hasta 2000 caracteres, lo presenta como texto y consulta por cursor `despues_de` (50, máximo 100 por petición). La actualización es manual; no hay polling continuo ni WebSockets. Bandeja devuelve hasta 50 conversaciones por página. Si el anuncio se oculta/elimina, se conserva historia solo para participantes, sin metadatos públicos ni nuevos envíos. [Evidencia](../evidencias/incremento-2-mensajeria-2026-11-03.md).
