#!/usr/bin/python

import subprocess
import sys
import os
import argparse
import euorun
import shutil

def main():
	parser = argparse.ArgumentParser(description='Run euo programm')
	parser.add_argument('config', help='config file')
	args = parser.parse_args()
	# add current working directory to system path
	sys.path.append(os.getcwd())
	# copy config file to temporary file to avoid syntax problems
	cfg_file_name="config_temp.py"
	cfg_name=cfg_file_name.rsplit('.py',1)[0]
	shutil.copyfile(args.config, cfg_file_name)

	# default values
	M=None
	N=1
	np=1
	ncr=None
	dW=None
	output=None
	input=None
	inputFlag=True
	isoDeltaFlag=True
	updatedbFlag=True
	initial_input=None
	iteration_parameter=''
	get_default_iteration_parameter=None
	check_database=False
	log='run'
	verbose=True
	temperatures=None
	findtc=False
	tsteps=None
	deltaM=None

	# import parameter from file
	##exec('from %s import *' % cfg_name) in globals(), locals()
	exec('from %s import *' % cfg_name)
	os.remove(cfg_file_name)
	os.remove(cfg_file_name + "c")
	#l=[np, system, N, M, ni, ncr, dW, output, input, initial_input, inputFlag, isoDeltaFlag, updatedbFlag, iteration_parameter, get_default_iteration_parameter, check_database, log, verbose, findtc, tsteps, deltaM] 
	#for x in l:
	#	print x

	# init euorun class
	erun=euorun.euorun(np, system, N, M, ni, ncr, dW, output, input, initial_input, inputFlag, isoDeltaFlag, updatedbFlag, iteration_parameter, get_default_iteration_parameter, check_database, log, verbose)

	# run 
	if findtc==True:
		#print "findTc"
		erun.findtc(temperatures,tsteps,deltaM)
	else:
		#print "sweep"
		erun.tempsweep(temperatures)


if __name__=="__main__":
	main()
