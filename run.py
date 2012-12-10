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
	parser = argparse.ArgumentParser(description='Run euo programm')
	parser.add_argument('config', help='config file')
  	parser.add_argument('--dry', action='store_true', help='Simulate runs')
	args = parser.parse_args()
	sys.path.append(os.getcwd())
	cfg_name=args.config.partition('.')[0]
	exec('import %s as %s' % (cfg_name, 'cfg')) in globals(), locals()

	# set mpicmd according to host
	host=euo.get_host()
	mpicmd = ''
	if host=='agem.th.physik.uni.bonn.de' or host=='bgem.th.physik.uni-bonn.de':
		mpicmd='mpirun -np %d' % cfg.np
	elif host=='login':
		mpicmd='mpirun.openmpi --mca btl ^udapl,openib --mca btl_tcp_if_include eth0 -x LD_LIBRARY_PATH --hostfile /users/stollenw/hostfile -np %d' % cfg.np
	else:
		mpicmd='mpirun --hostfile /users/stollenw/runs/hostfile -np %d' % cfg.np
	
	runcmd="%s %s" % (mpicmd, cfg.basecmd)

	#add input and isodeltas
	modpara= (host, cfg.inputFlag, cfg.special_input, cfg.isoFlag)
	def modfunc(cmd, host, inputFlag, special_input, isoFlag):
		rc=euo.runcmd(cmd)
		if inputFlag:
			if special_input==None:
				rc.add_input()
			else:
				rc.add_input(special_input)
		elif special_input!=None:
			rc.add_input(special_input)
		if isoFlag:
			rc.add_isodeltas()
		cmd=rc.cmd
		#if (host=='login'):
		#	cmd += "; runsync.py %s.py" % cfg_name
			
		return cmd
		

	p=pararun.pararun(runcmd, cfg.para_list, cfg.output, runfunc=pararun.run_submit, modfunc=modfunc, modpara=modpara, input=cfg.initial_input, log=cfg.log, email='stollenwerk@th.physik.uni-bonn.de')
	if args.dry:
		p=pararun.pararun(runcmd, cfg.para_list, cfg.output, runfunc=pararun.run_print, modfunc=modfunc, modpara=modpara, input=cfg.initial_input, log=cfg.log, email='stollenwerk@th.physik.uni-bonn.de')
	p.run()

if __name__=="__main__":
	main()
