import 'package:flutter/material.dart';

import '../catalogo/catalogo_detalle_page.dart';
import '../catalogo/widgets/catalogo_card.dart';
import 'favoritos_controller.dart';

class FavoritosPage extends StatefulWidget {
  const FavoritosPage({super.key, this.controller});
  final FavoritosController? controller;
  @override
  State<FavoritosPage> createState() => _FavoritosPageState();
}

class _FavoritosPageState extends State<FavoritosPage> {
  FavoritosController get controller => widget.controller ?? FavoritosController.instance;
  @override
  void initState() {
    super.initState();
    Future.microtask(() { if (mounted) controller.refresh(); });
  }

  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: controller,
    builder: (context, _) => LayoutBuilder(builder: (context, constraints) {
      final columns = constraints.maxWidth >= 1100 ? 4
          : constraints.maxWidth >= 750 ? 3
          : constraints.maxWidth >= 520 ? 2 : 1;
      return Column(children: [
        Padding(
          padding: const EdgeInsets.all(20),
          child: Row(children: [
            Expanded(child: Text('Mis favoritos', style: Theme.of(context).textTheme.headlineSmall)),
            IconButton(onPressed: controller.loading ? null : controller.refresh,
              tooltip: 'Actualizar favoritos', icon: const Icon(Icons.refresh)),
          ]),
        ),
        if (controller.loading) const LinearProgressIndicator(),
        if (controller.error != null)
          Padding(padding: const EdgeInsets.all(20), child: Semantics(liveRegion: true, child: Text(controller.error!))),
        Expanded(child: controller.items.isEmpty || controller.loading || controller.error != null
          ? Center(child: Padding(padding: const EdgeInsets.all(24), child: Text(
              controller.loading ? 'Consultando favoritos…' : controller.error != null
                ? 'Actualiza para volver a consultar tus favoritos.'
                : 'Aún no tienes favoritos disponibles. Guarda publicaciones con el corazón.',
              textAlign: TextAlign.center,
            )))
          : GridView.builder(
              padding: const EdgeInsets.fromLTRB(20, 0, 20, 24),
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: columns, mainAxisExtent: 450, crossAxisSpacing: 16, mainAxisSpacing: 16,
              ),
              itemCount: controller.items.length,
              itemBuilder: (context, index) {
                final p = controller.items[index];
                return CatalogoCard(publicacion: p, favoritosController: controller, onTap: () => Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => CatalogoDetallePage(publicacion: p)),
                ));
              },
            )),
      ]);
    }),
  );
}
