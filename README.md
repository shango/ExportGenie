# Export Genie

**Version v10**

Export Maya scenes to multiple formats (.ma, .fbx, .abc, .jsx, .mov) in a single operation with automatic folder structure and versioning. Three-tab interface serving camera trackers, matchmove/animation artists, and face track artists.

Requires **Maya 2025+**. Windows and macOS.

## Features

- Three-tab workflow for Camera Track, Matchmove, and Face Track pipelines
- Export to Maya ASCII (.ma), FBX (.fbx), Alembic (.abc), After Effects (.jsx + .obj), and Playblast QC (.mov) in one click
- Automatic versioned folder structure based on scene filename
- Editable version number with auto-detection from `_v##` scene naming
- Camera automatically renamed to `cam_main` during export and restored afterward
- Custom shaders stripped to default lambert for .ma exports
- Image plane references preserved in .ma exports
- FBX exports with baked keyframes, skins, and blend shapes
- Alembic exports in world space with UVs
- After Effects ExtendScript export with camera, geo, tracking nulls, and source footage
- Playblast QC at 1920x1080 through the shot camera: H.264 (.mov), PNG sequence, or H.264 (.mp4) via bundled ffmpeg
- Automatic Alembic-to-blendshape conversion for Face Track FBX delivery
- Multiple geo group entries in Camera Track tab
- Multiple static geo entries in Matchmove tab
- Multiple character rig/geo pairs in Matchmove tab
- Multiple face mesh entries in Face Track tab
- Optional T-pose frame for Matchmove FBX and ABC exports
- Render as Raw (sRGB) playblast with OCIO bypass (on by default)
- useBackground Shader + Wireframe overlay for Camera Track QC
- QC Checker Overlay with adjustable color, scale, and opacity (Matchmove and Face Track)
- Anti-Aliasing toggle between 8x and 16x
- Use Current Viewport Settings mode for unmodified playblasts
- Automatic playblast overrides: grid hidden, backface culling, far clip extended, 2D pan/zoom disabled, selection cleared
- Isolate select, motion blur, and forced display layers for Matchmove and Face Track playblasts
- Pre-export validation for missing assignments, duplicate picks, name conflicts, and invalid ranges
- Auto-loading of required plugins (fbxmaya, AbcExport, objExport)
- Rollover tooltips on every widget
- Drag-and-drop install with automatic shelf button

## What's New in v10

- New "H.264 (.mp4 Win)" playblast format — uses bundled ffmpeg to encode from PNG, no QuickTime needed (Windows only)
- FBX exports now import into UE5 with correct camera orientation and scene scale (Z-up axis, centimeter units)
- Camera animation is baked during Matchmove FBX prep for reliable UE5 import
- Playblast HUD and grid are now always hidden
- Playblast color management uses the dedicated playblast output transform instead of the main viewport setting
- Raw (sRGB) playblast view is now detected dynamically across all Maya OCIO configurations
- Renamed "Ctrl Rig Group" to "Rig Group" and "Anim Geo Group" to "Mesh Group"
- Export files now use tab-specific naming tags (`cam`, `charMM`, `KTHead`) while QC playblasts always use `track`
- Frame range auto-populates when a camera is loaded: start 1001, end from the camera's last keyframe
- Default start frame is now 1001, even if the Maya timeline starts earlier
- **Preview Playblast** — live viewport toggle that shows exactly what the QC render will look like (camera, lighting, shaders, checker overlay, color management) without running a full export. Salmon button indicates active preview; auto-exits on export or window close.
- Configurable **Far Clip** slider in Viewport Settings for all tabs (default 800,000)
- **ffmpeg pre-validation** — MP4 exports check for ffmpeg.exe before starting; skipped with a clear message if not found
- Viewport preview now applies the Raw (sRGB) view transform to the live viewport, matching the playblast output
- Default checker overlay opacity changed to 30% (Matchmove and Face Track)
- useBackground Shader + Wireframe checkbox now defaults to checked (Camera Track)
- Simplified log window output — short, user-friendly messages with detailed diagnostics directed to Script Editor
- ffmpeg errors now logged to Script Editor for easier troubleshooting

## What's New in v6

- Fixed exports failing when the camera lives under a static geo or rig group
- Fixed FBX export failing after namespace stripping when short names are ambiguous
- Fixed FBX export failing on scenes with namespaced rigs
- QC playblast format dropdown: choose between H.264 (.mov) or PNG image sequence
- Multiple geo groups on the Camera Track tab with +/- buttons
- Multiple static geo entries on the Matchmove tab with +/- buttons
- Raw (sRGB) playblast now works on Maya configs that label it "Raw (Legacy)"
- Fixed camera rename issue when the camera is already named `cam_main`
- Version number shown in all error dialogs for easier troubleshooting

## Install

1. Extract the distribution folder. It should contain:
   ```
   export_genie/
     ExportGenie.py
     bin/
       win/
         ffmpeg.exe
   ```
2. Drag `ExportGenie.py` into the Maya viewport.
3. A shelf button is added to your current shelf automatically.

That's it. The install automatically copies the script and the `bin/` folder (with ffmpeg) to Maya's scripts directory. Click the shelf button to open the tool.

**Note:** The `bin/` folder enables the "H.264 (.mp4 Win)" playblast format on Windows. If you only have the `.py` file, the tool still works — you just won't have the .mp4 option (H.264 .mov and PNG sequence remain available).

## Upgrade

To update to a newer version, restart Maya, open a fresh scene, then drag the new `ExportGenie.py` into the viewport again. It will overwrite the previous version in your scripts directory and replace the shelf button. If the new version includes an updated `bin/` folder, it will be copied as well. If you're upgrading with just the `.py` file, your existing `bin/` folder is preserved. Restart Maya after upgrading to ensure the new version is fully loaded.

## How to Use

1. Save your scene with a `_v##` version in the filename (e.g. `shot_layout_v03.ma`).
2. Click the **ExportGenie** shelf button.
3. Set the **Export Root** directory.
4. Set the **Version Num** — pre-populated from your scene filename, editable for manual override.
5. Select the appropriate tab for your workflow.
6. Assign roles by selecting objects in the viewport and clicking **Load Sel**.
7. Check the formats you want.
8. Set the **frame range** or click **Use Timeline Range**.
9. Click **EXPORT**.

All widgets have rollover tooltips describing their function.

## Three-Tab Workflow

### Tab 1 — Camera Track Export

For artists who have tracked a camera in SynthEyes (or similar) and brought it into Maya with some reference geometry. Simple scenes — no rigs, no constraints, no vertex animation.

**Export formats**: Maya ASCII (.ma), After Effects (.jsx + .obj), FBX (.fbx), Alembic (.abc), Playblast QC (.mov / .png / .mp4)

**Roles**:
- **Camera** — the tracked camera
- **Geo Group** — top-level geometry group (use +/- buttons to add or remove groups)

### Tab 2 — Matchmove Export

For animators and riggers working with full character rigs, complex vertex-animated objects, or proxy geometry. Supports multiple character rig/geo pairs.

**Export formats**: Maya ASCII (.ma), FBX (.fbx), Alembic (.abc), Playblast QC (.mov / .png / .mp4)

**Roles**:
- **Camera** — the shot camera
- **Static Geo** — proxy/set geometry (use +/- buttons to add or remove groups)
- **Rig Group** / **Mesh Group** — repeatable pairs for multiple characters or animated meshes (use +/- buttons to add or remove pairs)

Example picks for a character rig:
- **Rig Group** → `GenMan_rig_v05:GenMan_rig_hrc`
- **Mesh Group** → `GenMan_rig_v05:GMan_Mesh_GRP`

**T-Pose**: An optional T-pose frame (default: 991) can be included. When enabled, FBX and ABC exports extend their frame range to include the T-pose frame. The .ma export and QC playblast keep the original timeline range.

### Tab 3 — Face Track Export

For artists working with Alembic-cached facial animation (e.g. from face tracking software or animation caches). Supports multiple face mesh entries for multi-character scenes.

**Export formats**: Maya ASCII (.ma), FBX (.fbx), Playblast QC (.mov / .png / .mp4)

**Roles**:
- **Camera** — the shot camera
- **Static Geo** — static geometry for reference
- **Face Mesh Group** — repeatable entries for face geometry groups (use +/- buttons to add or remove entries)

**Automatic blendshape conversion**: Each mesh under a Face Mesh Group is classified as vertex-animated or transform-animated. Vertex-animated meshes (facial deformation) are converted to blendshape targets with per-frame keys. Transform-animated meshes (rigid bodies) have their channels baked. The result is an FBX with blendshape-driven facial animation ready for game engines and real-time renderers.

## Features

### Export Directory and Versioning
- Browse to set your export root directory
- Version number is auto-detected from your scene filename's `_v##` pattern
- Override the version number manually to export under any version
- All exports go into a versioned folder (e.g. `shot_track_v01/`)
- New versions create new folders alongside existing ones

### Export Formats
- **Maya ASCII (.ma)** — Camera renamed to `cam_main`, custom shaders stripped to default lambert, image plane references preserved, frame range matched to UI
- **FBX (.fbx)** — Keyframes baked, skins and blend shapes preserved, cameras included
- **Alembic (.abc)** — World space, UVs included, whole-frame geo sampling (Camera Track and Matchmove tabs)
- **After Effects (.jsx + .obj)** — ExtendScript that rebuilds the 3D scene in AE with camera, geo, tracking nulls, and source footage (Camera Track tab only)
- **Playblast QC (.mov, .png, or .mp4)** — H.264 QuickTime (.mov), PNG image sequence, or H.264 via ffmpeg (.mp4, Windows only) at 1920x1080 through the shot camera

### Viewport Settings (QC Playblast)

Each tab has a collapsible **Viewport Settings** section with controls for the QC render:

- **Render as Raw (sRGB)** (on by default) — Renders the playblast using the Raw color view, bypassing any OCIO tonemapping. All color management settings are restored after the render.
- **useBackground Shader + Wireframe** (Camera Track only) — Applies a useBackground shader to all geo so meshes become transparent (showing the camera plate) with wireframe edges drawn on top. Original shaders are restored after the render.
- **Anti-Aliasing 16x** — Bumps VP2.0 anti-aliasing from 8 to 16 samples. Higher quality but uses more GPU memory.
- **Use Current Viewport Settings** — Skips all viewport overrides and renders the playblast exactly as your viewport looks. Only the camera is switched to `cam_main`.
- **QC Checker Overlay** (Matchmove and Face Track tabs) — Applies a UV checker pattern over all geo with adjustable Color, Scale, and Opacity. The checker shader is created and cleaned up automatically.

### Automatic Playblast Overrides

Unless "Use Current Viewport Settings" is enabled, every QC playblast automatically:

- Hides the grid
- Enables backface culling on all meshes
- Extends the camera far clip plane so distant geometry is visible
- Disables 2D pan/zoom on the camera
- Sets anti-aliasing to 8x (or 16x with the toggle)
- Clears the selection so no highlight outlines appear
- Configures and restores color management settings

Additional overrides for Matchmove and Face Track tabs:

- Isolate select — only assigned geo, camera, and image planes are visible
- All display layers forced visible
- Smooth shaded display with no wireframe overlay
- Display textures enabled (for checker overlay)
- VP2.0 motion blur enabled

### Camera Handling
- Camera is temporarily renamed to `cam_main` during export for consistent naming downstream
- If the camera is already named `cam_main`, it is left as-is
- Original name is restored after export

### After Effects Export Details
- Creates an AE composition matching Maya's render resolution and frame rate
- Camera exported with per-frame position, rotation, and zoom keyframes
- Geo children named "nulls" become AE 3D nulls (SynthEyes tracking markers)
- Geo children named "chisels" are skipped
- Flat planes become AE solids
- All other geo exported as static OBJ files with per-frame transform keyframes
- Source footage from the camera's image plane is auto-imported as a background layer
- Run the .jsx file in After Effects via File > Scripts > Run Script File

### Validation
Before exporting, the tool checks for:
- Missing role assignments
- Duplicate picks (same node in multiple fields)
- Camera name conflicts with existing `cam_main` nodes
- OBJ filename collisions
- Empty export root or invalid frame range
- Empty version number (defaults to v01 with a warning)

Errors are shown in a popup. Warnings let you continue or cancel.

### Plugin Management
Required plugins (`fbxmaya`, `AbcExport`, `objExport`) are auto-loaded when needed. If a plugin can't be loaded, a dialog directs you to the Plug-in Manager.

## Output Folder Structure

All tabs export into a folder named `<scene>_track_<version>/`. Export files use a tab-specific tag while QC playblasts always use `track`:

**Camera Track:**
```
<export_root>/
  shot_track_v01/
    shot_cam_v01.ma
    shot_cam_v01.fbx
    shot_cam_v01.abc
    shot_track_v01.mov
    shot_track_afterEffects_v01/
      shot_ae_v01.jsx
      shot_cam_v01_geo1.obj
      shot_cam_v01_geo2.obj
```

**Matchmove:**
```
<export_root>/
  shot_track_v02/
    shot_charMM_v02.ma
    shot_charMM_v02.fbx
    shot_charMM_v02.abc
    shot_track_v02.mov
```

**Face Track:**
```
<export_root>/
  shot_track_v03/
    shot_KTHead_v03.ma
    shot_KTHead_v03.fbx
    shot_track_v03.mov
```
