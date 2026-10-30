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
