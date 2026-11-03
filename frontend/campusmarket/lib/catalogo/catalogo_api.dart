import 'dart:convert';

import 'package:http/http.dart' as http;

import '../shared/api_configuration.dart';
import '../shared/api_error.dart';
import 'publicacion_catalogo.dart';

class CatalogoApi {
  const CatalogoApi({String? baseUrl}) : _baseUrl = baseUrl;

  final String? _baseUrl;
  String get baseUrl => _baseUrl ?? defaultApiBaseUrl;

  Future<List<PublicacionCatalogo>> buscar({
    String? texto,
    String? modalidad,
    String? estado,
    double? precioMin,
    double? precioMax,
    int? universidadId,
  }) async {
    final query = <String, String>{};

    if (texto != null && texto.trim().isNotEmpty) {
      query['q'] = texto.trim();
    }

    if (modalidad != null && modalidad.isNotEmpty) {
      query['modalidad'] = modalidad;
    }

    if (estado != null && estado.isNotEmpty) {
      query['estado'] = estado;
    }

    if (precioMin != null) {
      query['precio_min'] = precioMin.toString();
    }

    if (precioMax != null) {
      query['precio_max'] = precioMax.toString();
    }

    if (universidadId != null) query['universidad_id'] = universidadId.toString();

    final uri = Uri.parse(
      '$baseUrl/catalogo',
    ).replace(queryParameters: query.isEmpty ? null : query);

    final response = await http.get(uri).timeout(const Duration(seconds: 20));

    if (response.statusCode != 200) {
      throw ApiException(responseMessage(response), statusCode: response.statusCode);
    }

    final data = jsonDecode(response.body) as List<dynamic>;

    return data
        .map(
          (item) => PublicacionCatalogo.fromJson(
            item as Map<String, dynamic>,
            baseUrl: baseUrl,
          ),
        )
        .toList();
  }

  Future<PublicacionCatalogo> obtenerDetalle(int id) async {
    final response = await http.get(Uri.parse('$baseUrl/catalogo/$id')).timeout(const Duration(seconds: 20));

    if (response.statusCode == 404) {
      throw const ApiException('Esta publicación ya no está disponible.', statusCode: 404);
    }

    if (response.statusCode != 200) {
      throw ApiException(responseMessage(response), statusCode: response.statusCode);
    }

    return PublicacionCatalogo.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
      baseUrl: baseUrl,
    );
  }
}
