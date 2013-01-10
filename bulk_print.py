#!/usr/bin/python
import itertools
import argparse
import os

import database

#material_list = ['Metal','Heisenberg-Metal','EuGd0','Band-Magnetic-Metal']
material_list = ['Bulk-Metal','Bulk-Heisenberg-Metal','Bulk-EuGdO', 'Bulk-EuO_1-x']
ni_list=[0.001, 0.002, 0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.1, 0.2]
parameter_list=[material_list,ni_list]
parameter=list(itertools.product(*parameter_list))

parser = argparse.ArgumentParser(description='Print database for bulk results')
parser.add_argument('-d', '--database', default='/home/stollenw/projects/euo/database/bulk.db', help='Database file name')
parser.add_argument('-p', '--plotfolder', default='/home/stollenw/projects/euo/database/analysis/bulk/mag/', help='Database file name')
parser.add_argument('-s', '--short', action='store_true', help='Less output')
args = parser.parse_args()

database=database.bulk_database()
if args.database!='/home/stollenw/projects/euo/database/bulk.db':
	database.read(args.database)
else:
	database.download()

if not os.path.exists(args.plotfolder):
	os.makedirs(args.plotfolder)

for p in parameter:
	#print "# Material: %s, ni=%06.4f" %(p[0], p[2])
	material = p[0]
	ni=p[1]
	if len(filter(lambda element : element[0] == material and element[1] == ni, database.data))!=0:
		print p
		print "Temperature\tMag\t\tSource"
		f = open("%s/mag_%s_ni%06.4f.dat" % (args.plotfolder, material, ni), 'w')
		for e in sorted(filter(lambda element : element[0] == material and element[1] == ni, database.data), key= lambda element: element[2]):
			if not args.short:
				print "%e\t%e\t%s" % (e[2], e[3], e[4])
				f.write("%e\t%e\t%s\n" % (e[2], e[3], e[4]))
			else:
				print "%e\t%e" % (e[2], e[3])
				f.write("%e\t%e\n" % (e[2], e[3]))
