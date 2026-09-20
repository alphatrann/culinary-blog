import re
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_validator, model_validator

from culinary_blog.categories.schemas import RecipePage
from culinary_blog.recipes.enums import RecipeDifficulty, RecipeStatus

_HTML = re.compile(r"[<>]")

DifficultyName = Literal["easy", "medium", "hard", "expert"]
RecipeSort = Literal["created_at", "-created_at", "title", "-title", "cook_time_minutes", "-cook_time_minutes"]


def _parse_etag(value: object) -> object:
    """`If-Match: 3`, `"3"` and `W/"3"` all carry row_version 3."""
    if isinstance(value, str):
        return value.strip().removeprefix("W/").strip('"')
    return value


# `If-Match` header value: the row_version the client last saw (FR-RCP-004).
IfMatchVersion = Annotated[int, BeforeValidator(_parse_etag), Field(ge=0)]


class NutritionIn(BaseModel):
    calories: Decimal | None = Field(default=None, ge=0, max_digits=8, decimal_places=2)
    protein: Decimal | None = Field(default=None, ge=0, max_digits=8, decimal_places=2)
    carbohydrates: Decimal | None = Field(default=None, ge=0, max_digits=8, decimal_places=2)
    fat: Decimal | None = Field(default=None, ge=0, max_digits=8, decimal_places=2)
    fiber: Decimal | None = Field(default=None, ge=0, max_digits=8, decimal_places=2)
    sodium: Decimal | None = Field(default=None, ge=0, max_digits=8, decimal_places=2)


class NutritionOut(BaseModel):
    calories: float | None = None
    protein: float | None = None
    carbohydrates: float | None = None
    fat: float | None = None
    fiber: float | None = None
    sodium: float | None = None


class StepIn(BaseModel):
    """`step_number` is deliberately absent: the server always assigns it (FR-RCP-010)."""

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    duration_minutes: int | None = Field(default=None, ge=0)
    image_url: str | None = Field(default=None, max_length=500)

    @field_validator("title", "description")
    @classmethod
    def _strip(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class IngredientIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    quantity: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=3)
    unit: str | None = Field(default=None, min_length=1, max_length=50)
    notes: str | None = Field(default=None, max_length=500)
    order_index: int | None = Field(default=None, ge=0)

    @field_validator("name")
    @classmethod
    def _clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name must not be blank")
        return value

    @model_validator(mode="after")
    def _quantity_and_unit_together(self) -> Self:
        if (self.quantity is None) != (self.unit is None):
            raise ValueError("quantity and unit must both be set or both be null")
        return self


class RecipeWrite(BaseModel):
    """Recipe fields shared by create (FR-RCP-003) and update (FR-RCP-004)."""

    title: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=1)
    category_id: uuid.UUID
    prep_time_minutes: int = Field(gt=0)
    cook_time_minutes: int = Field(gt=0)
    servings: int = Field(gt=0)
    difficulty: RecipeDifficulty = RecipeDifficulty.EASY
    nutrition: NutritionIn | None = None

    @field_validator("title")
    @classmethod
    def _clean_title(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 5:
            raise ValueError("title must be at least 5 characters")
        if _HTML.search(value):
            raise ValueError("title must not contain HTML")
        return value

    @field_validator("description")
    @classmethod
    def _clean_description(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("description must not be blank")
        return value


class RecipeCreateRequest(RecipeWrite):
    steps: list[StepIn] = Field(default_factory=list)
    ingredients: list[IngredientIn] = Field(default_factory=list)


class RecipeUpdateRequest(RecipeWrite):
    """Steps and ingredients are managed through their own endpoints (FR-RCP-009/010)."""


class StepOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    step_number: int
    title: str
    description: str
    duration_minutes: int | None
    image_url: str | None


class IngredientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    quantity: float | None
    unit: str | None
    notes: str | None
    order_index: int


class RecipeOut(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    description: str
    prep_time_minutes: int
    cook_time_minutes: int
    servings: int
    difficulty: RecipeDifficulty
    status: RecipeStatus
    category_id: uuid.UUID
    author_id: uuid.UUID
    published_at: datetime | None
    created_at: datetime
    row_version: int
    nutrition: NutritionOut
    steps: list[StepOut]
    ingredients: list[IngredientOut]


class RecipeListOut(RecipePage):
    has_next_page: bool
    has_previous_page: bool


class CategoryRefOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str


class AuthorOut(BaseModel):
    """Public author info only: never the email or roles."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    display_name: str
    avatar_url: str | None


class RecipeImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    original_url: str
    medium_url: str | None
    thumbnail_url: str | None
    alt_text: str | None
    is_primary: bool
    order_index: int


class RecipeDetailOut(RecipeOut):
    category: CategoryRefOut
    author: AuthorOut
    images: list[RecipeImageOut]
