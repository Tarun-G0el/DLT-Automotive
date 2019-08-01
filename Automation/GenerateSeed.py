import string
import random

def generateSeed():
	SEED = ""

	for i in range (81):
		SEED = SEED + random.choice(string.ascii_uppercase)

	return(SEED)