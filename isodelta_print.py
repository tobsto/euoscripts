#!/usr/bin/python
import itertools
import argparse
import database

#material_list = ['Metal','Heisenberg-Metal','EuGd0','Band-Magnetic-Metal']
material_list = ['Metal','Heisenberg-Metal','EuGdO']
N_list=[2,3,4,5,9,15]
nc_list=[0.01,1.00]
parameter_list=[material_list,N_list,nc_list]
parameter=list(itertools.product(*parameter_list))

parser = argparse.ArgumentParser(description='Print database for energy shifts in EuO and substrate')
parser.add_argument('-d', '--database', default='/home/stollenw/projects/euo/database/isolated.db', help='Database file name')
parser.add_argument('-p', '--plotfolder', default='/home/stollenw/projects/euo/database/plots', help='Database file name')
parser.add_argument('-s', '--short', action='store_true', help='Database file name')
args = parser.parse_args()

database=database.isolated_database()
if args.database!='/home/stollenw/projects/euo/database/isolated.db':
	database.read(args.database)
else:
	database.download()

for p in parameter:
	#print "# Material: %s, N=%03i, nc=%06.4f" %(p[0], p[1], p[2])
	material = p[0]
	N=p[1]
	nc=p[2]
	if len(filter(lambda element : element[0] == material and element[1] == N and element[2] == nc, database.data))!=0:
		print p
		print "Temperature\tDelta\t\tSource"
		f = open("%s/isodeltas_%s_N%03i_nc%e.dat" % (args.plotfolder, material, N, nc), 'w')
		for e in sorted(filter(lambda element : element[0] == material and element[1] == N and element[2] == nc, database.data), key= lambda element: element[3]):
			if not args.short:
				print "%e\t%e\t%s" % (e[3], e[4], e[5])
				f.write("%e\t%e\t%s\n" % (e[3], e[4], e[5]))
			else:
				print "%e\t%e" % (e[3], e[4])
				f.write("%e\t%e\n" % (e[3], e[4]))
