"""
Test CLIP loading in isolation.
"""
import sys
from pathlib import Path

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

print("Testing CLIP loading...")
print()

# Step 1: Import torch
print("1. Importing PyTorch...")
try:
    import torch
    print(f"   OK - PyTorch {torch.__version__}")
except Exception as e:
    print(f"   FAIL - {e}")
    sys.exit(1)

# Step 2: Import CLIP
print("2. Importing CLIP...")
try:
    import clip
    print(f"   OK - CLIP imported")
except Exception as e:
    print(f"   FAIL - {e}")
    sys.exit(1)

# Step 3: Check if model file exists
print("3. Checking for ViT-B/32 model file...")
cache_dir = Path.home() / ".cache" / "clip"
if not cache_dir.exists():
    cache_dir = Path(__file__).parent / "shap_e_model_cache"

vit_b32_file = cache_dir / "ViT-B-32.pt"
print(f"   Looking in: {cache_dir}")
if vit_b32_file.exists():
    size_mb = vit_b32_file.stat().st_size / (1024 * 1024)
    print(f"   OK - Found ViT-B-32.pt ({size_mb:.1f} MB)")
else:
    print(f"   Not found - will download on load")

# Step 4: Attempt to load CLIP WITHOUT actually loading it
print("4. Checking CLIP load function...")
print(f"   clip.load signature: {clip.load.__code__.co_varnames}")
print(f"   Available models: {clip.available_models()}")

print()
print("=" * 60)
print("CRITICAL TEST: Will attempt to load CLIP model")
print("This is where segfaults occur.")
print("If you see this message but no output after, it crashed.")
print("=" * 60)
print()

# Step 5: Try to load CLIP
print("5. Loading CLIP ViT-B/32 with jit=False, device='cpu'...")
sys.stdout.flush()  # Force flush before potential crash

try:
    print("   Calling clip.load()...")
    sys.stdout.flush()

    model, preprocess = clip.load("ViT-B/32", device='cpu', jit=False)

    print("   SUCCESS! CLIP loaded without crash!")
    print(f"   Model type: {type(model)}")

except MemoryError as e:
    print(f"   MEMORY ERROR: {e}")
    print("   This means it tried to allocate memory but failed")

except Exception as e:
    print(f"   ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print()
print("Test completed!")
