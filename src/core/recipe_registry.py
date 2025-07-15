from json import load
from os import listdir
from dataclasses import dataclass

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
    

class _RecipeRegistry:
    def __init__(self) -> None:
        self.recipes = self.load_recipes()
    
    def load_recipes(self):
        recipes = set()
        all_recipes = listdir("src/data/recipes/")
        for recipe in all_recipes:
            with open(f"src/data/recipes/{recipe}") as f:
                json = load(f)
                r = Recipe(json["id"], json["name"], json["inputs"], json["outputs"], json["required_capabilities"], json["duration"])
                recipes.add(r)
        return recipes
    
    def get_compatible_recipes(self, capabilities: list[str]):
        return [r for r in self.recipes if all(c in r.required_capabilities for c in capabilities)]

recipe_registry = _RecipeRegistry()