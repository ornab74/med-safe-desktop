# Image Asset Generation Loop

## A Prototype Journal for Model-Assisted GUI Asset Creation, Deterministic Fallback Rendering, and Secure Runtime Integration

**Date:** 2026-04-24  
**Project:** MedSafe / HealthDash desktop UI prototype  
**Context:** CustomTkinter desktop application, local image assets, secure asset hashing, high-DPI GUI theming  
**Primary research idea:** A future ChatGPT/OpenAI workflow that can generate a complete list of required UI assets one by one, validate them, place them into a GUI, run the application, inspect screenshots, and iterate until the interface is visually coherent.

---

## Abstract

This document records a small but surprisingly rich prototype that emerged while attempting to improve the visual quality of a Python `customtkinter` desktop application. The user requested a dramatic Tron-inspired redesign of the app, including a new logo, topbar, buttons, hover states, high-DPI quality, transparent backgrounds, and secure hashing, while avoiding Pillow.

The assistant initially implemented a deterministic local PNG generation pipeline in Python rather than using a model-native image generation pipeline. Although this was not exactly what the user intended, it accidentally demonstrated a useful adjacent pattern: a deterministic asset compiler that can create, hash, and validate GUI assets using only the standard library, then wire those assets into a runtime loader.

The subsequent clarification revealed the more important product idea:

> A future assistant should be able to enumerate all required visual assets for a GUI, generate them one by one using an image model, verify transparency and visual constraints, place them into the app, run the app, inspect screenshots, and iterate.

This document describes that loop as a formal system. It also documents what happened in the prototype, where it succeeded, where it failed, and how it can be generalized into a robust asset-generation-and-integration workflow for OpenAI tools.

---

## 1. Motivation

Modern application development increasingly asks language models to perform work that crosses boundaries:

- Code editing
- Visual design
- Asset generation
- Runtime verification
- UX iteration
- Security and integrity checking
- High-DPI correctness
- Platform-specific GUI behavior

Most coding agents are comfortable editing code. Most image models are comfortable producing standalone images. The gap is the loop between them.

For a real app, “make this look incredible” rarely means “generate one image.” It means:

1. Discover the current UI structure.
2. Infer every needed visual asset.
3. Generate assets with consistent style.
4. Save assets into the repo.
5. Wire them into code.
6. Run the app.
7. Inspect the result.
8. Detect stretching, wrong transparency, poor contrast, broken hover states, layout overflow, DPI problems, and mismatched style.
9. Regenerate or adjust only the failed parts.

The prototype showed that an assistant can already approximate pieces of this workflow, but not yet in a clean end-to-end way.

---

## 2. The Original User Goal

The user asked to inspect:

- `images/buttons.png`
- `images/logo.png`
- `images/buttons_topbar.png`
- `main.py`

The desired outcome was:

- New logo
- New topbar
- New buttons
- Transparent logo background
- Removed logo subtitle
- Better high-DPI output
- Hover color changes
- Advanced Tron-like theme
- Secure hashing
- No Pillow
- Broad pass across the whole app

The app already contained a substantial CustomTkinter desktop frontend in `main.py`, including:

- A `SecureButtonAtlas` loader
- Native `tk.PhotoImage` PNG loading
- SHA-256 asset hashing
- Topbar image loading
- Button decoration helpers
- Runtime UI theme constants
- Startup password gate
- Dashboard, medication, safety, dental, exercise, recovery, chat, help, and settings tabs

The existing assets had issues:

- `logo.png` was RGB, not RGBA.
- The logo had a dark background and subtitle text.
- The topbar was a fixed PNG strip.
- The button atlas was visually large but not necessarily active because the loader searched for `img/buttons.png`, while the repo had `images/buttons.png`.
- Some UI colors were hard-coded to the older teal-gray theme.

---

## 3. What Actually Happened

The assistant first read `main.py` and discovered that the app already had secure-ish asset loading logic:

- PNG signature checks
- File size checks
- Path/name restrictions
- Symlink rejection
- SHA-256 hashing
- Tk-native image decoding
- Atlas slicing with `tk.PhotoImage.copy`

The assistant then created a deterministic asset generator:

```text
scripts/generate_tron_assets.py
```

This script wrote PNG files directly using:

- `struct`
- `zlib`
- direct RGBA scanline encoding
- custom vector drawing primitives
- small bitmap font drawing
- signed-distance rounded rectangles
- line, circle, arc, and icon primitives

It generated:

```text
images/logo.png
images/buttons_topbar.png
images/buttons.png
images/theme_manifest.json
```

It also updated `main.py` to:

- Use a new Tron palette
- Load `images/buttons.png`
- Validate assets against `theme_manifest.json`
- Support a 4096x150 high-DPI topbar
- Add active/hover topbar overlays
- Add display scaling
- Remove the fallback subtitle under the logo
- Retheme buttons, checkboxes, scrollbars, and navigation

The implementation passed syntax and hash checks, but one runtime issue appeared:

```text
_tkinter.TclError: wrong # args: should be ".!canvas lower tagOrId ?belowThis?"
```

The cause was subtle:

```python
canvas.lower()
```

On a `tk.Canvas`, `.lower()` means “lower a canvas item/tag,” not “lower this widget behind other widgets.” The correct widget-lowering call was:

```python
self.window.tk.call("lower", str(canvas))
```

This was fixed. A CustomTkinter warning also appeared because `CTkButton` received a raw `tk.PhotoImage` instead of `CTkImage`:

```text
CTkButton Warning: Given image is not CTkImage but <class 'tkinter.PhotoImage'>.
Image can not be scaled on HighDPI displays, use CTkImage instead.
```

Since the user did not want Pillow and `CTkImage` commonly expects PIL images, the assistant removed raw `PhotoImage` attachments from `CTkButton` and retained the color/button styling rather than icon injection.

Finally, the user clarified that they meant image-model-generated assets, not a local Python renderer. The repo was reverted, leaving only this research note as the durable artifact.

---

## 4. The Important Concept Proven

The key insight is not the specific Tron theme.

The important concept is:

> A coding assistant can treat GUI asset generation as a closed-loop optimization problem across language, image, code, and visual verification.

The assistant should not merely generate an image. It should generate an asset plan.

For example:

```text
Required assets:
1. App logo, transparent PNG, 3 sizes
2. Topbar background, normal and hover variants
3. Nav icon set, 10 icons
4. Primary button background, normal/hover/pressed/disabled
5. Secondary button background, normal/hover/pressed/disabled
6. Warning button background, normal/hover/pressed/disabled
7. Danger button background, normal/hover/pressed/disabled
8. Empty-state illustration
9. Splash/loading emblem
10. Settings panel accent strips
```

Then generate each asset separately, with constraints and validation:

```text
Asset: nav_dashboard_icon.png
Prompt: cyber-neon medical dashboard icon, transparent background, cyan line art, square canvas, no text.
Validation:
- alpha channel present
- no non-transparent border
- visible subject coverage between 20% and 75%
- color palette consistent with theme
- no accidental text
- saved at expected path
```

The final step is to wire assets into the GUI and inspect screenshots.

---

## 5. Formal Model

Let the application be represented as:

```text
A = (C, L, S, R)
```

Where:

- `C` is code.
- `L` is layout structure.
- `S` is visual style state.
- `R` is runtime behavior.

Let the asset set be:

```text
X = {x_1, x_2, ..., x_n}
```

Each asset `x_i` has:

```text
x_i = (p_i, m_i, g_i, v_i)
```

Where:

- `p_i` is the prompt or generation specification.
- `m_i` is metadata: size, format, alpha, target path, semantic role.
- `g_i` is the generated bitmap.
- `v_i` is a validation record.

The GUI integration objective can be written as:

```text
maximize    Q(A, X)
subject to  V_i(x_i) = true for all i
            B(A, X) = true
            H(x_i) = expected_hash_i when pinning is required
```

Where:

- `Q(A, X)` is perceived visual quality and usability.
- `V_i` is per-asset validation.
- `B(A, X)` is build/runtime correctness.
- `H` is a cryptographic hash function.

A practical quality function could be decomposed:

```text
Q(A, X) =
    w_c C_contrast
  + w_a C_alignment
  + w_s C_style
  + w_d C_density
  + w_h C_highdpi
  + w_i C_interaction
  - w_o P_overlap
  - w_b P_blur
  - w_t P_text_errors
```

Where:

- `C_contrast` measures readable contrast.
- `C_alignment` measures layout alignment.
- `C_style` measures consistency with the visual direction.
- `C_density` measures whether the UI is neither sparse nor overcrowded.
- `C_highdpi` measures crispness at target DPI.
- `C_interaction` measures hover/focus/active states.
- `P_overlap` penalizes visual overlap.
- `P_blur` penalizes blur or scaling artifacts.
- `P_text_errors` penalizes misspelled/generated text inside assets.

The loop becomes:

```text
X_0 = plan_assets(A_0, user_goal)

for k in 0..K:
    for each missing or failed asset x_i:
        g_i = image_model_generate(p_i)
        v_i = validate(g_i, m_i)

    C_k+1 = integrate_assets(C_k, X_k)
    screenshot_k = run_and_capture(A_k+1)
    e_k = critique(screenshot_k, user_goal, constraints)

    if e_k is acceptable:
        stop

    X_k+1, C_k+1 = repair(e_k)
```

This is not just image generation. It is an agentic control loop.

---

## 6. Asset Generation as a Constraint Satisfaction Problem

For every asset, define a constraint vector:

```text
c_i = [
    width_i,
    height_i,
    alpha_required_i,
    semantic_role_i,
    allowed_palette_i,
    forbidden_colors_i,
    forbidden_text_i,
    safe_area_i,
    target_dpi_i,
    visual_style_i
]
```

The generated image is valid only if:

```text
V_i(g_i, c_i) =
    V_dimensions(g_i)
  ∧ V_alpha(g_i)
  ∧ V_palette(g_i)
  ∧ V_subject_coverage(g_i)
  ∧ V_semantic_match(g_i)
  ∧ V_no_forbidden_artifacts(g_i)
```

For alpha validation:

```text
alpha_coverage =
    count(alpha(p) > tau_alpha) / total_pixels
```

Require:

```text
alpha_min <= alpha_coverage <= alpha_max
```

For transparent corners:

```text
corner_alpha =
    mean(alpha(p) for p in corner_regions)
```

Require:

```text
corner_alpha <= epsilon
```

For palette consistency:

```text
palette_distance =
    min_{q in theme_palette} || RGB(p) - RGB(q) ||_2
```

Mean palette distance should remain below a threshold:

```text
E[palette_distance] <= delta_palette
```

For high-DPI:

```text
scale_ratio = source_pixels / display_pixels
```

Prefer:

```text
scale_ratio >= 2
```

This reduces visible blur when downsampling into UI elements.

---

## 7. The Role of Hashing

Hashing is useful for asset pipelines, but it should not force all assets into a single giant atlas.

In the prototype, the assistant used one large PNG atlas partly because:

- The existing app had an atlas loader.
- A single file is easy to hash.
- Slicing can be deterministic.
- Runtime loading can be restricted to one known image.

However, for a model-generated asset loop, the better design is probably:

```text
assets/
  manifest.json
  logo/
    healthdash-logo@1x.png
    healthdash-logo@2x.png
  nav/
    dashboard.png
    medications.png
    safety.png
  buttons/
    primary-normal.png
    primary-hover.png
    primary-pressed.png
```

With a manifest:

```json
{
  "version": 1,
  "style": "tron-medical-neon",
  "assets": {
    "logo/healthdash-logo@2x.png": {
      "sha256": "...",
      "role": "app_logo",
      "size": [960, 160],
      "alpha": true
    }
  }
}
```

The manifest should be the source of truth. The app should verify:

```text
sha256(file_bytes) == manifest.assets[path].sha256
```

This gives the security benefits of hashing without forcing all UI graphics into a single atlas.

---

## 8. Deterministic Renderer as a Control Path

The accidental Python renderer is still useful.

It acts as a control path:

- No network
- No model nondeterminism
- No copyright or prompt drift risk
- Exact geometry
- Exact colors
- Exact hashes
- Fully reproducible
- Works without Pillow

This is valuable for:

- Placeholder assets
- Emergency fallback assets
- Test fixtures
- Secure offline builds
- Deterministic CI snapshots
- Generating masks or layout guides for image models

A future system might combine both:

```text
deterministic_renderer -> layout masks / guides / placeholders
image_model            -> final expressive assets
validator              -> alpha/hash/size/visual checks
code_agent             -> GUI integration
vision_model           -> screenshot critique
```

The deterministic renderer should not replace the image model. It should scaffold it.

---

## 9. Proposed OpenAI Agent Architecture

A robust asset generation loop could involve the following agents or phases.

### 9.1 Asset Planner

Input:

- User request
- Existing source tree
- UI framework
- Current screenshots if available

Output:

- Asset inventory
- File paths
- Dimensions
- Required states
- Style guide
- Prompt list
- Validation rules

Example:

```text
Asset ID: nav.safety.icon
Path: images/nav/safety@2x.png
Size: 128x128
Alpha: required
States: normal, hover, active
Prompt: cyan Tron-style shield/check medical safety icon, transparent background, no text
Validation: alpha corners transparent, subject centered, cyan dominant, no text
```

### 9.2 Image Generator

Generates assets one by one, not as one giant sheet.

Important requirement:

```text
The model should support true transparent PNG output.
```

Chroma-key generation can work, but it is a workaround. It fails when:

- Edges glow
- Subject contains key color
- Shadows exist
- Glass/reflections exist
- Fine details exist
- The model makes the background uneven

Native transparency would dramatically improve this workflow.

### 9.3 Asset Validator

Checks:

- PNG signature
- Dimensions
- Alpha channel
- Transparent corners
- Subject coverage
- Hash
- File size
- Color palette
- OCR/text artifacts
- Contrast against target UI background

### 9.4 Code Integrator

Edits the GUI code.

For CustomTkinter this may include:

- Loading `CTkImage` where possible
- Avoiding raw `PhotoImage` in `CTkButton` if high-DPI scaling matters
- Preserving references to image objects
- Avoiding stretching raster assets beyond intended display size
- Using native widgets for hover state when possible
- Keeping layout responsive

### 9.5 Runtime Verifier

Runs the app and captures screenshots at:

- Desktop width
- Narrow width
- High-DPI scaling
- Light/dark modes if applicable
- Startup/unlock flow
- Main dashboard
- Each tab
- Hover/active states

### 9.6 Visual Critic

Uses a multimodal model to inspect screenshots and answer:

- Is anything black/blank?
- Are assets stretched?
- Is text readable?
- Are generated words misspelled?
- Are hover states visible?
- Does the logo have unwanted background?
- Do controls overlap?
- Does the app still look like the requested style?

### 9.7 Repair Loop

Failures are mapped back to either:

- Regenerate asset
- Change layout
- Change code loading behavior
- Change color constants
- Change image dimensions
- Change prompt
- Fall back to deterministic renderer

---

## 10. Lessons from the Prototype

### 10.1 Single PNG Atlases Are Tempting but Limiting

The atlas approach has benefits:

- Simple hashing
- One image file
- Fast loading
- Easy slicing

But it has drawbacks:

- Hard to regenerate one failed button
- Easy to stretch/crop incorrectly
- Text inside assets becomes brittle
- Large image prompts tend to produce bad small text
- Hover/active states are better represented as separate assets or runtime styles

For model generation, individual assets are better.

### 10.2 Text Inside Generated UI Assets Is Risky

Image models can make beautiful interfaces, but generated UI text is still fragile. For production GUI assets:

```text
Prefer icon-only or decoration-only generated images.
Render actual labels with the GUI framework.
```

This avoids:

- Misspellings
- Blurry labels
- Inconsistent font rendering
- Accessibility problems
- Localization problems

The best hybrid approach:

```text
image model -> background, icon, frame, ornament, texture
GUI toolkit  -> actual text
```

### 10.3 True Transparency Matters

The user noticed the key limitation immediately:

```text
bg is green not transparent
```

A chroma-key background is not equivalent to native transparency. For GUI asset generation, native alpha output is a core requirement.

### 10.4 High-DPI Is a Runtime Contract

The `CTkButton` warning exposed an important issue:

```text
Given image is not CTkImage but tkinter.PhotoImage.
Image can not be scaled on HighDPI displays.
```

High-DPI support is not only about generating a large PNG. It also requires the GUI framework to load and scale it correctly.

For CustomTkinter, the system should understand:

- `CTkImage`
- widget scaling
- window scaling
- Tk scaling
- image reference lifetime
- platform DPI behavior

### 10.5 Startup/Unlock Flows Must Be Tested

The black screen occurred after unlocking because a new background widget crashed during transition from startup gate to main app.

This shows that visual redesigns must test:

- First boot
- Password unlock
- Password repair
- Main app entry
- Error fallback
- Window teardown/rebuild

The screenshot loop should include all major app states, not only the happy-path dashboard.

---

## 11. A Concrete Future Workflow

An ideal assistant command might look like:

```text
Theme this CustomTkinter app in a Tron medical style.
Generate all required image assets with true transparency.
Wire them into the GUI.
Run the app.
Show me screenshots.
Iterate until it looks good.
```

The assistant should respond with a plan like:

```text
I found 10 tabs, 5 button tones, one logo area, one topbar, and 7 repeated card types.
I will generate 38 assets:
- 1 logo
- 10 nav icons
- 5 button backgrounds x 4 states
- 4 panel accents
- 3 empty states

Then I will integrate them into main.py, run the app, capture screenshots, and repair issues.
```

Then internally:

```text
for asset in asset_manifest:
    generate(asset.prompt)
    validate(asset)
    save(asset.path)

patch_code()
run_app()
capture_screenshots()
critique()
repair()
```

---

## 12. Suggested API/Tool Features

The prototype suggests several features that would make this workflow much stronger.

### 12.1 Native Transparent PNG Generation

Required:

```text
background = transparent
format = png
alpha = true
```

This is foundational for GUI assets.

### 12.2 Structured Asset Batch Generation

Instead of one prompt, allow:

```json
[
  {
    "id": "nav.dashboard",
    "path": "images/nav/dashboard.png",
    "size": "256x256",
    "background": "transparent",
    "prompt": "..."
  },
  {
    "id": "nav.safety",
    "path": "images/nav/safety.png",
    "size": "256x256",
    "background": "transparent",
    "prompt": "..."
  }
]
```

The model/tool should return:

```json
{
  "generated": [
    {
      "id": "nav.dashboard",
      "path": "...",
      "sha256": "...",
      "width": 256,
      "height": 256,
      "alpha": true
    }
  ]
}
```

### 12.3 Built-In Visual Validation

Useful checks:

- transparent corner check
- OCR accidental text check
- bounding box detection
- palette extraction
- contrast check
- blur/sharpness estimate
- safe area check

### 12.4 Screenshot-Aware GUI Repair

The agent should be able to:

- Launch app
- Interact with app
- Hover controls
- Capture screenshot
- Compare screenshot to design goal
- Patch layout/code/assets

### 12.5 Framework-Specific Asset Recipes

For CustomTkinter:

- Use `CTkImage` when high-DPI scaling is required.
- Keep image references alive.
- Prefer text rendered by widgets.
- Prefer generated images for icons, backgrounds, accents.
- Use native button hover colors for interactivity.
- Avoid huge image strips for text-bearing controls.

For web:

- Generate SVG or PNG/WebP depending on asset type.
- Use CSS for text and hover states.
- Use responsive image sizes.

For Qt:

- Use device-pixel-ratio-aware pixmaps.
- Generate `@2x` variants.

---

## 13. Proposed Manifest Schema

```json
{
  "version": 1,
  "theme": {
    "name": "tron-medical-neon",
    "background": "#03070d",
    "accent": "#00d9ff",
    "success": "#40f5b0",
    "warning": "#ffc857",
    "danger": "#ff5f8d"
  },
  "assets": {
    "images/logo/healthdash@2x.png": {
      "id": "logo.healthdash",
      "role": "app_logo",
      "sha256": "...",
      "width": 960,
      "height": 160,
      "alpha": true,
      "generated_by": "image-model",
      "prompt_hash": "...",
      "validated": true
    }
  }
}
```

The code loader should:

```python
def verify_asset(path, manifest):
    data = path.read_bytes()
    digest = sha256(data).hexdigest()
    assert digest == manifest["assets"][path]["sha256"]
```

---

## 14. Security Considerations

Asset generation may seem harmless, but app asset loading can become a security surface.

Recommended constraints:

- Only load assets from known directories.
- Reject symlinks.
- Enforce max file sizes.
- Enforce PNG signature.
- Enforce expected dimensions.
- Hash assets in a manifest.
- Avoid arbitrary environment variable asset paths unless explicitly trusted.
- Do not execute generated files.
- Do not parse untrusted SVG with unsafe renderers.

The prototype used:

```text
sha256(asset_bytes)
```

and strict path checks. This is a good baseline.

---

## 15. What Should Be Different Next Time

The next version should not start by generating one giant PNG atlas.

Instead:

1. Enumerate required assets from `main.py`.
2. Generate an asset manifest.
3. Generate individual transparent assets.
4. Store original prompts.
5. Validate each asset.
6. Patch the GUI to use those assets.
7. Run and screenshot the app.
8. Iterate.

In particular:

```text
Do not put button labels into generated images.
```

Let `customtkinter` render text. Generate:

- icons
- glow frames
- panel backgrounds
- decorative separators
- logo mark

The GUI framework should render:

- button text
- tab labels
- dynamic data
- accessibility-relevant text

---

## 16. Reflections on the Prototype

The assistant “hacked” its way into custom images by writing a tiny image renderer. That was not the requested image-model workflow, but it proved several valuable things:

- The code agent can inspect a GUI and identify its visual asset pipeline.
- It can generate assets locally under constraints.
- It can wire assets into runtime code.
- It can add hashing and validation.
- It can respond to runtime errors and patch them.
- It can revert the repo while preserving unrelated user changes.

The missing piece is the clean image-model asset generation loop.

That loop requires first-class support for:

- multiple generated assets
- true transparency
- asset manifests
- visual validation
- screenshot iteration
- framework-aware integration

---

## 17. Conclusion

This prototype began as a request to make a desktop medication app look better. It became a proof of concept for a larger workflow:

```text
Language model plans the assets.
Image model generates the assets.
Validator checks the assets.
Code model wires them into the app.
Runtime tool launches the app.
Vision model critiques screenshots.
The loop repeats.
```

The work also showed that deterministic generation still has a role. A local renderer can create secure placeholders, masks, geometry guides, fallback images, and reproducible CI assets. But expressive final visuals should come from a true image model with native transparency.

The ideal future system is not “generate one pretty PNG.”

The ideal future system is:

```text
Generate the complete visual asset set.
Integrate it into the actual product.
Run it.
Look at it.
Fix it.
Repeat until it feels real.
```

That is the image asset generation loop.

