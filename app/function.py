import json
import gspread
from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple
import time
from google.api_core import retry

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_requests: int = 60, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def wait_if_needed(self):
        current_time = time.time()
        self.requests = [req_time for req_time in self.requests 
                        if current_time - req_time < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            sleep_time = self.requests[0] + self.time_window - current_time
            if sleep_time > 0:
                logger.info(f"Rate limit reached, waiting {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
            self.requests = self.requests[1:]
        
        self.requests.append(current_time)

class RelayManager:
    def __init__(self, config_path: str = 'columnValues.json'):
        self.config = self._load_config(config_path)
        self.gc = None
        self.spreadsheet = None
        self.divisions = ["Open", "Mixed"]
        self.days = ["Day1", "Day2", "Day3"]
        self.rate_limiter = RateLimiter()
        self.cache = {}
        
    def _load_config(self, config_path: str) -> Dict:
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise

    def connect_sheets(self):
        try:
            self.gc = gspread.service_account()
            self.spreadsheet = self.gc.open("Relay Data")
            logger.info("Successfully connected to Google Sheets")
        except Exception as e:
            logger.error(f"Error connecting to sheets: {e}")
            raise

    def get_cached_worksheet(self, sheet_name: str):
        if sheet_name not in self.cache:
            self.rate_limiter.wait_if_needed()
            self.cache[sheet_name] = self.spreadsheet.worksheet(sheet_name)
        return self.cache[sheet_name]

    def get_cached_values(self, sheet_name: str):
        cache_key = f"{sheet_name}_values"
        if cache_key not in self.cache:
            self.rate_limiter.wait_if_needed()
            worksheet = self.get_cached_worksheet(sheet_name)
            self.cache[cache_key] = worksheet.get_all_values()
        return self.cache[cache_key]

    def time_str_to_decimal(self, time_str: str) -> Optional[float]:
        try:
            if not time_str or not time_str.strip():
                return None
            
            parts = time_str.split(':')
            if len(parts) != 3:
                return None
                
            hours = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])
            
            return hours + (minutes / 60) + (seconds / 3600)
        except:
            return None

    def decimal_to_time_str(self, decimal_time: float) -> str:
        hours = int(decimal_time)
        minutes = int((decimal_time * 60) % 60)
        seconds = int((decimal_time * 3600) % 60)
        return f"{hours}:{minutes:02d}:{seconds:02d}"

    def calculate_leg_times(self, values: List[str], timesheet_config: Dict) -> Optional[Dict]:
        """Calculate leg times while preserving team information."""
        try:
            start_idx = ord(timesheet_config["legBegin"]) - 65
            end_idx = ord(timesheet_config["legEnd"]) - 65
            
            leg_times = values[start_idx:end_idx+1]
            times = []
            
            for time_str in leg_times:
                if time_str and time_str.strip():
                    decimal_time = self.time_str_to_decimal(time_str)
                    if decimal_time is not None:
                        times.append(decimal_time)

            if not times:
                return None

            total_time = sum(times)
            return {
                'elapsed': self.decimal_to_time_str(total_time),
                'decimal': total_time
            }
            
        except Exception as e:
            logger.error(f"Error calculating leg times: {e}")
            return None

    def update_division_times(self, day: str, division: str) -> Tuple[int, int]:
        try:
            matches_found = 0
            total_attempts = 0

            logger.info(f"Getting sheets for {day} and {division}")
            day_sheet = self.get_cached_worksheet(day)
            division_sheet = self.get_cached_worksheet(division)
            
            day_values = self.get_cached_values(day)
            division_values = self.get_cached_values(division)
            
            timesheet_config = self.config['timesheet']
            day_columns = self.config[day]
            handicap_factor_col = self.config.get("handicapFactor", "D")  # Default to column D
            
            division_dict = {row[1].strip(): idx + 1 for idx, row in enumerate(division_values[1:]) 
                        if row and len(row) > 1 and row[1].strip()}

            division_updates = []
            
            # Determine the last row with data in the day sheet
            last_row = len(day_values)
            
            # Process rows dynamically
            for row_idx, row in enumerate(day_values[2:last_row], start=3):
                if not row or len(row) < 3:
                    continue

                team_id = row[2].strip()  # Column C
                if not team_id:
                    continue

                total_attempts += 1
                
                if team_id in division_dict:
                    div_row = division_dict[team_id] + 1
                    matches_found += 1
                    
                    # Get the handicap factor from column D
                    try:
                        handicap_factor = float(division_values[div_row - 1][ord(handicap_factor_col) - 65])
                    except (ValueError, IndexError, TypeError):
                        # If the handicap factor is missing or invalid, default to 1
                        handicap_factor = 1.0
                        logger.warning(f"No valid handicap factor for team {team_id} in row {div_row}. Using factor 1.")
                    
                    # Calculate times
                    times = self.calculate_leg_times(row, timesheet_config)
                    
                    if times:
                        decimal_pace = times['decimal'] / 95.3
                        actual_pace = self.decimal_to_time_str(decimal_pace)
                        
                        # Update division sheet with actual time and pace
                        division_updates.extend([
                            {
                                'range': f'{day_columns["act"]}{div_row}',
                                'values': [[times['elapsed']]]
                            },
                            {
                                'range': f'{day_columns["actpace"]}{div_row}',
                                'values': [[f"=TEXT(({day_columns['act']}{div_row})/95.3, \"hh:mm:ss\")"]]
                            },
                            {
                                'range': f'{day_columns["hc"]}{div_row}',
                                'values': [[f"={day_columns['act']}{div_row}*{handicap_factor}"]]
                            },
                            {
                                'range': f'{day_columns["hcpace"]}{div_row}',
                                'values': [[f"=TEXT(({day_columns['hc']}{div_row})/95.3, \"hh:mm:ss\")"]]
                            }
                        ])
                        
                        # Handle cumulative totals for Day2 and Day3
                        if day in ["Day2", "Day3"]:
                            logger.info(f"Processing cumulative totals for {day} Row {div_row}")
                            
                            # Build cumulative time formula
                            prev_days = self.days[:self.days.index(day)]  # Get all previous days
                            formula_parts = []
                            valid_days = 1  # Start with the current day
                            
                            # Start with current day
                            current_time_cell = f'{day_columns["act"]}{div_row}'
                            formula_parts.append(f'TIMEVALUE({current_time_cell})*24')  # Convert current time to hours
                            
                            # Add previous days
                            for prev_day in prev_days:
                                prev_col = self.config[prev_day]["act"]
                                prev_cell = f'{prev_col}{div_row}'
                                formula_parts.append(f'IF(NOT(ISBLANK({prev_cell})), TIMEVALUE({prev_cell})*24, 0)')  # Add previous day's time in hours
                                valid_days += 1
                            
                            # Construct final formulas
                            time_sum = '+'.join(formula_parts)  # Sum all time values (current day + previous days)
                            
                            # Total time formula (sum of all times in hh:mm:ss format)
                            total_time_formula = f'=TEXT(({time_sum})/24, "h:mm:ss")'
                            
                            # Total pace formula (total time / total distance)
                            total_pace_formula = f'=TEXT((({time_sum})/24)/(95.3*{valid_days}), "h:mm:ss")'
                            
                            # Handicap formulas
                            total_hc_formula = f'={day_columns["tact"]}{div_row}*{handicap_factor}'
                            total_hcpace_formula = f'=TEXT(({day_columns["thc"]}{div_row})/95.3, "hh:mm:ss")'
                            
                            logger.info(f"Adding formulas for row {div_row}: Time={total_time_formula}, Pace={total_pace_formula}")
                            
                            division_updates.extend([
                                {
                                    'range': f'{day_columns["tact"]}{div_row}',
                                    'values': [[total_time_formula]] 
                                },
                                {
                                    'range': f'{day_columns["tactpace"]}{div_row}',
                                    'values': [[total_pace_formula]]  
                                },
                                {
                                    'range': f'{day_columns["thc"]}{div_row}',
                                    'values': [[total_hc_formula]]  
                                },
                                {
                                    'range': f'{day_columns["thcpace"]}{div_row}',
                                    'values': [[total_hcpace_formula]]  
                                }
                            ])

            # Perform batch updates
            if division_updates:
                logger.info(f"Performing batch update for {division} {day} with {len(division_updates)} updates")
                self.rate_limiter.wait_if_needed()
                division_sheet.batch_update(division_updates, value_input_option='USER_ENTERED')
                logger.info(f"Batch update completed successfully")

            logger.info(f"Updated {division} division for {day}: {matches_found}/{total_attempts} matches")
            return matches_found, total_attempts
            
        except Exception as e:
            logger.error(f"Error updating {division} division for {day}: {e}", exc_info=True)
            return 0, 0

    def update_all_divisions(self) -> Dict[str, Dict[str, Tuple[int, int]]]:
        results = {}
        
        for division in self.divisions:
            results[division] = {}
            for day in self.days:
                matches, attempts = self.update_division_times(day, division)
                results[division][day] = (matches, attempts)
                time.sleep(1)  # ratelimiting
                
        return results

def test_relay_manager():
    """Test the relay manager functionality."""
    try:
        manager = RelayManager()
        print("✓ Successfully initialized RelayManager")
        
        manager.connect_sheets()
        print("✓ Successfully connected to Google Sheets")

        print("\nTesting all divisions and days...")
        for division in ["Open", "Mixed"]:
            print(f"\n{division} Division:")
            for day in ["Day1", "Day2", "Day3"]:
                matches, attempts = manager.update_division_times(day, division)
                print(f"  {day}: {matches}/{attempts} matches")
                time.sleep(1) # ratelimiting
        
        # Test single update
        #print("\nTesting single division update...")
        #matches, attempts = manager.update_division_times("Day1", "Open")
        #print(f"Day1 Open division: {matches}/{attempts} matches")
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_relay_manager()