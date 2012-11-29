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
	# get name of working directory
	cwd=os.getcwd().split('/')[-1]
	print cwd
	# get name of output directory
	cmd='rsync -avzt stollenw@debcluster:/users/stollenw/runs/%s/ deb/' % (cwd)
	print cmd
	subprocess.call(cmd, shell=True)

if __name__=="__main__":
	main()
