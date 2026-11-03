# Incremento 2 — Universidad declarada visible (2026-11-03)

> **Estado de cierre:** código y pruebas del fork **VERIFICADOS** en `058f63f0882d388e40c85c347e406bb9777cb343`. 126 pruebas backend + 4 de contrato, 33 Flutter y 12 criterios en cada recorrido Chrome escritorio/móvil y Android. **Incremento 2 no desplegado.** Los apartados intermedios conservan resultados fallidos/pendientes de su momento; el cierre al final los actualiza. Checks oficiales todavía no ejecutados: PR no abierto.


## Alcance y estado

Rama del fork `feat/incremento-2-20261103`, basada en oficial/fork `c7f15748a9a9dfd8b1160ab04fb8ee544a374437`. Corte posterior a [Favoritos](incremento-2-favoritos-2026-11-03.md) y [Mensajería](incremento-2-mensajeria-2026-11-03.md). No se modifica producción ni despliegue; PR oficial no abierto sin autorización.

## Implementación

- `PublicacionCatalogo.universidad` opcional/nullable reutiliza DTO Universidad. Rutas y resto de esquemas intactos; clientes antiguos siguen válidos.
- Catálogo resuelve IDs únicos mediante `universidades/service.py` → repositorio propio. Una consulta en lote de instituciones; sin N+1 por publicación ni widget. Fotografías conservan su capacidad en lote.
- Universidad procede del ID fijado al crear el anuncio, no del perfil actual. NULL no se inventa. Institución posteriormente inactiva mantiene identidad histórica, sin permitirse para nuevas declaraciones. Filtros existentes permanecen.
- Capa pública de Universidades también conserva listado, validación e inicialización de FK existente; Usuarios deja de importar su repositorio. Prueba de propiedad ahora cubre universidades además de los módulos nuevos. No hay tablas ni migraciones destructivas.
- Flutter: sigla en tarjeta, nombre en detalle y aclaración de declaración no verificada. Se conserva descripción/imagen/acciones; miniaturas compactas pasan a 16:10 para alojar etiqueta sin desbordamiento. Metadata también llega por la composición común a Favoritos/Mensajería.

## Pruebas antes de CI

- Ruff y diff: aprobados.
- Siete pruebas locales: lote de mil publicaciones/instituciones, frontera de servicio, composición de favoritos y cuatro de contrato. Seis adicionales de propiedad/erosión: **13 aprobadas en conjunto**.
- Comparación semántica OpenAPI frente a `871865d`: único cambio es el campo opcional/nullable universidad. La primera comprobación esperaba default explícito en JSON; se corrigió esa comprobación local a optional/union null porque FastAPI omite ese default, sin cambiar código ni contrato.
- Cinco casos backend nuevos: snapshot vs perfil actual, NULL heredado, institución inactiva, lote mil y frontera modular. Los tres primeros requieren MySQL 8.4 aislado de CI.
- Cinco casos Flutter añadidos: decodificación/legacy y cuatro anchos de tarjeta 250/285/350/500. Flujo real establece universidad en perfil antes de publicar y comprueba institución en tarjeta/detalle, conservando todos los criterios de Favoritos/Mensajería/EC-02.

## Commits, CI y límites

El commit de este corte inicia CI. Sus SHA/runs y resultados se incorporan después de verificar. **Integración MySQL/Flutter/recorrido conjunto: PENDIENTE.** No equivale a matrícula verificada ni revisión humana. No se publican imágenes o cambios productivos. ADR-0001/0003/0012/0019/0022 reutilizados; dos contenedores y presupuesto existentes, sin nueva infraestructura/dependencias. No se acredita carga institucional o recuperación productiva mediante estas pruebas sintéticas.

### Primera ejecución y corrección visual

Implementación: [`a079fb5`](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/commit/a079fb5f11b21bdfd161c798e7a4425bf48114cc). [Flutter 41586208778](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41586208778) aprobó analyze y **31/32 tests**. El nuevo caso de tarjeta de 250 px detectó un desbordamiento real de 27 px al incluir la institución. Se mantiene el test y se adapta únicamente la miniatura cuando tarjeta compacta tiene menos de 400 px de alto (proporción 2.2); se conservan título, precio, institución, descripción y acciones. Se repite validación completa sobre la corrección.

La corrección compacta está en [`dceb4ea`](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/commit/dceb4ea20ca82017749064037889248abe6c88c8). La revisión final también incorpora la revalidación de disponibilidad de Favoritos al volver a su pantalla (documentada en su evidencia), con un test adicional. El siguiente commit es la fuente conjunta a validar; no se atribuyen resultados de un SHA anterior al nuevo sin identificar la diferencia.

### Conservación de información de tarjeta

El corazón reemplazó el icono de modalidad del MVP. La revisión final conserva explícitamente «Venta»/«Alquiler» en la fila de contexto universitario, sin añadir altura ni quitar descripción/acciones. Los cuatro casos de tarjeta también exigen que siga visible la modalidad, evitando perder esa información al incorporar Favoritos.

## Validación conjunta final — fuente 058f63f

Fuente completa: [`058f63f0882d388e40c85c347e406bb9777cb343`](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/commit/058f63f0882d388e40c85c347e406bb9777cb343), rama del fork `feat/incremento-2-20261103`. Oficial y fork master seguían en `c7f15748a9a9dfd8b1160ab04fb8ee544a374437` al comprobar la integración.

| Comprobación | Run del fork | Resultado sobre esa fuente |
| --- | --- | --- |
| Backend/MySQL 8.4 | [41587498618](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41587498618) | Ruff, Gitleaks historial/checkout, **126 pytest + 4 contrato**, mutaciones detectadas y checkout limpio |
| Flutter | [41587498606](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41587498606) | analyze, **33 tests**, 2 mutaciones, builds Web/APK aprobados; toolchain snapshot vacío |
| Chrome escritorio/móvil y Android | [41587498624](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41587498624) | **Tres jobs aprobados; 12 criterios por plataforma** y capturas/informes con SHA igual; incluye Favoritos, Mensajería, universidad visible y controles previos de seguridad/imágenes |
| S10 candidato/producción | [41587498665](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41587498665) | Contrato candidato ejecutable; público comparado con contrato/revisión del despliegue vigente, sin exigir rutas nuevas no promovidas |

Los cuatro workflows/seis jobs terminaron en success. Las pruebas reales reportaron el mismo SHA de fuente; no se atribuye este resultado al contenido de una imagen productiva. Los estados intermedios anteriores explican correcciones y no sustituyen este conjunto final.

**Integración:** PR oficial no abierto sin autorización. No hay merge, publicación GHCR, despliegue ni cambios Dokploy. Compose, Dockerfile, variables, servicios, límites, redes, volúmenes y dominio permanecen intactos. Estos tests sintéticos no acreditan carga en los 512 MiB institucionales, backup/restore productivo, revisión humana ni retención jurídica aprobada. La promoción posterior requiere una imagen nueva del incremento, prueba por digest y autorización separada; no se reutiliza una imagen anterior como si contuviera este código.

## Propuesta de PR para revisión (todavía no abierto)

**Título:** feat: favoritos, mensajería privada e identidad universitaria visible

**Base:** `ISCOUTB:master` · **head:** `Nnigarp:feat/incremento-2-20261103` · estado solicitado: **Draft**.

**Descripción preparada:** CampusMarket incorpora favoritos privados persistentes, contacto/conversaciones/mensajes por participante mediante HTTP y universidad declarada en tarjetas/detalle. La identidad siempre procede de sesiones opacas; MySQL impide duplicados y las lecturas se componen en lote. Se preservan publicaciones heredadas y filtros actuales. OpenAPI evoluciona de forma aditiva, con validación separada de candidato y producción en S10.

**Validación para incluir:** los cuatro runs de la tabla anterior sobre fuente `058f63f`; 130 pytest, 33 Flutter y tres recorridos reales aprobados. Documentación canónica: arc42 §5/6/8, C4 L3, aspectos con ocho columnas, IA, README y tres evidencias incrementales enlazadas.

**Límites para incluir:** no despliega, modifica infraestructura ni publica imágenes; mantiene dos contenedores. Checks oficiales y revisión humana pendientes de abrir el PR y revisarlo. Promoción productiva separada, con los riesgos de recuperación ya registrados.

## PR #85 — Corrección de S10 y preparación de promoción

El usuario creó [PR #85, posteriormente fusionado](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/pull/85), head `531405c`, base institucional real `c7f15748a9a9dfd8b1160ab04fb8ee544a374437`. La autorización de apertura ya existe; las referencias anteriores a PR no abierto describen el cierre previo. PR #85 fue fusionado por el usuario en `1c07c2c3c2610455b1dc1c07b4ebc4c2ab362e24`. Esta corrección independiente parte de ese master y no autoriza otro merge ni despliegue.

Fallo oficial: [41590254139](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41590254139), job `contrato-publico`, paso «Preparar contrato de referencia segun entorno», exit 128: el Git ref `50d9352` no contiene la ruta en ese checkout. Las ocho pruebas anteriores sí aprobaron; no se llegaron a ejecutar las condiciones HTTP.

La revisión de imagen `50d9352e5081f8c3e470bd9cda9220d21b14cc0a` se conserva como expectativa del despliegue vigente, sin utilizarla para extraer archivos. `preparar_s10_referencias.py` recupera `refs/heads/master` de ISCOUTB y captura su SHA real; conserva contratos base, candidato, producción y referencia con sus hashes. Producción se compara contra contrato versionado en `c7f1574`, compatible con el despliegue observado, independientemente de futuras fusiones. `.github/s10-produccion.json` registra explícitamente esa separación. No se construye la expectativa copiando `/openapi.json` del objeto bajo prueba.

El modo manual `instalado` solo se ejecutará tras Deploy autorizado, con `source_sha` igual al SHA de la imagen realmente instalada: recupera el contrato de esa revisión desde Git y exige el mismo header. Se mantiene el checkout del workflow corregido, cuyo SHA se registra por separado; no se exige que la imagen anterior contenga el fix del propio orquestador. Una referencia inválida o inexistente falla antes de HTTP. **Los nueve criterios y la carga acotada del experimento permanecen intactos.** Tras acreditarlos, se podrá actualizar la baseline productiva mediante un cambio separado. El header no acredita por sí solo el código/digest.

Pruebas locales: 16 aprobadas, Ruff y Actionlint aprobados. Las historias sintéticas reproducen revisión sin fichero, candidato sin HEAD^1, avance de master antes de desplegar, selección estricta posdespliegue, referencia inválida y conservación de evidencias previas. La corrección anterior en la rama antigua no entró en el merge. Se reutiliza en `fix/s10-base-oficial-20261103`, basada en el último master `1c07c2c`. El CI de esta rama verificará la corrección antes de proponer un PR independiente. No se repiten manualmente Web/Android ya acreditados; las ejecuciones automáticas del PR verifican el nuevo HEAD.

Preparación operativa: ver [procedimiento canónico](../operacion/despliegue-ghcr.md#incremento-2--preparación-del-pr-85-sin-desplegar). La imagen nueva y su digest solo se preparan después de validar completamente PR #85; siguen pendientes al escribir esta corrección. El digest anterior configurado, acreditado en PR #82, es `ghcr.io/nnigarp/campusmarket-web-universidades@sha256:384cbd0c08242d4a6d0343f26fab8521fd027908b639f638b2b9653f0f53dde1`; antes de una promoción deberá confirmarse su correspondencia con la instancia ejecutada.

### Corrección independiente después del merge

Rama `fix/s10-base-oficial-20261103`, base oficial `1c07c2c`. Fuente [`39cc948`](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/commit/39cc948b74ff7a21f4b1dc40b4257ee82f85f727), [CI 41592547646](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41592547646): **16 tests y los nueve criterios HTTP aprobados**, 58 solicitudes seriales, correlación 1.0, catálogo público con hash antes/después idéntico, sin escrituras y revisión observada `50d9352`. Contrato productivo de `c7f1574`; master auditado `1c07c2c`; candidato `39cc948`. No se atribuye este verde al workflow antiguo de master, que necesita el PR correctivo.

La preparación de imagen utilizará una rama independiente del fork basada en ese master. Como el empaquetado Web anterior no está en master, se reutilizan Dockerfile/punto de entrada probados y se registrará el SHA completo que los incorpore, además de la base `1c07c2c`. S10 posdespliegue puede recuperar el contrato desde ese SHA del fork aunque aún no exista en la historia oficial; ambos remotos están fijados al proyecto, sin URLs arbitrarias. La baseline productiva solo cambiará tras Deploy verificado, indicando explícitamente el repositorio del contrato si procede. Prueba Git sintética adicional para este caso.

### Imagen del Incremento 2 publicada; promoción productiva pendiente

Resultado posterior a las notas de preparación: [S10 41595145649](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41595145649), fuente `ffdb59066bcc2f4562d779609938c0fced912afa`, aprobó **17 tests y los nueve criterios HTTP**, 58 GET seriales, revisión observada `50d9352`, correlación completa y catálogo sin cambios. El workflow antiguo del master `1c07c2c` sigue necesitando la integración del PR correctivo; no se le atribuye el verde del fork.

[Construcción y ensayo único 41595618179](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41595618179), rama `ops/imagen-incremento2-20261103`:

| Identidad | Valor acreditado |
| --- | --- |
| Base funcional oficial | `1c07c2c3c2610455b1dc1c07b4ebc4c2ab362e24` (merge PR #85) |
| Fuente completa de imagen | `46ede525602161826b75273fbb12528e739908cc` |
| Imagen publicada | `ghcr.io/nnigarp/campusmarket-web-universidades@sha256:11d92aa9b66f1a4c6b879a6e8cd62cc3c102a37c034a44cbde27442b73694fa7` |
| Image ID / configuración OCI | `sha256:3b5357bd997ad391426438b483e0b0794fd76ab92f6e054ce09cf80e15d59f96` |
| Rollback probado | `ghcr.io/nnigarp/campusmarket-web-universidades@sha256:384cbd0c08242d4a6d0343f26fab8521fd027908b639f638b2b9653f0f53dde1`; Image ID `sha256:a7d335ba525bc3cd786d90731d47ded9bf90f221fd3b88160d8ca3a666957ce2` |
| Hash contrato candidato normalizado | `da6d8d9322c32bb854f61355c74fe6bf837607140f7fae8aecc589edd97fae30` |
| SHA-256 de `main.dart.js` servido | `1c4de9fd3c813005c4319785765d6e2851d7a8ca75795720519c455832b9ff1f` |

Master no contenía el empaquetado Web usado por el despliegue anterior. La fuente completa reutiliza su Dockerfile/punto de entrada y añade el orquestador del ensayo; `backend/app`, `frontend` y `contracts` coinciden con master salvo el adaptador estático `web_entrypoint.py`. Por ello la revisión esperada después del Deploy es **`46ede525602161826b75273fbb12528e739908cc`**, no el SHA base `1c07c2c`. OCI, fichero REVISION, contrato y archivos servidos se comprobaron separadamente.

La imagen se construyó una vez, se ensayó por Image ID y se publicó sin reconstruir; manifiesto/configuración OCI y pull posterior por digest reprodujeron ese mismo ID. No se sobrescribió el digest anterior. Se conserva el [JSON de resultados y publicación](datos/imagen-incremento2-41595618179.json), además de [metadatos de promoción](../../deploy/promocion-incremento2.json) y GHCR. ZIP de evidencia original `13212201894`, SHA-256 `1aae2e616f74afa72b3973f96ea8bcb34e1b77e08481378f558eaba64e5c5569`, descargado y contrastado; el archivo de imagen `13211652917` es adicional, no el único mecanismo de conservación.

**13 comprobaciones aprobadas.** La imagen anterior creó usuarios/publicación/PNG sintéticos; después se comprobó migración a candidato, Favoritos privados/idempotentes, chat/bandejas/autorización/idempotencia, universidad/heredadas, cierre de sesión, contrato exacto y assets. Publicación, fotografía y sesión sobrevivieron al reinicio de API, rollback a la imagen anterior y nueva promoción. Los cinco inventarios contienen **un único ID de MySQL**, sin reiniciarlo. Las tablas añadidas siguen presentes durante el rollback; la API anterior las toleró y la nueva recuperó Favoritos/chat. No se ejecutan migraciones inversas ni se borran tablas.

Límites efectivos 256 MiB por servicio. Picos registrados en el ensayo: API **161,2 MiB**, MySQL **176,8 MiB**, sin OOM. Esto no acredita carga real institucional ni margen ante tráfico concurrente. Se reutiliza CI del master fusionado para backend/Flutter/recorridos; no se repiten los 33 tests Flutter ni Android manualmente.

La promoción propuesta vive en `ops/promocion-incremento2-20261103`, basada en la corrección S10 para integrarse después de ella. El delta del Compose respecto a `1c07c2c` es exclusivamente `api.image`; preserva Environment, dos servicios, MySQL 8.4, volúmenes, red, límites, healthchecks y routing. Configuración normalizada, Ruff y Actionlint locales aprobados; el workflow de promoción comprobará además manifiesto/configuración anónimos en GHCR. No crea contenedores ni hace build o Deploy.

**Pendiente productivo:** no se ha inspeccionado de nuevo Dokploy, descargado esta imagen desde ese host ni acreditado backup/restauración independiente. El rollback ensayado es sintético. Antes de autorizar Deploy se requiere identidad vigente, montajes efectivos, respaldo recuperable, capacidad de pull institucional y Autodeploy desactivado; si falta evidencia, detener. [Procedimiento canónico](../operacion/despliegue-ghcr.md#incremento-2--imagen-verificada-y-promoción-propuesta).

### Apertura del correctivo independiente

Head publicado: `Nnigarp:fix/s10-base-oficial-20261103` (`ffdb59066bcc2f4562d779609938c0fced912afa`), base `ISCOUTB:master` (`1c07c2c`). Título preparado: **fix: separar contrato S10 de revisión productiva tras PR #85**. El conector devolvió `403 Resource not accessible by integration` al intentar abrir el Draft PR; no existe un número de PR nuevo acreditado. [Comparación para crearlo manualmente](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/compare/master...Nnigarp:AS_202620_PROYECTO_CAMPUSMARKET:fix/s10-base-oficial-20261103?expand=1). Descripción: referencia oficial por SHA real, baseline productiva independiente, candidato/imagen con orquestador separado; 17 tests y nueve criterios aprobados en run 41595145649; no cambia código funcional ni producción. La promoción de imagen permanece en otra rama, dependiente de integrar primero ese correctivo.
