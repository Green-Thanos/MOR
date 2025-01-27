from flask import Flask, render_template
import gspread
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def get_google_sheet():
    creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    if not creds_json:
        raise ValueError("GOOGLE_CREDENTIALS_JSON environment variable is not set")
    
    creds_dict = json.loads(creds_json)
    gc = gspread.service_account_from_dict(creds_dict)
    return gc.open("Relay Data").worksheet("Open")

@app.route("/")
def leaderboard():
    sheet = get_google_sheet()
    
    with open('columnValues.json') as f:
        config = json.load(f)
    
    team_col = ord(config['teamName']) - 97  # Convert letter to 0-based index
    time_col = ord(config['actMatchLetter']) - 65
    
    all_values = sheet.get_all_values()[2:]  # Start from row 3
    
    leaderboard_data = []
    for row in all_values:
        if len(row) > max(team_col, time_col) and row[team_col].strip() and row[time_col].strip():
            leaderboard_data.append({
                "team": row[team_col],
                "time": row[time_col]
            })
        else:
            break
    
    try:
        leaderboard_data.sort(key=lambda x: x["time"])
    except Exception as e:
        print(f"Error sorting data: {e}")

    return render_template("leaderboard2.html", leaderboard=leaderboard_data)

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, port=port)