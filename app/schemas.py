from pydantic import BaseModel, ConfigDict, Field


class EventCreate(BaseModel):
    """Schema para criação de um novo evento."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(..., min_length=1, max_length=150)
    speaker: str = Field(..., min_length=1, max_length=120)
    capacity: int = Field(..., gt=0, le=10000)


class EventResponse(BaseModel):
    """Schema de resposta representando um evento cadastrado."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    speaker: str
    capacity: int
    created_at: str
