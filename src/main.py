import pandas as pd
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import streamlit as st

class RelayRaceManager:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID'
        
    def connect_to_sheets(self, credentials_path):
        """Initialize Google Sheets connection"""
        creds = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=self.SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        return service.spreadsheets()

    def parse_time(self, time_str):
        """Parse time string to datetime object"""
        try:
            return datetime.strptime(time_str, '%m/%d/%Y %H:%M:%S')
        except ValueError:
            try:
                return datetime.strptime(time_str, '%m/%d/%Y %H:%M')
            except ValueError:
                return None

    def calculate_leg_duration(self, start_time, end_time):
        """Calculate duration between two times, handling overnight transitions"""
        if isinstance(start_time, str):
            start_time = self.parse_time(start_time)
        if isinstance(end_time, str):
            end_time = self.parse_time(end_time)
            
        if start_time and end_time:
            duration = end_time - start_time
            # Handle overnight transitions
            if duration.total_seconds() < 0:
                duration += timedelta(days=1)
            return duration
        return timedelta(0)

    def process_registration_data(self, registration_df):
        """Process team registration data"""
        return pd.DataFrame({
            'team_name': registration_df['team_name'],
            'division': registration_df['division'],
            'handicap': registration_df['handicap']
        })

    def process_day_results(self, times_df, teams_df):
        """Process results for a single day"""
        results = []
        for _, team in teams_df.iterrows():
            team_times = times_df[times_df['team_name'] == team['team_name']]
            total_time = timedelta(0)
            
            for _, leg in team_times.iterrows():
                duration = self.calculate_leg_duration(leg['start_time'], leg['end_time'])
                total_time += duration
            
            # Apply handicap
            handicap_time = total_time * team['handicap']
            
            results.append({
                'team_name': team['team_name'],
                'division': team['division'],
                'actual_time': total_time,
                'handicap_time': handicap_time,
                'handicap': team['handicap']
            })
            
        return pd.DataFrame(results)

    def update_sheet(self, sheets_service, data, range_name):
        """Update Google Sheet with processed results"""
        try:
            body = {
                'values': data.values.tolist()
            }
            result = sheets_service.values().update(
                spreadsheetId=self.SPREADSHEET_ID,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            return result
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def create_web_display(self):
        """Create Streamlit web display"""
        st.title("Relay Race Results")
        
        # Add tabs for different views
        tab1, tab2, tab3 = st.tabs(["Daily Results", "Overall Rankings", "Team Details"])
        
        with tab1:
            st.header("Daily Results")
            day_select = st.selectbox("Select Day", ["Day 1", "Day 2", "Day 3"])
            # Display daily results table
            
        with tab2:
            st.header("Overall Rankings")
            division_filter = st.multiselect("Filter by Division", ["Open", "Mixed"])
            # Display overall rankings
            
        with tab3:
            st.header("Team Details")
            team_select = st.selectbox("Select Team", ["Team 1", "Team 2", "Team 3"])
            # Display team details

def format_duration(duration):
    """Format timedelta to HH:MM:SS"""
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"