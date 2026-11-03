import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import '../shared/api_configuration.dart';
import '../shared/api_error.dart';

class Usuario {
  const Usuario({
    required this.id,
    required this.nombre,
    required this.correo,
    required this.esAdmin,
    this.universidadId,
  });
  final int id;
  final String nombre;
  final String correo;
  final bool esAdmin;
  final int? universidadId;

  factory Usuario.fromJson(Map<String, dynamic> json) => Usuario(
    id: json['id'] as int,
    nombre: json['nombre'] as String,
    correo: json['correo'] as String,
    esAdmin: json['es_admin'] as bool,
    universidadId: json['universidad_id'] as int?,
  );
}

class SessionController extends ChangeNotifier {
  SessionController({http.Client? client, String? baseUrl})
    : _client = client ?? http.Client(),
      baseUrl = baseUrl ?? defaultApiBaseUrl;

  static final instance = SessionController();
  final http.Client _client;
  final String baseUrl;
  String? _token;
  Usuario? _usuario;
  DateTime? _expiresAt;
  Timer? _expiryTimer;

  Usuario? get usuario => _usuario;
  bool get authenticated => _token != null && _usuario != null &&
      _expiresAt != null && _expiresAt!.isAfter(DateTime.now().toUtc());

  Map<String, String> get authorizedHeaders {
    if (!authenticated) {
      throw const ApiException('Inicia sesión para continuar.', statusCode: 401);
    }
    return {'Authorization': 'Bearer $_token', 'Content-Type': 'application/json'};
  }

  void invalidateIfMatches(String? authorization) {
    if (authorization == 'Bearer $_token') _clear();
  }

  Future<void> registrar({
    required String nombre,
    required String correo,
    required String password,
    int? universidadId,
  }) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/usuarios/registro'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'nombre': nombre, 'correo': correo, 'password': password, if (universidadId != null) 'universidad_id': universidadId}),
    ).timeout(const Duration(seconds: 20));
    _check(response, 201);
  }

  Future<void> login({required String correo, required String password}) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/usuarios/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'correo': correo, 'password': password}),
    ).timeout(const Duration(seconds: 20));
    _check(response, 200);
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    _expiryTimer?.cancel();
    _token = data['access_token'] as String;
    _usuario = Usuario.fromJson(data['usuario'] as Map<String, dynamic>);
    _expiresAt = DateTime.parse(data['expira_en'] as String).toUtc();
    final remaining = _expiresAt!.difference(DateTime.now().toUtc());
    if (remaining.isNegative) {
      _clear();
      throw const ApiException('La sesión recibida ya expiró. Intenta nuevamente.');
    }
    _expiryTimer = Timer(remaining, _clear);
    notifyListeners();
  }

  Future<void> consultarActual() async {
    final headers = authorizedHeaders;
    final response = await _client.get(
      Uri.parse('$baseUrl/usuarios/me'), headers: headers,
    ).timeout(const Duration(seconds: 20));
    _check(response, 200, authorization: headers['Authorization']);
    if (headers['Authorization'] != 'Bearer $_token') return;
    _usuario = Usuario.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
    notifyListeners();
  }

  Future<void> editarPerfil(String nombre, {int? universidadId}) async {
    final headers = authorizedHeaders;
    final response = await _client.patch(
      Uri.parse('$baseUrl/usuarios/me'),
      headers: headers,
      body: jsonEncode({'nombre': nombre, if (universidadId != null) 'universidad_id': universidadId}),
    ).timeout(const Duration(seconds: 20));
    _check(response, 200, authorization: headers['Authorization']);
    if (headers['Authorization'] != 'Bearer $_token') return;
    _usuario = Usuario.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
    notifyListeners();
  }

  Future<void> logout() async {
    final headers = authorizedHeaders;
    final response = await _client.post(
      Uri.parse('$baseUrl/usuarios/logout'), headers: headers,
    ).timeout(const Duration(seconds: 20));
    if (response.statusCode != 204 && response.statusCode != 401) {
      _check(response, 204);
    }
    invalidateIfMatches(headers['Authorization']);
  }

  void _check(http.Response response, int expected, {String? authorization}) {
    if (response.statusCode == expected) return;
    if (response.statusCode == 401 && authorization != null) {
      invalidateIfMatches(authorization);
    }
    throw ApiException(responseMessage(response), statusCode: response.statusCode);
  }

  void _clear() {
    _expiryTimer?.cancel();
    _expiryTimer = null;
    _token = null;
    _usuario = null;
    _expiresAt = null;
    notifyListeners();
  }

  @override
  void dispose() {
    _expiryTimer?.cancel();
    _client.close();
    super.dispose();
  }
}
