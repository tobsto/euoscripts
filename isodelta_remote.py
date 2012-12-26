#!/usr/bin/python

import euo
import os
import argparse
import subprocess

# Update database for energy shifts in EuO and substrate
def main():
	parser = argparse.ArgumentParser(description='Update database for energy shifts in EuO and substrate on remote database')
	parser.add_argument('input', nargs='+', help='Folders containing results of isolated material runs')
  	parser.add_argument('--dry', action='store_true', help='Simulate updating of database')

	args = parser.parse_args()

	# get host
	host=euo.get_host()
	path_prefix=''
	path_suffix=''
	if host=='agem.th.physik.uni-bonn.de':
		path_prefix='/home/stollenw/runs/'
		path_suffix='agem/'
	elif host=='bgem.th.physik.uni-bonn.de':
		path_prefix='/home/stollenw/runs/'
		path_suffix='bgem/'
	elif host=='stgeorgenamreith':
		path_prefix='/home/stollenw/runs/'
		path_suffix='georg/'
	elif host=='pfaffenschlag':
		path_prefix='/home/stollenw/runs/'
		path_suffix='schlag/'
	elif host=='bischofstetten':
		path_prefix='/home/stollenw/runs/'
		path_suffix='stetten/'
	elif host=='stleonhardamforst':
		path_prefix='/home/stollenw/runs/'
		path_suffix='leo/'
	elif host=='lunzamsee':
		path_prefix='/home/stollenw/runs/'
		path_suffix='lunz/'
	elif host=='login':
		path_prefix='/home/stollenw/druns/'
		path_suffix=''
	elif host!='heisenberg':
		print "Error: Isodelta remote: Unknow host: %s" % host
		print "Break."
		exit(1)

	# get path on heisenberg
	inputs=[]
	if host!='heisenberg':
		version_part=''
		for ipath in args.input:
			# get absolute path
			apath=os.path.abspath(ipath)
			version_part_found=False
			for part in apath.split('/'):
				if part.startswith('runs_version'):
					version_part=part
					version_part_found=True
					break
			if version_part_found==False:
				print "Error: Isodelta remote: Unable to get version part from: %s" % apath
				print "Break."
				exit(1)
			name=apath.rstrip('/').split('/')[-1]
			inputs.append("%s%s/%s%s/" % (path_prefix, version_part, path_suffix, name))
	else:
		inputs=args.input
	cmd='/home/stollenw/Sonstiges/Programme/bin/isodelta_update.py'
	for inp in inputs:
		cmd+=" %s" % inp
	if args.dry:
		cmd+=" --dry"	

	rcmd="ssh heisenberg.physik.uni-bonn.de '%s'" % cmd
	#print rcmd
	subprocess.call(rcmd, shell=True)
if __name__=="__main__":
	main()
