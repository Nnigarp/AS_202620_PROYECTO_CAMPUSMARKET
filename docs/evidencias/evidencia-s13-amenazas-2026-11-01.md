# Evidencia S13 — STRIDE, cadena de suministro y privacidad · CampusMarket

**Fecha de preparación:** 2026-11-01 (Colombia). **Base de inspección:** `ISCOUTB/master` `ad9c784eb14f848a912788a7b9b12bf43eaeefb9`. **Estado:** evidencia en preparación, pendiente de ejecutar y revisar el análisis de dependencias en CI. No equivale a entrega calificada.

## 1. Alcance, C4 y fronteras de confianza

Modelo anclado en [C4 L2](../c4/02-contenedores.puml) y [C4 L3](../c4/03-componentes-backend.puml). Navegador o app Flutter y usuarios son **no confiables**; las llamadas HTTPS llegan a FastAPI; FastAPI controla credenciales y autorización, accede mediante PyMySQL a MySQL en la red interna de Compose y escribe imágenes en volumen separado. La cadena de suministro comprende GitHub Actions, dependencias Python/Dart, imagen de aplicación GHCR fijada por digest y MySQL 8.4. No hay servicio de IA generativa en tiempo de ejecución según [ADR-0010](../adr/0010-no-incorporar-componente-generativo-en-campusmarket.md).

**Método:** STRIDE; probabilidad (P) e impacto (I) de 1 (bajo) a 3 (alto). Riesgo = P × I; **alto 6–9, medio 3–4, bajo 1–2**. Clasificaciones son juicio de modelado, no resultados de explotación. Responsables propuestos por rol para asignación final por el equipo.

## 2. Amenazas y tratamiento priorizado

| ID | STRIDE | C4 / frontera y activo | Escenario de amenaza | P | I | Riesgo | Mitigación concreta y referencia | Responsable propuesto | Estado al preparar S13 |
|---|---|---|---|---:|---:|---:|---|---|---|
| T13-01 | Suplantación / Elevación | Flutter → API; sesión/propietario | Cliente altera propietario o reutiliza token robado para editar publicación ajena | 3 | 3 | **9 alto** | Identidad exclusiva desde Bearer, tokens opacos y revocables, pruebas de autorización y respuesta antigua de sesión; [dependencias](../../backend/app/usuarios/dependencies.py), [router](../../backend/app/usuarios/router.py), [tests](../../backend/tests/test_ec02_autorizacion.py) | Backend + QA | **Mitigación existente; revisar pruebas S13** |
| T13-02 | Manipulación / Denegación | Flutter → API → volumen de imágenes | Imagen maliciosa, descompresión excesiva o metadatos personales | 3 | 3 | **9 alto** | 5 MiB, 20 MP, formatos comprobados por contenido, reescritura de imagen sin EXIF; [image_storage.py](../../backend/app/publicaciones/image_storage.py); comprobar pruebas y carga sostenida | Backend + QA | **Mitigación existente; prueba de carga pendiente** |
| T13-03 | Divulgación / Manipulación | GitHub Actions → GHCR → API | Dependencia vulnerable o imagen sustituta compromete datos | 2 | 3 | **6 alto** | Versiones fijadas en [requirements](../../backend/requirements.txt), imagen GHCR por digest en [Compose](../../deploy/compose.prod.yaml), escaneo automatizado `pip-audit` propuesto en workflow; revisar reporte y corregir vulnerabilidades confirmadas | DevOps | **Parcial: falta resultado del escaneo** |
| T13-04 | Divulgación | API → MySQL / logs | Contraseña, correo o token expuestos en configuración o registros | 2 | 3 | **6 alto** | Secretos por variables `MYSQL_PASSWORD`; no registrar token/password; [security.py](../../backend/app/usuarios/security.py); revisar logs y hacer barrido HEAD e historial, no publicar valores | DevOps + Backend | **Parcial: barrido completo pendiente** |
| T13-05 | Repudio / Divulgación | API → MySQL; informes | Acceso de no moderador a reportes con identidad y motivos | 2 | 3 | **6 alto** | `ModeradorActual` en lectura/resolución, `UsuarioActual` para reportar; [router](../../backend/app/administracion/router.py); validar con pruebas negativas | Backend + QA | **Control existente; prueba negativa a confirmar** |
| T13-06 | Denegación | API ↔ MySQL; producción 512 MiB | Intentos masivos de login/scrypt saturan cuota y degradan catálogo | 2 | 3 | **6 alto** | Límite de intentos 429, `HEAVY_WORK_SLOT`, cuotas Compose y métricas; ensayar ráfaga sin afectar producción | Backend + Operación | **Parcial; ensayo de carga pendiente** |
| T13-07 | Manipulación | API → MySQL ↔ volumen de fotos | Fallo entre commit SQL y escritura/borrado del archivo produce inconsistencias | 2 | 2 | **4 medio** | Compensación existente, reconciliación y backup restaurable faltantes; [riesgos arc42](../arc42/11-riesgos-y-deuda-tecnica.md) | Backend + Operación | **Riesgo residual aceptado provisionalmente** |
| T13-08 | Divulgación | Navegador ↔ API | Exposición de perfil personal o catálogo más allá de audiencia prevista | 2 | 2 | **4 medio** | Minimizar respuestas, no publicar correo en catálogo, revisar CORS y permisos; prueba de endpoints públicos y autenticados | Backend + QA | **Revisión de minimización pendiente** |
| T13-09 | Repudio | API → registros de operación | Acciones dañinas no atribuibles a una solicitud sin exponer credenciales | 2 | 2 | **4 medio** | Logs estructurados con `request_id`, ruta y estado; revisar ausencia de valores personales en logs | Operación | **Control de correlación existente; privacidad por comprobar** |
| T13-10 | Manipulación | GHCR / Dokploy → API | Rollback a imagen equivocada o actualización que destruya volúmenes | 2 | 3 | **6 alto** | Digest inmutable, comando `up -d --no-deps --no-build api`, conservar MySQL y archivos; respaldo externo y restauración pendientes | Operación | **Parcial; no ensayar directamente en producción** |

**Orden de trabajo:** primero verificar T13-03 y T13-04 con escaneo/barrido y reporte; cerrar pruebas negativas T13-01/02/05; ensayar T13-06 en entorno aislado; planificar restauración T13-07/10. No confundir mitigación en código con prueba ejecutada en esta semana.

## 3. Análisis de dependencias y cadena de suministro

- **Inventario observado:** `fastapi==0.141.1`, `pydantic==2.13.5`, `uvicorn==0.53.0`, `PyMySQL==1.2.0`, `python-multipart==0.0.20`, `Pillow==12.3.0`; [backend/requirements.txt](../../backend/requirements.txt). Flutter y dependencias Dart en [pubspec.yaml](../../frontend/campusmarket/pubspec.yaml).
- **Automatización propuesta:** [`s13-dependencias.yml`](../../.github/workflows/s13-dependencias.yml) ejecutará `pip-audit`, conservará salida JSON y resumirá hallazgos; no se afirma análisis ejecutado hasta tener URL de run, SHA, cantidad, identificadores y decisiones documentadas.
- **Hallazgo bajo investigación:** la versión `python-multipart==0.0.20` ya estaba señalada en feedback. **No afirmar vulnerabilidad confirmada ni seguridad de la versión** hasta revisar salida del scanner/avisos aplicables. Tampoco actualizar a ciegas por posible ruptura de compatibilidad.
- **Dart / imágenes:** no cubiertos por `pip-audit`; documentar la brecha y planear `flutter pub outdated`, revisión de advisories y escaneo de imagen o SBOM por separado.
- **Protocolo de revisión:** identificar CVE/advisory, paquete y versión vulnerable, alcance real en CampusMarket, decisión (corregir, mitigar, aceptar temporalmente con motivo), responsable, PR, prueba de regresión y run de cierre.
- **Evidencia por completar tras CI:** Run URL: **PENDIENTE**; commit: **PENDIENTE**; hallazgos reales: **NO OBSERVADOS**; clasificación de hallazgos: **PENDIENTE**.

## 4. Privacidad y base de tratamiento

**Datos reales del modelo:** nombre, correo y hash de contraseña de cuenta; ID, token opaco resumido por digest, expiración/revocación y registros de intentos para autenticación; identificador de propietario, títulos/descripciones, imágenes y metadatos de publicación; motivos de reporte, cuenta reportante, moderador, decisión y nota de moderación. Fotos y textos libres pueden contener información personal adicional introducida por usuarios.

| Datos / propósito | Base o justificación propuesta | Control y riesgo |
|---|---|---|
| Nombre y correo — alta, identidad y contacto funcional | Necesidad de prestar el servicio a cuentas registradas; **base jurídica específica por validar** según política institucional y norma aplicable | Acceso autenticado a `/usuarios/me`; evitar exponer correo a terceros |
| Contraseña (solo derivado scrypt), token de sesión digerido e intentos | Seguridad y autenticación del servicio; **validación legal pendiente** | No almacenar contraseñas en claro; restringir acceso; política de retención por definir |
| Publicación, propietario e imágenes | Ejecutar funcionalidad solicitada y mostrar ofertas; consentimiento/información de publicación a verificar | Visibilidad pública, eliminación y EXIF eliminado; fotos podrían revelar identidad |
| Reportes y decisiones de moderación | Protección de la comunidad y gestión de abuso; **base y aviso de privacidad por formalizar** | `ModeradorActual` restringe lectura; definir plazos de conservación |

**No se afirma cumplimiento legal definitivo**: el equipo debe determinar responsable del tratamiento, aviso de privacidad, base jurídica exacta, derechos de acceso/corrección/supresión, conservación y procedimiento de incidentes conforme a la regulación colombiana aplicable antes de producción institucional sostenida. **Principio de minimización:** solo datos necesarios por función, mensajes de error sin credenciales, evitar volcar cuerpos HTTP o tokens a logs, controlar distribución de reportes y depurar metadatos de fotografías.

## 5. Riesgos de IA generativa

[ADR-0010](../adr/0010-no-incorporar-componente-generativo-en-campusmarket.md) declara ausencia de LLM en ejecución. Por tanto **prompt injection, fuga de contexto de RAG y envenenamiento de retrieval no son vectores actuales del producto**. Riesgo distinto: copiar datos personales, código sensible o secretos a herramientas de IA durante desarrollo; registrar usos en [docs/ia.md](../ia.md), minimizar entradas y revisar salidas. Si se incorpora generación en el futuro, exigir nuevo ADR y modelado de amenazas de proveedor, prompts, datos y salidas.

## 6. Decisiones arquitectónicas

Este documento **no cambia** estructura ni código de producto: propone observación, controles de pipeline y validaciones sobre mecanismos existentes. No requiere un ADR nuevo para declarar la ejecución de auditoría de dependencias. Cualquier modificación estructural (nuevo proxy, almacén de secretos, contenedor, autenticación distinta o herramienta generativa) requerirá **ADR nuevo**, pruebas y cambio C4 antes de implementarla.

## 7. Matriz S13, estado honesto antes de CI

| Criterio de ficha | Estado | Evidencia |
|---|---|---|
| Amenazas vinculadas a C4 | Documentado | §1–2 |
| P e I, prioridad | Documentado | §2, fórmula y orden |
| Mitigación, dueño y estado | Documentado | §2 |
| Plan ataca prioridad alta | **Preparado, ejecución parcial** | §2–3, faltan escaneo y pruebas |
| Scanner en CI y URL de run | **Pendiente** | workflow nuevo; ejecución por confirmar |
| Hallazgos revisados | **Pendiente** | requiere JSON real |
| Privacidad y base | **Parcial** | §4; base jurídica precisa por validar |
| LLM, si existe | **No aplica por ADR-0010** | §5 |
| arc42 §8 | **Pendiente de anexo** | §4 y [arc42](../arc42/08-conceptos-transversales.md) |
| arc42 §11 | **Pendiente de anexo** | §2 y [riesgos](../arc42/11-riesgos-y-deuda-tecnica.md) |
| ADR estructural | **No aplica al cambio documental/CI actual** | §6 |

**No reclamar 11/11 hasta completar la ejecución del pipeline, revisión del informe y validación documental.**