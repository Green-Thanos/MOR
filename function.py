import gspread
from datetime import datetime, timedelta

def connect_to_sheets():
    """Initialize connection to Google Sheets and get all worksheet references"""
    gc = gspread.service_account()
    spreadsheet = gc.open("Relay Data")
    
    return {
        'main': spreadsheet.worksheet("Main"),
        'registration': spreadsheet.worksheet("sheet1"),
        'day1': spreadsheet.worksheet("Day 1 Legs"),
        'day2': spreadsheet.worksheet("Day 2 Legs"),
        'day3': spreadsheet.worksheet("Day 3 Legs")
    }

def calculate_leg_time(start_time, end_time):
    try:
        start = datetime.strptime(start_time, "%H:%M:%S")
        end = datetime.strptime(end_time, "%H:%M:%S")
        
        if end < start:
            end += timedelta(days=1)
        
        duration = end - start
        return duration.total_seconds() / 3600 
    except ValueError:
        return 0  # Return 0 for invalid time formats

def calculate_handicap(team_data):
    ages = [int(age.strip()) for age in team_data['ages'].split(',') if age.strip().isdigit()]
    females = sum(1 for gender in team_data['gender'].split(',') if gender.strip().lower() == 'f')
    
    if not ages:
        return 1.0
        
    avg_age = sum(ages) / len(ages)
    gender_ratio = females / len(ages) if ages else 0
    
    handicap = 1.0
    
    if avg_age > 50:
        handicap *= 0.90
    elif avg_age > 40:
        handicap *= 0.95
    
    if gender_ratio >= 0.5:
        handicap *= 0.98
    
    return round(handicap, 3)

def calculate_day_totals(worksheet, start_row=6, end_row=18, time_col='A'):
    total_times = {}
    records = worksheet.get_all_records()
    
    for record in records:
        team_id = record.get('Team ID')
        if team_id:
            leg_times = []
            for row in range(start_row, end_row + 1):
                cell_value = worksheet.acell(f'{time_col}{row}').value
                if cell_value:
                    try:
                        time_parts = cell_value.split(':')
                        hours = float(time_parts[0])
                        minutes = float(time_parts[1]) / 60 if len(time_parts) > 1 else 0
                        seconds = float(time_parts[2]) / 3600 if len(time_parts) > 2 else 0
                        leg_times.append(hours + minutes + seconds)
                    except (ValueError, IndexError):
                        continue
            
            total_times[team_id] = sum(leg_times)
    
    return total_times

def update_main_sheet(worksheets, team_data):
    main_sheet = worksheets['main']
    
    # Calculate daily totals
    day1_totals = calculate_day_totals(worksheets['day1'], time_col='A')
    day2_totals = calculate_day_totals(worksheets['day2'], time_col='B')
    day3_totals = calculate_day_totals(worksheets['day3'], time_col='C')
    
    # Prepare headers
    headers = ['Team ID', 'Team Name', 'Day 1 Total', 'Day 2 Total', 'Day 3 Total', 
              'Overall Total', 'Handicap', 'Adjusted Total']
    main_sheet.clear()
    main_sheet.append_row(headers)
    
    # Update data for each team
    for team in team_data:
        team_id = team['Team ID']
        team_name = team['Team Name']
        
        day1_time = day1_totals.get(team_id, 0)
        day2_time = day2_totals.get(team_id, 0)
        day3_time = day3_totals.get(team_id, 0)
        
        overall_total = day1_time + day2_time + day3_time
        
        handicap = calculate_handicap({
            'ages': team.get('Ages', ''),
            'gender': team.get('Gender', '')
        })
        
        adjusted_total = overall_total * handicap
        
        row_data = [
            team_id,
            team_name,
            round(day1_time, 3),
            round(day2_time, 3),
            round(day3_time, 3),
            round(overall_total, 3),
            handicap,
            round(adjusted_total, 3)
        ]
        
        main_sheet.append_row(row_data)

def main():
    try:
        # Connect to sheets
        worksheets = connect_to_sheets()
        
        # Get team registration data
        team_data = worksheets['registration'].get_all_records()
        
        # Update main sheet with calculations
        update_main_sheet(worksheets, team_data)
        
        print("Relay data done")
        
    except Exception as e:
        print(f"Error processing relay data: {str(e)}")

if __name__ == "__main__":
    main()