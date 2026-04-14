# Export Genie

**Version v13** -- Maya 2025+ / Windows & macOS

One-click export from Maya to .ma, .fbx, .abc, .jsx, and playblast QC. Three tabs for three workflows: Camera Track, Matchmove, and Face Track.

---

## Quick Start -- Camera Track

For tracked cameras with reference geometry. No rigs, no constraints.

1. Open your scene and click the **ExportGenie** shelf button.
2. Set your **Export Root** path and **Export Name** (auto-filled from your scene file).
3. On the **Camera Track** tab:
   - Click your camera in the outliner, then click **<< Load Sel** next to **Camera**.
   - Click your geo group, then **<< Load Sel** next to **Geo Group**. Use **+** to add more groups.
4. Check the formats you want (MA, JSX, FBX, ABC, Playblast).
5. Set your **frame range** (or click **Use Timeline Range**).
6. Hit **EXPORT**.

Your files land in `<export_root>/<export_name>/`.

---

## Quick Start -- Matchmove

For character rigs, animated meshes, and proxy geometry. Supports multiple characters.

1. Open your scene and click the **ExportGenie** shelf button.
2. Set your **Export Root** path and **Export Name**.
3. On the **Matchmove** tab:
   - Load your **Camera**.
   - Load any **Static Geo** (set pieces, environment). Use **+** for more.
   - Load your **Rig Group** and **Mesh Group** as a pair. Use **+** to add more character pairs.
   - Optionally enable **T-Pose** and set the frame (default 991).
4. Check the formats you want (MA, FBX, ABC, Playblast).
5. Set your **frame range** and hit **EXPORT**.

The tool bakes all animation (joints, IK controls, constraints) into clean keyframes and strips namespaces -- ready for Unreal or any game engine.

---

## Quick Start -- Face Track

For Alembic-cached facial animation from tracking software or animation caches.

1. Open your scene and click the **ExportGenie** shelf button.
2. Set your **Export Root** path and **Export Name**.
3. On the **Face Track** tab:
   - Load your **Camera**.
   - Load any **Static Geo** for reference.
   - Load your **Face Mesh Group** -- the group containing your face meshes. Use **+** for more.
4. Check the formats you want (MA, FBX, Playblast).
5. Set your **frame range** and hit **EXPORT**.

Vertex-animated meshes are automatically converted to blendshape targets with per-frame keys -- no manual setup needed.

---

## Install

1. Extract the distribution folder:
   ```
   export_genie/
     ExportGenie.py
     bin/
       win/
         ffmpeg.exe
   ```
2. Drag `ExportGenie.py` into the Maya viewport.
3. A shelf button appears on your current shelf. Click it to open the tool.

That's it. The script and `bin/` folder (with ffmpeg) are copied to Maya's scripts directory automatically.

**Note:** The `bin/` folder enables the H.264 (.mp4) playblast format. Without it, the tool still works -- you just won't have the .mp4 option.

## Upgrade

Restart Maya, open a fresh scene, drag the new `ExportGenie.py` into the viewport. It overwrites the old version and replaces the shelf button. Restart Maya after upgrading.

---

## What's New in v13

- **STMap-driven lens distortion** -- Mesh Warp presets generated from STMap EXR files for undistort and redistort in After Effects. Pure-Python EXR reader, no external dependencies.
- **Outer comp for lens distortion** -- When STMaps and a raw plate are provided, creates a `<shot>_comp` at raw plate resolution containing the scaled `<shot>_work` comp with the redistort mesh warp applied, and the raw footage underneath.
- **AE project organization** -- `_Comps` and `Plates` folders in the AE project panel. Geo assets grouped in their own folder. Individual locators supported as 3D nulls. Geo and locator layers set to shy.
- **Image resolution from file headers** -- Reads actual EXR/PNG/JPEG/TIFF/DPX dimensions instead of Maya coverageX/Y. Sets image plane coverage, origin, and render resolution in exported MA files.
- **Auto playblast resolution** -- Resolution detected from camera image plane source file for all playblast modes, capped at 1920 wide.
- **Render Preview** -- Single-frame composite preview that opens in the system image viewer. Full multi-pass composite when ffmpeg is available.
- **Face Track bake before playblast** -- Bakes Alembic-driven geo transforms and extends camera bake by one pre-roll frame to eliminate motion blur artifact on frame 1. Uses temp-file save/restore instead of undo chunks.
- **USD blendshape fix** -- Only enables exportBlendShapes when blendShape nodes actually exist, silencing thousands of warnings. Wraps blendshape meshes under a temp SkelRoot group for USD face track export.
- **USD camera worldspace** -- Adds worldspace=True to mayaUSDExport so the camera exports at the correct world position.
- **Strip third-party nodes from MA** -- Removes Arnold, V-Ray, RenderMan, and other third-party plugin nodes from MA exports for clean downstream scenes.
- **Font scaling** -- All UI font sizes scale from Maya's application font instead of hardcoded pixel values.
- **Installer improvements** -- Drag-and-drop upgrade relaunches the UI immediately so the version updates without a restart. Force-loads module from disk to avoid stale bytecache. macOS installer copies only platform-relevant ffmpeg. Install splash dialog shown while files are being copied.
- **Raw plate browse field** -- New browse field in the Lens Distortion UI group for picking the raw (distorted) plate.

## What's New in v12

- **PySide6/Qt6 UI** -- Full UI rewrite from `maya.cmds` to PySide6 (PySide2 fallback). Collapsible groups, labels above fields, cleaner layout.
- **Export Folder field** -- Single editable field replaces separate Export Name + Version fields. Pre-populated with the scene filename. Folder name parsed into base + version for file naming.
- **Multiple cameras** -- All tabs now support multiple cameras via +/- buttons. Each camera is baked and exported.
- **Object Track (Camera Track)** -- New loader for animated object groups. Alembic-driven and constraint-driven transforms are auto-baked before export.
- **Dynamic field lists everywhere** -- Camera, Geo, Static Geo, Rig/Geo, Face Mesh, and Object Track loaders all have +/- buttons. Labels above fields.
- **Load/Unload toggle** -- Clicking "Load Sel" on a populated field clears it. Click again to reload.
- **QC spline crown (Face Track)** -- Auto-created per render, point+orient constrained to the face mesh. Rendered with useBackground shader occlusion and composited via ffmpeg alpha overlay.
- **Camera Track composited playblast** -- All Camera Track playblast formats now render to temp PNGs and encode via ffmpeg with full HUD metadata overlay.
- **Image plane resolution** -- Camera Track playblasts match the camera's image plane dimensions instead of hardcoded 1920x1080.
- **Motion blur checkbox** -- Matchmove / Face Track playblast section has a toggle for VP2.0 motion blur (default on).
- **AE JSX frame alignment fix** -- Composition and all layers now start at the correct Maya start frame (e.g., 1001). Fixed off-by-one in keyframe timing and footage layer start.
- **ffmpeg font fix (Windows)** -- Font paths written via `-filter_complex_script` with double-escaped colons for reliable drawtext on Windows.
- **AE folder naming** -- `{base}_afterEffects_{version}/`, OBJ files: `{base}_{geo}_{version}.obj`.

## What's New in v11

- **Scene protection** -- FBX export no longer relies on Maya's undo to restore your scene. The tool saves a snapshot before the destructive bake/prep, exports the FBX, then reopens the snapshot. Your master scene is guaranteed to stay clean.
- **Smarter bake** -- Constraint-driven transforms (IK controls, locators, space-switch nodes) are now baked alongside joints. This fixes broken animation in rigs where locators drive IK chains through constraints.
- **Alembic camera bake on Matchmove** -- Camera driven by AlembicNode is now baked before all exports (matching Camera Track and Face Track). Fixes 0-byte ABC exports when the source .abc tracking file is on another drive.
- **Export order** -- Non-destructive formats (MA, ABC, Playblast) now export first. FBX goes last since it requires baking.
- **Custom export naming** -- New "Export Name" field lets you set the exact folder and file base name. Auto-populated from your scene file, fully editable.
- **HUD in composite playblasts** -- Frame number and focal length now appear in multi-pass composite playblasts (Matchmove and Face Track).
- **Playblast color management fix** -- Raw (sRGB) setting now correctly disables "Use View Transform" for the playblast output.
- **No more stale versions** -- Shelf button and workspace restore clear Python bytecache on every launch. The tab label always reflects the current version.

## What's New in v10

- **H.264 (.mp4) playblast format** -- Uses bundled ffmpeg to encode from PNG sequences. No QuickTime needed (Windows and macOS).
- **UE5-ready FBX** -- Exports now import into Unreal Engine 5 with correct camera orientation and scene scale (Z-up axis, centimeter units).
- **Camera bake for FBX** -- Camera animation is baked during Matchmove FBX prep for reliable UE5 import.
- **Preview Playblast** -- Live viewport toggle that shows exactly what the QC render will look like (camera, lighting, shaders, checker overlay, color management) without running a full export. Salmon button indicates active preview; auto-exits on export or window close.
- **Far Clip slider** -- Configurable far clip plane in Viewport Settings for all tabs (default 800,000).
- **QC Checker Overlay** -- UV checker pattern with adjustable color, scale, and opacity for Matchmove and Face Track playblasts.
- **useBackground Shader + Wireframe** -- Camera Track QC overlay showing the plate through transparent meshes with wireframe edges.
- **Frame range auto-populate** -- Start and end frames fill in automatically when a camera is loaded (start 1001, end from last keyframe).
- **ffmpeg pre-validation** -- MP4 exports check for ffmpeg before starting; skipped with a clear message if not found.
- **Raw (sRGB) playblast** -- Dynamically detects the correct Raw view transform across all Maya OCIO configurations.
- **Tab-specific file naming** -- Export files use tab-specific tags (`cam`, `charMM`, `KTHead`) while QC playblasts always use `track`.
- **Simplified log** -- Short, user-friendly messages in the log window with detailed diagnostics in the Script Editor.
- **Multi-pass composited playblasts** -- Matchmove and Face Track playblasts render plate, color, and matte passes separately, then composite via ffmpeg for clean checker overlays.
- **macOS support** -- ffmpeg bundled for macOS, composite outputs as .mp4 on Mac.

---

## Features

### Export Directory and Naming
- Browse to set your export root directory
- **Export Folder** field is the full folder name -- auto-populated from the scene filename (without extension), fully editable
- Version and tag are parsed from the folder name: `{shot}_{plate}_{tag}_{version}` (e.g., `SHOT001_pl01_track_v03`)

### Export Formats
- **Maya ASCII (.ma)** -- Camera renamed to `cam_main`, custom shaders stripped to default lambert, image plane references preserved
- **FBX (.fbx)** -- All animation baked (joints, IK controls, constraints), skins and blend shapes preserved, UE5-ready settings
- **Alembic (.abc)** -- World space, UVs included (Camera Track and Matchmove tabs)
- **After Effects (.jsx + .obj)** -- Rebuilds the 3D scene in AE with camera, geo, tracking nulls, and source footage (Camera Track only)
- **Playblast QC (.mov, .png, or .mp4)** -- 1920x1080 through the shot camera with frame counter and focal length overlay

### Viewport Settings (QC Playblast)

Each tab has a collapsible **Viewport Settings** section:

- **Render as Raw (sRGB)** -- Bypasses OCIO tonemapping (on by default)
- **useBackground Shader + Wireframe** (Camera Track) -- Transparent meshes showing the plate with wireframe edges
- **QC Checker Overlay** (Matchmove / Face Track) -- UV checker pattern with adjustable color, scale, and opacity
- **HUD Overlay** -- Frame number and focal length burned into every frame
- **Anti-Aliasing 16x** -- Higher quality, more GPU memory
- **Use Current Viewport Settings** -- Renders exactly what your viewport shows
- **Far Clip** slider -- Adjustable camera far clip (default 800,000)

### Playblast Overrides

Unless "Use Current Viewport Settings" is enabled, every playblast automatically hides the grid, enables backface culling, extends far clip, disables 2D pan/zoom, clears selection, and configures color management.

Matchmove and Face Track playblasts also isolate assigned geo, force display layers visible, enable smooth shading, and turn on motion blur.

### Camera Handling
- Camera temporarily renamed to `cam_main` during export for consistent downstream naming
- Original name restored after export

### After Effects Export
- AE composition matching Maya's resolution and frame rate
- Per-frame camera keyframes (position, rotation, zoom)
- "nulls" children become AE 3D nulls (tracking markers)
- "chisels" children are skipped
- Flat planes become AE solids
- Source footage from the image plane auto-imported as background
- Run the .jsx in AE via File > Scripts > Run Script File

### Validation

Before exporting, the tool checks for missing assignments, duplicate picks, camera name conflicts, OBJ filename collisions, invalid frame ranges, and empty version numbers. Errors show in a popup. Warnings let you continue or cancel.

### Plugin Management

Required plugins (`fbxmaya`, `AbcExport`, `objExport`) are auto-loaded when needed. If a plugin can't load, a dialog points you to the Plug-in Manager.

## Output Folder Structure

Exports go into `<export_root>/<export_name>/`:

**Camera Track:**
```
<export_root>/
  <export_name>/
    <name>_cam_v01.ma
    <name>_cam_v01.fbx
    <name>_cam_v01.abc
    <name>_track_v01.mov
    <name>_afterEffects/
      <name>_ae_v01.jsx
      <name>_v01_geo1.obj
```

**Matchmove:**
```
<export_root>/
  <export_name>/
    <name>_charMM_v01.ma
    <name>_charMM_v01.fbx
    <name>_charMM_v01.abc
    <name>_track_v01.mov
```

**Face Track:**
```
<export_root>/
  <export_name>/
    <name>_KTHead_v01.ma
    <name>_KTHead_v01.fbx
    <name>_track_v01.mov
```
