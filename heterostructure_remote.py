#!/usr/bin/python

import database
import os
import argparse
import subprocess

# Update database for energy shifts in EuO and substrate
def main():
	parser = argparse.ArgumentParser(description='Update database for heterostructure runs on remote database')
	parser.add_argument('input', nargs='+', help='Folders containing results of isolated material runs or folders containing subfolders with results')
  	parser.add_argument('--dry', action='store_true', help='Simulate updating of database')
  	parser.add_argument('--archive', action='store_true', help='Archive all results')

	args = parser.parse_args()

	# get host
	host=database.get_host()
	idb=database.heterostructure_database()
	idb.download()
	found=False
	serverdir=''
	clientdir=''
	for worker in idb.workers:
		if host==worker.host:
			serverdir=worker.serverdir	
			clientdir=worker.clientdir	
			found=True
	if not found:	
		print "Error: Heterostructure database remote: Unknow host: %s" % host
		print "Break."
		exit(1)

	# get path on steinschal-tradigist
	inputs=[]
	for ipath in args.input:
		# get absolute path
		apath=os.path.abspath(ipath)
		if not apath.startswith(clientdir):
			print "Error: Heterostructure database remote: %s is an unknown run path. Break." % apath
			exit(1)
		inputs.append(apath.replace(clientdir, serverdir, 1))

	cmd='/users/stollenw/projects/euo/tools/euoscripts/heterostructure_update.py'
	for inp in inputs:
		cmd+=" %s" % inp
	if args.dry:
		cmd+=" --dry"	
	if args.archive:
		cmd+=" --archive"	

	try:
		rcmd=['ssh', 'steinschal-tradigist.th.physik.uni-bonn.de', '%s' % cmd]
		subprocess.call(rcmd)
	except:
		print "Unable to update remote database. Break."
		exit(1)

if __name__=="__main__":
	main()
