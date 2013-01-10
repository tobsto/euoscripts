#!/usr/bin/python

import subprocess
import argparse

def main():
	parser = argparse.ArgumentParser(description='Update database for energy shifts in EuO and substrate')
	parser.add_argument('input', nargs='+', help='Files containing x-y data in columns')
	parser.add_argument('-o', '--output', default='par.par', help='Output parameter file')
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
				I_right=i
	cut_left=paths[0][:I_left]
	cut_right=paths[0][I_right:]

	f=open(args.output,'w')
	f.write("title \"%s LEGEND %s\"\n" % (cut_left, cut_right))
	i=0
	for p in paths:
		f.write("s%i legend \"%s\"\n" % (i, p[I_left:I_right]))
		i=i+1
	f.close()
	
if __name__=="__main__":
	main()
