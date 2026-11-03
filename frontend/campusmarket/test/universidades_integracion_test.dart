import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:campusmarket/usuarios/session_controller.dart';
import 'package:campusmarket/usuarios/universidades_api.dart';
import 'package:campusmarket/catalogo/publicacion_catalogo.dart';
import 'package:campusmarket/catalogo/widgets/catalogo_card.dart';
import 'package:flutter/material.dart';

void main() {
  for (final width in [250.0, 285.0, 350.0, 500.0]) {
    testWidgets('Tarjeta muestra universidad declarada sin desbordar a ancho $width', (tester) async {
      final product = PublicacionCatalogo.fromJson({
        'id': 17, 'titulo': 'Libro de arquitectura para el próximo semestre',
        'descripcion': 'Material completo de ensayo para verificar la tarjeta de la comunidad.',
        'precio': 65000, 'modalidad': 'venta', 'estado': 'usado', 'imagenes': [],
        'universidad_id': 1,
        'universidad': {'id': 1, 'nombre': 'Universidad Tecnológica de Bolívar', 'sigla': 'UTB', 'ciudad': 'Cartagena'},
      }, baseUrl: 'http://localhost');
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: Center(child: SizedBox(
        width: width, height: width / 0.72,
        child: CatalogoCard(publicacion: product, onTap: () {}),
      )))));
      await tester.pumpAndSettle();
      expect(find.text('UTB'), findsOneWidget);
      expect(find.text('Venta'), findsOneWidget);
      expect(find.byTooltip('Universidad declarada al publicar: Universidad Tecnológica de Bolívar'), findsOneWidget);
      expect(tester.takeException(), isNull);
      await tester.pumpWidget(const SizedBox.shrink());
    });
  }

  test('Universidad decodifica el contrato público', () {
    final universidad = Universidad.fromJson({
      'id': 1,
      'nombre': 'Universidad Tecnológica de Bolívar',
      'sigla': 'UTB',
      'ciudad': 'Cartagena',
    });
    expect(universidad.id, 1);
    expect(universidad.sigla, 'UTB');
  });

  test('Publicación conserva universidad declarada y null heredado', () {
    final base = <String, dynamic>{
      'id': 3,
      'titulo': 'Libro',
      'descripcion': 'Prueba',
      'precio': 10,
      'modalidad': 'venta',
      'estado': 'usado',
      'imagenes': [],
    };
    final conUniversidad = PublicacionCatalogo.fromJson(
      {...base, 'universidad_id': 1},
      baseUrl: 'http://localhost:8001',
    );
    final heredada = PublicacionCatalogo.fromJson(
      base, baseUrl: 'http://localhost:8001',
    );
    expect(conUniversidad.universidadId, 1);
    expect(heredada.universidadId, isNull);
  });

  test('Registro envía universidad seleccionada sin exigir correo institucional', () async {
    Map<String, dynamic>? payload;
    final session = SessionController(
      baseUrl: 'http://localhost:8001',
      client: MockClient((request) async {
        expect(request.url.path, '/usuarios/registro');
        payload = jsonDecode(request.body) as Map<String, dynamic>;
        return http.Response('{}', 201);
      }),
    );
    addTearDown(session.dispose);

    await session.registrar(
      nombre: 'Prueba',
      correo: 'persona@gmail.com',
      password: 'una-frase-segura-de-prueba',
      universidadId: 1,
    );
    expect(payload?['universidad_id'], 1);
    expect(payload?['correo'], 'persona@gmail.com');
  });

  test('Catálogo presenta metadata declarada sin inferir universidad heredada', () {
    final base = <String, dynamic>{
      'id': 3, 'titulo': 'Libro', 'descripcion': 'Ensayo', 'precio': 10,
      'modalidad': 'venta', 'estado': 'usado', 'imagenes': [],
    };
    final publicada = PublicacionCatalogo.fromJson({...base, 'universidad_id': 1,
      'universidad': {'id': 1, 'nombre': 'Universidad Tecnológica de Bolívar', 'sigla': 'UTB', 'ciudad': 'Cartagena'},
    }, baseUrl: 'http://localhost');
    expect(publicada.universidadEtiqueta, 'UTB');
    expect(publicada.universidadDetalle, 'Universidad Tecnológica de Bolívar');
    final heredada = PublicacionCatalogo.fromJson(base, baseUrl: 'http://localhost');
    expect(heredada.universidad, isNull);
    expect(heredada.universidadEtiqueta, 'Universidad no declarada');
  });

  test('Perfil envía universidad actualizada y conserva sesión', () async {
    Map<String, dynamic>? patch;
    final session = SessionController(
      baseUrl: 'http://localhost:8001',
      client: MockClient((request) async {
        if (request.url.path == '/usuarios/login') {
          return http.Response(jsonEncode({
            'access_token': 'token-prueba',
            'token_type': 'bearer',
            'expira_en': DateTime.now().toUtc().add(const Duration(hours: 1)).toIso8601String(),
            'usuario': {'id': 7, 'nombre': 'Inicial', 'correo': 'persona@gmail.com', 'es_admin': false, 'universidad_id': null},
          }), 200);
        }
        expect(request.url.path, '/usuarios/me');
        patch = jsonDecode(request.body) as Map<String, dynamic>;
        expect(request.headers['Authorization'], 'Bearer token-prueba');
        return http.Response(jsonEncode({
          'id': 7, 'nombre': 'Actualizada', 'correo': 'persona@gmail.com',
          'es_admin': false, 'universidad_id': 2,
        }), 200);
      }),
    );
    addTearDown(session.dispose);

    await session.login(correo: 'persona@gmail.com', password: 'una-frase-segura-de-prueba');
    await session.editarPerfil('Actualizada', universidadId: 2);
    expect(patch?['universidad_id'], 2);
    expect(session.usuario?.universidadId, 2);
    expect(session.authenticated, isTrue);
  });
}
