#!/usr/bin/python

import subprocess
import sys
import os
import argparse
import database
import system_parameter
import itertools
import findtc

def read(filename, line=0):
	f=open(filename, 'r')
	lines=f.readlines()
	f.close()
	return lines[line].split()

class xmagfile(Exception): 
    def __init__(self, n): 
        self.name = n

def extractMag(t,dbtype,db,folder):
	magfile=None
	if dbtype=='bulk':
		magfile=folder + db.get_temp_output(t) + "results/totalmag.dat"
	elif dbtype=='isolated':
		magfile=folder + db.get_temp_output(t) + "results/avmag.dat"
	else:
		magfile=folder + db.get_temp_output(t) + "results/avmag.dat"
	# read magnetisation file or download it (in the case of checkdatabase==True)
	if os.path.exists(magfile):
		return float(database.extractResultValue2ndColumn(magfile))
	else:
		raise xmagfile(magfile)
		
def dummyrun(t):
	pass

def gettc(dbtype, db, folder, temperatures=None, tsteps=None, deltaM=None):
	# default magnetisation precision
	if deltaM==None:
		deltaM=1.0E-2
	# default temperatures steps
	if temperatures==None:
		temperatures=range(20,301,20)
	# default temperatures steps
	if tsteps==None:
		# default temperature increments
		tsteps=[20,10,5,1,0.1]
	# tsteps must contain at least one entry
	if len(tsteps)<1:
		print "Error: find_tc: No temperature steps given. Break"
		exit(1)	
	# sort tsteps
	tsteps.sort()
	# reverse order (decendent)
	tsteps.reverse()

	try:
		(tc, dT, dM)=findtc.findtc(dummyrun, extractMag, (), (), (dbtype, db, folder), temperatures, tsteps, deltaM) 
	except xmagfile, x:
		print x.name, "does not exist!"	
		return False
	##############################
	# save tc
	##############################
	tcfile="%s/tc.dat" % folder
	write=True
	if os.path.exists(tcfile):
		write=False
		print "The file %s, already exists. It reads:"
		f=open(tcfile, 'r')
		for l in f.readlines():
			print l
		answer=raw_input("Overwrite? (Y/n)")
		if answer!='n':
			write=True
	if write:
		f=open(tcfile, 'w')
		f.write("# Curie temperature of %s\n" % folder.rstrip('/') )
		f.write("# Magnetisation accuracy dM=%f\n" % dM)
		f.write("# Temperature accuracy dT=%f\n" % dT)
		f.write("# Tc=%f\n" % tc)
		f.write("%0.17e\n" % tc)
		f.close()
	return True
	
def main():
	parser = argparse.ArgumentParser(description='Analyse euo program results', formatter_class=argparse.RawTextHelpFormatter)
	keyword_help="""Calculate the temperature dependent 
quantity specified by one of the following keywords

print
print full
tc

occNum_c		(for bulk)
dopant_activation	(for bulk)
totalmag		(for bulk)
cond			(for bulk)
resist			(for bulk)
	
avmag			(for isolated and heterostructures)
cond_para		(for isolated and heterostructures)
resist_para		(for isolated and heterostructures)
cond_perp		(for isolated and heterostructures)
resist_perp 		(for isolated and heterostructures)
isodelta 		(energy shift (-mu) for isolated systems)

"""

	dataset_help="""Specify dataset 
	
e.g. "Metal-Metal-Heterostructure 5 9 0.01 0.01 0.125" 
(for material, N, M, ni, ncr and dW). 

You may use "all" as a placeholder or do not specify 
the last values e.g. "all 5 all 0.01

"""

	parser.add_argument('keyword', help=keyword_help)
	parser.add_argument('-d', '--database', help='Type of database: "bulk", "isolated" or "hetero"')
	parser.add_argument('-s', '--dataset', nargs='*', help=dataset_help)
	parser.add_argument('-o', '--output', default='/home/stollenw/projects/euo/analysis/', help='Output folder (optional)')
	parser.add_argument('--dbpath', help='Path to database file (optional)')
	parser.add_argument('--resultpath', default='/home/stollenw/projects/euo/results/', help='Path to results (optional)')
	parser.add_argument('--temperatures', nargs='*', default=None, help='Tempertures for tc search (optional, only for tc)', type=float)
	parser.add_argument('--tsteps', nargs='*', default=None, help='Temperture steps for tc search (optional, only for tc)', type=float)
	parser.add_argument('--dM', default=None, help='Magnetisation resolution for tc search (optional, only for tc)', type=float)
	parser.add_argument('--layer', default=0, help='Layer to calculate parallel conductivity/resistivity in', type=int)
	parser.add_argument('--layerx', help='First layer for perpendicular conductivity/resistivity', type=int)
	parser.add_argument('--layery', help='First layer for perpendicular conductivity/resistivity', type=int)
	
	args = parser.parse_args()

	if not args.database in ('bulk', 'isolated', 'hetero'):
		parser.print_help()
		exit(0)

	# allowed keywords
	print_keywords=['print', 'printfull']
	simple_result_keywords=None
	sophisticated_result_keywords=None
	if args.database=='bulk':
		simple_result_keywords=['cond', 'resist', 'totalmag']
		sophisticated_result_keywords=['tc', 'dopant_activation', 'occNum_c']
	elif args.database=='isolated' or args.database=='hetero':
		simple_result_keywords=['avmag']
		sophisticated_result_keywords=['cond_para', 'resist_para', 'cond_perp', 'resist_perp', 'isodelta', 'tc']

	# keywords that produce results
	result_keywords=simple_result_keywords + sophisticated_result_keywords
	# all keywords (including print keywords)
	allowed_keywords=simple_result_keywords + sophisticated_result_keywords + print_keywords

	# check if valid keyword was given
	if not args.keyword in allowed_keywords:
		parser.print_help()
		print "Allowed keywords are:"
		for ak in allowed_keywords:
			print ak
		exit(0)
	
	# set output
	output=args.output
	

	db=None
	corenames=None
	special=None
	subResultFolder=None
	if args.database=='bulk':
		db=database.bulk_database()	
		output=output+'bulk/'
		subResultFolder='bulk/'
		corenames=('material', 'ni', 'T')
		special='mag'
	elif args.database=='isolated':
		db=database.isolated_database()	
		output=output+'isolated/'
		subResultFolder='isolated/'
		corenames=('material', 'N', 'ni', 'T')
		special='isodelta'
	else:
		db=database.heterostructure_database()	
		output=output+'hetero/'
		subResultFolder='heterostructure/'
		corenames=('material', 'N', 'M', 'ni', 'ncr', 'dW', 'T')
		special='avmag'

	if args.dbpath==None:
		db.download()
	else:
		db.download("stollenw@heisenberg.physik.uni-bonn.de:%s" % args.dbpath)

	resultFolder=args.resultpath

	# get filtered data, i.e. reduce to defining properties without temperature
	filtered_data=database.filtrate(db.data, corenames, args.dataset, len(corenames)-1)

	# lower threshold for displaying results
	min_result_number=1
	# extract conductivity or other observables
	if args.keyword in result_keywords:
		# temperatrue sweep only makes sense if there are at least two temperatures
		min_result_number=2
		# create folder if necessary
		suboutput=output + "/data/%s/" % args.keyword
		if not os.path.exists(suboutput):
			os.makedirs(suboutput)
		
	# in the Curie temperature case, create single file for all datasets
	outfile=''
	tcd=''
	tci=0
	if args.keyword=='tc' or args.keyword=='dopant_activation' or args.keyword=='occNum_c':
		if args.dataset==None:
			print "Dataset needed for Curie temperature / dopant activation at T=5K / occNum at T=5K"
			exit(1)
		# check if number single attribute is filterd out
		if (args.dataset.count('all')+(len(corenames)-1-len(args.dataset))>1):
			print "Dataset has to many degrees of freedom."
			exit(1)
		tcc=[]
		i=0
		for d,n in zip(args.dataset,corenames):
			if d!='all':
				if n=='material':
					tcc.append(d)
				elif n=='N' or n=='M':
					tcc.append(n + "%03i" % int(d))
				else:
					tcc.append(n + "%06.4f" % float(d))
			else:
				tcd=n
				tci=i
			i=i+1
		if (tcd==''):
			tcd=corenames[-2]
			tci=len(corenames)-2
		tcname='_'.join(tcc)
		outfile="%s/%s_%s.dat" % (suboutput, args.keyword, tcname)
		#remove file if it already exists
		f=open(outfile, 'w')
		if args.keyword=='tc': 
			f.write("# %s\tCurie temperature Tc\tAccuracy of Tc\n" % tcd)
		elif args.keyword=='dopant_activation': 
			f.write("# %s\tdopant activation (n_c/n_i)\n" % tcd)
		elif args.keyword=='occNum_c': 
			f.write("# %s\tConduction band occupation number (n_c)\n" % tcd)
		f.close()

	# iterate through database
	for fd in filtered_data:
		# defining name
		material_folder=db.get_output(*fd)
		namestr=material_folder.rstrip('/')
		# get all datasets corresponding to fd (different temperatures)
		temperature_datasets=database.filtrate(db.data, corenames, fd)
		if args.keyword in simple_result_keywords:
			# extract data from relevant folders	
			cmd='cat '
			for td in temperature_datasets:
				temperature_folder=db.get_temp_output(td[len(corenames)-1])
				#cmd=cmd + "%s/results/%s.dat " % (fd[-1], args.keyword)
				cmd=cmd + "%s/%s/%s/%s/results/%s.dat " % (resultFolder, subResultFolder, material_folder, temperature_folder, args.keyword)
			cmd=cmd + " > %s/%s_%s.dat" % (suboutput, args.keyword, namestr)
			subprocess.call(cmd, shell=True)	

		elif args.keyword in sophisticated_result_keywords:
			if args.keyword=='cond_para':
				key=args.keyword
				if (args.layer!=0):
					key="%s_layer%03i" % (args.keyword, args.layer)
				outfile="%s/%s_%s.dat" % (suboutput, key, namestr)
				f=open(outfile, 'w')
				for td in temperature_datasets:
					temperature_folder=db.get_temp_output(td[len(corenames)-1])
					filename="%s/%s/%s/%s/results/%s.dat" % (resultFolder, subResultFolder, material_folder, temperature_folder, 'cond')
					value=float(read(filename, line=args.layer)[1])
					temp=td[len(corenames)-1]
					f.write("%0.17e\t%0.17e\n" % (temp, value))
				f.close()

			if args.keyword=='resist_para':
				key=args.keyword
				if (args.layer!=0):
					key="%s_layer%03i" % (args.keyword, args.layer)
				outfile="%s/%s_%s.dat" % (suboutput, key, namestr)
				f=open(outfile, 'w')
				for td in temperature_datasets:
					temperature_folder=db.get_temp_output(td[len(corenames)-1])
					filename="%s/%s/%s/%s/results/%s.dat" % (resultFolder, subResultFolder, material_folder, temperature_folder, 'resist')
					value=float(read(filename, line=args.layer)[1])
					temp=td[len(corenames)-1]
					f.write("%0.17e\t%0.17e\n" % (temp, value))
				f.close()


			if args.keyword=='cond_perp':
				if args.layerx==None or args.layery==None:
					outfile="%s/%s_%s.dat" % (suboutput, args.keyword, namestr)
					f=open(outfile, 'w')
					for td in temperature_datasets:
						temperature_folder=db.get_temp_output(td[len(corenames)-1])
						filename="%s/%s/%s/%s/results/%s.dat" % (resultFolder, subResultFolder, material_folder, temperature_folder, 'cond_perp')
						value=float(read(filename, line=0)[0])
						temp=td[len(corenames)-1]
						f.write("%0.17e\t%0.17e\n" % (temp, value))
					f.close()
				else:
					outfile="%s/%s_%s_%03i_%03i.dat" % (suboutput, args.keyword, namestr, args.layerx, args.layery)
					f=open(outfile, 'w')
					for td in temperature_datasets:
						temperature_folder=db.get_temp_output(td[len(corenames)-1])
						filename="%s/%s/%s/%s/results/%s.dat" % (resultFolder, subResultFolder, material_folder, temperature_folder, 'cond_perp_matrix')
						value=float(read(filename, line=args.layerx)[args.layery])
						temp=td[len(corenames)-1]
						f.write("%0.17e\t%0.17e\n" % (temp, value))
					f.close()

			if args.keyword=='resist_perp':
				if args.layerx==None or args.layery==None:
					outfile="%s/%s_%s.dat" % (suboutput, args.keyword, namestr)
					f=open(outfile, 'w')
					for td in temperature_datasets:
						temperature_folder=db.get_temp_output(td[len(corenames)-1])
						filename="%s/%s/%s/%s/results/%s.dat" % (resultFolder, subResultFolder, material_folder, temperature_folder, 'resist_perp')
						value=float(read(filename, line=0)[0])
						temp=td[len(corenames)-1]
						f.write("%0.17e\t%0.17e\n" % (temp, value))
					f.close()
				else:
					outfile="%s/%s_%s_%03i_%03i.dat" % (suboutput, args.keyword, namestr, args.layerx, args.layery)
					print outfile
					f=open(outfile, 'w')
					for td in temperature_datasets:
						temperature_folder=db.get_temp_output(td[len(corenames)-1])
						filename="%s/%s/%s/%s/results/%s.dat" % (resultFolder, subResultFolder, material_folder, temperature_folder, 'cond_perp_matrix')
						value=float(read(filename, line=args.layerx)[args.layery])
						temp=td[len(corenames)-1]
						f.write("%0.17e\t%0.17e\n" % (temp, 1.0/value))
					f.close()

			if args.keyword=='isodelta':
				outfile="%s/%s_%s.dat" % (suboutput, args.keyword, namestr)
				f=open(outfile, 'w')
				for td in temperature_datasets:
					temperature_folder=db.get_temp_output(td[len(corenames)-1])
					filename="%s/%s/%s/%s/results/%s.dat" % (resultFolder, subResultFolder, material_folder, temperature_folder, 'mu')
					mu=float(read(filename, line=0)[0])
					isodelta=-mu
					temp=td[len(corenames)-1]
					f.write("%0.17e\t%0.17e\n" % (temp, isodelta))
				f.close()

			if args.keyword=='dopant_activation' or args.keyword=='occNum_c':
				folder="%s/%s/%s/" % (resultFolder, subResultFolder, material_folder)
				filename="%s/%s/results/%s.dat" % (folder, db.get_temp_output(5.0), 'occNum_c')
				if not os.path.exists(filename):
					print "Warning: Dataset (T=5K) %s=%f is not present. %s does not exist." % (tcd, fd[tci], filename)
				else:
					occNum_c=float(read(filename, line=0)[0])
					f=open(outfile, 'a')
					if args.keyword=='dopant_activation':
						f.write("%0.17e\t%0.17e\n" % (fd[tci], occNum_c/fd[tci]))
					else:
						f.write("%0.17e\t%0.17e\n" % (fd[tci], occNum_c))
					f.close()

			if args.keyword=='tc':
				# get tc and error in tc
				folder="%s/%s/%s/" % (resultFolder, subResultFolder, material_folder)
				filename="%s/tc.dat" % folder
				success=True
				if not os.path.exists(filename):
					success=False
					print "Warning: Dataset %s=%f is not present. %s does not exist." % (tcd, fd[tci], filename)
					answer=raw_input("Try to get? (Y/n)")
					if answer!='n':
						success=gettc(args.database, db, folder, args.temperatures, args.tsteps, args.dM)
						if not success:
							print "Warning: Data for %s=%f is not present. -> Skip" % (tcd, fd[tci])
							
				if success:	
					print "Add dataset: %s=%f" % (tcd, fd[tci])
					g=open(filename, 'r')
					tc=0.0
					dtc=0.0
					for l in g.readlines():
						if not l.startswith('#'):
							tc=float(l.split()[0])
						elif l.startswith('# Temperature accuracy'):
							dtc=float(l.partition('=')[2])
					g.close()
					# write tc data row
					f=open(outfile, 'a')
					f.write("%f\t%f\t%f\n" % (fd[tci], tc, dtc))
					f.close()
			

		elif args.keyword=='print':
			print namestr
			print 'Temperature\t%s' % special
			for td in temperature_datasets:
				print "%e\t%e" % (td[-3], td[-2])
			print

		elif args.keyword=='printfull':
			print namestr
			print 'Temperature\t%s\tSource' % special
			for td in temperature_datasets:
				print "%e\t%e\t%s" % (td[-3], td[-2], td[-1])
			print

if __name__=="__main__":
	main()
