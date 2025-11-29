"""
Diagnose Shap-E model loading issue.
"""
import sys
import traceback
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("SHAP-E DIAGNOSTIC TOOL")
print("=" * 70)
print()

# Check imports
print("1. Checking imports...")
try:
    import torch
    print(f"   [OK] PyTorch {torch.__version__}")
    print(f"   [OK] CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"   [OK] GPU: {torch.cuda.get_device_name(0)}")
except Exception as e:
    print(f"   [FAIL] PyTorch import failed: {e}")
    sys.exit(1)

try:
    from shap_e.diffusion.sample import sample_latents
    from shap_e.models.download import load_model, load_config
    print("   [OK] Shap-E imports successful")
except Exception as e:
    print(f"   [FAIL] Shap-E import failed: {e}")
    print("\n   Install with: cd docs/useful_projects/shap-e-main && pip install -e .")
    sys.exit(1)

print()

# Check device
print("2. Checking device...")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"   Device: {device}")
if device.type == 'cuda':
    mem = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f"   GPU Memory: {mem:.1f} GB")
print()

# Try loading transmitter
print("3. Loading transmitter model...")
try:
    transmitter = load_model('transmitter', device=device)
    print("   ✅ Transmitter loaded successfully!")
except Exception as e:
    print(f"   ❌ Transmitter failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print()

# Try loading text300M (THIS IS WHERE IT FAILS)
print("4. Loading text300M model (this may take a while)...")
try:
    print("   Downloading/loading text300M (~500 MB)...")
    text_model = load_model('text300M', device=device)
    print("   ✅ text300M loaded successfully!")
except Exception as e:
    print(f"   ❌ text300M failed!")
    print(f"   Error type: {type(e).__name__}")
    print(f"   Error message: {str(e)}")
    print(f"   Error repr: {repr(e)}")
    print("\n   Full traceback:")
    traceback.print_exc()

    print("\n" + "=" * 70)
    print("DIAGNOSIS:")
    print("=" * 70)

    if "out of memory" in str(e).lower() or "cuda" in str(e).lower():
        print("   ⚠️  GPU MEMORY ISSUE")
        print("   Your RTX 3050 Ti (4GB) may not have enough memory.")
        print("\n   SOLUTION: Switch to CPU mode")
        print("   Edit backend/app/services/shap_e.py line 63:")
        print("   Change: device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')")
        print("   To:     device = torch.device('cpu')  # Force CPU")

    elif "connection" in str(e).lower() or "download" in str(e).lower():
        print("   ⚠️  DOWNLOAD ISSUE")
        print("   Model download from OpenAI failed.")
        print("\n   SOLUTION: Check internet connection and try again")

    else:
        print("   ⚠️  UNKNOWN ISSUE")
        print("   Check the error message above for details.")

    sys.exit(1)

print()

# Try loading diffusion config
print("5. Loading diffusion config...")
try:
    from shap_e.diffusion.gaussian_diffusion import diffusion_from_config
    diffusion = diffusion_from_config(load_config('diffusion'))
    print("   ✅ Diffusion config loaded successfully!")
except Exception as e:
    print(f"   ❌ Diffusion config failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 70)
print("✅ ALL MODELS LOADED SUCCESSFULLY!")
print("=" * 70)
print()
print("Shap-E is ready to use!")
print("Try generating a model in the app now.")
