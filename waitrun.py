#!/usr/bin/python

import itertools as it
import subprocess
import sys
import os
import job
import pararun
import euo
import argparse
import time

def main():
	parser = argparse.ArgumentParser(description='Run euo programm after a particular process is finished')
	parser.add_argument('config', help='config file')
  	parser.add_argument('-p', '--pid', help='pid of the process to wait for')
  	parser.add_argument('-i', '--intervall', default=10, help='check intervall in seconds', type=float)
	args = parser.parse_args()

	if args.pid==None:
		print "Give process id. Break"
		exit(1)
	while (os.path.exists("/proc/%s" % args.pid)):
		time.sleep(args.intervall)

	runcmd = "run.py %s" % args.config
	#print runcmd
	subprocess.call(runcmd, shell=True)

if __name__=="__main__":
	main()
