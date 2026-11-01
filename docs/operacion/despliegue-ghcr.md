# CampusMarket — Despliegue Web por imagen verificada

Estado: **mecanismo probado en CI; publicación productiva BLOQUEADA, no ejecutada**.
Este es el procedimiento vigente. La [evidencia canónica](../evidencias/despliegue-publico-mvp-2026-10-04.md#actualización-verificada-imagen-publicada-y-mecanismo-aislado--2026-10-30)
conserva identidades, runs e incertidumbres; no reemplaza la autorización operativa.

## Imagen y configuración

```text
ghcr.io/nnigarp/campusmarket-web-candidate@sha256:65d34f2de8d035d5a9672be2e6a81bab759089da2fbe91bdca23a17f2f0463fd
Fuente: a9b6709a67f8036346acb64b9c2b9849ee355cf2
Image ID: sha256:15a6fee324bc315d27ab85674781dfd1bded727243cb6ff752370e70b5d6fd19
Prueba original: Nnigarp/.../actions/runs/41094945507, artefacto 12996575905
Publicación sin reconstrucción: Nnigarp/.../actions/runs/41102641771
```

[compose.prod.yaml](../../deploy/compose.prod.yaml) cambia únicamente `api.image` respecto al plan
anterior. Comparado con `compose.lab.yaml`, sustituye `api.build` por esa imagen. Se mantienen servicios
`api`/`db`, Environment funcional, MySQL 8.4, healthchecks, logs, dependencias y volúmenes;
256 MiB y 0,5 CPU por servicio. El anuncio aportado de 1 GB/seis contenedores no cambia estos límites.
El Compose activo `compose.lab.yaml` permanece intacto.

Cuando existan overrides efectivos de Dokploy con labels/redes, utilizar **todos esos archivos** y añadir
[compose.web.yaml](../../deploy/compose.web.yaml) al final. Su `build: !reset null` elimina el build heredado
sin retirar el routing. No combinar lab + prod suponiendo que `image` elimina `build`.
[Docker documenta el reset](https://docs.docker.com/reference/compose-file/merge/#reset-value);
se probó con Compose 2.38.2 en CI y 5.6.1 local. Otra versión debe pasar `config` antes de avanzar.
Si no se pueden obtener los archivos efectivos que conservan el routing, detenerse.

## Precondiciones que siguen pendientes

El operador autorizado debe acreditar lo siguiente **sin entregar secretos ni contenido de usuarios**:

1. Control del autodeploy `On Push` y ausencia de despliegues pendientes antes del merge o publicación.
   La [guía §3.5–3.6](https://github.com/ISCOUTB/iscoutb.dev/blob/main/README.md) permite control manual
   con Autodeploy desactivado o una rama protegida de publicación. Esta tarea no cambia ninguno.
   Con el estado aportado actual, fusionar puede ejecutar `up -d --build --remove-orphans`.
   Los vectores de este plan exigen Autodeploy pausado durante la ventana, también si después se usa
   una rama de publicación. Mantenerlo pausado hasta revisar su futura ruta Compose por imagen y rama;
   reactivarlo apuntando a lab/build permitiría que otro push sustituyera el candidato.
2. Proyecto efectivo `campusmarket-sistema-2zvsxj`, archivos Compose generados y envfile existente.
   Inspección selectiva de contenedores: Type/Name/Destination/RW de MySQL e imágenes, redes,
   cuotas efectivas, salud y reinicios. Los nombres deducidos del YAML no son evidencia física.
3. Respaldo consistente de SQL y uploads del mismo corte, fuera de los volúmenes activos, con hashes.
   Coordinar pausa de escritores o snapshot consistente; un dump transaccional con archivos copiados
   mientras cambian publicaciones no garantiza coherencia. Comprobar tablas InnoDB, ausencia de DDL
   y objetos adicionales antes de escoger opciones de `mysqldump`.
4. Restauración aislada verificada del respaldo por el custodio autorizado, sin exponer registros reales.
   El ensayo de esta rama prueba el **método con fixtures sintéticos**, no la recuperabilidad de producción.
5. `.Image` real de API anterior, copia recuperable fuera de la limpieza de imágenes, checksum del archivo,
   carga aislada comprobada e identidad conservada. El digest antiguo `f9eaabdb…` no se toma como rollback
   sin demostrar que corresponde a la API activa. Acreditar compatibilidad de esquema y archivos con ambas
   versiones. Esta rama no modifica SQL, pero la versión efectiva desplegada sigue sin identificarse.
6. Descarga permitida del digest nuevo **desde el servidor Dokploy** y comprobación de su Image ID/OCI,
   plataforma linux/amd64, memoria disponible para el reemplazo y disco suficiente.
   El pull anónimo exitoso del runner no demuestra conectividad/acceso del servidor.
7. Autorización expresa y capacidad operativa de actualizar exclusivamente `api`, conservando Environment,
   proyecto, dominio, labels, redes y volúmenes. Si solo se dispone del despliegue global, no comenzar.

Sin respaldo restaurable, montajes acreditados e imagen anterior recuperable, **NO PUBLICAR**.
El valor antiguo/cacheado de REVISION no demuestra el código desplegado ni la ausencia de volúmenes.

## Recoger la primera evidencia sin desplegar — 2026-10-31

La consulta nueva no depende de haber resuelto respaldos, rollback ni GHCR. Un operador que **ya tenga**
lectura de metadatos Docker en el servidor del servicio puede ejecutar la versión de esta rama:

```bash
python3 -m scripts.preparar_despliegue_web inventory \
  --project campusmarket-sistema-2zvsxj
```

No requiere `.env`, Compose efectivo ni credenciales SQL. Consulta únicamente los dos contenedores del
proyecto mediante labels y selectores cerrados: Image ID activo, referencia configurada, Type/Name/target/RW
de montajes y cuotas/estado. La inspección de imagen añade RepoDigests, plataforma y revisión OCI si existe;
una imagen sin etiquetas conserva su identidad. Su salida excluye Environment, Source del montaje y contenido
de MySQL/uploads. No descarga, guarda ni inicia imágenes/contenedores. La salida JSON puede ser revisada
antes de compartirla; un error de lectura sale con código 1 y omite stderr privado.

**Identificar imagen o verla en caché no demuestra recuperabilidad ni un pull desde el servidor.**
El inventario mantiene `production_deployment_blocked: true` y las comprobaciones de backup, rollback,
pull y autodeploy en falso. Un fallo de inspección no se atribuye automáticamente a permisos o a GHCR.

La revisión de acceso de esta tarea se limitó a perfil/menús y Overview filtrado por CampusMarket.
La sesión disponible no expuso administración/consola de servidor; Overview ofreció Deploy y Stop,
que no se ejecutaron y no proporcionan estos metadatos. No se acreditó acceso al daemon desde esa cuenta.
No se revisitaron Backups, Volume Backups, View Mounts, View Config ni Docker Terminal ya fallidos.
No se deduce el rol exacto de la ausencia de botones, ni se propone montar el socket o ampliar privilegios.

Si no existe una vía autorizada de lectura, el bloqueo mínimo es **obtener esa salida selectiva del servidor**
por un operador con acceso existente. No se necesitan contraseñas, datos de usuarios ni otorgar acceso
administrativo al proyecto. No hay un botón acreditado en la cuenta actual que sustituya esa evidencia.
Después de ese único paso se podrá decidir cómo conservar la imagen activa y respaldar sus volúmenes;
no se autorizan esas operaciones por haber recogido el inventario.

## Preflight implementado, sin desplegar

[preparar_despliegue_web.py](../../scripts/preparar_despliegue_web.py) solo ejecuta lecturas `config`,
`ps`, `inspect` e inspección de imagen. No descarga, construye, ejecuta contenedores ni lee SQL/archivos.
Contrasta configuración completa antes/después, Environment efectivo sin imprimirlo, routing, redes,
montajes físicos, cuotas y salud. Exige Image ID/digest/OCI aprobados y copia recuperable correspondiente
al Image ID activo. Una discrepancia o dato ausente termina con exit 1.

Las condiciones externas no pueden certificarse con `inspect`: el operador aporta referencias verificables,
con fecha ISO 8601 y zona horaria de los últimos 30 minutos. Es un registro de evidencia revisada,
no una casilla que este programa pueda acreditar automáticamente. Plantilla **incompleta, bloqueante**:

```json
{
  "scope": "production",
  "project": "campusmarket-sistema-2zvsxj",
  "checked_at": "PENDIENTE",
  "gates": {
    "authorization": {"verified": false, "evidence": ""},
    "autodeploy_paused": {"verified": false, "evidence": ""},
    "no_queued_deployments": {"verified": false, "evidence": ""},
    "consistent_backup_restored": {"verified": false, "evidence": ""},
    "rollback_archive_restored": {"verified": false, "evidence": ""},
    "schema_compatible": {"verified": false, "evidence": ""},
    "ghcr_pull_from_server": {"verified": false, "evidence": ""}
  },
  "rollback": {"image_id": "", "archive_sha256": ""}
}
```

Solo después de reunir esas evidencias, el operador podrá preparar un plan privado, fuera del checkout:

```bash
python3 -m scripts.preparar_despliegue_web prepare \
  --project campusmarket-sistema-2zvsxj \
  --env-file /ruta/al/envfile-existente \
  --file /ruta/al/compose-efectivo.yaml \
  --evidence /ruta/privada/evidencias.json \
  --out /ruta/privada/plan-web
```

Repetir `--file` por cada override efectivo, en su orden original. No inventar rutas ni copiar Environment
a Git. El directorio nuevo usa modo 0700; `plan.json` y `rollback.compose.json`, 0600. No subirlos como
artefactos públicos. El script no sobrescribe planes existentes y marca `executed: false`.
Se debe regenerar el plan si cambia el estado observado o transcurren 30 minutos.
Antes de ejecutar el vector de promoción autorizado, comprobar otra vez sin modificar servicios:

```bash
python3 -m scripts.preparar_despliegue_web verify \
  --plan /ruta/privada/plan-web/plan.json --mode ready
```

Este modo exige evidencia reciente, el mismo estado de contenedores y la configuración original.
Los modos posteriores comparan también hashes de configuración normalizada, sin almacenar Environment
en claro en el plan: cambios de variables, routing u otros campos desde el preflight se rechazan.
El verificador solo acepta prefijos Docker Compose y vectores API con opciones cerradas; no ejecuta
comandos arbitrarios introducidos en un plan editado. Los hashes detectan cambios; no constituyen firma
ni sustituyen la revisión y autorización humanas. Los planes anteriores deben regenerarse.

## Publicación y verificación, pendientes de autorización

Revisar el vector de argumentos `promote` del plan. Conserva el mismo proyecto, envfile y archivos,
añade el override Web y termina exactamente en:

```text
up -d --no-deps --no-build --pull never --wait --wait-timeout 180 api
```

El [significado de estas opciones](https://docs.docker.com/reference/cli/docker/compose/up/) evita
iniciar dependencias y reconstruir/descargar implícitamente. El digest debe estar presente y verificado
antes. El operador ejecutará ese vector solo con autorización, sin `eval`, `--build`, `--remove-orphans`,
`down`, Fresh Volumes, recreación de MySQL ni otra API simultánea. El generador no lo ejecuta.
No cambiar dominio ni variables de revisión para aparentar otra versión: la fuente de esta imagen es `a9b6709…`.

Después del comando, comprobar metadatos con:

```bash
python3 -m scripts.preparar_despliegue_web verify \
  --plan /ruta/privada/plan-web/plan.json --mode promoted
```

Este control exige la imagen esperada, salud, cuotas y persistencia/red de API y el mismo contenedor,
Image ID, StartedAt, montajes y red de MySQL. Completar manualmente la aceptación pública:

- HTTPS válido; `/app` redirige a `/app/`; Inicio → Catálogo → detalle → atrás y recarga funcionan.
- JS, iconos e imágenes cargan sin 4xx/5xx ni contenido mixto; no consultar información privada.
- `/health`: 200/ok; `/docs` y `/openapi.json`: 200; contrato y rutas API conservados.
- Contrastar digest/Image ID y fuente OCI con `/app/REVISION`, SHA del bundle y `X-CampusMarket-Revision`.
  La cabecera sola no identifica el código.
- Sin OOM, reinicios inesperados, pérdida de montajes ni exceso de límites. Registrar hora y resultado.

## Rollback exclusivo de API

Ante fallo de salud, identidad, navegación, assets, contrato, persistencia o recursos, detener la aceptación.
El vector `rollback` del mismo plan añade únicamente el Image ID anterior mediante `rollback.compose.json`
y usa las mismas opciones, siempre solo `api`. La copia previa debe estar cargada y verificada; `--pull never`
impide sustituirla por una descarga implícita. Verificar luego con `--mode rollback` y repetir salud/contratos
públicos correspondientes a esa versión. No restaurar SQL ni volúmenes automáticamente.

Si el Image ID anterior no está disponible, hay incompatibilidad de datos o cambia MySQL, escalar dentro
del equipo al operador autorizado y detener acciones. La garantía de recuperación debe resolverse antes
de publicar; este procedimiento no intenta suplirla durante una caída.

## Pruebas acreditadas de esta rama

[Run 41133683253](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41133683253),
commit `61a9171a6fff1ebfd53b869fc1b37aeb7d405461`: 14 pruebas y siete criterios CUMPLE.
El [workflow](../../.github/workflows/despliegue-web-seguro.yml) descarga el digest ya publicado;
el [ensayo](../../scripts/ensayar_despliegue_web.py) usa MySQL/PNG sintéticos, hace dump/TAR y los restaura
en otro proyecto efímero, conserva/carga la imagen de control y ejecuta los vectores reales del plan.
Promoción y rollback reemplazaron API sin cambiar MySQL ni perder publicación/imagen.

El control usa el mismo Image ID por ID/digest: demuestra el mecanismo, **no compatibilidad con una
versión anterior distinta**. La recuperación productiva continúa pendiente. Los respaldos y credenciales
sintéticos se eliminan; solo se publica JSON sin Environment ni datos de usuarios. No se repitieron los
seis workflows ya aprobados ni se reconstruyó/republicó el candidato.


Actualización de preflight/inventario, fuente `b92d0aae6c6b8bf4723e6fab0eafda01636f56b7`:
[run 41248754966](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41248754966),
**22 pruebas aprobadas** en el job `preflight`, incluidos selectores Docker reales con dos contenedores
creados pero nunca arrancados, volúmenes vacíos e imagen de fixture importada sin descargar GHCR.
Se comprobó exclusión de Environment sintético, lectura de montajes e imagen sin etiquetas OCI,
rechazo de planes/comandos alterados, deriva de configuración, ausencia conjunta de montajes y referencias
`null` que no sirven como evidencia. Cleanup elimina exclusivamente los fixtures del runner.
Los runs `41248522797` y `41248591027` fallaron respectivamente por omitir `-` en el import del fixture
y por el selector OCI ante etiquetas nulas; commits `a36da68` y `b92d0aa` los corrigieron.
El job `mecanismo` se omitió intencionadamente: Compose y operaciones del ensayo siguen idénticos a
`61a9171…`, por lo que se conserva la evidencia válida `41133683253`. Cambios futuros en esos archivos,
o solicitud manual explícita `full_trial`, activan el ensayo completo. No se repiten los seis workflows previos.

## Ensayo independiente en development — 2026-10-31

**Preparado y probado en CI; no creado ni desplegado en Dokploy.** Esta alternativa usa datos nuevos
exclusivamente sintéticos. La ausencia de recuperación productiva acreditada no impide preparar este
ensayo separado, ni queda resuelta por él. Los procedimientos productivos anteriores mantienen todos sus gates.

### Configuración y evidencia nueva

- Rama del fork: `ops/development-web-aislado-20261031`, desde `f63bfcf…`, sin modificar PR #1 ni PR #76.
- [Compose](../../deploy/compose.development.yaml), [ensayo](../../scripts/ensayar_development.py),
  [rechazos](../../scripts/test_ensayar_development.py) y [workflow](../../.github/workflows/development-web.yml).
- Imagen API/Web: el digest `65d34f2d…` y el Image ID indicados al inicio; fuente de imagen `a9b6709…`.
  No se reconstruyó Flutter ni se publicó ninguna imagen.
- MySQL independiente: `mysql:8.4@sha256:a0225d1ea6631c8bc2385dc4c2faba17bbf1834ecf369e1659a9a382bd8d5dd7`.
  Ese digest ya figuraba en el ensayo `41051624793`; el nuevo ensayo lo descarga y ejecuta por esa identidad.
- Base fija `campusmarket_development_test`, usuario `campusmarket_dev`; solo se interpolan
  `DEV_MYSQL_PASSWORD` y `DEV_MYSQL_ROOT_PASSWORD`, nuevas y diferentes. No hereda las variables `MYSQL_*` de production.
- Volúmenes lógicos `dev_mysql_data` y `dev_publication_images`, redes propias `default` y `dev_data` interna;
  sin `external`, `name` global, bind mounts, puertos publicados ni contextos build. La única exposición es `api:8000`.
- [Run final 41258568018](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41258568018),
  commit de código `0e670cc8678624c3d507cd87f27c476ba758f24c`: **10 pruebas y nueve criterios CUMPLE**.
  Artefacto `development-web-41258568018-1`, ID `13064196858`, ZIP SHA-256
  `02f8f154aba107e1f386e584daff3b5c99ce9950f31d1bc12e358dcd6c4a3eea`, descargado y contrastado.
  SHA-256 del Compose `74f7c65c16cf3ffbebe72f6597a34c35c22fd6024230db1ce540bc90d29764a8`.

Dos proyectos efímeros CI usaron claves distintas y marcadores SQL/uploads diferentes; TCP desde API a la
base del otro proyecto quedó bloqueado. SQL y PNG sobrevivieron a recrear ambos contenedores propios.
Detener únicamente la base sintética produjo HTTP 503 y API unhealthy; arrancarla recuperó ambos healthchecks.
El bundle conservó `/app/` y CORS aceptó el nuevo origen. No se repitió el build ni la aceptación Flutter previa.

El ensayo final sustituyó la API por una configuración que termina con código 1 y restauró la configuración
aprobada usando `up -d --build --remove-orphans`, equivalente al log real del panel. No había `build` en ninguno
de los servicios: no construyó imágenes. MySQL conservó contenedor, Image ID, StartedAt, reinicios y montajes;
la API recuperó el mismo digest y SQL/fotos. El proyecto testigo quedó intacto. Esto prueba rollback de
**configuración a la misma imagen**, no una reversión entre versiones con esquemas diferentes.

Límites efectivos CI: 268435456 bytes y 500000000 NanoCpus por contenedor. Picos observados en las muestras:
API/Web 195538944 bytes (186,48 MiB), MySQL 185278464 bytes (176,70 MiB), sin OOM/reinicios automáticos.
Cleanup terminó sin contenedores, redes o volúmenes propios; se retiraron las claves efímeras. Solo se conserva
el resultado selectivo, sin Environment, SQL, fotos o sesiones. El primer ensayo `41258330172`, fuente `e2799b0…`,
pasó nueve pruebas/nueve criterios; el final añade MySQL por digest y acredita el camino de rollback del panel.

### Preflight anterior a autorizar el nuevo servicio

1. **Cuota conjunta:** la [guía vigente](https://github.com/ISCOUTB/iscoutb.dev/blob/main/README.md)
   y [políticas](https://github.com/ISCOUTB/iscoutb.dev/blob/main/docs/politicas-uso.md) todavía indican
   512 MB/cuatro contenedores. El anuncio aportado de 1 GB/seis no acredita la asignación efectiva del proyecto.
   La lectura del panel confirmó development vacío, pero no expuso una cuota efectiva que resolviera la diferencia.
   Se necesita evidencia oficial vigente de al menos **1073741824 bytes (1 GiB) y cuatro contenedores sumando
   ambos entornos**, y confirmar que no hay otros servicios del equipo consumiendo esa asignación.
   No interpretar 1 GB decimal como 1 GiB ni comprobar el límite agotando memoria. Sin esa evidencia, no crear/desplegar.

   | Entorno | Contenedores | Suma de límites de memoria |
   |---|---:|---:|
   | production actual, según Compose | 2 | 512 MiB |
   | development propuesto | 2 | 512 MiB |
   | Total propuesto | 4 | 1024 MiB |

2. **Permisos y separación:** usar únicamente `campusmarket → development`, actualmente vacío.
   `Create Service` visible no demuestra que el servidor aceptará el alta; si la deniega, detenerse.
   Debe ser un Compose nuevo, con identificador/appName/proyecto nuevo, distinto de
   `campusmarket-sistema-2zvsxj`. No clonar `production/sistema` ni trasladar sus variables o montajes.
3. **Fuente:** comprobar que la rama elegida contiene el Compose con el hash anterior y el código probado
   `0e670cc…`. El fork es público: el proveedor Git por HTTPS no requiere SSH ni ampliar permisos de GitHub App
   ([documentación de proveedores](https://docs.dokploy.com/docs/core/providers#git)). Si no está disponible,
   detenerse; no cambiar permisos, proveedor o credenciales de production.
4. **Routing/registro:** `dev-campusmarket.iscoutb.dev` debe estar libre dentro del espacio del equipo;
   no sustituir ningún dominio existente. El pull de este digest se acreditó en CI, no en Dokploy.
   La futura autorización del primer ensayo debe incluir su descarga en el nuevo servicio; un fallo de pull
   detiene el ensayo y no autoriza cambiar visibilidad, credenciales ni usar otra imagen.
5. **Autorización expresa:** crear/configurar/desplegar este servicio y, si falla, detener o revertir únicamente
   el nuevo ensayo. No incluye merge, Pages, cambios al autodeploy de production ni operaciones sobre sus datos.

### Configuración posterior desde el panel, solo con autorización

1. `campusmarket → development → Create Service → Compose`; nombre `web-ensayo`.
   Antes de conectar el repositorio, dejar **Autodeploy OFF en este servicio nuevo**, sin pulsar Deploy/Rebuild.
   En **Advanced**, activar **Enable Isolated Deployment**, aunque aparezca Deprecated. No tocar el de production.
2. **General → Provider → Git**: HTTPS URL `https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET.git`,
   Branch `ops/development-web-aislado-20261031`, Compose Path `./deploy/compose.development.yaml`; Save.
   Verificar que la rama sigue correspondiendo al Compose probado; no escribir un SHA en Branch suponiendo
   que el proveedor admite detached checkout. Los commits documentales posteriores no cambian ese Compose.
3. **Environment**: introducir únicamente `DEV_MYSQL_PASSWORD` y `DEV_MYSQL_ROOT_PASSWORD`, generadas localmente,
   diferentes entre sí y de todas las claves productivas. No copiarlas a Git, al chat ni a capturas. Guardar.
   Dokploy genera su propio `deploy/.env` en el checkout del nuevo servicio.
4. **Domains → Add Domain**: Host `dev-campusmarket.iscoutb.dev`; Service Name `api`; Path `/`;
   Container Port `8000`; Strip Path **no**; HTTPS **sí**, Certificate Provider **Let's Encrypt**.
   La UI se abrirá en `/app/`: no limitar el routing a `/app/`, porque `/health`, `/catalogo` y `/uploads` usan la raíz.
5. Antes del primer **General → Deploy**, comprobar entorno/nombre nuevos, Isolated Deployment, digest API/MySQL,
   ausencia de build/ports/binds y que ningún recurso externo señala a production. Dokploy añade una red propia
   para Traefik mediante Isolated Deployment; no declarar `dokploy-network` ni redes productivas en el repositorio.
   Si su vista generada no permite acreditar la configuración, detenerse antes de desplegar y obtener esa evidencia.
6. El primer Deploy crea solamente los dos contenedores nuevos. Conservar el log: su `-p` debe ser el proyecto
   nuevo y el fichero debe ser `compose.development.yaml`. El flag global `--build` no implica compilar si el
   Compose efectivo carece de `build`; cualquier contexto build o volumen productivo invalida este ensayo.
   Un fallo de permisos, pull o recursos no autoriza un cambio en production.

### Aceptación pública y rollback del ensayo

Verificar HTTPS válido en `https://dev-campusmarket.iscoutb.dev/app/`, `/app` → `/app/`, recursos sin errores,
Inicio → Catálogo → detalle → atrás → recarga; `/health` 200/ok, `/docs` y `/openapi.json` 200.
El catálogo debe comenzar vacío. Crear únicamente un usuario ficticio `demo-dev@example.test`, una publicación
DEMO y una imagen sin datos personales desde la propia UI; nunca importar SQL/fotos productivos.
Las peticiones deben ir al host **dev-campusmarket**, no a la API principal ni a Pages.
Contrastar en el nuevo despliegue el digest/Image ID con fuente OCI y `X-CampusMarket-Revision` `a9b6709…`;
la cabecera por sí sola no prueba identidad. Revisar salud y Monitoring sin interpretar ceros como memoria libre.

Referencia conservada para volver al baseline probado: rama del fork **`backup/development-web-0e670cc8`**,
que apunta a `0e670cc8678624c3d507cd87f27c476ba758f24c`. Después de un primer despliegue aceptado,
una configuración posterior defectuosa puede revertirse desde **web-ensayo → General → Provider → Branch**
seleccionando esa referencia y haciendo Save, seguido de **Deploy manual**. Mantener exactamente appName,
Compose Path, las dos claves de development, Isolated Deployment y dominio; no cambiar MySQL ni volúmenes.
La prueba CI acredita ese `up` global con imágenes fijadas y configuración DB idéntica; comprobar el log y
metadatos reales del nuevo servicio antes de atribuirle el mismo resultado. No invocar el rollback registral
de Applications suponiendo que es equivalente al servicio Compose ni volver a publicar GHCR.

Si falla el primer intento, aún no existe una versión institucional anterior de este ensayo: detener únicamente
`development/web-ensayo` dentro de la autorización recibida y conservar sus volúmenes para diagnóstico.
Nunca usar Fresh Volumes ni `down -v` en el panel. Detener aceptación ante discrepancia de cuota, identidad,
proyecto, montajes, salud, navegación, recursos o cambio inesperado de MySQL. Esta alternativa todavía no
publica `/app/` en el dominio principal y no acredita recuperación productiva.
