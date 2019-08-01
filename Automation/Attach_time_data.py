##
# Author: Tarun Goel
# Name: Attach_time_data.py
# Description: Makes a transaction and posts the time taken to the spreadsheet

from iota import *
from iota.adapter.wrappers import RoutingWrapper
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

def setup():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name('Compostable Cup Bin Project-abe8f907feca.json', scope)
  client = gspread.authorize(creds)
  wksp = client.open('Compostable Cups List').sheet1
  return(wksp)

sheet = setup()

for i in range(10,11):
  start = time.time()
  try:
    api =\
      Iota(
        # Send PoW requests to local node.
        # All other requests go to light wallet node.
        RoutingWrapper('https://nodes.thetangle.org:443')
          .add_route('attachToTangle', 'http://localhost:14265'),

        # Seed used for cryptographic functions.
        seed = b'CABREEMIRYLXLSWDLPUKFAMWMVBJYUIYQFBQGEE9BSCBCVOXXSTAXISQXGUIDPWZENEIYJNSXCGNHLRXG'
      )

    # Example of sending a transfer using the adapter.
    bundle = api.send_transfer(
      depth = 1, #100
        transfers = [
          ProposedTransaction(
            # Recipient of the transfer.
            address =
              Address(b'XXCPQKGFDFRLFXVUSZJTUKFPTJZKWKZHMZITQMCAEDOVUJYLXIYJGHEOLSDIGYDTUHUKVSC9YZZZDDOSC'),

            # Amount of IOTA to transfer.
            # This value may be zero.
            value = 0,

            # Optional tag to attach to the transfer.
            tag = Tag(b'9999999999999999'),

            # Optional message to include with the transfer.
            message = TryteString.from_string('Test: Hi!'),
          ),
        ],
    )
  except:
    print("failed")

  done = time.time()
  diffrence = done - start
  print(done - start)
  cell = 'G' + str(i+2)
  sheet.update_acell(cell, diffrence)

  time.sleep(4)