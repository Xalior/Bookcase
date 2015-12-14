#!/usr/bin/env python
import serial
import time

class TTYRelay(usbtty):
	# open the first USB TTY 
	fd=serial.Serial("/dev/ttyUSB0",9600)

	# wait for the stupid serial adapter to wake up...
	time.sleep(1)
	# pretend to be Windows...
	fd.write('\x50')
	# wait for modechange
	time.sleep(0.5)
	# tell it you're switching to commandmode
	fd.write('\x51')

	def bounce():
		# from here on in we are bitmashing, each significant digit is the next relay! :)
		# e.g.
		# turn them all off 
		fd.write('\x00')
		time.sleep(1)
		# turn _only_ #1 on
		fd.write('\x01')
		time.sleep(1)
		# turn _only_ #2 on
		fd.write('\x02')
		time.sleep(1)
		# turn _only_ #4 on
		fd.write('\x04')
		time.sleep(1)
		# turn _only_ #8 on
		fd.write('\x08')
		time.sleep(1)
		# turn them all on
		fd.write('\xff')
		time.sleep(1)
		# turn them all off again
		fd.write('\x00')
 
