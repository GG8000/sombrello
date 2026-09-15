import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    buildings_path: str
    trees_path: str


def get_settings() -> Settings:
    """
    Reads dataset paths from environment variables, falling back to
    sensible local-dev defaults. Set SOMBRELLO_BUILDINGS_PATH /
    SOMBRELLO_TREES_PATH in your environment (or a .env file) to
    override for different machines/deployments.
    """
    return Settings(
        buildings_path=os.environ.get("SOMBRELLO_BUILDINGS_PATH", "data/buildings.gpkg"),
        trees_path=os.environ.get("SOMBRELLO_TREES_PATH", "data/trees.gpkg"),
    )