#!/usr/bin/python
import itertools
import argparse
import os
import subprocess
import glob
import random

def isResults (resultsFolder):
	iterFolder="%s/iterOutput" % resultsFolder
	if os.path.exists(iterFolder):
		return True
	else:
		return False


def getRandTrash(trashFolder):
	for i in range(0, 1000):
		# random hash
		h = "%032x" % random.getrandbits(128)
		name="%s/%s" % (trashFolder, h)
		if not os.path.exists(name):
			os.mkdir(name)
			return name
	print "unable to create folder with random name in trash folder. break."
	exit(1)
			
parser = argparse.ArgumentParser(description='Clean up result folder from EuO runs')
parser.add_argument('input', nargs='+', help='folder containing results or containing subfolders with results')
parser.add_argument('-o', '--output', default="/users/stollenw/trash", help='trash folder')
args = parser.parse_args()

if not os.path.exists(args.output):
	os.mkdir(args.output)

# use time as random seed
random.seed()

resultFolders=[]
for i in args.input:
	if isResults(i):
		print i
		resultFolders.append(i)
	for isub in glob.glob("%s/*" % i):
		if isResults(isub):
			print isub
			resultFolders.append(isub)

patterns=('ac*','ad*', 'a??t.dat', 'subIter*')
for resultFolder in resultFolders:
	# multi
	for subfolder in filter(lambda x: x.startswith("layer_"), os.listdir(resultFolder + "/iterOutput/")):
		print "clean %s ..." % os.path.join(resultFolder+"/iterOutput/",subfolder)
		output=getRandTrash(args.output)
		for pattern in patterns:
			#print "%s/%s" % (os.path.join(resultFolder+"iterOutput/",subfolder), pattern)
			for f in glob.glob("%s/%s" % (os.path.join(resultFolder+"/iterOutput/",subfolder), pattern)):
				cmd = "mv %s %s/" % (f, output)
				subprocess.call(cmd, shell=True)
	# bulk
	print "clean %s ..." % (resultFolder+"/iterOutput/")
	output=getRandTrash(args.output)
	for pattern in patterns:
		#print "%s/%s" % (os.path.join(resultFolder+"iterOutput/",subfolder), pattern)
		for f in glob.glob("%s/%s" % (resultFolder+"/iterOutput/", pattern)):
			cmd = "mv %s %s/" % (f, output)
			#print cmd
			subprocess.call(cmd, shell=True)
