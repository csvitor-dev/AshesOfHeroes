# Scene System

## SceneManager

`src/core/scene.py` manages a `deque[Scene]` stack. Only the top scene receives `update` and `render` calls — paused scenes below it are frozen.

```python
manager.push_scene(scene)   # calls current.on_pause(), new.on_enter()
manager.pop_scene()         # calls current.on_exit(), previous.on_resume()
manager.replace_scene(s)    # pop + push without going through on_resume
manager.change_scene(name)  # clears entire stack, pushes named scene
```

Scenes are registered by string key and instantiated lazily:

```python
scenes.register("battleground", lambda: BattlegroundScene(services))
scenes.push_by_key("battleground")
```

## Scene ABC

Every scene extends `Scene` and must implement:

```python
on_enter(**params)      # load assets, subscribe events
on_exit()               # unload assets, unsubscribe events
on_pause()              # hide / suspend
on_resume()             # show / re-activate
update(dt: float)
render()
on_key(key, action, mods)
on_mouse_move(mx, my)
on_mouse_click(button, mx, my)
```

Two optional stubs exist with no-op defaults so subclasses don't have to implement them:

```python
on_mouse_press(mx, my)    # drag start
on_mouse_release(mx, my)  # drag end
```

## BattlegroundScene

`src/core/scenes/battleground_scene.py`

Owns a `BattlegroundRenderer` (created lazily on `on_enter`). Holds references to `Camera`, `GameState`, and `AnimationQueue`. Forwards all input events to the renderer.

```
on_enter()
  BattlegroundRenderer(renderer, events, animations, textures, game_state, camera)
  renderer.load_assets()

render()
  renderer.render(
      proj3d = camera.projection(),
      view   = camera.view(),
      proj2d = camera.ortho(),
  )

on_mouse_release(mx, my)
  renderer.on_mouse_release(mx, my)
```

## MenuScene

`src/core/scenes/menu_scene.py`

Simple 2D menu. On start-game action it calls `scene_manager.change_scene("battleground")`.

## Input routing

Input flows from GLFW to the top-of-stack scene without any branching logic in `SceneManager` — it just forwards to `self.__stack[-1]`. Scenes themselves decide which view objects handle each event.

```
GLFW → Input → Engine.__on_*  →  SceneManager.on_*  →  Scene.on_*  →  Renderer.on_*  →  ViewObject.on_*
```

The renderer layer dispatches to view objects in priority order:

```python
# BattlegroundRenderer.on_mouse_click
btn_hit = self._view_deck.on_mouse_click(…)   # turn button takes priority
if not btn_hit:
    self._view_board.on_mouse_click(…)
self._view_hand.on_mouse_click(…)
```
