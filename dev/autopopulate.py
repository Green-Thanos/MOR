import gspread
gc = gspread.service_account()
spreadsheet = gc.open("Relay Data")

times_sheet = spreadsheet.worksheet("Day1")  
worksheet = spreadsheet.worksheet("Open")

# AUTOPOPULATE IS VERY RATE LIMITED 

def actpace():
    for row in range(3, 47): # 2 to 10
        formula = f'=E{row}/95.3'
        worksheet.update_cell(row, 6, formula)
# worksheet.copy_formula(f'C{row}', base_formula)

def hctime():
    for row in range(3, 47): # 2 to 10
        formula = f'=E{row} * D{row}'
        worksheet.update_cell(row, 7, formula)


def hcpace():
    for row in range(3, 47): # 2 to 10
        formula = f'=E{row}/95.3 * D{row}'
        worksheet.update_cell(row, 8, formula)

hcpace()