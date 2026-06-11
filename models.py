from sqlalchemy import String, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, info={"description": "Название блюда"})
    cooking_time: Mapped[int] = mapped_column(Integer, nullable=False, info={"description": "Время приготовления в минутах"})
    views: Mapped[int] = mapped_column(Integer, default=0, info={"description": "Количество просмотров детальной страницы"})
    ingredients: Mapped[list] = mapped_column(JSON, nullable=False, info={"description": "Список ингредиентов"})
    description: Mapped[str] = mapped_column(String(1000), nullable=False, info={"description": "Текстовое описание рецепта"})