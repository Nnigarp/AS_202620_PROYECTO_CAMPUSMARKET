import 'dart:math';

import 'package:flutter/foundation.dart';

import '../shared/api_error.dart';
import 'mensajeria_api.dart';

class ChatController extends ChangeNotifier {
  ChatController({required this.conversacionId, MensajeriaApi? api}) : api = api ?? MensajeriaApi() {
    _identity = this.api.identity;
    this.api.session.addListener(_sessionChanged);
  }
  final int conversacionId;
  final MensajeriaApi api;
  final Map<int, Mensaje> _messages = {};
  String? _identity;
  String? _pendingText;
  String? _pendingKey;
  int _cursor = 0;
  int _epoch = 0;
  bool _disposed = false;
  Conversacion? conversacion;
  bool loading = false;
  bool sending = false;
  bool hayMas = false;
  String? error;
  bool get active => !_disposed && _identity != null && api.identity == _identity;
  List<Mensaje> get mensajes => List.unmodifiable(_messages.values.toList()..sort((a, b) => a.id.compareTo(b.id)));

  void _sessionChanged() {
    if (api.identity == _identity) return;
    _epoch++;
    // Una vista de conversación nunca se reutiliza con otra sesión/cuenta.
    _identity = null;
    _messages.clear();
    conversacion = null;
    _pendingText = _pendingKey = null;
    error = null;
    loading = sending = false;
    notifyListeners();
  }

  Future<void> load() async {
    if (!active || loading) return;
    final epoch = _epoch;
    loading = true;
    error = null;
    notifyListeners();
    try {
      final results = await Future.wait<dynamic>([
        api.detalle(conversacionId), api.mensajes(conversacionId, despuesDe: _cursor),
      ]);
      if (!active || epoch != _epoch) return;
      conversacion = results[0] as Conversacion;
      final page = results[1] as PaginaMensajes;
      for (final message in page.mensajes) { _messages[message.id] = message; }
      if (page.mensajes.isNotEmpty) _cursor = page.mensajes.last.id;
      hayMas = page.hayMas;
    } catch (e) {
      if (active && epoch == _epoch) error = readableError(e);
    } finally {
      if (!_disposed && epoch == _epoch) { loading = false; notifyListeners(); }
    }
  }

  Future<bool> enviar(String value) async {
    final texto = value.trim();
    if (!active || sending || conversacion?.publicacion == null || texto.isEmpty) return false;
    if (texto.length > 2000) { error = 'El mensaje admite hasta 2000 caracteres.'; notifyListeners(); return false; }
    final epoch = _epoch;
    if (texto != _pendingText || _pendingKey == null) {
      final random = Random.secure();
      _pendingKey = List.generate(16, (_) => random.nextInt(256).toRadixString(16).padLeft(2, '0')).join();
      _pendingText = texto;
    }
    sending = true;
    error = null;
    notifyListeners();
    try {
      final message = await api.enviar(conversacionId, texto, _pendingKey!);
      if (!active || epoch != _epoch) return false;
      _messages[message.id] = message;
      // El cursor solo avanza al leer la página; no salta mensajes intermedios
      // de otro participante al recibir un ID nuevo de mi propio envío.
      _pendingKey = _pendingText = null;
      await load();
      return active && epoch == _epoch;
    } catch (e) {
      if (active && epoch == _epoch) error = readableError(e);
      return false;
    } finally {
      if (!_disposed && epoch == _epoch) { sending = false; notifyListeners(); }
    }
  }

  @override
  void dispose() {
    _disposed = true;
    api.session.removeListener(_sessionChanged);
    api.dispose();
    super.dispose();
  }
}
