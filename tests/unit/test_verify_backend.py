import os
import pathlib


def _check_torch() -> bool:
    """Check Torch import and version."""
    try:
        import torch

        print(f"Torch version: {torch.__version__}")
        print(f"Torch file: {torch.__file__}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import torch: {e}")
        return False


def _check_cuda_path() -> tuple[str | None, str | None]:
    """Check CUDA_PATH environment variable."""
    cuda_path = os.environ.get("CUDA_PATH")
    print(f"\nCUDA_PATH (env): {cuda_path}")
    return cuda_path, cuda_path


def _check_kernel_import() -> tuple[bool, object]:
    """Import kernel module and check CUDA_PATH after import."""
    try:
        from computronium.acceleration import kernels as kernel

        print("Successfully imported computronium.acceleration.kernels")
        cuda_path_after = os.environ.get("CUDA_PATH")
        print(f"CUDA_PATH (after import): {cuda_path_after}")
        return True, kernel
    except ImportError as e:
        print(f"Failed to import computronium.acceleration.kernels: {e}")
        return False, None


def _validate_cuda_path(cuda_path_after: str | None) -> bool:
    """Validate CUDA_PATH exists."""
    if cuda_path_after:
        if pathlib.Path(cuda_path_after).exists():
            print(f"✅ CUDA_PATH exists: {cuda_path_after}")
            return True
        else:
            print(f"❌ CUDA_PATH does not exist: {cuda_path_after}")
            return False
    else:
        print("⚠️ CUDA_PATH not detected by kernel module")
        return True  # Not a failure, just a warning


def _check_cupy(kernel) -> bool:
    """Check CuPy availability and basic operation."""
    print("\n[Checking CuPy]...")
    print(f"HAS_CUPY: {kernel.HAS_CUPY}")
    if kernel.HAS_CUPY:
        import cupy

        print(f"CuPy version: {cupy.__version__}")
        try:
            cupy.array([1, 2, 3])
            print("✅ CuPy basic operation successful")
            return True
        except Exception as e:
            print(f"❌ CuPy operation failed: {e}")
            return False
    return True


def _check_triton() -> bool:
    """Check Triton availability."""
    print("\n[Checking Triton]...")
    try:
        from computronium.acceleration.triton_kernels import HAS_TRITON, TritonEqPropOps

        print(f"HAS_TRITON: {HAS_TRITON}")
        print(f"TritonEqPropOps.is_available(): {TritonEqPropOps.is_available()}")

        if TritonEqPropOps.is_available():
            print("✅ Triton is available")
            return True
        else:
            if not HAS_TRITON:
                print("⚠️ Triton import failed")
            elif not os.environ.get("CUDA_PATH"):
                print("⚠️ CUDA might be missing or torch.cuda.is_available() is False")
            import torch

            print(f"PyTorch CUDA available: {torch.cuda.is_available()}")
            return True
    except ImportError as e:
        print(f"Failed to import triton_kernel: {e}")
        return True  # Not a failure


def verify_backend():
    print("=" * 60)
    print("Backend Verification")
    print("=" * 60)

    # 0. Check Torch import
    print("\n[Checking Torch]...")
    _check_torch()

    # 1. Check Environment Variables
    _check_cuda_path()

    # 2. Import kernel (triggers auto-detection)
    print("\n[Importing computronium.acceleration.kernels]...")
    success, kernel = _check_kernel_import()
    if not success:
        return

    # Check detected CUDA_PATH in environment after import
    cuda_path_after = os.environ.get("CUDA_PATH")
    _validate_cuda_path(cuda_path_after)

    # 3. Check CuPy
    _check_cupy(kernel)

    # 4. Check Triton
    _check_triton()


if __name__ == "__main__":
    verify_backend()
