from time import sleep
import RPi.GPIO as GPIO
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def setup():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('Compostable Cup Bin Project-abe8f907feca.json', scope)
    client = gspread.authorize(creds)
    wksp = client.open('Compostable Cups List').sheet1
    return(wksp)

##GPIO.cleanup()

GPIO.setmode(GPIO.BCM)
motorA=15
motorB=4

GPIO.setup(motorA, GPIO.OUT)
GPIO.setup(motorB, GPIO.OUT)

def forward(wait):
    GPIO.output(motorB, False)
    GPIO.output(motorA, True)
    sleep(wait)

def reverse(wait):
    GPIO.output(motorA, False)
    GPIO.output(motorB, True)
    sleep(wait)

sheet = setup()

items = sheet.col_values(4)

forward(5)#lock on startup

print ('******** Please scan your cup ********** \n')

try:
    while True:
        sleep(0.1)

        print ('Bar code:')
    ##    code = '5099874240563'
        code = str(input())

        if code in items:
            cell = sheet.find(code)
            setTrue = 'F' + str(cell.row)
            sheet.update_acell(setTrue, 'T')
        ##        keys = list(items.keys())
        ##        values = list(items.values())
        ##        print (values[keys.index(code)] + ' is recyclable ^V^ \n')
            print ('The coffee cup with barcode ' + code + ' is recyclable ^V^ \n')
            print ('The bin is being opened now :)')
            
            #nearby_devices = discover_devices(lookup_names = True)
            #for name, addr in nearby_devices:
            #    print (" %s - %s" % (addr, name))
            
            reverse(5)
            forward(5)
            
            print ('******** Please scan your cup ********** \n')
            
        else:
            print ('The cup is not recycable !! \n')
            print ('******** Please scan your cup ********** \n')
finally:
    GPIO.cleanup()