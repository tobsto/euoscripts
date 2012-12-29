#!/usr/bin/python

import itertools as it
import subprocess
import sys
import os
import job
import system_parameter
import database

def system_equal(sp1, sp2):
	# conditions
	conditions=[]
	conditions.append(sp1.get_system().name==sp2.get_system().name)
	conditions.append(sp1.N==sp2.N)
	conditions.append(sp1.ni==sp2.ni)
	if sp1.get_system().constituents!=(None,None):
		conditions.append(sp1.N0==sp2.N0)
		conditions.append(sp1.ncr==sp2.ncr)
		conditions.append(sp1.Delta_W==sp2.Delta_w)
	return all(conditions)

class euorun:
	def __init__(self, material, N=5, M=None, ni=0.01, ncr=None, dW=None, output=None, input=None, initial_input=None, additional_parameter='', log='run', verbose=True, email='stollenwerk@th.physik.uni-bonn.de', mailcmd='mailx -s'):
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
		# additional parameter (like max2, wr1, etc.)
		self.additional_parameter=additional_parameter
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
	def run_exists(self, runcmd, output):
		if os.path.exists("%s/parameter.cfg" % output):
			sp1=system_parameter.system_parameter()
			sp1.read_file("%s/parameter.cfg" % output)
			sp2=system_parameter.system_parameter()
			sp2.read_cmd(runcmd)
			results_exists=os.path.exists("%s/results" % output)
			return system_equal(sp1, sp2) and results_exists
		else:
			return False
					
	def run_isolated(self, t, special_input=None):
		# run name
		runname="%s, N=%i, ni=%f, T=%f" % (self.material, self.N, self.ni, t)
		self.write_log("euorun: %s\n\n" % runname)
		# run command
		runcmd=self.sp.get_runcmd_isolated(self.material, self.N, self.ni, t)
		# add additional parameter
		runcmd+=self.additional_parameter
		# add temperature
		runcmd+=" -t %e" % t
		# add output
		runoutput=self.output + self.idb.get_temp_output(t)
		runcmd+=" -o %s/" % runoutput
		# add special input folder
		if special_input!=None:
			runcmd+=" -i %s" % (special_input)
		# search self.input folder for suitable input folders and add it
		else:
			runcmd=database.add_input(runcmd, download_path=self.input+"/download/", path=self.input)

		# run job
		if not run_exists(runcmd, runoutput):
			j=job.job(runname, self.log, self.email, [runcmd], logappend=True, verbose=self.verbose, mailcmd=self.mailcmd)
			j.run()

	def run_hetero(self, t, special_input=None):
		# run name
		runname="%s, N=%i, M=%i, ni=%f, ncr=%f, dW=%f, T=%f" % (self.material, self.N, self.M, self.ni, self.ncr, self.dW, t)
		self.write_log("euorun: %s\n\n" % runname)
		# run command
		runcmd=self.sp.get_runcmd_hetero(self.material, self.N, self.M, self.ni, self.ncr, self.dW, t)
		# add additional parameter
		runcmd+=self.additional_parameter
		# add temperature
		runcmd+=" -t %e" % t
		# add output
		runoutput=self.output + self.hdb.get_temp_output(t)
		runcmd+=" -o %s/" % runoutput
		# add special input folder
		if special_input!=None:
			runcmd+=" -i %s" % (special_input)
		# search self.input folder for suitable input folders and add it
		else:
			runcmd=database.add_input(runcmd, download_path=self.output+"/download/", path=self.input)

		######################################################################################
		####### add energy shift values for the isolated system constituents #################
		######################################################################################
		# check is values of energy shifts in the isolated system already exist
		(exists_left, material_left, N_left, nc_left, exists_right, material_right, N_right, nc_right, temp)=database.get_isodelta_info(runcmd)
		if t!=temp:
			print "Error: run_hetero: Temperatures do not match. This should not happen. Break." 
			exit(1)

		# if not start isolated runs
		if not exists_left or not exists_right:
			if not exists_left:
				# get name
				runname_left="%s, N=%i, ni=%f, T=%f" % (material_left, N_left, nc_left, t)
				self.write_log("euorun: get isodeltas: %s\n\n" % runname_left)
				# get run command
				runcmd_left=self.sp.get_runcmd_isolated(material_left, N_left, nc_left, t)
				# add output
				output_left=self.idb.get_output(material_left, N_left, nc_left) + self.idb.get_temp_output(t)
				runcmd_left+=" -o " + output_left
				# add input if existent
				runcmd_left=database.add_input(runcmd_left, download_path=output_left+"/download/", path=output_left)
				# run left system
				if not run_exists(runcmd_left, output_left):
					j=job.job(runname_left, self.log, self.email, [runcmd_left], logappend=True, verbose=self.verbose, proceed=False, mailcmd=self.mailcmd)
					j.run()
				# update database
				updatecmd_left="isodelta_remote.py %s" % output_left
				j=job.job("Update db: " + runname_left, self.log, self.email, [updatecmd_left], logappend=True, verbose=self.verbose, proceed=False, mailcmd=self.mailcmd)
				j.run()

			if not exists_right:
				# get name
				runname_right="%s, N=%i, ni=%f, T=%f" % (material_right, N_right, nc_right, t)
				self.write_log("euorun: get isodeltas: %s\n\n" % runname_right)
				# get run command
				runcmd_right=self.sp.get_runcmd_isolated(material_right, N_right, nc_right, t)
				# add output
				output_right=self.idb.get_output(material_right, N_right, nc_right)  + sefl.idb.get_temp_output(t)
				runcmd_right+=" -o " + output_right
				# add input if existent
				runcmd_right=database.add_input(runcmd_right, download_path=output_right+"/download/", path=output_right)
				# run right system
				if not run_exists(runcmd_right, output_right):
					j=job.job(runname_right, self.log, self.email, [runcmd_right], logappend=True, verbose=self.verbose, mailcmd=self.mailcmd)
					j.run()
				# update database
				updatecmd_right="isodelta_remote.py %s" % output_right
				j=job.job("Update db: " + runname_right, self.log, self.email, [updatecmd_right], logappend=True, verbose=self.verbose, proceed=False, mailcmd=self.mailcmd)
				j.run()


		# add isodeltas
		runcmd=database.add_isodeltas(runcmd)
		# run heterostructure job
		if not run_exists(runcmd, runoutput):
			j=job.job(runname, self.log, self.email, [runcmd], logappend=True, verbose=self.verbose, mailcmd=self.mailcmd)
			j.run()

	def run(self, t, special_input):
		if self.isolated:
			self.run_isolated(t, special_input)
		else:
			self.run_hetero(t, special_input)

	# temperature sweep
	def tempsweep(self, temperatures):

		first=True
		for t in temperatures: 
			if first:
				self.run(t, special_input=self.initial_input) 
			else:
				self.run(t) 
			first=False

		# send finishing notification
		runname="%s, N=%i, M=%i, ni=%f, ncr=%f, dW=%f, T=" % (self.material, self.N, self.M, self.ni, self.ncr, self.dW)
		if self.isolated:
			runname="%s, N=%i, ni=%f, T=" % (self.material, self.N, self.ni)
		for t in temperatures:
			runname +=" %f," % t
			
		cmd="echo "" | %s 'Temperature sweep finished: %s on %s.' %s" % (self.mailcmd, runname, self.host, self.email)
		subprocess.call(cmd, shell=True)

def main():
	material='Metal'
	N=2
	ni=1.0
	erun=euorun('Metal', N=2, ni=1.0)
	erun.tempsweep((20,40,60))

if __name__=="__main__":
	main()
