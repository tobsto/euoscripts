#!/usr/bin/python

import itertools as it
import subprocess
import sys
import job
import pararun
import euo
import argparse

def modfunc_iso(cmd):
	rc=euo.runcmd(cmd)
	rc.add_isodeltas()
	return rc.cmd

def modfunc_input_iso(cmd):
	rc=euo.runcmd(cmd)
	rc.add_isodeltas()
	rc.add_input()
	return rc.cmd
def modfunc_input(cmd):
	rc=euo.runcmd(cmd)
	rc.add_input()
	return rc.cmd
def modfunc_pass(cmd):
	return cmd
	

def main():
	# read in config file containing
	# basic command: basecmd
	# output cmdline key and name: output
	# number of processes: np
	# parameter list: para_list
	# log name: log
	parser = argparse.ArgumentParser(description='Run euo programm')
	parser.add_argument('config', help='config file')
	args = parser.parse_args()
	cfg_name=args.config.split('.')[0]
	exec('import %s as %s' % (cfg_name, 'cfg'))

	# set mpicmd accoring to host
	host=euo.get_host()
	mpicmd = ''
	if host=='stgeorgenamreith':
		mpicmd='mpirun -np %d' % cfg.np
	elif host=='agem.th.physik.uni-bonn.de' or host=='bgem.th.physik.uni-bonn.de':
		mpicmd='mpirun -np %d' % cfg.np
	elif host=='login':
		mpicmd='"mpirun.openmpi --mca btl ^udapl,openib --mca btl_tcp_if_include eth0 -x LD_LIBRARY_PATH --hostfile /users/stollenw/hostfile -np %d' % cfg.np
	else:
		mpicmd='"mpirun.openmpi --hostfile /users/stollenw/hostfile -np %d' % cfg.np
	
	runcmd="%s %s" % (mpicmd, cfg.basecmd)

	#add input and isodeltas
	modfunc=modfunc_pass
	if cfg.inputFlag and cfg.isoFlag:
		modfunc=modfunc_input_iso
	elif cfg.inputFlag:
		modfunc=modfunc_input
	elif cfg.isoFlag:
		modfunc=modfunc_iso

	p=pararun.pararun(runcmd, cfg.para_list, cfg.output, runfunc=pararun.run_submit, modfunc=modfunc, log=cfg.log, email='stollenwerk@th.physik.uni-bonn.de')
	p.run()

if __name__=="__main__":
	main()
