#!/usr/bin/env python
"""
Example showing how to use GUIPySOFI's API directly (without the GUI).

This script demonstrates how to use the DataManager class to load,
process, and save SOFI data programmatically.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from guipysofi.core.data_manager import DataManager

def main():
    """Demonstrate GUIPySOFI API usage."""
    # Create a data manager with custom callbacks
    data_manager = DataManager(
        status_callback=lambda msg: print(f"Status: {msg}"),
        progress_callback=lambda val: print(f"Progress: {val}%")
    )
    
    # Get the input file path
    file_path = input("Enter the path to a TIFF stack file: ")
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return
    
    # Load the file
    print(f"Loading {file_path}...")
    success, message = data_manager.load_file(file_path)
    if not success:
        print(f"Error: {message}")
        return
    
    # Display information about the loaded data
    print(f"Loaded {data_manager.total_frames} frames with shape {data_manager.data.shape}")
    
    # Show the first frame
    plt.figure(figsize=(8, 8))
    plt.imshow(data_manager.data[0], cmap='gray')
    plt.title("First frame")
    plt.axis('off')
    plt.show()
    
    # Ask user for parameters
    order = int(input("Enter SOFI order (2-8): "))
    frames = min(int(input("Enter number of frames to use: ")), data_manager.total_frames)
    
    # Create parameters
    parameters = {
        'order': order,
        'frames': frames,
        'method': 'xc',  # Cross-correlation (default)
        'weight': 'none',  # No weighting (default)
        'bleach_correction': True,  # Apply bleaching correction
        'drift_correction': False,  # Do not apply drift correction (not reliable)
        'deconvolution': False,  # Do not apply deconvolution
    }
    
    # Run SOFI analysis
    print(f"Running SOFI analysis with order {order}...")
    success, message = data_manager.run_sofi(parameters)
    if not success:
        print(f"Error: {message}")
        return
    
    # Display the result
    plt.figure(figsize=(10, 10))
    plt.imshow(data_manager.sofi_result, cmap='viridis')
    plt.title(f"{order}-order SOFI result")
    plt.colorbar(shrink=0.8, label='Intensity')
    plt.axis('off')
    plt.show()
    
    # Save the result
    save_path = input("Enter path to save SOFI result (or press Enter to skip): ")
    if save_path:
        success, message = data_manager.save_result(save_path)
        if success:
            print(f"Successfully saved result to {save_path}")
        else:
            print(f"Error saving result: {message}")

if __name__ == "__main__":
    main() 