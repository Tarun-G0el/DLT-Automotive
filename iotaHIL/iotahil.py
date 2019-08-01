from multiprocessing import Process, Manager
	# The multiprocessing module provides a way to work with shared objects if they run under the control of a so-called manager.  A manager is a separate subprocess where the
	# real objects exist and which operates as a server.  Other processes access the shared objects through the use of proxies that operate as clients of the manager server.

import socket
	# For TCP servers, the socket object used to receive connections is not the same socket used to perform subsequent communication with the client.  In particular, the accept()
	# system call returns a new socket object that's actually used for the connection.  This allows a server to manage connections from a large number of clients simultaneously.
	
import threading as thread
import time

import os, sys
import subprocess
import traci

import random
import numpy
from cvxpy import *

import iotasetup as setup
import requests

from iota import *
from iota.adapter.wrappers import RoutingWrapper

# server program
def server(flag_hello_smartphone, flag_goodbye_smartphone, smartphone_broadcast, central_authority_broadcast):
	
	# initialisation
	realVehicleIndex = 0 # track list indices corresponding to real vehicles
	
	# size of buffer and backlog
	buffer = 2048 # value should be a relatively small power of 2, e.g. 4096
	backlog = 1 # tells the operating system to keep a backlog of 1 connection; this means that you can have at most 1 client waiting while the server is handling the current client;
				# the operating system will typically allow a maximum of 5 waiting connections; to cope with this, busy servers need to generate a new thread to handle each incoming
				# connection so that it can quickly serve the queue of waiting clients

	# create a socket
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET = IPv4 socket family; SOCK_STREAM = TCP socket type

	# bind the socket to an address and port
	host = '127.0.0.1' # a string containing the hostname of the machine where the Python interpreter is currently executing
	port = 65432 # reserve a port for the service (i.e. a large number less than 2^16); the call will fail if some other application is already using this port number on the same machine
	serverSocket.bind((host, port)) # binds the socket to the hostname and port number

	# listen for incoming connections
	serverSocket.listen(backlog)
	
	def clientHandle(clientSocket, address, realVehicleIndex):
	
		while True: # infinite loop 2
			incoming = clientSocket.recv(buffer) # receive client data into buffer
			if (incoming == 'quit'):
				print ('Ending session with client.')
				clientSocket.close() # close the connection with the client
				smartphone_broadcast[realVehicleIndex] = 0.0
				central_authority_broadcast[realVehicleIndex] = 'No Advice'
				flag_goodbye_smartphone[realVehicleIndex] = True
				break # breaks out of infinite loop 2
			smartphone_broadcast[realVehicleIndex] = float(incoming)*1000/3600 # convert km/h to m/s
			clientSocket.send(central_authority_broadcast[realVehicleIndex] + '\n') # send the data to the client
			
	while True: # infinite loop 1
		clientSocket, address = serverSocket.accept() # passively accept TCP client connections; the call returns a pair of arguments:  clientSocket is a new Socket object used to communicate
													  # with the client and address is the address of the client
		# record client connection time (as seen from the server)
		start_time = time.strftime('%d %b %Y at %H:%M:%S')
		init_time = str(start_time) # convert connection time to a string
		print ('Made a connection with', address, 'on', init_time + '.')
		
		flag_hello_smartphone[0] = True
		smartphone_broadcast.append(0.0)
		central_authority_broadcast.append('No Advice')
		flag_goodbye_smartphone.append(False)
		
		# create new thread
		thread.start_new_thread(clientHandle, (clientSocket, address, realVehicleIndex))
		
		realVehicleIndex += 1

def iota_transaction(light_id):
	response = requests.post('http://127.0.0.1:8080/request_light_address', json=light_id) # request an address for the corresponding light that is arriving
	service_addr = response.json()['address']
					
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
	send_transfer_response = api.send_transfer(
	  depth = 1, #100
	    transfers = [
	      ProposedTransaction(
	        # Recipient of the transfer.
	        address =
	          Address(service_addr),

	        # Amount of IOTA to transfer.
	        # This value may be zero.
	        value = 0,

	        # Optional tag to attach to the transfer.
	        tag = Tag(b'9999999999999999'),

	        # Optional message to include with the transfer.
	        message = TryteString.from_string('transaction made'),
	      ),
	    ],
	)
	bundle = send_transfer_response['bundle']
	for i in range(len(bundle.transactions)):
		transaction = bundle.transactions[i]
		if transaction.address == service_addr: # transaction.address is the address associated with this transaction
			TRANSACTION_ID = str(transaction.hash) # the transaction hash is used to uniquely identify the transaction on the Tangle; the value is generated by taking a hash of the raw transaction trits
												   # we assume in the code here that a single transaction was made to the recipient's address; otherwise, the code must be modified so that multiple TRANSACTION_IDs are stored
			print ('{}. Transaction ID: {}'.format(i+1, TRANSACTION_ID))
		else:
			TRANSACTION_ID = 'This transaction was not intended for the client.'
			print ('{}. {}'.format(i+1, TRANSACTION_ID))
	
	response = {}
	response['transaction_id'] = TRANSACTION_ID # string
	final = requests.post('http://127.0.0.1:8080/request_transaction_read', json=response) # request an address for the corresponding light that is arriving

def iota_return(jsobj):
	response = requests.post('http://127.0.0.1:8080/return_token', json=jsobj) # request an address for the corresponding light that is arriving
	transaction_id_ret = response.json()['transaction_id']
	print('Transaction of return ID is ', transaction_id_ret)

if __name__ == '__main__':

	# constants
	endSim = 400000 # the simulation will be permitted to run for a total of endSim milliseconds
	timeout = 0.1 # a floating point number [s]
	FLAGHELLOSMARTPHONEDATA = False
	p = 1 # proportion of vehicles participating in the service; between 0 and 1, inclusive
	externalReference = 6.8 # 6.8m/s = 24.48km/h
	
	# cost function constants:  each function quantifies a vehicle's CO_2 emissions given the speed that it's travelling at
	aR007 = 2260.6 # vehicle type R007
	bR007 = 31.583 # vehicle type R007
	cR007 = 0.29263 # vehicle type R007
	dR007 = 0.0030199 # vehicle type R007
	aR014 = 2532.4 # vehicle type R014
	bR014 = 68.842 # vehicle type R014
	cR014 = -0.43167 # vehicle type R014
	dR014 = 0.0066776 # vehicle type R014
	aR021 = 3747.3 # vehicle type R021
	bR021 = 105.71 # vehicle type R021
	cR021 = -0.8527 # vehicle type R021
	dR021 = 0.012264 # vehicle type R021
	
	# cost function variable and tag initialisation
	costFunctionVariables = []
	costFunctionTags = []
	
	# initialisations
	step = 0 # time step
	ticket = 1 # used to provide unique IDs to real vehicles
	
	manager = Manager() # create a running manager server in a separate process
	flag_hello_smartphone = manager.list() # create a shared list instance on the manager server
	flag_hello_smartphone.append(FLAGHELLOSMARTPHONEDATA) # add an element to the list
	flag_goodbye_smartphone = manager.list() # create a shared list instance on the manager server
	smartphone_broadcast = manager.list() # create a shared list instance on the manager server
	central_authority_broadcast = manager.list() # create a shared list instance on the manager server
	serverThread = Process(target=server, args=(flag_hello_smartphone, flag_goodbye_smartphone, smartphone_broadcast, central_authority_broadcast)) # represents a task (i.e. the server program) running in a subprocess
	
	participants = [] # a list of vehicles participating in the service
	newSpeed = []
	controlHistory = []
	removedParticipants = []
	realVehicles = []
	transactionBools = {}
	rulesBools = {}
	rulesBools2 = {}

	print("")
	
	print ("Starting the main program.")
	print ("Connecting to SUMO via TraCI.")
	
	# import TraCI (to use the library, the <SUMO_HOME>/tools directory must be on the python load path)
	if 'SUMO_HOME' in os.environ:
		tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
		sys.path.append(tools)
	else:   
		sys.exit("Please declare environment variable 'SUMO_HOME'.")
		
	# interface with SUMO from Python:  (i) begin by starting SUMO-GUI from within the python script;...
	PORT = 8813
	sumoBinary = "/Program Files (x86)/DLR/Sumo/bin/sumo-gui"
	sumoProcess = subprocess.Popen([sumoBinary, "-c", "iota.sumocfg", "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)
		
	# ...then (ii) connect to the (waiting) simulation
	traci.init(PORT)
	
	print ("Launching the server.")
	serverThread.start()
	print ("The server has been launched.")
	
	print("")
	
	# begin the simulation
	traci.simulationStep(10100) # perform the simulation until the time in the day indicated (in milliseconds) is reached; use for time steps of 0.1s
	
	while step < endSim:
	
		print ('Time step [ms]: {}'.format(step))
		# print 'Current simulation time [ms]: {}'.format(traci.simulation.getCurrentTime())
		vehicles = traci.vehicle.getIDList() # a list of vehicles currently running in the scenario
		# print 'No. of vehicles currently running in the scenario: {}'.format(len(vehicles)) # number of vehicles currently running in the scenario
		print ('Vehicles currently running in the scenario: {}'.format(vehicles))

		departed = traci.simulation.getDepartedIDList() # a list of vehicles which departed (were inserted into the road network) in this time step
		if departed: # does departed have a value?
			transactionBools[departed[0]] = False
			rulesBools[departed[0]] = False
			rulesBools2[departed[0]] = False
			print(departed, 'was added in this time step')

		arrived = traci.simulation.getArrivedIDList() # A list of ids of vehicles which arrived (have reached their destination and are removed from the road network) in this time step
		if arrived:	# Assumes that vehicles queue, enter instance one at a time, leave instance one at a time
			veh_id = arrived[0]
			if veh_id in transactionBools: # or in rulesBools
				del transactionBools[veh_id]
				del rulesBools[veh_id]
				del rulesBools2[veh_id]
				print(arrived, 'was removed in this time step')

		for i in range(len(vehicles)):	# checks the distance of all vehicles to the lights
			nexttl = traci.vehicle.getNextTLS(vehicles[i])
			if not nexttl: # is the list empty?
				print(vehicles[i], ' has crossed the traffic light.')
				rulesBools[vehicles[i]] = True # TODO add functionality for random cars to break the rules and update accordingly
				if rulesBools[vehicles[i]] == True and rulesBools2[vehicles[i]] == False:
					rulesBools2[vehicles[i]] = True
					print(vehicles[i], ' thank you for following the rules. Token return being processed.')
					veh_addr = {}
					veh_addr['Vehicle Index'] = vehicles[i][3]
					threads = thread.Thread(target=iota_return, args=[veh_addr])
					threads.daemon = True                            # Daemonize thread
					threads.start()
			else:
				print(vehicles[i],' distance to upcoming light is: ', nexttl[0][2], 'meters')
				if nexttl[0][2] < 50 and transactionBools[vehicles[i]] == False:	# bluetooth signal tuned to accept and react to signal strength values of -30dBm equivalent to 50m with LoS
					# make transaction at corresponding light
					print(vehicles[i], ' is close now. Making IOTA Transaction now. . .')
					transactionBools[vehicles[i]] = True
					light_id = {}
					light_id['Light Node'] = nexttl[0][0]
					threads = thread.Thread(target=iota_transaction, args=[light_id])
					threads.daemon = True                            # Daemonize thread
					threads.start()
		'''
		departed = traci.simulation.getDepartedIDList() # a list of vehicles which departed (were inserted into the road network) in this time step
		# print 'Newly inserted vehicles: {}'.format(departed)
		for i in range(len(departed)):
			if 'vehPrius' in departed[i]:
				participants.append(departed[i]) # i.e. real vehicles are assumed to be always participating in the service
				newSpeed.append(-1)
				controlHistory.append(0)
				costFunctionVariables.append(Variable()) # append a scalar optimization variable
				costFunctionTags.append(random.randint(1,3))
			else:
				coin = random.uniform(0,1) # determine what vehicles are participating in the service; flip a weighted coin; returns a random floating point number r such that 0 <= r < 1
				if coin < p:
					participants.append(departed[i])
					newSpeed.append(-1)
					controlHistory.append(0)
					costFunctionVariables.append(Variable()) # append a scalar optimization variable
					costFunctionTags.append(random.randint(1,3))
		
		# arrived = traci.simulation.getArrivedIDList() # a list of vehicles which arrived (have reached their destination and are removed from the road network) in this time step
		# print 'Arrived vehicles: {}'.format(arrived)
		
		# clean the participants list
		for i in range(len(participants)):
			if participants[i] not in vehicles:
				removedParticipants.append(participants[i])
		for i in range(len(removedParticipants)):
			indexIdentifier = participants.index(removedParticipants[i])
			newSpeed.pop(indexIdentifier)
			controlHistory.pop(indexIdentifier)
			costFunctionVariables.pop(indexIdentifier)
			costFunctionTags.pop(indexIdentifier)
			participants.remove(removedParticipants[i])
		# print 'Vehicles ejected from the participants list: {}'.format(removedParticipants) # includes arrived, real and 'vanished' vehicles
		removedParticipants = []
		
		# print 'Vehicles currently running in the scenario and participating in the service: {}'.format(participants)
		
		# chose which control algorithm to apply
		# controlAlgorithmLeaderless(participants)
		# controlAlgorithmExternalReference(participants)
		# controlAlgorithmCostFunctions(participants)
		
		# check that all participating vehicles have a newSpeed registered each time step:  YEP! (DONE)
		
		# prepare the information to send to the real vehicles
		for i in range(len(participants)):
			if 'vehPrius' in participants[i]:
				indexIdentifier = realVehicles.index(participants[i])
				if newSpeed[i] == -1:
					central_authority_broadcast[indexIdentifier] = 'No Advise'
				else:
					central_authority_broadcast[indexIdentifier] = str(newSpeed[i] * 3.6) # convert m/s to km/h
		print ('Advised speeds sent to the real vehicles:', central_authority_broadcast)
		'''
		# communicate with the real vehicles
		serverThread.join(timeout) # implicitly controls the speed of the simulation; blocks the main program either until the server program terminates (if no timeout is defined) or until the timeout occurs
		
		# process the information received from the real vehicles
		if flag_hello_smartphone[0] == True:
			addRealVehicle(ticket)
			realVehicles.append('vehPrius{}'.format(ticket))
			flag_hello_smartphone[0] = False
			ticket += 1
		for i in range(len(smartphone_broadcast)):
			if 'vehPrius{}'.format(i+1) in vehicles:
				traci.vehicle.setSpeed('vehPrius{}'.format(i+1), smartphone_broadcast[i])
		for i in range(len(flag_goodbye_smartphone)):		
			if flag_goodbye_smartphone[i] == True:
				removeRealVehicle(i)
				flag_goodbye_smartphone[i] = False
		
		print("")
		
		# goto the next time step
		step += 100 # in milliseconds
		traci.simulationStep(10100+step) # perform the simulation until the time in the day indicated (in milliseconds) is reached; use for time steps of 0.1s
	
	print ("Shutting the server down.")
	serverThread.terminate()
	traci.close() # close the connection to SUMO