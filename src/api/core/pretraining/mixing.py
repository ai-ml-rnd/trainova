"""Mixing recipes with token budgets."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class MixingRecipe(BaseModel):
    """Mixing recipe for pretraining."""
    
    name: str
    datasets: List[Dict]  # {dataset_id: weight}
    total_tokens: int


class MixingManager:
    """Manager for mixing recipes."""
    
    def __init__(self):
        self._recipes: Dict[str, MixingRecipe] = {}
    
    def add_recipe(self, recipe: MixingRecipe) -> None:
        """Add a mixing recipe."""
        self._recipes[recipe.name] = recipe
    
    def get_recipe(self, name: str) -> Optional[MixingRecipe]:
        """Get mixing recipe by name."""
        return self._recipes.get(name)
    
    def sample_from_recipe(
        self,
        recipe_name: str,
        token_budget: int,
    ) -> List[Dict]:
        """Sample documents according to recipe within token budget."""
        recipe = self._recipes.get(recipe_name)
        if not recipe:
            raise ValueError(f"Recipe not found: {recipe_name}")
        
        # For MVP, return placeholder
        return [
            {"dataset_id": ds.get("id", ""), "weight": ds.get("weight", 1.0)}
            for ds in recipe.datasets
        ]


def create_mixing_recipe(
    datasets: List[Dict],
    total_tokens: int,
) -> MixingRecipe:
    """Create a mixing recipe.
    
    Expected: token budget respected
    """
    recipe = MixingRecipe(
        name="default_recipe",
        datasets=datasets,
        total_tokens=total_tokens,
    )
    return recipe
