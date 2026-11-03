import 'dart:convert';

import 'package:http/http.dart' as http;

import '../shared/api_configuration.dart';
import '../shared/api_error.dart';

class Universidad {
  const Universidad({required this.id, required this.nombre, required this.sigla});

  final int id;
  final String nombre;
  final String sigla;

  factory Universidad.fromJson(Map<String, dynamic> json) => Universidad(
    id: json['id'] as int,
    nombre: json['nombre'] as String,
    sigla: json['sigla'] as String,
  );
}

class UniversidadesApi {
  const UniversidadesApi();

  Future<List<Universidad>> listar() async {
    final response = await http.get(
      Uri.parse('$defaultApiBaseUrl/universidades'),
    ).timeout(const Duration(seconds: 20));
    if (response.statusCode != 200) {
      throw ApiException(responseMessage(response), statusCode: response.statusCode);
    }
    return (jsonDecode(response.body) as List<dynamic>)
      .map((item) => Universidad.fromJson(item as Map<String, dynamic>))
      .toList();
  }
}
