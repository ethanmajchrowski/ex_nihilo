from collections import defaultdict

class Recipe:
    def __init__(self, input_items: dict[str, int], output_items: dict[str, int], duration: float, machines: list[str]):
        self.inputs = input_items
        self.outputs = output_items
        self.duration = duration
        self.machines = machines

class RecipeDatabase:
    def __init__(self) -> None:
        self.recipes: list[Recipe] = []
        self.by_output: dict[str, list[Recipe]] = defaultdict(list)
        self.by_input: dict[str, list[Recipe]] = defaultdict(list)
        self.by_machine: dict[str, list[Recipe]] = defaultdict(list)

    def register(self, recipe: Recipe):
        self.recipes.append(recipe)
        for item in recipe.outputs:
            self.by_output[item].append(recipe)
        for item in recipe.inputs:
            self.by_input[item].append(recipe)
        for machine in recipe.machines:
            self.by_machine[machine].append(recipe)
    
    def get_recipes_by_output(self, item_name: str):
        return self.by_output.get(item_name, [])
    
    def get_recipes_by_input(self, item_name: str):
        return self.by_input.get(item_name, [])

    def get_recipes_by_machine(self, machine_name: str):
        return self.by_machine.get(machine_name, [])

    def get_all_recipes(self):
        return self.recipes

def setup_recipes() -> RecipeDatabase:
    RECIPE_DB = RecipeDatabase()
    
    RECIPE_DB.register(Recipe(input_items={"stone": 1}, output_items={"gravel": 1}, duration=0.5, machines=["Rock Crusher"]))
    RECIPE_DB.register(Recipe(input_items={}, output_items={"stone": 1}, duration=1.0, machines=["Mineshaft"]))
    
    return RECIPE_DB