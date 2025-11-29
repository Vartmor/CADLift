# CADLift API Documentation 📡

Complete API reference for CADLift - convert 2D floor plans to 3D CAD models.

**Base URL:** `http://your-server/api/v1`

**Version:** 1.0
**Status:** Production Ready

---

## Table of Contents

1. [Authentication](#authentication)
2. [Rate Limiting](#rate-limiting)
3. [Endpoints](#endpoints)
   - [Health Check](#health-check)
   - [Create Job](#create-job)
   - [Get Job Status](#get-job-status)
   - [Download File](#download-file)
4. [Error Codes](#error-codes)
5. [Examples](#examples)

---

## Authentication

Currently, CADLift uses IP-based rate limiting. **No API key required** for basic usage.

Future versions may add API key authentication for higher limits.

---

## Rate Limiting

| Limit Type | Value |
|-----------|-------|
| **Requests per minute** | 60 |
| **Requests per hour** | 1000 |
| **Per** | IP address |

**Rate limit headers:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1700000000
```

**Response when rate limited:**
```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
  "detail": "Rate limit exceeded. Try again in 30 seconds."
}
```

---

## Endpoints

### Health Check

Check if the API is running and healthy.

**Endpoint:** `GET /health`

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "ok",
  "timestamp": "2025-11-24T10:30:00Z"
}
```

**Example:**
```bash
curl "http://your-server/health"
```

---

### Create Job

Create a new geometry generation job.

**Endpoint:** `POST /api/v1/jobs`

#### Mode 1: CAD Pipeline (DXF Upload)

**Content-Type:** `multipart/form-data`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | ✅ Yes | DXF file (max 50MB) |
| `mode` | String | ✅ Yes | Must be `"cad"` |
| `params` | JSON String | No | Processing parameters (see below) |

**Params Object:**
```json
{
  "extrude_height": 3000,        // Wall height in mm (default: 3000)
  "wall_thickness": 200,         // Wall thickness in mm (default: 200, 0=solid)
  "tolerance": 0.1,              // Mesh tolerance (default: 0.1, range: 0.01-1.0)
  "layer_filter": ["WALLS"]      // Optional: Only process specific layers
}
```

**Request Example:**
```bash
curl -X POST "http://your-server/api/v1/jobs" \
  -F "file=@floor_plan.dxf" \
  -F "mode=cad" \
  -F "params={\"extrude_height\": 3000, \"wall_thickness\": 200}"
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "mode": "cad",
  "status": "queued",
  "input_file_id": "abc123def456",
  "created_at": "2025-11-24T10:30:00Z",
  "params": {
    "extrude_height": 3000,
    "wall_thickness": 200
  }
}
```

#### Mode 2: Prompt Pipeline (Text Description)

**Content-Type:** `application/json`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mode` | String | ✅ Yes | Must be `"prompt"` |
| `prompt` | String | ✅ Yes | Natural language description |
| `params` | Object | No | Processing parameters |

**Request Example:**
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

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "mode": "prompt",
  "status": "queued",
  "prompt": "Create a 5m × 4m bedroom with 3m high walls and 200mm thick walls",
  "created_at": "2025-11-24T10:30:00Z",
  "params": {
    "extrude_height": 3000,
    "wall_thickness": 200
  }
}
```

#### Mode 3: Image Pipeline (Floor Plan Photo)

**Content-Type:** `multipart/form-data`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | ✅ Yes | Image file: PNG or JPG (max 20MB) |
| `mode` | ✅ String | Yes | Must be `"image"` |
| `params` | JSON String | No | Processing parameters |

**Params Object:**
```json
{
  "extrude_height": 3000,     // Height in mm (default: 3000)
  "wall_thickness": 200,      // Thickness in mm (default: 200)
  "only_2d": false,           // If true, output 2D DXF only (default: false)
  "simplify_epsilon": 2.0     // Douglas-Peucker epsilon (default: 2.0)
}
```

**Request Example:**
```bash
curl -X POST "http://your-server/api/v1/jobs" \
  -F "file=@floor_plan.jpg" \
  -F "mode=image" \
  -F "params={\"extrude_height\": 3000, \"wall_thickness\": 200, \"only_2d\": true}"
```

---

### Get Job Status

Check the status of a job and retrieve output file IDs.

**Endpoint:** `GET /api/v1/jobs/{job_id}`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `job_id` | UUID | Job ID from create job response |

**Response (Queued):**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "mode": "cad",
  "status": "queued",
  "created_at": "2025-11-24T10:30:00Z"
}
```

**Response (Processing):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "mode": "cad",
  "status": "processing",
  "created_at": "2025-11-24T10:30:00Z",
  "started_at": "2025-11-24T10:30:05Z"
}
```

**Response (Completed):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "mode": "cad",
  "status": "completed",
  "output_file_id": "xyz789abc123",
  "created_at": "2025-11-24T10:30:00Z",
  "started_at": "2025-11-24T10:30:05Z",
  "completed_at": "2025-11-24T10:30:08Z",
  "processing_time_ms": 3215
}
```

**Response (Failed):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "mode": "cad",
  "status": "failed",
  "error": "DXF_NO_CLOSED_SHAPES",
  "error_message": "DXF file contains no closed polylines or shapes. Please ensure your DXF contains closed LWPOLYLINE, POLYLINE, or connected LINE entities.",
  "created_at": "2025-11-24T10:30:00Z",
  "started_at": "2025-11-24T10:30:05Z",
  "completed_at": "2025-11-24T10:30:06Z"
}
```

**Job Status Values:**

| Status | Description |
|--------|-------------|
| `queued` | Job is waiting to be processed |
| `processing` | Job is currently being processed |
| `completed` | Job finished successfully |
| `failed` | Job failed with error |

**Example:**
```bash
curl "http://your-server/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000"
```

---

### Download File

Download output files in various formats.

**Endpoint:** `GET /api/v1/files/{file_id}`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_id` | String | File ID from job status response |

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `format` | String | No | Output format (see table below) |

**Supported Formats:**

| Format | MIME Type | Extension | Use Case |
|--------|-----------|-----------|----------|
| Default | `application/dxf` | `.dxf` | CAD software (default) |
| `step` | `application/step` | `.step` | CAD editing (STEP ISO 10303-21) |
| `obj` | `model/obj` | `.obj` | 3D modeling, Blender |
| `stl` | `model/stl` | `.stl` | 3D printing |
| `ply` | `application/ply` | `.ply` | Point clouds, research |
| `gltf` | `model/gltf+json` | `.gltf` | Web 3D, AR/VR (JSON) |
| `glb` | `model/gltf-binary` | `.glb` | Game engines (Unity, Unreal) |
| `off` | `application/off` | `.off` | Simple mesh format |

**Request Examples:**
```bash
# Download DXF (default)
curl "http://your-server/api/v1/files/xyz789abc123" -o output.dxf

# Download STEP
curl "http://your-server/api/v1/files/xyz789abc123?format=step" -o output.step

# Download OBJ
curl "http://your-server/api/v1/files/xyz789abc123?format=obj" -o output.obj

# Download STL
curl "http://your-server/api/v1/files/xyz789abc123?format=stl" -o output.stl

# Download GLB
curl "http://your-server/api/v1/files/xyz789abc123?format=glb" -o output.glb
```

**Response (Success):**
```http
HTTP/1.1 200 OK
Content-Type: application/step
Content-Disposition: attachment; filename="output.step"
Content-Length: 29418

[Binary STEP file content]
```

**Response (File Not Found):**
```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "detail": "File not found"
}
```

**Response (Invalid Format):**
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "GEO_STEP_GENERATION_FAILED",
  "message": "Unsupported export format: fbx. Supported formats: step, obj, stl, ply, gltf, glb, off",
  "suggestion": "Use one of the supported formats: step, obj, stl, ply, gltf, glb, off"
}
```

---

## Error Codes

CADLift uses specific error codes for better debugging. All errors follow this format:

```json
{
  "error": "ERROR_CODE",
  "message": "User-friendly error message",
  "suggestion": "How to fix this error (optional)"
}
```

### Input Validation Errors

| Code | HTTP Status | Description | Solution |
|------|-------------|-------------|----------|
| `DXF_FILE_INVALID` | 400 | DXF file is corrupted or invalid | Check file format, re-export from CAD |
| `DXF_NO_ENTITIES` | 400 | DXF file contains no geometric entities | Ensure DXF has polylines, lines, or shapes |
| `DXF_NO_CLOSED_SHAPES` | 400 | No closed polylines found | Connect LINE entities or use LWPOLYLINE |
| `IMAGE_FILE_INVALID` | 400 | Image file is corrupted or unsupported | Use PNG or JPG format |
| `IMAGE_TOO_SMALL` | 400 | Image resolution too low | Use at least 1000×1000 pixels |
| `FILE_TOO_LARGE` | 413 | File exceeds size limit | DXF: <50MB, Images: <20MB |

### Geometry Errors

| Code | HTTP Status | Description | Solution |
|------|-------------|-------------|----------|
| `GEO_NO_POLYGONS` | 400 | No valid polygons extracted | Check DXF/image has closed shapes |
| `GEO_INVALID_POLYGON` | 400 | Polygon is self-intersecting or invalid | Fix self-intersections in CAD |
| `GEO_INVALID_HEIGHT` | 400 | Height must be > 0 | Set extrude_height > 0 |
| `GEO_INVALID_WALL_THICKNESS` | 400 | Wall thickness must be ≥ 0 | Use 0 or positive value |
| `GEO_STEP_GENERATION_FAILED` | 500 | Failed to generate STEP file | Check geometry validity |

### LLM/Prompt Errors

| Code | HTTP Status | Description | Solution |
|------|-------------|-------------|----------|
| `LLM_API_ERROR` | 500 | LLM API call failed | Check API key, network, quota |
| `LLM_INVALID_RESPONSE` | 500 | LLM returned invalid JSON | Try rephrasing prompt |
| `LLM_NO_POLYGONS_EXTRACTED` | 400 | LLM didn't generate valid polygons | Be more specific in prompt |

### System Errors

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `PROCESSING_ERROR` | 500 | Generic processing error |
| `FILE_NOT_FOUND` | 404 | Output file not found |
| `JOB_NOT_FOUND` | 404 | Job ID not found |

---

## Examples

### Complete Workflow (Python)

```python
import requests
import time
import json

BASE_URL = "http://your-server"

def process_dxf_to_3d(dxf_path, output_path):
    """Convert DXF to 3D STEP file."""

    # Step 1: Create job
    with open(dxf_path, 'rb') as f:
        response = requests.post(
            f"{BASE_URL}/api/v1/jobs",
            files={"file": f},
            data={
                "mode": "cad",
                "params": json.dumps({
                    "extrude_height": 3000,
                    "wall_thickness": 200
                })
            }
        )

    if response.status_code != 200:
        print(f"Error creating job: {response.json()}")
        return

    job = response.json()
    job_id = job["id"]
    print(f"Job created: {job_id}")

    # Step 2: Poll for completion
    while True:
        response = requests.get(f"{BASE_URL}/api/v1/jobs/{job_id}")
        job = response.json()

        if job["status"] == "completed":
            print(f"Job completed in {job['processing_time_ms']}ms")
            break
        elif job["status"] == "failed":
            print(f"Job failed: {job['error']}")
            print(f"Message: {job['error_message']}")
            return

        print(f"Status: {job['status']}")
        time.sleep(1)

    # Step 3: Download STEP file
    file_id = job["output_file_id"]
    response = requests.get(f"{BASE_URL}/api/v1/files/{file_id}?format=step")

    with open(output_path, 'wb') as f:
        f.write(response.content)

    print(f"STEP file saved: {output_path}")

# Usage
process_dxf_to_3d("floor_plan.dxf", "output.step")
```

### Batch Processing (Python)

```python
import requests
import concurrent.futures

BASE_URL = "http://your-server"

def process_file(dxf_path):
    """Process a single DXF file."""
    with open(dxf_path, 'rb') as f:
        response = requests.post(
            f"{BASE_URL}/api/v1/jobs",
            files={"file": f},
            data={"mode": "cad", "params": '{"extrude_height": 3000}'}
        )
    return response.json()["id"]

# Process multiple files concurrently
dxf_files = ["room1.dxf", "room2.dxf", "room3.dxf"]

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    job_ids = list(executor.map(process_file, dxf_files))

print(f"Created {len(job_ids)} jobs: {job_ids}")
```

### Error Handling (Python)

```python
import requests

def safe_create_job(dxf_path):
    """Create job with error handling."""
    try:
        with open(dxf_path, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/api/v1/jobs",
                files={"file": f},
                data={"mode": "cad"}
            )

        if response.status_code == 400:
            error = response.json()
            print(f"Validation error: {error['error']}")
            print(f"Message: {error['message']}")
            if 'suggestion' in error:
                print(f"Suggestion: {error['suggestion']}")
            return None

        elif response.status_code == 429:
            print("Rate limit exceeded. Wait and retry.")
            return None

        elif response.status_code != 200:
            print(f"HTTP {response.status_code}: {response.text}")
            return None

        return response.json()["id"]

    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
```

---

## Security Headers

All responses include security headers:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

---

## Performance

| Operation | Typical Duration |
|-----------|------------------|
| Simple room (5m×4m) STEP generation | 20-50ms |
| Complex room (L-shaped) STEP generation | 20-50ms |
| Multi-room layout (3 rooms) | 50-100ms |
| Format conversion (STEP → OBJ/STL/GLB) | <100ms |
| Image processing (floor plan) | 500-2000ms |
| Prompt processing (LLM + generation) | 2000-5000ms |

---

## Support

- **Documentation:** [Full docs](../docs/)
- **Quick Start:** [Quick Start Guide](QUICK_START_GUIDE.md)
- **Troubleshooting:** [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)
- **GitHub:** [Report issues](https://github.com/yourusername/cadlift/issues)

---

*Last updated: 2025-11-24*
*CADLift API v1.0*
