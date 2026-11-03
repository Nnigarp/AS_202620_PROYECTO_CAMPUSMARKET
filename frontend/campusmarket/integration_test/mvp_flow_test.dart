import 'dart:convert';
import 'dart:math';

import 'package:campusmarket/app/campus_market_app.dart';
import 'package:campusmarket/app/inicio_page.dart';
import 'package:campusmarket/favoritos/favoritos_controller.dart';
import 'package:campusmarket/publicaciones/publicaciones_api.dart';
import 'package:campusmarket/publicaciones/mis_publicaciones_page.dart';
import 'package:campusmarket/shared/api_configuration.dart';
import 'package:campusmarket/shared/api_error.dart';
import 'package:campusmarket/usuarios/session_controller.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:integration_test/integration_test.dart';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('MVP real: A, B y moderación con imágenes y aislamiento EC-02', (tester) async {
    final session = SessionController.instance;
    final api = PublicacionesApi();
    final checks = <String>[];
    final platform = kIsWeb ? const String.fromEnvironment('CAMPUSMARKET_VIEWPORT', defaultValue: 'web') : 'android';
    final nonce = DateTime.now().microsecondsSinceEpoch.toString();
    final emailA = 'a-$nonce@campus.test';
    final emailB = 'b-$nonce@campus.test';
    final emailC = 'c-$nonce@campus.test';
    final random = Random.secure();
    String password() => base64UrlEncode(List<int>.generate(24, (_) => random.nextInt(256)));
    final passwordA = password(), passwordB = password(), passwordC = password();
    final title = 'Libro de campus $nonce';
    final editedTitle = 'Libro actualizado $nonce';
    var screenNumber = 0;
    var surfaceConverted = false;
    final initialSemanticsHandles = binding.debugOutstandingSemanticsHandles;

    Future<void> until(bool Function() condition, String description) async {
      final deadline = DateTime.now().add(const Duration(seconds: 45));
      while (!condition() && DateTime.now().isBefore(deadline)) {
        await tester.pump(const Duration(milliseconds: 200));
      }
      expect(condition(), isTrue, reason: description);
    }

    Future<void> click(Finder finder) async {
      await until(() => finder.evaluate().isNotEmpty, 'Control visible');
      FocusManager.instance.primaryFocus?.unfocus();
      await tester.pump(const Duration(milliseconds: 150));
      await tester.ensureVisible(finder.first);
      await tester.pump(const Duration(milliseconds: 200));
      await until(() => finder.hitTestable().evaluate().isNotEmpty, 'Control alcanzable tras desplazar');
      await tester.tap(finder.first);
      await tester.pump(const Duration(milliseconds: 300));
    }

    Future<void> fill(String key, String text) async {
      final finder = find.byKey(Key(key));
      await click(finder);
      await tester.enterText(finder, text);
      await tester.pump(const Duration(milliseconds: 200));
      final editable = tester.widget<EditableText>(
        find.descendant(of: finder, matching: find.byType(EditableText)),
      );
      // Comparar booleanos evita imprimir contraseñas ante un fallo.
      expect(editable.controller.text == text, isTrue, reason: 'Texto entregado al campo $key');
    }

    Future<void> screenshot(String name) async {
      FocusManager.instance.primaryFocus?.unfocus();
      await tester.pump(const Duration(milliseconds: 350));
      if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android && !surfaceConverted) {
        await binding.convertFlutterSurfaceToImage();
        surfaceConverted = true;
        await tester.pump();
      }
      screenNumber++;
      await binding.takeScreenshot('$platform-$screenNumber-$name');
      expect(tester.takeException(), isNull, reason: 'Sin excepciones de layout ni imágenes');
    }

    Future<void> catalogResult(String text, String description) async {
      final results = find.byKey(const Key('catalogo-resultados'));
      await until(() => results.evaluate().isNotEmpty, 'Sección de resultados');
      await tester.ensureVisible(results);
      await tester.pump(const Duration(milliseconds: 250));
      await until(() => find.text(text).evaluate().isNotEmpty, description);
    }

    binding.reportData ??= <String, dynamic>{};
    binding.reportData!['checks'] = checks;
    binding.reportData!['platform'] = platform;

    Future<void> enterAccount(String name, String email, String pass, {bool register = false}) async {
      await click(find.byKey(const Key('cuenta')));
      if (register) {
        await click(find.text('Crear cuenta'));
        await fill('auth-nombre', name);
        await fill('auth-correo', email);
        await fill('auth-password', pass);
        await screenshot('registro');
        await click(find.byKey(const Key('auth-enviar')));
        await until(() => find.textContaining('Cuenta creada.').evaluate().isNotEmpty, 'Registro confirmado por backend');
      }
      await fill('auth-correo', email);
      await fill('auth-password', pass);
      await screenshot('login');
      await click(find.byKey(const Key('auth-enviar')));
      await until(() => session.authenticated && find.byKey(const Key('cuenta')).evaluate().isNotEmpty, 'Login y regreso al campus');
    }

    Future<void> logout() async {
      final previousHeaders = session.authorizedHeaders;
      await click(find.byKey(const Key('cuenta')));
      final control = find.byKey(const Key('logout'));
      await until(() => control.evaluate().isNotEmpty && tester.widget<OutlinedButton>(control).onPressed != null, 'Perfil consultado');
      await click(control);
      await until(() => !session.authenticated && find.byKey(const Key('cuenta')).evaluate().isNotEmpty, 'Logout confirmado');
      final response = await http.get(Uri.parse('$defaultApiBaseUrl/usuarios/me'), headers: previousHeaders);
      expect(response.statusCode, 401, reason: 'Token anterior revocado en MySQL');
    }

    Future<Map<String, dynamic>> ownPublication() async {
      final list = await api.listarMisPublicaciones();
      expect(list, hasLength(1));
      return list.single;
    }

    Future<void> waitImages(int count) async {
      final deadline = DateTime.now().add(const Duration(seconds: 45));
      while (DateTime.now().isBefore(deadline)) {
        await tester.pump(const Duration(milliseconds: 250));
        final own = await ownPublication();
        if ((own['imagenes'] as List).length == count &&
            find.byType(LinearProgressIndicator).evaluate().isEmpty) {
          return;
        }
      }
      fail('La galería no alcanzó la cantidad esperada.');
    }

    try {
    await tester.pumpWidget(const CampusMarketApp());
    await until(() => find.byType(CircularProgressIndicator).evaluate().isEmpty, 'Inicio cargado');
    await screenshot('inicio-vacio');
    final logicalSize = tester.view.physicalSize / tester.view.devicePixelRatio;
    binding.reportData!['viewport'] = {'width': logicalSize.width, 'height': logicalSize.height};
    if (platform == 'web-mobile') {
      expect(logicalSize.width, lessThanOrEqualTo(600), reason: 'Viewport móvil real');
    } else if (platform == 'web-desktop') {
      expect(logicalSize.width, greaterThanOrEqualTo(1100), reason: 'Viewport escritorio real');
    }
    await enterAccount('Estudiante A', emailA, passwordA, register: true);
    final ownerA = session.usuario!.id;
    checks.add('Registro, login y usuario actual A');

    await click(find.byKey(const Key('nav-catalogo')));
    await click(find.byKey(const Key('nav-publicar')));
    await fill('publicacion-titulo', title);
    await fill('publicacion-descripcion', 'Libro para el próximo semestre, conservado y con todas sus páginas.');
    await fill('publicacion-precio', '65000,50');
    await click(find.byKey(const Key('publicacion-fotografias')));
    await until(() => find.text('1/3').evaluate().isNotEmpty, 'Selector nativo/Web devuelve imagen real');
    await screenshot('publicar');
    await click(find.byKey(const Key('publicacion-guardar')));
    await until(() => find.byType(MisPublicacionesPage).evaluate().isNotEmpty &&
        find.text(title).evaluate().isNotEmpty && find.byType(CircularProgressIndicator).evaluate().isEmpty,
        'Guardado e imágenes terminados; publicación cargada en Mis publicaciones');
    var own = await ownPublication();
    final id = own['id'] as int;
    expect(own['propietario_id'], ownerA);
    expect(own['precio'], 65000.5);
    expect(own['imagenes'], hasLength(1));
    checks.add('Publicación con propietario real, precio normalizado e imagen desde selector');

    await click(find.text('Fotografías'));
    await until(() => find.byKey(const Key('galeria-agregar')).evaluate().isNotEmpty &&
        tester.widget<FilledButton>(find.byKey(const Key('galeria-agregar'))).onPressed != null, 'Galería propia cargada');
    await click(find.byKey(const Key('galeria-agregar')));
    await waitImages(2);
    await click(find.byKey(const Key('galeria-agregar')));
    await waitImages(3);
    own = await ownPublication();
    final images = (own['imagenes'] as List).cast<Map<String, dynamic>>();
    final firstImage = images.first;
    final thirdImage = images.last;
    final fixture = await http.get(Uri.parse('$defaultApiBaseUrl${firstImage['imagen_url']}'));
    expect(fixture.statusCode, 200);
    await expectLater(api.subirImagen(
      publicacionId: id, imagen: ImagenPublicacion(nombre: 'extra.png', bytes: fixture.bodyBytes),
    ), throwsA(isA<ApiException>().having((error) => error.statusCode, 'statusCode', 400)));
    expect(tester.widget<FilledButton>(find.byKey(const Key('galeria-agregar'))).onPressed, isNull);
    await click(find.byKey(Key("imagen-principal-${thirdImage['id']}")));
    await until(() => find.byKey(Key("imagen-principal-${thirdImage['id']}")).evaluate().isEmpty, 'Nueva principal confirmada');
    own = await ownPublication();
    expect((own['imagenes'] as List).where((image) => image['es_principal'] == true).single['id'], thirdImage['id']);
    await screenshot('galeria-tres');
    await click(find.byKey(Key("imagen-eliminar-${firstImage['id']}")));
    await click(find.widgetWithText(FilledButton, 'Eliminar fotografía'));
    await waitImages(2);
    expect((await http.get(Uri.parse('$defaultApiBaseUrl${firstImage['imagen_url']}'))).statusCode, 404);
    own = await ownPublication();
    final remainingImages = (own['imagenes'] as List).cast<Map<String, dynamic>>();
    checks.add('Máximo 3 imágenes, cambiar principal y eliminar fotografía con limpieza real');
    await tester.pageBack();
    await tester.pump(const Duration(milliseconds: 300));

    await click(find.byKey(const Key('nav-inicio')));
    // La portada carga async y muestra como máximo cuatro publicaciones.
    // Asegurar primero que el dato persiste y la lista realmente terminó de
    // cargar, antes de buscar la tarjeta visible en pantallas compactas.
    final catalogoRespuesta = await http.get(Uri.parse('$defaultApiBaseUrl/catalogo'));
    expect(catalogoRespuesta.statusCode, 200, reason: 'API catálogo disponible tras publicar');
    final catalogoDatos = (jsonDecode(catalogoRespuesta.body) as List).cast<Map<String, dynamic>>();
    expect(catalogoDatos.any((dato) => dato['titulo'] == title), isTrue,
        reason: 'Publicación persistida en catálogo antes de verificar portada');
    await until(() => find.text('Publicaciones recientes').evaluate().isNotEmpty,
        'Encabezado de publicaciones en Inicio');
    // En Android, LayoutBuilder no necesariamente se construye hasta entrar
    // al viewport. Mover primero el encabezado a la vista y luego comprobar
    // que la cuadrícula se haya construido, evitando un falso negativo.
    await tester.ensureVisible(find.text('Publicaciones recientes'));
    await tester.pumpAndSettle();
    await until(() => find.byKey(const Key('inicio-publicaciones-lista')).evaluate().isNotEmpty,
        'Inicio construyó la lista visible de publicaciones');
    final inicioScroll = find.descendant(
      of: find.byType(InicioPage),
      matching: find.byType(Scrollable),
    ).first;
    await tester.ensureVisible(find.byKey(const Key('inicio-publicaciones-lista')));
    await tester.pumpAndSettle();
    // El texto debe estar en la portada real, no solo en una respuesta HTTP.
    // Desplazar las tarjetas en Android sin asumir un viewport fijo.
    for (var intento = 0; intento < 8; intento++) {
      if (find.text(title).hitTestable().evaluate().isNotEmpty) break;
      await tester.drag(inicioScroll, const Offset(0, -180));
      await tester.pumpAndSettle();
    }
    await until(() => find.text(title).hitTestable().evaluate().isNotEmpty,
        'Portada usa publicación existente');
    await screenshot('inicio-con-producto');
    await click(find.byKey(const Key('nav-catalogo')));
    await catalogResult(title, 'Producto visible en catálogo');
    await screenshot('catalogo');
    await fill('catalogo-busqueda', 'inexistente-$nonce');
    await click(find.byTooltip('Buscar'));
    await catalogResult('No encontramos publicaciones', 'Búsqueda real sin resultados');
    await fill('catalogo-busqueda', 'LIBRO DE CAMPUS');
    await click(find.byTooltip('Buscar'));
    await catalogResult(title, 'Búsqueda real sin distinguir mayúsculas');
    await click(find.text('Limpiar'));
    await catalogResult(title, 'Limpiar restaura catálogo');
    await fill('catalogo-precio-min', '70000');
    await click(find.text('Aplicar filtros'));
    await catalogResult('No encontramos publicaciones', 'Precio mínimo filtra publicación real');
    await fill('catalogo-precio-min', '60000');
    await fill('catalogo-precio-max', '65000,50');
    await click(find.text('Aplicar filtros'));
    await catalogResult(title, 'Rango incluye precio exacto con coma');
    await fill('catalogo-precio-min', '70000');
    await click(find.text('Aplicar filtros'));
    await catalogResult('El precio mínimo no puede superar al máximo.', 'Error de rango visible');
    await click(find.text('Limpiar'));
    await catalogResult(title, 'Filtros restaurados');
    checks.add('Búsqueda, precios, error de rango, estado vacío y limpieza de filtros reales');
    await click(find.text(title));
    await until(() => find.text('Descripción').evaluate().isNotEmpty, 'Detalle actual consultado');
    expect(find.byKey(const Key('reportar-publicacion')), findsNothing);
    await screenshot('detalle-A');
    await click(find.byKey(Key('favorito-$id')));
    await until(() => FavoritosController.instance.contiene(id), 'Corazón A guardado en MySQL');
    await tester.pageBack();
    await tester.pump(const Duration(milliseconds: 200));

    await click(find.byKey(const Key('nav-mias')));
    await click(find.text('Editar'));
    await fill('editar-titulo', editedTitle);
    await click(find.text('Guardar cambios'));
    await until(() => find.text(editedTitle).evaluate().isNotEmpty, 'Edición persistida');
    await click(find.byWidgetPredicate((widget) => widget is PopupMenuButton<String>));
    await click(find.text('Marcar reservado'));
    await until(() => find.text('Reservado').evaluate().isNotEmpty, 'Estado reservado visible');
    own = await ownPublication();
    expect(own['titulo'], editedTitle);
    expect(own['estado_publicacion'], 'reservado');
    await screenshot('mias-A-reservado');
    checks.add('Edición y cambio de estado persistidos');
    await logout();

    await enterAccount('Estudiante B', emailB, passwordB, register: true);
    expect(session.usuario!.id, isNot(ownerA));
    await click(find.byKey(const Key('nav-catalogo')));
    await catalogResult(editedTitle, 'B ve publicación de A');
    await click(find.text(editedTitle));
    await until(() => find.byKey(const Key('reportar-publicacion')).evaluate().isNotEmpty, 'B puede reportar, sin controles de edición ajena');
    expect(find.text('Editar'), findsNothing);
    expect(find.text('Eliminar'), findsNothing);
    await screenshot('detalle-B');
    await FavoritosController.instance.ensureLoaded();
    expect(FavoritosController.instance.contiene(id), isFalse, reason: 'Favorito privado de A no aparece para B');
    await click(find.byKey(Key('favorito-$id')));
    await until(() => FavoritosController.instance.contiene(id), 'B guarda su propio favorito');
    await tester.pageBack();
    await tester.pump(const Duration(milliseconds: 200));
    await click(find.byKey(const Key('nav-favoritos')));
    await until(() => find.text(editedTitle).evaluate().isNotEmpty, 'Favorito visible en pantalla privada');
    await screenshot('favoritos-B');
    await logout();
    await enterAccount('Estudiante B', emailB, passwordB);
    await click(find.byKey(const Key('nav-favoritos')));
    await until(() => find.text(editedTitle).evaluate().isNotEmpty, 'Favorito persiste tras logout y nuevo login');
    await click(find.byKey(Key('favorito-$id')));
    await until(() => !FavoritosController.instance.contiene(id), 'Quitar favorito confirmado por API');
    checks.add('Favoritos privados A/B, corazón, pantalla, persistencia tras logout y eliminación');
    await click(find.byKey(const Key('nav-catalogo')));
    await catalogResult(editedTitle, 'Regreso al catálogo');
    await click(find.text(editedTitle));
    await until(() => find.byKey(const Key('reportar-publicacion')).evaluate().isNotEmpty, 'Detalle de B consultado de nuevo');

    final buyerMessage = 'Hola, me interesa el libro $nonce';
    final sellerMessage = 'Podemos coordinar la entrega en el campus $nonce';
    await click(find.byKey(const Key('contactar-vendedor')));
    await until(() => find.byKey(const Key('chat-texto')).evaluate().isNotEmpty &&
      tester.widget<TextField>(find.byKey(const Key('chat-texto'))).enabled == true, 'Conversación propia cargada');
    await fill('chat-texto', buyerMessage);
    await click(find.byKey(const Key('chat-enviar')));
    await until(() => find.text(buyerMessage).evaluate().isNotEmpty, 'Mensaje comprador persistido');
    await screenshot('chat-comprador');
    await tester.pageBack();
    await tester.pump(const Duration(milliseconds: 200));
    await tester.pageBack();
    await tester.pump(const Duration(milliseconds: 200));
    await click(find.byKey(const Key('nav-mensajes')));
    await until(() => find.text(editedTitle).evaluate().isNotEmpty, 'Bandeja del comprador');
    await logout();
    await enterAccount('Estudiante A', emailA, passwordA);
    await click(find.byKey(const Key('nav-mensajes')));
    await until(() => find.text(editedTitle).evaluate().isNotEmpty, 'Bandeja del vendedor recibe conversación');
    await click(find.text(editedTitle));
    await until(() => find.text(buyerMessage).evaluate().isNotEmpty, 'Vendedor recibe mensaje persistente');
    await fill('chat-texto', sellerMessage);
    await click(find.byKey(const Key('chat-enviar')));
    await until(() => find.text(sellerMessage).evaluate().isNotEmpty, 'Respuesta vendedor persistida');
    await screenshot('chat-vendedor');
    await tester.pageBack();
    await tester.pump(const Duration(milliseconds: 200));
    await logout();
    await enterAccount('Estudiante B', emailB, passwordB);
    await click(find.byKey(const Key('nav-mensajes')));
    await until(() => find.text(editedTitle).evaluate().isNotEmpty, 'Conversación persiste tras logout');
    await click(find.text(editedTitle));
    await until(() => find.text(sellerMessage).evaluate().isNotEmpty, 'Comprador recibe respuesta real');
    checks.add('Mensajería HTTP: contactar, bandejas A/B, envío/respuesta y persistencia tras logout');
    await tester.pageBack();
    await tester.pump(const Duration(milliseconds: 200));
    await click(find.byKey(const Key('nav-catalogo')));
    await catalogResult(editedTitle, 'Regreso desde Mensajes al catálogo');
    await click(find.text(editedTitle));
    await until(() => find.byKey(const Key('reportar-publicacion')).evaluate().isNotEmpty, 'Detalle antes de ataques EC-02');

    Future<void> spoofedRequest(String method, String path, {Object? body}) async {
      final request = http.Request(method, Uri.parse('$defaultApiBaseUrl$path?propietario_id=$ownerA'));
      request.headers.addAll(session.authorizedHeaders);
      if (body != null) request.body = jsonEncode(body);
      final response = await http.Response.fromStream(await request.send());
      expect(response.statusCode, 404);
      throw const ApiException('Publicación ajena rechazada.', statusCode: 404);
    }
    final attacks = <Future<void> Function()>[
      () async { await api.editarPublicacion(publicacionId: id, titulo: 'Cambio ajeno', descripcion: 'Intento válido de edición ajena', precio: 1, modalidad: 'venta', estado: 'nuevo'); },
      () => api.eliminarPublicacion(id),
      () async { await api.cambiarEstadoPublicacion(publicacionId: id, estadoPublicacion: 'vendido'); },
      () => api.elegirPrincipal(id, remainingImages.first['id'] as int),
      () => api.eliminarImagen(id, remainingImages.first['id'] as int),
      () async { await api.subirImagen(publicacionId: id, imagen: ImagenPublicacion(nombre: 'ajena.png', bytes: fixture.bodyBytes)); },
      () => spoofedRequest('DELETE', '/publicaciones/$id'),
      () => spoofedRequest('PUT', '/publicaciones/$id', body: {'titulo': 'Cambio ajeno', 'descripcion': 'Intento de suplantación', 'precio': 1, 'modalidad': 'venta', 'estado': 'nuevo'}),
      () => spoofedRequest('PATCH', '/publicaciones/$id/estado', body: {'estado_publicacion': 'vendido'}),
      () => spoofedRequest('PUT', "/publicaciones/$id/imagenes/${remainingImages.first['id']}/principal"),
    ];
    expect(attacks, hasLength(10));
    for (final attack in attacks) {
      await expectLater(attack(), throwsA(isA<ApiException>().having((error) => error.statusCode, 'statusCode', 404)));
      final response = await http.get(Uri.parse('$defaultApiBaseUrl/catalogo/$id'));
      expect(response.statusCode, 200);
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      expect(data['propietario_id'], ownerA);
      expect(data['titulo'], editedTitle);
      expect(data['precio'], 65000.5);
      expect(data['estado_publicacion'], 'reservado');
      expect(data['imagenes'], hasLength(2));
    }
    final adminAccess = await http.get(Uri.parse('$defaultApiBaseUrl/administracion/reportes'), headers: session.authorizedHeaders);
    expect(adminAccess.statusCode, 403);
    checks.add('EC-02: 10/10 modificaciones ajenas rechazadas; datos intactos tras cada ataque');

    await click(find.byKey(const Key('reportar-publicacion')));
    await fill('reporte-motivo', 'Revisar descripción en esta prueba funcional controlada.');
    await click(find.byKey(const Key('reporte-enviar')));
    await until(() => find.textContaining('Reporte recibido.').evaluate().isNotEmpty, 'Reporte registrado');
    await tester.pageBack();
    await tester.pump(const Duration(milliseconds: 200));
    await click(find.byKey(const Key('nav-mias')));
    await until(() => find.text('No hay publicaciones en este estado').evaluate().isNotEmpty, 'B no hereda publicaciones A');
    expect(await api.listarMisPublicaciones(), isEmpty);
    expect(find.text(editedTitle), findsNothing);
    expect(find.text('Editar'), findsNothing);
    await screenshot('mias-B-vacias');
    checks.add('Mis publicaciones B aisladas de A y reporte real');
    await logout();

    await enterAccount('Moderador de prueba', emailC, passwordC, register: true);
    expect(session.usuario!.esAdmin, isTrue, reason: 'Cuenta controlada habilitada por su ID en este entorno de pruebas');
    await click(find.byKey(const Key('cuenta')));
    await until(() => find.text('Revisar reportes').evaluate().isNotEmpty, 'Capacidad de moderación real');
    await click(find.text('Revisar reportes'));
    await until(() => find.text(editedTitle).evaluate().isNotEmpty, 'Reporte pendiente con título actual');
    await screenshot('moderacion-pendiente');
    await click(find.text('Ocultar publicación'));
    await fill('resolucion-nota', 'Ocultada como parte de la verificación funcional del MVP.');
    await click(find.text('Confirmar decisión'));
    await until(() => find.text('No hay reportes pendientes.').evaluate().isNotEmpty, 'Reporte resuelto');
    expect((await http.get(Uri.parse('$defaultApiBaseUrl/catalogo/$id'))).statusCode, 404);
    checks.add('Moderación oculta publicación y resuelve reporte con nota');
    await screenshot('moderacion-resuelta');
    await tester.pageBack();
    await tester.pump(const Duration(milliseconds: 200));
    await click(find.byKey(const Key('logout')));
    await until(() => !session.authenticated && find.byKey(const Key('cuenta')).evaluate().isNotEmpty, 'Logout moderador');

    await enterAccount('Estudiante A', emailA, passwordA);
    await click(find.byKey(const Key('nav-mias')));
    await until(() => find.text(editedTitle).evaluate().isNotEmpty, 'A conserva gestión de publicación oculta');
    expect(find.text('Oculta del catálogo'), findsOneWidget);
    expect((await ownPublication())['visible'], false);
    await screenshot('mias-A-oculta');
    await click(find.text('Eliminar'));
    await click(find.widgetWithText(FilledButton, 'Eliminar'));
    await until(() => find.text('No hay publicaciones en este estado').evaluate().isNotEmpty, 'A elimina su publicación');
    expect(await api.listarMisPublicaciones(), isEmpty);
    expect((await http.get(Uri.parse('$defaultApiBaseUrl/catalogo/$id'))).statusCode, 404);
    for (final image in remainingImages) {
      expect((await http.get(Uri.parse('$defaultApiBaseUrl${image['imagen_url']}'))).statusCode, 404);
    }
    await logout();
    checks.add('Eliminación por A con retiro de todas las imágenes y logout revocado');
    binding.reportData ??= <String, dynamic>{};
    binding.reportData!['checks'] = checks;
    binding.reportData!['platform'] = platform;
    if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
      await until(
        () => binding.debugOutstandingSemanticsHandles == initialSemanticsHandles,
        'UiAutomation libera la semántica nativa antes de cerrar el flujo',
      );
      binding.reportData!['semantics_handles_restored'] = true;
    }
    } catch (_) {
      FocusManager.instance.primaryFocus?.unfocus();
      await tester.pump(const Duration(milliseconds: 350));
      if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android && !surfaceConverted) {
        await binding.convertFlutterSurfaceToImage();
        surfaceConverted = true;
        await tester.pump();
      }
      await binding.takeScreenshot('$platform-fallo');
      rethrow;
    } finally {
      api.dispose();
    }
  });
}
