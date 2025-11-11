#!/usr/bin/env python3
"""
Setup verification script for Deep Learning IndabaX Guinea Practicals 2025

Run this script after installing requirements to verify your setup.
"""

import sys

def check_import(module_name, package_name=None):
    """Check if a module can be imported."""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        print(f"✓ {package_name} is installed")
        return True
    except ImportError:
        print(f"✗ {package_name} is NOT installed")
        return False

def main():
    print("=" * 60)
    print("Deep Learning IndabaX Guinea 2025 - Setup Verification")
    print("=" * 60)
    print()
    
    required_packages = [
        ('numpy', 'NumPy'),
        ('pandas', 'Pandas'),
        ('matplotlib', 'Matplotlib'),
        ('sklearn', 'scikit-learn'),
        ('torch', 'PyTorch'),
        ('torchvision', 'torchvision'),
        ('tensorflow', 'TensorFlow'),
        ('transformers', 'Hugging Face Transformers'),
        ('PIL', 'Pillow'),
        ('cv2', 'OpenCV'),
        ('tqdm', 'tqdm'),
    ]
    
    print("Checking required packages:")
    print("-" * 60)
    
    all_installed = True
    for module, package in required_packages:
        if not check_import(module, package):
            all_installed = False
    
    print()
    print("=" * 60)
    
    if all_installed:
        print("✓ All required packages are installed!")
        print()
        print("You're ready to start the practicals!")
        print()
        print("To get started:")
        print("  1. Navigate to practical_1_intro_to_nn/")
        print("  2. Open notebook.ipynb in Jupyter")
        print("  3. Follow the instructions")
    else:
        print("✗ Some packages are missing.")
        print()
        print("Please install the missing packages:")
        print("  pip install -r requirements.txt")
    
    print("=" * 60)
    
    # Check PyTorch GPU availability
    try:
        import torch
        print()
        print("PyTorch Information:")
        print(f"  Version: {torch.__version__}")
        print(f"  CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"  CUDA version: {torch.version.cuda}")
            print(f"  GPU(s) detected: {torch.cuda.device_count()}")
        else:
            print("  Running on CPU (GPU not available)")
    except ImportError:
        pass
    
    print("=" * 60)

if __name__ == "__main__":
    main()
