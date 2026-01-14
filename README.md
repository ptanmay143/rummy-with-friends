# Rummy With Friends

## Project Title

Rummy With Friends - Multiplayer Card Game

## Overview

A Python-based implementation of the Rummy card game with network multiplayer support. Players connect to a central TCP server via graphical client applications and participate in turn-based gameplay with real-time board synchronization. The system implements standard Rummy rules including automatic meld detection, deadwood calculation, and win condition validation.

**Supported Players**: 2-4 players on same network or remote with port forwarding

**Architecture**: TCP socket-based server-client with threading for concurrent player connections

## Architecture Overview

The system uses a client-server architecture with TCP sockets and threading:

```
┌─────────────────────────────────────┐
│  Server Process (src/server.py)     │
│  ┌─────────────────────────────────┐│
│  │ GameServer Class                ││
│  │ ├─ Listen on port 65432         ││
│  │ ├─ Accept player connections    ││
│  │ ├─ Manage game state            ││
│  │ └─ Broadcast state to players   ││
│  └─────────────────────────────────┘│
│              │                       │
│      ┌───────┼───────┬───────┐      │
│      │per    │per    │per    │      │
│     thread  thread  thread  thread  │
│      ↓       ↓       ↓       ↓      │
│  ┌────┐  ┌────┐  ┌────┐  ┌────┐   │
│  │Plr1│  │Plr2│  │Plr3│  │Plr4│   │
│  │Hdlr│  │Hdlr│  │Hdlr│  │Hdlr│   │
│  └────┘  └────┘  └────┘  └────┘   │
└─────────────────────────────────────┘
      TCP      TCP      TCP      TCP
      ↓        ↓        ↓        ↓
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ Client1 │ │ Client2 │ │ Client3 │ │ Client4 │
│  (GUI)  │ │  (GUI)  │ │  (GUI)  │ │  (GUI)  │
└─────────┘ └─────────┘ └─────────┘ └─────────┘
```

**Components**:
- **Server** (server.py): GameServer manages deck, discard pile, turn state; Player handlers manage per-client communication
- **Clients** (client.py): GameClient handles networking; App manages Tkinter GUI with card display and game state rendering
- **Communication**: Length-prefixed TCP messages (4-byte header + payload) with structured protocol
- **Game Logic**: Meld detection (permutation-based), deadwood calculation, win validation

## Installation and Setup

### Prerequisites

- Python 3.7 or higher
- Tkinter (included with Python on Windows/macOS; install separately on Linux)
- Card image assets (must be provided separately)

### Step 1: Clone Repository

```bash
git clone https://github.com/ptanmay143/rummy-with-friends.git
cd rummy-with-friends
```

### Step 2: Verify and Place Card Assets

Card images must be placed in correct directories:

```
assets/
├── cards/
│   ├── AS.png, 2S.png, ..., KS.png  (Spades)
│   ├── AH.png, 2H.png, ..., KH.png  (Hearts)
│   ├── AC.png, 2C.png, ..., KC.png  (Clubs)
│   ├── AD.png, 2D.png, ..., KD.png  (Diamonds)
│   └── (Total: 52 card files)
└── cards_special/
    └── gray_back.png  (Card back design)
```

**Naming Convention**:
- Format: `<RANK><SUIT>.png`
- Ranks: A (Ace), 2-9, T (10), J (Jack), Q (Queen), K (King)
- Suits: H (Hearts), C (Clubs), S (Spades), D (Diamonds)
- Recommended size: 71×96 pixels (standard poker aspect ratio)

### Step 3: Verify Python and Tkinter

```bash
python --version              # Verify Python 3.7+
python -m tkinter             # Verify Tkinter (window should appear)
```

**Install Tkinter if missing**:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install python3-tkinter

# macOS
# Usually included; if not: brew install python-tk

# Windows
# Usually included; reinstall Python if missing
```

### Step 4: Run Server

```bash
python src/server.py
```

Expected output: Tkinter window with input field for player count and "Start" button.

### Step 5: Run Clients (Separate Terminals)

```bash
python src/client.py
```

Repeat in additional terminals for each player.

### Step 6: Connect and Play

1. **Server terminal**: Enter player count (e.g., `2`) and click "Start"
2. **Each client terminal**: Enter server address and click "Connect"
   - Local: `localhost`
   - Remote: `<server-ip-address>`
3. **All clients**: Click "Ready" button to start game

## Configuration

### Current Hard-Coded Settings

| Setting | Value | Location |
|---------|-------|----------|
| Server Port | 65432 | server.py line 51 |
| Server Bind Address | 0.0.0.0 | server.py line 50 |
| Card Size | 71×96 pixels | client.py |
| Message Buffer Size | 1024 bytes | server.py, client.py |

### To Customize

**Change Server Port**:
```python
# server.py, __init__ method
self.port = 65432  # Change this value
```

**Change Player Count**:
```python
# server.py, run() method
self.n_players = int(self.app.n_players_input_str.get())
```

**Change Card Size** (client.py):
Modify card image loading and display dimensions.

## Usage

### Game Rules (Standard Rummy)

**Deal**: Each player receives 10 cards. One card placed in discard pile.

**Turn Sequence**:
1. **Draw Phase**: Choose to draw from Stock (main deck) or Discard pile
2. **Drop Phase**: Must drop exactly one card to discard pile
3. **Win Check**: Can declare win if melds + deadwood meet criteria

**Meld Types**:
- **Set**: 3+ cards of same rank (e.g., 3♥, 3♠, 3♦)
- **Run**: 3+ consecutive cards of same suit (e.g., 4♠, 5♠, 6♠)

**Card Values**:
- Ace (A) = 1 point
- Number cards (2-9) = face value
- Ten (T) = 10 points
- Face cards (J, Q, K) = 11, 12, 13 points

**Win Condition**: All cards melded (zero deadwood) OR total deadwood ≤ 1 point

### Network Communication Protocol

TCP messages use length-prefixed format (4-byte header + payload):

| Command | Direction | Format | Meaning |
|---------|-----------|--------|---------|
| @ID | S→C | @ID 0 | Assign player number |
| @STASH | S→C | @STASH AS | Add card to hand |
| @STOCK | S→C | @STOCK 2H | Stock pile top card |
| @DISCARD | S→C | @DISCARD 3S | Discard pile top card |
| @DRAWING | S→C | @DRAWING | Draw phase (enable input) |
| @DROPPING | S→C | @DROPPING | Drop phase (enable input) |
| @IDLE | S→C | @IDLE | Waiting (disable input) |
| @READY | C→S | @READY | Ready for game start |
| @DRAW | C→S | @DRAW STOCK/DISCARD | Draw from pile |
| @DROP | C→S | @DROP AS | Drop card |
| @END | C→S/S→C | @END | Declare game end |

## Dependencies

All dependencies from Python 3 standard library:

| Module | Purpose |
|--------|---------|
| `tkinter` | GUI framework and widgets |
| `socket` | TCP network communication |
| `struct` | Message length serialization |
| `threading` | Concurrent client handlers (server) |
| `logging` | Debug output |
| `itertools` | Permutation generation (meld detection) |

No external packages required - minimal setup.

## Development and Testing

### Code Organization

**server.py** (259 lines):
- `App` class - Tkinter UI for player count input
- `GameServer` class - Game state management, player threads, deck
- `Player` class - Per-connection handler thread

**client.py** (453+ lines):
- `App` class - Main Tkinter GUI (card display, buttons, status)
- `GameClient` class - Network communication thread

### Key Algorithms

**Meld Detection**:
- Generate all permutations of player's cards
- Check if subsets form valid sets or runs
- Return optimal partition maximizing melded cards

**Deadwood Calculation**:
- Sum card values of non-melded cards
- Compare against win threshold (≤1 points)

**Card Ranking**:
- Ace < 2-9 < 10 < J < Q < K for runs
- Ace value = 1 point for deadwood

### Code Quality Observations

✓ Separation: Server handles state, client handles UI
✓ Threading: Concurrent player connections
✓ Message Protocol: Structured communication format
✓ Standard Library: Minimal dependencies

⚠ Broad exception handlers mask errors
⚠ No server-side validation of player actions
⚠ Hard-coded network settings
⚠ UI can freeze during network operations
⚠ Race conditions possible on shared data
⚠ No game state persistence

### Testing

**Manual Test Procedure**:
```bash
# Terminal 1: Server
python src/server.py
→ Input: 2
→ Click: Start

# Terminal 2: Client 1
python src/client.py
→ Input: localhost
→ Click: Connect
→ Click: Ready

# Terminal 3: Client 2
python src/client.py
→ Input: localhost
→ Click: Connect
→ Click: Ready

# Verify: Cards deal, turn progression, meld detection works
```

**Recommended Test Cases**:
- Multiple client connections/disconnections
- Valid/invalid meld detection
- Deadwood calculation accuracy
- Correct turn order rotation
- Message delivery to all players
- Graceful client disconnection
- Edge cases (empty stock deck, repeated cards)

## Deployment

### Local Multiplayer (Same Machine)

```bash
# Terminal 1: Server
python src/server.py → [2] → [Start]

# Terminal 2: Client 1
python src/client.py → [localhost] → [Connect] → [Ready]

# Terminal 3: Client 2
python src/client.py → [localhost] → [Connect] → [Ready]
```

### Network Multiplayer (Different Machines)

```bash
# Machine A (Server)
python src/server.py → [2] → [Start]

# Machine B (Client 1)
python src/client.py → [<Machine-A-IP>] → [Connect] → [Ready]

# Machine C (Client 2)
python src/client.py → [<Machine-A-IP>] → [Connect] → [Ready]
```

**Networking Requirements**:
- Firewall allows port 65432
- Machines on same network or port forwarding configured
- Server machine has stable connection (disconnect ends all games)

### Production Considerations

1. Daemonize server (use nohup or systemd)
2. Redirect output to log file
3. No state persistence - games lost on crash
4. Resource-bound at ~10 players max
5. No authentication - firewall required

## Limitations and Future Improvements

### Limitations

| Issue | Severity | Impact |
|-------|----------|--------|
| No server-side win validation | High | Malicious clients can cheat |
| Stock deck underflow bug | High | Game crashes when empty |
| No meld validation on server | High | Invalid melds accepted |
| Bare exception handlers | Medium | Silent failures, hard to debug |
| Threading race conditions | Medium | Potential data corruption |
| UI blocking on network I/O | Medium | GUI freezes during operations |
| No graceful disconnection | Medium | Clients crash/hang on disconnect |
| Hard-coded settings | Medium | Not configurable without code edit |
| No game persistence | Low | Games lost on crash/disconnect |
| No spectator mode | Low | Cannot observe without playing |

### Known Issues

1. **Stock Deck Underflow** (server.py):
   - Current: `.reverse()` returns None (bug)
   - Fix: Use `.reverse()` correctly or `[::-1]`

2. **No Server-Side Meld Validation**:
   - Current: Accepts @END without checking
   - Fix: Add meld detection on server before accepting win

3. **Race Conditions** (shared data):
   - Current: No thread synchronization
   - Fix: Use threading.Lock for shared state

### Future Improvements

**Short Term (High Value)**:
- [ ] Fix stock underflow bug
- [ ] Add server-side meld validation
- [ ] Implement thread-safe data structures (Lock/RLock)
- [ ] Add configuration file (JSON/YAML)
- [ ] Write unit tests for meld detection

**Medium Term**:
- [ ] Game state persistence (save/resume)
- [ ] Spectator mode & game replay
- [ ] In-game chat
- [ ] Player statistics & rankings
- [ ] Difficulty levels & AI opponent

**Long Term**:
- [ ] Database for persistent stats
- [ ] Web-based interface (Flask/Django)
- [ ] Mobile app
- [ ] Tournament mode
- [ ] Streaming/video recording

## Contribution Guidelines

1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Make improvements with clear commits
4. Test thoroughly with multiple players
5. Submit pull request

## License

MIT License - See [LICENSE](LICENSE) file for complete terms.

**Copyright**: Tanmay Pachpande

**Permissions**: Commercial use, modification, distribution, private use

**Conditions**: License and copyright notice must be included

**Limitations**: No liability or warranty
