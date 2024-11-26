import gspread

worksheet = ... # worksheet

# Method 1: Using copy_formula()
base_formula = '=SUM(A1:B1)'  # example formula
for row in range(2, 11):  # copy from row 2 to row 10
    worksheet.copy_formula(f'C{row}', base_formula)

# Method 2: Update with relative cell references
for row in range(2, 11):
    formula = f'=SUM(A{row}:B{row})'  # formula adjusts for each row
    worksheet.update_cell(row, 3, formula)