#!/usr/bin/python

import subprocess
import argparse

def main():
	parser = argparse.ArgumentParser(description='Update database for energy shifts in EuO and substrate')
	parser.add_argument('input', nargs='+', help='Files containing x-y data in columns')
	parser.add_argument('-o', '--output', default='par.par', help='Output parameter file')
	parser.add_argument('--dots', action="store_true", help='plot with dots')
	parser.add_argument('--logscale', action="store_true", help='plot y-axis with logscale')
	#parser.add_argument('-l', '--cut_string_left', default='', help='Prefix string that matches in all input path will be cut out')
	#parser.add_argument('-r', '--cut_string_right', default='', help='Suffix string that matches in all input path will be cut out')
	args = parser.parse_args()
	
	paths=args.input
	cut_left=''
	cut_right=''
	I_left=0
	I_right=len(paths[0])
	for p in paths[1:]:
		# find index of left match
		for i in range(0,len(paths[0])):
			if p.startswith(paths[0][:i]):
				I_left=i
		# find index of right match
		for i in range(len(paths[0]),0,-1):
			if p.endswith(paths[0][i:]):
				I_right=i+1
	cut_left=paths[0][:I_left]
	cut_right=paths[0][I_right:]

	f=open(args.output,'w')
	f.write("title \"%s LEGEND %s\"\n" % (cut_left, cut_right))
	if args.logscale:
		f.write("yaxes scale Logarithmic\n")
		f.write("autoscale\n")
	i=0
	for p in paths:
		f.write("s%i legend \"%s\"\n" % (i, p[I_left:I_right]))
		if args.dots:
			f.write("s%i symbol 1\n" % i)
			f.write("s%i symbol size %f\n" % (i, (30 + 5*i)%100/100.0) )
		i=i+1
	f.close()
	
if __name__=="__main__":
	main()
