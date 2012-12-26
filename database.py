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

##############################################################################
##############################################################################
##### Database for class
##############################################################################
##############################################################################
class database:
	def __init__(self, special_data_names):
		self.names=['material', 'N', 'nc', 'T']
		for sd_name in special_data_names:
			self.names.append(sd_name)
		self.names.append('origin')
		self.special_data_names=special_data_names
		self.constants={}
		self.data=[]

	# write database to file
	def write(self, filename):
		f=open(filename, 'w')
		f.write('{:<30}\tN\tnc\t\t\tT\t\t\t'.format('#mat'))
		for sd_name in self.special_data_names:
			f.write('%s\t\t\t' % sd_name)
		f.write('origin\n')

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
			dataline=[material_val, N_val, nc_val, T_val]
			for sd in d[4:-1]:
				dataline.append(float(sd))
			origin_val=d[-1]
			dataline.append(origin_val)
			self.data.append(tuple(dataline))

	# read in database from remote file
	def download(self, remotepath=None):
		if remotepath==None:
			remotepath=self.remotepath
		cmd='scp %s database.db.temp' % remotepath
		try:
			proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
			proc.wait()
			self.read('database.db.temp')
			os.remove('database.db.temp')
		except:
			print 'Error: Failed to retrieve remote database: %s' % remotepath
			print 'Break.'
			exit(1)
		
	# overwrite database on remote host
	def upload(self, remotepath=None):
		if remotepath==None:
			remotepath=self.remotepath
		self.write('database.db.temp')
		cmd='scp database.db.temp %s' % remotepath
		try:
			proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
			proc.wait()
			os.remove('database.db.temp')
		except:
			print 'Error: Failed to write onto remote database: %s' % remotepath
			print 'Break.'
			exit(1)
		
	# check if special dataset exists in database
	def exists(self, material, N, nc, T):
		# constants
		match=False
		for k,v in self.constants.items():
			argument_value=eval('%s' % k)
			if argument_value==v:
				match=True
			else:
				match=False
				break
		if match:
			return True

		# check database
		for d in self.data:
			if material==d[0] and N==d[1] and nc==d[2] and T==d[3]:
				return True
		return False

	# extract Delta
	def getSpecialValue(self, key, material, N, nc, T):
		index=0
		found=False
		for sd_name in self.special_data_names:	
			if key==sd_name:
				found=True
				break	
			index=index+1
		if not found:
			print "Error: Unable to find data: '%s' in database." % key
			print "Break."
			exit(1)
		
		# return constant
		match=False
		for k,v in self.constants.items()[:-1]:
			argument_value=eval('%s' % k)
			if argument_value==v:
				match=True
			else:
				match=False
				break
		if match:
			return self.constants[key]	

		# return database value
		for d in self.data:
			if material==d[0] and N==d[1] and nc==d[2] and T==d[3]:
				return d[4+index]

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
					(material, N, nc, T, path, special_data)=self.extractValues(folder)
					if not self.exists(material, N, nc, T):
						message="Adding dataset: %s, N=%03i, nc=%06.4f, T=%05.1f" %(material, N, nc, T)
						for key,value in special_data.items():
							message+=", %s=%e" % (key,value)
						message+=", Source=%s" % path
						print message
						dataline=[material, N, nc, T]
						for key,value in special_data.items():
							dataline.append(value)
						dataline.append(path)
						self.data.append(tuple(dataline))

		# sort by 1st column i.e. N 
		self.data=sorted(self.data, key = lambda element : element[0])

##############################################################################
##############################################################################
##### Database for energy shifts in isolated subsystems EuO and substrate ####
##############################################################################
##############################################################################
class isolated_database(database):
	def __init__(self):
		special_data_names=('Delta',)
		database.__init__(self, special_data_names)
		self.remotepath='stollenw@heisenberg.physik.uni-bonn.de:/home/stollenw/projects/euo/database/isolated.db'
		self.constants={'material':'Metal', 'nc':1.0, 'Delta':-1.0}
	def extractValues (sefl,resultsFolder):
		# get system parameter
		parafilename="%s/parameter.cfg" % resultsFolder
		sp=system_parameter()
		sp.read_file(parafilename)
		system=sp.get_system()
		if (system==None):
			print "ExtractValues: Unable to find matching system type. Break."
			exit(1)
			
		# get Delta value
		mufilename="%s/results/mu.dat" % resultsFolder
		mu=float(extractResultValue(mufilename))
		Delta=-mu
		special_data={"Delta": Delta,}
		return (system.name, sp.N, sp.concentration, sp.temperature, os.path.abspath(resultsFolder), special_data)

##############################################################################
##### Get run commands necessary to get values of isodeltas
##############################################################################
def get_isodeltas(cmd, dbpath=None):
	# read database
	db=isolated_database()
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
			left_exists=db.exists(system.constituents[0], N_left, sp.concentration, sp.temparature)
			right_exists=db.exists(system.constituents[1], N_right, sp.ncr, sp.temparature)
			isodelta_cmd=''
			if not left_exists:
				isodelta_cmd+=sp.get_runcmd(system.constituents[0]) + "; "
			if not right_exists:
				isodelta_cmd+=sp.get_runcmd(system.constituents[1]) + "; "
		else:
			print "Error: Isodeltas exist: Isolated System: %s" % cmd
			print "Break."
			exit(1)
	else:
		print "No know system matches the run command: %s" % cmd
		print "Break."
		exit(1)
##############################################################################
##### Add energy shifts of isolated materials for known heterostruture runs
##############################################################################
def add_isodeltas(cmd, dbpath=None):
	# read database
	db=isolated_database()
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
			Delta_l=db.getSpecialValue('Delta', system.constituents[0], N_left, sp.concentration, sp.temparature)
			cmd+=" --Delta_l0 %0.15e" % Delta_l
			Delta_r=db.getSpecialValue('Delta', system.constituents[1], N_right, sp.ncr, sp.temparature)
			cmd+=" --Delta_r0 %0.15e" % Delta_r
	else:
		print "No know system matches the run command: %s" % cmd
		print "Break."
		exit(1)
##############################################################################
##### Check if energy shifts of isolated materials for known heterostruture already exist
##############################################################################
def isodeltas_exist(cmd, dbpath=None):
	# read database
	db=isolated_database()
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
			left_exists=db.exists(system.constituents[0], N_left, sp.concentration, sp.temparature)
			right_exists=db.exists(system.constituents[1], N_right, sp.ncr, sp.temparature)
			if left_exists and right_exists:
				return True
			else:
				return False
		else:
			print "Error: Isodeltas exist: Isolated System: %s" % cmd
			print "Break."
			exit(1)
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
	if sp.input==None:
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
					resultFolders.append((folder, float(extractParameter("%s/parameter.cfg" % folder, parameter))))
	
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
			
##############################################################################
##############################################################################
##### Database for heterostructre runs ####
##############################################################################
##############################################################################
class heterostructure_database(database):
	def __init__(self):
		special_data_names=('avmag',)
		database.__init__(self, special_data_names)
		self.remotepath='stollenw@heisenberg.physik.uni-bonn.de:/home/stollenw/projects/euo/database/hetero.db'
	def extractValues (sefl,resultsFolder):
		# get system parameter
		parafilename="%s/parameter.cfg" % resultsFolder
		sp=system_parameter()
		sp.read_file(parafilename)
		system=sp.get_system()
		if (system==None):
			print "ExtractValues: Unable to find matching system type. Break."
			exit(1)
			
		# get Delta value
		avmagfilename="%s/results/avmag.dat" % resultsFolder
		avmag=float(extractResultValue(avmagfilename))
		special_data={"avmag": avmag,}
		return (system.name, sp.N, sp.concentration, sp.temperature, os.path.abspath(resultsFolder), special_data)

#
def main():
	idb=isolated_database()
	idb.download()
	print idb.getSpecialValue('Delta', 'Metal', 5, 1.0, 88.8) 
	print idb.getSpecialValue('Delta', 'EuGdO', 5, 0.01, 20) 
	print idb.exists('EuGdO', 5, 0.01, 20) 
	print idb.exists('EuGdO', 5, 0.01, 1.1111111) 
	print idb.getSpecialValue('Delta', 'EuGdO', 5, 0.01, 1.1111111) 

if __name__=="__main__":
	main()
