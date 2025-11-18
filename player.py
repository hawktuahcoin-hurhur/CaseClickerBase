"""
Player module for the CSGO Case Clicker game.
Manages player state including balance and inventory.
"""
from dataclasses import dataclass
from inventory import Inventory
from case import Case
from item import Item


@dataclass
class Player:
    """Represents a player in the game."""
    name: str
    balance: float = 0.0
    inventory: Inventory = None
    cases_opened: int = 0
    
    def __post_init__(self):
        """Initialize the inventory if not provided."""
        if self.inventory is None:
            self.inventory = Inventory()
    
    def add_balance(self, amount: float) -> None:
        """Add money to the player's balance."""
        if amount < 0:
            raise ValueError("Cannot add negative balance")
        self.balance += amount
    
    def can_afford(self, amount: float) -> bool:
        """Check if the player can afford a purchase."""
        return self.balance >= amount
    
    def open_case(self, case: Case) -> Item:
        """
        Open a case if the player can afford it.
        Returns the item obtained from the case.
        Raises ValueError if the player cannot afford the case.
        """
        if not self.can_afford(case.price):
            raise ValueError(f"Insufficient balance. Need ${case.price}, have ${self.balance}")
        
        # Deduct the case price
        self.balance -= case.price
        self.cases_opened += 1
        
        # Open the case and get an item
        item = case.open()
        
        # Add item to inventory
        self.inventory.add_item(item)
        
        return item
    
    def sell_item(self, item: Item) -> bool:
        """
        Sell an item from the inventory and add its value to the balance.
        Returns True if successful, False if the item is not in inventory.
        """
        value = self.inventory.sell_item(item)
        if value > 0:
            self.balance += value
            return True
        return False
    
    def get_net_worth(self) -> float:
        """Calculate the player's total net worth (balance + inventory value)."""
        return self.balance + self.inventory.get_total_value()
    
    def __str__(self) -> str:
        """String representation of the player."""
        return (f"{self.name} - Balance: ${self.balance:.2f} | "
                f"{self.inventory} | Cases Opened: {self.cases_opened}")
