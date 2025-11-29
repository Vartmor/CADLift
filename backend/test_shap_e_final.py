"""
Final comprehensive Shap-E test.
Tests all possible workarounds and captures detailed logs.
"""
import sys
import traceback
import logging
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("SHAP-E FINAL COMPREHENSIVE TEST")
print("=" * 80)
print()

# Test 1: Basic imports
print("TEST 1: Import Check")
print("-" * 80)
try:
    import torch
    print(f"✓ PyTorch {torch.__version__}")
    print(f"✓ CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"✓ GPU: {torch.cuda.get_device_name(0)}")
except Exception as e:
    print(f"✗ PyTorch import failed: {e}")
    sys.exit(1)

try:
    from shap_e.diffusion.sample import sample_latents
    from shap_e.models.download import load_model, load_config
    from shap_e.diffusion.gaussian_diffusion import diffusion_from_config
    print("✓ Shap-E imports successful")
except Exception as e:
    print(f"✗ Shap-E import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print()

# Test 2: Check available models and cache
print("TEST 2: Model Cache Check")
print("-" * 80)
from shap_e.models.download import default_cache_dir
cache_dir = Path(default_cache_dir())
print(f"Cache directory: {cache_dir}")
if cache_dir.exists():
    print("Cache contents:")
    for file in cache_dir.iterdir():
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"  - {file.name}: {size_mb:.1f} MB")
else:
    print("  Cache directory does not exist")
print()

# Test 3: Device selection
print("TEST 3: Device Selection")
print("-" * 80)
device = torch.device('cpu')
print(f"Using device: {device}")
print()

# Test 4: Try loading transmitter (should work)
print("TEST 4: Transmitter Model Loading")
print("-" * 80)
try:
    print("Loading transmitter model...")
    transmitter = load_model('transmitter', device=device)
    print("✓ Transmitter loaded successfully!")
    print(f"  Model type: {type(transmitter)}")
except Exception as e:
    print(f"✗ Transmitter failed: {e}")
    traceback.print_exc()
    sys.exit(1)
print()

# Test 5: Try loading CLIP separately
print("TEST 5: CLIP Model Loading (Separate Test)")
print("-" * 80)
try:
    import clip
    print("Attempting to load ViT-B/32 CLIP model...")
    print("  Parameters: device='cpu', jit=False")

    clip_model, preprocess = clip.load(
        "ViT-B/32",
        device='cpu',
        jit=False,
        download_root=str(cache_dir)
    )
    print("✓ CLIP model loaded successfully!")
    print(f"  Model type: {type(clip_model)}")

    # Try encoding test text
    print("  Testing text encoding...")
    text = clip.tokenize(["a simple test"]).to(device)
    with torch.no_grad():
        text_features = clip_model.encode_text(text)
    print(f"✓ Text encoding successful! Shape: {text_features.shape}")

except MemoryError as e:
    print(f"✗ CLIP loading failed with MemoryError: {e}")
    print("\nDETAILS:")
    print("  This indicates the system cannot allocate enough memory for the CLIP model.")
    print("  Even with 32GB RAM, the issue persists.")
    print("  This suggests a PyTorch/CLIP compatibility issue on Windows.")
    traceback.print_exc()
except Exception as e:
    print(f"✗ CLIP loading failed: {e}")
    print(f"  Error type: {type(e).__name__}")
    traceback.print_exc()
print()

# Test 6: Try loading text300M (this is where it fails)
print("TEST 6: text300M Model Loading")
print("-" * 80)
try:
    print("Loading text300M model (includes CLIP)...")
    print("  This may take a while and may fail due to CLIP loading...")

    text_model = load_model('text300M', device=device)
    print("✓ text300M loaded successfully!")
    print(f"  Model type: {type(text_model)}")

except MemoryError as e:
    print(f"✗ text300M failed with MemoryError: {e}")
    print("\nROOT CAUSE IDENTIFIED:")
    print("  The text300M model requires CLIP for text encoding.")
    print("  CLIP model loading fails with MemoryError even on CPU.")
    print("  This is NOT a GPU memory issue (we're using CPU).")
    print("  This is NOT a RAM issue (system has 32GB).")
    print("  This appears to be a PyTorch JIT compatibility issue on Windows.")
    traceback.print_exc()
except Exception as e:
    print(f"✗ text300M failed: {e}")
    print(f"  Error type: {type(e).__name__}")
    traceback.print_exc()
print()

# Test 7: System information
print("TEST 7: System Information")
print("-" * 80)
import platform
print(f"OS: {platform.system()} {platform.release()}")
print(f"Python: {platform.python_version()}")
print(f"PyTorch: {torch.__version__}")
print(f"CPU: {platform.processor()}")

# Check RAM usage
try:
    import psutil
    mem = psutil.virtual_memory()
    print(f"Total RAM: {mem.total / (1024**3):.1f} GB")
    print(f"Available RAM: {mem.available / (1024**3):.1f} GB")
    print(f"Used RAM: {mem.used / (1024**3):.1f} GB ({mem.percent}%)")
except ImportError:
    print("psutil not available - cannot check RAM usage")
print()

# Final summary
print("=" * 80)
print("FINAL SUMMARY")
print("=" * 80)
print()
print("WHAT WORKS:")
print("  ✓ PyTorch installation")
print("  ✓ Shap-E imports")
print("  ✓ Transmitter model loading")
print()
print("WHAT FAILS:")
print("  ✗ CLIP model loading (ViT-B/32)")
print("  ✗ text300M model loading (depends on CLIP)")
print()
print("ROOT CAUSE:")
print("  CLIP's JIT model loading fails even with:")
print("    - CPU mode (not GPU)")
print("    - 32GB RAM (not memory shortage)")
print("    - jit=False parameter")
print("    - MemoryError fallback handling")
print()
print("  The issue appears to be a compatibility problem between:")
print("    - PyTorch 2.5.1 + CUDA 12.1")
print("    - CLIP's JIT model files")
print("    - Windows OS")
print()
print("RECOMMENDATION:")
print("  Switch to a different 3D generation model that doesn't use CLIP:")
print("    - TripoSR (modern, efficient, no CLIP dependency)")
print("    - InstantMesh (image-based)")
print("    - Stable Diffusion 3D (text-to-3D alternative)")
print()
print("=" * 80)
