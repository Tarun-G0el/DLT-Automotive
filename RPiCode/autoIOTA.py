import bluetooth
import time
import RPi.GPIO as GPIO
from setup import setup

GPIO.setmode(GPIO.BCM)

TRIG=4
ECHO=18
distList = []

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.0001)
    GPIO.output(TRIG, False)
    while GPIO.input(ECHO) == False:
        start = time.time()
    while GPIO.input(ECHO) == True:
        end = time.time()
    sig_time = end-start
##centimeter
    distance = sig_time / 0.000058
##    print('Distance: {} cm'.format(distance))
    return distance/100

sheet = setup() # Read cloud data base
##Each RPi will have its own light Id that it will update
col_items = sheet.col_values(7)
##The id assigned to this RPi indicates that this is the corresponding light
items = iter(col_items) # Skip the first set of values as it involves the titles always
next(items)

##codeSet = False # Flag for if value was assigned for RPi Light ID
for count, item in enumerate(items):
    if '(assigned)' not in item:
        code = item
        updateCell = code + ' (assigned)'
        cellValue = 'G' + str(count+2)
        
        print('Light ID of %s' % updateCell)
        sheet.update_acell(cellValue, updateCell)
##        codeSet = True
        break
cellRow = cellValue[1]
cellUpdate = 'C' + str(cellRow)

try:
    while True:
        items = sheet.col_values(10)
        items = iter(items) # Skip the first set of values as it involves the titles always
        next(items)
        if not any('T' in s for s in items):
            print('Searching for Bluetooth devices. . .')
            # do bluetooth checks
            time.sleep(1)
                    
            addr = '3C:2E:FF:27:52:F7'
            state = bluetooth.lookup_name(addr)
            services = bluetooth.find_service(address=addr)

            if state == None and services == []:
                print('Device not in range...')
            else:
                print('Device within range...Making change to cloud now')
                sheet.update_acell(cellUpdate, 'T')
                sheet.update_acell('J2', 'T')
        else:
            # do light and car proximity checks
            passed = False
            search = True
            light = sheet.col_values(9)
            state = light[1]
            prevVal = get_distance()
            while search == True:
                #if cell values show that a car is in proximity, then start checking for passing
                time.sleep(0.1)
                currVal = get_distance()
                print(prevVal, currVal)
                if prevVal - 1 >= currVal:
                    print('object presence detected')
                    while not prevVal + 1 <= currVal:
                        passed = True
                        print('object still present')
                        prevVal = currVal
                        currVal = get_distance()
                        print(prevVal, currVal)
                        time.sleep(0.1)
                prevVal = currVal

                if passed == True:
                    light = sheet.col_values(9)
                    state = light[1]
                    search = False
                    sheet.update_acell('J2', 'F')
                    if state == 'green':
                        sheet.update_acell('E2', 'T')
                        items = sheet.col_values(4)
                        items = iter(items) # Skip the first set of values as it involves the titles always
                        next(items)
                    flag = True
                    while flag == True:
                        time.sleep(1)
                        addr = '3C:2E:FF:27:52:F7'
                        state = bluetooth.lookup_name(addr)
                        services = bluetooth.find_service(address=addr)

                        if state == None and services == []:
                            flag = False
                        else:
                            print('Device still within range')
            # tolerance level of values change
            # an object has not passed through
            # compare more values
finally:
    sheet.update_acell(cellUpdate, 'F')
    sheet.update_acell('J2', 'F')
    sheet.update_acell(cellValue, str(int(cellValue[1])-1))
    GPIO.cleanup()