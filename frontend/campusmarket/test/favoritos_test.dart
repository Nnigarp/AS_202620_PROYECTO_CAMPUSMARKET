import 'dart:async';
import 'dart:convert';

import 'package:campusmarket/catalogo/publicacion_catalogo.dart';
import 'package:campusmarket/favoritos/favorito_button.dart';
import 'package:campusmarket/favoritos/favoritos_api.dart';
import 'package:campusmarket/favoritos/favoritos_controller.dart';
import 'package:campusmarket/favoritos/favoritos_page.dart';
import 'package:campusmarket/usuarios/session_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

final publication = <String, dynamic>{
  'id': 17, 'titulo': 'Libro sintético', 'descripcion': 'Ensayo de favoritos',
  'precio': 20, 'modalidad': 'venta', 'estado': 'usado', 'imagenes': [],
};
PublicacionCatalogo get product => PublicacionCatalogo.fromJson(publication, baseUrl: 'http://local');

SessionController sessionFixture() {
  var token = 0;
  return SessionController(baseUrl: 'http://local', client: MockClient((request) async {
    if (request.url.path.endsWith('/logout')) return http.Response('', 204);
    final email = (jsonDecode(request.body) as Map)['correo'];
    return http.Response(jsonEncode({
      'access_token': 'sintetico-${++token}',
      'expira_en': DateTime.now().toUtc().add(const Duration(hours: 1)).toIso8601String(),
      'usuario': {'id': email == 'a@campus.test' ? 1 : 2, 'nombre': 'Ensayo', 'correo': email, 'es_admin': false},
    }), 200);
  }));
}
Future<void> login(SessionController session, [String email = 'a@campus.test']) =>
    session.login(correo: email, password: 'frase-sintetica-de-prueba');

void main() {
  test('Carga privada, PUT/DELETE y estado compartido sin duplicados', () async {
    final session = sessionFixture();
    await login(session);
    final methods = <String>[];
    final controller = FavoritosController(session: session, api: FavoritosApi(
      session: session, baseUrl: 'http://local', client: MockClient((request) async {
        expect(request.headers['Authorization'], session.authorizedHeaders['Authorization']);
        expect(request.url.path, startsWith('/favoritos'));
        methods.add(request.method);
        return http.Response(request.method == 'GET' ? '[]' : '', request.method == 'GET' ? 200 : 204);
      }),
    ));
    addTearDown(() { controller.dispose(); session.dispose(); });
    await controller.ensureLoaded();
    await controller.toggle(product);
    expect(controller.contiene(17), isTrue);
    expect(controller.items, hasLength(1));
    await controller.toggle(product);
    expect(controller.items, isEmpty);
    expect(methods.where((m) => m != 'GET'), ['PUT', 'DELETE']);
  });

  test('Logout limpia inmediatamente y una respuesta anterior no cruza cuentas', () async {
    final session = sessionFixture();
    await login(session);
    final delayed = Completer<http.Response>();
    final controller = FavoritosController(session: session, api: FavoritosApi(
      session: session, baseUrl: 'http://local', client: MockClient((request) async {
        if (request.headers['Authorization'] == 'Bearer sintetico-1') return delayed.future;
        return http.Response('[]', 200);
      }),
    ));
    addTearDown(() { controller.dispose(); session.dispose(); });
    final pending = controller.ensureLoaded();
    await session.logout();
    expect(controller.items, isEmpty);
    await login(session, 'b@campus.test');
    await controller.ensureLoaded();
    delayed.complete(http.Response(jsonEncode([publication]), 200));
    await pending;
    expect(session.usuario?.id, 2);
    expect(controller.items, isEmpty);
  });

  test('401 atrasado no revoca una sesión renovada', () async {
    final session = sessionFixture();
    await login(session);
    final delayed = Completer<http.Response>();
    final api = FavoritosApi(session: session, client: MockClient((_) => delayed.future));
    addTearDown(() { api.dispose(); session.dispose(); });
    final request = api.listar();
    final assertion = expectLater(request, throwsException);
    await login(session);
    delayed.complete(http.Response('{"detail":"Sesión anterior vencida"}', 401));
    await assertion;
    expect(session.authenticated, isTrue);
  });

  test('Error de escritura no activa el corazón ni duplica envíos pendientes', () async {
    final session = sessionFixture();
    await login(session);
    final delayed = Completer<http.Response>();
    var writes = 0;
    final controller = FavoritosController(session: session, api: FavoritosApi(
      session: session, client: MockClient((request) async {
        if (request.method == 'GET') return http.Response('[]', 200);
        writes++;
        return delayed.future;
      }),
    ));
    addTearDown(() { controller.dispose(); session.dispose(); });
    await controller.ensureLoaded();
    final writing = controller.toggle(product);
    final assertion = expectLater(writing, throwsException);
    await Future<void>.delayed(Duration.zero);
    await controller.toggle(product);
    expect(writes, 1);
    delayed.complete(http.Response('{"detail":"No disponible"}', 503));
    await assertion;
    expect(controller.contiene(17), isFalse);
    expect(controller.pendiente(17), isFalse);
  });

  for (final width in [320.0, 390.0, 800.0, 1440.0]) {
    testWidgets('Favoritos privados y corazón accesible a ancho $width', (tester) async {
      tester.view.physicalSize = Size(width, 900);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      final session = sessionFixture();
      await login(session);
      final controller = FavoritosController(session: session, api: FavoritosApi(
        session: session, client: MockClient((request) async => http.Response(
          request.method == 'GET' ? '[]' : '', request.method == 'GET' ? 200 : 204,
        )),
      ));
      try {
        await controller.ensureLoaded();
        await tester.pumpWidget(MaterialApp(home: Scaffold(body: Column(children: [
        FavoritoButton(publicacion: product, controller: controller),
        Expanded(child: FavoritosPage(controller: controller)),
      ]))));
      await tester.pumpAndSettle();
      expect(find.text('Mis favoritos'), findsOneWidget);
      await tester.tap(find.byTooltip('Agregar a favoritos'));
      await tester.pumpAndSettle();
      expect(controller.contiene(17), isTrue);
      expect(find.byIcon(Icons.favorite), findsWidgets);
        expect(tester.takeException(), isNull);
      } finally {
        await tester.pumpWidget(const SizedBox.shrink());
        controller.dispose();
        session.dispose();
      }
    });
  }

  testWidgets('Revalidar favoritos oculta resultados anteriores mientras comprueba disponibilidad', (tester) async {
    final session = sessionFixture();
    await login(session);
    Completer<http.Response>? delayed;
    final controller = FavoritosController(session: session, api: FavoritosApi(session: session,
      client: MockClient((_) async {
        final waiting = delayed;
        if (waiting != null) return waiting.future;
        return http.Response(jsonEncode([publication]), 200);
      }),
    ));
    try {
      await controller.ensureLoaded();
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: FavoritosPage(controller: controller))));
      await tester.pumpAndSettle();
      expect(find.text('Libro sintético'), findsOneWidget);
      delayed = Completer<http.Response>();
      await tester.tap(find.byTooltip('Actualizar favoritos'));
      await tester.pump();
      expect(find.text('Libro sintético'), findsNothing);
      delayed.complete(http.Response('[]', 200));
      await tester.pumpAndSettle();
      expect(controller.items, isEmpty);
      expect(find.text('Libro sintético'), findsNothing);
      expect(tester.takeException(), isNull);
    } finally {
      if (delayed != null && !delayed.isCompleted) delayed.complete(http.Response('[]', 200));
      await tester.pumpWidget(const SizedBox.shrink());
      controller.dispose();
      session.dispose();
    }
  });
}
