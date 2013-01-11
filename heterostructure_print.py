#!/usr/bin/python
import itertools
import argparse
import os

import database

parser = argparse.ArgumentParser(description='Print database for heterostructure runs')
parser.add_argument('-d', '--database', default='/home/stollenw/projects/euo/database/hetero.db', help='Database file name')
parser.add_argument('-p', '--plotfolder', default='/home/stollenw/projects/euo/database/analysis/hetero/avmag/', help='Database file name')
parser.add_argument('-s', '--short', action='store_true', help='Less output')
args = parser.parse_args()

if not os.path.exists(args.plotfolder):
	os.makedirs(args.plotfolder)

database=database.heterostructure_database()
if args.database!='/home/stollenw/projects/euo/database/hetero.db':
	database.read(args.database)
else:
	database.download()

# get columns of data and remove duplicates by converting to
# a set (no duplicates) and back to a list 
material_list=list(set([row[0] for row in database.data ]))
N_list=list(set([int(row[1]) for row in database.data ]))
M_list=list(set([int(row[2]) for row in database.data ]))
ni_list=list(set([float(row[3]) for row in database.data ]))
ncr_list=list(set([float(row[4]) for row in database.data ]))
dW_list=list(set([float(row[5]) for row in database.data ]))

# sort data
material_list.sort()
N_list.sort()
M_list.sort()
ni_list.sort()
ncr_list.sort()
dW_list.sort()

# all combinations
parameter_list=[material_list,N_list,M_list,ni_list,ncr_list,dW_list]
parameter=list(itertools.product(*parameter_list))

for p in parameter:
	material = p[0]
	N=p[1]
	M=p[2]
	ni=p[3]
	ncr=p[4]
	dW=p[5]
	if len(filter(lambda element : element[0] == material and element[1] == N  and element[2] == M and element[3] == ni and element[4] == ncr and element[5] == dW, database.data))!=0:
		print p
		if not args.short:
			print "Temperature\tAvmag\t\tSource"
		else:
			print "Temperature\tAvmag"
		f = open("%s/avmag_%s_N%03i_M%03i_ni%06.4f_ncr%06.4f_dW%06.4f.dat" % (args.plotfolder, material, N, M, ni, ncr, dW), 'w')
		for e in sorted(filter(lambda element : element[0] == material and element[1] == N  and element[2] == M and element[3] == ni and element[4] == ncr and element[5] == dW, database.data), key= lambda element: element[6]):
			if not args.short:
				print "%e\t%e\t%s" % (e[6], e[7], e[8])
				f.write("%e\t%e\t%s\n" % (e[6], e[7], e[8]))
			else:
				print "%e\t%e" % (e[6], e[7])
				f.write("%e\t%e\n" % (e[6], e[7]))
