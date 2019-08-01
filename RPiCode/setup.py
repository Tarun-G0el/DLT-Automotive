import gspread
from oauth2client.service_account import ServiceAccountCredentials

def setup():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('Compostable Cup Bin Project-abe8f907feca.json', scope)
    client = gspread.authorize(creds)
    wksp = client.open('IOTA for Automotive').sheet1
    return(wksp)