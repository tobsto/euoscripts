#!/usr/bin/python

import itertools as it
import subprocess
import sys
import os
import job
import pararun
import database
import argparse
import system_parameter

def main():
	# read in config file containing
	# basic command: basecmd
	# output cmdline key and name: output
	# number of processes: np
	# parameter list: para_list
	# log name: log
	parser = argparse.ArgumentParser(description='Run euo programm')
	parser.add_argument('config', help='config file')
  	parser.add_argument('--dry', action='store_true', help='Simulate runs')
	args = parser.parse_args()
	sys.path.append(os.getcwd())
	cfg_name=args.config.partition('.')[0]
	exec('import %s as %s' % (cfg_name, 'cfg')) in globals(), locals()

	# set mpicmd according to host
	host=database.get_host()
	mpicmd = ''
	if host=='agem.th.physik.uni-bonn.de' or host=='bgem.th.physik.uni-bonn.de':
		mpicmd='mpirun -np %d' % cfg.np
	elif host=='login':
		mpicmd='mpirun.openmpi --mca btl ^udapl,openib --mca btl_tcp_if_include eth0 -x LD_LIBRARY_PATH --hostfile /users/stollenw/hostfile -np %d' % cfg.np
	else:
		mpicmd='mpirun --hostfile /users/stollenw/runs/hostfile -np %d' % cfg.np
	
	runcmd="%s %s" % (mpicmd, cfg.basecmd)

	# add keys to input and output option
	output=('-o', cfg.output, '/')
	initial_input=None
	if cfg.initial_input!=None:
		initial_input=('-i', cfg.initial_input)

	#add input function
	modpara= (cfg.inputFlag, cfg.special_input)
	def modfunc(cmd, inputFlag, special_input):
		#print cmd, host, inputFlag, special_input, isoFlag
		if inputFlag:
			if special_input==None:
				cmd=database.add_input(cmd,"temperature")
			else:
				cmd=database.add_input(cmd,"temperature",path=special_input)
		return cmd

	#add isodelta function
	prerunpara= (cfg.isoFlag,)
	def prerun_necessary_func(cmd, isoFlag):
		if isoFlag:
			return database.isodeltas_exist(cmd)
		else
			return False
	def prerun_cmd_func(cmd, isoFlag):
		if isoFlag:
			return database.get_isodeltas(cmd)
		else
			return cmd
	def prerun_add_func(cmd, isoFlag):
		if isoFlag:
			return database.add_isodeltas(cmd)
		else
			return cmd

	p=pararun.pararun(runcmd, cfg.para_list, output, runfunc=pararun.run_submit, modfunc=modfunc, modpara=modpara, input=initial_input, log=cfg.log, email='stollenwerk@th.physik.uni-bonn.de')
	if args.dry:
		p=pararun.pararun(runcmd, cfg.para_list, output, runfunc=pararun.run_print, modfunc=modfunc, modpara=modpara, input=initial_input, log=cfg.log, email='stollenwerk@th.physik.uni-bonn.de')
	p.run()

if __name__=="__main__":
	main()
