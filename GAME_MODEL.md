# CSGO Case Clicker Game Model

A Python-based game model inspired by CSGO case opening mechanics. This project provides a complete object-oriented framework for simulating the case opening experience from Counter-Strike: Global Offensive.

## Features

- **Item System**: Complete item model with rarities, conditions, and StatTrak™ support
- **Case Opening**: Probability-based item drops with realistic rarity distributions
- **Inventory Management**: Track and manage collected items
- **Player System**: Balance management and game progression tracking
- **Game Controller**: Orchestrate the overall game flow and state

## Game Model Components

### 1. Items (`item.py`)

Items represent in-game skins, weapons, and collectibles.

**Rarities** (from common to rare):
- Consumer Grade (79.92% drop rate)
- Industrial Grade (15.98% drop rate)
- Mil-Spec (3.2% drop rate)
- Restricted (0.64% drop rate)
- Classified (0.128% drop rate)
- Covert (0.026% drop rate)
- Special (0.026% drop rate) - Knives and special items

**Item Conditions**:
- Factory New (1.5x value multiplier)
- Minimal Wear (1.2x value multiplier)
- Field-Tested (1.0x value multiplier)
- Well-Worn (0.7x value multiplier)
- Battle-Scarred (0.5x value multiplier)

**Special Features**:
- StatTrak™: Items can have StatTrak (10% chance), which increases value by 1.5x
- Dynamic Valuation: Item value calculated based on base value, condition, and StatTrak status

### 2. Cases (`case.py`)

Cases are containers that hold multiple items with different rarities.

**Features**:
- Configurable item pools
- Probability-based item selection
- Random condition and StatTrak assignment on opening
- Multiple case types with different price points

### 3. Inventory (`inventory.py`)

Manages a player's collection of items.

**Capabilities**:
- Add/remove items
- Calculate total inventory value
- Filter items by rarity
- Track rarity distribution
- Sell items for currency

### 4. Player (`player.py`)

Represents a player in the game.

**Attributes**:
- Name
- Balance (currency)
- Inventory
- Cases opened counter

**Actions**:
- Open cases (if sufficient balance)
- Sell items
- Track net worth (balance + inventory value)

### 5. Game (`game.py`)

Main game controller that manages game state.

**Features**:
- Start new games
- Default case configurations
- Game statistics tracking
- Case management

## Usage

### Basic Example

```python
from game import Game

# Create and start a new game
game = Game()
player = game.start_new_game("PlayerName", starting_balance=100.0)

# Get a case
starter_case = game.get_case_by_name("Starter Case")

# Open the case
item = player.open_case(starter_case)
print(f"Got: {item} - Value: ${item.get_value()}")

# Check game statistics
stats = game.get_game_stats()
print(f"Net Worth: ${stats['net_worth']}")
print(f"Cases Opened: {stats['cases_opened']}")
```

### Running the Demo

```bash
python3 main.py
```

### Running Tests

```bash
python3 test_game.py -v
```

## Game Mechanics

### Case Opening Process

1. Player must have sufficient balance to afford the case price
2. Balance is deducted
3. Random item is selected based on rarity probabilities
4. Item receives random condition and StatTrak status
5. Item is added to player's inventory
6. Case opened counter increments

### Item Valuation

Item value is calculated using:
```
final_value = base_value × condition_multiplier × stattrak_multiplier
```

Where:
- `base_value`: Base market value of the item
- `condition_multiplier`: 0.5x to 1.5x based on wear condition
- `stattrak_multiplier`: 1.5x if StatTrak, 1.0x otherwise

### Probability System

Items are selected based on their rarity's drop rate. The system:
1. Calculates cumulative probabilities for all items in the case
2. Generates a random value
3. Selects the item whose probability range includes the random value

This ensures rare items appear less frequently than common ones, matching the CSGO experience.

## Default Cases

### Starter Case ($2.50)
Contains a mix of common to legendary items including:
- Consumer/Industrial grade items (common)
- Mil-Spec to Classified items (uncommon to rare)
- Covert items like AWP | Asiimov (very rare)
- Special items like Karambit | Fade (extremely rare)

### Premium Case ($10.00)
Contains higher-value items with better odds for rare items.

## Architecture

The game model follows object-oriented design principles:

- **Separation of Concerns**: Each class handles a specific aspect of the game
- **Encapsulation**: Internal state is protected, accessed through methods
- **Composition**: Complex objects (Player, Game) are built from simpler ones (Item, Inventory)
- **Extensibility**: Easy to add new items, cases, or game features

## Testing

The project includes comprehensive unit tests covering:
- Item creation and valuation
- Case opening mechanics
- Inventory management
- Player actions
- Game state management

All tests can be run with:
```bash
python3 test_game.py
```

## Future Enhancements

Potential additions to the game model:
- Trading system between players
- Item wear degradation over time
- Case key system
- Achievement/milestone tracking
- Market system with dynamic pricing
- Multiple player support
- Save/load game state
- Battle/competition modes

## Requirements

- Python 3.7 or higher
- No external dependencies (uses only Python standard library)

## License

This is a demonstration project for educational purposes.
