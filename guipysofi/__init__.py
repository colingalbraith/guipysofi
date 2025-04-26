"""
GUIPySOFI: An Open Source Graphical Extension to the PySOFI Analysis Tool.

This package provides a graphical user interface for the PySOFI (Python Super-resolution 
Optical Fluctuation Imaging) analysis tool.
"""

from guipysofi.version import __version__
__author__ = "Colin Galbraith"
__email__ = "chmartin@ucsb.edu"

# Import key functions for external API
from guipysofi.main import launch_gui
from guipysofi.core.data_manager import DataManager

# Check for PySOFI availability
try:
    import pysofi
    PYSOFI_AVAILABLE = True
except ImportError:
    PYSOFI_AVAILABLE = False
    import warnings
    warnings.warn(
        "PySOFI is required for GUIPySOFI to function properly. "
        "Please install it with: pip install pysofi"
    )

# Define public API
__all__ = [
    'launch_gui',
    'DataManager',
    'PYSOFI_AVAILABLE',
    '__version__',
]
