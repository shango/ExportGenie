# Export Genie — Product Requirements Document

## Overview

A Maya 2025+ addon that lets artists export their scene to multiple formats in a single operation, with automatic folder structure creation and versioning. Installed via drag-and-drop of a single `.py` file.

The tool serves three distinct user groups via a tabbed interface:
1. **Camera trackers** — simple scenes from SynthEyes with a tracked camera and reference geo. Export to After Effects (.jsx + .obj), Maya ASCII, FBX, Alembic, and QC playblast.
2. **Matchmove/animation artists** — complex scenes with character rigs, vertex animation, and static geo. Export to Maya ASCII, FBX, Alembic, and QC playblast.
3. **Face track artists** — scenes with Alembic-cached facial animation (vertex deformation and/or rigid transforms). Converts Alembic caches to blendshape-based FBX for delivery alongside Maya ASCII and QC playblast.

## Problem Statement

Artists in the studio need to export each scene they work on to multiple formats. This is currently a tedious manual process requiring:
- Switching export settings per format
- Manually creating folder structures
- Baking keyframes for FBX
- Remembering which objects to include/exclude per format
- Maintaining consistent versioning across formats
- Manually writing After Effects JSX scripts and exporting OBJ files for camera track handoff
- Converting Alembic-cached facial animation to blendshape FBX — a multi-step manual process involving duplicate meshes, blendShape node creation, per-frame weight keying, and careful cleanup

## Target Users

### Camera Trackers (Tab 1 — "Camera Track Export")
- Artists who have done a camera track in SynthEyes and brought it into Maya
- Creating static reference geo, possibly adjusting scene scale/orientation
- Only camera and maybe a few objects have keyframes — no rigs, no constraints, no vertex animation
- Need to hand off to After Effects compositors

### Matchmove/Animation Artists (Tab 2 — "Matchmove Export")
- 3D animators and riggers working with full character rigs or complex vertex-animated objects
- Working with animated geo, static geo for game engines, and cameras
- Never exporting to After Effects
- Need .ma, .fbx, .abc exports with baked animation

### Face Track Artists (Tab 3 — "Face Track Export")
- Artists working with Alembic-cached facial animation (e.g. from face tracking software or animation caches)
- Scenes contain meshes driven by AlembicNode connections — some with vertex-level deformation (blend shapes), some with rigid whole-transform animation
- Need to deliver FBX files with blendshape-based facial animation for downstream tools (game engines, real-time renderers)
- The Alembic-to-blendshape conversion is complex and error-prone when done manually

### Platform
- Windows and macOS
- Maya 2025+

## Functional Requirements

### Installation

- **Single-file drag-and-drop install**: User drags `ExportGenie.py` into the Maya viewport
- Automatically copies itself to Maya's user scripts directory
- Creates a custom shelf button with a distinctive icon (embedded as base64 in the .py)
- Works on both Windows and macOS
- **ffmpeg bundling**: If a `bin/` directory exists next to the source `.py` file at install time, the entire `bin/` folder is automatically copied to the scripts directory alongside the script. This enables H.264 .mp4 playblast encoding and multi-pass composite rendering. The distribution folder structure is:
  ```
  export_genie/
    ExportGenie.py    ← drag this into Maya
    bin/
      win/
        ffmpeg.exe
      mac/
        ffmpeg
  ```
  On .py-only upgrades (no `bin/` folder next to the source), any previously installed `bin/` folder is preserved.
- **macOS executable permissions**: On every install (first or re-install), the macOS ffmpeg binary is `chmod 755` and the Gatekeeper quarantine attribute is removed via `xattr -d com.apple.quarantine`. This runs regardless of whether the binary was freshly copied or already existed from a prior install.
- **Same-directory detection**: If the source and destination `bin/` directories are the same path (e.g. re-installing from the scripts directory), the copy is skipped. Detection uses `os.path.samefile()` with a `os.path.normpath()` string comparison fallback.
- **Module cache clearing**: On each install, deletes stale `.pyc` files from `__pycache__/` and purges the module from `sys.modules` before re-importing, ensuring the latest version always loads
- **Shelf button reload**: The shelf button command also clears `sys.modules` before importing, so launching the tool always runs the installed version
- **Legacy cleanup**: Removes old script/icon files from pre-rename versions (maya_multi_export.py)

### Shared Features

- **Scene Info**: Displays current scene name and detected version. Auto-refreshes via `cmds.scriptJob` on `SceneOpened`, `SceneSaved`, and `NewSceneOpened` events
- **Export Root**: Directory picker for the base export location
- **Version Number**: Auto-populated from scene filename using `_v##` pattern. Editable. Supports 2-3 digit versions.
- **Frame Range**: Start/end frame fields (start defaults to 1001) + "Use Timeline Range" button. When a camera is loaded, the frame range auto-populates from the camera's animCurve keyframes or AlembicNode time range.
- **Progress Bar**: Visual indicator with percentage label, advances per export format. JSX counts as 2 steps (setup + timeline scrub).
- **Export Button**: Triggers the export pipeline for the active tab
- **Status Log**: Scrollable text area showing export progress and results per format

### Versioning & Scene Name Parsing
- Parse version from Maya filename using `_v##` pattern (e.g., `shot_v01.ma`)
- Support 2-3 digit versions in the filename (`_v01`, `_v100`)
- **Version normalization**: Versions are always output as 2 digits (`v002` → `v02`)
- If multiple `_v##` patterns exist, use the last one
- If no version found: warn user, default to `v01`
- **Task name stripping**: The last underscore segment before the version is treated as the task name and removed from the export base name

### Folder Structure

Version-aware folder naming. All tabs use `_track_` in the folder name. Export files use a tab-specific tag (`cam`, `charMM`, or `KTHead`), while QC playblasts always use `track`:

**Camera Track:**
```
<export_root>/
  <base>_track_<version>/
    <base>_cam_<version>.ma
    <base>_cam_<version>.fbx
    <base>_cam_<version>.abc
    <base>_track_<version>.mov
    <base>_track_afterEffects_<version>/
      <base>_ae_<version>.jsx
      <base>_cam_<version>_<geo1>.obj
      <base>_cam_<version>_<geo2>.obj
```

**Matchmove:**
```
<export_root>/
  <base>_track_<version>/
    <base>_charMM_<version>.ma
    <base>_charMM_<version>.fbx
    <base>_charMM_<version>.abc
    <base>_track_<version>.mov
```

**Face Track:**
```
<export_root>/
  <base>_track_<version>/
    <base>_KTHead_<version>.ma
    <base>_KTHead_<version>.fbx
    <base>_track_<version>.mov
```

- Directories are created automatically if they don't exist
- **Version-aware reuse**: When re-exporting a new version, the tool finds any existing `_track_v##` folder in the export root and renames it to the current version

---

## Export Formats

### Camera Rename (all formats, all tabs)
- Camera is temporarily renamed to `cam_main` before any exports begin, then restored in a `finally` block after all exports complete
- If a `cam_main` node already exists from a prior export, it is used directly without marking for restore (prevents accidentally renaming an unrelated node)
- If the camera is a descendant of an assigned geo/rig/proxy group, it is excluded from the top-level export selection (it comes along as a descendant instead)

### Maya ASCII (.ma) — All Tabs

Exports the scene subset as a self-contained Maya ASCII file.

- **Selection**: Camera + all assigned geo/rig/proxy groups
- **Shader stripping**: All custom shaders replaced with default Lambert (`initialShadingGroup`). Original assignments restored after export.
- **Image plane preservation**: Image plane transforms are included in the export selection
- **Playback range**: Overridden to match the export frame range, restored afterward
- **Metadata**: Temporary group node with tool version and export date included, deleted after export
- **Face Track MA**: References are imported and namespaces stripped before export so the `.ma` has no external dependencies. Alembic vertex animation is converted to blendshapes within an undo chunk so the scene is restored afterward.

### FBX (.fbx) — All Tabs

Exports with UE5-conformant settings via MEL FBX commands.

**Export Settings:**
- Up Axis: Z (UE5 handles the flip on import)
- Unit: centimeters, scale factor 1
- File version: FBX202000 (binary)
- Bake Complex Animation: ON (start/end/step=1)
- Resample Animation: ON
- Quaternion: resample
- Skins: ON
- Shapes (blendshapes): ON
- Smoothing Groups: ON
- Tangents: ON
- Skeleton Definitions: ON
- Cameras: ON
- Constraints: OFF
- Lights: OFF
- Embedded Textures: OFF
- Input Connections: OFF by default, ON for Face Track and Matchmove vertex-animated exports

**Selection Logic:**
- Camera (unless already a descendant of a selected group)
- All geo_roots, rig_roots, proxy_geos
- **Auto-discovered skeleton roots**: Walks skinCluster influences on exported geo, finds the topmost joint parent, and includes its parent group if not already in the selection
- Metadata group (deleted after export)
- Path escaping: double-quote characters in the file path are escaped for the MEL command

**Matchmove UE5 Prep** (`prep_for_ue5_fbx_export`):
Before FBX export, the matchmove tab runs a multi-step preparation within an undo chunk:
1. Import all references (makes nodes editable)
2. Bake camera animation (translate/rotate/scale + focalLength)
3. Bake joint animation from rig_roots and skin influence roots
4. Delete skinCluster constraints
5. Log non-uniform joint scales as warnings
6. Delete construction history (except on vertex-animated meshes)
7. Freeze transforms on non-skinned geo
8. Strip all namespaces

**Locator Unlock** (Matchmove tab):
Before any exports, all locator transforms within the export groups have their translate/rotate/scale channels unlocked so FBX/ABC exporters can bake and export them.

### Alembic (.abc) — Tabs 1 and 2

Exports camera + geometry as an Alembic cache.

**AbcExport Job String Flags:**
- `-frameRange {start} {end}`
- `-uvWrite` (include UV coordinates)
- `-worldSpace` (world-space transforms)
- `-wholeFrameGeo` (full-frame geometry, no sub-frame interpolation)
- `-dataFormat ogawa` (newer, more efficient format)
- `-root '{node}'` per root node (quoted, with apostrophe escaping)
- `-file '{path}'` (quoted, with apostrophe escaping)

**Root Nodes:**
- Camera (unless descendant of another root)
- All geo_roots
- All rig_roots (recently added — previously omitted)
- All proxy_geos
- Metadata group (deleted after export)

**Post-export validation**: Verifies the `.abc` file was actually written to disk (guards against silent `cmds.AbcExport` failures).

### After Effects JSX + OBJ — Tab 1 Only

Generates an ExtendScript JSX file and companion OBJ files for After Effects import.

**JSX Composition:**
- Resolution and FPS derived from Maya render settings (`defaultResolution`, `timeUnit`)
- Creates `comp.layers.addCamera()` with `autoOrient = NO_AUTO_ORIENT`
- Wrapped in `app.beginUndoGroup()` / `app.endUndoGroup()`
- Includes helper functions: `findComp`, `firstComp`, `deselectAll`

**Camera Export:**
- Per-frame keyframes for position, rotation via `setValuesAtTimes()`
- **Animated focal length**: `focalLength` and `horizontalFilmAperture` sampled per-frame, computing `ae_zoom = focalLength * comp_width / filmAperture_mm` each frame. Exported via `zoom.setValuesAtTimes()` (not a static value).
- AE zoom formula: `focal_length_mm * comp_width_px / film_back_width_mm`

**Geo Children Classification** (from all assigned Geo Groups, case-insensitive):
- **"chisels"** — skipped entirely
- **"nulls"** — descended into; each Maya locator becomes an AE 3D null with position-only keyframes (SynthEyes tracking markers). No OBJ exported.
- **Simple planes** — flat meshes (bounding box min extent < 0.1% of max extent) become AE solids with `threeDLayer=true` and `rotationX=-90`. No OBJ exported.
- **All other children** — exported as static OBJ and imported into AE with position/rotation/scale from world matrix

**OBJ Export Pipeline:**
- Geometry is duplicated, history deleted, parented to world, and transforms zeroed to identity before OBJ export. This produces local-space vertices and handles locked/constrained/Alembic-driven channels that would cause a direct `cmds.xform` to silently fail. The duplicate is deleted after export.
- No vertex flipping — AE's OBJ importer handles standard Y-up OBJ natively
- OBJ scale in AE: `world_scale * ae_scale * 100 / 512`

**Multi-Geo-Root Support:**
- All assigned Geo Group fields are collected into a single `geo_children` list (with filtering for chisels/nulls/camera descendants)
- The JSX function iterates this pre-filtered list directly, ensuring all groups are exported

**Cross-Root Name Collision Detection:**
- Validation collects children from all geo roots and checks for duplicate short names across the combined set (OBJ files use short names, so duplicates would overwrite)

**Source Footage:**
- If the camera has a Maya image plane, the footage path is auto-detected and imported as the bottom layer in the AE comp. Path made relative to JSX when possible.

**Static Object Optimization:**
- Geo children and locators with no animCurve connections use a single `setValue()` call instead of per-frame `setValuesAtTimes()`

**Coordinate Conversion** (Maya Y-up → AE Y-down):
- Scale factor: `ae_scale = 10.0 * cm_per_unit / 2.54`
- Position: from world matrix translation: `x_ae = tx * ae_scale + comp_cx`, `y_ae = -ty * ae_scale + comp_cy`, `z_ae = -tz * ae_scale`
- Rotation: from local (objectSpace) matrix, normalized, T*R*T coordinate transform applied (T = diag(1,-1,-1)), decomposed as Rx*Ry*Rz intrinsic XYZ
- Scale: from world matrix column magnitudes
- Timing: `(frame - start_frame + 1) / fps`

### Alembic-to-Blendshape Conversion (Tabs 2 and 3)

Core technical pipeline for converting Alembic per-vertex animation to FBX-compatible blendshapes.

#### Animation Type Detection (`detect_vertex_anim_meshes`)

Samples vertex positions across **4 frames** (start, 1/3, 2/3, end) to classify meshes:
- Checks 3 vertices per mesh (first, middle, last) in local space
- If any vertex has moved between any sample frame and the reference → vertex animation (blendshape conversion needed)
- Multiple sample frames avoid false negatives when a mesh returns to rest pose at endpoints (e.g. blink, jaw open/close)
- Excludes skinned meshes (driven by skinCluster, not Alembic)

#### Leaf Node Classification (`prepare_face_track_for_export`)

Each node under a Face Mesh Group is recursively classified:
- **Vertex-animated meshes** → converted to blendshapes via `convert_abc_to_blendshape`
- **Driven-transform nodes** (AlembicNode/animCurve connections on TRS) → baked in-place via `_bake_transform_curves`
- **Non-mesh leaves** → only included if they have driven transforms (static locators/nulls filtered out)
- **Static meshes** → included as-is

#### Two-Pass Blendshape Conversion (`convert_abc_to_blendshape`)

**Pass 1 — Create blendshape targets:**
1. Create a clean base mesh (duplicate of source at first frame)
2. Preserve hierarchy (parent base under same parent as source)
3. Copy rotate order and pivots from source
4. Bake local TRS onto base mesh via parent/scale constraints
5. Create blendShape node on base mesh
6. For each frame: scrub timeline, duplicate deformed mesh as target, add to blendShape

**Pass 2 — Key all weights by index:**
1. For each target, key `weight[i]` with step-key pattern:
   - Frame before: 0.0
   - Current frame: 1.0
   - Frame after: 0.0
   - Step tangents (`itt="stepnext"`, `ott="step"`) for sharp transitions
2. Weights keyed by **index** (not alias names) — guaranteed correct mapping regardless of naming collisions

**Cleanup:**
1. Delete target shapes group (blendShape stores deltas internally)
2. Delete original Alembic-driven source mesh (prevents FBX InputConnections from including it)
3. Restore original timeline position

#### Driven Transform Baking (`_bake_transform_curves`)

For transform-animated meshes (rigid body motion from AlembicNode):
1. Unlock all TRS channels
2. Bake via `cmds.bakeResults()` over the frame range (no `minimizeRotation` — preserves exact rotation curves)
3. **Explicitly disconnect non-animCurve connections** after baking. Critical because `cmds.bakeResults` creates animCurve nodes but does not disconnect AlembicNode connections. With `FBXExportInputConnections=true`, surviving connections cause timing conflicts.

#### Local TRS Baking (`_bake_local_trs`)

Bakes transform channels onto a target mesh to match a source via constraints:
1. Unlock all TRS channels on target
2. Create parentConstraint and scaleConstraint from source to target
3. Bake results (no `minimizeRotation`)
4. Delete constraints

### Playblast QC — All Tabs

Renders a viewport playblast through the assigned camera at **1920x1080**.

#### Output Formats (dropdown)
- **H.264 (.mov)** — QuickTime format. Requires QuickTime on Windows, uses AVFoundation on macOS.
- **PNG Sequence** — Frame-padded filenames (`name.0001.png`) into a versioned subfolder.
- **H.264 (.mp4)** — Playblasts to temp PNG sequence, then encodes to H.264 via bundled ffmpeg. Temp PNGs deleted on success, preserved on failure.

#### ffmpeg Encoding Settings
- Codec: libx264 (H.264)
- Pixel format: yuv420p
- Profile: high, Level: 4.2
- Preset: ultrafast
- CRF: 18
- movflags: +faststart
- `stdin=subprocess.DEVNULL` (prevents macOS lockup from ffmpeg reading Maya's stdin)

#### Rendering Modes

**Camera Track Mode** (`camera_track_mode=True`):
- Wireframe display OR wireframe + useBackground shader (transparent meshes showing camera plate with wireframe edges)
- No checker overlay, no multi-pass composite
- All geometry types visible

**Matchmove/Face Track Mode** (`matchmove_geo=list`):
- Multi-pass composite when ffmpeg + composite paths are provided
- Single-pass fallback with semi-transparent checker overlay when ffmpeg unavailable
- Motion blur enabled
- Isolate select on assigned geo roots

**Raw Playblast Mode** (`raw_playblast=True`):
- Skips ALL viewport modifications
- Uses user's current VP2.0 settings as-is
- Only switches camera to cam_main

#### Multi-Pass Composite Pipeline (Matchmove/Face Track)

Three-pass rendering composited via ffmpeg:

**Pass 1 — Plate** (background only):
- Image plane visible, all geometry hidden
- `showOrnaments=False` (clean compositing, no HUD)
- Output: PNG sequence

**Pass 2 — Color** (solid mesh overlay):
- Black background, no gradient
- Flat lighting, shadows disabled
- Image plane hidden, all geometry visible
- All meshes assigned to solid Lambert (user-configurable color, default gray)
- `showOrnaments=False`
- Output: PNG sequence

**Pass 3 — Matte** (B&W checker):
- Checker texture: color1=white, color2=black
- Place2dTexture for scale control: `repeatU/V = max(1, 33 - checker_scale)`
- `showOrnaments=False`
- Output: PNG sequence

**ffmpeg Composite Command:**
```
[2:v]format=gray[matte];
[1:v][matte]alphamerge,format=rgba,colorchannelmixer=aa={opacity}[fg];
[0:v][fg]overlay=format=auto[out]
```
Uses matte as alpha on color pass, overlays on plate with configurable opacity.

**macOS composite output**: Silently outputs `.mp4` instead of `.mov` for reliable ffmpeg encoding.

#### Single-Pass Fallback (no ffmpeg)

- Semi-transparent UV checker Lambert applied to all geo
- Smooth shaded display with image plane and motion blur
- Rendered directly to H.264 .mov or PNG sequence

#### Viewport Overrides

**Color Management:**
- "Render as Raw (sRGB)" (on by default): Sets playblast view transform to "Raw" (dynamically detected from OCIO views). Only the playblast output transform is changed. Persists in scene (intentionally not reverted).
- Bypassed when "Use Current Viewport Settings" is enabled

**Camera:**
- Switch panel to camera via `cmds.lookThru()`
- Disable panZoomEnabled
- Set farClipPlane (configurable slider: 10,000–2,000,000, default 800,000)

**Scene State:**
- Grid hidden
- Selection cleared (no highlight in render)
- Backface culling set to Full (3) on all mesh shapes
- Anti-aliasing: MSAA 16 or 8 (user configurable)
- Smooth wireframe enabled

**Display Layers** (Matchmove/Face Track):
- All display layers forced visible (`visibility=True`, `hideOnPlayback=False`)
- Original values saved and restored

**Isolate Select** (Matchmove/Face Track):
- Only assigned geo roots (and descendants) visible
- Camera and image planes included
- All other scene objects hidden
- Restored afterward

**Shading:**
- Camera Track: wireframe or smoothShaded+wireframeOnShaded
- Matchmove/Face Track: smoothShaded (no wireframe overlay)
- Flat lighting for non-raw playblasts (skipped when composite path already set displayLights)
- Viewport shadows saved and restored in composite path

**HUD Overlay** (optional):
- Frame number (bottom-center, section 7)
- Focal length (bottom-right, section 9)
- Font size: 24

**Preview Mode:**
- Interactive viewport preview using single-pass checker overlay
- Togglable via Preview Playblast button
- Shows real-time viewport state matching final render

#### Checker Overlay Settings (Matchmove/Face Track)
- **Color**: RGB color picker
- **Scale**: Slider 1–32, maps to `repeatU/V = max(1, 33 - scale)`
- **Opacity**: Slider 0–100 (blend opacity for composite, transparency for single-pass)

### T-Pose Frame Handling (Matchmove Tab Only)

- Checkbox "Include T Pose" with configurable frame number (default 991)
- When enabled, FBX and ABC exports use `min(start_frame, tpose_frame)` as the start frame
- QC playblast always uses the original timeline range (no T-pose)
- **Pre-flight validation**: Warning shown if T-pose frame is not before start frame (would not be a distinct frame in the export)

### Alembic Camera Bake (Matchmove and Face Track Tabs)

When the camera is driven by an AlembicNode:
1. Open undo chunk
2. Unlock all TRS channels on camera transform
3. Bake transform channels via `cmds.bakeResults()` (no `minimizeRotation` — exact rotation curves preserved)
4. Bake focalLength on camera shape
5. Disconnect all non-animCurve source connections (keep baked animCurves)
6. Close undo chunk in `finally` block, then undo to restore scene

---

## Pre-flight Validation & Error Handling

### Validation (per tab)
- **Required fields**: At least one export format selected, required role assignments per format
- **Node existence**: All assigned nodes validated against `cmds.objExists()`
- **Name collision detection**:
  - Duplicate picks (same node in multiple role fields)
  - `cam_main` conflict (picked camera ≠ `cam_main` but `cam_main` already exists)
  - OBJ filename collisions across all geo roots (Camera Track, JSX enabled)
- **T-pose frame validation** (Matchmove): Warning if T-pose frame ≥ start frame
- Validation errors shown in popup dialog AND logged to Status panel

### Error Handling
- Per-format try/except — one format failing doesn't block others
- **Verbose Script Editor errors**: Formatted error report with tag, message, and full traceback via `sys.stderr` (red text). Status panel shows brief "FAILED (see Script Editor)" message.
- Plugin auto-loading for FBX (`fbxmaya`), Alembic (`AbcExport`), and OBJ (`objExport`) with error dialogs if unavailable
- QuickTime availability check for playblast with platform-appropriate popup
- ffmpeg availability pre-check with expected path in error message
- Selection state saved and restored after all exports
- Version number included in all error/warning dialogs
- Undo chunks for destructive operations (FBX prep, blendshape conversion, camera bake) with scene restoration in `finally` blocks
- Namespace resolution with ambiguity warnings when multiple nodes match after namespace strip

---

## Non-Functional Requirements

- **Platform**: Windows and macOS
- **Maya Version**: 2025+ only
- **UI Framework**: Pure `maya.cmds` (no PySide dependency)
- **Single file**: All code in one `.py` file for simplicity
- **No external dependencies**: Only Maya built-in modules (ffmpeg is an optional bundled binary)
- **String formatting**: `.format()` style (no f-strings, for broader Maya Python compatibility)

---

## JSX Export Technical Reference

This section documents the complete Maya-to-After Effects conversion pipeline.

### Coordinate Systems

| Property       | Maya                        | After Effects                    |
|---------------|-----------------------------|----------------------------------|
| Handedness    | Right-handed                | Left-handed                      |
| Y axis        | Up                          | Down (screen origin top-left)    |
| Z axis        | Forward (camera looks -Z)   | Away from camera (looks +Z)      |
| Matrix layout | Row-major 4x4               | N/A (properties set individually)|

The axis-fix matrix that converts between them is `T = diag(1, -1, -1)`.

### Position Conversion

Position is extracted from the **world** matrix (row 3 in Maya's row-major layout: indices 12, 13, 14):

```
x_ae = tx * ae_scale + comp_cx
y_ae = -ty * ae_scale + comp_cy
z_ae = -tz * ae_scale
```

Where `comp_cx = comp_width / 2` and `comp_cy = comp_height / 2`.

### Scale Factor (`ae_scale`)

```python
ae_scale = 10.0 * cm_per_unit / 2.54
```

Matches SynthEyes's internal convention where `rescale = 10` calibrated against an inch-based unit system.

### Rotation Conversion

**Step 1**: Extract rotation from the LOCAL (objectSpace) matrix. This excludes parent group orientation (important for SynthEyes scenes with Z-up to Y-up conversion groups).

**Step 2**: Normalize to remove scale (divide columns by their magnitudes).

**Step 3**: Apply T*R*T coordinate change-of-basis:
```
T = diag(1, -1, -1)

TRT produces:
  [[r00, -r01, -r02],
   [-r10, r11,  r12],
   [-r20, r21,  r22]]
```

**Step 4**: Decompose as Rx*Ry*Rz (intrinsic XYZ) — this is AE's native rotation order:
```
ry = asin(-R_ae[2][0])
rx = atan2(-R_ae[2][1], R_ae[2][2])
rz = atan2(R_ae[1][0], R_ae[0][0])
```

### OBJ Export — Do NOT Flip Vertices

AE's OBJ importer handles standard Y-up OBJ format natively. The JSX position/rotation/scale properties handle the coordinate transformation. Flipping OBJ vertices causes double inversion.

The correct pipeline:
1. Duplicate geo, zero transforms, export in local space
2. No vertex modification in the OBJ file
3. JSX applies world-space transforms

### Debugging Checklist

1. **Compare camera frame-1 values** numerically — should match within ~0.001
2. **If rotations wrong**: Check Euler decomposition convention (`Rx*Ry*Rz`, not `Rz*Ry*Rx`)
3. **If mesh offset**: OBJ exported in world space — use identity matrix trick
4. **If scene flipped**: OBJ vertices double-flipped — remove vertex transformation
5. **If scale wrong**: Check local vs world-space scale (matrix column magnitudes vs `getAttr`)
6. **If rotation differs slightly**: Check world vs local matrix for rotation extraction

---

## Face Track Technical Reference

### Why Blendshape Conversion Is Needed

Alembic stores per-vertex positions per frame. FBX requires blendshape weights (scalar values over time) with target shapes. The conversion bridges these representations.

### The InputConnections Discovery

`FBXExportInputConnections -v true` is required for Face Track FBX exports. The FBX plugin must follow: selected mesh → blendShape deformer → weight attributes → animCurve nodes. Without this, blendshape targets export but weight animation is lost.

### Secondary Issues from InputConnections=True

1. **Double geometry**: Original Alembic-driven source mesh discovered via AlembicNode connection. Fix: delete source mesh after conversion.
2. **Timing conflicts**: `cmds.bakeResults` doesn't disconnect AlembicNode connections. Fix: explicitly disconnect non-animCurve connections after baking.
3. **Alias naming collisions**: Fix: key weights by `weight[i]` index instead of alias names.

### FBX File Size Optimization

Deleting the targets group after keying removes N full mesh duplicates from the scene before FBX export. The blendShape node stores deltas internally.

---

## Out of Scope (future)
- Batch export of multiple scenes
- Custom FBX/Alembic settings UI
- USD export support
- Network/cloud export paths
- Automatic version incrementing (creating v02 from v01)
