from pydantic import BaseModel, Field, ConfigDict
from typing import List

class RecipeCreate(BaseModel):
    title: str = Field(..., max_length=100, description="Название блюда", examples=["Борщ"])
    cooking_time: int = Field(..., gt=0, description="Время приготовления в минутах", examples=[60])
    ingredients: List[str] = Field(..., description="Список ингредиентов", examples=[["Свекла", "Капуста", "Мясо"]])
    description: str = Field(..., max_length=1000, description="Пошаговое описание рецепта", examples=["Сварите бульон..."])
class RecipeListResponse(BaseModel):
    title: str = Field(..., description="Название блюда")
    views: int = Field(..., description="Количество просмотров")
    cooking_time: int = Field(..., description="Время приготовления (мин)")
    model_config = ConfigDict(from_attributes=True)
class RecipeDetailResponse(BaseModel):
    title: str = Field(..., description="Название блюда")
    cooking_time: int = Field(..., description="Время приготовления (мин)")
    ingredients: List[str] = Field(..., description="Список ингредиентов")
    description: str = Field(..., description="Полное текстовое описание")
    model_config = ConfigDict(from_attributes=True)