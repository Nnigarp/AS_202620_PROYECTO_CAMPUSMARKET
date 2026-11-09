# CampusMarket — cliente Flutter

Cliente Web y Android del monolito CampusMarket: catálogo y filtros, sesión/perfil, publicaciones con fotografías, moderación, universidad declarada, Favoritos y conversaciones HTTP con actualización manual. La universidad visible no acredita matrícula; las publicaciones anteriores pueden no tenerla.

## Desarrollo y comprobación

Desde este directorio, con Flutter y el backend local disponibles:

```bash
flutter pub get
flutter analyze
flutter test
flutter run -d chrome --web-port=3000
```

La [configuración de API](lib/shared/api_configuration.dart) usa `CAMPUSMARKET_API_BASE_URL` mediante `--dart-define`: por defecto `http://localhost:8000` en Web y `http://10.0.2.2:8000` en el emulador Android. La [reproducción del backend y del emulador](../../README.md#reproducción-local) está en el README raíz. No introducir tokens ni credenciales en el bundle.

## Publicación y evidencias

La imagen integrada ya promovida compila Web con base href `/app/` y API `https://campusmarket.iscoutb.dev`; el [workflow de empaquetado](../../.github/workflows/release-incremento2.yml) conserva esa configuración. El bundle se sirve dentro de `api`, sin un contenedor Flutter adicional. Esta revisión documental no lo recompila ni publica.

Consultar [C4 L2](../../docs/c4/02-contenedores.md), [aceptación observada el 3/nov](../../docs/evidencias/cierre-productivo-incremento2-2026-11-03.md), [evidencia Web/Android del Incremento 2](../../docs/evidencias/incremento-2-universidad-visible-2026-11-03.md) y [auditoría S1–S14 del 8/nov](../../docs/evidencias/auditoria-documental-s1-s14-2026-11-08.md). Los resultados CI, la observación pública y los pendientes operativos se registran por separado; no implican una nueva aceptación humana.
