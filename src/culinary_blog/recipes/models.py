import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    SmallInteger,
    Text,
    text,
)
from sqlmodel import Field

from culinary_blog.database.base import BaseModel
from culinary_blog.recipes.enums import RecipeDifficulty, RecipeStatus


class Recipe(BaseModel, table=True):
    __tablename__ = "recipes"
    __table_args__ = (
        CheckConstraint("prep_time_minutes > 0", name="ck_recipe_prep_time_positive"),
        CheckConstraint("cook_time_minutes >= 0", name="ck_recipe_cook_time_non_negative"),
        CheckConstraint("servings > 0", name="ck_recipe_servings_positive"),
        Index(
            "idx_recipe_title_trgm_gin",
            text("f_unaccent(lower(title))"),
            postgresql_using="gin",
            postgresql_ops={"f_unaccent(lower(title))": "gin_trgm_ops"},
        ),
    )

    title: str = Field(max_length=200, nullable=False)
    slug: str = Field(max_length=220, nullable=False, unique=True, index=True)
    description: str = Field(sa_column=Column(Text, nullable=False))
    prep_time_minutes: int = Field(nullable=False)
    cook_time_minutes: int = Field(nullable=False)
    servings: int = Field(nullable=False)
    difficulty: RecipeDifficulty = Field(
        default=RecipeDifficulty.EASY,
        sa_column=Column(
            SmallInteger, nullable=False, server_default=text(str(int(RecipeDifficulty.EASY))), index=True
        ),
    )
    status: RecipeStatus = Field(
        default=RecipeStatus.DRAFT,
        sa_column=Column(SmallInteger, nullable=False, server_default=text(str(int(RecipeStatus.DRAFT))), index=True),
    )

    category_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    )
    author_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)

    published_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True, index=True)
    )

    nutrition_calories: Decimal | None = Field(default=None, sa_column=Column(Numeric(8, 2)))
    nutrition_protein: Decimal | None = Field(default=None, sa_column=Column(Numeric(8, 2)))
    nutrition_carbohydrates: Decimal | None = Field(default=None, sa_column=Column(Numeric(8, 2)))
    nutrition_fat: Decimal | None = Field(default=None, sa_column=Column(Numeric(8, 2)))
    nutrition_fiber: Decimal | None = Field(default=None, sa_column=Column(Numeric(8, 2)))
    nutrition_sodium: Decimal | None = Field(default=None, sa_column=Column(Numeric(8, 2)))


class RecipeStep(BaseModel, table=True):
    __tablename__ = "recipe_steps"
    __table_args__ = (
        CheckConstraint("step_number > 0", name="ck_recipe_step_number_positive"),
        CheckConstraint(
            "duration_minutes IS NULL OR duration_minutes >= 0", name="ck_recipe_step_duration_non_negative"
        ),
        # live rows only: a soft-deleted step keeps its number but must not block renumbering (FR-RCP-010)
        Index(
            "uq_recipe_step_number",
            "recipe_id",
            "step_number",
            unique=True,
            postgresql_where=text("is_deleted = false"),
        ),
    )

    recipe_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    step_number: int = Field(nullable=False)
    title: str = Field(max_length=200, nullable=False)
    description: str = Field(sa_column=Column(Text, nullable=False))
    duration_minutes: int | None = Field(default=None, nullable=True)
    image_url: str | None = Field(default=None, max_length=500, nullable=True)


class RecipeIngredient(BaseModel, table=True):
    __tablename__ = "recipe_ingredients"
    __table_args__ = (
        CheckConstraint("(quantity IS NULL) = (unit IS NULL)", name="ck_recipe_ingredient_quantity_unit_conullable"),
        CheckConstraint("quantity IS NULL OR quantity > 0", name="ck_recipe_ingredient_quantity_positive"),
    )

    recipe_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    name: str = Field(max_length=200, nullable=False)
    quantity: Decimal | None = Field(default=None, sa_column=Column(Numeric(10, 3)))
    unit: str | None = Field(default=None, max_length=50, nullable=True)
    notes: str | None = Field(default=None, max_length=500, nullable=True)
    order_index: int = Field(default=0, nullable=False)


class RecipeImage(BaseModel, table=True):
    __tablename__ = "recipe_images"

    recipe_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    )
    original_url: str = Field(max_length=500, nullable=False)
    medium_url: str | None = Field(default=None, max_length=500, nullable=True)
    thumbnail_url: str | None = Field(default=None, max_length=500, nullable=True)
    alt_text: str | None = Field(default=None, max_length=200, nullable=True)
    is_primary: bool = Field(default=False, nullable=False)
    order_index: int = Field(default=0, nullable=False)
