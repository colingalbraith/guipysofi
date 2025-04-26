"""
Optimization Module for GUIPySOFI.

This module provides performance optimizations for SOFI calculations.
IMPORTANT: These optimizations are for supporting operations only and 
NEVER replace the core PySOFI algorithms. All actual SOFI calculations
are performed by the PySOFI package.
"""

import os
import numpy as np


# Try to import optional dependencies
try:
    import numba
    from numba import jit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False


def get_optimal_thread_count():
    """
    Determine the optimal number of threads to use for parallel processing.
    
    Returns:
        int: The optimal number of threads
    """
    try:
        import psutil
        # Use physical cores rather than logical cores for better performance
        num_physical_cores = psutil.cpu_count(logical=False)
        if num_physical_cores is None:
            # Fall back to logical cores if physical count not available
            num_physical_cores = psutil.cpu_count()
            
        # Reserve one core for the UI
        optimal_threads = max(1, num_physical_cores - 1)
        
        # Ensure we don't excessively split the work
        return min(optimal_threads, 8)  # Cap at 8 threads
    except ImportError:
        # Default to 2 threads if psutil not available
        return 2


def configure_numba():
    """Configure Numba for optimal performance."""
    if not NUMBA_AVAILABLE:
        return
    
    # Set the number of threads for Numba
    thread_count = get_optimal_thread_count()
    numba.set_num_threads(thread_count)
    
    # Set environment variable for other libraries that might use OpenMP
    os.environ['OMP_NUM_THREADS'] = str(thread_count)
    os.environ['MKL_NUM_THREADS'] = str(thread_count)
    os.environ['OPENBLAS_NUM_THREADS'] = str(thread_count)
    
    return thread_count


if NUMBA_AVAILABLE:
    # JIT-compiled functions for faster processing
    
    @jit(nopython=True, parallel=True)
    def fast_cross_correlation(data, frames, height, width):
        """
        Faster implementation of cross-correlation calculation using Numba.
        
        Args:
            data: 3D numpy array of shape (frames, height, width)
            frames: Number of frames
            height: Image height
            width: Image width
            
        Returns:
            4D numpy array of cross-correlation result
        """
        result = np.zeros((height, width, height, width), dtype=np.float32)
        
        # Calculate mean of each pixel over time
        means = np.zeros((height, width), dtype=np.float32)
        for i in prange(height):
            for j in range(width):
                pixel_sum = 0.0
                for f in range(frames):
                    pixel_sum += data[f, i, j]
                means[i, j] = pixel_sum / frames
        
        # Calculate cross-correlation
        for i in prange(height):
            for j in range(width):
                for k in range(height):
                    for l in range(width):
                        corr_sum = 0.0
                        for f in range(frames):
                            corr_sum += (data[f, i, j] - means[i, j]) * (data[f, k, l] - means[k, l])
                        result[i, j, k, l] = corr_sum / frames
                        
        return result
    
    @jit(nopython=True, parallel=True)
    def fast_normalize_data(data):
        """
        Faster implementation of data normalization using Numba.
        
        Args:
            data: Numpy array to normalize
            
        Returns:
            Normalized numpy array
        """
        min_val = np.min(data)
        max_val = np.max(data)
        
        if max_val == min_val:
            return np.zeros_like(data)
            
        result = np.zeros_like(data)
        factor = 1.0 / (max_val - min_val)
        
        # Normalize each element
        for i in prange(data.shape[0]):
            for j in range(data.shape[1]):
                result[i, j] = (data[i, j] - min_val) * factor
                
        return result
else:
    # Fallback non-optimized functions
    def fast_cross_correlation(data, frames, height, width):
        """
        Standard implementation of cross-correlation calculation.
        
        Args:
            data: 3D numpy array of shape (frames, height, width)
            frames: Number of frames
            height: Image height
            width: Image width
            
        Returns:
            4D numpy array of cross-correlation result
        """
        # Reshape for vectorized operations
        data_reshaped = data.reshape(frames, -1)
        
        # Calculate mean of each pixel over time
        means = np.mean(data_reshaped, axis=0)
        
        # Subtract means
        data_centered = data_reshaped - means
        
        # Calculate correlation matrix
        correlation = np.dot(data_centered.T, data_centered) / frames
        
        # Reshape back to 4D
        return correlation.reshape(height, width, height, width)
    
    def fast_normalize_data(data):
        """
        Standard implementation of data normalization.
        
        Args:
            data: Numpy array to normalize
            
        Returns:
            Normalized numpy array
        """
        min_val = np.min(data)
        max_val = np.max(data)
        
        if max_val == min_val:
            return np.zeros_like(data)
            
        return (data - min_val) / (max_val - min_val) 