from flask import Flask, render_template
import gspread

app = Flask(__name__)

def get_google_sheet():
    gc = gspread.service_account()
    return gc.open("Relay Data").worksheet("Open")

@app.route("/")
def leaderboard():
    sheet = get_google_sheet()
    
    all_values = sheet.get_all_values()[2:]  # Start from row 3
    
    leaderboard_data = []
    for row in all_values:
        if len(row) >= 7 and row[2].strip() and row[6].strip():
            leaderboard_data.append({
                "team": row[2],  # Column C
                "time": row[6]   # Column G
            })
        else:
            break
    
    try:
        leaderboard_data.sort(key=lambda x: x["time"])
    except:
        pass

    return render_template("./leaderboard.html", leaderboard=leaderboard_data)

if __name__ == "__main__":
    app.run(debug=True)