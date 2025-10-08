#!/usr/bin/env python3
"""
SheetsManager - Google Sheets Integration Module
Handles authentication, data synchronization, and template management for EvonyGenerals

Author: EvonyGenerals Development Team
Version: 1.0
Date: October 7, 2025
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

class SheetsManager:
    """Manages Google Sheets integration for EvonyGenerals"""
    
    def __init__(self, credentials_file: str = "credentials.json"):
        """
        Initialize the Google Sheets manager
        
        Args:
            credentials_file: Path to Google Sheets service account credentials
        """
        self.credentials_file = credentials_file
        self.client = None
        self.spreadsheet = None
        self.spreadsheet_id = None
        self.logger = logging.getLogger(__name__)
        
        # Define the scope for Google Sheets API
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Worksheet names for different data types
        self.worksheets = {
            'generals': 'Generals_Data',
            'analysis': 'Analysis_Results',
            'templates': 'General_Templates',
            'specialties': 'Specialty_Rankings',
            'equipment': 'Equipment_Tracking'
        }
        
    def authenticate(self, spreadsheet_id: str) -> bool:
        """
        Authenticate with Google Sheets API
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Check if credentials file exists
            if not os.path.exists(self.credentials_file):
                self.logger.error(f"Credentials file not found: {self.credentials_file}")
                return False
                
            # Authenticate using service account credentials
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_file, self.scope
            )
            self.client = gspread.authorize(credentials)
            
            # Open the specified spreadsheet
            self.spreadsheet = self.client.open_by_key(spreadsheet_id)
            self.spreadsheet_id = spreadsheet_id
            
            # Verify access by getting spreadsheet info
            sheet_info = self.spreadsheet.sheet1
            self.logger.info(f"Successfully authenticated to spreadsheet: {self.spreadsheet.title}")
            
            # Initialize worksheets if they don't exist
            self._initialize_worksheets()
            
            return True
            
        except gspread.exceptions.SpreadsheetNotFound:
            self.logger.error(f"Spreadsheet not found: {spreadsheet_id}")
            return False
        except gspread.exceptions.APIError as e:
            self.logger.error(f"Google Sheets API error: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            return False
            
    def _initialize_worksheets(self):
        """Initialize required worksheets if they don't exist"""
        try:
            existing_sheets = [ws.title for ws in self.spreadsheet.worksheets()]
            
            for sheet_type, sheet_name in self.worksheets.items():
                if sheet_name not in existing_sheets:
                    self.logger.info(f"Creating worksheet: {sheet_name}")
                    worksheet = self.spreadsheet.add_worksheet(
                        title=sheet_name, rows=1000, cols=20
                    )
                    self._setup_worksheet_headers(worksheet, sheet_type)
                    
        except Exception as e:
            self.logger.error(f"Failed to initialize worksheets: {str(e)}")
            
    def _setup_worksheet_headers(self, worksheet, sheet_type: str):
        """Setup headers for different worksheet types"""
        try:
            if sheet_type == 'generals':
                headers = [
                    'General_ID', 'Name', 'Level', 'Stars', 'Specialty', 
                    'Attack', 'Defense', 'Leadership', 'Politics',
                    'Equipment_1', 'Equipment_2', 'Equipment_3', 'Equipment_4',
                    'Skill_1', 'Skill_2', 'Skill_3', 'Skill_4',
                    'Last_Updated', 'Notes', 'Status'
                ]
            elif sheet_type == 'analysis':
                headers = [
                    'Analysis_Date', 'Analysis_Type', 'Total_Generals',
                    'Average_Level', 'Top_Specialty', 'Recommendations',
                    'Generated_By'
                ]
            elif sheet_type == 'templates':
                headers = [
                    'Template_Name', 'Purpose', 'Recommended_Generals',
                    'Formation', 'Strategy_Notes', 'Created_Date'
                ]
            elif sheet_type == 'specialties':
                headers = [
                    'Specialty', 'General_Count', 'Average_Level',
                    'Top_General', 'Effectiveness_Rating', 'Usage_Notes'
                ]
            elif sheet_type == 'equipment':
                headers = [
                    'General_Name', 'Slot_1', 'Slot_2', 'Slot_3', 'Slot_4',
                    'Total_Power', 'Optimization_Score', 'Last_Updated'
                ]
            else:
                headers = ['Data', 'Timestamp']
                
            worksheet.append_row(headers)
            self.logger.info(f"Set up headers for {sheet_type} worksheet")
            
        except Exception as e:
            self.logger.error(f"Failed to setup headers for {sheet_type}: {str(e)}")
            
    def save_generals_data(self, generals_data: List[Dict[str, Any]]) -> bool:
        """
        Save generals data to Google Sheets
        
        Args:
            generals_data: List of general dictionaries
            
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            if not self.spreadsheet:
                self.logger.error("Not authenticated to Google Sheets")
                return False
                
            # Get or create the generals worksheet
            try:
                worksheet = self.spreadsheet.worksheet(self.worksheets['generals'])
            except gspread.exceptions.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(
                    title=self.worksheets['generals'], rows=1000, cols=20
                )
                self._setup_worksheet_headers(worksheet, 'generals')
                
            # Clear existing data (keep headers)
            if len(worksheet.get_all_values()) > 1:
                worksheet.delete_rows(2, len(worksheet.get_all_values()))
                
            # Prepare data for upload
            upload_data = []
            for i, general in enumerate(generals_data):
                row_data = [
                    f"GEN_{i:04d}",  # General_ID
                    general.get('name', ''),
                    general.get('level', ''),
                    general.get('stars', ''),
                    general.get('specialty', ''),
                    general.get('attack', ''),
                    general.get('defense', ''),
                    general.get('leadership', ''),
                    general.get('politics', ''),
                    general.get('equipment_1', ''),
                    general.get('equipment_2', ''),
                    general.get('equipment_3', ''),
                    general.get('equipment_4', ''),
                    general.get('skill_1', ''),
                    general.get('skill_2', ''),
                    general.get('skill_3', ''),
                    general.get('skill_4', ''),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    general.get('notes', ''),
                    general.get('status', 'Active')
                ]
                upload_data.append(row_data)
                
            # Upload data in batches to avoid API limits
            batch_size = 100
            for i in range(0, len(upload_data), batch_size):
                batch = upload_data[i:i + batch_size]
                worksheet.append_rows(batch)
                self.logger.info(f"Uploaded batch {i//batch_size + 1}: {len(batch)} generals")
                
            self.logger.info(f"Successfully saved {len(generals_data)} generals to Google Sheets")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save generals data: {str(e)}")
            return False
            
    def load_generals_data(self) -> List[Dict[str, Any]]:
        """
        Load generals data from Google Sheets
        
        Returns:
            List of general dictionaries
        """
        try:
            if not self.spreadsheet:
                self.logger.error("Not authenticated to Google Sheets")
                return []
                
            # Get the generals worksheet
            try:
                worksheet = self.spreadsheet.worksheet(self.worksheets['generals'])
            except gspread.exceptions.WorksheetNotFound:
                self.logger.error("Generals worksheet not found")
                return []
                
            # Get all data from the worksheet
            all_data = worksheet.get_all_records()
            
            # Convert to our internal format
            generals_data = []
            for row in all_data:
                general = {
                    'name': row.get('Name', ''),
                    'level': row.get('Level', ''),
                    'stars': row.get('Stars', ''),
                    'specialty': row.get('Specialty', ''),
                    'attack': row.get('Attack', ''),
                    'defense': row.get('Defense', ''),
                    'leadership': row.get('Leadership', ''),
                    'politics': row.get('Politics', ''),
                    'equipment_1': row.get('Equipment_1', ''),
                    'equipment_2': row.get('Equipment_2', ''),
                    'equipment_3': row.get('Equipment_3', ''),
                    'equipment_4': row.get('Equipment_4', ''),
                    'skill_1': row.get('Skill_1', ''),
                    'skill_2': row.get('Skill_2', ''),
                    'skill_3': row.get('Skill_3', ''),
                    'skill_4': row.get('Skill_4', ''),
                    'timestamp': row.get('Last_Updated', ''),
                    'notes': row.get('Notes', ''),
                    'status': row.get('Status', 'Active')
                }
                generals_data.append(general)
                
            self.logger.info(f"Successfully loaded {len(generals_data)} generals from Google Sheets")
            return generals_data
            
        except Exception as e:
            self.logger.error(f"Failed to load generals data: {str(e)}")
            return []
            
    def save_analysis_results(self, analysis_data: Dict[str, Any]) -> bool:
        """
        Save analysis results to Google Sheets
        
        Args:
            analysis_data: Dictionary containing analysis results
            
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            if not self.spreadsheet:
                self.logger.error("Not authenticated to Google Sheets")
                return False
                
            # Get or create the analysis worksheet
            try:
                worksheet = self.spreadsheet.worksheet(self.worksheets['analysis'])
            except gspread.exceptions.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(
                    title=self.worksheets['analysis'], rows=1000, cols=10
                )
                self._setup_worksheet_headers(worksheet, 'analysis')
                
            # Prepare analysis data row
            analysis_row = [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                analysis_data.get('analysis_type', 'General Analysis'),
                analysis_data.get('total_generals', 0),
                analysis_data.get('average_level', 0),
                analysis_data.get('top_specialty', ''),
                analysis_data.get('recommendations', ''),
                'EvonyGenerals v1.0'
            ]
            
            worksheet.append_row(analysis_row)
            self.logger.info("Successfully saved analysis results to Google Sheets")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save analysis results: {str(e)}")
            return False
            
    def create_general_template(self, template_data: Dict[str, Any]) -> bool:
        """
        Create a new general template in Google Sheets
        
        Args:
            template_data: Dictionary containing template information
            
        Returns:
            bool: True if creation successful, False otherwise
        """
        try:
            if not self.spreadsheet:
                self.logger.error("Not authenticated to Google Sheets")
                return False
                
            # Get or create the templates worksheet
            try:
                worksheet = self.spreadsheet.worksheet(self.worksheets['templates'])
            except gspread.exceptions.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(
                    title=self.worksheets['templates'], rows=1000, cols=10
                )
                self._setup_worksheet_headers(worksheet, 'templates')
                
            # Prepare template data row
            template_row = [
                template_data.get('name', ''),
                template_data.get('purpose', ''),
                template_data.get('generals', ''),
                template_data.get('formation', ''),
                template_data.get('notes', ''),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
            
            worksheet.append_row(template_row)
            self.logger.info(f"Successfully created template: {template_data.get('name', 'Unnamed')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create template: {str(e)}")
            return False
            
    def update_specialty_rankings(self, specialty_data: Dict[str, Any]) -> bool:
        """
        Update specialty rankings in Google Sheets
        
        Args:
            specialty_data: Dictionary containing specialty analysis
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            if not self.spreadsheet:
                self.logger.error("Not authenticated to Google Sheets")
                return False
                
            # Get or create the specialties worksheet
            try:
                worksheet = self.spreadsheet.worksheet(self.worksheets['specialties'])
            except gspread.exceptions.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(
                    title=self.worksheets['specialties'], rows=1000, cols=10
                )
                self._setup_worksheet_headers(worksheet, 'specialties')
                
            # Clear existing data and update with new rankings
            if len(worksheet.get_all_values()) > 1:
                worksheet.delete_rows(2, len(worksheet.get_all_values()))
                
            # Prepare specialty rankings data
            rankings_data = []
            for specialty, data in specialty_data.items():
                row_data = [
                    specialty,
                    data.get('count', 0),
                    data.get('average_level', 0),
                    data.get('top_general', ''),
                    data.get('effectiveness', 0),
                    data.get('notes', '')
                ]
                rankings_data.append(row_data)
                
            # Sort by effectiveness rating
            rankings_data.sort(key=lambda x: float(x[4]), reverse=True)
            
            worksheet.append_rows(rankings_data)
            self.logger.info("Successfully updated specialty rankings")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update specialty rankings: {str(e)}")
            return False
            
    def export_to_csv(self, worksheet_name: str, output_path: str) -> bool:
        """
        Export worksheet data to CSV file
        
        Args:
            worksheet_name: Name of the worksheet to export
            output_path: Path for the CSV output file
            
        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            if not self.spreadsheet:
                self.logger.error("Not authenticated to Google Sheets")
                return False
                
            # Get the specified worksheet
            try:
                worksheet = self.spreadsheet.worksheet(worksheet_name)
            except gspread.exceptions.WorksheetNotFound:
                self.logger.error(f"Worksheet not found: {worksheet_name}")
                return False
                
            # Get all data and convert to DataFrame
            all_data = worksheet.get_all_records()
            df = pd.DataFrame(all_data)
            
            # Export to CSV
            df.to_csv(output_path, index=False, encoding='utf-8')
            
            self.logger.info(f"Successfully exported {worksheet_name} to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export to CSV: {str(e)}")
            return False
            
    def backup_spreadsheet(self, backup_path: str) -> bool:
        """
        Create a backup of the entire spreadsheet
        
        Args:
            backup_path: Directory path for backup files
            
        Returns:
            bool: True if backup successful, False otherwise
        """
        try:
            if not self.spreadsheet:
                self.logger.error("Not authenticated to Google Sheets")
                return False
                
            # Create backup directory if it doesn't exist
            os.makedirs(backup_path, exist_ok=True)
            
            # Backup each worksheet
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            for worksheet in self.spreadsheet.worksheets():
                # Export each worksheet to CSV
                csv_filename = f"{worksheet.title}_{timestamp}.csv"
                csv_path = os.path.join(backup_path, csv_filename)
                
                all_data = worksheet.get_all_records()
                if all_data:
                    df = pd.DataFrame(all_data)
                    df.to_csv(csv_path, index=False, encoding='utf-8')
                    
            self.logger.info(f"Successfully backed up spreadsheet to {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to backup spreadsheet: {str(e)}")
            return False
            
    def get_spreadsheet_info(self) -> Dict[str, Any]:
        """
        Get information about the current spreadsheet
        
        Returns:
            Dictionary containing spreadsheet information
        """
        try:
            if not self.spreadsheet:
                return {"error": "Not authenticated"}
                
            worksheets = self.spreadsheet.worksheets()
            worksheet_info = []
            
            for ws in worksheets:
                worksheet_info.append({
                    'name': ws.title,
                    'rows': ws.row_count,
                    'cols': ws.col_count,
                    'data_rows': len(ws.get_all_values()) - 1  # Subtract header row
                })
                
            return {
                'title': self.spreadsheet.title,
                'id': self.spreadsheet_id,
                'worksheets': worksheet_info,
                'total_worksheets': len(worksheets)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get spreadsheet info: {str(e)}")
            return {"error": str(e)}
            
    def test_connection(self) -> bool:
        """
        Test the Google Sheets connection
        
        Returns:
            bool: True if connection is working, False otherwise
        """
        try:
            if not self.spreadsheet:
                return False
                
            # Try to read a cell to test the connection
            self.spreadsheet.sheet1.acell('A1')
            return True
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False
            
    def create_credentials_template(self, output_path: str = "credentials_template.json"):
        """
        Create a template for Google Sheets credentials file
        
        Args:
            output_path: Path for the credentials template file
        """
        template = {
            "type": "service_account",
            "project_id": "your-project-id",
            "private_key_id": "your-private-key-id",
            "private_key": "-----BEGIN PRIVATE KEY-----\\nYOUR_PRIVATE_KEY\\n-----END PRIVATE KEY-----\\n",
            "client_email": "your-service-account@your-project-id.iam.gserviceaccount.com",
            "client_id": "your-client-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com"
        }
        
        try:
            with open(output_path, 'w') as f:
                json.dump(template, f, indent=2)
            self.logger.info(f"Credentials template created at {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to create credentials template: {str(e)}")

# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create sheets manager instance
    sheets_manager = SheetsManager()
    
    # Create credentials template
    sheets_manager.create_credentials_template()
    
    print("SheetsManager module loaded successfully")
    print("To use this module:")
    print("1. Create a Google Cloud Project")
    print("2. Enable the Google Sheets API")
    print("3. Create a service account and download credentials")
    print("4. Save credentials as 'credentials.json'")
    print("5. Share your spreadsheet with the service account email")