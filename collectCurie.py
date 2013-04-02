#!/usr/bin/python

import subprocess
import argparse
import os
import shutil
import numpy
import scipy.optimize
import math

def main():
	parser = argparse.ArgumentParser(description='Collect Curie temperatures')
	parser.add_argument('input', nargs='+', help='Tc files')
	parser.add_argument('-o', '--output', default="tcs.dat", help='Output file')
	parser.add_argument('-x', '--xvalues', nargs='*', help='x-axis values', type=float)
	args = parser.parse_args()
	
	if args.xvalues==None:
		print "No x-values given. Print Tc files"
		for tcfile in args.input:
			print tcfile
		exit(0)

	if len(args.xvalues)!=len(args.input):
		print "Number of input files and x-values does not match. Break." 
		exit(0)

	of=open(args.output, 'w')
	for tcfile,x in zip(args.input, args.xvalues):
		f=open(tcfile, 'r')
		tc=float(f.readlines()[-1])
		f.close()
		of.write("%0.17e\t%0.17e\n" % (x, tc))
	of.close()
	
if __name__=="__main__":
	main()
