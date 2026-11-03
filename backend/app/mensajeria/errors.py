class ConversationNotFoundError(LookupError):
    """No existe una conversación accesible para esta identidad."""


class ConversationUnavailableError(ValueError):
    """No se puede iniciar/enviar en este contexto de publicación."""


class MessageIdempotencyConflictError(ValueError):
    """La clave del mensaje ya pertenece a un contenido diferente."""
