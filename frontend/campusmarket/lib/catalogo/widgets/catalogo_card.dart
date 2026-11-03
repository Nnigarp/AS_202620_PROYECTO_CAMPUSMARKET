import 'package:flutter/material.dart';

import '../../shared/formatters.dart';
import '../../favoritos/favorito_button.dart';
import '../../favoritos/favoritos_controller.dart';

import '../publicacion_catalogo.dart';

class CatalogoCard extends StatelessWidget {
  const CatalogoCard({
    required this.publicacion,
    required this.onTap,
    super.key,
    this.favoritosController,
  });

  final PublicacionCatalogo publicacion;
  final VoidCallback onTap;
  final FavoritosController? favoritosController;

  String _formatearPrecio(double value) => formatoPrecio(value);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;
    final imagenPrincipal = publicacion.imagenPrincipal;

    return LayoutBuilder(
      builder: (context, constraints) {
        final compacta = constraints.maxWidth < 290;

        return Card(
          clipBehavior: Clip.antiAlias,
          child: InkWell(
            onTap: onTap,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                AspectRatio(
                  aspectRatio: 16 / 10,
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      imagenPrincipal == null
                          ? _PlaceholderImagen(colorScheme: colors)
                          : Image.network(
                              imagenPrincipal.imagenUrl,
                              fit: BoxFit.cover,
                              errorBuilder: (context, error, stackTrace) {
                                return _PlaceholderImagen(colorScheme: colors);
                              },
                            ),
                      Positioned(
                        left: 10,
                        top: 10,
                        child: _Etiqueta(
                          texto: publicacion.estado,
                          icono: Icons.verified_outlined,
                        ),
                      ),
                      Positioned(
                        right: 10,
                        top: 10,
                        child: FavoritoButton(publicacion: publicacion, controller: favoritosController),
                      ),
                      if (publicacion.estadoPublicacion != 'disponible')
                        Positioned(
                          left: 10, bottom: 10,
                          child: _Etiqueta(
                            texto: publicacion.estadoPublicacion == 'reservado' ? 'Reservado' : 'Vendido',
                            icono: Icons.circle_outlined,
                          ),
                        ),
                      if (publicacion.imagenes.length > 1)
                        Positioned(
                          right: 10,
                          bottom: 10,
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 9,
                              vertical: 5,
                            ),
                            decoration: BoxDecoration(
                              color: colors.surface.withValues(alpha: 0.92),
                              borderRadius: BorderRadius.circular(999),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(
                                  Icons.photo_library_outlined,
                                  size: 14,
                                ),
                                const SizedBox(width: 4),
                                Text('${publicacion.imagenes.length}'),
                              ],
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
                Expanded(
                  child: Padding(
                    padding: EdgeInsets.fromLTRB(
                      compacta ? 13 : 16,
                      compacta ? 12 : 14,
                      compacta ? 13 : 16,
                      compacta ? 12 : 14,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          publicacion.titulo,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: (compacta
                                  ? theme.textTheme.titleSmall
                                  : theme.textTheme.titleMedium)
                              ?.copyWith(
                                fontWeight: FontWeight.w800,
                                height: 1.18,
                              ),
                        ),
                        const SizedBox(height: 7),
                        Text(
                          _formatearPrecio(publicacion.precio),
                          style: (compacta
                                  ? theme.textTheme.titleLarge
                                  : theme.textTheme.headlineSmall)
                              ?.copyWith(
                                color: colors.primary,
                                fontWeight: FontWeight.w900,
                              ),
                        ),
                        const SizedBox(height: 7),
                        Tooltip(
                          message: publicacion.universidad == null ? publicacion.universidadEtiqueta
                            : 'Universidad declarada al publicar: ${publicacion.universidadDetalle}',
                          child: Row(children: [
                            Icon(Icons.school_outlined, size: 15, color: colors.onSurfaceVariant),
                            const SizedBox(width: 5),
                            Expanded(child: Text(publicacion.universidadEtiqueta, maxLines: 1, overflow: TextOverflow.ellipsis,
                              style: theme.textTheme.labelSmall?.copyWith(color: colors.onSurfaceVariant))),
                          ]),
                        ),
                        const SizedBox(height: 7),
                        Text(
                          publicacion.descripcion,
                          maxLines: compacta ? 1 : 2,
                          overflow: TextOverflow.ellipsis,
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: colors.onSurfaceVariant,
                            height: 1.35,
                          ),
                        ),
                        const Spacer(),
                        SizedBox(
                          width: double.infinity,
                          child: OutlinedButton.icon(
                            onPressed: onTap,
                            icon: const Icon(Icons.visibility_outlined),
                            label: Text(compacta ? 'Detalles' : 'Ver detalles'),
                            style: compacta
                                ? OutlinedButton.styleFrom(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 12,
                                      vertical: 11,
                                    ),
                                  )
                                : null,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _PlaceholderImagen extends StatelessWidget {
  const _PlaceholderImagen({required this.colorScheme});

  final ColorScheme colorScheme;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            colorScheme.primaryContainer,
            colorScheme.surfaceContainerHighest,
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
      ),
      child: Center(
        child: Icon(
          Icons.shopping_bag_outlined,
          size: 54,
          color: colorScheme.primary,
        ),
      ),
    );
  }
}

class _Etiqueta extends StatelessWidget {
  const _Etiqueta({required this.texto, required this.icono});

  final String texto;
  final IconData icono;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
      decoration: BoxDecoration(
        color: colors.surface.withValues(alpha: 0.92),
        borderRadius: BorderRadius.circular(999),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.06),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icono, size: 13, color: colors.primary),
          const SizedBox(width: 4),
          Text(
            texto[0].toUpperCase() + texto.substring(1),
            style: TextStyle(
              color: colors.onSurface,
              fontWeight: FontWeight.w700,
              fontSize: 11,
            ),
          ),
        ],
      ),
    );
  }
}
