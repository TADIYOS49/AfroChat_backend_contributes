from pydantic import BaseModel


class ParsedTextOut(BaseModel):
    text: str
