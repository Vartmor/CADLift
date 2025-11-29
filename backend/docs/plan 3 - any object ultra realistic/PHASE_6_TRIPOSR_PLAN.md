# Phase 6: TripoSR Integration (Shap-E Replacement)

**Date Started**: November 29, 2025
**Status**: 📋 IN PROGRESS
**Goal**: Replace Shap-E with TripoSR for AI-powered image-to-3D mesh generation

---

## Why TripoSR?

### Problem with Shap-E
- ❌ **PyTorch/CLIP JIT incompatibility** on Windows
- ❌ Segmentation fault when loading CLIP models
- ❌ Unfixable from application layer (PyTorch core bug)
- ❌ See [SHAP_E_INVESTIGATION.md](SHAP_E_INVESTIGATION.md) for full details

### TripoSR Advantages
| Feature | Shap-E (2022) | TripoSR (2024) |
|---------|---------------|----------------|
| **Release** | 2022 (OpenAI) | 2024 (Stability AI) |
| **Input** | Text prompts | Images (sketches, drawings, photos) |
| **CLIP Dependency** | ❌ Required (broken) | ✅ No CLIP (uses custom encoder) |
| **Model Size** | ~4GB (3 models) | ~2GB (single model) |
| **Quality** | Good | **Excellent** (state-of-art 2024) |
| **Speed (GPU)** | ~30s | **~5-10s** |
| **Speed (CPU)** | ~2-5 min | ~1-2 min |
| **Windows Support** | ❌ Broken (JIT bug) | ✅ **Works** |
| **Maintenance** | Archived (no updates) | **Active development** |
| **CAD Use Case** | Text → 3D (indirect) | **Image → 3D (perfect for drawings!)** |

---

## Integration with Existing System

### Current Working Pipeline (Phase 2)
```
User uploads image
    ↓
GPT-4 Vision analyzes image
    ↓
Generates detailed description
    ↓
GPT-4 generates OpenSCAD code
    ↓
Compiles to 3D model
    ↓
Export as DXF/GLB/STEP
```

### New TripoSR Pipeline (Phase 6)
```
User uploads image (engineering drawing, sketch, or photo)
    ↓
TripoSR processes image directly
    ↓
Generates 3D mesh (GLB format)
    ↓
Optional: GPT-4 analyzes for refinements
    ↓
Mesh cleanup & conversion
    ↓
Export as DXF/GLB/STEP (using existing converters)
```

### Hybrid Workflow (Best of Both)
```
User uploads engineering drawing
    ├─ Option A: TripoSR (fast, AI mesh)
    │      → Direct image-to-3D
    │      → Good for organic/complex shapes
    │
    └─ Option B: GPT-4 Vision + OpenSCAD (precise, parametric)
           → Analysis → Code generation
           → Perfect for mechanical parts with dimensions
```

**User can choose which approach based on use case!**

---

## Implementation Tasks

### Task 1: TripoSR Installation (1-2 hours)
**Subtasks**:
- [ ] Install TripoSR from HuggingFace (`stabilityai/triposr`)
- [ ] Download pre-trained model weights (~2GB)
- [ ] Test basic model loading (CPU and GPU modes)
- [ ] Verify dependencies (torch, PIL, numpy, trimesh)

**Success Criteria**:
- ✅ Model loads without errors
- ✅ Can run inference on sample image
- ✅ GPU acceleration working (CUDA)

---

### Task 2: Service Wrapper Creation (3-4 hours)
**File**: `backend/app/services/triposr.py`

**Structure** (similar to shap_e.py):
```python
class TripoSRService:
    def __init__(self):
        self.enabled = True
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None  # Lazy load

    def _load_model(self):
        """Load TripoSR model (first use)."""
        from tsr.system import TSR
        self.model = TSR.from_pretrained(
            "stabilityai/triposr",
            config_name="config.yaml",
            weight_name="model.ckpt"
        )
        self.model.to(self.device)

    def generate_from_image(
        self,
        image_bytes: bytes,
        output_format: str = "glb"
    ) -> bytes:
        """Generate 3D mesh from image."""
        # Load image
        image = Image.open(BytesIO(image_bytes))

        # Run TripoSR
        scene_codes = self.model([image], device=self.device)
        meshes = self.model.extract_mesh(scene_codes)

        # Convert to GLB/OBJ
        return self._export_mesh(meshes[0], output_format)
```

**Success Criteria**:
- ✅ Service initializes correctly
- ✅ Lazy model loading works
- ✅ GPU/CPU device selection
- ✅ Proper error handling

---

### Task 3: API Integration (2-3 hours)
**Files**:
- `backend/app/api/v1/generate.py` (add TripoSR endpoint)
- `backend/app/pipelines/triposr.py` (pipeline orchestration)

**New Endpoint**:
```python
@router.post("/generate/triposr")
async def generate_triposr(
    file: UploadFile = File(...),
    output_formats: list[str] = Query(default=["glb"])
):
    """Generate 3D model from image using TripoSR."""
    # Validate image format
    # Call TripoSR service
    # Convert formats
    # Save to database
    # Return job status
```

**Success Criteria**:
- ✅ Endpoint accepts image upload
- ✅ Returns job ID
- ✅ Async processing works
- ✅ Multiple format exports

---

### Task 4: Frontend Integration (2-3 hours)
**Files**:
- `components/ImageUpload.tsx` (add TripoSR option)
- `services/jobService.ts` (add TripoSR API call)

**UI Changes**:
```tsx
// Add toggle for generation method
<select onChange={setGenerationMethod}>
  <option value="gpt4_openscad">GPT-4 + OpenSCAD (Precise CAD)</option>
  <option value="triposr">TripoSR (AI Mesh - Fast)</option>
</select>

// Show estimated time
{generationMethod === "triposr" && (
  <p>⚡ Estimated time: ~10-30 seconds</p>
)}
```

**Success Criteria**:
- ✅ User can select TripoSR
- ✅ Upload button triggers TripoSR endpoint
- ✅ Progress tracking works
- ✅ 3D viewer displays result

---

### Task 5: Testing & Benchmarking (3-4 hours)
**Test Cases**:
1. **Engineering Drawing** (primary use case)
   - Upload mechanical part drawing
   - Generate with TripoSR
   - Verify dimensions/proportions
   - Export to DXF/STEP

2. **Hand-drawn Sketch**
   - Upload rough sketch
   - Generate mesh
   - Check quality score

3. **Photo of Object**
   - Upload photo
   - Generate 3D model
   - Validate topology

4. **Complex Shape**
   - Upload organic shape drawing
   - Generate mesh
   - Test mesh cleanup

5. **Performance Benchmarks**
   - GPU vs CPU timing
   - Memory usage
   - Quality metrics

**Success Criteria**:
- ✅ 5/5 test cases passing
- ✅ Generation time < 30s (GPU)
- ✅ Quality score > 8.5/10
- ✅ Mesh watertight and manifold

---

### Task 6: Documentation (2-3 hours)
**Documents to Create/Update**:
1. `PHASE_6_COMPLETION_SUMMARY.md`
2. Update `README.md` with TripoSR features
3. API documentation for `/generate/triposr`
4. User guide: "When to use TripoSR vs OpenSCAD"

**Success Criteria**:
- ✅ All docs complete
- ✅ Examples with images
- ✅ Troubleshooting guide

---

## Timeline

| Task | Duration | Status |
|------|----------|--------|
| 1. TripoSR Installation | 1-2 hours | 📋 TODO |
| 2. Service Wrapper | 3-4 hours | 📋 TODO |
| 3. API Integration | 2-3 hours | 📋 TODO |
| 4. Frontend Integration | 2-3 hours | 📋 TODO |
| 5. Testing & Benchmarks | 3-4 hours | 📋 TODO |
| 6. Documentation | 2-3 hours | 📋 TODO |
| **Total** | **15-20 hours** | |

**Target Completion**: December 1-2, 2025 (2-3 days)

---

## Technical Specifications

### Model Details
- **Name**: TripoSR
- **Source**: Stability AI / Hugging Face
- **Size**: ~2GB
- **Architecture**: Transformer-based (no CLIP!)
- **Input**: Single image (any size, auto-resized)
- **Output**: Mesh (vertices, faces, normals)
- **Formats**: GLB, OBJ natively

### System Requirements
- **RAM**: 8GB minimum (16GB recommended)
- **GPU**: NVIDIA with CUDA (optional, 4GB+ VRAM)
- **CPU**: Any modern CPU (fallback mode)
- **Disk**: 5GB for model + cache

### Dependencies
```bash
pip install triposr torch torchvision trimesh pillow
```

---

## Success Metrics

### Performance Targets
- ✅ Generation time: <30s (GPU), <2min (CPU)
- ✅ Quality score: >8.5/10
- ✅ Success rate: >90%
- ✅ Mesh validity: 100% watertight

### User Experience
- ✅ Easy image upload
- ✅ Clear generation method selection
- ✅ Real-time progress tracking
- ✅ Interactive 3D preview
- ✅ Multiple format download

### Integration
- ✅ Works with existing pipeline
- ✅ Compatible with mesh converter
- ✅ Integrates with 3D viewer
- ✅ No breaking changes

---

## Risk Mitigation

### Potential Issues
1. **GPU Memory**: TripoSR needs ~2GB VRAM
   - **Mitigation**: CPU fallback mode, memory management

2. **Model Download**: 2GB download on first use
   - **Mitigation**: Pre-download during setup, show progress

3. **Quality Variability**: AI-generated meshes may vary
   - **Mitigation**: Multiple attempts, quality scoring, refinement options

4. **Windows Compatibility**: Ensure no PyTorch issues
   - **Mitigation**: Thorough testing, no CLIP dependency

---

## Next Steps

1. **Install TripoSR** and test basic functionality
2. **Create service wrapper** with lazy loading
3. **Integrate API** endpoint
4. **Update frontend** with generation method selector
5. **Run comprehensive tests**
6. **Document everything**
7. **Deploy and monitor**

---

**Status**: Ready to begin implementation!
**First Task**: Install TripoSR and verify model loading
