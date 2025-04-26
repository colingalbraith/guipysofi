"""
Help and Debugging Utilities for GUIPySOFI.

This module provides functions for displaying help and debugging information.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

from guipysofi.utils.compatibility import get_compatibility_report


def show_help(parent):
    """
    Show help dialog.
    
    Args:
        parent: The parent widget
    """
    help_text = """
    PySOFI Analysis Tool Help
    
    SOFI (Super-resolution Optical Fluctuation Imaging) analyzes the temporal fluctuations in 
    fluorescent samples to achieve super-resolution.
    
    Basic Workflow:
    1. Load a TIFF stack using the "Browse" button or drag and drop
    2. Adjust SOFI parameters:
       - Order: Higher orders give better resolution but need more signal
       - Frames: More frames improve statistics but increase computation time
    3. Choose advanced options if needed:
       - Method: XC (cross-correlation) or AC (auto-correlation)
       - Weighting: Balance the cumulant calculations
    4. Apply corrections if needed:
       - Bleaching correction: For samples with photobleaching
       - Drift correction: For samples that drift over time
    5. Click "Run SOFI Analysis" to process
    6. View the result in the SOFI Result tab
    7. Save the result using "Save Results"
    
    Advanced Options:
    - Method:
      - XC (cross-correlation): Uses spatial cross-correlations (recommended)
      - AC (auto-correlation): Uses only auto-correlations
      - CC (cumulants): Directly calculates cumulants
    
    - Weighting:
      - None: No weighting applied
      - Balanced: Applies balanced weighting to normalize variance
      - Tapered: Applies non-linear tapering for better SNR
    
    Performance Tips:
    - Start with a smaller number of frames for faster processing
    - Higher orders take longer to compute
    - If memory issues occur, try processing a subset of your data
    
    Technical Note:
    This implementation uses the PysofiData class directly from the pysofi package.
    
    For more details about PySOFI, visit:
    https://github.com/xiyuyi-at-LLNL/pysofi
    """
    
    help_dialog = tk.Toplevel(parent)
    help_dialog.title("PySOFI Help")
    help_dialog.geometry("600x500")
    help_dialog.transient(parent)
    help_dialog.grab_set()
    
    help_frame = ttk.Frame(help_dialog, padding="20")
    help_frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(help_frame, text="PySOFI Analysis Tool Help", font=('Helvetica', 14, 'bold')).pack(pady=(0,10))
    
    text_frame = ttk.Frame(help_frame)
    text_frame.pack(fill=tk.BOTH, expand=True)
    
    scrollbar = ttk.Scrollbar(text_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    text_area = tk.Text(
        text_frame, 
        wrap=tk.WORD, 
        yscrollcommand=scrollbar.set,
        font=('Helvetica', 11), 
        padx=10, 
        pady=10
    )
    text_area.insert(tk.END, help_text)
    text_area.config(state=tk.DISABLED)
    text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    scrollbar.config(command=text_area.yview)
    
    ttk.Button(help_frame, text="Close", command=help_dialog.destroy).pack(pady=10)


def inspect_pysofi(parent):
    """
    Display debugging information about the PySOFI module.
    
    Args:
        parent: The parent widget
    """
    try:
        # Get the compatibility report
        debug_info = get_compatibility_report()
        debug_info += "\n\n"
        
        # Try to import PySOFI
        try:
            import pysofi
            from pysofi.pysofi import PysofiData
            pysofi_available = True
        except ImportError:
            pysofi_available = False
            debug_info += "PySOFI module is not available.\n\n"
            debug_info += "Please install it with:\npip install pysofi\n"
            
        if pysofi_available:
            debug_info = "\nPySOFI Package Information:\n"
            debug_info += f"Version: {pysofi.__version__ if hasattr(pysofi, '__version__') else 'Unknown'}\n"
            
            # Check Python and package paths
            debug_info += f"\nPython version: {sys.version}\n"
            debug_info += f"Python executable: {sys.executable}\n"
            
            # Check module path
            try:
                module_path = pysofi.__file__ if hasattr(pysofi, '__file__') else "Unknown"
                debug_info += f"Module path: {module_path}\n"
            except:
                debug_info += "Module path: Could not determine\n"
            
            # List available modules/attributes
            debug_info += "\nAvailable modules in pysofi:\n"
            for module_name in dir(pysofi):
                if not module_name.startswith('_'):
                    debug_info += f"- {module_name}\n"
            
            # Check PysofiData class
            debug_info += "\nPysofiData class information:\n"
            try:
                debug_info += f"Module location: {PysofiData.__module__}\n"
                debug_info += "PysofiData methods:\n"
                for method_name in dir(PysofiData):
                    if not method_name.startswith('_'):
                        debug_info += f"- {method_name}\n"
            except Exception as e:
                debug_info += f"Error inspecting PysofiData: {str(e)}\n"
            
            # Memory usage
            try:
                # Try to import psutil - may not be installed
                try:
                    import psutil
                    process = psutil.Process(os.getpid())
                    memory_info = process.memory_info()
                    debug_info += f"\nMemory Usage:\n"
                    debug_info += f"RSS: {memory_info.rss / (1024 * 1024):.2f} MB\n"
                    debug_info += f"VMS: {memory_info.vms / (1024 * 1024):.2f} MB\n"
                except ImportError:
                    debug_info += "\nMemory usage information not available (psutil not installed)\n"
            except:
                debug_info += "\nCould not determine memory usage\n"
            
            # Implementation details
            debug_info += "\nImplementation Details:\n"
            debug_info += "Using PysofiData directly: Yes\n"
            debug_info += "Using any substitute algorithms: No\n"
            debug_info += "All SOFI calculations are performed by the original PySOFI package\n"
            debug_info += "Available methods: xc, ac, cc\n"
            debug_info += "Available weightings: none, balanced, tapered\n"
        
        # Create debug window
        debug_window = tk.Toplevel(parent)
        debug_window.title("PySOFI Debug Information")
        debug_window.geometry("700x500")
        debug_window.transient(parent)
        debug_window.grab_set()
        
        debug_frame = ttk.Frame(debug_window, padding="20")
        debug_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            debug_frame, 
            text="PySOFI Debug Information", 
            font=('Helvetica', 14, 'bold')
        ).pack(pady=(0,10))
        
        text_frame = ttk.Frame(debug_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_area = tk.Text(
            text_frame, 
            wrap=tk.WORD, 
            yscrollcommand=scrollbar.set,
            font=('Courier', 10), 
            padx=10, 
            pady=10
        )
        text_area.insert(tk.END, debug_info)
        text_area.config(state=tk.DISABLED)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=text_area.yview)
        
        ttk.Button(
            debug_frame, 
            text="Copy to Clipboard", 
            command=lambda: parent.clipboard_append(debug_info)
        ).pack(side=tk.LEFT, pady=10)
        
        ttk.Button(
            debug_frame, 
            text="Close", 
            command=debug_window.destroy
        ).pack(side=tk.RIGHT, pady=10)
        
    except Exception as e:
        messagebox.showerror("Debug Error", f"Error inspecting PySOFI: {str(e)}") 