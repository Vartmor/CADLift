# Prompt-to-3D Realism Improvement Plan

## Executive Summary
This plan addresses critical bugs and implements enhancements to make the prompt-to-3D feature generate highly realistic, production-quality 3D models from natural language descriptions.

**Current Status**: The pipeline has solid architecture but suffers from a critical validation bug that blocks advanced geometry, no support for tapered shapes, and silent error handling that hides failures.

**Goal**: Enable users to generate realistic objects (mugs, bottles, tools, parts) with accurate geometry including tapers, curves, threads, and complex features.

---

## Critical Issues Identified

### 🔴 Issue #1: LLM Validation Bug (BLOCKING)
**Location**: `backend/app/services/llm.py:154`

**Problem**:
- LLM system prompt (line 206-207) tells GPT-4 it can generate `thread`, `revolve`, `sweep` shapes
- But validation only allows: `{"box", "cylinder", "polygon"}`
- Result: LLM generates sophisticated shapes → validation rejects them → retry loop → fallback to basic shapes

**Impact**: HIGH - Blocks all advanced geometry generation

**Fix Complexity**: TRIVIAL (1 line change)

---

### 🟡 Issue #2: No Taper Support (FEATURE GAP)
**Location**: `backend/app/pipelines/prompt.py:159`

**Problem**:
```python
obj = wp.circle(r).extrude(h)  # Always straight cylinder
```
- Coffee cups, vases, funnels need tapered cylinders
- Current code only creates straight extrusions
- CadQuery supports `loft()` for tapers (confirmed in venv)

**Impact**: MEDIUM - Realistic objects impossible

**Fix Complexity**: MEDIUM (new shape type + LLM prompt update)

---

### 🟡 Issue #3: Silent Error Handling (DEBUGGING NIGHTMARE)
**Location**: `backend/app/pipelines/prompt.py:215, 222`

**Problem**:
```python
try:
    obj = obj.shell(-w_thick)
except Exception:
    pass  # Silently falls back to solid!
```
- Users don't know when hollow/fillet operations fail
- Makes debugging impossible
- Violates the error handling patterns in `errors.py`

**Impact**: MEDIUM - Poor user experience, hard to debug

**Fix Complexity**: EASY (add logging + optional warnings)

---

### 🟢 Issue #4: LLM Prompt Quality (ACCURACY)
**Location**: `backend/app/services/llm.py:185-220`

**Problem**:
- Generic examples don't guide realistic dimensions
- No guidance on handle attachments, curved features
- Missing examples for common objects (cups, bottles, containers)

**Impact**: LOW-MEDIUM - Affects output quality

**Fix Complexity**: EASY (prompt engineering)

---

## Implementation Plan

### Phase 1: Critical Bug Fixes (30 mins)
**Priority**: IMMEDIATE - These are blocking all advanced features

#### Task 1.1: Fix LLM Validation Bug
**File**: `backend/app/services/llm.py`

**Changes**:
```python
# Line 154: Add missing shape types
allowed = {"box", "cylinder", "polygon", "thread", "revolve", "sweep"}
```

**Testing**:
- Prompt: "A screw with M6 thread"
- Expected: Should generate thread shape without retries

---

#### Task 1.2: Replace Silent Failures with Logging
**File**: `backend/app/pipelines/prompt.py`

**Changes**:
1. Line 215 (shell operation):
```python
if hollow and w_thick > 0 and stype not in {"thread"}:
    try:
        obj = obj.shell(-w_thick)
    except Exception as e:
        logger.warning(f"Shell operation failed for shape {idx} ({stype}): {e}. Falling back to solid.")
        # Continue with solid object
```

2. Line 222 (fillet operation):
```python
if fillet > 0 and stype not in {"thread"}:
    try:
        obj = obj.edges("|Z").fillet(fillet)
    except Exception as e:
        logger.warning(f"Fillet operation failed for shape {idx} ({stype}): {e}. Skipping fillet.")
        # Continue without fillet
```

3. Line 191 (thread fallback):
```python
except Exception as e:
    logger.warning(f"Thread generation failed for shape {idx}: {e}. Using cylinder approximation.")
    obj = wp.circle(major_r).extrude(length)
```

**Benefits**:
- Users see warnings in job logs
- Developers can debug failures
- Matches error handling patterns in rest of codebase

---

### Phase 2: Advanced Geometry Support (2 hours)

#### Task 2.1: Add Tapered Cylinder Support
**File**: `backend/app/pipelines/prompt.py`

**Approach**: Add new shape type `tapered_cylinder` using CadQuery's loft

**Implementation**:
```python
elif stype == "tapered_cylinder":
    top_radius = float(shape.get("top_radius", 0))
    bottom_radius = float(shape.get("bottom_radius", 0))
    h = float(shape.get("height", model.get("extrude_height", 100)))

    if top_radius <= 0 or bottom_radius <= 0 or h <= 0:
        raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED,
                          details=f"Invalid tapered_cylinder in shapes[{idx}]")

    # Create bottom and top circles
    bottom_circle = cq.Workplane("XY").circle(bottom_radius)
    top_circle = cq.Workplane("XY").workplane(offset=h).circle(top_radius)

    # Loft between circles
    obj = cq.Workplane("XY").circle(bottom_radius).workplane(offset=h).circle(top_radius).loft()

    if pos_x or pos_y:
        obj = obj.translate((x_off, y_off, 0))
```

**Validation Update** (`llm.py:154`):
```python
allowed = {"box", "cylinder", "tapered_cylinder", "polygon", "thread", "revolve", "sweep"}
```

**LLM Prompt Update** (`llm.py:206`):
```python
"- Supported shapes: box(width,length,height),
   cylinder(radius,height),
   tapered_cylinder(bottom_radius,top_radius,height),
   polygon(vertices,height),
   thread(major_radius, pitch, turns, length),
   revolve(profile_vertices, angle_deg),
   sweep(profile_vertices, path_vertices)."
```

---

#### Task 2.2: Improve Handle/Curve Generation
**File**: `backend/app/services/llm.py`

**Add Example to System Prompt** (line 217):
```python
"Prompt: \"Coffee cup with handle\" -> {
  \"shapes\": [
    {\"type\":\"tapered_cylinder\",\"bottom_radius\":60,\"top_radius\":75,\"height\":90,\"hollow\":true,\"wall_thickness\":3},
    {\"type\":\"sweep\",\"profile\":[[0,0],[4,0],[4,10],[0,10]],\"path\":[[75,0,20],[85,0,20],[85,0,50],[75,0,70]],\"operation\":\"union\"}
  ]
}"
```

**Benefits**:
- LLM learns to generate handles as sweep operations
- Realistic curved attachments

---

### Phase 3: LLM Prompt Engineering (1 hour)

#### Task 3.1: Enhanced System Prompt
**File**: `backend/app/services/llm.py:185-220`

**Add Realistic Dimension Guidance**:
```python
"Dimension Guidelines:
- Coffee cup: 70-90mm diameter, 80-120mm tall, 2-4mm wall thickness
- Water bottle: 60-80mm diameter, 180-250mm tall, 1-3mm wall thickness
- Mug: 80-100mm diameter, 90-110mm tall, 3-5mm wall thickness
- Screw: 3-10mm diameter, 10-50mm length, M3-M10 thread pitch
- Power adapter: 40-80mm body, 10-30mm plug
- Handle dimensions: 3-6mm thick, attach at 70-80% of body radius"
```

**Add More Examples**:
```python
"Examples:
Prompt: \"6x4m room\" -> {\"rooms\":[{\"name\":\"main\",\"width\":6000,\"length\":4000}],\"extrude_height\":3000,\"wall_thickness\":200}

Prompt: \"A realistic coffee mug\" -> {
  \"shapes\":[
    {\"type\":\"tapered_cylinder\",\"bottom_radius\":70,\"top_radius\":80,\"height\":100,\"hollow\":true,\"wall_thickness\":4,\"fillet\":2},
    {\"type\":\"sweep\",\"profile\":[[0,0],[5,0],[5,12],[0,12]],\"path\":[[80,0,25],[95,0,25],[95,0,65],[80,0,75]]}
  ],
  \"extrude_height\":100,\"wall_thickness\":4
}

Prompt: \"Water bottle with threaded cap\" -> {
  \"shapes\":[
    {\"type\":\"tapered_cylinder\",\"bottom_radius\":62,\"top_radius\":65,\"height\":200,\"hollow\":true,\"wall_thickness\":2},
    {\"type\":\"thread\",\"major_radius\":14,\"pitch\":2,\"turns\":8,\"length\":20,\"position\":[0,0,200]}
  ]
}

Prompt: \"M6 screw, 30mm long\" -> {
  \"shapes\":[
    {\"type\":\"thread\",\"major_radius\":3,\"pitch\":1,\"turns\":25,\"length\":25},
    {\"type\":\"cylinder\",\"radius\":5,\"height\":3,\"position\":[0,0,25]},
    {\"type\":\"cylinder\",\"radius\":1.5,\"height\":5,\"position\":[0,0,28]}
  ]
}

Prompt: \"Power adapter\" -> {
  \"shapes\":[
    {\"type\":\"box\",\"width\":60,\"length\":80,\"height\":40,\"hollow\":false,\"fillet\":5},
    {\"type\":\"box\",\"width\":15,\"length\":25,\"height\":10,\"position\":[0,80],\"operation\":\"union\"}
  ]
}"
```

---

#### Task 3.2: Better Object Detection Heuristics
**File**: `backend/app/pipelines/prompt.py:579-583`

**Expand Keywords**:
```python
building_keywords = [
    "house", "room", "floor", "plan", "apartment", "office", "building",
    "layout", "villa", "kitchen", "bathroom", "living", "bedroom",
    "duvar", "kat", "plan", "oda", "daire",  # Turkish
    "corridor", "hallway", "garage", "basement", "attic", "warehouse"
]

object_keywords = [
    "mug", "cup", "bottle", "container", "glass", "jar",
    "screw", "bolt", "nut", "washer", "fastener",
    "adapter", "plug", "connector", "cable",
    "tool", "wrench", "hammer", "part", "component",
    "vase", "pot", "bowl", "plate"
]

is_object = any(word in prompt_lower for word in object_keywords)
if has_rooms and not has_shapes and not is_building and is_object:
    raise CADLiftError(ErrorCode.PROMPT_VALIDATION_FAILED,
                      details="Object prompt incorrectly parsed as building. Try more specific description.")
```

---

### Phase 4: Testing & Validation (1 hour)

#### Task 4.1: Create Test Cases
**File**: `backend/tests/test_prompt_pipeline.py` (NEW)

**Test Suite**:
```python
import pytest
from app.pipelines import prompt
from app.services.llm import llm_service

@pytest.mark.asyncio
async def test_tapered_cylinder_validation():
    """Test that tapered_cylinder shapes are accepted"""
    instructions = {
        "shapes": [
            {
                "type": "tapered_cylinder",
                "bottom_radius": 60,
                "top_radius": 75,
                "height": 100
            }
        ]
    }
    # Should not raise
    prompt._validate_instruction_schema(instructions)

@pytest.mark.asyncio
async def test_thread_validation():
    """Test that thread shapes are accepted"""
    instructions = {
        "shapes": [
            {
                "type": "thread",
                "major_radius": 5,
                "pitch": 1.5,
                "turns": 20,
                "length": 30
            }
        ]
    }
    # Should not raise
    prompt._validate_instruction_schema(instructions)

@pytest.mark.asyncio
async def test_coffee_cup_prompt():
    """End-to-end test for coffee cup generation"""
    if not llm_service.enabled:
        pytest.skip("LLM service not enabled")

    prompt_text = "A realistic coffee cup, 90mm tall, 75mm diameter"
    instructions = await llm_service.generate_instructions(prompt_text)

    # Should have shapes
    assert "shapes" in instructions
    assert len(instructions["shapes"]) >= 1

    # Should be hollow
    assert any(s.get("hollow") for s in instructions["shapes"])
```

#### Task 4.2: Manual Testing Prompts
**Create**: `backend/test_prompts.md`

```markdown
# Test Prompts for Validation

## Simple Objects (Should Work Now)
1. "A simple cylinder, 100mm tall, 50mm diameter"
2. "A box, 80mm x 60mm x 40mm"
3. "A hollow cylinder, 3mm wall thickness"

## Advanced Objects (After Phase 2)
4. "Coffee cup with handle, 90mm tall"
5. "Water bottle, 200mm tall with threaded neck"
6. "Tapered vase, narrow at bottom, wide at top"
7. "M6 screw, 30mm long"

## Complex Objects (Stretch Goals)
8. "Power adapter with plug attachment"
9. "Wrench with hexagonal opening"
10. "Threaded jar with lid"

## Buildings (Should Still Work)
11. "A 6x4 meter room"
12. "2 bedroom apartment, 10x8 meters"
```

---

### Phase 5: Performance & Polish (30 mins)

#### Task 5.1: Optimize Segment Count Based on Detail
**File**: `backend/app/pipelines/prompt.py:130`

**Current**:
```python
segments = int(16 + detail * 1.2)  # 24-160 segments
```

**Improved**:
```python
# Adjust segments based on shape type and detail
def get_optimal_segments(shape_type: str, detail: float) -> int:
    """Calculate optimal segment count for smooth curves"""
    base_segments = {
        "cylinder": 24,
        "tapered_cylinder": 32,
        "thread": 48,
        "revolve": 32
    }
    base = base_segments.get(shape_type, 24)
    multiplier = 1 + (detail / 100)  # 1.0 to 2.0
    return min(160, max(16, int(base * multiplier)))
```

#### Task 5.2: Add Quality Metrics to Output
**File**: `backend/app/pipelines/prompt.py:100`

**Add Metadata**:
```python
merged_params["quality_metrics"] = {
    "shapes_generated": len(instructions.get("shapes", [])),
    "advanced_features_used": {
        "tapered": any(s.get("type") == "tapered_cylinder" for s in instructions.get("shapes", [])),
        "threaded": any(s.get("type") == "thread" for s in instructions.get("shapes", [])),
        "hollow": any(s.get("hollow") for s in instructions.get("shapes", [])),
        "filleted": any(s.get("fillet", 0) > 0 for s in instructions.get("shapes", []))
    },
    "detail_level": detail,
    "llm_retries": 0  # Track if LLM needed retries
}
```

---

## Implementation Timeline

### Day 1 - Critical Fixes
- **Morning** (2 hours):
  - Task 1.1: Fix validation bug ✅
  - Task 1.2: Add logging ✅
  - Task 3.2: Improve keywords ✅
  - **Test with simple prompts**

- **Afternoon** (2 hours):
  - Task 3.1: Enhanced LLM prompt ✅
  - Task 4.2: Manual testing ✅
  - **Deploy and test in production**

### Day 2 - Advanced Features
- **Morning** (3 hours):
  - Task 2.1: Tapered cylinder support ✅
  - Update validation & LLM prompts ✅
  - **Test coffee cup prompt**

- **Afternoon** (2 hours):
  - Task 2.2: Handle generation examples ✅
  - Task 4.1: Automated tests ✅
  - Task 5.1-5.2: Performance polish ✅

---

## Success Criteria

### Phase 1 (Critical Fixes)
- ✅ Thread/revolve/sweep shapes pass validation
- ✅ No more silent failures in logs
- ✅ Simple object prompts work (cylinder, box)

### Phase 2 (Advanced Geometry)
- ✅ Coffee cup prompt generates tapered body + handle
- ✅ Water bottle prompt generates threaded neck
- ✅ All shapes render correctly in STEP viewer

### Phase 3 (Quality)
- ✅ 90%+ of object prompts generate correct shape type (not buildings)
- ✅ Realistic dimensions (cup is cup-sized, not building-sized)
- ✅ Handles and attachments positioned correctly

### Phase 4 (Production Ready)
- ✅ All automated tests pass
- ✅ 10+ manual test prompts validated
- ✅ Quality metrics in job output

---

## Risk Mitigation

### Risk 1: CadQuery Loft Complexity
**Mitigation**: If loft fails, fallback to straight cylinder with warning

### Risk 2: LLM Generates Invalid Dimensions
**Mitigation**: Add dimension validation in `_validate_instruction_schema`

### Risk 3: Breaking Existing Building Prompts
**Mitigation**: Run full test suite before merging, keep building keywords comprehensive

---

## Future Enhancements (Out of Scope)

1. **Custom material properties** (PBR textures, colors)
2. **Multi-part assemblies** (lids, caps, hinges)
3. **Parametric constraints** ("make handle proportional to body")
4. **AI-powered dimension correction** (fix unrealistic sizes automatically)
5. **Style transfer** ("make it look modern/vintage/industrial")

---

## Questions for User

Before implementation, please clarify:

1. **LLM Provider**: Is OpenAI API key configured in `.env`? (Required for testing advanced prompts)

2. **Testing Approach**: Should I test after each phase, or complete all phases then test?

3. **Backward Compatibility**: Are there any existing production prompts/jobs we need to ensure still work?

4. **Priority**: If time is limited, should I focus on:
   - A) Critical bug fixes only (Phase 1)
   - B) Critical fixes + tapered cylinders (Phase 1-2)
   - C) Full implementation (All phases)

5. **Deployment**: Should I create a feature branch or work directly on main?

---

## File Modification Summary

### Files to Modify
1. `backend/app/services/llm.py` - Fix validation, improve prompts
2. `backend/app/pipelines/prompt.py` - Add tapered cylinders, logging
3. `backend/app/core/errors.py` - Add new error codes (if needed)

### Files to Create
1. `backend/tests/test_prompt_pipeline.py` - Automated tests
2. `backend/test_prompts.md` - Manual test cases
3. `backend/docs/PROMPT_EXAMPLES.md` - User documentation

### Total Estimated Changes
- **Lines modified**: ~200
- **Lines added**: ~400
- **Files modified**: 3
- **Files created**: 3
- **Tests added**: 10+

---

**Plan Status**: READY FOR APPROVAL

Please review and let me know:
1. Any concerns or modifications needed
2. Which priority level to target (A/B/C above)
3. If I should proceed with implementation

Once approved, I'll begin with Phase 1 (Critical Fixes) immediately.
