# CaseClickerBase

A complete game model for a CSGO-inspired case clicker game, built in Python.

## Overview

CaseClickerBase provides a fully-functional game model that simulates the case opening mechanics from Counter-Strike: Global Offensive. The model includes items with rarities and conditions, cases with probability-based drops, inventory management, and player progression.

## Quick Start

```bash
# Run the demo
python3 main.py

# Run tests
python3 test_game.py
```

## Documentation

For detailed information about the game model, see [GAME_MODEL.md](GAME_MODEL.md).

## Features

- ✅ Complete item system with 7 rarity tiers
- ✅ Realistic case opening with probability-based drops
- ✅ Item conditions (Factory New to Battle-Scarred)
- ✅ StatTrak™ support (10% chance)
- ✅ Dynamic item valuation
- ✅ Inventory management
- ✅ Player balance and progression tracking
- ✅ Comprehensive test suite

## Game Components

- **Items**: Weapons, skins, and collectibles with rarities and conditions
- **Cases**: Containers with configurable item pools
- **Inventory**: Item collection and management system
- **Player**: Balance, inventory, and statistics tracking
- **Game**: Main controller for game state and flow

## Example

```python
from game import Game

# Start a new game
game = Game()
player = game.start_new_game("Player1", starting_balance=100.0)

# Open a case
case = game.get_case_by_name("Starter Case")
item = player.open_case(case)

print(f"Unboxed: {item} - Worth ${item.get_value()}")
```