from iota import Iota

def genAddrFromSeed(seed, num):
	api = Iota('http://localhost:14265', seed)
	gna_result = api.get_new_addresses(count=num) # generates 1 address, starting with index 0
	result = gna_result['addresses']
	return(result)