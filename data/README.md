# Data Directory

This directory is for storing datasets used in the practical exercises.

## Directory Structure

```
data/
├── raw/           # Original, immutable data
├── processed/     # Cleaned and preprocessed data
├── external/      # Data from third-party sources
└── README.md      # This file
```

## Datasets Used in Practicals

### Practical 1: Introduction to Neural Networks
- **MNIST**: Handwritten digit dataset
- Automatically downloaded via PyTorch/TensorFlow datasets

### Practical 2: Convolutional Neural Networks
- **CIFAR-10**: 10-class image classification dataset
- Automatically downloaded via PyTorch/TensorFlow datasets

### Practical 3: Recurrent Neural Networks
- **Text datasets**: Various text corpora
- Will be provided or downloaded programmatically

### Practical 4: Advanced Topics
- **ImageNet subset** or pre-downloaded features
- **Custom datasets** as needed

### Practical 5: Projects
- Datasets will vary based on chosen projects

## Downloading Datasets

Most datasets will be downloaded automatically when you run the notebooks. However, if you need to download datasets manually:

```python
# Example for PyTorch
from torchvision import datasets

# Downloads to ./data directory
datasets.MNIST('./data', download=True)
datasets.CIFAR10('./data', download=True)
```

## Important Notes

- Large datasets (>100MB) are excluded from git via `.gitignore`
- Downloaded datasets will be cached locally
- Do not commit large data files to the repository
- For custom datasets, provide download links in the practical README

## Data License

Please ensure you comply with the licenses of any datasets you use:
- MNIST: Public domain
- CIFAR-10: MIT License
- Check specific licenses for other datasets
