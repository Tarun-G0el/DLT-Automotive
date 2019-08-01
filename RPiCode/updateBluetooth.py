import bluetooth
import time
import RPi.GPIO as GPIO
from setup import setup

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
# TODO: If we run out of code values in database, to add more and set it. . .
##code = '5'
##cell = sheet.find(code)
##cellValue = 'C' + str(cell.row)

cellRow = cellValue[1]
cellUpdate = 'C' + str(cellRow)

print('Searching for Bluetooth devices. . .')

try:
    while True:
        time.sleep(1)
        nearby_devices = bluetooth.discover_devices(lookup_names=True)

        print('Found %d devices!' % len(nearby_devices))

        i = 1
        for addr, name in nearby_devices:
            print('%s: %s - %s' % (i, addr, name))
            i += 1
                
        addr = '3C:2E:FF:27:52:F7'
        state = bluetooth.lookup_name(addr)
        services = bluetooth.find_service(address=addr)

        if state == None and services == []:
            print('Device not in range...')
        else:
            print('Device within range...Making change to cloud now')
            sheet.update_acell(cellUpdate, 'T')
finally:
    sheet.update_acell(cellValue, str(int(cellValue[1])-1))



