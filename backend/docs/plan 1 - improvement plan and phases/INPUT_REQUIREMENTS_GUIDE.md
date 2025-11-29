# CADLift Input Requirements Guide 📋

Comprehensive guide to preparing input files for optimal results with CADLift.

---

## Table of Contents

1. [DXF Files](#dxf-files)
2. [Image Files](#image-files)
3. [Text Prompts](#text-prompts)
4. [General Limits](#general-limits)

---

## DXF Files

### Supported Versions

| DXF Version | AutoCAD Version | Status |
|-------------|-----------------|--------|
| R12 | AutoCAD Release 12 | ✅ Supported |
| R13-R14 | AutoCAD 13-14 | ✅ Supported |
| R2000 | AutoCAD 2000-2002 | ✅ Supported |
| R2004 | AutoCAD 2004-2006 | ✅ **Recommended** |
| R2007-R2010 | AutoCAD 2007-2010 | ✅ **Recommended** |
| R2013-R2018 | AutoCAD 2013-2024 | ✅ **Recommended** |

**Recommendation:** Use **DXF 2013 (R2013)** or **DXF 2018 (R2018)** for best compatibility.

---

### Supported Entities

CADLift processes the following DXF entities:

| Entity Type | Support Level | Description |
|-------------|---------------|-------------|
| **LWPOLYLINE** | ✅ **Full** | Lightweight polylines (preferred) |
| **POLYLINE** | ✅ **Full** | Regular polylines |
| **LINE** | ✅ **Full** | Individual line segments |
| **CIRCLE** | ✅ **Full** | Circular arcs (converted to polygons) |
| **ARC** | ✅ **Full** | Circular arcs |
| **TEXT** | ⚠️ **Partial** | Room labels (extracted for metadata) |
| **MTEXT** | ⚠️ **Partial** | Multiline text (extracted for metadata) |
| **INSERT** | ❌ Not supported | Blocks/references (ignored) |
| **HATCH** | ❌ Not supported | Fill patterns (ignored) |
| **DIMENSION** | ❌ Not supported | Dimensions (ignored) |
| **SPLINE** | ❌ Not supported | Curved lines (not supported yet) |

---

### File Requirements

#### File Format
- **Extension:** `.dxf`
- **Encoding:** ASCII or UTF-8
- **Max Size:** 50 MB
- **Compression:** Not supported (use uncompressed DXF)

#### Geometry Requirements
✅ **Required:**
- At least one **closed polyline** representing a room boundary
- Polylines must be properly closed (start point = end point)
- All coordinates in same unit system (millimeters recommended)

⚠️ **Recommended:**
- Use LWPOLYLINE instead of LINE entities
- Keep geometry on layer 0 or named layers (e.g., "WALLS", "ROOMS")
- Remove unnecessary entities (dimensions, text, hatches)
- Clean file with `PURGE` command before exporting

❌ **Avoid:**
- Self-intersecting polygons
- Duplicate vertices
- Zero-length edges
- Open polylines (gaps in geometry)
- 3D geometry mixed with 2D floor plan

---

### Preparing Your DXF

#### Step 1: Clean Up in AutoCAD

```
1. Remove unnecessary layers:
   Command: PURGE
   Select: All
   Purge unused layers, blocks, styles

2. Join separate lines into polylines:
   Command: PEDIT
   Select lines: M (Multiple)
   Type: J (Join)
   Fuzz distance: 0.1
   Press Enter

3. Close open polylines:
   Command: PEDIT
   Select polyline
   Type: C (Close)

4. Check for errors:
   Command: AUDIT
   Fix errors: Yes
```

#### Step 2: Verify Geometry

```
1. Select a polyline
   Command: LIST

2. Check properties:
   ✅ Entity type: LWPOLYLINE or POLYLINE
   ✅ Closed: Yes
   ✅ Area: > 0
   ✅ Vertices: 4+ (for rooms)

3. Visual check:
   Command: ZOOM
   Type: E (Extents)
   Verify all rooms visible
```

#### Step 3: Export as DXF

```
Method 1: Save As
1. File → Save As
2. File type: AutoCAD 2018 DXF (*.dxf)
3. Save

Method 2: DXFOUT Command
1. Command: DXFOUT
2. Choose save location
3. Select DXF version: 2018 or 2013
```

---

### Layer Conventions

CADLift processes all layers by default. You can optionally filter specific layers:

**Recommended layer names:**
- `WALLS` or `WALL` - Wall outlines
- `ROOMS` or `ROOM` - Room boundaries
- `DOORS` or `DOOR` - Door locations (future support)
- `WINDOWS` or `WINDOW` - Window locations (future support)

**Using layer filter:**
```json
{
  "params": {
    "layer_filter": ["WALLS", "ROOMS"],
    "extrude_height": 3000
  }
}
```

---

### Common DXF Issues

#### Issue: "No closed shapes found"

**Causes:**
- Lines are not connected
- Polylines have gaps
- Using LINE instead of LWPOLYLINE

**Solutions:**
```
1. Join lines:
   PEDIT → M → J → Fuzz: 0.1

2. Use BOUNDARY to create polylines:
   Command: BOUNDARY
   Click inside each room

3. Check closure:
   LIST command → Check "Closed: Yes"
```

#### Issue: "Self-intersecting polygon"

**Causes:**
- Walls cross each other
- Duplicate vertices
- Incorrect topology

**Solutions:**
```
1. Remove duplicates:
   Command: OVERKILL
   Tolerance: 0.1

2. Fix intersections:
   Manually edit crossing lines
   Use BREAK or TRIM commands

3. Redraw if necessary:
   Use PLINE to trace clean outline
```

---

### DXF Best Practices

✅ **DO:**
- Use closed LWPOLYLINE entities
- Keep units consistent (millimeters recommended)
- Use simple, rectangular rooms when possible
- Export in DXF 2013 or 2018 format
- Clean file with PURGE before exporting
- Test in a CAD viewer before uploading

❌ **DON'T:**
- Mix 2D and 3D geometry
- Include dimensions, text, or hatches in geometry layers
- Use curved walls unless necessary (SPLINE not supported)
- Include furniture or fixtures in room outlines
- Use blocks or external references (xrefs)

---

## Image Files

### Supported Formats

| Format | Extension | Max Size | Color Support |
|--------|-----------|----------|---------------|
| PNG | `.png` | 20 MB | RGB, Grayscale |
| JPEG | `.jpg`, `.jpeg` | 20 MB | RGB |

**Recommendation:** Use **PNG** for best quality (lossless compression).

---

### Image Requirements

#### Resolution
- **Minimum:** 1000 × 1000 pixels
- **Recommended:** 2000 × 2000 pixels or higher
- **Optimal:** 3000 × 3000+ pixels

**Why higher is better:**
- Better line detection
- More accurate vectorization
- Cleaner output geometry

#### Quality
- **DPI:** 300+ DPI for scans
- **Contrast:** High contrast (black walls, white background)
- **Sharpness:** Clear, focused image
- **Lighting:** Even lighting, no shadows

---

### Preparing Your Image

#### Best Practices

✅ **DO:**
- Use high-resolution scans (300+ DPI)
- Ensure good contrast (adjust in image editor)
- Straighten the image (walls should be vertical/horizontal)
- Remove all furniture, dimensions, annotations
- Use black walls on white background
- Crop to show only floor plan

❌ **DON'T:**
- Use low-resolution photos (<1000px)
- Include cluttered or busy images
- Use color images with poor contrast
- Include multiple floor plans in one image
- Have shadows or uneven lighting
- Include text or dimensions overlapping walls

---

### Image Preprocessing

**Recommended workflow:**

1. **Scan or photograph:**
   - Use scanner at 300+ DPI
   - Or use good camera with steady hand
   - Ensure image is straight and well-lit

2. **Open in image editor** (Photoshop, GIMP, Paint.NET):
   ```
   1. Rotate to straighten (walls horizontal/vertical)
   2. Crop to floor plan only
   3. Adjust levels/curves for high contrast
   4. Convert to grayscale (optional)
   5. Threshold to black & white (optional)
   6. Erase furniture, text, dimensions
   7. Ensure walls are solid black lines
   8. Background should be clean white
   ```

3. **Save as PNG:**
   - File → Save As → PNG
   - 8-bit color depth
   - No compression artifacts

---

### Image Processing Parameters

**API Parameters:**
```json
{
  "params": {
    "extrude_height": 3000,
    "wall_thickness": 200,
    "only_2d": false,
    "simplify_epsilon": 2.0
  }
}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `extrude_height` | Number | 3000 | Height in mm for 3D extrusion |
| `wall_thickness` | Number | 200 | Wall thickness in mm |
| `only_2d` | Boolean | false | If true, output 2D DXF only |
| `simplify_epsilon` | Number | 2.0 | Douglas-Peucker simplification factor |

**Simplify Epsilon:**
- Lower value (0.5-1.0): More detail, more vertices
- Default (2.0): Balanced detail and simplicity
- Higher value (5.0-10.0): Simplified, fewer vertices

---

### Common Image Issues

#### Issue: "No contours detected"

**Causes:**
- Image too blurry
- Poor contrast
- Walls not visible
- Image too cluttered

**Solutions:**
1. Increase contrast in image editor
2. Convert to black & white (threshold)
3. Remove furniture and annotations
4. Use higher resolution image
5. Ensure walls are solid black

#### Issue: "Image too small"

**Causes:**
- Resolution below 1000×1000 pixels

**Solutions:**
1. Re-scan at higher DPI
2. Use better camera
3. Don't upscale (creates artifacts)
4. Start with higher quality source

---

## Text Prompts

### Prompt Guidelines

CADLift uses an LLM (Large Language Model) to convert natural language into 3D geometry.

---

### Prompt Requirements

#### Essential Information

✅ **Must include:**
- Room dimensions (length × width in meters)
- Wall height (in meters or mm)
- Room type or name (bedroom, office, kitchen, etc.)

⚠️ **Recommended:**
- Wall thickness (in mm)
- Room layout (rectangular, L-shaped, etc.)
- Number of rooms if multiple

❌ **Don't need:**
- Furniture details
- Color or materials
- Exact architectural specifications

---

### Good vs Bad Prompts

#### ✅ GOOD Prompts

```
✅ "Create a 5m × 4m bedroom with 3m high walls and 200mm thick walls"

✅ "Design an L-shaped office: 8m × 5m main area with 3m × 3m alcove, 2.8m ceiling height, 150mm walls"

✅ "Generate a 10m × 8m open-plan kitchen with dining area, 3.5m tall walls, 200mm thickness"

✅ "Make a rectangular living room 6 meters by 5 meters, 3 meter ceiling, solid extrusion (no wall thickness)"

✅ "Create two connected rooms: 4m×4m bedroom and 3m×2m bathroom, both 2.8m high with 200mm walls"
```

**Why these work:**
- Specific dimensions
- Clear room type
- Wall height specified
- Layout described

#### ❌ BAD Prompts

```
❌ "Make me a room"
→ Too vague, no dimensions

❌ "A big house with many rooms"
→ Not specific, no measurements

❌ "Create a modern minimalist bedroom with wooden floors"
→ Too focused on aesthetics, missing dimensions

❌ "Design my apartment"
→ Too complex, no specific layout

❌ "A nice office space"
→ Vague, no dimensions or height
```

---

### Prompt Structure Templates

#### Single Room
```
"Create a [LENGTH]m × [WIDTH]m [ROOM_TYPE] with [HEIGHT]m high walls and [THICKNESS]mm thick walls"

Examples:
- "Create a 5m × 4m bedroom with 3m high walls and 200mm thick walls"
- "Create a 6m × 5m living room with 3.5m high walls and 150mm thick walls"
```

#### L-Shaped Room
```
"Design an L-shaped [ROOM_TYPE]: [LENGTH1]m × [WIDTH1]m main area with [LENGTH2]m × [WIDTH2]m [SECTION], [HEIGHT]m ceiling height"

Example:
- "Design an L-shaped office: 8m × 5m main area with 3m × 3m alcove, 2.8m ceiling height"
```

#### Multiple Rooms
```
"Create [NUMBER] connected rooms: [ROOM1_DESC] and [ROOM2_DESC], both [HEIGHT]m high with [THICKNESS]mm walls"

Example:
- "Create two connected rooms: 4m×4m bedroom and 3m×2m bathroom, both 2.8m high with 200mm walls"
```

---

### Advanced Prompts

#### With Positioning
```
"Create a 10m × 8m floor plan with:
- Kitchen: 5m × 4m in the northwest
- Living room: 5m × 4m in the southwest
- Bedroom: 4m × 4m in the northeast
- Bathroom: 2m × 4m in the southeast
All with 3m ceiling height and 200mm walls"
```

#### With Adjacency
```
"Design a 3-room apartment:
- Master bedroom (5m × 4m) adjacent to bathroom (3m × 2m)
- Open-plan living room (8m × 6m) separate from bedroom
- All rooms 2.8m high with 150mm walls"
```

---

### Prompt Parameters

**API Request:**
```json
{
  "mode": "prompt",
  "prompt": "Create a 5m × 4m bedroom with 3m high walls and 200mm thick walls",
  "params": {
    "extrude_height": 3000,
    "wall_thickness": 200
  }
}
```

**Note:** `extrude_height` and `wall_thickness` in params override values in prompt text.

---

### Prompt Best Practices

✅ **DO:**
- Be specific about dimensions (meters or millimeters)
- Use standard room names (bedroom, kitchen, office, etc.)
- Specify wall height and thickness
- Describe layout clearly (rectangular, L-shaped, etc.)
- Keep prompts simple and focused

❌ **DON'T:**
- Be vague about dimensions
- Focus on aesthetics (colors, materials)
- Expect complex multi-story buildings from single prompt
- Include furniture or fixture details
- Use non-standard terminology

---

## General Limits

### File Size Limits

| Input Type | Maximum Size |
|------------|--------------|
| DXF Files | 50 MB |
| Image Files | 20 MB |
| Prompt Text | 1000 characters |

### Processing Limits

| Metric | Limit |
|--------|-------|
| Max Polygons per Job | 100 |
| Max Vertices per Polygon | 1000 |
| Max Total Vertices | 10,000 |
| Processing Timeout | 60 seconds |

### Rate Limits

| Type | Limit |
|------|-------|
| Requests per Minute | 60 |
| Requests per Hour | 1000 |
| Concurrent Jobs per IP | 10 |

---

## Summary

### Quick Checklist

**DXF Files:**
- ✅ Closed LWPOLYLINE entities
- ✅ DXF 2013 or 2018 format
- ✅ Clean with PURGE before export
- ✅ < 50 MB file size

**Image Files:**
- ✅ PNG or JPG format
- ✅ Minimum 1000×1000 pixels
- ✅ High contrast (black walls, white background)
- ✅ Clean (no furniture, text, dimensions)
- ✅ < 20 MB file size

**Text Prompts:**
- ✅ Include dimensions (length × width)
- ✅ Specify wall height
- ✅ Use standard room names
- ✅ Keep simple and specific

---

## Next Steps

- 📖 [Quick Start Guide](QUICK_START_GUIDE.md) - Get started in 5 minutes
- 🔌 [API Documentation](API_DOCUMENTATION.md) - Complete API reference
- 🛠️ [Troubleshooting](TROUBLESHOOTING_GUIDE.md) - Fix common issues
- 📦 [Output Formats](OUTPUT_FORMAT_GUIDE.md) - Opening files in different software

---

*Last updated: 2025-11-24*
*CADLift Input Requirements Guide v1.0*
