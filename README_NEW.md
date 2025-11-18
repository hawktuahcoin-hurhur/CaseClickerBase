# Global Coalition - Arms Dealer Game

A multiplayer arms trading and gambling game built with Python Flask and WebSockets.

## Features

- **Real-time Multiplayer**: WebSocket-based live updates
- **Marketplace**: Buy and sell weapons with other players
- **Gambling**: Coin flip and Blackjack games
- **Persistent Database**: SQLite database for all game data
- **Leaderboard**: Real-time rankings based on total wealth
- **User Accounts**: Persistent user IDs with saved progress

## Tech Stack

**Backend:**
- Flask 3.0 (Python web framework)
- Flask-SocketIO (WebSocket support)
- Flask-SQLAlchemy (ORM)
- SQLite (Database)

**Frontend:**
- HTML5/CSS3
- Vanilla JavaScript
- Socket.IO client

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python app.py
```

Or use the startup script:
```bash
./start.sh
```

## Usage

1. Server starts on `http://localhost:5000`
2. Open in your browser
3. Create your account (name + company name)
4. Start with $100 balance
5. Trade items, gamble, and climb the leaderboard!

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create new user
- `POST /api/auth/login` - Login existing user

### User
- `GET /api/user/<user_id>` - Get user data
- `POST /api/user/<user_id>/balance` - Update balance

### Marketplace
- `GET /api/marketplace/listings` - Get all listings
- `POST /api/marketplace/list` - List item for sale
- `POST /api/marketplace/buy/<listing_id>` - Buy item
- `POST /api/marketplace/cancel/<listing_id>` - Cancel listing

### Gambling
- `POST /api/gambling/coinflip` - Play coin flip
- `POST /api/gambling/blackjack/start` - Start blackjack game
- `POST /api/gambling/blackjack/action` - Hit/Stand/Double

### Leaderboard
- `GET /api/leaderboard` - Get top 50 players

## WebSocket Events

### Client → Server
- `join_game` - Join game room
- `request_leaderboard` - Request leaderboard update
- `request_market` - Request marketplace update

### Server → Client
- `connected` - Connection confirmation
- `leaderboard_update` - Real-time leaderboard data
- `market_update` - Real-time marketplace data
- `player_joined` - Player joined notification

## Database Models

### User
- user_id (unique identifier)
- name, company_name
- balance
- created_at, last_login

### InventoryItem
- Linked to user
- name, rarity, price, weapon_type
- acquired_at timestamp

### MarketListing
- Linked to seller
- item details, listing_price
- active status

### TradeOffer (future)
- sender/receiver IDs
- item arrays
- status tracking

## Game Structure

```
CaseClickerBase/
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── start.sh              # Startup script
├── game.db               # SQLite database (auto-created)
├── templates/
│   └── index.html        # Main game page
└── static/
    ├── styles.css        # Game styling
    └── script.js         # Frontend logic
```

## Development

The server runs in debug mode by default with hot-reload enabled.

**Default Port:** 5000  
**Database:** SQLite (`game.db` - auto-created on first run)

## Future Features

- [ ] P2P Trading system
- [ ] More gambling games
- [ ] Achievement system
- [ ] Chat functionality
- [ ] Item crafting/upgrading
