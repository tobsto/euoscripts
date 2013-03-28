#!/usr/bin/python

import subprocess
import argparse
import os
import shutil
import numpy
import scipy.optimize
import math

def getLegend(names):
	cut_left=''
	cut_right=''
	I_left_max=len(names[0])
	I_right_min=0
	for p in names[1:]:
		I_left=0
		I_right=len(names[0])
		# find index of left match
		for i in range(0,len(names[0])):
			if p.startswith(names[0][:i]):
				I_left=i
		# find index of right match
		for i in range(len(names[0]),0,-1):
			if p.endswith(names[0][i:]):
				I_right=i+1
		# reset max/min indices
		if I_left<I_left_max:
			I_left_max=I_left
		if I_right>I_right_min:
			I_right_min=I_right
	cut_left=names[0][:I_left_max]
	cut_right=names[0][I_right_min:]
	title="%s LEGEND %s" % (cut_left, cut_right)
	legend=[]
	for p in names:
		legend.append(p[I_left_max:I_right_min])
	return title, legend


def main():
	parser = argparse.ArgumentParser(description='Plot and manipulate 2d data')
	parser.add_argument('input', nargs='+', help='Files containing xy-data')
	parser.add_argument('-i', '--integrate', action="store_true" , help='integrate data')
	parser.add_argument('-n', '--normalize', action="store_true" , help='normalize data')
	parser.add_argument('--dots', action="store_true", help='plot with dots')
	parser.add_argument('--symbols', action="store_true", help='plot with diffent symbols')
	parser.add_argument('--nolines', action="store_true", help='plot without lines')
	parser.add_argument('--logscale', action="store_true", help='plot y-axis with logscale')
	parser.add_argument('--normalizeby', help='normalize data to specific value', type=float)
	parser.add_argument('--rkkyfit', action="store_true" , help='fit rkky coupling function of a free band do data')
	args = parser.parse_args()
	
	# manipulate data
	data=[]
	for i in args.input:
		data.append(numpy.loadtxt(i))
	
	fitdata=[]
	fitpara=[]
	for i in range(0,len(data)):
		if args.integrate:
			data[i][:,1]=(numpy.cumsum(data[i][:,1], axis=0))
		# normalize to the last value
		if args.normalize and args.integrate:
			data[i][:,1]=data[i][:,1]/data[i][-1,1]
		# normalize to the first value
		elif args.normalize and not args.integrate:
			data[i][:,1]=data[i][:,1]/data[i][0,1]
		# normalize to given value
		elif args.normalizeby!=None:
			data[i][:,1]=data[i][:,1]/args.normalizeby
		# fit 
		if args.rkkyfit:
			def func(x, k, j):
				return j*(numpy.sin(2*k*x)-2*k*x*numpy.cos(2*k*x))/numpy.power(2*k*x, 4)
			popt,pcov=scipy.optimize.curve_fit(func, data[i][:,0],  data[i][:,1])
			xdata=numpy.linspace(data[i][0,0],data[i][-1,0],1000)
			fd=func(xdata, popt[0], popt[1])
			fitdata.append(numpy.dstack((xdata,fd))[0])
			fitpara.append((popt[0], popt[1]))
			
	# save data
	output="temp_plt"
	if not os.path.exists(output):
		os.mkdir(output)
	for i in range(0,len(data)):
		numpy.savetxt(output + "/temp%i.dat" %i, data[i])
	for i in range(len(data),len(data)+len(fitdata)):
		numpy.savetxt(output + "/temp%i.dat" %i, fitdata[i-len(data)])

	# write plot config file
	title, legend=getLegend(args.input)
	f=open(output+"/temp.par",'w')
	f.write("title \"%s\"\n" % title)
	if args.logscale:
		f.write("yaxes scale Logarithmic\n")
		f.write("autoscale\n")
	for i in range(0,len(data)+len(fitdata)):
		if i<len(data):
			f.write("s%i legend \"%s\"\n" % (i, legend[i] ))
			f.write("s%i line color %i\n" % (i,i+1))
			if args.nolines:
				f.write("s%i linestyle 0\n" % i)
			if args.dots:
				f.write("s%i symbol 1\n" % i)
				f.write("s%i symbol size %f\n" % (i, (5*i)%100/100.0+0.3) )
			elif args.symbols:
				f.write("s%i symbol %i\n" % (i,(i)%10+1))
		else:
			f.write("s%i legend \"Fit with k\sF\N=%f\"\n" % (i, fitpara[i-len(data)][0] ))
			f.write("s%i linestyle 3\n" % i)
			f.write("s%i line color %i\n" % (i,i-len(data)+1))
	f.close()

	# plot data
	p=subprocess.Popen('xmgrace -free -geometry 600 -para %s/temp.par %s/*.dat' % (output,output), shell=True)
	p.communicate()
	
	# remove data
	shutil.rmtree(output, ignore_errors=True)
	
if __name__=="__main__":
	main()
