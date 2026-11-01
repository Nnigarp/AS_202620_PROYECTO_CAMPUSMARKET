# 8. Conceptos transversales

## 8.1 Lenguaje ubicuo

| Término | Significado en el MVP |
|---|---|
| Publicación | Oferta universitaria de un artículo; no hay entidad producto separada |
| Propietario | Cuenta resuelta por una sesión vigente; `propietario_id` es una referencia persistida |
| Estado del producto | `nuevo`, `usado`, `reacondicionado` |
| Disponibilidad | `disponible`, `reservado`, `vendido`; independiente del estado físico |
| Visible | Bandera de moderación; ocultamiento no destruye gestión del propietario |
| Sesión | Token opaco aleatorio, digest persistido, expiración absoluta y revocación |
| Moderador | Cuenta existente/comprobada habilitada externamente por ID |
| Reporte | Motivo, autor, publicación y resolución pendiente/ocultado/descartado con nota |

## 8.2 Contextos delimitados

Usuarios posee identidad, sesiones y presupuestos de intentos. Publicaciones posee
ciclo de vida, propiedad y fotografías. Catálogo compone lecturas. Administración
posee reportes y coordina revisión; solicita cambios de visibilidad a Publicaciones.
Todos están materializados al nivel MVP en una sola aplicación FastAPI.

## 8.3 Mapa de contextos

| Proveedor → consumidor | Capacidad usada | Frontera |
|---|---|---|
| Usuarios → Publicaciones | Identidad de sesión por dependencia | Sin repository ajeno ni identidad de query/body |
| Usuarios → Administración | Identidad y capacidad de moderación | Configuración por ID fuera del registro público |
| Publicaciones → Catálogo | Publicaciones públicas y galerías en lote | Catálogo no escribe ni usa SQL |
| Publicaciones → Administración | Obtener y ocultar publicación | Administración escribe solo reportes |

Estas dependencias son llamadas internas de servicio. No se introduce un Shared
Kernel de entidades ni servicios desplegables por contexto.

## 8.4 Propiedad de datos

| Tablas | Único contexto escritor | Repository |
|---|---|---|
| `usuarios`, `sesiones_usuario`, `intentos_autenticacion` | Usuarios | `usuarios/repository.py` |
| `publicaciones`, `publicacion_imagenes` | Publicaciones | `publicaciones/repository.py` |
| `reportes_publicacion` | Administración | `administracion/repository.py` |
| Ninguna | Catálogo | Consume services; no repository SQL |

`db.py` aporta conexión/transacción común, sin tablas de dominio. Cada operación
sigue router → service → repository → MySQL. Infraestructura compartida no concede
autoridad para escribir tablas de otro contexto.

## 8.5 Seguridad y comunicación

Contraseñas scrypt con salt; tokens de 256 bits solo en memoria del cliente y
SHA-256 en MySQL; expiración 12 horas y logout inmediato de esa sesión. Login limita
intentos por correo y peer real. La cuenta no verifica correo ni afiliación.
Múltiples dispositivos conservan sesiones independientes (ADR-0012).

Propiedad SQL en toda mutación y galería; imágenes públicas después de sanitizar.
Pillow verifica contenido real, límite 5 MiB/20 MP, orientación y normalización.
La guardia común limita trabajo de memoria intensivo. Errores de validación omiten
el input de contraseñas; respuestas privadas tienen no-store y logs no registran
tokens. HTTPS es requisito previo a exposición pública. CORS se configura por
orígenes y no autentica ni autoriza a un cliente.

## 8.6 Contratos

Externo: HTTP/JSON síncrono, multipart, Bearer y
[OpenAPI v2](../../contracts/openapi-v2.json), API 2.0.0 / OpenAPI 3.1.0.
v1 se conserva como contrato histórico. Interno: capacidades del servicio
propietario; ningún contexto importa su repository.

## 8.7 Errores, consistencia y operación

Transacciones MySQL confirman/retroceden escrituras. Galería bloquea su publicación;
revisión bloquea reporte; la migración de identidad usa GET_LOCK y retira de forma
ordenada el DEFAULT 1 heredado (ADR-0017).
SQL/filesystem usan compensación; crash o error de borrado puede dejar huérfanos
que deben reconciliarse. El ocultamiento y la resolución usan transacciones de
contextos diferentes y permiten reintento ante fallo parcial (ADR-0013).

Health consulta MySQL; indisponibilidad produce 503, no autorización permisiva.
Límites de cuerpo: 64 KiB JSON/6 MiB multipart y 413 también con streaming.
Observabilidad agrega correlación UUID, tiempos HTTP y métrica EC-01 sin payloads
ni credenciales. Compose: un worker, concurrencia 6, 256 MiB/0,5 CPU por servicio y
volúmenes nombrados para SQL/fotos. Reprovisionar base requiere revisar IDs de
moderación y no reutilizar allowlist automáticamente (ADR-0014).

## 8.8 Verificación y evolución

`test_propiedad_datos.py`, `test_modularidad_s6.py` y `test_erosion_s9.py` validan
fronteras; contrato compara proveedor exacto; EC-02 comprueba datos tras cada ataque.
Mutaciones verifican sensibilidad al defecto; el integration_test valida las
plataformas reales. Véanse [C4 Nivel 3](../c4/03-componentes-backend.md),
[aspectos](../aspectos.md), [decisiones](09-decisiones.md) y
[auditoría](../evidencias/auditoria-mvp-continuacion-2026-10-03.md).

SQLite y bloqueo del primer corte permanecen en evidencia/ADR históricos.
La evolución materializa los cuatro contextos; conserva ADR-0001 y el único
escritor por tabla. Esta continuación sincroniza documentación, no cambia ADR
aceptados ni efectúa despliegue.


## 8.9 Estrategia de datos y consistencia — S12 (2026-10-25)

La garantía se determina **por operación**, no como propiedad universal de CampusMarket. MySQL es la fuente de verdad: las escrituras locales confirman o revierten mediante transacciones; la creación/edición de publicaciones y los reportes permanecen en sus contextos propietarios. Catálogo consulta a Publicaciones por una llamada interna, sin proyección asíncrona; la revisión de reportes bloquea la fila con `FOR UPDATE`, pero el ocultamiento entre contextos no constituye una única transacción global. Las imágenes abarcan MySQL y filesystem con compensaciones, y un timeout HTTP en la creación no equivale a que la escritura haya fallado ni garantiza idempotencia.

La [tabla operación → garantía de S12](../evidencias/evidencia-s12-2026-10-25.md#2-tabla-operación--garantía-de-consistencia) identifica rutas, consecuencias de desfase y límites por operación. Se conserva [ADR-0022](../adr/0022-mantener-mysql-como-fuente-de-verdad-y-evitar-proyecciones-asincronas.md) para explicar el costo de revertir la propiedad de datos.

## 8.10 Estrategia de caché — S12 (2026-10-25)

**No incorporar caché mutable de aplicación en S12.** Las lecturas del catálogo acceden al servicio propietario/MySQL. No hay entradas ni TTL de aplicación que invalidar; cualquier futura caché necesitaría una política explícita de invalidación **tras cada escritura confirmada** (creación, edición, cambio de estado, moderación, borrado) y clave o versión para todas las variantes de filtros. TTL por sí solo dejaría lecturas obsoletas. Esta alternativa de cache-aside es **propuesta, no implementada**, y requiere medición EC-01 para justificarla. Los motores y navegadores pueden tener mecanismos internos distintos, que no se presentan aquí como caché del dominio.

La implementación productiva no agrega broker ni consumidor de mensajes; un eventual laboratorio de mensajería se documenta como prototipo aislado. [Evidencia y política completa S12](../evidencias/evidencia-s12-2026-10-25.md).


## 8.11 Arquitectura de seguridad y privacidad — S13 (2026-11-01)

El modelado STRIDE se ancla al [C4 L2](../c4/02-contenedores.puml) y se detalla en [la evidencia S13](../evidencias/evidencia-s13-amenazas-2026-11-01.md). Fronteras de confianza: dispositivo/navegador no confiable → API FastAPI; API → MySQL privado y volumen de imágenes; GitHub Actions/GHCR → imagen por digest en Dokploy. Flutter Web son archivos estáticos servidos por la API en el mismo contenedor, no un tercer servicio.

Controles observados en el código: autorización por usuario y moderador en routers; sesiones opacas con digest, revocación y contraseña derivada con scrypt; límites de autenticación; imágenes con tamaño/formato/píxeles limitados y reencodificación sin metadatos originales; imágenes GHCR por digest y configuración con variables de entorno. Esto **no certifica** ausencia de vulnerabilidades, prueba de intrusión ni protección integral contra incidentes. El escaneo de dependencias Python se propone en [workflow S13](../../.github/workflows/s13-dependencias.yml), cuyos hallazgos, run y decisiones están pendientes de ejecución y revisión.

Datos personales: correo, nombre, credenciales derivadas, sesiones e intentos; contenido/imágenes asociadas a propietarios; reportes y datos de moderación. Principio de minimización: no registrar contraseñas/tokens, limitar exposición de correo y reportes, eliminar EXIF al cargar fotos, documentar conservación y derechos. La **base jurídica exacta, aviso y retención** requieren verificación con responsable institucional antes de afirmar cumplimiento de protección de datos. No existe LLM productivo según [ADR-0010](../adr/0010-no-incorporar-componente-generativo-en-campusmarket.md); sus vectores de prompt/contexto no aplican al runtime actual.


**Seguimiento del escáner S13:** [primer run](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41360317202) auditó 16 dependencias Python y reportó 51 entradas de advisory; las versiones candidatas de `python-multipart` y `Pillow` se actualizan únicamente en el fork. Un run fallido que descubre vulnerabilidades es evidencia del análisis, pero no de remediación completada. [Detalle y artefacto](../evidencias/evidencia-s13-amenazas-2026-11-01.md).
