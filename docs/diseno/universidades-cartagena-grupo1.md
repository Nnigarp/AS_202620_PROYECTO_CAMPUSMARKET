# CampusMarket — diseño de universidades de Cartagena

Estado: especificación de diseño, todavía no implementada ni desplegada. Alcance: Grupo 1, sin S14.

## Registro y acceso

- Conservar interfaz Material 3, paleta violeta y formulario adaptable actual de 460 px, con los modos Iniciar sesión y Crear cuenta.
- Registro: nombre, correo personal o institucional, contraseña y universidad de Cartagena. El campo de universidad solo se muestra al crear cuenta; no al iniciar sesión.
- Presentar universidad como **declarada por el usuario**, nunca como matrícula verificada.
- Catálogo de universidades cargado desde API, con etiquetas completas y orden alfabético. Si la institución falta, explicar cómo solicitar su incorporación, sin aceptar identificadores arbitrarios.
- Indicador al cargar, mensaje claro con Reintentar ante error, validación visible y prevención de envíos duplicados. Teclado y lectores de pantalla accesibles.
- Conservar sesión, cierre de sesión y restricciones actuales de contraseña; el restablecimiento de contraseña se desarrollará como incremento independiente.

## Perfil y publicaciones

- Perfil: mostrar universidad, permitir cambiarla y ofrecer a cuentas antiguas sin universidad completarla sin bloquear el acceso.
- Publicación nueva: guardar institución asociada del usuario desde el backend, sin confiar en un propietario o universidad enviado por el cliente.
- Publicaciones antiguas sin institución: se siguen mostrando, sin inventar asociación retrospectiva.
- Cambiar institución en el perfil no debe cambiar silenciosamente la institución histórica de una publicación.

## Catálogo

- Toda Cartagena es el filtro predeterminado y presenta también publicaciones sin institución.
- Mi universidad aparece para usuarios registrados con institución asignada; visitantes pueden seleccionar universidad manualmente.
- Filtrado por universidad debe combinarse con búsqueda, modalidad, estado y rango de precios.
- Conservar las respuestas contra cambios rápidos de filtros mediante el mecanismo de revisión de solicitudes actual.
- Estados vacíos, carga, error y Reintentar deben ser claros tanto en Web como Android.

## Modelo/API propuestos

- Tabla universidades: id estable, nombre, sigla, ciudad, activa; semillas versionadas.
- usuarios.universidad_id: nullable inicialmente y referencia válida a universidades.
- publicaciones.universidad_id: nullable inicialmente y referencia válida a universidades.
- GET /universidades: catálogo público.
- POST /usuarios/registro: campo universidad_id, inicialmente compatible con clientes antiguos.
- GET/PATCH /usuarios/me: lectura y edición de universidad.
- GET /catalogo?universidad_id=ID: filtro público con validación, sin consultas cruzadas directas entre módulos.
- Ampliar OpenAPI y pruebas junto a cada cambio de contrato.

## Criterios verificables

1. Correo Gmail o institucional aceptado; universidad válida guardada.
2. Login existente no solicita universidad.
3. Cuenta heredada sin universidad inicia sesión y puede completar perfil.
4. Nueva publicación conserva la universidad del vendedor en el momento de creación.
5. Filtro por institución excluye otras y Toda Cartagena incluye publicaciones antiguas.
6. No hay escalada de permisos ni atribución arbitraria de instituciones o propietarios.
7. Web móvil/escritorio y Android sin overflow; controles accesibles.
8. Test backend + Flutter + contrato y CI del mismo SHA aprobados antes de integrar.
9. No modificar producción ni volúmenes, contenedores o red de Dokploy sin autorización y respaldo verificable.

## Flujo de implementación

Backend/MySQL y pruebas -> Flutter responsive y pruebas -> OpenAPI/documentación -> PR de revisión -> despliegue aprobado.
