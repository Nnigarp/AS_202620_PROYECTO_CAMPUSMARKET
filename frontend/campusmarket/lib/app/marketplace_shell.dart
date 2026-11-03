import 'package:flutter/material.dart';

import '../catalogo/catalogo_page.dart';
import '../favoritos/favoritos_page.dart';
import '../mensajeria/bandeja_page.dart';
import '../publicaciones/mis_publicaciones_page.dart';
import '../publicaciones/publicacion_form_page.dart';
import '../usuarios/auth_page.dart';
import '../usuarios/perfil_page.dart';
import '../usuarios/session_controller.dart';
import 'inicio_page.dart';

class MarketplaceShell extends StatefulWidget {
  const MarketplaceShell({super.key});
  @override
  State<MarketplaceShell> createState() => _MarketplaceShellState();
}

class _MarketplaceShellState extends State<MarketplaceShell> {
  int _indice = 0;
  int _catalogRevision = 0;
  int _ownRevision = 0;
  int? _accountId;
  final Set<int> _visited = {0};

  @override
  void initState() {
    super.initState();
    _accountId = SessionController.instance.usuario?.id;
    SessionController.instance.addListener(_sessionChanged);
  }

  @override
  void dispose() {
    SessionController.instance.removeListener(_sessionChanged);
    super.dispose();
  }

  void _sessionChanged() {
    if (!mounted) return;
    setState(() {
      final id = SessionController.instance.usuario?.id;
      if (id != _accountId) {
        _accountId = id;
        _indice = 0;
        _visited..clear()..add(0);
        _ownRevision++;
      }
    });
  }

  Future<void> _seleccionar(int indice) async {
    if (indice >= 2 && !SessionController.instance.authenticated) {
      final entered = await Navigator.of(context).push<bool>(
        MaterialPageRoute(builder: (_) => const AuthPage()),
      );
      if (!mounted || entered != true || !SessionController.instance.authenticated) return;
    }
    if (!mounted) return;
    setState(() {
      // Inicio vuelve a consultar la fuente de verdad al regresar de otra vista.
      // No conservar una portada potencialmente obsoleta tras editar imágenes
      // o publicaciones en las pantallas de gestión.
      if (indice == 0 && _indice != 0) {
        _catalogRevision++;
      }
      _indice = indice;
      _visited.add(indice);
    });
  }

  void _irInicio() => _seleccionar(0);
  void _irCatalogo() => _seleccionar(1);
  void _irMisPublicaciones() => _seleccionar(2);
  void _irPublicar() => _seleccionar(3);
  void _irFavoritos() => _seleccionar(4);
  void _irMensajes() => _seleccionar(5);

  void _publicacionCambiada() => setState(() => _catalogRevision++);

  void _publicacionCreada() {
    setState(() {
      _catalogRevision++;
      _ownRevision++;
      _visited.add(2);
      _indice = 2;
    });
  }

  void _cuenta() {
    Navigator.of(context).push(MaterialPageRoute(
      builder: (_) => SessionController.instance.authenticated ? const PerfilPage() : const AuthPage(),
    ));
  }

  Widget _accountButton({bool compact = false}) {
    final authenticated = SessionController.instance.authenticated;
    final icon = authenticated ? Icons.account_circle_outlined : Icons.login;
    final label = authenticated ? 'Mi cuenta' : 'Iniciar sesión';
    return compact
      ? IconButton(key: const Key('cuenta'), tooltip: label, onPressed: _cuenta, icon: Icon(icon))
      : TextButton.icon(key: const Key('cuenta'), onPressed: _cuenta, icon: Icon(icon), label: Text(label));
  }

  @override
  Widget build(BuildContext context) {
    final authenticated = SessionController.instance.authenticated;
    final identity = _accountId?.toString() ?? 'visitante';
    final paginas = [
      InicioPage(
        key: ValueKey('inicio-$_catalogRevision'),
        onIrCatalogo: _irCatalogo, onIrPublicar: _irPublicar,
      ),
      _visited.contains(1)
        ? CatalogoPage(key: ValueKey('catalogo-$_catalogRevision'))
        : const SizedBox.shrink(),
      authenticated && _visited.contains(2)
        ? MisPublicacionesPage(
            key: ValueKey('mias-$identity-$_ownRevision'), onChanged: _publicacionCambiada,
          )
        : const SizedBox.shrink(),
      authenticated && _visited.contains(3)
        ? PublicacionFormPage(
            key: ValueKey('publicar-$identity'), onPublicada: _publicacionCreada,
          )
        : const SizedBox.shrink(),
      authenticated && _visited.contains(4)
        ? FavoritosPage(key: ValueKey('favoritos-$identity'))
        : const SizedBox.shrink(),
      authenticated && _visited.contains(5)
        ? BandejaPage(key: ValueKey('mensajes-$identity'))
        : const SizedBox.shrink(),
    ];

    return LayoutBuilder(builder: (context, constraints) {
      final desktop = constraints.maxWidth >= 1200;
      final tablet = constraints.maxWidth >= 700 && !desktop;
      final content = IndexedStack(index: _indice, children: paginas);
      return Scaffold(
        appBar: AppBar(
          toolbarHeight: desktop ? 76 : 64,
          titleSpacing: desktop ? 28 : 16,
          title: InkWell(
            borderRadius: BorderRadius.circular(14), onTap: _irInicio,
            child: _CampusMarketBrand(compact: !desktop),
          ),
          actions: [
            if (desktop) ...[
              _DesktopNavButton(key: const Key('nav-inicio'), icon: Icons.home_outlined, label: 'Inicio', selected: _indice == 0, onPressed: _irInicio),
              _DesktopNavButton(key: const Key('nav-catalogo'), icon: Icons.storefront_outlined, label: 'Catálogo', selected: _indice == 1, onPressed: _irCatalogo),
              _DesktopNavButton(key: const Key('nav-mias'), icon: Icons.inventory_2_outlined, label: 'Mis publicaciones', selected: _indice == 2, onPressed: _irMisPublicaciones),
              _DesktopNavButton(key: const Key('nav-publicar'), icon: Icons.add_circle_outline, label: 'Publicar', selected: _indice == 3, onPressed: _irPublicar),
              _DesktopNavButton(key: const Key('nav-favoritos'), icon: Icons.favorite_border, label: 'Favoritos', selected: _indice == 4, onPressed: _irFavoritos),
              IconButton(key: const Key('nav-mensajes'), tooltip: 'Mis mensajes', isSelected: _indice == 5,
                icon: const Icon(Icons.chat_bubble_outline), onPressed: _irMensajes),
              const SizedBox(width: 12),
            ],
            _accountButton(compact: !desktop),
            const SizedBox(width: 12),
          ],
        ),
        body: tablet
          ? Row(children: [
              NavigationRail(
                selectedIndex: _indice,
                onDestinationSelected: _seleccionar,
                labelType: NavigationRailLabelType.all,
                destinations: const [
                  NavigationRailDestination(icon: Icon(Icons.home_outlined, key: Key('nav-inicio')), selectedIcon: Icon(Icons.home), label: Text('Inicio')),
                  NavigationRailDestination(icon: Icon(Icons.storefront_outlined, key: Key('nav-catalogo')), selectedIcon: Icon(Icons.storefront), label: Text('Catálogo')),
                  NavigationRailDestination(icon: Icon(Icons.inventory_2_outlined, key: Key('nav-mias')), selectedIcon: Icon(Icons.inventory_2), label: Text('Mis publicaciones')),
                  NavigationRailDestination(icon: Icon(Icons.add_circle_outline, key: Key('nav-publicar')), selectedIcon: Icon(Icons.add_circle), label: Text('Publicar')),
                  NavigationRailDestination(icon: Icon(Icons.favorite_border, key: Key('nav-favoritos')), selectedIcon: Icon(Icons.favorite), label: Text('Favoritos')),
                  NavigationRailDestination(icon: Icon(Icons.chat_bubble_outline, key: Key('nav-mensajes')), selectedIcon: Icon(Icons.chat_bubble), label: Text('Mensajes')),
                ],
              ),
              const VerticalDivider(width: 1),
              Expanded(child: content),
            ])
          : content,
        bottomNavigationBar: desktop || tablet ? null : NavigationBar(
          selectedIndex: _indice, onDestinationSelected: _seleccionar,
          labelBehavior: constraints.maxWidth < 520 ? NavigationDestinationLabelBehavior.onlyShowSelected : NavigationDestinationLabelBehavior.alwaysShow,
          destinations: const [
            NavigationDestination(key: Key('nav-inicio'), icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Inicio'),
            NavigationDestination(key: Key('nav-catalogo'), icon: Icon(Icons.storefront_outlined), selectedIcon: Icon(Icons.storefront), label: 'Catálogo'),
            NavigationDestination(key: Key('nav-mias'), icon: Icon(Icons.inventory_2_outlined), selectedIcon: Icon(Icons.inventory_2), label: 'Mis publicaciones'),
            NavigationDestination(key: Key('nav-publicar'), icon: Icon(Icons.add_circle_outline), selectedIcon: Icon(Icons.add_circle), label: 'Publicar'),
            NavigationDestination(key: Key('nav-favoritos'), icon: Icon(Icons.favorite_border), selectedIcon: Icon(Icons.favorite), label: 'Favoritos'),
            NavigationDestination(key: Key('nav-mensajes'), icon: Icon(Icons.chat_bubble_outline), selectedIcon: Icon(Icons.chat_bubble), label: 'Mensajes'),
          ],
        ),
      );
    });
  }
}

class _CampusMarketBrand extends StatelessWidget {
  const _CampusMarketBrand({this.compact = false});

  final bool compact;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;

    return Semantics(
      button: true,
      label: 'CampusMarket, ir al inicio',
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: compact ? 38 : 42,
            height: compact ? 38 : 42,
            decoration: BoxDecoration(
              color: colors.primaryContainer,
              borderRadius: BorderRadius.circular(13),
            ),
            child: Icon(Icons.school_outlined, color: colors.primary),
          ),
          const SizedBox(width: 11),
          RichText(
            text: TextSpan(
              style:
                  (compact
                          ? theme.textTheme.titleMedium
                          : theme.textTheme.titleLarge)
                      ?.copyWith(fontWeight: FontWeight.w900),
              children: [
                TextSpan(
                  text: 'Campus',
                  style: TextStyle(color: colors.onSurface),
                ),
                TextSpan(
                  text: 'Market',
                  style: TextStyle(color: colors.primary),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _DesktopNavButton extends StatelessWidget {
  const _DesktopNavButton({
    super.key,
    required this.icon,
    required this.label,
    required this.selected,
    required this.onPressed,
  });

  final IconData icon;
  final String label;
  final bool selected;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return TextButton.icon(
      onPressed: onPressed,
      icon: Icon(icon),
      label: Text(label),
      style: TextButton.styleFrom(
        foregroundColor: selected ? colors.primary : colors.onSurfaceVariant,
        backgroundColor: selected
            ? colors.primaryContainer.withValues(alpha: 0.55)
            : Colors.transparent,
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 15),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      ),
    );
  }
}
