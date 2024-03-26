from app.constants import LLMModels, IMAGEModels
from config import initial_config as config

IMAGE_GENERATOR_API = config.IMAGE_GENERATOR_API
TOKEN_LIMIT = 800

llm_models = [
    # {
    #     "name": LLMModels.GPT35,
    #     "image": "https://res.cloudinary.com/afrochat/image/upload/v1710313786/odjmswq05ncz1obtgdky.png",
    #     "is_permium": False,
    # },
    {
        "name": LLMModels.GEMINIPRO,
        "image": "https://res.cloudinary.com/afrochat/image/upload/v1710313752/nxx81sfgyr3tgv0iyvhf.png",
        "is_permium": False,
    },
    {
        "name": LLMModels.MISTRAL,
        "image": "https://res.cloudinary.com/afrochat/image/upload/v1710313950/pn2qpdqkrd3ubderq5z5.png",
        "is_permium": False,
    },
    {
        "name": LLMModels.LLAMA,
        "image": "https://res.cloudinary.com/afrochat/image/upload/v1710313823/gq16qjatrgthsilt0vwy.png",
        "is_permium": False,
    },
    {
        "name": LLMModels.GEMMA,
        "image": "https://res.cloudinary.com/afrochat/image/upload/v1710920239/gazkwpopw1q2ecgjs7xy.png",
        "is_permium": False,
    },
]

image_models = [
    {
        "name": IMAGEModels.STABLEDIFFUSION,
        "image": "https://res.cloudinary.com/afrochat/image/upload/v1710750908/gwo0hgk9o5x7cakhedo7.png",
        "is_permium": False,
    },
    # {
    #     "name": IMAGEModels.DALLE3,
    #     "image": "https://res.cloudinary.com/afrochat/image/upload/v1710313786/odjmswq05ncz1obtgdky.png",
    #     "is_permium": True,
    # },
]
