# Rummy With Friends

> Play Rummy card game with friends over a network using Python

A multiplayer implementation of the classic Rummy card game. Connect 2-4 players over TCP/IP, play with a graphical interface, and enjoy automatic meld detection and scoring. Built entirely with Python's standard library.


## Features

- **2-4 player multiplayer** over local network or internet
- **Graphical interface** with card images using Tkinter
- **Automatic meld detection** - system identifies valid sets and runs
- **Real-time synchronization** - all players see current game state
- **Standard Rummy rules** - draw, drop, meld, win
- **Zero external dependencies** - uses only Python standard library

## Quick Start

### Prerequisites

- Python 3.7+
- Card image assets (see [Card Assets](#card-assets) below)

### Run the Game

**1. Start the server:**
```bash
python src/server.py
```
Enter number of players (2-4) and click "Start"

**2. Start each client (in separate terminals):**
```bash
python src/client.py
```
Enter server address (`localhost` for local, or server IP) and click "Connect"

**3. Play:**
All players click "Ready" to begin. Take turns drawing and dropping cards to form melds and win!

### Card Assets

Place 52 card images (71×96px recommended) in `assets/cards/` and a card back in `assets/cards_special/gray_back.png`.

**Naming convention:** `<RANK><SUIT>.png` where:
- Ranks: `A`, `2-9`, `T` (10), `J`, `Q`, `K`
- Suits: `H` (Hearts), `C` (Clubs), `S` (Spades), `D` (Diamonds)
- Example: `AS.png`, `7H.png`, `KD.png`

## How to Play

**Objective:** Form melds (sets or runs) and reduce deadwood to win.

**Turn sequence:**
1. **Draw** - Take a card from stock or discard pile
2. **Drop** - Discard one card
3. **Win** (optional) - Declare victory if conditions met

**Melds:**
- **Set:** 3+ cards of same rank (e.g., 7♥ 7♠ 7♦)
- **Run:** 3+ consecutive cards of same suit (e.g., 4♠ 5♠ 6♠)

**Win condition:** Fewer than 2 cards unmelded AND total deadwood < 14 points (e.g., all cards melded, or 1 King remaining)

**Card values:** A=1, 2-9=face value, T=10, J=11, Q=12, K=13


## Installation

### Clone the Repository

```bash
git clone https://github.com/ptanmay143/rummy-with-friends.git
cd rummy-with-friends
```

### Install Tkinter (if needed)

Tkinter is included with Python on Windows/macOS. On Linux:

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install python3-tkinter
```

Verify installation:
```bash
python -m tkinter  # A window should appear
```

## Network Setup

### Local Network (Same Machine)

Use `localhost` as the server address in each client.

### Remote Network (Different Machines)

1. Ensure firewall allows port 65432
2. Use server's IP address in clients
3. Configure port forwarding if needed

## Architecture

**Client-Server model** with TCP sockets:
- **Server** (`src/server.py`) - Manages game state, deck, and turn order. Spawns thread per player.
- **Client** (`src/client.py`) - Tkinter GUI with networking thread for server communication.
- **Protocol** - Length-prefixed messages (4-byte header + payload)

**Key components:**
- Meld detection using permutation analysis
- Deadwood calculation for win validation
- Thread-safe message passing between server and clients

## Configuration

Settings are currently hard-coded in source files:

| Setting | Default | Location |
|---------|---------|----------|
| Server Address | 0.0.0.0 | `server.py` line 55 |
| Server Port | 65432 | `server.py` line 56 |
| Card Size | 71×96px | `client.py` |

To customize, edit the values directly in the source files.


## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and test with multiple players
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## Known Issues

- **Stock deck underflow** - Game may crash when deck empties
- **No server-side validation** - Client can send invalid moves
- **Threading race conditions** - Shared data not fully synchronized
- **UI blocking** - Network operations can freeze the GUI

See the [full issue list](#limitations) below for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.

Copyright © Tanmay Pachpande

---

## Technical Details

<details>
<summary>Expand for implementation details, protocol specification, and advanced topics</summary>

### Protocol Specification

TCP messages use length-prefixed format (4-byte header + payload):

| Command | Direction | Format | Description |
|---------|-----------|--------|-------------|
| `@ID` | Server→Client | `@ID 0` | Assign player number |
| `@STASH` | Server→Client | `@STASH AS` | Add card to hand |
| `@STOCK` | Server→Client | `@STOCK 2H` | Stock pile top card |
| `@DISCARD` | Server→Client | `@DISCARD 3S` | Discard pile top card |
| `@DRAWING` | Server→Client | `@DRAWING` | Draw phase (enable input) |
| `@DROPPING` | Server→Client | `@DROPPING` | Drop phase (enable input) |
| `@IDLE` | Server→Client | `@IDLE` | Waiting (disable input) |
| `@READY` | Client→Server | `@READY;` | Ready for game start |
| `@DRAW` | Client→Server | `@DRAW STOCK/DISCARD` | Draw from pile |
| `@DROP` | Client→Server | `@DROP AS` | Drop card to discard |
| `@END` | Bidirectional | `@END` | Declare/notify game end |

### Code Organization

**`src/server.py`** (259 lines):
- `App` - Tkinter UI for player count input
- `GameServer` - Game state, deck management, player threads
- `Player` - Per-connection handler thread

**`src/client.py`** (453+ lines):
- `App` - Main Tkinter GUI (cards, buttons, status)
- `GameClient` - Network communication thread

### Algorithms

**Meld Detection:**
```python
# Generate all permutations of player's cards
# Check if subsets form valid sets (same rank) or runs (consecutive suit)
# Return optimal partition maximizing melded cards
```

**Deadwood Calculation:**
```python
# Sum card values of non-melded cards
# Win if fewer than 2 unmelded cards AND total < 14 points
```

### Dependencies

All from Python 3 standard library:

- `tkinter` - GUI framework
- `socket` - TCP networking
- `struct` - Binary message encoding
- `threading` - Concurrent connections
- `logging` - Debug output
- `itertools` - Permutations for meld detection

### Testing

**Manual test procedure:**
```bash
# Terminal 1: Server
python src/server.py
# Input: 2, Click: Start

# Terminal 2-3: Clients
python src/client.py
# Input: localhost, Click: Connect, Click: Ready
```

**Test cases:**
- Multiple connections/disconnections
- Meld detection accuracy
- Turn rotation
- Win condition validation
- Network error handling

### Architecture Diagram

```
┌─────────────────────────────────────┐
│  Server (src/server.py)             │
│  ┌─────────────────────────────────┐│
│  │ GameServer                      ││
│  │ ├─ Port 65432                   ││
│  │ ├─ Game state & deck            ││
│  │ └─ Player threads (1 per conn.) ││
│  └─────────────────────────────────┘│
└──────────┬──────────────────────────┘
           │ TCP connections
    ┌──────┼──────┬──────┬──────┐
    ↓      ↓      ↓      ↓      ↓
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│GUI 1│ │GUI 2│ │GUI 3│ │GUI 4│
│     │ │     │ │     │ │     │
└─────┘ └─────┘ └─────┘ └─────┘
Clients (src/client.py)
```

</details>

## Limitations

<details>
<summary>Click to expand known limitations and future improvements</summary>

### Current Limitations

| Issue | Impact |
|-------|--------|
| No server-side win validation | Clients can cheat |
| Stock deck underflow bug | Crashes when deck empty |
| Bare exception handlers | Silent failures, hard to debug |
| Threading race conditions | Potential data corruption |
| UI blocking on network I/O | GUI freezes |
| Hard-coded settings | Not configurable |
| No game persistence | Progress lost on disconnect |

### Future Improvements

**High Priority:**
- Fix stock underflow bug
- Add server-side validation
- Thread synchronization (locks)
- Configuration file support

**Medium Priority:**
- Game state persistence
- Spectator mode
- In-game chat
- Player statistics

**Long Term:**
- Web-based interface
- Mobile app
- AI opponent
- Tournament mode

</details>
