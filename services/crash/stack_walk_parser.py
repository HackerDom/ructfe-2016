import sys
import os

class StackWalkParser:

	def __init__(self):
		self.crash_reason = ''
		self.crash_address = ''
		self.crash_thread = 0
		self.crash_thread_stack = []
		self.signature = ''
		return

	def parse(self, file_name):
		try:
			f = open(file_name, 'r')
			self.raw_lines = f.readlines()
			f.close()
		except:
			log.error("can't read '%s'", file_name)
			return False

		for line in self.raw_lines:
			fields = line.strip().split("|")

			type = fields[0]

			if type == "Crash":
				self.crash_reason = fields[1]
				self.crash_address = fields[2]
				self.crash_thread = int(fields[3])

			elif type.isdigit():
				thread_id = int(type)
				if thread_id == self.crash_thread:
					frame = {
						'idx': int(fields[1]) if fields[1].isdigit() else 0,
						'module': fields[2],
						'signature': fields[3],
						'source': fields[4],
						'line': int(fields[5]) if fields[5].isdigit() else 0
					}
					self.crash_thread_stack.append( frame )
					self.signature = fields[3]

		return True
