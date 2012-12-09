#!/usr/bin/python

import jobscheduler
import subprocess
import sys
import os
import job
import pararun
import euo
import argparse

def main():
	parser = argparse.ArgumentParser(description='Submit programm to jobscheduler')
	parser.add_argument('runcmd', nargs='+', help='run command')
	parser.add_argument('-q', '--queue', default=None, help='Queue config file (Default is $HOME/.queue)')
	parser.add_argument('-t', '--timeout', default=10.0, help='Job scheduler timeout', type=float)
	parser.add_argument('-e', '--email', default='stollenwerk@th.physik.uni-bonn.de', help='Email address')
	parser.add_argument('-m', '--mailcmd', default='mailx -s', help='Mail command')
	args = parser.parse_args()

	# start jobscheduler if necessary
	js_running=True
	cmd = "ps -e | grep jobscheduler.py"
	process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        allout= process.communicate()
	if allout==('',''):
		#print "not running"
		# start jobscheduler
		cmd=''
		if args.queue!=None:
			cmd="jobscheduler.py -q %s -t %f -e %s -m '%s'" % (args.queue, args.timeout, args.email, args.mailcmd)
		else:
			cmd="jobscheduler.py -t %f -e %s -m '%s'" % (args.timeout, args.email, args.mailcmd)
		subprocess.Popen(cmd, shell=True)

	elif not len(allout[0].split('\n'))==2:
		print "Submit: Error: It seems that there are multiple instances of jobscheduler running:"
		for l in (allout[0].split('\n')):
			print l
		print "Break."
		exit(1)

	# add job to queue
	q=jobscheduler.queue(args.queue)
	runstr=''
	for r in args.runcmd:
		runstr+=r + " "
	q.add(runstr)
	#q.list()

if __name__=="__main__":
	main()
