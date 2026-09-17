from sqlalchemy import Column, Text
from sqlmodel import Field

from culinary_blog.database.base import BaseModel


class Category(BaseModel, table=True):
    __tablename__ = "categories"

    name: str = Field(max_length=100, nullable=False, unique=True)
    slug: str = Field(max_length=120, nullable=False, unique=True, index=True)
    description: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    image_url: str | None = Field(default=None, max_length=500, nullable=True)
    order_index: int = Field(default=0, nullable=False)
