#!/usr/bin/python

import subprocess
import sys
import os
import argparse
import database
import system_parameter
import itertools

def main():
	parser = argparse.ArgumentParser(description='Analyse euo program results')
	keyword_help="1.) cond: calculate the temperature dependent conductivity out of the given database"
	parser.add_argument('keyword', help=keyword_help)
	parser.add_argument('-d', '--database', help='Type of database: "bulk", "isolated" or "hetero"')
	parser.add_argument('-o', '--output', default='/home/stollenw/projects/euo/analysis/', help='Output folder')
	args = parser.parse_args()

	if not args.database in ('bulk', 'isolated', 'hetero'):
		parser.print_help()
		exit(0)
	allowed_keywords=('cond', 'cond_perp', 'resist', 'resist_perp', 'totalmag', 'avmag', 'print', 'printfull')
	result_keywords=('cond', 'cond_perp', 'resist', 'resist_perp', 'totalmag', 'avmag')
	if not args.keyword in allowed_keywords:
		parser.print_help()
		print "Allowed keywords are:"
		for ak in allowed_keywords:
			print ak
		exit(0)
	
	output=args.output
	

	resultFolder='/home/stollenw/projects/euo/results/'
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
	db.download()

	# get columns of data and remove duplicates by converting to
	# a set (no duplicates) and back to a list 
	parameter_list=[]
	for i in range(0, len(corenames[:-1])):
		parameter_list.append(list(set([row[i] for row in db.data ])))
	
	# sort data
	for pl in parameter_list:
		pl.sort()
	
	# all combinations
	parameter=list(itertools.product(*parameter_list))
	

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
	for p in parameter:
		# defining name
		namestr=db.get_output(*p).rstrip('/')
		# get datasets from database which match current dataset (material, N, M, ...) and sort it by temperatures
		filtered_datasets=sorted(filter(lambda element : all([element[i]==p[i] for i in range(0,len(p))]), db.data), key= lambda element: element[len(p)])
		if (len(filtered_datasets)>=min_result_number):
			print p
			if args.keyword in result_keywords:
				# extract data from relevant folders	
				cmd='cat '
				for fd in filtered_datasets:
					#cmd=cmd + "%s/results/%s.dat " % (fd[-1], args.keyword)
					cmd=cmd + "%s/%s/%s/%s/results/%s.dat " % (resultFolder, subResultFolder, namestr, db.get_temp_output(fd[len(p)]), args.keyword)
				cmd=cmd + " > %s/%s_%s.dat" % (suboutput, args.keyword, namestr)
				subprocess.call(cmd, shell=True)	
			elif args.keyword=='print':
				print 'Temperature\t%s' % special
				for fd in filtered_datasets:
					print "%e\t%e" % (fd[-3], fd[-2])
				print
			elif args.keyword=='printfull':
				print 'Temperature\t%s\tSource' % special
				for fd in filtered_datasets:
					print "%e\t%e\t%s" % (fd[-3], fd[-2], fd[-1])
				print

if __name__=="__main__":
	main()
