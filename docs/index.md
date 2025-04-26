# GUIPySOFI Documentation

Welcome to the GUIPySOFI documentation. GUIPySOFI is an open-source graphical extension to the PySOFI analysis tool, making super-resolution optical fluctuation imaging analysis accessible through an intuitive user interface.

## Overview

GUIPySOFI provides a user-friendly graphical interface for the PySOFI (Python Super-resolution Optical Fluctuation Imaging) analysis tool. This application allows researchers to easily apply SOFI analysis to their microscopy image stacks without requiring programming knowledge.

## SOFI Theory

Super-resolution Optical Fluctuation Imaging (SOFI) is a computational super-resolution technique that analyzes the temporal fluctuations in fluorescent samples to achieve resolution beyond the diffraction limit. Unlike other super-resolution methods, SOFI:

- Works with conventional wide-field fluorescence microscopes
- Requires relatively few frames compared to other techniques
- Improves both spatial resolution and signal-to-noise ratio

SOFI works by calculating higher-order statistical cumulants of temporal intensity fluctuations. These higher moments enable sub-diffraction resolution by effectively sharpening the point spread function (PSF) of the microscope.

## Installation

### Prerequisites

- Python 3.7 or higher
- PySOFI library (optional but recommended)

### Install from PyPI

```bash
pip install guipysofi
```

### Install from source

```bash
git clone https://github.com/yourusername/guipysofi.git
cd guipysofi
pip install -e .
```

For development dependencies:

```bash
pip install -e ".[dev]"
```

For performance optimizations:

```bash
pip install -e ".[performance]"
```

## Usage

### Launch the GUI

```bash
guipysofi
```

Or from Python:

```python
from guipysofi import launch_gui
launch_gui()
```

### Basic Workflow

1. Load a TIFF stack using the "Browse" button or drag and drop
2. Adjust SOFI parameters:
   - Order: Higher orders give better resolution but need more signal
   - Frames: More frames improve statistics but increase computation time
3. Choose advanced options if needed
4. Click "Run SOFI Analysis" to process
5. View and save results

## Project Structure

```
guipysofi/
├── guipysofi/          # Package source code
│   ├── core/           # Core functionality
│   │   ├── data_manager.py   # Handles data loading and processing
│   │   └── optimization.py   # Performance optimizations
│   ├── ui/             # User interface
│   │   ├── gui.py      # Main GUI class
│   │   └── visualizer.py     # Visualization components
│   └── utils/          # Utility functions
│       └── help.py     # Help dialogs
├── docs/               # Documentation
├── tests/              # Unit tests
├── setup.py            # Package setup script
└── README.md           # Project README
```

## API Reference

### Module: `guipysofi.core.data_manager`

The `DataManager` class handles loading, processing, and saving SOFI data.

```python
from guipysofi.core.data_manager import DataManager

# Create a data manager
data_manager = DataManager(
    status_callback=lambda msg: print(f"Status: {msg}"),
    progress_callback=lambda val: print(f"Progress: {val}%")
)

# Load a TIFF stack
success, message = data_manager.load_file("path/to/stack.tif")

# Run SOFI analysis
parameters = {
    'order': 2,
    'frames': 200,
    'method': 'xc',
    'weight': 'none',
    'bleach_correction': False,
    'drift_correction': False,
    'deconvolution': False
}
success, message = data_manager.run_sofi(parameters)

# Save the result
success, message = data_manager.save_result("path/to/result.tif")
```

### Module: `guipysofi.main`

The `launch_gui` function initializes and launches the GUIPySOFI application.

```python
from guipysofi import launch_gui

# Launch the GUI
launch_gui()
```

## Performance Optimization

GUIPySOFI includes several performance optimizations:

1. **Multithreading**: Utilizes multiple CPU cores for faster processing
2. **Memory Management**: Carefully manages memory to handle large datasets
3. **Numba Acceleration**: Uses JIT compilation for computation-heavy tasks when available
4. **Optimized Data I/O**: Implements efficient data loading and saving

## Contributing

Contributions are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows our coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 