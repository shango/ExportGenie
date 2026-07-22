# ExportGenie v19 - Release Notes

_v18 to v19. Covers the QC/witness camera, the performance repair pass, and the
bug fixes that shipped alongside them._

---

## Headline: the QC / Witness Camera

Camera Track and Matchmove exports now write a second review movie,
`<shot>_qc.mp4`, rendered from a locked-off camera parked beside the shot. It is
there to answer "is this track actually sitting in the world correctly?" - a
question the through-the-lens playblast cannot answer.

- **Locked-off side view.** The QC camera sits exactly 90 degrees around world Y
  from the tracked camera's average aim, and dead level with it. The orientation
  is fixed by design, so every shot's QC movie reads the same way.
- **Automatic framing.** The standoff distance is solved so the frame encloses
  all assigned geo, the tracked camera's entire path, and the origin measuring
  stick, with padding. There is no distance control to get wrong: the solved
  distance is used as is.
- **Ground plane and measuring stick.** A subdivided poly plane at y=0 in soft-red
  wireframe (Maya's viewport grid does not render in an offscreen playblast, so
  the tool builds a real one) plus a true 6 ft measuring stick at the origin,
  unit-aware in cm / inch / metre / whatever the scene uses. Both are witness-only
  and torn down after the render.
- **Scene geo renders as wireframe** so the camera path and ground read through it.
- **Sky dome backdrop.** An artist's existing dome is reused (and hidden from the
  QC render), otherwise an inward-facing hemisphere is built enclosing the geo and
  camera path.
- **Tracked-camera icon scales with the standoff**, so it stays legible on a large
  scene without becoming a giant icon on a small one.
- **Automatic far clip.** The Far Clip spinner is gone. The render far clip is
  derived from the fitted `farClipPlane` (past the geo, the camera path, and the
  dome) plus a margin, instead of being pinned at 800000.

### QC burn-ins

- **Shot name**, top-left at 48px, from the same export name the main playblast
  HUD uses.
- **Frame counter**, 4-digit padded, bottom-right at 64px so it reads at review
  resolution.
- **Scaled-camera warning**, top-right in red. A scale on the camera itself reads
  `CAM SCALE`; a scale inherited from a parent group reads `PARENT SCALE`, so the
  artist is pointed at the node that actually needs fixing rather than at a camera
  whose own attrs read 1,1,1. Every non-default camera in the scene is also
  reported to the log.
- The burned-in shot name is echoed to the log, and if a burn-in cannot be drawn
  the log says which piece is missing rather than shipping a nameless QC movie.

### What the QC framing ignores

Junk geo used to drag the QC camera halfway across the scene. Three classes are
now dropped from the framing solve:

- **Sky domes** (including ambiguously named ones the artist confirms at a prompt).
- **Tracking markers** - SynthEyes `chisel` markers, `tracker` pyramids. These are
  also hidden for the duration of the QC render, since the render is a viewport
  playblast and shows the whole scene, not just the assigned geo.
- **Camera Track only:** geo that is not the rig. Only paths naming
  `genhuman` / `genman` / `lineup` drive the standoff.

Matching runs on every ancestor segment of each shape's full DAG path, so a
correctly named marker nested under a generically named group is still caught.
Excluded geo still renders where appropriate; it just stops pushing the camera
back. The hidden nodes, kept/dropped shape counts, and resulting bounds and
standoff are traced to the Script Editor, so a blown-out frame is diagnosable
without inspection.

---

## Speed Improvements

> **On the percentages:** these are rough engineering estimates from what each
> change does, **not measured benchmarks**. Actual gains scale with scene
> complexity (number of tracked nodes, frame count, zoom vs. static lens), so
> each is given as a range with its condition. Treat them as order-of-magnitude,
> not precise.

- **Batched animation baking** (~50-90% less bake time) - object tracks and
  face-track geo bake in a single timeline playthrough instead of one pass per
  node. Savings scale with node count: N nodes go from N passes to 1, so the
  more objects in the scene, the closer to the top of that range.
- **No more per-frame timeline scrubbing** (~40-70% faster JSX/AE export) -
  camera, mesh, and locator matrices are read via timed `getAttr` instead of
  scrubbing the whole timeline once per object; avoids a full scene
  re-evaluation per frame per object.
- **Suspended viewport redraws** (~20-40% faster on bake/blendshape steps) -
  Maya no longer redraws the viewport on every frame during camera bake and the
  blendshape conversion loop.
- **Faster QC/HUD encoding on zoom shots** (up to ~10x on long zooms; ~0% on
  static-lens shots) - HUD frame-number burn-in is capped at 60 filter runs.
  Zoom shots previously created one drawtext per frame, making encode time grow
  with frames squared; static lenses were already fine.
- **Focal-length sampling gated** (~seconds to minutes saved on long shots
  without a HUD) - the per-frame focal-length sweep only runs when a HUD is
  actually being burned and the lens is not static.
- **Lighter PNG fallback** (~95%+ less time on the fallback copy) - rendered
  frames are moved instead of copying multi-gigabyte sequences; a move is near
  instant vs. a full byte copy.
- **Faster EXR reads** (~2-5x on the decode step) - the pure-Python EXR decode
  is vectorized and allocates (h,w,2) instead of (h,w,4). Verified against a
  standalone synthetic-EXR test suite.
- **Cached probes** (fixed cost removed per encode, seconds each) - ffmpeg path,
  drawtext capability, and plate-resolution lookups are memoized; previously
  re-globbed network plate dirs and respawned ffmpeg on every encode.
- **Fewer scene queries** (~5-15% on export prep) - one-pass display-layer
  filtering, a single shared mesh sweep for USD prep, deduped FBX skin-influence
  walks, batched Alembic-driver detection across all three handlers, batched
  plugin-node deletion and MA shader reassignment, batched history type checks
  via `cmds.ls(type=)`, and a static-plug result cache reused across blendshape
  weights.
- **Cheaper QC framing math** (~seconds on long shots) - camera-path sampling for
  the witness framing and sky-dome bounds is stride-capped instead of walking
  every frame, and the multi-camera far-clip fit measures each geo bbox once per
  frame instead of once per camera per frame.
- **Skip redundant save/reload** (one full scene save/reload avoided) -
  face-track export no longer saves and reloads the scene a second time when no
  camera bake ran.
- **No backface-culling churn** on intermediate shapes during export prep.

### Still on the list

These are real wins that change rendering or scene behaviour rather than just
call counts, so they need in-Maya visual regression testing before they ship:

- Rewriting the ABC-to-blendshape conversion against the OpenMaya API (a single
  timeline pass writing point targets directly, instead of a duplicate mesh per
  frame). This is the biggest remaining face-track cost: minutes to seconds.
- Feeding the original plate sequence straight to ffmpeg for the composite pass
  instead of playblasting the image plane over the full timeline, removing one
  of three to five full viewport passes.
- Sharing one face-track prep between the USD and FBX exports, which currently
  prep twice with a full scene reload in between.

---

## Bug Fixes

- **Unreal FBX camera rotation** - a camera parented under a group exported to
  FBX no longer lands ~90 degrees off in Unreal. Unreal's axis conversion and
  camera-aim fix do not compose through a parent null, so FBX export now
  substitutes a standalone, world-space-baked copy of the camera. FBX only; the
  original hierarchy is untouched.
- **QC camera no longer clips its subject** - the solved standoff is used as is,
  with only the frame margins and the keep-the-eye-in-front-of-the-bounds floor
  applied. An earlier pull-in was cropping the tracked camera icon.
- **EXR resolution fallback** - multi-channel plates no longer silently fall
  back to 1920x1080 from a too-small header read (the header read is now 64KB).
- **Image plane depth under scaled parents** - Camera Track preview and playblast
  auto-fit the image plane correctly when the camera sits under a scaled parent,
  and the VP2 buffer is warmed so frame 1 is no longer brighter than the rest.
- **Undo / state safety** - export uses an exception-safe undo chunk and
  restores playback state, viewport background, and image-plane settings even on
  error.
- **ffmpeg timeouts scale with frame count**, so long shots no longer trip a
  fixed timeout mid-encode.
- **Preview temp-dir leak** fixed.
- **Export folder** is no longer clobbered by a scene save after the user edited
  it.
- **UI** - collapse/expand no longer un-hides intentionally hidden buttons.
- **QC witness grid** readability restored (finer subdivisions, grid lines
  forced on regardless of the artist's grid prefs).
- **Status window** stays broad and readable; technical breadcrumbs go to the
  Script Editor instead.
