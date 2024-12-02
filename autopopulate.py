import gspread
gc = gspread.service_account()
spreadsheet = gc.open("Relay Data")

times_sheet = spreadsheet.worksheet("Day1")  
worksheet = spreadsheet.worksheet("Open") # or mixed

formulaList = [
    [2, 3]
]

# Method 2: Update with relative cell references
for row in range(2, 11): # 2 to 10
    formula = f'=SUM(A{row}:B{row})'  # adjust formula for each row?
    worksheet.update_cell(row, 3, formula)
# alt syntax  
# worksheet.copy_formula(f'C{row}', base_formula)
