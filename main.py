from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from contextlib import asynccontextmanager

from database import engine, Base, get_db
import models
import schemas

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="Cookbook API",
    description="API для кулинарной книги с сортировкой по популярности. Идеально для интеграции с фронтендом.",
    version="1.0.0",
    lifespan=lifespan
)


@app.get(
    "/recipes",
    response_model=List[schemas.RecipeListResponse],
    summary="Получить список всех рецептов (Экран 1)",
    description="Возвращает список рецептов, отсортированных по количеству просмотров (от самых популярных). Если просмотры равны, сортирует по времени приготовления."
)
async def get_recipes(db: AsyncSession = Depends(get_db)):
    query = select(models.Recipe).order_by(models.Recipe.views.desc(), models.Recipe.cooking_time.asc())
    result = await db.execute(query)
    recipes = result.scalars().all()
    return recipes
@app.get(
    "/recipes/{recipe_id}",
    response_model=schemas.RecipeDetailResponse,
    summary="Получить детальную информацию о рецепте (Экран 2)",
    description="Возвращает подробные данные рецепта и увеличивает счетчик просмотров на 1."
)
async def get_recipe_detail(recipe_id: int, db: AsyncSession = Depends(get_db)):
    query = select(models.Recipe).where(models.Recipe.id == recipe_id)
    result = await db.execute(query)
    recipe = result.scalar_one_or_none()
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецепт не найден")

    recipe.views += 1
    
    await db.commit()
    await db.refresh(recipe)
    return recipe
@app.post(
    "/recipes",
    response_model=schemas.RecipeDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый рецепт",
    description="Добавляет новый рецепт в базу данных. Счетчик просмотров изначально равен 0."
)
async def create_recipe(recipe_data: schemas.RecipeCreate, db: AsyncSession = Depends(get_db)):
    new_recipe = models.Recipe(**recipe_data.model_dump())
    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe)
    return new_recipe