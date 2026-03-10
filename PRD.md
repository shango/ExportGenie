# Maya Multi-Export Tool — Product Requirements Document

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
- **ffmpeg bundling (Windows)**: If a `bin/win/ffmpeg.exe` directory exists next to the source `.py` file at install time, the entire `bin/` folder is automatically copied to the scripts directory alongside the script. This enables the H.264 (.mp4 Win) playblast format. The distribution folder structure is:
  ```
  export_genie/
    ExportGenie.py    ← drag this into Maya
    bin/
      win/
        ffmpeg.exe
  ```
  On .py-only upgrades (no `bin/` folder next to the source), any previously installed `bin/` folder is preserved.
- **Module cache clearing**: On each install, deletes stale `.pyc` files from `__pycache__/` and purges the module from `sys.modules` before re-importing, ensuring the latest version always loads
- **Shelf button reload**: The shelf button command also clears `sys.modules` before importing, so launching the tool always runs the installed version

### UI — Three-Tab Layout (cmds.tabLayout)

Shared elements stay outside the tabs; only role assignments, format checkboxes, and viewport settings go inside tabs.

```
window "Export Genie v10"
+-- columnLayout (main)
|   +-- frameLayout "Scene Info"              <-- SHARED (auto-refreshes on save/open)
|   +-- frameLayout "Export Root Directory"    <-- SHARED
|   +-- tabLayout
|   |   +-- "Camera Track Export"             <-- TAB 1
|   |   |   +-- Node Picker (In the outliner)
|   |   |   |   +-- Camera       (Load Sel)
|   |   |   |   +-- Geo Group    (Load Sel)   repeatable (+/- buttons)
|   |   |   +-- Export Formats
|   |   |   |   +-- Maya ASCII (.ma)
|   |   |   |   +-- After Effects (.jsx + .obj)
|   |   |   |   +-- FBX (.fbx)
|   |   |   |   +-- Alembic (.abc)
|   |   |   |   +-- Playblast QC (.mov / .png / .mp4)
|   |   |   +-- Viewport Settings
|   |   |       +-- Render as Raw (sRGB)
|   |   |       +-- useBackground Shader + Wireframe
|   |   |       +-- Anti-Aliasing 16x
|   |   |       +-- Use Current Viewport Settings
|   |   +-- "Matchmove Export"                <-- TAB 2
|   |   |   +-- Node Picker (In the outliner)
|   |   |   |   +-- Camera           (Load Sel)
|   |   |   |   +-- Static Geo       (Load Sel)   repeatable (+/- buttons)
|   |   |   |   +-- ---- separator ----
|   |   |   |   +-- Rig Group        (Load Sel)   \
|   |   |   |   +-- Mesh Group       (Load Sel)   / repeatable pair
|   |   |   |   +-- [+] [-] buttons
|   |   |   +-- Export Formats
|   |   |   |   +-- Maya ASCII (.ma)
|   |   |   |   +-- FBX (.fbx)
|   |   |   |   +-- Alembic (.abc)
|   |   |   |   +-- Playblast QC (.mov / .png / .mp4)
|   |   |   +-- Viewport Settings
|   |   |   |   +-- Render as Raw (sRGB)
|   |   |   |   +-- Anti-Aliasing 16x
|   |   |   |   +-- Use Current Viewport Settings
|   |   |   |   +-- QC Checker Overlay (Color, Scale, Opacity)
|   |   |   +-- checkBox "Include T Pose" + intField (991)
|   |   +-- "Face Track Export"               <-- TAB 3
|   |       +-- Node Picker (In the outliner)
|   |       |   +-- Camera           (Load Sel)
|   |       |   +-- Static Geo       (Load Sel)
|   |       |   +-- ---- separator ----
|   |       |   +-- Face Mesh Group  (Load Sel)   repeatable (+/- buttons)
|   |       +-- Export Formats
|   |       |   +-- Maya ASCII (.ma)
|   |       |   +-- FBX (.fbx)
|   |       |   +-- Playblast QC (.mov / .png / .mp4)
|   |       +-- Viewport Settings
|   |           +-- Render as Raw (sRGB)
|   |           +-- Anti-Aliasing 16x
|   |           +-- Use Current Viewport Settings
|   |           +-- QC Checker Overlay (Color, Scale, Opacity)
|   +-- frameLayout "Frame Range"             <-- SHARED
|   |   +-- Start / End fields
|   |   +-- "Use Timeline Range" button
|   +-- progressBar + label                   <-- SHARED
|   +-- button "E X P O R T"                 <-- SHARED
|   +-- frameLayout "Status"                 <-- SHARED
|   +-- text "v10"                            <-- SHARED
```

#### Shared UI Elements
- **Scene Info**: Displays current scene name, detected version, and status. Auto-refreshes via `cmds.scriptJob` on `SceneOpened`, `SceneSaved`, and `NewSceneOpened` events (jobs parented to window for automatic cleanup)
- **Export Root**: Directory picker for the base export location
- **Frame Range**: Start/end frame fields (start defaults to 1001) + "Use Timeline Range" button (clamps start to minimum 1001). When a camera is loaded via Load Sel, the frame range auto-populates: start is set to 1001 and end is set to the camera's last keyframe (queried from both transform and shape channels)
- **Progress Bar**: Visual progress indicator with percentage label, advances per export format
- **Export Button**: Triggers the export pipeline for the active tab
- **Status Panel**: Scrollable text area showing export progress and results. Shows "Export to: {path}" at start, then one-line status per format ("MA ... done" or "MA ... FAILED (see Script Editor)"). Validation errors are also logged here before appearing in the popup dialog

#### Tab 1 — Camera Track Export
- **Node Picker**: Camera and Geo Group fields with "Load Sel" buttons. Multiple Geo Groups can be added dynamically with +/- buttons. Frame label includes subtitle "(In the outliner)".
  - User selects object(s) in viewport, clicks the corresponding "Load Sel" button
  - Tool validates the object type (camera shape, transform)
- **Export Formats**: Checkboxes for Maya ASCII (.ma), After Effects (.jsx + .obj), FBX (.fbx), Alembic (.abc), Playblast QC (.mov / .png / .mp4)
  - **Playblast format dropdown**: Choose between H.264 (.mov), PNG image sequence, or H.264 (.mp4 Win). The .mp4 option uses bundled ffmpeg to encode from a temp PNG sequence (Windows only). PNG exports numbered frames into a subfolder.
- **Viewport Settings**: Collapsible section with:
  - **Render as Raw (sRGB)**: Checkbox (on by default). Sets the playblast output color transform to "Raw" (dynamically detected from available OCIO views), giving sRGB passthrough without tonemapping. Only the playblast output transform is changed — the main view transform is unaffected.
  - **useBackground Shader + Wireframe**: Applies a useBackground shader to all geo so meshes become transparent (showing the camera plate) with wireframe edges drawn on top. Original shaders restored after render.
  - **Anti-Aliasing 16x**: Bumps VP2.0 anti-aliasing from 8 to 16 samples.
  - **Use Current Viewport Settings**: Checkbox (off by default). Skips all VP2.0 overrides — the playblast uses the user's own viewport state as-is (only the camera is switched to cam_main).

#### Tab 2 — Matchmove Export
- **Node Picker**: Camera and Static Geo are scene-level fields. Multiple Static Geo entries can be added with +/- buttons. Below a separator, Rig Group / Mesh Group pairs can be added dynamically for multiple characters or vertex-animated meshes. Frame label includes subtitle "(In the outliner)".
  - **Camera**: Single field with "Load Sel" button
  - **Static Geo**: Repeatable entries with +/- buttons for multiple static geo groups
  - **Rig/Geo pairs**: Each pair has a Rig Group and Mesh Group field with "Load Sel" buttons. The first pair is always shown. A `[+]` button adds additional pairs (labeled "Rig Group 2" / "Mesh Group 2", etc.). A `[-]` button appears when 2+ pairs exist to remove the last pair. The UI grows/shrinks vertically as pairs are added/removed.
  - For vertex-animated meshes (blend shapes, cached deformation), assign as Mesh Group with Rig Group left empty
  - Tool validates the object type (camera shape, transform)
- **Export Formats**: Checkboxes for Maya ASCII (.ma), FBX (.fbx), Alembic (.abc), Playblast QC (.mov / .png / .mp4)
  - **Playblast format dropdown**: Choose between H.264 (.mov), PNG image sequence, or H.264 (.mp4 Win)
  - **Include T Pose**: Checkbox (checked by default) with an editable frame number field (default 991). When checked and "Use Timeline Range" is clicked, the start frame is set to the T-pose frame value, ensuring the T-pose frame is included in FBX and ABC exports. The QC playblast always uses the original timeline range (no T-pose). Only visible/active on the Matchmove tab.
- **Viewport Settings**: Collapsible section with:
  - **Render as Raw (sRGB)**: Checkbox (on by default)
  - **Anti-Aliasing 16x**: Checkbox (off by default)
  - **Use Current Viewport Settings**: Checkbox (off by default)
  - **QC Checker Overlay**: Color picker, Scale slider (1–32), Opacity slider (0–100)

#### Tab 3 — Face Track Export
- **Node Picker**: Camera and Static Geo are scene-level fields. Below a separator, Face Mesh Group entries can be added dynamically for multiple face geometry groups (e.g. multiple characters). Frame label includes subtitle "(In the outliner)".
  - **Camera** and **Static Geo**: Single fields with "Load Sel" buttons
  - **Face Mesh Groups**: Each entry has a single Face Mesh Group field with "Load Sel" button. The first entry is always shown. A `[+]` button adds additional entries. A `[-]` button appears when 2+ entries exist to remove the last. The UI grows/shrinks vertically as entries are added/removed.
  - Each Face Mesh Group should be a top-level transform containing one or more Alembic-cached meshes (vertex-deformed and/or rigidly transformed)
- **Export Formats**: Checkboxes for Maya ASCII (.ma), FBX (.fbx), Playblast QC (.mov / .png / .mp4)
  - **Playblast format dropdown**: Choose between H.264 (.mov), PNG image sequence, or H.264 (.mp4 Win)
- **Viewport Settings**: Collapsible section with:
  - **Render as Raw (sRGB)**: Checkbox (on by default)
  - **Anti-Aliasing 16x**: Checkbox (off by default)
  - **Use Current Viewport Settings**: Checkbox (off by default)
  - **QC Checker Overlay**: Color picker, Scale slider (1–32), Opacity slider (0–100)

### Versioning & Scene Name Parsing
- Parse version from Maya filename using `_v##` pattern (e.g., `shot_v01.ma`)
- Support 2-3 digit versions in the filename (`_v01`, `_v100`)
- **Version normalization**: Versions are always output as 2 digits (`v002` → `v02`, `v01` → `v01`)
- If multiple `_v##` patterns exist, use the last one
- If no version found: warn user, default to `v01`
- **Task name stripping**: The last underscore segment before the version is treated as the task name and removed from the export base name. For example:
  - `shotNum_plateNum_taskName_v002.ma` → base `shotNum_plateNum`, version `v02`
  - `shot_task_v01.ma` → base `shot`, version `v01`
  - `shot_v01.ma` → base `shot`, version `v01` (no task segment to strip)

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
- **Version-aware reuse**: When re-exporting a new version, the tool finds any existing `_track_v##` folder in the export root and renames it to the current version, adding new files alongside existing ones rather than overwriting. The same applies to the After Effects subfolder.

### Export Behavior

#### Source Footage Auto-Detection (JSX and MA exports)
- If the selected camera has a Maya **image plane** attached, the source footage path is auto-detected via `cmds.listConnections(cameraShape + ".imagePlane")` and `cmds.getAttr(imagePlaneShape + ".imageName")`
- **JSX**: The footage is imported as a sequence (`ImportOptions` with `sequence = true`) and added as the bottom layer in the AE comp via `moveToEnd()`. If the file doesn't exist on the AE machine, a placeholder is created instead. Silently skipped if no image plane is found.
- **MA**: Image plane transform nodes are added to the export selection so the footage reference is preserved in the `.ma` file. Silently skipped if no image plane is found.
- If the path is incorrect or unavailable, the feature skips silently — no errors or warnings

#### Camera Rename (all formats, all tabs)
- Camera is temporarily renamed to `cam_main` before any exports begin, then restored after all exports complete
- Rename happens once at the orchestration level (not per-format)
- If the camera lives under a static geo, rig group, or mesh group, it is excluded from the top-level export selection (it comes along as a descendant of its parent group instead)

#### Maya ASCII (.ma) — All tabs
- **Tab 1**: Exports Camera + Geo Root
- **Tab 2**: Exports Camera + Mesh Groups + Rig Groups + Static Geo
- **Tab 3**: Exports Camera + Face Mesh Groups + Static Geo
- No baking or special processing
- Uses `cmds.file(exportSelected=True, type="mayaAscii")`

#### FBX (.fbx) — All tabs
- **Tab 1**: Exports Camera + Geo Root
- **Tab 2**: Exports Camera + Mesh Groups + Rig Groups + Static Geo
- **Tab 3**: Exports Camera + converted blendshape meshes + Static Geo (see "Alembic-to-Blendshape Conversion" below)
- **Animation baking**: Handled by the FBX plugin's built-in `FBXExportBakeComplexAnimation` setting, which bakes internally during export without modifying the source scene. No pre-bake or undo chunk needed.
- FBX export settings overridden via MEL commands:
  - **Up axis: Z** — UE5 expects Z-up; the FBX plugin handles Y→Z conversion automatically on export
  - **Unit conversion: centimeters** — explicit `FBXExportConvertUnitString cm` and `FBXExportScaleFactor 1` so UE5 imports at correct scale
  - Bake complex animation: on (plugin-internal baking)
  - Quaternion: resample
  - Constraints: off
  - Cameras: on
  - Lights: off
  - Input connections: off by default, **on for Face Track exports** (required for blendshape weight animation — see below)
  - Embedded textures: off
  - Skins/Shapes: on
  - Smoothing groups: on
  - Skeleton definitions: on
  - Binary format, FBX 2020 compatibility
- Uses `mel.eval("FBXExport -f ... -s")` for fine-grained control

##### FBXExportInputConnections — Critical for Blendshape Animation

The `FBXExportInputConnections` MEL flag controls whether the FBX plugin follows input connections from selected nodes during export. When set to `false` (the default for Tabs 1 and 2), the FBX plugin only exports the selected nodes and their direct attributes.

For Face Track exports, this **must** be set to `true`. The reason: the FBX plugin needs to follow the connection chain from the selected mesh → blendShape deformer node → weight animation curves. Without input connections enabled, `FBXExportShapes` exports the blendshape target topology/deltas, but the **animation on the weights** is lost — resulting in an FBX with static blendshape targets and no facial animation.

The `export_input_connections` parameter on `export_fbx()` is set to `True` only for Face Track FBX calls.

#### Alembic (.abc) — Tabs 1 and 2
- **Tab 1**: Exports Camera + Geo Root
- **Tab 2**: Exports Camera + Geo Root + Static Geo
- Animation is baked implicitly by Alembic's frame-range sampling (no explicit `bakeResults`)
- Flags: `-uvWrite`, `-worldSpace`, `-wholeFrameGeo`, `-dataFormat ogawa`
- Uses `cmds.AbcExport(j=job_string)` with `-root` flag per assigned role

#### Alembic-to-Blendshape Conversion (Tab 3 — Face Track)

This is the core technical pipeline for the Face Track tab. Alembic caches store per-vertex positions at each frame, but FBX requires blendshape-based animation for facial deformation. The tool automatically converts between these representations.

##### Animation Type Detection

Each mesh under a Face Mesh Group is classified as either **vertex-animated** (facial deformation) or **transform-animated** (rigid body motion). The detection works by:

1. Sampling vertex positions at the **start frame** and **end frame** in local space
2. If any vertex has moved between those frames → vertex animation (blendshape conversion needed)
3. If no vertices moved → check for driven transforms (AlembicNode connections to translate/rotate/scale channels) → transform animation (bake keyframes only)

Using start and end frames (rather than consecutive frames) ensures detection catches animation across the full range, even for meshes that are static for most of the shot but animate briefly.

##### Two-Pass Blendshape Conversion

For each vertex-animated mesh, the conversion follows a two-pass approach:

**Pass 1 — Create blendshape targets:**
1. Create a clean base mesh (duplicate of the source at the first frame)
2. For each frame in the range, scrub the timeline, duplicate the deformed mesh, and add it as a blendshape target
3. Targets are added to the blendShape node via `cmds.blendShape(edit=True, target=...)`
4. A unique name is generated for each target to avoid naming collisions

**Pass 2 — Key all weights by index:**
1. For each target, key the corresponding `weight[i]` attribute with a step-key pattern:
   - Frame before: value 0.0
   - Current frame: value 1.0
   - Frame after: value 0.0
   - Step tangents to ensure sharp transitions (no interpolation between shapes)
2. Weights are keyed by **index** (`weight[0]`, `weight[1]`, etc.) rather than alias names. This is critical because `cmds.aliasAttr` can return aliases in a different order than creation order, and `_unique_name()` may append numbers that collide with frame numbers. Index-based keying guarantees correct weight-to-target mapping.

**Cleanup after keying:**
1. Delete the target shapes group (blendShape stores deltas internally after `cmds.blendShape(edit=True, target=...)`, so the full mesh copies are no longer needed). This significantly reduces FBX file size — for a 270-frame shot, this removes 270 full mesh duplicates.
2. Delete the original Alembic-driven source mesh. With `FBXExportInputConnections` enabled, the FBX plugin would otherwise discover and include the original mesh (via its AlembicNode connections), causing a visible "glitch" where a second copy of the geometry pops in and out.

##### Driven Transform Baking

For transform-animated meshes (rigid body motion from AlembicNode), the tool:

1. Bakes translate/rotate/scale channels using `cmds.bakeResults()` over the frame range
2. **Explicitly disconnects non-animCurve connections** after baking. This is critical because `cmds.bakeResults` creates animCurve nodes but does not necessarily disconnect the original AlembicNode connections. With `FBXExportInputConnections=true`, the FBX plugin would discover these surviving AlembicNode connections and apply them alongside the baked curves, causing timing conflicts and delayed animation.

The disconnection logic iterates over all translate/rotate/scale plugs, checks each source connection, and disconnects anything that is not an `animCurve` node.

##### Namespace and Alias Resolution

Alembic imports can create deeply nested namespace hierarchies. The tool handles this by:
- Using `cmds.aliasAttr` to resolve blendshape weight aliases when needed
- Preferring `weight[i]` index-based access over alias names for reliability
- Handling namespace-qualified node names throughout the pipeline

#### After Effects (.jsx + .obj) — Tab 1 only
- Generates an ExtendScript JSX file and companion OBJ files for After Effects import
- JSX header includes tool version for traceability
- **Camera**: Exported with per-frame keyframes for position, rotation, and zoom
  - Queries Maya camera shape for `focalLength` (mm) and `horizontalFilmAperture` (inches -> mm via `*25.4`)
  - AE zoom formula: `focal_length_mm * comp_width_px / film_back_width_mm`
  - Creates `comp.layers.addCamera()` with `autoOrient = NO_AUTO_ORIENT`
  - Uses direct property access (`.position`, `.rotationX`, `.rotationY`, `.rotationZ`, `.zoom`) matching SynthEyes conventions
  - Uses `setValuesAtTimes()` for batch keyframe application
- **Geo children classification** (case-insensitive name matching):
  - **"chisels"** — any child whose name contains "chisels" is skipped entirely
  - **"nulls"** — any child whose name contains "nulls" is descended into; each Maya locator found inside becomes an AE 3D null with **position-only** keyframes (representing SynthEyes tracking markers). No OBJ exported.
  - **Simple planes** — flat meshes (bounding box thinnest extent < 0.1% of largest) become AE solids via `comp.layers.addSolid()` with `threeDLayer = true` and `rotationX = -90` (lying on the ground plane XZ). Scale is computed from world bounding box extents mapped to AE pixel space. No OBJ exported.
  - **All other children** — exported as a static OBJ (frame 1) and imported into AE via `ImportOptions` + `app.project.importFile()` + `comp.layers.add()`, with position/rotation/scale applied from the world matrix.
- **OBJ export pipeline**:
  - Maya's OBJ exporter writes vertices in **world space** by default. To avoid double-offset (JSX also applies position/rotation/scale), the node's world matrix is temporarily reset to identity before export, then restored. This produces local-space OBJ vertices.
  - OBJ vertices are **not** flipped/transformed — AE's OBJ importer natively handles the standard Y-up OBJ format. (See "JSX Export Technical Reference" below for why.)
  - OBJ scale in AE: `world_scale * ae_scale * 100 / 512` (AE maps 1 OBJ unit = 512 pixels at 100% scale)
- **Static object optimization**: Geo children and locators with no `animCurve` connections are detected at export time and use a single `setValue()` call (position read once) instead of scrubbing the timeline frame-by-frame with `setValuesAtTimes()`
- **Coordinate conversion** (Maya Y-up -> AE Y-down) — see detailed "JSX Export Technical Reference" section below:
  - **Scale factor (`ae_scale`)**: `10.0 * cm_per_unit / 2.54` — unit-aware conversion matching SynthEyes's internal inch-based system
  - **Position**: From the **world** matrix translation row: `x_ae = tx * ae_scale + comp_cx`, `y_ae = -ty * ae_scale + comp_cy`, `z_ae = -tz * ae_scale`
  - **Rotation**: From the **local** (objectSpace) matrix — excludes parent group orientation. Upper-left 3x3 is normalized, the T\*R\*T coordinate transform is applied (T = diag(1, -1, -1)), and the result is decomposed as **Rx\*Ry\*Rz intrinsic XYZ** Euler angles (AE's native rotation order).
  - **Scale**: From **world** matrix column magnitudes — captures full parent-inclusive scale
  - **Timing**: Keyframe times use `(frame - start_frame + 1) / fps` so frame 1 maps to `1/fps` seconds (matching SynthEyes convention)
- **Comp settings**: Resolution and fps derived from Maya render settings (`defaultResolution`) and time unit
- JSX includes helper functions: `findComp`, `firstComp`, `deselectAll`
- JSX wraps all operations in `app.beginUndoGroup()` / `app.endUndoGroup()`

#### Playblast QC (.mov, .png, or .mp4) — All tabs
- Renders a viewport playblast through the assigned camera (`cam_main`) at **1920x1080**
- **Format dropdown** with three options:
  - **H.264 (.mov)** — QuickTime format with compression quality 70. Requires QuickTime on Windows, uses avfoundation on macOS.
  - **PNG Sequence** — Image sequence with frame-padded filenames into a versioned subfolder.
  - **H.264 (.mp4 Win)** — Windows only. Playblasts to a temporary PNG sequence, then encodes to H.264 .mp4 using the bundled `ffmpeg.exe`. No QuickTime dependency. Temp PNGs are deleted on success; preserved on failure for debugging. ffmpeg encoding settings: `-c:v libx264 -pix_fmt yuv420p -profile:v high -level 4.2 -preset ultrafast -crf 18 -movflags +faststart`. If ffmpeg is not found, an error dialog shows the expected install path.
- Output filename: `<base>_<tag>_<version>.mov`, `<base>_<tag>_<version>.mp4`, or `<base>_<tag>_<version>/` (PNG subfolder)
- Uses `cmds.playblast()` with `widthHeight=[1920, 1080]`
- Finds a visible model panel for rendering (does not rely on `withFocus` since clicking Export shifts focus)
- Switches the panel to the assigned camera via `cmds.lookThru()`, restores original camera afterward
- **HUD hidden**: `showOrnaments=False` suppresses all heads-up display elements
- **2D Pan/Zoom disabled**: Camera `panZoomEnabled` is temporarily set to `False` during the playblast to prevent pan/zoom overrides from affecting the render
- **Selection cleared**: Viewport selection is cleared before the playblast so no highlight appears, restored afterward
- **Platform-aware format** (.mov only): Prefers `avfoundation` (macOS native) over `qt` (Windows QuickTime). If neither is available, shows a platform-appropriate popup dialog

##### View Transform (Color Management)
- **Render as Raw (sRGB)** (on by default): When enabled, the playblast output color transform is set to the "Raw" view (dynamically detected from available OCIO views by finding the first view name starting with "Raw"). This gives clean sRGB passthrough without tonemapping.
- Controlled via `cmds.colorManagementPrefs(edit=True, outputTransformEnabled=True, outputUseViewTransform=True, outputTransformName=<raw_view>, outputTarget="playblast")` — only the playblast output transform is changed; the main viewport view transform is unaffected
- **Dynamic Raw detection**: Queries `cmds.colorManagementPrefs(query=True, viewNames=True)` and finds the first view starting with "Raw" — handles "Raw", "Raw (Legacy)", and other variants across Maya versions
- Original playblast output transform settings are saved and restored in the finally block

##### Backface Culling (All Playblast Paths)
- **Full backface culling** (value `3`) is applied to every mesh shape node in the scene before the playblast
- This applies to all tabs and all playblast modes (Camera Track wireframe, Matchmove/Face Track shaded)
- Ensures clean rendering in wireframe, shaded, and textured views
- Original per-mesh culling values are saved and restored afterward
- Skipped when "Use Current Viewport Settings" is enabled

##### Camera Track Playblast (Tab 1)
- **Wireframe display**: `displayAppearance="wireframe"` with smooth wireframe enabled
- **Anti-aliasing**: Multisampling AA (`multiSampleEnable`, `multiSampleCount=8`)
- **All geo visible**: Ensures polymeshes, NURBS surfaces, and subdiv surfaces are visible

##### Matchmove Playblast (Tab 2)
- **Display layers forced visible**: All display layers have both `.visibility` and `.playback` attributes set to `True` before the playblast, ensuring nothing is hidden by layer overrides. Original values are saved and restored afterward.
- **Isolate select**: Only the assigned Mesh Group roots (and their descendants) are shown via `cmds.isolateSelect()`. Hides rigs, proxy geo, locators, and all other scene objects. The camera and its image planes are also included so background plates are visible. Restored afterward.
- **Smooth shaded**: `displayAppearance="smoothShaded"` with `wireframeOnShaded=False`
- **Anti-aliasing**: Multisampling AA (`multiSampleEnable`, `multiSampleCount=8`)
- **Motion blur**: VP2.0 hardware motion blur enabled during playblast
- **UV checker overlay**: A temporary shader network (`lambert` + `checker` + `place2dTexture`) is created with user-configurable color, scale, and opacity. Assigned to all meshes within the isolated geo via `cmds.hyperShade()`. `displayTextures` is enabled on the viewport. Original shading engines are saved and restored afterward; temporary `mme_uvChecker_*` nodes are deleted.
- **T-pose excluded**: Uses the original timeline range for the playblast frame range, not the T-pose-adjusted start frame (FBX and ABC exports include the T-pose frame; the playblast does not)

##### Face Track Playblast (Tab 3)
- Same overrides as Matchmove Playblast (display layers, isolate select, smooth shaded, AA, motion blur, UV checker overlay)
- Isolates the Face Mesh Group roots instead of Mesh Group roots

### Progress Bar
- Visual progress bar with percentage label shown during export
- Advances once per completed export format
- JSX export counts as 2 steps (setup + timeline scrub) so the bar advances early before the slow frame-by-frame processing begins
- Hidden after export completes

### Pre-flight Validation & Name Collision Detection
- Pre-flight validation before any export begins, per active tab
- **Validation errors logged to Status panel** as well as shown in a popup dialog, so they remain visible after dismissing the popup
- **Name collision detection**:
  - **Duplicate picks**: Detects the same scene node assigned to multiple role fields (e.g., same node in Camera and Geo Group). Error message identifies both roles.
  - **cam_main conflict**: If the picked camera is not already named `cam_main` and a node named `cam_main` already exists in the scene, an error is raised (the camera rename during export would conflict)
  - **OBJ filename collisions** (Camera Track, JSX enabled): Checks that all geo children (after filtering chisels/nulls/camera) have unique short names. Duplicate names would produce overwriting OBJ files.

### Error Handling
- Per-format try/except (one format failing doesn't block others)
- **Verbose Script Editor errors**: On export failure, `_log_error` writes a formatted error report to Maya's Script Editor via `sys.stderr` (displayed as red text), including the error tag, error message, and full Python traceback. The Status panel shows only a brief "FAILED (see Script Editor)" message.
- Plugin auto-loading for FBX (`fbxmaya`), Alembic (`AbcExport`), and OBJ (`objExport`)
- QuickTime availability check for playblast (popup if missing)
- Selection state saved and restored after all exports
- **Version number in error dialogs**: All error and warning dialogs include "Export Genie {version}" in the message header for easy troubleshooting
- FBX baking delegated to the FBX plugin's internal baking (no scene modification or undo chunks)
- **Matchmove UE5 prep**: Before FBX export, the tool bakes camera animation (translate/rotate/scale) and prepares rigs for Unreal import. Camera baking ensures the camera exports correctly with Z-up axis conversion. The entire prep operation runs in an undo chunk and is reverted after export.
- Face Track conversion uses an undo chunk so the entire operation can be reverted if something fails

## Non-Functional Requirements

- **Platform**: Windows and macOS
- **Maya Version**: 2025+ only
- **UI Framework**: Pure `maya.cmds` (no PySide dependency)
- **Single file**: All code in one `.py` file for simplicity
- **No external dependencies**: Only Maya built-in modules (ffmpeg.exe is an optional bundled binary for the .mp4 playblast format on Windows)
- **String formatting**: `.format()` style (no f-strings, for broader Maya Python compatibility)

## JSX Export Technical Reference

This section documents the complete Maya-to-After Effects conversion pipeline and the critical lessons learned during development. It is intended as a reference for reproducing this work in future projects.

### Reference Materials

The conversion guide `maya_to_after_effects_worldspace.md` describes the general theory. However, several of its recommendations apply specifically to **manually constructed geometry** in AE's coordinate space (e.g., shape layers, point clouds) and do **not** apply to OBJ files imported via `ImportOptions`. The distinctions are documented below.

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

Where `comp_cx = comp_width / 2` and `comp_cy = comp_height / 2` (AE's origin is top-left; comp center offsets to match).

### Scale Factor (`ae_scale`)

```python
ae_scale = 10.0 * cm_per_unit / 2.54
```

This matches SynthEyes's internal convention where `rescale = 10` calibrated against an inch-based unit system. The `cm_per_unit` lookup converts from Maya's current linear unit (mm, cm, in, ft, yd, m) to centimeters.

### Rotation Conversion — Critical Details

This was the hardest part to get right. The rotation matrix itself is straightforward; the Euler decomposition is where things go wrong if the convention is incorrect.

**Step 1: Extract rotation from the LOCAL (objectSpace) matrix.**

Using `cmds.xform(node, query=True, objectSpace=True, matrix=True)`. This excludes parent group orientation — important because SynthEyes often wraps scene content in a tracking group that rotates the Z-up solve to Maya's Y-up convention. The world matrix would include that parent rotation, producing wrong AE rotations. Position still comes from the world matrix (correct absolute placement).

**Step 2: Normalize to remove scale.**

Extract column magnitudes from the local matrix and divide each column to get a pure rotation matrix R.

**Step 3: Apply the T\*R\*T coordinate change-of-basis.**

```
T = diag(1, -1, -1)

TRT produces (from row-major R):
  [[r00, -r01, -r02],
   [-r10, r11,  r12],
   [-r20, r21,  r22]]
```

Then transpose to get column-major `R_ae` for decomposition.

**Step 4: Decompose as Rx\*Ry\*Rz (intrinsic XYZ).**

After Effects applies rotation properties as `Rx * Ry * Rz`. This is the **critical convention** — using `Rz * Ry * Rx` (which is the other common convention) produces angles that look close but are wrong. The correct decomposition from the column-major `R_ae`:

```
 ry = asin(-R_ae[2][0])         # = asin(-r20)
rx = atan2(-R_ae[2][1], R_ae[2][2])  # = atan2(-r21, r22)
rz = atan2(R_ae[1][0], R_ae[0][0])   # = atan2(r10, r00)
```

With gimbal lock handling when `cos(ry) ≈ 0`.

**Why this matters:** In our test scene, the wrong convention (`Rz*Ry*Rx`) produced rx=-18.2, ry=25.5, rz=-0.4. The correct convention (`Rx*Ry*Rz`) produced rx=-19.8, ry=24.3, rz=8.0 — matching the known-working SynthEyes export exactly. The rotation *matrix* was correct in both cases; only the Euler angle extraction differed.

### World-Space Scale

Scale is extracted from the **world** matrix column magnitudes:

```python
sx = sqrt(m[0]**2 + m[1]**2 + m[2]**2)
sy = sqrt(m[4]**2 + m[5]**2 + m[6]**2)
sz = sqrt(m[8]**2 + m[9]**2 + m[10]**2)
```

This captures the full accumulated scale (parent + local). Using `cmds.getAttr(".scaleX")` returns only the local scale attribute, which misses scale inherited from parent groups.

### OBJ Export — Do NOT Flip Vertices

The conversion guide says to flip every vertex `(x, y, z) → (x, -y, -z)`. **This applies to manually constructed geometry in AE's coordinate space, not to OBJ files imported via `ImportOptions`.**

AE's OBJ importer understands the standard Y-up OBJ format natively. The JSX position/rotation/scale properties already handle the Maya-to-AE coordinate transformation for layer placement. Flipping OBJ vertices causes a **double inversion** — the mesh appears upside-down and backwards, making the entire scene look like it's viewed from the bottom-rear.

The correct OBJ pipeline:
1. **Export in local space**: Temporarily reset the node's world matrix to identity before calling `cmds.file(exportSelected=True, type="OBJexport")`, then restore. This prevents Maya's OBJ exporter from baking world-space position into vertices (which would double-offset when AE also applies position/rotation/scale from the JSX).
2. **No vertex modification**: The OBJ file contains standard Y-up local-space geometry. AE imports it as-is.
3. **JSX applies transforms**: Position, rotation, and scale from `_world_matrix_to_ae()` position the mesh correctly in AE's 3D space.

### Simple Plane → AE Solid

Flat meshes (ground planes, cards) are better represented as AE solids than imported OBJ files. Detection uses bounding box flatness: if `min_extent / max_extent < 0.001`, the mesh is considered flat.

The solid is created at comp dimensions, rotated `rx = -90` to lie on the ground plane (AE solids default to the XY plane; `-90` rotates to XZ), and scaled to match the Maya plane's world-space extent:

```
scale_x = (plane_width * ae_scale) / comp_width * 100
scale_y = (plane_depth * ae_scale) / comp_height * 100
```

### OBJ Mesh Scale in AE

AE maps 1 OBJ unit = 512 pixels at 100% scale. The scale applied to imported OBJ layers:

```
scale = world_scale * ae_scale * 100 / 512
```

Where `world_scale` is from the world matrix column magnitudes.

### Camera Rename Safety

The camera is temporarily renamed to `cam_main` for all exports. If a previous export run crashes or is aborted mid-export, the camera may be left renamed. The code checks `cmds.objExists(camera)` before renaming, and falls back to using `cam_main` if it already exists from a prior run.

### Debugging Checklist

When the JSX output doesn't match a known-working reference (e.g., SynthEyes direct export):

1. **Compare camera frame-1 values** (position, rotation, zoom) numerically between the working JSX and your output. They should match within ~0.001.
2. **If positions match but rotations are wrong**: Check the Euler decomposition convention. AE uses `Rx*Ry*Rz`, not `Rz*Ry*Rx`. The matrix itself may be correct while the angles are wrong.
3. **If the mesh is offset from its origin**: The OBJ was likely exported in world space. Use the identity-matrix trick to export in local space.
4. **If the scene appears flipped/upside-down**: OBJ vertices are being double-flipped. Remove any vertex coordinate transformation — AE's OBJ importer handles Y-up natively.
5. **If scale is wrong on geometry**: Check whether you're reading local scale (`cmds.getAttr(".scaleX")`) vs world-space scale (matrix column magnitudes). Parent groups contribute scale that local attributes don't capture.
6. **If rotation differs slightly but consistently**: Check whether you're using the world matrix or local matrix for rotation. Parent group rotations (e.g., SynthEyes Z-up to Y-up conversion groups) should be excluded.

## Face Track Technical Reference

This section documents the Alembic-to-blendshape conversion pipeline and the critical issues discovered during development.

### Why Blendshape Conversion Is Needed

Alembic caches store per-vertex positions at each frame — this is efficient for playback but incompatible with FBX's animation model. FBX represents facial animation through blendshape weights (scalar values animated over time), where each target shape represents a single frame's deformation. The conversion bridges these two representations.

### The InputConnections Discovery

The single most critical finding in the Face Track pipeline: `FBXExportInputConnections -v false` (the default for Tabs 1 and 2) **prevents the FBX plugin from exporting blendshape weight animation**.

The FBX plugin must follow the connection chain: selected mesh → blendShape deformer → weight attributes → animCurve nodes. With input connections disabled, the plugin sees the blendshape targets (topology/deltas via `FBXExportShapes`) but cannot discover the animation curves that drive the weights. The result is an FBX with correct blendshape targets but zero animation.

Setting `FBXExportInputConnections -v true` fixes this — but introduces secondary issues that required their own fixes (see below).

### Secondary Issues from InputConnections=True

Enabling input connections caused the FBX plugin to discover and include nodes that should not be in the export:

1. **Glitchy double geometry**: The original Alembic-driven source mesh was discovered via its AlembicNode connection. Both the source mesh and the converted blendshape mesh ended up in the FBX, causing a visible "pop" where a second copy of the geometry appeared and disappeared. **Fix**: Delete the source mesh after blendshape conversion.

2. **Driven transform timing conflicts**: For transform-animated meshes, `cmds.bakeResults` creates animCurve nodes but doesn't disconnect the original AlembicNode connections. The FBX plugin discovered both the baked curves and the live AlembicNode, causing conflicting animation (delayed/wrong timing). **Fix**: Explicitly disconnect non-animCurve connections after baking.

3. **Alias naming collisions**: `cmds.aliasAttr` can return weight aliases in a different order than creation order, and `_unique_name()` may generate names that look like frame numbers. **Fix**: Key weights by `weight[i]` index instead of alias names — guaranteed creation order.

### FBX File Size Optimization

After keying, the blendShape node stores deltas internally. The full mesh copies used as targets during creation are no longer needed. Deleting the targets group removes N full mesh duplicates from the FBX file (e.g., 270 targets = 270 mesh copies removed).

## Out of Scope (future)
- Batch export of multiple scenes
- Custom FBX/Alembic settings UI
- USD export support
- Network/cloud export paths
- Automatic version incrementing (creating v02 from v01)
- Vertex animation detection/filtering for AE export (simple scenes only in Tab 1)
