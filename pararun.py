#!/usr/bin/python

import itertools as it
import subprocess
import sys
import os
import job

class sformat(object):

	def __init__(self, Type='s', width=1, precision=0):
		self.Type=Type
		self.width=width
		self.precision=precision

def code_string(key, value, t, width=1, precision=0):
	if t=='s':
		return "_" + value
	elif t=='f':
		return "_" + key + '{val:0{width}.{precision}{type}}'.format(val=value, width=width, precision=precision, type=t)
	elif t=='d':
		return "_" + key + '{val:0{width}{type}}'.format(val=value, width=width, type=t)

def run_shell(cmd, logstring, append, email, mailcmd):
	subprocess.call(cmd, shell=True)

class pararun:
	def __init__(self, bcmd, plist, output=None, runfunc=None, modfunc=None, modpara=None, input=None, log='run', append=True, email='stollenwerk@th.physik.uni-bonn.de', mailcmd='mailx -s'):

		self.basecmd=bcmd
		self.para_list=plist
		if output!=None:
			self.output=output
		self.output=output
		if runfunc==None:
			self.runfunc=run_shell
		else:
			self.runfunc=runfunc
		self.log=log
		self.append=append
		self.email=email
		self.mailcmd=mailcmd
		self.modfunc=modfunc
		self.modpara=modpara
		self.input=input

		#parse parameter list
		self.names=list(pl[0] for pl in plist)
		self.form=list(sformat(*pl[1]) for pl in plist)
		self.keys=list(pl[2] for pl in plist)
		self.parameter=list(it.product(*list(pl[3] for pl in plist)))

	def run(self):
		# remove log files if they exist
		if os.path.exists("%s.log" % self.log):
			os.remove("%s.log" % self.log)
		if os.path.exists("%s.err" % self.log):
			os.remove("%s.err" % self.log)
		first=True
		for para in self.parameter:
			runcmd=self.basecmd
			outputFolder=''
			if self.output!=None:
				outputFolder=self.output[1]
			logstring=''
			logstring=self.log
			for f,n,k,p in zip(self.form, self.names, self.keys, para):
				runcmd+=" %s %s" % (k,p)
				outputFolder+= code_string(n, p, f.Type, f.width, f.precision)
				if not self.append:
					logstring+= code_string(n, p, f.Type, f.width, f.precision)

			if self.input!=None and first:
				runcmd+=" %s %s" % (self.input[0], self.input[1])
			if self.output!=None:
				runcmd+=" %s %s%s" % (self.output[0], outputFolder, self.output[2])
			if self.modfunc!=None:
				runcmd=self.modfunc(runcmd, *self.modpara)
			self.runfunc(runcmd, logstring, self.append, self.email, self.mailcmd)
			first=False

# specify how to execute the commands (optional, default is execution in shell)
def run_shell_log(cmd, logstring, append, email, mailcmd):
	logfile= "%s.log" % logstring
	fileMode='w'
	if append:
		fileMode='a'
	fstdout = open(logfile, fileMode)
	fstdout.write("run: %s\n" % cmd)
	error_logfile= "%s.err" % logstring
	fstderr = open(error_logfile, fileMode)
	fstderr.write("run: %s\n" % cmd)
	process=subprocess.Popen(cmd, shell=True, stdout=fstdout, stderr=fstderr)
	fstdout.close()
	fstderr.close()
	process.wait()
	status=process.returncode
	#if status:
	#	sys.stderr.write("Warning: And error has occured during the run\n")
	#	sys.stderr.write("%s\n" % cmd)
	#	sys.stderr.write("See error log file %s.\n" % error_logfile)
		#efile = open(error_logfile, 'r')
		#for line in efile:
		#	sys.stderr.write(line)
		
def run_submit(cmd, logstring, append, email, mailcmd):
	cmds=[cmd]
	j=job.job(logstring, logstring, email, cmds, logappend=append, mailcmd=mailcmd)
	j.run()

def run_print(cmd, logstring, append, email, mailcmd):
	print cmd
