"""Examples of integrating the service container with the recipe API."""
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from .context import AppContext
from .db import create_engine, create_session_factory
from .dependencies import ServiceContainer, create_fastapi_dependency
from .main import RecipeResponse, get_recipe, list_recipes

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker


class RecipeService:
    """Small service wrapper used by the dependency-injection examples."""

    def __init__(self, engine: AsyncEngine):
        self.session_factory: async_sessionmaker[AsyncSession] = create_session_factory(engine)

    async def get_all_recipes(self):
        async with self.session_factory() as session:
            return await list_recipes(session)

    async def get_recipe_by_id(self, recipe_id: int) -> RecipeResponse:
        async with self.session_factory() as session:
            return await get_recipe(session, recipe_id)


class DatabaseModule:
    """Register database services in the container."""

    @staticmethod
    def configure(container: ServiceContainer, app_context: AppContext) -> None:
        container.register(AsyncEngine).singleton(create_engine(app_context.db_path))


class ServiceModule:
    """Register business services in the container."""

    @staticmethod
    def configure(container: ServiceContainer) -> None:
        container.register(RecipeService).transient()


def create_app_with_manual_di(app_context: AppContext) -> FastAPI:
    """Create a FastAPI app using the custom container for service resolution."""
    container = ServiceContainer()
    DatabaseModule.configure(container, app_context)
    ServiceModule.configure(container)
    service_dependency = create_fastapi_dependency(container, RecipeService)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        await container.resolve(AsyncEngine).dispose()

    app = FastAPI(lifespan=lifespan)
    app.state.container = container

    @app.get("/recipes")
    async def list_recipes_route(
        service: RecipeService = Depends(service_dependency),  # noqa: B008
    ):
        return await service.get_all_recipes()

    @app.get("/recipe/{recipe_id}")
    async def get_recipe_route(
        recipe_id: int,
        service: RecipeService = Depends(service_dependency),  # noqa: B008
    ):
        return await service.get_recipe_by_id(recipe_id)

    return app


class DIFactory:
    """Factory for creating and resetting a configured container."""

    _container: ServiceContainer | None = None

    @classmethod
    def get_container(cls) -> ServiceContainer:
        if cls._container is None:
            cls._container = ServiceContainer()
        return cls._container

    @classmethod
    def initialize(cls, app_context: AppContext) -> ServiceContainer:
        container = cls.get_container()
        container.clear_singletons()
        DatabaseModule.configure(container, app_context)
        ServiceModule.configure(container)
        return container

    @classmethod
    def reset(cls) -> None:
        if cls._container is not None:
            cls._container.clear_singletons()
        cls._container = None


def get_recipe_service(container: ServiceContainer) -> RecipeService:
    """Resolve the recipe service from a configured container."""
    return container.resolve(RecipeService)


class RequestDIScope:
    """Manage request-scoped dependencies."""

    def __init__(self, container: ServiceContainer, request_id: int):
        self.container = container
        self.request_id = request_id

    def __enter__(self):
        return self.container.get_request_context(self.request_id)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.container.clear_request_context(self.request_id)


class ConfigurableRecipeService:
    """Example service that accepts configuration."""

    def __init__(self, engine: AsyncEngine, cache_enabled: bool = True):
        self.engine = engine
        self.cache_enabled = cache_enabled
        self._cache: dict[str, object] | None = {} if cache_enabled else None

    def get_all_recipes(self):
        if self.cache_enabled and self._cache is not None:
            return self._cache.setdefault("recipes", [])
        return []


def configure_dependent_services(
    container: ServiceContainer,
    app_context: AppContext,
) -> None:
    """Register services whose factories depend on the database engine."""
    container.register(AsyncEngine).singleton(create_engine(app_context.db_path))
    container.register(ConfigurableRecipeService).transient(
        lambda engine: ConfigurableRecipeService(engine, cache_enabled=True)
    )
