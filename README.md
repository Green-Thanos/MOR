# How to use

1. Copy [this](https://docs.google.com/spreadsheets/d/1vNqw4AmZjE4meE7uHoIqmmQzYV6XElKkV-SPNdfqfas/edit?usp=sharing) template
2. Create google forms for each day sheet with Timestamp, Email, Team Number, Start time, and Leg Times (ensuring columns match correctly with the template)
3. Install Python 3 and Git
4. `git clone Green-Thanos/MOR`
5. `cd MOR`
6. `pip install -r requirements.txt`
7. Edit any column values if you need to change the format in `app/columnValues.json`
8. Format column values for ALL times in Open/Mixed to be "Duration"
8. `python app/function.py` to update the leaderboard automatically


# Steps to get a google sheet service account

Enable API Access for a Project
Head to Google Developers Console and create a new project (or select the one you already have).

In the box labeled “Search for APIs and Services”, search for “Google Drive API” and enable it.

In the box labeled “Search for APIs and Services”, search for “Google Sheets API” and enable it.

For Bots: Using Service Account
A service account is a special type of Google account intended to represent a non-human user that needs to authenticate and be authorized to access data in Google APIs [sic].

Since it’s a separate account, by default it does not have access to any spreadsheet until you share it with this account. Just like any other Google account.

Here’s how to get one:

Enable API Access for a Project if you haven’t done it yet.

Go to “APIs & Services > Credentials” and choose “Create credentials > Service account key”.

Fill out the form

Click “Create” and “Done”.

Press “Manage service accounts” above Service Accounts.

Press on ⋮ near recently created service account and select “Manage keys” and then click on “ADD KEY > Create new key”.

Select JSON key type and press “Create”.

You will automatically download a JSON file with credentials. It may look like this:

{
    "type": "service_account",
    "project_id": "api-project-XXX",
    "private_key_id": "2cd … ba4",
    "private_key": "-----BEGIN PRIVATE KEY-----\nNrDyLw … jINQh/9\n-----END PRIVATE KEY-----\n",
    "client_email": "473000000000-yoursisdifferent@developer.gserviceaccount.com",
    "client_id": "473 … hd.apps.googleusercontent.com",
    ...
}
Remember the path to the downloaded credentials file. Also, in the next step you’ll need the value of client_email from this file.

Very important! Go to your spreadsheet and share it with a client_email from the step above. Just like you do with any other Google account. If you don’t do this, you’ll get a gspread.exceptions.SpreadsheetNotFound exception when trying to access this spreadsheet from your application or a script.


Copy the downloaded file to app/creds.json

**NOT RECOMMENDED**
Move the downloaded file to ~/.config/gspread/service_account.json. Windows users should put this file to %APPDATA%\gspread\service_account.json.



# Hosting

In progress

`python app/server.py` to run development server with automatically updating spreadsheet
leaderboard at `http://localhost:5000`
post credentials in .env

render.com for python (clone git repo)








# Michigan Outback Relay System

3 Day results
Start time, end time (date being recorded and clock time, not stopwatched)
Actual Time, Pace
Handicap Time Pace
Penalties

# Problems

- rate limit
- not sure if accounting for team times over 24 hours works

# Steps

Make sure the all the time columns on all the sheets are formatted to time duration
grab credential file from google api
the script will not edit the original time sheet (the ones with the google form times)
race numbers should be unique to each team (its like id, if you put the same id in both the mix/open division it will get confused and assign the last one to show to all the teams with the same id)
Google form should have id

+ cli usage

















# TODO

## Issue:
- google api rate limit fix (add a delay?)
```
APIError: [429]: Quota exceeded for quota metric 'Read requests' and limit 'Read requests per minute per user' of service 'sheets.googleapis.com' for consumer 'project_number:1091241016890'.
```
https://www.reddit.com/r/learnpython/comments/1bfsqb2/best_way_to_import_a_python_file_into_your_main/

main.py spreadsheet api depreciated


Questions:

Which parts need automation - I'm assuming moving times to the main sheet for ACT time, then everything else can be autopopulated and the dates removed

Moving parts:
- The formulas for the different stats, a proper display maybe, penalties, which division, handicap formula
