# Export Genie - Changelog

---

## v12 to v13

### STMap-Driven Lens Distortion (Mesh Warp)

- New Lens Distortion UI group on Camera Track tab with browse fields for undistort STMap, redistort STMap, and raw plate
- Reads STMap EXR files with a pure-Python EXR reader (no OpenEXR dependency)
- Generates AE Mesh Warp `.ffx` presets for both undistort (remove lens distortion) and redistort (apply lens distortion)
- 11x11 grid resolution with 1/3-neighbour tangent handles matching 3DE4 reference
- Automatic overscan detection from STMap edge values
- Border grid points extrapolated from interior points instead of unreliable STMap edge pixels
- FFX presets named `{shot}_mesh_warp_remove_LD_{version}.ffx` and `{shot}_mesh_warp_apply_LD_{version}.ffx`
- Undistort and redistort adjustment layers added to `_work` comp (disabled by default)
- Diagnostic logging for STMap UV range, overscan, and grid corner positions

### Outer Comp for Lens Distortion

- When STMaps and a raw plate are provided, creates a `<shot>_comp` at raw plate native resolution
- `<shot>_work` comp nested inside `<shot>_comp`, scaled to fit the raw plate resolution
- Redistort mesh warp automatically applied to the work comp layer so CG matches the distorted raw plate underneath
- Raw plate imported as bottom layer in the outer comp
- Outer comp opened in the AE viewer on script run

### AE Project Organization

- `_Comps` and `Plates` folders created in the AE project panel
- Geo assets grouped under their own project folder
- Individual locators (not just "nulls" groups) supported as 3D nulls
- Geo and locator layers set to shy for a cleaner timeline
- Source footage alpha channel ignored to prevent premultiplication issues

### Image Resolution from File Headers

- Reads actual image dimensions from EXR, PNG, JPEG, TIFF, and DPX file headers instead of Maya coverageX/Y attributes
- Sets image plane coverage, origin, and render resolution in exported MA files to match the source plate
- AE JSX comp sized from plate resolution instead of Maya render settings
- Playblast resolution auto-detected from camera image plane source file for all modes (Camera Track, Matchmove, Face Track, Render Preview), capped at 1920 wide

### Face Track Bake Before Playblast

- Bakes Alembic-driven geo transforms before the playblast to eliminate motion blur artifact on frame 1
- Camera bake extended by one pre-roll frame
- Uses temp-file save/restore instead of undo-chunk approach for more reliable scene restoration

### Render Preview

- Replaces the live viewport preview toggle with a single-frame Render Preview
- Opens the rendered frame in the system image viewer
- Full multi-pass composite when ffmpeg is available

### USD Fixes

- `worldspace=True` added to mayaUSDExport so cameras export at the correct world position
- `exportBlendShapes` only enabled when blendShape nodes actually exist, silencing thousands of warnings
- Blendshape meshes wrapped under a temp SkelRoot group for USD face track export

### Clean MA Exports

- Third-party plugin nodes (Arnold, V-Ray, RenderMan, etc.) and unknown nodes stripped from MA exports

### UI and Font Scaling

- All UI font sizes scale from Maya's application font instead of hardcoded pixel values
- Guard against deleted-widget crash in `_refresh_scene_info` via shiboken isValid check

### Installer Improvements

- Drag-and-drop upgrade relaunches the UI immediately so the version updates without restarting Maya
- Force-loads module from disk via `spec_from_file_location` to avoid stale bytecache
- macOS installer copies only platform-relevant ffmpeg binary
- Install splash dialog shown while files are being copied
- `shutil.copy` used instead of `copy2` so timestamp reflects install time
- ffmpeg install status reports "Replaced" instead of "Already installed" on upgrade

### Script Editor Logging

- Version-tagged `LOG_PREFIX` (`[ExportGenie v13]`) in all Script Editor messages
- ffmpeg version included in error reports

---

## v11 to v12

### PySide6/Qt6 UI

- Full UI rewrite from `maya.cmds` to PySide6 with PySide2 fallback
- Collapsible groups, labels above fields, cleaner layout
- Load/Unload toggle: clicking "Load Sel" on a populated field clears it

### Export Folder Field

- Single editable field replaces separate Export Name + Version fields
- Pre-populated from the scene filename, fully editable
- Folder name parsed into base + version for file naming

### Multiple Cameras and Object Tracks

- All tabs now support multiple cameras via +/- buttons, each baked and exported
- New Object Track loader on Camera Track tab for animated object groups
- Alembic-driven and constraint-driven transforms auto-baked before export
- Dynamic +/- field lists on all loaders (Camera, Geo, Static Geo, Rig/Geo, Face Mesh, Object Track)

### Composited Playblasts

- Camera Track playblasts render to temp PNGs and encode via ffmpeg with full HUD metadata overlay
- Image plane resolution used instead of hardcoded 1920x1080
- Motion blur checkbox added to Matchmove / Face Track playblast section (default on)

### QC Spline Crown (Face Track)

- Auto-created per render, point+orient constrained to the face mesh
- Rendered with useBackground shader occlusion and composited via ffmpeg alpha overlay

### AE JSX Fixes

- Composition and all layers start at the correct Maya start frame (e.g., 1001)
- Fixed off-by-one in keyframe timing and footage layer start
- AE folder naming: `{base}_afterEffects_{version}/`, OBJ files: `{base}_{geo}_{version}.obj`

### ffmpeg Font Fix (Windows)

- Font paths written via `-filter_complex_script` with double-escaped colons for reliable drawtext on Windows

---

## v10 to v11

### Scene Protection (FBX Export)

- FBX export no longer relies on Maya's undo chunk to restore the scene after destructive prep (bake, import references, strip namespaces)
- New save-snapshot/reopen approach: saves the scene to a temp file before prep, reopens it after export - guaranteed clean restore
- Snapshot preserves unsaved changes; falls back to the original file on disk if the snapshot fails
- Matchmove tab: export order changed to MA → ABC → Playblast → FBX (non-destructive first, FBX last)
- Face Track tab: export order changed to Playblast → MA → FBX (destructive exports last)

### Smarter Animation Bake

- Constraint-driven non-joint transforms (IK controls, locators, space-switch nodes) are now discovered and baked alongside joints in `prep_for_ue5_fbx_export`
- Scans all constraints under rig_roots, identifies their parent transforms, and includes them in the `simulation=True` bake pass
- Disconnects non-animCurve sources on all baked nodes (joints and transforms) after bake
- Fixes broken animation in rigs where external locators drive IK chains through pointConstraints (e.g. SynthPipe tracker locators → IK anim controls)

### Alembic Camera Bake on Matchmove

- Matchmove tab now detects AlembicNode-driven cameras and bakes TRS + focal length before any exports (matching Camera Track and Face Track behavior)
- Fixes 0-byte ABC exports when the source .abc tracking file is missing or on another drive
- Bake runs in an undo chunk and is restored in the `finally` block

### Custom Export Naming

- New "Export Name" text field in the Export Directory section (between Path and Version)
- Auto-populated from the scene filename via `get_scene_base_name`; fully editable for custom names
- Folder name is now exactly the export name (no more `_track_v##` appended)
- File names inside use `{exportName}_{tag}_{version}.ext` pattern
- All three tabs (Camera Track, Matchmove, Face Track) read from this field
- `build_export_paths` and `build_ae_export_paths` updated to use the custom name
- `resolve_versioned_dir` and `resolve_ae_dir` simplified - no more old-version folder renaming logic

### HUD in Composite Playblasts

- Frame number and focal length HUD now renders on the plate pass in multi-pass composite playblasts (Matchmove and Face Track)
- Previously all three composite passes used `showOrnaments=False`; now the plate pass uses `showOrnaments=show_hud`

### Playblast Color Management Fix

- `_ensure_playblast_raw_srgb` now explicitly sets `outputUseViewTransform=False` for the playblast target before setting the output transform name
- Previously, if "Use View Transform" was enabled for playblast, Maya would ignore the explicit `outputTransformName` and use the viewport's view transform instead
- Added diagnostic logging: current output transform name, useViewTransform state, and target name are logged to Script Editor before applying changes

### Cache-Proof Shelf Button

- `launch()` now clears `sys.modules`, calls `importlib.invalidate_caches()`, and deletes all `ExportGenie.*.pyc` files from `__pycache__/` before importing
- `_restore_ui()` (workspace control restore on Maya startup) does the same cleanup
- Shelf button command string updated to include the same cache-clearing logic
- `_restore_ui()` now updates the workspace control tab label via `cmds.workspaceControl(..., edit=True, label=...)` so the version is always current after restart

### ABC Export Diagnostics

- ABC export now logs the full `AbcExport` job string to Script Editor before running
- Checks for 0-byte output files after export and reports failure
- Full Python traceback printed on exception for easier debugging

---

## v6 to v7

### UE5 FBX Conformance

- FBX exports now use Z-up axis (`FBXExportUpAxis z`) so cameras import into UE5 without the -90 X rotation offset
- Explicit centimeter unit metadata (`FBXExportConvertUnitString cm`, `FBXExportScaleFactor 1`) so UE5 imports at correct scene scale
- Camera animation is now baked during Matchmove UE5 prep, ensuring reliable camera export with axis conversion

### H.264 (.mp4) via ffmpeg

- New "H.264 (.mp4 Win)" playblast format on all three tabs
- Playblasts to a temporary PNG sequence, then encodes to H.264 .mp4 using a bundled ffmpeg.exe (Windows only)
- No QuickTime installation required - ffmpeg is included in the distribution and auto-installed during drag-and-drop setup
- Temp PNGs are automatically cleaned up after successful encoding; preserved on failure for debugging
- If ffmpeg is not installed, the tool shows a clear error dialog with the expected file path

### Playblast Improvements

- HUD elements are now hidden in all playblasts (`showOrnaments=False`)
- Playblast color management now uses the dedicated playblast output transform setting instead of changing the main viewport view transform
- Raw (sRGB) view is detected dynamically by querying available OCIO views for any name starting with "Raw" - handles "Raw", "Raw (Legacy)", and other variants across Maya versions

### Export Naming

- Export files now use tab-specific naming tags: `cam` (Camera Track), `charMM` (Matchmove), `KTHead` (Face Track)
- QC playblast files always use `track` as their naming tag, regardless of tab
- Folder name remains `<scene>_track_<version>/` for all tabs
- Example: Camera Track exports `shot_cam_v01.ma` + `shot_track_v01.mov` into `shot_track_v01/`

### UI Changes

- "Ctrl Rig Group" renamed to "Rig Group"
- "Anim Geo Group" renamed to "Mesh Group"
- Frame range auto-populates when a camera is loaded - start set to 1001, end set to the camera's last keyframe (queries both transform and shape channels)
- Default start frame is now 1001, even if the Maya timeline starts earlier
- "Use Timeline Range" clamps the start frame to a minimum of 1001

---

## v7 to v10

### Rebranding

- Tool renamed from "Maya Multi-Export" to "Export Genie"
- Script filename changed from `maya_multi_export.py` to `ExportGenie.py`
- Shelf button label updated to `ExportGenie`
- Icon filename changed to `ExportGenie.png`

### Preview Playblast

- New "Preview Playblast" toggle button on all three tabs - provides a live viewport preview of what the QC render will look like
- Preview applies all per-tab overrides: camera switch, wireframe/shader, isolate select, checker overlay, motion blur, AA, far clip, grid, backface culling, and color management
- Button turns salmon/red when active ("Exit Preview") with hint text: "Re-toggle preview to apply setting changes."
- Preview sets the live viewport view transform to Raw so it matches the playblast output
- Auto-exits on export or window close; full state restoration on exit

### Playblast Format Picker

- New playblast format dropdown on all three tabs with three options: "H.264 (.mov)", "PNG Sequence", "H.264 (.mp4 Win)"
- On Windows the dropdown defaults to "H.264 (.mp4 Win)" automatically
- PNG sequence output writes frame-padded PNG files into a versioned subfolder

### Far Clip Control

- New far clip slider on all three tabs (Viewport Settings section)
- Default 800,000; range 10,000–2,000,000; field range 1,000–10,000,000
- Applied during both preview and playblast; properly saved and restored afterward

### Dynamic Geo Group Fields

- Camera Track tab now supports multiple Geo Groups with +/- buttons (previously a single field)
- Matchmove tab now supports multiple Static Geo entries with +/- buttons (previously a single field)
- All export functions (`export_ma`, `export_fbx`, `export_abc`) accept a list of geo transforms instead of a single node

### UE5 Matchmove FBX Pipeline

- New `prep_for_ue5_fbx_export` method that: bakes camera animation, bakes animation to skeleton joints, removes constraints, disconnects non-animCurve connections on baked joints, checks joint scale warnings, deletes non-deformer history, freezes transforms on non-skinned geo, strips namespaces
- Entire UE5 prep + FBX export runs inside an undo chunk that is reverted after export, keeping the scene clean
- New `_resolve_name()` function resolves node names to unique DAG paths after namespace stripping
- FBX tangents export enabled (`FBXExportTangents -v true`)
- FBX resample animation always on (`FBXExportBakeResampleAnimation -v true`)

### Playblast Rendering Improvements

- Grid always hidden during playblasts (`grid=False`)
- Flat lighting applied during non-raw playblasts (`displayLights="flat"`)
- NURBS curves hidden during MM/FT playblasts unless a `QC_head_GRP` exists with NURBS curves (then kept visible and added to isolate set)
- Raw (sRGB) color management setting now persists in the scene as a user preference (not restored after playblast)
- Far clip, grid visibility, and all color management settings properly saved and restored

### Face Track Blendshape Fix

- Blendshape target shapes are now kept alive after keying instead of being deleted - the FBX plugin follows InputConnections from base_mesh to blendShape to targets; without them the exported FBX contained no blendshape data
- The undo chunk handles cleanup

### QuickTime Diagnostics (MOV Format)

- New multi-layer QuickTime validation (`_validate_playblast_format`): checks Maya's available formats, Windows registry for QuickTime installation, and disk for QuickTime core files
- Context-aware error dialogs for: not installed, partially installed (missing core files), installed but Maya can't see it, and macOS (AVFoundation missing)

### ffmpeg Improvements

- Pre-validates ffmpeg.exe existence before starting MP4 playblast - skips immediately with a clear message instead of failing mid-export
- Full ffmpeg command line logged to Script Editor (stderr) for debugging
- Drag-and-drop installer now copies the `bin/` directory (containing ffmpeg.exe) alongside the script; existing `bin/` preserved on upgrade

### UI Polish

- "Rig Group" renamed to "Main Rig Group"
- useBackground Shader + Wireframe checkbox now defaults to checked
- Default checker overlay color changed to darker red `(0.6, 0.1, 0.1)`
- Default checker overlay opacity raised from 15% to 30%
- Render as Raw (sRGB) checkbox removed from per-tab UI - Raw color management is now applied automatically
- Window close handler added for proper preview cleanup

### Log & Error Messages

- All status messages simplified to short, user-friendly text (e.g. `"MA skipped - nothing to export."` instead of `"[MA] Nothing to export"`)
- Verbose diagnostics redirected to Script Editor (stderr red text) instead of the in-tool status panel
- All error dialogs now include "Export Genie {version}" in the header

### Installer Overhaul

- Legacy file cleanup: removes old `maya_multi_export.py`, `maya_multi_export.png`, clears `.pyc` cache, evicts `maya_multi_export` from `sys.modules`
- Legacy shelf button cleanup: removes buttons with either `"ExportGenie"` or `"Export_Genie"` labels
- Post-install dialog now shows a detailed list of all installed files and removed legacy files
- Reports ffmpeg status: bundled, already installed from previous version, or not found (with expected path)
