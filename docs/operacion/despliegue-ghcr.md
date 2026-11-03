# CampusMarket - Plan de despliegue GHCR

## 1. Objetivo

Desplegar una imagen Docker previamente probada en CI,
sin reconstruirla en Dokploy y sin afectar la persistencia.

Estado del plan productivo: PREPARADO, NO EJECUTADO.

El [ensayo aislado en Actions](ensayo-ghcr.md) terminó con 10/10 criterios
aprobados en el [run 41051624793](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41051624793).
No modifica el estado de este plan ni satisface por sí solo sus condiciones
de acceso, respaldo y recuperación del servidor Dokploy.

## 2. Evidencia de origen

Repositorio:
ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET

Commit validado:
2154e7880e5111537256206a29f4f4c29a8c86c4

Run de Compose:
41024201484

Run de publicacion GHCR:
41026286264

Imagen:
ghcr.io/iscoutb/campusmarket-api@sha256:f9eaabdb166274225e9ad490c44999f71f6b1f7c9c5902dc68ab98b07115ce8b

## 3. Infraestructura actual

Dokploy: campusmarket / production / sistema

Proyecto Compose:
campusmarket-sistema-2zvsxj

Compose activo:
deploy/compose.lab.yaml

Servicios:
- api
- db

Volumenes declarados:
- mysql_data
- publication_images

El servicio actual construye api desde GitHub.
El autodeploy desde master sigue activo.

## 4. Configuracion propuesta

Archivo:
deploy/compose.prod.yaml

Cambio funcional:
- api.build se sustituye por api.image con digest inmutable.

Sin cambios estructurales en:
- servicio db;
- variables funcionales de API;
- servicios y dependencias;
- volumenes declarados;
- healthchecks;
- limites de recursos.

La equivalencia declarativa no confirma montajes fisicos.

## 5. Condiciones obligatorias antes de desplegar

[ ] Confirmar acceso de Dokploy al paquete GHCR Internal.
[ ] Confirmar montajes efectivos de MySQL y uploads.
[ ] Confirmar los nombres fisicos de los volumenes.
[ ] Obtener y verificar un respaldo recuperable de datos.
[ ] Conservar una referencia recuperable de la imagen anterior.
[ ] Verificar compatibilidad de esquema para rollback.
[ ] Evitar conflictos con autodeploy desde master.
[ ] Confirmar ruta Compose y mecanismo de variables de Dokploy.
[ ] Obtener autorizacion explicita para intervenir produccion.

Si alguna condicion falla, NO DESPLEGAR.

## 6. Ensayo previo

1. Validar el YAML con Docker Compose config.
2. Verificar acceso al digest GHCR desde el servidor.
3. Revisar diferencias entre Compose actual y propuesto.
4. Comprobar que la imagen tiene el SHA esperado.
5. Registrar el estado y los identificadores anteriores.

No ejecutar docker compose down, down -v ni comandos
que eliminen volumenes.

## 7. Despliegue controlado (procedimiento propuesto)

Aplicar exclusivamente una actualizacion del servicio api
usando el mismo proyecto Compose existente.

El comando exacto y la integracion con Dokploy se
confirmaran cuando esten verificados los requisitos previos.

No cambiar el servicio db ni recrear sus volumenes.

## 8. Verificacion posterior

Comprobar:
- API running y healthy.
- MySQL running y healthy, sin recreacion.
- Identidad de imagen por digest.
- Revision OCI igual al commit aprobado.
- Archivo /app/REVISION igual al commit aprobado.
- Encabezado X-CampusMarket-Revision esperado.
- Persistencia de los montajes fisicos.
- Operaciones publicas no destructivas de la API.

Guardar fecha, SHA, digest, evidencia y resultado.

## 9. Rollback

Si la API falla:
1. Detener la promocion de nuevas versiones.
2. Restaurar la referencia de imagen anterior.
3. Actualizar solamente api mediante procedimiento autorizado.
4. Confirmar estado healthy y version restaurada.
5. Verificar MySQL y montajes sin alteraciones.

El rollback de imagen no revierte automaticamente
migraciones de datos ni cambios en archivos.

No declarar rollback probado hasta realizar un ensayo
controlado con una version compatible.

## 10. Riesgos pendientes

- Acceso GHCR desde Dokploy: no confirmado.
- Montajes fisicos: no confirmados.
- Backups recuperables: no confirmados.
- Autodeploy desde master: activo.
- Ensayo de rollback: no realizado.

La publicacion GHCR NO equivale a un despliegue
de produccion completado.

## 11. Candidato Flutter para el servicio existente — 2026-10-31

**Preparación verificada; no desplegado; rollback productivo todavía bloqueado.** Esta sección actualiza
el candidato del plan. Las referencias `2154e788…`/`f9eaabdb…` anteriores conservan su significado histórico
y no identifican la imagen actualmente ejecutada. No usar development para esta promoción.

### Cambio mínimo, origen y validación

Base de la rama del fork `ops/produccion-web-digest-20261031`: `ISCOUTB/master`
`40be256f52d74ad8c9148886f040845658a38855`, sin modificaciones posteriores observadas.
El único cambio de infraestructura del repositorio es `api.image` en el
[Compose alternativo existente](../../deploy/compose.prod.yaml):

```text
ghcr.io/nnigarp/campusmarket-web-candidate@sha256:65d34f2de8d035d5a9672be2e6a81bab759089da2fbe91bdca23a17f2f0463fd
Image ID: sha256:15a6fee324bc315d27ab85674781dfd1bded727243cb6ff752370e70b5d6fd19
Fuente de imagen: a9b6709a67f8036346acb64b9c2b9849ee355cf2
```

`compose.lab.yaml` permanece intacto. La futura aplicación cambiaría exclusivamente Compose Path a
`./deploy/compose.prod.yaml`, conservando repositorio oficial/master, proyecto `campusmarket-sistema-2zvsxj`,
Environment, dominio, Isolated Deployment, labels de Traefik y recursos actuales. Comparado con el Compose
activo, el alternativo solo sustituye `api.build` por `api.image`; no se superponen ambos archivos.
También se sincronizan las dos constantes de identidad del ensayo GHCR manual, para que no espere el digest antiguo.

[Run 41270390431](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41270390431),
fuente `65e4d468490bfb1a00cfa56ab48d049b66ad5dc9`: el
[verificador de lectura](../../scripts/verificar_promocion_web.py) compara los JSON reales de Compose,
exige el delta exacto y lee el manifiesto/configuración OCI anónimamente verificando ambos SHA-256 y la fuente.
Confirma dos servicios/512 MiB, MySQL/variables/redes/volúmenes sin diferencias y ausencia de puertos/build.
Los módulos de dominio/persistencia, dependencias y contrato son idénticos entre `40be256…` y `a9b6709…`;
las diferencias de backend inspeccionadas son el montaje Web y sus archivos. Esto no demuestra el código
del contenedor productivo actual. Artefacto `13069002355`, ZIP SHA-256
`9da99f551de7dba193832b791afe353f0419ee715a3e790513587d72a869bf81`.

Se reutilizan la imagen y ensayos anteriores; no se reconstruyó Flutter ni se publicó imagen alguna.
El [ensayo local añadido por el equipo, commit 52762bd](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/blob/52762bd/docs/operacion/evidencia-ensayo-flutter-local-20261031.md)
acredita UI, edición, fotos y persistencia sintéticas, distintos de una aceptación institucional.
La CI específica nueva cubre configuración/registro. El commit documental usa `[skip ci]` para mantener
la restricción de no recompilar Flutter al abrir este borrador: los workflows oficiales genéricos del nuevo PR
quedan **sin reejecutar**, no aprobados por herencia. Resolver ese requisito antes de considerar una fusión.

### Auditoría productiva y riesgos todavía abiertos

Lectura del panel: GitHub oficial/master, `./deploy/compose.lab.yaml`, Trigger On Push, Autodeploy ON;
Isolated Deployment ON; Run Command vacío (usa el `up -d --build --remove-orphans` global).
API `bd294e94091a` y MySQL `baedd6d65e17` running/healthy. Son identificadores de contenedor, no Image ID.
Lectura pública: `/health` devuelve `ok`; `/app/` devuelve `Not Found`.
View Config no proporcionó Image ID. No se volvió a consultar SQL, usuarios o fotos productivos.

| Riesgo | Evidencia disponible | Condición antes de publicar |
|---|---|---|
| Imagen equivocada | Digest/config OCI contrastados; el equipo acredita el pull en el mismo servidor durante development | Verificar disponibilidad local del digest exacto, no solo credenciales o cabecera |
| MySQL recreado por un up global | Compose DB idéntico; `mysql:8.4` sigue mutable | Usar Run Command dirigido solo a API, con `--no-deps --no-build --pull never` |
| Red nueva con pools agotados | Se conserva Isolated Deployment y la red del mismo servicio; no se añaden redes al YAML | Acreditar la red existente `campusmarket-sistema-2zvsxj` y el Compose efectivo sin redes adicionales |
| Pérdida de SQL/fotos | Solo declaraciones y ensayos sintéticos; sin nueva evidencia de recuperación productiva | Montajes efectivos y respaldo consistente/restauración acreditados, sin exponer datos |
| Rollback no ejecutable | Imagen activa sin identificar; existe un archivo de una versión conocida, descrito abajo | Identificar/conservar una referencia recuperable y comprobar compatibilidad/acceso desde el servidor |
| Autodeploy inesperado | Toggle ON observado | Autorización para pausarlo y cola vacía antes de cualquier merge/cambio de Provider |
| Memoria/interrupción | 256 MiB/0,5 CPU por servicio; las pruebas anteriores acreditan carga sintética | Ventana de interrupción de API; detener aceptación ante OOM, reinicios, 503 o pérdida de fotos |

Dokploy v0.30.10 permite un comando personalizado en **Advanced → Run Command**. Su
[implementación](https://github.com/Dokploy/dokploy/blob/v0.30.10/packages/server/src/utils/builders/compose.ts)
antepone `docker` al valor del campo, genera el Compose/Environment y comprueba la red aislada existente antes
de ejecutar el comando. Por eso usar Run Command sigue siendo una operación del servicio que requiere autorización;
no equivale a tener SSH ni permite eludir controles. Si la red no existe, Dokploy intentaría crearla: detenerse.

### Primera fase que requiere aprobación: identificar la API sin sustituirla

No ejecutar esta fase por la existencia del documento. Requiere aprobación explícita del usuario.

1. En `campusmarket → production → sistema → General`, desactivar únicamente Autodeploy; confirmar ausencia
   de despliegues en cola. No hacer merge. Conservar Provider/Compose Path/Environment y todas las opciones de Advanced.
2. Acreditar que la red aislada actual existe. En **Advanced → Run Command**, guardar temporalmente:

   ```text
   compose -p campusmarket-sistema-2zvsxj --env-file deploy/.env -f ./deploy/compose.lab.yaml images -q api
   ```

3. **General → Deploy** ejecutaría esa lectura mediante el envoltorio de Dokploy. La orden elegida no contiene
   `up`, `build`, `pull`, `exec`, `start` ni elimina recursos; imprime el Image ID de la API que está ejecutándose.
   Dokploy sí vuelve a preparar su checkout/archivos de configuración y procesa su red existente: esta es la
   razón para pedir autorización antes. No ejecutar si no se puede acreditar la red o el comando efectivo.
4. Leer únicamente ese SHA-256 y el estado de los dos contenedores en Deployments/Containers. Restaurar el campo
   Run Command a vacío con Save, sin hacer otro Deploy; dejar Autodeploy pausado para continuar la preparación.
   Conservar los mismos contenedores y salud. Esta autorización no incluye publicar la candidata ni cambiar datos.

### Archivo de una versión conocida, sin atribuirlo a la API activa

El [run oficial 41057456301](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41057456301)
aprobó Compose sobre `40be256…` y exportó `campusmarket-imagen-40be256f52d74ad8c9148886f040845658a38855`,
artefacto `12977916121`. Se recuperó el ZIP original sin reconstrucción y se contrastó SHA-256
`8c83f194964ab80dc053711a61721afcf58e790d28b480f42bdfb93b9367b781`; `source-sha.txt` y la configuración
de `api.tar` identifican fuente `40be256…` e Image ID
`sha256:b24a47b2889b0898f617e15ad7e3cd01fc17abbff9947edbb21ebf66f6a60267` (amd64).
**No se ha demostrado que ese ID sea el productivo ni se ha publicado un digest de rollback para él.**
El artefacto vence el 6/nov/2026; no constituye por sí solo conservación duradera o acceso desde Dokploy.
Si coincide con la imagen activa, todavía se debe acreditar conservación/carga y restauración. Si no coincide,
sería una alternativa de recuperación a una versión conocida que exige aceptación y ensayo específicos,
no una reversión idéntica a la anterior. No sustituirlo por `f9eaabdb…` ni deducir código del header `785641…`.

### Publicación posterior, solamente cuando se cierren los gates y se apruebe

1. Con Autodeploy pausado y sin cola, acordar/revisar los PR de implementación y configuración; cualquier fusión
   requiere autorización separada. Comprobar el commit final oficial, el archivo por digest y el diff efectivo.
2. Acreditar montajes efectivos, respaldo/restauración, imagen de retorno conservada y accesible, misma red
   existente y candidato en caché con Image ID `15a6fee…`. No cambiar variables, credenciales, volumen/nombre
   de proyecto, etiquetas o dominio. No usar Import/Load, Fresh Volumes o el Compose de development.
3. Cambiar únicamente **General → Provider → Compose Path** a `./deploy/compose.prod.yaml` y Save.
   En **Advanced → Run Command**, guardar (el campo no lleva el prefijo `docker`):

   ```text
   compose -p campusmarket-sistema-2zvsxj --env-file deploy/.env -f ./deploy/compose.prod.yaml up -d --no-deps --no-build --pull never --wait --wait-timeout 180 api
   ```

4. Tras la aprobación final de esa configuración exacta, General → Deploy. El comando solo selecciona API;
   no inicia/recrea MySQL ni hace pull/build implícito. Comparar después ID/StartedAt/imagen/montajes/red de MySQL
   con el inventario anterior; comparar imagen/OCI/REVISION y cabecera de API con fuente `a9b6709…`.
5. Verificar HTTPS válido, `/app` → `/app/`, catálogo/filtros/detalle/atrás/recarga, fotos existentes mediante
   lecturas autorizadas, recursos sin errores, `/health` 200/ok, `/docs` y `/openapi.json` 200.
   No crear cuentas, publicaciones o escrituras de ensayo en producción durante esta aceptación.
6. Detener aceptación ante cambio de MySQL, identidad/red/montajes inesperados, OOM/reinicios, 503, errores
   de navegación/fotos o contrato. Ejecutar solamente el rollback previamente cerrado y autorizado, que cambia
   la imagen de API y mantiene el mismo proyecto, Environment, volúmenes, routing y comando solo de API.
   No volver a `compose.lab.yaml` suponiendo que reconstruye la imagen anterior: eso no es un rollback reproducible.

No se puede completar ahora un fichero de rollback con Image ID/digest anterior sin inventarlo. La publicación
sigue bloqueada por esa identidad/recuperabilidad, montajes y respaldo/restauración; la primera solicitud de
aprobación es únicamente la inspección limitada anterior. No reactivar Autodeploy sin una decisión explícita.


## 12. Resultado posterior de promoción Flutter — 2026-11-01 (adenda de ejecución)

**La restricción histórica de las secciones 1–11 describe el estado de planificación anterior; no debe confundirse con el resultado posterior.** Tras PR #77 (merge `5ef0d6b139138d1260435b1b884240f093904749`), Dokploy usó `./deploy/compose.prod.yaml` y un comando personalizado dirigido a `api`: `docker compose -p campusmarket-sistema-2zvsxj --env-file deploy/.env -f ./deploy/compose.prod.yaml up -d --no-deps --no-build api`.

El log registró `api-1 Recreated` y `Docker Compose Deployed: ✅`. La comprobación posterior acreditó `/health` OK y Flutter en `/app/`; `api-1` healthy y `db-1` healthy con ID `baedd6d65e17` idéntico al anterior. Ambos paquetes GHCR (`campusmarket-web-candidate` y `campusmarket-api-rollback`) eran públicos según GitHub; la primera imagen se consumió en la promoción.

**Advertencia persistente:** los montajes se confirmaron, pero no se acreditó backup recuperable ni se ejecutó rollback en el host. El rollback con MySQL sintético en Actions no sustituye la restauración real. Conservar Autodeploy desactivado y revisar antes de cualquier despliegue el Run Command personalizado, ya que el valor predeterminado incorpora `--build --remove-orphans`.

Véanse la [evidencia de cierre](../evidencias/cierre-web-institucional-2026-11-01.md), el [ADR-0025](../adr/0025-servir-flutter-web-con-fastapi-en-servicio-existente.md) y [arc42 §7](../arc42/07-vista-despliegue.md).

## Incremento 2 — Preparación del PR #85 sin desplegar

PR #85 ya fue fusionado por el usuario (`1c07c2c`). Orden pendiente: validar/corregir S10 por PR independiente → preparar/aprobar promoción independiente de `api.image` → autorización expresa de Deploy → comprobación HTTP posdespliegue. Nada de lo siguiente ejecuta un cambio productivo. Autodeploy permanece desactivado; si se observa activado, detener el procedimiento y resolver la coordinación antes de integrar.

Servicio existente `campusmarket → production → sistema`, Compose `./deploy/compose.prod.yaml`. **Conservar exactamente Advanced → Run Command:**

```text
compose -p campusmarket-sistema-2zvsxj --env-file deploy/.env -f ./deploy/compose.prod.yaml up -d --no-deps --no-build --pull always api
```

La promoción solo podrá cambiar `api.image` al digest de una imagen nueva del incremento, ensayada con MySQL sintético. Mantener servicios api/db, MySQL 8.4, Environment, red, nombres de proyecto/volúmenes, fotos, etiquetas, healthchecks y límites existentes. No usar down, Fresh Volumes, build ni recrear db.

Rollback configurado actual: `ghcr.io/nnigarp/campusmarket-web-universidades@sha256:384cbd0c08242d4a6d0343f26fab8521fd027908b639f638b2b9653f0f53dde1` (evidencia PR #82). Reconfirmar imagen ejecutada/recuperable y respaldo consistente antes de autorizar promoción. Favoritos/conversaciones/mensajes añaden tablas propias y no eliminan ni renombran columnas heredadas; esa compatibilidad y la vuelta a API anterior deben ensayarse con datos sintéticos, no inferirse solo de leer el esquema.

S10 normal resuelve base oficial por SHA y compara HTTP con baseline productiva independiente. Tras Deploy autorizado, ejecutar workflow S10 con `mode=instalado`, `source_sha=<SHA construido e instalado>`, seleccionando la revisión de workflow correspondiente. Recupera el contrato del SHA de imagen y registra por separado el checkout del orquestador; mantiene los nueve criterios de tres fases, igualdad OpenAPI antes/después y revisión. Añadir pruebas públicas de /health, /app/, catálogo/detalle/fotos, login/favoritos/chat con cuenta de ensayo autorizada. No usar datos reales ni registrar secretos. Parar/revertir exclusivamente API si salud, revisión/digest, contrato, persistencia o navegación no coinciden. La baseline no se actualiza anticipadamente para aparentar verde.

La rama/PR de promoción documentará fuente, run único de construcción/ensayo, Image ID, digest inmutable nuevo, digest anterior y resultados. Aún no hay imagen/digest nuevo del incremento acreditados en esta revisión; no sustituirlos por el digest anterior ni desplegar antes de autorización.

## Incremento 2 — Imagen verificada y promoción propuesta

Esta adenda sustituye únicamente el estado «imagen nueva pendiente» del apartado anterior. La producción no cambia. [Run 41595618179](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41595618179) aprobó 13 comprobaciones de actualización/persistencia/rollback sobre MySQL y PNG sintéticos y publicó exactamente el Image ID probado, sin reconstrucción posterior. Fuente `46ede525602161826b75273fbb12528e739908cc`, base oficial `1c07c2c`; imagen candidata **`ghcr.io/nnigarp/campusmarket-web-universidades@sha256:11d92aa9b66f1a4c6b879a6e8cd62cc3c102a37c034a44cbde27442b73694fa7`**, Image ID `sha256:3b5357bd997ad391426438b483e0b0794fd76ab92f6e054ce09cf80e15d59f96`. [Identidad y resultados conservados](../evidencias/incremento-2-universidad-visible-2026-11-03.md#imagen-del-incremento-2-publicada-promoción-productiva-pendiente).

Rama `ops/promocion-incremento2-20261103`, dependiente de la corrección `fix/s10-base-oficial-20261103`. No integrar la promoción antes de revisar/aprobar el correctivo. `scripts/verificar_promocion_incremento2.py --registry` valida Compose con variables sintéticas, delta exclusivo `api.image`, fuente/contrato y manifiesto/configuración OCI por hashes; únicamente lee Git/GHCR. No usa Environment productivo. [CI 41597711177](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41597711177) aprobó este preflight sobre `0d98ff6` y conservó el resultado: lectura anónima/identidad GHCR acreditadas desde el runner, delta exclusivo `api.image`. No reconstruyó ni desplegó; no acredita pull ni recuperación en el host institucional.

### Preflight para una autorización posterior

1. Revisar/fusionar por separado el correctivo S10 y luego la promoción, solo con autorización. Confirmar que el SHA oficial seleccionado contiene el digest anterior y después el candidato según cada fase; no confundir SHA del Compose/orquestador con fuente de imagen `46ede525602161826b75273fbb12528e739908cc`.
2. En `campusmarket → production → sistema`, comprobar **Autodeploy desactivado**, sin despliegue en cola, Compose Path `./deploy/compose.prod.yaml` y Run Command exactamente igual al ya utilizado arriba (`--no-deps --no-build --pull always api`). No modificarlo ni usar el comando predeterminado. Conservar proyecto `campusmarket-sistema-2zvsxj`, Environment y sus referencias, etiquetas/dominio/red existentes y ambos volúmenes.
3. Antes de Deploy, obtener evidencia de la imagen API ejecutada y de los montajes físicos de `mysql_data` y `publication_images`; confirmar imagen anterior `ghcr.io/nnigarp/campusmarket-web-universidades@sha256:384cbd0c08242d4a6d0343f26fab8521fd027908b639f638b2b9653f0f53dde1` recuperable. Conservar inventario no sensible de MySQL (ID/StartedAt/imagen/montajes/red) para comparar después. El header `50d9352` aislado no acredita esos datos.
4. Acreditar respaldo consistente y restauración recuperable de SQL y uploads sin ensayar sobre producción. Confirmar capacidad del host de descargar **este digest nuevo**. Un GET anónimo o pull desde Actions no prueba acceso desde Dokploy; el pull previo de otra imagen tampoco. Si el panel no ofrece esas comprobaciones, faltan permisos/evidencia y no se autoriza Deploy. No crear servicios, ejecutar Fresh Volumes ni cambiar secretos para sortearlo.
5. Presentar el plan/digest y solicitar autorización expresa de Deploy y del rollback exclusivamente API. Solo entonces pulsar **General → Deploy** una vez. El comando conserva MySQL y selecciona `api`; no elimina la breve interrupción mientras se recrea API ni garantiza que un pull/build host previo no falle. Si el log selecciona db, build u otra red, abortar aceptación y no repetir a ciegas.

### Verificación y rollback después del Deploy autorizado

- Comparar el inventario MySQL: mismo ID/StartedAt, imagen, montajes y red; API healthy, digest candidato, Image ID `sha256:3b5357bd997ad391426438b483e0b0794fd76ab92f6e054ce09cf80e15d59f96` y OCI/REVISION `46ede525602161826b75273fbb12528e739908cc`. Leer límites/reinicios/OOM; los picos sintéticos 161,2/176,8 MiB bajo 256 MiB por servicio no sustituyen monitorización real.
- HTTPS válido; `/health` 200/ok; `/app` redirige a `/app/`; Flutter carga assets, catálogo/filtros/detalle/atrás/recarga y fotografías ya existentes; `/docs` y `/openapi.json` 200. Usar una cuenta sintética autorizada para la aceptación de Favoritos/Mensajería/universidad, sin registrar tokens o datos personales.
- Ejecutar S10 corregido en modo **`instalado`**, `source_sha=46ede525602161826b75273fbb12528e739908cc`: contrato recuperado desde ese SHA del fork y revisión esperada idéntica, **nueve criterios completos**. El SHA del workflow/Compose se registra por separado. No actualizar `.github/s10-produccion.json` antes de esta aceptación. Tras verificarla, proponer otro cambio que fije `contract_repository=Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET`, contrato/revisión `46ede525602161826b75273fbb12528e739908cc` e imagen candidata; nunca usar el OpenAPI descargado como expectativa de sí mismo.
- Detener ante db recreada, montajes/red diferentes, pérdida de archivos, OOM/reinicios, salud fallida, revisión/contrato/digest/JS incorrectos o recorridos rotos. No hacer down ni tocar MySQL.
- **Rollback autorizado:** en una rama del fork revertir exclusivamente `api.image` a `ghcr.io/nnigarp/campusmarket-web-universidades@sha256:384cbd0c08242d4a6d0343f26fab8521fd027908b639f638b2b9653f0f53dde1`, revisar/integrar esa reversión por PR y, con Autodeploy aún desactivado, usar el mismo **General → Deploy** y Run Command API-only. Conservar Environment, red, límites y volúmenes; no eliminar tablas nuevas. Comparar ID MySQL y fotografías, salud y revisión anterior `50d9352`; ejecutar S10 normal contra baseline anterior. La nueva funcionalidad deja de estar disponible en la API vieja, pero los datos añadidos permanecen para una promoción posterior, como comprobó el ensayo. La recuperación real del host y sus respaldos sigue sin acreditarse.

Si falta identidad anterior efectiva, respaldo/restauración, montajes o evidencia de pull del host, **la promoción productiva permanece bloqueada** aunque el PR, GHCR y los ensayos estén verdes. Esta preparación no autoriza tocar Dokploy.

## Actualización operativa — Incremento 2 desplegado el 2026-11-03

**Este apartado actualiza el estado, no sustituye las instrucciones y ensayos históricos anteriores.** Tras fusionar los PR #85–#88, Dokploy obtuvo el digest aprobado `sha256:11d92aa9b66f1a4c6b879a6e8cd62cc3c102a37c034a44cbde27442b73694fa7` y ejecutó el Run Command existente con `--no-deps --no-build --pull always api`. Log: `api-1 Recreated/Started`, `Docker Compose Deployed: ✅`; sin recreación de DB registrada. El operador observó publicaciones, favoritos y mensajería bidireccional en Web. [Evidencia consolidada](../evidencias/cierre-productivo-incremento2-2026-11-03.md).

El éxito del comando **no certifica** la continuidad de todos los montajes ni un respaldo recuperable. S10 quedó aprobado en modo instalado ([run 41613284005](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41613284005)) y producción ([run 41616502184](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41616502184), 9/9 criterios). Antes de otra promoción, rollback o cierre operativo definitivo comprobar ID DB, Image ID de API, healthchecks, montajes efectivos y recuperación de datos. Mantener Autodeploy desactivado y no usar `down` ni `Fresh Volumes`.
