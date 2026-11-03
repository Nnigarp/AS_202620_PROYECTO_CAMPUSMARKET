import 'package:flutter/material.dart';

import '../administracion/moderacion_page.dart';
import '../shared/api_error.dart';
import 'session_controller.dart';
import 'universidades_api.dart';

class PerfilPage extends StatefulWidget {
  const PerfilPage({super.key});
  @override
  State<PerfilPage> createState() => _PerfilPageState();
}

class _PerfilPageState extends State<PerfilPage> {
  final _nombre = TextEditingController(text: SessionController.instance.usuario?.nombre);
  final _formKey = GlobalKey<FormState>();
  bool _busy = false;
  String? _error;
  String? _notice;
  List<Universidad> _universidades = const [];
  int? _universidadId;
  String? _universidadesError;

  @override
  void initState() {
    super.initState();
    _actualizar();
    _cargarUniversidades();
  }

  Future<void> _cargarUniversidades() async {
    try {
      final lista = await const UniversidadesApi().listar();
      if (mounted) setState(() => _universidades = lista);
    } catch (_) {
      if (mounted) setState(() => _universidadesError = 'No se pudo cargar la lista de universidades.');
    }
  }

  @override
  void dispose() {
    _nombre.dispose();
    super.dispose();
  }

  Future<void> _actualizar() async {
    setState(() { _busy = true; _error = null; });
    try {
      await SessionController.instance.consultarActual();
      _nombre.text = SessionController.instance.usuario?.nombre ?? '';
      if (mounted) setState(() => _universidadId = SessionController.instance.usuario?.universidadId);
    } catch (error) {
      if (mounted) setState(() => _error = readableError(error));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _guardar() async {
    if (_busy || !_formKey.currentState!.validate()) return;
    setState(() { _busy = true; _error = null; _notice = null; });
    try {
      await SessionController.instance.editarPerfil(_nombre.text.trim(), universidadId: _universidadId);
      if (mounted) setState(() => _notice = 'Tu perfil fue actualizado.');
    } catch (error) {
      if (mounted) setState(() => _error = readableError(error));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _salir() async {
    if (_busy) return;
    setState(() { _busy = true; _error = null; });
    try {
      await SessionController.instance.logout();
      if (!mounted) return;
      Navigator.of(context).popUntil((route) => route.isFirst);
    } catch (error) {
      if (mounted) setState(() => _error = readableError(error));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
    animation: SessionController.instance,
    builder: (context, _) {
      final user = SessionController.instance.usuario;
      final theme = Theme.of(context);
      if (user == null) {
        return Scaffold(
          appBar: AppBar(title: const Text('Mi cuenta')),
          body: Center(child: FilledButton(
            onPressed: () => Navigator.of(context).popUntil((route) => route.isFirst),
            child: const Text('Volver al catálogo'),
          )),
        );
      }
      return Scaffold(
        appBar: AppBar(
          title: const Text('Mi cuenta'),
          actions: [IconButton(tooltip: 'Actualizar perfil', onPressed: _busy ? null : _actualizar, icon: const Icon(Icons.refresh))],
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 600),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: 20),
                  CircleAvatar(
                    radius: 38,
                    backgroundColor: theme.colorScheme.primaryContainer,
                    child: const Icon(Icons.person_outline, size: 40),
                  ),
                  const SizedBox(height: 20),
                  Text(user.nombre, style: theme.textTheme.headlineMedium, textAlign: TextAlign.center),
                  const SizedBox(height: 8),
                  Text(user.correo, textAlign: TextAlign.center),
                  const SizedBox(height: 28),
                  Card(child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Form(
                      key: _formKey,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text('Cómo te conoce tu comunidad', style: theme.textTheme.titleLarge),
                          const SizedBox(height: 20),
                          TextFormField(
                            key: const Key('perfil-nombre'),
                            controller: _nombre,
                            enabled: !_busy,
                            maxLength: 80,
                            decoration: const InputDecoration(labelText: 'Nombre'),
                            validator: (value) => (value ?? '').trim().length < 2 ? 'Ingresa al menos 2 caracteres.' : null,
                          ),
                          const SizedBox(height: 20),
                          DropdownButtonFormField<int>(
                            key: ValueKey('perfil-universidad-${_universidadId ?? "sin-asignar"}-${_universidades.length}'),
                            initialValue: _universidades.any((u) => u.id == _universidadId) ? _universidadId : null,
                            isExpanded: true,
                            decoration: InputDecoration(
                              labelText: 'Universidad en Cartagena',
                              helperText: 'Universidad declarada en tu perfil',
                              errorText: _universidadesError,
                            ),
                            items: _universidades.map((u) => DropdownMenuItem<int>(
                              value: u.id, child: Text(u.nombre, overflow: TextOverflow.ellipsis),
                            )).toList(),
                            onChanged: _busy ? null : (id) => setState(() => _universidadId = id),
                          ),
                          const SizedBox(height: 20),
                          FilledButton(
                            onPressed: _busy ? null : _guardar,
                            child: const Text('Guardar perfil'),
                          ),
                        ],
                      ),
                    ),
                  )),
                  if (_busy) ...[const SizedBox(height: 20), const LinearProgressIndicator()],
                  if (_error != null || _notice != null) ...[
                    const SizedBox(height: 20),
                    Semantics(liveRegion: true, child: Text(
                      _error ?? _notice!,
                      style: TextStyle(color: _error != null ? theme.colorScheme.error : theme.colorScheme.primary),
                    )),
                  ],
                  const SizedBox(height: 24),
                  if (user.esAdmin) ...[
                    OutlinedButton.icon(
                      onPressed: _busy ? null : () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const ModeracionPage())),
                      icon: const Icon(Icons.flag_outlined), label: const Text('Revisar reportes'),
                    ),
                    const SizedBox(height: 16),
                  ],
                  OutlinedButton.icon(
                    key: const Key('logout'),
                    onPressed: _busy ? null : _salir,
                    icon: const Icon(Icons.logout),
                    label: const Text('Cerrar sesión'),
                  ),
                ],
              ),
            ),
          ),
        ),
      );
    },
  );
}
