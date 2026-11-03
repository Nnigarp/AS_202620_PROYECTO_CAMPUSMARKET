import 'package:flutter/material.dart';

import '../shared/api_error.dart';
import '../usuarios/session_controller.dart';
import 'catalogo_api.dart';
import 'catalogo_detalle_page.dart';
import 'publicacion_catalogo.dart';
import 'widgets/catalogo_card.dart';

class CatalogoPage extends StatefulWidget {
  const CatalogoPage({super.key});

  @override
  State<CatalogoPage> createState() => _CatalogoPageState();
}

class _CatalogoPageState extends State<CatalogoPage> {
  final _api = const CatalogoApi();

  final _busquedaController = TextEditingController();
  final _precioMinController = TextEditingController();
  final _precioMaxController = TextEditingController();

  List<PublicacionCatalogo> _publicaciones = [];

  String? _modalidad;
  String? _estado;
  bool _miUniversidad = false;
  bool _cargando = true;
  int _requestRevision = 0;
  String? _error;

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  @override
  void dispose() {
    _busquedaController.dispose();
    _precioMinController.dispose();
    _precioMaxController.dispose();
    super.dispose();
  }

  Future<void> _cargar() async {
    final revision = ++_requestRevision;
    final minimumText = _precioMinController.text.trim().replaceAll(',', '.');
    final maximumText = _precioMaxController.text.trim().replaceAll(',', '.');
    final minimum = double.tryParse(minimumText);
    final maximum = double.tryParse(maximumText);
    final invalid = (minimumText.isNotEmpty && (minimum == null || !minimum.isFinite || minimum < 0))
        || (maximumText.isNotEmpty && (maximum == null || !maximum.isFinite || maximum < 0));
    if (invalid || (minimum != null && maximum != null && minimum > maximum)) {
      setState(() {
        _cargando = false;
        _error = invalid ? 'Ingresa precios válidos, mayores o iguales a cero.'
          : 'El precio mínimo no puede superar al máximo.';
      });
      return;
    }
    setState(() {
      _cargando = true;
      _error = null;
    });

    try {
      final resultado = await _api.buscar(
        texto: _busquedaController.text,
        modalidad: _modalidad,
        estado: _estado,
        precioMin: minimum,
        precioMax: maximum,
        universidadId: _miUniversidad ? SessionController.instance.usuario?.universidadId : null,
      );

      if (!mounted || revision != _requestRevision) return;

      setState(() {
        _publicaciones = resultado;
      });
    } catch (error) {
      if (!mounted || revision != _requestRevision) return;

      setState(() {
        _error = readableError(error);
      });
    } finally {
      if (mounted && revision == _requestRevision) {
        setState(() {
          _cargando = false;
        });
      }
    }
  }

  void _limpiarFiltros() {
    _busquedaController.clear();
    _precioMinController.clear();
    _precioMaxController.clear();

    setState(() {
      _modalidad = null;
      _estado = null;
      _miUniversidad = false;
    });

    _cargar();
  }

  void _abrirDetalle(PublicacionCatalogo publicacion) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => CatalogoDetallePage(publicacion: publicacion),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Scaffold(
      backgroundColor: colors.surface,
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, viewport) {
            final horizontalPadding = viewport.maxWidth < 600 ? 14.0 : 24.0;

            return SingleChildScrollView(
              padding: EdgeInsets.fromLTRB(
                horizontalPadding,
                24,
                horizontalPadding,
                36,
              ),
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 1400),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _HeroCatalogo(
                        busquedaController: _busquedaController,
                        onBuscar: _cargar,
                      ),
                      const SizedBox(height: 28),
                      LayoutBuilder(
                        builder: (context, constraints) {
                          final desktop = constraints.maxWidth >= 950;

                          final filtros = _PanelFiltros(
                            miUniversidad: _miUniversidad,
                            universidadDisponible: SessionController.instance.authenticated && SessionController.instance.usuario?.universidadId != null,
                            onMiUniversidadChanged: (value) {
                              setState(() => _miUniversidad = value);
                              _cargar();
                            },
                            modalidad: _modalidad,
                            estado: _estado,
                            precioMinController: _precioMinController,
                            precioMaxController: _precioMaxController,
                            onModalidadChanged: (value) {
                              setState(() {
                                _modalidad = value;
                              });
                              _cargar();
                            },
                            onEstadoChanged: (value) {
                              setState(() {
                                _estado = value;
                              });
                              _cargar();
                            },
                            onAplicar: _cargar,
                            onLimpiar: _limpiarFiltros,
                          );

                          final resultados = _ResultadosCatalogo(
                            key: const Key('catalogo-resultados'),
                            publicaciones: _publicaciones,
                            cargando: _cargando,
                            error: _error,
                            onRetry: _cargar,
                            onTap: _abrirDetalle,
                          );

                          if (desktop) {
                            return Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                SizedBox(width: 280, child: filtros),
                                const SizedBox(width: 24),
                                Expanded(child: resultados),
                              ],
                            );
                          }

                          return Column(
                            children: [
                              filtros,
                              const SizedBox(height: 24),
                              resultados,
                            ],
                          );
                        },
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}

class _HeroCatalogo extends StatelessWidget {
  const _HeroCatalogo({
    required this.busquedaController,
    required this.onBuscar,
  });

  final TextEditingController busquedaController;
  final VoidCallback onBuscar;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;

    return LayoutBuilder(
      builder: (context, constraints) {
        final compact = constraints.maxWidth < 700;

        return Container(
          width: double.infinity,
          padding: EdgeInsets.all(compact ? 22 : 32),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(compact ? 22 : 28),
            gradient: LinearGradient(
              colors: [
                colors.primaryContainer,
                colors.surfaceContainerHighest,
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
          child: Builder(
            builder: (context) {
              final contenido = Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 7,
                    ),
                    decoration: BoxDecoration(
                      color: colors.secondaryContainer,
                      borderRadius: BorderRadius.circular(999),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.groups_outlined,
                          size: 17,
                          color: colors.onSecondaryContainer,
                        ),
                        const SizedBox(width: 6),
                        Text(
                          'Comunidad universitaria',
                          style: theme.textTheme.labelLarge?.copyWith(
                            color: colors.onSecondaryContainer,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 18),
                  Text(
                    'Compra, vende y conecta\nen tu universidad',
                    style: (compact
                            ? theme.textTheme.headlineMedium
                            : theme.textTheme.displaySmall)
                        ?.copyWith(
                          fontWeight: FontWeight.w900,
                          height: 1.05,
                        ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Explora publicaciones de la comunidad universitaria '
                    'y encuentra productos por modalidad, estado y precio.',
                    style: theme.textTheme.bodyLarge?.copyWith(
                      color: colors.onSurfaceVariant,
                      height: 1.5,
                    ),
                  ),
                  const SizedBox(height: 24),
                  Wrap(
                    spacing: 18,
                    runSpacing: 12,
                    children: const [
                      _Beneficio(
                        icono: Icons.shield_outlined,
                        texto: 'Seguro y confiable',
                      ),
                      _Beneficio(
                        icono: Icons.school_outlined,
                        texto: 'Comunidad universitaria',
                      ),
                      _Beneficio(
                        icono: Icons.recycling_outlined,
                        texto: 'Segunda vida a productos',
                      ),
                    ],
                  ),
                ],
              );

              final buscador = Container(
                padding: const EdgeInsets.all(22),
                decoration: BoxDecoration(
                  color: colors.surface,
                  borderRadius: BorderRadius.circular(22),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.04),
                      blurRadius: 20,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '¿Qué estás buscando?',
                      style: theme.textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'Busca por título o descripción.',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: colors.onSurfaceVariant,
                      ),
                    ),
                    const SizedBox(height: 18),
                    TextField(
                      key: const Key('catalogo-busqueda'),
                      controller: busquedaController,
                      textInputAction: TextInputAction.search,
                      onSubmitted: (_) => onBuscar(),
                      decoration: InputDecoration(
                        hintText: 'Ej. calculadora, libro, portátil...',
                        prefixIcon: const Icon(Icons.search),
                        suffixIcon: IconButton(
                          tooltip: 'Buscar',
                          onPressed: onBuscar,
                          icon: const Icon(Icons.arrow_forward),
                        ),
                        filled: true,
                        fillColor: colors.surfaceContainerLowest,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(16),
                          borderSide: BorderSide(
                            color: colors.outlineVariant,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 14),
                    SizedBox(
                      width: double.infinity,
                      child: FilledButton.icon(
                        onPressed: onBuscar,
                        icon: const Icon(Icons.search),
                        label: const Padding(
                          padding: EdgeInsets.symmetric(vertical: 13),
                          child: Text('Buscar en el catálogo'),
                        ),
                      ),
                    ),
                  ],
                ),
              );

              if (compact) {
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    contenido,
                    const SizedBox(height: 24),
                    buscador,
                  ],
                );
              }

              return Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Expanded(flex: 3, child: contenido),
                  const SizedBox(width: 40),
                  Expanded(flex: 2, child: buscador),
                ],
              );
            },
          ),
        );
      },
    );
  }
}

class _Beneficio extends StatelessWidget {
  const _Beneficio({required this.icono, required this.texto});

  final IconData icono;
  final String texto;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 38,
          height: 38,
          decoration: BoxDecoration(
            color: colors.surface.withValues(alpha: 0.85),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(icono, size: 20, color: colors.primary),
        ),
        const SizedBox(width: 9),
        Text(texto, style: const TextStyle(fontWeight: FontWeight.w600)),
      ],
    );
  }
}

class _PanelFiltros extends StatelessWidget {
  const _PanelFiltros({
    required this.miUniversidad,
    required this.universidadDisponible,
    required this.onMiUniversidadChanged,
    required this.modalidad,
    required this.estado,
    required this.precioMinController,
    required this.precioMaxController,
    required this.onModalidadChanged,
    required this.onEstadoChanged,
    required this.onAplicar,
    required this.onLimpiar,
  });

  final bool miUniversidad;
  final bool universidadDisponible;
  final ValueChanged<bool> onMiUniversidadChanged;
  final String? modalidad;
  final String? estado;
  final TextEditingController precioMinController;
  final TextEditingController precioMaxController;
  final ValueChanged<String?> onModalidadChanged;
  final ValueChanged<String?> onEstadoChanged;
  final VoidCallback onAplicar;
  final VoidCallback onLimpiar;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;

    return Card(
      elevation: 0,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(Icons.tune, color: colors.primary),
                const SizedBox(width: 8),
                Text(
                  'Filtros',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const Spacer(),
                TextButton(onPressed: onLimpiar, child: const Text('Limpiar')),
              ],
            ),
            const SizedBox(height: 20),
            SegmentedButton<bool>(
              segments: [
                const ButtonSegment(value: false, label: Text('Toda Cartagena')),
                ButtonSegment(value: true, label: const Text('Mi universidad'), enabled: universidadDisponible),
              ],
              selected: {miUniversidad},
              onSelectionChanged: (selection) => onMiUniversidadChanged(selection.first),
            ),
            if (!universidadDisponible) ...[
              const SizedBox(height: 8),
              Text('Inicia sesión y selecciona tu universidad en tu perfil para activar este filtro.', style: theme.textTheme.bodySmall),
            ],
            const SizedBox(height: 20),
            Text(
              'Modalidad',
              style: theme.textTheme.labelLarge?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              initialValue: modalidad,
              decoration: const InputDecoration(
                hintText: 'Todas',
                border: OutlineInputBorder(),
              ),
              items: const [
                DropdownMenuItem(value: 'venta', child: Text('Venta')),
                DropdownMenuItem(value: 'alquiler', child: Text('Alquiler')),
              ],
              onChanged: onModalidadChanged,
            ),
            const SizedBox(height: 20),
            Text(
              'Estado del producto',
              style: theme.textTheme.labelLarge?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              initialValue: estado,
              decoration: const InputDecoration(
                hintText: 'Todos',
                border: OutlineInputBorder(),
              ),
              items: const [
                DropdownMenuItem(value: 'nuevo', child: Text('Nuevo')),
                DropdownMenuItem(value: 'usado', child: Text('Usado')),
                DropdownMenuItem(
                  value: 'reacondicionado',
                  child: Text('Reacondicionado'),
                ),
              ],
              onChanged: onEstadoChanged,
            ),
            const SizedBox(height: 20),
            Text(
              'Rango de precio',
              style: theme.textTheme.labelLarge?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              key: const Key('catalogo-precio-min'),
              controller: precioMinController,
              keyboardType: const TextInputType.numberWithOptions(
                decimal: true,
              ),
              decoration: const InputDecoration(
                labelText: 'Mínimo',
                prefixText: '\$ ',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              key: const Key('catalogo-precio-max'),
              controller: precioMaxController,
              keyboardType: const TextInputType.numberWithOptions(
                decimal: true,
              ),
              decoration: const InputDecoration(
                labelText: 'Máximo',
                prefixText: '\$ ',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 20),
            FilledButton.icon(
              onPressed: onAplicar,
              icon: const Icon(Icons.filter_alt_outlined),
              label: const Text('Aplicar filtros'),
            ),
          ],
        ),
      ),
    );
  }
}

class _ResultadosCatalogo extends StatelessWidget {
  const _ResultadosCatalogo({
    super.key,
    required this.publicaciones,
    required this.cargando,
    required this.error,
    required this.onRetry,
    required this.onTap,
  });

  final List<PublicacionCatalogo> publicaciones;
  final bool cargando;
  final String? error;
  final VoidCallback onRetry;
  final ValueChanged<PublicacionCatalogo> onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;

    if (cargando) {
      return const Padding(
        padding: EdgeInsets.all(60),
        child: Center(child: CircularProgressIndicator()),
      );
    }

    if (error != null) {
      return Container(
        width: double.infinity,
        padding: const EdgeInsets.all(40),
        decoration: BoxDecoration(
          color: colors.errorContainer.withValues(alpha: 0.35),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Column(
          children: [
            Icon(Icons.cloud_off_outlined, size: 54, color: colors.error),
            const SizedBox(height: 16),
            Text(
              'No fue posible cargar el catálogo',
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              error!,
              textAlign: TextAlign.center,
              style: TextStyle(color: colors.onSurfaceVariant),
            ),
            const SizedBox(height: 20),
            FilledButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh),
              label: const Text('Reintentar'),
            ),
          ],
        ),
      );
    }

    if (publicaciones.isEmpty) {
      return Container(
        width: double.infinity,
        padding: const EdgeInsets.all(50),
        decoration: BoxDecoration(
          color: colors.surfaceContainerLow,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Column(
          children: [
            Icon(
              Icons.search_off_outlined,
              size: 52,
              color: colors.onSurfaceVariant,
            ),
            const SizedBox(height: 14),
            Text(
              'No encontramos publicaciones',
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Prueba con otros términos o modifica los filtros.',
              textAlign: TextAlign.center,
              style: TextStyle(color: colors.onSurfaceVariant),
            ),
          ],
        ),
      );
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        var columnas = 1;
        var proporcion = 0.66;

        if (constraints.maxWidth >= 1050) {
          columnas = 4;
          proporcion = 0.72;
        } else if (constraints.maxWidth >= 930) {
          columnas = 3;
          proporcion = 0.74;
        } else if (constraints.maxWidth >= 560) {
          columnas = 2;
          proporcion = 0.72;
        }

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    'Resultados (${publicaciones.length})',
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                IconButton(
                  tooltip: 'Actualizar',
                  onPressed: onRetry,
                  icon: const Icon(Icons.refresh),
                ),
              ],
            ),
            const SizedBox(height: 18),
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: publicaciones.length,
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: columnas,
                crossAxisSpacing: 18,
                mainAxisSpacing: 18,
                childAspectRatio: proporcion,
              ),
              itemBuilder: (context, index) {
                final publicacion = publicaciones[index];

                return CatalogoCard(
                  publicacion: publicacion,
                  onTap: () => onTap(publicacion),
                );
              },
            ),
          ],
        );
      },
    );
  }
}
