import gspread
gc = gspread.service_account()
spreadsheet = gc.open("Relay Data")

times_sheet = spreadsheet.worksheet("Day1")  
worksheet = spreadsheet.worksheet("Open")

formulaList = [
    [2, 3]
]

for row in range(3, 48): # 2 to 10
    formula = f'=G{row}/95.3'
    worksheet.update_cell(row, 8, formula)
# worksheet.copy_formula(f'C{row}', base_formula)
