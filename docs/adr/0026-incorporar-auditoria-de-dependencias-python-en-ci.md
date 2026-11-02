# ADR-0026 — Incorporar auditoría automatizada de dependencias Python en CI

- **Estado:** Propuesto para aceptación del equipo
- **Fecha:** 2026-11-01 (Colombia)
- **Ámbito:** proceso de integración y cadena de suministro del backend
- **Relacionado:** [T13-03 en S13](../evidencias/evidencia-s13-amenazas-2026-11-01.md), [ASP-S13-01](../aspectos.md), [arc42 §8](../arc42/08-conceptos-transversales.md)
- **Implantación comprobada:** PR [#79](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/pull/79), merge `049dc30ceac1386b648bef5f6713c050762e2dbf`.

## Contexto y problema

CampusMarket recibe entradas no confiables desde el cliente y procesa imágenes mediante dependencias Python. Versionar paquetes no demuestra que carezcan de vulnerabilidades conocidas. S13 identificó T13-03 en la frontera GitHub Actions → dependencias → imagen de API. La primera ejecución de `pip-audit` detectó **51 entradas de aviso** al analizar 16 paquetes; algunas entradas se repiten y no representan 51 defectos independientes. Se señalaron `python-multipart==0.0.20` y `Pillow==12.3.0`.

## Alternativas

| Alternativa | Ventaja | Riesgo / costo |
|---|---|---|
| A. Inspección manual periódica | Sin nuevos jobs | Detección irregular y difícil de auditar |
| B. Auditoría informativa sin bloquear | Visibilidad temprana | Puede integrar cambios con hallazgos sin decisión |
| **C. Auditoría en CI con fallo explícito** | Evidencia repetible y no oculta hallazgos | Requiere mantener herramienta, revisar falsos positivos y disponibilidad de fuentes |

## Decisión

**Adoptar C**: ejecutar `pip-audit` en [workflow S13](../../.github/workflows/s13-dependencias.yml) para [dependencias Python](../../backend/requirements.txt); conservar JSON como artefacto y resumen en Actions. Cuando encuentre vulnerabilidades o errores de ejecución, el job falla y exige revisión. Este control no sustituye tests, análisis estático, revisión humana ni análisis de otros ecosistemas.

No añade contenedores, redes ni servicios; **sí cambia el proceso de control de integración**. No reescribe ADR anteriores.

## Evidencia y mitigación

- [Primer run — hallazgos](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41360317202): 16 paquetes y 51 entradas de avisos; JSON conservado.
- [Corrección en PR #79](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/pull/79): `python-multipart` 0.0.20 → 0.0.33; `Pillow` 12.3.0 → 13.0.0, con regresiones.
- [Run de remediación](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41362904998): 16 paquetes, **0 avisos reportados**, salida 0.
- [Commit fusionado y checks de master](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/commit/049dc30ceac1386b648bef5f6713c050762e2dbf): comprobaciones exitosas, incluido el auditor.

## Consecuencias y riesgos aceptados provisionalmente

El escáner cubre el conjunto resuelto de paquetes Python; **no analiza Flutter/Dart, imágenes OCI ni secretos del historial**, ni acredita la imagen que ya estaba desplegada en Dokploy. Un resultado sin avisos no garantiza seguridad futura. Responsable propuesto: DevOps y backend; el equipo debe ratificar asignación nominal y estado del ADR. Las nuevas vulnerabilidades exigirán triage, actualización o aceptación documentada con responsable y fecha.

## Reconsideración

Revisar al cambiar ecosistema, gestor de dependencias, alcance del pipeline o cuando se requiera una herramienta con mejor cobertura. Cualquier cambio estructural adicional requiere nuevo ADR y revisión C4.

## Cadena de trazabilidad

S13 → [C4 L2](../c4/02-contenedores.puml) → T13-03 → **ADR-0026** → [requirements](../../backend/requirements.txt) → [workflow](../../.github/workflows/s13-dependencias.yml) → [runs](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41362904998) → [arc42 §8](../arc42/08-conceptos-transversales.md) / [§11](../arc42/11-riesgos-y-deuda-tecnica.md).
