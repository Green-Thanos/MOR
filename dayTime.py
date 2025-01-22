import gspread
from datetime import datetime, timedelta
import time

def calculate_leg_duration(race_time_str, start_time=datetime(2024, 1, 1, 6, 0)):
    try:
        race_time = datetime.strptime(race_time_str, "%I:%M:%S %p")
        
        if race_time.hour < 6: #6 am
            hours = race_time.hour + 12 + (race_time.minute / 60) + (race_time.second / 3600)
        elif race_time.hour >= 6:
            hours = (race_time.hour - 6) + (race_time.minute / 60) + (race_time.second / 3600)
        
        return hours
    except ValueError:
        print(f"Error processing time: {race_time_str}")
        return 0

def sum_leg_times(sheet):
    gc = gspread.service_account()
    sheet = gc.open("Relay Data").worksheet(sheet)
    
    # row 3 to 52
    for row in range(3, 53):
        f_to_r_values = sheet.range(f'F{row}:R{row}') # f to r in row
        e_col_value = sheet.acell(f'E{row}').value
        
        values = [cell.value for cell in f_to_r_values]
        times = [time_to_decimal_hours(val) for val in values]
        
        if e_col_value:
            leg_duration = calculate_leg_duration(e_col_value)
            times.append(leg_duration)
        
        decimal_sum = sum(times)
        
        hours = int(decimal_sum)
        minutes = int((decimal_sum * 60) % 60)
        seconds = int((decimal_sum * 3600) % 60)
        time_str = f"{hours}:{minutes:02d}:{seconds:02d}"
        
        # column D
        sheet.update_cell(row, 4, time_str)
        time.sleep(1.5) # rate limit (can change to one request for better scaling)

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

sum_leg_times("Day1")
print("Times updated column U")