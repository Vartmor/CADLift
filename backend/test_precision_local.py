
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from app.services.solidpython_service import get_solidpython_service

def test_service():
    print("Initializing SolidPythonService...")
    service = get_solidpython_service()
    
    print(f"Enabled: {service.enabled}")
    print(f"OpenSCAD Path: {service.openscad_path}")
    print(f"Can Render: {service.can_render()}")
    
    if not service.can_render():
        print("Cannot render - check OpenSCAD installation.")
        return

    instructions = {
        "parts": [
            {"type": "cube", "size": [10, 20, 30], "centered": True}
        ]
    }
    
    print("\nAttempting to render STL...")
    try:
        stl_bytes = service.render_to_stl(instructions)
        print(f"Success! STL size: {len(stl_bytes)} bytes")
        
        # Save for manual inspection if needed
        with open("test_output.stl", "wb") as f:
            f.write(stl_bytes)
        print("Saved to test_output.stl")
        
    except Exception as e:
        print(f"Render failed: {e}")

if __name__ == "__main__":
    test_service()
