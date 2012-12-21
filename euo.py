#!/usr/bin/python

import os
import subprocess

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
##############################################################################
##############################################################################
##### Extract results from a given folder ####################################
##############################################################################
##############################################################################
def extractParameter (filename, name):
	parafile=open(filename, 'r')
	lines=parafile.readlines()
	parafile.close()
	for l in lines:
		if l.startswith(name):
			value=l.split()[2]
			return value
	print "Error: parameter %s in file %s not found!" % (name, filename)
	exit(1)

def parameterExists (filename, name):
	parafile=open(filename, 'r')
	lines=parafile.readlines()
	parafile.close()
	exists=False
	for l in lines:
		if l.startswith(name):
			exists=True
	return exists

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

# read in parameter file and map this onto a material class. Return the other material defining parameters
def extractSystemParameter(parafilename):
	concentration      = float(extractParameter(parafilename, 'concentration'     ))
	temperature        = float(extractParameter(parafilename, 'temperature'       ))
	N                  =   int(extractParameter(parafilename, 'N'                 ))
	N0                 =   int(extractParameter(parafilename, 'N0'                ))
	Ed0                =   int(extractParameter(parafilename, 'Ed0'               ))
	gamma              = float(extractParameter(parafilename, 'gamm'              ))
	impurity           =       extractParameter(parafilename, 'impurity'          )
	ncc_oxy            = float(extractParameter(parafilename, 'ncc_oxy'           ))
	ncc_gad            = float(extractParameter(parafilename, 'ncc_gad'           ))
	ncr                = float(extractParameter(parafilename, 'n_cr'              ))
	Delta_g            = float(extractParameter(parafilename, 'Delta_g'           ))
	J4f                = float(extractParameter(parafilename, 'J4f'               ))
	Jcf                = float(extractParameter(parafilename, 'Jcf'               ))
	D0                 = float(extractParameter(parafilename, 'D0 '               ))
	W                  = float(extractParameter(parafilename, 'W  '               ))
	spin0              = float(extractParameter(parafilename, 'spin0'             ))
	Ul                 = float(extractParameter(parafilename, 'Ul'                ))
	Ur                 = float(extractParameter(parafilename, 'Ur'                ))
	Delta_l0           = float(extractParameter(parafilename, 'Delta_l0'          ))
	Delta_r0           = float(extractParameter(parafilename, 'Delta_r0'          ))
	Delta_W            = float(extractParameter(parafilename, 'Delta_W'           ))
	eta                = float(extractParameter(parafilename, 'eta'               ))
	iota               = float(extractParameter(parafilename, 'iota'              ))
	domega_log_max     = float(extractParameter(parafilename, 'domega_log_max'    ))
	omega_log_1        = float(extractParameter(parafilename, 'omega_log_1'       ))
	N_log              = float(extractParameter(parafilename, 'N_log'             ))
	N_fermi            = float(extractParameter(parafilename, 'N_fermi'           ))
	domega_min_steps_l = float(extractParameter(parafilename, 'domega_min_steps_l'))
	domega_min_steps_r = float(extractParameter(parafilename, 'domega_min_steps_r'))
	#omega_min          = float(extractParameter(parafilename, 'omega_min'         ))
	#omega_max          = float(extractParameter(parafilename, 'omega_max'         ))
	dntol              = float(extractParameter(parafilename, 'dntol'             ))
	fltol              = float(extractParameter(parafilename, 'fltol'             ))
	tol                = float(extractParameter(parafilename, 'tol'               ))
	#wr1                = float(extractParameter(parafilename, 'wr1'               ))
	#wr0                = float(extractParameter(parafilename, 'wr0'               ))
	#wru                = float(extractParameter(parafilename, 'wru'               ))
	#max1               = float(extractParameter(parafilename, 'max1'              ))
	#max2               = float(extractParameter(parafilename, 'max2'              ))

	mirror=False
	if parameterExists(parafilename, 'mirror'):
		mirror=True
	insulator=False
	if parameterExists(parafilename, 'insulator'):
		insulator=True

	# map parameters to system configuration
	# check common parameters
	if not (Ed0==0.0 and gamma==0.05 and J4f==7e-5 and D0==8 and W==0 and spin0==0 and Ul==0 and Ur==0 and iota==1E-4 and domega_log_max==0.01 and omega_log_1==0.1 and N_log==200 and N_fermi==100 and domega_min_steps_l==1E-4 and domega_min_steps_r==1E-3 and dntol==1E-6 and fltol==1E-7 and tol==1E-3):
		print "Error: System parameter are non standard. Folder: %s" % resultsFolder
		exit(1)

	# define material classed by system relevant parameters:
	# N0
	# impurity
	# ncc_oxy
	# ncc_gad
	# n_cr
	# Delta_g
	# Jcf
	# eta 
	# mirror
	# insulator
	material=''
	isolated=False
	if (N0==0 and impurity=='None' and Jcf==0.0 and eta==0.0 and mirror==True):
		material='Metal'
		# double number of layers since this material serves as a capping layer
		N=2*N-1
		isolated=True
	elif (N0==0 and impurity=='None' and Jcf==0.05 and eta==0.0 and mirror==True):
		material='Heisenberg-Metal'
		# double number of layers since this material serves as a capping layer
		N=2*N-1
		isolated=True
	#elif (N0==0, impurity=='None' and Jcf==0.00 and eta==0.0 and mirror==True and bandSplit==0.01):
	#	material='Band-Magnetic-Metal          '
	#	# double number of layers since this material serves as a capping layer
	#	N=2*N-1
	#	isolated=True
	elif (N0==0 and impurity=='Gd' and ncc_gad==0.9952 and Jcf==0.05 and eta==1e-9 and mirror==True):
		material='EuGdO'
		isolated=True
	elif (N0!=0 and impurity=='Gd' and ncc_gad==0.9952 and Jcf==0.05 and eta==1e-4 and mirror==True and insulator==False):
		material='EuGdO-Metal-eta1e-4'
	elif (N0!=0 and impurity=='Gd' and ncc_gad==0.9952 and Jcf==0.05 and eta==1e-7 and mirror==True and insulator==False):
		material='EuGdO-Metal-eta1e-7'
	else:
		print "Error: Unable to extract material type from file %s" % parafilename
		exit(1)

	return (material, N, N0, concentration, ncr, temperature, Delta_W, isolated)

def extractIsodeltaParameter (resultsFolder):
	# get system parameter
	parafilename="%s/parameter.cfg" % resultsFolder
	(material, N, N0, concentration, ncr, temperature, Delta_W, isolated)=extractSystemParameter(parafilename)
		
	if not isolated:
		print "Error: Results in folder %s does not correspond to an isolated material. Material is %s" % (resultsFolder, material)
		exit(1)

	# get Delta value
	mufilename="%s/results/mu.dat" % resultsFolder
	mu=float(extractResultValue(mufilename))
	Delta=-mu

	return (material, N, concentration, temperature, Delta, os.path.abspath(resultsFolder))

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
		cmd='scp %s isodelta.db.temp' % remotepath
		try:
			proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
			proc.wait()
			self.read('isodelta.db.temp')
			os.remove('isodelta.db.temp')
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
##############################################################################
##### Class managing the EuO program run commands ############################
##############################################################################
##############################################################################
class runcmd:
	def __init__(self, c):
		self.cmd=c

	######################################################################
	##### Interface run - Add energy shifts of isolated materials ########
	######################################################################
	def get_option(self, key, default=None):
		# get command line options
		options=self.cmd.partition('euo.out')[2].split()
		# extract temperature (if none given, default is 40 K)
		try:
			i=options.index(key)
			value=options[i+1].rstrip('/')
			return value
		except ValueError:
			if default!=None:
				return default
			else:
				print 'Error: Failed to extract value for option %s in run command: %s. No default was given. Break.' % (key, self.cmd)
				exit(1)
	def option_exists(self, key):
		# get command line options
		options=self.cmd.partition('euo.out')[2].split()
		# extract temperature (if none given, default is 40 K)
		try:
			i=options.index(key)
			value=options[i+1].rstrip('/')
			return True
		except ValueError:
			return False

	def add_isodeltas(self, dbpath=None):
		# get relevant command line options
		T=float(self.get_option('-t'))
		N=int(self.get_option('-n'))
		N0=int(self.get_option('-m'))
		ni=float(self.get_option('-x', 0.01))
		deltaW=float(self.get_option('--Delta_W', 0.0))
		ncr=float(self.get_option('--n_cr', 0.01))
		Delta_g=float(self.get_option('--Delta_g', 0.125))
		insulator=self.option_exists('--insulator')

		# read database
		db=isodeltabase()
		if dbpath==None:
			db.download()
		else:
			db.read(dbpath)

		# get Deltas (isolated energy shifts) for EuO and metallic substrate
		# for the insulating case, just shift Delta_r by Delta_g
		Delta_l=db.getDelta('EuGdO', N, ni, T)
		self.cmd+=" --Delta_l0 %0.15e" % Delta_l
		if not insulator:
			Delta_r=db.getDelta('Metal', N0, ncr, T)
			self.cmd+=" --Delta_r0 %0.15e" % Delta_r

	#######################################################################
	##### Add suitable input to euo run command if available ##############
	#######################################################################
	# Add input path to EuO run command 'runcmd'. Hereby the output path and the 
	# temperature in 'runcmd' is extracted. It's parent directory is then searched 
	# for folder containing results with smaller temperatures. The full run command
	# with input options is then returned.
	def add_input (self, path=None):
		options=self.cmd.split()
		# check if there is already in input folder given, if this is the case, skip
		if not '-i' in options:

			# extract output folder from run command if path variable is not given
			if path==None:
				try:
					i=options.index('-o')
					path=os.path.dirname(os.path.abspath(options[i+1].rstrip('/')))
				except ValueError:
					path=os.getcwd()
		
	
			# extract temperature (if none given, default is 40 K)
			T=0.0
			try:
				i=options.index('-t')
				T=float(options[i+1].rstrip('/'))
			except ValueError:
				T=40.0
		
			inputOptions=''
			# Search search 'resultsFolder' for sub folders containing results with
			# smaller temperatures thant 'T' 
			resultFolders=[]
			if os.path.exists(path):
				for d in os.listdir(path):
					folder=os.path.join(path, d)
					if os.path.isdir(folder) and isResults(folder):
						resultFolders.append((folder, extractSystemParameter("%s/parameter.cfg" % folder)[5]))
		
				# find a folder with lower temperature than T
				tmax=0.0
				for (f,t) in resultFolders:
					if t>tmax and t<=T:
						tmax=t
						inputFolder=f
			
				if tmax>0.0:
					self.cmd+=" -i " + inputFolder + "/"

#db=isodeltabase()
#db.fill(['../../runs/runs_version-a177549/pure_ncr0.50/n3/','../../runs/runs_version-a177549/n5/'])
#db.write('../../database/isodelta.db')
#r=run('euo.out -n 5 -m 5 --n_cr 0.5 -o ../../runs/runs_version-a177549/n5/output_t050/ -t 60')
#r.add_input('../../runs/runs_version-a177549/n5_m2_ncr0.10/')
#r.add_isodeltas()
#print r.cmd
