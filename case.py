"""
Case module for the CSGO Case Clicker game.
Defines cases that can be opened to obtain items.
"""
import random
from dataclasses import dataclass, field
from typing import List
from item import Item, Rarity, Condition


@dataclass
class Case:
    """Represents a case that can be opened to get random items."""
    name: str
    price: float
    possible_items: List[Item] = field(default_factory=list)
    
    def add_item(self, item: Item) -> None:
        """Add an item to the case's loot pool."""
        self.possible_items.append(item)
    
    def open(self) -> Item:
        """
        Open the case and return a random item based on rarity probabilities.
        Returns a copy of the item with randomized condition and StatTrak status.
        """
        if not self.possible_items:
            raise ValueError("Cannot open an empty case")
        
        # Calculate total drop rate
        total_rate = sum(item.rarity.drop_rate for item in self.possible_items)
        
        # Normalize probabilities
        rand_value = random.random() * total_rate
        
        # Select item based on probability
        cumulative = 0
        selected_item = None
        for item in self.possible_items:
            cumulative += item.rarity.drop_rate
            if rand_value <= cumulative:
                selected_item = item
                break
        
        # Fallback to last item if none selected (shouldn't happen)
        if selected_item is None:
            selected_item = self.possible_items[-1]
        
        # Create a copy with random condition and StatTrak
        return self._randomize_item(selected_item)
    
    def _randomize_item(self, item: Item) -> Item:
        """Create a copy of an item with randomized attributes."""
        # 10% chance for StatTrak
        stat_trak = random.random() < 0.1
        
        # Random condition (if item supports it)
        condition = None
        if item.category not in ["Sticker", "Case"]:
            condition = random.choice(list(Condition))
        
        # Create new item instance
        return Item(
            name=item.name,
            rarity=item.rarity,
            category=item.category,
            base_value=item.base_value,
            condition=condition,
            stat_trak=stat_trak
        )
    
    def __str__(self) -> str:
        """String representation of the case."""
        return f"{self.name} (${self.price})"
