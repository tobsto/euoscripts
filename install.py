#!/usr/bin/python

import subprocess

programms=['euo.py', 'get_total_magnetisation.py','job.py', 'pararun.py','reflect.py','run.py','waitrun.py','isodelta_update.py', 'fetchdeb.py', 'isodelta_print.py', 'jobscheduler.py', 'submit.py', 'queue.py']

destinations=['/home/stollenw/Sonstiges/Programme/bin','/mnt/stollenw/sonstiges/local/python', '/mnt/dhome/programms/bin']
for d in destinations:
	for p in programms:
		cmd="cp %s %s" % (p,d)
		print cmd
		subprocess.call(cmd, shell=True)

