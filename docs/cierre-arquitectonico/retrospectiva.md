# Retrospectiva del cierre arquitectónico

## Qué repetiríamos

La separación entre consumidor y proveedor permitió mantener OpenAPI v2 y observar la secuencia 200 → 422 → 200 con el cliente adaptado. Conservar el resultado fallido de noviembre hizo posible detectar que una promoción había cambiado la imagen mientras el contrato seguía siendo el mismo. En otra entrega registraríamos juntos el digest, el SHA de construcción y el contrato independiente en el momento de promover. [Experimento S17](../evidencias/datos/s17-contrato-publico/resumen.json)

## Qué cambiaríamos

La matriz de aspectos tenía destinos navegables, pero una prueba de health no respondía a la pregunta de si podíamos recuperar fotos y filas del mismo instante. Elegiríamos primero el fallo que debe detectar cada prueba y después la evidencia que se enlazará. La omisión de la tabla de idempotencia ilustra el coste de mantener una lista manual de propietarios. En cada cambio de esquema pediríamos una prueba que falle ante una escritura desde otro contexto. [Guarda](../../backend/tests/test_propiedad_datos.py)

En EC-01 se contó el tiempo de red antes de tener un observador fiable del resultado pintado. La última serie conservó cinco muestras válidas, tres fallos de preparación y dos consultas del filtro anterior. Validaríamos primero el observador con una búsqueda conocida y un retraso visible controlado. Congelaríamos carga, navegador y límites antes de iniciar los diez intentos. [Ensayo S14](../evidencias/evidencia-s14-ec01-2026-11-05.md)

El registro de IA permitió reconstruir propuestas descartadas. También puso en evidencia el límite de la asistencia automática cuando faltan el formulario del jurado y las observaciones de pares. En futuras entregas guardaríamos los originales al recibirlos, con fecha, procedencia y acceso apropiado. [Registro de IA](../ia.md)

## Lecciones individuales confirmadas

Las tres lecciones, inicialmente propuestas con apoyo de IA, fueron confirmadas conjuntamente por los integrantes el 27 de noviembre de 2026.

| Integrante | Lección confirmada | Acción observable en otro proyecto |
|---|---|---|
| Nilver García Pimentel | Una promoción puede cambiar la revisión servida aunque el esquema conserve su contenido. | Adjuntar al PR de promoción la relación entre fuente, digest, contrato y lectura posterior. |
| Joshua Tenorio | Un observador que conserva el filtro anterior invalida la medición de experiencia visible. | Incluir un control previo que distinga la búsqueda nueva y registrar todos los intentos. |
| Camilo Martínez | Una suite funcional puede aprobar mientras una tabla queda fuera de la guarda arquitectónica. | Revisar cada nueva tabla junto a su propietario y demostrar el fallo con un segundo escritor sintético. |

## Conformidad del equipo

El 27/nov/2026 a las 19:04 (Colombia), los tres integrantes, Nilver García Pimentel, Joshua Tenorio y Camilo Martínez, comunicaron conjuntamente en el chat de cierre que confirmaban sus respectivas lecciones individuales, aprobaban el ADR-0027 y autorizaban registrar la conformidad en GitHub. Es una declaración conjunta del equipo recibida en el chat, no tres firmas digitales independientes.

Texto comunicado: «Los tres integrantes, Nilver, Joshua y Camilo, confirmamos nuestras respectivas lecciones individuales y aprobamos el ADR-0027. Autorizamos registrar esta conformidad en nuestra rama de GitHub.»

[ADR-0027 aceptado](../adr/0027-validar-trazabilidad-documental-en-ci.md). Esta conformidad no acredita la recepción de las recomendaciones originales del jurado ni de pares.
