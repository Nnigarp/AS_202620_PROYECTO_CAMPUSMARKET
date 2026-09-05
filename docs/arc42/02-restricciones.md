# Restricciones - CampusMarket

Las siguientes restricciones delimitan el desarrollo de CampusMarket y
condicionan las decisiones arquitectónicas que puede tomar el equipo. Se
identifican a partir del contexto académico, las condiciones del proyecto
y el alcance definido para el prototipo.

## R-01. Tiempo de desarrollo

**Tipo:** Organizativa  
**Origen:** Asignatura / calendario académico

CampusMarket debe alcanzar un prototipo funcional dentro del semestre
académico.

**Justificación:** El proyecto se desarrolla de manera incremental durante
el curso y debe producir un sistema funcional y verificable dentro del
periodo establecido. Esta condición limita el alcance y la complejidad que
puede asumir el equipo, por lo que las funcionalidades seleccionadas deben
poder implementarse, probarse y documentarse durante el semestre.

---

## R-02. Tamaño del equipo

**Tipo:** Organizativa  
**Origen:** Conformación del equipo

CampusMarket será desarrollado por un equipo de tres integrantes.

**Justificación:** La capacidad de desarrollo disponible está limitada al
trabajo de tres integrantes durante el semestre. Por esta razón, las
decisiones arquitectónicas, el número de funcionalidades y la complejidad
de la solución deben ser compatibles con los recursos humanos disponibles.

---

## R-03. Repositorio y control de versiones

**Tipo:** Técnica / organizativa  
**Origen:** Metodología de trabajo del curso

El código fuente, la documentación arquitectónica y las evidencias
incrementales de CampusMarket deberán mantenerse versionados en el
repositorio del proyecto.

**Justificación:** El repositorio constituye el punto de referencia para
verificar la evolución del sistema y la correspondencia entre documentación,
implementación y evidencias. Además, permite mantener trazabilidad sobre los
cambios realizados por el equipo durante el semestre.

---

## R-04. Análisis de calidad del código

**Tipo:** Técnica  
**Origen:** Herramientas de calidad utilizadas en el proyecto

El repositorio de CampusMarket deberá mantenerse integrado con el proyecto
oficial de SonarQube Cloud durante el desarrollo.

**Justificación:** La integración permite analizar de manera continua
características relacionadas con la calidad y seguridad del código y obtener
evidencia verificable sobre problemas detectados durante el desarrollo. Esta
condición debe considerarse al organizar el repositorio y el flujo de trabajo
del proyecto.

---

## R-05. Alcance funcional del prototipo

**Tipo:** Organizativa / alcance  
**Origen:** Alcance definido por el equipo

La versión inicial de CampusMarket no incluirá pagos en línea, procesamiento
bancario, servicios de envío ni logística de entrega.

**Justificación:** Estas funcionalidades requieren integraciones con servicios
externos y aumentan considerablemente la complejidad técnica y operativa del
sistema. Excluirlas permite concentrar el esfuerzo del equipo en las
capacidades principales del marketplace: gestión de usuarios, publicación
de productos, búsqueda, filtrado y gestión de publicaciones.

---

## R-06. Plataforma web

**Tipo:** Técnica  
**Origen:** Alcance tecnológico inicial

CampusMarket será desarrollado como una aplicación web accesible desde
navegadores modernos.

**Justificación:** La aplicación permite que los estudiantes accedan a
CampusMarket desde computadores, tabletas o teléfonos mediante un navegador,
sin requerir la instalación de una aplicación de escritorio. Esta decisión
mantiene el proyecto dentro de un alcance tecnológico adecuado para el
semestre.

---

## R-07. Persistencia sin nueva infraestructura durante el primer corte

**Tipo:** Técnica / despliegue  
**Origen:** Restricción definida por el equipo para la evaluación arquitectónica S5

Durante el primer corte, CampusMarket debe mantener SQLite como mecanismo
de persistencia y conservar una única unidad de despliegue. La respuesta
arquitectónica al reto no incorporará una base de datos externa, colas,
cachés distribuidas ni nuevos servicios desplegables.

**Justificación:** La restricción limita deliberadamente el espacio de
solución para evaluar si el corte vertical puede responder de manera
controlada ante una condición adversa de persistencia sin resolver el
problema mediante infraestructura adicional.

La solución deberá conservar las fronteras del monolito modular y mejorar
el comportamiento observable del sistema utilizando mecanismos disponibles
dentro de la arquitectura actual.

La línea base medida antes de aplicar cualquier cambio mostró que, ante un
bloqueo temporal de SQLite, la creación de una publicación respondió con
HTTP `500` después de `7.323 s`, sin producir una escritura parcial. Después
de liberar la base, el sistema recuperó la operación normal con HTTP `201`.

Esta evidencia motiva el análisis arquitectónico de S5 sin modificar la
restricción de mantener SQLite y una única unidad de despliegue.

**Evidencia de línea base:**  
[`../evidencias/linea-base-bloqueo-sqlite-2026-09-05.md`](../evidencias/linea-base-bloqueo-sqlite-2026-09-05.md)

---

## Restricciones legales

En esta etapa del proyecto no se ha identificado una restricción legal
específica impuesta formalmente al prototipo.

Si el alcance de CampusMarket evoluciona e incorpora tratamiento adicional
de datos personales, pagos electrónicos u otros servicios externos, las
restricciones legales aplicables deberán identificarse y documentarse antes
de tomar las decisiones arquitectónicas correspondientes.

---

## Resumen

| ID | Restricción | Tipo | Origen |
|---|---|---|---|
| R-01 | Tiempo de desarrollo | Organizativa | Asignatura / calendario académico |
| R-02 | Equipo de tres integrantes | Organizativa | Conformación del equipo |
| R-03 | Repositorio y control de versiones | Técnica / organizativa | Metodología de trabajo del curso |
| R-04 | Integración con SonarQube Cloud | Técnica | Herramientas de calidad del proyecto |
| R-05 | Alcance funcional limitado | Organizativa / alcance | Definición del equipo |
| R-06 | Aplicación web | Técnica | Alcance tecnológico inicial |
| R-07 | Persistencia sin nueva infraestructura durante el primer corte | Técnica / despliegue | Restricción definida por el equipo para S5 |

Estas restricciones establecen límites concretos para CampusMarket y permiten
distinguir las condiciones que restringen el espacio de solución de los
requisitos funcionales y de los escenarios de calidad que posteriormente
deberán verificarse mediante evidencia.
