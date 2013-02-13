#!/usr/bin/python

import subprocess
import argparse

def main():
	parser = argparse.ArgumentParser(description='Make plotscript')
	parser.add_argument('-n', '--name', help='Name')
	parser.add_argument('-i', '--input', nargs='+', help='Input Paths')
	parser.add_argument('--dots', action="store_true", help='plot with dots')
	parser.add_argument('--logscale', action="store_true", help='plot y-axis with logscale')
	args = parser.parse_args()
	if args.name==None or args.input==None:
		parser.print_help()
		exit(1)
	
	output="plot_" + args.name + ".sh"
	f=open(output,'w')
	f.write("#!/bin/bash\n")
	mkpar="xmpar.py"
	if args.dots:
		mkpar=mkpar + " --dots"
	if args.logscale:
		mkpar=mkpar + " --logscale"

	for inp in args.input:
		mkpar=mkpar + " %s" % inp 
	mkpar=mkpar +" -o %s.par " % args.name

	f.write("%s\n" % mkpar)

	plotcmd="xmgrace " 
	for inp in args.input:
		plotcmd=plotcmd + " %s" % inp
	plotcmd=plotcmd + " -para %s.par &" % args.name
	f.write("%s\n" % plotcmd)
	f.close()
	
if __name__=="__main__":
	main()
