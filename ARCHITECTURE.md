"""
Architecture diagram for the CSGO Case Clicker game model.

Component Relationships:
=======================

┌──────────────────────────────────────────────────────────┐
│                         Game                             │
│  - Manages game state and available cases                │
│  - Creates and tracks player                             │
│  - Provides statistics and game flow control             │
└─────────────────┬────────────────────────────────────────┘
                  │
                  │ contains
                  ▼
         ┌────────────────┐
         │     Player     │
         │  - name        │
         │  - balance     │
         │  - cases_opened│
         └───┬────────┬───┘
             │        │
    contains │        │ opens
             │        │
             ▼        ▼
      ┌──────────┐  ┌────────┐
      │Inventory │  │  Case  │
      │          │  │        │
      └────┬─────┘  └───┬────┘
           │            │
  contains │            │ contains
           │            │
           └─────┬──────┘
                 │
                 ▼
            ┌────────┐
            │  Item  │
            │        │
            │ Rarity │
            │Condition│
            │StatTrak │
            └────────┘

Data Flow:
==========

1. Game Setup:
   Game → Create Player → Initialize Inventory

2. Case Opening:
   Player → Check Balance → Open Case → Generate Item → Add to Inventory

3. Item Selling:
   Player → Select Item from Inventory → Sell → Add value to Balance

4. Statistics:
   Game → Query Player → Query Inventory → Calculate Stats

Module Dependencies:
===================

item.py
  ↑
  │ imports
  │
case.py, inventory.py
  ↑
  │ imports
  │
player.py
  ↑
  │ imports
  │
game.py
  ↑
  │ imports
  │
main.py, test_game.py

All modules are independent with clear interfaces.
No circular dependencies exist.
"""
