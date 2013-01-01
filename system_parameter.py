#!/usr/bin/python

import os
import subprocess

# class defining different types of physical systems
class physical_system:
	def __init__(self, name, positve, negative, constituents=(None,None)):
		self.name=name
		self.positive=positive
		self.negative=negative
		self.constituents=constituents

physical_systems=[]

# common default parameter
common_positive={}
common_positive['Ed0']=0.0
common_positive['gamma']=0.05
common_positive['J4f']=7E-5
common_positive['D0']=8.0
common_positive['W']=0.0
common_positive['spin0']=0.0
common_positive['Ul']=0.0
common_positive['Ur']=0.0
common_positive['iota']=1E-4
common_positive['domega_log_max']=0.01
common_positive['omega_log_1']=0.1
common_positive['N_log']=200
common_positive['N_fermi']=100
common_positive['domega_min_steps_l']=1E-4
common_positive['domega_min_steps_r']=1E-3
common_positive['omega_min']=-4.0
common_positive['omega_max']=4.0
common_positive['dntol']=1E-6
common_positive['fltol']=1E-7
common_positive['tol']=1E-3
common_positive['twod']=False

# metal
name='Metal'
positive={}
positive['N0']=0
positive['impurity']='None'
positive['Jcf']=0.0
positive['eta']=0.0
positive['mirror']=True
positive.update(common_positive)
negative={}
physical_systems.append(physical_system (name, positive, negative))

# heisenberg-metal
name='Heisenberg-Metal'
positive={}
positive['N0']=0
positive['impurity']='None'
positive['Jcf']=0.05
positive['eta']=0.0
positive['mirror']=True
positive.update(common_positive)
negative={}
physical_systems.append(physical_system (name, positive, negative))

# EuGdO
name='EuGdO'
positive={}
positive['N0']=0
positive['impurity']='Gd'
positive['ncc_gad']=0.9952
positive['Jcf']=0.05
positive['eta']=1E-9
positive['mirror']=True
positive.update(common_positive)
negative={}
physical_systems.append(physical_system (name, positive, negative))

# EuGdO-Metal-Heterostructure
name='EuGdO-Metal-Heterostructure-eta1e-4'
left='EuGdO'
right='Metal'
positive={}
positive['impurity']='Gd'
positive['ncc_gad']=0.9952
positive['Jcf']=0.05
positive['eta']=1E-4
positive['mirror']=True
positive['insulator']=False
positive.update(common_positive)
negative={}
negative['N0']=0
physical_systems.append(physical_system (name, positive, negative, (left,right)))

# HeisenbergMetal-Metal-Heterostructure
name='HeisenbergMetal-Metal-Heterostructure'
left='Heisenberg-Metal'
right='Metal'
positive={}
positive['impurity']='None'
positive['Jcf']=0.05
positive['eta']=0.0
positive['mirror']=True
positive['insulator']=False
positive.update(common_positive)
negative={}
negative['N0']=0
physical_systems.append(physical_system (name, positive, negative, (left,right)))

# Metal-Metal-Heterostructure
name='Metal-Metal-Heterostructure'
left='Metal'
right='Metal'
positive={}
positive['impurity']='None'
positive['Jcf']=0.00
positive['eta']=0.0
positive['mirror']=True
positive['insulator']=False
positive.update(common_positive)
negative={}
negative['N0']=0
physical_systems.append(physical_system (name, positive, negative, (left,right)))

############################################
# extract options from run command string
############################################
def option_exists(cmd, keys):
		# get command line options
		options=cmd.partition('euo.out')[2].split()
		# extract option (if none given, return false)
		found=False
		for key in keys:
			try:
				i=options.index(key)
				found=True
				break
			except ValueError:
				found=False
		
		return found

def get_option(cmd, keys, default=None):
		# get command line options
		options=cmd.partition('euo.out')[2].split()
		# extract option (if none given, give default)
		found=False
		for key in keys:
			try:
				i=options.index(key)
				value=options[i+1].rstrip('/')
				found=True
				break
			except ValueError:
				found=False
		if found:
			return value
		else:
			if default!=None:
				return default
			else:
				print 'Error: Failed to extract value for option %s in run command: %s. No default was given. Break.' % (key, self.cmd)
				exit(1)	

############################################
# extract single value from parameter file
############################################
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

############################################
# class mapping the programm parameter to a physical system
############################################
class system_parameter:
	def __init__(self):
		self.physical_systems=physical_systems
	# read in parameter file and map this onto a material class.
	def read_cmd(self, runcmd):
		self.concentration       = float(get_option(runcmd, ('-x','--concentration'),                0.01))
		self.temperature         = float(get_option(runcmd, ('-t','--temperature'),                  40.0))
		self.N                   =   int(get_option(runcmd, ('-n','--N'),                               1))
		self.N0                  =   int(get_option(runcmd, ('-m','--N0'),                              0))
		self.Ed0                 = float(get_option(runcmd, ('-e','--Ed0'),                          0.00))
		self.gamma               = float(get_option(runcmd, ('-g','--gamma'),                        0.05))
		self.impurity            =      (get_option(runcmd, ('-p','--impurity'),                     "Gd"))
		self.output              =      (get_option(runcmd, ('-o','--output'),                   "output"))
		self.input=None
		if option_exists(runcmd, ('-i','--input')):
			self.input       =      (get_option(runcmd, ('-i','--input')))
		self.mirror              =    option_exists(runcmd, ('-s','--mirror'))
		self.ncc_oxy             = float(get_option(runcmd, ('--ncc_oxy',),                        0.9864))
		self.ncc_gad             = float(get_option(runcmd, ('--ncc_gad',),                        0.9952))
		self.n_cr                = float(get_option(runcmd, ('--n_cr',),                             0.01))
		self.Delta_g             = float(get_option(runcmd, ('--Delta_g',),                         0.125))
		self.J4f                 = float(get_option(runcmd, ('--J4f',),                              7E-5))
		self.Jcf                 = float(get_option(runcmd, ('--Jcf',),                              5E-2))
		self.D0                  = float(get_option(runcmd, ('--D0',),                                8.0))
		self.W                   = float(get_option(runcmd, ('--W',),                                 0.0))
		self.spin0               = float(get_option(runcmd, ('--spin0',),                             0.0))
		self.Ul                  = float(get_option(runcmd, ('--Ul',),                                0.0))
		self.Ur                  = float(get_option(runcmd, ('--Ur',),                                0.0))
		self.Delta_l0            = float(get_option(runcmd, ('--Delta_l0',),                          0.0))
		self.Delta_r0            = float(get_option(runcmd, ('--Delta_r0',),                          0.0))
		self.Delta_W             = float(get_option(runcmd, ('--Delta_W',),                           0.0))
		self.eta                 = float(get_option(runcmd, ('--eta',),                              1E-9))
		self.iota                = float(get_option(runcmd, ('--iota',),                             1E-4))
		self.domega_log_max      = float(get_option(runcmd, ('--domega_log_max',),                   0.01))
		self.omega_log_1         = float(get_option(runcmd, ('--omega_log_1',),                       0.1))
		self.N_log               =   int(get_option(runcmd, ('--N_log',),                             200))
		self.N_fermi             =   int(get_option(runcmd, ('--N_fermi',),                           100))
		self.domega_min_steps_l  = float(get_option(runcmd, ('--domega_min_steps_l',),               1E-4))
		self.domega_min_steps_r  = float(get_option(runcmd, ('--domega_min_steps_r',),               1E-3))
		self.omega_min           = float(get_option(runcmd, ('--omega_min',),                        -4.0))
		self.omega_max           = float(get_option(runcmd, ('--omega_max',),                         4.0))
		self.dntol               = float(get_option(runcmd, ('--dntol',),                            1e-6))
		self.fltol               = float(get_option(runcmd, ('--fltol',),                            1e-7))
		self.tol                 = float(get_option(runcmd, ('--tol',),                              1e-3))
		self.wr1                 = float(get_option(runcmd, ('--wr1',),                               0.3))
		self.wr0                 = float(get_option(runcmd, ('--wr0',),                              0.05))
		self.max1                =   int(get_option(runcmd, ('--max1',),                            10000))
		max2_default=10
		if self.impurity=="None":
			max2_default=0
		self.max2                =   int(get_option(runcmd, ('--max2',),                     max2_default))
		self.insulator           =    option_exists(runcmd, ('--insulator',))
		self.twod                =    option_exists(runcmd, ('--2d',))
		self.verbose             =    option_exists(runcmd, ('--verbose',))
		self.no_cleaning         =    option_exists(runcmd, ('--no_cleaning',))

	# read in parameter file and map this onto a material class.
	def read_file(self, parafilename):
		self.concentration      = float(extractParameter(parafilename, 'concentration'     ))
		self.temperature        = float(extractParameter(parafilename, 'temperature'       ))
		self.N                  =   int(extractParameter(parafilename, 'N'                 ))
		self.N0                 =   int(extractParameter(parafilename, 'N0'                ))
		self.Ed0                =   int(extractParameter(parafilename, 'Ed0'               ))
		self.gamma              = float(extractParameter(parafilename, 'gamma'             ))
		self.impurity           =      (extractParameter(parafilename, 'impurity'          ))
		self.output             =      (extractParameter(parafilename, 'output'            ))
		inputOption              =      (extractParameter(parafilename, 'input'             ))
		if inputOption=='None':
			self.input=None
		else:
			self.input=inputOption
		self.mirror=False
		if parameterExists(parafilename, 'mirror'):
			self.mirror=True

		self.ncc_oxy            = float(extractParameter(parafilename, 'ncc_oxy'           ))
		self.ncc_gad            = float(extractParameter(parafilename, 'ncc_gad'           ))
		self.n_cr                = float(extractParameter(parafilename, 'n_cr'              ))
		self.Delta_g            = float(extractParameter(parafilename, 'Delta_g'           ))
		self.J4f                = float(extractParameter(parafilename, 'J4f'               ))
		self.Jcf                = float(extractParameter(parafilename, 'Jcf'               ))
		self.D0                 = float(extractParameter(parafilename, 'D0 '               ))
		self.W                  = float(extractParameter(parafilename, 'W  '               ))
		self.spin0              = float(extractParameter(parafilename, 'spin0'             ))
		self.Ul                 = float(extractParameter(parafilename, 'Ul'                ))
		self.Ur                 = float(extractParameter(parafilename, 'Ur'                ))
		self.Delta_l0           = float(extractParameter(parafilename, 'Delta_l0'          ))
		self.Delta_r0           = float(extractParameter(parafilename, 'Delta_r0'          ))
		self.Delta_W            = float(extractParameter(parafilename, 'Delta_W'           ))
		self.eta                = float(extractParameter(parafilename, 'eta'               ))
		self.iota               = float(extractParameter(parafilename, 'iota'              ))
		self.domega_log_max     = float(extractParameter(parafilename, 'domega_log_max'    ))
		self.omega_log_1        = float(extractParameter(parafilename, 'omega_log_1'       ))
		self.N_log              = float(extractParameter(parafilename, 'N_log'             ))
		self.N_fermi            = float(extractParameter(parafilename, 'N_fermi'           ))
		self.domega_min_steps_l = float(extractParameter(parafilename, 'domega_min_steps_l'))
		self.domega_min_steps_r = float(extractParameter(parafilename, 'domega_min_steps_r'))
		self.omega_min          = float(extractParameter(parafilename, 'omega_min'         ))
		self.omega_max          = float(extractParameter(parafilename, 'omega_max'         ))
		self.dntol              = float(extractParameter(parafilename, 'dntol'             ))
		self.fltol              = float(extractParameter(parafilename, 'fltol'             ))
		self.tol                = float(extractParameter(parafilename, 'tol'               ))
		self.wr1                = float(extractParameter(parafilename, 'wr1'               ))
		self.wr0                = float(extractParameter(parafilename, 'wr0'               ))
		self.wru                = float(extractParameter(parafilename, 'wru'               ))
		self.max1               = float(extractParameter(parafilename, 'max1'              ))
		self.max2               = float(extractParameter(parafilename, 'max2'              ))
	
		self.insulator=False
		if parameterExists(parafilename, 'insulator'):
			self.insulator=True
		self.twod=False
		if parameterExists(parafilename, '2d'):
			self.twod=True
		self.verbose=False
		if parameterExists(parafilename, 'verbose'):
			self.verbose=True
		self.no_cleaning=False
		if parameterExists(parafilename, 'no_cleaning'):
			self.no_cleaning=True

	def match(self, key, value):
		saved_value=eval('self.%s' % key)
		#print "%s: %s %s" % (key, value, saved_value)
		if saved_value==value:
			return True
		else:
			return False

	def get_system(self):
		for system in self.physical_systems:
			#print "%s (positive):" % system.name
			match=True
			for key,value in system.positive.items():
				match=self.match(key,value)
				if match==False:
					break
			#print "%s (negative):" % system.name
			notmatch=True
			for key,value in system.negative.items():
				notmatch= not self.match(key,value)
				if notmatch==False:
					break

			if match and notmatch:
				#print "system found: %s" % system.name
				return system
		return None

	# get run command for isolated systems
	def get_runcmd_hetero(self, name, N, M, ni, ncr, dW, T=None):
		for system in self.physical_systems:
			if (system.name==name):
				if system.constituents==(None,None):
					print "Error: System parameter class: Not a heterostructure system: %s. Break." % name
					exit(1)
				runcmd='euo.out'
				for (key, value) in system.positive.items():
					if not key in common_positive:
						if type(value)!=bool:
							runcmd+=' --%s %s' % (key, value)
						else:
							if value==True:
								runcmd+=' --%s' % key
				if T==None:
					runcmd+=' -n %i -m %i -x %e --n_cr %e --Delta_W %e' % (N, M, ni, ncr, dW) 
				else:
					runcmd+=' -n %i -m %i -x %e --n_cr %e --Delta_W %e -t %e' % (N, M, ni, ncr, dW, T) 
				return runcmd
		# if system name is not found:
		print "Error: System parameter class: Unknown system: %s. Break." % name
		exit(1)
			
	def get_runcmd_isolated(self, name, N, nc, T=None):
		for system in self.physical_systems:
			if (system.name==name):
				if system.constituents!=(None,None):
					print "Error: System parameter class: Not an isolated system: %s. Break." % name
					exit(1)
				runcmd='euo.out'
				for (key, value) in system.positive.items():
					if not key in common_positive:
						if type(value)!=bool:
							runcmd+=' --%s %s' % (key, value)
						else:
							if value==True:
								runcmd+=' --%s' % key
				if T==None:
					runcmd+=' -n %i -x %e' % (N, nc)
				else:
					runcmd+=' -n %i -x %e -t %e' % (N, nc, T)
				return runcmd
		# if system name is not found:
		print "Error: System parameter class: Unknown system: %s. Break." % name
		exit(1)

	def get_physical_system(self, name):
		for system in self.physical_systems:
			if (system.name==name):
				return system
		# if system name is not found:
		print "Error: System parameter class: Unknown system: %s. Break." % name
		exit(1)

def main():
	sp=system_parameter()
	cmd="mpirun -np 4 euo.out -s -m 2 -n 5 --n_cr 1.0 --eta 1E-4"
	sp.read_cmd(cmd)
	sp.get_system()

	


if __name__=="__main__":
	main()