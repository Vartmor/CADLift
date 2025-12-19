"""
Parametric component library for Phase 6.5.

Provides parametric building components (doors, windows, furniture)
that can be generated with custom dimensions and placed in 3D models.

NOTE: This module requires CadQuery which is not installed in production.
It is only available when running locally with CadQuery installed.
"""

import math
from typing import Literal, Any
import logging

# CadQuery is optional - this module only works if CadQuery is installed
try:
    import cadquery as cq
    CADQUERY_AVAILABLE = True
except ImportError:
    cq = None
    CADQUERY_AVAILABLE = False

logger = logging.getLogger("cadlift.components")


# Component type definitions
ComponentType = Literal["door", "window", "desk", "chair", "bed", "table", "cabinet"]


class ParametricDoor:
    """
    Parametric door component generator.

    Generates 3D door geometry with customizable dimensions and style.
    """

    def __init__(
        self,
        width: float = 900.0,
        height: float = 2100.0,
        thickness: float = 40.0,
        frame_width: float = 100.0,
        door_type: Literal["single", "double", "sliding"] = "single"
    ):
        """
        Initialize parametric door.

        Args:
            width: Door width in mm
            height: Door height in mm
            thickness: Door panel thickness in mm
            frame_width: Door frame width in mm
            door_type: Type of door (single, double, sliding)
        """
        self.width = width
        self.height = height
        self.thickness = thickness
        frame_width = frame_width
        self.door_type = door_type

    def generate(self) -> cq.Workplane:
        """
        Generate 3D door geometry.

        Returns:
            CadQuery Workplane with door solid
        """
        if self.door_type == "single":
            return self._generate_single_door()
        elif self.door_type == "double":
            return self._generate_double_door()
        elif self.door_type == "sliding":
            return self._generate_sliding_door()
        else:
            raise ValueError(f"Unknown door type: {self.door_type}")

    def _generate_single_door(self) -> cq.Workplane:
        """Generate single hinged door."""
        # Door panel
        panel = (
            cq.Workplane("XY")
            .box(self.width, self.thickness, self.height)
            .translate((self.width / 2, self.thickness / 2, self.height / 2))
        )

        # Door frame (simplified)
        frame_thickness = 50.0
        frame = (
            cq.Workplane("XY")
            .rect(self.width + 2 * frame_thickness, frame_thickness)
            .extrude(self.height + frame_thickness)
            .translate((self.width / 2, -frame_thickness / 2, self.height / 2))
        )

        # Combine
        result = frame.union(panel)

        logger.debug(f"Generated single door: {self.width}x{self.height}mm")
        return result

    def _generate_double_door(self) -> cq.Workplane:
        """Generate double hinged doors."""
        half_width = self.width / 2

        # Left panel
        left_panel = (
            cq.Workplane("XY")
            .box(half_width, self.thickness, self.height)
            .translate((half_width / 2, self.thickness / 2, self.height / 2))
        )

        # Right panel
        right_panel = (
            cq.Workplane("XY")
            .box(half_width, self.thickness, self.height)
            .translate((self.width - half_width / 2, self.thickness / 2, self.height / 2))
        )

        result = left_panel.union(right_panel)

        logger.debug(f"Generated double door: {self.width}x{self.height}mm")
        return result

    def _generate_sliding_door(self) -> cq.Workplane:
        """Generate sliding door."""
        # Simplified sliding door (similar to single but with track)
        panel = (
            cq.Workplane("XY")
            .box(self.width, self.thickness, self.height)
            .translate((self.width / 2, self.thickness / 2, self.height / 2))
        )

        # Track (top rail)
        track = (
            cq.Workplane("XY")
            .box(self.width * 1.2, 60.0, 40.0)
            .translate((self.width / 2, 30.0, self.height + 20.0))
        )

        result = panel.union(track)

        logger.debug(f"Generated sliding door: {self.width}x{self.height}mm")
        return result


class ParametricWindow:
    """
    Parametric window component generator.

    Generates 3D window geometry with customizable dimensions and style.
    """

    def __init__(
        self,
        width: float = 1200.0,
        height: float = 1200.0,
        frame_thickness: float = 60.0,
        glass_thickness: float = 6.0,
        window_type: Literal["fixed", "casement", "sliding", "awning"] = "fixed",
        mullions: int = 1
    ):
        """
        Initialize parametric window.

        Args:
            width: Window width in mm
            height: Window height in mm
            frame_thickness: Frame thickness in mm
            glass_thickness: Glass pane thickness in mm
            window_type: Type of window
            mullions: Number of vertical mullions (dividers)
        """
        self.width = width
        self.height = height
        self.frame_thickness = frame_thickness
        self.glass_thickness = glass_thickness
        self.window_type = window_type
        self.mullions = mullions

    def generate(self) -> cq.Workplane:
        """
        Generate 3D window geometry.

        Returns:
            CadQuery Workplane with window solid
        """
        # Outer frame
        outer_frame = (
            cq.Workplane("XY")
            .rect(self.width, self.frame_thickness)
            .extrude(self.height)
            .translate((self.width / 2, self.frame_thickness / 2, self.height / 2))
        )

        # Inner opening (glass area)
        inner_width = self.width - 2 * self.frame_thickness
        inner_height = self.height - 2 * self.frame_thickness

        glass = (
            cq.Workplane("XY")
            .box(inner_width, self.glass_thickness, inner_height)
            .translate((
                self.width / 2,
                self.frame_thickness / 2,
                self.height / 2
            ))
        )

        result = outer_frame.union(glass)

        # Add mullions if requested
        if self.mullions > 0:
            mullion_spacing = inner_width / (self.mullions + 1)
            for i in range(1, self.mullions + 1):
                mullion_x = self.frame_thickness + i * mullion_spacing
                mullion = (
                    cq.Workplane("XY")
                    .box(30.0, self.frame_thickness, inner_height)
                    .translate((mullion_x, self.frame_thickness / 2, self.height / 2))
                )
                result = result.union(mullion)

        logger.debug(f"Generated {self.window_type} window: {self.width}x{self.height}mm, mullions={self.mullions}")
        return result


class FurnitureLibrary:
    """
    Basic furniture component generator.

    Provides simple parametric furniture (desk, chair, bed, etc.).
    """

    @staticmethod
    def generate_desk(
        width: float = 1500.0,
        depth: float = 750.0,
        height: float = 750.0,
        thickness: float = 25.0
    ) -> cq.Workplane:
        """
        Generate desk geometry.

        Args:
            width: Desk width in mm
            depth: Desk depth in mm
            height: Desk height in mm
            thickness: Top thickness in mm

        Returns:
            CadQuery Workplane with desk solid
        """
        # Desktop
        desktop = (
            cq.Workplane("XY")
            .box(width, depth, thickness)
            .translate((width / 2, depth / 2, height))
        )

        # Legs (4 legs at corners)
        leg_size = 50.0
        leg_positions = [
            (leg_size / 2, leg_size / 2),
            (width - leg_size / 2, leg_size / 2),
            (width - leg_size / 2, depth - leg_size / 2),
            (leg_size / 2, depth - leg_size / 2)
        ]

        result = desktop
        for x, y in leg_positions:
            leg = (
                cq.Workplane("XY")
                .box(leg_size, leg_size, height)
                .translate((x, y, height / 2))
            )
            result = result.union(leg)

        logger.debug(f"Generated desk: {width}x{depth}x{height}mm")
        return result

    @staticmethod
    def generate_chair(
        width: float = 450.0,
        depth: float = 450.0,
        seat_height: float = 450.0,
        back_height: float = 450.0
    ) -> cq.Workplane:
        """
        Generate chair geometry.

        Args:
            width: Chair width in mm
            depth: Chair depth in mm
            seat_height: Seat height from ground in mm
            back_height: Backrest height above seat in mm

        Returns:
            CadQuery Workplane with chair solid
        """
        # Seat
        seat_thickness = 50.0
        seat = (
            cq.Workplane("XY")
            .box(width, depth, seat_thickness)
            .translate((width / 2, depth / 2, seat_height))
        )

        # Backrest
        back_thickness = 50.0
        backrest = (
            cq.Workplane("XY")
            .box(width, back_thickness, back_height)
            .translate((width / 2, back_thickness / 2, seat_height + seat_thickness / 2 + back_height / 2))
        )

        # Legs (4 legs)
        leg_size = 40.0
        leg_positions = [
            (leg_size / 2, leg_size / 2),
            (width - leg_size / 2, leg_size / 2),
            (width - leg_size / 2, depth - leg_size / 2),
            (leg_size / 2, depth - leg_size / 2)
        ]

        result = seat.union(backrest)
        for x, y in leg_positions:
            leg = (
                cq.Workplane("XY")
                .box(leg_size, leg_size, seat_height)
                .translate((x, y, seat_height / 2))
            )
            result = result.union(leg)

        logger.debug(f"Generated chair: {width}x{depth}, seat_height={seat_height}mm")
        return result

    @staticmethod
    def generate_bed(
        width: float = 2000.0,
        length: float = 1500.0,
        mattress_height: float = 500.0,
        headboard_height: float = 800.0
    ) -> cq.Workplane:
        """
        Generate bed geometry.

        Args:
            width: Bed width in mm (standard: 2000mm for queen)
            length: Bed length in mm (standard: 1500mm)
            mattress_height: Height from floor to mattress top in mm
            headboard_height: Headboard height above mattress in mm

        Returns:
            CadQuery Workplane with bed solid
        """
        # Mattress
        mattress_thickness = 200.0
        mattress = (
            cq.Workplane("XY")
            .box(length, width, mattress_thickness)
            .translate((length / 2, width / 2, mattress_height))
        )

        # Bed frame
        frame_height = 100.0
        frame = (
            cq.Workplane("XY")
            .box(length, width, frame_height)
            .translate((length / 2, width / 2, mattress_height - mattress_thickness / 2 - frame_height / 2))
        )

        # Headboard
        headboard_thickness = 100.0
        headboard = (
            cq.Workplane("XY")
            .box(headboard_thickness, width, headboard_height)
            .translate((headboard_thickness / 2, width / 2, mattress_height + headboard_height / 2))
        )

        result = mattress.union(frame).union(headboard)

        logger.debug(f"Generated bed: {length}x{width}mm, mattress_height={mattress_height}mm")
        return result

    @staticmethod
    def generate_table(
        diameter: float = 1000.0,
        height: float = 750.0,
        top_thickness: float = 30.0
    ) -> cq.Workplane:
        """
        Generate round table geometry.

        Args:
            diameter: Table diameter in mm
            height: Table height in mm
            top_thickness: Top thickness in mm

        Returns:
            CadQuery Workplane with table solid
        """
        # Table top (cylinder)
        radius = diameter / 2
        top = (
            cq.Workplane("XY")
            .circle(radius)
            .extrude(top_thickness)
            .translate((0, 0, height))
        )

        # Central pedestal
        pedestal_radius = 100.0
        pedestal = (
            cq.Workplane("XY")
            .circle(pedestal_radius)
            .extrude(height)
            .translate((0, 0, height / 2))
        )

        result = top.union(pedestal)

        logger.debug(f"Generated round table: diameter={diameter}mm, height={height}mm")
        return result


def place_component(
    component: cq.Workplane,
    position: tuple[float, float, float],
    rotation: float = 0.0
) -> cq.Workplane:
    """
    Place a component at a specific position and rotation.

    Args:
        component: Component solid (CadQuery Workplane)
        position: (x, y, z) position in mm
        rotation: Rotation in degrees (around Z axis)

    Returns:
        Transformed component
    """
    result = component.translate(position)

    if rotation != 0.0:
        result = result.rotate((position[0], position[1], 0), (position[0], position[1], 1), rotation)

    return result


def check_collision(
    component1: cq.Workplane,
    component2: cq.Workplane,
    tolerance: float = 10.0
) -> bool:
    """
    Check if two components collide (basic bounding box check).

    Args:
        component1: First component
        component2: Second component
        tolerance: Collision tolerance in mm

    Returns:
        True if components collide, False otherwise
    """
    try:
        # Get bounding boxes
        bbox1 = component1.val().BoundingBox()
        bbox2 = component2.val().BoundingBox()

        # Check for overlap (with tolerance)
        x_overlap = not (bbox1.xmax + tolerance < bbox2.xmin or bbox2.xmax + tolerance < bbox1.xmin)
        y_overlap = not (bbox1.ymax + tolerance < bbox2.ymin or bbox2.ymax + tolerance < bbox1.ymin)
        z_overlap = not (bbox1.zmax + tolerance < bbox2.zmin or bbox2.zmax + tolerance < bbox1.zmin)

        collision = x_overlap and y_overlap and z_overlap

        if collision:
            logger.warning("Collision detected between components")

        return collision

    except Exception as e:
        logger.error(f"Collision check failed: {e}")
        return False
