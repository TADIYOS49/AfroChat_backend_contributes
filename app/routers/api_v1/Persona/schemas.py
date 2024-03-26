from typing import List
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, HttpUrl


# PersonaOut, PersonaCreate


class PersonaType(Enum):
    ATHLETE = "Athlete"
    AUTHOR = "Author & Poet"
    BUSINESS_MAGNATE = "Business Magnate"
    CELEBRITY_CHEF = "Celebrity Chef"
    COMEDIAN = "Comedian"
    DOCTOR = "Doctor"
    ENTREPRENEUR = "Entrepreneur"
    FICTIONAL = "Fictional"
    HISTORIAN = "Historian"
    INFLUENCER = "Influencer"
    MEDICAL_PROFESSIONAL = "Medical Professional"
    MUSICIAN = "Musician"
    PHILOSOPHER = "Philosopher"
    POLITICIAN = "Politician"
    PSYCHOLOGIST = "Psychologist"
    SCIENTIST = "Scientist"
    SPACE_EXPLORER = "Space Explorer"
    SPIRITUAL_LEADERS = "Spiritual Leaders"
    TECHNOCRAT = "Technocrat"
    ASSISTANT = "Assistant"


class PersonaExists(BaseModel):
    exists: bool
    message: str


class PersonaCategories(BaseModel):
    categories: List[str]


class QuotesOut(BaseModel):
    quote: str = Field(..., max_length=10000)

    class Config:
        from_attributes = True


class OnboardingPersonaOut(BaseModel):
    id: UUID
    full_name: str = Field(..., max_length=100)

    class Config:
        from_attributes = True


# TODO add validators based on the database models
# e.g validator for the color that it can't be 10
class PersonaBase(BaseModel):
    full_name: str = Field(..., max_length=100)
    persona_type: PersonaType
    persona_image: HttpUrl
    default_color: str = Field(..., max_length=10)
    description: str = Field(..., max_length=3000)
    long_description: str = Field(..., max_length=3000)
    is_premium: bool = False

    @field_validator("persona_type")
    def validate_persona_type(cls, v: PersonaType):
        persona_types = [
            persona_type.value for persona_type in PersonaType.__members__.values()
        ]
        if v.value not in persona_types:
            raise ValueError(
                "Invalid persona type. It must be one of the following: "
                + ", ".join(persona_types)
            )
        return v


class PersonaCreate(PersonaBase):
    initial_prompt: str = Field(..., max_length=10000)
    quotes: list[str] = Field(default_factory=list)
    visible: bool = True
    functional_tools: list[str] = Field(default_factory=list)


class PersonaEdit(BaseModel):
    id: UUID
    full_name: str | None = None
    persona_type: PersonaType | None = None
    persona_image: HttpUrl | None = None
    default_color: str | None = None
    description: str | None = None
    long_description: str | None = None
    initial_prompt: str | None = None

    @field_validator("persona_type")
    def validate_persona_type(cls, v: PersonaType):
        persona_types = [
            persona_type.value for persona_type in PersonaType.__members__.values()
        ]
        if v and v.value and v.value not in persona_types:
            raise ValueError(
                "Invalid persona type. It must be one of the following: "
                + ", ".join(persona_types)
            )
        return v


class PersonaOut(PersonaBase):
    id: UUID
    creator_uuid: UUID
    created_at: datetime
    quotes: list[QuotesOut] = Field(default_factory=list)

    class Config:
        from_attributes = True


class PersonaOutDiscover(PersonaBase):
    id: UUID
    creator_uuid: UUID
    created_at: datetime
    created_by: str

    class Config:
        from_attributes = True


class PersonaOutWithVisible(PersonaOut):
    visible: bool
    age: int | None = None
    occupation: str | None = None
    additional_info: str | None = None

    class Config:
        from_attributes = True


class PersonaOutNoQuotes(PersonaBase):
    id: UUID
    creator_uuid: UUID
    created_at: datetime
    is_preferable_persona: bool

    class Config:
        from_attributes = True


class PersonaOutWithOutQuotes(PersonaBase):
    id: UUID
    creator_uuid: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class PersonaWithPreferenceSchema(PersonaOut):
    is_preferable_persona: bool


class PersonaNoQuotes(PersonaBase):
    id: UUID
    creator_uuid: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class PersonasByCategory(BaseModel):
    persona_type: PersonaType
    personas: list[PersonaOutNoQuotes] = Field(default_factory=list)

    class Config:
        from_attributes = True


class OrderBy(str, Enum):
    PERSONA_NAME_ASC = "persona_name_asc"
    PERSONA_NAME_DESC = "persona_name_desc"
    CATEGORY_ASC = "category_asc"
    CATEGORY_DESC = "category_desc"


class PersonaInitialPromptInput(BaseModel):
    persona_name: str
    persona_type: PersonaType
    persona_image: HttpUrl
    default_color: str = "#EEF6FE"
    age: int | None = None
    occupation: str | None = None
    description: str
    additional_info: str | None = None
    visible: bool = True  # to be used for the persona to be visible to the public
    language: str | None = None


class PersonaEditInitialPromptInput(BaseModel):
    persona_name: str | None = None
    persona_type: PersonaType | None = None
    persona_image: HttpUrl | None = None
    age: int | None = None
    occupation: str | None = None
    description: str | None = None
    long_description: str | None = None
    additional_info: str | None = None
    visible: bool | None = None
    language: str | None = None
