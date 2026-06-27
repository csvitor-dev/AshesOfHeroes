# Event System

## EventManager

`src/core/event.py` — a `Singleton` pub/sub bus. All cross-layer communication goes through it; no layer holds direct references to layers below it.

```python
events = EventManager()   # same instance everywhere (Singleton)

events.subscribe(Events.CARD_DRAWN, my_callback)
events.emit(Events.CARD_DRAWN, card=view_card_instance)
events.unsubscribe(Events.CARD_DRAWN, my_callback)
```

`emit` passes all keyword arguments as a single `dict` to every registered callback:

```python
# emit call:
events.emit(Events.CARD_PLACED, card_id="blue_0", slot_key=key, texture="path.png", card=vc)

# callback signature:
def _on_card_placed(self, data: dict) -> None:
    card_id  = data["card_id"]
    slot_key = data["slot_key"]
    texture  = data["texture"]
    card     = data["card"]
```

> **Common mistake**: calling `emit(Events.FOO, data={...})` will pass `{"data": {...}}` to callbacks instead of the flat dict. Always pass kwargs directly.

Subscriptions should be registered in `load_assets` and removed in `unload_assets` to avoid dangling callbacks after scene transitions.

## Event catalog

### Game flow

| Event | Payload keys | Producer | Consumer |
|---|---|---|---|
| `ACTION_EXIT_GAME` | — | `MenuScene` (ESC) | `Engine` → `window.close_window()` |
| `ACTION_PAUSE_GAME` | — | (reserved) | — |
| `TURN_END_REQUESTED` | — | `ViewDeck` (turn button click) | `Engine` → `camera.rotate_perspective()` |
| `TURN_CHANGED` | — | `MatchLogic` | (HUD update) |
| `TURN_STARTED` | — | `MatchLogic` | — |

### Card lifecycle

| Event | Payload keys | Producer | Consumer |
|---|---|---|---|
| `DECK_LOADED` | `side: GameSide`, `cards: list[dict]` | game logic / `BattleHandler` | `ViewDeck._on_deck_loaded` |
| `DECK_UPDATED` | — | game logic | — |
| `CARD_DRAWN` | `card: ViewCard` | `ViewDeck.on_mouse_click` | `ViewInventory._on_card_drawn` |
| `CARD_PLACED` | `card_id`, `slot_key: SlotKey`, `texture: str`, `card: ViewCard` | `ViewInventory.on_mouse_release` | `ViewBoard._on_card_placed` |
| `CARD_REMOVED` | `card_id` | game logic | `ViewInventory._on_card_removed` |
| `CARD_DAMAGED` | (TBD) | combat system | — |
| `CARD_DESTROYED` | (TBD) | combat system | — |
| `ENTITY_SELECTED` | (TBD) | `ViewBoard` | — |

### Combat

| Event | Payload keys | Producer | Consumer |
|---|---|---|---|
| `ON_ATTACK` | (TBD) | `MatchLogic` | — |
| `LOGIC_COMBAT_RESOLVED` | (TBD) | `MatchLogic` | — |
| `LOGIC_MATCH_SETUP_COMPLETE` | — | `MatchLogic` | — |

### Input (low-level, internal)

| Event | Notes |
|---|---|
| `RAW_INPUT_KEY` | Not currently used; reserved for global hotkey handling |
| `RAW_INPUT_MOUSE` | Not currently used |

## Drag-and-drop flow (CARD_DRAWN → CARD_PLACED)

```
User clicks deck card
  ViewDeck.on_mouse_click
    stack.pop_card() → ViewCard
    EventManager.emit(CARD_DRAWN, card=view_card)
      ViewInventory._on_card_drawn(data)
        slot.card = view_card
        card.move_to(slot position)

User drags card over board slot and releases mouse
  GLFW RELEASE → Input → Engine.__on_mouse_release
    SceneManager.on_mouse_release
      BattlegroundScene.on_mouse_release
        BattlegroundRenderer.on_mouse_release
          ViewInventory.on_mouse_release(mx, my, proj, view, viewport, board_layout, can_interact)
            ray_o, ray_d = unproject_ray(mx, my, proj, view, viewport)
            slot_3d = board_layout.ray_hit(ray_o, ray_d)
            if slot_3d and can_interact(slot_3d) and slot_3d.card is None:
              EventManager.emit(CARD_PLACED, card_id=…, slot_key=…, texture=…, card=…)
                ViewBoard._on_card_placed(data)
                  old_inv_card.delete()
                  vis.position = glm.vec3(slot.center)
                  slot.card = vis
                  vis.face_flip = 1.0 if slot.key.owner == OPPONENT else 0.0
              dragging_from.card = None
            else:
              card.move_to(original slot position)  # snap back
```
