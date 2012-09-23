#!/usr/bin/python

import itertools as it
import subprocess
import sys
import job
import pararun

########################################
### ARGUMENTS FOR THE PARARUN OBJECT ###
########################################
# basic run command
basecmd = 'mpirun -np 4 euo.out'

# list of parameters: output key, output format (type, width, precision), commanline key, parameter values  
para_list=[]
para_list.append( (  '', ('s',)     , '-p', ('Gd', 'O')                         ) )
para_list.append( ('ni', ('f', 4, 2), '-x', (0.01,0.02)                         ) )
para_list.append( ( 't', ('f', 5, 1), '-t', (20,40,60,70,75)+tuple(range(80,96))) )

# output (optional, default is no output) : commandline key, prefix, suffix
output = ('-o', 'output', '/')

# runfunc: a function
# It specifies how to execute the commands (optional, default is execution in shell)
#
# arguments: 
# cmd: string containing the commanline run argument
# logstring: string containing the basic 'name' of the run. Can be used for logfiles
# append: Bool. Can be used to decide if logfiles should be appended or not. If False,
#         the logstring contains information about the parameters. 
# email: string containing email address
#
# Build in runs are:
# - run_shell
#   default, exection in shell, ignoring logstring and append
# - run_shell_log
#   execution in shell, by writing the standard output into <logstring>.log and <logstring>.err
# - run_submit
#   use the job class to submit the job. Receive an email with status message about the jobs.
#   writing the standard output into <logstring>.log and <logstring>.err
# - run_print
#   print for testing purposes (no excecution)
# Example for a runcommand defined by the user:
def run_bash(cmd, logstring, append, email):
	if append:
		subprocess.call('bash %s >> %s.log 2>>%s.err)' % (cmd, logstring, logstring))
	else:
		subprocess.call('bash %s  > %s.log  2>%s.err)' % (cmd, logstring, logstring))

# log: string containing the name of the log files (default is 'run')
# append: Bool. It is passed to runfunc
# email: Email address, also passed to runfunc

		
########################################
### USAGE ##############################
########################################
# test run (no excetution) for the above parameters
p=pararun.pararun(basecmd, para_list, output, runfunc=pararun.run_print, log='lauf')
p.run()


########################################
### FURTHER EXAMPLES ###################
########################################
# excecute: sleep 1, sleep sdjfkl, sleep 2 
# without logfiles
# Of course, the second command will result 
# in an error
sleep_list=[]
sleep_list.append(('', ('s',), '', ('1','sdjfkl', '2')))
q=pararun.pararun('sleep', sleep_list)
q.run()

# excecute: sleep 1, sleep sdjfkl, sleep 2 
# in shell with logfiles
# tired_1.log
# tired_1.err
# tired_sdjfk.log
# tired_sdjfk.err
# tired_2.log
# tired_2.err
q=pararun.pararun('sleep', sleep_list, runfunc=pararun.run_shell_log, log='tired', append=False)
q.run()

# excecute: sleep 1, sleep sdjfkl, sleep 2 
# by submitting. Status is send to via email and there will be only two log files (append=True by default):
# tired.log
# tired.err
q=pararun.pararun('sleep', sleep_list, runfunc=pararun.run_submit, log='tired', email='stollenwerk@th.physik.uni-bonn.de')
q.run()
