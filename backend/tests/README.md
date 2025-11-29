# CADLift Test Suite

This folder contains all test files for the CADLift backend.

## Running Tests

### Run All Phase 2 Tests
```bash
cd /home/muhammed/İndirilenler/cadlift/backend
python tests/test_phase2_improvements.py  # Phase 2.1 & 2.2
python tests/test_phase2_3_prompt.py       # Phase 2.3
```

### Run Individual Test Suites

**Phase 1 Tests:**
```bash
python tests/test_cadquery.py                       # cadquery library validation
python tests/test_build123d.py                      # build123d library validation
python tests/test_geometry_integration.py           # STEP generation integration
python tests/test_dxf_improved.py                   # DXF POLYFACE mesh generation
python tests/test_wall_thickness_experiments.py     # Wall thickness approaches
python tests/test_wall_thickness.py                 # Wall thickness integration
```

**Phase 2 Tests:**
```bash
python tests/test_phase2_improvements.py   # CAD (CIRCLE/ARC, layers) + Image (preprocessing, Douglas-Peucker)
python tests/test_phase2_3_prompt.py       # Prompt (position-based, custom polygons, LLM validation)
```

**Prompt-to-3D Improvement Tests:**
```bash
python tests/test_phase1_fixes.py          # Critical bug fixes (validation, logging, keywords)
python tests/test_phase2_features.py       # Tapered cylinders, realistic dimensions, LLM integration
python tests/test_phase5_complete.py       # Performance optimization, quality metrics
```

**Existing Tests:**
```bash
python tests/test_auth.py      # Authentication tests
python tests/test_health.py    # Health endpoint tests
python tests/test_jobs.py      # Job management tests
```

## Test Organization

### Phase 1 Tests (22 tests)
- **test_cadquery.py** (4 tests) - cadquery library evaluation
- **test_build123d.py** (4 tests) - build123d library evaluation
- **test_geometry_integration.py** (4 tests) - STEP generation
- **test_dxf_improved.py** (4 tests) - DXF POLYFACE mesh
- **test_wall_thickness_experiments.py** (4 tests) - Wall thickness experiments
- **test_wall_thickness.py** (6 tests) - Wall thickness integration

### Phase 2 Tests (10 tests)
- **test_phase2_improvements.py** (4 tests)
  - CIRCLE/ARC support (CAD pipeline)
  - Layer filtering (CAD pipeline)
  - Enhanced preprocessing (Image pipeline)
  - Douglas-Peucker simplification (Image pipeline)

- **test_phase2_3_prompt.py** (6 tests)
  - Simple rectangular rooms
  - Positioned L-shaped layouts
  - Custom polygon shapes
  - Mixed layouts
  - LLM response validation (9 sub-cases)
  - Cluster layouts

### Prompt-to-3D Improvement Tests (15 tests)
- **test_phase1_fixes.py** (3 tests)
  - Thread/revolve/sweep validation fixes
  - Object keyword detection
  - LLM service integration

- **test_phase2_features.py** (6 tests)
  - Tapered cylinder validation
  - Tapered cylinder model generation
  - LLM coffee cup generation
  - Coffee cup with handle
  - Water bottle generation
  - Dimension validation

- **test_phase5_complete.py** (6 tests)
  - Segment optimization
  - Quality metrics for shapes
  - Quality metrics for rooms
  - Shape type distribution
  - Segment count bounds
  - Polygon/vertex counting

### Integration Tests
- **test_auth.py** - User authentication
- **test_health.py** - API health checks
- **test_jobs.py** - Job lifecycle

## Test Results

**Current Status:**
```
Phase 1 Tests:                 22/22 PASSED ✅
Phase 2 Tests:                 10/10 PASSED ✅
Prompt-to-3D Improvements:     15/15 PASSED ✅
Total:                         47/47 PASSED ✅ (100% success rate)
```

## Test Outputs

Test artifacts are stored in `test_outputs/` directory:
- `test_outputs/*.step` - Phase 1 library evaluation files
- `test_outputs/integration/*.step` - Integration test files
- `test_outputs/dxf_improved/*.dxf` - DXF test files
- `test_outputs/wall_thickness/*.step` - Wall thickness test files

## Test Requirements

**Dependencies:**
```bash
pip install pytest cadquery>=2.6 ezdxf>=1.3 opencv-python numpy
```

**Python Version:** 3.13+ (current environment)

## Adding New Tests

When adding new tests:
1. Create test file: `test_<feature_name>.py`
2. Follow naming convention: `test_<what_is_being_tested>()`
3. Include docstrings explaining what is tested
4. Add print statements for progress tracking
5. Return `True` for pass, `False` for fail
6. Update this README with test count

## Continuous Integration

For CI/CD pipelines, run:
```bash
# Run all Phase 2 tests
python tests/test_phase2_improvements.py && python tests/test_phase2_3_prompt.py
```

Expected output: `ALL TESTS PASSED (10/10)`

---

**Last Updated:** 2025-11-27
**Total Tests:** 47/47 passing
**Status:** ✅ All tests green
