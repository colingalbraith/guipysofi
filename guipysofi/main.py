"""
Main Entry Point for GUIPySOFI.

This module provides the main entry point for the GUIPySOFI application.
"""

import sys
import os
import warnings

# Initialize multithreading optimizations before other imports
from guipysofi.core.optimization import configure_numba

# Configure Numba if available
thread_count = configure_numba()


def setup_environment():
    """Set up the environment for the application."""
    # Configure matplotlib to use a non-interactive backend
    import matplotlib
    matplotlib.use('Agg')  # Use Agg backend for better performance
    
    # Suppress warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    
    # Configure NumPy
    import numpy as np
    np.seterr(invalid='ignore')  # Ignore invalid value warnings
    
    # Configure logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Print initialization info
    logger = logging.getLogger("guipysofi")
    logger.info(f"Initialized with {thread_count} worker threads" if thread_count else "Initialized")
    
    return logger


def launch_gui():
    """
    Launch the GUIPySOFI GUI.
    
    This function initializes and launches the GUIPySOFI application.
    """
    # Set up environment
    logger = setup_environment()
    
    try:
        # Import tkinterdnd2
        try:
            from tkinterdnd2 import TkinterDnD
        except ImportError:
            logger.error("Could not import tkinterdnd2. Please install it with: pip install tkinterdnd2")
            print("ERROR: Could not import tkinterdnd2. Please install it with: pip install tkinterdnd2")
            sys.exit(1)
        
        # Import GUI
        from guipysofi.ui.gui import SOFIGUI
        
        # Check for PySOFI
        try:
            import pysofi
            logger.info(f"Found PySOFI version: {getattr(pysofi, '__version__', 'Unknown')}")
            
            # Verify PySOFI package integrity
            if hasattr(pysofi, 'pysofi') and hasattr(pysofi.pysofi, 'PysofiData'):
                logger.info("PySOFI package structure verified - using official PySOFI for all calculations")
            else:
                logger.warning("PySOFI package structure looks non-standard - SOFI analysis may fail")
                print("WARNING: PySOFI package structure looks non-standard - please install the official PySOFI package")
                
        except ImportError:
            logger.warning("PySOFI not found. Some functionality will be limited.")
            print("WARNING: PySOFI not found. Some functionality will be limited.")
            print("To install PySOFI: pip install pysofi")
        
        # Create root window
        logger.info("Creating main window")
        root = TkinterDnD.Tk()
        
        # Set icon if available
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'icon.png')
            if os.path.exists(icon_path):
                from PIL import Image, ImageTk
                icon = ImageTk.PhotoImage(Image.open(icon_path))
                root.iconphoto(True, icon)
        except Exception as e:
            logger.warning(f"Could not set application icon: {str(e)}")
        
        # Initialize GUI
        app = SOFIGUI(root)
        
        # Run the application
        logger.info("Starting main loop")
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Error launching GUI: {str(e)}", exc_info=True)
        print(f"ERROR: Failed to launch GUIPySOFI: {str(e)}")
        sys.exit(1)


def main():
    """Main entry point for the application."""
    launch_gui()


if __name__ == "__main__":
    main() 