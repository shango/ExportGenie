# Blender Camera Track Export — Feature Research & Implementation Pathway

## Context

Export Genie's Camera Track tab currently exports to .ma, .fbx, .abc, .jsx, and playblast formats. A Blender export option would allow artists to bring tracked cameras (with animated focal length) into Blender without manual recreation. This document captures the research and outlines the implementation path for a future update.

---

## Current State (Maya Side)

### What the Camera Track tab exports today
- **Camera transforms**: baked per-frame via `cmds.xform(camera, q=True, ws=True, matrix=True)`
- **Focal length**: read once as a **static value** — `cmds.getAttr(cam_shape + ".focalLength")`
- **Film aperture**: `cmds.getAttr(cam_shape + ".horizontalFilmAperture")` (inches)
- **Image plane**: source footage path extracted if present
- **Geometry**: optional geo groups and proxy geo hierarchies
- **Camera rename**: always renamed to `cam_main` during export

### Key gap
Focal length is **not** sampled per-frame. For Blender export with animated focal length, the extraction loop must query `focalLength` at each frame.

---

## Blender Python API Findings (bpy 4.5, confirmed via Context7)

### Camera creation
```python
cam_data = bpy.data.cameras.new("cam_main")
cam_data.lens = 35.0                    # focal length in mm
cam_data.sensor_width = 36.0            # in mm (Maya stores in inches × 25.4)
cam_data.clip_start = 0.1
cam_data.clip_end = 1000.0

cam_obj = bpy.data.objects.new("cam_main", cam_data)
bpy.context.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
```

### Transform keyframes (on the object)
```python
scene.frame_set(frame)
cam_obj.location = (tx, ty, tz)
cam_obj.rotation_euler = (rx, ry, rz)
cam_obj.keyframe_insert(data_path="location", frame=frame)
cam_obj.keyframe_insert(data_path="rotation_euler", frame=frame)
```

### Focal length keyframes (on the camera data block)
```python
cam_data.lens = focal_length_mm
cam_data.keyframe_insert(data_path="lens", frame=frame)
```

This is the critical finding — `keyframe_insert` works on any animatable property of the data block, and `lens` is fully supported. No workarounds needed.

### Scene setup
```python
scene.frame_start = 1001
scene.frame_end = 1200
scene.render.fps = 24
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
```

---

## Coordinate System Conversion

| | Maya | Blender |
|---|---|---|
| Up axis | Y | Z |
| Handedness | Right | Right |
| Units | cm | m (by default, but configurable) |

### Recommended approach: matrix-based conversion

The codebase already extracts 4×4 world-space matrices via `cmds.xform(..., matrix=True)`. The conversion is:

1. Read Maya's 4×4 row-major matrix
2. Apply axis-swap matrix (swap Y↔Z rows/columns, negate new Y)
3. Scale translation by 0.01 (cm → m)
4. Decompose into Blender location + Euler rotation

This avoids gimbal issues that a naive Euler-angle swap would have. The existing `_jsx_camera` method in ExportGenie.py (lines ~2777–2904) already does similar matrix decomposition for After Effects — that logic can be adapted.

---

## Implementation Pathway

### Step 1 — Per-frame focal length extraction

Modify the camera data extraction to sample `focalLength` at each frame alongside the transform matrix. Also capture:
- `horizontalFilmAperture` (→ `sensor_width` in mm)
- `verticalFilmAperture` (→ `sensor_height` in mm)
- `horizontalFilmOffset` / `verticalFilmOffset` (→ `shift_x` / `shift_y`)
- `nearClipPlane` / `farClipPlane`
- `cmds.getAttr(camera + ".rotateOrder")` for correct Euler decomposition
- `cmds.playbackOptions(q=True, fps=True)` for frame rate

### Step 2 — Generate a standalone .py script

Output a Python script that, when run inside Blender (File → Run Script or CLI `blender --python script.py`), builds the scene:

1. Clear default objects or create a fresh scene
2. Set frame range, FPS, render resolution
3. Create camera data + camera object with static properties (sensor, clip planes, film offset)
4. Loop over baked frame data, per frame:
   - Apply coordinate conversion (matrix → Blender location + rotation)
   - Set `cam_obj.location`, `cam_obj.rotation_euler`, `cam_data.lens`
   - Insert keyframes for all three
5. Set as active scene camera
6. Optionally set up background image from image plane path

Output filename: `shot_cam_v01_blender.py` (follows existing naming pattern with `cam` tag)

### Step 3 — UI integration

Add a "Blender (.py)" checkbox to the Camera Track tab's export format section, alongside the existing .ma, .fbx, .abc checkboxes. No new UI sections needed.

### Step 4 — Optional enhancements (later)

- Film offset animation (if non-static)
- Background image setup from image plane
- Geo import hints (print instructions for importing the .abc/.fbx in Blender)
- Direct .blend file writing (heavier dependency, less portable)

---

## Risks & Edge Cases

| Risk | Mitigation |
|---|---|
| Rotation order mismatch | Query Maya's `rotateOrder` attr; set matching `rotation_mode` on Blender object |
| Gimbal lock with Euler angles | Use matrix decomposition, not direct Euler remapping |
| Unit scale (cm vs m) | Divide translation by 100; document that Blender scene should use metric |
| Film offset (lens shift) | Map `horizontalFilmOffset` / `verticalFilmOffset` to `shift_x` / `shift_y` — units differ (inches vs normalized), needs conversion |
| Large frame counts | Baked per-frame data can make large scripts; acceptable for camera-only data |
| Blender version compatibility | `keyframe_insert` API is stable across 3.x–4.x; the low-level action/slot/strip API changed in 4.5 but the high-level method hasn't |

---

## Key Files to Modify (When Ready)

| File | Change |
|---|---|
| `ExportGenie.py` — `_jsx_camera` area (~line 2777) | Reference for matrix extraction pattern to adapt |
| `ExportGenie.py` — `_run_camera_track` (~line 6060) | Add Blender .py export call alongside existing formats |
| `ExportGenie.py` — `_build_tab_camera_track` | Add "Blender (.py)" checkbox to UI |
| `ExportGenie.py` — new method `_export_blender_cam` | Generate the .py script with baked camera data |

---

## Summary

The Blender Python API fully supports animated focal length via `cam_data.keyframe_insert(data_path="lens", frame=N)`. The main work is: (1) extending the Maya-side extraction to sample focal length per-frame, (2) writing a coordinate conversion from Maya Y-up matrices to Blender Z-up, and (3) generating a self-contained .py script. No external dependencies required on either side.
