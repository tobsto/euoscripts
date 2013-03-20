#!/usr/bin/python

import os
import subprocess
import argparse
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

def extractResultValue2ndColumn (filename):
	f=open(filename, 'r')
	l=f.readline().split()[1]
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
		return "%0.17e" % val
	else:
		print "Error: Sting conversion: Unknown type. Break"
		exit(1)

# mapping for remote worker clients
class worker:
	def __init__(self, host, serverdir, clientdir, mpicmd):
		self.host=host
		self.serverdir=serverdir
		self.clientdir=clientdir
		self.mpicmd=mpicmd
workers=[]

workers.append(worker(	'heisenberg', 
	 		'/home/stollenw/runs/',
			'/home/stollenw/runs/',
			 'mpirun'))
workers.append(worker(	'agem.th.physik.uni-bonn.de',
			'/home/stollenw/runs/',
			'/users/stollenw/runs/',
			'mpirun --hostfile /users/stollenw/runs/hostfile_agem'))
workers.append(worker(	'bgem.th.physik.uni-bonn.de',
			'/home/stollenw/runs/',
			'/users/stollenw/runs/',
			'mpirun --hostfile /users/stollenw/runs/hostfile_bgem'))
workers.append(worker(	'cgem.th.physik.uni-bonn.de',
			'/home/stollenw/runs/',
			'/users/stollenw/runs/',
			'mpirun --hostfile /users/stollenw/runs/hostfile_cgem'))
workers.append(worker(	'stgeorgenamreith',
			'/home/stollenw/runs/',
			'/users/stollenw/runs/',
			'mpirun --hostfile /users/stollenw/runs/hostfile'))
workers.append(worker(	'pfaffenschlag',
			'/home/stollenw/runs/',	
			'/users/stollenw/runs/', 'mpirun --hostfile /users/stollenw/runs/hostfile_schlag'))
workers.append(worker(	'lunzamsee',
			'/home/stollenw/runs/',
			'/users/stollenw/runs/',
			'mpirun --hostfile /users/stollenw/runs/hostfile_lunz'))
workers.append(worker(	'stleonhardamforst',	
			'/home/stollenw/runs/',
			'/users/stollenw/runs/',
			'mpirun --hostfile /users/stollenw/runs/hostfile_leon'))
workers.append(worker(	'bischofstetten',
			'/home/stollenw/runs/',	
			'/users/stollenw/runs/',
			'mpirun --hostfile /users/stollenw/runs/hostfile_stetten'))
workers.append(worker(	'login',
			'/home/stollenw/druns/',
			'/checkpoints/',
			'mpirun.openmpi --mca btl ^udapl,openib --mca btl_tcp_if_include eth0 -x LD_LIBRARY_PATH --hostfile /users/stollenw/hostfile'))

# default iteration parameter for the different types of systems
def get_iteration_parameter(system_name):
	if system_name=='Metal':
		return ''
	elif system_name=='Heisenberg-Metal':
		return ''
	elif system_name=='EuGdO':
		return ''
	elif system_name=='EuGdO-Metal-Heterostructure-eta1e-4':
		return ''
	elif system_name=='HeisenbergMetal-Metal-Heterostructure':
		return ''
	elif system_name=='Metal-Metal-Heterostructure':
		return ''
	else:
		return ''
		#print "Error: get iteration parameter. Unknow system name: %s. Break." % system_name
		#exit(1)

###############################################
# Database for bulk results
###############################################
class bulk_database:
	def __init__(self):
		self.names=('material', 'ni', 'T', 'mag', 'origin')
		self.data=[]
		self.workers=workers

	def extractData (self, resultsFolder):
		# get system parameter
		parafilename="%s/parameter.cfg" % resultsFolder
		sp=system_parameter()
		sp.read_file(parafilename)
		system=sp.get_system()
		if (system==None):
			print "ExtractValues: Unable to find matching system type. Break."
			exit(1)
		if (system.material_class!='bulk'):
			print "ExtractValues: System in %s is not bulk. Break." % resultsFolder
			exit(1)
			
		# get magnetisation value
		magfilename="%s/results/totalmag.dat" % resultsFolder
		mag=float(extractResultValue2ndColumn(magfilename))
		return (system.name, sp.concentration, sp.temperature, mag, os.path.abspath(resultsFolder))


	# write database to file
	def write(self, filename):
		f=open(filename, 'w')
		f.write('{:<30}\tni\t\t\tT\t\t\tmag\t\t\torigin\n'.format('# material'))
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
		self.names=('material', 'ni', 'T', 'mag', 'origin')

	# read database from file
	def read(self, filename):
		f=open(filename, 'r')
		lines=f.readlines()
		f.close()

		self.data=[]
		for l in lines[1:]:
			d=l.split()
			material=d[0]
			ni=float(d[1])
			T=float(d[2])
			mag=float(d[3])
			origin=d[4]
			self.data.append((material, ni, T, mag, origin))

	# read in database from remote file
	def download(self, remotepath='stollenw@heisenberg.physik.uni-bonn.de:/home/stollenw/projects/euo/database/bulk.db'):
		cmd='scp %s bulk.db.temp' % remotepath
		try:
			proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
			proc.wait()
			self.read('bulk.db.temp')
			os.remove('bulk.db.temp')
		except:
			print 'Error: Failed to retrieve remote bulk database: %s' % remotepath
			print 'Break.'
			exit(1)
		
	# overwrite database on remote host
	def upload(self, remotepath=None):
		if remotepath==None:
			remotepath=self.remotepath
		self.write('bulk.db.temp')
		cmd='scp bulk.db.temp %s' % remotepath
		try:
			proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
			proc.wait()
			os.remove('bulk.db.temp')
		except:
			print 'Error: Failed to write onto remote bulk database: %s' % remotepath
			print 'Break.'
			exit(1)
			
	# check if special dataset exists in database
	def exists(self, material, ni, T):
		for d in self.data:
			if material==d[0] and ni==d[1] and T==d[2]:
				return True
		return False

	# get magnetisation
	def getMag(self, material, ni, T):
		for d in self.data:
			if material==d[0] and ni==d[1] and T==d[2]:
				return d[3]

		print "Error: Unable to find dataset in database:"
		print "material=%s" % material
		print "ni=%s" % ni 
		print "T=%s" % T
		print "Break."
		exit(1)
	
	# fill database by extracting results form a special folder
	def fill(self, topResultsFolders, overwrite=False):
		if overwrite:
			self.data=[]
		for topfolder in topResultsFolders:
			# if top folder contains results
			if os.path.isdir(topfolder) and isResults(topfolder):
				(material, ni, T, mag, path)=self.extractData(topfolder)
				if not self.exists(material, ni, T):
					print "Adding dataset: %s, ni=%06.4f, T=%05.1f, mag=%06.4f, Source=%s" %(material, ni, T, mag, path)
					self.data.append((material, ni, T, mag, path))

			# if not search sub folder for results
			else:
				for d in os.listdir(topfolder):
					folder=os.path.join(topfolder, d)
					if os.path.isdir(folder) and isResults(folder):
						(material, ni, T, mag, path)=self.extractData(folder)
						if not self.exists(material, ni, T):
							print "Adding dataset: %s, ni=%06.4f, T=%05.1f, mag=%06.4f, Source=%s" %(material, ni, T, mag, path)
							self.data.append((material, ni, T, mag, path))
	
		# sort by 1st column i.e. material
		self.data=sorted(self.data, key = lambda element : element[0])

	def get_output(self, material, ni):
			return "%s_ni%06.4f/" % (material, ni)
	def get_temp_output(self, t):
			return "t%07.3f/" % t
	# archive results
	def archive(self, dest='/home/stollenw/projects/euo/results/bulk/'):
		if not os.path.exists(dest):
			os.makedirs(dest)
		for d in self.data:
			print "archive", d 
			dest_path=dest + self.get_output(d[0], d[1])
			if not os.path.exists(dest_path):
				os.mkdir(dest_path)
			dest_temp_path=dest_path + self.get_temp_output(d[2])
			if not os.path.exists(dest_temp_path):
				os.mkdir(dest_temp_path)
			try:
				cmd="rsync -avztq %s %s" % ("%s/parameter.cfg" % d[4], dest_temp_path)
				subprocess.call(cmd, shell=True)
				cmd="rsync -avztq %s %s" % ("%s/source" % d[4], dest_temp_path)
				subprocess.call(cmd, shell=True)
				cmd="rsync -avztq %s %s" % ("%s/results" % d[4], dest_temp_path)
				subprocess.call(cmd, shell=True)
				f=open("%s/origin.txt" % dest_temp_path, 'w')
				f.write("%s\n" % d[4])
				f.close()

			except:
				print 'Error: Failed to archive: %s' % d[4]
				print 'Break.'
				exit(1)
	# download results
	def download_results(self, material, ni, T, dest, source='stollenw@heisenberg.physik.uni-bonn.de:/home/stollenw/projects/euo/results/bulk/'):
		for d in self.data:
			if material==d[0] and ni==d[1] and T==d[2]:
				source_path=source + self.get_output(d[0], d[1])
				dest_path  =dest   + self.get_output(d[0], d[1])
				if not os.path.exists(dest_path):
					os.makedirs(dest_path)
				source_temp_path=source_path + self.get_temp_output(d[2])
				dest_temp_path  =dest_path   + self.get_temp_output(d[2])
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
					f.write("%s\n" % d[4])
					f.close()

				except:
					print 'Error: Failed to read from remote archive: %s' % source_temp_path
					print 'Break.'
					exit(1)
				
				return dest_temp_path

		print 'Error: Failed to find dataset in remote archive: %s' % source
		print "material=%s" % material
		print "ni=%s" % ni 
		print "T=%s" % T
		print "Break."
		exit(1)
	
###############################################
# Database for isolated Deltas
###############################################
class isolated_database:
	def __init__(self):
		self.names=('material', 'N', 'nc', 'T', 'Delta', 'origin')
		self.data=[]
		self.workers=workers

	def extractData (self, resultsFolder):
		# get system parameter
		parafilename="%s/parameter.cfg" % resultsFolder
		sp=system_parameter()
		sp.read_file(parafilename)
		system=sp.get_system()
		if (system==None):
			print "ExtractValues: Unable to find matching system type. Break."
			exit(1)
		if (system.material_class!='isolated'):
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
		f.write('{:<30}\tN\tnc\t\t\tT\t\t\tDelta\t\t\torigin\n'.format('# material'))
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
	def fill(self, topResultsFolders, overwrite=False):
		if overwrite:
			self.data=[]
		for topfolder in topResultsFolders:
			# if top folder contains results
			if os.path.isdir(topfolder) and isResults(topfolder):
				(material, N, nc, T, Delta, path)=self.extractData(topfolder)
				if not self.exists(material, N, nc, T):
					print "Adding dataset: %s, N=%03i, nc=%06.4f, T=%05.1f, Delta=%01.9f, Source=%s" %(material, N, nc, T, Delta, path)
					self.data.append((material, N, nc, T, Delta, path))

			# if not search sub folder for results
			else:
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
	def get_temp_output(self, t):
			return "t%07.3f/" % t
	# archive results
	def archive(self, dest='/home/stollenw/projects/euo/results/isolated/'):
		if not os.path.exists(dest):
			os.makedirs(dest)
		for d in self.data:
			print "archive", d 
			dest_path=dest + self.get_output(d[0], d[1], d[2])
			if not os.path.exists(dest_path):
				os.mkdir(dest_path)
			dest_temp_path=dest_path + self.get_temp_output(d[3])
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
					os.makedirs(dest_path)
				source_temp_path=source_path + self.get_temp_output(d[3])
				dest_temp_path  =dest_path   + self.get_temp_output(d[3])
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
		self.workers=workers

	def extractData (self, resultsFolder):
		# get system parameter
		parafilename="%s/parameter.cfg" % resultsFolder
		sp=system_parameter()
		sp.read_file(parafilename)
		system=sp.get_system()
		if (system==None):
			print "ExtractValues: Unable to find matching system type. Break."
			exit(1)
		if (system.material_class!='heterostructure'):
			print "ExtractValues: System in %s is not a heterostructure. Break." % resultsFolder
			exit(1)
	
		# get values
		avmagfilename="%s/results/avmag.dat" % resultsFolder
		avmag=float(extractResultValue2ndColumn(avmagfilename))
		return (system.name, sp.N, sp.N0, sp.concentration, sp.n_cr, sp.Delta_W, sp.temperature, avmag, os.path.abspath(resultsFolder))


	# write database to file
	def write(self, filename):
		f=open(filename, 'w')
		f.write('{:<50}\tN\tM\tni\tncr\t\t\tdW\t\t\tT\t\t\tavmag\t\t\torigin\n'.format('# material'))
		for d in self.data:
			f.write('{:<50}'.format(d[0]))
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
	def fill(self, topResultsFolders, overwrite=False):
		if overwrite:
			self.data=[]
		for topfolder in topResultsFolders:
			# if top folder contains results
			# if not search sub folder for results
			if os.path.isdir(topfolder) and isResults(topfolder):
				(material, N_l, N_r, nc_l, nc_r, DeltaW, T, avmag, path)=self.extractData(topfolder)
				if not self.exists(material, N_l, N_r, nc_l, nc_r, DeltaW, T):
					print "Adding dataset: %s, N_l=%03i, N_r=%03i, nc_l=%06.4f, nc_r=%06.4f, dW=%06.4f, T=%05.1f, AvMag=%06.4f, Source=%s" %(material, N_l, N_r, nc_l, nc_r, DeltaW, T, avmag, path)
					self.data.append((material, N_l, N_r, nc_l, nc_r, DeltaW, T, avmag, path))

			else:
				for d in os.listdir(topfolder):
					folder=os.path.join(topfolder, d)
					if os.path.isdir(folder) and isResults(folder):
						(material, N_l, N_r, nc_l, nc_r, DeltaW, T, avmag, path)=self.extractData(folder)
						if not self.exists(material, N_l, N_r, nc_l, nc_r, DeltaW, T):
							print "Adding dataset: %s, N_l=%03i, N_r=%03i, nc_l=%06.4f, nc_r=%06.4f, dW=%06.4f, T=%05.1f, AvMag=%06.4f, Source=%s" %(material, N_l, N_r, nc_l, nc_r, DeltaW, T, avmag, path)
							self.data.append((material, N_l, N_r, nc_l, nc_r, DeltaW, T, avmag, path))
	
		# sort by 2nd column i.e. N 
		self.data=sorted(self.data, key = lambda element : element[1])

	def get_output(self, material, N, M, ni, ncr, dW):
		return "%s_N%03i_M%03i_ni%06.4f_ncr%06.4f_dW%06.4f/" % (material, N, M, ni, ncr, dW)

	def get_temp_output(self, t):
			return "t%07.3f/" % t
	# archive results
	def archive(self, dest='/home/stollenw/projects/euo/results/heterostructure/'):
		if not os.path.exists(dest):
			os.makedirs(dest)
		for d in self.data:
			print "archive", d 
			dest_path=dest + self.get_output(d[0], d[1], d[2], d[3], d[4], d[5])
			if not os.path.exists(dest_path):
				os.mkdir(dest_path)
			dest_temp_path=dest_path + self.get_temp_output(d[6])
			if not os.path.exists(dest_temp_path):
				os.mkdir(dest_temp_path)
			cmd="rsync -avztq %s %s" % ("%s/parameter.cfg" % d[8], dest_temp_path)
			subprocess.call(cmd, shell=True)
			cmd="rsync -avztq %s %s" % ("%s/source" % d[8], dest_temp_path)
			subprocess.call(cmd, shell=True)
			cmd="rsync -avztq %s %s" % ("%s/results" % d[8], dest_temp_path)
			subprocess.call(cmd, shell=True)
			f=open("%s/origin.txt" % dest_temp_path, 'w')
			f.write("%s\n" % d[8])
			f.close()

	def download_results(self, material, N, M, ni, ncr, dW, T, dest, source='stollenw@heisenberg.physik.uni-bonn.de:/home/stollenw/projects/euo/results/heterostructure/'):
		for d in self.data:
			if material==d[0] and N==d[1]  and M==d[2] and ni==d[3] and ncr==d[4] and dW==d[5] and T==d[6]:
				source_path=source + self.get_output(d[0], d[1], d[2], d[3], d[4], d[5])
				dest_path  =dest   + self.get_output(d[0], d[1], d[2], d[3], d[4], d[5])
				if not os.path.exists(dest_path):
					os.makedirs(dest_path)
				source_temp_path=source_path + self.get_temp_output(d[6])
				dest_temp_path  =dest_path   + self.get_temp_output(d[6])
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
					f.write("%s\n" % d[8])
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
##### Get isolated deltas from parameter configuration file
##############################################################################
def get_isodeltas_from_parafile(parafile, dbpath=None):
	# read database
	db=isolated_database()
	if dbpath==None:
		db.download()
	else:
		db.read(dbpath)
	# get system parameter
	sp=system_parameter()	
	sp.read_file(parafile)
	system=sp.get_system()
	# check if system type is known
	if system!=None:
		# check if system is a heterostructure
		if system.material_class=='heterostructure':
			N_left=sp.N
			# the isolated system is mirror symmetric. For example, a heterostructure with N0=9
			# corresponds to an isolated mirror symmetric system with N=5=9+1/2
			if (sp.N0%2==0):
				print "Error: get_isodelta_info: No even values for number of layers in the right material allowed. Break."
				exit(1)
			N_right=int((sp.N0+1)/2.0)
			# if the heterostructure is not mirror symmetric the left system with N=5 corresponds to a
			# mirror symmetric system with N=3=5+1/2
			if not sp.mirror:
				if (sp.N%2==0):
					print "Error: get_isodelta_info: No even values for number of layers in the left, non-mirror-symmetric material allowed. Break."
					exit(1)
				N_left=int((sp.N+1)/2.0)

			left_exists=db.exists(system.constituents[0], N_left, sp.concentration, sp.temperature)
			right_exists=db.exists(system.constituents[1], N_right, sp.n_cr, sp.temperature)
			isolated_cmd=''
			if not left_exists or not right_exists:
				print "Error: Get isodeltas: Unable to get isolated delta values."
				print "Break."
				exit(1)

			Delta_l=db.getDelta(system.constituents[0], N_left, sp.concentration, sp.temperature)
			Delta_r=db.getDelta(system.constituents[1], N_right, sp.n_cr, sp.temperature)
			return (Delta_l, Delta_r)
		else:
			print "Error: Get isodeltas: Cannot add isodeltas to non heterostructure system."
			print "Break."
			exit(1)
	else:
		print "No know system matches the run command: %s" % cmd
		print "Break."
		exit(1)


##############################################################################
##### Get isolated deltas
##############################################################################
def get_isodeltas(matrial_name, N, M, ni, ncr, t, dbpath=None):
	# read database
	db=isolated_database()
	if dbpath==None:
		db.download()
	else:
		db.read(dbpath)
	# get system parameter
	sp=system_parameter()	
	system=sp.get_system_by_name(material_name)
	# check if system type is known
	if system!=None:
		# check if system is a heterostructure
		if system.material_class=='heterostructure':
			N_left=N
			# the isolated system is mirror symmetric. For example, a heterostructure with N0=9
			# corresponds to an isolated mirror symmetric system with N=5=9+1/2
			if (M%2==0):
				print "Error: get_isodelta_info: No even values for number of layers in the right material allowed. Break."
				exit(1)
			N_right=int((M+1)/2.0)
			# if the heterostructure is not mirror symmetric the left system with N=5 corresponds to a
			# mirror symmetric system with N=3=5+1/2
			if not system.positive['mirror']:
				if (N%2==0):
					print "Error: get_isodelta_info: No even values for number of layers in the left, non-mirror-symmetric material allowed. Break."
					exit(1)
				N_left=int((N+1)/2.0)

			left_exists=db.exists(system.constituents[0], N_left, ni, t)
			right_exists=db.exists(system.constituents[1], N_right, n_cr, t)
			isolated_cmd=''
			if not left_exists or not right_exists:
				print "Error: Get isodeltas: Cannot add isodeltas to non heterostructure system."
				print "Break."
				exit(1)

			Delta_l=db.getDelta(system.constituents[0], N_left, ni, t)
			Delta_r=db.getDelta(system.constituents[1], N_right, ncr, t)
			return (Delta_l, Delta_r)
		else:
			print "Error: Get isodeltas: Cannot add isodeltas to non heterostructure system."
			print "Break."
			exit(1)
	else:
		print "No know system matches the run command: %s" % cmd
		print "Break."
		exit(1)


##############################################################################
##### Get run commands necessary to get values of isolated deltas
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
		if system.material_class=='heterostructure':
			N_left=sp.N
			# the isolated system is mirror symmetric. For example, a heterostructure with N0=9
			# corresponds to an isolated mirror symmetric system with N=5=9+1/2
			if (sp.N0%2==0):
				print "Error: get_isodelta_info: No even values for number of layers in the right material allowed. Break."
				exit(1)
			N_right=int((sp.N0+1)/2.0)
			# if the heterostructure is not mirror symmetric the left system with N=5 corresponds to a
			# mirror symmetric system with N=3=5+1/2
			if not sp.mirror:	
				if (sp.N%2==0):
					print "Error: get_isodelta_info: No even values for number of layers in the left, non-mirror-symmetric material allowed. Break."
					exit(1)
				N_left=int((sp.N+1)/2.0)

			left_exists=db.exists(system.constituents[0], N_left, sp.concentration, sp.temperature)
			right_exists=db.exists(system.constituents[1], N_right, sp.n_cr, sp.temperature)
			isolated_cmd=''
			if not left_exists:
				isolated_cmd+=sp.get_runcmd(system.constituents[0]) + "; "
			if not right_exists:
				isolated_cmd+=sp.get_runcmd(system.constituents[1]) + "; "
		else:
			print "Error: Get isodeltas: Cannot add isodeltas to non heterostructure system."
			print "Cmd: %s" % cmd
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
		if system.material_class=='heterostructure':
			N_left=sp.N
			# the isolated system is mirror symmetric. For example, a heterostructure with N0=9
			# corresponds to an isolated mirror symmetric system with N=5=9+1/2
			if (sp.N0%2==0):
				print "Error: get_isodelta_info: No even values for number of layers in the right material allowed. Break."
				exit(1)
			N_right=int((sp.N0+1)/2.0)
			# if the heterostructure is not mirror symmetric the left system with N=5 corresponds to a
			# mirror symmetric system with N=3=5+1/2
			if not sp.mirror:	
				if (sp.N%2==0):
					print "Error: get_isodelta_info: No even values for number of layers in the left, non-mirror-symmetric material allowed. Break."
					exit(1)
				N_left=int((sp.N+1)/2.0)

			Delta_l=db.getDelta(system.constituents[0], N_left, sp.concentration, sp.temperature)
			cmd+=" --Delta_l0 %0.17e" % Delta_l
			Delta_r=db.getDelta(system.constituents[1], N_right, sp.n_cr, sp.temperature)
			cmd+=" --Delta_r0 %0.17e" % Delta_r

			return cmd
	else:
		print "No know system matches the run command: %s" % cmd
		print "Break."
		exit(1)

##############################################################################
##### Check if energy shifts of isolated materials for known heterostruture already exist
##############################################################################
def get_isodelta_info(cmd, dbpath=None):
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
		if system.material_class=='heterostructure':
			N_left=sp.N
			# the isolated system is mirror symmetric. For example, a heterostructure with N0=9
			# corresponds to an isolated mirror symmetric system with N=5=9+1/2
			if (sp.N0%2==0):
				print "Error: get_isodelta_info: No even values for number of layers in the right material allowed. Break."
				exit(1)
			N_right=int((sp.N0+1)/2.0)
			# if the heterostructure is not mirror symmetric the left system with N=5 corresponds to a
			# mirror symmetric system with N=3=5+1/2
			if not sp.mirror:	
				if (sp.N%2==0):
					print "Error: get_isodelta_info: No even values for number of layers in the left, non-mirror-symmetric material allowed. Break."
					exit(1)
				N_left=int((sp.N+1)/2.0)

			left_exists=db.exists(system.constituents[0], N_left, sp.concentration, sp.temperature)
			right_exists=db.exists(system.constituents[1], N_right, sp.n_cr, sp.temperature)
			return (left_exists, system.constituents[0], N_left, sp.concentration, right_exists, system.constituents[1], N_right, sp.n_cr, sp.temperature)
		else:
			print "Error: Get isodeltas: Cannot add isodeltas to non heterostructure system."
			print "Cmd: %s" % cmd
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
def add_input (runcmd, download_path=None, path=None, source=None, input_system_name=None):
	if not source in (None, "local", "remote"):
		print "Error: Add input: source must be: None, 'local' or 'remote', not %s. Break." % source
		exit(1)
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
		# local path where the download is stored
		if download_path==None:
			download_path=os.path.dirname(os.path.abspath(sp.output))
		
		inputOptions=''
		# Search search 'resultsFolder' for sub folders containing results with
		# smaller temperatures thant 'T' 
		foundInput=False
		resultFolders=[]
		if os.path.exists(path) and (source==None or source=="local"):
			for d in os.listdir(path):
				folder=os.path.join(path, d)
				if os.path.isdir(folder) and isResults(folder):
					resultFolders.append((folder, float(extractParameter("%s/parameter.cfg" % folder, 'temperature'))))
	
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
		if foundInput==False and sp.get_system!=None and (source==None or source=="remote"):
			# physical system which serves as input
			if input_system_name==None:
				input_system_name=sp.get_system().name
			database=None
			# bulk systems
			if sp.get_system().material_class=='bulk':
				database=bulk_database()
				database.download()
				# find a folder with lower temperature than T
				tmax=0.0
				for d in sorted(filter(lambda element : element[0] == input_system_name and element[1] == sp.concentration, database.data), key= lambda element: element[2]):
					t=d[2]
					if t>tmax and t<=T:
						tmax=t

				if tmax>0.0:
					inputFolder=database.download_results(input_system_name, sp.concentration, tmax, download_path)
					runcmd+=" -i " + inputFolder + "/"


			# isolated systems
			elif sp.get_system().material_class=='isolated':
				database=isolated_database()
				database.download()
				# find a folder with lower temperature than T
				tmax=0.0
				for d in sorted(filter(lambda element : element[0] == input_system_name and element[1] == sp.N and element[2] == sp.concentration, database.data), key= lambda element: element[3]):
					t=d[3]
					if t>tmax and t<=T:
						tmax=t

				if tmax>0.0:
					inputFolder=database.download_results(input_system_name, sp.N, sp.concentration, tmax, download_path)
					runcmd+=" -i " + inputFolder + "/"

			# heterostructures
			else:
				database=heterostructure_database()
				database.download()
				# find a folder with lower temperature than T
				tmax=0.0
				for d in sorted(filter(lambda element : element[0] == input_system_name and element[1] == sp.N and element[2] == sp.N0 and element[3] == sp.concentration and element[4] == sp.n_cr and element[5] == sp.Delta_W, database.data), key= lambda element: element[6]):
					t=d[6]
					if t>tmax and t<=T:
						tmax=t

				if tmax>0.0:
					inputFolder=database.download_results(input_system_name, sp.N, sp.N0, sp.concentration, sp.n_cr, sp.Delta_W, tmax, download_path)
					runcmd+=" -i " + inputFolder + "/"

	return runcmd
			
def test():
	idb=isolated_database()
	idb.fill(('/home/stollenw/runs/runs_version-4e9912f/bgem/eugdo_n5_ni0.01/',))
	#idb.archive()

	sp=system_parameter()
	print sp.get_runcmd_isolated('Metal', N=5, nc=1.0, T=100.1)
	print idb.get_output('Metal', N=5, nc=1.0)
	print sp.get_runcmd_hetero('EuGdO-Metal-Heterostructure-eta1e-4', N=5, M=9, ni=0.01, ncr=1.0, dW=0.125, T=100.1)
	
	for worker in idb.workers:
		print worker.host, worker.mpicmd
	

def filtrate(data, dataset_names, dataset_input, length=None):
	# collect all datasets with different core attributes
	if length==None:
		rdata=list(set([row for row in data]))
	else:
		rdata=list(set([row[:length] for row in data]))

	# filter special datasets
	if dataset_input!=None:
		# parse dataset input an get matches
		matches={}
		i=0
		for d,n in zip(dataset_input, dataset_names):
			check=True
			if isinstance(d, str):
				check=(d.find('all')==-1)
			if check:
				if n=='material':
					matches[i]=d
				elif n=='N' or n=='M':
					matches[i]=int(d)
				else:
					matches[i]=float(d)
			i=i+1
	
		# filter function
		def filter_func(db_dataset):
			conditions=[]
			for index,value in matches.items():
				conditions.append(db_dataset[index]==value)
			return all(conditions) 

		# filter special datasets
		rdata=filter(filter_func, rdata)

	# sort data
	rdata=sorted(rdata)
	return rdata

def main():
	parser = argparse.ArgumentParser(description='Print database defining entries without temperatures')
	parser.add_argument('-d', '--database', help='Type of database: "bulk", "isolated" or "hetero"')
	parser.add_argument('-s', '--dataset', nargs='*', help='Specify dataset e.g. "Metal-Metal-Heterostructure 5 9 0.01 0.01 0.125" (for material, N, M, ni, ncr and dW). You may use "all" as a placeholder or do not specify the last values e.g. "all 5 all 0.01" ')
	args = parser.parse_args()

	if not args.database in ('bulk', 'isolated', 'hetero'):
		parser.print_help()
		exit(0)

	resultFolder='/home/stollenw/projects/euo/results/'
	db=None
	corenames=None
	special=None
	subResultFolder=None
	if args.database=='bulk':
		db=bulk_database()	
		corenames=('material', 'ni', 'T')
	elif args.database=='isolated':
		db=isolated_database()	
		corenames=('material', 'N', 'ni', 'T')
	else:
		db=heterostructure_database()	
		corenames=('material', 'N', 'M', 'ni', 'ncr', 'dW', 'T')
	db.download()


	rdata=filtrate(db.data, corenames, args.dataset, len(corenames)-1)

	for rd in rdata:
		print rd
	
if __name__=="__main__":
	main()

