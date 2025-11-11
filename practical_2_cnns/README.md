# Practical 2: Convolutional Neural Networks (CNNs)

## 🎯 Learning Objectives

By the end of this practical, you will:
- Understand how convolutional layers work
- Build CNNs for image classification
- Learn about pooling, padding, and stride
- Implement data augmentation techniques
- Work with popular CNN architectures

## 📚 Topics Covered

1. **Convolution Operations**
   - Filters/kernels
   - Feature maps
   - Receptive fields
   - Parameter sharing

2. **CNN Architecture Components**
   - Convolutional layers
   - Pooling layers (Max, Average)
   - Batch normalization
   - Dropout for regularization

3. **Building CNNs**
   - LeNet architecture
   - VGG-style networks
   - ResNet concepts
   - Skip connections

4. **Data Augmentation**
   - Random flips and rotations
   - Color jittering
   - Cropping and resizing
   - Why augmentation helps

5. **Training CNNs**
   - CIFAR-10 dataset
   - Learning rate scheduling
   - Monitoring overfitting
   - Model evaluation

## 🛠️ Prerequisites

- Completion of Practical 1 (Neural Networks basics)
- Understanding of image data representation
- Familiarity with PyTorch basics

## 📝 Exercises

The notebook contains the following exercises:

1. **Exercise 2.1**: Understand convolution operations
2. **Exercise 2.2**: Build a simple CNN from scratch
3. **Exercise 2.3**: Implement data augmentation
4. **Exercise 2.4**: Train on CIFAR-10
5. **Exercise 2.5**: Experiment with deeper architectures

## 🚀 Getting Started

1. Open `notebook.ipynb` in Jupyter
2. Make sure you have completed Practical 1
3. Follow the instructions and complete the TODOs
4. Run training and observe convergence

## 📖 Additional Resources

- [CS231n Convolutional Neural Networks](http://cs231n.github.io/convolutional-networks/)
- [A guide to convolution arithmetic](https://github.com/vdumoulin/conv_arithmetic)
- [PyTorch CNN Tutorial](https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html)
- [ResNet Paper](https://arxiv.org/abs/1512.03385)
- [Understanding CNNs Visually](https://setosa.io/ev/image-kernels/)

## ⏱️ Estimated Time

3-4 hours

## 💡 Tips

- Visualize filters and feature maps to understand what the network learns
- Start with small networks and gradually increase complexity
- Use GPU if available for faster training
- Monitor both training and validation metrics
