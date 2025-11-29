# Technical Architecture - Any Object Ultra-Realistic System

**Date**: 2025-11-27
**Version**: 1.0

---

## System Overview

The ultra-realistic "any object" system uses a **hybrid architecture** combining:
1. **Parametric CAD** (existing CadQuery system) - precision engineering
2. **AI Generation** (Shap-E, TripoSR) - organic/artistic shapes
3. **Intelligent Routing** - automatic pipeline selection
4. **Quality Enhancement** - mesh refinement and optimization

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CADLift Backend API                         │
│                    (FastAPI + SQLAlchemy)                          │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Job Queue & Processing                         │
│                       (Celery + Redis)                             │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Intelligent Routing Engine                       │
│                                                                     │
│  ┌───────────────────────────────────────────────────────┐        │
│  │  Prompt Analyzer                                      │        │
│  │  • NLP keyword extraction                             │        │
│  │  • Object type classification                         │        │
│  │  • Complexity assessment                              │        │
│  │  • Feature detection                                  │        │
│  └───────────────────────────────────────────────────────┘        │
│                           │                                         │
│                           ▼                                         │
│  ┌───────────────────────────────────────────────────────┐        │
│  │  Pipeline Selector                                    │        │
│  │  • Decision: parametric | ai | hybrid                 │        │
│  │  • Confidence scoring                                 │        │
│  │  • Fallback strategies                                │        │
│  └───────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│   Parametric     │  │   AI Generation  │  │   Hybrid Pipeline    │
│   Pipeline       │  │   Pipeline       │  │                      │
└──────────────────┘  └──────────────────┘  └──────────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Pipeline-Specific Processing                     │
│                                                                     │
│  ┌──────────────────────────────────────────────────────┐         │
│  │ Parametric Pipeline (Existing)                       │         │
│  │ • LLM instructions (GPT-4o-mini)                     │         │
│  │ • CadQuery shape generation                          │         │
│  │ • Features: hollow, fillet, thread, etc.             │         │
│  │ • Output: Precise STEP/DXF                           │         │
│  └──────────────────────────────────────────────────────┘         │
│                                                                     │
│  ┌──────────────────────────────────────────────────────┐         │
│  │ AI Generation Pipeline (New)                         │         │
│  │                                                       │         │
│  │ Text-to-3D Branch:                                   │         │
│  │   • Shap-E API (OpenAI)                              │         │
│  │   • Prompt optimization                              │         │
│  │   • Mesh generation (GLB format)                     │         │
│  │                                                       │         │
│  │ Image-to-3D Branch:                                  │         │
│  │   • TripoSR (local/GPU)                              │         │
│  │   • Image preprocessing                              │         │
│  │   • Depth estimation                                 │         │
│  │   • Multi-view fusion (optional)                     │         │
│  │                                                       │         │
│  │ Output: Mesh (GLB, OBJ)                              │         │
│  └──────────────────────────────────────────────────────┘         │
│                                                                     │
│  ┌──────────────────────────────────────────────────────┐         │
│  │ Hybrid Pipeline (New)                                │         │
│  │ • Generate AI base mesh                              │         │
│  │ • Extract parametric constraints                     │         │
│  │ • Add parametric features                            │         │
│  │ • Boolean operations (union/diff)                    │         │
│  │ • Dimension correction                               │         │
│  │ • Output: Combined mesh                              │         │
│  └──────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Quality Enhancement Layer                        │
│                                                                     │
│  ┌───────────────────────────────────────────────────────┐        │
│  │  Mesh Processing                                      │        │
│  │  • Cleanup (remove artifacts, duplicate vertices)     │        │
│  │  • Auto-repair (fix holes, normals, manifoldness)     │        │
│  │  • Smoothing (Laplacian, subdivision)                 │        │
│  │  • Decimation (polygon reduction)                     │        │
│  │  • UV unwrapping                                      │        │
│  └───────────────────────────────────────────────────────┘        │
│                                                                     │
│  ┌───────────────────────────────────────────────────────┐        │
│  │  Texture & Material Processing                        │        │
│  │  • PBR texture generation                             │        │
│  │  • Material assignment                                │        │
│  │  • Normal map generation                              │        │
│  │  • AO baking (optional)                               │        │
│  └───────────────────────────────────────────────────────┘        │
│                                                                     │
│  ┌───────────────────────────────────────────────────────┐        │
│  │  Quality Validation                                   │        │
│  │  • Mesh integrity check                               │        │
│  │  • Quality scoring (1-10)                             │        │
│  │  • Metrics collection                                 │        │
│  │  • Auto-retry if quality too low                      │        │
│  └───────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Format Conversion Layer                        │
│                                                                     │
│  Mesh → STEP:        Mesh → DXF:         Mesh → GLB:              │
│  • trimesh → STEP    • 2D projection     • Native format           │
│  • CadQuery bridge   • Footprint + mesh  • PBR materials           │
│  • Precision CAD     • Compatible        • Textures                │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Storage & Delivery                           │
│  • File storage (MinIO/S3)                                         │
│  • Database records (PostgreSQL)                                   │
│  • Download URLs                                                   │
│  • Preview thumbnails                                              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Intelligent Routing Engine

**Location**: `backend/app/services/routing.py` (new)

**Responsibilities**:
- Analyze user prompts
- Classify object type
- Select optimal pipeline
- Provide confidence scores

**Key Functions**:
```python
def analyze_prompt(prompt: str) -> PromptAnalysis:
    """Analyze prompt and extract features."""

def classify_object_type(analysis: PromptAnalysis) -> ObjectType:
    """Classify as: engineering, architectural, organic, artistic."""

def select_pipeline(object_type: ObjectType) -> PipelineType:
    """Return: 'parametric' | 'ai' | 'hybrid'."""

def calculate_confidence(analysis: PromptAnalysis) -> float:
    """Confidence score 0.0-1.0."""
```

**Classification Rules**:

| Keywords | Object Type | Pipeline | Confidence |
|----------|-------------|----------|------------|
| cup, bottle, screw, bolt, adapter | Engineering | Parametric | 0.95 |
| room, house, apartment, building | Architectural | Parametric | 0.95 |
| dragon, face, animal, plant, tree | Organic | AI | 0.90 |
| statue, sculpture, art, decorative | Artistic | AI | 0.85 |
| cup with dragon, decorative bottle | Hybrid | Hybrid | 0.80 |
| unknown/ambiguous | Default | AI | 0.60 |

---

### 2. AI Generation Pipeline

**Location**: `backend/app/pipelines/ai.py` (new)

**Sub-components**:

#### A. Shap-E Service
**Location**: `backend/app/services/shap_e.py` (new)

```python
class ShapEService:
    """OpenAI Shap-E text-to-3D generation."""

    async def generate_from_text(
        self,
        prompt: str,
        guidance_scale: float = 15.0,
        num_steps: int = 64
    ) -> bytes:
        """
        Generate 3D mesh from text prompt.

        Returns: GLB file bytes
        """

    async def optimize_prompt(self, prompt: str) -> str:
        """Optimize prompt for better Shap-E results."""
```

**API Integration**:
- Endpoint: OpenAI Shap-E API
- Authentication: OpenAI API key
- Rate limiting: 100 requests/minute
- Retry logic: 3 attempts with exponential backoff
- Timeout: 120 seconds

#### B. TripoSR Service
**Location**: `backend/app/services/triposr.py` (new)

```python
class TripoSRService:
    """Image-to-3D using TripoSR model."""

    async def generate_from_image(
        self,
        image_path: str,
        mc_resolution: int = 256
    ) -> bytes:
        """
        Generate 3D mesh from single image.

        Returns: OBJ file bytes
        """

    async def generate_from_multiview(
        self,
        image_paths: list[str]
    ) -> bytes:
        """Generate from multiple view images."""
```

**Model Details**:
- Model: TripoSR (Stability AI)
- Size: ~1.5GB
- Runtime: GPU ~10s, CPU ~60s
- Input: Single RGB image
- Output: Mesh (OBJ + MTL)

---

### 3. Mesh Processing Layer

**Location**: `backend/app/services/mesh_processor.py` (new)

**Operations**:

#### A. Mesh Cleanup
```python
def clean_mesh(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """
    Clean mesh artifacts:
    • Remove duplicate vertices
    • Remove degenerate faces
    • Fix normals
    • Remove disconnected components (if small)
    """
```

#### B. Mesh Repair
```python
def repair_mesh(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """
    Repair mesh issues:
    • Fill holes
    • Make manifold
    • Fix orientation
    • Ensure watertight
    """
```

#### C. Mesh Optimization
```python
def optimize_mesh(
    mesh: trimesh.Trimesh,
    target_faces: int = 50000
) -> trimesh.Trimesh:
    """
    Optimize polygon count:
    • Quadric edge collapse decimation
    • Preserve sharp edges
    • Preserve UV boundaries
    • Target: 10k-100k faces
    """
```

#### D. Mesh Smoothing
```python
def smooth_mesh(
    mesh: trimesh.Trimesh,
    iterations: int = 2
) -> trimesh.Trimesh:
    """
    Smooth mesh surface:
    • Laplacian smoothing
    • Preserve volume
    • Preserve features
    """
```

---

### 4. Quality Validation System

**Location**: `backend/app/services/quality_validator.py` (new)

**Quality Metrics**:

```python
@dataclass
class QualityMetrics:
    # Mesh integrity
    is_watertight: bool
    is_manifold: bool
    has_degenerate_faces: bool

    # Geometry quality
    face_count: int
    vertex_count: int
    edge_count: int
    avg_edge_length: float
    aspect_ratio_min: float
    aspect_ratio_max: float

    # Topology
    genus: int  # Number of holes
    num_components: int
    euler_characteristic: int

    # Quality score (1-10)
    overall_score: float

    # Recommendations
    needs_repair: bool
    needs_decimation: bool
    needs_smoothing: bool
```

**Scoring Algorithm**:
```python
def calculate_quality_score(mesh: trimesh.Trimesh) -> float:
    """
    Calculate quality score 1.0-10.0 based on:
    • Manifoldness: +3.0
    • Watertight: +2.0
    • No degenerate faces: +1.0
    • Good aspect ratios: +2.0
    • Appropriate face count: +1.0
    • Single component: +1.0

    Total: 10.0 possible
    """
```

**Auto-Retry Logic**:
```python
async def generate_with_quality_check(
    prompt: str,
    min_quality: float = 7.0,
    max_retries: int = 3
) -> tuple[bytes, QualityMetrics]:
    """
    Generate mesh and retry if quality too low.
    """
    for attempt in range(max_retries):
        mesh_bytes = await generate_mesh(prompt)
        quality = calculate_quality(mesh_bytes)

        if quality.overall_score >= min_quality:
            return mesh_bytes, quality

        # Adjust parameters for retry
        prompt = optimize_prompt_for_retry(prompt, quality)

    # Return best attempt
    return mesh_bytes, quality
```

---

### 5. Hybrid Pipeline

**Location**: `backend/app/pipelines/hybrid.py` (new)

**Process Flow**:

```python
async def generate_hybrid(
    prompt: str,
    params: dict
) -> dict:
    """
    Generate hybrid object (AI base + parametric features).

    Steps:
    1. Generate AI base mesh (Shap-E)
    2. Extract key dimensions
    3. Generate parametric additions (CadQuery)
    4. Perform boolean operations
    5. Apply refinements
    6. Export combined mesh
    """

    # Example: "Coffee cup with dragon decoration"

    # 1. Generate dragon decoration (AI)
    dragon_mesh = await shap_e_service.generate("dragon decoration relief")

    # 2. Generate cup body (Parametric - precise)
    cup_solid = generate_parametric_cup(
        height=90,
        top_radius=37.5,
        bottom_radius=30,
        hollow=True,
        wall_thickness=3
    )

    # 3. Convert meshes to compatible format
    dragon_solid = mesh_to_solid(dragon_mesh)

    # 4. Position dragon on cup surface
    positioned_dragon = position_on_surface(dragon_solid, cup_solid)

    # 5. Boolean union
    combined = cup_solid.union(positioned_dragon)

    # 6. Apply fillet
    result = combined.edges().fillet(2.0)

    return {
        "model": result,
        "metadata": {
            "type": "hybrid",
            "ai_parts": ["dragon"],
            "parametric_parts": ["cup"],
            "operations": ["union", "fillet"]
        }
    }
```

---

### 6. Format Conversion System

**Location**: `backend/app/services/mesh_converter.py` (new)

**Supported Conversions**:

| From | To | Method | Quality |
|------|-----|--------|---------|
| GLB | STEP | trimesh + OCC | High |
| OBJ | STEP | trimesh + OCC | High |
| Mesh | DXF | 2D projection + 3DFACE | Medium |
| GLB | GLB | Direct | Perfect |
| STEP | GLB | OCC + trimesh | High |

**Key Functions**:

```python
def glb_to_step(glb_bytes: bytes) -> bytes:
    """
    Convert GLB mesh to STEP solid.

    Process:
    1. Load GLB with trimesh
    2. Extract mesh geometry
    3. Convert to OpenCASCADE solid
    4. Export as STEP
    """

def mesh_to_dxf_with_3d(mesh: trimesh.Trimesh) -> bytes:
    """
    Convert mesh to DXF with 3DFACE entities.

    Process:
    1. Extract mesh faces
    2. Create 3DFACE for each triangle
    3. Add 2D footprint on layer "FOOTPRINT"
    4. Add 3D mesh on layer "3D_MESH"
    """

def add_textures_to_glb(
    mesh: trimesh.Trimesh,
    texture_path: str
) -> bytes:
    """
    Add PBR textures to GLB export.
    """
```

---

## Data Flow

### 1. Parametric Object (Current Flow)
```
User Prompt
    │
    ├─> GPT-4o-mini (instructions)
    │
    ├─> CadQuery (3D generation)
    │
    ├─> STEP export
    │
    └─> DXF export
```

### 2. AI Object (New Flow)
```
User Prompt
    │
    ├─> Prompt optimization
    │
    ├─> Shap-E API (3D mesh generation)
    │
    ├─> GLB mesh
    │
    ├─> Mesh cleanup & repair
    │
    ├─> Quality validation
    │
    ├─> Format conversion
    │       ├─> STEP
    │       ├─> DXF
    │       └─> GLB
    │
    └─> Storage
```

### 3. Image-to-3D (New Flow)
```
User Image
    │
    ├─> Image preprocessing
    │
    ├─> TripoSR (local GPU/CPU)
    │
    ├─> OBJ mesh
    │
    ├─> Mesh refinement
    │
    ├─> Quality validation
    │
    ├─> Format conversion
    │       ├─> STEP
    │       ├─> DXF
    │       └─> GLB
    │
    └─> Storage
```

### 4. Hybrid Object (New Flow)
```
User Prompt
    │
    ├─> Split prompt (AI parts + parametric parts)
    │
    ├─> AI generation (organic parts)
    │
    ├─> Parametric generation (precise parts)
    │
    ├─> Boolean operations (combine)
    │
    ├─> Refinement
    │
    ├─> Quality validation
    │
    ├─> Format conversion
    │
    └─> Storage
```

---

## Database Schema Changes

### New Tables

#### 1. `ai_generations` table
```sql
CREATE TABLE ai_generations (
    id UUID PRIMARY KEY,
    job_id UUID REFERENCES jobs(id),
    provider VARCHAR(50),  -- 'shap_e', 'triposr'
    prompt TEXT,
    optimized_prompt TEXT,
    model_version VARCHAR(50),
    generation_params JSONB,
    mesh_format VARCHAR(10),  -- 'glb', 'obj'
    raw_mesh_storage_key VARCHAR(255),
    quality_score FLOAT,
    quality_metrics JSONB,
    api_cost DECIMAL(10, 4),
    generation_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 2. `mesh_quality_metrics` table
```sql
CREATE TABLE mesh_quality_metrics (
    id UUID PRIMARY KEY,
    job_id UUID REFERENCES jobs(id),
    ai_generation_id UUID REFERENCES ai_generations(id),
    face_count INTEGER,
    vertex_count INTEGER,
    is_watertight BOOLEAN,
    is_manifold BOOLEAN,
    overall_score FLOAT,
    metrics_json JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 3. `pipeline_routing` table
```sql
CREATE TABLE pipeline_routing (
    id UUID PRIMARY KEY,
    job_id UUID REFERENCES jobs(id),
    prompt TEXT,
    object_type VARCHAR(50),  -- 'engineering', 'organic', etc.
    pipeline_selected VARCHAR(50),  -- 'parametric', 'ai', 'hybrid'
    confidence_score FLOAT,
    routing_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Modified Tables

#### Update `jobs` table:
```sql
ALTER TABLE jobs ADD COLUMN pipeline_type VARCHAR(50);
ALTER TABLE jobs ADD COLUMN ai_generation_id UUID REFERENCES ai_generations(id);
ALTER TABLE jobs ADD COLUMN quality_score FLOAT;
```

---

## Configuration

### Environment Variables

```bash
# OpenAI Shap-E
OPENAI_API_KEY=sk-...
SHAP_E_MODEL=shap-e
SHAP_E_GUIDANCE_SCALE=15.0
SHAP_E_NUM_STEPS=64
SHAP_E_TIMEOUT=120

# TripoSR
TRIPOSR_DEVICE=cuda  # or 'cpu'
TRIPOSR_MODEL_PATH=/models/triposr
TRIPOSR_MC_RESOLUTION=256

# Routing
ROUTING_DEFAULT_PIPELINE=ai  # 'parametric', 'ai', 'hybrid'
ROUTING_CONFIDENCE_THRESHOLD=0.7
ROUTING_ENABLE_HYBRID=true

# Quality
QUALITY_MIN_SCORE=7.0
QUALITY_AUTO_RETRY=true
QUALITY_MAX_RETRIES=3

# Mesh Processing
MESH_TARGET_FACES=50000
MESH_SMOOTHING_ITERATIONS=2
MESH_CLEANUP_ENABLED=true

# API Costs & Limits
SHAP_E_COST_PER_CALL=0.10
API_RATE_LIMIT_PER_MINUTE=100
API_MONTHLY_BUDGET=500.00
```

---

## Performance Considerations

### Expected Response Times

| Pipeline | Operation | Average Time | Max Time |
|----------|-----------|--------------|----------|
| Parametric | Simple object | 2-5s | 15s |
| Parametric | Complex assembly | 5-15s | 60s |
| AI (Shap-E) | Simple object | 10-20s | 60s |
| AI (Shap-E) | Complex object | 20-40s | 120s |
| Image-to-3D (GPU) | Single image | 5-15s | 30s |
| Image-to-3D (CPU) | Single image | 30-90s | 180s |
| Hybrid | Simple combo | 20-40s | 120s |
| Mesh processing | Cleanup | 1-3s | 10s |
| Format conversion | Any → Any | 2-5s | 15s |

### Optimization Strategies

1. **Caching**:
   - Cache common objects (cup, chair, etc.)
   - Cache AI generations for 24 hours
   - Redis-based mesh cache

2. **Batching**:
   - Batch API calls when possible
   - Process multiple quality checks together

3. **GPU Acceleration**:
   - Use GPU for TripoSR (10x faster)
   - Consider GPU for mesh processing

4. **Async Processing**:
   - All pipelines run async
   - Non-blocking quality validation

---

## Security Considerations

### API Security
- Rate limiting per user
- API key rotation
- Cost monitoring and alerts
- Input validation (prompt length, image size)

### Mesh Security
- Virus scanning for uploaded images
- Size limits (mesh < 100MB)
- Complexity limits (faces < 1M)
- Sandbox mesh processing

### Data Privacy
- No storing of user prompts longer than needed
- Option to delete AI generations
- GDPR compliance

---

## Monitoring & Observability

### Metrics to Track

```python
# Pipeline metrics
pipeline_selection_counter  # Count by type
pipeline_success_rate  # Success % by type
pipeline_duration_histogram  # Response times

# AI metrics
shap_e_api_calls_total
shap_e_api_errors_total
shap_e_cost_total
triposr_generations_total
triposr_gpu_utilization

# Quality metrics
mesh_quality_score_histogram
mesh_repair_success_rate
mesh_cleanup_operations_total

# Business metrics
objects_generated_by_category
user_satisfaction_score
api_cost_per_object
```

### Logging

```python
logger.info("Pipeline selected", extra={
    "job_id": job.id,
    "prompt": prompt,
    "pipeline": "ai",
    "confidence": 0.92,
    "object_type": "organic"
})

logger.info("AI generation complete", extra={
    "job_id": job.id,
    "provider": "shap_e",
    "duration_ms": 15420,
    "cost": 0.12,
    "quality_score": 8.5
})
```

---

## Disaster Recovery

### Fallback Strategies

1. **Shap-E API Down**:
   - Fall back to parametric if possible
   - Queue for later retry
   - Notify user of delay

2. **TripoSR Model Error**:
   - Use Shap-E for text description of image
   - Fall back to traditional image-to-2D
   - Manual review option

3. **Quality Too Low**:
   - Auto-retry with optimized parameters
   - Fall back to alternative pipeline
   - Provide mesh with quality warning

4. **GPU Out of Memory**:
   - Fall back to CPU
   - Reduce resolution
   - Queue for later processing

---

## Next Steps

1. Implement routing engine (Week 1)
2. Integrate Shap-E API (Week 1-2)
3. Add mesh processing (Week 3-4)
4. Integrate TripoSR (Week 3)
5. Build hybrid pipeline (Week 5)
6. Testing and optimization (Week 6-7)
7. Production deployment (Week 8)

---

**Architecture Status**: 📋 **Design Complete**
**Ready for**: Implementation Phase 1
