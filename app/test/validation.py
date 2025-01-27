import logging
from typing import Dict, List, Tuple
import unittest
from unittest.mock import patch, MagicMock
from function import RelayManager, RateLimiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestRelayManager(unittest.TestCase):
    def setUp(self):
        """Set up the test environment."""
        self.manager = RelayManager()
        self.manager.connect_sheets = MagicMock()  # Mock Google Sheets connection
        self.manager.get_cached_worksheet = MagicMock()
        self.manager.get_cached_values = MagicMock()

        # Mock data for division and day sheets
        self.mock_division_values = [
            ["Team ID", "Team Name", "Handicap Factor"],
            ["1", "Team A", "1.2"],
            ["2", "Team B", ""],  # Missing handicap factor
            ["3", "Team C", "invalid"],  # Invalid handicap factor
            ["4", "Team D", "1.5"]
        ]
        self.mock_day_values = [
            ["Race Number", "Team ID", "Leg Times"],
            ["1", "1", "1:30:00", "2:00:00"],  # Team A
            ["2", "2", "1:45:00", "2:15:00"],  # Team B
            ["3", "3", "1:20:00", "1:50:00"],  # Team C
            ["4", "4", "1:10:00", "1:40:00"]   # Team D
        ]

        # Mock worksheet and values
        self.manager.get_cached_values.return_value = self.mock_division_values
        self.manager.get_cached_worksheet.return_value.get_all_values.return_value = self.mock_day_values

    def test_normal_scenario(self):
        """Test normal scenario with valid data."""
        logger.info("Testing normal scenario...")
        matches, attempts = self.manager.update_division_times("Day1", "Open")
        self.assertEqual(matches, 4)  # All teams should match
        self.assertEqual(attempts, 4)

    def test_missing_handicap_factor(self):
        """Test scenario where handicap factor is missing."""
        logger.info("Testing missing handicap factor...")
        matches, attempts = self.manager.update_division_times("Day1", "Open")
        self.assertEqual(matches, 4)
        self.assertEqual(attempts, 4)

        # Verify that the handicap factor defaults to 1 for Team B
        division_updates = self.manager.get_cached_worksheet.return_value.batch_update.call_args[0][0]
        for update in division_updates:
            if "hc" in update["range"] and "Team B" in str(update):
                self.assertIn("*1.0", update["values"][0][0])  # Default factor 1

    def test_invalid_handicap_factor(self):
        """Test scenario where handicap factor is invalid."""
        logger.info("Testing invalid handicap factor...")
        matches, attempts = self.manager.update_division_times("Day1", "Open")
        self.assertEqual(matches, 4)
        self.assertEqual(attempts, 4)

        # Verify that the handicap factor defaults to 1 for Team C
        division_updates = self.manager.get_cached_worksheet.return_value.batch_update.call_args[0][0]
        for update in division_updates:
            if "hc" in update["range"] and "Team C" in str(update):
                self.assertIn("*1.0", update["values"][0][0])  # Default factor 1

    def test_cumulative_totals(self):
        """Test cumulative totals for Day2 and Day3."""
        logger.info("Testing cumulative totals...")
        # Mock data for Day2
        self.mock_day_values = [
            ["Race Number", "Team ID", "Leg Times"],
            ["1", "1", "1:30:00", "2:00:00"],  # Team A
            ["2", "2", "1:45:00", "2:15:00"],  # Team B
            ["3", "3", "1:20:00", "1:50:00"],  # Team C
            ["4", "4", "1:10:00", "1:40:00"]   # Team D
        ]
        self.manager.get_cached_values.return_value = self.mock_day_values

        # Test Day2
        matches, attempts = self.manager.update_division_times("Day2", "Open")
        self.assertEqual(matches, 4)
        self.assertEqual(attempts, 4)

        # Verify cumulative totals
        division_updates = self.manager.get_cached_worksheet.return_value.batch_update.call_args[0][0]
        for update in division_updates:
            if "tact" in update["range"]:
                self.assertIn("TEXT", update["values"][0][0])  # Cumulative time formula
            if "tactpace" in update["range"]:
                self.assertIn("TEXT", update["values"][0][0])  # Cumulative pace formula

    def test_empty_rows(self):
        """Test scenario with empty rows in the day sheet."""
        logger.info("Testing empty rows...")
        self.mock_day_values = [
            ["Race Number", "Team ID", "Leg Times"],
            [],  # Empty row
            ["1", "1", "1:30:00", "2:00:00"],  # Team A
            [],  # Empty row
            ["2", "2", "1:45:00", "2:15:00"]   # Team B
        ]
        self.manager.get_cached_values.return_value = self.mock_day_values

        matches, attempts = self.manager.update_division_times("Day1", "Open")
        self.assertEqual(matches, 2)  # Only 2 valid teams
        self.assertEqual(attempts, 2)

    def test_no_matching_teams(self):
        """Test scenario where no teams match between division and day sheets."""
        logger.info("Testing no matching teams...")
        self.mock_division_values = [
            ["Team ID", "Team Name", "Handicap Factor"],
            ["5", "Team E", "1.2"],  # No match in day sheet
            ["6", "Team F", "1.3"]   # No match in day sheet
        ]
        self.manager.get_cached_values.return_value = self.mock_division_values

        matches, attempts = self.manager.update_division_times("Day1", "Open")
        self.assertEqual(matches, 0)  # No matches
        self.assertEqual(attempts, 2)  # 2 attempts

if __name__ == "__main__":
    unittest.main()