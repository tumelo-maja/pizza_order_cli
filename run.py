import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('fresh_leafy_greens')

orders_sheet = SHEET.worksheet('orders')

orders_df = get_as_dataframe(orders_sheet)
print(orders_df)

print("Hello")
