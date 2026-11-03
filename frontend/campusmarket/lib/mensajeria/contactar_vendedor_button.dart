import 'package:flutter/material.dart';

import '../catalogo/publicacion_catalogo.dart';
import '../shared/api_error.dart';
import '../usuarios/auth_page.dart';
import 'chat_page.dart';
import 'mensajeria_api.dart';

class ContactarVendedorButton extends StatefulWidget {
  const ContactarVendedorButton({super.key, required this.publicacion});
  final PublicacionCatalogo publicacion;
  @override
  State<ContactarVendedorButton> createState() => _ContactarVendedorButtonState();
}

class _ContactarVendedorButtonState extends State<ContactarVendedorButton> {
  final _api = MensajeriaApi();
  bool _busy = false;
  Future<void> _contactar() async {
    if (_busy) return;
    setState(() => _busy = true);
    try {
      if (!_api.session.authenticated) {
        final entered = await Navigator.of(context).push<bool>(MaterialPageRoute(builder: (_) => const AuthPage()));
        if (!mounted || entered != true || !_api.session.authenticated) return;
      }
      final identity = _api.identity;
      final result = await _api.iniciar(widget.publicacion.id);
      if (!mounted || identity != _api.identity) return;
      await Navigator.of(context).push(MaterialPageRoute(builder: (_) => ChatPage(conversacionId: result.id)));
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(readableError(e))));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }
  @override
  void dispose() { _api.dispose(); super.dispose(); }
  @override
  Widget build(BuildContext context) => ListenableBuilder(listenable: _api.session, builder: (context, _) {
    if (widget.publicacion.propietarioId == null || widget.publicacion.propietarioId == _api.session.usuario?.id) {
      return const SizedBox.shrink();
    }
    return FilledButton.icon(key: const Key('contactar-vendedor'), onPressed: _busy ? null : _contactar,
      icon: const Icon(Icons.chat_bubble_outline), label: Text(_busy ? 'Abriendo conversación…' : 'Contactar al vendedor'));
  });
}
