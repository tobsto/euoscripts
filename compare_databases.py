#!/usr/bin/python

import database
import os
import argparse

# Update database for energy shifts in EuO and substrate
def main():
	parser = argparse.ArgumentParser(description='Update database for heterostructure runs')
	parser.add_argument('input', nargs=2, help='Two database files')
  	parser.add_argument('-d', '--database', default='hetero', help='Database type: bulk, isolated or hetero (default)')
  	parser.add_argument('-r', '--reverse', action='store_true', help='reverse input file order')

	args = parser.parse_args()
	
	#print args.overwrite
	#print args.input
	#print args.database
	if args.reverse:
		args.input.reverse()	

	# initialize databases
	d1=None
	d2=None
	length=None
	if args.database=='hetero':
		d1=database.heterostructure_database()
		d2=database.heterostructure_database()
		length=6
	elif args.database=='isolated':
		d1=database.isolated_database()
		d2=database.isolated_database()
		length=3
	elif args.database=='bulk':
		d1=database.bulk_database()
		d2=database.bulk_database()
		length=2
	else:
		print "Database type must be 'bulk', 'isolated' or 'hetero' (default). Break"
		exit(1)
	d1.download("stollenw@heisenberg.physik.uni-bonn.de:%s" % args.input[0])
	d2.download("stollenw@heisenberg.physik.uni-bonn.de:%s" % args.input[1])

	print "Datasets present in %s but not in %s:" % (args.input[0], args.input[1])
	reduced_data2=[dset2[:length] for dset2 in d2.data]
	for dset1 in d1.data:
		if not dset1[:length] in reduced_data2:
			print dset1[:-1]

	
if __name__=="__main__":
	main()
