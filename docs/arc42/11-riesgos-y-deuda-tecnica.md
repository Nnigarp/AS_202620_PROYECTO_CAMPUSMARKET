# 11. Riesgos y deuda técnica

Esta sección consolida los riesgos documentados en S10 y la evolución S11 sin alterar los hechos históricos de cada revisión.

## Riesgos registrados en S10

Fecha: 2026-10-11, America/Bogota. No sustituye los riesgos ya descritos en evidencias S8/S9.

| Riesgo o deuda | Estado y evidencia | Efecto en S10 |
|---|---|---|
| Scanner Sonar en pipeline | La [revisión docente preliminar](https://github.com/ISCOUTB/AS_202620_feedback/blob/master/revisiones/2026-2/AS_202620_PROYECTO_CAMPUSMARKET/semana-10-corte2.md) lo marca No cumple; el workflow vigente no ejecuta scanner. No se corrige ni se presenta un badge como ejecución. | CI funcional no equivale a cierre de CONTRATO 8. |
| Reescritura histórica de ADR aceptados | La misma revisión registra cambios antiguos en ADR-0002/0003/0005. S10 no altera esos archivos ni elimina el hallazgo. | El ADR-0020 es nuevo; esto no repara el historial anterior. |
| Permisos para controlar contenedores de Dokploy | [Evidencia pública S9](../evidencias/despliegue-publico-mvp-2026-10-04.md) registra rechazo de restart por permisos. El entorno de trabajo S10 no dispone de control Docker del despliegue. | Se elige incompatibilidad de consumidor; no se declara una caída o recuperación de MySQL no ejecutada. |
| Logs privados de producción | S10 obtiene request IDs reales y valida el emisor con pruebas del mismo código; no descarga logs privados de Dokploy. | Correlación pública comprobada; extracción de logs de servidor pendiente para la sustentación si el docente la exige. |
| Fuente de selección del escenario | Nilver informa que el docente autorizó al equipo a elegir uno. Se identifica expresamente S10-CT-01; la indicación oral no se presenta como una asignación escrita localizada en Git. | El docente conserva la validación de la consigna. |
| Catálogo pequeño y consumidor serial | La corrida mide el catálogo actual y un consumidor; no carga masiva. | No prueba escalabilidad, presión de memoria, throughput ni todo EC-01. |
| Factores externos de medición | Red, DNS, TLS, proxy y tráfico ajeno pueden afectar tiempos; mismo origen, revisión y secuencia sin reintentos. Se conservan todas las muestras. | Las latencias son del observador externo, sin atribuirlas a tiempo exclusivo del backend. |
| Consistencia de snapshots | Se compara el hash del catálogo público antes/después; otro usuario podría modificarlo legítimamente durante la corrida. | Igualdad observada no equivale a prueba de integridad de todas las tablas. |
| Registro IA y conservación de historia | Se añade S10 al final de [docs/ia.md](../ia.md) y el detalle en [docs/ia-s10.md](../ia-s10.md). No se elimina ni reescribe ningún registro anterior. | S10 mantiene la ubicación canónica y evidencia decisiones aceptadas/rechazadas. |
| Sustentación y pipeline en vivo | Solo el docente puede calificarlos durante la sesión. El workflow nuevo permite repetición manual. | No se otorga nota ni se marca C5 cerrado desde el repositorio. |

## Riesgos S11 — fallos parciales en integración Flutter → FastAPI → MySQL (2026-10-18)

La evidencia específica se encuentra en [`docs/evidencias/evidencia-s11-2026-10-18.md`](../evidencias/evidencia-s11-2026-10-18.md) y la decisión en [ADR-0021](../adr/0021-mantener-catalogo-en-el-monolito-modular.md).

| Riesgo | Impacto | Mitigación actual verificada en código / deuda explícita |
|---|---|---|
| Respuesta inexistente a `POST /publicaciones` | Resultado incierto de escritura | Flutter aplica timeout; **pendiente** identificar operación/reconciliar sin reintento ciego |
| Respuesta tardía | UX y duplicación por segundo intento | 20 s por etapas en cliente; **pendiente** prueba con inyección de latencia, política de deadline global |
| Solicitud repetida tras pérdida de respuesta | Publicaciones duplicadas | **Pendiente** Idempotency-Key persistida con unicidad SQL, transacción y pruebas seriales/concurrentes |
| MySQL indisponible | 503 y catálogo no disponible | 503 controlado y rollback de errores MySQL; **pendiente** prueba de inyección y recuperación en Compose aislado |
| Crash/error entre disco y MySQL para fotografías | Archivos huérfanos o referencias inválidas | Compensación existente de registro fallido; **pendiente** reconciliador persistente ante crash y borrado fallido |
| Extraer Catálogo prematuramente | Más fronteras de red, costo y sincronización | ADR-0021 decide no extraer ahora; reevaluar con pruebas de capacidad y requisitos medidos |

**Estado de validación:** inspección estática del `master` base, no pruebas S11 ejecutadas ni verificación del entorno remoto. La ficha S11 admite mitigaciones diseñadas y claramente pendientes con plan; las pruebas de fallos siguen como deuda para el proyecto final. Conservar los riesgos S10 anteriores, sin sobrescribirlos.


## Riesgos residuales del despliegue Web institucional — 2026-11-01

| Riesgo | Estado verificable | Mitigación / siguiente control |
|---|---|---|
| Ausencia de respaldo externo de MySQL y fotos | **Abierto:** volúmenes montados y datos visibles, pero no hay restauración desde backup acreditada | Configurar almacenamiento y backup externo; ensayar recuperación sin comprometer producción |
| Rollback de aplicación no ejecutado en Dokploy | **Abierto:** imagen antigua reconstruida, probada con MySQL sintético y publicada por digest; sin reversión real del servidor | Realizar simulacro controlado en entorno equivalente con permisos y datos de prueba; verificar compatibilidad de esquema |
| Uso futuro del comando predeterminado de Dokploy | **Abierto:** `--build --remove-orphans` no equivale a promoción dirigida de `api` | Documentar y revisar Run Command y Compose Path antes de cualquier Deploy; mantener Autodeploy desactivado hasta adoptar política |
| Brecha entre infraestructura académica histórica y vigente | **Mitigado documentalmente al integrarse esta adenda:** S8/Pages/Azure son históricos | Mantener sección de topología 2026-11-01 y enlaces a ADR/evidencia sin borrar la historia |
| Frontend y API compartiendo ciclo de vida | **Costo aceptado:** un cambio de frontend obliga a promover el artefacto `api` | Probar imagen única, fijar digest y validar `/health`, `/app/` y funcionalidades después de cada actualización |

Referencia: [ADR-0025](../adr/0025-servir-flutter-web-con-fastapi-en-servicio-existente.md), [evidencia institucional](../evidencias/cierre-web-institucional-2026-11-01.md). Ninguna de estas verificaciones prueba continuidad 24/7 ni recuperación tras pérdida del host.
