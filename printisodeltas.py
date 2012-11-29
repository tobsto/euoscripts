#!/usr/bin/python
import euo
import itertools
database=euo.isodeltabase()
database.download()
material_list = ['EuO','Sub']
N_list=[5,9,15]
nc_list=[0.01,1.00]
parameter_list=[material_list,N_list,nc_list]
parameter=list(itertools.product(*parameter_list))

for p in parameter:
	print p
	material = p[0]
	N=p[1]
	nc=p[2]
	for e in sorted(filter(lambda element : element[0] == material and element[1] == N and element[2] == nc, database.data), key= lambda element: element[3]):
		print "%e\t%e\t%s" % (e[3], e[4], e[5])
		f = open("/home/stollenw/projects/euo/database/plots/isodeltas_%s_N%03i_nc%e.dat" % (material, N, nc), 'a')
		f.write("%e\t%e\t#%s\n" % (e[3], e[4], e[5]))
