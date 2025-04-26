"""
Tests for the DataManager class.
"""

import os
import numpy as np
import unittest
from unittest.mock import MagicMock

from guipysofi.core.data_manager import DataManager


class TestDataManager(unittest.TestCase):
    """Test suite for the DataManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.status_callback = MagicMock()
        self.progress_callback = MagicMock()
        self.data_manager = DataManager(
            status_callback=self.status_callback,
            progress_callback=self.progress_callback
        )
    
    def test_initialization(self):
        """Test initialization of DataManager."""
        self.assertIsNone(self.data_manager.data)
        self.assertIsNone(self.data_manager.sofi_result)
        self.assertEqual(self.data_manager.total_frames, 0)
    
    def test_status_updates(self):
        """Test status update mechanism."""
        test_message = "Test status message"
        self.data_manager.update_status(test_message)
        self.status_callback.assert_called_once_with(test_message)
    
    def test_progress_updates(self):
        """Test progress update mechanism."""
        test_value = 50
        self.data_manager.update_progress(test_value)
        self.progress_callback.assert_called_once_with(test_value)
    
    def test_load_file_nonexistent(self):
        """Test loading a nonexistent file."""
        success, message = self.data_manager.load_file("nonexistent_file.tif")
        self.assertFalse(success)
        self.assertTrue("Could not find the file" in message)
    
    def test_cleanup(self):
        """Test cleanup of temporary files."""
        # Create a temp file
        temp_path = "temp_test_file.txt"
        with open(temp_path, "w") as f:
            f.write("test")
        
        # Add it to temp_files list
        self.data_manager.temp_files.append(temp_path)
        
        # Clean up
        self.data_manager._cleanup_temp_files()
        
        # Check file is removed
        self.assertFalse(os.path.exists(temp_path))
        self.assertEqual(len(self.data_manager.temp_files), 0)


if __name__ == "__main__":
    unittest.main() 