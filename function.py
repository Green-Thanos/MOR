import gspread
from datetime import datetime, timedelta

gc = gspread.service_account()
spreadsheet = gc.open("Relay Data")

# Access individual worksheets
registration = spreadsheet.worksheet("sheet1")
open_division = spreadsheet.worksheet("Open Division")
mixed_division = spreadsheet.worksheet("Mixed Division")
day1_legs = spreadsheet.worksheet("Day 1 Legs")
day2_legs = spreadsheet.worksheet("Day 2 Legs")
day3_legs = spreadsheet.worksheet("Day 3 Legs")

def calculate_leg_time(start_time, end_time):
    start = datetime.strptime(start_time, "%H:%M:%S")
    end = datetime.strptime(end_time, "%H:%M:%S")
    
    if end < start:
        end += timedelta(days=1)
    
    duration = end - start
    return duration.total_seconds() / 3600  # Return hours

def calculate_handicap(team_data):
    # Example algorithm for handicap calculation
    avg_age = sum(team_data['ages']) / len(team_data['ages'])
    gender_ratio = team_data['females'] / len(team_data['ages'])
    
    handicap = 1.0
    
    if avg_age > 40:
        handicap *= 0.95
    if gender_ratio > 0.5:
        handicap *= 0.98
    
    return handicap

def process_team_results(team_id, division):
    team_data = registration.row_values(team_id + 1)  # Assuming team_id starts at 0
    team_name = team_data[1]
    
    total_time = 0
    for day in [day1_legs, day2_legs, day3_legs]:
        day_legs = day.get_all_records()
        team_legs = [leg for leg in day_legs if leg['Team ID'] == team_id]
        
        day_start = datetime.strptime("06:00:00", "%H:%M:%S")
        for leg in team_legs:
            leg_time = calculate_leg_time(leg['Start Time'], leg['End Time'])
            total_time += leg_time
    
    handicap = calculate_handicap({
        'ages': [int(age) for age in team_data[2].split(',')],
        'females': sum(1 for gender in team_data[3].split(',') if gender.lower() == 'f')
    })
    
    adjusted_time = total_time * handicap
    
    if division == "Open":
        worksheet = open_division
    else:
        worksheet = mixed_division
    
    worksheet.append_row([team_id, team_name, total_time, handicap, adjusted_time])

# Process results for all teams
all_teams = registration.get_all_records()
for team in all_teams:
    process_team_results(team['Team ID'], team['Division'])

print("Results processed successfully.")