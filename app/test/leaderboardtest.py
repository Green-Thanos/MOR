import requests

# Replace with your development server's URL
BASE_URL = "http://127.0.0.1:5000"

def test_leaderboard_fetch():
    try:
        # Test Open Division
        open_response = requests.get(f"{BASE_URL}/api/leaderboard", params={"division": "Open"})
        if open_response.status_code == 200:
            print("Open Division:")
            print(open_response.json())
        else:
            print(f"Failed to fetch Open Division: {open_response.status_code} - {open_response.text}")

        # Test Mixed Division
        mixed_response = requests.get(f"{BASE_URL}/api/leaderboard", params={"division": "Mixed"})
        if mixed_response.status_code == 200:
            print("Mixed Division:")
            print(mixed_response.json())
        else:
            print(f"Failed to fetch Mixed Division: {mixed_response.status_code} - {mixed_response.text}")

    except Exception as e:
        print(f"Error during leaderboard fetch: {e}")

if __name__ == "__main__":
    test_leaderboard_fetch()
