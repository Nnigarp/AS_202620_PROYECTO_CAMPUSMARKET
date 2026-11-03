import 'dart:convert';

import 'package:http/http.dart' as http;

import '../catalogo/publicacion_catalogo.dart';
import '../shared/api_configuration.dart';
import '../shared/api_error.dart';
import '../usuarios/session_controller.dart';

class FavoritosApi {
  FavoritosApi({http.Client? client, SessionController? session, String? baseUrl})
      : _client = client ?? http.Client(),
        _session = session ?? SessionController.instance,
        _baseUrl = baseUrl ?? defaultApiBaseUrl;

  final http.Client _client;
  final SessionController _session;
  final String _baseUrl;

  Future<http.Response> _request(String method, String path) async {
    final headers = _session.authorizedHeaders;
    final request = http.Request(method, Uri.parse('$_baseUrl$path'))
      ..headers.addAll(headers);
    final response = await _client.send(request).then(http.Response.fromStream)
        .timeout(const Duration(seconds: 20));
    if (response.statusCode == 401) {
      _session.invalidateIfMatches(headers['Authorization']);
    }
    if (response.statusCode != (method == 'GET' ? 200 : 204)) {
      throw ApiException(responseMessage(response), statusCode: response.statusCode);
    }
    return response;
  }

  Future<List<PublicacionCatalogo>> listar() async {
    final response = await _request('GET', '/favoritos');
    return (jsonDecode(response.body) as List<dynamic>)
        .map((item) => PublicacionCatalogo.fromJson(
              item as Map<String, dynamic>, baseUrl: _baseUrl,
            )).toList();
  }

  Future<void> guardar(int id) async { await _request('PUT', '/favoritos/$id'); }
  Future<void> quitar(int id) async { await _request('DELETE', '/favoritos/$id'); }
  void dispose() => _client.close();
}
