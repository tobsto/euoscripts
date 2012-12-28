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

###############################################
# Database for isolated Deltas
###############################################

class isolated_database:
	def __init__(self):
		self.names=('material', 'N', 'nc', 'T', 'Delta', 'origin')
		self.data=[]

	def extractData (self, resultsFolder):
		# get system parameter
		parafilename="%s/parameter.cfg" % resultsFolder
		sp=system_parameter()
		sp.read_file(parafilename)
		system=sp.get_system()
		if (system==None):
			print "ExtractValues: Unable to find matching system type. Break."
			exit(1)
		if (system.constituents!=(None,None)):
			print "ExtractValues: System in %s is not isolated. Break." % resultsFolder
			exit(1)
			
		# get Delta value
		mufilename="%s/results/mu.dat" % resultsFolder
		mu=float(extractResultValue(mufilename))
		Delta=-mu
		return (system.name, sp.N, sp.concentration, sp.temperature, Delta, os.path.abspath(resultsFolder))


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
			material=d[0]
			N=int(d[1])
			nc=float(d[2])
			T=float(d[3])
			Delta=float(d[4])
			origin=d[5]
			self.data.append((material, N, nc, T, Delta, origin))

	# read in database from remote file
	def download(self, remotepath='stollenw@heisenberg.physik.uni-bonn.de:/home/stollenw/projects/euo/database/isolated.db'):
		cmd='scp %s isolated.db.temp' % remotepath
		try:
			proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
			proc.wait()
			self.read('isolated.db.temp')
			os.remove('isolated.db.temp')
		except:
			print 'Error: Failed to retrieve remote isolated database: %s' % remotepath
			print 'Break.'
			exit(1)
		
	# overwrite database on remote host
	def upload(self, remotepath=None):
		if remotepath==None:
			remotepath=self.remotepath
		self.write('isolated.db.temp')
		cmd='scp isolated.db.temp %s' % remotepath
		try:
			proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
			proc.wait()
			os.remove('isolated.db.temp')
		except:
			print 'Error: Failed to write onto remote isolated database: %s' % remotepath
			print 'Break.'
			exit(1)
			
	# check if special dataset exists in database
	def exists(self, material, N, nc, T):
		# Special case for Metals with half filling. Delta is always equal to 1.0 
		if material=='Metal' and nc==1.0:
			return True
		for d in self.data:
			if material==d[0] and N==d[1] and nc==d[2] and T==d[3]:
				return True
		return False

	# get Delta
	def getDelta(self, material, N, nc, T):
		# Special case for Metals with half filling. Delta is always equal to 1.0 
		if material=='Metal' and nc==1.0:
			return -1.0
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
			print topfolder
			for d in os.listdir(topfolder):
				folder=os.path.join(topfolder, d)
				if os.path.isdir(folder) and isResults(folder):
					(material, N, nc, T, Delta, path)=self.extractData(folder)
					if not self.exists(material, N, nc, T):
						print "Adding dataset: %s, N=%03i, nc=%06.4f, T=%05.1f, Delta=%01.9f, Source=%s" %(material, N, nc, T, Delta, path)
						self.data.append((material, N, nc, T, Delta, path))

		# sort by 1st column i.e. N 
		self.data=sorted(self.data, key = lambda element : element[0])

	def get_output(self, material, N, nc):
			return "%s_N%03i_nc%06.4f/" % (material, N, nc)
	# archive results
	def archive(self, dest='/home/stollenw/projects/euo/results/isolated/'):
		for d in self.data:
			print "archive", d 
			dest_path=dest + self.get_output(d[0], d[1], d[2])
			if not os.path.exists(dest_path):
				os.mkdir(dest_path)
			dest_temp_path=dest_path + "output_t%07.3f/" % d[3]
			if not os.path.exists(dest_temp_path):
				os.mkdir(dest_temp_path)
			try:
				cmd="rsync -avztq %s %s" % ("%s/parameter.cfg" % d[5], dest_temp_path)
				subprocess.call(cmd, shell=True)
				cmd="rsync -avztq %s %s" % ("%s/source" % d[5], dest_temp_path)
				subprocess.call(cmd, shell=True)
				cmd="rsync -avztq %s %s" % ("%s/results" % d[5], dest_temp_path)
				subprocess.call(cmd, shell=True)
				f=open("%s/origin.txt" % dest_temp_path, 'w')
				f.write("%s\n" % d[5])
				f.close()

			except:
				print 'Error: Failed to archive: %s' % d[5]
				print 'Break.'
				exit(1)
	# download results
	def download_results(self, material, N, nc, T, dest, source='stollenw@heisenberg.physik.uni-bonn.de:/home/stollenw/projects/euo/results/isolated/'):
		for d in self.data:
			if material==d[0] and N==d[1] and nc==d[2] and T==d[3]:
				source_path=source + self.get_output(d[0], d[1], d[2])
				dest_path  =dest   + self.get_output(d[0], d[1], d[2])
				if not os.path.exists(dest_path):
					os.mkdir(dest_path)
				source_temp_path=source_path + "output_t%07.3f/" % d[3]
				dest_temp_path  =dest_path   + "output_t%07.3f/" % d[3]
				if not os.path.exists(dest_temp_path):
					os.mkdir(dest_temp_path)
				try:
					cmd="rsync -avztq %s %s" % ("%s/parameter.cfg" % source_temp_path, dest_temp_path)
					subprocess.call(cmd, shell=True)
					cmd="rsync -avztq %s %s" % ("%s/source" % source_temp_path, dest_temp_path)
					subprocess.call(cmd, shell=True)
					cmd="rsync -avztq %s %s" % ("%s/results" % source_temp_path, dest_temp_path)
					subprocess.call(cmd, shell=True)
					f=open("%s/origin.txt" % dest_temp_path, 'w')
					f.write("%s\n" % d[5])
					f.close()

				except:
					print 'Error: Failed to read from remote archive: %s' % source_temp_path
					print 'Break.'
					exit(1)
				
				return dest_temp_path

		print 'Error: Failed to find dataset in remote archive: %s' % source
		print "material=%s" % material
		print "N=%s" % N
		print "nc=%s" % nc 
		print "T=%s" % T
		print "Break."
		exit(1)
	
###############################################
# Database for Heterostructure runs
###############################################
class heterostructure_database:
	def __init__(self):
		self.names=('system', 'N', 'M', 'ni', 'ncr', 'dW' 'T', 'avmag', 'origin')
		self.data=[]

	def extractData (self, resultsFolder):
		# get system parameter
		parafilename="%s/parameter.cfg" % resultsFolder
		sp=system_parameter()
		sp.read_file(parafilename)
		system=sp.get_system()
		if (system==None):
			print "ExtractValues: Unable to find matching system type. Break."
			exit(1)
		if (system.constituens==(None,None)):
			print "ExtractValues: System in %s is not a heterostructure. Break." % resultsFolder
			exit(1)
	
		# get values
		avmagfilename="%s/results/avmag.dat" % resultsFolder
		avmag=float(extractResultValue(mufilename))
		return (system.name, sp.N, sp.concentration, sp.temperature, avmag, os.path.abspath(resultsFolder))


	# write database to file
	def write(self, filename):
		f=open(filename, 'w')
		f.write('{:<30}\tN\tM\tni\tncr\t\t\tdW\t\t\tT\t\t\tavmag\t\t\torigin\n'.format('#mat'))
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
		self.names=('system', 'N', 'M', 'ni', 'ncr', 'dW' 'T', 'avmag', 'origin')

	# read database from file
	def read(self, filename):
		f=open(filename, 'r')
		lines=f.readlines()
		f.close()

		self.data=[]
		for l in lines[1:]:
			d=l.split()
			material=d[0]
			N=int(d[1])
			M=int(d[2])
			ni=float(d[3])
			ncr=float(d[4])
			dW=float(d[5])
			T=float(d[6])
			avmag=float(d[7])
			origin=d[8]
			self.data.append((material, N, M, ni, ncr, dW, T, avmag, origin))

	# read in database from remote file
	def download(self, remotepath='stollenw@heisenberg.physik.uni-bonn.de:/home/stollenw/projects/euo/database/hetero.db'):
		cmd='scp %s hetero.db.temp' % remotepath
		try:
			proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
			proc.wait()
			self.read('hetero.db.temp')
			os.remove('hetero.db.temp')
		except:
			print 'Error: Failed to retrieve remote isolated database: %s' % remotepath
			print 'Break.'
			exit(1)
		
	# overwrite database on remote host
	def upload(self, remotepath=None):
		if remotepath==None:
			remotepath=self.remotepath
		self.write('hetero.db.temp')
		cmd='scp hetero.db.temp %s' % remotepath
		try:
			proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
			proc.wait()
			os.remove('hetero.db.temp')
		except:
			print 'Error: Failed to write onto remote isolated database: %s' % remotepath
			print 'Break.'
			exit(1)
			
	# check if special dataset exists in database
	def exists(self, material, N, M, ni, ncr, dW, T):
		for d in self.data:
			if material==d[0] and N==d[1]  and M==d[2] and ni==d[3] and ncr==d[4] and dW==d[5] and T==d[6]:
				return True
		return False

	# extract avmag
	def getAvmag(self, material, N, M, ni, ncr, dW, T):
		for d in self.data:
			if material==d[0] and N==d[1]  and M==d[2] and ni==d[3] and ncr==d[4] and dW==d[5] and T==d[6]:
				return d[7]

		print "Error: Unable to find dataset in database:"
		print "material=%s" % material
		print "N=%s" % N
		print "M=%s" % M
		print "ni=%s" % ni 
		print "ncr=%s" % ncr 
		print "dW=%s" % dW 
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
					(material, N_l, N_r, nc_l, nc_r, DeltaW, T, avmag, path)=self.extractData(folder)
					if not self.exists(material, N, nc, T):
						print "Adding dataset: %s, N_l=%03i, N_r=%03i, nc_l=%06.4f, nc_r=%06.4f, dW=%06.4f, T=%05.1f, AvMag=%06.4f, Source=%s" %(material, N_l, N_r, nc_l, nc_r, DeltaW, T, avmag, path)
						self.data.append((material, N_l, N_r, nc_l, nc_r, DeltaW, T, avmag, path))

		# sort by 2nd column i.e. N 
		self.data=sorted(self.data, key = lambda element : element[1])

	def get_output(self, material, N, M, ni, ncr, dW):
		return "%s_N%03i_M%03i_ni%06.4f_ncr%06.4f_dW%06.4/" % (material, N, M, ni, ncr, dW)

	# archive results
	def archive(self, dest='/home/stollenw/projects/euo/results/heterostructures/'):
		for d in self.data:
			print "archive", d 
			dest_path=dest + self.get_output(d[0], d[1], d[2], d[3], d[4], d[5])
			if not os.path.exists(dest_path):
				os.mkdir(dest_path)
			dest_temp_path=dest_path + "output_t%07.3f/" % d[6]
			if not os.path.exists(dest_temp_path):
				os.mkdir(dest_temp_path)
			cmd="rsync -avztq %s %s" % ("%s/parameter.cfg" % d[8], dest_temp_path)
			subprocess.call(cmd, shell=True)
			cmd="rsync -avztq %s %s" % ("%s/source" % d[8], dest_temp_path)
			subprocess.call(cmd, shell=True)
			cmd="rsync -avztq %s %s" % ("%s/results" % d[8], dest_temp_path)
			subprocess.call(cmd, shell=True)
			f=open("%s/origin.txt" % dest_temp_path, 'w')
			f.write("%s\n" % d[5])
			f.close()

	def download_results(self, material, N, M, ni, ncr, dW, T, dest, source='stollenw@heisenberg.physik.uni-bonn.de:/home/stollenw/projects/euo/results/isolated/'):
		for d in self.data:
			if material==d[0] and N==d[1]  and M==d[2] and ni==d[3] and ncr==d[4] and dW==d[5] and T==d[6]:
				sourch_path=source + self.get_output(d[0], d[1], d[2], d[3], d[4], d[5])
				dest_path  =dest   + self.get_output(d[0], d[1], d[2], d[3], d[4], d[5])
				if not os.path.exists(dest_path):
					os.mkdir(dest_path)
				source_temp_path=source_path + "output_t%07.3f/" % d[3]
				dest_temp_path  =dest_path   + "output_t%07.3f/" % d[3]
				if not os.path.exists(dest_temp_path):
					os.mkdir(dest_temp_path)
				try:
					cmd="rsync -avztq %s %s" % ("%s/parameter.cfg" % source_temp_path, dest_temp_path)
					subprocess.call(cmd, shell=True)
					cmd="rsync -avztq %s %s" % ("%s/source" % source_temp_path, dest_temp_path)
					subprocess.call(cmd, shell=True)
					cmd="rsync -avztq %s %s" % ("%s/results" % source_temp_path, dest_temp_path)
					subprocess.call(cmd, shell=True)
					f=open("%s/origin.txt" % dest_temp_path, 'w')
					f.write("%s\n" % d[5])
					f.close()

				except:
					print 'Error: Failed to read from remote archive: %s' % source_temp_path
					print 'Break.'
					exit(1)
				
				return dest_temp_path

		print 'Error: Failed to find dataset in remote archive: %s' % source
		print "material=%s" % material
		print "N=%s" % N
		print "M=%s" % M
		print "ni=%s" % ni 
		print "ncr=%s" % ncr 
		print "dW=%s" % dW 
		print "T=%s" % T
		print "Break."
		exit(1)

##############################################################################
##### Get run commands necessary to get values of isolateds
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
			isolated_cmd=''
			if not left_exists:
				isolated_cmd+=sp.get_runcmd(system.constituents[0]) + "; "
			if not right_exists:
				isolated_cmd+=sp.get_runcmd(system.constituents[1]) + "; "
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

			return cmd
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
# if no suitable input was found the database will be search and copy of a suitable
# input folder is downloaded from the archive
def add_input (runcmd, path=None):
	# get system parameter
	sp=system_parameter()
	sp.read_cmd(runcmd)
	# get current temperature
	T=sp.temperature
	# check if there is already in input folder given, if this is the case, skip
	if sp.input==None:
		# extract output folder from run command if path variable is not given
		if path==None:
			path=os.path.dirname(os.path.abspath(sp.output))
		
		inputOptions=''
		# Search search 'resultsFolder' for sub folders containing results with
		# smaller temperatures thant 'T' 
		foundInput=False
		resultFolders=[]
		if os.path.exists(path):
			for d in os.listdir(path):
				folder=os.path.join(path, d)
				if os.path.isdir(folder) and isResults(folder):
					resultFolders.append((folder, float(extractParameter("%s/parameter.cfg" % folder, parameter))))
	
			# find a folder with lower temperature than T
			tmax=0.0
			for (f,t) in resultFolders:
				if t>tmax and t<=T:
					tmax=t
					inputFolder=f
		
			if tmax>0.0:
				foundInput=True
				runcmd+=" -i " + inputFolder + "/"

		# no suitable input was found in local folder, check database
		if foundInput==False and sp.get_system!=None:
			database=None
			# isolated systems
			if sp.constituents==(None,None):
				database=isolated_database()
				database.download()
				# find a folder with lower temperature than T
				tmax=0.0
				for d in database.data:
					t=d[3]
					if t>tmax and t<=T:
						tmax=t

				if tmax>0.0:
					inputFolder=database.download_results(sp.get_system, sp.N, sp.concentration, tmax, path)
					runcmd+=" -i " + inputFolder + "/"

			# heterostructures
			else:
				database=heterostructure_database()
				database.download()
				# find a folder with lower temperature than T
				tmax=0.0
				for d in database.data:
					t=d[5]
					if t>tmax and t<=T:
						tmax=t

				if tmax>0.0:
					inputFolder=database.download_results(sp.get_system, sp.N, sp.N0, sp.concentration, sp.n_cr, tmax, path)
					runcmd+=" -i " + inputFolder + "/"

	return runcmd
			
def main():
	idb=isolated_database()
	idb.fill(('/home/stollenw/runs/runs_version-4e9912f/bgem/eugdo_n5_ni0.01/',))
	#idb.archive()

	sp=system_parameter()
	print sp.get_runcmd_isolated('Metal', N=5, nc=1.0, T=100.1)
	print idb.get_output('Metal', N=5, nc=1.0)
	print sp.get_runcmd_hetero('EuGdO-Metal-Heterostructure-eta1e-4', N=5, M=9, ni=0.01, ncr=1.0, dW=0.125, T=100.1)
	
if __name__=="__main__":
	main()
