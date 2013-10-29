#!/usr/bin/python
import itertools
import argparse
import os

import database

parser = argparse.ArgumentParser(description='Print database for bulk results')
parser.add_argument('-d', '--database', default='/users/stollenw/projects/euo/database/bulk.db', help='Database file name')
parser.add_argument('-p', '--plotfolder', default='/users/stollenw/projects/euo/database/analysis/bulk/mag/', help='Database file name')
parser.add_argument('-s', '--short', action='store_true', help='Less output')
args = parser.parse_args()

if not os.path.exists(args.plotfolder):
	os.makedirs(args.plotfolder)

database=database.bulk_database()
if args.database!='/users/stollenw/projects/euo/database/bulk.db':
	database.read(args.database)
else:
	database.download()

# get columns of data and remove duplicates by converting to
# a set (no duplicates) and back to a list 
material_list=list(set([row[0] for row in database.data ]))
ni_list=list(set([float(row[1]) for row in database.data ]))

# sort data
material_list.sort()
ni_list.sort()

# all combinations
parameter_list=[material_list,ni_list]
parameter=list(itertools.product(*parameter_list))

for p in parameter:
	#print "# Material: %s, ni=%06.4f" %(p[0], p[2])
	material = p[0]
	ni=p[1]
	if len(filter(lambda element : element[0] == material and element[1] == ni, database.data))!=0:
		print p
		if not args.short:
			print "Temperature\tMag\t\tSource"
		else:
			print "Temperature\tMag"
		f = open("%s/mag_%s_ni%06.4f.dat" % (args.plotfolder, material, ni), 'w')
		for e in sorted(filter(lambda element : element[0] == material and element[1] == ni, database.data), key= lambda element: element[2]):
			if not args.short:
				print "%e\t%e\t%s" % (e[2], e[3], e[4])
				f.write("%e\t%e\t%s\n" % (e[2], e[3], e[4]))
			else:
				print "%e\t%e" % (e[2], e[3])
				f.write("%e\t%e\n" % (e[2], e[3]))
