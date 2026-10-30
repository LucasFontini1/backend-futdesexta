"""Validação de imagens recebidas antes de enviar ao Cloudinary ou disco."""
from PIL import Image, UnidentifiedImageError
from rest_framework.exceptions import ValidationError

MAX_UPLOAD_BYTES = 3 * 1024 * 1024
MAX_PIXELS = 12_000_000
ALLOWED_FORMATS = {'JPEG', 'PNG', 'WEBP'}


def validate_user_image(upload):
    if upload is None:
        return upload
    if upload.size > MAX_UPLOAD_BYTES:
        raise ValidationError('A imagem deve ter no máximo 3 MB.')
    try:
        with Image.open(upload) as image:
            if image.format not in ALLOWED_FORMATS:
                raise ValidationError('Envie imagem JPG, PNG ou WebP.')
            if image.width * image.height > MAX_PIXELS:
                raise ValidationError('Imagem com resolução excessiva.')
            image.verify()
    except (OSError, ValueError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
        raise ValidationError('Arquivo de imagem inválido.') from exc
    finally:
        if hasattr(upload, 'seek'):
            upload.seek(0)
    return upload
