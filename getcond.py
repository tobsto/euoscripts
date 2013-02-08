#!/usr/bin/python

import subprocess
import sys
import os
import argparse
import database
import system_parameter
import shutil

def get_worker():
	host=database.get_host()
	idb=database.isolated_database()
	idb.download()
	for worker in idb.workers:
		if worker.host==host:
			return worker
	print "Error: get_worker: %s is an unknown working host. Break." % host
	exit(1)
	
def getcond(inputFolder, mpicmd, np=1, isodeltadb=False, outputFolder=None):
	runcmd=mpicmd + " -np %i" % np
	runcmd=runcmd + " getcond.out -i %s" % inputFolder
	if outputFolder!=None:
		runcmd=runcmd + " -o %s" % outputFolder

	if isodeltadb:
		# get isodeltas from database
		parafile=inputFolder+"/parameter.cfg"
		(Delta_l, Delta_r)=database.get_isodeltas_from_parafile(parafile)
		runcmd=runcmd + " --Delta_l0 %0.17e --Delta_r0 %0.17e" % (Delta_l, Delta_r)
	#print runcmd
	subprocess.call(runcmd, shell=True)

def getcondremote(host, db, filenames, inputFolder, mpicmd, np=1, isodeltadb=False, outputFolder=None):
	if host=='heisenberg':
		getcond(inputFolder, mpicmd, np, isodeltadb, outputFolder)
	else:
		print "download ..."
		cmd = "rsync -avz stollenw@heisenberg.physik.uni-bonn.de:%s/results temp_cond/" % inputFolder
		cmd = cmd+ "; rsync -avz stollenw@heisenberg.physik.uni-bonn.de:%s/parameter.cfg temp_cond/" % inputFolder
		#print cmd
		proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
		proc.communicate()

		print "calculate ..."
		getcond("temp_cond/", mpicmd, np, isodeltadb, outputFolder)

		print "upload ..."
		cmd='scp '
		for filename in filenames:
			cmd=cmd+"temp_cond/results/%s " % filename
		cmd=cmd+"stollenw@heisenberg.physik.uni-bonn.de:%s/results/" % inputFolder

		#print cmd
		proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
		proc.communicate()
		print "done"
				

def check_file_exists(host, path):
	if host=='heisenberg':
		return os.path.exists(path)
	else:
		cmd = "ssh %s '[[ -f %s ]]'" % ('stollenw@heisenberg.physik.uni-bonn.de', path)
		proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
		proc.communicate()
		if proc.returncode==0:
			return True
		else:
			return False	

	
def main():
	parser = argparse.ArgumentParser(description='Calculate conductivity out of euo program results')
	parser.add_argument('-d', '--database', help='specify database')
	parser.add_argument('-s', '--dataset', nargs='+', help='specify dataset without temperature')
	parser.add_argument('-n', '--np', default=1, help='Number of processes for parallel use', type=int)
	parser.add_argument('-i', '--input', help='Input folder containing result of a single run.')
	parser.add_argument('-o', '--output', default=None, help='Output Folder for the single run results (optional, default=input)')
	parser.add_argument('--no_isodelta_db', action='store_false', help='No fetching of more accurate isodeltas in the case of heterostructures')
	parser.add_argument('--overwrite', action="store_true", help='recalculate conductivity, even if it is present in the database')
	#parser.add_argument('--force_download', action="store_true", help='Download *all* results from database, even if they exist in the current folder')
	args = parser.parse_args()
	

	# remote or heisenberg
	host=database.get_host()
	# get mpi run command depening on host
	mpicmd=get_worker().mpicmd

	# add current working directory to system path
	sys.path.append(os.getcwd())

	if not args.input==None:
		getcond(args.input, np=args.np, isodeltadb=args.no_isodelta_db, outputFolder=args.output)
	else:
		if not args.database in ('bulk', 'isolated', 'hetero'):
			print "Database must be 'bulk', 'isolated' or 'hetero'"
			exit(1)
			
		db=None
		corenames=None
		isodeltadb=False
		if args.database=='bulk':
			db=database.bulk_database()	
			corenames=('material', 'ni', 'T')
			filenames=("cond.dat", "resist.dat")
			top_result_folder = "/home/stollenw/projects/euo/results/bulk/"
		elif args.database=='isolated':
			db=database.isolated_database()	
			corenames=('material', 'N', 'ni', 'T')
			top_result_folder = "/home/stollenw/projects/euo/results/isolated/"
			filenames=("cond.dat", "resist.dat", "cond_perp.dat", "resist_perp.dat", "cond_perp_matrix.dat", "resist_perp_matrix.dat")
		else:
			db=database.heterostructure_database()	
			corenames=('material', 'N', 'M', 'ni', 'ncr', 'dW', 'T')
			top_result_folder = "/home/stollenw/projects/euo/results/heterostructure/"
			filenames=("cond.dat", "resist.dat", "cond_perp.dat", "resist_perp.dat", "cond_perp_matrix.dat", "resist_perp_matrix.dat")
			isodeltadb=args.no_isodelta_db
		db.download()
	
		# get filtered data, i.e. reduce according to args.dataset (if not given, only sort)
		filtered_data=database.filtrate(db.data, corenames, args.dataset)

		for fd in filtered_data:
			print fd
			result_folder = fd[-1] + "/"
			# check if conductivity calculation was already performed
			print "check existence ..." 
			exists=check_file_exists(host, '%s/results/%s' % (result_folder, filenames[0]))
			# calculate conductivity if necessary or forced
			if not exists or args.overwrite:
				print "calculate conductivity ..." 
				getcondremote(host, db, filenames, result_folder, mpicmd, args.np, isodeltadb)
	
if __name__=="__main__":
	main()
