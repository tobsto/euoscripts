#!/usr/bin/python

import subprocess
import argparse
import os
import numpy

def main():
	parser = argparse.ArgumentParser(description='Plot 3d matrix data')
	parser.add_argument('input', help='File containing 3d data as matrix')
	parser.add_argument('-o', '--output', default=None, help='Output file')
	parser.add_argument('-c', '--column', default=None, help='Column for 2d plot', type=int)
	parser.add_argument('-r', '--row', default=None, help='Row for 2d plot', type=int)
	parser.add_argument('-l', '--logscale', action="store_true" , help='plot z axis with logscale')
	parser.add_argument('-q', '--quiet', action="store_true" , help='no screen output')
	parser.add_argument('-p', '--config', default=None, help='gnuplot config file')
	args = parser.parse_args()
	
	if args.column==None and args.row==None:
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
	else:
		data = numpy.loadtxt(args.input)
		f=open("temp.dat", 'w')
		if args.column!=None:
			subdata=data[:,args.column]
			for x,y in zip(numpy.arange(0,len(subdata)), subdata):
				print x,y
				f.write("%i\t%e\n" % (x,y))
		else:
			subdata=data[args.row,:]
			for x,y in zip(numpy.arange(0,len(subdata)), subdata):
				print x,y
				f.write("%i\t%e\n" % (x,y))
		f.close()
		if args.output!=None:
			os.copy("temp.dat", args.output)
		cmd = 'xmgrace temp.dat'
		subprocess.call(cmd, shell=True)
		os.remove("temp.dat")
if __name__=="__main__":
	main()
