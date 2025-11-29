# CADLift Troubleshooting Guide 🔧

Common issues and solutions for CADLift geometry generation.

---

## Table of Contents

1. [DXF File Issues](#dxf-file-issues)
2. [Image Processing Issues](#image-processing-issues)
3. [Prompt/LLM Issues](#promptllm-issues)
4. [Geometry Generation Issues](#geometry-generation-issues)
5. [Performance Issues](#performance-issues)
6. [API & Network Issues](#api--network-issues)

---

## DXF File Issues

### Error: `DXF_FILE_INVALID`

**Message:** "DXF file is corrupted or invalid"

**Causes:**
- File is corrupted during upload
- File is not actually a DXF file
- DXF version is too old or incompatible

**Solutions:**
1. ✅ **Re-export from your CAD software:**
   - AutoCAD: `SAVEAS` → Select DXF format → Choose `AutoCAD 2018 DXF` or newer
   - FreeCAD: File → Export → Select DXF format

2. ✅ **Verify file integrity:**
   ```bash
   # Check file starts with valid DXF header
   head -n 10 your_file.dxf
   # Should start with:
   # 0
   # SECTION
   # 2
   # HEADER
   ```

3. ✅ **Try different DXF version:**
   - Use DXF 2018 (R2018) or 2013 (R2013) format
   - Avoid very old formats (R12, R14)

---

### Error: `DXF_NO_ENTITIES`

**Message:** "DXF file contains no geometric entities"

**Causes:**
- DXF file is empty
- All geometry is on hidden layers
- Geometry was not exported

**Solutions:**
1. ✅ **Check layers are visible:**
   - In AutoCAD: `LAYER` command → Ensure layers are ON and THAWED
   - Export again with all layers visible

2. ✅ **Verify geometry exists:**
   - Open DXF in CAD software
   - Zoom to extents (`ZOOM` → `E`)
   - Check if geometry is visible

3. ✅ **Export selection:**
   - Select the geometry you want to export
   - Use `WBLOCK` (Write Block) instead of `SAVEAS`

---

### Error: `DXF_NO_CLOSED_SHAPES`

**Message:** "DXF file contains no closed polylines or shapes"

**Causes:**
- Room boundaries are not closed (open polylines)
- Using separate LINE entities instead of LWPOLYLINE
- Gaps in geometry

**Solutions:**
1. ✅ **Convert lines to polylines:**
   ```
   AutoCAD:
   1. Select all lines: window selection
   2. Command: PEDIT
   3. Type: M (Multiple)
   4. Type: J (Join)
   5. Set fuzz distance: 0.1
   6. Press Enter to join
   ```

2. ✅ **Check for gaps:**
   - Use `OVERKILL` to remove duplicate entities
   - Use `DRAWORDER` to check overlapping geometry
   - Zoom in to corners to verify connections

3. ✅ **Create proper polylines:**
   - Use `PLINE` command to trace over open geometry
   - Or use `BOUNDARY` command to detect closed areas:
     ```
     Command: BOUNDARY
     Click inside each room
     ```

4. ✅ **Verify closure:**
   ```
   Command: SELECT
   Select the polyline
   Command: LIST
   # Check if "Closed: Yes"
   ```

---

### Error: `DXF_PARSE_ERROR`

**Message:** "Failed to parse DXF file"

**Causes:**
- File encoding issues
- Corrupted DXF structure
- Non-standard DXF format

**Solutions:**
1. ✅ **Check file encoding:**
   - Save DXF as UTF-8 or ASCII
   - Avoid special characters in layer names

2. ✅ **Simplify DXF:**
   - Remove unused layers: `PURGE` → `All`
   - Remove blocks and references if not needed
   - Flatten geometry: `FLATTEN` command

3. ✅ **Use EXPLODE and rejoin:**
   ```
   1. EXPLODE all blocks and groups
   2. Join entities: PEDIT → M → J
   3. Export fresh DXF
   ```

---

## Image Processing Issues

### Error: `IMAGE_FILE_INVALID`

**Message:** "Image file is corrupted or unsupported format"

**Causes:**
- File is not PNG or JPG
- File is corrupted
- Unsupported color mode

**Solutions:**
1. ✅ **Convert to supported format:**
   - Use PNG or JPG only
   - Convert using image editor (Photoshop, GIMP, Paint.NET)

2. ✅ **Check file integrity:**
   ```bash
   # Verify file type
   file floor_plan.png
   # Should say: PNG image data
   ```

3. ✅ **Re-save image:**
   - Open in image editor
   - File → Save As → PNG (8-bit) or JPG (RGB)

---

### Error: `IMAGE_TOO_SMALL`

**Message:** "Image resolution too low for reliable processing"

**Causes:**
- Image is smaller than 1000×1000 pixels
- Low-quality scan or photo

**Solutions:**
1. ✅ **Use higher resolution:**
   - Minimum: 1000×1000 pixels
   - Recommended: 2000×2000 pixels or higher
   - For best results: 3000×3000+ pixels

2. ✅ **Re-scan with higher DPI:**
   - Scanner settings: 300 DPI minimum
   - Photo: Use better camera or better lighting

3. ✅ **Upscale (not recommended):**
   - Use AI upscaling tools
   - Note: Won't improve actual detail

---

### Error: `IMAGE_NO_CONTOURS_FOUND`

**Message:** "No room contours detected in image"

**Causes:**
- Image is too blurry
- Poor contrast (walls not visible)
- Complex or cluttered image

**Solutions:**
1. ✅ **Improve image quality:**
   - Increase contrast in image editor
   - Convert to black & white (walls = black, background = white)
   - Remove furniture, annotations, dimensions

2. ✅ **Clean up the image:**
   ```
   Before uploading:
   1. Remove all text and dimensions
   2. Erase furniture and fixtures
   3. Keep only wall outlines
   4. Ensure walls are solid black lines
   5. Background should be white
   ```

3. ✅ **Adjust settings:**
   - Try grayscale instead of color
   - Increase brightness/contrast
   - Ensure image is rotated correctly (walls horizontal/vertical)

---

## Prompt/LLM Issues

### Error: `LLM_API_ERROR`

**Message:** "Failed to call LLM API"

**Causes:**
- Missing or invalid API key
- Network issues
- API quota exceeded
- API service down

**Solutions:**
1. ✅ **Check API key configuration:**
   - Verify `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` environment variable
   - Ensure key has proper permissions

2. ✅ **Check quota:**
   - Log into OpenAI/Anthropic dashboard
   - Verify account has available credits
   - Check rate limits

3. ✅ **Test API connection:**
   ```bash
   # Test OpenAI
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

---

### Error: `LLM_NO_POLYGONS_EXTRACTED`

**Message:** "LLM did not generate valid room polygons"

**Causes:**
- Prompt is too vague
- LLM returned invalid JSON
- Dimensions not specified

**Solutions:**
1. ✅ **Be more specific in prompts:**
   ```
   Bad:  "Make me a room"
   Good: "Create a 5m × 4m bedroom with 3m high walls"

   Bad:  "A big house"
   Good: "Design an L-shaped office: 8m × 5m main area with 3m × 3m alcove, 2.8m ceiling height"
   ```

2. ✅ **Include dimensions:**
   - Always specify length and width in meters
   - Specify wall height
   - Optionally specify wall thickness

3. ✅ **Use standard room names:**
   - "bedroom", "kitchen", "office", "living room"
   - LLM understands typical room dimensions

---

### Error: `LLM_INVALID_RESPONSE`

**Message:** "LLM returned invalid JSON format"

**Causes:**
- LLM didn't follow schema
- Prompt confused the LLM
- Random LLM error

**Solutions:**
1. ✅ **Rephrase prompt:**
   - Use simpler language
   - Break complex layouts into simpler descriptions
   - Avoid ambiguous terms

2. ✅ **Try again:**
   - LLM responses can be non-deterministic
   - Simply retry the request

---

## Geometry Generation Issues

### Error: `GEO_NO_POLYGONS`

**Message:** "No valid polygons extracted from input"

**Causes:**
- DXF has no closed shapes
- Image processing failed to detect rooms
- Prompt didn't specify room layout

**Solutions:**
- See [DXF_NO_CLOSED_SHAPES](#error-dxf_no_closed_shapes) above
- See [IMAGE_NO_CONTOURS_FOUND](#error-image_no_contours_found) above
- Ensure prompt includes room dimensions

---

### Error: `GEO_INVALID_POLYGON`

**Message:** "Polygon is self-intersecting or invalid"

**Causes:**
- Polygon crosses itself
- Polygon has duplicate vertices
- Polygon is not properly oriented

**Solutions:**
1. ✅ **Fix self-intersections in CAD:**
   ```
   AutoCAD:
   1. Command: OVERKILL (removes duplicate geometry)
   2. Command: PEDIT → Join → close gaps
   3. Manually fix crossing lines
   ```

2. ✅ **Check polygon winding:**
   - Polygons should be counter-clockwise (CCW)
   - Use `REVERSE` if polygon is inside-out

3. ✅ **Simplify complex shapes:**
   - Break complex rooms into multiple simple rectangles
   - Use multiple separate polylines instead of one complex shape

---

### Error: `GEO_INVALID_HEIGHT`

**Message:** "Extrusion height must be greater than 0"

**Solutions:**
- Set `extrude_height` to a positive value (e.g., 3000 = 3 meters)
- Typical values: 2500-3500 mm (residential), 3000-4500 mm (commercial)

---

### Error: `GEO_INVALID_WALL_THICKNESS`

**Message:** "Wall thickness must be >= 0"

**Solutions:**
- Use `wall_thickness`: 0 for solid extrusion
- Use `wall_thickness`: 150-300 mm for hollow rooms (typical)
- Cannot be negative

---

### Error: `GEO_STEP_GENERATION_FAILED`

**Message:** "Failed to generate STEP solid geometry"

**Causes:**
- Polygon is too complex for solid modeling
- Boolean operations failed (hollow rooms)
- Internal geometry error

**Solutions:**
1. ✅ **Try solid extrusion first:**
   - Set `wall_thickness`: 0
   - If this works, issue is with hollow geometry

2. ✅ **Simplify polygon:**
   - Reduce number of vertices
   - Remove unnecessary details
   - Break into multiple simpler shapes

3. ✅ **Check for degenerate geometry:**
   - Remove zero-length edges
   - Remove duplicate vertices
   - Ensure minimum edge length > 1mm

---

## Performance Issues

### Issue: Job takes too long

**Expected times:**
- Simple room (rectangle): <100ms
- Complex room (L-shape): <100ms
- Multi-room layout: <500ms
- Image processing: 1-3 seconds
- Prompt processing: 3-10 seconds (includes LLM call)

**Solutions:**
1. ✅ **Check job status:**
   - Job might be queued behind other jobs
   - Use `GET /api/v1/jobs/{job_id}` to check status

2. ✅ **Simplify input:**
   - Reduce number of rooms/polygons
   - Simplify polygon geometry
   - Use lower image resolution (if acceptable)

3. ✅ **Optimize parameters:**
   - Increase `tolerance` (0.1 → 0.5) for faster processing
   - Reduces mesh quality but speeds up generation

---

### Issue: Output file is too large

**Typical file sizes:**
- DXF: 10-50 KB
- STEP: 20-50 KB
- OBJ: 1-5 KB
- STL: 1-10 KB
- GLB: 1-5 KB

**Solutions:**
1. ✅ **Use mesh formats instead of STEP:**
   - OBJ/STL/GLB are 10-30x smaller than STEP
   - Still usable for visualization

2. ✅ **Increase tolerance:**
   - Higher tolerance = fewer triangles = smaller files
   - `tolerance`: 0.1 (default) → 0.5 (lower quality, smaller)

3. ✅ **Simplify geometry:**
   - Remove unnecessary details
   - Use simpler room shapes

---

## API & Network Issues

### Error: Rate Limit Exceeded (429)

**Message:** "Rate limit exceeded. Try again in X seconds."

**Limits:**
- 60 requests per minute
- 1000 requests per hour
- Per IP address

**Solutions:**
1. ✅ **Implement backoff and retry:**
   ```python
   import time
   import requests

   def create_job_with_retry(dxf_path, max_retries=3):
       for attempt in range(max_retries):
           response = requests.post(url, files={"file": open(dxf_path, 'rb')})

           if response.status_code == 429:
               wait_time = 60 / 60  # 1 second per request
               print(f"Rate limited. Waiting {wait_time}s...")
               time.sleep(wait_time)
               continue

           return response.json()
   ```

2. ✅ **Batch requests:**
   - Group multiple files
   - Process during off-peak hours

3. ✅ **Request higher limits:**
   - Contact admin for API key with higher limits

---

### Error: Connection Timeout

**Solutions:**
1. ✅ **Check network:**
   - Verify server is reachable: `curl http://your-server/health`
   - Check firewall rules

2. ✅ **Increase timeout:**
   ```python
   requests.post(url, files=files, timeout=30)  # 30 second timeout
   ```

3. ✅ **Check server status:**
   - Server might be under heavy load
   - Check server logs for errors

---

## General Tips

### Best Practices for DXF Files

✅ **DO:**
- Use closed LWPOLYLINE entities
- Keep geometry simple
- Use consistent units (millimeters recommended)
- Clean up file with PURGE before exporting
- Use DXF 2018 or 2013 format

❌ **DON'T:**
- Use complex blocks or xrefs
- Include 3D geometry in 2D floor plan
- Use curved walls (unless necessary)
- Mix different unit systems

### Best Practices for Images

✅ **DO:**
- Use high resolution (2000×2000+ pixels)
- Ensure good contrast (black walls, white background)
- Remove all text, dimensions, furniture
- Straighten image (walls should be horizontal/vertical)
- Use clean scans or photos

❌ **DON'T:**
- Use low resolution images
- Include cluttered or busy images
- Use color images with poor contrast
- Include multiple floor plans in one image

### Best Practices for Prompts

✅ **DO:**
- Be specific about dimensions (meters)
- Specify wall height
- Use standard room names
- Describe layout clearly (L-shaped, rectangular, etc.)

❌ **DON'T:**
- Use vague descriptions
- Omit dimensions
- Use non-standard terminology
- Expect complex multi-room layouts from single prompt

---

## Still Having Issues?

1. **Check API Documentation:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
2. **Review Quick Start:** [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)
3. **Report Bug:** [GitHub Issues](https://github.com/yourusername/cadlift/issues)
4. **Contact Support:** Open an issue with:
   - Error message and code
   - Input file (if possible)
   - Steps to reproduce
   - Expected vs actual behavior

---

*Last updated: 2025-11-24*
*CADLift Troubleshooting Guide v1.0*
