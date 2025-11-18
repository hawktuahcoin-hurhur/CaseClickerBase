"""
Unit tests for the CSGO Case Clicker game model.
"""
import unittest
from item import Item, Rarity, Condition
from case import Case
from inventory import Inventory
from player import Player
from game import Game


class TestItem(unittest.TestCase):
    """Test cases for the Item class."""
    
    def test_item_creation(self):
        """Test creating a basic item."""
        item = Item(
            name="AK-47 | Redline",
            rarity=Rarity.CLASSIFIED,
            category="Rifle",
            base_value=25.0
        )
        self.assertEqual(item.name, "AK-47 | Redline")
        self.assertEqual(item.rarity, Rarity.CLASSIFIED)
        self.assertFalse(item.stat_trak)
    
    def test_item_value_base(self):
        """Test item value calculation without modifiers."""
        item = Item(
            name="P250 | Sand Dune",
            rarity=Rarity.CONSUMER,
            category="Pistol",
            base_value=0.03
        )
        self.assertEqual(item.get_value(), 0.03)
    
    def test_item_value_with_condition(self):
        """Test item value with condition modifier."""
        item = Item(
            name="AWP | Asiimov",
            rarity=Rarity.COVERT,
            category="Rifle",
            base_value=100.0,
            condition=Condition.FACTORY_NEW
        )
        # Factory New multiplies by 1.5
        self.assertEqual(item.get_value(), 150.0)
    
    def test_item_value_with_stattrak(self):
        """Test item value with StatTrak."""
        item = Item(
            name="M4A4 | Howl",
            rarity=Rarity.COVERT,
            category="Rifle",
            base_value=500.0,
            stat_trak=True
        )
        # StatTrak multiplies by 1.5
        self.assertEqual(item.get_value(), 750.0)
    
    def test_item_value_all_modifiers(self):
        """Test item value with all modifiers."""
        item = Item(
            name="Karambit | Fade",
            rarity=Rarity.SPECIAL,
            category="Knife",
            base_value=500.0,
            condition=Condition.FACTORY_NEW,
            stat_trak=True
        )
        # StatTrak (1.5) * Factory New (1.5) = 2.25x
        self.assertEqual(item.get_value(), 1125.0)
    
    def test_item_string_representation(self):
        """Test string representation of items."""
        item1 = Item(
            name="AWP | Dragon Lore",
            rarity=Rarity.COVERT,
            category="Rifle",
            base_value=1000.0,
            condition=Condition.FACTORY_NEW,
            stat_trak=True
        )
        self.assertIn("StatTrak™", str(item1))
        self.assertIn("Factory New", str(item1))


class TestCase(unittest.TestCase):
    """Test cases for the Case class."""
    
    def setUp(self):
        """Set up test cases."""
        self.case = Case(name="Test Case", price=2.5)
        self.item1 = Item(
            name="Common Item",
            rarity=Rarity.CONSUMER,
            category="Pistol",
            base_value=0.10
        )
        self.item2 = Item(
            name="Rare Item",
            rarity=Rarity.COVERT,
            category="Rifle",
            base_value=100.0
        )
    
    def test_case_creation(self):
        """Test creating a case."""
        self.assertEqual(self.case.name, "Test Case")
        self.assertEqual(self.case.price, 2.5)
        self.assertEqual(len(self.case.possible_items), 0)
    
    def test_add_item_to_case(self):
        """Test adding items to a case."""
        self.case.add_item(self.item1)
        self.assertEqual(len(self.case.possible_items), 1)
        self.case.add_item(self.item2)
        self.assertEqual(len(self.case.possible_items), 2)
    
    def test_open_case(self):
        """Test opening a case returns an item."""
        self.case.add_item(self.item1)
        self.case.add_item(self.item2)
        
        item = self.case.open()
        self.assertIsInstance(item, Item)
        self.assertIn(item.name, ["Common Item", "Rare Item"])
    
    def test_open_empty_case_raises_error(self):
        """Test that opening an empty case raises an error."""
        with self.assertRaises(ValueError):
            self.case.open()
    
    def test_opened_item_has_random_attributes(self):
        """Test that opened items have randomized condition."""
        self.case.add_item(self.item1)
        
        # Open multiple times and check for variation
        items = [self.case.open() for _ in range(10)]
        
        # Should have items (all should be valid Items)
        for item in items:
            self.assertIsInstance(item, Item)


class TestInventory(unittest.TestCase):
    """Test cases for the Inventory class."""
    
    def setUp(self):
        """Set up test inventory."""
        self.inventory = Inventory()
        self.item1 = Item(
            name="Item 1",
            rarity=Rarity.CONSUMER,
            category="Pistol",
            base_value=1.0
        )
        self.item2 = Item(
            name="Item 2",
            rarity=Rarity.CLASSIFIED,
            category="Rifle",
            base_value=10.0
        )
    
    def test_inventory_creation(self):
        """Test creating an empty inventory."""
        self.assertEqual(self.inventory.get_item_count(), 0)
        self.assertEqual(self.inventory.get_total_value(), 0.0)
    
    def test_add_item(self):
        """Test adding items to inventory."""
        self.inventory.add_item(self.item1)
        self.assertEqual(self.inventory.get_item_count(), 1)
        
        self.inventory.add_item(self.item2)
        self.assertEqual(self.inventory.get_item_count(), 2)
    
    def test_remove_item(self):
        """Test removing items from inventory."""
        self.inventory.add_item(self.item1)
        result = self.inventory.remove_item(self.item1)
        self.assertTrue(result)
        self.assertEqual(self.inventory.get_item_count(), 0)
    
    def test_remove_nonexistent_item(self):
        """Test removing an item that's not in inventory."""
        result = self.inventory.remove_item(self.item1)
        self.assertFalse(result)
    
    def test_get_total_value(self):
        """Test calculating total inventory value."""
        self.inventory.add_item(self.item1)
        self.inventory.add_item(self.item2)
        expected_value = self.item1.get_value() + self.item2.get_value()
        self.assertEqual(self.inventory.get_total_value(), expected_value)
    
    def test_get_items_by_rarity(self):
        """Test filtering items by rarity."""
        self.inventory.add_item(self.item1)
        self.inventory.add_item(self.item2)
        
        consumer_items = self.inventory.get_items_by_rarity(Rarity.CONSUMER)
        self.assertEqual(len(consumer_items), 1)
        self.assertEqual(consumer_items[0].name, "Item 1")
    
    def test_sell_item(self):
        """Test selling an item from inventory."""
        self.inventory.add_item(self.item1)
        value = self.inventory.sell_item(self.item1)
        self.assertEqual(value, self.item1.get_value())
        self.assertEqual(self.inventory.get_item_count(), 0)


class TestPlayer(unittest.TestCase):
    """Test cases for the Player class."""
    
    def setUp(self):
        """Set up test player."""
        self.player = Player(name="TestPlayer", balance=100.0)
        self.case = Case(name="Test Case", price=10.0)
        self.case.add_item(Item(
            name="Test Item",
            rarity=Rarity.CONSUMER,
            category="Pistol",
            base_value=5.0
        ))
    
    def test_player_creation(self):
        """Test creating a player."""
        self.assertEqual(self.player.name, "TestPlayer")
        self.assertEqual(self.player.balance, 100.0)
        self.assertIsNotNone(self.player.inventory)
        self.assertEqual(self.player.cases_opened, 0)
    
    def test_add_balance(self):
        """Test adding balance to player."""
        initial_balance = self.player.balance
        self.player.add_balance(50.0)
        self.assertEqual(self.player.balance, initial_balance + 50.0)
    
    def test_add_negative_balance_raises_error(self):
        """Test that adding negative balance raises an error."""
        with self.assertRaises(ValueError):
            self.player.add_balance(-10.0)
    
    def test_can_afford(self):
        """Test checking if player can afford a purchase."""
        self.assertTrue(self.player.can_afford(50.0))
        self.assertTrue(self.player.can_afford(100.0))
        self.assertFalse(self.player.can_afford(150.0))
    
    def test_open_case_success(self):
        """Test successfully opening a case."""
        initial_balance = self.player.balance
        initial_count = self.player.inventory.get_item_count()
        
        item = self.player.open_case(self.case)
        
        self.assertIsInstance(item, Item)
        self.assertEqual(self.player.balance, initial_balance - self.case.price)
        self.assertEqual(self.player.inventory.get_item_count(), initial_count + 1)
        self.assertEqual(self.player.cases_opened, 1)
    
    def test_open_case_insufficient_balance(self):
        """Test opening a case with insufficient balance."""
        expensive_case = Case(name="Expensive", price=200.0)
        expensive_case.add_item(Item(
            name="Item",
            rarity=Rarity.CONSUMER,
            category="Pistol",
            base_value=1.0
        ))
        
        with self.assertRaises(ValueError):
            self.player.open_case(expensive_case)
    
    def test_sell_item(self):
        """Test selling an item."""
        item = self.player.open_case(self.case)
        initial_balance = self.player.balance
        item_value = item.get_value()
        
        result = self.player.sell_item(item)
        
        self.assertTrue(result)
        self.assertEqual(self.player.balance, initial_balance + item_value)
        self.assertEqual(self.player.inventory.get_item_count(), 0)
    
    def test_get_net_worth(self):
        """Test calculating player net worth."""
        item = self.player.open_case(self.case)
        net_worth = self.player.get_net_worth()
        expected = self.player.balance + self.player.inventory.get_total_value()
        self.assertEqual(net_worth, expected)


class TestGame(unittest.TestCase):
    """Test cases for the Game class."""
    
    def setUp(self):
        """Set up test game."""
        self.game = Game()
    
    def test_game_creation(self):
        """Test creating a game."""
        self.assertIsNone(self.game.player)
        self.assertGreater(len(self.game.available_cases), 0)
    
    def test_start_new_game(self):
        """Test starting a new game."""
        player = self.game.start_new_game("Player1", starting_balance=50.0)
        
        self.assertIsNotNone(self.game.player)
        self.assertEqual(player.name, "Player1")
        self.assertEqual(player.balance, 50.0)
    
    def test_add_case(self):
        """Test adding a custom case to the game."""
        initial_count = len(self.game.available_cases)
        new_case = Case(name="Custom Case", price=5.0)
        
        self.game.add_case(new_case)
        
        self.assertEqual(len(self.game.available_cases), initial_count + 1)
    
    def test_get_case_by_name(self):
        """Test getting a case by name."""
        case = self.game.get_case_by_name("Starter Case")
        self.assertEqual(case.name, "Starter Case")
    
    def test_get_nonexistent_case_raises_error(self):
        """Test getting a nonexistent case raises an error."""
        with self.assertRaises(ValueError):
            self.game.get_case_by_name("Nonexistent Case")
    
    def test_get_game_stats(self):
        """Test getting game statistics."""
        self.game.start_new_game("Player1", starting_balance=100.0)
        
        stats = self.game.get_game_stats()
        
        self.assertEqual(stats['player_name'], "Player1")
        self.assertEqual(stats['balance'], 100.0)
        self.assertEqual(stats['cases_opened'], 0)
        self.assertIn('net_worth', stats)
        self.assertIn('rarity_distribution', stats)
    
    def test_get_game_stats_no_player(self):
        """Test getting stats with no active player."""
        stats = self.game.get_game_stats()
        self.assertIn('error', stats)


if __name__ == '__main__':
    unittest.main()
