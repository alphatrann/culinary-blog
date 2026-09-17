from enum import IntEnum


class RecipeDifficulty(IntEnum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXPERT = 4


class RecipeStatus(IntEnum):
    DRAFT = 0
    PUBLISHED = 1
    ARCHIVED = 2
