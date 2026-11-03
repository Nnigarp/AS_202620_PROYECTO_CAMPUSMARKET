import 'dart:async';
import 'dart:convert';

import 'package:campusmarket/mensajeria/bandeja_page.dart';
import 'package:campusmarket/mensajeria/chat_controller.dart';
import 'package:campusmarket/mensajeria/chat_page.dart';
import 'package:campusmarket/mensajeria/mensajeria_api.dart';
import 'package:campusmarket/usuarios/session_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

final _conversation = <String, dynamic>{
  'id': 9, 'publicacion_id': 17, 'comprador_id': 1, 'vendedor_id': 2,
  'publicacion': {'id': 17, 'propietario_id': 2, 'titulo': 'Libro sintético',
    'descripcion': 'Libro de prueba', 'precio': 20, 'modalidad': 'venta', 'estado': 'usado', 'imagenes': []},
};
Map<String, dynamic> _message(int id, String text, {int sender = 1}) => {
  'id': id, 'conversacion_id': 9, 'remitente_id': sender, 'texto': text, 'creado_en': '2026-11-03T12:00:00Z',
};
http.Response _json(Object data, [int status = 200]) => http.Response(jsonEncode(data), status);
SessionController _session() => SessionController(client: MockClient((request) async {
  if (request.url.path.endsWith('/logout')) return http.Response('', 204);
  final email = (jsonDecode(request.body) as Map)['correo'];
  return _json({
    'access_token': 'sesion-$email',
    'expira_en': DateTime.now().toUtc().add(const Duration(hours: 1)).toIso8601String(),
    'usuario': {'id': email == 'b@campus.test' ? 2 : 1, 'nombre': 'Ensayo', 'correo': email, 'es_admin': false},
  });
}));
Future<void> _login(SessionController session, [String email = 'a@campus.test']) =>
  session.login(correo: email, password: 'frase-sintetica-de-prueba');

void main() {
  test('API envía solo contexto/texto/clave e identidad Bearer', () async {
    final session = _session();
    await _login(session);
    final api = MensajeriaApi(session: session, client: MockClient((request) async {
      expect(request.headers['Authorization'], session.authorizedHeaders['Authorization']);
      if (request.url.path == '/conversaciones') {
        expect(jsonDecode(request.body), {'publicacion_id': 17});
        return _json(_conversation);
      }
      expect(jsonDecode(request.body), {'texto': 'Hola', 'clave': ''.padLeft(32, 'a')});
      return _json(_message(1, 'Hola'), 201);
    }));
    addTearDown(() { api.dispose(); session.dispose(); });
    expect((await api.iniciar(17)).vendedorId, 2);
    expect((await api.enviar(9, 'Hola', ''.padLeft(32, 'a'))).remitenteId, 1);
  });

  test('Cursor no salta mensajes intermedios al enviar y páginas no duplican', () async {
    final session = _session();
    await _login(session);
    final cursors = <int>[];
    final controller = ChatController(conversacionId: 9, api: MensajeriaApi(session: session,
      client: MockClient((request) async {
        if (!request.url.path.endsWith('/mensajes')) return _json(_conversation);
        if (request.method == 'POST') return _json(_message(4, 'Mi respuesta'), 201);
        final cursor = int.parse(request.url.queryParameters['despues_de']!);
        cursors.add(cursor);
        final messages = cursor == 0 ? [_message(1, 'Uno')]
          : cursor == 1 ? [_message(2, 'Dos', sender: 2)]
          : [_message(3, 'Tres', sender: 2), _message(4, 'Mi respuesta')];
        return _json({'mensajes': messages, 'hay_mas': cursor == 0});
      }),
    ));
    addTearDown(() { controller.dispose(); session.dispose(); });
    await controller.load();
    expect(controller.hayMas, isTrue);
    await controller.load();
    expect(await controller.enviar('Mi respuesta'), isTrue);
    expect(cursors, [0, 1, 2]);
    expect(controller.mensajes.map((m) => m.id), [1, 2, 3, 4]);
  });

  test('Fallo incierto conserva clave de reintento y no envía como otra persona', () async {
    final session = _session();
    await _login(session);
    final bodies = <Map<String, dynamic>>[];
    final controller = ChatController(conversacionId: 9, api: MensajeriaApi(session: session,
      client: MockClient((request) async {
        if (!request.url.path.endsWith('/mensajes')) return _json(_conversation);
        if (request.method == 'GET') return _json({'mensajes': [], 'hay_mas': false});
        bodies.add(jsonDecode(request.body) as Map<String, dynamic>);
        return bodies.length == 1 ? _json({'detail': 'No disponible'}, 503) : _json(_message(1, 'Hola'), 201);
      }),
    ));
    addTearDown(() { controller.dispose(); session.dispose(); });
    await controller.load();
    expect(await controller.enviar('Hola'), isFalse);
    expect(await controller.enviar('Hola'), isTrue);
    expect(bodies[0], bodies[1]);
    expect(bodies.first.keys, containsAll(['texto', 'clave']));
    expect(bodies.first.containsKey('remitente_id'), isFalse);
  });

  test('Respuesta de conversación atrasada se descarta al cambiar sesión', () async {
    final session = _session();
    await _login(session);
    final delayed = Completer<http.Response>();
    final controller = ChatController(conversacionId: 9, api: MensajeriaApi(session: session,
      client: MockClient((request) async => request.url.path.endsWith('/mensajes')
        ? delayed.future : _json(_conversation)),
    ));
    addTearDown(() { controller.dispose(); session.dispose(); });
    final loading = controller.load();
    await session.logout();
    await _login(session, 'b@campus.test');
    delayed.complete(_json({'mensajes': [_message(1, 'Privado A')], 'hay_mas': false}));
    await loading;
    expect(controller.active, isFalse);
    expect(controller.mensajes, isEmpty);
    expect(controller.conversacion, isNull);
  });

  for (final width in [320.0, 390.0, 1440.0]) {
    testWidgets('Chat adapta texto/envío/actualización a ancho $width', (tester) async {
      tester.view.physicalSize = Size(width, 844);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      final session = _session();
      await _login(session);
      final controller = ChatController(conversacionId: 9, api: MensajeriaApi(session: session,
        client: MockClient((request) async {
          if (!request.url.path.endsWith('/mensajes')) return _json(_conversation);
          return request.method == 'POST' ? _json(_message(2, 'Respuesta de prueba'), 201)
            : _json({'mensajes': [_message(1, 'Consulta del comprador', sender: 2)], 'hay_mas': false});
        }),
      ));
      try {
        await tester.pumpWidget(MaterialApp(home: ChatPage(conversacionId: 9, controller: controller)));
        await tester.pumpAndSettle();
        expect(find.text('Consulta del comprador'), findsOneWidget);
        await tester.enterText(find.byKey(const Key('chat-texto')), 'Respuesta de prueba');
        await tester.tap(find.byKey(const Key('chat-enviar')));
        await tester.pumpAndSettle();
        expect(find.text('Respuesta de prueba'), findsOneWidget);
        expect(tester.widget<TextField>(find.byKey(const Key('chat-texto'))).controller!.text, isEmpty);
        await session.logout();
        await tester.pumpAndSettle();
        expect(find.text('Consulta del comprador'), findsNothing);
        expect(tester.takeException(), isNull);
      } finally {
        await tester.pumpWidget(const SizedBox.shrink());
        controller.dispose();
        session.dispose();
      }
    });
  }

  testWidgets('Bandeja borra conversaciones al cerrar sesión', (tester) async {
    final session = _session();
    await _login(session);
    final api = MensajeriaApi(session: session, client: MockClient((_) async => _json([_conversation])));
    try {
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: BandejaPage(api: api))));
      await tester.pumpAndSettle();
      expect(find.text('Libro sintético'), findsOneWidget);
      await session.logout();
      await tester.pumpAndSettle();
      expect(find.text('Libro sintético'), findsNothing);
      expect(tester.takeException(), isNull);
    } finally {
      await tester.pumpWidget(const SizedBox.shrink());
      api.dispose();
      session.dispose();
    }
  });
}
