#!/usr/bin/python

import subprocess
import sys
import os
import argparse
import euorun

def main():
	parser = argparse.ArgumentParser(description='Run euo programm')
	parser.add_argument('config', help='config file')
	args = parser.parse_args()
	sys.path.append(os.getcwd())
	cfg_name=args.config.partition('.')[0]
	exec('import %s as %s' % (cfg_name, 'cfg')) in globals(), locals()

	erun=euorun.euorun(cfg.np, cfg.system, cfg.N, cfg.M, cfg.ni, cfg.ncr, cfg.dW, cfg.output, cfg.input, cfg.initial_input, cfg.iteration_parameter, cfg.get_default_iteration_parameter, cfg.log, cfg.verbose)
	erun.tempsweep(cfg.temperatures)

if __name__=="__main__":
	main()
