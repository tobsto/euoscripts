#!/usr/bin/python

import subprocess

programms=['job.py', 'system_parameter.py', 'database.py', 'euorun.py', 'runeuo.py', 'heterostructure_remote.py','heterostructure_update.py', 'heterostructure_print.py', 'heterostructure_remote.py','heterostructure_update.py', 'heterostructure_print.py']

destinations=['/home/stollenw/Sonstiges/Programme/bin','/mnt/stollenw/sonstiges/local/python', '/mnt/dhome/programms/bin']
for d in destinations:
	for p in programms:
		cmd="cp %s %s" % (p,d)
		print cmd
		subprocess.call(cmd, shell=True)

