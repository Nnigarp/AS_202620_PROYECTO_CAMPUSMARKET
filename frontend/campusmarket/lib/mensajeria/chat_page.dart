import 'package:flutter/material.dart';

import 'chat_controller.dart';

class ChatPage extends StatefulWidget {
  const ChatPage({super.key, required this.conversacionId, this.controller});
  final int conversacionId;
  final ChatController? controller;
  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  late final ChatController _controller;
  final _text = TextEditingController();
  final _scroll = ScrollController();
  int _messageCount = 0;
  @override
  void initState() {
    super.initState();
    _controller = widget.controller ?? ChatController(conversacionId: widget.conversacionId);
    _controller.addListener(_changed);
    Future.microtask(_controller.load);
  }
  void _changed() {
    if (!_controller.active) _text.clear();
    if (_controller.mensajes.length != _messageCount) {
      _messageCount = _controller.mensajes.length;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted && _scroll.hasClients) _scroll.jumpTo(_scroll.position.maxScrollExtent);
      });
    }
  }
  Future<void> _enviar() async {
    final draft = _text.text;
    if (await _controller.enviar(draft) && mounted && _text.text == draft) _text.clear();
  }
  @override
  void dispose() {
    _controller.removeListener(_changed);
    if (widget.controller == null) _controller.dispose();
    _text.dispose();
    _scroll.dispose();
    super.dispose();
  }
  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: _controller,
    builder: (context, _) {
      final conversation = _controller.conversacion;
      final enabled = _controller.active && conversation?.publicacion != null;
      return Scaffold(
        appBar: AppBar(
          title: Text(conversation?.publicacion?.titulo ?? 'Conversación', maxLines: 1, overflow: TextOverflow.ellipsis),
          actions: [IconButton(key: const Key('chat-actualizar'), tooltip: 'Actualizar mensajes',
            onPressed: _controller.loading || !_controller.active ? null : _controller.load, icon: const Icon(Icons.refresh))],
        ),
        body: !_controller.active ? const Center(child: Text('La sesión cambió. Vuelve a abrir Mensajes.'))
          : Center(child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 920), child: Column(children: [
            if (_controller.loading) const LinearProgressIndicator(),
            if (conversation != null) Padding(padding: const EdgeInsets.all(12), child: Text(
              conversation.publicacion == null ? 'Publicación no disponible. Se conserva tu historial privado.'
                : conversation.compradorId == _controller.api.session.usuario?.id ? 'Conversas con el vendedor. Actualiza para recibir mensajes.'
                : 'Conversas con el comprador. Actualiza para recibir mensajes.',
              textAlign: TextAlign.center,
            )),
            if (_controller.error != null) Padding(padding: const EdgeInsets.all(12),
              child: Semantics(liveRegion: true, child: Text(_controller.error!))),
            if (_controller.hayMas) TextButton(onPressed: _controller.loading ? null : _controller.load,
              child: const Text('Cargar mensajes siguientes')),
            Expanded(child: _controller.mensajes.isEmpty
              ? const Center(child: Text('Aún no hay mensajes.'))
              : ListView.builder(controller: _scroll, padding: const EdgeInsets.all(16),
                itemCount: _controller.mensajes.length,
                itemBuilder: (context, index) {
                  final message = _controller.mensajes[index];
                  final own = message.remitenteId == _controller.api.session.usuario?.id;
                  return Align(alignment: own ? Alignment.centerRight : Alignment.centerLeft,
                    child: Container(
                      constraints: const BoxConstraints(maxWidth: 600),
                      margin: EdgeInsets.fromLTRB(own ? 28 : 0, 4, own ? 0 : 28, 4),
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(color: own ? Theme.of(context).colorScheme.primaryContainer
                        : Theme.of(context).colorScheme.surfaceContainerHighest, borderRadius: BorderRadius.circular(16)),
                      child: Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisSize: MainAxisSize.min, children: [
                        Text(own ? 'Tú' : 'Otro participante', style: Theme.of(context).textTheme.labelSmall),
                        Text(message.texto),
                        Text(MaterialLocalizations.of(context).formatTimeOfDay(TimeOfDay.fromDateTime(message.creadoEn.toLocal())),
                          style: Theme.of(context).textTheme.labelSmall),
                      ]),
                    ));
                })),
            SafeArea(top: false, child: Padding(padding: const EdgeInsets.all(12), child: Row(crossAxisAlignment: CrossAxisAlignment.end, children: [
              Expanded(child: TextField(key: const Key('chat-texto'), controller: _text, enabled: enabled,
                minLines: 1, maxLines: 3, maxLength: 2000, decoration: const InputDecoration(labelText: 'Mensaje', counterText: ''))),
              const SizedBox(width: 8),
              IconButton.filled(key: const Key('chat-enviar'), tooltip: 'Enviar mensaje',
                onPressed: enabled && !_controller.sending ? _enviar : null,
                icon: Icon(_controller.sending ? Icons.hourglass_top : Icons.send)),
            ]))),
          ]))),
      );
    },
  );
}
