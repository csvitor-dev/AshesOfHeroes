# Ashes of Heroes

A 3D/2D hybrid card game built with Python and OpenGL 4.6.

## Development setup

> [!IMPORTANT]
> This project runs **Python 3.14.3**.

> [!NOTE]
> The steps below assume a Linux environment. For other platforms, see the [virtualenv guide](https://python.land/virtual-environments/virtualenv).

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --require-virtualenv -r requirements.txt

# Run
python main.py

# Deactivate when done
deactivate
```

## About the project

AshesOfHeroes is a turn-based card game rendered with raw OpenGL. The board is a 3D perspective scene; the hand/inventory is a 2D HUD overlay. Cards can be dragged from the deck to the hand and from the hand onto board slots, with per-side restrictions (BLUE cannot interact with RED's deck or slots and vice versa).

Camera rotation animates the perspective switch between players at the end of each turn.

## About the game

Two players — **BLUE** and **RED** — face each other across a board of 7 columns. Each column has two battle rows (one per side) and neutral turret positions. Players draw cards from their deck, place them on their side of the board, and resolve combat.

Card classes: Hero · Minion · Turret · Spell · Enchantment · Item · Event.

## Project structure

```
.
├── assets/
│   ├── cards/heroes/       Card artwork (PNG)
│   └── fonts/              CinzelDecorative TTF
├── docs/                   Architecture and system documentation
├── lib/
│   ├── events.py           Events enum
│   └── types.py            GameSide, CardClass, SlotOwner, … enums
├── shaders/
│   ├── objects/            Per-object vertex + fragment shaders
│   └── scenes/             Scene-level shaders (background, HUD)
├── src/
│   ├── bootstrap/          Engine construction (Bootstrap, EngineBuilder)
│   ├── core/               Engine, SceneManager, EventManager, Input, Camera
│   ├── graphics/
│   │   ├── layouts/        BoardLayout — slot grid and ray-hit
│   │   ├── objects/        High-level view objects (ViewCard, ViewBoard, …)
│   │   ├── primitives/     Low-level geometry (Entity3D, CardStack, shapes)
│   │   └── rendering/      Renderer + scene-level renderers
│   ├── handlers/           Event handlers bridging logic ↔ graphics
│   ├── logic/              Pure-Python game rules (Board, CardDeck, …)
│   └── mechanics/          High-level match flow
├── main.py
└── requirements.txt
```

## Documentation

| Document | Description |
|---|---|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Layer overview, boot sequence, main loop, coordinate systems |
| [`docs/OPENGL.md`](docs/OPENGL.md) | Renderer, VAO/VBO/EBO management, shaders, camera, ray casting |
| [`docs/EVENTS.md`](docs/EVENTS.md) | Event bus, full event catalog, drag-and-drop flow |
| [`docs/SCENES.md`](docs/SCENES.md) | Scene stack lifecycle, input routing |
| [`docs/CARDS.md`](docs/CARDS.md) | ViewCard dual representation, face_flip, drag-and-drop, board placement |
