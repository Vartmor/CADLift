"""
Intelligent routing service for pipeline selection.

Routes user prompts to the optimal pipeline:
- Parametric: Engineering objects, architecture (precise dimensions)
- AI: Organic shapes, artistic objects (realistic, creative)
- Hybrid: Combination of both (decorated functional objects)
"""
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
        "duvar", "kat", "oda", "daire", "ev",

        # Features
        "wall", "door", "window", "ceiling", "floor plan",
        "multi-story", "storey", "level", "meters", "metre"
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
        "detailed", "intricate", "complex surface",
        "carved", "sculpted", "engraved", "embossed",
        "relief", "pattern", "ornate"
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

    def route(self, prompt: str, force_pipeline: str | None = None) -> RoutingDecision:
        """
        Route prompt to optimal pipeline.

        Args:
            prompt: User's text prompt
            force_pipeline: Optional override ('parametric', 'ai', 'hybrid')

        Returns:
            RoutingDecision with pipeline selection and reasoning
        """
        analysis = self.analyze_prompt(prompt)

        # Handle user override
        if force_pipeline and force_pipeline in ("parametric", "ai", "hybrid"):
            logger.info(
                f"User override: forcing pipeline to '{force_pipeline}'",
                extra={"prompt": prompt[:100]}
            )
            return RoutingDecision(
                pipeline=force_pipeline,
                confidence=1.0,
                reasoning=f"User override: {force_pipeline} pipeline forced",
                object_category=ObjectCategory.UNKNOWN,
                prompt_analysis=analysis
            )

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
            elif parametric_features or has_dimensions:
                return (
                    "parametric",
                    "Mixed category but parametric features/dimensions specified"
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
