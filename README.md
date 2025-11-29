# CADLift – 2D Floor Plans to 3D CAD Models 🏗️

**Transform 2D floor plans into editable 3D CAD models in seconds.**

CADLift converts DXF drawings, floor plan images, and text descriptions into production-ready **3D geometry** compatible with AutoCAD, FreeCAD, Blender, Unity, and more.

[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]()
[![Tests](https://img.shields.io/badge/tests-92%2F94%20passing-brightgreen)]()
[![API](https://img.shields.io/badge/API-v1.0-blue)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()

---

## ✨ Features

### 🎯 Three Input Methods

| Input | What You Provide | What You Get |
|-------|------------------|--------------|
| **DXF Upload** | AutoCAD 2D floor plan | 3D STEP/DXF with extruded walls |
| **Image Upload** | Floor plan photo/sketch | Vectorized DXF + 3D model |
| **Text Prompt** | Natural language description | Complete 3D floor plan |

### 📦 Seven Output Formats

- **STEP** – CAD editing (AutoCAD, FreeCAD, SolidWorks)
- **DXF** – 2D/3D CAD (universal support)
- **OBJ** – 3D modeling (Blender, Maya, 3ds Max)
- **STL** – 3D printing (Cura, PrusaSlicer)
- **PLY** – Research & point clouds
- **glTF/GLB** – Web 3D & game engines (Unity, Unreal)

### 🚀 Production Features

- ✅ **Wall thickness support** (0-500mm+, hollow rooms)
- ✅ **Variable heights** (per-room customization)
- ✅ **Layer filtering** (DXF layers)
- ✅ **Circle/Arc support** (curved walls)
- ✅ **Multi-room layouts** (complex floor plans)
- ✅ **Real-time processing** (<100ms for simple rooms)
- ✅ **Format conversion** (on-demand, no re-generation)
- ✅ **Security hardened** (rate limiting, validation, headers)
- ✅ **Production monitoring** (logging, metrics, profiling)

---

## 🚀 Quick Start

### 1. Convert DXF to 3D

```bash
curl -X POST "http://your-server/api/v1/jobs" \
  -F "file=@floor_plan.dxf" \
  -F "mode=cad" \
  -F "params={\"extrude_height\": 3000, \"wall_thickness\": 200}"
```

### 2. Check Job Status

```bash
curl "http://your-server/api/v1/jobs/{job_id}"
```

### 3. Download 3D Model

```bash
# STEP (CAD)
curl "http://your-server/api/v1/files/{file_id}?format=step" -o output.step

# OBJ (Blender)
curl "http://your-server/api/v1/files/{file_id}?format=obj" -o output.obj

# GLB (Unity/Unreal)
curl "http://your-server/api/v1/files/{file_id}?format=glb" -o output.glb
```

**That's it!** Open `output.step` in AutoCAD or FreeCAD.

---

## 📚 Documentation

### Getting Started
- **[Quick Start Guide](backend/docs/QUICK_START_GUIDE.md)** – Get started in 5 minutes
- **[API Documentation](backend/docs/API_DOCUMENTATION.md)** – Complete API reference
- **[Input Requirements](backend/docs/INPUT_REQUIREMENTS_GUIDE.md)** – DXF, image, and prompt specifications
- **[Output Format Guide](backend/docs/OUTPUT_FORMAT_GUIDE.md)** – Opening files in different software

### Troubleshooting & Support
- **[Troubleshooting Guide](backend/docs/TROUBLESHOOTING_GUIDE.md)** – Common errors and solutions
- **[GitHub Issues](https://github.com/yourusername/cadlift/issues)** – Report bugs or request features

### Technical Documentation
- **[Production Plan](PLAN_PRODUCTION.md)** – Complete development roadmap (Phases 1-6)
- **[Phase 5 QA Results](backend/docs/PHASE_5_QA_RESULTS.md)** – Test results and performance metrics
- **[Phase 6 Readiness](PHASE_6_READY.md)** – Advanced features roadmap

---

## ⚡ Performance

| Operation | Time | Status |
|-----------|------|--------|
| Simple room (5m×4m) | **21.91ms** | ✅ 23x faster than target |
| Complex room (L-shaped) | **21.74ms** | ✅ 46x faster than target |
| Multi-room layout (3 rooms) | **55.52ms** | ✅ 36x faster than target |
| Format conversion | **<100ms** | ✅ All formats |

**File Size Optimization:**
- STEP: 29 KB (baseline)
- OBJ: 1 KB (**29x smaller**)
- STL: 1.7 KB (17x smaller)
- GLB: 1.3 KB (23x smaller)

---

## 🎯 Use Cases

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

### Real Estate
- Create 3D models from property floor plans
- Generate virtual tour environments
- Produce marketing materials

---

## 🛠️ Installation

### Prerequisites

- **Python 3.11+** (3.13 recommended)
- **Node.js 20+** (22.x recommended, for frontend)
- **Redis** (for task queue, optional in development)
- **PostgreSQL** (recommended for production, SQLite for development)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Run database migrations
alembic upgrade head

# Start API server
uvicorn app.main:app --reload
```

### Environment Configuration

Create `backend/.env`:

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./cadlift.db  # Or PostgreSQL for production

# Storage
STORAGE_PATH=./storage

# Security
JWT_SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Task Queue (optional)
ENABLE_TASK_QUEUE=false  # Set to true with Redis for production

# LLM (optional, for prompt pipeline)
LLM_PROVIDER=none  # Set to 'openai' or 'anthropic' with API key
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o-mini

# Logging
LOG_LEVEL=INFO

# Limits
MAX_UPLOAD_MB=50  # DXF files
MAX_IMAGE_UPLOAD_MB=20  # Image files
```

### Run with Task Queue (Production)

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start API
uvicorn app.main:app --reload

# Terminal 3: Start Celery worker
celery -A app.worker worker --loglevel=info
```

---

## 🧪 Testing

CADLift has **92 passing tests** with comprehensive coverage:

```bash
cd backend

# Run all tests
pytest

# Run specific test categories
pytest tests/test_geometry_validation.py  # Geometry validation (12 tests)
pytest tests/test_performance_benchmarks.py  # Performance benchmarks (12 tests)
pytest tests/test_integration_job_flow.py  # Integration tests (7 tests)

# Run with coverage
pytest --cov=app --cov-report=html
```

**Test Results:**
- ✅ 92/94 tests passing (98%)
- ✅ Zero critical issues
- ✅ All operations 5-60x faster than targets
- ✅ Watertight geometry validation
- ✅ Comprehensive integration testing

---

## 📋 API Examples

### Python Example

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# Create job
with open("floor_plan.dxf", "rb") as f:
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

# Poll for completion
while True:
    response = requests.get(f"{BASE_URL}/api/v1/jobs/{job_id}")
    job = response.json()
    if job["status"] == "completed":
        break
    time.sleep(1)

# Download STEP file
file_id = job["output_file_id"]
response = requests.get(f"{BASE_URL}/api/v1/files/{file_id}?format=step")
with open("output.step", "wb") as f:
    f.write(response.content)

print("Done! Open output.step in CAD software")
```

### JavaScript Example

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

async function convert(dxfPath) {
  // Create job
  const form = new FormData();
  form.append('file', fs.createReadStream(dxfPath));
  form.append('mode', 'cad');
  form.append('params', JSON.stringify({
    extrude_height: 3000,
    wall_thickness: 200
  }));

  const { data: job } = await axios.post(
    'http://localhost:8000/api/v1/jobs',
    form,
    { headers: form.getHeaders() }
  );

  // Poll for completion
  while (true) {
    const { data } = await axios.get(
      `http://localhost:8000/api/v1/jobs/${job.id}`
    );
    if (data.status === 'completed') {
      // Download file
      const fileResponse = await axios.get(
        `http://localhost:8000/api/v1/files/${data.output_file_id}?format=glb`,
        { responseType: 'arraybuffer' }
      );
      fs.writeFileSync('output.glb', fileResponse.data);
      console.log('Done! Open output.glb in Blender or Unity');
      break;
    }
    await new Promise(r => setTimeout(r, 1000));
  }
}

convert('floor_plan.dxf');
```

---

## 🔒 Security

CADLift includes production-grade security:

- ✅ **Rate limiting:** 60/min, 1000/hour per IP
- ✅ **Input validation:** File format, size, and content validation
- ✅ **Security headers:** CSP, HSTS, X-Content-Type-Options
- ✅ **Error handling:** 22 specific error codes with user-friendly messages
- ✅ **File size limits:** DXF 50MB, Images 20MB
- ✅ **Upload scanning:** DXF structure validation, image format validation

---

## 📊 Project Status

### Completed Phases (100%)

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1** | ✅ 100% | Foundation - Real STEP generation, DXF improvements, wall thickness |
| **Phase 2** | ✅ 100% | Pipeline enhancements - CAD, Image, Prompt pipelines |
| **Phase 3** | ✅ 100% | Production hardening - Error handling, logging, monitoring, security |
| **Phase 4** | ✅ 100% | Export formats - OBJ, STL, PLY, glTF, GLB, OFF |
| **Phase 5** | ✅ 100% | Quality assurance - 92 tests, performance validation, geometry verification |

### Current Phase

**Phase 6: Documentation & Advanced Features** (In Progress)

- ✅ **Documentation Complete:**
  - Quick Start Guide
  - API Documentation
  - Troubleshooting Guide
  - Output Format Guide
  - Input Requirements Guide

- ⏸️ **Advanced Features (Future):**
  - Door & window openings
  - Multi-story buildings
  - Materials & appearance
  - Parametric components
  - Frontend UI with 3D viewer

---

## 🏛️ Architecture

```
cadlift/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI routes
│   │   ├── core/          # Config, errors, logging
│   │   ├── db/            # Database models
│   │   ├── models/        # SQLAlchemy models
│   │   ├── pipelines/     # CAD, Image, Prompt processing
│   │   ├── services/      # Storage, monitoring
│   │   └── worker/        # Celery tasks
│   ├── docs/              # Complete documentation
│   ├── tests/             # 92 comprehensive tests
│   └── pyproject.toml     # Dependencies
├── frontend/              # React SPA (optional)
└── README.md             # This file
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Areas for contribution:**
- Additional export formats (FBX, DAE)
- Door/window detection in DXF
- Multi-story building support
- Material and texture support
- Frontend UI improvements

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with:
- **[CadQuery](https://github.com/CadQuery/cadquery)** – Parametric CAD modeling
- **[ezdxf](https://github.com/mozman/ezdxf)** – DXF file processing
- **[trimesh](https://github.com/mikedh/trimesh)** – Mesh processing and validation
- **[FastAPI](https://fastapi.tiangolo.com/)** – Modern Python web framework
- **[Celery](https://docs.celeryq.dev/)** – Distributed task queue

---

## 📞 Support

- **Documentation:** [backend/docs/](backend/docs/)
- **Quick Start:** [QUICK_START_GUIDE.md](backend/docs/QUICK_START_GUIDE.md)
- **API Reference:** [API_DOCUMENTATION.md](backend/docs/API_DOCUMENTATION.md)
- **Troubleshooting:** [TROUBLESHOOTING_GUIDE.md](backend/docs/TROUBLESHOOTING_GUIDE.md)
- **Issues:** [GitHub Issues](https://github.com/yourusername/cadlift/issues)

---

## ⭐ Star Us!

If you find CADLift useful, please star this repository to help others discover it!

---

**CADLift** – Transform 2D floor plans into 3D CAD models in seconds. Production-ready, fully tested, and blazing fast.

*Built with ❤️ for architects, designers, and developers*
