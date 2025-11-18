"""
Game module for the CSGO Case Clicker game.
Main game controller and state management.
"""
from typing import List, Dict
from player import Player
from case import Case
from item import Item, Rarity, Condition


class Game:
    """Main game controller for the CSGO Case Clicker."""
    
    def __init__(self):
        """Initialize the game with default settings."""
        self.player: Player = None
        self.available_cases: List[Case] = []
        self._setup_default_cases()
    
    def start_new_game(self, player_name: str, starting_balance: float = 100.0) -> Player:
        """Start a new game with a new player."""
        self.player = Player(name=player_name, balance=starting_balance)
        return self.player
    
    def add_case(self, case: Case) -> None:
        """Add a case to the available cases."""
        self.available_cases.append(case)
    
    def get_case_by_name(self, name: str) -> Case:
        """Get a case by its name."""
        for case in self.available_cases:
            if case.name == name:
                return case
        raise ValueError(f"Case '{name}' not found")
    
    def _setup_default_cases(self) -> None:
        """Set up some default cases with items."""
        # Create a starter case
        starter_case = Case(name="Starter Case", price=2.5)
        
        # Add common items
        starter_case.add_item(Item(
            name="P250 | Sand Dune",
            rarity=Rarity.CONSUMER,
            category="Pistol",
            base_value=0.03
        ))
        starter_case.add_item(Item(
            name="MP9 | Sand Dashed",
            rarity=Rarity.CONSUMER,
            category="SMG",
            base_value=0.04
        ))
        
        # Add uncommon items
        starter_case.add_item(Item(
            name="M4A4 | Desert-Strike",
            rarity=Rarity.INDUSTRIAL,
            category="Rifle",
            base_value=0.15
        ))
        starter_case.add_item(Item(
            name="AK-47 | Safari Mesh",
            rarity=Rarity.INDUSTRIAL,
            category="Rifle",
            base_value=0.20
        ))
        
        # Add rare items
        starter_case.add_item(Item(
            name="AWP | Worm God",
            rarity=Rarity.MIL_SPEC,
            category="Rifle",
            base_value=1.50
        ))
        starter_case.add_item(Item(
            name="M4A1-S | Bright Water",
            rarity=Rarity.RESTRICTED,
            category="Rifle",
            base_value=5.00
        ))
        
        # Add very rare items
        starter_case.add_item(Item(
            name="AK-47 | Redline",
            rarity=Rarity.CLASSIFIED,
            category="Rifle",
            base_value=25.00
        ))
        starter_case.add_item(Item(
            name="AWP | Asiimov",
            rarity=Rarity.COVERT,
            category="Rifle",
            base_value=100.00
        ))
        
        # Add special item (knife)
        starter_case.add_item(Item(
            name="★ Karambit | Fade",
            rarity=Rarity.SPECIAL,
            category="Knife",
            base_value=500.00
        ))
        
        self.available_cases.append(starter_case)
        
        # Create a premium case
        premium_case = Case(name="Premium Case", price=10.0)
        
        premium_case.add_item(Item(
            name="Glock-18 | Dragon Tattoo",
            rarity=Rarity.RESTRICTED,
            category="Pistol",
            base_value=3.00
        ))
        premium_case.add_item(Item(
            name="M4A4 | Howl",
            rarity=Rarity.COVERT,
            category="Rifle",
            base_value=500.00
        ))
        premium_case.add_item(Item(
            name="★ Butterfly Knife | Tiger Tooth",
            rarity=Rarity.SPECIAL,
            category="Knife",
            base_value=1000.00
        ))
        
        self.available_cases.append(premium_case)
    
    def get_game_stats(self) -> Dict:
        """Get current game statistics."""
        if not self.player:
            return {"error": "No active game"}
        
        return {
            "player_name": self.player.name,
            "balance": self.player.balance,
            "net_worth": self.player.get_net_worth(),
            "cases_opened": self.player.cases_opened,
            "items_owned": self.player.inventory.get_item_count(),
            "inventory_value": self.player.inventory.get_total_value(),
            "rarity_distribution": {
                rarity.display_name: count 
                for rarity, count in self.player.inventory.get_rarity_distribution().items()
            }
        }
    
    def __str__(self) -> str:
        """String representation of the game state."""
        if not self.player:
            return "Game: No active player"
        return f"Game: {self.player}"
