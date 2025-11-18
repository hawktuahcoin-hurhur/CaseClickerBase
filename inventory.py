"""
Inventory module for the CSGO Case Clicker game.
Manages player's items and currency.
"""
from dataclasses import dataclass, field
from typing import List, Dict
from item import Item, Rarity


@dataclass
class Inventory:
    """Manages the player's collection of items."""
    items: List[Item] = field(default_factory=list)
    
    def add_item(self, item: Item) -> None:
        """Add an item to the inventory."""
        self.items.append(item)
    
    def remove_item(self, item: Item) -> bool:
        """Remove an item from the inventory. Returns True if successful."""
        if item in self.items:
            self.items.remove(item)
            return True
        return False
    
    def get_total_value(self) -> float:
        """Calculate the total value of all items in the inventory."""
        return sum(item.get_value() for item in self.items)
    
    def get_items_by_rarity(self, rarity: Rarity) -> List[Item]:
        """Get all items of a specific rarity."""
        return [item for item in self.items if item.rarity == rarity]
    
    def get_item_count(self) -> int:
        """Get the total number of items in the inventory."""
        return len(self.items)
    
    def get_rarity_distribution(self) -> Dict[Rarity, int]:
        """Get the count of items for each rarity level."""
        distribution = {rarity: 0 for rarity in Rarity}
        for item in self.items:
            distribution[item.rarity] += 1
        return distribution
    
    def sell_item(self, item: Item) -> float:
        """
        Sell an item from the inventory and return its value.
        Returns 0 if the item is not in the inventory.
        """
        if self.remove_item(item):
            return item.get_value()
        return 0.0
    
    def __str__(self) -> str:
        """String representation of the inventory."""
        return f"Inventory: {self.get_item_count()} items (${self.get_total_value():.2f})"
