import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    test_engine, expire_on_commit=False, class_=AsyncSession
)


@pytest_asyncio.fixture(autouse=True, loop_scope="function")
async def init_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.mark.asyncio(loop_scope="function")
async def test_cookbook_workflow():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:

        # 1. Создаем первый рецепт
        new_recipe_1 = {
            "title": "Борщ",
            "cooking_time": 60,
            "ingredients": ["Свекла", "Мясо"],
            "description": "Варить до готовности",
        }
        response = await ac.post("/recipes", json=new_recipe_1)
        assert response.status_code == 201

        # 2. Создаем второй рецепт
        new_recipe_2 = {
            "title": "Яичница",
            "cooking_time": 5,
            "ingredients": ["Яйца", "Масло"],
            "description": "Пожарить",
        }
        response = await ac.post("/recipes", json=new_recipe_2)
        assert response.status_code == 201

        # 3. Проверяем список рецептов
        response = await ac.get("/recipes")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Яичница"  # Яичница быстрее, она первая

        # 4. Имитируем просмотр Борща
        response = await ac.get("/recipes/1")
        assert response.status_code == 200
        assert response.json()["title"] == "Борщ"

        # 5. Проверяем сортировку заново
        response = await ac.get("/recipes")
        data = response.json()
        assert data[0]["title"] == "Борщ"
        assert data[0]["views"] == 1
