#!/usr/bin/env python3
"""
EvonyGenerals - Advanced General Management and Analysis Tool
Main application for extracting, managing, and analyzing Evony generals using OCR and Google Sheets integration.

Author: EvonyGenerals Development Team
Version: 1.0
Date: October 7, 2025
"""

import sys
import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QTextEdit, QProgressBar,
                            QGroupBox, QGridLayout, QComboBox, QSpinBox, QCheckBox,
                            QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
                            QMessageBox, QFileDialog, QLineEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon

# Import our custom modules
from EvonyADB import EvonyADB
from ManageImage import ManageImage
from evony_shared import show_styled_message, apply_dark_theme
try:
    from SheetsManager import SheetsManager
except ImportError:
    print("SheetsManager not available - Google Sheets integration disabled")
    SheetsManager = None

try:
    from OCREngine import OCREngine
except ImportError:
    print("OCREngine not available - using basic OCR from ManageImage")
    OCREngine = None

try:
    from GeneralData import GeneralData
except ImportError:
    print("GeneralData not available - using basic data structures")
    GeneralData = None

class GeneralExtractionWorker(QThread):
    """Worker thread for OCR processing to prevent UI freezing"""
    progress_updated = pyqtSignal(int)
    general_extracted = pyqtSignal(dict)
    extraction_complete = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, adb_connection, image_manager, extraction_mode="single"):
        super().__init__()
        self.adb_connection = adb_connection
        self.image_manager = image_manager
        self.extraction_mode = extraction_mode
        self.should_stop = False
        
    def run(self):
        """Execute general extraction process"""
        try:
            if self.extraction_mode == "single":
                self.extract_single_general()
            elif self.extraction_mode == "batch":
                self.extract_batch_generals()
        except Exception as e:
            self.error_occurred.emit(f"Extraction error: {str(e)}")
            
    def extract_single_general(self):
        """Extract data from currently visible general"""
        self.progress_updated.emit(10)
        
        # Take screenshot
        screenshot_path = self.adb_connection.TakeScreenshot("general_screen")
        if not screenshot_path:
            self.error_occurred.emit("Failed to capture screenshot")
            return
            
        self.progress_updated.emit(30)
        
        # Extract general data using OCR
        if OCREngine:
            ocr_engine = OCREngine()
            general_data = ocr_engine.extract_general_data(screenshot_path)
        else:
            # Fallback to basic OCR from ManageImage
            general_data = self.image_manager.ExtractGeneralsData(screenshot_path)
            
        self.progress_updated.emit(80)
        
        if general_data:
            self.general_extracted.emit(general_data)
        else:
            self.error_occurred.emit("Failed to extract general data")
            
        self.progress_updated.emit(100)
        
    def extract_batch_generals(self):
        """Extract data from multiple generals"""
        generals_list = []
        total_generals = 50  # Assume max 50 generals for progress calculation
        
        for i in range(total_generals):
            if self.should_stop:
                break
                
            # Update progress
            progress = int((i / total_generals) * 100)
            self.progress_updated.emit(progress)
            
            # Take screenshot and extract data
            screenshot_path = self.adb_connection.TakeScreenshot(f"general_{i}")
            if screenshot_path:
                if OCREngine:
                    ocr_engine = OCREngine()
                    general_data = ocr_engine.extract_general_data(screenshot_path)
                else:
                    general_data = self.image_manager.ExtractGeneralsData(screenshot_path)
                    
                if general_data:
                    generals_list.append(general_data)
                    self.general_extracted.emit(general_data)
            
            # Navigate to next general (implement navigation logic)
            # self.navigate_to_next_general()
            
        self.extraction_complete.emit(generals_list)
        self.progress_updated.emit(100)
        
    def stop_extraction(self):
        """Stop the extraction process"""
        self.should_stop = True

class EvonyGeneralsMainWindow(QMainWindow):
    """Main application window for EvonyGenerals"""
    
    def __init__(self):
        super().__init__()
        self.adb_connection = EvonyADB()
        self.image_manager = ManageImage()
        self.sheets_manager = SheetsManager() if SheetsManager else None
        self.extraction_worker = None
        
        # Data storage
        self.generals_data = []
        self.current_general = None
        
        # Setup logging
        self.setup_logging()
        
        # Initialize UI
        self.init_ui()
        
        # Setup connections
        self.setup_connections()
        
        # Apply dark theme
        apply_dark_theme(self)
        
    def setup_logging(self):
        """Configure logging for the application"""
        log_filename = f"evony_generals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("EvonyGenerals - General Management Tool v1.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create tab widget for different sections
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Setup tabs
        self.setup_connection_tab()
        self.setup_extraction_tab()
        self.setup_data_management_tab()
        self.setup_analysis_tab()
        
    def setup_connection_tab(self):
        """Setup device connection tab"""
        connection_widget = QWidget()
        layout = QVBoxLayout(connection_widget)
        
        # Connection group
        connection_group = QGroupBox("Device Connection")
        connection_layout = QVBoxLayout(connection_group)
        
        # Device selection
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Device:"))
        self.device_combo = QComboBox()
        device_layout.addWidget(self.device_combo)
        
        self.refresh_devices_btn = QPushButton("Refresh Devices")
        device_layout.addWidget(self.refresh_devices_btn)
        
        self.connect_btn = QPushButton("Connect")
        device_layout.addWidget(self.connect_btn)
        
        connection_layout.addLayout(device_layout)
        
        # Connection status
        self.connection_status = QLabel("Status: Disconnected")
        connection_layout.addWidget(self.connection_status)
        
        layout.addWidget(connection_group)
        
        # Google Sheets configuration
        if self.sheets_manager:
            sheets_group = QGroupBox("Google Sheets Configuration")
            sheets_layout = QVBoxLayout(sheets_group)
            
            # Spreadsheet ID input
            sheets_id_layout = QHBoxLayout()
            sheets_id_layout.addWidget(QLabel("Spreadsheet ID:"))
            self.sheets_id_input = QLineEdit()
            sheets_id_layout.addWidget(self.sheets_id_input)
            sheets_layout.addLayout(sheets_id_layout)
            
            # Authentication button
            self.auth_sheets_btn = QPushButton("Authenticate Google Sheets")
            sheets_layout.addWidget(self.auth_sheets_btn)
            
            # Sheets status
            self.sheets_status = QLabel("Status: Not authenticated")
            sheets_layout.addWidget(self.sheets_status)
            
            layout.addWidget(sheets_group)
        
        layout.addStretch()
        self.tab_widget.addTab(connection_widget, "Connection")
        
    def setup_extraction_tab(self):
        """Setup OCR extraction tab"""
        extraction_widget = QWidget()
        layout = QVBoxLayout(extraction_widget)
        
        # Extraction controls
        controls_group = QGroupBox("Extraction Controls")
        controls_layout = QGridLayout(controls_group)
        
        # Extraction mode
        controls_layout.addWidget(QLabel("Mode:"), 0, 0)
        self.extraction_mode_combo = QComboBox()
        self.extraction_mode_combo.addItems(["Single General", "Batch Processing"])
        controls_layout.addWidget(self.extraction_mode_combo, 0, 1)
        
        # OCR settings
        controls_layout.addWidget(QLabel("OCR Language:"), 1, 0)
        self.ocr_language_combo = QComboBox()
        self.ocr_language_combo.addItems(["eng", "chi_sim", "spa", "fra", "deu"])
        controls_layout.addWidget(self.ocr_language_combo, 1, 1)
        
        # Validation checkbox
        self.validate_data_checkbox = QCheckBox("Validate extracted data")
        self.validate_data_checkbox.setChecked(True)
        controls_layout.addWidget(self.validate_data_checkbox, 2, 0, 1, 2)
        
        # Action buttons
        self.start_extraction_btn = QPushButton("Start Extraction")
        controls_layout.addWidget(self.start_extraction_btn, 3, 0)
        
        self.stop_extraction_btn = QPushButton("Stop Extraction")
        self.stop_extraction_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_extraction_btn, 3, 1)
        
        layout.addWidget(controls_group)
        
        # Progress tracking
        progress_group = QGroupBox("Extraction Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Ready to start extraction")
        progress_layout.addWidget(self.progress_label)
        
        layout.addWidget(progress_group)
        
        # Current general preview
        preview_group = QGroupBox("Current General Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.general_preview = QTextEdit()
        self.general_preview.setMaximumHeight(200)
        preview_layout.addWidget(self.general_preview)
        
        layout.addWidget(preview_group)
        
        layout.addStretch()
        self.tab_widget.addTab(extraction_widget, "Extraction")
        
    def setup_data_management_tab(self):
        """Setup data management tab"""
        data_widget = QWidget()
        layout = QVBoxLayout(data_widget)
        
        # Data controls
        controls_layout = QHBoxLayout()
        
        self.load_data_btn = QPushButton("Load from Sheets")
        controls_layout.addWidget(self.load_data_btn)
        
        self.save_data_btn = QPushButton("Save to Sheets")
        controls_layout.addWidget(self.save_data_btn)
        
        self.export_csv_btn = QPushButton("Export CSV")
        controls_layout.addWidget(self.export_csv_btn)
        
        self.clear_data_btn = QPushButton("Clear Data")
        controls_layout.addWidget(self.clear_data_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Search and filter
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addWidget(QLabel("Min Level:"))
        self.min_level_spin = QSpinBox()
        self.min_level_spin.setRange(1, 50)
        filter_layout.addWidget(self.min_level_spin)
        
        filter_layout.addWidget(QLabel("Stars:"))
        self.stars_combo = QComboBox()
        self.stars_combo.addItems(["All", "1", "2", "3", "4", "5"])
        filter_layout.addWidget(self.stars_combo)
        
        self.apply_filter_btn = QPushButton("Apply Filter")
        filter_layout.addWidget(self.apply_filter_btn)
        
        layout.addLayout(filter_layout)
        
        # Generals table
        self.generals_table = QTableWidget()
        self.setup_generals_table()
        layout.addWidget(self.generals_table)
        
        self.tab_widget.addTab(data_widget, "Data Management")
        
    def setup_analysis_tab(self):
        """Setup analysis and reporting tab"""
        analysis_widget = QWidget()
        layout = QVBoxLayout(analysis_widget)
        
        # Analysis controls
        analysis_group = QGroupBox("Analysis Options")
        analysis_layout = QGridLayout(analysis_group)
        
        self.generate_report_btn = QPushButton("Generate Report")
        analysis_layout.addWidget(self.generate_report_btn, 0, 0)
        
        self.specialty_analysis_btn = QPushButton("Specialty Analysis")
        analysis_layout.addWidget(self.specialty_analysis_btn, 0, 1)
        
        self.level_distribution_btn = QPushButton("Level Distribution")
        analysis_layout.addWidget(self.level_distribution_btn, 1, 0)
        
        self.recommendations_btn = QPushButton("Get Recommendations")
        analysis_layout.addWidget(self.recommendations_btn, 1, 1)
        
        layout.addWidget(analysis_group)
        
        # Analysis results
        results_group = QGroupBox("Analysis Results")
        results_layout = QVBoxLayout(results_group)
        
        self.analysis_results = QTextEdit()
        results_layout.addWidget(self.analysis_results)
        
        layout.addWidget(results_group)
        
        self.tab_widget.addTab(analysis_widget, "Analysis")
        
    def setup_generals_table(self):
        """Configure the generals data table"""
        columns = ["Name", "Level", "Stars", "Specialty", "Attack", "Defense", 
                  "Leadership", "Politics", "Equipment", "Last Updated"]
        self.generals_table.setColumnCount(len(columns))
        self.generals_table.setHorizontalHeaderLabels(columns)
        
        # Set column widths
        header = self.generals_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Name
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Specialty
        header.setSectionResizeMode(8, QHeaderView.Stretch)          # Equipment
        
    def setup_connections(self):
        """Setup signal-slot connections"""
        # Connection tab
        self.refresh_devices_btn.clicked.connect(self.refresh_devices)
        self.connect_btn.clicked.connect(self.connect_device)
        
        if self.sheets_manager:
            self.auth_sheets_btn.clicked.connect(self.authenticate_sheets)
        
        # Extraction tab
        self.start_extraction_btn.clicked.connect(self.start_extraction)
        self.stop_extraction_btn.clicked.connect(self.stop_extraction)
        
        # Data management tab
        self.load_data_btn.clicked.connect(self.load_data_from_sheets)
        self.save_data_btn.clicked.connect(self.save_data_to_sheets)
        self.export_csv_btn.clicked.connect(self.export_to_csv)
        self.clear_data_btn.clicked.connect(self.clear_data)
        self.apply_filter_btn.clicked.connect(self.apply_data_filter)
        self.search_input.textChanged.connect(self.filter_generals_table)
        
        # Analysis tab
        self.generate_report_btn.clicked.connect(self.generate_analysis_report)
        self.specialty_analysis_btn.clicked.connect(self.analyze_specialties)
        
    def refresh_devices(self):
        """Refresh available ADB devices"""
        try:
            devices = self.adb_connection.GetAvailableDevices()
            self.device_combo.clear()
            self.device_combo.addItems(devices)
            self.logger.info(f"Found {len(devices)} devices")
        except Exception as e:
            show_styled_message("Error", f"Failed to refresh devices: {str(e)}", self)
            self.logger.error(f"Failed to refresh devices: {str(e)}")
            
    def connect_device(self):
        """Connect to selected device"""
        device = self.device_combo.currentText()
        if not device:
            show_styled_message("Error", "Please select a device to connect", self)
            return
            
        try:
            success = self.adb_connection.CheckDeviceConnection()
            if success:
                self.connection_status.setText("Status: Connected")
                self.connection_status.setStyleSheet("color: #00ff88;")
                show_styled_message("Success", f"Connected to {device}", self)
            else:
                self.connection_status.setText("Status: Connection Failed")
                self.connection_status.setStyleSheet("color: #ff4444;")
                show_styled_message("Error", f"Failed to connect to {device}", self)
        except Exception as e:
            show_styled_message("Error", f"Connection error: {str(e)}", self)
            self.logger.error(f"Connection error: {str(e)}")
            
    def authenticate_sheets(self):
        """Authenticate with Google Sheets"""
        if not self.sheets_manager:
            show_styled_message("Error", "Google Sheets integration not available", self)
            return
            
        try:
            spreadsheet_id = self.sheets_id_input.text().strip()
            if not spreadsheet_id:
                show_styled_message("Error", "Please enter a valid Spreadsheet ID", self)
                return
                
            success = self.sheets_manager.authenticate(spreadsheet_id)
            if success:
                self.sheets_status.setText("Status: Authenticated")
                self.sheets_status.setStyleSheet("color: #00ff88;")
                show_styled_message("Success", "Google Sheets authenticated successfully", self)
            else:
                self.sheets_status.setText("Status: Authentication Failed")
                self.sheets_status.setStyleSheet("color: #ff4444;")
        except Exception as e:
            show_styled_message("Error", f"Authentication error: {str(e)}", self)
            self.logger.error(f"Authentication error: {str(e)}")
            
    def start_extraction(self):
        """Start the general extraction process"""
        if not self.adb_connection.CheckDeviceConnection():
            show_styled_message("Error", "Please connect to a device first", self)
            return
            
        # Setup extraction worker
        mode = "single" if self.extraction_mode_combo.currentIndex() == 0 else "batch"
        self.extraction_worker = GeneralExtractionWorker(
            self.adb_connection, self.image_manager, mode
        )
        
        # Connect worker signals
        self.extraction_worker.progress_updated.connect(self.update_progress)
        self.extraction_worker.general_extracted.connect(self.handle_extracted_general)
        self.extraction_worker.extraction_complete.connect(self.handle_extraction_complete)
        self.extraction_worker.error_occurred.connect(self.handle_extraction_error)
        
        # Update UI state
        self.start_extraction_btn.setEnabled(False)
        self.stop_extraction_btn.setEnabled(True)
        self.progress_label.setText("Starting extraction...")
        
        # Start worker
        self.extraction_worker.start()
        self.logger.info(f"Started {mode} extraction")
        
    def stop_extraction(self):
        """Stop the current extraction process"""
        if self.extraction_worker:
            self.extraction_worker.stop_extraction()
            self.extraction_worker.wait()  # Wait for thread to finish
            
        self.start_extraction_btn.setEnabled(True)
        self.stop_extraction_btn.setEnabled(False)
        self.progress_label.setText("Extraction stopped")
        self.logger.info("Extraction stopped by user")
        
    def update_progress(self, value):
        """Update the progress bar"""
        self.progress_bar.setValue(value)
        
    def handle_extracted_general(self, general_data):
        """Handle newly extracted general data"""
        try:
            # Add to our data collection
            self.generals_data.append(general_data)
            
            # Update preview
            preview_text = f"Name: {general_data.get('name', 'Unknown')}\n"
            preview_text += f"Level: {general_data.get('level', 'N/A')}\n"
            preview_text += f"Stars: {general_data.get('stars', 'N/A')}\n"
            preview_text += f"Specialty: {general_data.get('specialty', 'Unknown')}"
            
            self.general_preview.setPlainText(preview_text)
            
            # Update table
            self.refresh_generals_table()
            
            self.logger.info(f"Extracted general: {general_data.get('name', 'Unknown')}")
            
        except Exception as e:
            self.logger.error(f"Error handling extracted general: {str(e)}")
            
    def handle_extraction_complete(self, generals_list):
        """Handle completion of batch extraction"""
        self.start_extraction_btn.setEnabled(True)
        self.stop_extraction_btn.setEnabled(False)
        self.progress_label.setText(f"Extraction complete - {len(generals_list)} generals processed")
        
        show_styled_message("Success", 
                          f"Successfully extracted {len(generals_list)} generals", self)
        self.logger.info(f"Batch extraction complete: {len(generals_list)} generals")
        
    def handle_extraction_error(self, error_message):
        """Handle extraction errors"""
        self.start_extraction_btn.setEnabled(True)
        self.stop_extraction_btn.setEnabled(False)
        self.progress_label.setText(f"Error: {error_message}")
        
        show_styled_message("Error", f"Extraction failed: {error_message}", self)
        self.logger.error(f"Extraction error: {error_message}")
        
    def refresh_generals_table(self):
        """Refresh the generals table with current data"""
        self.generals_table.setRowCount(len(self.generals_data))
        
        for row, general in enumerate(self.generals_data):
            self.generals_table.setItem(row, 0, QTableWidgetItem(str(general.get('name', ''))))
            self.generals_table.setItem(row, 1, QTableWidgetItem(str(general.get('level', ''))))
            self.generals_table.setItem(row, 2, QTableWidgetItem(str(general.get('stars', ''))))
            self.generals_table.setItem(row, 3, QTableWidgetItem(str(general.get('specialty', ''))))
            self.generals_table.setItem(row, 4, QTableWidgetItem(str(general.get('attack', ''))))
            self.generals_table.setItem(row, 5, QTableWidgetItem(str(general.get('defense', ''))))
            self.generals_table.setItem(row, 6, QTableWidgetItem(str(general.get('leadership', ''))))
            self.generals_table.setItem(row, 7, QTableWidgetItem(str(general.get('politics', ''))))
            self.generals_table.setItem(row, 8, QTableWidgetItem(str(general.get('equipment', ''))))
            self.generals_table.setItem(row, 9, QTableWidgetItem(str(general.get('timestamp', ''))))
            
    def filter_generals_table(self):
        """Filter generals table based on search criteria"""
        search_text = self.search_input.text().lower()
        
        for row in range(self.generals_table.rowCount()):
            should_show = True
            
            # Check if search text matches any column
            if search_text:
                row_text = ""
                for col in range(self.generals_table.columnCount()):
                    item = self.generals_table.item(row, col)
                    if item:
                        row_text += item.text().lower() + " "
                should_show = search_text in row_text
                
            self.generals_table.setRowHidden(row, not should_show)
            
    def apply_data_filter(self):
        """Apply advanced data filters"""
        min_level = self.min_level_spin.value()
        stars_filter = self.stars_combo.currentText()
        
        for row in range(self.generals_table.rowCount()):
            should_show = True
            
            # Level filter
            level_item = self.generals_table.item(row, 1)
            if level_item:
                try:
                    level = int(level_item.text())
                    if level < min_level:
                        should_show = False
                except ValueError:
                    pass
                    
            # Stars filter
            if stars_filter != "All":
                stars_item = self.generals_table.item(row, 2)
                if stars_item and stars_item.text() != stars_filter:
                    should_show = False
                    
            self.generals_table.setRowHidden(row, not should_show)
            
    def load_data_from_sheets(self):
        """Load general data from Google Sheets"""
        if not self.sheets_manager:
            show_styled_message("Error", "Google Sheets integration not available", self)
            return
            
        try:
            self.generals_data = self.sheets_manager.load_generals_data()
            self.refresh_generals_table()
            show_styled_message("Success", 
                              f"Loaded {len(self.generals_data)} generals from sheets", self)
        except Exception as e:
            show_styled_message("Error", f"Failed to load data: {str(e)}", self)
            self.logger.error(f"Failed to load data: {str(e)}")
            
    def save_data_to_sheets(self):
        """Save current general data to Google Sheets"""
        if not self.sheets_manager:
            show_styled_message("Error", "Google Sheets integration not available", self)
            return
            
        if not self.generals_data:
            show_styled_message("Warning", "No data to save", self)
            return
            
        try:
            self.sheets_manager.save_generals_data(self.generals_data)
            show_styled_message("Success", 
                              f"Saved {len(self.generals_data)} generals to sheets", self)
        except Exception as e:
            show_styled_message("Error", f"Failed to save data: {str(e)}", self)
            self.logger.error(f"Failed to save data: {str(e)}")
            
    def export_to_csv(self):
        """Export general data to CSV file"""
        if not self.generals_data:
            show_styled_message("Warning", "No data to export", self)
            return
            
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export to CSV", f"evony_generals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)")
                
            if filename:
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    if self.generals_data:
                        fieldnames = self.generals_data[0].keys()
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(self.generals_data)
                        
                show_styled_message("Success", f"Data exported to {filename}", self)
        except Exception as e:
            show_styled_message("Error", f"Failed to export data: {str(e)}", self)
            self.logger.error(f"Failed to export data: {str(e)}")
            
    def clear_data(self):
        """Clear all general data"""
        reply = QMessageBox.question(self, 'Clear Data', 
                                   'Are you sure you want to clear all general data?',
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.generals_data.clear()
            self.refresh_generals_table()
            self.general_preview.clear()
            show_styled_message("Info", "All data cleared", self)
            
    def generate_analysis_report(self):
        """Generate comprehensive analysis report"""
        if not self.generals_data:
            show_styled_message("Warning", "No data available for analysis", self)
            return
            
        try:
            report = "=== EVONY GENERALS ANALYSIS REPORT ===\n\n"
            
            # Basic statistics
            total_generals = len(self.generals_data)
            report += f"Total Generals: {total_generals}\n\n"
            
            # Level distribution
            levels = [int(g.get('level', 0)) for g in self.generals_data if g.get('level')]
            if levels:
                avg_level = sum(levels) / len(levels)
                max_level = max(levels)
                min_level = min(levels)
                report += f"Level Statistics:\n"
                report += f"  Average Level: {avg_level:.2f}\n"
                report += f"  Highest Level: {max_level}\n"
                report += f"  Lowest Level: {min_level}\n\n"
            
            # Star distribution
            stars_count = {}
            for general in self.generals_data:
                stars = general.get('stars', 'Unknown')
                stars_count[stars] = stars_count.get(stars, 0) + 1
                
            if stars_count:
                report += "Star Distribution:\n"
                for stars, count in sorted(stars_count.items()):
                    percentage = (count / total_generals) * 100
                    report += f"  {stars} Stars: {count} ({percentage:.1f}%)\n"
                report += "\n"
            
            # Specialty distribution
            specialty_count = {}
            for general in self.generals_data:
                specialty = general.get('specialty', 'Unknown')
                specialty_count[specialty] = specialty_count.get(specialty, 0) + 1
                
            if specialty_count:
                report += "Specialty Distribution:\n"
                for specialty, count in sorted(specialty_count.items(), 
                                             key=lambda x: x[1], reverse=True):
                    percentage = (count / total_generals) * 100
                    report += f"  {specialty}: {count} ({percentage:.1f}%)\n"
                    
            self.analysis_results.setPlainText(report)
            
        except Exception as e:
            show_styled_message("Error", f"Failed to generate report: {str(e)}", self)
            self.logger.error(f"Failed to generate report: {str(e)}")
            
    def analyze_specialties(self):
        """Perform detailed specialty analysis"""
        if not self.generals_data:
            show_styled_message("Warning", "No data available for analysis", self)
            return
            
        # Implement specialty-specific analysis
        analysis = "=== SPECIALTY ANALYSIS ===\n\n"
        analysis += "Top generals by specialty coming soon...\n"
        
        self.analysis_results.setPlainText(analysis)
        
    def closeEvent(self, event):
        """Handle application close event"""
        if self.extraction_worker and self.extraction_worker.isRunning():
            self.extraction_worker.stop_extraction()
            self.extraction_worker.wait()
            
        self.logger.info("Application closed")
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("EvonyGenerals")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("EvonyTools")
    
    # Create and show main window
    window = EvonyGeneralsMainWindow()
    window.show()
    
    # Start application event loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()