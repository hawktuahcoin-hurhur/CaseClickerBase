from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets
import random
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for development

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ==================== GAME DATA ====================

# Crate types with weapons
CRATE_TYPES = [
    {
        'id': 'weapon-case',
        'name': 'Weapon Case',
        'price': 2.50,
        'keyPrice': 5.00,
        'color': 'linear-gradient(135deg, #4b69ff, #8847ff)',
        'weapons': [
            {'name': 'AWP | Dragon Lore', 'rarity': 'covert', 'minPrice': 50.00, 'maxPrice': 150.00, 'chance': 0.32},
            {'name': 'M4A4 | Howl', 'rarity': 'covert', 'minPrice': 45.00, 'maxPrice': 140.00, 'chance': 0.32},
            {'name': 'AK-47 | Redline', 'rarity': 'classified', 'minPrice': 15.00, 'maxPrice': 35.00, 'chance': 0.64},
            {'name': 'M4A1-S | Hyper Beast', 'rarity': 'classified', 'minPrice': 12.00, 'maxPrice': 30.00, 'chance': 0.64},
            {'name': 'AWP | Asiimov', 'rarity': 'classified', 'minPrice': 18.00, 'maxPrice': 40.00, 'chance': 0.64},
            {'name': 'AK-47 | Vulcan', 'rarity': 'restricted', 'minPrice': 6.00, 'maxPrice': 15.00, 'chance': 3.2},
            {'name': 'M4A4 | Desolate Space', 'rarity': 'restricted', 'minPrice': 5.00, 'maxPrice': 12.00, 'chance': 3.2},
            {'name': 'AK-47 | Blue Laminate', 'rarity': 'mil-spec', 'minPrice': 1.00, 'maxPrice': 3.00, 'chance': 16.0},
            {'name': 'M4A4 | Griffin', 'rarity': 'mil-spec', 'minPrice': 0.80, 'maxPrice': 2.50, 'chance': 16.0},
            {'name': 'P2000 | Granite Marbleized', 'rarity': 'industrial', 'minPrice': 0.10, 'maxPrice': 0.50, 'chance': 0.13},
        ]
    },
    {
        'id': 'chroma-case',
        'name': 'Chroma Case',
        'price': 5.00,
        'keyPrice': 10.00,
        'color': 'linear-gradient(135deg, #00d4ff, #00ff88)',
        'weapons': [
            {'name': 'AK-47 | Fire Serpent', 'rarity': 'covert', 'minPrice': 80.00, 'maxPrice': 200.00, 'chance': 0.32},
            {'name': 'M4A4 | Temukau', 'rarity': 'covert', 'minPrice': 60.00, 'maxPrice': 160.00, 'chance': 0.32},
            {'name': 'AWP | Hyper Beast', 'rarity': 'classified', 'minPrice': 20.00, 'maxPrice': 45.00, 'chance': 0.64},
            {'name': 'AK-47 | Neon Revolution', 'rarity': 'classified', 'minPrice': 18.00, 'maxPrice': 42.00, 'chance': 0.64},
            {'name': 'M4A4 | X-Ray', 'rarity': 'restricted', 'minPrice': 7.00, 'maxPrice': 16.00, 'chance': 3.2},
            {'name': 'AK-47 | Elite Build', 'rarity': 'restricted', 'minPrice': 6.00, 'maxPrice': 14.00, 'chance': 3.2},
            {'name': 'Galil AR | Chatterbox', 'rarity': 'mil-spec', 'minPrice': 1.20, 'maxPrice': 3.50, 'chance': 16.0},
            {'name': 'MP9 | Deadly Poison', 'rarity': 'industrial', 'minPrice': 0.15, 'maxPrice': 0.60, 'chance': 0.13},
        ]
    },
    {
        'id': 'operation-case',
        'name': 'Operation Case',
        'price': 10.00,
        'keyPrice': 20.00,
        'color': 'linear-gradient(135deg, #ff6b00, #ffd700)',
        'weapons': [
            {'name': 'AK-47 | The Empress', 'rarity': 'covert', 'minPrice': 100.00, 'maxPrice': 250.00, 'chance': 0.32},
            {'name': 'M4A4 | Neo-Noir', 'rarity': 'covert', 'minPrice': 90.00, 'maxPrice': 220.00, 'chance': 0.32},
            {'name': 'AWP | Wildfire', 'rarity': 'classified', 'minPrice': 25.00, 'maxPrice': 55.00, 'chance': 0.64},
            {'name': 'AK-47 | Phantom Disruptor', 'rarity': 'classified', 'minPrice': 22.00, 'maxPrice': 50.00, 'chance': 0.64},
            {'name': 'AK-47 | Uncharted', 'rarity': 'restricted', 'minPrice': 8.00, 'maxPrice': 18.00, 'chance': 3.2},
            {'name': 'M4A4 | In Living Color', 'rarity': 'restricted', 'minPrice': 7.00, 'maxPrice': 16.00, 'chance': 3.2},
            {'name': 'SSG 08 | Parallax', 'rarity': 'mil-spec', 'minPrice': 1.50, 'maxPrice': 4.00, 'chance': 16.0},
            {'name': 'R8 Revolver | Survivalist', 'rarity': 'industrial', 'minPrice': 0.20, 'maxPrice': 0.70, 'chance': 0.13},
        ]
    },
]

# AI Coalition Names
AI_COALITION_NAMES = [
    {'name': 'Tokyo Syndicate', 'avatar': '🗼', 'type': 'location'},
    {'name': 'Berlin Cartel', 'avatar': '🏛️', 'type': 'location'},
    {'name': 'Moscow Alliance', 'avatar': '⭐', 'type': 'location'},
    {'name': 'Shanghai Collective', 'avatar': '🏮', 'type': 'location'},
    {'name': 'Dubai Consortium', 'avatar': '🕌', 'type': 'location'},
    {'name': 'London Underground', 'avatar': '🎩', 'type': 'location'},
    {'name': 'Paris Legion', 'avatar': '🗼', 'type': 'location'},
    {'name': 'New York Empire', 'avatar': '🗽', 'type': 'location'},
    {'name': 'Los Angeles Syndicate', 'avatar': '🌴', 'type': 'location'},
    {'name': 'Hong Kong Triad', 'avatar': '🐉', 'type': 'location'},
    {'name': 'Seoul Dynasty', 'avatar': '🏯', 'type': 'location'},
    {'name': 'Singapore Coalition', 'avatar': '🦁', 'type': 'location'},
    {'name': 'Kalashnikov Corps', 'avatar': '⚔️', 'type': 'manufacturer'},
    {'name': 'Colt Alliance', 'avatar': '🔫', 'type': 'manufacturer'},
    {'name': 'Glock Syndicate', 'avatar': '🔧', 'type': 'manufacturer'},
    {'name': 'HK Consortium', 'avatar': '🛡️', 'type': 'manufacturer'},
    {'name': 'Beretta Family', 'avatar': '👔', 'type': 'manufacturer'},
    {'name': 'FN Herstal Group', 'avatar': '⚙️', 'type': 'manufacturer'},
    {'name': 'SIG Sauer Collective', 'avatar': '🎯', 'type': 'manufacturer'},
]

# ==================== DATABASE MODELS ====================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, default=100.0)
    game_mode = db.Column(db.String(20))  # 'story' or 'pvp'
    cases_opened = db.Column(db.Integer, default=0)
    keys_owned = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    
    inventory = db.relationship('InventoryItem', backref='owner', lazy=True, cascade='all, delete-orphan')
    listings = db.relationship('MarketListing', backref='seller', lazy=True, cascade='all, delete-orphan')
    owned_cases = db.relationship('OwnedCase', backref='owner', lazy=True, cascade='all, delete-orphan')

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.user_id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    rarity = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    weapon_type = db.Column(db.String(50))
    acquired_at = db.Column(db.DateTime, default=datetime.utcnow)

class OwnedCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.user_id'), nullable=False)
    case_id = db.Column(db.String(50), nullable=False)  # e.g., 'weapon-case'
    quantity = db.Column(db.Integer, default=0)

class AIRival(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)  # Associated with user's story mode
    rival_id = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    avatar = db.Column(db.String(10))
    type = db.Column(db.String(50))  # 'location' or 'manufacturer'
    balance = db.Column(db.Float, default=100.0)
    cases_opened = db.Column(db.Integer, default=0)
    last_action = db.Column(db.DateTime, default=datetime.utcnow)

class MarketListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.String(100), unique=True, nullable=False)
    seller_id = db.Column(db.String(50), db.ForeignKey('user.user_id'), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    item_rarity = db.Column(db.String(50), nullable=False)
    item_price_base = db.Column(db.Float, nullable=False)
    listing_price = db.Column(db.Float, nullable=False)
    weapon_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)

class TradeOffer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trade_id = db.Column(db.String(100), unique=True, nullable=False)
    sender_id = db.Column(db.String(50), nullable=False)
    receiver_id = db.Column(db.String(50), nullable=False)
    sender_items = db.Column(db.Text)  # JSON array of item IDs
    receiver_items = db.Column(db.Text)  # JSON array of item IDs
    status = db.Column(db.String(20), default='pending')  # pending, accepted, declined, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== INITIALIZE DATABASE ====================

def init_db():
    with app.app_context():
        db.create_all()
        print("Database initialized!")

# ==================== HELPER FUNCTIONS ====================

def generate_user_id():
    return f"user_{secrets.token_hex(8)}_{int(datetime.utcnow().timestamp())}"

def get_user_data(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return None
    
    inventory = [{
        'id': item.id,
        'name': item.name,
        'rarity': item.rarity,
        'price': item.price,
        'weapon_type': item.weapon_type
    } for item in user.inventory]
    
    owned_cases = {}
    for case in user.owned_cases:
        owned_cases[case.case_id] = case.quantity
    
    return {
        'user_id': user.user_id,
        'name': user.name,
        'company_name': user.company_name,
        'balance': user.balance,
        'game_mode': user.game_mode,
        'cases_opened': user.cases_opened,
        'keys_owned': user.keys_owned,
        'inventory': inventory,
        'owned_cases': owned_cases,
        'inventory_value': sum(item.price for item in user.inventory)
    }

def init_ai_rivals(user_id):
    """Initialize AI rivals for a user's story mode"""
    # Check if rivals already exist
    existing = AIRival.query.filter_by(user_id=user_id).count()
    if existing > 0:
        return
    
    # Create 30-35 AI rivals
    rival_count = 30 + random.randint(0, 5)
    shuffled = random.sample(AI_COALITION_NAMES, min(rival_count, len(AI_COALITION_NAMES)))
    
    for i, coalition in enumerate(shuffled):
        rival = AIRival(
            user_id=user_id,
            rival_id=f"ai_{i}",
            name=coalition['name'],
            avatar=coalition['avatar'],
            type=coalition['type'],
            balance=80 + random.random() * 120,
            cases_opened=random.randint(0, 4)
        )
        db.session.add(rival)
    
    db.session.commit()
    print(f"Created {len(shuffled)} AI rivals for user {user_id}")

def get_ai_rivals(user_id):
    """Get all AI rivals for a user"""
    rivals = AIRival.query.filter_by(user_id=user_id).all()
    return [{
        'id': rival.rival_id,
        'name': rival.name,
        'avatar': rival.avatar,
        'type': rival.type,
        'balance': rival.balance,
        'cases_opened': rival.cases_opened
    } for rival in rivals]

def update_ai_rivals(user_id):
    """Simulate AI rival actions"""
    rivals = AIRival.query.filter_by(user_id=user_id).all()
    
    for rival in rivals:
        # Random chance to perform action
        if random.random() < 0.1:  # 10% chance per update
            action = random.choice(['open_case', 'buy_item', 'nothing'])
            
            if action == 'open_case' and rival.balance > 10:
                # AI opens a case
                case_cost = 7.50  # Average case cost
                rival.balance -= case_cost
                rival.cases_opened += 1
                
                # Random item value
                item_value = random.uniform(0.10, 50.00)
                rival.balance += item_value
                
            elif action == 'buy_item' and rival.balance > 5:
                # AI buys from market
                cost = random.uniform(1.00, min(20.00, rival.balance * 0.3))
                rival.balance -= cost
        
        rival.last_action = datetime.utcnow()
    
    db.session.commit()

def open_case(user_id, case_id):
    """Open a case and return a random weapon"""
    # Find the crate type
    crate = next((c for c in CRATE_TYPES if c['id'] == case_id), None)
    if not crate:
        return None
    
    # Select weapon based on rarity chances
    total_chance = sum(w['chance'] for w in crate['weapons'])
    rand = random.uniform(0, total_chance)
    
    cumulative = 0
    selected_weapon = None
    for weapon in crate['weapons']:
        cumulative += weapon['chance']
        if rand <= cumulative:
            selected_weapon = weapon
            break
    
    if not selected_weapon:
        selected_weapon = crate['weapons'][-1]  # Fallback to last weapon
    
    # Generate random price within range
    price = random.uniform(selected_weapon['minPrice'], selected_weapon['maxPrice'])
    
    return {
        'name': selected_weapon['name'],
        'rarity': selected_weapon['rarity'],
        'price': round(price, 2),
        'weapon_type': selected_weapon['name'].split(' | ')[0] if ' | ' in selected_weapon['name'] else 'Weapon'
    }

def broadcast_leaderboard():
    users = User.query.order_by(User.balance.desc()).limit(50).all()
    leaderboard = [{
        'rank': idx + 1,
        'name': user.name,
        'company': user.company_name,
        'balance': user.balance,
        'inventory_value': sum(item.price for item in user.inventory),
        'total_value': user.balance + sum(item.price for item in user.inventory)
    } for idx, user in enumerate(users)]
    
    socketio.emit('leaderboard_update', {'leaderboard': leaderboard})

def broadcast_market_update():
    listings = MarketListing.query.filter_by(active=True).order_by(MarketListing.created_at.desc()).all()
    market_data = [{
        'listing_id': listing.listing_id,
        'seller_name': User.query.filter_by(user_id=listing.seller_id).first().name,
        'seller_id': listing.seller_id,
        'item_name': listing.item_name,
        'item_rarity': listing.item_rarity,
        'listing_price': listing.listing_price,
        'weapon_type': listing.weapon_type
    } for listing in listings]
    
    socketio.emit('market_update', {'listings': market_data})

# ==================== API ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    company = data.get('company')
    game_mode = data.get('game_mode', 'pvp')  # 'story' or 'pvp'
    
    if not name or not company:
        return jsonify({'error': 'Name and company required'}), 400
    
    user_id = generate_user_id()
    new_user = User(
        user_id=user_id,
        name=name,
        company_name=company,
        game_mode=game_mode
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    # Initialize AI rivals if story mode
    if game_mode == 'story':
        init_ai_rivals(user_id)
    
    return jsonify({
        'success': True,
        'user': get_user_data(user_id)
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'user': get_user_data(user_id)
    })

@app.route('/api/user/<user_id>', methods=['GET'])
def get_user(user_id):
    user_data = get_user_data(user_id)
    if not user_data:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user_data)

@app.route('/api/user/<user_id>/balance', methods=['POST'])
def update_balance(user_id):
    data = request.json
    amount = data.get('amount')
    
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user.balance += amount
    db.session.commit()
    
    broadcast_leaderboard()
    
    return jsonify({'success': True, 'balance': user.balance})

@app.route('/api/marketplace/listings', methods=['GET'])
def get_listings():
    search = request.args.get('search', '').lower()
    rarity = request.args.get('rarity', 'all')
    
    query = MarketListing.query.filter_by(active=True)
    
    if search:
        query = query.filter(MarketListing.item_name.ilike(f'%{search}%'))
    if rarity != 'all':
        query = query.filter_by(item_rarity=rarity)
    
    listings = query.order_by(MarketListing.created_at.desc()).all()
    
    market_data = [{
        'listing_id': listing.listing_id,
        'seller_name': User.query.filter_by(user_id=listing.seller_id).first().name,
        'seller_id': listing.seller_id,
        'item_name': listing.item_name,
        'item_rarity': listing.item_rarity,
        'listing_price': listing.listing_price,
        'weapon_type': listing.weapon_type
    } for listing in listings]
    
    return jsonify({'listings': market_data})

@app.route('/api/marketplace/list', methods=['POST'])
def create_listing():
    data = request.json
    user_id = data.get('user_id')
    item_id = data.get('item_id')
    price = data.get('price')
    
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    item = InventoryItem.query.filter_by(id=item_id, user_id=user_id).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    listing_id = f"listing_{secrets.token_hex(8)}_{int(datetime.utcnow().timestamp())}"
    
    listing = MarketListing(
        listing_id=listing_id,
        seller_id=user_id,
        item_name=item.name,
        item_rarity=item.rarity,
        item_price_base=item.price,
        listing_price=price,
        weapon_type=item.weapon_type
    )
    
    db.session.add(listing)
    db.session.delete(item)
    db.session.commit()
    
    broadcast_market_update()
    
    return jsonify({'success': True, 'listing_id': listing_id})

@app.route('/api/marketplace/buy/<listing_id>', methods=['POST'])
def buy_listing(listing_id):
    data = request.json
    buyer_id = data.get('user_id')
    
    listing = MarketListing.query.filter_by(listing_id=listing_id, active=True).first()
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404
    
    buyer = User.query.filter_by(user_id=buyer_id).first()
    seller = User.query.filter_by(user_id=listing.seller_id).first()
    
    if not buyer or not seller:
        return jsonify({'error': 'User not found'}), 404
    
    if buyer.balance < listing.listing_price:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Transfer money
    buyer.balance -= listing.listing_price
    seller.balance += listing.listing_price
    
    # Transfer item
    new_item = InventoryItem(
        user_id=buyer_id,
        name=listing.item_name,
        rarity=listing.item_rarity,
        price=listing.item_price_base,
        weapon_type=listing.weapon_type
    )
    
    db.session.add(new_item)
    listing.active = False
    db.session.commit()
    
    broadcast_market_update()
    broadcast_leaderboard()
    
    return jsonify({'success': True})

@app.route('/api/marketplace/cancel/<listing_id>', methods=['POST'])
def cancel_listing(listing_id):
    data = request.json
    user_id = data.get('user_id')
    
    listing = MarketListing.query.filter_by(listing_id=listing_id, seller_id=user_id, active=True).first()
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404
    
    # Return item to inventory
    returned_item = InventoryItem(
        user_id=user_id,
        name=listing.item_name,
        rarity=listing.item_rarity,
        price=listing.item_price_base,
        weapon_type=listing.weapon_type
    )
    
    db.session.add(returned_item)
    listing.active = False
    db.session.commit()
    
    broadcast_market_update()
    
    return jsonify({'success': True})

# ==================== CASES & KEYS API ====================

@app.route('/api/crates', methods=['GET'])
def get_crates():
    """Get all available crate types"""
    return jsonify({'crates': CRATE_TYPES})

@app.route('/api/cases/buy', methods=['POST'])
def buy_cases():
    """Buy cases"""
    data = request.json
    user_id = data.get('user_id')
    case_id = data.get('case_id')
    quantity = data.get('quantity', 1)
    
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Find crate type
    crate = next((c for c in CRATE_TYPES if c['id'] == case_id), None)
    if not crate:
        return jsonify({'error': 'Invalid case type'}), 400
    
    total_cost = crate['price'] * quantity
    if user.balance < total_cost:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    user.balance -= total_cost
    
    # Add or update owned cases
    owned_case = OwnedCase.query.filter_by(user_id=user_id, case_id=case_id).first()
    if owned_case:
        owned_case.quantity += quantity
    else:
        owned_case = OwnedCase(user_id=user_id, case_id=case_id, quantity=quantity)
        db.session.add(owned_case)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'balance': user.balance,
        'owned_cases': {oc.case_id: oc.quantity for oc in user.owned_cases}
    })

@app.route('/api/keys/buy', methods=['POST'])
def buy_keys():
    """Buy keys"""
    data = request.json
    user_id = data.get('user_id')
    quantity = data.get('quantity', 1)
    
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    key_price = 5.00  # Base key price
    total_cost = key_price * quantity
    
    if user.balance < total_cost:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    user.balance -= total_cost
    user.keys_owned += quantity
    db.session.commit()
    
    return jsonify({
        'success': True,
        'balance': user.balance,
        'keys_owned': user.keys_owned
    })

@app.route('/api/cases/open', methods=['POST'])
def open_case_endpoint():
    """Open a case"""
    data = request.json
    user_id = data.get('user_id')
    case_id = data.get('case_id')
    
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if user has the case
    owned_case = OwnedCase.query.filter_by(user_id=user_id, case_id=case_id).first()
    if not owned_case or owned_case.quantity < 1:
        return jsonify({'error': 'No cases available'}), 400
    
    # Check if user has keys
    if user.keys_owned < 1:
        return jsonify({'error': 'No keys available'}), 400
    
    # Open the case
    item_data = open_case(user_id, case_id)
    if not item_data:
        return jsonify({'error': 'Failed to open case'}), 500
    
    # Add item to inventory
    new_item = InventoryItem(
        user_id=user_id,
        name=item_data['name'],
        rarity=item_data['rarity'],
        price=item_data['price'],
        weapon_type=item_data['weapon_type']
    )
    db.session.add(new_item)
    
    # Deduct case and key
    owned_case.quantity -= 1
    user.keys_owned -= 1
    user.cases_opened += 1
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'item': item_data,
        'balance': user.balance,
        'keys_owned': user.keys_owned,
        'cases_opened': user.cases_opened
    })

# ==================== AI RIVALS API ====================

@app.route('/api/rivals/init', methods=['POST'])
def init_rivals():
    """Initialize AI rivals for story mode"""
    data = request.json
    user_id = data.get('user_id')
    
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    init_ai_rivals(user_id)
    rivals = get_ai_rivals(user_id)
    
    return jsonify({
        'success': True,
        'rivals': rivals
    })

@app.route('/api/rivals/<user_id>', methods=['GET'])
def get_rivals(user_id):
    """Get all AI rivals for a user"""
    rivals = get_ai_rivals(user_id)
    return jsonify({'rivals': rivals})

@app.route('/api/rivals/update', methods=['POST'])
def update_rivals():
    """Update AI rival states"""
    data = request.json
    user_id = data.get('user_id')
    
    update_ai_rivals(user_id)
    rivals = get_ai_rivals(user_id)
    
    return jsonify({
        'success': True,
        'rivals': rivals
    })

# ==================== GAMBLING API ====================

@app.route('/api/gambling/coinflip', methods=['POST'])
def coin_flip():
    data = request.json
    user_id = data.get('user_id')
    bet = data.get('bet')
    choice = data.get('choice')
    
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.balance < bet:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    result = random.choice(['heads', 'tails'])
    won = result == choice
    
    if won:
        user.balance += bet
        winnings = bet * 2
    else:
        user.balance -= bet
        winnings = 0
    
    db.session.commit()
    broadcast_leaderboard()
    
    return jsonify({
        'success': True,
        'result': result,
        'won': won,
        'winnings': winnings,
        'balance': user.balance
    })

@app.route('/api/gambling/blackjack/start', methods=['POST'])
def start_blackjack():
    data = request.json
    user_id = data.get('user_id')
    bet = data.get('bet')
    
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.balance < bet:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    user.balance -= bet
    db.session.commit()
    
    # Create deck
    suits = ['♠', '♥', '♦', '♣']
    values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    deck = [{'suit': s, 'value': v} for s in suits for v in values]
    random.shuffle(deck)
    
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]
    
    game_state = {
        'deck': deck,
        'player_hand': player_hand,
        'dealer_hand': dealer_hand,
        'bet': bet
    }
    
    return jsonify({
        'success': True,
        'game_state': game_state,
        'balance': user.balance
    })

@app.route('/api/gambling/blackjack/action', methods=['POST'])
def blackjack_action():
    data = request.json
    user_id = data.get('user_id')
    action = data.get('action')
    game_state = data.get('game_state')
    
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    deck = game_state['deck']
    player_hand = game_state['player_hand']
    dealer_hand = game_state['dealer_hand']
    bet = game_state['bet']
    
    def card_value(card):
        if card['value'] == 'A':
            return 11
        if card['value'] in ['J', 'Q', 'K']:
            return 10
        return int(card['value'])
    
    def hand_value(hand):
        value = sum(card_value(card) for card in hand)
        aces = sum(1 for card in hand if card['value'] == 'A')
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        return value
    
    if action == 'hit':
        player_hand.append(deck.pop())
        player_value = hand_value(player_hand)
        
        if player_value > 21:
            result = 'bust'
            winnings = 0
        else:
            result = 'continue'
            winnings = None
    
    elif action == 'stand' or action == 'double':
        if action == 'double':
            if user.balance < bet:
                return jsonify({'error': 'Insufficient balance to double'}), 400
            user.balance -= bet
            bet *= 2
            player_hand.append(deck.pop())
        
        # Dealer plays
        while hand_value(dealer_hand) < 17:
            dealer_hand.append(deck.pop())
        
        player_value = hand_value(player_hand)
        dealer_value = hand_value(dealer_hand)
        
        if player_value > 21:
            result = 'bust'
            winnings = 0
        elif dealer_value > 21:
            result = 'dealer_bust'
            winnings = bet * 2
            user.balance += winnings
        elif player_value > dealer_value:
            result = 'win'
            winnings = bet * 2
            user.balance += winnings
        elif player_value < dealer_value:
            result = 'lose'
            winnings = 0
        else:
            result = 'push'
            winnings = bet
            user.balance += winnings
        
        db.session.commit()
        broadcast_leaderboard()
    
    return jsonify({
        'success': True,
        'result': result,
        'winnings': winnings,
        'game_state': {
            'deck': deck,
            'player_hand': player_hand,
            'dealer_hand': dealer_hand,
            'bet': bet
        },
        'player_value': hand_value(player_hand),
        'dealer_value': hand_value(dealer_hand) if result != 'continue' else card_value(dealer_hand[0]),
        'balance': user.balance
    })

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    users = User.query.order_by(User.balance.desc()).limit(50).all()
    leaderboard = [{
        'rank': idx + 1,
        'name': user.name,
        'company': user.company_name,
        'balance': user.balance,
        'inventory_value': sum(item.price for item in user.inventory),
        'total_value': user.balance + sum(item.price for item in user.inventory)
    } for idx, user in enumerate(users)]
    
    return jsonify({'leaderboard': leaderboard})

# ==================== WEBSOCKET EVENTS ====================

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connected', {'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')

@socketio.on('join_game')
def handle_join(data):
    user_id = data.get('user_id')
    join_room('game_room')
    emit('player_joined', {'user_id': user_id}, room='game_room')
    broadcast_leaderboard()
    broadcast_market_update()

@socketio.on('request_leaderboard')
def handle_leaderboard_request():
    broadcast_leaderboard()

@socketio.on('request_market')
def handle_market_request():
    broadcast_market_update()

# ==================== RUN SERVER ====================

if __name__ == '__main__':
    init_db()
    print("=" * 60)
    print("🚀 STARTING GLOBAL COALITION SERVER")
    print("=" * 60)
    print("📍 Server running on: http://localhost:5000")
    print("🌐 Access via Codespaces forwarded port 5000")
    print("=" * 60)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
