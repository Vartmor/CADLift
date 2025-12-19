# 🚀 CADLift – Transform Anything Into 3D

<div align="center">

**From CAD files to images to text prompts — CADLift uses AI to generate production-ready 3D models in seconds.**

[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![React](https://img.shields.io/badge/react-18+-61dafb)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

[🎯 Live Demo](#) · [📖 Docs](backend/docs/) · [🐛 Report Bug](https://github.com/vartmor/cadlift/issues)

🌍 [Türkçe](README.tr.md) | English

</div>

---

## ✨ Three Ways to Create 3D

| 🏗️ CAD Files | 🖼️ Images | 💬 Text Prompts |
|:---:|:---:|:---:|
| Upload DWG or DXF | Upload any image | Describe what you want |
| Auto-detect layers | AI-powered reconstruction | Stable Diffusion + TripoSR |
| Extrude to 3D | TripoSR AI model | Generate from imagination |

---

## 🎯 What Makes CADLift Special

### 🏗️ DWG/DXF to 3D
- **DWG Support** – Native AutoCAD files via ODA File Converter
- **DXF Support** – All versions, all layers
- **Smart Detection** – Auto-detects closed shapes, walls, doors, windows
- **co2tools Integration** – Robust extrusion engine

### 🖼️ Image to 3D  
- **Any Image** – Photos, sketches, renders, screenshots
- **TripoSR AI** – State-of-the-art single-image 3D reconstruction
- **Background Removal** – Automatic subject isolation

### 💬 Prompt to 3D
- **Natural Language** – Just describe what you want
- **Stable Diffusion** – AI-generated reference images
- **End-to-End** – From text to viewable 3D model

### 📦 Multi-Format Export
| Format | Use Case |
|--------|----------|
| **GLB** | Web 3D, game engines (Unity, Unreal, Three.js) |
| **STL** | 3D printing (Cura, PrusaSlicer) |
| **DXF** | CAD software (AutoCAD, FreeCAD) |
| **STEP** | Engineering CAD (SolidWorks, Fusion 360) |

### 🎨 Built-in 3D Viewer
- **Instant Preview** – View models in browser before download
- **Interactive** – Rotate, zoom, pan
- **Online3DViewer** – Industry-standard GLB support

### ⚡ Real-Time Progress
- **Live Updates** – Watch conversion progress in real-time
- **Status Tracking** – Detailed stage-by-stage feedback

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 18, TypeScript, Tailwind CSS, Vite |
| **Backend** | FastAPI, Python 3.11+, SQLAlchemy, Celery |
| **AI Models** | Stable Diffusion, TripoSR, OpenAI (optional) |
| **CAD Tools** | ezdxf, co2tools, ODA Converter, trimesh, SolidPython |
| **Storage** | Local filesystem, PostgreSQL/SQLite |

---

## ⚠️ Local-Only Features

Some features require local installation due to GPU requirements:

| Feature | Requirement | Cloud Available |
|---------|-------------|--------|
| DWG/DXF to 3D | ODA Converter | ✅ |
| Prompt to 3D (Precision) | OpenAI API | ✅ |
| Prompt to 3D (Creative) | TripoSR + SD | ❌ Local only |
| Image to 3D | TripoSR | ❌ Local only |

> **Note:** For GPU-powered features, please [run CADLift locally](#-quick-start).

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- [ODA File Converter](https://www.opendesign.com/guestfiles/oda_file_converter) (for DWG support)

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
npm install
npm run dev
```

### Environment Variables

Create `backend/.env`:

```env
DATABASE_URL=sqlite+aiosqlite:///./cadlift.db
STORAGE_PATH=./storage
JWT_SECRET_KEY=your-secret-key
ENABLE_TASK_QUEUE=false
LOG_LEVEL=INFO
```

---

## 📋 API Examples

### Upload DWG/DXF
```bash
curl -X POST "http://localhost:8000/api/v1/jobs" \
  -F "upload=@building.dwg" \
  -F "job_type=cad" \
  -F "mode=cad" \
  -F 'params={"extrude_height": 3000}'
```

### Image to 3D
```bash
curl -X POST "http://localhost:8000/api/v1/jobs" \
  -F "upload=@photo.jpg" \
  -F "job_type=image" \
  -F "mode=3d"
```

### Prompt to 3D
```bash
curl -X POST "http://localhost:8000/api/v1/jobs" \
  -F "job_type=prompt" \
  -F "mode=3d" \
  -F 'params={"prompt": "a modern glass office building"}'
```

---

## 📁 Project Structure

```
cadlift/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI routes
│   │   ├── pipelines/     # CAD, Image, Prompt processing
│   │   ├── services/      # co2tools, ODA converter, storage
│   │   └── models/        # Database models
│   └── docs/              # API documentation
├── components/            # React components
├── pages/                 # Home, Dashboard, About
├── services/              # Frontend API client
└── docs/useful_projects/  # co2tools, libdxfrw
```

---

## 🎨 Screenshots

*Coming soon*

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

**Ideas for contribution:**
- Additional export formats (FBX, DAE)
- Multi-story building detection
- Texture and material support
- Mobile app

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- **[co2tools](https://github.com/Mambix/co2tools)** – DXF to STL extrusion
- **[TripoSR](https://github.com/VAST-AI-Research/TripoSR)** – AI 3D reconstruction
- **[Stable Diffusion](https://stability.ai/)** – AI image generation
- **[ODA](https://www.opendesign.com/)** – DWG file conversion
- **[ezdxf](https://github.com/mozman/ezdxf)** – DXF parsing
- **[trimesh](https://github.com/mikedh/trimesh)** – Mesh processing
- **[FastAPI](https://fastapi.tiangolo.com/)** – Python web framework

---

<div align="center">

**Built with ❤️ by [Vartmor](https://github.com/vartmor)**

⭐ Star us if you find CADLift useful!

</div>
