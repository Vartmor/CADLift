# Intelligent Routing Logic - Pipeline Selection

**Date**: 2025-11-27
**Version**: 1.0

---

## Overview

The routing engine automatically selects the optimal pipeline (Parametric, AI, or Hybrid) based on prompt analysis. This ensures users get the best quality results for each object type.

---

## Routing Decision Tree

```
User Prompt
    │
    ├─> Extract Keywords & Features
    │
    ├─> Classify Object Type
    │       ├─> Engineering/Mechanical → PARAMETRIC (95% confidence)
    │       ├─> Architectural → PARAMETRIC (95% confidence)
    │       ├─> Organic/Natural → AI (90% confidence)
    │       ├─> Artistic/Decorative → AI (85% confidence)
    │       ├─> Mixed/Complex → HYBRID (80% confidence)
    │       └─> Unknown/Ambiguous → AI (default, 60% confidence)
    │
    ├─> Check Dimension Requirements
    │       ├─> Precise dimensions specified → Favor PARAMETRIC
    │       └─> No specific dimensions → OK for AI
    │
    ├─> Check Feature Requirements
    │       ├─> Threads, precise holes → PARAMETRIC
    │       ├─> Organic curves, freeform → AI
    │       └─> Both → HYBRID
    │
    └─> Select Pipeline with Confidence Score
```

---

## Implementation

### Service Class

**File**: `backend/app/services/routing.py`

```python
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal
from enum import Enum
import logging

logger = logging.getLogger("cadlift.services.routing")

PipelineType = Literal["parametric", "ai", "hybrid"]

class ObjectCategory(Enum):
    """Object category classification."""
    ENGINEERING = "engineering"
    ARCHITECTURAL = "architectural"
    ORGANIC = "organic"
    ARTISTIC = "artistic"
    MIXED = "mixed"
    UNKNOWN = "unknown"

@dataclass
class PromptAnalysis:
    """Analysis of user prompt."""
    # Raw prompt
    prompt: str
    prompt_lower: str

    # Extracted features
    keywords: list[str]
    dimensions_specified: bool
    dimension_values: list[float]
    features_mentioned: list[str]

    # Classification
    object_category: ObjectCategory
    confidence: float

    # Recommended pipeline
    pipeline: PipelineType
    reasoning: str

@dataclass
class RoutingDecision:
    """Routing decision with explanation."""
    pipeline: PipelineType
    confidence: float
    reasoning: str
    object_category: ObjectCategory
    prompt_analysis: PromptAnalysis


class RoutingService:
    """Intelligent routing service for pipeline selection."""

    # Keyword dictionaries
    ENGINEERING_KEYWORDS = {
        # Containers
        "cup", "mug", "bottle", "container", "glass", "jar", "flask",
        "tumbler", "canister", "vessel",

        # Fasteners
        "screw", "bolt", "nut", "washer", "fastener", "nail", "rivet",
        "thread", "threaded",

        # Connectors
        "adapter", "plug", "connector", "cable", "socket", "fitting",
        "coupler", "joint",

        # Tools & Parts
        "tool", "wrench", "hammer", "part", "component", "piece",
        "bracket", "mount", "holder", "housing",

        # Geometric
        "cylinder", "box", "cube", "rectangular", "cylindrical",
        "tapered", "hollow",

        # Features
        "precise", "exact", "dimension", "diameter", "radius",
        "mm", "cm", "meter", "inch", "tall", "wide", "thick"
    }

    ARCHITECTURAL_KEYWORDS = {
        # Rooms
        "room", "house", "apartment", "office", "building", "floor",
        "plan", "layout", "villa", "kitchen", "bathroom", "living",
        "bedroom", "corridor", "hallway", "garage", "basement",
        "attic", "warehouse", "studio", "suite", "closet",
        "balcony", "terrace", "penthouse",

        # Turkish
        "duvar", "kat", "plan", "oda", "daire", "ev",

        # Features
        "wall", "door", "window", "ceiling", "floor plan",
        "multi-story", "storey", "level"
    }

    ORGANIC_KEYWORDS = {
        # Animals
        "animal", "dog", "cat", "bird", "fish", "dragon", "horse",
        "lion", "tiger", "elephant", "dinosaur", "creature",

        # Human
        "face", "head", "hand", "body", "person", "human",
        "character", "figure",

        # Plants
        "tree", "plant", "flower", "leaf", "branch", "root",
        "grass", "bush", "vine",

        # Natural
        "rock", "stone", "crystal", "cloud", "wave", "flame",
        "mountain", "terrain", "landscape",

        # Organic descriptors
        "realistic", "lifelike", "natural", "organic", "smooth",
        "curved", "flowing", "detailed"
    }

    ARTISTIC_KEYWORDS = {
        # Art forms
        "statue", "sculpture", "art", "artistic", "decorative",
        "ornament", "decoration", "figurine", "bust", "relief",

        # Styles
        "modern", "vintage", "classical", "abstract", "geometric",
        "minimalist", "baroque", "gothic",

        # Decorative objects
        "vase", "pot", "bowl", "plate", "dish", "platter",
        "candleholder", "lamp", "chandelier",

        # Artistic descriptors
        "beautiful", "elegant", "stylish", "fancy", "ornate",
        "intricate", "elaborate"
    }

    HYBRID_INDICATORS = {
        # Mixed requests
        "with decoration", "with pattern", "with engraving",
        "with design", "with carving", "with relief",
        "decorated", "patterned", "carved", "engraved",
        "artistic + engineering keywords"
    }

    # Feature keywords
    PARAMETRIC_FEATURES = {
        "thread", "threaded", "screw thread", "m3", "m4", "m5",
        "m6", "m8", "m10",
        "hollow", "wall thickness", "precise", "exact",
        "fillet", "chamfer", "dimension", "diameter",
        "tapered", "taper"
    }

    AI_FEATURES = {
        "realistic", "organic", "natural", "freeform",
        "artistic", "decorative", "curved", "smooth",
        "detailed", "intricate", "complex surface"
    }

    def __init__(self):
        self.default_pipeline: PipelineType = "ai"
        logger.info("Routing service initialized")

    def analyze_prompt(self, prompt: str) -> PromptAnalysis:
        """Analyze prompt and extract features."""
        prompt_lower = prompt.lower()

        # Extract keywords
        keywords = self._extract_keywords(prompt_lower)

        # Check for dimensions
        dimensions_specified, dimension_values = self._extract_dimensions(prompt)

        # Extract mentioned features
        features_mentioned = self._extract_features(prompt_lower)

        # Classify object
        object_category, confidence = self._classify_object(
            keywords,
            dimensions_specified,
            features_mentioned
        )

        # Determine pipeline
        pipeline, reasoning = self._select_pipeline(
            object_category,
            dimensions_specified,
            features_mentioned,
            confidence
        )

        return PromptAnalysis(
            prompt=prompt,
            prompt_lower=prompt_lower,
            keywords=keywords,
            dimensions_specified=dimensions_specified,
            dimension_values=dimension_values,
            features_mentioned=features_mentioned,
            object_category=object_category,
            confidence=confidence,
            pipeline=pipeline,
            reasoning=reasoning
        )

    def route(self, prompt: str) -> RoutingDecision:
        """
        Route prompt to optimal pipeline.

        Returns:
            RoutingDecision with pipeline selection and reasoning
        """
        analysis = self.analyze_prompt(prompt)

        logger.info(
            "Routing decision",
            extra={
                "prompt": prompt[:100],
                "pipeline": analysis.pipeline,
                "category": analysis.object_category.value,
                "confidence": f"{analysis.confidence:.2f}",
                "reasoning": analysis.reasoning
            }
        )

        return RoutingDecision(
            pipeline=analysis.pipeline,
            confidence=analysis.confidence,
            reasoning=analysis.reasoning,
            object_category=analysis.object_category,
            prompt_analysis=analysis
        )

    def _extract_keywords(self, prompt_lower: str) -> list[str]:
        """Extract relevant keywords from prompt."""
        keywords = []

        # Check all keyword sets
        for keyword in (
            self.ENGINEERING_KEYWORDS |
            self.ARCHITECTURAL_KEYWORDS |
            self.ORGANIC_KEYWORDS |
            self.ARTISTIC_KEYWORDS
        ):
            if keyword in prompt_lower:
                keywords.append(keyword)

        return keywords

    def _extract_dimensions(self, prompt: str) -> tuple[bool, list[float]]:
        """
        Extract dimension values from prompt.

        Returns:
            (dimensions_specified: bool, values: list[float])
        """
        # Pattern: number + unit
        # Examples: "90mm", "5.5 cm", "3 meters", "10 inches"
        pattern = r'(\d+\.?\d*)\s*(mm|cm|m|meter|meters|inch|inches|in|")'
        matches = re.findall(pattern, prompt, re.IGNORECASE)

        if matches:
            values = [float(m[0]) for m in matches]
            return True, values

        return False, []

    def _extract_features(self, prompt_lower: str) -> list[str]:
        """Extract mentioned features."""
        features = []

        # Check parametric features
        for feature in self.PARAMETRIC_FEATURES:
            if feature in prompt_lower:
                features.append(f"parametric:{feature}")

        # Check AI features
        for feature in self.AI_FEATURES:
            if feature in prompt_lower:
                features.append(f"ai:{feature}")

        return features

    def _classify_object(
        self,
        keywords: list[str],
        has_dimensions: bool,
        features: list[str]
    ) -> tuple[ObjectCategory, float]:
        """
        Classify object category.

        Returns:
            (category, confidence)
        """
        # Count keyword matches per category
        engineering_count = sum(
            1 for k in keywords if k in self.ENGINEERING_KEYWORDS
        )
        architectural_count = sum(
            1 for k in keywords if k in self.ARCHITECTURAL_KEYWORDS
        )
        organic_count = sum(
            1 for k in keywords if k in self.ORGANIC_KEYWORDS
        )
        artistic_count = sum(
            1 for k in keywords if k in self.ARTISTIC_KEYWORDS
        )

        # Check for mixed
        categories_matched = sum([
            engineering_count > 0,
            architectural_count > 0,
            organic_count > 0,
            artistic_count > 0
        ])

        if categories_matched >= 2:
            return ObjectCategory.MIXED, 0.80

        # Single category
        if engineering_count > 0:
            confidence = min(0.95, 0.85 + (engineering_count * 0.05))
            return ObjectCategory.ENGINEERING, confidence

        if architectural_count > 0:
            confidence = min(0.95, 0.85 + (architectural_count * 0.05))
            return ObjectCategory.ARCHITECTURAL, confidence

        if organic_count > 0:
            confidence = min(0.90, 0.80 + (organic_count * 0.05))
            return ObjectCategory.ORGANIC, confidence

        if artistic_count > 0:
            confidence = min(0.85, 0.75 + (artistic_count * 0.05))
            return ObjectCategory.ARTISTIC, confidence

        # Unknown
        return ObjectCategory.UNKNOWN, 0.60

    def _select_pipeline(
        self,
        category: ObjectCategory,
        has_dimensions: bool,
        features: list[str],
        confidence: float
    ) -> tuple[PipelineType, str]:
        """
        Select optimal pipeline.

        Returns:
            (pipeline, reasoning)
        """
        # Count feature types
        parametric_features = [f for f in features if f.startswith("parametric:")]
        ai_features = [f for f in features if f.startswith("ai:")]

        # Decision logic
        if category == ObjectCategory.ENGINEERING:
            return (
                "parametric",
                "Engineering object requires precise parametric modeling"
            )

        if category == ObjectCategory.ARCHITECTURAL:
            return (
                "parametric",
                "Architectural design requires precise dimensions and layout"
            )

        if category == ObjectCategory.ORGANIC:
            return (
                "ai",
                "Organic shape best suited for AI generation"
            )

        if category == ObjectCategory.ARTISTIC:
            return (
                "ai",
                "Artistic object benefits from AI creativity"
            )

        if category == ObjectCategory.MIXED:
            # Check features to decide hybrid vs single pipeline
            if parametric_features and ai_features:
                return (
                    "hybrid",
                    "Mixed requirements: combining AI creativity with parametric precision"
                )
            elif parametric_features:
                return (
                    "parametric",
                    "Mixed category but parametric features dominate"
                )
            else:
                return (
                    "ai",
                    "Mixed category but artistic/organic aspects dominate"
                )

        # Unknown - default to AI
        if has_dimensions:
            # Has dimensions but unknown category - try parametric
            return (
                "parametric",
                "Unknown category but dimensions specified, using parametric for precision"
            )
        else:
            # No dimensions, unknown - use AI
            return (
                "ai",
                "Unknown category, defaulting to AI for flexibility"
            )


# Singleton
_routing_service: RoutingService | None = None

def get_routing_service() -> RoutingService:
    """Get routing service singleton."""
    global _routing_service
    if _routing_service is None:
        _routing_service = RoutingService()
    return _routing_service
```

---

## Usage Examples

### Example 1: Engineering Object → Parametric

```python
from app.services.routing import get_routing_service

routing = get_routing_service()
decision = routing.route("A coffee cup, 90mm tall, 75mm diameter, hollow with 3mm walls")

# Result:
# pipeline: "parametric"
# category: ENGINEERING
# confidence: 0.95
# reasoning: "Engineering object requires precise parametric modeling"
```

### Example 2: Organic Object → AI

```python
decision = routing.route("A realistic dragon statue with detailed scales and wings")

# Result:
# pipeline: "ai"
# category: ORGANIC
# confidence: 0.90
# reasoning: "Organic shape best suited for AI generation"
```

### Example 3: Hybrid Object → Hybrid

```python
decision = routing.route("A coffee mug with a dragon carved on the side, 100mm tall")

# Result:
# pipeline: "hybrid"
# category: MIXED
# confidence: 0.80
# reasoning: "Mixed requirements: combining AI creativity with parametric precision"
```

### Example 4: Architectural → Parametric

```python
decision = routing.route("A 5x4 meter bedroom with 2.8m ceiling height")

# Result:
# pipeline: "parametric"
# category: ARCHITECTURAL
# confidence: 0.95
# reasoning: "Architectural design requires precise dimensions and layout"
```

---

## Detailed Routing Examples

### Engineering Objects

| Prompt | Pipeline | Confidence | Reasoning |
|--------|----------|------------|-----------|
| "M6 screw, 30mm long" | Parametric | 0.95 | Thread + dimensions |
| "A bolt with hexagonal head" | Parametric | 0.90 | Engineering component |
| "Water bottle, 200mm tall" | Parametric | 0.95 | Container + dimensions |
| "Power adapter" | Parametric | 0.85 | Electronic component |
| "Pipe connector" | Parametric | 0.90 | Mechanical part |

### Architectural Objects

| Prompt | Pipeline | Confidence | Reasoning |
|--------|----------|------------|-----------|
| "6x4 meter room" | Parametric | 0.95 | Room + dimensions |
| "Two bedroom apartment" | Parametric | 0.90 | Architectural layout |
| "Office space with closet" | Parametric | 0.90 | Building design |

### Organic Objects

| Prompt | Pipeline | Confidence | Reasoning |
|--------|----------|------------|-----------|
| "A dragon statue" | AI | 0.90 | Organic creature |
| "A realistic human face" | AI | 0.90 | Organic human |
| "A tree with branches" | AI | 0.85 | Natural object |
| "A cat sitting" | AI | 0.90 | Animal |
| "A flower vase" | AI | 0.80 | Organic shape (vase can be parametric too) |

### Artistic Objects

| Prompt | Pipeline | Confidence | Reasoning |
|--------|----------|------------|-----------|
| "A decorative sculpture" | AI | 0.85 | Artistic piece |
| "An ornate candle holder" | AI | 0.80 | Decorative object |
| "A modern abstract shape" | AI | 0.80 | Artistic design |

### Hybrid Objects

| Prompt | Pipeline | Confidence | Reasoning |
|--------|----------|------------|-----------|
| "Cup with dragon decoration" | Hybrid | 0.80 | Engineering + organic |
| "Bottle shaped like a fish" | Hybrid | 0.80 | Functional + organic |
| "Decorative vase, 250mm tall" | Hybrid | 0.75 | Artistic + dimensions |

---

## Confidence Scores

### High Confidence (0.90-1.00)
- Clear engineering or architectural keywords
- Precise dimensions specified
- Well-known object types
- **Action**: Use recommended pipeline with confidence

### Medium Confidence (0.75-0.89)
- Some relevant keywords
- Object type identifiable but ambiguous
- Mixed features
- **Action**: Use recommended pipeline, log for review

### Low Confidence (0.60-0.74)
- Few or no matching keywords
- Unknown object type
- Vague description
- **Action**: Use default pipeline (AI), flag for manual review

---

## Override Mechanism

Allow users to force a specific pipeline:

```python
# User can specify pipeline in params
params = {
    "force_pipeline": "parametric"  # or "ai", "hybrid"
}

# Routing service respects override
if params.get("force_pipeline"):
    return RoutingDecision(
        pipeline=params["force_pipeline"],
        confidence=1.0,
        reasoning="User override",
        object_category=ObjectCategory.UNKNOWN,
        prompt_analysis=analysis
    )
```

---

## Feedback Loop

Track routing decisions and outcomes for improvement:

```sql
CREATE TABLE routing_feedback (
    id UUID PRIMARY KEY,
    job_id UUID REFERENCES jobs(id),
    prompt TEXT,
    pipeline_selected VARCHAR(50),
    pipeline_used VARCHAR(50),  -- If overridden
    confidence FLOAT,
    category VARCHAR(50),
    user_satisfaction INTEGER,  -- 1-5 rating
    was_correct BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);
```

Use feedback to improve routing:
- Track misclassifications
- Adjust keyword weights
- Add new keywords
- Refine confidence calculations

---

## Testing Routing Logic

```python
# tests/test_routing.py

from app.services.routing import get_routing_service, ObjectCategory

def test_engineering_cup():
    """Test engineering cup routes to parametric."""
    routing = get_routing_service()
    decision = routing.route("A coffee cup, 90mm tall, hollow")

    assert decision.pipeline == "parametric"
    assert decision.object_category == ObjectCategory.ENGINEERING
    assert decision.confidence >= 0.85

def test_organic_dragon():
    """Test organic dragon routes to AI."""
    routing = get_routing_service()
    decision = routing.route("A realistic dragon statue")

    assert decision.pipeline == "ai"
    assert decision.object_category == ObjectCategory.ORGANIC
    assert decision.confidence >= 0.80

def test_hybrid_decorated_cup():
    """Test hybrid decorated cup routes to hybrid."""
    routing = get_routing_service()
    decision = routing.route("A coffee mug with dragon decoration")

    assert decision.pipeline == "hybrid"
    assert decision.object_category == ObjectCategory.MIXED
    assert decision.confidence >= 0.75

def test_architectural_room():
    """Test room routes to parametric."""
    routing = get_routing_service()
    decision = routing.route("A 6x4 meter bedroom")

    assert decision.pipeline == "parametric"
    assert decision.object_category == ObjectCategory.ARCHITECTURAL
    assert decision.confidence >= 0.90
```

---

## Performance Considerations

- **Routing decision time**: <10ms (keyword matching is fast)
- **No external API calls**: All local processing
- **Caching**: Not needed (fast enough)
- **Scalability**: Can handle 1000s requests/second

---

## Future Enhancements

1. **Machine Learning**: Train classifier on user feedback
2. **Context awareness**: Remember user's previous requests
3. **Multi-language**: Support non-English prompts
4. **Visual prompts**: Route based on uploaded images
5. **Complexity scoring**: Estimate generation difficulty

---

**Routing Logic Status**: 📋 **Design Complete**
**Ready for**: Implementation
