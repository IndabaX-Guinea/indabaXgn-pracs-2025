# Quick Start Guide

Welcome to the Deep Learning IndabaX Guinea Practicals 2025!

## Getting Started in 5 Minutes

### 1. Clone the Repository
```bash
git clone https://github.com/IndabaX-Guinea/indabaXgn-pracs-2025.git
cd indabaXgn-pracs-2025
```

### 2. Set Up Your Environment

**Option A: Using Virtual Environment (Recommended)**
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Option B: Using Conda**
```bash
# Create conda environment
conda create -n indabax python=3.8

# Activate it
conda activate indabax

# Install dependencies
pip install -r requirements.txt
```

### 3. Verify Your Setup
```bash
python setup_check.py
```

This will check if all required packages are installed correctly.

### 4. Start Learning!
```bash
# Launch Jupyter Notebook
jupyter notebook
```

Then navigate to `practical_1_intro_to_nn/notebook.ipynb` and start learning!

## What's Included?

### Practicals

1. **Practical 1: Introduction to Neural Networks**
   - Duration: 2-3 hours
   - Topics: Basic neural networks, forward/backward propagation, training
   - Dataset: MNIST

2. **Practical 2: Convolutional Neural Networks**
   - Duration: 3-4 hours
   - Topics: CNNs, data augmentation, image classification
   - Dataset: CIFAR-10

3. **Practical 3: Recurrent Neural Networks**
   - Duration: 3-4 hours
   - Topics: RNNs, LSTMs, GRUs, text processing
   - Datasets: Text datasets

4. **Practical 4: Advanced Topics**
   - Duration: 4-5 hours
   - Topics: Transfer learning, attention, transformers
   - Datasets: Various

5. **Practical 5: Deep Learning Projects**
   - Duration: 6-8 hours
   - Topics: End-to-end project implementation
   - Datasets: Your choice!

### Support Files

- **utils/**: Helper functions for training and visualization
- **data/**: Directory for storing datasets (auto-downloaded)
- **requirements.txt**: All required Python packages
- **setup_check.py**: Setup verification script

## Tips for Success

✅ **Do:**
- Work through practicals in order
- Experiment with different parameters
- Ask questions and discuss with peers
- Save your work regularly
- Use GPU if available (faster training)

❌ **Don't:**
- Skip the exercises - they're crucial for learning
- Just copy solutions without understanding
- Ignore error messages - they teach you debugging
- Compare yourself to others - learn at your own pace

## Troubleshooting

### Import Errors
```bash
# Make sure you activated your environment
# Then reinstall requirements
pip install -r requirements.txt
```

### CUDA/GPU Issues
```bash
# Check if PyTorch detects your GPU
python -c "import torch; print(torch.cuda.is_available())"

# If False, you might need to reinstall PyTorch
# Visit: https://pytorch.org/get-started/locally/
```

### Jupyter Not Starting
```bash
# Reinstall Jupyter
pip install --upgrade jupyter notebook

# Or use JupyterLab
pip install jupyterlab
jupyter lab
```

### Out of Memory Errors
- Reduce batch size
- Use smaller models
- Restart your kernel
- Close other applications

## Getting Help

1. **Check the practical README**: Each practical has detailed instructions
2. **Review the solutions**: Solutions are provided but try first!
3. **Ask questions**: Create an issue on GitHub
4. **Collaborate**: Discuss with fellow participants

## Additional Resources

- [PyTorch Tutorials](https://pytorch.org/tutorials/)
- [TensorFlow Tutorials](https://www.tensorflow.org/tutorials)
- [Deep Learning Book](https://www.deeplearningbook.org/)
- [Fast.ai Course](https://course.fast.ai/)

## Next Steps

Once you complete all practicals:
1. Build your own project (Practical 5)
2. Share your work with the community
3. Contribute improvements to this repository
4. Keep learning and experimenting!

---

**Happy Learning! 🚀**

For detailed information, see the main [README.md](README.md)
