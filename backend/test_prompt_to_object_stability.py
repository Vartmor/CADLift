"""
Test prompt-to-object with 4 different prompts (one at a time).
Run each test sequentially to ensure GPU memory is properly managed.
"""
import requests
import time
import os
import sys

BASE_URL = "http://localhost:8000"

# Test prompts: 2 creative + 2 engineering
TEST_PROMPTS = [
    ("A fantasy dragon statue with spread wings", "creative"),
    ("A decorative ceramic vase with floral patterns", "creative"),
    ("A coffee cup with curved handle, 90mm tall, 75mm diameter", "engineering"),
    ("M8 hex bolt, 40mm long with threaded shaft", "engineering"),
]

def wait_for_job(job_id: str, timeout: int = 300):
    """Poll job status until completion or timeout."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(f"{BASE_URL}/api/v1/jobs/{job_id}")
            resp.raise_for_status()
            job = resp.json()
            status = job.get("status", "unknown")
            progress = job.get("progress", 0)
            print(f"  Status: {status}, Progress: {progress}%")
            
            if status == "completed":
                return True, job
            elif status in ("failed", "error"):
                return False, job
            
            time.sleep(5)  # Poll every 5 seconds
        except Exception as e:
            print(f"  Poll error: {e}")
            time.sleep(5)
    
    return False, {"error": "Timeout"}

def run_prompt_test(prompt: str, category: str, test_num: int):
    """Run a single prompt-to-object test."""
    print(f"\n{'='*60}")
    print(f"TEST {test_num}: {category.upper()}")
    print(f"Prompt: {prompt}")
    print('='*60)
    
    try:
        # Create job using Form data (not JSON - matches API signature)
        import json
        resp = requests.post(
            f"{BASE_URL}/api/v1/jobs",
            data={
                "job_type": "prompt",
                "mode": "2d_to_3d",
                "params": json.dumps({
                    "prompt": prompt,
                    "use_ai": True,
                    "detail": 70
                })
            }
        )
        resp.raise_for_status()
        job = resp.json()
        job_id = job["id"]
        print(f"Job created: {job_id}")
        
        # Wait for completion
        success, result = wait_for_job(job_id)
        
        if success:
            print(f"\n✅ TEST {test_num} PASSED!")
            # Check for output files
            params = result.get("params", {})
            glb_id = params.get("glb_file_id")
            step_id = params.get("step_file_id")
            print(f"  GLB file ID: {glb_id}")
            print(f"  STEP file ID: {step_id}")
            
            ai_meta = params.get("ai_metadata", {})
            if ai_meta:
                print(f"  Pipeline: {ai_meta.get('pipeline', 'N/A')}")
                print(f"  Provider: {ai_meta.get('provider', 'N/A')}")
        else:
            print(f"\n❌ TEST {test_num} FAILED!")
            print(f"  Error: {result.get('error_message', result.get('error', 'Unknown'))}")
        
        return success
        
    except Exception as e:
        print(f"\n❌ TEST {test_num} ERROR: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("PROMPT-TO-OBJECT STABILITY TEST")
    print("Testing 4 prompts one by one with memory optimizations")
    print("="*60)
    
    # Check server health first
    try:
        resp = requests.get(f"{BASE_URL}/health")
        resp.raise_for_status()
        print(f"\n✅ Server is healthy: {resp.json()}")
    except Exception as e:
        print(f"\n❌ Server not reachable: {e}")
        sys.exit(1)
    
    results = []
    for i, (prompt, category) in enumerate(TEST_PROMPTS, 1):
        success = run_prompt_test(prompt, category, i)
        results.append((prompt[:40], category, success))
        
        # Wait between tests for memory to clear
        if i < len(TEST_PROMPTS):
            print(f"\n⏳ Waiting 10 seconds before next test for GPU memory cleanup...")
            time.sleep(10)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(1 for _, _, s in results if s)
    for prompt, category, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} [{category}] {prompt}...")
    print(f"\nTotal: {passed}/{len(results)} passed")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
