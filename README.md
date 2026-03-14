<h1 align="center">
    <a href="https://github.com/ptanmay143/rummy-with-friends">
        <img src="docs/images/logo.svg" alt="Logo" width="100" height="100">
    </a>
</h1>

<div align="center">
    Rummy With Friends
    <br />
    <a href="#about"><strong>Explore the screenshots »</strong></a>
    <br />
    <br />
    <a href="https://github.com/ptanmay143/rummy-with-friends/issues/new?assignees=&labels=bug&template=01_BUG_REPORT.md&title=bug%3A+">Report a Bug</a>
    ·
    <a href="https://github.com/ptanmay143/rummy-with-friends/issues/new?assignees=&labels=enhancement&template=02_FEATURE_REQUEST.md&title=feat%3A+">Request a Feature</a>
    ·
    <a href="https://github.com/ptanmay143/rummy-with-friends/issues/new?assignees=&labels=question&template=04_SUPPORT_QUESTION.md&title=support%3A+">Ask a Question</a>
</div>

<div align="center">
<br />

[![Project license](https://img.shields.io/github/license/ptanmay143/rummy-with-friends.svg?style=flat-square)](LICENSE)
[![Pull Requests welcome](https://img.shields.io/badge/PRs-welcome-ff69b4.svg?style=flat-square)](https://github.com/ptanmay143/rummy-with-friends/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
[![code with love by ptanmay143](https://img.shields.io/badge/%3C%2F%3E%20with%20%E2%99%A5%20by-ptanmay143-ff1414.svg?style=flat-square)](https://github.com/ptanmay143)

</div>

<details open="open">
<summary>Table of Contents</summary>

- [About](#about)
  - [Built With](#built-with)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Roadmap](#roadmap)
- [Support](#support)
- [Project Assistance](#project-assistance)
- [Contributing](#contributing)
- [Authors & contributors](#authors--contributors)
- [Security](#security)
- [License](#license)
- [Acknowledgements](#acknowledgements)

</details>

---

## About

Rummy With Friends is a multiplayer desktop card game implementation of Rummy using a TCP client-server architecture. Players run a central Python server and connect multiple Tkinter-based clients to play turn-based rounds over a local or remote network.

The project is built for lightweight multiplayer experimentation: no third-party frameworks, no game engine, and no database. All networking, game-state updates, UI rendering, and protocol handling are implemented with Python standard-library modules.

Game progression follows an explicit command protocol where the server assigns IDs, distributes cards, controls turn state (`@DRAWING`, `@DROPPING`, `@IDLE`), and broadcasts discard updates. Clients render cards, send draw/drop actions, and evaluate local meld/deadwood conditions to enable end-game signaling.

A key design tradeoff is simplicity over strict authority. The server manages deck/turn flow, while parts of winner logic are client-driven. This makes development approachable but also introduces trust and validation constraints that should be considered before public deployment.

<details>
<summary>Screenshots</summary>
<br>

Add screenshots to `docs/images/` if you want visual previews in this README.

|                               Server Window                               |                               Client Window                               |
| :-----------------------------------------------------------------------: | :-----------------------------------------------------------------------: |
| <img src="docs/images/screenshot.png" title="Server Window" width="100%"> | <img src="docs/images/screenshot.png" title="Client Window" width="100%"> |

</details>

### Built With

- **Python 3** — runtime for server, client, and game logic.
- **Tkinter / ttk** — desktop GUI for server controls and card-table client UI.
- **socket** — TCP communication between server and clients.
- **struct** — 4-byte length-prefixed message framing.
- **threading** — per-player communication concurrency.
- **itertools.permutations** — meld/deadwood evaluation on client side.

---

## Getting Started

Setup requires Python plus local card image assets. The game starts by launching one server and then one client per player.

### Prerequisites

- **Python 3.7+** with Tkinter available.
- **Card assets** in the expected local folders:
  - `assets/cards/` for 52 face cards.
  - `assets/cards_special/gray_back.png` for card back.

Card naming format must match runtime lookups in `client.py`:

```text
<RANK><SUIT>.png
Ranks: A,2,3,4,5,6,7,8,9,T,J,Q,K
Suits: H,C,S,D
Examples: AS.png, 7H.png, KD.png
```

### Installation

1. Clone the repository.

```bash
git clone https://github.com/ptanmay143/rummy-with-friends.git
```

2. Enter the project directory.

```bash
cd rummy-with-friends
```

3. Verify Tkinter support.

```bash
python -m tkinter
```

4. Start the server.

```bash
python src/server.py
```

5. In server UI, enter number of players and click **Start**.

6. Launch each client in a separate terminal.

```bash
python src/client.py
```

7. In each client, enter server address and click **Connect**, then **Ready**.

### Environment Variables

No environment variables are used.

| Variable | Required | Default | Description                                           | Example Value |
| -------- | -------- | ------- | ----------------------------------------------------- | ------------- |
| None     | No       | N/A     | Network and gameplay config are hard-coded in source. | N/A           |

---

## Usage

Start server:

```bash
python src/server.py
```

Start each client:

```bash
python src/client.py
```

Network defaults:

- Server bind address: `0.0.0.0`
- Server port: `65432`

Gameplay sequence:

1. Server deals 10 cards to each connected player and initializes discard pile.
2. Active player receives `@DRAWING` and can draw from `STOCK` or `DISCARD`.
3. After draw, active player receives `@DROPPING` and must drop one card.
4. Turn advances to next player with `@DRAWING`.
5. Client computes meld/deadwood after drops and enables **End** when win criteria pass.

Win criteria in current client logic:

- Fewer than 2 deadwood cards.
- Deadwood score < 14.

Protocol summary examples:

```text
Server -> Client: @ID 0
Server -> Client: @STASH AS
Client -> Server: @DRAW STOCK
Client -> Server: @DROP 7H
Client -> Server: @END
```

Framing format for all messages:

```text
[4-byte big-endian message length][UTF-8 payload]
```

---

## Roadmap

See the [open issues](https://github.com/ptanmay143/rummy-with-friends/issues) for a full list of proposed features and known bugs.

- [Top Feature Requests](https://github.com/ptanmay143/rummy-with-friends/issues?q=label%3Aenhancement+is%3Aopen+sort%3Areactions-%2B1-desc) (Add your votes using the 👍 reaction)
- [Top Bugs](https://github.com/ptanmay143/rummy-with-friends/issues?q=is%3Aissue+is%3Aopen+label%3Abug+sort%3Areactions-%2B1-desc) (Add your votes using the 👍 reaction)
- [Newest Bugs](https://github.com/ptanmay143/rummy-with-friends/issues?q=is%3Aopen+is%3Aissue+label%3Abug)

Likely future work includes server-authoritative move validation, safer stock/deck rollover logic, synchronization hardening, and optional persistence/rejoin support.

---

## Support

Reach out to the maintainer at one of the following places:

- [GitHub issues](https://github.com/ptanmay143/rummy-with-friends/issues/new?assignees=&labels=question&template=04_SUPPORT_QUESTION.md&title=support%3A+)
- Contact options listed on [this GitHub profile](https://github.com/ptanmay143)

---

## Project Assistance

If you want to say **thank you** or support active development of Rummy With Friends:

- Add a [GitHub Star](https://github.com/ptanmay143/rummy-with-friends) to the project.
- Share reproducible multiplayer test scenarios in issue reports.
- Contribute protocol stability or gameplay-rule improvements.

Together, we can make Rummy With Friends **better**!

---

## Contributing

First off, thanks for taking the time to contribute! Contributions are what make the open-source community such an amazing place to learn, inspire, and create.

Suggested process:

1. Fork and branch from `master`.
2. Apply focused changes (server, client, protocol, or UI).
3. Test with at least two clients against one server.
4. Provide clear reproduction for gameplay/network fixes.
5. Open a pull request.

No dedicated `docs/CONTRIBUTING.md` file exists currently.

---

## Authors & Contributors

The original setup of this repository is by [Tanmay Pachpande](https://github.com/ptanmay143).

For a full list of all authors and contributors, see [the contributors page](https://github.com/ptanmay143/rummy-with-friends/contributors).

---

## Security

Rummy With Friends follows good practices of security, but 100% security cannot be assured. Rummy With Friends is provided **"as is"** without any **warranty**. Use at your own risk.

Current implementation caveats include limited server-side move validation and plaintext TCP communication without authentication/encryption.

---

## License

This project is licensed under the **MIT License**.

See [LICENSE](LICENSE) for more information.

---

## Acknowledgements

- Python and Tkinter communities for robust standard-library tooling.
- Classic Rummy rule sets that inspired gameplay flow.
- Contributors testing multiplayer edge cases and networking behavior.

<!-- Generated by README_GENERATOR_PROMPT v0.1 -->
