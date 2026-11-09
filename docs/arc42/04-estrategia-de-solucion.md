# 4. Estrategia de solución

> **Evolución contrastada — 8/nov/2026:** la comparación y la organización
> inicial siguientes conservan el razonamiento de S3. El código integrado mantiene
> ADR-0001 con siete contextos en una API, MySQL y archivos; Favoritos,
> Mensajería y Universidades no añaden servicios Docker. La composición actual
> está en [§5](05-bloques-de-construccion.md) y [C4 L3](../c4/03-componentes-backend.md).
> No se reabre la decisión de estilo ni se sustituye un ADR aceptado.

La comparación y elección inicial siguientes conservan su contexto histórico.
En el código actual ADR-0001 sigue vigente: un backend modular, siete contextos
materializados, Flutter Web/Android y MySQL. La autenticación y las sesiones,
fotografías, moderación y límites se concretan en ADR-0012–0017; ADR-0018 prepara
Compose y ADR-0019 optimiza lecturas sin cambiar fronteras. El estado ejecutable
se detalla en [bloques](05-bloques-de-construccion.md),
[ejecución](06-vista-ejecucion.md) y [decisiones](09-decisiones.md).

## 4.1 Contexto de la decisión

CampusMarket necesita una estrategia arquitectónica que permita construir un prototipo funcional durante el semestre y, al mismo tiempo, mantener una estructura que facilite su evolución sin introducir una complejidad innecesaria.

La decisión se toma considerando las restricciones actuales del proyecto y los escenarios priorizados en el árbol de utilidad.

Las principales restricciones que condicionan la decisión son:

- **R-01 - Tiempo de desarrollo:** el prototipo debe completarse dentro del semestre académico.
- **R-02 - Tamaño del equipo:** CampusMarket será desarrollado por un equipo de tres integrantes.
- **R-05 - Alcance funcional:** el prototipo inicial no incluirá pagos electrónicos, procesamiento bancario, servicios de envío ni logística de entrega.
- **R-06 - Plataforma web:** CampusMarket será desarrollado inicialmente como una aplicación web.

Los escenarios de calidad utilizados para comparar las alternativas arquitectónicas son:

| Escenario | Atributo de calidad | Prioridad |
|---|---|---|
| EC-01 - Consulta de productos | Rendimiento | Alta |
| EC-02 - Protección de publicaciones | Seguridad | Alta |
| EC-03 - Modificación del sistema | Mantenibilidad | Alta |
| EC-04 - Recuperación del prototipo | Disponibilidad y recuperación | Media |

La estrategia seleccionada debe responder principalmente a los escenarios de prioridad alta, pero también debe ser compatible con el tiempo disponible y con la capacidad de desarrollo de un equipo pequeño.

---

## 4.2 Alternativas arquitectónicas evaluadas

Para CampusMarket se evaluaron las siguientes alternativas:

1. **Arquitectura en capas**
2. **Arquitectura hexagonal**
3. **Monolito modular**

La comparación se realiza tomando como referencia los escenarios de calidad del proyecto y no solamente las características generales de cada estilo.

---

## 4.3 Matriz comparativa contra el árbol de utilidad

| Escenario / criterio | Arquitectura en capas | Arquitectura hexagonal | Monolito modular |
|---|---|---|---|
| **EC-01 - Consulta de productos** | **Favorable.** Al ejecutarse dentro de una sola aplicación evita comunicación distribuida. Sin embargo, una consulta puede atravesar varias capas antes de acceder a los datos. | **Favorable.** Permite aislar la lógica de consulta de la infraestructura, aunque introduce puertos y adaptadores que no aportan directamente a reducir el tiempo de respuesta. | **Muy favorable.** El módulo de catálogo puede realizar las consultas dentro del mismo proceso, evitando comunicación remota y manteniendo una estructura sencilla. |
| **EC-02 - Protección de publicaciones** | **Favorable.** Las reglas de autorización pueden ubicarse en la capa de negocio, aunque debe evitarse que estas validaciones se dupliquen entre controladores y servicios. | **Muy favorable.** Las reglas de autorización pueden mantenerse independientes de los mecanismos externos y de persistencia mediante puertos y adaptadores. | **Muy favorable.** El módulo de publicaciones puede ser responsable de validar la propiedad de una publicación antes de permitir su modificación o eliminación. |
| **EC-03 - Modificación del sistema** | **Intermedio.** La organización horizontal puede provocar que un cambio funcional requiera modificaciones en presentación, negocio y persistencia. | **Muy favorable.** Proporciona un aislamiento fuerte entre dominio e infraestructura y facilita las pruebas, pero requiere más interfaces y abstracciones. | **Muy favorable.** Las funcionalidades se agrupan por capacidades del negocio, permitiendo que un cambio relacionado con productos permanezca principalmente dentro de su módulo. |
| **EC-04 - Recuperación del prototipo** | **Favorable.** Puede mantenerse como una sola unidad de despliegue, facilitando el reinicio del sistema. | **Favorable.** Puede desplegarse como una sola aplicación, aunque su estructura interna no aporta por sí misma una ventaja significativa en la recuperación. | **Muy favorable.** Mantiene una única unidad de despliegue y reduce la cantidad de componentes que deben iniciarse o recuperarse durante una demostración. |
| **Complejidad para el equipo** | **Baja.** Es sencilla de comprender e implementar, aunque puede aumentar el acoplamiento entre funcionalidades a medida que crece el sistema. | **Alta.** Requiere definir puertos, adaptadores e interfaces adicionales, aumentando el trabajo inicial del equipo. | **Media-baja.** Define fronteras entre las capacidades del sistema sin introducir infraestructura distribuida ni todas las abstracciones de una arquitectura hexagonal. |
| **Adecuación al alcance actual** | **Aceptable.** Permite desarrollar rápidamente el prototipo, pero ofrece menor aislamiento funcional. | **Aceptable con sobrecosto.** Ofrece buen aislamiento, pero resulta más compleja de lo necesario para el alcance actual. | **Alta.** Equilibra mantenibilidad, simplicidad de despliegue y capacidad de evolución dentro de las restricciones del proyecto. |

---

## 4.4 Decisión

A partir de la comparación realizada, **CampusMarket adoptará un monolito modular como estrategia arquitectónica inicial**.

Esta alternativa mantiene una sola aplicación y una sola unidad de despliegue, pero organiza internamente el sistema mediante módulos con responsabilidades y fronteras explícitas.

La decisión responde especialmente a **EC-03 - Modificación del sistema**, debido a que la separación por capacidades del negocio permite reducir el impacto de los cambios y evitar que una modificación funcional afecte innecesariamente otras partes del sistema.

También resulta adecuada para las restricciones de tiempo y tamaño del equipo, ya que no requiere introducir la complejidad operativa de una solución distribuida ni todas las abstracciones de una arquitectura hexagonal completa.

La decisión se documenta formalmente en:

[ADR-0001 - Usar monolito modular](../adr/0001-usar-monolito-modular.md)

---

## 4.5 Organización inicial del sistema

CampusMarket se organizará inicialmente alrededor de las siguientes capacidades:

### Usuarios

Responsable de:

- registro de usuarios;
- autenticación;
- gestión básica de la información del usuario.

### Publicaciones

Responsable de:

- creación de publicaciones;
- modificación de publicaciones;
- eliminación de publicaciones;
- validación de propiedad de una publicación.

### Catálogo

Responsable de:

- consulta de productos;
- búsqueda;
- filtrado;
- presentación de productos disponibles.

### Administración

Responsable de:

- supervisión básica de publicaciones;
- apoyo a la gestión del contenido de la plataforma.

Cada módulo deberá mantener responsabilidades claras y evitar dependencias directas hacia los detalles internos de otros módulos.

Cuando sea necesaria la comunicación entre módulos, esta deberá realizarse mediante interfaces o servicios explícitos definidos por la aplicación.

Los módulos no se desplegarán como servicios independientes durante esta etapa del proyecto.

---

## 4.6 Tácticas arquitectónicas

### EC-01 - Rendimiento de las consultas

Para favorecer el cumplimiento del escenario de consulta de productos se aplicarán las siguientes tácticas:

- mantener las operaciones de búsqueda dentro del mismo proceso de la aplicación;
- evitar comunicación remota innecesaria entre módulos;
- concentrar las operaciones de consulta y filtrado en el módulo de catálogo;
- preparar las consultas para utilizar paginación e índices cuando se implemente la persistencia.

Estas tácticas buscan contribuir al cumplimiento de la medida definida en EC-01: que al menos **9 de 10 consultas consecutivas**, sobre un catálogo de hasta **1.000 publicaciones**, presenten los resultados en un máximo de **2 segundos**.

### EC-02 - Seguridad de las publicaciones

Para proteger las publicaciones se aplicarán las siguientes tácticas:

- autenticar al usuario antes de ejecutar operaciones protegidas;
- verificar la propiedad de una publicación antes de permitir su modificación o eliminación;
- centralizar las reglas relacionadas con publicaciones dentro del módulo correspondiente;
- rechazar por defecto cualquier operación que no cumpla las reglas de autorización.

Estas tácticas apoyan el cumplimiento de EC-02, que exige rechazar los intentos de modificación realizados por usuarios que no sean propietarios de la publicación.

### EC-03 - Mantenibilidad

Para limitar el impacto de las modificaciones se aplicarán las siguientes tácticas:

- modularizar el sistema por capacidades del negocio;
- mantener responsabilidades explícitas para cada módulo;
- evitar dependencias directas hacia componentes internos de otros módulos;
- utilizar contratos claros para la comunicación entre módulos;
- mantener separadas las responsabilidades de usuarios, publicaciones, catálogo y administración.

Estas tácticas están directamente relacionadas con la medida de EC-03: una modificación relacionada con el estado de un producto deberá requerir cambios en **como máximo dos módulos principales**, sin afectar autenticación ni búsqueda.

### EC-04 - Recuperación del prototipo

Para facilitar la recuperación del sistema se aplicarán las siguientes tácticas:

- mantener una única unidad de despliegue durante el prototipo;
- proporcionar un único comando de inicio documentado en el README;
- mantener dentro del repositorio la configuración necesaria para reproducir la ejecución, sin almacenar credenciales;
- separar los datos persistentes del proceso de ejecución de la aplicación;
- mantener un procedimiento reproducible de inicio y prueba.

Estas decisiones buscan apoyar el objetivo de recuperar el funcionamiento del prototipo en un máximo de **10 minutos** ante una falla durante una prueba o demostración.

---

## 4.7 Consecuencias de la decisión

La adopción de un monolito modular presenta las siguientes consecuencias positivas:

- mantiene una única aplicación para desarrollar y desplegar;
- reduce la complejidad operativa para un equipo de tres integrantes;
- permite organizar el código de acuerdo con capacidades del negocio;
- facilita limitar el impacto de los cambios;
- evita introducir comunicación distribuida innecesaria;
- facilita las pruebas de los módulos;
- permite evolucionar posteriormente la solución si aparecen nuevas necesidades.

También introduce las siguientes responsabilidades y limitaciones:

- las fronteras entre módulos deberán respetarse durante la implementación;
- deberá evitarse que las dependencias entre módulos conviertan el sistema en un monolito sin estructura;
- la aplicación continuará desplegándose como una sola unidad;
- no será posible escalar cada módulo de manera independiente;
- el equipo deberá mantener explícitas las dependencias permitidas entre módulos.

Para el alcance actual de CampusMarket, estas consecuencias se consideran aceptables frente a las restricciones de tiempo, tamaño del equipo y alcance del prototipo.

---

## 4.8 Alternativa menos adecuada para el contexto actual

De las alternativas evaluadas, la **arquitectura hexagonal es la menos adecuada para el alcance actual de CampusMarket**, aunque técnicamente ofrece ventajas importantes en testabilidad, sustitución de infraestructura y aislamiento del dominio.

El principal problema no es que el estilo sea inadecuado en sí mismo, sino el costo que introduce frente a las restricciones actuales del proyecto. Su aplicación requiere definir puertos, adaptadores, interfaces y mecanismos adicionales de inversión de dependencias, aumentando la cantidad de código de infraestructura y la indirección que debe mantener el equipo.

Para un proyecto desarrollado por tres integrantes dentro de un semestre y con un prototipo de alcance controlado, este costo inicial no genera una mejora suficiente frente al monolito modular.

En particular:

- **EC-03 - Mantenibilidad:** la arquitectura hexagonal ofrece una respuesta muy favorable, pero el monolito modular permite obtener un aislamiento suficiente con menor complejidad estructural.
- **EC-01 - Rendimiento:** ninguno de los dos estilos requiere comunicación distribuida, por lo que la arquitectura hexagonal no aporta una ventaja determinante para el tiempo de respuesta esperado.
- **R-01 - Tiempo de desarrollo:** la cantidad adicional de interfaces y adaptadores aumenta el trabajo inicial del equipo.
- **R-02 - Tamaño del equipo:** mantener correctamente las abstracciones de una arquitectura hexagonal exige una disciplina que resulta costosa para el tamaño y alcance actual del proyecto.

Por estas razones, la arquitectura hexagonal se descarta para esta etapa. Podría reconsiderarse en el futuro si CampusMarket requiere sustituir infraestructura con frecuencia, integrar múltiples mecanismos externos o aislar con mayor rigor el dominio de sus adaptadores.

---

## 4.9 Principios de modularidad aplicados

La estrategia de monolito modular se complementará con principios de diseño orientados a mantener bajo acoplamiento y alta cohesión.

Para **EC-03 - Modificación del sistema**, se utilizarán principalmente:

- **SRP (Single Responsibility Principle):** cada componente tendrá una responsabilidad y una razón principal de cambio.
- **DIP (Dependency Inversion Principle):** cuando sea necesario desacoplar módulos, las dependencias se dirigirán hacia contratos o abstracciones y no hacia detalles internos.
- **Alta cohesión (GRASP):** las responsabilidades relacionadas permanecerán dentro del mismo módulo.
- **Bajo acoplamiento (GRASP):** se limitarán las dependencias entre los módulos `usuarios`, `publicaciones`, `catalogo` y `administracion`.
- **Variaciones protegidas (GRASP):** los elementos que se espera que cambien se mantendrán encapsulados detrás de responsabilidades o contratos claramente definidos.

Estas tácticas favorecen la mantenibilidad, pero introducen un costo: requieren mayor disciplina en la organización del código y, en algunos casos, interfaces o elementos de indirección adicionales. El equipo acepta este costo porque permite reducir el impacto de futuras modificaciones sin adoptar la complejidad completa de una arquitectura hexagonal.
