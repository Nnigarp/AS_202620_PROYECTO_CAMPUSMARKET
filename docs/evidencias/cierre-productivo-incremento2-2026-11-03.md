# Incremento 2 — aceptación productiva observada (2026-11-03)

**Alcance:** cierre operativo **posterior a S13**, sin recalificar semanas previas. Las comprobaciones manuales corresponden a las capturas y el log compartidos por el operador en la sesión del 3 de noviembre de 2026 (hora de Colombia); **esas capturas no se incorporan como archivos al repositorio**. Los resultados CI sí tienen enlaces persistentes. No se registran credenciales, tokens, correo de prueba ni conversaciones privadas completas.

## 1. Referencias reproducibles

| Eslabón | Referencia comprobable |
|---|---|
| Funciones Favoritos, Mensajería y universidad visible | [PR #85](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/pull/85), merge `1c07c2c3c2610455b1dc1c07b4ebc4c2ab362e24` |
| Corrección de referencias S10 | [PR #86](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/pull/86), merge `2215d5420a8414c4486a0db5a145dfbd3ed1c687` |
| Promoción por digest | [PR #87](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/pull/87), merge `7c27087af768f39d8f6859aa4a8713c4c681e88c` |
| Construcción/ensayo versionados | [PR #88](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/pull/88), master `cfb93309ea159ee82ddc8faf54fb1561d25b6d57` |
| Fuente de la imagen | `46ede525602161826b75273fbb12528e739908cc` sobre base funcional `1c07c2c` |
| Imagen promovida de API + Web | `ghcr.io/nnigarp/campusmarket-web-universidades@sha256:11d92aa9b66f1a4c6b879a6e8cd62cc3c102a37c034a44cbde27442b73694fa7` |
| Imagen anterior identificada para reversión | `ghcr.io/nnigarp/campusmarket-web-universidades@sha256:384cbd0c08242d4a6d0343f26fab8521fd027908b639f638b2b9653f0f53dde1` |
| Ensayo de integración/rollback sintético | [Run 41595618179](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41595618179), [artefacto registrado](datos/imagen-incremento2-41595618179.json) |
| Verificador de promoción | [Run 41597711177](https://github.com/Nnigarp/AS_202620_PROYECTO_CAMPUSMARKET/actions/runs/41597711177) |
| CI final del master | [Commit `cfb9330`](https://github.com/ISCOUTB/AS_202620_PROYECTO_CAMPUSMARKET/commit/cfb93309ea159ee82ddc8faf54fb1561d25b6d57): backend, Flutter, recorridos Android/Web, Compose, SonarCloud y S10 en verde **antes del despliegue** |

## 2. Despliegue observado en Dokploy

Servicio: `campusmarket → production → sistema`, Compose `./deploy/compose.prod.yaml`; Autodeploy desactivado. El **Preview Compose** presentado antes de ejecutar confirmó digest nuevo en `api.image`, `mysql:8.4`, los volúmenes `publication_images` y `mysql_data`, red externa `campusmarket-sistema-2zvsxj` y 256 MiB por servicio. El Run Command se conservó:

`docker compose -p campusmarket-sistema-2zvsxj --env-file deploy/.env -f ./deploy/compose.prod.yaml up -d --no-deps --no-build --pull always api`

El log aportado por el operador registró clonación del repositorio oficial, `Image ...11d92aa9... Pulled`, `api-1 Recreate/Recreated/Starting/Started` y **`Docker Compose Deployed: ✅`**. No registró recreación de `db-1`. **Esto acredita la ejecución del despliegue, no por sí solo el Image ID o los montajes efectivos posdespliegue.** Antes del deploy, `api-1` y `db-1` estaban `running/healthy`; el ID visible de DB era `baedd6d65e17` (prefijo). No se incluye una nueva comprobación posdespliegue de ese ID.

## 3. Aceptación funcional manual observada

| Caso | Observación en capturas aportadas por operador | Estado |
|---|---|---|
| Catálogo universitario | `/universidades` entregó doce instituciones; Flutter cargó bajo `/app/` | **Observado** |
| Publicaciones y fotografías | Publicación de prueba de mouse con tres fotos aparece en «Mis publicaciones» y portada del catálogo; formulario rechazó descripción de más de 500 caracteres | **Observado** |
| Favoritos | Corazones activos y «Mis favoritos» mostrando dos publicaciones guardadas en una cuenta autenticada | **Observado**; persistencia entre sesiones/aislamiento entre cuentas acreditados en CI, no repetidos manualmente |
| Contacto y bandeja | «Contactar al vendedor», «Mis mensajes» y conversación asociada a la publicación | **Observado** |
| Mensajería bidireccional | Comprador envió una consulta; vendedor la vio y respondió; la respuesta apareció en la conversación del comprador | **Observado en ambas cuentas** |
| Universidad visible | La publicación heredada muestra «Universidad no declarada», sin inferir afiliación; nuevo anuncio creado y visible, pero no se adjuntó prueba manual de etiqueta universitaria no nula en esa creación | **Compatibilidad heredada observada**; caso con institución declarada pendiente |

La mensajería usa **HTTP/JSON y actualización manual**; no se afirma entrega instantánea, notificaciones push ni cifrado extremo a extremo. Las pruebas automatizadas de autorización y concurrencia están vinculadas a las evidencias funcionales previas: [Favoritos](incremento-2-favoritos-2026-11-03.md), [Mensajería](incremento-2-mensajeria-2026-11-03.md), [Universidad](incremento-2-universidad-visible-2026-11-03.md).

## 4. Pendientes explícitos y decisión de cierre

- **Pendiente:** comprobar después de la promoción `/health`, estado `healthy` e ID de `db-1`, montajes efectivos e Image ID/configuración del nuevo `api-1`; no se atribuyen estas verificaciones a las capturas previas.
- **Pendiente:** ejecutar S10 posdespliegue en modo instalado contra revisión de imagen `46ede525602161826b75273fbb12528e739908cc`; el éxito de S10 en CI predeploy no sustituye esta ejecución.
- **Pendiente:** respaldo externo y restauración de MySQL/fotografías **no acreditados**; el rollback probado fue **sintético**, no rollback productivo. Evitar una prueba destructiva sin autorización y recuperación verificable.
- **Pendiente:** capturar una publicación nueva con universidad declarada visible y, si se requiere para la evaluación, un nuevo inicio de sesión que demuestre persistencia de Favoritos en la UI.

**Conclusión limitada:** el despliegue de la nueva imagen se completó según los logs; Favoritos, publicaciones y mensajería bidireccional tienen aceptación visual/manual en el dominio institucional. La identidad exacta de los contenedores instalados, las verificaciones operativas pendientes y la recuperación productiva no se declaran cerradas. No se requiere otro despliegue para este cambio documental.

**Navegación:** [arc42 §7](../arc42/07-vista-despliegue.md) · [aspectos](../aspectos.md) · [registro IA](../ia.md) · [operación GHCR](../operacion/despliegue-ghcr.md).
