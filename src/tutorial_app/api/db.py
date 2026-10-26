from collections.abc import AsyncIterator
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .configuration import RecipeSeed, load_seed_recipes


class Base(DeclarativeBase):
    pass


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]


class Ingredient(Base):
    __tablename__ = "ingredients"

    recipe_id: Mapped[int] = mapped_column(
        sa.ForeignKey("recipes.id"), primary_key=True
    )
    name: Mapped[str] = mapped_column(primary_key=True)


class Instruction(Base):
    __tablename__ = "instructions"

    recipe_id: Mapped[int] = mapped_column(
        sa.ForeignKey("recipes.id"), primary_key=True
    )
    step_number: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]


def create_engine(db_path: Path) -> AsyncEngine:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_async_engine(f"sqlite+aiosqlite:///{db_path}")


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


async def initialize_database(
    engine: AsyncEngine, seed_recipes: dict[int, RecipeSeed] | None = None
) -> None:
    seed_recipes: dict[int, RecipeSeed] = seed_recipes or load_seed_recipes()
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        for recipe_id, recipe_data in seed_recipes.items():
            recipe = await session.get(Recipe, recipe_id)
            if recipe is None:
                session.add(
                    Recipe(
                        id=recipe_id,
                        name=recipe_data["name"],
                        description=recipe_data["description"],
                    )
                )
            else:
                recipe.name = recipe_data["name"]
                recipe.description = recipe_data["description"]

            await session.execute(
                sa.delete(Ingredient).where(Ingredient.recipe_id == recipe_id)
            )
            await session.execute(
                sa.delete(Instruction).where(Instruction.recipe_id == recipe_id)
            )
            session.add_all(
                Ingredient(recipe_id=recipe_id, name=name)
                for name in recipe_data["ingredients"]
            )
            session.add_all(
                Instruction(recipe_id=recipe_id, step_number=step, text=text)
                for step, text in enumerate(recipe_data["instructions"], start=1)
            )
        await session.commit()


async def close_engine(engine: AsyncEngine) -> None:
    await engine.dispose()


async def get_session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    async_session = create_session_factory(engine)
    async with async_session() as session:
        yield session
