"""
Main entry point for the CSGO Case Clicker game.
Demonstrates the game model functionality.
"""
from game import Game


def main():
    """Run a demo of the game."""
    print("=" * 60)
    print("CSGO Case Clicker - Game Model Demo")
    print("=" * 60)
    print()
    
    # Create a new game
    game = Game()
    
    # Start a new game with a player
    player = game.start_new_game("Player1", starting_balance=100.0)
    print(f"Game started! {player}")
    print()
    
    # Show available cases
    print("Available Cases:")
    for case in game.available_cases:
        print(f"  - {case}")
    print()
    
    # Open some cases
    print("Opening cases...")
    print("-" * 60)
    
    for i in range(5):
        try:
            case = game.available_cases[0]  # Open starter cases
            print(f"\nOpening {case.name}...")
            item = player.open_case(case)
            print(f"  Got: {item} [{item.rarity.display_name}]")
            print(f"  Value: ${item.get_value():.2f}")
            print(f"  Balance: ${player.balance:.2f}")
        except ValueError as e:
            print(f"  Error: {e}")
            break
    
    print()
    print("-" * 60)
    print("Game Statistics:")
    print("-" * 60)
    stats = game.get_game_stats()
    print(f"Player: {stats['player_name']}")
    print(f"Balance: ${stats['balance']:.2f}")
    print(f"Inventory Value: ${stats['inventory_value']:.2f}")
    print(f"Net Worth: ${stats['net_worth']:.2f}")
    print(f"Cases Opened: {stats['cases_opened']}")
    print(f"Items Owned: {stats['items_owned']}")
    print()
    print("Rarity Distribution:")
    for rarity_name, count in stats['rarity_distribution'].items():
        if count > 0:
            print(f"  {rarity_name}: {count}")
    
    print()
    print("=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
