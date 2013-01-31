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
	
	if not args.database in ('bulk', 'isolated', 'hetero'):
		print "Database must be 'bulk', 'isolated' or 'hetero'"
		exit(1)
		
	# remote or heisenberg
	host=database.get_host()
	# get mpi run command depening on host
	mpicmd=get_worker().mpicmd

	# add current working directory to system path
	sys.path.append(os.getcwd())

	if not args.input==None:
		getcond(args.input, np=args.np, isodeltadb=args.no_isodelta_db, outputFolder=args.output)
	else:
		if args.database=='bulk':
			# bulk database
			print "Bulk database"
			filenames=("cond.dat", "resist.dat")
			bdb=database.bulk_database()	
			bdb.download()
			for (material, ni, T, mag, path) in bdb.data:
				result_folder = "/home/stollenw/projects/euo/results/bulk/" + bdb.get_output(material, ni) + bdb.get_temp_output(T)
				# check if conductivity calculation was already performed
				print "check %s, ni=%f, T=%f ..." % (material, ni, T)
				exists=check_file_exists(host, '%s/results/cond.dat' % result_folder)
				# calculate conductivity if necessary or forced
				if not exists or args.overwrite:
					print "calculate %s, ni=%f, T=%f ..." % (material, ni, T)
					getcondremote(host, bdb, filenames, result_folder, mpicmd, np=args.np, isodeltadb=False)

		if args.database=='isolated':
			# isolated database
			print "Isolated database"
			filenames=("cond.dat", "resist.dat", "cond_perp.dat", "resist_perp.dat", "cond_perp_matrix.dat", "resist_perp_matrix.dat")
			idb=database.isolated_database()	
			idb.download()
			for (material, N, ni, T, isodelta, path) in idb.data:
				result_folder = "/home/stollenw/projects/euo/results/isolated/" + idb.get_output(material, N, ni) + idb.get_temp_output(T)
				# check if conductivity calculation was already performed
				print "check %s, N=%i, ni=%f, T=%f ..." % (material, N, ni, T)
				exists=check_file_exists(host, '%s/results/cond_perp_matrix.dat' % result_folder)
				# calculate conductivity if necessary or forced
				if not exists or args.overwrite:
					print "calculate %s, N=%i, ni=%f, T=%f ..." % (material, N, ni, T)
					getcondremote(host, idb, filenames, result_folder, mpicmd, np=args.np, isodeltadb=False)
	
		if args.database=='hetero':
			# heterostructure database
			print "Heterostructure database"
			filenames=("cond.dat", "resist.dat", "cond_perp.dat", "resist_perp.dat", "cond_perp_matrix.dat", "resist_perp_matrix.dat")
			hdb=database.heterostructure_database()	
			hdb.download()
			for (material, N, M, ni, ncr, dW, T, avmag, path) in hdb.data:
				result_folder = "/home/stollenw/projects/euo/results/heterostructure/" + hdb.get_output(material, N, M, ni, ncr, dW) + hdb.get_temp_output(T)
				# check if conductivity calculation was already performed
				print "check %s, N=%i, M=%i, ni=%f, ncr=%f, dW=%f, T=%f ..." % (material, N, M, ni, ncr, dW, T)
				exists=check_file_exists(host, '%s/results/cond_perp_matrix.dat' % result_folder)
				# calculate conductivity if necessary or forced
				if not exists or args.overwrite:
					print "calculate %s, N=%i, M=%i, ni=%f, ncr=%f, dW=%f, T=%f ..." % (material, N, M, ni, ncr, dW, T)
					getcondremote(host, hdb, filenames, result_folder, mpicmd, np=args.np, isodeltadb=args.no_isodelta_db)
	
if __name__=="__main__":
	main()
