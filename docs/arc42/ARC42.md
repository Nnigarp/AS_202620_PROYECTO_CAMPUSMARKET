# CampusMarket - Documentación arc42

> **Lectura vigente hasta S13 · 2026-11-01:** este archivo resume fundamentos y conserva texto histórico de la evolución. Las secciones independientes `02`–`12` son la **fuente canónica** por tema; no se reescriben ADR ni se atribuyen resultados actuales a escenarios históricos. El estado de entrega y despliegue más reciente está en [README](../../README.md).

## Índice consolidado de arquitectura

| Tema arc42 | Fuente canónica y estado vigente |
|---|---|
| 1. Objetivos | Este archivo §1, [README](../../README.md) y [aspectos](../aspectos.md) |
| 2. Restricciones | [02-restricciones](02-restricciones.md): cuota del servicio y topología existente |
| 3. Contexto | [03-contexto](03-contexto.md) · [C4 L1](../c4/01-contexto.md) |
| 4. Estrategia | [04-estrategia](04-estrategia-de-solucion.md): monolito modular, [ADR-0001](../adr/0001-usar-monolito-modular.md) |
| 5. Bloques | [05-bloques](05-bloques-de-construccion.md) · [C4 L2](../c4/02-contenedores.md) · [C4 L3](../c4/03-componentes-backend.md) |
| 6. Ejecución | [06-vista-ejecucion](06-vista-ejecucion.md): autenticación, publicaciones y persistencia |
| 7. Despliegue | [07-vista-despliegue](07-vista-despliegue.md): Dokploy, `api` + `db`, Flutter en `/app/`, persistencia en volúmenes, digest GHCR, rollback productivo no acreditado |
| 8. Conceptos transversales | [08-conceptos](08-conceptos-transversales.md): consistencia S12, seguridad/privacidad S13 y [auditoría CI](../../.github/workflows/s13-dependencias.yml) |
| 9. Decisiones | [09-decisiones](09-decisiones.md), ADR-0001…0025 y [ADR-0026 propuesto](../adr/0026-incorporar-auditoria-de-dependencias-python-en-ci.md) |
| 10. Calidad | [10-escenarios](10-escenarios-de-calidad.md) · [árbol](10-arbol-de-utilidad.md); no equiparar medidas HTTP aisladas con navegador público |
| 11. Riesgos | [11-riesgos](11-riesgos-y-deuda-tecnica.md): riesgos STRIDE aceptados provisionalmente, backup y privacidad pendiente |
| 12. Glosario | [12-glosario](12-glosario.md) |

**Evidencia S13:** [tabla STRIDE, mitigaciones, responsables, privacidad y revisión de hallazgos](../evidencias/evidencia-s13-amenazas-2026-11-01.md). Integración [PR #79](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/pull/79) y [commit comprobado](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/commit/049dc30ceac1386b648bef5f6713c050762e2dbf). No hay LLM de producto ([ADR-0010](../adr/0010-no-incorporar-componente-generativo-en-campusmarket.md)).

**Precisión de alcance:** frontend institucional y API están publicados; los cambios de paquetes Python S13 en Git no certifican nueva imagen productiva. Sigue sin acreditarse una restauración real desde respaldo externo, y la base legal de tratamiento requiere confirmación institucional.

---


## 1. Introducción y objetivos

### 1.1 Descripción del sistema

CampusMarket es una plataforma orientada a estudiantes universitarios que busca
facilitar la publicación, búsqueda, venta y alquiler de productos nuevos o
usados dentro de la comunidad estudiantil.

La idea surge debido a que muchos estudiantes ofrecen productos mediante grupos
de WhatsApp, redes sociales u otros medios informales, donde las publicaciones
pueden perderse fácilmente y no existe una forma centralizada y organizada de
consultar los artículos disponibles.

CampusMarket busca centralizar estas publicaciones en una plataforma donde los
estudiantes puedan encontrar y ofrecer productos de manera organizada,
manteniendo un alcance adecuado para el desarrollo académico durante el
semestre.

La interfaz se desarrolla con Flutter y está verificada en Web y Android.
iOS queda fuera de la validación actual.

---

### 1.2 Objetivos de negocio e interesados

Los objetivos de negocio de CampusMarket se orientan a mejorar la forma en que
los estudiantes universitarios ofrecen y encuentran productos dentro de su
comunidad.

| ID | Objetivo de negocio | Interesado principal |
|---|---|---|
| ON-01 | Centralizar en una sola plataforma las publicaciones de productos que actualmente se encuentran dispersas en grupos de WhatsApp, redes sociales y otros medios informales. | Estudiantes universitarios |
| ON-02 | Facilitar que los estudiantes encuentren productos disponibles para compra o alquiler dentro de la comunidad universitaria. | Estudiantes compradores o arrendatarios |
| ON-03 | Dar mayor visibilidad a los productos que los estudiantes desean vender o alquilar mediante publicaciones organizadas y consultables. | Estudiantes vendedores o propietarios |
| ON-04 | Mantener un entorno controlado para las publicaciones y apoyar la supervisión del contenido disponible en la plataforma. | Administrador de CampusMarket |

---

### 1.3 Objetivos de calidad

Los principales atributos de calidad considerados para CampusMarket son los
siguientes.

#### Mantenibilidad

La aplicación debe estar organizada de forma que sea posible modificar o
agregar funcionalidades sin afectar innecesariamente partes del sistema que no
estén relacionadas con el cambio.

Este objetivo se desarrolla mediante el escenario de calidad:

**EC-03 - Modificación del sistema**.

#### Seguridad

Un estudiante solamente podrá modificar o eliminar las publicaciones que le
pertenecen.

Los intentos de modificación realizados por usuarios que no sean propietarios
deberán ser rechazados.

Este objetivo se desarrolla mediante el escenario:

**EC-02 - Protección de publicaciones**.

#### Rendimiento

Las funciones principales de consulta y búsqueda deben responder en tiempos
adecuados durante la operación normal del sistema.

Este objetivo se desarrolla mediante:

**EC-01 - Consulta de productos**.

#### Disponibilidad y recuperación

En caso de una falla durante una prueba o demostración, el equipo debe poder
recuperar el funcionamiento del prototipo en un tiempo controlado y sin perder
la información almacenada correctamente antes de la falla.

Este objetivo se desarrolla mediante:

**EC-04 - Recuperación del prototipo**.

Los escenarios completos y sus medidas verificables se encuentran en:

[10-escenarios-de-calidad.md](./10-escenarios-de-calidad.md)

El árbol de utilidad y su priorización se encuentran en:

[10-arbol-de-utilidad.md](./10-arbol-de-utilidad.md)

---


## 2. Restricciones

Tiempo de semestre, equipo de tres, alcance universitario y monolito modular.
MySQL es la persistencia vigente. El alcance no incluye pagos, banca ni logística.
La preparación Compose aplica la cuota de ADR-0016: 512 MiB sumados, un worker.
Detalle: [02-restricciones.md](02-restricciones.md).

## 3. Contexto y alcance

### 3.2 Alcance funcional

Registro/login/logout/perfil, catálogo/detalle, CRUD y disponibilidad propia,
galería de hasta tres imágenes y reportes/moderación. Cuatro contextos materializados.
Correo/afiliación universitaria no se verifican; sesión del cliente vive en memoria.
Detalle: [03-contexto.md](03-contexto.md) y [C4 Nivel 1](../c4/01-contexto.md).

## 4. Estrategia de solución

ADR-0001: monolito modular. ADR-0003: HTTP/JSON síncrono. ADR-0004: MySQL.
Usuarios y Administración se materializan respetando la propiedad de sus datos;
Catálogo consume lectura del servicio de Publicaciones, incluida galería en lote.
Alternativas y tensiones: [04-estrategia-de-solucion.md](04-estrategia-de-solucion.md).

## 5. Bloques de construcción

Flutter Web/Android → FastAPI único → repositories por contexto → MySQL.
Archivos separados de metadatos y directorio/volumen configurable.
Componentes y tablas: [05-bloques-de-construccion.md](05-bloques-de-construccion.md)
y [C4 Nivel 3](../c4/03-componentes-backend.md).

## 6. Vista de ejecución

Identidad resuelta por sesión, propiedad SQL y 10/10 rechazos EC-02 con datos
intactos. Selector real, sanitización de fotografías, catálogo actualizado,
reporte/resolución y logout revocado.
Secuencia: [06-vista-ejecucion.md](06-vista-ejecucion.md).

## 7. Vista de despliegue

S8 acredita una revisión anterior en Pages/Azure. El backend público vigente está
operativo en Dokploy con revisión `7856416795bb4accdf9d05e01adb470654875e56`.
Pages conserva frontend compilado desde c38e0cf con la API Dokploy; PR #51 cambia
workflow/documentación, no código de aplicación. El 4 de octubre a las 03:27 UTC
se recreó API y se comprobó HTTP 200, la revisión, la publicación y su imagen
con hash idéntico; MySQL permaneció running/healthy, sin recrearse públicamente.
ADR-0018 define volúmenes/cuota; la persistencia ante recreación API/MySQL en CI
se acredita separadamente. [Decisiones y alcance vigente](09-decisiones.md).
Detalle: [07-vista-despliegue.md](07-vista-despliegue.md).

## 8. Conceptos transversales

Único escritor de seis tablas, sin repositories ajenos. Sesiones revocables,
scrypt, capacidad de moderación por ID comprobado, límites de cuerpo/trabajo y
observabilidad sin credenciales. SQL y archivos usan compensación ante errores.
Detalle: [08-conceptos-transversales.md](08-conceptos-transversales.md).

## 9. Decisiones arquitectónicas

[09-decisiones.md](09-decisiones.md) indexa ADR-0001 a ADR-0019. Los ADR aceptados
conservan su contenido; decisiones posteriores indican qué extienden o sustituyen.
ADR-0002 y despliegue S8 son historia. ADR-0018 fue aceptado para preparación;
el estado operativo posterior se actualiza en el índice, sin reescribir ese ADR.
La lectura agrupada explica qué complementa o sustituye cada decisión.

## 10. Escenarios de calidad

[Escenarios y medidas](10-escenarios-de-calidad.md) y [árbol de utilidad](10-arbol-de-utilidad.md).
EC-01 en Compose exige diez búsquedas de 1000 filas y >=9/10 bajo 2 s
(loopback/MySQL/cuota). El run del SHA contrastado cumple ese gate; los valores
históricos 10/10 pertenecen a sus respectivos hashes. EC-01 completo desde el
navegador público con 1000 filas todavía no está acreditado.
EC-02: dos cuentas reales, 10/10 mutaciones ajenas rechazadas y datos intactos.
EC-06: [OpenAPI v2](../../contracts/openapi-v2.json) coincide exactamente con FastAPI.
[Ejecuciones por hash](../evidencias/auditoria-mvp-continuacion-2026-10-03.md).

## 11. Riesgos y deuda técnica

| Riesgo/límite | Tratamiento actual / trabajo siguiente |
|---|---|
| Sesión solo en memoria; no recuperación/verificación de correo | Limitación explícita MVP; no simular capacidades ausentes |
| Token robado hasta expiración/logout | HTTPS obligatorio antes de exposición; digest en SQL; no-store |
| SQL/archivos y revisión/ocultamiento sin transacción conjunta | Compensación, bloqueo por reporte y reintento; reconciliación de huérfanos |
| Un worker/cuota pequeña; búsquedas en memoria | Guardia intensiva, galería en lote y medición al volumen MVP |
| Reprovisionar SQL puede reutilizar IDs | Revisar allowlist de moderadores por entorno y cuenta comprobada |
| Fotografías sin volumen durable en otro entorno | Montaje persistente obligatorio antes de despliegue |
| Gate de calidad de otra revisión | Exigir SonarCloud asociado al PR/HEAD actual; estado en auditoría |

## 12. Glosario

[12-glosario.md](12-glosario.md) y [lenguaje ubicuo](08-conceptos-transversales.md#81-lenguaje-ubicuo).
Trazabilidad: [aspectos](../aspectos.md), [uso de IA](../ia.md),
[auditoría de continuación](../evidencias/auditoria-mvp-continuacion-2026-10-03.md).

## Lectura específica de S9

La [evidencia S9](../evidencias/evidencia-s9-2026-10-01.md) centraliza la cadena
ASP-01→EC-01→C4→ADR-0009/0019→Catálogo→prueba/mutación→medición, el extracto
[IA](../ia.md#s9--criterio-y-verificacion-del-catalogo) y la matriz de la ficha.
El despliegue se mantiene como operación adicional. La extensión de arc42 no
sustituye la comprobación de enlaces, resultados por SHA y comprensión del equipo.
