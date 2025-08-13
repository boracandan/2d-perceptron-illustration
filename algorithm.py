from typing import List, Tuple
import numpy as np


def train_perceptron(points: List[Tuple]) -> np.ndarray:
    # +1 in length for the bias term w0
    w = np.zeros(len(points[0]))  
    
    hyperplaneFound = False
    while not hyperplaneFound:
        hyperplaneFound = True
        for point in points:
            y = point[-1]                       # Class label (-1 or 1)
            x = np.array([1, *point[:-1]])      # Add bias term at start
            
            if y * (w @ x) <= 0:                # Misclassified
                w = w + y * x
                hyperplaneFound = False

    return w