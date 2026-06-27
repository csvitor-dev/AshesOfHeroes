# OpenGL Rendering Pipeline

## Stack

| Component | Library |
|---|---|
| Window + event loop | GLFW (via `pyglfw`) |
| OpenGL bindings | PyOpenGL 3.x |
| Math | pyglm (GLM port) |
| Texture loading | Pillow (PIL) |
| GLSL version | 4.60 |

## Renderer

`src/graphics/rendering/renderer.py` is the single point of contact with raw OpenGL buffer and program objects.

```
Renderer
 ├─ __buffers: dict[str, BufferSet]   # VAO + VBO + optional EBO
 └─ __programs: dict[str, int]        # compiled GLSL programs
```

**Program key convention**: `f"{scope}_{filename}"` — e.g. `"objects_card"` for `shaders/objects/card.{vertex,fragment}.glsl`.

### Uploading geometry

```python
renderer.upload(
    name="my_quad",        # string key
    vertices=np.array(…),  # flat float32 array
    layout=VertexLayout(…),
    indices=np.array(…),   # optional EBO; omit for glDrawArrays
)
```

Internally this calls `glGenVertexArrays`, `glGenBuffers`, `glBufferData`, then `VertexLayout.bind()` which iterates attributes and calls `glVertexAttribPointer` + `glEnableVertexAttribArray` for each one.

### Drawing

```python
renderer.draw("my_quad")                    # glDrawElements or glDrawArrays
renderer.draw("my_quad", mode=GL_LINES)     # mode override
renderer.draw_instanced("my_quad", count=N) # instanced draw
```

### VertexLayout

`src/graphics/vertex.py` describes the in-memory layout of a vertex buffer:

```python
VertexLayout([
    VertexAttribute("position", GL_FLOAT, 3),  # location 0, 12 bytes
    VertexAttribute("uv",       GL_FLOAT, 2),  # location 1,  8 bytes
])  # stride = 20 bytes
```

Each attribute maps to a `layout(location = N)` input in the vertex shader. The location index is the position in the `attributes` list (0-based).

## Shader programs

Shaders live in `shaders/<scope>/<name>.{vertex,fragment}.glsl`. They are loaded with `renderer.load_program(scope, name)` and referenced later as `renderer.use(f"{scope}_{name}")`.

### Card shader (unified 2D + 3D)

`shaders/objects/card.{vertex,fragment}.glsl` handles both the inventory (2D screen-space) and the board/deck (3D world-space) with a single program.

**Vertex shader**
```glsl
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 uv;

uniform mat4 projection;
uniform mat4 camera;    // identity mat4 for 2D, view matrix for 3D
uniform mat4 model;
uniform float face_flip; // 0.0 = normal UV, 1.0 = flip V axis

out vec2 out_uv;

void main() {
    gl_Position = projection * camera * model * vec4(position, 1.0);
    out_uv = vec2(uv.x, mix(uv.y, 1.0 - uv.y, face_flip));
}
```

**Fragment shader**
```glsl
in vec2 out_uv;
uniform sampler2D u_texture;
uniform vec4 color_tint;
uniform float alpha;
uniform float glow;        // 0..1 adds golden highlight

void main() {
    vec4 texel = texture(u_texture, out_uv);
    if (texel.a < 0.05) discard;  // hard alpha cut-out
    vec3 rgb = texel.rgb * color_tint.rgb;
    rgb = mix(rgb, GLOW_COLOR, glow * 0.35);
    fragColor = vec4(rgb, texel.a * color_tint.a * alpha);
}
```

**`face_flip` uniform** solves the UV orientation problem for RED-side cards. Because the camera rotates 180° when switching perspective, cards placed on the opponent's side would appear upside-down. Setting `face_flip = 1.0` flips the V coordinate in the shader without duplicating geometry or textures.

| Situation | `camera` uniform | `face_flip` |
|---|---|---|
| Inventory (2D) | `glm.mat4(1.0)` (identity) | `0.0` |
| BLUE deck / BLUE board slots | view matrix | `0.0` |
| RED deck / RED board slots | view matrix | `1.0` |

### Other shaders

| Key | Scope/File | Purpose |
|---|---|---|
| `objects_aegis` | `objects/aegis` | 3D hero aegis (colored geometry, phong-like) |
| `objects_board` | `objects/board` | Board slot quads and borders |
| `objects_slot` | `objects/slot` | Slot highlight overlay |
| `scenes_battleground` | `scenes/battleground` | 2D background primitives (HUD, inventory slots) |
| `scenes_menu` | `scenes/menu` | Menu background |
| `fonts_text` | `fonts/text` | SDF-like bitmap text rendering |

## Rendering layers per frame

```
Engine.__render()
  glClear(COLOR | DEPTH)
  SceneManager.render()
    BattlegroundScene.render()
      BattlegroundRenderer.render(proj3d, view, proj2d)
        ┌─ _render_3d(proj3d, view)
        │    glEnable(GL_DEPTH_TEST)
        │    ViewBoard.render()        ← slot quads, placed cards (draw_3d)
        │    ViewDeck.render()         ← tray geometry, stacked cards (draw_3d)
        │    ViewAegis.render()        ← hero aegis cylinders/spheres
        │
        ├─ _render_2d(proj2d)
        │    glDisable(GL_DEPTH_TEST)
        │    ViewInventory.render()    ← slot backgrounds, card textures (draw_2d)
        │
        └─ _render_hud(proj2d)
             ViewHud.render()          ← health bars, turn indicator
  window.swap_buffers()
```

## ViewCard — dual representation

A single `ViewCard` object owns three VAOs:

| VAO | Geometry | Shader | Used when |
|---|---|---|---|
| `_vao_3d` | box (pos3 + color3 + normal3, 9 floats/vertex) | `objects_aegis` | Always in `draw_3d` |
| `_vao_face` | flat textured quad (pos3 + uv2, 5 floats/vertex) | `objects_card` | In `draw_3d` when `proj`/`view` provided |
| `_vao_2d` | screen-space quad (pos3 + uv2) | `objects_card` | `draw_2d` for inventory display |

`_vao_3d` is managed manually (raw `glGenVertexArrays`/`glDeleteVertexArrays`) because its vertex layout differs from the central `Renderer`'s managed buffers. `_vao_face` and `_vao_2d` go through `Renderer.upload` / `Renderer.delete`.

## Camera

```
Camera
 ├─ projection()  glm.perspective(fov=30°, aspect, near=0.1, far=100.0)
 ├─ view()        glm.lookAt(eye, center, up=Z)
 └─ ortho()       glm.ortho(0, W, H, 0, -1, 1)   # Y-down screen space
```

Eye position is orbital at radius 9, Z=12. BLUE sits at angle 270° (−Y), RED at 90° (+Y). Rotation is triggered by `TURN_END_REQUESTED` and interpolated with ease-in-out over ~0.55 s.

## Ray casting

`unproject_ray` (defined in `view_deck.py`, imported where needed) converts a screen-space mouse position into a world-space ray:

```python
inv = glm.inverse(proj * view)
near = inv * glm.vec4(ndc_x, ndc_y, -1.0, 1.0)
far  = inv * glm.vec4(ndc_x, ndc_y,  1.0, 1.0)
ray_origin = vec3(near) / near.w
ray_dir    = normalize(vec3(far) / far.w - ray_origin)
```

`BoardLayout.ray_hit` then tests the ray against each `BattleSlot`'s bounding rectangle at the slot's Z plane using a ray-plane intersection.

## Texture management

`TextureManager` keeps a `dict[path, gl_texture_id]` cache. `load(path)` calls `PIL.Image.open`, uploads with `glTexImage2D` (RGBA, UNSIGNED_BYTE), and sets linear filtering. `bind(path, slot=0)` calls `glActiveTexture(GL_TEXTURE0 + slot)` then `glBindTexture`. PIL does **not** flip the image on load — UV convention: `(0,0) = image top`.
