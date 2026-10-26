from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import sqlalchemy as sa
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from .configuration import load_seed_recipes
from .db import (
    Ingredient,
    Instruction,
    Recipe,
    close_engine,
    create_engine,
    create_session_factory,
    initialize_database,
)

if TYPE_CHECKING:
    from sqlalchemy.engine.result import Result
    from sqlalchemy.ext.asyncio.engine import AsyncEngine
    from sqlalchemy.ext.asyncio.session import async_sessionmaker


class RecipeSummary(BaseModel):
    id: int
    name: str


class RecipeResponse(RecipeSummary):
    description: str | None
    ingredients: list[str]
    instructions: list[str]


async def list_recipes(session: AsyncSession) -> list[RecipeSummary]:
    result = await session.execute(sa.select(Recipe).order_by(Recipe.id))
    return [
        RecipeSummary(id=recipe.id, name=recipe.name) for recipe in result.scalars()
    ]


async def get_recipe(session: AsyncSession, recipe_id: int) -> RecipeResponse:
    recipe: Recipe | None = await session.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found"
        )

    ingredients_result: Result[str] = await session.execute(
        sa.select(Ingredient.name)
        .where(Ingredient.recipe_id == recipe_id)
        .order_by(Ingredient.name)
    )
    instructions_result = await session.execute(
        sa.select(Instruction.text)
        .where(Instruction.recipe_id == recipe_id)
        .order_by(Instruction.step_number)
    )
    return RecipeResponse(
        id=recipe.id,
        name=recipe.name,
        description=recipe.description,
        ingredients=list(ingredients_result.scalars()),
        instructions=list(instructions_result.scalars()),
    )


def build_app(db_path: Path) -> FastAPI:
    engine: AsyncEngine = create_engine(db_path)
    session_factory: async_sessionmaker[AsyncSession] = create_session_factory(engine)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        await initialize_database(engine, load_seed_recipes())
        yield
        await close_engine(engine)

    app = FastAPI(title="Recipe API", lifespan=lifespan)

    async def session_dependency() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    @app.get("/api/recipes", response_model=list[RecipeSummary])
    async def recipes(
        session: Annotated[AsyncSession, Depends(session_dependency)],
    ) -> list[RecipeSummary]:
        return await list_recipes(session)

    @app.get("/api/recipes/{recipe_id}", response_model=RecipeResponse)
    async def recipe(
        recipe_id: int,
        session: Annotated[AsyncSession, Depends(session_dependency)],
    ) -> RecipeResponse:
        return await get_recipe(session, recipe_id)

    frontend_dir = Path(__file__).resolve().parents[1] / "dist"
    if frontend_dir.is_dir():
        app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

    return app


def create_app() -> FastAPI:
    runtime_dir = Path(".data")
    runtime_dir.mkdir(parents=True, exist_ok=True)
    return build_app(runtime_dir / "recipes.db")


app = create_app()
