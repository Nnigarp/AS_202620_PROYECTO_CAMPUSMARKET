# Evidencia de ensayo local — Flutter Web, API y MySQL

Fecha: 2026-10-31
Proyecto: CampusMarket
Entorno: Docker local (Windows)
Rama: fix/development-redes-20261031
Commit de configuración: 0d22a94

## Alcance

Prueba funcional local con datos de ensayo.
No constituye evidencia de despliegue exitoso en ISCOUTB.
No se utilizaron volúmenes ni bases de datos de producción.

## Componentes

- Flutter Web y FastAPI: imagen GHCR inmutable sha256:65d34f2de8d035d5a9672be2e6a81bab759089da2fbe91bdca23a17f2f0463fd
- MySQL 8.4: imagen fijada por digest en deploy/compose.development.yaml
- Red de datos: campusmarket-ensayo-local-20261031_dev_data
- Red HTTP simulada: campusmarket-ensayo-traefik-local
- Proxy local: Nginx en 127.0.0.1:8088

## Resultados observados

1. Docker Compose valido sintacticamente.
2. FastAPI y MySQL alcanzaron estado healthy.
3. GET /health devolvio status=ok y service=campusmarket-api.
4. GET /app/ devolvio HTTP 200 y contenido HTML.
5. Flutter Web se renderizo en Chrome.
6. El catalogo y la navegacion funcionaron.
7. Se creo un usuario de ensayo.
8. Se creo una publicacion con fotografias.
9. La publicacion aparecio en Mis publicaciones y Catalogo.
10. Se probaron las opciones de edicion y cambio de estado.
11. Tras reiniciar api y db, la publicacion y su fotografia siguieron disponibles.
12. MySQL permanecio fuera de la red HTTP simulada.

## Persistencia verificada

MySQL:
- Volumen: campusmarket-ensayo-local-20261031_dev_mysql_data
- Destino: /var/lib/mysql

Fotografias:
- Volumen: campusmarket-ensayo-local-20261031_dev_publication_images
- Destino: /app/backend/uploads

## Limitaciones

- El despliegue development de ISCOUTB no se completo.
- Docker en ISCOUTB reporto: all predefined address pools have been fully subnetted.
- La prueba local no demuestra disponibilidad de subredes en ISCOUTB.
- Preview Compose de Dokploy sigue agregando la red externa al servicio db.
- No se realizaron cambios en production ni en ISCOUTB/master.

## Conclusion

Ensayo funcional local aprobado.
Despliegue institucional pendiente por restricciones de red.
