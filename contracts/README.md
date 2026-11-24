# Contrato HTTP de CampusMarket

El [contrato vigente v2](openapi-v2.json) describe la API de FastAPI, desde salud y catálogo público hasta operaciones autenticadas de publicaciones, usuarios, favoritos, mensajería y moderación. El [contrato v1](openapi-v1.json) conserva las tres operaciones del laboratorio S7. La [decisión de compatibilidad](../docs/adr/0020-preservar-contrato-v2-y-adaptar-consumidor-incompatible.md) explica cómo evolucionó el consumidor.

## Verificación

Desde la raíz del repositorio:

```bash
python -m pytest backend/tests/test_contrato_openapi.py -q
```

La prueba compara el documento versionado con el esquema expuesto por el
proveedor. Si se elimina o renombra una ruta, operación, campo o respuesta sin
evolucionar el contrato, la comparación falla.

## Generación de cliente del laboratorio S7

En S7 se comprobaron los `operationId` de v1 generando un cliente
Dart con OpenAPI Generator 7.25.0:

```bash
npx --yes @openapitools/openapi-generator-cli@2.25.2 generate \
  -i contracts/openapi-v1.json \
  -g dart \
  -o tmp/s7-client \
  --additional-properties=pubName=campusmarket_api_client,pubVersion=1.0.0
```

El resultado se mantiene como artefacto reproducible del laboratorio y no se
incorpora al producto mientras el frontend continúe utilizando su cliente
Dart mantenido por módulo. El comando reproduce la generación histórica sobre v1.

## Regla de evolución

1. Proponer primero el cambio en este contrato.
2. Clasificarlo como compatible o incompatible.
3. Actualizar proveedor y consumidor en el mismo PR o planificar coexistencia.
4. Ejecutar la prueba de contrato antes de fusionar.
5. Para cambios incompatibles, publicar una nueva versión mayor y no sustituir
   silenciosamente la versión consumida.
