import uuid
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WidgetType(str, Enum):
    CONTACT_FORM = "CONTACT_FORM"
    SIGNUP_FORM = "SIGNUP_FORM"


class WidgetField(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=50
    )

    type: str = Field(
        min_length=1,
        max_length=30
    )

    label: str = Field(
        min_length=1,
        max_length=100
    )

    required: bool = False


class WidgetCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100
    )

    type: WidgetType

    title: str = Field(
        min_length=1,
        max_length=200
    )

    description: str | None = Field(
        default=None,
        max_length=1000
    )

    button_text: str = Field(
        default="Submit",
        min_length=1,
        max_length=100
    )

    fields: list[WidgetField] = Field(
        min_length=1,
        max_length=20
    )

    display_options: dict[str, Any] = Field(
        default_factory=dict
    )


class WidgetUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    type: WidgetType | None = None

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200
    )

    description: str | None = Field(
        default=None,
        max_length=1000
    )

    button_text: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    fields: list[WidgetField] | None = None

    display_options: dict[str, Any] | None = None

    is_active: bool | None = None


class WidgetResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID

    name: str
    type: str
    title: str
    description: str | None
    button_text: str

    fields: list[dict[str, Any]]
    display_options: dict[str, Any]

    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class PublicWidgetConfig(BaseModel):
    id: uuid.UUID
    type: str
    title: str
    description: str | None
    button_text: str
    fields: list[dict[str, Any]]
    display_options: dict[str, Any]

    model_config = ConfigDict(
        from_attributes=True
    )


class EmbedSnippetResponse(BaseModel):
    snippet: str