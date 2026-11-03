import '../usuarios/universidades_api.dart' show Universidad;

class ImagenCatalogo {
  const ImagenCatalogo({
    required this.id,
    required this.publicacionId,
    required this.imagenUrl,
    required this.orden,
    required this.esPrincipal,
  });

  final int id;
  final int publicacionId;
  final String imagenUrl;
  final int orden;
  final bool esPrincipal;

  factory ImagenCatalogo.fromJson(
    Map<String, dynamic> json, {
    required String baseUrl,
  }) {
    final rawUrl = json['imagen_url'] as String;
    final normalizedBaseUrl = baseUrl.endsWith('/')
        ? baseUrl.substring(0, baseUrl.length - 1)
        : baseUrl;
    final absoluteUrl = rawUrl.startsWith('http://') || rawUrl.startsWith('https://')
        ? rawUrl
        : '$normalizedBaseUrl${rawUrl.startsWith('/') ? rawUrl : '/$rawUrl'}';

    return ImagenCatalogo(
      id: json['id'] as int,
      publicacionId: json['publicacion_id'] as int,
      imagenUrl: absoluteUrl,
      orden: json['orden'] as int,
      esPrincipal: json['es_principal'] as bool,
    );
  }
}


class PublicacionCatalogo {
  const PublicacionCatalogo({
    required this.id,
    required this.titulo,
    required this.descripcion,
    required this.precio,
    required this.modalidad,
    required this.estado,
    required this.imagenes,
    this.propietarioId,
    this.universidadId,
    this.universidad,
    this.estadoPublicacion = 'disponible',
  });

  final int id;
  final String titulo;
  final String descripcion;
  final double precio;
  final String modalidad;
  final String estado;
  final List<ImagenCatalogo> imagenes;
  final int? propietarioId;
  final int? universidadId;
  final Universidad? universidad;
  final String estadoPublicacion;

  String get universidadEtiqueta => universidad?.sigla ??
      (universidadId == null ? 'Universidad no declarada' : 'Universidad no disponible');
  String get universidadDetalle => universidad?.nombre ?? universidadEtiqueta;

  ImagenCatalogo? get imagenPrincipal {
    if (imagenes.isEmpty) {
      return null;
    }

    for (final imagen in imagenes) {
      if (imagen.esPrincipal) {
        return imagen;
      }
    }

    return imagenes.first;
  }

  factory PublicacionCatalogo.fromJson(
    Map<String, dynamic> json, {
    required String baseUrl,
  }) {
    final imagenesJson = json['imagenes'] as List<dynamic>? ?? const [];

    final imagenes = imagenesJson
        .map(
          (item) => ImagenCatalogo.fromJson(
            item as Map<String, dynamic>,
            baseUrl: baseUrl,
          ),
        )
        .toList()
      ..sort((a, b) => a.orden.compareTo(b.orden));

    return PublicacionCatalogo(
      id: json['id'] as int,
      titulo: json['titulo'] as String,
      descripcion: json['descripcion'] as String,
      precio: (json['precio'] as num).toDouble(),
      modalidad: json['modalidad'] as String,
      estado: json['estado'] as String,
      imagenes: imagenes,
      propietarioId: json['propietario_id'] as int?,
      universidadId: json['universidad_id'] as int?,
      universidad: json['universidad'] == null ? null : Universidad.fromJson(json['universidad'] as Map<String, dynamic>),
      estadoPublicacion: json['estado_publicacion'] as String? ?? 'disponible',
    );
  }
}
