#!/usr/bin/python

import subprocess
import time
import os
import sys

class job:
	def __init__(self, n, l, e, c, logappend=False, verbose=True, proceed=True, mailcmd='mailx -s'):
		self.name=n
		self.log=l
		self.email=e
		self.cmd=c
		self.mailcmd=mailcmd
		self.logappend=logappend
		self.verbose=verbose

	def run(self):
		# get hostname
		proc = subprocess.Popen('hostname', stdout=subprocess.PIPE)
		host = proc.stdout.read().rstrip('\n')
	
		# open log files
		logfile= "%s.log" % self.log
		error_logfile= "%s.err" % self.log
		# if logs should not be appended to existing logfiles, remove them first
		if not self.logappend:
			if (os.path.exists(logfile)):
				os.remove(logfile)
			if (os.path.exists(error_logfile)):
				os.remove(error_logfile)

		# run all jobs
		for runcmd in self.cmd:
			# append logs to logfiles
			fstdout = open(logfile, 'a')
			fstdout.write("run: " + runcmd + "\n")
			fstderr = open(error_logfile, 'a')
			fstderr.write("run: " + runcmd + "\n")

			# start time
			stime=time.asctime()
			start=time.time()
		
			# run job
			process=subprocess.Popen( runcmd, shell=True, stdout=fstdout, stderr=fstderr)
			fstdout.close()
			fstderr.close()
			process.wait()
			status=process.returncode
		
			# end time
			end=time.time()

			# check status and send email
			if status and self.verbose:
				f=open("message.temp", 'w')
				f.write("And error has occured during the run: %s.\n" % self.name)
				f.write("Run command was: %s.\n" % runcmd)
				f.write("Run started at: %s.\n" % stime)
				f.write("Duration: %s.\n" % time.strftime('%H:%M:%S', time.gmtime(end-start)))
				f.write("Print error log file %s and break.\n" % error_logfile)
				efile = open(error_logfile, 'r')
				for line in efile:
					f.write(line)
				f.close()
					
				cmd="cat message.temp | %s 'Job Monitor: An error has occured durring the job %s on %s.' %s" % (self.mailcmd, self.name, host, self.email)
				#print cmd
				subprocess.call(cmd, shell=True)
				os.remove("message.temp")

			elif status==False:
				f=open("message.temp", 'w')
				f.write("Successful run: %s.\n" % self.name)
				f.write("Run command was: %s.\n" % runcmd)
				f.write("Run started at: %s.\n" % stime)
				f.write("Duration: %s.\n" % time.strftime('%H:%M:%S', time.gmtime(end-start)))
				f.close()
					
				cmd="cat message.temp  | %s 'Job Monitor: Successful job %s on %s.' %s" % (self.mailcmd, self.name, host, self.email)
				#print cmd
				subprocess.call(cmd, shell=True)
				os.remove("message.temp")
				if not proceed:
					exit(1)	
def main():
	j=job('myjob', 'mylog', 'stollenwerk@th.physik.uni-bonn.de', ['sleep 1', 'sleep sdfjkl', 'sleep 2'], logappend=True)
	j.run()

if __name__=="__main__":
	main()
