# Línea base S5 - Bloqueo temporal de SQLite

**Fecha:** 05/09/2026  
**Rama:** `S5-restriccion-persistencia`

## Objetivo

Medir el comportamiento actual del corte vertical de creación de publicaciones
cuando la persistencia SQLite se encuentra bloqueada temporalmente, antes de
realizar cualquier modificación relacionada con la restricción arquitectónica
de la Semana 5.

## Procedimiento

La medición utilizó una base SQLite temporal mediante
`CAMPUSMARKET_DB_PATH`.

Se realizaron los siguientes pasos:

1. Inicializar una base de datos limpia.
2. Mantener un bloqueo exclusivo sobre SQLite.
3. Ejecutar un `POST /publicaciones`.
4. Medir el tiempo de respuesta.
5. Verificar la cantidad de registros antes y después del intento.
6. Liberar el bloqueo.
7. Repetir la creación de la publicación.
8. Comprobar la recuperación normal del sistema.

## Resultado con SQLite bloqueada

| Métrica | Resultado |
|---|---:|
| HTTP obtenido | `500` |
| Tiempo de respuesta | `7.323 s` |
| Registros antes del intento | `0` |
| Registros después del intento | `0` |
| Escritura parcial | `No` |

## Recuperación después de liberar SQLite

| Métrica | Resultado |
|---|---:|
| HTTP obtenido | `201` |
| Tiempo de respuesta | `0.007 s` |
| Registros finales | `1` |

## Diagnóstico de línea base

La implementación actual conserva la integridad de los datos, ya que el
intento realizado durante el bloqueo no produjo una escritura parcial.

Sin embargo, el bloqueo temporal de SQLite genera una respuesta HTTP `500`
después de `7.323 s`. Este comportamiento no permite distinguir una
indisponibilidad temporal de persistencia de un error interno no controlado
y mantiene al cliente esperando durante varios segundos.

Una vez liberada la base de datos, CampusMarket recupera su funcionamiento
normal: la creación responde con HTTP `201` en `0.007 s`.

Estos resultados constituyen la línea base previa a la decisión
arquitectónica de S5 y serán comparados con la medición posterior a la
implementación.
