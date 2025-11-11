"""
Helper functions for Deep Learning IndabaX Guinea Practicals 2025
"""

import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from typing import List, Tuple, Optional


def set_seed(seed: int = 42):
    """
    Set random seed for reproducibility across numpy, torch, and random.
    
    Args:
        seed (int): Random seed value
    """
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def plot_training_history(train_losses: List[float], 
                          val_losses: Optional[List[float]] = None,
                          train_accs: Optional[List[float]] = None,
                          val_accs: Optional[List[float]] = None,
                          title: str = "Training History"):
    """
    Plot training and validation losses and accuracies.
    
    Args:
        train_losses: List of training losses
        val_losses: List of validation losses (optional)
        train_accs: List of training accuracies (optional)
        val_accs: List of validation accuracies (optional)
        title: Plot title
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    
    # Plot losses
    axes[0].plot(train_losses, label='Train Loss', marker='o')
    if val_losses:
        axes[0].plot(val_losses, label='Val Loss', marker='s')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title(f'{title} - Loss')
    axes[0].legend()
    axes[0].grid(True)
    
    # Plot accuracies
    if train_accs or val_accs:
        if train_accs:
            axes[1].plot(train_accs, label='Train Accuracy', marker='o')
        if val_accs:
            axes[1].plot(val_accs, label='Val Accuracy', marker='s')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Accuracy (%)')
        axes[1].set_title(f'{title} - Accuracy')
        axes[1].legend()
        axes[1].grid(True)
    else:
        fig.delaxes(axes[1])
    
    plt.tight_layout()
    plt.show()


def visualize_predictions(images: np.ndarray, 
                         true_labels: np.ndarray, 
                         pred_labels: np.ndarray,
                         class_names: Optional[List[str]] = None,
                         n_samples: int = 10):
    """
    Visualize predictions vs ground truth.
    
    Args:
        images: Array of images
        true_labels: Array of true labels
        pred_labels: Array of predicted labels
        class_names: List of class names (optional)
        n_samples: Number of samples to display
    """
    n_samples = min(n_samples, len(images))
    fig, axes = plt.subplots(2, 5, figsize=(15, 6))
    axes = axes.flatten()
    
    for i in range(n_samples):
        ax = axes[i]
        
        # Handle different image formats
        if images[i].shape[0] == 1:  # Grayscale
            ax.imshow(images[i][0], cmap='gray')
        elif images[i].shape[0] == 3:  # RGB
            ax.imshow(np.transpose(images[i], (1, 2, 0)))
        else:
            ax.imshow(images[i], cmap='gray')
        
        # Set title with prediction info
        true_label = class_names[true_labels[i]] if class_names else true_labels[i]
        pred_label = class_names[pred_labels[i]] if class_names else pred_labels[i]
        
        color = 'green' if true_labels[i] == pred_labels[i] else 'red'
        ax.set_title(f'True: {true_label}\nPred: {pred_label}', color=color)
        ax.axis('off')
    
    plt.tight_layout()
    plt.show()


def count_parameters(model: nn.Module) -> int:
    """
    Count the number of trainable parameters in a model.
    
    Args:
        model: PyTorch model
        
    Returns:
        Number of trainable parameters
    """
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def get_device() -> torch.device:
    """
    Get the best available device (CUDA, MPS, or CPU).
    
    Returns:
        torch.device object
    """
    if torch.cuda.is_available():
        return torch.device('cuda')
    elif torch.backends.mps.is_available():
        return torch.device('mps')
    else:
        return torch.device('cpu')


def print_model_summary(model: nn.Module):
    """
    Print a summary of the model architecture.
    
    Args:
        model: PyTorch model
    """
    print("=" * 80)
    print(f"Model Architecture: {model.__class__.__name__}")
    print("=" * 80)
    print(model)
    print("=" * 80)
    print(f"Total trainable parameters: {count_parameters(model):,}")
    print("=" * 80)


class EarlyStopping:
    """Early stopping to stop training when validation loss doesn't improve."""
    
    def __init__(self, patience: int = 7, min_delta: float = 0, verbose: bool = False):
        """
        Args:
            patience: How many epochs to wait after last improvement
            min_delta: Minimum change to qualify as improvement
            verbose: Print messages
        """
        self.patience = patience
        self.min_delta = min_delta
        self.verbose = verbose
        self.counter = 0
        self.best_loss = None
        self.early_stop = False
        
    def __call__(self, val_loss: float) -> bool:
        """
        Check if training should stop.
        
        Args:
            val_loss: Current validation loss
            
        Returns:
            True if training should stop
        """
        if self.best_loss is None:
            self.best_loss = val_loss
        elif val_loss > self.best_loss - self.min_delta:
            self.counter += 1
            if self.verbose:
                print(f'EarlyStopping counter: {self.counter} out of {self.patience}')
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_loss = val_loss
            self.counter = 0
        
        return self.early_stop


def save_checkpoint(model: nn.Module, optimizer: torch.optim.Optimizer, 
                   epoch: int, loss: float, filepath: str):
    """
    Save model checkpoint.
    
    Args:
        model: PyTorch model
        optimizer: PyTorch optimizer
        epoch: Current epoch
        loss: Current loss
        filepath: Path to save checkpoint
    """
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
    }
    torch.save(checkpoint, filepath)
    if hasattr(model, '__class__'):
        print(f'Checkpoint saved: {filepath}')


def load_checkpoint(model: nn.Module, optimizer: Optional[torch.optim.Optimizer], 
                   filepath: str) -> Tuple[int, float]:
    """
    Load model checkpoint.
    
    Args:
        model: PyTorch model
        optimizer: PyTorch optimizer (optional)
        filepath: Path to checkpoint file
        
    Returns:
        Tuple of (epoch, loss)
    """
    checkpoint = torch.load(filepath)
    model.load_state_dict(checkpoint['model_state_dict'])
    if optimizer:
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    epoch = checkpoint['epoch']
    loss = checkpoint['loss']
    print(f'Checkpoint loaded: {filepath}')
    return epoch, loss
