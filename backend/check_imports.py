
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath("c:\\Users\\Muhammed\\Desktop\\cadlift\\backend"))

print("Checking imports...")

try:
    print("Importing app.services.llm...")
    import app.services.llm
    print("SUCCESS: app.services.llm")
except Exception as e:
    print(f"FAILED: app.services.llm - {e}")

try:
    print("Importing app.services.parametric_service...")
    import app.services.parametric_service
    print("SUCCESS: app.services.parametric_service")
except Exception as e:
    print(f"FAILED: app.services.parametric_service - {e}")

try:
    print("Importing app.pipelines.image...")
    import app.pipelines.image
    print("SUCCESS: app.pipelines.image")
except Exception as e:
    print(f"FAILED: app.pipelines.image - {e}")
