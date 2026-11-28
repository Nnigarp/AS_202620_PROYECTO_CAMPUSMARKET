# ADR-0027 — Validar la trazabilidad documental en integración continua

- **Estado:** Aceptado por el equipo; implementado y verificado en CI
- **Fecha:** 2026-11-27 (Colombia)
- **Ámbito:** integración de cambios al monolito modular
- **Relacionado:** [RF-02 y RF-03](../cierre-arquitectonico/matriz-retroalimentacion.md), [arc42 §9](../arc42/09-decisiones.md)

## Contexto y problema

En S16 se recorrieron tres aspectos. El equipo ya disponía de un verificador de enlaces, anclas y matrices, pero un PR podía romper un destino sin ejecutar ese control. La evidencia de una decisión pierde valor si el lector no puede llegar al ensayo que la respalda.

## Alternativas

| Alternativa | Coste y consecuencia |
|---|---|
| Ejecutar el script a mano antes del cierre | Bajo coste de CI. El resultado depende de que alguien recuerde ejecutarlo. |
| Ejecutarlo dentro del job MySQL | Reutiliza Python. Una indisponibilidad de la base oculta el resultado documental. |
| Job independiente en el workflow de backend | Un checkout adicional. Permite ver si fallaron la documentación o la aplicación y ejecuta ambos controles en paralelo. |

## Decisión

Incorporar el job [documentacion](../../.github/workflows/backend-tests.yml) a las ejecuciones existentes. Instala el parser fijado por el verificador y comprueba su código de salida con tres repositorios sintéticos antes de analizar el checkout completo. Una referencia rota o una celda ausente hacen fallar el job. Los enlaces externos requieren cotejo con la fuente.

## Consecuencias y reconsideración

El control detecta errores estructurales. Una ruta válida puede apuntar a una prueba que ejercita otro comportamiento. Cada cambio de aspecto exige una lectura semántica por el revisor. Para exigir el job como condición de merge se requiere configurar la protección institucional. Revisar el coste si crece el corpus o cambia el parser.

## Evidencia

[Pruebas de sensibilidad](../../scripts/test_verificar_documentacion.py) · [Verificador](../../scripts/verificar_documentacion.py) · [Resultados S17](../cierre-arquitectonico/evidencias-cierre.md).

El [commit de implementación](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/commit/7f9253c9bc6a1c85bf9b98af976299f191dbd15f) incorpora el control que acompaña la revisión de [C4 L3](../c4/03-componentes-backend.md). El [primer run del fork](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46075883867) permite comprobar que documentación terminó correctamente aun cuando el barrido de secretos detuvo el job de backend.

## Verificación y ratificación

El job documental y sus pruebas aprobaron en [el candidato técnico a32e3ce](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46076400865) y en [el candidato documental 2b393a7](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/46079427723). El 27/nov/2026 a las 19:04 (Colombia), los tres integrantes, Nilver García Pimentel, Joshua Tenorio y Camilo Martínez, comunicaron conjuntamente en el chat de cierre que confirmaban sus respectivas lecciones individuales, aprobaban el ADR-0027 y autorizaban registrar la conformidad en GitHub. Es una declaración conjunta del equipo recibida en el chat, no tres firmas digitales independientes. [Registro de conformidad](../cierre-arquitectonico/retrospectiva.md#conformidad-del-equipo). La decisión conserva su alcance y no reemplaza ADR anteriores.
