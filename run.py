import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]


def connect_google_sheets(sheet_name):
    
    CREDS = Credentials.from_service_account_file('creds.json')
    SCOPED_CREDS = CREDS.with_scopes(SCOPE)
    GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
    SHEET = GSPREAD_CLIENT.open('fresh_leafy_greens')
    
    sheet_object = SHEET.worksheet(sheet_name)
    
    return sheet_object

def main():

    print("Main is running")
    
    orders_sheet = connect_google_sheets('orders')
    orders_df = get_as_dataframe(orders_sheet)
    print(orders_df)


main()
