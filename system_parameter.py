#!/usr/bin/python

import os
import subprocess

# class defining different types of physical systems
class physical_system:
	def __init__(self, name, material_class, positve, negative, constituents=(None,None)):
		self.name=name
		if material_class!='bulk' and material_class!='isolated' and material_class!='heterostructure':
			print "Error: physical system class: Unknown material class: %s" % material_class
			print "Allowed classes are: 'bulk', 'isolated' and 'heterostructure'. Break."
			exit(1)
		self.material_class=material_class
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
#common_positive['B']=0.0

#######################################
### Bulk materials ####################
#######################################
# bulk metal
name='Bulk-Metal'
material_class='bulk'
positive={}
positive['N']=1
positive['N0']=0
positive['impurity']='None'
positive['Jcf']=0.0
positive['eta']=0.0
positive.update(common_positive)
negative={}
physical_systems.append(physical_system (name, material_class, positive, negative))

# bulk Gadolinium
name='Bulk-Gadolinium'
material_class='bulk'
positive={}
positive['N']=1
positive['N0']=0
positive['impurity']='None'
positive['Jcf']=0.03036
positive['eta']=0.0
positive.update(common_positive)
positive['J4f']=0.0
positive['longrange']=True
positive['hcp']=False
positive['hcpsub']=False
negative={}
physical_systems.append(physical_system (name, material_class, positive, negative))

# bulk Gadolinium with HCP lattice
name='Bulk-Gadolinium-HCP'
material_class='bulk'
positive={}
positive['N']=1
positive['N0']=0
positive['impurity']='None'
positive['Jcf']=0.03036
positive['eta']=0.0
positive['longrange']=True
positive['D0l']=2.985
positive.update(common_positive)
positive['J4f']=0.0
positive['hcp']=True
positive['hcpsub']=True
positive['omega_min']=-8.0
positive['omega_max']=8.0
negative={}
physical_systems.append(physical_system (name, material_class, positive, negative))



# bulk heisenberg-metal
name='Bulk-Heisenberg-Metal'
material_class='bulk'
positive={}
positive['N']=1
positive['N0']=0
positive['impurity']='None'
positive['Jcf']=0.05
positive['eta']=0.0
positive.update(common_positive)
negative={}
physical_systems.append(physical_system (name, material_class, positive, negative))

# EuGdO
name='Bulk-EuGdO'
material_class='bulk'
positive={}
positive['N']=1
positive['N0']=0
positive['impurity']='Gd'
positive['ncc_gad']=0.9952
positive['Jcf']=0.05
positive['eta']=1E-9
positive.update(common_positive)
negative={}
physical_systems.append(physical_system (name, material_class, positive, negative))

# EuGdO with external magnetic field
#Bvalues=(1E-9,1E-8,1E-7,2E-7,5E-7,1E-6,2E-6,5E-6,1E-5,2E-5,5E-5,1E-4,2E-4,5E-4,1E-3,2E-3,5E-3,1E-2)
#for B in Bvalues:
#	name='Bulk-EuGdO-B%0.8f' % B
#	material_class='bulk'
#	positive={}
#	positive['N']=1
#	positive['N0']=0
#	positive['impurity']='Gd'
#	positive['ncc_gad']=0.9952
#	positive['Jcf']=0.05
#	positive['eta']=1E-9
#	positive.update(common_positive)
#	positive['B']=B
#	negative={}
#	physical_systems.append(physical_system (name, material_class, positive, negative))


# Kondometal
EdKondoValues=(0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9)
for Ed in EdKondoValues:
	name='Bulk-KondoMetal-Ed%06.4f' % Ed
	material_class='bulk'
	positive={}
	positive['N']=1
	positive['N0']=0
	positive['impurity']='Gd'
	positive['ncc_gad']=1.0
	positive['Jcf']=0.00
	positive['eta']=1E-9
	positive.update(common_positive)
	positive['Ed0']=Ed
	positive['kondo']=True
	negative={}
	physical_systems.append(physical_system (name, material_class, positive, negative))

# EuGdO with various impurity energies
EdValues=(-0.00,-0.01,-0.02,-0.03,-0.04,-0.05,-0.06,-0.1,-0.15)
for Ed in EdValues:
	name='Bulk-EuGdO-Ed%+05.3f' % Ed
	material_class='bulk'
	positive={}
	positive['N']=1
	positive['N0']=0
	positive['impurity']='Gd'
	positive['ncc_gad']=0.9952
	positive['Jcf']=0.05
	positive['eta']=1E-9
	positive.update(common_positive)
	positive['Ed0']=Ed
	negative={}
	physical_systems.append(physical_system (name, material_class, positive, negative))

# EuO_1-x
name='Bulk-EuO_1-x'
material_class='bulk'
positive={}
positive['N']=1
positive['N0']=0
positive['impurity']='O'
positive['ncc_gad']=0.9864
positive['Jcf']=0.05
positive['eta']=1E-9
positive.update(common_positive)
negative={}
physical_systems.append(physical_system (name, material_class, positive, negative))

# EuO_1-x with finite on-site Coulomb repulsion
Wvalues=(0.000,0.001,0.002,0.003,0.004,0.005,0.01,0.02,0.03,0.04,0.045,0.044,0.05,0.06,0.07,0.08,0.09,0.093,0.094,0.1,0.125,0.2,0.5)
EdValues=(0.00,-0.01,-0.02,-0.03,-0.04,-0.05,-0.06,-0.1,-0.125,-0.15)
for W in Wvalues:
	name='Bulk-EuO_1-x-W%05.3f' % W
	material_class='bulk'
	positive={}
	positive['N']=1
	positive['N0']=0
	positive['impurity']='O'
	positive['ncc_gad']=0.9864
	positive['Jcf']=0.05
	positive['eta']=1E-9
	positive.update(common_positive)
	positive['W']=W
	negative={}
	physical_systems.append(physical_system (name, material_class, positive, negative))

# EuO_1-x with finite on-site Coulomb repulsion and varying impurity level energy
for W in Wvalues:
	for Ed in EdValues:
		name='Bulk-EuO_1-x-Ed%+05.3f-W%05.3f' % (Ed,W)
		material_class='bulk'
		positive={}
		positive['N']=1
		positive['N0']=0
		positive['impurity']='O'
		positive['ncc_gad']=0.9864
		positive['Jcf']=0.05
		positive['eta']=1E-9
		positive.update(common_positive)
		positive['W']=W
		positive['Ed0']=Ed
		negative={}
		physical_systems.append(physical_system (name, material_class, positive, negative))


#######################################
### Isolated materials ################
#######################################
# metal
name='Metal'
material_class='isolated'
positive={}
positive['N0']=0
positive['impurity']='None'
positive['Jcf']=0.0
positive['eta']=0.0
positive['mirror']=True
positive.update(common_positive)
negative={}
physical_systems.append(physical_system (name, material_class, positive, negative))

# heisenberg-metal
name='Heisenberg-Metal'
material_class='isolated'
positive={}
positive['N0']=0
positive['impurity']='None'
positive['Jcf']=0.05
positive['eta']=0.0
positive['mirror']=True
positive.update(common_positive)
negative={}
physical_systems.append(physical_system (name, material_class, positive, negative))

# EuGdO
name='EuGdO'
material_class='isolated'
positive={}
positive['N0']=0
positive['impurity']='Gd'
positive['ncc_gad']=0.9952
positive['Jcf']=0.05
positive['eta']=1E-9
positive['mirror']=True
positive.update(common_positive)
negative={}
physical_systems.append(physical_system (name, material_class, positive, negative))

# Kondometal
for Ed in EdKondoValues:
	name='KondoMetal-Ed%06.4f' % Ed
	material_class='isolated'
	positive={}
	positive['N0']=0
	positive['impurity']='Gd'
	positive['ncc_gad']=1.0
	positive['Jcf']=0.00
	positive['eta']=1E-9
	positive['mirror']=True
	positive.update(common_positive)
	positive['Ed0']=Ed
	positive['kondo']=True
	negative={}
	physical_systems.append(physical_system (name, material_class, positive, negative))

#######################################
### Two component heterostructures ####
#######################################
# EuGdO-Metal-Heterostructure
name='EuGdO-Metal-Heterostructure-eta1e-6'
material_class='heterostructure'
left='EuGdO'
right='Metal'
positive={}
positive['impurity']='Gd'
positive['ncc_gad']=0.9952
positive['Jcf']=0.05
positive['eta']=1E-6
positive['mirror']=True
positive['insulator']=False
positive['magnsub']=False
positive['ifcoupl']=False
positive['kondosub']=False
positive.update(common_positive)
negative={}
negative['N0']=0
physical_systems.append(physical_system (name, material_class, positive, negative, (left,right)))

# EuGdO-Metal-Heterostructure
name='EuGdO-Metal-Heterostructure-eta1e-4'
material_class='heterostructure'
left='EuGdO'
right='Metal'
positive={}
positive['impurity']='Gd'
positive['ncc_gad']=0.9952
positive['Jcf']=0.05
positive['eta']=1E-4
positive['mirror']=True
positive['insulator']=False
positive['magnsub']=False
positive['ifcoupl']=False
positive['kondosub']=False
positive.update(common_positive)
negative={}
negative['N0']=0
physical_systems.append(physical_system (name, material_class, positive, negative, (left,right)))

# EuGdO-Metal-Heterostructure with intensified interface coupling
JcfpValues=(0.01, 0.02, 0.03, 0.04, 0.0405, 0.05)
for Jcfp in JcfpValues:
	name='EuGdO-Metal-Heterostructure-eta1e-4-IIC-Jcfp%06.4f' % Jcfp
	material_class='heterostructure'
	left='EuGdO'
	right='Metal'
	positive={}
	positive['impurity']='Gd'
	positive['ncc_gad']=0.9952
	positive['Jcf']=0.05
	positive['eta']=1E-4
	positive['mirror']=True
	positive['insulator']=False
	positive['magnsub']=False
	positive['ifcoupl']=True
	positive['Jcfp']=Jcfp
	positive['kondosub']=False
	positive.update(common_positive)
	negative={}
	negative['N0']=0
	physical_systems.append(physical_system (name, material_class, positive, negative, (left,right)))


# EuGdO-KondoMetal-Heterostructure
for Ed in EdKondoValues:
	name='EuGdO-KondoMetal-Edr%06.4f-Heterostructure-eta1e-4' % Ed
	material_class='heterostructure'
	left='EuGdO'
	right='KondoMetal-Ed%06.4f' % Ed
	positive={}
	positive['impurity']='Gd'
	positive['ncc_gad']=0.9952
	positive['Jcf']=0.05
	positive['eta']=1E-4
	positive['mirror']=True
	positive['insulator']=False
	positive['magnsub']=False
	positive['ifcoupl']=False
	positive['kondosub']=True
	positive['Ed0r']=Ed
	positive.update(common_positive)
	negative={}
	negative['N0']=0
	physical_systems.append(physical_system (name, material_class, positive, negative, (left,right)))

# EuGdO-HeisenbergMetal-Heterostructure
name='EuGdO-HeisenbergMetal-Heterostructure-eta1e-4'
material_class='heterostructure'
left='EuGdO'
right='Heisenberg-Metal'
positive={}
positive['impurity']='Gd'
positive['ncc_gad']=0.9952
positive['Jcf']=0.05
positive['eta']=1E-4
positive['mirror']=True
positive['magnsub']=True
positive['ifcoupl']=False
positive['Jcfs']=0.05
positive['J4fs']=7E-5
positive['insulator']=False
positive['kondosub']=False
positive.update(common_positive)
negative={}
negative['N0']=0
physical_systems.append(physical_system (name, material_class, positive, negative, (left,right)))

# HeisenbergMetal-Metal-Heterostructure
name='HeisenbergMetal-Metal-Heterostructure'
material_class='heterostructure'
left='Heisenberg-Metal'
right='Metal'
positive={}
positive['impurity']='None'
positive['Jcf']=0.05
positive['eta']=0.0
positive['mirror']=True
positive['insulator']=False
positive['magnsub']=False
positive['ifcoupl']=False
positive['kondosub']=False
positive.update(common_positive)
negative={}
negative['N0']=0
physical_systems.append(physical_system (name, material_class, positive, negative, (left,right)))

# Metal-Metal-Heterostructure
name='Metal-Metal-Heterostructure'
material_class='heterostructure'
left='Metal'
right='Metal'
positive={}
positive['impurity']='None'
positive['Jcf']=0.00
positive['eta']=0.0
positive['mirror']=True
positive['insulator']=False
positive['magnsub']=False
positive['ifcoupl']=False
positive['kondosub']=False
positive.update(common_positive)
negative={}
negative['N0']=0
physical_systems.append(physical_system (name, material_class, positive, negative, (left,right)))

####################################################################
### Bulk materials with long range RKKY coupling
####################################################################

# EuGdO with long range (LR) coupling
name='Bulk-EuGdO-LR'
material_class='bulk'
positive={}
positive['N']=1
positive['N0']=0
positive['impurity']='Gd'
positive['ncc_gad']=0.9952
positive['Jcf']=0.0405
positive['eta']=1E-9
positive['longrange']=True
positive.update(common_positive)
negative={}
physical_systems.append(physical_system (name, material_class, positive, negative))


# EuGdO with long range (LR) coupling with various c-f couplings
JcfValues=(0.0395,0.0400,0,0405,0.0410)
RmaxValues=(5,10,15,20)
for Jcf in JcfValues:
	for Rmax in RmaxValues:
		name='Bulk-EuGdO-LR-Jcf%06.4f_Rmax%02i' % (Jcf, Rmax)
		material_class='bulk'
		positive={}
		positive['N']=1
		positive['N0']=0
		positive['impurity']='Gd'
		positive['ncc_gad']=0.9952
		positive['Jcf']=Jcf
		positive['Rmax']=Rmax
		positive['eta']=1E-9
		positive['longrange']=True
		positive.update(common_positive)
		negative={}
		physical_systems.append(physical_system (name, material_class, positive, negative))

# bulk heisenberg-metal with long range RKKY coupling
name='Bulk-Heisenberg-Metal-LR'
material_class='bulk'
positive={}
positive['N']=1
positive['N0']=0
positive['impurity']='None'
positive['Jcf']=0.0405
#positive['Rmax']=10
positive['eta']=0.0
positive['longrange']=True
positive.update(common_positive)
negative={}
physical_systems.append(physical_system (name, material_class, positive, negative))

####################################################################
### Isolated materials with long range RKKY coupling
####################################################################

# heisenberg-metal with long range RKKY coupling
name='Heisenberg-Metal-LR'
material_class='isolated'
positive={}
positive['N0']=0
positive['impurity']='None'
positive['Jcf']=0.0405
#positive['Rmax']=10
positive['eta']=0.0
positive['mirror']=True
positive['longrange']=True
positive.update(common_positive)
negative={}
physical_systems.append(physical_system (name, material_class, positive, negative))

# heisenberg-metal with long range RKKY coupling
name='Gadolinium'
material_class='isolated'
positive={}
positive['N0']=0
positive['impurity']='None'
positive['Jcf']=0.03036
#positive['Rmax']=10
positive['eta']=0.0
positive['mirror']=True
positive['longrange']=True
positive['hcp']=False
positive['hcpsub']=False
positive.update(common_positive)
positive['J4f']=0.0
negative={}
physical_systems.append(physical_system (name, material_class, positive, negative))

# Gadolinium with HCP lattice
name='Gadolinium-HCP'
material_class='isolated'
positive={}
positive['N0']=0
positive['impurity']='None'
positive['Jcf']=0.03036
#positive['Rmax']=10
positive['eta']=0.0
positive['mirror']=True
positive['longrange']=True
positive.update(common_positive)
positive['J4f']=0.0
positive['hcp']=True
positive['hcpsub']=True
positive['D0l']=2.985
positive['omega_min']=-8.0
positive['omega_max']=8.0
negative={}
physical_systems.append(physical_system (name, material_class, positive, negative))

# EuGdO with long range RKKY coupling
name='EuGdO-LR'
material_class='isolated'
positive={}
positive['N0']=0
positive['impurity']='Gd'
positive['ncc_gad']=0.9952
positive['Jcf']=0.0405
#positive['Rmax']=10
positive['eta']=1E-9
positive['mirror']=True
positive['longrange']=True
positive.update(common_positive)
negative={}
physical_systems.append(physical_system (name, material_class, positive, negative))

####################################################################
### Heterostructure materials with long range RKKY coupling
####################################################################

# EuGdO-Metal-Heterostructure with long range RKKY coupling
name='EuGdO-Metal-Heterostructure-eta1e-4-LR'
material_class='heterostructure'
left='EuGdO-LR'
right='Metal'
positive={}
positive['impurity']='Gd'
positive['ncc_gad']=0.9952
positive['Jcf']=0.0405
#positive['Rmax']=10
positive['eta']=1E-4
positive['mirror']=True
positive['insulator']=False
positive['longrange']=True
positive['magnsub']=False
positive['ifcoupl']=False
positive['kondosub']=False
positive.update(common_positive)
negative={}
negative['N0']=0
physical_systems.append(physical_system (name, material_class, positive, negative, (left,right)))

# EuGdO-Metal-Heterostructure with long range RKKY coupling and intensified interface coupling
for Jcfp in JcfpValues:
	name='EuGdO-Metal-Heterostructure-eta1e-4-LR-IIC-Jcfp%06.4f' % Jcfp
	material_class='heterostructure'
	left='EuGdO-LR'
	right='Metal'
	positive={}
	positive['impurity']='Gd'
	positive['ncc_gad']=0.9952
	positive['Jcf']=0.0405
	#positive['Rmax']=10
	positive['eta']=1E-4
	positive['mirror']=True
	positive['insulator']=False
	positive['longrange']=True
	positive['magnsub']=False
	positive['ifcoupl']=True
	positive['Jcfp']=Jcfp
	positive['kondosub']=False
	positive.update(common_positive)
	negative={}
	negative['N0']=0
	physical_systems.append(physical_system (name, material_class, positive, negative, (left,right)))


# EuGdO-HeisenbergMetal-Heterostructure with long range RKKY coupling
name='EuGdO-HeisenbergMetal-Heterostructure-eta1e-4-LR'
material_class='heterostructure'
left='EuGdO-LR'
right='Heisenberg-Metal'
positive={}
positive['impurity']='Gd'
positive['ncc_gad']=0.9952
positive['Jcf']=0.0405
#positive['Rmax']=10
positive['eta']=1E-4
positive['magnsub']=True
positive['ifcoupl']=False
positive['kondosub']=False
positive['Jcfs']=0.0405
positive['J4fs']=7E-5
positive['mirror']=True
positive['insulator']=False
positive['longrange']=True
positive.update(common_positive)
negative={}
negative['N0']=0
physical_systems.append(physical_system (name, material_class, positive, negative, (left,right)))

# EuGdO-Gadolinium-Heterostructure with long range RKKY coupling
name='EuGdO-Gadolinium-Heterostructure-eta1e-4-LR'
material_class='heterostructure'
left='EuGdO-LR'
right='Gadolinium'
positive={}
positive['impurity']='Gd'
positive['ncc_gad']=0.9952
positive['Jcf']=0.0405
#positive['Rmax']=10
positive['eta']=1E-4
positive['magnsub']=True
positive['ifcoupl']=False
positive['kondosub']=False
positive['Jcfs']=0.03036
positive['J4fs']=0.0
positive['mirror']=True
positive['insulator']=False
positive['longrange']=True
positive.update(common_positive)
negative={}
negative['N0']=0
physical_systems.append(physical_system (name, material_class, positive, negative, (left,right)))


# HeisenbergMetal-Metal-Heterostructure with long range RKKY coupling
name='HeisenbergMetal-Metal-Heterostructure-LR'
material_class='heterostructure'
left='Heisenberg-Metal-LR'
right='Metal'
positive={}
positive['impurity']='None'
positive['Jcf']=0.0405
#positive['Rmax']=10
positive['eta']=0.0
positive['mirror']=True
positive['insulator']=False
positive['longrange']=True
positive['magnsub']=False
positive['ifcoupl']=False
positive['kondosub']=False
positive.update(common_positive)
negative={}
negative['N0']=0
physical_systems.append(physical_system (name, material_class, positive, negative, (left,right)))

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
		self.hcp                 =    option_exists(runcmd, ('--hcp',))
		self.hcpsub              =    option_exists(runcmd, ('--hcpsub',))
		self.kondo               =    option_exists(runcmd, ('--kondo',))
		self.kondosub            =    option_exists(runcmd, ('--kondosub',))
		self.Ed0r                = float(get_option(runcmd, ('--Ed0r',),                               0.5))
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
		self.D0l                 = float(get_option(runcmd, ('--D0l',),                               1.0))
		self.D0r                 = float(get_option(runcmd, ('--D0r',),                               1.0))
		self.Delta_l0            = float(get_option(runcmd, ('--Delta_l0',),                          0.0))
		self.Delta_r0            = float(get_option(runcmd, ('--Delta_r0',),                          0.0))
		self.Delta_W             = float(get_option(runcmd, ('--Delta_W',),                           0.0))
		self.eta                 = float(get_option(runcmd, ('--eta',),                              1E-9))
		self.iota                = float(get_option(runcmd, ('--iota',),                             1E-4))
		self.domega_log_max      = float(get_option(runcmd, ('--domega_log_max',),                   0.01))
		self.omega_log_1         = float(get_option(runcmd, ('--omega_log_1',),                       0.1))
		self.N_log               = float(get_option(runcmd, ('--N_log',),                             200))
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
		self.longrange           =    option_exists(runcmd, ('--longrange',))
		self.Rmax                = float(get_option(runcmd, ('--Rmax',),                              2.0))
		self.magnsub             =    option_exists(runcmd, ('--magnsub',))
		self.J4fs                = float(get_option(runcmd, ('--J4fs',),                             7E-5))
		self.Jcfs                = float(get_option(runcmd, ('--Jcfs',),                             5E-2))
		self.ifcoupl             =    option_exists(runcmd, ('--ifcoupl',))
		self.Jcfp                = float(get_option(runcmd, ('--Jcfp',),                             1E-2))
		self.Delta_m             = float(get_option(runcmd, ('--Delta_m',),                           0.0))
		self.B                   = float(get_option(runcmd, ('--B',),                                 0.0))

	# read in parameter file and map this onto a material class.
	def read_file(self, parafilename):
		self.concentration      = float(extractParameter(parafilename, 'concentration'     ))
		self.temperature        = float(extractParameter(parafilename, 'temperature'       ))
		self.N                  =   int(extractParameter(parafilename, 'N'                 ))
		self.N0                 =   int(extractParameter(parafilename, 'N0'                ))
		self.Ed0                = float(extractParameter(parafilename, 'Ed0'               ))
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
		self.n_cr               = float(extractParameter(parafilename, 'n_cr'              ))
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
		self.N_fermi            =   int(extractParameter(parafilename, 'N_fermi'           ))
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
		self.max1               =   int(extractParameter(parafilename, 'max1'              ))
		self.max2               =   int(extractParameter(parafilename, 'max2'              ))
	
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
		self.hcp=False
		if parameterExists(parafilename, 'hcp'):
			self.hcp=True
		self.hcpsub=False
		if parameterExists(parafilename, 'hcpsub'):
			self.hcpsub=True
		self.kondo=False
		if parameterExists(parafilename, 'kondo'):
			self.kondo=True
		self.kondosub=False
		if parameterExists(parafilename, 'kondosub'):
			self.kondosub=True
		if parameterExists(parafilename, 'Ed0r'):
			self.Ed0r      = float(extractParameter(parafilename, 'Ed0r'              ))
		self.D0l=1.0
		self.D0r=1.0
		if parameterExists(parafilename, 'D0l'):
			self.D0l       = float(extractParameter(parafilename, 'D0l'               ))
		if parameterExists(parafilename, 'D0r'):
			self.D0r       = float(extractParameter(parafilename, 'D0r'               ))
		self.longrange=False
		self.Rmax=2.0
		if parameterExists(parafilename, 'longrange'):
			self.longrange = True
			self.Rmax      = float(extractParameter(parafilename, 'Rmax'              ))
		self.magnsub=False
		self.J4fs=7E-5
		self.Jcfs=5E-2
		if parameterExists(parafilename, 'magnsub'):
			self.magnsub = True
			self.J4fs    = float(extractParameter(parafilename, 'J4fs'                ))
			self.Jcfs    = float(extractParameter(parafilename, 'Jcfs'                ))
		self.ifcoupl=False
		self.Jcfp=1E-2
		if parameterExists(parafilename, 'ifcoupl'):
			self.ifcoupl = True
			self.Jcfp    = float(extractParameter(parafilename, 'Jcfp'                ))
		if parameterExists(parafilename, 'Delta_m'):
			self.Delta_m = float(extractParameter(parafilename, 'Delta_m'             ))
		if parameterExists(parafilename, 'B'):
			self.B       = float(extractParameter(parafilename, 'B'                   ))

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
					#print "\t%s=%s does not match" % (key,value)
					break
			#print "%s (negative):" % system.name
			notmatch=True
			for key,value in system.negative.items():
				notmatch= not self.match(key,value)
				if notmatch==False:
					#print "\t%s=%s does not match" % (key,value)
					break

			if match and notmatch:
				#print "system found: %s" % system.name
				return system
		return None

	def get_system_by_name(self, system_name):
		for system in self.physical_systems:
			if system.name==system_name:
				return system

		print "Error: System parameter class: Unknown system: %s. Break." % system_name
		exit(1)


	# get run command for isolated systems
	def get_runcmd_hetero(self, name, N, M, ni, ncr, dW, T=None):
		for system in self.physical_systems:
			if (system.name==name):
				if system.material_class!='heterostructure':
					print "Error: System parameter class: Not a heterostructure system: %s. Break." % name
					exit(1)
				runcmd='euo.out'
				for (key, value) in system.positive.items():
					if not (key, value) in common_positive.items():
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
				if system.material_class!='isolated':
					print "Error: System parameter class: Not an isolated system: %s. Break." % name
					exit(1)
				runcmd='euo.out'
				for (key, value) in system.positive.items():
					if not (key, value) in common_positive.items():
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

	def get_runcmd_bulk(self, name, ni, T=None):
		for system in self.physical_systems:
			if (system.name==name):
				if system.material_class!='bulk':
					print "Error: System parameter class: Not an isolated system: %s. Break." % name
					exit(1)
				runcmd='euo.out'
				for (key, value) in system.positive.items():
					if not (key, value) in common_positive.items():
						if type(value)!=bool:
							runcmd+=' --%s %s' % (key, value)
						else:
							if value==True:
								runcmd+=' --%s' % key
				if T==None:
					runcmd+=' -x %e' % (ni)
				else:
					runcmd+=' -x %e -t %e' % (ni, T)
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

	def print_physical_systems(self):
		for system in self.physical_systems:
			print "###########################################"
			print system.name
			print "###########################################"
			print "\tMaterial class: ", system.material_class
			print ""
			print "\tAttributes:"
			for (key, value) in system.positive.items():
				if not (key, value) in common_positive.items():
					print '\t\t'+'{0: <10}'.format(key)+'\t{0: <10}'.format(value)
			print ""
			print "\tNegated Attributes:"
			for (key, value) in system.negative.items():
				print "\t\t", key,"\t", value
			print ""
def main():
	sp=system_parameter()
	cmd="mpirun --hostfile /users/stollenw/runs/hostfile_bgem -np 64 euo.out --N 1 --N0 0 --longrange --impurity Gd --eta 1e-09 --ncc_gad 0.9952 -x 4.000000e-02 -t 1.200000e+02 --wrs 0.05 --max2 0 --max2_end 5 --Jcf 0.03000 --Rmax 10.0 --max1 5000 -o Bulk-EuGdO-TestJcf_ni0.0400_Jcf0.03000_Rmax10.00/t120.000// -i /users/stollenw/runs/runs_version-8812385/bgem/Bulk-EuGdO_ni0.0400/t120.000/"
	#cmd="mpirun -np 4 euo.out -s -m 2 -n 5 --n_cr 1.0 --eta 1E-4"
	sp.read_cmd(cmd)
	print sp.get_system().name

	


if __name__=="__main__":
	main()
