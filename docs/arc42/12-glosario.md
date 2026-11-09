# 12. Glosario

| Término | Definición en CampusMarket |
|---|---|
| Publicación | Registro mediante el cual un estudiante ofrece un producto en la plataforma. |
| Producto | Artículo que un estudiante desea vender o alquilar. |
| Modalidad | Forma en que se ofrece un producto: `venta` o `alquiler`. |
| Estado del producto | Condición del artículo: `nuevo`, `usado` y `reacondicionado`. |
| Estado de publicación | Disponibilidad del anuncio: `disponible`, `reservado` o `vendido`. |
| Sesión opaca | Token aleatorio Bearer; el servidor conserva su digest y puede revocarlo. |
| Propietario | Usuario identificado por la sesión; solo su ID resuelto por el servidor autoriza mutaciones propias. |
| Visibilidad | Permiso de aparición pública en catálogo; moderación puede ocultar sin eliminar la gestión del propietario. |
| Reporte | Solicitud registrada por un usuario y revisada por una cuenta con capacidad de moderación. |
| Estudiante | Usuario principal que publica o consulta productos dentro de CampusMarket. |
| Administrador | Usuario responsable de supervisar publicaciones y apoyar la gestión del contenido. |
| Catálogo | Conjunto consultable de publicaciones disponibles en CampusMarket. |
| Corte vertical | Recorrido mínimo ejecutable que conecta la interfaz, la lógica y la persistencia del sistema. |
| Universidad declarada | Institución elegida por la cuenta; se fija en el anuncio al crearlo y no demuestra matrícula. |
| Publicación heredada | Anuncio anterior que puede conservar institución `NULL`; no se le atribuye la del perfil actual. |
| Favorito | Referencia privada cuenta/publicación, persistida en MySQL y filtrada por visibilidad al leer. |
| Conversación | Contexto de una publicación y dos participantes autorizados: comprador y vendedor. |
| Mensaje | Texto privado de una conversación; se obtiene por HTTP y actualización manual, sin promesa de push. |
| Clave de idempotencia | Identificador estable del intento; permite recuperar el resultado sin duplicar una creación equivalente. |
| Hash del payload | Huella de la solicitud para detectar contenido distinto reutilizando una clave; no reemplaza autorización. |
| Imagen por digest | Artefacto OCI inmutable; su digest, Image ID, código fuente y revisión informada tienen funciones distintas. |
| Evidencia histórica | Observación con fecha, SHA y entorno propios; un cambio documental posterior no la vuelve a ejecutar. |
