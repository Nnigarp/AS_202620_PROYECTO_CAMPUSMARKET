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


## Amenazas residuales S13 — priorización provisional (2026-11-01)

[Modelo STRIDE y plan completo](../evidencias/evidencia-s13-amenazas-2026-11-01.md). Son riesgos **aceptados provisionalmente para documentación y ensayo aislado**, no una autorización institucional definitiva.

| Riesgo aceptado/provisional | Severidad inicial | Motivo y condición de aceptación | Responsable propuesto y próxima acción |
|---|---|---|---|
| T13-07 — inconsistencia MySQL/archivos tras crash | 4 media | Monolito sin transacción distribuida SQL+filesystem; compensaciones, pero falta reconciliación/backup verificables | Backend/operación: diseñar reconciliación y restauración aislada |
| T13-10 — recuperación productiva incompleta | 6 alta | Imágenes por digest y rollback sintético disponibles, pero no existe ensayo de restauración de respaldos de producción; **no considerar resuelto** | Operación: backup externo, prueba aislada y protocolo de reversión |
| T13-03 — dependencias/imágenes vulnerables | 6 alta | Versiones fijadas no equivalen a seguridad; el primer run reportó 51 entradas; [corrección Python en CI](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41362904998) dejó 0 avisos en 16 paquetes; todavía falta escaneo de Dart/OCI y nueva imagen productiva | DevOps: mantener auditoría Python y evaluar dependencias Dart/imagen en siguientes cambios |
| T13-04 — exposición de datos/secretos | 6 alta | No hay hallazgo confirmado; barrido HEAD + historial y revisión de logs aún pendientes | Backend/DevOps: ejecutar barrido sin revelar valores |
| T13-08 — base jurídica y minimización | 4 media | Datos personales presentes; no se acredita aviso, retención ni base legal precisa | Equipo y responsable institucional: validar el tratamiento y adoptar aviso |

No ejecutar pruebas destructivas ni restauraciones sobre los volúmenes productivos. Aceptar/documentar un riesgo no equivale a afirmar que está mitigado.


**Vinculación S13:** el [ADR-0026 propuesto](../adr/0026-incorporar-auditoria-de-dependencias-python-en-ci.md) trata el riesgo T13-03 en Python. Conservamos abiertos el análisis de Dart e imagen OCI, la revisión de secretos de todo el historial y la aprobación formal de bases de tratamiento de datos. Los riesgos históricos no se borran al actualizar la estrategia.

## Evaluación S14 — 2026-11-05

[Procedimiento, mediciones y ATAM reducido](../evidencias/evidencia-s14-ec01-2026-11-05.md), orquestador `e4f5c1026206a86c2df7d07f7a16479c807dd34b`, fuente de imagen `46ede525602161826b75273fbb12528e739908cc`. HTTP/MySQL real obtuvo 10/10 ≤2 s con 1.000 publicaciones sintéticas bajo 256 MiB/0,5 CPU por servicio. Chrome no acredita diez estímulos válidos: registra filtros anteriores y un fallo de preparación. **EC-01 completo sigue NO CONCLUYENTE**. No se atribuye causalidad ni se incorporan optimizaciones por preferencia.

| ID / origen | Componente y consecuencia | Estado / siguiente acción |
| --- | --- | --- |
| R14-01 / medición técnica S14 | Observador HTML/Flutter y consulta: estímulos no acreditados impiden inferir latencia visible | Pendiente: contrastar entrada real con observador independiente; conservar todas las muestras |
| R14-02 / límites del experimento | Red/dispositivo/carga: CI serial sin fotos ni universidad no representa toda experiencia institucional | Pendiente: mantener alcance; contraste autorizado antes de extrapolar |
| R14-03 / revisión técnica, no de pares | Recursos/consistencia: picos seriales sin OOM no prueban concurrencia, recuperación o consistencia SQL/fotos | Pendiente; T13-07/T13-10 y respaldos/rollback productivos permanecen abiertos |
| R14-04 / contraste documental | C4 L2/L3 conserva notas de despliegue antiguas; puede confundirse fuente/imagen/estado instalado | Pendiente para S16: reconciliar notas con arc42 §7 y evidencias sin reescribir ADR aceptados |

**Revisión entre pares S14: pendiente de recepción.** No hay observaciones auténticas en las fuentes consultadas. El seguimiento docente y esta revisión asistida por IA no se presentan como pares. Cuando se reciban, registrar para cada una origen/autor/fecha/enlace, componente, consecuencia y evidencia, respuesta motivada y estado **corregido, asumido o pendiente**. No se inventan observaciones para cerrar los criterios 6 y 7.

No se alteran estados históricos S10–S13: siguen pendientes copia externa, restauración SQL/fotos, rollback del host, configuración/montajes efectivos, seguridad de alcance limitado y la revisión de issue #33 contra la documentación S6 existente.
