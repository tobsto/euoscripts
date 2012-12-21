#!/usr/bin/python
import euo
import itertools
import argparse

#material_list = ['Metal','Heisenberg-Metal','EuGd0','Band-Magnetic-Metal']
material_list = ['Metal','Heisenberg-Metal','EuGdO']
N_list=[2,3,4,5,9,15]
nc_list=[0.005,0.01,0.02,0.05,1.00]
parameter_list=[material_list,N_list,nc_list]
parameter=list(itertools.product(*parameter_list))

parser = argparse.ArgumentParser(description='Print database for energy shifts in EuO and substrate')
parser.add_argument('-d', '--database', default='/home/stollenw/projects/euo/database/isodelta.db', help='Database file name')
parser.add_argument('-p', '--plotfolder', default='/home/stollenw/projects/euo/database/plots', help='Database file name')
args = parser.parse_args()

database=euo.isodeltabase()
if args.database!='/home/stollenw/projects/euo/database/isodelta.db':
	database.read(args.database)
else:
	database.download()

for p in parameter:
	#print "# Material: %s, N=%03i, nc=%06.4f" %(p[0], p[1], p[2])
	print p
	material = p[0]
	N=p[1]
	nc=p[2]
	f = open("%s/isodeltas_%s_N%03i_nc%e.dat" % (args.plotfolder, material, N, nc), 'w')
	for e in sorted(filter(lambda element : element[0] == material and element[1] == N and element[2] == nc, database.data), key= lambda element: element[3]):
		print "T=%e\tDelta=%e\t%s" % (e[3], e[4], e[5])
		f.write("%e\t%e\t%s\n" % (e[3], e[4], e[5]))
