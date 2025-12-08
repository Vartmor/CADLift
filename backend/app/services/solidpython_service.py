"""
SolidPython service for parametric CAD generation.

Uses SolidPython (solid2) to generate OpenSCAD code from structured instructions,
then renders to STL using the OpenSCAD CLI.

This provides precise, parametric CAD output suitable for manufacturing,
unlike AI mesh generation which produces organic but imprecise shapes.
"""
from __future__ import annotations

import gc
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("cadlift.services.solidpython")

# Add SolidPython to path
_solidpython_path = Path(__file__).parent.parent.parent.parent / "docs" / "useful_projects" / "SolidPython-master-2.0.0-beta-dev"

SOLIDPYTHON_AVAILABLE = False
_solid2 = None

if _solidpython_path.exists():
    try:
        sys.path.insert(0, str(_solidpython_path))
        import solid2 as _solid2_module
        _solid2 = _solid2_module
        SOLIDPYTHON_AVAILABLE = True
        logger.info(f"SolidPython module found at {_solidpython_path}")
    except ImportError as e:
        logger.warning(f"SolidPython import failed: {e}")
else:
    logger.warning(f"SolidPython not found at {_solidpython_path}")


class SolidPythonError(Exception):
    """SolidPython generation error."""
    pass


def _find_openscad_path() -> Optional[str]:
    """Find OpenSCAD executable path."""
    # Check environment variable first
    env_path = os.environ.get("OPENSCAD_PATH")
    if env_path and Path(env_path).exists():
        return env_path
    
    # Common installation paths
    if platform.system() == "Windows":
        candidates = [
            r"C:\Program Files\OpenSCAD\openscad.exe",
            r"C:\Program Files (x86)\OpenSCAD\openscad.exe",
            Path.home() / "AppData" / "Local" / "Programs" / "OpenSCAD" / "openscad.exe",
        ]
    elif platform.system() == "Darwin":  # macOS
        candidates = [
            "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD",
            "/usr/local/bin/openscad",
        ]
    else:  # Linux
        candidates = [
            "/usr/bin/openscad",
            "/usr/local/bin/openscad",
        ]
    
    for path in candidates:
        if Path(path).exists():
            return str(path)
    
    # Try to find in PATH
    openscad = shutil.which("openscad")
    if openscad:
        return openscad
    
    return None


class SolidPythonService:
    """SolidPython parametric CAD service."""
    
    def __init__(self):
        self.enabled = SOLIDPYTHON_AVAILABLE
        self.openscad_path = _find_openscad_path()
        
        if not self.enabled:
            logger.warning("SolidPython service DISABLED - library not available")
        elif not self.openscad_path:
            logger.warning("SolidPython available but OpenSCAD not found - STL rendering disabled")
        else:
            logger.info(f"SolidPython service initialized (OpenSCAD: {self.openscad_path})")
    
    def is_available(self) -> bool:
        """Check if service is available."""
        return self.enabled
    
    def can_render(self) -> bool:
        """Check if STL rendering is available (requires OpenSCAD)."""
        return self.enabled and self.openscad_path is not None
    
    def generate_scad(self, instructions: dict) -> str:
        """
        Generate OpenSCAD code from structured instructions.
        
        Args:
            instructions: Dict with 'parts' list, each containing shape definitions
            
        Returns:
            OpenSCAD code as string
        """
        if not self.enabled or _solid2 is None:
            raise SolidPythonError("SolidPython not available")
        
        try:
            root_object = self._build_object(instructions)
            scad_code = _solid2.scad_render(root_object)
            return scad_code
        except Exception as exc:
            logger.exception("Failed to generate OpenSCAD code")
            raise SolidPythonError(f"Failed to generate OpenSCAD code: {exc}")
    
    def render_to_stl(self, instructions: dict) -> bytes:
        """
        Generate STL bytes from structured instructions.
        
        Args:
            instructions: Dict with 'parts' list
            
        Returns:
            STL file bytes
        """
        if not self.can_render():
            raise SolidPythonError("OpenSCAD not available for rendering")
        
        scad_code = self.generate_scad(instructions)
        return self._render_scad_to_stl(scad_code)
    
    def _render_scad_to_stl(self, scad_code: str) -> bytes:
        """Render OpenSCAD code to STL using CLI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scad_path = Path(tmpdir) / "model.scad"
            stl_path = Path(tmpdir) / "model.stl"
            
            # Write SCAD file
            scad_path.write_text(scad_code, encoding="utf-8")
            
            # Run OpenSCAD
            cmd = [
                self.openscad_path,
                "-o", str(stl_path),
                str(scad_path)
            ]
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=120,  # 2 minute timeout
                    check=True
                )
                logger.info("OpenSCAD rendering complete")
            except subprocess.TimeoutExpired:
                raise SolidPythonError("OpenSCAD rendering timed out")
            except subprocess.CalledProcessError as e:
                stderr = e.stderr.decode() if e.stderr else "Unknown error"
                raise SolidPythonError(f"OpenSCAD rendering failed: {stderr}")
            
            # Read STL output
            if not stl_path.exists():
                raise SolidPythonError("OpenSCAD did not produce output file")
            
            return stl_path.read_bytes()
    
    def _build_object(self, instructions: dict) -> Any:
        """Build SolidPython object from instructions."""
        parts = instructions.get("parts", [])
        if not parts:
            raise SolidPythonError("No parts defined in instructions")
        
        # Build each part
        result = None
        for idx, part in enumerate(parts):
            obj = self._build_part(part, idx)
            
            # Apply operation (union/difference/intersection)
            operation = part.get("operation", "union").lower()
            
            if result is None:
                result = obj
            elif operation == "difference":
                result = result - obj
            elif operation == "intersection":
                result = result * obj
            else:  # union (default)
                result = result + obj
        
        return result
    
    def _build_part(self, part: dict, idx: int) -> Any:
        """Build a single part from instructions."""
        part_type = part.get("type", "").lower()
        
        # Get position/transform
        position = part.get("position", [0, 0, 0])
        rotation = part.get("rotation", [0, 0, 0])
        
        # Build the primitive
        if part_type == "cube" or part_type == "box":
            obj = self._build_cube(part)
        elif part_type == "cylinder":
            obj = self._build_cylinder(part)
        elif part_type == "sphere":
            obj = self._build_sphere(part)
        elif part_type == "cone":
            obj = self._build_cone(part)
        elif part_type == "hole":
            obj = self._build_hole(part)
        elif part_type == "polyhedron":
            obj = self._build_polyhedron(part)
        elif part_type == "text":
            obj = self._build_text(part)
        else:
            raise SolidPythonError(f"Unsupported part type: {part_type}")
        
        # Apply transformations
        if rotation != [0, 0, 0]:
            obj = _solid2.rotate(rotation)(obj)
        
        if position != [0, 0, 0]:
            obj = _solid2.translate(position)(obj)
        
        # Apply fillet if specified
        # Note: OpenSCAD doesn't have native fillet, would need CGAL or approximation
        
        return obj
    
    def _build_cube(self, part: dict) -> Any:
        """Build a cube/box."""
        # Support both 'size' as array and individual dimensions
        size = part.get("size")
        if size is None:
            width = float(part.get("width", 10))
            length = float(part.get("length", 10))
            height = float(part.get("height", 10))
            size = [width, length, height]
        
        centered = part.get("centered", True)
        return _solid2.cube(size, center=centered)
    
    def _build_cylinder(self, part: dict) -> Any:
        """Build a cylinder."""
        h = float(part.get("height", part.get("h", 10)))
        r = part.get("radius", part.get("r"))
        d = part.get("diameter", part.get("d"))
        
        if r is not None:
            r = float(r)
        elif d is not None:
            r = float(d) / 2
        else:
            r = 5.0  # Default
        
        # Support tapered cylinder (r1, r2)
        r1 = part.get("r1", part.get("bottom_radius"))
        r2 = part.get("r2", part.get("top_radius"))
        
        centered = part.get("centered", False)
        segments = int(part.get("segments", part.get("$fn", 32)))
        
        if r1 is not None and r2 is not None:
            obj = _solid2.cylinder(h=h, r1=float(r1), r2=float(r2), center=centered)
        else:
            obj = _solid2.cylinder(h=h, r=r, center=centered)
        
        # Apply segments using set_global_fn if needed
        if segments != 32:
            obj = obj.add_param('$fn', segments)
        return obj
    
    def _build_sphere(self, part: dict) -> Any:
        """Build a sphere."""
        r = part.get("radius", part.get("r"))
        d = part.get("diameter", part.get("d"))
        
        if r is not None:
            r = float(r)
        elif d is not None:
            r = float(d) / 2
        else:
            r = 5.0
        
        segments = int(part.get("segments", part.get("$fn", 32)))
        obj = _solid2.sphere(r=r)
        if segments != 32:
            obj = obj.add_param('$fn', segments)
        return obj
    
    def _build_cone(self, part: dict) -> Any:
        """Build a cone (cylinder with r2=0)."""
        h = float(part.get("height", 10))
        r = float(part.get("radius", part.get("r", 5)))
        centered = part.get("centered", False)
        segments = int(part.get("segments", 32))
        
        obj = _solid2.cylinder(h=h, r1=r, r2=0, center=centered)
        if segments != 32:
            obj = obj.add_param('$fn', segments)
        return obj
    
    def _build_hole(self, part: dict) -> Any:
        """Build a hole (cylinder for subtraction)."""
        h = float(part.get("depth", part.get("height", 100)))
        d = part.get("diameter", part.get("d"))
        r = part.get("radius", part.get("r"))
        
        if d is not None:
            r = float(d) / 2
        elif r is not None:
            r = float(r)
        else:
            r = 3.0  # Default M6 hole
        
        segments = int(part.get("segments", 32))
        
        # Make hole slightly longer for clean boolean
        obj = _solid2.cylinder(h=h + 0.2, r=r, center=False).down(0.1)
        if segments != 32:
            obj = obj.add_param('$fn', segments)
        return obj
    
    def _build_polyhedron(self, part: dict) -> Any:
        """Build a polyhedron from vertices and faces."""
        points = part.get("points", part.get("vertices", []))
        faces = part.get("faces", [])
        
        if not points or not faces:
            raise SolidPythonError("Polyhedron requires points and faces")
        
        return _solid2.polyhedron(points=points, faces=faces)
    
    def _build_text(self, part: dict) -> Any:
        """Build extruded text."""
        text = part.get("text", "CAD")
        size = float(part.get("size", 10))
        height = float(part.get("height", 2))
        font = part.get("font", "Liberation Sans")
        
        text_obj = _solid2.text(text, size=size, font=font)
        return _solid2.linear_extrude(height=height)(text_obj)


# Singleton
_solidpython_service: Optional[SolidPythonService] = None


def get_solidpython_service() -> SolidPythonService:
    """Get SolidPython service singleton."""
    global _solidpython_service
    if _solidpython_service is None:
        _solidpython_service = SolidPythonService()
    return _solidpython_service
