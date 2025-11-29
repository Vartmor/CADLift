# CADLift Quick Start Guide 🚀

**Welcome to CADLift!** This guide will help you get started in less than 5 minutes.

CADLift converts 2D floor plans and text descriptions into **editable 3D CAD models** that work with AutoCAD, FreeCAD, Blender, and game engines.

---

## Table of Contents

1. [Overview](#overview)
2. [Workflow 1: DXF → 3D STEP](#workflow-1-dxf--3d-step)
3. [Workflow 2: Text Prompt → 3D Model](#workflow-2-text-prompt--3d-model)
4. [Workflow 3: Image → DXF](#workflow-3-image--dxf)
5. [Format Conversion](#format-conversion)
6. [Next Steps](#next-steps)

---

## Overview

CADLift supports **3 input methods**:

| Input Type | What You Provide | What You Get |
|------------|------------------|--------------|
| **DXF File** | AutoCAD 2D floor plan | 3D STEP/DXF with walls |
| **Text Prompt** | "Create a 5m×4m bedroom" | Complete 3D model |
| **Image** | Floor plan photo/sketch | Vectorized DXF |

**Output formats:** STEP, DXF, OBJ, STL, PLY, glTF, GLB

---

## Workflow 1: DXF → 3D STEP

Convert a 2D AutoCAD floor plan into a 3D model with walls.

### Step 1: Prepare Your DXF

Your DXF file should contain:
- Closed polylines representing room boundaries
- CIRCLE or ARC entities (optional, for curves)
- Layers to organize geometry (optional)

**Supported entities:** LWPOLYLINE, POLYLINE, LINE, CIRCLE, ARC

### Step 2: Upload via API

```bash
curl -X POST "http://your-server/api/v1/jobs" \
  -F "file=@floor_plan.dxf" \
  -F "mode=cad" \
  -F "params={\"extrude_height\": 3000, \"wall_thickness\": 200}"
```

**Parameters:**
- `extrude_height`: Wall height in millimeters (e.g., 3000 = 3 meters)
- `wall_thickness`: Wall thickness in millimeters (e.g., 200 = 200mm, 0 = solid extrusion)

### Step 3: Check Job Status

```bash
curl "http://your-server/api/v1/jobs/{job_id}"
```

Response:
```json
{
  "id": "abc123",
  "status": "completed",
  "mode": "cad",
  "output_file_id": "xyz789",
  "created_at": "2025-11-24T10:30:00Z"
}
```

### Step 4: Download Your 3D Model

**Download as STEP (default):**
```bash
curl "http://your-server/api/v1/files/{file_id}" -o output.step
```

**Convert to other formats:**
```bash
# OBJ (text-based mesh)
curl "http://your-server/api/v1/files/{file_id}?format=obj" -o output.obj

# STL (3D printing)
curl "http://your-server/api/v1/files/{file_id}?format=stl" -o output.stl

# GLB (Blender, Unity, Unreal)
curl "http://your-server/api/v1/files/{file_id}?format=glb" -o output.glb
```

### Step 5: Open in CAD Software

- **AutoCAD:** File → Import → STEP file
- **FreeCAD:** File → Open → Select STEP file
- **Blender:** File → Import → Wavefront (.obj) or glTF (.glb)

**Done!** You now have an editable 3D model with proper wall thickness.

---

## Workflow 2: Text Prompt → 3D Model

Generate a 3D model from a natural language description.

### Step 1: Write Your Prompt

Be specific about dimensions, room layout, and features:

**Good prompts:**
- ✅ "Create a 5m × 4m bedroom with 3m high walls and 200mm thick walls"
- ✅ "Design an L-shaped office: 8m × 5m main area with 3m × 3m alcove, 2.8m ceiling height"
- ✅ "Generate a 10m × 8m open-plan kitchen with dining area, 3.5m tall walls, 150mm thickness"

**Avoid vague prompts:**
- ❌ "Make me a room" (missing dimensions)
- ❌ "A big house" (too vague)

### Step 2: Submit via API

```bash
curl -X POST "http://your-server/api/v1/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "prompt",
    "prompt": "Create a 5m × 4m bedroom with 3m high walls and 200mm thick walls",
    "params": {
      "extrude_height": 3000,
      "wall_thickness": 200
    }
  }'
```

### Step 3: Check Status & Download

Same as Workflow 1 (Steps 3-5).

**Note:** Prompt mode requires an LLM API key (OpenAI, Anthropic, etc.) configured on the server.

---

## Workflow 3: Image → DXF

Convert a floor plan image (photo or sketch) into a vectorized DXF.

### Step 1: Prepare Your Image

**Requirements:**
- Format: PNG or JPG
- Resolution: At least 1000×1000 pixels (higher is better)
- Quality: Clear lines, good contrast
- Max size: 20MB

**Tips for best results:**
- Use a clean scan or high-quality photo
- Ensure good lighting (no shadows)
- Straighten the image (walls should be vertical/horizontal)

### Step 2: Upload via API

```bash
curl -X POST "http://your-server/api/v1/jobs" \
  -F "file=@floor_plan.jpg" \
  -F "mode=image" \
  -F "params={\"extrude_height\": 3000, \"wall_thickness\": 200, \"only_2d\": true}"
```

**Parameters:**
- `only_2d`: Set to `true` to output 2D DXF only (no 3D extrusion)
- `extrude_height`: Height for 3D extrusion (if `only_2d` is false)
- `wall_thickness`: Wall thickness for 3D model

### Step 3: Download DXF

```bash
curl "http://your-server/api/v1/files/{file_id}" -o output.dxf
```

Open in AutoCAD or any CAD software to clean up and refine the vectorized floor plan.

---

## Format Conversion

CADLift supports **7 output formats**. Convert on-demand using the `format` query parameter:

| Format | Use Case | MIME Type | Query Parameter |
|--------|----------|-----------|-----------------|
| **STEP** | CAD editing (default) | `application/step` | `?format=step` |
| **DXF** | 2D/3D CAD | `application/dxf` | (default) |
| **OBJ** | 3D modeling, Blender | `model/obj` | `?format=obj` |
| **STL** | 3D printing | `model/stl` | `?format=stl` |
| **PLY** | Point clouds, research | `application/ply` | `?format=ply` |
| **glTF** | Web 3D, AR/VR | `model/gltf+json` | `?format=gltf` |
| **GLB** | Game engines (Unity, Unreal) | `model/gltf-binary` | `?format=glb` |

### Example: Convert to Multiple Formats

```bash
# Download as STEP (CAD)
curl "http://your-server/api/v1/files/{file_id}?format=step" -o model.step

# Download as STL (3D printing)
curl "http://your-server/api/v1/files/{file_id}?format=stl" -o model.stl

# Download as GLB (Unity/Unreal)
curl "http://your-server/api/v1/files/{file_id}?format=glb" -o model.glb
```

**Performance:** All conversions complete in <100ms. No re-generation required!

---

## Python Example

Here's a complete example using Python:

```python
import requests
import time

# Configuration
BASE_URL = "http://your-server"
DXF_FILE = "floor_plan.dxf"

# Step 1: Create job
with open(DXF_FILE, 'rb') as f:
    response = requests.post(
        f"{BASE_URL}/api/v1/jobs",
        files={"file": f},
        data={
            "mode": "cad",
            "params": '{"extrude_height": 3000, "wall_thickness": 200}'
        }
    )

job = response.json()
job_id = job["id"]
print(f"Job created: {job_id}")

# Step 2: Wait for completion
while True:
    response = requests.get(f"{BASE_URL}/api/v1/jobs/{job_id}")
    job = response.json()

    if job["status"] == "completed":
        print("Job completed!")
        break
    elif job["status"] == "failed":
        print(f"Job failed: {job.get('error')}")
        exit(1)

    print(f"Status: {job['status']}")
    time.sleep(1)

# Step 3: Download files
file_id = job["output_file_id"]

# Download STEP file
response = requests.get(f"{BASE_URL}/api/v1/files/{file_id}")
with open("output.step", "wb") as f:
    f.write(response.content)
print("STEP file saved: output.step")

# Download OBJ file
response = requests.get(f"{BASE_URL}/api/v1/files/{file_id}?format=obj")
with open("output.obj", "wb") as f:
    f.write(response.content)
print("OBJ file saved: output.obj")
```

---

## JavaScript Example

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const BASE_URL = 'http://your-server';

async function convertDXFto3D(dxfPath) {
  // Step 1: Upload DXF
  const form = new FormData();
  form.append('file', fs.createReadStream(dxfPath));
  form.append('mode', 'cad');
  form.append('params', JSON.stringify({
    extrude_height: 3000,
    wall_thickness: 200
  }));

  const createResponse = await axios.post(`${BASE_URL}/api/v1/jobs`, form, {
    headers: form.getHeaders()
  });

  const jobId = createResponse.data.id;
  console.log(`Job created: ${jobId}`);

  // Step 2: Poll for completion
  let job;
  while (true) {
    const statusResponse = await axios.get(`${BASE_URL}/api/v1/jobs/${jobId}`);
    job = statusResponse.data;

    if (job.status === 'completed') {
      console.log('Job completed!');
      break;
    } else if (job.status === 'failed') {
      throw new Error(`Job failed: ${job.error}`);
    }

    console.log(`Status: ${job.status}`);
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  // Step 3: Download STEP file
  const fileId = job.output_file_id;
  const fileResponse = await axios.get(`${BASE_URL}/api/v1/files/${fileId}`, {
    responseType: 'arraybuffer'
  });

  fs.writeFileSync('output.step', fileResponse.data);
  console.log('STEP file saved: output.step');
}

// Run
convertDXFto3D('floor_plan.dxf').catch(console.error);
```

---

## Next Steps

### Learn More
- 📖 [API Documentation](API_DOCUMENTATION.md) - Complete API reference
- 🛠️ [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md) - Common issues and solutions
- 📦 [Output Format Guide](OUTPUT_FORMAT_GUIDE.md) - Opening files in different software
- 📋 [Input Requirements](INPUT_REQUIREMENTS_GUIDE.md) - File format specifications

### Advanced Features
- **Wall Thickness:** Adjust from 0mm (solid) to 500mm+ (thick walls)
- **Custom Heights:** Set different heights for different areas
- **Layer Filtering:** Process only specific layers from DXF
- **Tolerance Control:** Adjust mesh quality (0.05 = high detail, 0.5 = low detail)

### Get Help
- **GitHub Issues:** [Report bugs or request features](https://github.com/yourusername/cadlift/issues)
- **Documentation:** [Full documentation](../docs/)
- **API Status:** Check `/health` endpoint for system status

---

## Performance & Limits

| Metric | Value |
|--------|-------|
| **Processing Speed** | <100ms for simple rooms, <1s for complex layouts |
| **File Size Limits** | DXF: 50MB, Images: 20MB |
| **Rate Limiting** | 60 requests/minute, 1000 requests/hour per IP |
| **Supported CAD Versions** | AutoCAD 2000-2024, FreeCAD 0.20+, BricsCAD V21+ |

---

## Common Use Cases

### Architecture & Design
- Convert 2D floor plans to 3D for client presentations
- Generate quick massing models from sketches
- Create base geometry for detailed modeling

### Game Development
- Generate building interiors for game levels
- Convert architectural plans to Unity/Unreal assets
- Create collision meshes from floor plans

### 3D Printing
- Convert floor plans to printable models
- Create architectural scale models
- Generate custom building parts

### Real Estate & Visualization
- Create 3D models from property floor plans
- Generate virtual tour environments
- Produce marketing materials

---

**Happy modeling!** 🎉

For questions or issues, please refer to our [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md) or open an issue on GitHub.

---

*Last updated: 2025-11-24*
*CADLift v1.0 - Production Ready*
