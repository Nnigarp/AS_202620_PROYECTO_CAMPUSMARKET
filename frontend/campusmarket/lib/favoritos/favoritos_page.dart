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
    builder: (context, _) => LayoutBuilder(
      builder: (context, viewport) {
        final horizontalPadding = viewport.maxWidth < 600 ? 16.0 : 24.0;
        return Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1200),
            child: Padding(
              padding: EdgeInsets.symmetric(horizontal: horizontalPadding),
              child: LayoutBuilder(
                builder: (context, constraints) {
                  final width = constraints.maxWidth;
                  final columns = width >= 1050 ? 4
                      : width >= 760 ? 3
                      : width >= 520 ? 2 : 1;
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 24),
                        child: Row(
                          children: [
                            Container(
                              width: 44,
                              height: 44,
                              decoration: BoxDecoration(
                                color: Theme.of(context).colorScheme.primaryContainer,
                                borderRadius: BorderRadius.circular(14),
                              ),
                              child: Icon(Icons.favorite_outline,
                                color: Theme.of(context).colorScheme.primary),
                            ),
                            const SizedBox(width: 14),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text('Mis favoritos',
                                    style: Theme.of(context).textTheme.headlineSmall),
                                  const SizedBox(height: 4),
                                  Text('Tus publicaciones guardadas, siempre a mano.',
                                    style: Theme.of(context).textTheme.bodySmall),
                                ],
                              ),
                            ),
                            IconButton(
                              onPressed: controller.loading ? null : controller.refresh,
                              tooltip: 'Actualizar favoritos',
                              icon: const Icon(Icons.refresh),
                            ),
                          ],
                        ),
                      ),
                      if (controller.loading) const LinearProgressIndicator(),
                      if (controller.error != null)
                        Padding(
                          padding: const EdgeInsets.only(bottom: 12),
                          child: Semantics(liveRegion: true,
                            child: Text(controller.error!)),
                        ),
                      Expanded(
                        child: controller.items.isEmpty ||
                                controller.loading ||
                                controller.error != null
                            ? Center(
                                child: Padding(
                                  padding: const EdgeInsets.all(24),
                                  child: Column(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(Icons.favorite_border,
                                        size: 48,
                                        color: Theme.of(context).colorScheme.primary),
                                      const SizedBox(height: 14),
                                      Text(
                                        controller.loading ? 'Consultando favoritos…'
                                            : controller.error != null
                                                ? 'No pudimos consultar tus favoritos'
                                                : 'Aún no tienes favoritos',
                                        style: Theme.of(context).textTheme.titleLarge,
                                        textAlign: TextAlign.center,
                                      ),
                                      const SizedBox(height: 8),
                                      Text(
                                        controller.error != null
                                            ? 'Actualiza para volver a consultar tus favoritos.'
                                            : 'Guarda publicaciones con el corazón para encontrarlas aquí.',
                                        textAlign: TextAlign.center,
                                      ),
                                    ],
                                  ),
                                ),
                              )
                            : GridView.builder(
                                padding: const EdgeInsets.only(bottom: 24),
                                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                                  crossAxisCount: columns,
                                  mainAxisExtent: 450,
                                  crossAxisSpacing: 16,
                                  mainAxisSpacing: 16,
                                ),
                                itemCount: controller.items.length,
                                itemBuilder: (context, index) {
                                  final publication = controller.items[index];
                                  return CatalogoCard(
                                    publicacion: publication,
                                    favoritosController: controller,
                                    onTap: () => Navigator.of(context).push(
                                      MaterialPageRoute(
                                        builder: (_) => CatalogoDetallePage(publicacion: publication),
                                      ),
                                    ),
                                  );
                                },
                              ),
                      ),
                    ],
                  );
                },
              ),
            ),
          ),
        );
      },
    ),
  );
}
