import 'package:flutter/material.dart';

import '../shared/formatters.dart';

import '../administracion/reportar_publicacion.dart';
import '../shared/api_error.dart';
import '../favoritos/favorito_button.dart';
import 'catalogo_api.dart';
import 'publicacion_catalogo.dart';

class CatalogoDetallePage extends StatefulWidget {
  const CatalogoDetallePage({super.key, required this.publicacion});
  final PublicacionCatalogo publicacion;
  @override
  State<CatalogoDetallePage> createState() => _CatalogoDetallePageState();
}

class _CatalogoDetallePageState extends State<CatalogoDetallePage> {
  late Future<PublicacionCatalogo> _detalle;
  @override
  void initState() {
    super.initState();
    _detalle = const CatalogoApi().obtenerDetalle(widget.publicacion.id);
  }

  @override
  Widget build(BuildContext context) => FutureBuilder<PublicacionCatalogo>(
    future: _detalle,
    builder: (context, snapshot) {
      if (snapshot.hasData) return _DetalleContenido(publicacion: snapshot.data!);
      return Scaffold(
        appBar: AppBar(title: const Text('Detalle de publicación')),
        body: Center(
          child: snapshot.hasError
            ? Padding(
                padding: const EdgeInsets.all(28),
                child: Column(mainAxisSize: MainAxisSize.min, children: [
                  const Icon(Icons.inventory_2_outlined, size: 60),
                  const SizedBox(height: 20),
                  Text(readableError(snapshot.error!), textAlign: TextAlign.center),
                  const SizedBox(height: 20),
                  OutlinedButton(
                    onPressed: () => setState(() => _detalle = const CatalogoApi().obtenerDetalle(widget.publicacion.id)),
                    child: const Text('Reintentar'),
                  ),
                ]),
              )
            : const CircularProgressIndicator(),
        ),
      );
    },
  );
}

class _DetalleContenido extends StatelessWidget {
  const _DetalleContenido({required this.publicacion});

  final PublicacionCatalogo publicacion;

  String _precio(double value) => formatoPrecio(value);

  String _capitalizar(String value) {
    if (value.isEmpty) return value;
    return value[0].toUpperCase() + value.substring(1);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;

    return Scaffold(
      appBar: AppBar(title: const Text('Detalle de publicación')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(24, 24, 24, 48),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1240),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                LayoutBuilder(
                  builder: (context, constraints) {
                    final desktop = constraints.maxWidth >= 900;

                    final visual = Card(
                      clipBehavior: Clip.antiAlias,
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: _GaleriaPublicacion(
                          publicacion: publicacion,
                          height: desktop ? 520 : 380,
                        ),
                      ),
                    );

                    final informacion = Card(
                      child: Padding(
                        padding: EdgeInsets.all(desktop ? 30 : 22),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Wrap(
                              spacing: 8,
                              runSpacing: 8,
                              children: [
                                _EtiquetaDetalle(
                                  icono: Icons.circle_outlined,
                                  texto: _capitalizar(publicacion.estadoPublicacion),
                                ),
                                _EtiquetaDetalle(
                                  icono: Icons.verified_outlined,
                                  texto: _capitalizar(publicacion.estado),
                                ),
                                _EtiquetaDetalle(
                                  icono: publicacion.modalidad == 'venta'
                                      ? Icons.sell_outlined
                                      : Icons.key_outlined,
                                  texto: _capitalizar(publicacion.modalidad),
                                ),
                              ],
                            ),
                            const SizedBox(height: 22),
                            Text(
                              publicacion.titulo,
                              style: theme.textTheme.displaySmall?.copyWith(
                                fontWeight: FontWeight.w900,
                                height: 1.08,
                              ),
                            ),
                            const SizedBox(height: 14),
                            Text(
                              _precio(publicacion.precio),
                              style: theme.textTheme.headlineLarge?.copyWith(
                                color: colors.primary,
                                fontWeight: FontWeight.w900,
                              ),
                            ),
                            const SizedBox(height: 28),
                            Divider(color: colors.outlineVariant),
                            const SizedBox(height: 22),
                            Row(
                              children: [
                                Icon(Icons.notes_outlined, color: colors.primary),
                                const SizedBox(width: 8),
                                Text(
                                  'Descripción',
                                  style: theme.textTheme.titleLarge?.copyWith(
                                    fontWeight: FontWeight.w800,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            Text(
                              publicacion.descripcion,
                              style: theme.textTheme.bodyLarge?.copyWith(
                                height: 1.65,
                                color: colors.onSurfaceVariant,
                              ),
                            ),
                            const SizedBox(height: 28),
                            Container(
                              width: double.infinity,
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: colors.primaryContainer.withValues(
                                  alpha: 0.35,
                                ),
                                borderRadius: BorderRadius.circular(16),
                              ),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Icon(
                                    Icons.info_outline,
                                    color: colors.primary,
                                  ),
                                  const SizedBox(width: 10),
                                  Expanded(
                                    child: Text(
                                      'Revisa la condición y las fotografías del producto. Si encuentras contenido engañoso o inapropiado, avisa a la comunidad con un reporte.',
                                      style: theme.textTheme.bodyMedium?.copyWith(
                                        color: colors.onSurfaceVariant,
                                        height: 1.45,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 18),
                            Row(children: [FavoritoButton(publicacion: publicacion), const Text('Guardar en favoritos')]),
                            const SizedBox(height: 12),
                            ReportarPublicacionButton(
                              publicacionId: publicacion.id,
                              propietarioId: publicacion.propietarioId,
                            ),
                          ],
                        ),
                      ),
                    );

                    if (!desktop) {
                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          visual,
                          const SizedBox(height: 20),
                          informacion,
                        ],
                      );
                    }

                    return Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(flex: 6, child: visual),
                        const SizedBox(width: 24),
                        Expanded(flex: 5, child: informacion),
                      ],
                    );
                  },
                ),
                const SizedBox(height: 24),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(22),
                    child: Wrap(
                      spacing: 36,
                      runSpacing: 18,
                      children: [
                        _DatoResumen(
                          icono: Icons.image_outlined,
                          titulo: 'Fotografías',
                          valor: '${publicacion.imagenes.length}',
                        ),
                        _DatoResumen(
                          icono: Icons.verified_outlined,
                          titulo: 'Estado',
                          valor: _capitalizar(publicacion.estado),
                        ),
                        _DatoResumen(
                          icono: Icons.swap_horiz,
                          titulo: 'Modalidad',
                          valor: _capitalizar(publicacion.modalidad),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _EtiquetaDetalle extends StatelessWidget {
  const _EtiquetaDetalle({required this.icono, required this.texto});

  final IconData icono;
  final String texto;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: colors.primaryContainer.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icono, size: 17, color: colors.primary),
          const SizedBox(width: 6),
          Text(texto, style: const TextStyle(fontWeight: FontWeight.w700)),
        ],
      ),
    );
  }
}

class _DatoResumen extends StatelessWidget {
  const _DatoResumen({
    required this.icono,
    required this.titulo,
    required this.valor,
  });

  final IconData icono;
  final String titulo;
  final String valor;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 42,
          height: 42,
          decoration: BoxDecoration(
            color: colors.primaryContainer,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(icono, color: colors.primary),
        ),
        const SizedBox(width: 10),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(titulo, style: theme.textTheme.labelMedium),
            Text(
              valor,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w800,
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _GaleriaPublicacion extends StatefulWidget {
  const _GaleriaPublicacion({
    required this.publicacion,
    required this.height,
  });

  final PublicacionCatalogo publicacion;
  final double height;

  @override
  State<_GaleriaPublicacion> createState() => _GaleriaPublicacionState();
}

class _GaleriaPublicacionState extends State<_GaleriaPublicacion> {
  late final PageController _controller;
  int _indiceActual = 0;

  @override
  void initState() {
    super.initState();
    _controller = PageController();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _irA(int index) {
    final imagenes = widget.publicacion.imagenes;
    if (imagenes.isEmpty) return;

    final destino = index.clamp(0, imagenes.length - 1);
    _controller.animateToPage(
      destino,
      duration: const Duration(milliseconds: 260),
      curve: Curves.easeOutCubic,
    );
  }

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    final imagenes = widget.publicacion.imagenes;

    if (imagenes.isEmpty) {
      return Container(
        height: widget.height,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(22),
          gradient: LinearGradient(
            colors: [colors.primaryContainer, colors.surfaceContainerHighest],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Center(
          child: Icon(
            Icons.shopping_bag_outlined,
            size: 110,
            color: colors.primary,
          ),
        ),
      );
    }

    final altoPrincipal = imagenes.length > 1 ? widget.height - 94 : widget.height;

    return SizedBox(
      height: widget.height,
      child: Column(
        children: [
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(22),
              child: ColoredBox(
                color: colors.surfaceContainerLowest,
                child: Stack(
                  children: [
                    PageView.builder(
                      controller: _controller,
                      itemCount: imagenes.length,
                      onPageChanged: (index) {
                        setState(() => _indiceActual = index);
                      },
                      itemBuilder: (context, index) {
                        final imagen = imagenes[index];
                        return Image.network(
                          imagen.imagenUrl,
                          width: double.infinity,
                          height: altoPrincipal,
                          fit: BoxFit.contain,
                          errorBuilder: (context, error, stackTrace) {
                            return ColoredBox(
                              color: colors.surfaceContainerHighest,
                              child: Center(
                                child: Icon(
                                  Icons.broken_image_outlined,
                                  size: 72,
                                  color: colors.onSurfaceVariant,
                                ),
                              ),
                            );
                          },
                        );
                      },
                    ),
                    if (imagenes.length > 1) ...[
                      Positioned(
                        left: 14,
                        top: 0,
                        bottom: 0,
                        child: Center(
                          child: _BotonGaleria(
                            icono: Icons.chevron_left,
                            habilitado: _indiceActual > 0,
                            onPressed: () => _irA(_indiceActual - 1),
                          ),
                        ),
                      ),
                      Positioned(
                        right: 14,
                        top: 0,
                        bottom: 0,
                        child: Center(
                          child: _BotonGaleria(
                            icono: Icons.chevron_right,
                            habilitado: _indiceActual < imagenes.length - 1,
                            onPressed: () => _irA(_indiceActual + 1),
                          ),
                        ),
                      ),
                      Positioned(
                        right: 16,
                        bottom: 16,
                        child: DecoratedBox(
                          decoration: BoxDecoration(
                            color: colors.surface.withValues(alpha: 0.92),
                            borderRadius: BorderRadius.circular(999),
                          ),
                          child: Padding(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 7,
                            ),
                            child: Text(
                              '${_indiceActual + 1} / ${imagenes.length}',
                              style: Theme.of(context).textTheme.labelMedium?.copyWith(
                                    fontWeight: FontWeight.w800,
                                  ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ),
          if (imagenes.length > 1) ...[
            const SizedBox(height: 12),
            SizedBox(
              height: 76,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                itemCount: imagenes.length,
                separatorBuilder: (_, _) => const SizedBox(width: 10),
                itemBuilder: (context, index) {
                  final seleccionada = index == _indiceActual;
                  return InkWell(
                    borderRadius: BorderRadius.circular(14),
                    onTap: () => _irA(index),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 180),
                      width: 92,
                      padding: const EdgeInsets.all(3),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(
                          color: seleccionada ? colors.primary : colors.outlineVariant,
                          width: seleccionada ? 2.5 : 1,
                        ),
                      ),
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(10),
                        child: Image.network(
                          imagenes[index].imagenUrl,
                          fit: BoxFit.cover,
                          errorBuilder: (_, _, _) => ColoredBox(
                            color: colors.surfaceContainerHighest,
                            child: Icon(
                              Icons.broken_image_outlined,
                              color: colors.onSurfaceVariant,
                            ),
                          ),
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _BotonGaleria extends StatelessWidget {
  const _BotonGaleria({
    required this.icono,
    required this.habilitado,
    required this.onPressed,
  });

  final IconData icono;
  final bool habilitado;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Material(
      color: colors.surface.withValues(alpha: habilitado ? 0.92 : 0.55),
      shape: const CircleBorder(),
      elevation: habilitado ? 2 : 0,
      child: IconButton(
        tooltip: icono == Icons.chevron_left ? 'Imagen anterior' : 'Imagen siguiente',
        onPressed: habilitado ? onPressed : null,
        icon: Icon(icono),
      ),
    );
  }
}
