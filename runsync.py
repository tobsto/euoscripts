#!/usr/bin/python

import itertools as it
import subprocess
import sys
import os
import job
import pararun
import euo
import argparse

def main():
	# read in config file containing
	# basic command: basecmd
	# output cmdline key and name: output
	# number of processes: np
	# parameter list: para_list
	# log name: log
	parser = argparse.ArgumentParser(description='copy results from cluster run specifies by config file to head node (only for debcluster)')
	parser.add_argument('config', help='config file')
	args = parser.parse_args()
	sys.path.append(os.getcwd())
	cfg_name=args.config.partition('.')[0]
	exec('import %s as %s' % (cfg_name, 'cfg'))

	# get 1st node, i.e. the node where the data is stored locally
	hostfile='/users/stollenw/hostfile'
	f=open(hostfile, 'r')
	host=f.readline().split()[0]
	f.close()

	# get name of working directory
	cwd=os.getcwd().split('/')[-1]
	print cwd
	# get name of output directory
	output=cfg.output[1]
	match=False
	name=''
	for n in output.split('/'):		
		if n==cwd:
			name=n
			match=True
			break
	
	if match:	
		cmd='rsync -avzt stollenw@%s:/ext/%s/* .' % (host, name)
		print cmd
		subprocess.call(cmd, shell=True)
	else:
		print "Error: Failed to finde working directory: %s in remote directory: %s. Break" % (cwd, output)

if __name__=="__main__":
	main()
