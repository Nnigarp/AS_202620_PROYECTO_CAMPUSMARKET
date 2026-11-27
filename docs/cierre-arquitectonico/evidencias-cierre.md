# Evidencias y auditoría del cierre S17

## Revisiones y procedencia

| Referencia | Identidad y alcance |
|---|---|
| S16 histórico | [c79c73d47936790b0f248bdea5c0a700ce8fe017](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/commit/c79c73d47936790b0f248bdea5c0a700ce8fe017), evaluado antes de la sustentación. |
| Base de S17 | [5f8928c266e83175a18d99e56c7fd6fe61244c4d](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/commit/5f8928c266e83175a18d99e56c7fd6fe61244c4d), 24/nov 07:39:29 Colombia. Confirmada por `ls-remote upstream`. Objeto anotado `final` en `6e4e889498f297e0db29a8d0b53ecd6eb2226bf8`, resuelto a esta base. [20 commits desde S16](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/compare/c79c73d47936790b0f248bdea5c0a700ce8fe017...5f8928c266e83175a18d99e56c7fd6fe61244c4d). |
| Implementación T y ajuste L | [7f9253c9bc6a1c85bf9b98af976299f191dbd15f](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/commit/7f9253c9bc6a1c85bf9b98af976299f191dbd15f) y [e69f28487923185a76429f673c5ca6bb102f45a1](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/commit/e69f28487923185a76429f673c5ca6bb102f45a1). |
| Documentación D y comprobaciones finales | [Historial de la rama del fork](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/commits/fix/cierre-arquitectonico/) · [runs posteriores a cada push](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions?query=branch%3Afix%2Fcierre-arquitectonico). Para validar un resultado usar el `head_sha` del run y el último commit de la rama. La revisión institucional y el merge quedan a cargo del equipo. |

## Contrato público e identidad de la imagen

El [run institucional previo](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/45395636283) terminó en fallo sobre la base S17. El catálogo y OpenAPI respondían, pero se esperaba el build del 3/nov. El 27/nov se contrastaron cuatro fuentes.

1. El [Compose institucional](../../deploy/compose.prod.yaml) fija el manifiesto `sha256:42a3258b215c9b06d26b92761e8d2c95a03642fb50032a112eda3a1d696d5a9d`. GHCR devolvió ese manifiesto y su config `sha256:9d8e94327c424d124a78b28bc2d120a8074239a9a127ae9c8915d4373faef329`. La etiqueta OCI de revisión identifica `4af0e620beab1aa344af1cdcc4f275252db66807`. [Publicación de la imagen](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/45340726731).
2. La cabecera pública de `/app/` informó ese mismo SHA y HTTP 200. El [registro operativo](../operacion/despliegue-ghcr.md) conserva la promoción humana del 24/nov. La medición S17 no inspeccionó el host productivo.
3. Git devolvió el mismo blob `8b49500e6e5a871f13327e8e0c705dab9497f193` para `contracts/openapi-v2.json` en el build anterior y el actual. El [resolutor](../../scripts/preparar_s10_referencias.py) obtuvo del fork el contrato esperado, con hash canónico `585d197f684f6b0b38b8182f2cf4c4c0a9d1b8fc73f7416f5e3f2b24901a0e92`. El candidato de preparación fue T. El plan del ensayo registra L, que añade únicamente el ajuste de lint. [Referencias](../evidencias/datos/s17-contrato-publico/references.json) · [plan](../evidencias/datos/s17-contrato-publico/plan.json).
4. Entre 17:09:58 y 17:10:28 de Colombia se completaron 58 GET. Los nueve criterios aprobaron, con 15/15 respuestas 200 de base, 15/15 rechazos 422 y 15/15 respuestas 200 tras adaptar el consumidor. Se conservaron todas las muestras. [Resumen](../evidencias/datos/s17-contrato-publico/resumen.json) · [observaciones](../evidencias/datos/s17-contrato-publico/observaciones.jsonl).

## Pruebas y límites

| Validación | Evidencia y alcance |
|---|---|
| Propiedad, modularidad, erosión, OpenAPI y guardas de medición | 27 pruebas locales aprobadas en la selección de `backend/tests/test_propiedad_datos.py`, `test_modularidad_s6.py`, `test_erosion_s9.py`, `test_contrato_openapi.py` y `scripts/test_medir_ec01_s14.py`. La guarda reconoce once tablas y señala el módulo infractor en un fixture. |
| Backend completo e idempotencia | La [suite institucional](../../.github/workflows/backend-tests.yml) usa MySQL 8.4, ejecuta pruebas funcionales, contrato OpenAPI, mutaciones y Gitleaks. El job de documentación ejecuta el mismo CLI utilizado localmente. |
| Documentación y análisis estático | Tres fixtures aprobados con markdown-it-py 3.0.0. El enlace ausente y la fila truncada devolvieron salida 1. Ruff aprobó tras L. La matriz general contiene 14 aspectos. El verificador también procesa las matrices suplementarias. |
| Flutter y flujo integrado | `flutter test --reporter expanded` aprobó 33 pruebas localmente. El workflow [Web/Android](../../.github/workflows/mvp-flujo-real.yml) ejecuta los recorridos con API y datos sintéticos. |
| Compose y persistencia | [Workflow](../../.github/workflows/compose-mvp.yml) del fork sobre la rama. Docker Desktop local no respondió. La recreación de contenedores en CI deja abierta la restauración desde copias. |
| Seguridad de dependencias | El auditor [S13](../../.github/workflows/s13-dependencias.yml) se activa con cambios de dependencias o del propio workflow. S17 no modifica paquetes del producto. El barrido de secretos del backend cubre checkout e historial desde la revisión especificada por el workflow. |

## Sonar y límites de seguridad

La API pública identificó el último análisis de master en `5f8928c`, el 24/nov a las 12:39:37 UTC. El Gate de ese análisis devolvió OK. El check informó 25 nuevas y cero hotspots nuevos. Una consulta independiente el 27/nov devolvió **25 incidencias abiertas** en el proyecto y rama consultados. La coincidencia numérica es propia de esta consulta. Se conservaron clave, regla, ruta, impacto y estado de cada incidencia. [Check](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/runs/138450759483) · [inventario](../evidencias/datos/s17-sonar-master.json).

| Clave con impacto HIGH en mantenibilidad | Disposición propuesta y prueba necesaria |
|---|---|
| AaGKyLOAfXH_OCHShqcj · complejidad 19, Publicaciones | Aplazar extracción de ramas transaccionales hasta caracterizar concurrentes, repetición y conflicto de claves. |
| AaD6-B5CXnO4Tmn1lOKu · complejidad 23, Catálogo | Separar preparación y enriquecimiento en seguimiento con pruebas de filtros y consultas en lote. |
| AaEDl5MKM1Oq-5Se4fTQ · texto de persistencia en servicio | Consolidar el literal al intervenir el mapeo de fallos y verificar el detalle HTTP actual. |
| AaEBsl_cDMRQps-2ki7j · texto de propiedad en servicio | Consolidar preservando la misma respuesta ante recurso inexistente y recurso ajeno. |
| AaCoxeHSH9A6RWBEzH67 · texto de persistencia en repositorio | Extraer una constante de módulo con prueba de la traducción de errores. |

La [regla aplicada a master](https://api.github.com/repos/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/rules/branches/master) exige PR y check `test`. Sonar y el job documental quedan fuera de los checks obligatorios de esa regla.

## Auditoría de los diez criterios S17

Estados según la [ficha](https://github.com/ISCOUTB/AS_202620_feedback/blob/4849b408e24bc9dfd63075ea29e4c31f25932f71/fichas/semana-17-cierre.md). T, L y D remiten a las revisiones de la primera tabla. El estado institucional depende de la revisión que llegue a master antes del cierre.

| Criterio | Estado en el candidato | Ruta, evidencia, revisión y límite |
|---|---|---|
| 1. Trabajo posterior | Cumple | T y L posteriores a la base #95. La comparación distingue S16 de S17. |
| 2. Matriz frente a lo recibido | No verificado | [Matriz](matriz-retroalimentacion.md), D. Faltan originales de jurado y pares. |
| 3. Clasificación | Cumple para fuentes disponibles | [Decisiones por fila](matriz-retroalimentacion.md), D. El conjunto completo depende del cotejo anterior. |
| 4. Justificaciones | Cumple para fuentes disponibles | RF-06 y RF-07 identifican riesgo, dependencia y condición verificable de cierre, D. |
| 5. Cambios enlazados | Cumple | [Referencia S10](../../.github/s10-produccion.json), [guarda](../../backend/tests/test_propiedad_datos.py), [CI](../../.github/workflows/backend-tests.yml) y [aspectos](../aspectos.md), T/L/D. |
| 6. Pruebas modificadas | Cumple | T/L. La guarda discrimina propietario, los [tests del CLI](../../scripts/test_verificar_documentacion.py) fallan ante dos clases de defecto. |
| 7. ADR | Cumple como propuesta documentada | [ADR-0027](../adr/0027-validar-trazabilidad-documental-en-ci.md), D. Pendiente ratificación nominal. |
| 8. Diagramas y arc42 | Cumple | [C4 L2](../c4/02-contenedores.md), [C4 L3](../c4/03-componentes-backend.md) y [arc42](../arc42/ARC42.md), D. FastAPI sirve Flutter Web y Publicaciones conserva el único escritor. El cambio afecta CI, sin delta gráfico. |
| 9. Pipeline del último cambio | Verificar al terminar los runs de D | [Actions de la rama](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions?query=branch%3Afix%2Fcierre-arquitectonico). Exigir coincidencia de SHA y conclusión success. |
| 10. Lección por integrante | No verificado como testimonio | [Retrospectiva](retrospectiva.md), D. Tres propuestas individuales pendientes de validación. |

## Matriz transversal del contrato

| Criterio | Estado | Evidencia, revisión y límite |
|---|---|---|
| Organización, nombre y visibilidad | Cumple | [API pública del repo oficial](https://api.github.com/repos/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET) devolvió `private=false`. |
| Estructura | Cumple | En la base existen README, docs/adr, docs/arc42, docs/c4, docs/aspectos.md y docs/ia.md. D conserva esas rutas. |
| Estado calificable | No verificado | Base y fecha en la tabla de revisiones. El corte del domingo 29/nov a las 23:55 Colombia y la integración institucional son posteriores a esta revisión. |
| Nombres de ADR | Cumple | D conserva la secuencia 0001–0026 y añade 0027 con nombre kebab-case. |
| ADR aceptados inmutables | No verificado para todo el semestre | S17 añade una decisión. Nueve archivos ADR históricos tienen más de un commit. Determinar si los deltas son correcciones o reemplazos exige revisar sus estados de aceptación. |
| Registro IA | Cumple en el candidato | [Entrada S17](../ia.md), D, con herramientas, decisiones descartadas y validación humana pendiente. |
| Pipeline, Sonar y Gate | No verificado en el futuro SHA institucional | Runs del fork por SHA y check Sonar de la base en este documento. Regla de rama y análisis tienen alcances distintos. |
| Secretos | No verificado para todo el historial | [Procedimiento Gitleaks](../../.github/workflows/backend-tests.yml), con tramo Git explícito y checkout. La conclusión depende del alcance del scanner. |
| Contribuciones | No verificado nominalmente | `git shortlog -sn` de la base mostró cinco firmas con 541, 38, 26, 19 y 10 commits. La correspondencia persona/cuenta requiere confirmación de los tres integrantes. |

## Reproducción en Windows y corrección de las pruebas de imagen

La primera ejecución completa con MySQL 9.3 aislado registró 138 aprobadas, una fallida y dos errores de pytest. La prueba de galería encontró ficheros de una ejecución anterior en la ruta local de uploads. Además, pytest intentó introducir el payload de 5 MiB en su variable de entorno de identificación del caso. Windows limita el tamaño de esa variable. Se repitió la suite con un directorio temporal de imágenes y se identificaron explícitamente los cuatro casos de archivo inválido. Se conservan el payload de 5 MiB + 1 y todas las aserciones. [Ajuste y activación de las cinco suites del fork](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/commit/5dd251fbc944a6265fc962ff187212e369d5610f).
