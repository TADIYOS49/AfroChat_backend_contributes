from enum import Enum


class LLMModels(Enum):
    # GPT35 = "GPT 3.5"
    GEMINIPRO = "Gemini Pro"
    MISTRAL = "Mistral"
    LLAMA = "Llama"
    GEMMA = "Gemma"

    @classmethod
    def from_string(cls, string):
        for enum_member in cls:
            if enum_member.value == string:
                return enum_member
        raise ValueError("Invalid string: " + string)


class IMAGEModels(Enum):
    STABLEDIFFUSION = "Stable Diffusion"
    # DALLE3 = "DALL-E 3"

    @classmethod
    def from_string(cls, string):
        for enum_member in cls:
            if enum_member.value == string:
                return enum_member
        raise ValueError("Invalid string: " + string)
