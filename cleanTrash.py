#!/usr/bin/python
import itertools
import argparse
import os
import subprocess
import glob
import random
import shutil
from datetime import datetime, time
from time import sleep

parser = argparse.ArgumentParser(description='Empty trash folder')
parser.add_argument('-t', '--time', help='trash folder')
parser.add_argument('-f', '--trash', help='trash folder')
args = parser.parse_args()

if args.trash==None:
	args.trash="%s/trash" % os.getenv("HOME")

def wait_until(runTime):
	startTime = time(*(map(int, runTime.split(':'))))
	print startTime
	# you can add here any additional variable to break loop if necessary
	while startTime > datetime.today().time():
		sleep(60)

if args.time!=None:
	wait_until(args.time)

os.chdir(args.trash)
for sub in os.listdir("."):
	print "remove %s ..." % sub
	shutil.rmtree(sub)
print "remove %s ..." % args.trash
shutil.rmtree(args.trash)
