#!/usr/bin/python

import argparse
import subprocess
import time
import os
import sys

class queue:
	def __init__(self, qfile):
		if qfile==None:
			home=os.environ['HOME']	
			qfile=home + "/.queue"
		self.queuefile=qfile
		self.lockfile="%s.lock" % qfile
		try:
			f = open(qfile, 'a')
			f.close()
		except:
			print "Unable to open queue configuration file %s. Break." % qfile
			sys.exit(1)
	# is config file currently open
	def waitfree(self):
		if os.path.exists(self.lockfile):
			time.sleep(1)
			if os.path.exists(self.lockfile):
				print "Queue config file: %s is locked. Remove %s manually?. Break." % (self.queuefile, self.lockfile)
				exit(1)

	def lock(self):
		f = open(self.lockfile, 'w')
		f.close()
	def unlock(self):
		os.remove(self.lockfile)
					
	def clear(self):
		self.waitfree()
		self.lock()
		f = open(self.queuefile, 'w')
		f.close()
		self.unlock()
	def get(self):
		self.waitfree()
		self.lock()
		f=open(self.queuefile, 'r')
		job=f.readline().rstrip('\n')
		f.close()
		self.unlock()
		if job=='':
			return None
		else:
			return job

	def remove(self):
		self.waitfree()
		self.lock()
		f=open(self.queuefile, 'r')
		lines=f.readlines()
		f.close();
		f=open(self.queuefile, 'w')
		for i in range(1,len(lines)):
			f.write(lines[i])
		f.close();
		self.unlock()

	def add(self, runcmd):
		self.waitfree()
		self.lock()
		f=open(self.queuefile, 'a')
		f.write("%s\n" % runcmd)
		f.close();
		self.unlock()
	def list(self):
		self.waitfree()
		self.lock()
		f=open(self.queuefile, 'r')
		lines=f.readlines()
		f.close()
		self.unlock()
		for l in lines:
			print l.rstrip('\n')
	
		
class jobscheduler:
	def __init__(self, timeout=10.0, queue_config=None, email='stollenwerk@th.physik.uni-bonn.de', mailcmd='mailx -s'):
		self.timeout=timeout
		self.email=email
		queuefile=queue_config
		if queue_config==None:
			home=os.environ['HOME']	
			queuefile=home + "/.queue"
		self.queue=queue(queuefile)
		self.mailcmd=mailcmd
		self.first=True
		# get hostname
		proc = subprocess.Popen('hostname', stdout=subprocess.PIPE)
		self.host = proc.stdout.read().rstrip('\n')
		self.cpid=0

	def start(self):
		recent=True
		while True:
			runcmd=self.queue.get()
			#print "Next job is: %s" % runcmd
			if runcmd!=None:
				process=subprocess.Popen(runcmd, shell=True)	
				process.wait()
				recent=True
				self.queue.remove()
			else:
				if recent:
					cmd="echo ' '  | %s 'Job Scheduler: %s has nothing to do.' %s" % (self.mailcmd, self.host, self.email)
					recent=False
					#print cmd
					subprocess.call(cmd, shell=True)
			#print "Wait %i seconds ..." % self.timeout
			self.first=False
			# wait <timeout> seconds
			time.sleep(self.timeout)

def main():
	parser = argparse.ArgumentParser(description='start jobscheduler')
	parser.add_argument('-q', '--queue', default=None, help='Queue config file (Default is $HOME/.queue)')
	parser.add_argument('-t', '--timeout', default=10.0, help='Job scheduler timeout', type=float)
	parser.add_argument('-e', '--email', default='stollenwerk@th.physik.uni-bonn.de', help='Email address')
	parser.add_argument('-m', '--mailcmd', default='mailx -s', help='Mail command')
	args = parser.parse_args()
	js=jobscheduler(timeout=args.timeout, queue_config=args.queue, email=args.email, mailcmd=args.mailcmd)
	js.start()

if __name__=="__main__":
	main()
