# Export Genie — Changelog

---

## v6 to v7

### UE5 FBX Conformance

- FBX exports now use Z-up axis (`FBXExportUpAxis z`) so cameras import into UE5 without the -90 X rotation offset
- Explicit centimeter unit metadata (`FBXExportConvertUnitString cm`, `FBXExportScaleFactor 1`) so UE5 imports at correct scene scale
- Camera animation is now baked during Matchmove UE5 prep, ensuring reliable camera export with axis conversion

### H.264 (.mp4) via ffmpeg

- New "H.264 (.mp4 Win)" playblast format on all three tabs
- Playblasts to a temporary PNG sequence, then encodes to H.264 .mp4 using a bundled ffmpeg.exe (Windows only)
- No QuickTime installation required — ffmpeg is included in the distribution and auto-installed during drag-and-drop setup
- Temp PNGs are automatically cleaned up after successful encoding; preserved on failure for debugging
- If ffmpeg is not installed, the tool shows a clear error dialog with the expected file path

### Playblast Improvements

- HUD elements are now hidden in all playblasts (`showOrnaments=False`)
- Playblast color management now uses the dedicated playblast output transform setting instead of changing the main viewport view transform
- Raw (sRGB) view is detected dynamically by querying available OCIO views for any name starting with "Raw" — handles "Raw", "Raw (Legacy)", and other variants across Maya versions

### Export Naming

- Export files now use tab-specific naming tags: `cam` (Camera Track), `charMM` (Matchmove), `KTHead` (Face Track)
- QC playblast files always use `track` as their naming tag, regardless of tab
- Folder name remains `<scene>_track_<version>/` for all tabs
- Example: Camera Track exports `shot_cam_v01.ma` + `shot_track_v01.mov` into `shot_track_v01/`

### UI Changes

- "Ctrl Rig Group" renamed to "Rig Group"
- "Anim Geo Group" renamed to "Mesh Group"
- Frame range auto-populates when a camera is loaded — start set to 1001, end set to the camera's last keyframe (queries both transform and shape channels)
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

- New "Preview Playblast" toggle button on all three tabs — provides a live viewport preview of what the QC render will look like
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

- Blendshape target shapes are now kept alive after keying instead of being deleted — the FBX plugin follows InputConnections from base_mesh to blendShape to targets; without them the exported FBX contained no blendshape data
- The undo chunk handles cleanup

### QuickTime Diagnostics (MOV Format)

- New multi-layer QuickTime validation (`_validate_playblast_format`): checks Maya's available formats, Windows registry for QuickTime installation, and disk for QuickTime core files
- Context-aware error dialogs for: not installed, partially installed (missing core files), installed but Maya can't see it, and macOS (AVFoundation missing)

### ffmpeg Improvements

- Pre-validates ffmpeg.exe existence before starting MP4 playblast — skips immediately with a clear message instead of failing mid-export
- Full ffmpeg command line logged to Script Editor (stderr) for debugging
- Drag-and-drop installer now copies the `bin/` directory (containing ffmpeg.exe) alongside the script; existing `bin/` preserved on upgrade

### UI Polish

- "Rig Group" renamed to "Main Rig Group"
- useBackground Shader + Wireframe checkbox now defaults to checked
- Default checker overlay color changed to darker red `(0.6, 0.1, 0.1)`
- Default checker overlay opacity raised from 15% to 30%
- Render as Raw (sRGB) checkbox removed from per-tab UI — Raw color management is now applied automatically
- Window close handler added for proper preview cleanup

### Log & Error Messages

- All status messages simplified to short, user-friendly text (e.g. `"MA skipped — nothing to export."` instead of `"[MA] Nothing to export"`)
- Verbose diagnostics redirected to Script Editor (stderr red text) instead of the in-tool status panel
- All error dialogs now include "Export Genie {version}" in the header

### Installer Overhaul

- Legacy file cleanup: removes old `maya_multi_export.py`, `maya_multi_export.png`, clears `.pyc` cache, evicts `maya_multi_export` from `sys.modules`
- Legacy shelf button cleanup: removes buttons with either `"ExportGenie"` or `"Export_Genie"` labels
- Post-install dialog now shows a detailed list of all installed files and removed legacy files
- Reports ffmpeg status: bundled, already installed from previous version, or not found (with expected path)
