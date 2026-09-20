import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from culinary_blog.recipes.enums import RecipeDifficulty, RecipeStatus

_HTML = re.compile(r"[<>]")


class CategoryWrite(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: str | None = Field(default=None, max_length=2000)
    image_url: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def _clean_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("name must be at least 2 characters")
        if _HTML.search(value):
            raise ValueError("name must not contain HTML")
        return value


class CategoryCreateRequest(CategoryWrite):
    pass


class CategoryUpdateRequest(CategoryWrite):
    order_index: int = Field(default=0, ge=0)


class CategoryOut(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    image_url: str | None
    recipe_count: int = 0


class RecipeSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    slug: str
    description: str
    prep_time_minutes: int
    cook_time_minutes: int
    servings: int
    difficulty: RecipeDifficulty
    status: RecipeStatus
    author_id: uuid.UUID
    published_at: datetime | None


class RecipePage(BaseModel):
    items: list[RecipeSummaryOut]
    total_count: int
    page: int
    page_size: int
    total_pages: int


class CategoryDetailOut(BaseModel):
    category: CategoryOut
    recipes: RecipePage
