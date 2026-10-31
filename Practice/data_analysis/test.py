import numpy as np
import pandas as pd
import torch
import tensorflow as tf

# Test PyTorch Tensor
x_torch = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
print("PyTorch Matrix Multiplications:\n", torch.matmul(x_torch, x_torch))

# Test TensorFlow Tensor
x_tf = tf.constant([[1.0, 2.0], [3.0, 4.0]])
print("\nTensorFlow Matrix Multiplication:\n", tf.matmul(x_tf, x_tf))