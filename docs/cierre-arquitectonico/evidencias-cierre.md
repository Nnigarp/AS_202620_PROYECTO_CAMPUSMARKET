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
| Backend completo e idempotencia | En Windows la repetición aislada sobre MySQL 9.3 aprobó **140/140** en 313,58 s, con una advertencia de deprecación de Starlette sobre el nombre de HTTP 422. Incluye las ocho pruebas de idempotencia. La [suite institucional](../../.github/workflows/backend-tests.yml) usa MySQL 8.4, ejecuta pruebas funcionales, contrato OpenAPI, mutaciones y Gitleaks. El job de documentación ejecuta el mismo CLI utilizado localmente. |
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
| 2. Matriz frente a lo recibido | No verificado | [Matriz](matriz-retroalimentacion.md), D. Faltan originales de jurado y pares; el comentario oral sobre colores correspondía a la presentación HTML, no al software. |
| 3. Clasificación | Cumple para fuentes disponibles | [Decisiones por fila](matriz-retroalimentacion.md), D. El conjunto completo depende del cotejo anterior. |
| 4. Justificaciones | Cumple para fuentes disponibles | RF-06 y RF-07 identifican riesgo, dependencia y condición verificable de cierre, D. |
| 5. Cambios enlazados | Cumple | [Referencia S10](../../.github/s10-produccion.json), [guarda](../../backend/tests/test_propiedad_datos.py), [CI](../../.github/workflows/backend-tests.yml) y [aspectos](../aspectos.md), T/L/D. |
| 6. Pruebas modificadas | Cumple | T/L. La guarda discrimina propietario, los [tests del CLI](../../scripts/test_verificar_documentacion.py) fallan ante dos clases de defecto. |
| 7. ADR | Cumple en el candidato | [ADR-0027](../adr/0027-validar-trazabilidad-documental-en-ci.md), implementado y aceptado por el equipo; [conformidad](retrospectiva.md#conformidad-del-equipo). |
| 8. Diagramas y arc42 | Cumple | [C4 L2](../c4/02-contenedores.md), [C4 L3](../c4/03-componentes-backend.md) y [arc42](../arc42/ARC42.md), D. FastAPI sirve Flutter Web y Publicaciones conserva el único escritor. El cambio afecta CI, sin delta gráfico. |
| 9. Pipeline posterior a los cambios técnicos | Cumple en a32e3ce; pendiente en el SHA documental posterior y en master | [Cinco runs por SHA](#verificación-independiente-del-candidato-a32e3ce). No trasladar automáticamente el resultado a otro SHA. |
| 10. Lección por integrante | Cumple según declaración conjunta | [Retrospectiva](retrospectiva.md#lecciones-individuales-confirmadas): tres lecciones para tres integrantes, confirmadas conjuntamente en el chat. |

## Matriz transversal del contrato

| Criterio | Estado | Evidencia, revisión y límite |
|---|---|---|
| Organización, nombre y visibilidad | Cumple | [API pública del repo oficial](https://api.github.com/repos/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET) devolvió `private=false`. |
| Estructura | Cumple | En la base existen README, docs/adr, docs/arc42, docs/c4, docs/aspectos.md y docs/ia.md. D conserva esas rutas. |
| Estado calificable | No verificado | Base y fecha en la tabla de revisiones. El corte del domingo 29/nov a las 23:55 Colombia y la integración institucional son posteriores a esta revisión. |
| Nombres de ADR | Cumple | D conserva la secuencia 0001–0026 y añade 0027 con nombre kebab-case. |
| ADR aceptados inmutables | No cumple históricamente | ADR-0002 ya estaba aceptado en `77e1323` y su texto se modificó posteriormente en [04fe631](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/commit/04fe631). ADR-0003 presenta también una [edición tras su aceptación](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/commit/df72b1c). S17 conserva esos archivos y añade 0027. |
| Registro IA | Cumple en el candidato | [Entrada S17](../ia.md), D, con herramientas, decisiones descartadas y conformidad humana registrada. |
| Pipeline, Sonar y Gate | No verificado en el futuro SHA institucional | Runs del fork por SHA y check Sonar de la base en este documento. Regla de rama y análisis tienen alcances distintos. |
| Secretos | No verificado para todo el historial | [Procedimiento Gitleaks](../../.github/workflows/backend-tests.yml), con tramo Git explícito y checkout. La conclusión depende del alcance del scanner. |
| Contribuciones | No verificado nominalmente | `git shortlog -sn` de la base mostró cinco firmas con 541, 38, 26, 19 y 10 commits. La correspondencia persona/cuenta requiere confirmación de los tres integrantes. |

## Reproducción en Windows y corrección de las pruebas de imagen

La primera ejecución completa con MySQL 9.3 aislado registró 138 aprobadas, una fallida y dos errores de pytest. La prueba de galería encontró ficheros de una ejecución anterior en la ruta local de uploads. Además, pytest intentó introducir el payload de 5 MiB en su variable de entorno de identificación del caso. Windows limita el tamaño de esa variable. Se repitió la suite con un directorio temporal de imágenes y se identificaron explícitamente los cuatro casos de archivo inválido. Se conservan el payload de 5 MiB + 1 y todas las aserciones. [Ajuste y activación de las cinco suites del fork](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/commit/5dd251fbc944a6265fc962ff187212e369d5610f).

## Primera ejecución remota del fork y clasificación de los avisos

El push [a8e8952](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/commit/a8e8952ab5602be7844bc86366508b815d7f7c9c) activó cinco workflows. [S10](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46075884002) y [Compose/persistencia](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46075883946) aprobaron. En [backend](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46075883867) aprobó documentación, pero Gitleaks detuvo el job antes de MySQL. El [informe redactado](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46075883867/artifacts/15234354800) contiene 26 alertas de regla `generic-api-key`, todas en el JSON de Sonar. Cada coordenada corresponde a un identificador consultable sin autenticación en la API de Sonar. Se limitó la [configuración](../../.gitleaks.toml) a esos valores exactos, esa ruta y esa regla. Una réplica del fichero válido dio salida 0 y añadir un valor sintético desconocido en el mismo campo y ruta produjo salida 1. El barrido del tramo configurado en CI devolvió 0 localmente.

El barrido adicional de todos los ancestros de esta rama produjo cinco alertas históricas. Sus commits, líneas y reglas coinciden con las cinco entradas del [barrido S10](../evidencias/s10/barrido-secretos-historial-redactado.json), clasificadas como identificadores públicos en [S9](../evidencias/evidencia-s9-2026-10-01.md). Conservamos el resultado negativo del historial completo. La verificación no implica ausencia universal de credenciales.

Los ocho enlaces a runs históricos en las catorce filas generales de aspectos respondieron a la API pública. Siete correspondían a ejecuciones exitosas y el ensayo incompatible a una ejecución fallida. La referencia externa a las normas del laboratorio también respondió HTTP 200.

Para EC-01 el script S14 fija el build `46ede525` y comprueba que coinciden código, imagen y revisión. Cuatro archivos de la aplicación Flutter cambiaron entre aquel build y la base actual. La repetición histórica aislada no certificaría la interfaz del build `4af0e620`. Cerrar RF-06 exige validar el observador sobre la imagen vigente con los recursos y el fixture declarados.


## Verificación independiente del candidato a32e3ce

Consulta de GitHub Actions del 27/nov/2026 a las 17:46 Colombia. Los cinco workflows tienen estado completed y conclusión success para el mismo [SHA técnico completo](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/commit/a32e3ce2f9a0ac57869652a41968c6bf9c77e6f2).

| Workflow | Run exacto | Conclusión |
|---|---|---|
| Backend y documentación | [46076400865](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46076400865) | success |
| Flutter MVP | [46076400859](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46076400859) | success |
| Compose y persistencia | [46076400866](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46076400866) | success |
| Contrato público S10 | [46076400937](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46076400937) | success |
| Flujo real Web y Android | [46076400841](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46076400841) | success |

En backend aprobaron ambos jobs (test y documentacion), incluidos Ruff, Gitleaks, contrato OpenAPI, pruebas funcionales y arquitectónicas y sensibilidad mediante mutaciones. La excepción Gitleaks se limita a valores enumerados, regla y ruta; se revisó el diff, pero no se repitió independientemente el ensayo sintético ni la consulta de Sonar de cada valor. Los resultados son del candidato técnico, no certifican el SHA que agrega este registro ni el futuro merge institucional. Consultar [runs de la rama](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions?query=branch%3Afix%2Fcierre-arquitectonico) y [Actions institucionales](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions) por el SHA efectivamente integrado.

### Condiciones de cierre académico

Pendientes: cotejo de los originales del jurado y pares (o confirmación explícita de su ausencia/exención por el docente), verificación de CI y Sonar del SHA institucional; la validación de las lecciones y la ratificación del ADR-0027 quedaron registradas el 27/nov. No se modifica el estado de esos criterios sin evidencia. La ficha S17 evalúa master al cierre, no el fork ni la etiqueta final. No se requiere otra sustentación ni un despliegue para este ajuste documental.


## Segundo candidato y actualización de procedencia

El 27/nov/2026 a las 18:05 Colombia se consultaron los cinco workflows completed/success para el SHA [`2b393a7136a3120b2df227ddd4fc322f2f5fa04c`](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/commit/2b393a7136a3120b2df227ddd4fc322f2f5fa04c).

| Workflow | Run exacto | Conclusión |
|---|---|---|
| Backend y documentación | [46079427723](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46079427723) | success |
| Flutter MVP | [46079427695](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46079427695) | success |
| Compose y persistencia | [46079427686](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46079427686) | success |
| Contrato público S10 | [46079427699](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46079427699) | success |
| Flujo real Web y Android | [46079427733](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46079427733) | success |

El integrante aclaró el 27/nov que la observación oral sobre colores y cuadros se refería a la presentación HTML, no al producto. Se retiró RF-11 como fila técnica y se corrigió la atribución en la matriz y retrospectiva. No se requiere cambiar Flutter ni promover una imagen por esa observación. Se mantiene pendiente el cotejo con originales; la ratificación y las lecciones se confirmaron posteriormente. Los runs citados acreditan 2b393a7, no el nuevo SHA documental ni master. Verificar las ejecuciones posteriores sin modificar las pruebas para forzar resultados.


## Conformidad y verificación del PR 96

El 27/nov/2026 a las 19:04 (Colombia), los tres integrantes, Nilver García Pimentel, Joshua Tenorio y Camilo Martínez, comunicaron conjuntamente en el chat de cierre que confirmaban sus respectivas lecciones individuales, aprobaban el ADR-0027 y autorizaban registrar la conformidad en GitHub. Es una declaración conjunta del equipo recibida en el chat, no tres firmas digitales independientes.

[Retrospectiva y conformidad](retrospectiva.md#conformidad-del-equipo) · [ADR-0027](../adr/0027-validar-trazabilidad-documental-en-ci.md) · [PR institucional #96](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/pull/96).

El candidato `e354c1b` registró cinco workflows exitosos en el fork y, según la pantalla del PR #96 aportada por el equipo, diez checks exitosos, uno omitido (s14-ec01) y ningún conflicto. [Backend](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46080840087) · [Flutter](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46080840006) · [Compose](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46080840040) · [S10](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46080840038) · [Web/Android](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46080840049). Los checks del nuevo commit de ratificación y del futuro master deben verificarse por separado. El check omitido no demuestra una nueva medición EC-01. Persiste la ausencia de originales del jurado y pares.
