#!/usr/bin/python

import subprocess
import argparse
import os

def check(f, prefix, suffix):
	if prefix==None and suffix==None:
		return true, f
	elif prefix==None:
		return f.endswith(suffix), f.rsplit(suffix,1)[0]
	elif suffix==None:
		return f.startswith(prefix),  f.split(prefix,1)[1]
	else:
		return f.startswith(prefix) and f.endswith(suffix), f.split(prefix,1)[1].rsplit(suffix,1)[0]

def main():
	parser = argparse.ArgumentParser(description='Plot Curie temperature against some quantity')
	parser.add_argument('-p','--prefix', help='Input folder names given as prefix and suffix (e.g. -p N -s x0.01 for folders names N<something>x0.01 )')
	parser.add_argument('-s','--suffix', help='Input folder names given as prefix and suffix (e.g. -p N -s x0.01 for folders names N<something>x0.01 )')
	parser.add_argument('-t','--topfolder', default=".", help='optional top folder')
	parser.add_argument('-o', '--output', default='tc.dat', help='output file')
	args = parser.parse_args()

	
	prefix=args.prefix
	suffix=args.suffix
	# get folder names
	allItems=os.listdir(args.topfolder)
	folders=[]
	for f in allItems:
		#print f, prefix, suffix
		# find index of left match
		match,value= check(f,prefix,suffix)
		if match:
			folders.append((f,value))
			#print f, value

	tcdata=[]
	for f,v in folders:
		tcfile="%s/%s/tc.dat" % (args.topfolder, f)
		if os.path.exists(tcfile): 
			f=open(tcfile)
			lines=f.readlines()
			for l in lines:
				if not l.startswith('#'):
					tc=float(l)
			tcdata.append((float(v), tc))

	tcdata.sort()
	out=open(args.output, 'w')
	for v,tc in tcdata:
		print "%f\t%f" % (v, tc)
		out.write("%.17e\t%.17e\n" % (v, tc))	
	out.close()
if __name__=="__main__":
	main()
