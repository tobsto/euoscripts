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
	
def getcond(inputFolder, np=1, isodeltadb=False, outputFolder=None):
	mpicmd=get_worker().mpicmd
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

def remote_file_exists(host, path):
	cmd = "ssh %s '[[ -f %s ]]'" % (host, path)
	proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	proc.communicate()
	if proc.returncode==0:
		return True
	else:
		return False	
	
def main():
	parser = argparse.ArgumentParser(description='Calculate conductivity out of euo program results')
	parser.add_argument('-i', '--input', help='Input folder containing results. If not given, calculate the conductivity for all results from all databases')
	parser.add_argument('--no_isodelta_db', action='store_false', help='No fetching of more accurate isodeltas in the case of heterostructures')
	parser.add_argument('-n', '--np', default=1, help='Number of processes for parallel use', type=int)
	parser.add_argument('-o', '--output', default=None, help='Output Folder')
	parser.add_argument('--overwrite', action="store_true", help='recalculate conductivity in all results from all databases (hetero, isolated, bulk)')
	parser.add_argument('-d', '--db', default='all', help='specify database')
	args = parser.parse_args()
	
	flag_bulk=False
	flag_iso=False
	flag_hetero=False
	if args.db=='all':
		flag_bulk=True
		flag_iso=True
		flag_hetero=True
	elif args.db=='bulk':
		flag_bulk=True
	elif args.db=='isolated':
		flag_iso=True
	elif args.db=='hetero':
		flag_hetero=True
		
	# add current working directory to system path
	sys.path.append(os.getcwd())

	if not args.input==None:
		getcond(args.input, np=args.np, isodeltadb=args.no_isodelta_db, outputFolder=args.output)
	else:
		if flag_bulk:
			# bulk database
			print "Bulk database"
			bdb=database.bulk_database()	
			bdb.download()
			temp_output="temp_cond/bulk/"
			for (material, ni, T, mag, path) in bdb.data:
				result_folder = bdb.get_output(material, ni) + bdb.get_temp_output(T)
				temp_result_folder = temp_output + result_folder 
				# check if conductivity calculation was already performed
				print "check %s, ni=%f, T=%f ..." % (material, ni, T)
				exists=remote_file_exists('stollenw@heisenberg.physik.uni-bonn.de', '/home/stollenw/projects/euo/results/bulk/%s/results/cond.dat' % result_folder)
				# calculate conductivity if necessary or forced
				if not exists or args.overwrite:
					bdb.download_results(material, ni, T, temp_output)
					print "calculate %s, ni=%f, T=%f ..." % (material, ni, T)
					getcond(temp_result_folder, np=args.np, isodeltadb=False)
	
					# copy conductivity results to result-database
					result_names=("cond.dat", "resist.dat")
					cmd='scp '
					for filename in result_names:
						cmd=cmd+"%s/results/%s " % (temp_result_folder, filename)
					cmd=cmd+"stollenw@heisenberg.physik.uni-bonn.de:/home/stollenw/projects/euo/results/bulk/%s/results/" % result_folder
					#print cmd
					proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
					proc.wait()
		if flag_iso:
			# isolated database
			print "Isolated database"
			idb=database.isolated_database()	
			idb.download()
			temp_output="temp_cond/isolated/"
			for (material, N, ni, T, isodelta, path) in idb.data:
				result_folder = idb.get_output(material, N, ni) + idb.get_temp_output(T)
				temp_result_folder = temp_output + result_folder 
				# check if conductivity calculation was already performed
				print "check %s, N=%i, ni=%f, T=%f ..." % (material, N, ni, T)
				exists=remote_file_exists('stollenw@heisenberg.physik.uni-bonn.de', '/home/stollenw/projects/euo/results/isolated/%s/results/cond_perp_matrix.dat' % result_folder)
				# calculate conductivity if necessary or forced
				if not exists or args.overwrite:
					idb.download_results(material, N, ni, T, temp_output)
					print "calculate %s, N=%i, ni=%f, T=%f ..." % (material, N, ni, T)
					getcond(temp_result_folder, np=args.np, isodeltadb=False)
	
					# copy conductivity results to result-database
					result_names=("cond.dat", "resist.dat", "cond_perp.dat", "resist_perp.dat", "cond_perp_matrix.dat", "resist_perp_matrix.dat")
					cmd='scp '
					for filename in result_names:
						cmd=cmd+"%s/results/%s " % (temp_result_folder, filename)
					cmd=cmd+"stollenw@heisenberg.physik.uni-bonn.de:/home/stollenw/projects/euo/results/isolated/%s/results/" % result_folder
					#print cmd
					proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
					proc.wait()
	
		if flag_hetero:
			# heterostructure database
			print "Heterostructure database"
			hdb=database.heterostructure_database()	
			hdb.download()
			temp_output="temp_cond/heterostructure/"
			for (material, N, M, ni, ncr, dW, T, avmag, path) in hdb.data:
				result_folder = hdb.get_output(material, N, M, ni, ncr, dW) + hdb.get_temp_output(T)
				temp_result_folder = temp_output + result_folder 
				# check if conductivity calculation was already performed
				print "check %s, N=%i, M=%i, ni=%f, ncr=%f, T=%f ..." % (material, N, M, ni, ncr, T)
				exists=remote_file_exists('stollenw@heisenberg.physik.uni-bonn.de', '/home/stollenw/projects/euo/results/heterostructure/%s/results/cond_perp_matrix.dat' % result_folder)
				# calculate conductivity if necessary or forced
				if not exists or args.overwrite:
					hdb.download_results(material, N, M, ni, ncr, dW, T, temp_output)
					print "calculate %s, N=%i, M=%i, ni=%f, ncr=%f, T=%f ..." % (material, N, M, ni, ncr, T)
					getcond(temp_result_folder, np=args.np, isodeltadb=args.no_isodelta_db)
	
					# copy conductivity results to result-database
					result_names=("cond.dat", "resist.dat", "cond_perp.dat", "resist_perp.dat", "cond_perp_matrix.dat", "resist_perp_matrix.dat")
					cmd='scp '
					for filename in result_names:
						cmd=cmd+"%s/results/%s " % (temp_result_folder, filename)
					cmd=cmd+"stollenw@heisenberg.physik.uni-bonn.de:/home/stollenw/projects/euo/results/heterostructure/%s/results/" % result_folder
					#print cmd
					proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
					proc.wait()
	
	
if __name__=="__main__":
	main()
