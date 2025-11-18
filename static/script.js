// API Configuration
const API_URL = window.location.origin;
const socket = io(API_URL);

// Game State
let gameState = {
    balance: 0,
    inventory: [],
    player: {
        name: '',
        companyName: '',
        userId: ''
    },
    marketListings: [],
    blackjackGame: null
};

// Socket.IO Event Handlers
socket.on('connected', (data) => {
    console.log('Connected to server:', data.message);
});

socket.on('leaderboard_update', (data) => {
    updateLeaderboardDisplay(data.leaderboard);
});

socket.on('market_update', (data) => {
    gameState.marketListings = data.listings;
    renderMarketListings();
});

// User ID Management
function getUserID() {
    let userID = localStorage.getItem('globalCoalition_userID');
    return userID;
}

function setUserID(userID) {
    localStorage.setItem('globalCoalition_userID', userID);
    gameState.player.userId = userID;
}

// API Calls
async function apiCall(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    const response = await fetch(`${API_URL}${endpoint}`, options);
    const data = await response.json();
    
    if (!response.ok) {
        throw new Error(data.error || 'API request failed');
    }
    
    return data;
}

// DOM Elements
const welcomeModal = document.getElementById('welcome-modal');
const playerNameInput = document.getElementById('player-name');
const companyNameInput = document.getElementById('company-name');
const startGameBtn = document.getElementById('start-game-btn');
const userDisplay = document.getElementById('user-display');
const balanceEl = document.getElementById('balance');
const inventoryCountEl = document.getElementById('inventory-count');
const totalValueEl = document.getElementById('total-value');
const inventoryEl = document.getElementById('inventory');
const inventoryEmptyEl = document.getElementById('inventory-empty');

// Initialize
async function init() {
    setupTabs();
    setupEventListeners();
    
    // Check for existing user
    const userID = getUserID();
    if (userID) {
        try {
            const data = await apiCall(`/api/user/${userID}`);
            gameState.player.userId = data.user_id;
            gameState.player.name = data.name;
            gameState.player.companyName = data.company_name;
            gameState.balance = data.balance;
            gameState.inventory = data.inventory;
            
            welcomeModal.classList.add('hidden');
            displayUserInfo();
            updateUI();
            
            // Join game room
            socket.emit('join_game', { user_id: userID });
        } catch (error) {
            console.error('Failed to load user:', error);
            localStorage.removeItem('globalCoalition_userID');
        }
    }
}

// Setup Tabs
function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.dataset.tab;
            
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(`${targetTab}-tab`).classList.add('active');
            
            if (targetTab === 'leaderboard') {
                socket.emit('request_leaderboard');
            } else if (targetTab === 'market') {
                socket.emit('request_market');
            }
        });
    });
}

// Setup Event Listeners
function setupEventListeners() {
    startGameBtn.addEventListener('click', startGame);
    document.getElementById('menu-btn').addEventListener('click', () => {
        document.getElementById('game-menu-modal').classList.remove('hidden');
    });
    document.getElementById('close-menu-btn').addEventListener('click', () => {
        document.getElementById('game-menu-modal').classList.add('hidden');
    });
    document.getElementById('new-game-btn').addEventListener('click', newGame);
    document.getElementById('reset-hwid-btn').addEventListener('click', resetUserID);
    
    // Inventory filters
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterInventory(btn.dataset.filter);
        });
    });
    
    // Market
    document.getElementById('list-item-btn').addEventListener('click', showListItemModal);
    document.getElementById('cancel-list').addEventListener('click', () => {
        document.getElementById('list-item-modal').classList.add('hidden');
    });
    document.getElementById('market-search')?.addEventListener('input', loadMarketListings);
    document.getElementById('market-filter-rarity')?.addEventListener('change', loadMarketListings);
    
    // Gambling - Coin Flip
    document.querySelectorAll('.choice-btn').forEach(btn => {
        btn.addEventListener('click', () => playCoinFlip(btn.dataset.choice));
    });
    
    // Gambling - Blackjack
    document.getElementById('start-blackjack').addEventListener('click', startBlackjack);
    document.getElementById('hit-btn').addEventListener('click', () => blackjackAction('hit'));
    document.getElementById('stand-btn').addEventListener('click', () => blackjackAction('stand'));
    document.getElementById('double-btn').addEventListener('click', () => blackjackAction('double'));
}

// Start Game
async function startGame() {
    const name = playerNameInput.value.trim();
    const company = companyNameInput.value.trim();
    
    if (!name || !company) {
        alert('Please enter both your name and company name!');
        return;
    }
    
    try {
        const data = await apiCall('/api/auth/register', 'POST', { name, company });
        
        gameState.player.userId = data.user.user_id;
        gameState.player.name = data.user.name;
        gameState.player.companyName = data.user.company_name;
        gameState.balance = data.user.balance;
        gameState.inventory = data.user.inventory;
        
        setUserID(data.user.user_id);
        
        welcomeModal.classList.add('hidden');
        displayUserInfo();
        updateUI();
        
        // Join game room
        socket.emit('join_game', { user_id: data.user.user_id });
    } catch (error) {
        alert('Failed to create account: ' + error.message);
    }
}

// Display User Info
function displayUserInfo() {
    userDisplay.textContent = `${gameState.player.name} | ${gameState.player.companyName}`;
}

// Update UI
async function updateUI() {
    balanceEl.textContent = `$${gameState.balance.toFixed(2)}`;
    inventoryCountEl.textContent = gameState.inventory.length;
    
    const totalValue = gameState.inventory.reduce((sum, item) => sum + item.price, 0);
    totalValueEl.textContent = `$${totalValue.toFixed(2)}`;
    
    renderInventory();
}

// Render Inventory
function renderInventory(filter = 'all') {
    inventoryEl.innerHTML = '';
    
    let items = gameState.inventory;
    if (filter !== 'all') {
        items = items.filter(item => item.rarity === filter);
    }
    
    if (items.length === 0) {
        inventoryEmptyEl.style.display = 'block';
    } else {
        inventoryEmptyEl.style.display = 'none';
        
        items.forEach((item) => {
            const itemEl = document.createElement('div');
            itemEl.className = `inventory-item rarity-${item.rarity}`;
            itemEl.innerHTML = `
                <div class="item-name">${item.name}</div>
                <div class="item-price">$${item.price.toFixed(2)}</div>
            `;
            itemEl.addEventListener('click', () => showItemOptions(item));
            inventoryEl.appendChild(itemEl);
        });
    }
}

function filterInventory(filter) {
    renderInventory(filter);
}

function showItemOptions(item) {
    const action = confirm(`${item.name} - $${item.price.toFixed(2)}\n\nList this item on the market?`);
    
    if (action) {
        const price = prompt(`Set price for ${item.name}:`, item.price.toFixed(2));
        if (price && !isNaN(price) && parseFloat(price) > 0) {
            listItemForSale(item.id, parseFloat(price));
        }
    }
}

// Market
function showListItemModal() {
    if (gameState.inventory.length === 0) {
        alert('You have no items to sell!');
        return;
    }
    
    const modal = document.getElementById('list-item-modal');
    const selectionDiv = document.getElementById('list-item-selection');
    selectionDiv.innerHTML = '<h3>Select an item to list:</h3>';
    
    gameState.inventory.forEach((item) => {
        const itemDiv = document.createElement('div');
        itemDiv.className = `inventory-item rarity-${item.rarity}`;
        itemDiv.style.marginBottom = '10px';
        itemDiv.innerHTML = `
            <div class="item-name">${item.name}</div>
            <div class="item-price">$${item.price.toFixed(2)}</div>
        `;
        itemDiv.addEventListener('click', () => {
            const price = prompt(`Set price for ${item.name}:`, item.price.toFixed(2));
            if (price && !isNaN(price) && parseFloat(price) > 0) {
                listItemForSale(item.id, parseFloat(price));
            }
        });
        selectionDiv.appendChild(itemDiv);
    });
    
    modal.classList.remove('hidden');
}

async function listItemForSale(itemId, price) {
    try {
        await apiCall('/api/marketplace/list', 'POST', {
            user_id: gameState.player.userId,
            item_id: itemId,
            price: price
        });
        
        // Refresh user data
        const data = await apiCall(`/api/user/${gameState.player.userId}`);
        gameState.balance = data.balance;
        gameState.inventory = data.inventory;
        
        updateUI();
        document.getElementById('list-item-modal').classList.add('hidden');
        alert('Item listed successfully!');
    } catch (error) {
        alert('Failed to list item: ' + error.message);
    }
}

async function loadMarketListings() {
    const searchTerm = document.getElementById('market-search')?.value || '';
    const rarityFilter = document.getElementById('market-filter-rarity')?.value || 'all';
    
    try {
        const data = await apiCall(`/api/marketplace/listings?search=${searchTerm}&rarity=${rarityFilter}`);
        gameState.marketListings = data.listings;
        renderMarketListings();
    } catch (error) {
        console.error('Failed to load market listings:', error);
    }
}

function renderMarketListings() {
    const listingsEl = document.getElementById('market-listings');
    const listings = gameState.marketListings;
    
    listingsEl.innerHTML = '';
    
    if (listings.length === 0) {
        listingsEl.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No listings available</p>';
        return;
    }
    
    listings.forEach(listing => {
        const listingEl = document.createElement('div');
        listingEl.className = `market-listing rarity-${listing.item_rarity}`;
        listingEl.innerHTML = `
            <div class="listing-seller">Seller: ${listing.seller_name}</div>
            <div class="item-name">${listing.item_name}</div>
            <div class="listing-price">$${listing.listing_price.toFixed(2)}</div>
            ${listing.seller_id !== gameState.player.userId ? 
                `<button class="btn" onclick="buyListing('${listing.listing_id}')">Buy</button>` : 
                `<button class="btn cancel-btn" onclick="removeListing('${listing.listing_id}')">Remove</button>`}
        `;
        listingsEl.appendChild(listingEl);
    });
}

async function buyListing(listingId) {
    try {
        await apiCall(`/api/marketplace/buy/${listingId}`, 'POST', {
            user_id: gameState.player.userId
        });
        
        // Refresh user data
        const data = await apiCall(`/api/user/${gameState.player.userId}`);
        gameState.balance = data.balance;
        gameState.inventory = data.inventory;
        
        updateUI();
        alert('Purchase successful!');
    } catch (error) {
        alert('Failed to buy item: ' + error.message);
    }
}

async function removeListing(listingId) {
    try {
        await apiCall(`/api/marketplace/cancel/${listingId}`, 'POST', {
            user_id: gameState.player.userId
        });
        
        // Refresh user data
        const data = await apiCall(`/api/user/${gameState.player.userId}`);
        gameState.balance = data.balance;
        gameState.inventory = data.inventory;
        
        updateUI();
    } catch (error) {
        alert('Failed to remove listing: ' + error.message);
    }
}

// Gambling - Coin Flip
async function playCoinFlip(choice) {
    const betAmount = parseFloat(document.getElementById('coin-bet').value);
    
    if (!betAmount || betAmount <= 0) {
        alert('Please enter a valid bet amount!');
        return;
    }
    
    if (betAmount > gameState.balance) {
        alert('Not enough balance!');
        return;
    }
    
    try {
        const coin = document.getElementById('coin');
        coin.className = 'coin flip-' + choice;
        
        const data = await apiCall('/api/gambling/coinflip', 'POST', {
            user_id: gameState.player.userId,
            bet: betAmount,
            choice: choice
        });
        
        coin.className = 'coin flip-' + data.result;
        
        setTimeout(() => {
            const resultEl = document.getElementById('coin-result');
            
            if (data.won) {
                resultEl.className = 'game-result win';
                resultEl.textContent = `🎉 You won $${data.winnings.toFixed(2)}!`;
            } else {
                resultEl.className = 'game-result lose';
                resultEl.textContent = `❌ You lost $${betAmount.toFixed(2)}`;
            }
            
            gameState.balance = data.balance;
            updateUI();
            
            setTimeout(() => {
                coin.className = 'coin';
            }, 2000);
        }, 1000);
    } catch (error) {
        alert('Coin flip failed: ' + error.message);
    }
}

// Gambling - Blackjack
async function startBlackjack() {
    const betAmount = parseFloat(document.getElementById('blackjack-bet-input').value);
    
    if (!betAmount || betAmount <= 0) {
        alert('Please enter a valid bet amount!');
        return;
    }
    
    if (betAmount > gameState.balance) {
        alert('Not enough balance!');
        return;
    }
    
    try {
        const data = await apiCall('/api/gambling/blackjack/start', 'POST', {
            user_id: gameState.player.userId,
            bet: betAmount
        });
        
        gameState.balance = data.balance;
        gameState.blackjackGame = data.game_state;
        
        document.getElementById('blackjack-bet-screen').style.display = 'none';
        document.getElementById('blackjack-table').style.display = 'block';
        document.getElementById('blackjack-result').textContent = '';
        
        renderBlackjackHands(data.game_state.player_hand, data.game_state.dealer_hand, false);
        updateUI();
    } catch (error) {
        alert('Failed to start blackjack: ' + error.message);
    }
}

function renderBlackjackHands(playerHand, dealerHand, showDealerCards = false) {
    // Dealer cards
    const dealerCardsEl = document.getElementById('dealer-cards');
    dealerCardsEl.innerHTML = '';
    dealerHand.forEach((card, index) => {
        const cardEl = document.createElement('div');
        cardEl.className = 'card' + (['♥', '♦'].includes(card.suit) ? ' red' : '');
        if (index === 1 && !showDealerCards) {
            cardEl.classList.add('hidden');
            cardEl.textContent = '?';
        } else {
            cardEl.textContent = card.value + card.suit;
        }
        dealerCardsEl.appendChild(cardEl);
    });
    
    // Player cards
    const playerCardsEl = document.getElementById('player-cards');
    playerCardsEl.innerHTML = '';
    playerHand.forEach(card => {
        const cardEl = document.createElement('div');
        cardEl.className = 'card' + (['♥', '♦'].includes(card.suit) ? ' red' : '');
        cardEl.textContent = card.value + card.suit;
        playerCardsEl.appendChild(cardEl);
    });
}

async function blackjackAction(action) {
    try {
        const data = await apiCall('/api/gambling/blackjack/action', 'POST', {
            user_id: gameState.player.userId,
            action: action,
            game_state: gameState.blackjackGame
        });
        
        gameState.blackjackGame = data.game_state;
        gameState.balance = data.balance;
        
        const showDealer = data.result !== 'continue';
        renderBlackjackHands(data.game_state.player_hand, data.game_state.dealer_hand, showDealer);
        
        document.getElementById('player-score').textContent = data.player_value;
        document.getElementById('dealer-score').textContent = data.dealer_value;
        
        if (data.result !== 'continue') {
            document.getElementById('hit-btn').disabled = true;
            document.getElementById('stand-btn').disabled = true;
            document.getElementById('double-btn').disabled = true;
            
            const resultEl = document.getElementById('blackjack-result');
            
            if (data.result === 'bust') {
                resultEl.className = 'game-result lose';
                resultEl.textContent = `❌ BUST! You lost $${data.game_state.bet.toFixed(2)}`;
            } else if (data.result === 'dealer_bust') {
                resultEl.className = 'game-result win';
                resultEl.textContent = `🎉 Dealer BUST! You won $${data.winnings.toFixed(2)}!`;
            } else if (data.result === 'win') {
                resultEl.className = 'game-result win';
                resultEl.textContent = `🎉 You WIN! You won $${data.winnings.toFixed(2)}!`;
            } else if (data.result === 'lose') {
                resultEl.className = 'game-result lose';
                resultEl.textContent = `❌ Dealer WINS! You lost $${data.game_state.bet.toFixed(2)}`;
            } else if (data.result === 'push') {
                resultEl.className = 'game-result';
                resultEl.textContent = `🤝 PUSH! Bet returned: $${data.winnings.toFixed(2)}`;
            }
            
            updateUI();
            
            setTimeout(() => {
                document.getElementById('blackjack-table').style.display = 'none';
                document.getElementById('blackjack-bet-screen').style.display = 'block';
                document.getElementById('hit-btn').disabled = false;
                document.getElementById('stand-btn').disabled = false;
                document.getElementById('double-btn').disabled = false;
                gameState.blackjackGame = null;
            }, 3000);
        }
    } catch (error) {
        alert('Blackjack action failed: ' + error.message);
    }
}

// Leaderboard
function updateLeaderboardDisplay(leaderboard) {
    const leaderboardList = document.getElementById('leaderboard-list');
    leaderboardList.innerHTML = '';
    
    if (leaderboard.length === 0) {
        leaderboardList.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No players yet</p>';
        return;
    }
    
    leaderboard.forEach(player => {
        const playerEl = document.createElement('div');
        playerEl.className = 'leaderboard-item';
        playerEl.innerHTML = `
            <div class="rank">#${player.rank}</div>
            <div class="player-info">
                <div class="player-name">${player.name}</div>
                <div class="company-name">${player.company}</div>
            </div>
            <div class="player-stats">
                <div>Balance: $${player.balance.toFixed(2)}</div>
                <div>Inventory: $${player.inventory_value.toFixed(2)}</div>
                <div class="total-value">Total: $${player.total_value.toFixed(2)}</div>
            </div>
        `;
        leaderboardList.appendChild(playerEl);
    });
}

// Menu Functions
function newGame() {
    if (confirm('Start a new game? This will reset all progress!')) {
        if (confirm('Are you ABSOLUTELY sure? This cannot be undone!')) {
            localStorage.removeItem('globalCoalition_userID');
            
            document.getElementById('game-menu-modal').classList.add('hidden');
            location.reload();
        }
    }
}

function resetUserID() {
    if (confirm('Reset your User ID? ALL save files will become inaccessible!')) {
        if (confirm('This will make ALL your saves unreachable. Continue?')) {
            localStorage.removeItem('globalCoalition_userID');
            alert('User ID reset! Reloading...');
            location.reload();
        }
    }
}

// Initialize on load
window.addEventListener('DOMContentLoaded', init);
