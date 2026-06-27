# Card System

## Logic layer

Cards in the game-rules layer live under `src/logic/`:

```
contracts/card.py       Card ABC  (id, class, name, cost, …)
cards/
  hero_card.py          HeroCard
  minion_card.py        MinionCard
  turret_card.py        TurretCard
  spell_card.py         SpellCard
  enchantment_card.py   EnchantmentCard
  item_card.py          ItemCard
  event_card.py         EventCard
card_deck.py            CardDeck  (ordered list + draw/shuffle)
card_cell.py            CardCell  (single board slot occupancy)
```

`CardClass` and `SlotKind` enums live in `lib/types.py` and are shared by both the logic and graphics layers.

## Visual layer — ViewCard

`src/graphics/objects/view_card.py`

A `ViewCard` wraps a logical card and owns all GPU resources needed to draw it. It extends `Entity3D` (which provides `position: glm.vec3` and `model_matrix()`).

### Three VAOs

| Field | Key | Layout | Draw call |
|---|---|---|---|
| `_vao_3d` | raw GL id | pos3 + color3 + normal3 (9 f/v) | `glDrawArrays` via raw bind |
| `_vao_face` | `"card_face_{id}"` | pos3 + uv2 (5 f/v) | `renderer.draw(self._vao_face)` |
| `_vao_2d` | `"card2d_{id}"` | pos3 + uv2 (5 f/v) | `renderer.draw(self._vao_2d)` |

`_vao_face` is a flat quad at `z = CARD_H_3D + 0.001` (just above the card surface). It renders the texture in world space when `draw_3d` is called with `proj` and `view` arguments.

`_vao_2d` is a screen-space quad sized to fit an inventory slot (`SLOT_W - 8` × `SLOT_H - 8` pixels).

### face_flip

```python
self.face_flip: float = 0.0   # 0.0 = BLUE side, 1.0 = RED side
```

Passed to the `card.vertex.glsl` uniform. When `1.0`, the V coordinate is flipped (`1.0 - uv.y`) so cards on the opponent's side appear right-side-up regardless of camera orientation.

### Drawing methods

```python
card.draw_3d(program, proj=None, view=None)
```
Always draws the box body (`_vao_3d`) using the caller's active program. If `proj` and `view` are provided, also renders the textured face by switching to `"objects_card"`, uploading all uniforms, and restoring the caller's program.

```python
card.draw_2d(program, proj)
```
Renders the inventory card. Sets `camera = identity` and `face_flip = 0.0` — orientation is always upright in screen space.

### Card dimensions

| Constant | Value | Where used |
|---|---|---|
| `CARD_W_3D` | 1.04 | ViewCard box and face geometry |
| `CARD_D_3D` | 1.44 | ViewCard box and face geometry |
| `CARD_H_3D` | 0.005 | Card body height (Z extent) |
| `CardStack.CARD_W` | 1.07 | Tray footprint and ray detection |
| `CardStack.CARD_D` | 1.47 | Tray footprint and ray detection |
| `SLOT_W` (inventory) | 90 px | Inventory slot width |
| `SLOT_H` (inventory) | 125 px | Inventory slot height (90/125 ≈ 0.72 ratio) |

The ~0.72 width/height ratio is consistent across all representations.

## Drag-and-drop

Drag state lives entirely in `ViewInventory`:

```python
self._dragging_card: ViewCard | None
self._dragging_from: InventorySlot | None
```

| Event | Method | Effect |
|---|---|---|
| Mouse PRESS over inventory slot | `on_mouse_press` | `card.start_drag(mx, my)` |
| Mouse MOVE | `on_mouse_move` | `card.update_drag(mx, my)` — card follows cursor |
| Mouse RELEASE | `on_mouse_release` | ray-cast to board; emit `CARD_PLACED` or snap back |

On release, `ViewBoard._can_interact(slot)` is passed as a callable filter to `on_mouse_release`. This prevents BLUE from dropping cards on RED slots and vice versa.

## Deck stacks

`CardStack` (`src/graphics/primitives/card_stack.py`) is an `Entity3D` that manages a physical stack of `ViewCard` objects. Cards are pushed face-down in a tray; only the top card is ray-tested for clicks.

```python
stack.push_card(vis)   # sets vis.position relative to stack origin
stack.pop_card()       # returns top ViewCard for transfer to inventory
stack.peek()           # top card without removing
stack.count            # current depth
```

Two stacks exist per match (one per `GameSide`), positioned at `x=5.2, y=±1.1` in world space.

## Board placement

When a card is dropped on a valid board slot (`CARD_PLACED` event):

1. Old `ViewCard` in inventory is deleted (`old_inv_card.delete()` frees all VAOs).
2. `vis.position = glm.vec3(slot.center)` places the card in world space.
3. `slot.card = vis` marks the slot occupied (prevents double-placement).
4. `vis.face_flip` is set to `1.0` for `SlotOwner.OPPONENT` slots, `0.0` for `SlotOwner.PLAYER`.
5. `ViewBoard._render_cards` calls `vc.draw_3d(prog, proj=proj, view=view)` each frame.
