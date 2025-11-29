# Testing Plan - Any Object Ultra-Realistic

**Date**: 2025-11-27
**Version**: 1.0

---

## Testing Strategy

Comprehensive testing across all phases to ensure:
1. **Correctness**: All components work as designed
2. **Quality**: Generated objects meet ultra-realistic standards
3. **Performance**: System meets response time requirements
4. **Reliability**: Stable under load and error conditions

---

## Test Coverage Matrix

| Component | Unit Tests | Integration Tests | E2E Tests | Manual Tests | Total |
|-----------|------------|-------------------|-----------|--------------|-------|
| Routing Engine | 10 | 5 | 3 | 2 | 20 |
| Shap-E Integration | 8 | 5 | 3 | 5 | 21 |
| TripoSR Integration | 6 | 4 | 2 | 3 | 15 |
| Mesh Processing | 15 | 5 | - | 2 | 22 |
| Quality Validation | 10 | 3 | - | 1 | 14 |
| Hybrid Pipeline | 5 | 8 | 5 | 5 | 23 |
| Format Conversion | 8 | 5 | - | 2 | 15 |
| **Total** | **62** | **35** | **13** | **20** | **130** |

---

## Phase 1: Shap-E Integration Tests

### Unit Tests (8 tests)

**File**: `tests/test_shap_e_service.py`

```python
import pytest
from app.services.shap_e import get_shap_e_service, ShapEAPIError

@pytest.mark.asyncio
async def test_shap_e_service_initialization():
    """Test Shap-E service initializes correctly."""
    service = get_shap_e_service()
    assert service is not None
    assert service.model == "shap-e"

@pytest.mark.asyncio
async def test_shap_e_simple_cube():
    """Test Shap-E generates simple cube."""
    service = get_shap_e_service()

    if not service.enabled:
        pytest.skip("Shap-E not enabled")

    glb_bytes = await service.generate_from_text("a simple cube")

    assert len(glb_bytes) > 0
    assert glb_bytes[:4] == b"glTF"  # GLB magic number

@pytest.mark.asyncio
async def test_shap_e_organic_dragon():
    """Test Shap-E generates organic dragon."""
    service = get_shap_e_service()

    if not service.enabled:
        pytest.skip("Shap-E not enabled")

    glb_bytes = await service.generate_from_text("a detailed dragon statue")

    # Verify mesh
    mesh = trimesh.load(BytesIO(glb_bytes), file_type="glb")
    assert len(mesh.vertices) > 1000  # Reasonable complexity
    assert len(mesh.faces) > 500

@pytest.mark.asyncio
async def test_shap_e_prompt_optimization():
    """Test prompt optimization improves prompts."""
    service = get_shap_e_service()

    optimized = service._optimize_prompt("dragon")

    assert "3d" in optimized.lower() or "model" in optimized.lower()
    assert len(optimized) > len("dragon")

@pytest.mark.asyncio
async def test_shap_e_batch_generation():
    """Test batch generation works correctly."""
    service = get_shap_e_service()

    if not service.enabled:
        pytest.skip("Shap-E not enabled")

    prompts = ["cube", "sphere", "cylinder"]
    results = await service.generate_batch(prompts, max_concurrent=2)

    assert len(results) == 3
    assert all(len(r) > 0 for r in results if r is not None)

@pytest.mark.asyncio
async def test_shap_e_error_handling():
    """Test error handling for invalid prompts."""
    service = get_shap_e_service()

    if not service.enabled:
        pytest.skip("Shap-E not enabled")

    # Very long prompt (may fail)
    try:
        await service.generate_from_text("a" * 10000)
    except ShapEAPIError:
        pass  # Expected

@pytest.mark.asyncio
async def test_shap_e_guidance_scale():
    """Test different guidance scales work."""
    service = get_shap_e_service()

    if not service.enabled:
        pytest.skip("Shap-E not enabled")

    # Low guidance
    result1 = await service.generate_from_text("cube", guidance_scale=5.0)
    assert len(result1) > 0

    # High guidance
    result2 = await service.generate_from_text("cube", guidance_scale=20.0)
    assert len(result2) > 0

@pytest.mark.asyncio
async def test_shap_e_retry_logic():
    """Test retry logic on API failures."""
    # Mock API to fail first 2 times
    # ... test implementation
    pass
```

### Integration Tests (5 tests)

**File**: `tests/test_shap_e_integration.py`

```python
@pytest.mark.asyncio
async def test_shap_e_to_step_conversion():
    """Test GLB → STEP conversion."""
    service = get_shap_e_service()

    if not service.enabled:
        pytest.skip("Shap-E not enabled")

    glb_bytes = await service.generate_from_text("cube")

    # Convert to STEP
    from app.services.mesh_converter import convert_mesh
    step_bytes = convert_mesh(glb_bytes, "glb", "step")

    assert len(step_bytes) > 0
    assert b"ISO-10303-21" in step_bytes  # STEP header

@pytest.mark.asyncio
async def test_shap_e_with_mesh_processing():
    """Test Shap-E + mesh processing pipeline."""
    service = get_shap_e_service()

    if not service.enabled:
        pytest.skip("Shap-E not enabled")

    glb_bytes = await service.generate_from_text("dragon")

    # Process mesh
    from app.services.mesh_processor import process_mesh
    processed, quality = await process_mesh(glb_bytes)

    assert quality.overall_score >= 5.0
    assert quality.face_count <= 100000

# ... 3 more integration tests
```

---

## Phase 2: TripoSR Tests

### Unit Tests (6 tests)

**File**: `tests/test_triposr_service.py`

```python
@pytest.mark.asyncio
async def test_triposr_initialization():
    """Test TripoSR service initializes."""
    service = get_triposr_service()
    assert service is not None
    assert service.model is not None

@pytest.mark.asyncio
async def test_triposr_simple_object():
    """Test TripoSR generates from simple object image."""
    service = get_triposr_service()

    test_image = "tests/fixtures/cube_image.jpg"
    obj_bytes = await service.generate_from_image(
        test_image,
        mc_resolution=128  # Fast test
    )

    assert len(obj_bytes) > 0

    # Verify mesh
    mesh = trimesh.load(BytesIO(obj_bytes), file_type="obj")
    assert len(mesh.vertices) > 100
    assert len(mesh.faces) > 100

# ... 4 more tests
```

---

## Phase 3: Routing Tests

### Unit Tests (10 tests)

**File**: `tests/test_routing.py`

```python
from app.services.routing import get_routing_service, ObjectCategory

def test_route_engineering_cup():
    """Test cup with dimensions routes to parametric."""
    routing = get_routing_service()
    decision = routing.route("Coffee cup, 90mm tall, 75mm diameter")

    assert decision.pipeline == "parametric"
    assert decision.object_category == ObjectCategory.ENGINEERING
    assert decision.confidence >= 0.85

def test_route_organic_dragon():
    """Test dragon routes to AI."""
    routing = get_routing_service()
    decision = routing.route("A realistic dragon statue")

    assert decision.pipeline == "ai"
    assert decision.object_category == ObjectCategory.ORGANIC
    assert decision.confidence >= 0.80

def test_route_architectural_room():
    """Test room routes to parametric."""
    routing = get_routing_service()
    decision = routing.route("A 6x4 meter bedroom")

    assert decision.pipeline == "parametric"
    assert decision.object_category == ObjectCategory.ARCHITECTURAL
    assert decision.confidence >= 0.90

def test_route_hybrid_decorated_cup():
    """Test decorated cup routes to hybrid."""
    routing = get_routing_service()
    decision = routing.route("Coffee mug with dragon carved on it")

    assert decision.pipeline == "hybrid"
    assert decision.object_category == ObjectCategory.MIXED

def test_dimension_extraction():
    """Test dimension extraction works."""
    routing = get_routing_service()
    analysis = routing.analyze_prompt("A cup, 90mm tall, 75mm diameter")

    assert analysis.dimensions_specified
    assert 90 in analysis.dimension_values
    assert 75 in analysis.dimension_values

# ... 5 more tests
```

---

## Phase 4: Mesh Processing Tests

### Unit Tests (15 tests)

**File**: `tests/test_mesh_processor.py`

```python
@pytest.mark.asyncio
async def test_mesh_cleanup():
    """Test mesh cleanup removes artifacts."""
    # Create mesh with duplicates
    vertices = np.array([
        [0, 0, 0],
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 0],  # Duplicate
    ])
    faces = np.array([[0, 1, 2]])
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    processor = get_mesh_processor()
    cleaned = processor._cleanup_mesh(mesh)

    assert len(cleaned.vertices) == 3  # Duplicate removed

@pytest.mark.asyncio
async def test_mesh_decimation():
    """Test mesh decimation reduces faces."""
    # Create high-poly sphere
    mesh = trimesh.creation.icosphere(subdivisions=5)
    initial_faces = len(mesh.faces)

    processor = get_mesh_processor()
    decimated = processor._decimate_mesh(mesh, target_faces=500)

    assert len(decimated.faces) <= 500
    assert len(decimated.faces) < initial_faces

@pytest.mark.asyncio
async def test_quality_calculation():
    """Test quality metrics calculation."""
    # Perfect cube
    mesh = trimesh.creation.box()

    processor = get_mesh_processor()
    quality = processor._calculate_quality(mesh)

    assert quality.is_watertight
    assert quality.overall_score >= 8.0
    assert not quality.needs_repair

# ... 12 more tests
```

---

## Phase 5: End-to-End Tests

### E2E Test Suite (13 tests)

**File**: `tests/test_e2e_any_object.py`

```python
@pytest.mark.asyncio
async def test_e2e_parametric_cup():
    """Test end-to-end: prompt → parametric → files."""
    prompt = "A coffee cup, 90mm tall, hollow with 3mm walls"

    # Run through full pipeline
    result = await run_pipeline(prompt, pipeline_type="parametric")

    assert result["status"] == "completed"
    assert result["mesh_step"] is not None
    assert result["mesh_dxf"] is not None
    assert result["quality_score"] >= 8.0

@pytest.mark.asyncio
async def test_e2e_ai_dragon():
    """Test end-to-end: prompt → AI → files."""
    prompt = "A detailed dragon statue"

    result = await run_pipeline(prompt, pipeline_type="ai")

    assert result["status"] == "completed"
    assert result["mesh_glb"] is not None
    assert result["quality_score"] >= 7.0

@pytest.mark.asyncio
async def test_e2e_hybrid_decorated_cup():
    """Test end-to-end: prompt → hybrid → files."""
    prompt = "Coffee mug with dragon decoration"

    result = await run_pipeline(prompt, pipeline_type="hybrid")

    assert result["status"] == "completed"
    assert result["mesh_glb"] is not None
    assert "hybrid" in result["metadata"]["pipeline"]

@pytest.mark.asyncio
async def test_e2e_image_to_3d():
    """Test end-to-end: image → 3D → files."""
    image_path = "tests/fixtures/chair.jpg"

    result = await run_image_pipeline(image_path)

    assert result["status"] == "completed"
    assert result["mesh_glb"] is not None

@pytest.mark.asyncio
async def test_e2e_routing_automatic():
    """Test automatic routing selects correct pipeline."""
    prompts = [
        ("Coffee cup, 90mm tall", "parametric"),
        ("A dragon statue", "ai"),
        ("Cup with dragon", "hybrid"),
        ("6x4 meter room", "parametric"),
    ]

    for prompt, expected_pipeline in prompts:
        result = await run_pipeline_with_routing(prompt)
        assert result["pipeline_used"] == expected_pipeline

# ... 8 more E2E tests
```

---

## Performance Tests

### Load Testing

**File**: `tests/test_performance.py`

```python
@pytest.mark.performance
async def test_concurrent_generations():
    """Test system handles 10 concurrent generations."""
    prompts = [f"object_{i}" for i in range(10)]

    start = time.time()
    results = await asyncio.gather(*[
        run_pipeline(p) for p in prompts
    ])
    duration = time.time() - start

    assert all(r["status"] == "completed" for r in results)
    assert duration < 600  # 10 minutes for 10 objects

@pytest.mark.performance
async def test_response_time_parametric():
    """Test parametric pipeline response time."""
    start = time.time()
    result = await run_pipeline("cup, 90mm tall", "parametric")
    duration = time.time() - start

    assert duration < 15  # < 15 seconds

@pytest.mark.performance
async def test_response_time_ai():
    """Test AI pipeline response time."""
    start = time.time()
    result = await run_pipeline("dragon", "ai")
    duration = time.time() - start

    assert duration < 60  # < 60 seconds
```

---

## Manual Test Checklist

### Phase 1 Manual Tests
- [ ] Generate 10 diverse objects via Shap-E
- [ ] Verify all generate valid GLB files
- [ ] Check quality scores are reasonable (7+/10)
- [ ] Validate STEP conversion works
- [ ] Test error handling with bad prompts

### Phase 2 Manual Tests
- [ ] Upload 5 different object images
- [ ] Verify TripoSR generates reasonable meshes
- [ ] Check background removal works
- [ ] Test multi-view reconstruction (if implemented)

### Phase 3 Manual Tests
- [ ] Test 20 diverse prompts
- [ ] Verify routing makes correct decisions
- [ ] Check confidence scores are reasonable
- [ ] Test override mechanism

### Phase 4 Manual Tests
- [ ] Inspect 10 generated meshes in CAD software
- [ ] Verify no visual artifacts
- [ ] Check dimensions are correct
- [ ] Test exports in multiple formats

### Phase 5 Manual Tests
- [ ] Generate 5 complex hybrid objects
- [ ] Verify parametric + AI combination works
- [ ] Check boolean operations succeed
- [ ] Test dimension scaling accuracy

---

## Acceptance Criteria

### Quality Standards
- [ ] 95%+ test pass rate
- [ ] Average quality score: 8.0+/10
- [ ] Generation success rate: 95%+
- [ ] Zero critical bugs

### Performance Standards
- [ ] Parametric: <15s average
- [ ] AI: <60s average
- [ ] Hybrid: <120s average
- [ ] Concurrent: 10+ requests

### User Acceptance
- [ ] 100+ example prompts documented
- [ ] User satisfaction: 4.5/5+
- [ ] Feature usage: 80%+ try AI generation

---

## Test Execution Schedule

| Week | Phase | Tests to Run | Expected Coverage |
|------|-------|--------------|-------------------|
| 1 | Shap-E Integration | Unit + Integration | 80%+ |
| 2 | Routing | Unit + Integration | 90%+ |
| 3 | TripoSR | Unit + Integration | 85%+ |
| 4 | Mesh Processing | Unit | 95%+ |
| 5 | Hybrid Pipeline | Integration + E2E | 85%+ |
| 6 | Quality Validation | All types | 90%+ |
| 7 | Full E2E | All E2E + Manual | 95%+ |
| 8 | Production Testing | Load + Performance | 100% |

---

## Bug Tracking

### Severity Levels
- **Critical**: System crash, data loss, security issue
- **High**: Major feature broken, incorrect results
- **Medium**: Minor feature issue, degraded performance
- **Low**: UI issue, documentation error

### Bug Template
```
**Title**: [Component] Brief description

**Severity**: Critical | High | Medium | Low

**Steps to Reproduce**:
1. ...
2. ...
3. ...

**Expected**: ...
**Actual**: ...

**Environment**: Python version, OS, GPU/CPU

**Logs**: [attach relevant logs]
```

---

## Continuous Integration

### CI Pipeline
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.13
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: pytest tests/ -m "not performance"
      - name: Run integration tests
        run: pytest tests/test_*_integration.py
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## Test Reporting

### Metrics to Track
- Test pass rate (%)
- Code coverage (%)
- Average response times
- Quality score distribution
- API cost per test run
- Failure rate by component

### Weekly Test Report Template
```
## Week N Test Report

**Overall Status**: 🟢 Green | 🟡 Yellow | 🔴 Red

**Test Results**:
- Unit tests: X/Y passed (Z%)
- Integration tests: X/Y passed (Z%)
- E2E tests: X/Y passed (Z%)

**Quality Metrics**:
- Average quality score: X.X/10
- Objects generated: X
- Success rate: X%

**Performance**:
- Average response time: Xs
- P95 response time: Xs

**Issues**:
- Critical: X
- High: X
- Medium: X
- Low: X

**Next Week Focus**:
- ...
```

---

**Testing Plan Status**: 📋 **Complete**
**Total Tests**: 130 tests planned
**Target Coverage**: 95%+
