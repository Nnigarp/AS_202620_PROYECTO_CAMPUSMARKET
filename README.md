# CampusMarket

Marketplace universitario para publicar, consultar, vender y alquilar productos dentro de la comunidad universitaria.

## Frontend institucional: candidato probado, aún sin publicar — 2026-10-30

La interfaz pública continúa en [GitHub Pages](https://nnigarp.github.io/AS_202620_PROYECTO_CAMPUSMARKET/).
El dominio [campusmarket.iscoutb.dev](https://campusmarket.iscoutb.dev) sirve la API;
la inspección de `/app/` todavía devuelve `Not Found`. **El cumplimiento institucional de toda la solución sigue parcial.**

La rama de esta fase implementa Flutter compilado en GitHub Actions y servido en `/app/`
por el mismo contenedor FastAPI, conservando `/health`, `/docs` y el contrato del catálogo.
El [run 41094945507](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41094945507),
fuente `a9b6709a67f8036346acb64b9c2b9849ee355cf2`, pasó compilación, 15 pruebas backend,
7 pruebas Flutter y 10/10 criterios con Chrome, MySQL real y datos sintéticos.
Dos contenedores, límites de 256 MiB y 0,5 CPU cada uno; picos CI de 186,73 y 176,66 MiB.
La misma imagen se publicó sin reconstrucción en [GHCR](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41102641771), con digest `65d34f2d…`. **No se desplegó en Dokploy**.
El [mecanismo de promoción y rollback de API](docs/operacion/despliegue-ghcr.md) pasó el
[ensayo aislado 41133683253](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41133683253):
Compose sin build, respaldo/restauración sintéticos y sustitución exclusiva de API en ambos sentidos.
La recuperación productiva, sus montajes y la imagen anterior siguen sin acreditarse: **publicación bloqueada**.

Véanse [ADR-0025](docs/adr/0025-servir-flutter-precompilado-desde-fastapi.md),
[implementación y workflow](.github/workflows/web-institucional.yml) y
[evidencia, limitaciones y pasos pendientes](docs/evidencias/despliegue-publico-mvp-2026-10-04.md#fase-2--frontend-institucional-candidato-probado-en-ci--2026-10-30).
Un checkout Git sin el build mantiene la API sola; fusionar este cambio no publica Flutter.
El autodeploy de `master` sigue activo: coordinar su control antes de cualquier merge.

## Integrantes

- Joshua Tenorio Alvarez
- Camilo Martinez Berrio
- Nilver Garcia Pimentel

---

# Evolución y evidencias del proyecto

El README funciona como **puerta de entrada al estado vigente**. La evolución semanal no se repite completa aquí: se conserva mediante enlaces navegables a las decisiones, modelos, código, pruebas y evidencias que se fueron acumulando.

| Semana | Evolución principal | Evidencia / punto de entrada |
|---|---|---|
| **S1** | Problema, interesados, objetivos y trazabilidad inicial | [`docs/aspectos.md`](docs/aspectos.md), [`docs/ia.md`](docs/ia.md) |
| **S2** | Restricciones, escenarios de calidad, árbol de utilidad y C4 nivel 1 | [`docs/arc42/02-restricciones.md`](docs/arc42/02-restricciones.md), [`docs/arc42/10-escenarios-de-calidad.md`](docs/arc42/10-escenarios-de-calidad.md), [`docs/arc42/10-arbol-de-utilidad.md`](docs/arc42/10-arbol-de-utilidad.md), [`docs/c4/01-contexto.md`](docs/c4/01-contexto.md) |
| **S3** | Decisión del monolito modular y estrategia de solución | [`docs/adr/0001-usar-monolito-modular.md`](docs/adr/0001-usar-monolito-modular.md), [`docs/arc42/04-estrategia-de-solucion.md`](docs/arc42/04-estrategia-de-solucion.md) |
| **S4** | Corte vertical ejecutable Flutter → FastAPI → persistencia y CI | [`frontend/campusmarket/`](frontend/campusmarket/), [`backend/`](backend/), [`.github/workflows/backend-tests.yml`](.github/workflows/backend-tests.yml) |
| **S5** | Primera evaluación arquitectónica y evolución de persistencia hacia MySQL | [`docs/adr/0004-migrar-persistencia-a-mysql.md`](docs/adr/0004-migrar-persistencia-a-mysql.md), [`docs/arc42/09-decisiones.md`](docs/arc42/09-decisiones.md) |
| **S6** | Modularidad explícita, propiedad de datos y C4 nivel 3 | [`docs/evidencias/auditoria-modularidad-s6-2026-09-12.md`](docs/evidencias/auditoria-modularidad-s6-2026-09-12.md), [`docs/c4/03-componentes-backend.md`](docs/c4/03-componentes-backend.md), [`backend/tests/test_modularidad_s6.py`](backend/tests/test_modularidad_s6.py) |
| **S7** | Interfaces y contratos OpenAPI ejecutables | [`docs/evidencias/evidencia-s7-2026-09-15.md`](docs/evidencias/evidencia-s7-2026-09-15.md), [`contracts/openapi-v1.json`](contracts/openapi-v1.json), [`backend/tests/test_contrato_openapi.py`](backend/tests/test_contrato_openapi.py) |
| **S8** | Despliegue, operación, health check e infraestructura como código | [`docs/evidencias/evidencia-s8-2026-09-27.md`](docs/evidencias/evidencia-s8-2026-09-27.md), [`docs/arc42/07-vista-despliegue.md`](docs/arc42/07-vista-despliegue.md), [`infra/main.bicep`](infra/main.bicep) |
| **S9** | Catálogo materializado, verificación con IA, medición EC-01 y auditoría de erosión/dependencias | [`docs/evidencias/evidencia-s9-2026-10-01.md`](docs/evidencias/evidencia-s9-2026-10-01.md), [`docs/evidencias/evidencia-ec01-catalogo-s9-2026-10-01.md`](docs/evidencias/evidencia-ec01-catalogo-s9-2026-10-01.md), [`docs/evidencias/auditoria-s9-dependencias-secretos-2026-10-01.md`](docs/evidencias/auditoria-s9-dependencias-secretos-2026-10-01.md) |
| **S10** | Contrato cliente-servidor, estímulo `sale` incompatible, adaptación del consumidor y ADR-0020 | [`docs/evidencias/evidencia-s10-corte2-2026-10-11.md`](docs/evidencias/evidencia-s10-corte2-2026-10-11.md), [`docs/adr/0020-preservar-contrato-v2-y-adaptar-consumidor-incompatible.md`](docs/adr/0020-preservar-contrato-v2-y-adaptar-consumidor-incompatible.md), [`docs/ia-s10.md`](docs/ia-s10.md) |
| **S11** | Fallos parciales Flutter → FastAPI; diseño de idempotencia, decisión de no extraer Catálogo, riesgos y trazabilidad | [`docs/evidencias/evidencia-s11-2026-10-18.md`](docs/evidencias/evidencia-s11-2026-10-18.md), [`docs/adr/0021-mantener-catalogo-en-el-monolito-modular.md`](docs/adr/0021-mantener-catalogo-en-el-monolito-modular.md), [`docs/arc42/11-riesgos-y-deuda-tecnica.md`](docs/arc42/11-riesgos-y-deuda-tecnica.md), [`docs/aspectos.md`](docs/aspectos.md), [`docs/ia.md`](docs/ia.md) |
| **Evolución posterior a S9** | Marketplace responsive, gestión de publicaciones propias e imágenes | [`docs/adr/0011-gestionar-imagenes-de-publicaciones.md`](docs/adr/0011-gestionar-imagenes-de-publicaciones.md), [`docs/aspectos.md`](docs/aspectos.md), [`backend/tests/test_gestion_publicaciones.py`](backend/tests/test_gestion_publicaciones.py) |

Para una revisión automática o manual, la ruta recomendada es:

```text
README
  ↓
docs/aspectos.md
  ↓
escenario de calidad / C4 / ADR
  ↓
código
  ↓
prueba ejecutable
  ↓
medición o evidencia
```

Así se conserva la historia del proyecto sin duplicar en el README el contenido completo de cada evidencia semanal.

---

## Despliegue público del MVP — 2026-10-04

Revisión del repositorio auditada para S9: `b5f10a2c93836cad539a9a195f6a0911d4b3ca91`.

Frontend publicado desde `c38e0cf36a30dddec39f169b7618b7c6127e0a71`.

API observada con revisión `7856416795bb4accdf9d05e01adb470654875e56`.

El diff de `backend`, `frontend`, `contracts` y `deploy` entre esas revisiones y el commit auditado está vacío. Son hashes distintos con código relevante idéntico; no se atribuye el despliegue al commit documental.

- Frontend: https://nnigarp.github.io/AS_202620_PROYECTO_CAMPUSMARKET/
- API: https://campusmarket.iscoutb.dev
- Salud: https://campusmarket.iscoutb.dev/health
- OpenAPI interactivo: https://campusmarket.iscoutb.dev/docs
- Métrica: https://campusmarket.iscoutb.dev/ops/metrics/ec01
- [Evidencia pública y pendientes](docs/evidencias/despliegue-publico-mvp-2026-10-04.md)

El registro público inicial conserva 23 comprobaciones HTTP y observación de Inicio/detalle. La revisión del 4 de octubre de 2026 volvió a comprobar `/health` y `/docs` con HTTP 200 y el bundle Pages con la URL API Dokploy, sin la URL Azure antigua. La raíz del dominio API no aloja Flutter; el frontend está en Pages.

La recreación pública registrada corresponde solo a API, con publicación e imagen conservadas; MySQL no se recreó. Recreación de API/MySQL y EC-01 con 1000 filas se verifican separadamente en CI/Compose. EC-01 extremo a extremo público, moderación pública y flujo autenticado en navegador siguen fuera de ese alcance. El scanner Sonar en CI está pendiente de configuración/ejecución; el Quality Gate automático no basta para cerrar CONTRATO §8.

Véase el [complemento final S9](docs/evidencias/evidencia-s9-2026-10-01.md#17-complemento-final-de-auditoria-s9--4-de-octubre-de-2026).

---

# Estado arquitectónico vigente

CampusMarket utiliza un **monolito modular** en el backend.

Decisión principal:

- [ADR-0001 - Usar monolito modular](docs/adr/0001-usar-monolito-modular.md)

Contextos delimitados:

- `usuarios`;
- `publicaciones`;
- `catalogo`;
- `administracion`.

La persistencia vigente es **MySQL**. Usuarios, Publicaciones y Administración escriben únicamente sus tablas mediante sus repositories y PyMySQL; Catálogo consume lectura del servicio de Publicaciones. `db.py` comparte infraestructura.

La dirección por contexto es:

```text
router → service → repository → MySQL
```

Usuarios materializa identidad/sesiones; Publicaciones, gestión y galería; Catálogo, búsqueda/detalle; Administración, reportes y revisión. FastAPI registra los cuatro routers en una sola aplicación.

Véase [C4 Nivel 3](docs/c4/03-componentes-backend.md).

Reglas de frontera verificadas:

- `publicaciones` mantiene la propiedad de escritura de `publicaciones`;
- `catalogo` no importa `publicaciones.repository`;
- `catalogo` no usa PyMySQL directamente;
- `catalogo` consume capacidades de lectura expuestas por Publicaciones;
- Flutter no accede directamente a la base de datos;
- la dirección de Publicaciones permanece `router → service → repository → MySQL`.

La modularidad se verifica automáticamente mediante:

- [`backend/tests/test_modularidad_s6.py`](backend/tests/test_modularidad_s6.py)
- [`backend/tests/test_erosion_s9.py`](backend/tests/test_erosion_s9.py)

---

# Estado funcional vigente

CampusMarket materializa actualmente:

- Inicio responsive;
- Catálogo de publicaciones;
- búsqueda por texto;
- filtros por modalidad, estado y rango de precio;
- detalle de publicación;
- creación de publicaciones desde Flutter;
- carga de hasta tres imágenes por publicación;
- imagen principal y galería;
- listado de publicaciones propias;
- edición de publicaciones;
- cambio de estado operativo `disponible`, `reservado` y `vendido`;
- eliminación de publicaciones;
- persistencia MySQL;
- contrato OpenAPI v2 ejecutable;
- registro, login, perfil y logout revocable;
- reportes y moderación con capacidad comprobada;
- health check y degradación controlada cuando la persistencia no está disponible.

El flujo fue verificado tanto en Flutter Web como en Android.

## Identidad y alcance MVP

Registro, login, logout, usuario actual y perfil usan sesiones opacas revocables (ADR-0012). El propietario procede del token y se restringe en SQL. EC-02 se ejecuta con dos usuarios reales: 10/10 mutaciones ajenas rechazadas y datos intactos.

Reporte/moderación requieren sesión/capacidad; registro/perfil no conceden privilegios.

El token vive en memoria: recargar Web o reiniciar Android requiere login.

El MVP no verifica correo/afiliación ni incluye recuperación de contraseña, chat, pagos o logística. Las limitaciones y comprobaciones se detallan en la [auditoría de continuación](docs/evidencias/auditoria-mvp-continuacion-2026-10-03.md).

---

# Catálogo y S9

El aspecto **ASP-01 - Consulta y búsqueda de productos** fue materializado durante S9.

Decisión:

- [ADR-0009 - Materializar catálogo sin romper fronteras](docs/adr/0009-materializar-catalogo-sin-romper-fronteras.md)
- [ADR-0019 - Consultar imágenes en lote a través de Publicaciones](docs/adr/0019-consultar-imagenes-en-lote-a-traves-de-publicaciones.md)

Código principal:

- [`backend/app/catalogo/router.py`](backend/app/catalogo/router.py)
- [`backend/app/catalogo/service.py`](backend/app/catalogo/service.py)
- [`frontend/campusmarket/lib/catalogo/`](frontend/campusmarket/lib/catalogo/)

Pruebas:

- [`backend/tests/test_catalogo.py`](backend/tests/test_catalogo.py)
- [`backend/tests/test_ec01_catalogo.py`](backend/tests/test_ec01_catalogo.py)
- [`backend/tests/test_erosion_s9.py`](backend/tests/test_erosion_s9.py)
- [`backend/tests/test_propiedad_datos.py`](backend/tests/test_propiedad_datos.py)
- [`backend/tests/test_modularidad_s6.py`](backend/tests/test_modularidad_s6.py)

Mutaciones controladas:

- [`scripts/verificar_mutaciones_mvp.py`](scripts/verificar_mutaciones_mvp.py)

Evidencia:

- [`docs/evidencias/evidencia-s9-2026-10-01.md`](docs/evidencias/evidencia-s9-2026-10-01.md)
- [`docs/evidencias/evidencia-ec01-catalogo-s9-2026-10-01.md`](docs/evidencias/evidencia-ec01-catalogo-s9-2026-10-01.md)
- [`docs/evidencias/auditoria-s9-dependencias-secretos-2026-10-01.md`](docs/evidencias/auditoria-s9-dependencias-secretos-2026-10-01.md)

La medición inicial S9 de EC-01 registró 10/10 búsquedas dentro del umbral de 2 segundos con 1.000 publicaciones controladas.

La verificación posterior en CI/Compose ejecutó el escenario con MySQL real, HTTP loopback y la cuota del laboratorio, conservando el umbral de `<= 2 s`.

Estas mediciones no se presentan como una medición extremo a extremo de red desde un navegador público.

## Verificación con IA

La porción S9 fue construida con apoyo de IA y sometida a revisión del equipo.

El registro de criterio se conserva en:

- [`docs/ia.md`](docs/ia.md)

Durante S9 se documentaron explícitamente propuestas:

- aceptadas;
- corregidas;
- rechazadas con motivo técnico.

Entre las decisiones registradas se encuentran:

- aceptar Catálogo como porción real de S9;
- corregir lecturas N+1 mediante lectura en lote;
- rechazar acceso directo de Catálogo al repository de Publicaciones;
- rechazar aumentar la cuota de infraestructura para ocultar un defecto de rendimiento;
- rechazar retirar el umbral de EC-01;
- rechazar atribuir resultados de un SHA distinto al estado auditado;
- rechazar considerar los cuatro workflows verdes como prueba suficiente de Sonar scanner;
- rechazar incorporar un modelo generativo únicamente por tratarse de la semana de IA.

La decisión de no incorporar actualmente un componente generativo en el producto está documentada en:

- [ADR-0010 - No incorporar componente generativo en CampusMarket](docs/adr/0010-no-incorporar-componente-generativo-en-campusmarket.md)

---

# Imágenes de publicaciones

La estrategia de imágenes se documenta mediante:

- [ADR-0011 - Gestionar imágenes de publicaciones](docs/adr/0011-gestionar-imagenes-de-publicaciones.md)

Reglas principales:

- máximo tres imágenes por publicación;
- primera imagen como principal;
- orden determinista;
- formatos JPG, JPEG, PNG y WEBP;
- máximo 5 MiB por imagen;
- MySQL conserva metadatos y referencias, no BLOB/Base64;
- `catalogo` obtiene las imágenes mediante Publicaciones;
- en desarrollo local los archivos se sirven desde `/uploads`.

Pillow verifica contenido real, orienta/normaliza fotos y retira metadatos (ADR-0015).

Compose conserva fotos en volumen nombrado (ADR-0018), probado tras recreación.

En el despliegue público vigente, Flutter Web se publica mediante GitHub Pages y la API FastAPI se ejecuta en Dokploy.

Las imágenes se conservan en el volumen nombrado `publication_images` y MySQL utiliza el volumen `mysql_data`.

La verificación pública acreditó la recreación de la API conservando la publicación y su imagen. La recreación conjunta de API y MySQL está verificada en CI/Compose; no se atribuye esa prueba de recreación completa al entorno público.

---

# Contrato API

Contrato vigente:

```text
API 2.0.0
OpenAPI 3.1.0
```

Archivos:

- [`contracts/openapi-v2.json`](contracts/openapi-v2.json)
- `openapi-v1.json` se conserva como referencia histórica S7.

Prueba contractual:

- [`backend/tests/test_contrato_openapi.py`](backend/tests/test_contrato_openapi.py)

La prueba compara el contrato versionado con la superficie OpenAPI generada por FastAPI y detecta divergencias en:

- rutas;
- métodos;
- `operationId`;
- esquemas;
- campos requeridos;
- respuestas.

Operaciones materializadas incluyen, entre otras:

```text
GET    /health
POST   /usuarios/registro
POST   /usuarios/login
POST   /usuarios/logout
GET    /usuarios/me
PATCH  /usuarios/me
POST   /administracion/reportes
GET    /administracion/reportes
PATCH  /administracion/reportes/{report_id}
POST   /publicaciones
GET    /publicaciones
GET    /publicaciones/mias
PUT    /publicaciones/{publication_id}
PATCH  /publicaciones/{publication_id}/estado
DELETE /publicaciones/{publication_id}
POST   /publicaciones/{publication_id}/imagenes
GET    /catalogo
GET    /catalogo/{publication_id}
```

---

# Verificación histórica al cierre del PR #47

La verificación local previa a integración del 3 de octubre de 2026 terminó con:

```text
python -m pytest backend/tests -q
36 passed, 2 warnings

python -m pytest backend/tests/test_contrato_openapi.py -q
3 passed

flutter analyze frontend/campusmarket
No issues found!

git diff --check
sin errores
```

El PR #47 (`Producto Marketplace UI - catálogo, gestión e imágenes`) fue integrado a `master` después de que GitHub Actions y SonarQube Cloud finalizaran en verde.

El merge quedó registrado en:

```text
cd7e029ded6ad33bfff0ff33557bf8efbd34f50f
```

Los dos warnings locales corresponden a deprecaciones de dependencias y no a fallos funcionales de la suite.

---

# Verificación del checkpoint MVP

La continuación parte de:

```text
fda38976882fd5abcca8486b4b114efd28ca2b1c
```

Backend:

- 77 pruebas;
- diez mutaciones detectadas.

Flutter:

- `flutter analyze`;
- seis pruebas;
- dos mutaciones;
- build Web;
- APK debug.

Tres flujos completos producen:

- nueve comprobaciones;
- 19 capturas por plataforma.

Compose verifica:

- volumen;
- cuota;
- EC-02;
- diez búsquedas de 1000 filas para EC-01.

Estas cifras corresponden al SHA y los artefactos documentados en la evidencia correspondiente.

El resultado del HEAD de continuación, incluidos CI y SonarCloud, se registra en:

- [`docs/evidencias/auditoria-mvp-continuacion-2026-10-03.md`](docs/evidencias/auditoria-mvp-continuacion-2026-10-03.md)

No se considera un gate de otro hash como validación automática de un estado distinto.

---

# Tecnologías vigentes

| Elemento | Tecnología |
|---|---|
| Frontend | Flutter / Dart |
| Plataformas verificadas | Web y Android |
| Backend | FastAPI / Python 3.12 |
| Servidor ASGI | Uvicorn |
| Estilo arquitectónico | Monolito modular |
| Persistencia | MySQL 8.4 |
| Driver | PyMySQL |
| API | REST / HTTP(S) / JSON |
| Contrato | OpenAPI 3.1 |
| Pruebas | pytest |
| Análisis estático | Ruff / `flutter analyze` |
| Integración continua | GitHub Actions |
| Calidad | SonarQube Cloud |
| IaC vigente de laboratorio | Docker Compose (`deploy/compose.lab.yaml`) |
| IaC histórica S8 | Azure Bicep (`infra/main.bicep`) |
| Frontend público vigente | GitHub Pages |
| Backend/API público vigente | Dokploy |
| Persistencia pública vigente | MySQL 8.4 en servicio interno del Compose de Dokploy |
| Despliegue histórico S8 | Azure App Service + Azure Database for MySQL |
| Diagramas | PlantUML |

---

# Reproducción local

## Backend

Requisitos:

- Python 3.12;
- MySQL disponible;
- dependencias instaladas;
- variables de entorno configuradas.

Instalación:

```bash
pip install -r backend/requirements.txt
# Para pytest y TestClient:
pip install -r backend/requirements-dev.txt
```

Ejemplo de configuración PowerShell:

```powershell
$env:CAMPUSMARKET_DB_HOST="localhost"
$env:CAMPUSMARKET_DB_PORT="3306"
$env:CAMPUSMARKET_DB_USER="campusmarket_app"
$env:CAMPUSMARKET_DB_PASSWORD="<PASSWORD_LOCAL>"
$env:CAMPUSMARKET_DB_NAME="campusmarket"
$env:CAMPUSMARKET_DB_SSL="false"
```

Nunca versionar una credencial real.

Ejecución:

```bash
python -m uvicorn backend.app.main:app --reload
```

Backend local:

```text
http://localhost:8000
```

Health:

```text
http://localhost:8000/health
```

## Frontend Web

```bash
cd frontend/campusmarket
flutter analyze
flutter run -d chrome --web-port=3000
```

## Android Emulator

Con backend ejecutándose en el host:

```bash
cd frontend/campusmarket
flutter run -d emulator-5554 --dart-define=CAMPUSMARKET_API_BASE_URL=http://10.0.2.2:8000
```

`10.0.2.2` permite al emulador Android acceder al host local.

---

# Despliegue público vigente

La topología pública vigente es:

```text
Usuario
   ↓
Flutter Web
GitHub Pages
   ↓ HTTPS / JSON
FastAPI
Dokploy
   ↓
MySQL 8.4
   ↓
volúmenes persistentes
```

Frontend:

```text
https://nnigarp.github.io/AS_202620_PROYECTO_CAMPUSMARKET/
```

API:

```text
https://campusmarket.iscoutb.dev
```

Health:

```text
https://campusmarket.iscoutb.dev/health
```

OpenAPI interactivo:

```text
https://campusmarket.iscoutb.dev/docs
```

Infraestructura vigente para el laboratorio:

- [`deploy/compose.lab.yaml`](deploy/compose.lab.yaml)
- [`backend/Dockerfile`](backend/Dockerfile)

El Compose despliega:

- `api`;
- `db`.

La API y MySQL están limitados a la cuota documentada del laboratorio y utilizan volúmenes nombrados para persistencia.

El dominio público expone la API. Flutter Web permanece publicado independientemente en GitHub Pages.

---

# Despliegue histórico S8

Durante S8 se desplegó una línea base pública con:

```text
GitHub Pages → Azure App Service → Azure Database for MySQL
```

Frontend histórico S8:

```text
https://nnigarp.github.io/AS_202620_PROYECTO_CAMPUSMARKET/
```

Backend histórico S8:

```text
https://campusmarket-s8-api-nilver.azurewebsites.net
```

Health histórico:

```text
https://campusmarket-s8-api-nilver.azurewebsites.net/health
```

Infraestructura como código utilizada en S8:

- [`infra/main.bicep`](infra/main.bicep)

La plantilla declara App Service, Azure Database for MySQL Flexible Server y configuración dependiente del entorno. Las credenciales sensibles se suministran mediante configuración externa y parámetros seguros.

> Las URLs anteriores corresponden exclusivamente al despliegue histórico verificado en S8.
> El estado público vigente evolucionó posteriormente a Flutter Web en GitHub Pages y API FastAPI en Dokploy.
> Las evidencias de cada despliegue conservan sus hashes y resultados por separado; no se atribuyen resultados de una revisión a otra únicamente porque formen parte de la misma evolución del proyecto.
> Véase el apartado «Despliegue público vigente» y la evidencia asociada.

---

# Integración continua

Workflows:

- [`.github/workflows/backend-tests.yml`](.github/workflows/backend-tests.yml)
- [`.github/workflows/flutter-mvp.yml`](.github/workflows/flutter-mvp.yml)
- [`.github/workflows/mvp-flujo-real.yml`](.github/workflows/mvp-flujo-real.yml)
- [`.github/workflows/compose-mvp.yml`](.github/workflows/compose-mvp.yml)

El pipeline configura Python y MySQL, instala dependencias, verifica la base de datos, ejecuta análisis estático, pruebas funcionales/arquitectónicas y la prueba contractual OpenAPI.

La línea de CI del MVP verifica además:

- fronteras arquitectónicas;
- propiedad de datos;
- mutaciones controladas;
- contrato OpenAPI;
- Flutter;
- Web;
- Android;
- Compose;
- persistencia;
- cuotas;
- EC-01;
- EC-02.

SonarQube Cloud dispone de Quality Gate automático para el repositorio.

El scanner ejecutado explícitamente desde GitHub Actions continúa registrado como pendiente del contrato transversal; no se presenta el Quality Gate automático como sustituto de esa evidencia.

---

# Evidencia S9 — generación verificada y trazable

La evidencia S9 se concentra en la materialización y verificación del contexto **Catálogo**.

Cadena de trazabilidad:

```text
ASP-01
  ↓
EC-01
  ↓
C4 Nivel 3
  ↓
ADR-0009 / ADR-0019
  ↓
Catálogo / Publicaciones
  ↓
Pruebas funcionales
  ↓
Auditoría de erosión y propiedad
  ↓
Mutaciones controladas
  ↓
Medición EC-01
  ↓
Evidencia
```

Puntos de entrada:

- [`docs/aspectos.md`](docs/aspectos.md)
- [`docs/ia.md`](docs/ia.md)
- [`docs/adr/0009-materializar-catalogo-sin-romper-fronteras.md`](docs/adr/0009-materializar-catalogo-sin-romper-fronteras.md)
- [`docs/adr/0010-no-incorporar-componente-generativo-en-campusmarket.md`](docs/adr/0010-no-incorporar-componente-generativo-en-campusmarket.md)
- [`docs/adr/0019-consultar-imagenes-en-lote-a-traves-de-publicaciones.md`](docs/adr/0019-consultar-imagenes-en-lote-a-traves-de-publicaciones.md)
- [`backend/app/catalogo/service.py`](backend/app/catalogo/service.py)
- [`backend/tests/test_catalogo.py`](backend/tests/test_catalogo.py)
- [`backend/tests/test_erosion_s9.py`](backend/tests/test_erosion_s9.py)
- [`backend/tests/test_propiedad_datos.py`](backend/tests/test_propiedad_datos.py)
- [`scripts/verificar_mutaciones_mvp.py`](scripts/verificar_mutaciones_mvp.py)
- [`docs/evidencias/evidencia-s9-2026-10-01.md`](docs/evidencias/evidencia-s9-2026-10-01.md)
- [`docs/evidencias/auditoria-s9-dependencias-secretos-2026-10-01.md`](docs/evidencias/auditoria-s9-dependencias-secretos-2026-10-01.md)

La asistencia de IA se utilizó para generar, revisar y contrastar alternativas, pero las decisiones arquitectónicas permanecen bajo responsabilidad del equipo.

Las pruebas de mutación demuestran que las reglas de erosión y propiedad no solo pasan en el estado correcto: fallan ante defectos introducidos deliberadamente.

La auditoría de dependencias comprueba que los paquetes incorporados existen en sus registros oficiales y utiliza nombres legítimos.

La auditoría de secretos incluye código, configuración, ejemplos y documentación.

CampusMarket no incorpora actualmente un componente generativo en runtime. La decisión y sus motivos están documentados mediante ADR-0010.

---

# Documentación arquitectónica

Puntos de entrada principales:

- [arc42](docs/arc42/ARC42.md)
- [C4 Nivel 1](docs/c4/01-contexto.md)
- [C4 Nivel 2](docs/c4/02-contenedores.md)
- [C4 Nivel 3](docs/c4/03-componentes-backend.md)
- [Decisiones arquitectónicas](docs/arc42/09-decisiones.md)
- [Escenarios de calidad](docs/arc42/10-escenarios-de-calidad.md)
- [Árbol de utilidad](docs/arc42/10-arbol-de-utilidad.md)
- [Trazabilidad de aspectos](docs/aspectos.md)
- [Registro de uso de IA](docs/ia.md)
- [ADR](docs/adr/)
- [Evidencias](docs/evidencias/)


## Semana 12 — Arquitecturas de datos y eventos (2026-10-25)

- [Evidencia S12: tabla operación→garantía, caché e invalidación y matriz](docs/evidencias/evidencia-s12-2026-10-25.md).
- [ADR-0022: fuente de verdad MySQL y costo de reversión](docs/adr/0022-mantener-mysql-como-fuente-de-verdad-y-evitar-proyecciones-asincronas.md).
- [arc42 sección 8: consistencia y caché](docs/arc42/08-conceptos-transversales.md).
- [C4 nivel 2: contenedores productivos reales](docs/c4/02-contenedores.md) y [diagrama fuente](docs/c4/02-contenedores.puml).
- [Matriz de trazabilidad de aspectos](docs/aspectos.md) y [registro IA](docs/ia.md).

Estas decisiones no introducen infraestructura de mensajería productiva ni una caché que no exista. La evidencia del taller es una entrega separada. **El trabajo de `s12` solo será evaluable tras integrarse a `master` antes del cierre**; consultar en la evidencia los límites y comprobaciones pendientes.


### S12 — Adenda correctiva y auditoría de cierre

[Auditoría S12 por hash, nueve criterios, límites y matriz transversal](docs/evidencias/cierre-s12-2026-10-25.md). Se mantiene la evidencia original y el ADR-0022 sin reescritura. El resultado del commit correctivo depende del merge en master antes del cierre del aula.


## Taller aplicado Semana 12 — Mensajes y consistencia (prototipo aislado)

Prototipo académico `PublicacionCreada.v1` **sin conexión al backend de producción**. Python 3.12, estándar de biblioteca:

```bash
python -m unittest discover -s backend/tests -p 'test_taller_mensajes_s12.py' -v
python scripts/taller_mensajes_s12.py
```

[Contrato JSON](contracts/messages/publicacion-creada-v1.schema.json) · [ADR-0023](docs/adr/0023-probar-mensajes-aislados-sin-introducir-broker-productivo.md) · [Evidencia, 11 criterios y límites](docs/evidencias/taller-mensajes-s12-2026-10-25.md) · [CI específico](.github/workflows/s12-taller-mensajes.yml). No se modifica C4 ni se declara un broker desplegado.


### Taller S12 — Cierre correctivo de backoff (sin alterar ADR históricos)

El consumidor aplica espera real por defecto con `time.sleep` entre los intentos (2 s y 4 s). Las pruebas inyectan un sleeper de prueba que registra las esperas requeridas, manteniendo CI rápido sin eliminar la política temporal del código real. Véanse [pruebas del backoff](backend/tests/test_taller_mensajes_s12.py), [simulador](scripts/taller_mensajes_s12.py), [evidencia y adenda](docs/evidencias/taller-mensajes-s12-2026-10-25.md), [trazabilidad](docs/aspectos.md) y [registro de IA](docs/ia.md). La corrección no altera la arquitectura productiva ni reescribe el ADR-0023. El resultado definitivo depende de pruebas del nuevo commit y del `master` fusionado.
