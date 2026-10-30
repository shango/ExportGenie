# Export Genie v23.4 beta 2 - What's New

Everything added since v22, from v23 up to this beta.

---

## New in v23.4 beta 2

### New folder and file naming (Pre Pro 3d publishing)

- Every shot now has one folder, `SHOT_pl01_prePro3d`, with no version
  in its name. Camera Track, Matchmove and Face Track all export into it.
- Each product has its own name and version: `cam`, `charMM` and
  `KTHead`. The version comes from your Maya scene name, so
  `SHOT_pl01_cam_v04.ma` exports `SHOT_pl01_cam_v04.abc`, `.fbx`, `.ma`
  and so on.
- The movies are named after their product too: `SHOT_pl01_cam_v04.mp4`
  instead of `SHOT_pl01_track_v04.mp4`, plus `_qc.mp4` and `_array.mp4`
  next to it.
- The Export Folder field now just shows the folder. It can't be edited.
- A scene name without a version (`_v01`, `_v02`...) can't be exported.
- Older exports in versioned folders (like `SHOT_pl01_cam_v04/`) stay
  where they are. New exports go into the `_prePro3d` folder.

### Resolution checks

- Before a Camera Track export with STMaps, Export Genie compares the
  camera's back plate, both STMaps and the raw plate. If they don't fit
  together, for example an HD STMap with a 4K plate, it warns you and
  lists all the sizes. You can still continue.
- The playblast burn-in now shows the real plate size (for example 4K)
  instead of the smaller review movie size.

---

## New in v23.4 beta 1

### Tell Export Genie where your STMaps came from

The Lens Distortion section on the Camera Track tab has a new row:
**STMaps exported from: SynthEyes / 3DEqualizer**.

- Tick the one you used. Only one can be ticked at a time.
- If you've added an STMap and haven't picked one, Export Genie stops and
  asks you to choose before it exports.
- No STMaps? Nothing changes for you.

SynthEyes and 3DEqualizer lay out their STMaps a little differently.
Knowing which one you used lets Export Genie set up the Nuke script to
match, so the distortion lines up.

### New Nuke QC script

When you export with STMaps, the Nuke script now comes from the team's
latest QC template and opens cleanly in Nuke 17. It has two new sections,
and Export Genie loads your footage into them for you:

- **STMap Double-Check:** a quick way to confirm your STMaps undo and redo
  the lens distortion correctly.
- **Comp starter:** a ready-made setup for putting CG back onto the
  original, distorted plate.

Everything that was in the QC script before is still there, including the
playblast movie output.

---

## v23.3: Your scene is left exactly as you had it

- **Your scene comes back untouched after every export.** Camera Track,
  Matchmove and Face Track exports now put your scene back the way it was
  when they finish, whether the export worked, failed or was cancelled.
  Before, things like the sky dome or a changed far clip could be left
  behind in your scene.
- **New Cancel button** next to the progress bar. One click stops the
  export and restores your scene.
- While an export runs, the rest of the window is locked so you can't
  change things mid-export by accident.
- **Render Preview** no longer leaves your camera's far clip or image
  plane changed after it renders.

## v23.2: Scale warnings

Before exporting, Camera Track and Matchmove now check that the scene is
at real-world scale and warn you if something looks wrong:

- The scene isn't set to centimetres.
- There's no GenHuman in the scene to compare against.
- The GenHuman is shorter than 140 cm or taller than 210 cm.
- The camera, or the group it sits in, has been scaled.

These are warnings only. You can choose to continue or cancel.

## v23.1: Cleaner Camera Track files

- **Camera Track Alembic files no longer carry namespaces** in their
  object names, so they come in clean in other apps. Matchmove and Face
  Track keep them, because two characters from the same rig can only be
  told apart by their namespace.
- **Stricter camera slot.** "Load Sel" for the camera now only accepts the
  camera itself. Selecting a group or several objects shows an error
  instead of loading the wrong thing.

## v23: Array Cam playblast

A new, optional review movie on the **Camera Track** tab (on by default).

- It renders through your tracked camera with a large 3D grid of small
  wireframe shapes fixed in the world, about 60 ft across.
- If the track is off, the grid visibly drifts or slides against the
  plate, so problems are easy to spot.
- The geo and object tracks you assigned on the Camera Track tab also show
  up in it, so you can judge them against the grid too.
- The grid is never hidden by the plate or cut off by the far clip, and
  everything is put back after the movie is made.

---

## Please test

This is a beta. In particular, please:

- Export a shot from each tab and check that everything lands in the
  `_prePro3d` folder with the right names and versions.
- Try the STMap changes on a real shot, once with SynthEyes STMaps and
  once with 3DEqualizer STMaps, and report anything that looks off in the
  Nuke script.
- Tell us if the resolution warning pops up when it shouldn't, or stays
  quiet when the sizes are wrong.
