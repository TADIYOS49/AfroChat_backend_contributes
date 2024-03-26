from app.exceptions import UnprocessableEntityHTTPException

IMAGE_SIZE_EXCEEDED = UnprocessableEntityHTTPException(msg="Image size exceeded")

IMAGE_FORMAT_NOT_SUPPORTED = UnprocessableEntityHTTPException(
    msg="Image format not supported. Only .png, .svg, .jpg, .jpeg are supported"
)

AUDIO_SIZE_EXCEEDED = UnprocessableEntityHTTPException(
    msg="The uploaded audio must be less than 25 MB"
)

AUDIO_FORMAT_NOT_SUPPORTED = UnprocessableEntityHTTPException(
    msg="Invalid file format. Supported formats: ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']"
)
