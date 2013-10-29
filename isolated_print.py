#!/usr/bin/python
import itertools
import argparse
import os

import database

parser = argparse.ArgumentParser(description='Print database for energy shifts in EuO and substrate')
parser.add_argument('-d', '--database', default='/users/stollenw/projects/euo/database/isolated.db', help='Database file name')
parser.add_argument('-p', '--plotfolder', default='/users/stollenw/projects/euo/database/analysis/isolated/isodelta/', help='Database file name')
parser.add_argument('-s', '--short', action='store_true', help='Less output')
args = parser.parse_args()

if not os.path.exists(args.plotfolder):
	os.makedirs(args.plotfolder)

database=database.isolated_database()
if args.database!='/users/stollenw/projects/euo/database/isolated.db':
	database.read(args.database)
else:
	database.download()

# get columns of data and remove duplicates by converting to
# a set (no duplicates) and back to a list 
material_list=list(set([row[0] for row in database.data ]))
N_list=list(set([int(row[1]) for row in database.data ]))
nc_list=list(set([float(row[2]) for row in database.data ]))

# sort data
material_list.sort()
N_list.sort()
nc_list.sort()

# all combinations
parameter_list=[material_list,N_list,nc_list]
parameter=list(itertools.product(*parameter_list))

for p in parameter:
	#print "# Material: %s, N=%03i, nc=%06.4f" %(p[0], p[1], p[2])
	material = p[0]
	N=p[1]
	nc=p[2]
	if len(filter(lambda element : element[0] == material and element[1] == N and element[2] == nc, database.data))!=0:
		print p
		if not args.short:
			print "Temperature\tDelta\t\tSource"
		else:
			print "Temperature\tDelta"
		f = open("%s/isodeltas_%s_N%03i_nc%06.4f.dat" % (args.plotfolder, material, N, nc), 'w')
		for e in sorted(filter(lambda element : element[0] == material and element[1] == N and element[2] == nc, database.data), key= lambda element: element[3]):
			if not args.short:
				print "%e\t%e\t%s" % (e[3], e[4], e[5])
				f.write("%e\t%e\t%s\n" % (e[3], e[4], e[5]))
			else:
				print "%e\t%e" % (e[3], e[4])
				f.write("%e\t%e\n" % (e[3], e[4]))
