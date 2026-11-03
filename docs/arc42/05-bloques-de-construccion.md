# 5. Bloques de construcción

## 5.1 Backend modular

ADR-0001 mantiene una sola aplicación FastAPI. Los cuatro contextos tienen
funcionalidad MVP comprobable; sus componentes se detallan en
[C4 Nivel 3](../c4/03-componentes-backend.md) y su fuente PlantUML.

| Contexto | Capacidades materializadas | Tablas propias / escritor |
|---|---|---|
| Usuarios | Registro, login, usuario actual, perfil, logout, expiración y presupuesto de intentos | `usuarios`, `sesiones_usuario`, `intentos_autenticacion`; `usuarios/repository.py` |
| Publicaciones | Crear, consultar propias, editar, estado, eliminar y galería segura | `publicaciones`, `publicacion_imagenes`; `publicaciones/repository.py` |
| Catálogo | Búsqueda, filtros, composición de imágenes y detalle | Sin SQL ni tablas; servicio de Publicaciones |
| Administración | Reportar, listar pendientes, resolver con nota y ocultar | `reportes_publicacion`; `administracion/repository.py` |

## 5.2 Componentes e interfaces

`main.py` registra cuatro routers, CORS, middleware de tamaño, errores,
observabilidad, health y StaticFiles. Cada router → service → repository → MySQL.
`db.py` comparte conexión/transacción sin entidades ni SQL de dominio.
`usuarios/dependencies.py` resuelve identidad y capacidad de moderación;
`usuarios/security.py` aplica scrypt y digest de tokens.
`publicaciones/image_storage.py` procesa y almacena fotos dentro de su contexto.

Catálogo lee publicaciones e imágenes en lote a través de Publicaciones
(ADR-0009/0019). Administración llama a `obtener_publicacion` y
`ocultar_publicacion` de su servicio; no importa el repository ajeno.

## 5.3 Consumidor y contrato

Flutter comparte SessionController en memoria, navegación condicionada por sesión,
formularios, perfil, catálogo/detalle, gestión de galería y revisión de reportes.
Un cambio de identidad recrea las vistas privadas; una respuesta antigua no puede
invalidar la sesión nueva. Web y Android usan la misma API 2.0.0, descrita en
[OpenAPI v2](../../contracts/openapi-v2.json). v1 es histórico.

## 5.4 Datos e imágenes

El ID de propietario sale de la sesión. SQL de edición/eliminación/cambio de estado
y galería limita por propietario. Publicaciones heredadas sin identidad comprobada
no aparecen en catálogo ni se atribuyen al primer registrado (ADR-0012/0017).
Pillow verifica contenido real, elimina metadatos y normaliza orientación/tamaño
(ADR-0015/0016). MySQL conserva referencias; Compose usa volúmenes para binarios
y datos (ADR-0018). No hay servicios de imágenes independientes.

## 5.5 Verificación

`test_propiedad_datos.py`: único escritor de cada tabla y ausencia de repositories
ajenos; `test_modularidad_s6.py`: dirección de dependencias;
`test_erosion_s9.py`: frontera de catálogo; `test_contrato_openapi.py`: igualdad
del proveedor. Tests funcionales y mutaciones completan la evidencia.
Véanse [auditoría](../evidencias/auditoria-mvp-continuacion-2026-10-03.md),
[conceptos transversales](08-conceptos-transversales.md) y
[decisiones](09-decisiones.md). Los ADR aceptados conservan su contenido original.


## 5.6 Incremento posterior a S13 — universidad declarada y catálogo de Cartagena

El [PR #81](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/pull/81) agrega el catálogo de doce universidades y su asociación opcional a usuarios y publicaciones. La ruta `GET /universidades` expone el catálogo; Usuarios administra la universidad declarada en registro y perfil; Publicaciones fija la universidad del propietario al crear el anuncio; Catálogo filtra por `universidad_id` a través de la capacidad de consulta de Publicaciones. **No se extrae un microservicio** ni se concede a Catálogo escritura directa en MySQL.

La interfaz Flutter reutiliza la autenticación y la navegación actuales. Los usuarios existentes y publicaciones históricas con `universidad_id = NULL` siguen siendo compatibles y visibles en «Toda Cartagena». Elegir una universidad no demuestra matrícula verificada. Se mantiene la frontera `router → service → repository` y el contrato [OpenAPI v2](../../contracts/openapi-v2.json).

**Evidencia verificable:** [pruebas backend de universidades](../../backend/tests/test_universidades_integracion.py), [publicaciones](../../backend/tests/test_universidades_publicaciones.py), [Flutter](../../frontend/campusmarket/test/universidades_integracion_test.dart) y [cierre público](../evidencias/cierre-universidades-cartagena-2026-11-02.md). Los apartados 5.1–5.5 conservan el estado histórico del MVP.

## 5.7 Incremento 2 — Favoritos privados (2026-11-03)

`favoritos/router → service → repository` es el único escritor de `favoritos`, con clave primaria `(usuario_id, publicacion_id)`. La identidad procede exclusivamente de `UsuarioActual`. GET privado compone referencias vigentes mediante Catálogo → capacidad pública por IDs de Publicaciones e imágenes en lote; no importa repositorios ajenos. Las referencias a anuncios ocultos/eliminados se omiten; reservado/vendido conserva su estado real. No se cambian tablas ni datos heredados.

Flutter comparte `FavoritosController` entre corazones y «Mis favoritos»; MySQL conserva los favoritos al cerrar sesión. Cambio de token vacía la caché y descarta respuestas de la sesión anterior. [Evidencia del corte](../evidencias/incremento-2-favoritos-2026-11-03.md).

## 5.8 Incremento 2 — Mensajería HTTP privada

`mensajeria/router → service → repository` posee `conversaciones` y `mensajes`; las únicas escrituras son propias. La clave de contexto `(publicacion_id, comprador_id, vendedor_id)` impide duplicados. El servicio determina al vendedor leyendo la publicación pública; comprador/remitente proceden de `UsuarioActual`. Cada consulta/escritura exige ser participante; los DTOs de entrada rechazan identidades adicionales. Bandeja con preview se resuelve en una consulta propia y compone publicaciones/imágenes en lote, sin correos ni nuevos servicios.

Flutter incorpora contacto en detalle, bandeja y chat, actualización manual y cursor de mensajes; el contenido privado se vacía al cambiar la sesión. Se conserva el monolito/API y MySQL existentes. [Código y pruebas](../evidencias/incremento-2-mensajeria-2026-11-03.md).
