import 'package:flutter/material.dart';

import '../shared/api_error.dart';
import 'chat_page.dart';
import 'mensajeria_api.dart';

class BandejaPage extends StatefulWidget {
  const BandejaPage({super.key, this.api});
  final MensajeriaApi? api;
  @override
  State<BandejaPage> createState() => _BandejaPageState();
}

class _BandejaPageState extends State<BandejaPage> {
  late final MensajeriaApi _api;
  final Map<int, Conversacion> _items = {};
  String? _identity;
  String? _error;
  int _epoch = 0;
  int _offset = 0;
  bool _loading = false;
  bool _more = false;
  @override
  void initState() {
    super.initState();
    _api = widget.api ?? MensajeriaApi();
    _identity = _api.identity;
    _api.session.addListener(_sessionChanged);
    Future.microtask(_refresh);
  }
  void _sessionChanged() {
    if (!mounted || _api.identity == _identity) return;
    setState(() {
      _identity = _api.identity;
      _epoch++;
      _items.clear();
      _offset = 0;
      _loading = _more = false;
      _error = null;
    });
    if (_identity != null) Future.microtask(_refresh);
  }
  Future<void> _refresh({bool append = false}) async {
    if (!mounted || _identity == null || _loading) return;
    final epoch = _epoch;
    setState(() { _loading = true; _error = null; });
    try {
      final data = await _api.bandeja(desplazamiento: append ? _offset : 0);
      if (!mounted || epoch != _epoch) return;
      setState(() {
        if (!append) { _items.clear(); _offset = 0; }
        _items.addEntries(data.map((item) => MapEntry(item.id, item)));
        _offset += data.length;
        _more = data.length == 30;
      });
    } catch (e) {
      if (mounted && epoch == _epoch) setState(() => _error = readableError(e));
    } finally {
      if (mounted && epoch == _epoch) setState(() => _loading = false);
    }
  }
  Future<void> _open(Conversacion item) async {
    final epoch = _epoch;
    await Navigator.of(context).push(MaterialPageRoute(builder: (_) => ChatPage(conversacionId: item.id)));
    if (mounted && epoch == _epoch) await _refresh();
  }
  @override
  void dispose() {
    _api.session.removeListener(_sessionChanged);
    if (widget.api == null) _api.dispose();
    super.dispose();
  }
  @override
  Widget build(BuildContext context) => Column(children: [
    Padding(padding: const EdgeInsets.all(20), child: Row(children: [
      Expanded(child: Text('Mis mensajes', style: Theme.of(context).textTheme.headlineSmall)),
      IconButton(tooltip: 'Actualizar bandeja', onPressed: _loading ? null : _refresh, icon: const Icon(Icons.refresh)),
    ])),
    if (_loading) const LinearProgressIndicator(),
    if (_error != null) Padding(padding: const EdgeInsets.all(16), child: Semantics(liveRegion: true, child: Text(_error!))),
    Expanded(child: _items.isEmpty
      ? const Center(child: Padding(padding: EdgeInsets.all(24), child: Text(
          'Aún no tienes conversaciones. Contacta al vendedor desde una publicación.', textAlign: TextAlign.center,
        )))
      : ListView.separated(padding: const EdgeInsets.symmetric(horizontal: 16), itemCount: _items.length,
          separatorBuilder: (_, _) => const Divider(), itemBuilder: (context, index) {
            final item = _items.values.elementAt(index);
            final buyer = item.compradorId == _api.session.usuario?.id;
            return ListTile(
              key: ValueKey('conversacion-${item.id}'),
              leading: const Icon(Icons.chat_bubble_outline),
              title: Text(item.publicacion?.titulo ?? 'Publicación no disponible', maxLines: 2, overflow: TextOverflow.ellipsis),
              subtitle: Text('${buyer ? 'Vendedor' : 'Comprador'} · ${item.ultimoMensaje?.texto ?? 'Sin mensajes todavía'}',
                maxLines: 2, overflow: TextOverflow.ellipsis),
              trailing: const Icon(Icons.chevron_right), onTap: () => _open(item),
            );
          })),
    if (_more) TextButton(onPressed: _loading ? null : () => _refresh(append: true), child: const Text('Cargar más conversaciones')),
  ]);
}
