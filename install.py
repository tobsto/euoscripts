#!/usr/bin/python

import subprocess

programms=['runeuo.py','euorun.py', 'database.py', 'job.py', 'isolated_remote.py','isolated_update.py', 'isolated_print.py', 'system_parameter.py']
#programms=['euorun.py', 'database.py', 'get_total_magnetisation.py','job.py', 'pararun.py','reflect.py','isolated_remote.py','isolated_update.py', 'fetchdeb.py', 'isolated_print.py', 'system_parameter.py']

destinations=['/home/stollenw/Sonstiges/Programme/bin','/mnt/stollenw/sonstiges/local/python', '/mnt/dhome/programms/bin']
for d in destinations:
	for p in programms:
		cmd="cp %s %s" % (p,d)
		print cmd
		subprocess.call(cmd, shell=True)

