from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger("cadlift.llm")
settings = get_settings()


class LLMService:
    def __init__(self, provider: str, api_key: str | None, timeout_seconds: float = 30.0, model: str | None = None, max_retries: int = 3):
        self.provider = (provider or "none").lower()
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.model = model or "gpt-4o-mini"
        self.max_retries = max_retries

    @property
    def enabled(self) -> bool:
        return self.provider != "none" and bool(self.api_key)

    async def generate_instructions(self, prompt_text: str) -> dict[str, Any]:
        """
        Generate instructions from prompt with retry logic.

        Retries up to max_retries times if:
        - LLM returns invalid JSON
        - JSON doesn't match expected schema
        - Network errors (with backoff)

        Args:
            prompt_text: User's natural language prompt

        Returns:
            Validated instruction dictionary

        Raises:
            RuntimeError: If LLM service not enabled
            ValueError: If all retries fail
        """
        if not self.enabled:
            raise RuntimeError("LLM service not enabled")
        if self.provider == "openai":
            return await self._call_openai_with_retry(prompt_text)
        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    async def _call_openai_with_retry(self, prompt_text: str) -> dict[str, Any]:
        """Call OpenAI API with retry logic for validation failures."""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                result = await self._call_openai(prompt_text)
                # Validate the result before returning
                self._validate_llm_response(result)
                logger.info(
                    "LLM call successful",
                    extra={"attempt": attempt + 1, "max_retries": self.max_retries}
                )
                return result
            except (json.JSONDecodeError, ValueError, KeyError) as exc:
                last_error = exc
                logger.warning(
                    "LLM response validation failed, retrying",
                    extra={
                        "attempt": attempt + 1,
                        "max_retries": self.max_retries,
                        "error": str(exc)
                    }
                )
                # Continue to next retry
                continue
            except httpx.HTTPError as exc:
                last_error = exc
                logger.warning(
                    "LLM HTTP error, retrying",
                    extra={
                        "attempt": attempt + 1,
                        "max_retries": self.max_retries,
                        "error": str(exc)
                    }
                )
                # Continue to next retry
                continue

        # All retries failed
        raise ValueError(f"LLM failed after {self.max_retries} attempts: {last_error}") from last_error

    def _validate_llm_response(self, response: dict[str, Any]) -> None:
        """
        Validate LLM response structure.

        Supports two schemas:
        1) Architectural layout: {rooms:[...], wall_thickness?, extrude_height?}
        2) Object primitives: {shapes:[...], wall_thickness?, extrude_height?}

        Raises ValueError if response doesn't match expected schema.
        """
        if not isinstance(response, dict):
            raise ValueError("LLM response must be a dict")

        has_rooms = isinstance(response.get("rooms"), list) and len(response["rooms"]) > 0
        has_shapes = isinstance(response.get("shapes"), list) and len(response["shapes"]) > 0

        if not (has_rooms or has_shapes):
            raise ValueError("LLM response must include non-empty 'rooms' or 'shapes'")

        if has_rooms:
            for idx, room in enumerate(response["rooms"]):
                if not isinstance(room, dict):
                    raise ValueError(f"rooms[{idx}] must be a dict")

                if "name" not in room:
                    raise ValueError(f"rooms[{idx}] missing 'name'")

                # Must have either (width + length) OR vertices
                has_dimensions = "width" in room and "length" in room
                has_vertices = "vertices" in room

                if not has_dimensions and not has_vertices:
                    raise ValueError(f"rooms[{idx}] must have either (width+length) or vertices")

                # Validate dimensions if present
                if has_dimensions:
                    if not isinstance(room.get("width"), (int, float)) or room["width"] <= 0:
                        raise ValueError(f"rooms[{idx}].width must be a positive number")
                    if not isinstance(room.get("length"), (int, float)) or room["length"] <= 0:
                        raise ValueError(f"rooms[{idx}].length must be a positive number")

                # Validate vertices if present
                if has_vertices:
                    if not isinstance(room["vertices"], list):
                        raise ValueError(f"rooms[{idx}].vertices must be a list")
                    if len(room["vertices"]) < 3:
                        raise ValueError(f"rooms[{idx}].vertices must have at least 3 points")
                    for pt_idx, pt in enumerate(room["vertices"]):
                        if not isinstance(pt, list) or len(pt) != 2:
                            raise ValueError(f"rooms[{idx}].vertices[{pt_idx}] must be [x,y]")

                # Validate position if present
                if "position" in room:
                    pos = room["position"]
                    if not isinstance(pos, list) or len(pos) != 2:
                        raise ValueError(f"rooms[{idx}].position must be [x,y]")
                    if not all(isinstance(coord, (int, float)) for coord in pos):
                        raise ValueError(f"rooms[{idx}].position coordinates must be numbers")

        if has_shapes:
            allowed = {"box", "cylinder", "tapered_cylinder", "polygon", "thread", "revolve", "sweep"}
            for idx, shape in enumerate(response["shapes"]):
                if not isinstance(shape, dict):
                    raise ValueError(f"shapes[{idx}] must be a dict")
                shape_type = str(shape.get("type", "")).lower()
                if shape_type not in allowed:
                    raise ValueError(f"shapes[{idx}].type must be one of {sorted(allowed)}")
                if "height" in shape and (not isinstance(shape["height"], (int, float)) or shape["height"] <= 0):
                    raise ValueError(f"shapes[{idx}].height must be a positive number")
                if "wall_thickness" in shape and (not isinstance(shape["wall_thickness"], (int, float)) or shape["wall_thickness"] < 0):
                    raise ValueError(f"shapes[{idx}].wall_thickness must be non-negative")
                if shape_type == "box":
                    if not all(isinstance(shape.get(k), (int, float)) and shape[k] > 0 for k in ("width", "length")):
                        raise ValueError(f"shapes[{idx}] box requires positive width and length")
                if shape_type == "cylinder":
                    if not isinstance(shape.get("radius"), (int, float)) or shape["radius"] <= 0:
                        raise ValueError(f"shapes[{idx}] cylinder requires positive radius")
                if shape_type == "tapered_cylinder":
                    if not all(isinstance(shape.get(k), (int, float)) and shape[k] > 0 for k in ("bottom_radius", "top_radius")):
                        raise ValueError(f"shapes[{idx}] tapered_cylinder requires positive bottom_radius and top_radius")
                if shape_type == "polygon":
                    verts = shape.get("vertices")
                    if not isinstance(verts, list) or len(verts) < 3:
                        raise ValueError(f"shapes[{idx}] polygon requires at least 3 vertices")
                    for pt_idx, pt in enumerate(verts):
                        if not isinstance(pt, list) or len(pt) != 2:
                            raise ValueError(f"shapes[{idx}].vertices[{pt_idx}] must be [x,y]")

    async def _call_openai(self, prompt_text: str) -> dict[str, Any]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        system_prompt = (
            "You are a CAD geometry planner. Output JSON describing either architectural layouts OR detailed solids.\n\n"
            "CHOOSE ONE OF TWO SCHEMAS:\n"
            "1) Architectural layout:\n"
            "{\n"
            "  \"rooms\": [ {\"name\": \"room\", \"width\": 4000, \"length\": 3000, \"position\": [0,0]} ... ],\n"
            "  \"wall_thickness\": 200,\n"
            "  \"extrude_height\": 3000\n"
            "}\n"
            "- rooms can use width/length or vertices; position is bottom-left [x,y] in mm.\n"
            "- Use this for buildings, floor plans, spaces.\n\n"
            "2) Object primitives (for products/objects/parts):\n"
            "{\n"
            "  \"shapes\": [\n"
            "    {\"type\": \"cylinder\", \"radius\": 45, \"height\": 110, \"hollow\": true, \"wall_thickness\": 3, \"fillet\": 2},\n"
            "    {\"type\": \"box\", \"width\": 80, \"length\": 120, \"height\": 50, \"hollow\": false, \"fillet\": 5, \"position\": [100,0]},\n"
            "    {\"type\": \"polygon\", \"vertices\": [[0,0],[50,0],[40,30],[0,30]], \"height\": 40}\n"
            "  ],\n"
            "  \"extrude_height\": 110,\n"
            "  \"wall_thickness\": 3\n"
            "}\n"
            "- Supported shapes: box(width,length,height), cylinder(radius,height), tapered_cylinder(bottom_radius,top_radius,height), polygon(vertices,height), thread(major_radius, pitch, turns, length), revolve(profile_vertices, angle_deg), sweep(profile_vertices, path_vertices).\n"
            "- Optional: hollow (bool), wall_thickness (mm), fillet (mm), position [x,y], rotate_deg, operation (\"union\" default, \"diff\" to cut from previous).\n"
            "- Use mm units. Pick the most relevant shape(s) for the prompt.\n\n"
            "Dimension Guidelines (use realistic sizes):\n"
            "- Coffee cup/mug: 70-90mm diameter, 80-120mm tall, 2-4mm wall thickness\n"
            "- Water bottle: 60-80mm diameter, 180-250mm tall, 1-3mm wall thickness\n"
            "- Vase: 60-100mm bottom, 80-150mm top, 150-300mm tall\n"
            "- Screw: 3-10mm diameter, 10-50mm length, M3-M10 thread pitch (0.5-2mm)\n"
            "- Power adapter: 40-80mm body, 10-30mm plug\n"
            "- Handle: 3-6mm thick profile, attach at 70-80%% of body radius\n\n"
            "Rules:\n"
            "- Return only JSON, no prose.\n"
            "- For objects (mug, cup, bottle, vase, tool, part, screw), ALWAYS use shapes schema. Never return rooms for objects.\n"
            "- For tapered objects (cups, bottles, vases), use tapered_cylinder with different bottom_radius and top_radius.\n"
            "- Only use rooms schema if user clearly asks for building/room/floor/plan/house/office.\n"
            "- For handles/curved attachments, use sweep with profile and path vertices.\n\n"
            "Examples:\n"
            "Prompt: \"6x4m room\" -> {\"rooms\":[{\"name\":\"main\",\"width\":6000,\"length\":4000}],\"extrude_height\":3000,\"wall_thickness\":200}\n\n"
            "Prompt: \"A realistic coffee cup\" -> {\"shapes\":[{\"type\":\"tapered_cylinder\",\"bottom_radius\":60,\"top_radius\":75,\"height\":90,\"hollow\":true,\"wall_thickness\":3,\"fillet\":2}]}\n\n"
            "Prompt: \"Coffee cup with handle\" -> {\"shapes\":[{\"type\":\"tapered_cylinder\",\"bottom_radius\":60,\"top_radius\":75,\"height\":90,\"hollow\":true,\"wall_thickness\":3,\"fillet\":2},{\"type\":\"sweep\",\"profile\":[[0,0],[4,0],[4,10],[0,10]],\"path\":[[75,0,20],[90,0,20],[90,0,55],[75,0,70]]}]}\n\n"
            "Prompt: \"Water bottle, 200mm tall\" -> {\"shapes\":[{\"type\":\"tapered_cylinder\",\"bottom_radius\":62,\"top_radius\":65,\"height\":180,\"hollow\":true,\"wall_thickness\":2},{\"type\":\"cylinder\",\"radius\":30,\"height\":20,\"hollow\":true,\"wall_thickness\":2,\"position\":[0,0]}]}\n\n"
            "Prompt: \"M6 screw, 30mm long\" -> {\"shapes\":[{\"type\":\"thread\",\"major_radius\":3,\"pitch\":1,\"turns\":25,\"length\":25},{\"type\":\"cylinder\",\"radius\":5,\"height\":3,\"position\":[0,0]},{\"type\":\"cylinder\",\"radius\":1.5,\"height\":5,\"position\":[0,0]}]}\n\n"
            "Prompt: \"Power adapter\" -> {\"shapes\":[{\"type\":\"box\",\"width\":60,\"length\":80,\"height\":40,\"fillet\":5},{\"type\":\"box\",\"width\":15,\"length\":25,\"height\":10,\"position\":[0,80]}]}\n\n"
            "**OUTPUT ONLY VALID JSON. NO EXPLANATIONS.**"
        )
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_text},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(url, headers=headers, json=body)
            response.raise_for_status()
            data = response.json()
        logger.info(
            "LLM call completed",
            extra={"provider": self.provider, "model": self.model, "prompt_chars": len(prompt_text)},
        )
        try:
            content = data["choices"][0]["message"]["content"]
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"LLM response missing content: {data}") from exc
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(f"LLM returned non-JSON content: {content}") from exc
        logger.info("LLM parsed prompt", extra={"provider": self.provider, "model": self.model})
        return parsed

    async def generate_from_image(self, image_bytes: bytes, prompt_text: str | None = None) -> dict[str, Any]:
        """
        Generate CAD instructions from an image (Blueprint/Technical Drawing).
        
        Args:
            image_bytes: Raw image data
            prompt_text: Optional user prompt to exact specific details
            
        Returns:
            Validated instruction dictionary (shapes or rooms)
        """
        if not self.enabled:
            raise RuntimeError("LLM service not enabled")
            
        import base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        if self.provider == "openai":
            return await self._call_openai_vision(base64_image, prompt_text)
            
        raise ValueError(f"Provider {self.provider} does not support vision capability")

    async def _call_openai_vision(self, base64_image: str, user_prompt: str | None) -> dict[str, Any]:
        """Call OpenAI Vision API."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        system_prompt = (
            "You are an expert Mechanical Engineer and CAD Designer. "
            "Your task is to analyze technical drawings (blueprints) and extract precise geometric construction instructions.\n\n"
            "OUTPUT SCHEMA (JSON):\n"
            "Return a JSON object describing the PART or FLOOR PLAN seen in the image.\n"
            "Choose schema based on image content:\n"
            "1. MECHANICAL PART (Brackets, gears, manufacturing parts):\n"
            "{\n"
            "  \"shapes\": [\n"
            "    {\"type\": \"box\", \"width\": 100, \"length\": 50, \"height\": 20, \"fillet\": 5},\n"
            "    {\"type\": \"cylinder\", \"radius\": 10, \"height\": 20, \"operation\": \"diff\", \"position\": [0,0]}, \n"
            "    {\"type\": \"polygon\", \"vertices\": [[-50,-20],[50,-20],[50,20],[-50,20]], \"height\": 10, \"operation\": \"union\"}\n"
            "  ],\n"
            "  \"extrude_height\": 20,\n"
            "  \"units\": \"mm\"\n"
            "}\n"
            "- USE BOOLEAN OPERATIONS: Build the object by adding ('union') bodies and cutting ('diff') holes.\n"
            "- Look for DIMENSIONS in the image (e.g., '38', 'R30', '├ÿ15'). Use these EXACT values.\n"
            "- 'operation': 'union' (default) or 'diff' (to cut holes/slots from previous shapes).\n"
            "- Align the main body center at [0,0].\n"
            "- For U-brackets or irregular profiles, use ONE 'polygon' shape for the main body if possible, then cut holes.\n"
            "- DO NOT use 'wall_thickness' for solid parts. Use 0.\n\n"
            "2. FLOOR PLAN (Architectural):\n"
            "{\n"
            "  \"rooms\": [ ... ], \n"
            "  \"wall_thickness\": 200,\n"
            "  \"extrude_height\": 3000\n"
            "}\n\n"
            "CRITICAL RULES:\n"
            "- ACCURACY: Use the exact numbers written on the blueprint. If a number is '30', use 30.0.\n"
            "- INFERENCE: If a dimension is missing, estimate proportionally based on known dimensions.\n"
            "- OUTPUT: Raw JSON only. No markdown formatting."
        )
        
        user_content = [
            {"type": "text", "text": user_prompt or "Analyze this technical drawing and extract the geometry."}
        ]
        
        # Add image
        user_content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        })

        body = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "max_tokens": 4096,
            "temperature": 0.1, # Low temperature for precision
            "response_format": {"type": "json_object"},
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client: # Longer timeout for image analysis
            response = await client.post(url, headers=headers, json=body)
            response.raise_for_status()
            data = response.json()
            
        try:
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            self._validate_llm_response(parsed)
            return parsed
        except Exception as exc:
             logger.warning(f"Vision analysis failed: {exc}", extra={"response": data})
             raise ValueError("Failed to parse vision response") from exc

    async def describe_image(self, image_bytes: bytes, prompt_text: str | None = None) -> str:
        """
        Generate a text description (CAD prompt) from an image.
        Used for the Unified Image-to-Precision pipeline.
        """
        if not self.enabled:
             raise RuntimeError("LLM service not enabled")
            
        import base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        if self.provider == "openai":
            return await self._call_openai_vision_text(base64_image, prompt_text)
            
        raise ValueError(f"Provider {self.provider} does not support vision capability")

    async def _call_openai_vision_text(self, base64_image: str, user_prompt: str | None) -> str:
        """Call OpenAI Vision API and return text description."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        system_prompt = (
            "You are an expert Mechanical Engineer and CAD Designer. "
            "Your task is to analyze technical drawings (blueprints) and write a precise, step-by-step CAD instruction prompt.\n\n"
            "GOAL: Convert the visual drawing into a text description that another AI can use to generate 3D code.\n"
            "FORMAT: A numbered list of geometric operations.\n\n"
            "EXAMPLE OUTPUT:\n"
            "Create a mounting bracket.\n"
            "1. The base is a box with width 100mm, length 60mm, and height 10mm.\n"
            "2. In the center, add a vertical cylinder with radius 20mm and height 40mm.\n"
            "3. Cut a 10mm hole (cylinder) through the center of the vertical cylinder.\n"
            "4. Cut two 5mm screw holes in the base, positioned at [-35, 0] and [35, 0].\n\n"
            "RULES:\n"
            "- Be precise with numbers found in the image.\n"
            "- Use 'Add' for unions and 'Cut' for differences/holes.\n"
            "- Specify positions relative to the center [0,0] if possible.\n"
            "- Return ONLY the text description. Do not wrap in JSON."
        )
        
        user_content = [
            {"type": "text", "text": user_prompt or "Analyze this blueprint and write a CAD generation prompt."}
        ]
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        })

        body = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "max_tokens": 1024,
            "temperature": 0.1,
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=body)
            response.raise_for_status()
            data = response.json()
            
        try:
            return data["choices"][0]["message"]["content"]
        except Exception as exc:
             logger.warning(f"Vision text analysis failed: {exc}", extra={"response": data})
             raise ValueError("Failed to parse vision response") from exc
llm_service = LLMService(
    provider=getattr(settings, "llm_provider", "none"),
    api_key=getattr(settings, "openai_api_key", None),
    timeout_seconds=getattr(settings, "llm_timeout_seconds", 30.0),
    model=getattr(settings, "openai_model", "gpt-4o-mini"),
)

