#!/usr/bin/python

import subprocess

programms=['job.py', 'system_parameter.py', 'database.py', 'euorun.py', 'run.py', 'bulk_remote.py','bulk_update.py', 'bulk_print.py', 'isolated_remote.py','isolated_update.py', 'isolated_print.py', 'heterostructure_remote.py','heterostructure_update.py', 'heterostructure_print.py', 'get_total_magnetisation.py', 'reflect.py', 'xmpar.py', 'plot3d.py', 'getcond.py', 'analysis.py', 'mkplot.py', 'compare_databases.py', 'neighbors.py', 'heisenberg.py', 'findtc.py', 'tcplot.py', 'cleanResults.py', 'cleanTrash.py', 'plot.py', 'collectCurie.py', 'psearch', 'setup.sh', 'cumusum', 'convert3d.py', 'replace']

destinations=['/home/stollenw/Sonstiges/Programme/bin','/mnt/stollenw/sonstiges/local/python']
#destinations=['/home/stollenw/Sonstiges/Programme/bin']
for d in destinations:
	for p in programms:
		cmd="cp %s %s" % (p,d)
		print cmd
		subprocess.call(cmd, shell=True)

