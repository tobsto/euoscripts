#!/usr/bin/python

import subprocess
import sys
import os

import database
import job
import system_parameter

def system_equal(sp1, sp2):
	# conditions
	conditions=[]
	conditions.append(sp1.get_system().name==sp2.get_system().name)
	conditions.append(sp1.N==sp2.N)
	conditions.append(sp1.concentration==sp2.concentration)
	if sp1.get_system().constituents!=(None,None):
		conditions.append(sp1.N0==sp2.N0)
		conditions.append(sp1.n_cr==sp2.n_cr)
		conditions.append(sp1.Delta_W==sp2.Delta_W)
	return all(conditions)

def database_exists(sp):
	if sp.get_system().constituents==(None,None):
		idb=database.isolated_database()
		idb.download()
		if idb.exists(sp.get_system().name, sp.N, sp.concentration, sp.temperature):
			return True
		else:
			return False
	else:
		hdb=database.heterostructure_database()
		hdb.download()
		if hdb.exists(sp.get_system().name, sp.N, sp.N0, sp.concentration, sp.n_cr, sp.Delta_W, sp.temperature):
			return True
		else:
			return False

def get_worker():
	host=database.get_host()
	idb=database.isolated_database()
	idb.download()
	for worker in idb.workers:
		if worker.host==host:
			return worker
	print "Error: get_worker: %s is an unknown working host. Break." % host
	exit(1)
	
class euorun:
	def __init__(self, np, material, N=5, M=None, ni=0.01, ncr=None, dW=None, output=None, input=None, initial_input=None, inputFlag=True, isoDeltaFlag=True, updatedbFlag=True, iteration_parameter=None, get_default_iteration_parameter=None, log='run', verbose=True, email='stollenwerk@th.physik.uni-bonn.de', mailcmd='mailx -s'):
		# number of nodes
		self.np=np
		# material name
		self.material=material
		# number of left layers
		self.N=N
		# number of right layers
		self.M=M
		# number of charge carriers in the left system
		self.ni=ni
		# number of charge carriers in the right system
		self.ncr=ncr
		# workfunction difference between left and right system
		self.dW=dW
		# initial input folder
		self.initial_input=initial_input
		# search automatically for suitable input
		self.inputFlag=inputFlag
		# add isolated delta values automatically 
		self.isoDeltaFlag=isoDeltaFlag
		# update databases after succesfful runs automatically
		self.updatedbFlag=updatedbFlag
		# additional parameter (like max2, wr1, etc.)
		# user defined parameter (if not defined add nothing)
		if iteration_parameter!=None:
			self.iteration_parameter=iteration_parameter
		else:
			self.iteration_parameter=''

		# function which gives the default iteration parameter depending on the material 
		# (only relevant for automatic isodelta runs)
		if get_default_iteration_parameter!=None:
			self.get_default_iteration_parameter=get_default_iteration_parameter
		else:
			self.get_default_iteration_parameter=database.get_iteration_parameter
		# isolated flag
		self.isolated=False
		if M==None or ncr==None or dW==None:
			self.isolated=True

	
		# logfile name
		self.log=log
		# email address
		self.email=email
		# send intermediate notifications
		self.verbose=verbose
		# email command
		self.mailcmd=mailcmd

		# keep an instance of the system parameter class for later use
		self.sp=system_parameter.system_parameter()
		# keep an instance of isolated database for later use
		self.idb=database.isolated_database()
		self.idb.download()
		# keep an instance of heterostructure database for later use
		self.hdb=database.heterostructure_database()
		self.hdb.download()

		# get mpicmd
		self.mpicmd=get_worker().mpicmd
		# set top output folder to current working directory by default
		if output==None:
			if self.isolated:
				self.output=self.idb.get_output(self.material, self.N, self.ni)
			else:
				self.output=self.hdb.get_output(self.material, self.N, self.M, self.ni, self.ncr, self.dW)
		else:
			self.output=output
	
		# set top input search folder to output folder by default
		if input==None:
			self.input=self.output
		else:
			self.input=input
		# host
		self.host=database.get_host()

	# write to log file
	def write_log(self, message):
		f=open("%s.log" % self.log, 'a')
		f.write(message)
		f.close()

	# write to error log file
	def write_error_log(self, message):
		f=open("%s.err" % self.log, 'a')
		f.write(message)
		f.close()

	# remove log files if they exist
	def log_prepare(self):
		if os.path.exists("%s.log" % self.log):
			os.remove("%s.log" % self.log)
		if os.path.exists("%s.err" % self.log):
			os.remove("%s.err" % self.log)

	# check output folder if results are already there
	def run_exists(self, runcmd, output, check_database=True):
		if os.path.exists("%s/parameter.cfg" % output):
			sp1=system_parameter.system_parameter()
			sp1.read_file("%s/parameter.cfg" % output)
			sp2=system_parameter.system_parameter()
			sp2.read_cmd(runcmd)
			results_exists=os.path.exists("%s/results" % output)
			return system_equal(sp1, sp2) and results_exists
		elif check_database:
			sp=system_parameter.system_parameter()
			sp.read_cmd(runcmd)
			return database_exists(sp)
		else:
			return False
					
	def run_isolated(self, t, special_input=None):
		# run name
		runname="%s, N=%i, ni=%f, T=%f" % (self.material, self.N, self.ni, t)
		self.write_log("##############################################\n")
		self.write_log("### euorun: %s\n" % runname)
		self.write_log("##############################################\n")
		# run command
		runcmd=self.mpicmd + " -np %i " % self.np
		runcmd+=self.sp.get_runcmd_isolated(self.material, self.N, self.ni, t)
		# add additional parameter
		runcmd+=self.iteration_parameter
		# add output
		runoutput=self.output + self.idb.get_temp_output(t)
		runcmd+=" -o %s/" % runoutput
		# add special input folder
		if special_input!=None:
			runcmd+=" -i %s" % (special_input)
		# search self.input folder for suitable input folders and add it
		else:
			if self.inputFlag:
				runcmd=database.add_input(runcmd, download_path=self.output+"/download/", path=self.output)

		# run job
		if not self.run_exists(runcmd, runoutput, check_database=False):
			j=job.job(runname, self.log, self.email, [runcmd], logappend=True, verbose=self.verbose, mailcmd=self.mailcmd)
			j.run()

		# update database
		if self.updatedbFlag:
			self.write_log("* Update isolated database\n")
			updatecmd="isolated_remote.py --no_archive %s" % runoutput
			#subprocess.call(updatecmd, shell=True)
			j=job.job("update remote isolated database", self.log, self.email, [updatecmd], logappend=True, verbose=False, mailcmd=self.mailcmd)
			j.run()
		self.write_log("\n")


	def run_hetero(self, t, special_input=None):
		# run name
		runname="%s, N=%i, M=%i, ni=%f, ncr=%f, dW=%f, T=%f" % (self.material, self.N, self.M, self.ni, self.ncr, self.dW, t)
		self.write_log("##############################################\n")
		self.write_log("### euorun: %s\n" % runname)
		self.write_log("##############################################\n")
		# run command
		runcmd=self.mpicmd + " -np %i " % self.np
		runcmd+=self.sp.get_runcmd_hetero(self.material, self.N, self.M, self.ni, self.ncr, self.dW, t)
		# add additional parameter
		runcmd+=self.iteration_parameter
		# add output
		runoutput=self.output + self.hdb.get_temp_output(t)
		runcmd+=" -o %s/" % runoutput
		# add special input folder
		if special_input!=None:
			runcmd+=" -i %s" % (special_input)
		# search self.input folder for suitable input folders and add it
		else:
			if self.inputFlag:
				runcmd=database.add_input(runcmd, download_path=self.output+"/download/", path=self.output)

		#print "check", runcmd
		# check if run not already exist 
		if not self.run_exists(runcmd, runoutput, check_database=False):
			if self.isoDeltaFlag:
				######################################################################################
				####### add energy shift values for the isolated system constituents #################
				######################################################################################
				# check is values of energy shifts in the isolated system already exist
				#print "check isodeltas:",  database.get_isodelta_info(runcmd)
				self.write_log("* Check isolated deltas: %s, %s, %s, %s, %s, %s, %s, %s\n"  % (database.get_isodelta_info(runcmd)[:-1]))
				(exists_left, material_left, N_left, nc_left, exists_right, material_right, N_right, nc_right, temp)=database.get_isodelta_info(runcmd)
				if t!=temp:
					print "Error: run_hetero: Temperatures do not match. This should not happen. Break." 
					exit(1)

				# if not start isolated runs
				if not exists_left or not exists_right:
					if not exists_left:
						# get name
						runname_left="%s, N=%i, ni=%f, T=%f" % (material_left, N_left, nc_left, t)
						self.write_log("* Isolated run necessary: %s\n" % runname_left)
						# get run command
						runcmd_left=self.mpicmd + " -np %i " % self.np
						runcmd_left+=self.sp.get_runcmd_isolated(material_left, N_left, nc_left, t)
						# add default additional parameter for iteration 
						runcmd_left+=self.get_default_iteration_parameter(material_left)
						# add output
						output_left=self.idb.get_output(material_left, N_left, nc_left)
						runoutput_left=output_left + self.idb.get_temp_output(t)
						runcmd_left+=" -o " + runoutput_left
						# add input if existent
						runcmd_left=database.add_input(runcmd_left, download_path=output_left+"/download/", path=output_left)
						# run left system
						if not self.run_exists(runcmd_left, runoutput_left):
							j=job.job(runname_left, self.log, self.email, [runcmd_left], logappend=True, verbose=self.verbose, mailcmd=self.mailcmd)
							j.run()
						# update database
						self.write_log("* Update isolated database\n")
						#print "update isolated db"
						updatecmd_left="isolated_remote.py --no_archive  %s" % output_left
						#subprocess.call(updatecmd_left, shell=True)
						j=job.job("update remote isolated database" , self.log, self.email, [updatecmd_left], logappend=True, verbose=False, mailcmd=self.mailcmd)
						j.run()
		
					if not exists_right:
						# get name
						runname_right="%s, N=%i, ni=%f, T=%f" % (material_right, N_right, nc_right, t)
						self.write_log("* Isolated run necessary: %s\n" % runname_right)
						# get run command
						runcmd_right=self.mpicmd + " -np %i " % self.np
						runcmd_right+=self.sp.get_runcmd_isolated(material_right, N_right, nc_right, t)
						# add default additional parameter for iteration 
						runcmd_right+=self.get_default_iteration_parameter(material_right)
						# add output
						output_right=self.idb.get_output(material_right, N_right, nc_right)
						runoutput_right=output_right + self.idb.get_temp_output(t)
						runcmd_right+=" -o " + runoutput_right
						# add input if existent
						runcmd_right=database.add_input(runcmd_right, download_path=output_right+"/download/", path=output_right)
						# run right system
						if not self.run_exists(runcmd_right, runoutput_right):
							j=job.job(runname_right, self.log, self.email, [runcmd_right], logappend=True, verbose=self.verbose, mailcmd=self.mailcmd)
							j.run()
						# update database
						#print "update isolated db"
						self.write_log("* Update isolated database\n")
						updatecmd_right="isolated_remote.py --no_archive  %s" % output_right
						#subprocess.call(updatecmd_right, shell=True)
						j=job.job("update remote isolated database" , self.log, self.email, [updatecmd_right], logappend=True, verbose=False, mailcmd=self.mailcmd)
						j.run()
		
		
				# add isodeltas
				runcmd=database.add_isodeltas(runcmd)

			# run heterostructure job
			#print "run", runcmd
			j=job.job(runname, self.log, self.email, [runcmd], logappend=True, verbose=self.verbose, mailcmd=self.mailcmd)
			j.run()

			# update database
			if self.updatedbFlag:
				self.write_log("* Update heterostructure database\n")
				#print "update heterostructure db"
				updatecmd="heterostructure_remote.py %s" % runoutput
				#subprocess.call(updatecmd, shell=True)
				j=job.job("update remote heterostructure database", self.log, self.email, [updatecmd], logappend=True, verbose=False, mailcmd=self.mailcmd)
				j.run()

		self.write_log("\n")

	def run(self, t, special_input=None):
		if self.isolated:
			self.run_isolated(t, special_input)
		else:
			self.run_hetero(t, special_input)

	# temperature sweep
	def tempsweep(self, temperatures):
		self.log_prepare()

		first=True
		for t in temperatures: 
			if first:
				self.run(t, special_input=self.initial_input) 
			else:
				self.run(t) 
			first=False

		# send finishing notification
		runname="%s, N=%i, ni=%f, T=" % (self.material, self.N, self.ni)
		if not self.isolated:
			runname="%s, N=%i, M=%i, ni=%f, ncr=%f, dW=%f, T=" % (self.material, self.N, self.M, self.ni, self.ncr, self.dW)
		for t in temperatures:
			runname +=" %f," % t
			
		cmd="echo "" | %s 'Temperature sweep finished: %s on %s.' %s" % (self.mailcmd, runname, self.host, self.email)
		subprocess.call(cmd, shell=True)

def main():
	erun=euorun(64, 'Metal', N=2, ni=0.5)
	erun.tempsweep((21,22))

if __name__=="__main__":
	main()
