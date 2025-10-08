# evony_shared.py
# Shared Evony classes for reuse in other applications

"""
Evony Shared Classes

This module provides access to reusable Evony game automation classes:
- EvonyADB: Handles Android Debug Bridge communications with BlueStacks
- ManageImage: Provides image processing and OCR capabilities  
- General: Manages general data structures (for EvonyGenerals project)

Usage in other applications:
    from evony_shared import EvonyADB, ManageImage, General
    
    # Initialize
    image_manager = ManageImage()
    adb_manager = EvonyADB(image_manager)
    general = General("General Name")

Dependencies:
    - PyQt5
    - OpenCV (cv2)
    - pytesseract
    - Pillow (PIL)
    - pure-python-adb (ppadb)
    - imagehash
    - gspread (for Google Sheets integration)
"""

from EvonyADB import EvonyADB
from ManageImage import ManageImage

# Export the classes for easy import
__all__ = ['EvonyADB', 'ManageImage']

# Version info
__version__ = '1.0.0'
__author__ = 'EvonyGenerals Project'

# Usage example (commented out)
"""
Example usage:
    from evony_shared import EvonyADB, ManageImage
    
    # Create instances
    image_mgr = ManageImage() 
    adb_mgr = EvonyADB(image_mgr)
    
    # Use the functionality
    if adb_mgr.CheckDeviceConnection():
        adb_mgr.GetScreenshot()
        coords = image_mgr.TextOnScreen("Generals", adb_mgr.objScreenshot)
"""