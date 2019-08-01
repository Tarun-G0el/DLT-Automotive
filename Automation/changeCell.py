import gspread
from oauth2client.service_account import ServiceAccountCredentials
from GenerateSeed import generateSeed
from GenerateAddress import genAddrFromSeed
import time

def setup():
	scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
	creds = ServiceAccountCredentials.from_json_keyfile_name('Compostable Cup Bin Project-abe8f907feca.json', scope)
	client = gspread.authorize(creds)
	wksp = client.open('IOTA for Automotive').sheet1
	return(wksp)

sheet = setup()

while True: # Periodically to indicate light passing
	sheet.update_acell('I2', 'green')
	print('green')
	time.sleep(10)
	sheet.update_acell('I2', 'red')
	print('red')
	time.sleep(10)