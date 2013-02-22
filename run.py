#!/usr/bin/python

import subprocess
import sys
import os
import argparse
import euorun
import shutil

def main():

	usage="""Config file can (must) contain:"

	Necessary Parameter:
	
	system			:	System name (e.g. Bulk-EuGdO)
	ni			:	Charge carrier concentation in inner layers

	Parameter (=Default values):
	
	np=1			:	Number of processes for MPI
	M=None 			:	Number of outer material layer
	N=1			:	Number of inner material layer
	ncr=None		:	Charge carrier concentation in outer layers
	dW=None			:	Work function difference

	temperatures=None	:	Tuple which contains the temperatures
	findtc=False		:	Find Tc automatically, Start with 'temperatures'
	tsteps=None		:	List with decreasing time steps for findtc routine
	deltaM=None		:	Magnetisation tolerance for findtc routine

	output=None		:	Alternative output folder
	input=None		:	Alternative input folder
	initial_input=None	:	Alternative initial input
	inputFlag=True		:	Search for suitable input
	check_database=False	:	Check database for suitable input
	source=None		:	Source for suitable input ('local', 'remote' or None(both))
	isoDeltaFlag=True	:	Add isolated energy shifts in heterostr. case
	updatedbFlag=True	:	Update database after successful run
	iteration_parameter=''	:	Additional/Alternative iteration parameter
	get_iterpara=None	:	Function which determines default iter. param.
	log='run'		:	Name of the log files
	verbose=True		:	Send email after every successful run
	
	"""
	
	parser = argparse.ArgumentParser(description='Run euo programm', formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument('config', help=usage)
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
	get_iterpara=None
	check_database=False
	source=None
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
	#l=[np, system, N, M, ni, ncr, dW, output, input, initial_input, inputFlag, isoDeltaFlag, updatedbFlag, iteration_parameter, get_iterpara, check_database, source, log, verbose, findtc, tsteps, deltaM] 
	#for x in l:
	#	print x

	# init euorun class
	erun=euorun.euorun(np, system, N, M, ni, ncr, dW, output, input, initial_input, inputFlag, isoDeltaFlag, updatedbFlag, iteration_parameter, get_iterpara, check_database, source, log, verbose)

	# run 
	if findtc==True:
		#print "findTc"
		erun.findtc(temperatures,tsteps,deltaM)
	else:
		#print "sweep"
		erun.tempsweep(temperatures)


if __name__=="__main__":
	main()
