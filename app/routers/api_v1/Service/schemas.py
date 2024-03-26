from typing import List, TypeVar, Generic

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel


class ImageUploadOut(BaseModel):
    secure_url: str
    public_id: str


T = TypeVar("T", bound=BaseModel)


class Meta(BaseModel):
    total: int
    offset: int
    limit: int
    returned: int
    max_value: int = Field(default=0)


class Paginate(GenericModel, Generic[T]):
    data: List[T]
    meta_data: Meta


class TranscribeOut(BaseModel):
    text: str
