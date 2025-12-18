# ♠️ Casino Blackjack – Flask Web App

A fully playable Blackjack (21) casino game built with Python and Flask, featuring betting, splits, doubles, insurance, surrender, and a polished UI.
This project was developed as a learning exercise for web development, game logic, and session-based state management.

---

## Game Features

This Blackjack implementation includes:

- 🃏 Standard Blackjack Rules
    - Blackjack pays 3:2
    - Dealer stands on all 17
    - Infinite reshuffled deck
      
- 💰 Bankroll & Betting System
    - Chip-based betting (5 / 25 / 100)
    - Persistent bankroll using Flask sessions

- ✌️ Player Actions
    - Hit
    - Stand
    - Double Down
    - Split (one split max)
    - Late Surrender
    - Insurance (dealer Ace up-card)

- 🔁 Multiple Hands Support
    - Active hand highlighting
    - Independent bet tracking per hand
 
- 🎨 Modern Casino-Style UI
    - Animated cards
    - Responsive layout
    - Visual feedback for game state

---

## 🛠️ Technologies Used

- Python 3.10+
- Flask – backend web framework
- HTML5 / CSS3 – frontend layout and styling
- Vanilla JavaScript – game interaction & API calls
- Flask Sessions – state persistence
- PyCharm / VS Code – recommended IDEs

---

##  📂 Project Structure

- **app.py**
  🎮 Main Flask application
  🧠 Handles game flow, session state, API endpoints
  🔄 Manages betting, player actions, dealer logic, and payouts

- **game,.py**
  🃏 Core Blackjack logic
  ♠️ Deck creation and shuffling
  ➕ Hand value calculation (Ace handling)
  🖤 Blackjack detection

- **templates/index.html**
  🖥️ Main UI layout
  🎯 Buttons, betting controls, and card rendering
  🔗 Connects frontend to backend API

- **static/style.css**
  🎨 Casino-inspired styling
  🟢 Felt table background
  🃏 Card animations and chip visuals
  📱 Responsive design

---

## ## 🛠️ Setup

### Step 1: Clone the Repository

`git clone https://github.com/your-username/BlackJack.git`


### Step 2: Dependencies

Make sure you have Python 3.x installed. You can check your version with:

`python3 --version`

Install Flask:

`pip install flask` 

### Step 3: Run the project

Start the Flask server:

`python app.py`

Open your browser and visit:

`[python app.py](http://127.0.0.1:5000)`

---

## 🕹️ How to Play

- Add chips to your bet
- Click **Deal**
- Use available actions:
  - Hit / Stand
  - Double / Split (when allowed)
  - Insurance if dealer shows Ace
  - Surrender before hitting
- Click **Next Round** to continue
- Use **Reset** to restart with a fresh bankroll

---

## 🤝 Contributing

Contributions are welcome! If you'd like to improve the project, feel free to:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to your branch (`git push origin feature-name`).
5. Submit a pull request.

If you find bugs or have feature requests, please [open an issue](https://github.com/ximenes13/BlackJack/issues).
