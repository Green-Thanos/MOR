import gspread
# import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def match_team_times():
    gc = gspread.service_account()
    spreadsheet = gc.open("Relay Data")
    
    times_sheet = spreadsheet.worksheet("Day1")  
    main_sheet = spreadsheet.worksheet("Open")
    
    times_data = times_sheet.get_all_values()[2:52]  
    main_sheet_data = main_sheet.get_all_values()
    
    matches_found = 0
    total_attempts = 0
    
    main_sheet_dict = {row[1].strip(): row for row in main_sheet_data if row and len(row) > 0}
    
    batch_updates = []
    
    for row_index, row in enumerate(times_data, start=4):
        try:
            if len(row) < 22:
                logger.warning(f"insuf columns row {row_index}")
                continue
            
            team_id = row[21].strip()  # Column V
            total_time = row[20].strip()  # Column U
            
            # Skip empty team IDs
            if not team_id:
                logger.warning(f"Empty team ID in row {row_index}")
                continue
            
            total_attempts += 1
            
            if team_id in main_sheet_dict:
                main_row_index = main_sheet_dict[team_id][0]  
                batch_updates.append({
                    'range': f'G{main_row_index}',
                    'values': [[total_time]]
                })
                matches_found += 1
            else:
                logger.warning(f"No match found for team ID {team_id} in row {row_index}")
        
        except Exception as row_error:
            logger.error(f"Error row {row_index}: {row_error}")
    
    if batch_updates:
        try:
            main_sheet.batch_update(batch_updates)
        except Exception as batch_error:
            logger.error(f"Batch update failed: {batch_error}")
    
    logger.info(f"Total attempts: {total_attempts}")
    logger.info(f"Matches found: {matches_found}")
    print(f"Matched {matches_found} out of {total_attempts} team times to main sheet")

match_team_times()