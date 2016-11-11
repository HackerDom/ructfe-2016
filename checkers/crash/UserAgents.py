import random

UserAgents = None

def get():
	global UserAgents
	if UserAgents is None:
		with open('user-agents') as fin:
			UserAgents = [line.strip() for line in fin]
	return random.choice(UserAgents)