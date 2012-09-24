#!/usr/bin/python

import subprocess

programms=['euo.py', 'get_total_magnetisation.py','job.py', 'pararun.py','reflect.py','run.py','update.py']

destinations=['/home/stollenw/sonstiges/programms/bin','/mnt/stollenw/sonstiges/local/python', '/mnt/debcluster/programms/bin']
for d in destinations:
	for p in programms:
		cmd="cp %s %s" % (p,d)
		print cmd
		subprocess.call(cmd, shell=True)

