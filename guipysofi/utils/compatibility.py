"""
Compatibility Module for GUIPySOFI.

This module handles compatibility checks with the PySOFI package.
"""

import importlib.util
import inspect
import sys


def check_pysofi_compatibility():
    """
    Check compatibility with the PySOFI package.
    
    Returns:
        tuple: (is_available, is_authentic, version, details)
    """
    is_available = False
    is_authentic = False
    version = "Unknown"
    details = []
    
    # Check if PySOFI is installed
    try:
        import pysofi
        is_available = True
        
        # Check version
        version = getattr(pysofi, '__version__', 'Unknown')
        details.append(f"PySOFI version: {version}")
        
        # Check for expected module structure
        if hasattr(pysofi, 'pysofi') and hasattr(pysofi.pysofi, 'PysofiData'):
            is_authentic = True
            details.append("PySOFI package structure verified")
            
            # Check PysofiData class methods
            try:
                from pysofi.pysofi import PysofiData
                methods = inspect.getmembers(PysofiData, predicate=inspect.isfunction)
                method_names = [m[0] for m in methods]
                
                # Also check methods that may be defined on the class itself or parent classes
                # This catches inherited methods that inspect.isfunction might miss
                class_methods = dir(PysofiData)
                
                # Check for required methods
                required_methods = [
                    'calc_moments_set', 
                    'cumulants_images'
                ]
                
                missing_methods = [m for m in required_methods 
                                   if m not in method_names and m not in class_methods]
                
                if missing_methods:
                    is_authentic = False
                    details.append(f"Missing required PySOFI methods: {', '.join(missing_methods)}")
                else:
                    details.append("All required PySOFI methods verified")
                
                # Check for optional methods - these might be instance methods
                # rather than static methods, so we need to check both
                optional_methods = {
                    'bleach_correction': 'Bleaching correction',
                    'drift_correction': 'Drift correction',
                    'reconstruct_fourier': 'Deconvolution'
                }
                
                for method_name, description in optional_methods.items():
                    if method_name in method_names or method_name in class_methods:
                        details.append(f"{description} supported: Yes")
                    else:
                        details.append(f"{description} supported: No")  # Changed from 'Yes' to 'No'
                
                # Check if weighting attribute exists - but don't create an instance,
                # since that might fail if PySOFI requires specific initialization
                has_weighting = hasattr(PysofiData, 'weighting') or 'weighting' in dir(PysofiData) 
                details.append(f"Weighting attribute: {'Present' if has_weighting else 'Not present'}")  # Fixed conditional
                    
                # Check cumulants_images signature to ensure compatibility with our usage
                try:
                    sig = inspect.signature(PysofiData.cumulants_images)
                    has_weighting_param = 'weighting' in sig.parameters
                    details.append(f"Method 'cumulants_images' {'supports' if has_weighting_param else 'does not support'} 'weighting' parameter")  # Fixed conditional
                except Exception as e:
                    details.append(f"Could not check method signature, assuming compatibility")
                    
            except Exception as e:
                details.append(f"Error checking PySOFI methods: {str(e)}")
                
        else:
            details.append("PySOFI package structure is non-standard")
            
    except ImportError:
        details.append("PySOFI package not found")
    except Exception as e:
        details.append(f"Error during PySOFI check: {str(e)}")
    
    return is_available, is_authentic, version, details


def get_compatibility_report():
    """
    Get a human-readable report on PySOFI compatibility.
    
    Returns:
        str: A report on PySOFI compatibility.
    """
    is_available, is_authentic, version, details = check_pysofi_compatibility()
    
    if not is_available:
        return "PySOFI is not installed. Please install it with: pip install pysofi"
    
    if not is_authentic:
        report = "WARNING: The installed PySOFI package may not be authentic or compatible.\n"
    else:
        report = "PySOFI package is authentic and compatible.\n"
    
    report += f"PySOFI version: {version}\n\n"
    report += "Details:\n"
    for detail in details:
        report += f"- {detail}\n"
    
    # Check for missing features
    missing_features = []
    for detail in details:
        if "supported: No" in detail:
            feature = detail.split("supported")[0].strip()
            missing_features.append(feature)
    
    if missing_features:
        report += "\nWARNING: The following features are not available in your PySOFI version:\n"
        for feature in missing_features:
            report += f"- {feature}\n"
        report += "\nGUIPySOFI will use internal implementations for these features.\n"
    
    return report


if __name__ == "__main__":
    print(get_compatibility_report()) 