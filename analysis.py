#!/usr/bin/python

import subprocess
import sys
import os
import argparse
import database
import system_parameter
import itertools

def read(filename, line=0):
	f=open(filename, 'r')
	lines=f.readlines()
	f.close()
	return lines[line].split()
			
def main():
	parser = argparse.ArgumentParser(description='Analyse euo program results', formatter_class=argparse.RawTextHelpFormatter)
	keyword_help="""Calculate the temperature dependent 
quantity specified by one of the following keywords

print
print full

totalmag	(for bulk)
cond		(for bulk)
resist		(for bulk)

avmag		(for isolated and heterostructures)
cond_para	(for isolated and heterostructures)
resist_para	(for isolated and heterostructures)
cond_perp	(for isolated and heterostructures)
resist_perp 	(for isolated and heterostructures)
isodelta 	(energy shift (-mu) for isolated systems)

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
		sophisticated_result_keywords=[]
	elif args.database=='isolated' or args.database=='hetero':
		simple_result_keywords=['avmag']
		sophisticated_result_keywords=['cond_para', 'resist_para', 'cond_perp', 'resist_perp', 'isodelta']

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
		

	# iterate through database
	for fd in filtered_data:
		print fd
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
				outfile="%s/%s_%s.dat" % (suboutput, args.keyword, namestr)
				f=open(outfile, 'w')
				for td in temperature_datasets:
					temperature_folder=db.get_temp_output(td[len(corenames)-1])
					filename="%s/%s/%s/%s/results/%s.dat" % (resultFolder, subResultFolder, material_folder, temperature_folder, 'cond')
					value=float(read(filename, line=0)[1])
					temp=td[len(corenames)-1]
					f.write("%0.17e\t%0.17e\n" % (temp, value))
				f.close()

			if args.keyword=='resist_para':
				outfile="%s/%s_%s.dat" % (suboutput, args.keyword, namestr)
				f=open(outfile, 'w')
				for td in temperature_datasets:
					temperature_folder=db.get_temp_output(td[len(corenames)-1])
					filename="%s/%s/%s/%s/results/%s.dat" % (resultFolder, subResultFolder, material_folder, temperature_folder, 'resist')
					value=float(read(filename, line=0)[1])
					temp=td[len(corenames)-1]
					f.write("%0.17e\t%0.17e\n" % (temp, value))
				f.close()


			if args.keyword=='cond_perp':
				outfile="%s/%s_%s.dat" % (suboutput, args.keyword, namestr)
				f=open(outfile, 'w')
				for td in temperature_datasets:
					temperature_folder=db.get_temp_output(td[len(corenames)-1])
					filename="%s/%s/%s/%s/results/%s.dat" % (resultFolder, subResultFolder, material_folder, temperature_folder, 'cond_perp')
					value=float(read(filename, line=0)[0])
					temp=td[len(corenames)-1]
					f.write("%0.17e\t%0.17e\n" % (temp, value))
				f.close()

			if args.keyword=='resist_perp':
				outfile="%s/%s_%s.dat" % (suboutput, args.keyword, namestr)
				f=open(outfile, 'w')
				for td in temperature_datasets:
					temperature_folder=db.get_temp_output(td[len(corenames)-1])
					filename="%s/%s/%s/%s/results/%s.dat" % (resultFolder, subResultFolder, material_folder, temperature_folder, 'resist_perp')
					value=float(read(filename, line=0)[0])
					temp=td[len(corenames)-1]
					f.write("%0.17e\t%0.17e\n" % (temp, value))
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


		elif args.keyword=='print':
			print 'Temperature\t%s' % special
			for td in temperature_datasets:
				print "%e\t%e" % (td[-3], td[-2])
			print

		elif args.keyword=='printfull':
			print 'Temperature\t%s\tSource' % special
			for td in temperature_datasets:
				print "%e\t%e\t%s" % (td[-3], td[-2], td[-1])
			print

if __name__=="__main__":
	main()
