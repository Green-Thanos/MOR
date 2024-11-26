import gspread

# Match Act times from day sheet to main worksheet

def match_team_times():
    gc = gspread.service_account()
    spreadsheet = gc.open("Relay Data")
    
    times_sheet = spreadsheet.worksheet("Relay Legs")  
    main_sheet = spreadsheet.worksheet("Main")
    
    # Get Team IDs and their corresponding times from the times sheet
    times_data = times_sheet.get_all_values()[2:52]  # Rows 3-52
    
    main_sheet_data = main_sheet.get_all_values()
    
    # Process each row
    for row_index, row in enumerate(times_data, start=3):
        team_id = row[0]  # Team ID from first column (change!!!!)
        total_time = row[20]  # Column U (index 20)
        
        # Find this team in the main sheet
        for main_row_index, main_row in enumerate(main_sheet_data, start=1):
            if main_row and main_row[0] == team_id:
                # Adjust column as needed - this is just an example _!!!!!!! COlumn is wrong
                main_sheet.update_cell(main_row_index, 21, total_time)
                break

match_team_times()
print("Team times matched to main sheet")