# Incremento 2 — Mensajería privada (2026-11-03)

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
