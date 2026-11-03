# Incremento 2 — Universidad declarada visible (2026-11-03)

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
