#!/usr/bin/python

import subprocess
from sys import argv, stderr
from shutil import copy
import os

def getTotMag (sfilename, cfilename, avcfilename):
	# read in data
	f = open(sfilename, 'r')
	lines=f.readlines()
	f.close()
	spin=[]
	for l in lines:
		spin.append(float(l.split()[1]))
	f = open(cfilename, 'r')
	lines=f.readlines()
	f.close()
	cmag=[]
	for l in lines:
		cmag.append(float(l.split()[1]))
	
	f = open(avcfilename, 'r')
	line=f.readline()
	f.close()
	T=float(line.split()[0])

	# sum data
	filename_totMag='totalMag.dat'
	filename_avTotMag='avTotalMag.dat'
	f = open(filename_totMag, 'w')
	avTotMag=0.0
	for i in range(0,len(spin)):
		f.write("%i\t%s\n" % (i, 2*(spin[i]+cmag[i])))
		avTotMag=avTotMag+2*(spin[i]+cmag[i])
	avTotMag=avTotMag/float(len(spin)+1)
	f.close()	

	f = open(filename_avTotMag, 'w')
	f.write("%f\t%s\n" % (T, avTotMag))
	f.close()	

def main():
	if (len(argv))!=1+3:
		stderr.write( """not enought arguments. call with
		1.) Spin file 
		2.) C-Mag file)
		3.) Average C-Mag file\n""")
		exit(1)
	sfilename=argv[1]
	cfilename=argv[2]
	avcfilename=argv[3]

	getTotMag(sfilename, cfilename, avcfilename)
	
if __name__=="__main__":
	main()
