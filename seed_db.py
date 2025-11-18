from app import app, db, User, InventoryItem, MarketListing
import random

# Weapon data
WEAPONS = [
    {'name': 'AK-47 | Redline', 'rarity': 'classified', 'price': 250.00, 'weapon_type': 'Rifle'},
    {'name': 'M4A4 | Asiimov', 'rarity': 'covert', 'price': 450.00, 'weapon_type': 'Rifle'},
    {'name': 'AWP | Dragon Lore', 'rarity': 'covert', 'price': 2500.00, 'weapon_type': 'Sniper'},
    {'name': 'Desert Eagle | Blaze', 'rarity': 'restricted', 'price': 180.00, 'weapon_type': 'Pistol'},
    {'name': 'Glock-18 | Fade', 'rarity': 'restricted', 'price': 120.00, 'weapon_type': 'Pistol'},
    {'name': 'USP-S | Kill Confirmed', 'rarity': 'covert', 'price': 380.00, 'weapon_type': 'Pistol'},
    {'name': 'P90 | Asiimov', 'rarity': 'classified', 'price': 85.00, 'weapon_type': 'SMG'},
    {'name': 'MP7 | Fade', 'rarity': 'restricted', 'price': 65.00, 'weapon_type': 'SMG'},
]

def seed_database():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        print("🌱 Seeding database...")
        
        # Create test users
        test_users = [
            {'name': 'John Wick', 'company': 'Continental Arms'},
            {'name': 'Tony Stark', 'company': 'Stark Industries'},
            {'name': 'James Bond', 'company': 'MI6 Arsenal'},
        ]
        
        created_users = []
        for user_data in test_users:
            user_id = f"test_{user_data['name'].lower().replace(' ', '_')}"
            user = User(
                user_id=user_id,
                name=user_data['name'],
                company_name=user_data['company'],
                balance=random.randint(500, 2000)
            )
            db.session.add(user)
            created_users.append(user)
            print(f"✅ Created user: {user.name} | {user.company_name} | ${user.balance}")
        
        db.session.commit()
        
        # Add inventory items to users
        for user in created_users:
            num_items = random.randint(2, 5)
            for _ in range(num_items):
                weapon = random.choice(WEAPONS)
                item = InventoryItem(
                    user_id=user.user_id,
                    name=weapon['name'],
                    rarity=weapon['rarity'],
                    price=weapon['price'],
                    weapon_type=weapon['weapon_type']
                )
                db.session.add(item)
            print(f"   📦 Added {num_items} items to {user.name}'s inventory")
        
        db.session.commit()
        
        # Create marketplace listings
        for user in created_users[:2]:  # First 2 users list items
            items_to_list = random.sample(list(user.inventory), min(2, len(user.inventory)))
            for item in items_to_list:
                listing_id = f"listing_{item.id}_{random.randint(1000, 9999)}"
                listing_price = item.price * random.uniform(0.8, 1.5)
                listing = MarketListing(
                    listing_id=listing_id,
                    seller_id=user.user_id,
                    item_name=item.name,
                    item_rarity=item.rarity,
                    item_price_base=item.price,
                    listing_price=listing_price,
                    weapon_type=item.weapon_type
                )
                db.session.add(listing)
                db.session.delete(item)
                print(f"   💰 {user.name} listed {item.name} for ${listing_price:.2f}")
        
        db.session.commit()
        
        print("\n✨ Database seeded successfully!")
        print(f"📊 Total users: {User.query.count()}")
        print(f"📦 Total inventory items: {InventoryItem.query.count()}")
        print(f"🏪 Total market listings: {MarketListing.query.filter_by(active=True).count()}")

if __name__ == '__main__':
    seed_database()
