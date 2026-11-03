import 'package:flutter/material.dart';

import '../shared/api_error.dart';
import 'session_controller.dart';
import 'universidades_api.dart';

class AuthPage extends StatefulWidget {
  const AuthPage({super.key, this.registroInicial = false});
  final bool registroInicial;
  @override
  State<AuthPage> createState() => _AuthPageState();
}

class _AuthPageState extends State<AuthPage> {
  final _formKey = GlobalKey<FormState>();
  final _nombre = TextEditingController();
  final _correo = TextEditingController();
  final _password = TextEditingController();
  late bool _registro = widget.registroInicial;
  bool _busy = false;
  bool _ocultar = true;
  String? _error;
  String? _notice;
  List<Universidad> _universidades = const [];
  int? _universidadId;
  bool _cargandoUniversidades = true;
  String? _errorUniversidades;

  @override
  void initState() {
    super.initState();
    _cargarUniversidades();
  }

  Future<void> _cargarUniversidades() async {
    try {
      final lista = await const UniversidadesApi().listar();
      if (mounted) setState(() { _universidades = lista; _cargandoUniversidades = false; _errorUniversidades = null; });
    } catch (_) {
      if (mounted) setState(() { _cargandoUniversidades = false; _errorUniversidades = 'No se pudo cargar el listado de universidades.'; });
    }
  }

  @override
  void dispose() {
    _nombre.dispose();
    _correo.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _enviar() async {
    if (_busy || !_formKey.currentState!.validate()) return;
    FocusScope.of(context).unfocus();
    setState(() { _busy = true; _error = null; _notice = null; });
    try {
      final session = SessionController.instance;
      if (_registro) {
        await session.registrar(
          nombre: _nombre.text.trim(),
          correo: _correo.text.trim(),
          password: _password.text,
          universidadId: _universidadId,
        );
        if (!mounted) return;
        _password.clear();
        setState(() {
          _registro = false;
          _notice = 'Cuenta creada. Inicia sesión para publicar y gestionar tus productos.';
        });
      } else {
        await session.login(correo: _correo.text.trim(), password: _password.text);
        _password.clear();
        if (!mounted) return;
        Navigator.of(context).pop(true);
      }
    } catch (error) {
      if (mounted) setState(() => _error = readableError(error));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;
    return Scaffold(
      appBar: AppBar(title: const Text('CampusMarket')),
      body: LayoutBuilder(builder: (context, constraints) {
        final wide = constraints.maxWidth >= 900;
        final form = ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 460),
          child: AutofillGroup(
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Icon(Icons.school_outlined, color: colors.primary, size: 44),
                  const SizedBox(height: 22),
                  Text(
                    _registro ? 'Tu campus. Tu comunidad.' : 'Qué bueno verte de nuevo',
                    style: theme.textTheme.headlineLarge,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    _registro
                        ? 'Dale una segunda vida a lo que ya no usas y encuentra lo que necesitas.'
                        : 'Tus publicaciones y tu próximo hallazgo te esperan.',
                    style: theme.textTheme.bodyLarge?.copyWith(color: colors.onSurfaceVariant),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 28),
                  SegmentedButton<bool>(
                    segments: const [
                      ButtonSegment(value: false, label: Text('Iniciar sesión')),
                      ButtonSegment(value: true, label: Text('Crear cuenta')),
                    ],
                    selected: {_registro},
                    onSelectionChanged: _busy ? null : (selection) {
                      setState(() {
                        _registro = selection.first;
                        _error = null;
                        _notice = null;
                      });
                    },
                  ),
                  const SizedBox(height: 28),
                  if (_registro) ...[
                    TextFormField(
                      key: const Key('auth-nombre'),
                      controller: _nombre,
                      enabled: !_busy,
                      maxLength: 80,
                      textInputAction: TextInputAction.next,
                      autofillHints: const [AutofillHints.name],
                      decoration: const InputDecoration(labelText: 'Nombre', prefixIcon: Icon(Icons.person_outline)),
                      validator: (value) => (value ?? '').trim().length < 2
                          ? 'Ingresa un nombre de al menos 2 caracteres.' : null,
                    ),
                    const SizedBox(height: 16),
                    DropdownButtonFormField<int>(
                      key: const Key('auth-universidad'),
                      initialValue: _universidadId,
                      isExpanded: true,
                      decoration: InputDecoration(
                        labelText: 'Universidad en Cartagena',
                        helperText: _cargandoUniversidades ? 'Cargando universidades...' : 'Selecciona tu universidad; no exigimos correo institucional.',
                        errorText: _errorUniversidades,
                        prefixIcon: const Icon(Icons.school_outlined),
                      ),
                      items: _universidades.map((u) => DropdownMenuItem<int>(
                        value: u.id, child: Text(u.nombre, overflow: TextOverflow.ellipsis),
                      )).toList(),
                      onChanged: _busy || _cargandoUniversidades ? null : (id) => setState(() => _universidadId = id),
                    ),
                    const SizedBox(height: 16),
                  ],
                  TextFormField(
                    key: const Key('auth-correo'),
                    controller: _correo,
                    enabled: !_busy,
                    keyboardType: TextInputType.emailAddress,
                    textInputAction: TextInputAction.next,
                    autofillHints: const [AutofillHints.username, AutofillHints.email],
                    decoration: const InputDecoration(labelText: 'Correo electrónico', prefixIcon: Icon(Icons.alternate_email)),
                    validator: (value) {
                      final email = (value ?? '').trim();
                      return email.length > 254 || !RegExp(r'^[^\s@]+@[^\s@]+\.[^\s@]+$').hasMatch(email)
                          ? 'Ingresa un correo electrónico válido.' : null;
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    key: const Key('auth-password'),
                    controller: _password,
                    enabled: !_busy,
                    obscureText: _ocultar,
                    autocorrect: false,
                    enableSuggestions: false,
                    textInputAction: TextInputAction.done,
                    autofillHints: [_registro ? AutofillHints.newPassword : AutofillHints.password],
                    onFieldSubmitted: (_) => _enviar(),
                    decoration: InputDecoration(
                      labelText: 'Contraseña',
                      helperText: _registro ? 'Entre 12 y 128 caracteres. Puedes usar una frase.' : null,
                      prefixIcon: const Icon(Icons.lock_outline),
                      suffixIcon: IconButton(
                        tooltip: _ocultar ? 'Mostrar contraseña' : 'Ocultar contraseña',
                        onPressed: () => setState(() => _ocultar = !_ocultar),
                        icon: Icon(_ocultar ? Icons.visibility_outlined : Icons.visibility_off_outlined),
                      ),
                    ),
                    validator: (value) => value == null || value.length < 12 || value.length > 128
                        ? 'La contraseña debe tener entre 12 y 128 caracteres.' : null,
                  ),
                  if (_error != null || _notice != null) ...[
                    const SizedBox(height: 20),
                    Semantics(
                      liveRegion: true,
                      child: Container(
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          color: _error != null ? colors.errorContainer : colors.primaryContainer,
                          borderRadius: BorderRadius.circular(14),
                        ),
                        child: Text(_error ?? _notice!),
                      ),
                    ),
                  ],
                  const SizedBox(height: 24),
                  FilledButton(
                    key: const Key('auth-enviar'),
                    onPressed: _busy ? null : _enviar,
                    child: _busy
                        ? const SizedBox(width: 22, height: 22, child: CircularProgressIndicator(strokeWidth: 2))
                        : Text(_registro ? 'Crear mi cuenta' : 'Entrar a CampusMarket'),
                  ),
                  const SizedBox(height: 18),
                  Text(
                    'Puedes explorar el catálogo sin iniciar sesión.',
                    textAlign: TextAlign.center,
                    style: theme.textTheme.bodyMedium?.copyWith(color: colors.onSurfaceVariant),
                  ),
                ],
              ),
            ),
          ),
        );
        final formArea = SingleChildScrollView(
          padding: EdgeInsets.symmetric(horizontal: wide ? 48 : 24, vertical: 36),
          child: Center(child: form),
        );
        if (!wide) return formArea;
        return Row(children: [
          Expanded(
            child: Container(
              height: double.infinity,
              padding: const EdgeInsets.all(56),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft, end: Alignment.bottomRight,
                  colors: [colors.primary, const Color(0xFF29216B)],
                ),
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.storefront_outlined, size: 86, color: Colors.white),
                  const SizedBox(height: 36),
                  Text('Lo que necesitas\nestá más cerca.', style: theme.textTheme.displaySmall?.copyWith(color: Colors.white)),
                  const SizedBox(height: 24),
                  const Text(
                    'Libros para el próximo semestre.\nUna calculadora que sigue dando todo.\nUn hallazgo con historia.',
                    style: TextStyle(color: Colors.white, fontSize: 19, height: 1.7),
                  ),
                  const SizedBox(height: 36),
                  const Text('HECHO PARA LA VIDA UNIVERSITARIA', style: TextStyle(color: Colors.white70, letterSpacing: 1.7, fontWeight: FontWeight.w700)),
                ],
              ),
            ),
          ),
          Expanded(child: formArea),
        ]);
      }),
    );
  }
}
