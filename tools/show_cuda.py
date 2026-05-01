import os

print("# Python‑side CUDA environment")
print("CUDA_PATH:", os.environ.get("CUDA_PATH"))
print("CUDA_HOME:", os.environ.get("CUDA_HOME"))

print("\n# CUDA / GPU detection in Python")
try:
    import torch
    print("PyTorch found:", torch.__version__)
    print("CUDA available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("CUDA version:", torch.version.cuda)
        print("GPU count:", torch.cuda.device_count())
        for i in range(torch.cuda.device_count()):
            print(f"GPU-{i}:", torch.cuda.get_device_name(i))
            print(f"  Memory: {torch.cuda.get_device_properties(i).total_memory / 1e9:.2f} GB")
except ImportError:
    print("PyTorch not installed; skipping CUDA test.")

try:
    import cupy as cp
    print("\nCuPy found:", cp.__version__)
    print("CuPy CUDA version:", cp.cuda.runtime.get_version())
except ImportError:
    print("CuPy not installed.")

print("Done.")