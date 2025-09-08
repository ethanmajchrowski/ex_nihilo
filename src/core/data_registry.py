from json import load
from os import listdir
from dataclasses import dataclass
from logger import logger

@dataclass
class Recipe:
    id: str
    name: str
    inputs: dict[str, int]
    outputs: dict[str, int]
    required_capabilities: list[str]
    duration: float
    
    def __hash__(self):
        return 0

class _DataRegistry:
    def __init__(self) -> None:
        self.recipes: dict[str, Recipe] = self.load_recipes()
        self.machines: dict[str, dict] = self.load_data("machines")
        self.transfer_links: dict[str, dict] = self.load_data("transfer_links")
        self.resource_nodes: dict[str, dict] = self.load_data("resource_nodes")

    def load_data(self, data_type):
        data = {}
        all_data = listdir(f"src/data/{data_type}/")
        for file in all_data:
            if file in data and data_type == "machine":
                logger.warning(f"{data_type} in machine already exists, skipping {file}")
                continue
            if file in data and data_type == "transfer_link":
                logger.warning(f"{data_type} in transfer_links already exists, skipping {file}")
                continue
            
            with open(f"src/data/{data_type}/{file}") as f:
                json = load(f)
                data[file[:-5]] = json
                logger.info(f"Loaded {data_type} data for {file[:-5]}")
        return data
    
    def load_recipes(self):
        recipes = {}
        all_recipes = listdir("src/data/recipes/")
        for recipe in all_recipes:
            with open(f"src/data/recipes/{recipe}") as f:
                json = load(f)
                r = Recipe(json["id"], json["name"], json["inputs"], json["outputs"], json["required_capabilities"], json["duration"])
                recipes[r.id] = r
        return recipes
    
    def get_compatible_recipes(self, capabilities: list[str]):
        return [r for r in self.recipes.values() if all(c in r.required_capabilities for c in capabilities)]

data_registry = _DataRegistry()