import 'dart:async';

import 'package:flutter/foundation.dart';

import '../catalogo/publicacion_catalogo.dart';
import '../shared/api_error.dart';
import '../usuarios/session_controller.dart';
import 'favoritos_api.dart';

/// Caché privada de la sesión actual; MySQL sigue siendo la fuente de verdad.
class FavoritosController extends ChangeNotifier {
  FavoritosController({SessionController? session, FavoritosApi? api})
      : _session = session ?? SessionController.instance,
        _api = api ?? FavoritosApi(session: session) {
    _session.addListener(_sessionChanged);
    _sessionChanged();
  }

  static final instance = FavoritosController();
  final SessionController _session;
  final FavoritosApi _api;
  final Map<int, PublicacionCatalogo> _items = {};
  final Set<int> _pending = {};
  String? _identity;
  int _epoch = 0;
  int _version = 0;
  bool _disposed = false;
  Future<void>? _refreshing;
  bool loading = false;
  bool loaded = false;
  String? error;

  List<PublicacionCatalogo> get items => List.unmodifiable(_items.values);
  bool contiene(int id) => _items.containsKey(id);
  bool pendiente(int id) => _pending.contains(id);

  void _sessionChanged() {
    final identity = _session.authenticated
        ? _session.authorizedHeaders['Authorization'] : null;
    if (identity == _identity) return;
    _identity = identity;
    _epoch++;
    _version++;
    _items.clear();
    _pending.clear();
    loading = false;
    _refreshing = null;
    loaded = false;
    error = null;
    notifyListeners();
    if (identity != null) unawaited(Future.microtask(refresh));
  }

  Future<void> ensureLoaded() async {
    if (!loaded) await refresh();
  }

  Future<void> refresh() {
    if (_refreshing != null) return _refreshing!;
    final future = _load();
    _refreshing = future;
    future.whenComplete(() { if (identical(_refreshing, future)) _refreshing = null; });
    return future;
  }

  Future<void> _load() async {
    if (_disposed || !_session.authenticated || loading || _pending.isNotEmpty) return;
    final epoch = _epoch;
    final version = _version;
    loading = true;
    error = null;
    notifyListeners();
    try {
      final values = await _api.listar();
      if (_disposed || epoch != _epoch || version != _version) return;
      _items..clear()..addEntries(values.map((p) => MapEntry(p.id, p)));
      loaded = true;
    } catch (e) {
      if (!_disposed && epoch == _epoch && version == _version) {
        error = readableError(e);
      }
    } finally {
      if (!_disposed && epoch == _epoch) {
        loading = false;
        notifyListeners();
      }
    }
  }

  Future<void> toggle(PublicacionCatalogo publicacion) async {
    if (!_session.authenticated || pendiente(publicacion.id)) return;
    final epoch = _epoch;
    // No decidir PUT/DELETE a partir de una carga todavía desconocida.
    await ensureLoaded();
    if (_disposed || epoch != _epoch || !_session.authenticated || pendiente(publicacion.id)) return;
    if (!loaded) throw const ApiException('No se pudieron consultar tus favoritos. Reintenta.');
    final active = contiene(publicacion.id);
    _pending.add(publicacion.id);
    _version++;
    notifyListeners();
    try {
      if (active) {
        await _api.quitar(publicacion.id);
      } else {
        await _api.guardar(publicacion.id);
      }
      if (_disposed || epoch != _epoch) return;
      if (active) {
        _items.remove(publicacion.id);
      } else {
        _items[publicacion.id] = publicacion;
      }
    } finally {
      if (!_disposed && epoch == _epoch) {
        _pending.remove(publicacion.id);
        _version++;
        notifyListeners();
      }
    }
  }

  @override
  void dispose() {
    _disposed = true;
    _session.removeListener(_sessionChanged);
    _api.dispose();
    super.dispose();
  }
}
