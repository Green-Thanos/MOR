import gspread
from datetime import datetime, timedelta

def calculate_leg_duration(race_time_str, start_time=datetime(2024, 1, 1, 6, 0)):
    try:
        # Parse the race time with AM/PM
        race_time = datetime.strptime(race_time_str, "%I:%M:%S %p")
        race_datetime = start_time.replace(hour=race_time.hour, minute=race_time.minute, second=race_time.second)
        
        # Add 12 hours for PM times
        if 'PM' in race_time_str and race_time.hour != 12:
            race_datetime += timedelta(hours=12)
        
        # Handle times before 6 AM (consider them as next day)
        if race_datetime.hour < 6:
            race_datetime += timedelta(days=1)
        
        # Calculate duration from 6 AM start
        duration = race_datetime - start_time
        
        # Convert to decimal hours
        hours = duration.total_seconds() / 3600
        return hours
    except ValueError:
        return 0
    
# TODO - just subtract 6 from the time, and then parse AM or PM and add it to the leg sum time hopefully that works for the column
# Then how to add this time to the right team in the main page?




def sum_leg_times():
    gc = gspread.service_account()
    sheet = gc.open("Relay Data").worksheet("Sheet2")
    
    # Process rows 3 to 52
    for row in range(3, 53):
        # Get values from F to R and E for current row
        f_to_r_values = sheet.range(f'F{row}:R{row}')
        e_col_value = sheet.acell(f'E{row}').value
        
        # Convert F-R times to decimal hours
        values = [cell.value for cell in f_to_r_values]
        times = [time_to_decimal_hours(val) for val in values]
        
        # Add leg duration from column E
        if e_col_value:
            leg_duration = calculate_leg_duration(e_col_value)
            times.append(leg_duration)
        
        # Sum times
        decimal_sum = sum(times)
        
        # Convert back to time format
        hours = int(decimal_sum)
        minutes = int((decimal_sum * 60) % 60)
        seconds = int((decimal_sum * 3600) % 60)
        time_str = f"{hours}:{minutes:02d}:{seconds:02d}"
        
        # Update column U
        sheet.update_cell(row, 21, time_str)

def time_to_decimal_hours(time_str):
    if not time_str or time_str.strip() == '':
        return 0
    
    try:
        time_parts = time_str.split(':')
        hours = float(time_parts[0])
        minutes = float(time_parts[1])
        seconds = float(time_parts[2])
        return hours + (minutes / 60) + (seconds / 3600)
    except:
        return 0

sum_leg_times()
print("Times summed and updated in column U")