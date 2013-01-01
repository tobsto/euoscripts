#!/usr/bin/python

import subprocess
import sys
import os
import argparse
import time

def main():
	parser = argparse.ArgumentParser(description='Run programm after a particular process is finished')
	parser.add_argument('runcmd', nargs='+', help='run command')
  	parser.add_argument('-p', '--pid', help='pid of the process to wait for')
  	parser.add_argument('-i', '--intervall', default=10, help='check intervall in seconds', type=float)
	args = parser.parse_args()

	if args.pid==None:
		parser.print_help()
		exit(1)
	while (os.path.exists("/proc/%s" % args.pid)):
		time.sleep(args.intervall)

	cmd=''
	for a in args.runcmd:
		cmd+="%s " % a
	print cmd
	subprocess.call(cmd, shell=True)

if __name__=="__main__":
	main()
