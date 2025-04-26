#!/usr/bin/env python
"""
Simple example showing how to use GUIPySOFI.

This script demonstrates the simplest way to launch the GUIPySOFI GUI.
"""

# Import the launch_gui function from guipysofi
from guipysofi import launch_gui, PYSOFI_AVAILABLE, __version__

def main():
    """Launch the GUIPySOFI GUI."""
    print(f"GUIPySOFI version: {__version__}")
    print(f"PySOFI available: {'Yes' if PYSOFI_AVAILABLE else 'No'}")
    
    if not PYSOFI_AVAILABLE:
        print("Warning: PySOFI not found. Some functionality will be limited.")
        print("To install PySOFI: pip install pysofi")
    
    # Launch the GUI
    print("Launching GUIPySOFI GUI...")
    launch_gui()

if __name__ == "__main__":
    main() 