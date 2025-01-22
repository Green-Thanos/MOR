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
