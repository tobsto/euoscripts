#!/usr/bin/python

import subprocess
import argparse
import os

def main():
	parser = argparse.ArgumentParser(description='Update database for energy shifts in EuO and substrate')
	parser.add_argument('input', help='File containing 3d data as matrix')
	parser.add_argument('-o', '--output', default=None, help='Output file')
	parser.add_argument('-l', '--logscale', action="store_true" , help='plot z axis with logscale')
	parser.add_argument('-q', '--quiet', action="store_true" , help='no screen output')
	parser.add_argument('-c', '--config', default=None, help='gnuplot config file')
	args = parser.parse_args()
	
	f=open("temp.plt", 'w')
	f.write("set pm3d\n")
	f.write("unset surface\n")
	if args.logscale:
		f.write("set logscale z\n")
	if not args.quiet:
		f.write("splot '%s' matrix\n" % args.input)
		f.write("pause -1\n")
	if args.output!=None:
		f.write("set terminal postscript enhanced color\n")
		f.write("set output '%s'\n" % args.output)
		f.write("splot '%s' matrix\n" % args.input)
	f.close();
	cmd = 'gnuplot temp.plt'
	subprocess.call(cmd, shell=True)
	if args.config==None:
		os.remove("temp.plt")
	else:
		cmd = 'mv temp.plt %s' % args.config
		subprocess.call(cmd, shell=True)
	
if __name__=="__main__":
	main()
