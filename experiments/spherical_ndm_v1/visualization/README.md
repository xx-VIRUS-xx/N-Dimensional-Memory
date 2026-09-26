# Spherical NDM v1 Visualization

An interactive 3D diagnostic tool for inspecting the entity-point/dimension structure of the Spherical NDM v1 experiment.

## Input Files Consumed

This visualization reads from and renders data from:

- `../corpus/raw_events.jsonl` — Raw event texts (t0–t9)
- `../extraction/entity_dimensions.jsonl` — LLM-extracted entity dimensions for each event
- `../space/reference_dimensions.json` — Space metadata (conversationByTime dimension)
- `../space/space_definition.md` — NDM space definition (read for context; not consumed programmatically)

## Running the Visualization

1. Open `index.html` in a modern web browser
2. The visualization loads automatically with embedded data

No build step, no server required—it's self-contained.

## Controls

| Input | Action |
|-------|--------|
| **Left Mouse Drag** | Rotate view |
| **Right Mouse Drag** | Pan view |
| **Scroll Wheel** | Zoom in/out |
| **Click Point** | Select and inspect point |
| **Click Entity Name** | Navigate to first occurrence of entity |
| **Time Slider** | Filter events (show t0 through selected time) |
| **Entity Checkboxes** | Hide/show entities by name |
| **Dimension Checkboxes** | Hide/show specific dimension keys in the inspector |

## Features

### Time Navigation
- Slider controls conversationByTime progression (t0 → t9)
- Points are only visible up to the selected time
- Reference dimension ordering is preserved

### Entity Filtering
- Uncheck entity names to hide all occurrences
- Occurrence count shown for each entity
- Visible entity list updates dynamically

### Dimension Filtering
- Dimension keys are collected dynamically from all extracted dimensions actually present in `entity_dimensions.jsonl`
- Uncheck a key to hide it from the inspector panel for every point
- Filtering only affects display; underlying data is never altered

### Point Inspection
- Select any point to view:
  - Entity name and event timestamp
  - Full event text from raw_events.jsonl
  - Extracted dimensions from entity_dimensions.jsonl
  - All occurrences of that entity across time
- Point highlighting on selection (yellow emissive)

### Visualization Semantics

Each point in the space represents **P(entity, event)**—a distinct occurrence of an entity in an event.

- **X, Y axes**: No predetermined meaning (random jitter for clarity)
- **Z axis**: conversationByTime ordering (t0 at origin, t9 at z = 18)
- **Color**: Consistent per entity (hash of entity name)
- **Grid**: XZ plane reference (XY is time/entity space)

### Explicit Design Constraints

Per the agent prompt:

1. ✓ Entities are points; repeated occurrences are different points
2. ✓ conversationByTime is the reference dimension and orders events t0 → tN
3. ✓ Extracted dimensions are semantic metadata attached to each point
4. ✓ No relationship edges are created (only present data)
5. ✓ No inferred formulas or mathematical claims are presented
6. ✓ Ambiguity in extraction results is preserved (shown as-is)
7. ✓ Geometric proximity is **not** presented as proof of semantic relationship
8. ✓ Source artifacts (raw events, entity dimensions, space definition) are not modified

## Purpose

This visualization is a **diagnostic instrument** for the research team to:

- Inspect the actual point structure before defining distance metrics
- Verify LLM extraction results visually
- Explore entity occurrences and their dimensional attributes across time
- Preserve ambiguity for later mathematical analysis

Geometric proximity **must not** be interpreted as semantic relationship. The position of points in XY space is arbitrary; the Z-axis progression encodes time via conversationByTime.

## Technical Details

- **Framework**: Three.js for 3D rendering
- **Data**: Embedded JSON (raw_events, entity_dimensions, reference_dimensions)
- **Interactivity**: Mouse controls + sidebar filters
- **No external dependencies**: Loads Three.js from CDN; all other code is inline

## Notes

- The visualization is read-only; it does not modify source data or create new files
- Browser console may show Three.js warnings (non-fatal)
- Tested on Chrome, Firefox, Safari; WebGL required
