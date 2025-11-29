# Implementation Checklist - Phase by Phase

**Date**: 2025-11-27
**Purpose**: Step-by-step implementation guide for Plan 3

---

## Pre-Implementation Setup

### Environment Setup
- [ ] OpenAI API key added to `.env`
- [ ] Verify API key works: `echo $OPENAI_API_KEY`
- [ ] GPU instance provisioned (or confirmed CPU fallback)
- [ ] All dependencies installed
- [ ] Development branch created: `git checkout -b feature/any-object-ai`

### Verify Current System
- [ ] Run current tests: `python tests/test_phase1_fixes.py`
- [ ] Verify 47/47 tests passing
- [ ] Current prompt-to-3D works (test with "coffee cup")
- [ ] No blocking bugs or issues

### Documentation Review
- [ ] Read main plan: `ULTRA_REALISTIC_ANY_OBJECT_PLAN.md`
- [ ] Study architecture: `ARCHITECTURE.md`
- [ ] Review API integration: `API_INTEGRATION.md`
- [ ] Understand routing logic: `ROUTING_LOGIC.md`

---

## Phase 1: Shap-E Integration (Week 1-2)

### 1.1 Create Routing Service
**File**: `backend/app/services/routing.py`

- [ ] Create `RoutingService` class
- [ ] Implement `analyze_prompt()` method
- [ ] Implement `classify_object_type()` method
- [ ] Implement `select_pipeline()` method
- [ ] Add keyword dictionaries (engineering, architectural, organic, artistic)
- [ ] Add dimension extraction logic
- [ ] Add feature detection logic
- [ ] Create confidence scoring algorithm
- [ ] Test with 10 example prompts

**Verification**:
```bash
python -c "from app.services.routing import get_routing_service;
service = get_routing_service();
print(service.route('coffee cup, 90mm tall').pipeline)"
# Expected: "parametric"
```

### 1.2 Create Shap-E Service
**File**: `backend/app/services/shap_e.py`

- [ ] Create `ShapEService` class
- [ ] Implement `__init__()` with API key
- [ ] Implement `generate_from_text()` method
- [ ] Implement `_optimize_prompt()` helper
- [ ] Implement `generate_batch()` for multiple prompts
- [ ] Add error handling and retries
- [ ] Add cost tracking
- [ ] Test with simple prompt: "cube"

**Verification**:
```bash
python -c "from app.services.shap_e import get_shap_e_service;
import asyncio;
service = get_shap_e_service();
result = asyncio.run(service.generate_from_text('simple cube'));
print(f'Generated {len(result)} bytes')"
# Expected: GLB file bytes
```

### 1.3 Create Mesh Converter
**File**: `backend/app/services/mesh_converter.py`

- [ ] Create `MeshConverter` class
- [ ] Implement `glb_to_step()` conversion
- [ ] Implement `glb_to_dxf()` conversion
- [ ] Implement `obj_to_step()` conversion
- [ ] Add format validation
- [ ] Add error handling
- [ ] Test all conversions

**Verification**:
```bash
# Test GLB → STEP conversion
python -c "from app.services.mesh_converter import convert_mesh;
glb_data = open('test.glb', 'rb').read();
step_data = convert_mesh(glb_data, 'glb', 'step');
print(f'STEP size: {len(step_data)} bytes')"
```

### 1.4 Create AI Pipeline
**File**: `backend/app/pipelines/ai.py`

- [ ] Create `run_ai_pipeline()` function
- [ ] Add text-to-3D branch (Shap-E)
- [ ] Add mesh processing call
- [ ] Add format conversion
- [ ] Add quality metrics
- [ ] Add metadata tracking
- [ ] Test end-to-end with simple object

**Verification**:
```bash
# Test full AI pipeline
python tests/test_ai_pipeline_simple.py
# Expected: PASS
```

### 1.5 Update Main Pipeline
**File**: `backend/app/pipelines/prompt.py`

- [ ] Add routing service integration
- [ ] Add AI pipeline branch
- [ ] Keep parametric pipeline (existing)
- [ ] Add pipeline selection logic
- [ ] Add fallback mechanisms
- [ ] Test routing works correctly

**Verification**:
```bash
# Test parametric still works
python -c "from app.pipelines.prompt import run; # test existing"

# Test AI routing
# ... verify AI objects route to Shap-E
```

### 1.6 Testing
**File**: `backend/tests/test_shap_e_integration.py`

- [ ] Test 1: Service initialization
- [ ] Test 2: Simple cube generation
- [ ] Test 3: Organic dragon generation
- [ ] Test 4: Prompt optimization
- [ ] Test 5: Batch generation
- [ ] Test 6: Error handling
- [ ] Test 7: Retry logic
- [ ] Test 8: GLB → STEP conversion
- [ ] All 8 tests passing

**Verification**:
```bash
python tests/test_shap_e_integration.py
# Expected: 8/8 PASSED
```

### 1.7 Database Changes
**File**: `backend/alembic/versions/XXX_add_ai_generation.py`

- [ ] Create migration for `ai_generations` table
- [ ] Create migration for `mesh_quality_metrics` table
- [ ] Create migration for `pipeline_routing` table
- [ ] Update `jobs` table (add columns)
- [ ] Run migration: `alembic upgrade head`
- [ ] Verify tables created

**Verification**:
```sql
SELECT table_name FROM information_schema.tables
WHERE table_name IN ('ai_generations', 'mesh_quality_metrics', 'pipeline_routing');
```

### Phase 1 Deliverables Checklist
- [ ] ✅ Routing service works (90%+ accuracy)
- [ ] ✅ Shap-E generates 10+ object types
- [ ] ✅ Mesh conversion successful (GLB → STEP, DXF)
- [ ] ✅ 8/8 integration tests passing
- [ ] ✅ Database migrations complete
- [ ] ✅ Documentation updated
- [ ] ✅ Code reviewed and merged

---

## Phase 2: Image-to-3D (Week 3)

### 2.1 Download TripoSR Model
- [ ] Install dependencies: `pip install torch transformers`
- [ ] Download model:
```python
from transformers import AutoModel
model = AutoModel.from_pretrained("stabilityai/TripoSR",
                                    trust_remote_code=True,
                                    cache_dir="/models/triposr")
```
- [ ] Verify model loaded: ~1.5GB size
- [ ] Test on GPU: `torch.cuda.is_available()`

### 2.2 Create TripoSR Service
**File**: `backend/app/services/triposr.py`

- [ ] Create `TripoSRService` class
- [ ] Implement model loading
- [ ] Implement `generate_from_image()` method
- [ ] Add background removal (`_remove_background()`)
- [ ] Add image preprocessing
- [ ] Test with sample image

**Verification**:
```bash
python -c "from app.services.triposr import get_triposr_service;
import asyncio;
service = get_triposr_service();
result = asyncio.run(service.generate_from_image('test_chair.jpg'));
print(f'Generated {len(result)} bytes')"
```

### 2.3 Update AI Pipeline
**File**: `backend/app/pipelines/ai.py`

- [ ] Add image-to-3D branch
- [ ] Add image source type handling
- [ ] Add OBJ → GLB conversion
- [ ] Test with image input

### 2.4 Testing
**File**: `backend/tests/test_triposr_integration.py`

- [ ] Test 1: Service initialization
- [ ] Test 2: Simple object from image
- [ ] Test 3: Background removal
- [ ] Test 4: Different resolutions
- [ ] Test 5: Error handling
- [ ] Test 6: OBJ → STEP conversion
- [ ] All 6 tests passing

**Verification**:
```bash
python tests/test_triposr_integration.py
# Expected: 6/6 PASSED
```

### Phase 2 Deliverables Checklist
- [ ] ✅ TripoSR generates from images
- [ ] ✅ Background removal works
- [ ] ✅ Image-to-3D success rate: 85%+
- [ ] ✅ 6/6 tests passing
- [ ] ✅ GPU/CPU fallback working

---

## Phase 3: Quality Enhancement (Week 4)

### 3.1 Create Mesh Processor
**File**: `backend/app/services/mesh_processor.py`

- [ ] Create `MeshProcessor` class
- [ ] Implement `_cleanup_mesh()` method
- [ ] Implement `_repair_mesh()` method
- [ ] Implement `_decimate_mesh()` method
- [ ] Implement `_smooth_mesh()` method
- [ ] Implement `_calculate_quality()` method
- [ ] Test each operation individually

### 3.2 Quality Metrics System
**Same file**: `backend/app/services/mesh_processor.py`

- [ ] Create `QualityMetrics` dataclass
- [ ] Implement topology checks (watertight, manifold)
- [ ] Implement geometry checks (edges, angles)
- [ ] Implement quality scoring (1-10 scale)
- [ ] Add recommendations (needs_repair, etc.)
- [ ] Test with good and bad meshes

### 3.3 Auto-Retry Logic
- [ ] Implement `process_mesh()` with retry
- [ ] Add quality threshold checking
- [ ] Add parameter adjustment on retry
- [ ] Test retry behavior

### 3.4 Integrate into Pipeline
- [ ] Add mesh processing to AI pipeline
- [ ] Add quality metrics to job output
- [ ] Store quality data in database
- [ ] Test full flow

### 3.5 Testing
**File**: `backend/tests/test_mesh_processor.py`

- [ ] Test 1: Cleanup removes duplicates
- [ ] Test 2: Repair fixes holes
- [ ] Test 3: Decimation reduces faces
- [ ] Test 4: Smoothing works
- [ ] Test 5: Quality calculation correct
- [ ] Test 6-15: Edge cases
- [ ] All 15 tests passing

### Phase 3 Deliverables Checklist
- [ ] ✅ Mesh cleanup works (95%+ success)
- [ ] ✅ Quality scoring accurate
- [ ] ✅ Average quality: 8/10+
- [ ] ✅ 15/15 tests passing
- [ ] ✅ Auto-retry reduces failures

---

## Phase 4: Hybrid Pipeline (Week 5)

### 4.1 Create Hybrid Service
**File**: `backend/app/pipelines/hybrid.py`

- [ ] Create `run_hybrid_pipeline()` function
- [ ] Implement prompt splitting (AI + parametric parts)
- [ ] Generate AI base mesh
- [ ] Generate parametric features
- [ ] Implement boolean operations (union, difference)
- [ ] Add dimension scaling
- [ ] Test with simple hybrid object

### 4.2 Boolean Operations
- [ ] Test union (combine two meshes)
- [ ] Test difference (subtract mesh)
- [ ] Test intersection
- [ ] Handle failures gracefully

### 4.3 Update Routing
**File**: `backend/app/services/routing.py`

- [ ] Add hybrid detection logic
- [ ] Update classification for mixed prompts
- [ ] Test hybrid routing accuracy

### 4.4 Testing
**File**: `backend/tests/test_hybrid_pipeline.py`

- [ ] Test 1: Decorated cup generation
- [ ] Test 2: Boolean union works
- [ ] Test 3: Boolean difference works
- [ ] Test 4: Dimension scaling accurate
- [ ] Test 5-8: Complex assemblies
- [ ] All 8 tests passing

### Phase 4 Deliverables Checklist
- [ ] ✅ Hybrid objects generated (20+ examples)
- [ ] ✅ Boolean operations work (90%+ success)
- [ ] ✅ Dimension accuracy: 95%+
- [ ] ✅ 8/8 tests passing

---

## Phase 5: Textures & Materials (Week 6)

### 5.1 Texture Generation
**File**: `backend/app/services/texture_generator.py`

- [ ] Create `TextureGenerator` class
- [ ] Implement PBR texture generation
- [ ] Add UV unwrapping
- [ ] Add normal map generation
- [ ] Test with simple object

### 5.2 Material Library
**File**: `backend/app/services/materials.py`

- [ ] Create material definitions (50+ materials)
- [ ] Add material categories (metal, wood, plastic, etc.)
- [ ] Implement material assignment
- [ ] Test material application

### 5.3 Update Export
- [ ] Add textures to GLB export
- [ ] Add materials to STEP export (if possible)
- [ ] Test exports with textures

### Phase 5 Deliverables Checklist
- [ ] ✅ Textures generated (85%+ success)
- [ ] ✅ 50+ materials available
- [ ] ✅ UV mapping works
- [ ] ✅ Exports include materials

---

## Phase 6: Testing & Documentation (Week 7)

### 6.1 Unit Tests (62 total)
- [ ] Routing tests: 10/10
- [ ] Shap-E tests: 8/8
- [ ] TripoSR tests: 6/6
- [ ] Mesh processing tests: 15/15
- [ ] Quality validation tests: 10/10
- [ ] Hybrid tests: 5/5
- [ ] Conversion tests: 8/8

### 6.2 Integration Tests (35 total)
- [ ] Routing integration: 5/5
- [ ] Shap-E integration: 5/5
- [ ] TripoSR integration: 4/4
- [ ] Mesh processing integration: 5/5
- [ ] Hybrid integration: 8/8
- [ ] Conversion integration: 5/5
- [ ] Quality validation integration: 3/3

### 6.3 E2E Tests (13 total)
- [ ] Parametric E2E: 3/3
- [ ] AI E2E: 3/3
- [ ] Hybrid E2E: 3/3
- [ ] Image-to-3D E2E: 2/2
- [ ] Routing E2E: 2/2

### 6.4 Performance Tests
- [ ] Concurrent generation test (10 objects)
- [ ] Response time test (parametric < 15s)
- [ ] Response time test (AI < 60s)
- [ ] Load test (sustained load)

### 6.5 Documentation
- [ ] Update API documentation
- [ ] Create user guide with 100+ examples
- [ ] Write migration guide
- [ ] Create troubleshooting guide
- [ ] Update README

### Phase 6 Deliverables Checklist
- [ ] ✅ 110/110 automated tests passing (100%)
- [ ] ✅ Performance benchmarks met
- [ ] ✅ Documentation complete
- [ ] ✅ User examples (100+)

---

## Phase 7: Production Deployment (Week 8)

### 7.1 Pre-Deployment Checklist
- [ ] All 110 tests passing
- [ ] Code reviewed by team
- [ ] Security audit completed
- [ ] Performance optimized
- [ ] API costs within budget
- [ ] Documentation published
- [ ] User training completed

### 7.2 Monitoring Setup
- [ ] Prometheus metrics configured
- [ ] Grafana dashboards created
- [ ] Alert rules defined
- [ ] Log aggregation working
- [ ] Error tracking (Sentry/etc) configured

### 7.3 Deployment
- [ ] Database migrations run on production
- [ ] Environment variables configured
- [ ] TripoSR model downloaded to prod
- [ ] API keys configured
- [ ] Deploy to staging first
- [ ] Run smoke tests on staging
- [ ] Deploy to production
- [ ] Verify production deployment

### 7.4 Post-Deployment
- [ ] Monitor for 24 hours
- [ ] Check error rates
- [ ] Verify API costs
- [ ] Collect user feedback
- [ ] Create incident response plan

### Phase 7 Deliverables Checklist
- [ ] ✅ Production deployment successful
- [ ] ✅ Monitoring active
- [ ] ✅ Zero critical bugs
- [ ] ✅ User feedback positive

---

## Final Verification Checklist

### Quality Standards
- [ ] Test pass rate: 95%+ (110+ tests)
- [ ] Average quality score: 8.0+/10
- [ ] Generation success rate: 95%+
- [ ] Object coverage: 95%+ (any type)

### Performance Standards
- [ ] Parametric: <15s average
- [ ] AI: <60s average
- [ ] Hybrid: <120s average
- [ ] Concurrent: 10+ simultaneous requests

### Business Standards
- [ ] User satisfaction: 4.5/5+
- [ ] Feature usage: 80%+ try AI
- [ ] API cost: <$0.20 per object
- [ ] Uptime: 99.9%+

### Documentation Standards
- [ ] 100+ example prompts documented
- [ ] API documentation complete
- [ ] User guide published
- [ ] Troubleshooting guide available
- [ ] Migration guide clear

---

## Success Metrics Dashboard

### Week 1-2 (Phase 1)
- Objects generated: ___/10 ✅
- Tests passing: ___/8 ✅
- Routing accuracy: ___%/90%+ ✅

### Week 3 (Phase 2)
- Image conversions: ___/10 ✅
- Tests passing: ___/6 ✅
- Success rate: ___%/85%+ ✅

### Week 4 (Phase 3)
- Quality score avg: ___/8.0+ ✅
- Tests passing: ___/15 ✅
- Cleanup success: ___%/95%+ ✅

### Week 5 (Phase 4)
- Hybrid objects: ___/20 ✅
- Tests passing: ___/8 ✅
- Boolean success: ___%/90%+ ✅

### Week 6 (Phase 5)
- Materials created: ___/50 ✅
- Texture success: ___%/85%+ ✅

### Week 7 (Phase 6)
- Total tests passing: ___/110 ✅
- Documentation: ___/100% ✅
- Examples created: ___/100+ ✅

### Week 8 (Phase 7)
- Production deployed: ___✅
- Uptime: ___%/99.9%+ ✅
- User satisfaction: ___/4.5+ ✅

---

## Troubleshooting Common Issues

### Shap-E API Issues
- **Error**: "Invalid API key"
  - [ ] Check `.env` file has correct key
  - [ ] Verify key starts with `sk-`
  - [ ] Test key: `openai api key.validate`

### TripoSR Issues
- **Error**: "CUDA out of memory"
  - [ ] Reduce `mc_resolution` (512 → 256 → 128)
  - [ ] Use CPU: `TRIPOSR_DEVICE=cpu`
  - [ ] Clear cache: `torch.cuda.empty_cache()`

### Mesh Processing Issues
- **Error**: "Mesh conversion failed"
  - [ ] Check mesh is valid (watertight)
  - [ ] Run repair first
  - [ ] Try alternative conversion method

### Database Issues
- **Error**: "Table already exists"
  - [ ] Check migration status: `alembic current`
  - [ ] Rollback if needed: `alembic downgrade -1`
  - [ ] Re-run: `alembic upgrade head`

---

## Notes & Learnings

### Week 1 Notes
```
Date: ___________
Progress: _______
Blockers: _______
Learnings: ______
```

### Week 2 Notes
```
Date: ___________
Progress: _______
Blockers: _______
Learnings: ______
```

---

**Checklist Status**: ✅ **Complete**
**Ready for**: Phase 1 Implementation
**Use this**: As daily implementation guide
