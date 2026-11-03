import 'dart:convert';

import 'package:http/http.dart' as http;

import '../catalogo/publicacion_catalogo.dart';
import '../shared/api_configuration.dart';
import '../shared/api_error.dart';
import '../usuarios/session_controller.dart';

class Mensaje {
  const Mensaje({required this.id, required this.remitenteId, required this.texto, required this.creadoEn});
  final int id;
  final int remitenteId;
  final String texto;
  final DateTime creadoEn;
  factory Mensaje.fromJson(Map<String, dynamic> json) => Mensaje(
    id: json['id'] as int, remitenteId: json['remitente_id'] as int,
    texto: json['texto'] as String, creadoEn: DateTime.parse(json['creado_en'] as String),
  );
}

class Conversacion {
  const Conversacion({required this.id, required this.compradorId, required this.vendedorId,
    required this.publicacionId, this.publicacion, this.ultimoMensaje});
  final int id;
  final int compradorId;
  final int vendedorId;
  final int publicacionId;
  final PublicacionCatalogo? publicacion;
  final Mensaje? ultimoMensaje;
  factory Conversacion.fromJson(Map<String, dynamic> json, String baseUrl) => Conversacion(
    id: json['id'] as int, compradorId: json['comprador_id'] as int,
    vendedorId: json['vendedor_id'] as int, publicacionId: json['publicacion_id'] as int,
    publicacion: json['publicacion'] == null ? null : PublicacionCatalogo.fromJson(
      json['publicacion'] as Map<String, dynamic>, baseUrl: baseUrl,
    ),
    ultimoMensaje: json['ultimo_mensaje'] == null ? null : Mensaje.fromJson(json['ultimo_mensaje'] as Map<String, dynamic>),
  );
}

class PaginaMensajes {
  const PaginaMensajes(this.mensajes, this.hayMas);
  final List<Mensaje> mensajes;
  final bool hayMas;
}

class MensajeriaApi {
  MensajeriaApi({http.Client? client, SessionController? session, String? baseUrl})
      : _client = client ?? http.Client(),
        session = session ?? SessionController.instance,
        _baseUrl = baseUrl ?? defaultApiBaseUrl;
  final http.Client _client;
  final SessionController session;
  final String _baseUrl;
  String? get identity => session.authenticated ? session.authorizedHeaders['Authorization'] : null;

  Future<dynamic> _request(String method, String path, {Map<String, dynamic>? body}) async {
    final headers = session.authorizedHeaders;
    final request = http.Request(method, Uri.parse('$_baseUrl$path'))..headers.addAll(headers);
    if (body != null) request.body = jsonEncode(body);
    final response = await _client.send(request).then(http.Response.fromStream).timeout(const Duration(seconds: 20));
    if (response.statusCode == 401) session.invalidateIfMatches(headers['Authorization']);
    if (response.statusCode != 200 && response.statusCode != 201) {
      throw ApiException(responseMessage(response), statusCode: response.statusCode);
    }
    if (identity != headers['Authorization']) {
      throw const ApiException('La sesión cambió. Vuelve a abrir Mensajes.', statusCode: 401);
    }
    return jsonDecode(response.body);
  }

  Future<Conversacion> iniciar(int publicacionId) async => Conversacion.fromJson(
    await _request('POST', '/conversaciones', body: {'publicacion_id': publicacionId}) as Map<String, dynamic>, _baseUrl,
  );
  Future<Conversacion> detalle(int id) async => Conversacion.fromJson(
    await _request('GET', '/conversaciones/$id') as Map<String, dynamic>, _baseUrl,
  );
  Future<List<Conversacion>> bandeja({int desplazamiento = 0}) async =>
    (await _request('GET', '/conversaciones?limite=30&desplazamiento=$desplazamiento') as List<dynamic>)
      .map((item) => Conversacion.fromJson(item as Map<String, dynamic>, _baseUrl)).toList();
  Future<PaginaMensajes> mensajes(int id, {int despuesDe = 0}) async {
    final data = await _request('GET', '/conversaciones/$id/mensajes?despues_de=$despuesDe&limite=50') as Map<String, dynamic>;
    return PaginaMensajes((data['mensajes'] as List<dynamic>)
      .map((item) => Mensaje.fromJson(item as Map<String, dynamic>)).toList(), data['hay_mas'] as bool);
  }
  Future<Mensaje> enviar(int id, String texto, String clave) async => Mensaje.fromJson(
    await _request('POST', '/conversaciones/$id/mensajes', body: {'texto': texto, 'clave': clave}) as Map<String, dynamic>,
  );
  void dispose() => _client.close();
}
