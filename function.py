import gspread

gc = gspread.service_account()

wks = gc.open("Relay Data").sheet1

values_list = wks.col_values(1)

print(values_list)