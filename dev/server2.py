from flask import Flask, render_template
import gspread

app = Flask(__name__)

def get_google_sheet():
    gc = gspread.service_account()
    return gc.open("Relay Data").worksheet("Open")

# Switch to periodically saving the times so that gspread doesn't ratelimit 

team = ord('c') - 97
time = ord('e') - 97

@app.route("/")
def leaderboard():
    sheet = get_google_sheet()
    
    all_values = sheet.get_all_values()[2:]  # Start from row 3
    
    leaderboard_data = []
    for row in all_values:
        if len(row) >= 7 and row[team].strip() and row[time].strip():
            print(row)
            leaderboard_data.append({
                "team": row[team], 
                "time": row[time]  
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