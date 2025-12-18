from __future__ import annotations

import logging
import re
from typing import Any
from app.core.errors import CADLiftError, ErrorCode

logger = logging.getLogger("cadlift.service.parametric")

def validate_instruction_schema(instructions: dict[str, Any]) -> None:
    """Validate that instructions match the expected parametric schema."""
    if not isinstance(instructions, dict):
        raise ValueError("Instructions must be a dictionary")
    
    # Must have either rooms or shapes
    has_rooms = "rooms" in instructions and isinstance(instructions["rooms"], list)
    has_shapes = "shapes" in instructions and isinstance(instructions["shapes"], list)
    
    if not (has_rooms or has_shapes):
        raise ValueError("Instructions must contain either 'rooms' or 'shapes'")
    
    # Additional validation logic can be migrated here if needed
    
def detect_room_adjacency(rooms_with_polygons: list[tuple[dict, list[list[float]]]]) -> list[dict[str, Any]]:
    """Detect which rooms share walls."""
    adjacencies = []
    
    def points_equal(p1, p2, tol=1.0):
        return abs(p1[0] - p2[0]) < tol and abs(p1[1] - p2[1]) < tol

    for i in range(len(rooms_with_polygons)):
        for j in range(i + 1, len(rooms_with_polygons)):
            room1_def, poly1 = rooms_with_polygons[i]
            room2_def, poly2 = rooms_with_polygons[j]

            for k in range(len(poly1)):
                p1_a = poly1[k]
                p1_b = poly1[(k + 1) % len(poly1)]

                for m in range(len(poly2)):
                    p2_a = poly2[m]
                    p2_b = poly2[(m + 1) % len(poly2)]

                    if (points_equal(p1_a, p2_a) and points_equal(p1_b, p2_b)) or \
                       (points_equal(p1_a, p2_b) and points_equal(p1_b, p2_a)):
                        adjacencies.append({
                            "room1": room1_def.get("name", f"room_{i}"),
                            "room2": room2_def.get("name", f"room_{j}"),
                            "shared_wall": [p1_a, p1_b]
                        })
                        break
    return adjacencies

def validate_room_dimensions(room: dict[str, Any], idx: int) -> None:
    """Validate room dimensions."""
    if "width" not in room or "length" not in room:
        return
        
    width = float(room["width"])
    length = float(room["length"])
    
    if width <= 0 or length <= 0:
         raise CADLiftError(ErrorCode.PROMPT_INVALID_DIMENSIONS, details=f"Room {idx} has invalid dimensions")
         
    # Basic sanity checks
    if width < 500 or length < 500: # 0.5m
        logger.warning(f"Room {idx} seems very small (<0.5m)")

def shape_span(s: dict[str, Any]) -> float:
    """Calculate the estimated width of a shape for auto-positioning."""
    st = str(s.get("type", "")).lower()
    if st == "box":
        return float(s.get("length", 0)) or float(s.get("width", 0)) or 20.0
    if st == "cylinder":
        r = float(s.get("radius", 0))
        return max(1.0, r * 2)
    if st == "tapered_cylinder":
        r = max(float(s.get("bottom_radius", 0)), float(s.get("top_radius", 0)))
        return max(1.0, r * 2)
    return 20.0

def instructions_to_model(instructions: dict[str, Any], prompt_text: str, params: dict[str, Any]) -> dict[str, Any]:
    """
    Convert instructions (from LLM or heuristic) into a standard CADLift model dict.
    This model dict is used by geometry.build_artifacts.
    """
    validate_instruction_schema(instructions)
    has_shapes = instructions.get("shapes")
    has_rooms = instructions.get("rooms")
    
    extrude_height = float(instructions.get("extrude_height", params.get("extrude_height", 3000.0)))
    # Determine smart default for wall thickness
    # Mechanical parts (shapes) -> 0.0 (Solid)
    # Architectural (rooms) -> 200.0 (Walls)
    default_wall = 0.0 if has_shapes else 200.0
    wall_thickness = float(instructions.get("wall_thickness", params.get("wall_thickness", default_wall)))

    # --- SHAPES MODE ---
    if has_shapes:
        polygons: list[list[list[float]]] = []
        auto_offset = 0.0
        max_height = extrude_height or 0.0
        max_wall = wall_thickness or 0.0
        spacing = 20.0
        detail = float(params.get("detail", 70))
        fillets: list[float] = []
        operations: list[str] = []
        origins: list[tuple[float, float]] = []
        
        # Helper for circle polygons
        import math
        def circle_polygon(radius, segments=32):
            pts = []
            for i in range(segments):
                theta = 2 * math.pi * (i / segments)
                pts.append([radius * math.cos(theta), radius * math.sin(theta)])
            return pts

        for idx, shape in enumerate(has_shapes):
            stype = str(shape.get("type", "")).lower()
            shape_height = float(shape.get("height", extrude_height))
            if shape_height > 0:
                max_height = max(max_height, shape_height)
            if "wall_thickness" in shape:
                max_wall = max(max_wall, float(shape["wall_thickness"]))
            
            fillets.append(float(shape.get("fillet", 0)))
            operations.append(str(shape.get("operation", "union")).lower())
            
            # Positioning
            pos = shape.get("position")
            pos_x = float(pos[0]) if isinstance(pos, (list, tuple)) and len(pos) == 2 else 0.0
            pos_y = float(pos[1]) if isinstance(pos, (list, tuple)) and len(pos) == 2 else 0.0
            
            # Auto-position if no position given (and not first object or instructed otherwise)
            # Actually, standard logic:
            explicit_pos = shape.get("position") is not None
            if not explicit_pos:
                # If it's a hole (diff), default to 0,0 (center of main object)
                if operations[-1] == "diff":
                    pos_x, pos_y = 0.0, 0.0
                else: 
                     # Union parts - auto offset if desired, or default to 0,0
                     # For Image-to-CAD, we usually assume the drawing is one assembly centered at 0,0
                     # unless there are multiple distinct parts.
                     # Let's default to [0,0] for Vision-generated assembly.
                     pos_x, pos_y = 0.0, 0.0

            origins.append((pos_x, pos_y))

            poly = []
            if stype == "box":
                w = float(shape.get("width", 20))
                l = float(shape.get("length", 20))
                hw, hl = w / 2, l / 2
                poly = [
                    [pos_x - hw, pos_y - hl],
                    [pos_x + hw, pos_y - hl],
                    [pos_x + hw, pos_y + hl],
                    [pos_x - hw, pos_y + hl],
                ]
            elif stype in ("cylinder", "tapered_cylinder", "thread", "revolve"):
                r = float(shape.get("radius", 0))
                if stype == "tapered_cylinder":
                    r = max(float(shape.get("bottom_radius", 0)), float(shape.get("top_radius", 0)))
                if stype == "thread":
                    r = float(shape.get("major_radius", 0))
                
                # Simple circle for footprint
                base_poly = circle_polygon(r, 64)
                poly = [[pt[0] + pos_x, pt[1] + pos_y] for pt in base_poly]
                
            elif stype == "polygon":
                 verts = shape.get("vertices", [])
                 poly = [[float(v[0]) + pos_x, float(v[1]) + pos_y] for v in verts]
            
            if poly:
                polygons.append(poly)

        return {
            "prompt": prompt_text,
            "instructions": instructions,
            "contours": polygons,
            "extrude_height": max_height,
            "wall_thickness": max_wall,
            "only_2d": False, # Explicitly 3D
            "metadata": {
                "source": "shapes",
                "shape_count": len(polygons),
                "fillets": fillets,
                "operations": operations,
                "origins": origins,
            },
        }

    # --- ROOMS MODE ---
    corridor_gap = float(instructions.get("corridor_gap", 1000))
    contours = []
    width_offset = 0.0
    rooms_by_floor = {}
    rooms_with_polygons = []

    for idx, room in enumerate(has_rooms):
        validate_room_dimensions(room, idx)
        floor = int(room.get("floor", room.get("level", 0)))
        
        if "vertices" in room:
             poly = [[float(p[0]), float(p[1])] for p in room["vertices"]]
        else:
            w = float(room.get("width", 5000))
            l = float(room.get("length", 4000))
            if "position" in room:
                px, py = room["position"]
                poly = [[px, py], [px+w, py], [px+w, py+l], [px, py+l]]
            else:
                poly = [[width_offset, 0], [width_offset+w, 0], [width_offset+w, l], [width_offset, l]]
                width_offset += w + corridor_gap
        
        rooms_with_polygons.append((room, poly))
        contours.append(poly)
        if floor not in rooms_by_floor: rooms_by_floor[floor] = []
        rooms_by_floor[floor].append((room, poly))

    adjacencies = detect_room_adjacency(rooms_with_polygons)

    return {
        "prompt": prompt_text,
        "instructions": instructions,
        "contours": contours,
        "extrude_height": extrude_height,
        "wall_thickness": wall_thickness,
        "metadata": {
            "source": "prompt",
            "room_count": len(contours),
            "floors": sorted(rooms_by_floor.keys()),
            "adjacencies": adjacencies
        }
    }
