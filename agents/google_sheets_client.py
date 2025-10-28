"""
Google Sheets Client for the FeedbackTrainerAgent.

This module provides proper Google Sheets API integration for writing
recommendations and performance data to spreadsheets.
"""

import os
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google.oauth2.service_account import Credentials as ServiceAccountCredentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False


class GoogleSheetsClient:
    """
    Google Sheets API client for writing data to spreadsheets.
    
    Supports both service account and OAuth2 authentication methods.
    """
    
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self, sheet_id: str, credentials_file: Optional[str] = None):
        """
        Initialize the Google Sheets client.
        
        Args:
            sheet_id: The ID of the Google Sheet to write to
            credentials_file: Path to credentials JSON file (service account or OAuth2)
        """
        self.sheet_id = sheet_id
        self.credentials_file = credentials_file or os.getenv('GOOGLE_CREDENTIALS_FILE')
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with Google Sheets API."""
        if not GOOGLE_SHEETS_AVAILABLE:
            raise ImportError(
                "Google Sheets dependencies not installed. "
                "Install with: pip install google-auth google-auth-oauthlib google-api-python-client"
            )
        
        creds = None
        
        # Try service account authentication first
        if self.credentials_file and os.path.exists(self.credentials_file):
            try:
                # Check if it's a service account file
                with open(self.credentials_file, 'r') as f:
                    import json
                    cred_data = json.load(f)
                    if cred_data.get('type') == 'service_account':
                        creds = ServiceAccountCredentials.from_service_account_file(
                            self.credentials_file, scopes=self.SCOPES
                        )
                        print("✅ Service account authentication successful")
                    else:
                        # It's OAuth2 credentials, use flow
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_file, self.SCOPES
                        )
                        creds = flow.run_local_server(port=0)
                        print("✅ OAuth2 authentication successful")
            except Exception as e:
                print(f"❌ Authentication failed: {e}")
                creds = None
        else:
            creds = None
        
        # Check if we have valid credentials
        if not creds:
            raise ValueError(
                "No valid credentials found. Please set GOOGLE_CREDENTIALS_FILE "
                "environment variable to point to your credentials JSON file."
            )
        
        # Refresh credentials if needed
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        # Build the service
        self.service = build('sheets', 'v4', credentials=creds)
    
    def write_recommendations(self, recommendations: List[Dict[str, Any]], 
                            sheet_name: str = "Recommendations") -> bool:
        """
        Write recommendations to Google Sheets.
        
        Args:
            recommendations: List of recommendation dictionaries
            sheet_name: Name of the sheet to write to
            
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            return False
        
        try:
            # Prepare data for Google Sheets
            values = [
                # Header row
                ["Timestamp", "Type", "Priority", "Title", "Description", 
                 "Suggestions", "Expected Impact", "Status"]
            ]
            
            # Add recommendation data
            for rec in recommendations:
                values.append([
                    datetime.now().isoformat(),
                    rec.get("type", ""),
                    rec.get("priority", ""),
                    rec.get("title", ""),
                    rec.get("description", ""),
                    "; ".join(rec.get("suggestions", [])),
                    rec.get("expected_impact", ""),
                    "pending"
                ])
            
            # Write to sheet
            range_name = f"{sheet_name}!A:H"
            body = {"values": values}
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body
            ).execute()
            
            print(f"Successfully wrote {len(recommendations)} recommendations to Google Sheets")
            return True
            
        except HttpError as error:
            print(f"Google Sheets API error: {error}")
            return False
        except Exception as e:
            print(f"Error writing to Google Sheets: {e}")
            return False
    
    def write_performance_metrics(self, metrics: Dict[str, Any], 
                                sheet_name: str = "Performance") -> bool:
        """
        Write performance metrics to Google Sheets.
        
        Args:
            metrics: Dictionary containing performance metrics
            sheet_name: Name of the sheet to write to
            
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            return False
        
        try:
            # Prepare data for Google Sheets
            values = [
                # Header row
                ["Timestamp", "Metric", "Value", "Category"]
            ]
            
            # Add metric data
            timestamp = datetime.now().isoformat()
            for category, data in metrics.items():
                if isinstance(data, dict):
                    for metric, value in data.items():
                        values.append([timestamp, metric, str(value), category])
                else:
                    values.append([timestamp, category, str(data), "general"])
            
            # Write to sheet
            range_name = f"{sheet_name}!A:D"
            body = {"values": values}
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body
            ).execute()
            
            print(f"Successfully wrote performance metrics to Google Sheets")
            return True
            
        except HttpError as error:
            print(f"Google Sheets API error: {error}")
            return False
        except Exception as e:
            print(f"Error writing performance metrics to Google Sheets: {e}")
            return False
    
    def create_sheets_if_not_exist(self) -> bool:
        """
        Create the required sheets if they don't exist.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            return False
        
        try:
            # Get existing sheets
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.sheet_id
            ).execute()
            
            existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
            
            # Sheets to create
            required_sheets = ["Recommendations", "Performance", "Campaign_Data"]
            sheets_to_create = [sheet for sheet in required_sheets if sheet not in existing_sheets]
            
            if not sheets_to_create:
                return True
            
            # Create new sheets
            requests = []
            for sheet_name in sheets_to_create:
                requests.append({
                    "addSheet": {
                        "properties": {
                            "title": sheet_name
                        }
                    }
                })
            
            if requests:
                body = {"requests": requests}
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.sheet_id,
                    body=body
                ).execute()
                
                print(f"Created sheets: {', '.join(sheets_to_create)}")
            
            return True
            
        except HttpError as error:
            print(f"Google Sheets API error: {error}")
            return False
        except Exception as e:
            print(f"Error creating sheets: {e}")
            return False
