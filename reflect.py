#!/usr/bin/python

import subprocess
from sys import argv, stderr
from shutil import copy
import os

def reflectData (filename):
	# read in data
	f = open(filename, 'r')
	lines=f.readlines()
	f.close()
	data=[]
	for l in lines:
		data.append(l.split()[1])

	# mirror data
	for i in range(1,len(data)):
		data.insert(0, data[2*i-1])

	filename_reflect='reflect_' + filename 
	f = open(filename_reflect, 'w')
	for i in range(0,len(data)):
		f.write("%i\t%s\n" % (i+1, data[i]))
	f.close()	

def reflectFiles (folder, name, N):
	files=[]
	files_reflect=[]
	# mirror data
	for i in range(0,N):
		files.append("%s/%s_%03i.dat" % (folder, name, i) )
	for i in range(0,2*N-1):
		files_reflect.append("%s/reflect_%s_%03i.dat" % (folder, name, i)) 
	for i in range(0,N):
		print i, "to", i+N-1
		copy(files[i],files_reflect[i+N-1])
	for i in range(1,N):
		print i, "to", N-1-i
		copy(files[i], files_reflect[N-1-i])

def main():
	if (len(argv))<1+1:
		stderr.write( """not enought arguments. call with
		1.) Data files to reflect
		
		or
	
		1.) '-f'
		2.) folder name 
		3.) data name 
		4.) Number of layers\n""")
		exit(1)

	if argv[1]=="-f" and len(argv)<1+4:
		stderr.write( """not enought arguments. call with
		1.) '-f'
		2.) folder name 
		3.) data name 
		4.) Number of layers\n""")
		exit(1)

	if argv[1]!="-f":
		for i in range(1,len(argv)):
			reflectData(argv[i])
	else:
		folder=argv[2]
		name=argv[3]
		N=int(argv[4])
		reflectFiles(folder, name, N)
	
if __name__=="__main__":
	main()
