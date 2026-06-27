# Architecture

## Overview

AshesOfHeroes is a 3D/2D hybrid card game built on Python + OpenGL 4.6 (via PyOpenGL) and GLFW. The codebase is organized in four vertical layers that communicate exclusively through an event bus — no layer holds a direct reference to a layer below it except through the dependency injection wired at boot time.

```
┌──────────────────────────────────────────────────────────────┐
│  Bootstrap / Engine                                          │
│  Window · Camera · SceneManager · Input                      │
├──────────────────────────────────────────────────────────────┤
│  Scenes  (battleground_scene, menu_scene)                    │
│  Renderers  (BattlegroundRenderer, MenuRenderer)             │
├──────────────────────────────────────────────────────────────┤
│  View objects  (ViewCard · ViewBoard · ViewDeck · ViewHud …) │
│  Primitives    (CardStack · Entity3D · Cylinder · Sphere …)  │
├──────────────────────────────────────────────────────────────┤
│  Logic  (Board · CardDeck · GameState · MatchLogic …)        │
│  Contracts  (Card · Effect · EntityCard …)                   │
└──────────────────────────────────────────────────────────────┘
```

## Directory map

```
src/
├── bootstrap/          Engine construction (Bootstrap, EngineBuilder)
├── core/
│   ├── engine.py       Main loop, input wiring, camera tick
│   ├── event.py        EventManager singleton (pub/sub)
│   ├── input.py        GLFW callback adapter
│   ├── scene.py        SceneManager stack + Scene ABC
│   ├── animation.py    AnimationQueue
│   └── scenes/         Concrete scene implementations
├── graphics/
│   ├── camera.py       Orbital camera, perspective toggle, projection helpers
│   ├── vertex.py       VertexLayout / VertexAttribute descriptors
│   ├── texture_manager.py  Texture cache (load-once, bind-by-path)
│   ├── slots.py        Slot data classes (BattleSlot, InventorySlot, …)
│   ├── layouts/        BoardLayout — slot grid geometry and ray-hit
│   ├── objects/        High-level view objects (own their draw logic)
│   ├── primitives/     Low-level geometry helpers (Entity3D, shapes)
│   └── rendering/      Renderer + scene-level renderers
├── logic/              Pure-Python game rules (no GL)
├── handlers/           Event handlers that bridge logic ↔ graphics
└── mechanics/          High-level match flow
shaders/
├── objects/            Per-object vertex+fragment pairs
└── scenes/             Scene-level (background, HUD) shaders
lib/
├── events.py           Events enum
└── types.py            GameSide, SlotOwner, CardClass, … enums
```

## Boot sequence

```
main.py
  └─ EngineBuilder.build()         # declarative config
       └─ Bootstrap.build()
            ├─ EventManager()       # singleton
            ├─ Window(glfw)
            ├─ Camera()
            ├─ services dict        # DI container
            ├─ SceneManager()
            └─ Engine(window, events, scenes, camera, services)
                  └─ SceneManager.push_by_key("battleground")
                        └─ BattlegroundScene.on_enter()
                              └─ BattlegroundRenderer.load_assets()
```

## Main loop

```
Engine.run()
  while not should_close:
    dt = tick()
    window.poll_events()          # fires GLFW callbacks → Input → Engine → SceneManager
    camera.update(dt)             # lerp orbital rotation
    scenes.update(dt)             # top-of-stack scene only
    glClear(…)
    scenes.render()               # top-of-stack scene only
    window.swap_buffers()
```

## Input chain

```
GLFW callback
  └─ Input._mouse_click_callback(button, action, mods)
       ├─ PRESS   → Engine.__on_mouse_click  → scenes.on_mouse_click
       │          → Engine.__on_mouse_press   → scenes.on_mouse_press
       └─ RELEASE → Engine.__on_mouse_release → scenes.on_mouse_release
                         └─ BattlegroundScene.on_mouse_release
                               └─ BattlegroundRenderer.on_mouse_release
                                     └─ ViewInventory.on_mouse_release
```

## Event bus

`EventManager` is a `Singleton` keyed on `Events` (enum). Every cross-layer communication goes through `emit` / `subscribe` / `unsubscribe`. View objects subscribe on `load_assets` and unsubscribe on `unload_assets` so there are no dangling callbacks after a scene exit.

Key events:

| Event | Producer | Consumer |
|---|---|---|
| `CARD_DRAWN` | `ViewDeck` | `ViewInventory` |
| `CARD_PLACED` | `ViewInventory` | `ViewBoard` |
| `CARD_REMOVED` | game logic | `ViewInventory` |
| `TURN_END_REQUESTED` | `ViewDeck` (turn button) | `Engine` → `Camera.rotate_perspective` |
| `DECK_LOADED` | game logic | `ViewDeck` |

See [`EVENTS.md`](EVENTS.md) for full catalog and payload shapes.

## Coordinate systems

| Space | Origin | Units | Used by |
|---|---|---|---|
| World 3D | center of board | meters (~1 unit ≈ 1 card width) | Board, Deck, Camera |
| Screen 2D | top-left (0,0) | pixels | Inventory, HUD, Fonts |
| NDC | center | −1…+1 | Shaders (gl_Position) |

The `Camera` class exposes three matrices:
- `projection()` — perspective (FOV 30°, 1280×720)
- `view()` — `glm.lookAt` from orbital eye position
- `ortho()` — `glm.ortho(0, W, H, 0, -1, 1)` for 2D screen-space rendering

See [`OPENGL.md`](OPENGL.md) for how these matrices flow into shaders.
