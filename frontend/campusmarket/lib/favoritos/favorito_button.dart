import 'package:flutter/material.dart';

import '../catalogo/publicacion_catalogo.dart';
import '../shared/api_error.dart';
import '../usuarios/auth_page.dart';
import '../usuarios/session_controller.dart';
import 'favoritos_controller.dart';

class FavoritoButton extends StatefulWidget {
  const FavoritoButton({super.key, required this.publicacion, this.controller});
  final PublicacionCatalogo publicacion;
  final FavoritosController? controller;
  @override
  State<FavoritoButton> createState() => _FavoritoButtonState();
}

class _FavoritoButtonState extends State<FavoritoButton> {
  FavoritosController get controller => widget.controller ?? FavoritosController.instance;
  @override
  void initState() {
    super.initState();
    Future.microtask(() { if (mounted) controller.ensureLoaded(); });
  }

  Future<void> _toggle() async {
    if (widget.controller == null && !SessionController.instance.authenticated) {
      final entered = await Navigator.of(context).push<bool>(
        MaterialPageRoute(builder: (_) => const AuthPage()),
      );
      if (!mounted || entered != true) return;
    }
    try {
      await controller.toggle(widget.publicacion);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(readableError(e))));
    }
  }

  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: controller,
    builder: (context, _) {
      final active = controller.contiene(widget.publicacion.id);
      return IconButton.filledTonal(
        key: ValueKey('favorito-${widget.publicacion.id}'),
        tooltip: active ? 'Quitar de favoritos' : 'Agregar a favoritos',
        isSelected: active,
        onPressed: controller.pendiente(widget.publicacion.id) ? null : _toggle,
        icon: Icon(active ? Icons.favorite : Icons.favorite_border),
      );
    },
  );
}
