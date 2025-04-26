# GUIPySOFI

An Open Source Graphical Extension to the PySOFI Analysis Tool for Super-resolution Optical Fluctuation Imaging.

## Overview

GUIPySOFI provides a user-friendly graphical interface for the PySOFI (Python Super-resolution Optical Fluctuation Imaging) analysis tool. It allows researchers to easily process and analyze SOFI data without writing code.

Key features:
- User-friendly GUI with intuitive controls
- Real-time visualization of SOFI results
- Support for various SOFI orders and methods
- Built-in corrections for bleaching and drift
- Deconvolution for further resolution enhancement
- Compatible with standard TIFF stacks

## Installation

### Prerequisites

- Python 3.7 or higher
- PySOFI (`pip install pysofi`)

### Installation options

#### Option 1: Install from PyPI (recommended)

```bash
pip install guipysofi
```

#### Option 2: Install from source

```bash
git clone https://github.com/YOUR_USERNAME/guipysofi.git
cd guipysofi
pip install -e .
```

## Usage

### Launching the GUI

After installation, you can launch GUIPySOFI in several ways:

#### Option 1: Using the command-line entry point

```bash
guipysofi
```

#### Option 2: As a Python module

```bash
python -m guipysofi
```

#### Option 3: In Python code

```python
from guipysofi import launch_gui
launch_gui()
```

### Basic Workflow

1. Load a TIFF stack using the "Browse" button or drag-and-drop
2. Set the desired SOFI parameters (order, frames to use)
3. Apply corrections if needed (bleaching, drift)
4. Click "Run SOFI Analysis"
5. View and compare results in the visualization tabs
6. Save the results using the "Save Results" button

## Advanced Features

### SOFI Parameters

- **SOFI Order**: Higher orders provide better resolution but require more frames (2-8)
- **Frames to use**: Number of frames to process (more frames = better statistics but longer processing time)

### Methods

- **Cross-correlation (XC)**: Standard SOFI implementation
- **Auto-correlation (AC)**: Alternative approach
- **Cumulants (CC)**: Direct cumulants calculation

### Corrections

- **Bleaching Correction**: Compensates for photobleaching during acquisition
- **Drift Correction**: Corrects for sample drift

### Reconstruction

- **Deconvolution**: Further enhances resolution (requires order 3+)

## Implementation Details

GUIPySOFI will preferentially use the PySOFI package's native implementations for features like bleaching correction, drift correction, and deconvolution. If these are not available in your PySOFI installation, GUIPySOFI will use internal implementations to provide the functionality.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use GUIPySOFI in your research, please cite:

```
Galbraith, C. (2023). GUIPySOFI: An Open Source Graphical Extension to the PySOFI Analysis Tool.
```

## Acknowledgements

- The PySOFI team for their excellent SOFI implementation
- TestaLab at UCSB for supporting this development 