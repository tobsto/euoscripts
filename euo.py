#!/usr/bin/python

import os
import subprocess
from system_parameter import *

##############################################################################
##############################################################################
##### Various functions ######################################################
##############################################################################
##############################################################################

# get hostname
def get_host():
	proc = subprocess.Popen('hostname', stdout=subprocess.PIPE)
	host = proc.stdout.read().rstrip('\n')
	return host

def extractResultValue (filename):
	f=open(filename, 'r')
	l=f.readline()
	f.close()
	return l

def isResults (resultsFolder):
	parafilename="%s/parameter.cfg" % resultsFolder
	mufilename="%s/results/mu.dat" % resultsFolder
	if os.path.exists(parafilename) and os.path.exists(mufilename):
		return True
	else:
		return False


def extractIsodeltaParameter (resultsFolder):
	# get system parameter
	parafilename="%s/parameter.cfg" % resultsFolder
	sp=system_parameter()
	sp.read_file(parafilename)
	system=sp.get_system()
	if (system==None):
		print "euo.py: Unable to find matching system type. Break."
		exit(1)
		
	# get Delta value
	mufilename="%s/results/mu.dat" % resultsFolder
	mu=float(extractResultValue(mufilename))
	Delta=-mu

	return (system.name, sp.N, sp.concentration, sp.temperature, Delta, os.path.abspath(resultsFolder))

##############################################################################
##############################################################################
##### Database for energy shifts in isolated subsystems EuO and substrate ####
##############################################################################
##############################################################################
# convert data values to strings
def tostring(val):
	if type(val).__name__=='str':
		return val
	elif type(val).__name__=='int':
		return "%d" % val
	elif type(val).__name__=='float':
		return "%0.15e" % val
	else:
		print "Error: Sting conversion: Unknown type. Break"
		exit(1)

class isodeltabase:
	def __init__(self):
		self.names=('material', 'N', 'nc', 'T', 'Delta', 'origin')
		self.data=[]

	# write database to file
	def write(self, filename):
		f=open(filename, 'w')
		f.write('{:<30}\tN\tnc\t\t\tT\t\t\tDelta\t\t\torigin\n'.format('#mat'))
		for d in self.data:
			f.write('{:<30}'.format(d[0]))
			f.write('\t')
			for val in d[1:]:
				f.write(tostring(val))
				f.write('\t')
			f.write('\n')

	# fill database 
	def set(self, d):
		self.data=d
		self.names=('material', 'N', 'nc', 'T', 'Delta', 'origin')

	# read database from file
	def read(self, filename):
		f=open(filename, 'r')
		lines=f.readlines()
		f.close()

		self.data=[]
		for l in lines[1:]:
			d=l.split()
			material_val=d[0]
			N_val=int(d[1])
			nc_val=float(d[2])
			T_val=float(d[3])
			Delta_val=float(d[4])
			origin_val=d[5]
			self.data.append((material_val, N_val, nc_val, T_val, Delta_val, origin_val))

	# read in database from remote file
	def download(self, remotepath='stollenw@heisenberg.physik.uni-bonn.de:/home/stollenw/projects/euo/database/isodelta.db'):
		cmd='scp %s isodelta.db' % remotepath
		try:
			proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
			proc.wait()
			self.read('isodelta.db')
			os.remove('isodelta.db')
		except:
			print 'Error: Failed to retrieve remote isodelta database: %s' % remotepath
			print 'Break.'
			exit(1)
		
		
	# check if special dataset exists in database
	def exists(self, material, N, nc, T):
		for d in self.data:
			if material==d[0] and N==d[1] and nc==d[2] and T==d[3]:
				return True
		return False

	# extract Delta
	def getDelta(self, material, N, nc, T):
		for d in self.data:
			if material==d[0] and N==d[1] and nc==d[2] and T==d[3]:
				return d[4]

		print "Error: Unable to find dataset in database:"
		print "material=%s" % material
		print "N=%s" % N
		print "nc=%s" % nc 
		print "T=%s" % T
		print "Break."
		exit(1)
	
	# fill database by extracting results form a special folder
	def fill(self, topResultsFolders, overwrite=True):
		if overwrite:
			self.data=[]
		for topfolder in topResultsFolders:
			for d in os.listdir(topfolder):
				folder=os.path.join(topfolder, d)
				if os.path.isdir(folder) and isResults(folder):
					(material, N, nc, T, Delta, path)=extractIsodeltaParameter(folder)
					if not self.exists(material, N, nc, T):
						print "Adding dataset: %s, N=%03i, nc=%06.4f, T=%05.1f, Delta=%01.9f, Source=%s" %(material, N, nc, T, Delta, path)
						self.data.append((material, N, nc, T, Delta, path))

		# sort by 1st column i.e. N 
		self.data=sorted(self.data, key = lambda element : element[0])

##############################################################################
##### Add energy shifts of isolated materials for known heterostruture runs
##############################################################################
def add_isodeltas(cmd, dbpath=None):
	# read database
	db=isodeltabase()
	if dbpath==None:
		db.download()
	else:
		db.read(dbpath)
	# get system parameter
	sp=system_parameter()	
	sp.read_cmd(cmd)
	system=sp.get_system()
	# check if system type is known
	if system!=None:
		# check if system is a heterostructure
		if system.constituents!=(None, None):
			N_left=sp.N
			# the isolated system is mirror symmetric. For example, a heterostructure with N0=9
			# corresponds to an isolated mirror symmetric system with N=5=9+1/2
			N_right=int(sp.N0+1/2.0)
			# if the heterostructure is not mirror symmetric the left system with N=5 corresponds to a
			# mirror symmetric system with N=3=5+1/2
			if not sp.mirror:	
				N_left=int(sp.N+1/2.0)
			Delta_l=db.getDelta(system.constituents[0], N_left, sp.concentration, sp.temparature)
			cmd+=" --Delta_l0 %0.15e" % Delta_l
			Delta_r=db.getDelta(system.constituents[1], N_right, sp.ncr, sp.temparature)
			cmd+=" --Delta_r0 %0.15e" % Delta_r
	else:
		print "No know system matches the run command: %s" % cmd
		print "Break."
		exit(1)

#######################################################################
##### Add suitable input to euo run command if available ##############
#######################################################################
# Add input path to EuO run command 'runcmd'. Hereby the output path and the 
# temperature in 'runcmd' is extracted. It's parent directory is then searched 
# for folder containing results with smaller temperatures. The full run command
# with input options is then returned.
# parameter: to make this generic temperature can be any parameter,
# small: seach for smaller values of the parameter (alternative greater values)
# limit: minimal/maximal value for the parameter
def add_input (runcmd, parameter, smaller=True, limit=0.0,  path=None):
	# get system parameter
	sp=system_parameter()
	sp.read_cmd(runcmd)
	# get current temperature
	T=eval('sp.%s' % parameter)
	# check if there is already in input folder given, if this is the case, skip
	if sp.input!=None:
		# extract output folder from run command if path variable is not given
		if path==None:
			path=os.path.dirname(os.path.abspath(sp.output))
		
		inputOptions=''
		# Search search 'resultsFolder' for sub folders containing results with
		# smaller temperatures thant 'T' 
		resultFolders=[]
		if os.path.exists(path):
			for d in os.listdir(path):
				folder=os.path.join(path, d)
				if os.path.isdir(folder) and isResults(folder):
					resultFolders.append((folder, extractParameter("%s/parameter.cfg" % folder, parameter)))
	
			# find a folder with lower temperature than T
			tmax=limit
			if smaller:
				for (f,t) in resultFolders:
					if t>tmax and t<=T:
						tmax=t
						inputFolder=f
			
				if tmax>limit:
					runcmd+=" -i " + inputFolder + "/"
			else:
				for (f,t) in resultFolders:
					if t<tmax and t>=T:
						tmax=t
						inputFolder=f
			
				if tmax<limit:
					runcmd+=" -i " + inputFolder + "/"

	return runcmd
			

#db=isodeltabase()
#db.fill(['../../runs/runs_version-a177549/pure_ncr0.50/n3/','../../runs/runs_version-a177549/n5/'])
#db.write('../../database/isodelta.db')
#r=run('euo.out -n 5 -m 5 --n_cr 0.5 -o ../../runs/runs_version-a177549/n5/output_t050/ -t 60')
#r.add_input('../../runs/runs_version-a177549/n5_m2_ncr0.10/')
#r.add_isodeltas()
#print r.cmd

########################################################################################
# Database containing all results
########################################################################################

class resultbase:
	def __init__(self):
		self.names=('material', 'N', 'nc', 'T', 'Delta', 'origin')
		self.data=[]

	# write database to file
	def write(self, filename):
		f=open(filename, 'w')
		f.write('{:<30}\tN\tnc\t\t\tT\t\t\tDelta\t\t\torigin\n'.format('#mat'))
		for d in self.data:
			f.write('{:<30}'.format(d[0]))
			f.write('\t')
			for val in d[1:]:
				f.write(tostring(val))
				f.write('\t')
			f.write('\n')

	# fill database 
	def set(self, d):
		self.data=d
		self.names=('material', 'N', 'nc', 'T', 'Delta', 'origin')

	# read database from file
	def read(self, filename):
		f=open(filename, 'r')
		lines=f.readlines()
		f.close()

		self.data=[]
		for l in lines[1:]:
			d=l.split()
			material_val=d[0]
			N_val=int(d[1])
			nc_val=float(d[2])
			T_val=float(d[3])
			Delta_val=float(d[4])
			origin_val=d[5]
			self.data.append((material_val, N_val, nc_val, T_val, Delta_val, origin_val))

	# read in database from remote file
	def download(self, remotepath='stollenw@heisenberg.physik.uni-bonn.de:/home/stollenw/projects/euo/database/isodelta.db'):
		cmd='scp %s isodelta.db' % remotepath
		try:
			proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
			proc.wait()
			self.read('isodelta.db')
			os.remove('isodelta.db')
		except:
			print 'Error: Failed to retrieve remote isodelta database: %s' % remotepath
			print 'Break.'
			exit(1)
		
		
	# check if special dataset exists in database
	def exists(self, material, N, nc, T):
		for d in self.data:
			if material==d[0] and N==d[1] and nc==d[2] and T==d[3]:
				return True
		return False

	# extract Delta
	def getDelta(self, material, N, nc, T):
		for d in self.data:
			if material==d[0] and N==d[1] and nc==d[2] and T==d[3]:
				return d[4]

		print "Error: Unable to find dataset in database:"
		print "material=%s" % material
		print "N=%s" % N
		print "nc=%s" % nc 
		print "T=%s" % T
		print "Break."
		exit(1)
	
	# fill database by extracting results form a special folder
	def fill(self, topResultsFolders, overwrite=True):
		if overwrite:
			self.data=[]
		for topfolder in topResultsFolders:
			for d in os.listdir(topfolder):
				folder=os.path.join(topfolder, d)
				if os.path.isdir(folder) and isResults(folder):
					(material, N, nc, T, Delta, path)=extractIsodeltaParameter(folder)
					if not self.exists(material, N, nc, T):
						print "Adding dataset: %s, N=%03i, nc=%06.4f, T=%05.1f, Delta=%01.9f, Source=%s" %(material, N, nc, T, Delta, path)
						self.data.append((material, N, nc, T, Delta, path))

		# sort by 1st column i.e. N 
		self.data=sorted(self.data, key = lambda element : element[0])


