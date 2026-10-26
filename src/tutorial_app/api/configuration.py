import json
import os
from configparser import ConfigParser
from pathlib import Path
from typing import TypedDict

CONFIG_DIR: Path = Path(__file__).with_name("config")


class RecipeSeed(TypedDict):
    name: str
    description: str | None
    ingredients: list[str]
    instructions: list[str]


def load_config(environment: str | None = None) -> ConfigParser:
    selected_environment: str = (
        environment or os.getenv("APP_ENVIRONMENT") or os.getenv("APP_ENV") or "dev"
    ).lower()
    config = ConfigParser()
    config_files: list[Path] = [
        CONFIG_DIR / "base.ini",
        CONFIG_DIR / f"{selected_environment}.ini",
    ]
    if len(config.read(config_files)) != len(config_files):
        message = f"Unknown configuration environment: {selected_environment}"
        raise FileNotFoundError(message)
    return config


def load_seed_recipes(config: ConfigParser | None = None) -> dict[int, RecipeSeed]:
    config = config or load_config()
    recipes_file: Path = CONFIG_DIR / config.get("app", "recipes_file")
    with recipes_file.open() as file:
        raw_recipes = json.load(file)
    return {int(recipe_id): recipe for recipe_id, recipe in raw_recipes.items()}
