
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from app.services.solidpython_service import get_solidpython_service

def test_polygon_fix():
    print("Testing Polygon Fix...")
    service = get_solidpython_service()
    
    # 1. Test 2D polygon with extrusion (The failing case)
    print("\n--- Testing 2D Polygon Extrusion ---")
    poly_instruction = {
        "parts": [
            {
                "type": "polygon",
                "vertices": [[0,0], [20,0], [10,20]],
                "height": 15
            }
        ]
    }
    
    try:
        stl = service.render_to_stl(poly_instruction)
        print(f"✅ Polygon generated: {len(stl)} bytes")
        with open("test_polygon_fixed.stl", "wb") as f:
            f.write(stl)
    except Exception as e:
        print(f"❌ Polygon failure: {e}")

if __name__ == "__main__":
    test_polygon_fix()
