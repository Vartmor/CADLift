"""Simple test for a single prompt."""
import requests
import json
import time

BASE_URL = "http://localhost:8000"
PROMPT = "M8 hex bolt, 40mm long with threaded shaft"

print(f"Testing prompt: {PROMPT}")

# Create job
r = requests.post(
    f"{BASE_URL}/api/v1/jobs",
    data={
        "job_type": "prompt",
        "mode": "2d_to_3d",
        "params": json.dumps({
            "prompt": PROMPT,
            "use_ai": True,
            "detail": 70
        })
    }
)
r.raise_for_status()
job_id = r.json()["id"]
print(f"Job created: {job_id}")

# Poll until complete
while True:
    time.sleep(5)
    r2 = requests.get(f"{BASE_URL}/api/v1/jobs/{job_id}")
    job = r2.json()
    status = job.get("status", "unknown")
    progress = job.get("progress", 0)
    print(f"Status: {status}, Progress: {progress}%")
    
    if status == "completed":
        print("\n✅ SUCCESS!")
        params = job.get("params", {})
        print(f"GLB file ID: {params.get('glb_file_id')}")
        print(f"STEP file ID: {params.get('step_file_id')}")
        ai_meta = params.get("ai_metadata", {})
        if ai_meta:
            print(f"Pipeline: {ai_meta.get('pipeline')}")
            print(f"Provider: {ai_meta.get('provider')}")
        break
    elif status == "failed":
        print("\n❌ FAILED!")
        print(f"Error: {job.get('error_message')}")
        break
