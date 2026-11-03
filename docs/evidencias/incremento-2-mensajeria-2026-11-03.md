# Incremento 2 — Mensajería privada (2026-11-03)

> **Estado de cierre:** código y pruebas del fork **VERIFICADOS** en `058f63f0882d388e40c85c347e406bb9777cb343`. 126 pruebas backend + 4 de contrato, 33 Flutter y 12 criterios en cada recorrido Chrome escritorio/móvil y Android. **Incremento 2 no desplegado.** Los apartados intermedios conservan resultados fallidos/pendientes de su momento; el cierre al final los actualiza. Checks oficiales todavía no ejecutados: PR no abierto.


## Alcance

Rama `feat/incremento-2-20261103` del fork Nnigarp. Corte posterior a [Favoritos probado](incremento-2-favoritos-2026-11-03.md). No se abre PR oficial sin autorización; no se modifica producción, Compose ni imágenes.

Archivos principales: `backend/app/mensajeria/`, registro en `main.py`; `lib/mensajeria/`, contacto desde detalle y destino Mensajes en shell. Contrato OpenAPI aditivo, fixture sintético y prueba de propiedad ampliados. Pruebas `test_mensajeria.py`, `mensajeria_test.dart` y recorrido real Web/Android ampliado con contacto, dos bandejas, envío comprador/respuesta vendedor y logout/login.

## Requisitos y seguridad

- POST `/conversaciones` con solo publicacion_id recupera contexto único (comprador autenticado, vendedor real). Autocontacto y anuncios ocultos/eliminados se rechazan.
- Bandeja/detalle/lectura/envío exigen ser participante y Bearer; ajeno e inexistente devuelven 404 equivalente. DTOs prohíben identidades adicionales. Correo/tokens no se exponen en mensajes/bandeja.
- Texto 1–2000 caracteres tras trim; paginado por cursor (50, máximo 100); bandeja 30, máximo 50. No WebSockets ni sondeo continuo.
- Clave por mensaje/remitente/contexto y bloqueo de conversación impiden duplicados concurrentes. Cambiar texto con misma clave devuelve 409. Envío y preview son una transacción MySQL.
- Ocultar/eliminar anuncio no publica detalles ni borra la historia privada; bloquea nuevos mensajes. No modifica tablas ajenas ni datos heredados.
- Flutter conserva nonce ante error incierto; no avanza el cursor por el ID de un envío y descarta respuestas al cambiar sesión. Logout vacía conversación y borrador en memoria.
- ADR-0001/0003/0012/0022 aplicables; no ADR/infraestructura/dependencias nuevas. Dos contenedores y presupuesto existente conservados.

## Pruebas previas a CI

Ruff aprobado. Nueve casos de frontera/sin MySQL: rutas exigen Bearer, composición de bandeja en lote y texto inválido rechazado antes de servicio. Validación local combinada de contrato/propiedad/frontera: 15 passed, 6 deselected (los cinco casos MySQL y una prueba de propiedad excluida por el filtro de nombres; se ejecutarán completos en CI). Gitleaks de checkout y diff verificados.

Pruebas Flutter preparadas: payload/identidad, cursor sin saltos, reintento con misma clave, respuesta tardía, diseño 320/390/1440 y limpieza de bandeja. No se declaran aprobadas antes de CI. Esta máquina carece de SDK Flutter y daemon Docker.

## Commits/runs y límites

El commit de implementación inicia los workflows del fork; SHA y resultados se añadirán después de verificar. **MySQL/Flutter/recorrido Mensajería: PENDIENTE.** No hay cambios productivos ni aprobación humana afirmada. Datos sintéticos, sin acceso a usuarios reales. No equivale a cifrado extremo a extremo, moderación de mensajes, política de retención aprobada ni ensayo de carga institucional.

### Primera ejecución y corrección del recorrido

Implementación/documentación: [`3b23980`](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/commit/3b239804b215338f2ab2b6e9dfd85f96a0b22176). [Backend 41584776751](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41584776751) aprobado en MySQL 8.4. [S10 41584776642](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41584776642) aprobado. Analyze/tests Flutter aprobados; compilación y recorrido pendientes al registrar este apartado.

[Recorrido 41584776511](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41584776511): Chrome escritorio/móvil enviaron y mostraron el mensaje del comprador, pero fallaron al segundo pageBack: con solo 200 ms entre dos pops, la transición todavía exponía dos tooltips Back. Se corrige únicamente el ensayo para esperar pumpAndSettle tras volver de chat; se mantienen ambos retornos, controles de identidad y todas las aserciones. No se cambia la navegación ni la lógica productiva.

### Resultados comprobados después de corregir navegación

- Backend [41584776751](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41584776751): **121 pruebas + 4 de contrato**, mutaciones y checkout limpio sobre `3b23980`.
- Flutter [41584776574](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41584776574): **27 tests**, analyze, dos mutaciones y builds Web/APK aprobados.
- Corrección del ensayo [`871865d`](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/commit/871865de804ae00a86d11993946d9c26108f115c). [Recorrido 41585402540](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41585402540): Chrome escritorio/móvil aprobaron **11 criterios**, incluido contacto, bandejas A/B, envío/respuesta, persistencia tras logout y todas las comprobaciones previas de Favoritos/EC-02/galería/moderación. Android aún en ejecución al registrar este apartado; no se lo presenta como aprobado. [Backend de corrección 41585402733](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41585402733) aprobado.

Contrato de Mensajería aditivo: se conservaron todas las rutas y esquemas previos de Favoritos/MVP. Solo resta registrar el recorrido Android y la validación conjunta del siguiente corte.

**Cierre Mensajería:** Android también aprobó [41585402540](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41585402540) sobre `871865d`: los tres flujos reales completaron 11 criterios. Implementación probada en MySQL, Flutter, Chrome escritorio/móvil y Android; no desplegada. La validación conjunta posterior a universidad visible queda en su evidencia.

## Cierre conjunto del Incremento 2

Fuente final `058f63f0882d388e40c85c347e406bb9777cb343`: **126 + 4 pytest, 33 Flutter y 12 criterios en cada uno de los tres recorridos reales**, con los seis jobs aprobados. Tabla de runs, correspondencia del SHA, propuesta de PR y límites en [validación conjunta](incremento-2-universidad-visible-2026-11-03.md#validación-conjunta-final--fuente-058f63f). Este corte está probado en el fork y todavía no desplegado.
