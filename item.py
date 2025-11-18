"""
Item module for the CSGO Case Clicker game.
Defines items that can be obtained from cases.
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class Rarity(Enum):
    """Item rarity levels, from most common to rarest."""
    CONSUMER = ("Consumer Grade", "white", 0.7992)
    INDUSTRIAL = ("Industrial Grade", "light_blue", 0.1598)
    MIL_SPEC = ("Mil-Spec", "blue", 0.032)
    RESTRICTED = ("Restricted", "purple", 0.0064)
    CLASSIFIED = ("Classified", "pink", 0.00128)
    COVERT = ("Covert", "red", 0.00026)
    SPECIAL = ("Special", "gold", 0.00026)  # Knives, gloves, etc.
    
    def __init__(self, display_name: str, color: str, drop_rate: float):
        self.display_name = display_name
        self.color = color
        self.drop_rate = drop_rate


class Condition(Enum):
    """Item wear conditions."""
    FACTORY_NEW = "Factory New"
    MINIMAL_WEAR = "Minimal Wear"
    FIELD_TESTED = "Field-Tested"
    WELL_WORN = "Well-Worn"
    BATTLE_SCARRED = "Battle-Scarred"


@dataclass
class Item:
    """Represents an in-game item (skin, weapon, knife, etc.)."""
    name: str
    rarity: Rarity
    category: str  # e.g., "Rifle", "Pistol", "Knife", "Glove"
    base_value: float  # Base market value
    condition: Optional[Condition] = None
    stat_trak: bool = False
    
    def get_value(self) -> float:
        """Calculate the current value of the item."""
        value = self.base_value
        
        # StatTrak items are worth more
        if self.stat_trak:
            value *= 1.5
        
        # Condition affects value
        if self.condition:
            condition_multipliers = {
                Condition.FACTORY_NEW: 1.5,
                Condition.MINIMAL_WEAR: 1.2,
                Condition.FIELD_TESTED: 1.0,
                Condition.WELL_WORN: 0.7,
                Condition.BATTLE_SCARRED: 0.5,
            }
            value *= condition_multipliers[self.condition]
        
        return round(value, 2)
    
    def __str__(self) -> str:
        """String representation of the item."""
        parts = []
        if self.stat_trak:
            parts.append("StatTrak™")
        parts.append(self.name)
        if self.condition:
            parts.append(f"({self.condition.value})")
        return " ".join(parts)
